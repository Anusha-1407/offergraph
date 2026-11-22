from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional, Dict, Any

from ..database import get_db
from ..models import Report, Entity, ReportEntity
from ..schemas import ReportCreate, ReportResponse
from ..services.extraction_service import (
    normalize_phone, normalize_email, normalize_domain, normalize_upi,
    mask_phone, mask_email, mask_upi, ExtractionService
)
from ..services.risk_engine import RiskEngine

router = APIRouter(prefix="/api/reports", tags=["Reports"])

def get_or_create_entity(
    db: Session,
    entity_type: str,
    raw_value: str,
    normalized_value: str
) -> Entity:
    entity = db.query(Entity).filter(
        Entity.entity_type == entity_type,
        Entity.normalized_value == normalized_value
    ).first()

    if not entity:
        entity = Entity(
            entity_type=entity_type,
            normalized_value=normalized_value,
            display_value=raw_value
        )
        db.add(entity)
        db.flush()

    return entity

@router.post("", response_model=Dict[str, Any])
def create_report(payload: ReportCreate, db: Session = Depends(get_db)):
    if not payload.description or len(payload.description.strip()) < 10:
        raise HTTPException(status_code=400, detail="Please provide a descriptive explanation of the incident.")

    # Calculate initial risk score
    extracted = ExtractionService.extract_all(payload.description)
    if payload.phone_number:
        extracted["phone_numbers"].append(normalize_phone(payload.phone_number))
    if payload.recruiter_email:
        extracted["recruiter_emails"].append(normalize_email(payload.recruiter_email))
    if payload.upi_id:
        extracted["upi_ids"].append(normalize_upi(payload.upi_id))
    if payload.website:
        extracted["domains"].append(normalize_domain(payload.website))

    risk_score, risk_category, _ = RiskEngine.evaluate(payload.description, extracted)

    # If user selected specific high-risk category
    if payload.report_type in ["Registration fee scam", "Data theft attempt", "Training fee scam"]:
        risk_score = max(risk_score, 65.0)
        risk_category = "High Risk"

    new_report = Report(
        company_name=payload.company_name.strip() if payload.company_name else "Unknown Company",
        recruiter_name=payload.recruiter_name.strip() if payload.recruiter_name else "Unspecified Recruiter",
        description=payload.description.strip(),
        job_role=payload.job_role.strip() if payload.job_role else "Unspecified Role",
        risk_score=risk_score,
        risk_category=risk_category,
        report_type=payload.report_type,
        verification_status="Unverified Submission"
    )
    db.add(new_report)
    db.flush()

    # Link / create company entity
    if payload.company_name:
        c_entity = get_or_create_entity(
            db, "company", payload.company_name.strip(), payload.company_name.strip().lower()
        )
        db.add(ReportEntity(report_id=new_report.id, entity_id=c_entity.id, relationship_type="MENTIONS_COMPANY"))

    # Link / create recruiter entity
    if payload.recruiter_name:
        r_entity = get_or_create_entity(
            db, "recruiter", payload.recruiter_name.strip(), payload.recruiter_name.strip().lower()
        )
        db.add(ReportEntity(report_id=new_report.id, entity_id=r_entity.id, relationship_type="REPRESENTS_RECRUITER"))

    # Link / create phone entity
    if payload.phone_number:
        norm_p = normalize_phone(payload.phone_number)
        p_entity = get_or_create_entity(db, "phone", payload.phone_number.strip(), norm_p)
        db.add(ReportEntity(report_id=new_report.id, entity_id=p_entity.id, relationship_type="USES_PHONE"))

    # Link / create email entity
    if payload.recruiter_email:
        norm_e = normalize_email(payload.recruiter_email)
        e_entity = get_or_create_entity(db, "email", payload.recruiter_email.strip(), norm_e)
        db.add(ReportEntity(report_id=new_report.id, entity_id=e_entity.id, relationship_type="CONTAINS_EMAIL"))

    # Link / create website/domain entity
    if payload.website:
        norm_d = normalize_domain(payload.website)
        d_entity = get_or_create_entity(db, "domain", payload.website.strip(), norm_d)
        db.add(ReportEntity(report_id=new_report.id, entity_id=d_entity.id, relationship_type="MENTIONS_DOMAIN"))

    # Link / create UPI entity
    if payload.upi_id:
        norm_u = normalize_upi(payload.upi_id)
        u_entity = get_or_create_entity(db, "upi", payload.upi_id.strip(), norm_u)
        db.add(ReportEntity(report_id=new_report.id, entity_id=u_entity.id, relationship_type="CONTAINS_UPI"))

    db.commit()
    db.refresh(new_report)

    return {
        "status": "success",
        "report_id": new_report.id,
        "company_name": new_report.company_name,
        "risk_score": new_report.risk_score,
        "risk_category": new_report.risk_category,
        "verification_status": new_report.verification_status,
        "message": f"Incident Report #{new_report.id} registered into OfferGraph Intelligence database successfully."
    }

@router.get("")
def list_reports(
    risk_category: Optional[str] = Query(None),
    report_type: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Report)

    if risk_category and risk_category != "All":
        query = query.filter(Report.risk_category == risk_category)

    if report_type and report_type != "All":
        query = query.filter(Report.report_type == report_type)

    if q:
        query = query.filter(
            or_(
                Report.company_name.ilike(f"%{q}%"),
                Report.recruiter_name.ilike(f"%{q}%"),
                Report.description.ilike(f"%{q}%"),
                Report.job_role.ilike(f"%{q}%")
            )
        )

    total_count = query.count()
    reports = query.order_by(desc(Report.created_at)).offset(offset).limit(limit).all()

    results = []
    for r in reports:
        # Connected entities count
        ent_count = db.query(ReportEntity).filter(ReportEntity.report_id == r.id).count()
        results.append({
            "id": r.id,
            "company_name": r.company_name or "Unspecified Entity",
            "recruiter_name": r.recruiter_name or "Not Specified",
            "job_role": r.job_role or "Internship",
            "description": r.description,
            "risk_score": r.risk_score,
            "risk_category": r.risk_category,
            "report_type": r.report_type,
            "verification_status": r.verification_status,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "N/A",
            "connected_entities_count": ent_count
        })

    return {
        "total": total_count,
        "reports": results
    }

@router.get("/{report_id}")
def get_report_detail(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Fetch connected entities
    links = db.query(ReportEntity).filter(ReportEntity.report_id == report_id).all()
    entities = []
    for l in links:
        e = db.query(Entity).filter(Entity.id == l.entity_id).first()
        if e:
            masked = e.display_value
            if e.entity_type == "phone":
                masked = mask_phone(e.display_value)
            elif e.entity_type == "email":
                masked = mask_email(e.display_value)
            elif e.entity_type == "upi":
                masked = mask_upi(e.display_value)

            entities.append({
                "entity_id": e.id,
                "entity_type": e.entity_type,
                "display_value": masked,
                "relationship": l.relationship_type
            })

    return {
        "id": report.id,
        "company_name": report.company_name,
        "recruiter_name": report.recruiter_name,
        "job_role": report.job_role,
        "description": report.description,
        "risk_score": report.risk_score,
        "risk_category": report.risk_category,
        "report_type": report.report_type,
        "verification_status": report.verification_status,
        "created_at": report.created_at.strftime("%Y-%m-%d %H:%M") if report.created_at else "N/A",
        "connected_entities": entities
    }
