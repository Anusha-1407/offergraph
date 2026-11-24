import io
import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from ..database import get_db
from ..models import AnalysisHistory, Entity, ReportEntity, Report
from ..schemas import AnalysisResponse, ExtractedEntities, RiskIndicator
from ..services.extraction_service import (
    ExtractionService, normalize_phone, normalize_email,
    normalize_upi, normalize_domain, mask_phone, mask_email, mask_upi
)
from ..services.risk_engine import RiskEngine
from ..services.ai_service import AIService

router = APIRouter(prefix="/api/analyze", tags=["Analyze"])

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024 # 5 MB
MAX_TEXT_LENGTH = 30000

def sanitize_text(text: str) -> str:
    """Strips dangerous script tags and null bytes from input."""
    if not text:
        return ""
    cleaned = text.replace("\x00", "")
    # Basic tag strip for script/iframe
    import re
    cleaned = re.sub(r'<\s*(script|iframe|style|object|embed)[^>]*>.*?<\s*/\s*\1\s*>', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    return cleaned

def extract_text_from_file(file: UploadFile) -> str:
    # 1. File extension validation
    filename = (file.filename or "upload.txt").lower()
    if not (filename.endswith(".pdf") or filename.endswith(".txt")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only .pdf and .txt offer letters are accepted for forensic analysis."
        )

    # 2. File size enforcement
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of 5MB (Received {len(content) / (1024 * 1024):.2f}MB)."
        )

    if filename.endswith(".pdf"):
        # Validate PDF magic header
        if not content.startswith(b"%PDF"):
            raise HTTPException(status_code=400, detail="Corrupted or invalid PDF header structure.")
        try:
            import fitz # PyMuPDF
            doc = fitz.open(stream=content, filetype="pdf")
            extracted_text = []
            for page in doc:
                extracted_text.append(page.get_text())
            doc.close()
            return "\n".join(extracted_text)
        except Exception as e:
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(content))
                pages_text = [page.extract_text() or "" for page in reader.pages]
                return "\n".join(pages_text)
            except Exception as e2:
                raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e2)}")
    else:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")

