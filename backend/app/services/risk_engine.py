import re
from typing import Dict, Any, List, Tuple
from ..schemas import RiskIndicator

class RiskEngine:
    """
    Explainable, rule-based risk scoring engine for job offers & recruiter messages.
    Deterministic, transparent, and provides granular evidence citations.
    """

    INDICATOR_RULES = [
        {
            "code": "PAYMENT_REQUEST",
            "title": "Registration / Application Fee Demanded",
            "points": 25,
            "patterns": [
                r'registration\s+fee',
                r'application\s+fee',
                r'pay\s+(?:₹|rs\.?|inr)?\s*[0-9]+',
                r'processing\s+fee',
                r'examination\s+fee',
                r'onboarding\s+fee',
                r'booking\s+charge'
            ],
            "description": "Legitimate employers NEVER ask candidates or interns to pay registration or processing fees."
        },
        {
            "code": "SECURITY_DEPOSIT",
            "title": "Security Deposit / Training Fee Demanded",
            "points": 25,
            "patterns": [
                r'security\s+deposit',
                r'refundable\s+deposit',
                r'laptop\s+deposit',
                r'training\s+(?:fee|charges|cost)',
                r'kit\s+charge',
                r'equipment\s+fee'
            ],
            "description": "Asking for refundable security deposits or upfront training costs is a hallmark of internship fraud."
        },
        {
            "code": "URGENT_PRESSURE",
            "title": "Urgent Payment / Deadline Pressure",
            "points": 15,
            "patterns": [
                r'within\s+(?:24|12|48|2|3)\s*hours',
                r'immediately',
                r'urgent(?:ly)?',
                r'offer\s+expires\s+today',
                r'limited\s+slots?',
                r'last\s+day\s+to\s+confirm',
                r'strictly\s+time-bound'
            ],
            "description": "Creating artificial urgency is a social engineering tactic to bypass candidate scrutiny before payment."
        },
        {
            "code": "GUARANTEED_SELECTION",
            "title": "Guaranteed Direct Selection Without Interview",
            "points": 15,
            "patterns": [
                r'direct\s+selection',
                r'without\s+any?\s+interview',
                r'no\s+interview\s+required',
                r'guaranteed\s+selection',
                r'selected\s+based\s+on\s+(?:your\s+)?profile\s+view',
                r'congratulations!.*you\s+have\s+been\s+selected'
            ],
            "description": "Reputable companies do not issue formal job/internship selections without a standard technical or HR screening."
        },
        {
            "code": "SUSPICIOUS_DOMAIN",
            "title": "Personal / Free Email Used For Official Recruitment",
            "points": 15,
            "patterns": [
                r'@(?:gmail|yahoo|hotmail|outlook|proton|rediffmail)\.com',
                r'@(?:apexjobs|quickhire|hiring-desk|careers-fast)\.(?:xyz|top|site|club|space)'
            ],
            "description": "Official corporate recruiters use company domain emails (e.g. @google.com, @infosys.com), not free webmail."
        },
        {
            "code": "OTP_PASSWORD_REQUEST",
            "title": "Request for OTP, Passwords, or Banking Credentials",
            "points": 25,
            "patterns": [
                r'\botp\b',
                r'one\s*time\s*password',
                r'net\s*banking',
                r'upi\s*pin',
                r'cvv',
                r'debit\s*card\s*number',
                r'account\s*password'
            ],
            "description": "Critical security threat: Any request for OTPs, PINs, or card CVVs indicates an active credential theft attack."
        },
        {
            "code": "SENSITIVE_PERSONAL_INFO",
            "title": "Excessive Sensitive Document Requests Upfront",
            "points": 15,
            "patterns": [
                r'aadhaar(?:\s*card)?',
                r'pan\s*card',
                r'bank\s*passbook',
                r'cheque\s*leaf',
                r'signature\s*specimen'
            ],
            "description": "Demanding government IDs and bank proofs before sending an official signed offer letter poses high identity theft risks."
        },
        {
            "code": "UNREALISTIC_COMPENSATION",
            "title": "Unrealistic Compensation For Skill / Experience Level",
            "points": 10,
            "patterns": [
                r'(?:stipend|salary).*(?:[5-9]\d{4}|[1-9]\d{5})\s*(?:pm|per\s+month)',
                r'(?:1[5-9]|2\d|3\d)\s*lpa.*fresher',
                r'earn\s+up\s+to\s+₹?[0-9,]+\s+daily',
                r'daily\s+payout'
            ],
            "description": "Excessively inflated compensation promises for basic beginner roles are commonly used as lure mechanisms."
        }
    ]

    @classmethod
    def evaluate(cls, text: str, extracted_entities: Dict[str, Any]) -> Tuple[float, str, List[RiskIndicator]]:
        indicators: List[RiskIndicator] = []
        total_points = 0
        text_lower = text.lower()

        for rule in cls.INDICATOR_RULES:
            matched = False
            snippet = None
            for pat in rule["patterns"]:
                match = re.search(pat, text, re.IGNORECASE)
                if match:
                    matched = True
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    snippet = text[start:end].strip()
                    break

            # Extra check for free email domains if not caught in regex
            if not matched and rule["code"] == "SUSPICIOUS_DOMAIN":
                for email in extracted_entities.get("recruiter_emails", []):
                    domain = email.split("@")[-1].lower()
                    if domain in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
                        matched = True
                        snippet = f"Recruiter contact email: {email}"
                        break

            # Extra check for payment requests (UPI or rupee amounts)
            if not matched and rule["code"] == "PAYMENT_REQUEST":
                if extracted_entities.get("upi_ids") or extracted_entities.get("payment_requests"):
                    matched = True
                    upi_str = ", ".join(extracted_entities.get("upi_ids", []))
                    snippet = f"Payment coordinates found: UPI: {upi_str}" if upi_str else "Payment amount requested in offer"

            if matched:
                total_points += rule["points"]
                indicators.append(RiskIndicator(
                    code=rule["code"],
                    title=rule["title"],
                    points=rule["points"],
                    description=rule["description"],
                    evidence_snippet=snippet
                ))

        # Cap score at 100
        final_score = min(100.0, float(total_points))

        # Risk categories:
        # 0–29: Low Risk
        # 30–59: Medium Risk
        # 60–100: High Risk
        if final_score < 30.0:
            category = "Low Risk"
        elif final_score < 60.0:
            category = "Medium Risk"
        else:
            category = "High Risk"

        return final_score, category, indicators
