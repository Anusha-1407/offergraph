import os
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("offergraph.ai")

# AI API Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
GOOGLE_SAFE_BROWSING_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()

class AIService:
    @staticmethod
    def get_active_provider() -> str:
        """Determines the active AI intelligence provider."""
        if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10 and not GEMINI_API_KEY.startswith("your_"):
            return "google-gemini"
        elif OPENAI_API_KEY and len(OPENAI_API_KEY) > 10 and not OPENAI_API_KEY.startswith("your_"):
            return "openai"
        return "deterministic-demo"

    @staticmethod
    def is_live_available() -> bool:
        return AIService.get_active_provider() in ["google-gemini", "openai"]

    @staticmethod
    def check_google_web_risk(domain: str) -> Dict[str, Any]:
        """
        Queries Google Safe Browsing / Web Risk API to check if a domain is flagged
        for Social Engineering / Phishing / Malware.
        Falls back to local heuristic detection if API key is not configured.
        """
        if not domain:
            return {"status": "clean", "threat_types": []}

        # Live Google Safe Browsing lookup if key is configured
        if GOOGLE_SAFE_BROWSING_API_KEY:
            try:
                url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_SAFE_BROWSING_API_KEY}"
                payload = {
                    "client": {"clientId": "offergraph", "clientVersion": "1.0.0"},
                    "threatInfo": {
                        "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                        "platformTypes": ["ANY_PLATFORM"],
                        "threatEntryTypes": ["URL"],
                        "threatEntries": [{"url": f"http://{domain}/"}]
                    }
                }
                with httpx.Client(timeout=4.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        matches = resp.json().get("matches", [])
                        if matches:
                            threat_types = list(set([m.get("threatType") for m in matches]))
                            return {
                                "status": "flagged",
                                "threat_types": threat_types,
                                "source": "Google Safe Browsing v4"
                            }
            except Exception as e:
                logger.warning(f"Google Safe Browsing API check failed: {e}")

        # Local heuristic reputation for suspicious TLDs & fake lookalikes
        suspicious_tlds = [".xyz", ".top", ".site", ".online", ".club", ".space", ".buzz", ".work"]
        is_suspicious_tld = any(domain.endswith(tld) for tld in suspicious_tlds)
        is_recruitment_lure = any(w in domain for w in ["career", "job", "hiring", "recruit", "desk", "verify", "offer"])

        if is_suspicious_tld and is_recruitment_lure:
            return {
                "status": "flagged",
                "threat_types": ["SUSPICIOUS_RECRUITMENT_DOMAIN"],
                "source": "OfferGraph Domain Reputation Heuristics"
            }

        return {"status": "clean", "threat_types": []}

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
        Uses Google Gemini API if GEMINI_API_KEY is configured,
        or OpenAI if OPENAI_API_KEY is configured,
        otherwise generates deterministic forensic explanation.
        """
        provider = AIService.get_active_provider()

        prompt = f"""You are the OfferGraph Forensic Cyber Analyst.
Analyze this recruitment communication:
Target Entity: {company_name}
Calculated Risk: {risk_score}/100 ({risk_category})
Detected Threat Indicators: {json.dumps(indicators)}
Database Incident Matches: {len(matched_reports)} prior incident(s) correlated

Original Communication Excerpt:
\"\"\"{text[:1500]}\"\"\"

Provide an objective forensic report in clear markdown:
### Executive Threat Summary
### Forensic Red Flags (referencing exact clauses)
### Syndicate Network Correlation
### Recommended Verification Protocol

Tone: Formal cybersecurity intelligence report. Never declare absolute guilt without qualification; highlight high-confidence risk vectors."""

        # 1. Google Gemini Provider
        if provider == "google-gemini":
            try:
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 750}
                }
                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(gemini_url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["candidates"][0]["content"]["parts"][0]["text"]
                        return {
                            "explanation": content,
                            "ai_mode": "live",
                            "model": f"Google Gemini ({GEMINI_MODEL})"
                        }
                    else:
                        logger.error(f"Gemini API returned status {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"Google Gemini generation failed: {e}")

        # 2. OpenAI Provider
        elif provider == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)
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
                    "model": f"OpenAI ({OPENAI_MODEL})"
                }
            except Exception as e:
                logger.error(f"OpenAI generation failed: {e}")

        # 3. Deterministic Forensic Demo Fallback
        return AIService._generate_deterministic_explanation(
            company_name, risk_score, risk_category, indicators, matched_reports
        )

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

        points_text = f"**Executive Threat Summary:** The analyzed communication for **{company_name or 'the stated employer'}** exhibits a calculated risk score of **{int(risk_score)}/100** categorized as **{risk_category}**.\n\n"

        flags_text = "### Forensic Red Flags Detected:\n"
        if has_payment or has_deposit:
            flags_text += "- **Monetary Demand Detected:** Legitimate employers and corporate internship programs never require registration, documentation, or equipment deposits upfront. Section 66D of the Information Technology Act and corporate hiring codes strictly prohibit onboarding charges.\n"
        if has_domain:
            flags_text += "- **Suspicious Recruiter Domain:** The sender is communicating via an unauthenticated, disposable, or free webmail service rather than an authenticated enterprise domain with valid SPF/DKIM/DMARC DNS records.\n"
        if has_urgency:
            flags_text += "- **High-Pressure Coercion:** An artificial deadline was imposed to induce rapid compliance before the candidate can independently corroborate credentials.\n"
        if not (has_payment or has_deposit or has_domain or has_urgency):
            flags_text += "- **Standard Pattern:** No severe payment coercion detected; maintain standard verification on company identity and employment contracts.\n"

        corr_text = "\n### Fraud Intelligence Correlation:\n"
        if matches_count > 0:
            corr_text += f"- **Database Match Alert:** OfferGraph cross-referenced extracted identifiers (phone number, UPI ID, or domain) and matched **{matches_count} previously reported suspicious incident(s)** in the shared intelligence repository. This provides high-confidence evidence of a recurring recruitment lure syndicate.\n"
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