@router.post("", response_model=AnalysisResponse)
def analyze_offer(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    analyzed_text = ""
    if file:
        analyzed_text = extract_text_from_file(file)
    elif text:
        analyzed_text = text
    else:
        raise HTTPException(status_code=400, detail="Please provide either text or a file to analyze.")

    analyzed_text = sanitize_text(analyzed_text.strip())
    if len(analyzed_text) < 15:
        raise HTTPException(status_code=400, detail="The input text is too short to perform a forensic analysis.")
    if len(analyzed_text) > MAX_TEXT_LENGTH:
        analyzed_text = analyzed_text[:MAX_TEXT_LENGTH]

    # Step 3: Extract structured entities
    extracted = ExtractionService.extract_all(analyzed_text)

    # Step 4 & 5: Detect suspicious indicators & calculate explainable risk score
    risk_score, risk_category, indicators = RiskEngine.evaluate(analyzed_text, extracted)

    # Step 6: Search extracted identifiers against fraud intelligence DB
    normalized_identifiers = []
    for p in extracted["phone_numbers"]:
        normalized_identifiers.append(p)
    for e in extracted["recruiter_emails"]:
        normalized_identifiers.append(e)
    for u in extracted["upi_ids"]:
        normalized_identifiers.append(u)
    for d in extracted["domains"]:
        normalized_identifiers.append(d)

    matched_entities = db.query(Entity).filter(
        Entity.normalized_value.in_(normalized_identifiers)
    ).all() if normalized_identifiers else []

    matched_entity_ids = [e.id for e in matched_entities]

    # Find reports linked to these entities
    matched_reports = []
    connected_suspicious_entities = []

    if matched_entity_ids:
        report_links = db.query(ReportEntity).filter(
            ReportEntity.entity_id.in_(matched_entity_ids)
        ).all()
        rep_ids = list(set([l.report_id for l in report_links]))

        reps = db.query(Report).filter(Report.id.in_(rep_ids)).all()
        for r in reps:
            matched_reports.append({
                "report_id": r.id,
                "company_name": r.company_name,
                "recruiter_name": r.recruiter_name,
                "risk_score": r.risk_score,
                "risk_category": r.risk_category,
                "report_type": r.report_type,
                "date": r.created_at.strftime("%Y-%m-%d") if r.created_at else "N/A",
                "snippet": r.description[:120] + "..." if len(r.description) > 120 else r.description
            })

        for me in matched_entities:
            # mask
            masked = me.display_value
            if me.entity_type == "phone":
                masked = mask_phone(me.display_value)
            elif me.entity_type == "email":
                masked = mask_email(me.display_value)
            elif me.entity_type == "upi":
                masked = mask_upi(me.display_value)

            connected_suspicious_entities.append({
                "entity_id": me.id,
                "entity_type": me.entity_type,
                "masked_value": masked,
                "linked_reports_count": len([l for l in report_links if l.entity_id == me.id])
            })

    # If database matches found, add extra risk points
    if matched_reports:
        risk_score = min(100.0, risk_score + 20.0)
        if risk_score >= 60.0:
            risk_category = "High Risk"
        elif risk_score >= 30.0:
            risk_category = "Medium Risk"

        indicators.append(RiskIndicator(
            code="NETWORK_MATCH",
            title=f"Shared Intelligence Match ({len(matched_reports)} Linked Reports)",
            points=20,
            description="Extracted phone/email/UPI identifier has appeared in prior recruitment fraud complaints in OfferGraph.",
            evidence_snippet=f"Matches {len(matched_reports)} prior incident reports."
        ))

    # Google Safe Browsing / Web Risk check on extracted domains
    for dom in extracted.get("domains", []):
        web_risk = AIService.check_google_web_risk(dom)
        if web_risk["status"] == "flagged":
            risk_score = min(100.0, risk_score + 15.0)
            if risk_score >= 60.0:
                risk_category = "High Risk"
            indicators.append(RiskIndicator(
                code="GOOGLE_WEB_RISK_FLAG",
                title=f"Flagged Domain Reputation ({dom})",
                points=15,
                description=f"Domain flagged for potential deceptive recruitment lure by {web_risk.get('source', 'Google Web Risk service')}.",
                evidence_snippet=f"Threat types: {', '.join(web_risk.get('threat_types', ['POTENTIALLY_HARMFUL']))}"
            ))

    # Step 8: Generate AI explanation
    ai_result = AIService.generate_offer_explanation(
        analyzed_text,
        extracted["company_name"] or "Unspecified Entity",
        risk_score,
        risk_category,
        [ind.model_dump() for ind in indicators],
        matched_reports
    )

    # Standard verification recommendations
    verification_steps = [
        "Never transfer any registration, gate-pass, or training fee prior to starting work.",
        "Check company domain credentials via official registrar (whois lookup / MCA portal).",
        "Verify recruiter's email domain (@company.com vs free webmail such as @gmail.com).",
        "Reach out via official corporate LinkedIn directory to confirm recruiter employment.",
        "Verify salary and stipend realism against industry standard averages on Glassdoor/AmbitionBox."
    ]

    # Save to AnalysisHistory
    history_record = AnalysisHistory(
        input_text=analyzed_text[:3000],
        extracted_data=json.dumps(extracted),
        risk_score=risk_score,
        risk_category=risk_category
    )
    db.add(history_record)
    db.commit()
    db.refresh(history_record)

    return AnalysisResponse(
        analysis_id=history_record.id,
        risk_score=risk_score,
        risk_category=risk_category,
        company_name=extracted["company_name"],
        extracted_entities=ExtractedEntities(**extracted),
        suspicious_indicators=indicators,
        matched_previous_reports=matched_reports,
        connected_suspicious_entities=connected_suspicious_entities,
        ai_explanation=ai_result["explanation"],
        ai_mode=ai_result["ai_mode"],
        recommended_verification_steps=verification_steps
    )

@router.get("/{analysis_id}")
def get_analysis_by_id(analysis_id: int, db: Session = Depends(get_db)):
    rec = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    extracted = json.loads(rec.extracted_data)
    _, _, indicators = RiskEngine.evaluate(rec.input_text, extracted)

    return {
        "analysis_id": rec.id,
        "input_text": rec.input_text,
        "risk_score": rec.risk_score,
        "risk_category": rec.risk_category,
        "extracted_entities": extracted,
        "suspicious_indicators": [ind.model_dump() for ind in indicators],
        "created_at": rec.created_at.strftime("%Y-%m-%d %H:%M") if rec.created_at else "N/A"
    }
