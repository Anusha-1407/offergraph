import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

class AIService:
    @staticmethod
    def is_live_available() -> bool:
        return bool(OPENAI_API_KEY and len(OPENAI_API_KEY) > 10 and not OPENAI_API_KEY.startswith("your_"))

    @staticmethod
    def generate_offer_explanation(
        text: str,
        company_name: str,
        risk_score: float,
        risk_category: str,
        indicators: List[Dict[str, Any]],
        matched_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generates an explainable risk assessment summary and safety advisory.
        Uses OpenAI GPT if key is set, otherwise generates high-fidelity deterministic mock analysis.
        """
        if AIService.is_live_available():
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)

                prompt = f"""
You are the OfferGraph AI Forensic Analyst.
Analyze the following job/internship communication:
Company: {company_name}
Risk Score: {risk_score}/100 ({risk_category})
Detected Indicators: {json.dumps(indicators)}
Prior Matching Database Incidents: {len(matched_reports)} incidents found

Original Message Text:
\"\"\"{text[:1500]}\"\"\"

Provide a professional, objective forensic breakdown in markdown:
1. Executive Risk Summary
2. Forensic Red Flags (referencing exact clauses)
3. Shared Pattern Correlation (noting database linkages)
4. Recommended Immediate Verification Steps

Rules: Maintain an objective cybersecurity analyst tone. Do not assert absolute fraud without qualification; treat indicators as critical risk flags.
"""
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a cyber fraud investigation AI specialized in recruitment scams."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=650
                )
                explanation = response.choices[0].message.content or ""
                return {
                    "explanation": explanation,
                    "ai_mode": "live",
                    "model": OPENAI_MODEL
                }
            except Exception as e:
                # Fall back gracefully with clear labelling if API call fails
                mock = AIService._generate_deterministic_explanation(company_name, risk_score, risk_category, indicators, matched_reports)
                mock["explanation"] = f"*[Note: Live OpenAI call encountered: {str(e)[:60]}... Switched to Deterministic Demo Engine]*\n\n" + mock["explanation"]
                mock["ai_mode"] = "demo"
                return mock

        # Deterministic Demo Mode
        return AIService._generate_deterministic_explanation(company_name, risk_score, risk_category, indicators, matched_reports)

    @staticmethod
    def _generate_deterministic_explanation(
        company_name: str,
        risk_score: float,
        risk_category: str,
        indicators: List[Dict[str, Any]],
        matched_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        has_payment = any("PAYMENT" in ind.get("code", "") or "FEE" in ind.get("code", "") for ind in indicators)
        has_deposit = any("DEPOSIT" in ind.get("code", "") for ind in indicators)
        has_urgency = any("URGENT" in ind.get("code", "") for ind in indicators)
        has_domain = any("DOMAIN" in ind.get("code", "") for ind in indicators)
        matches_count = len(matched_reports)

        points_text = f"**Overall Assessment:** The analyzed communication for **{company_name or 'the stated employer'}** exhibits a calculated risk score of **{int(risk_score)}/100** categorized as **{risk_category}**.\n\n"

        flags_text = "### Forensic Red Flags Detected:\n"
        if has_payment or has_deposit:
            flags_text += "- **Monetary Demand Detected:** Legitimate employers and corporate internship programs never require registration, documentation, or equipment deposits upfront. Section 66D of the IT Act and standard corporate recruitment policies strictly forbid onboarding charges.\n"
        if has_domain:
            flags_text += "- **Suspicious Recruiter Domain:** The recruiter is communicating via an unofficial, free, or disposable email service rather than an authenticated enterprise domain with valid SPF/DKIM records.\n"
        if has_urgency:
            flags_text += "- **High-Pressure Coercion:** An artificial time limit was imposed to induce rapid compliance before the candidate can independently corroborate credentials.\n"
        if not (has_payment or has_deposit or has_domain or has_urgency):
            flags_text += "- **Standard Pattern:** No severe payment coercion detected, but exercise standard vigilance regarding company registration and official contract terms.\n"

        corr_text = "\n### Fraud Intelligence Correlation:\n"
        if matches_count > 0:
            corr_text += f"- **Database Match Alert:** OfferGraph cross-referenced extracted identifiers (phone number, UPI ID, or domain) and matched **{matches_count} previously reported suspicious incident(s)** in the shared intelligence repository. This strongly indicates a recurring recruitment lure syndicate.\n"
        else:
            corr_text += "- **Zero Historical Matches:** No identical identifier has been previously flagged in this local node. However, behavioral scoring remains the primary risk indicator.\n"

        rec_text = "\n### Recommended Verification Protocol:\n"
        rec_text += "1. **Never transfer money:** Do not pay any registration, gate-pass, or laptop fee regardless of refund assurances.\n"
        rec_text += "2. **Verify via Official Channels:** Cross-check on the company's verified LinkedIn page or official careers portal (`.com` or `.in`).\n"
        rec_text += "3. **Report if pressured:** If payment is repeatedly demanded, file a cyber incident log at [cybercrime.gov.in](https://cybercrime.gov.in) or call the 1930 national cybercrime helpline."

        full_explanation = points_text + flags_text + corr_text + rec_text

        return {
            "explanation": full_explanation,
            "ai_mode": "demo",
            "model": "OfferGraph Rule & Knowledge Engine (Deterministic Fallback)"
        }
