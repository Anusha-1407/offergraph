from fastapi import APIRouter
from typing import Dict, Any, List

router = APIRouter(prefix="/api/safety", tags=["Safety"])

@router.get("/resources")
def get_safety_resources() -> Dict[str, Any]:
    return {
        "disclaimer": "OfferGraph is an educational intelligence and evidence-correlation tool, not an official law-enforcement authority or legal advisory service. Always corroborate allegations independently and report fraud directly to cybercrime authorities.",
        "emergency_contacts": {
            "helpline": "1930",
            "helpline_title": "National Cybercrime Reporting Helpline (India)",
            "helpline_desc": "Dial 1930 immediately if money has been transferred within the last few hours to initiate an inter-bank freeze protocol.",
            "portal_url": "https://cybercrime.gov.in/",
            "portal_name": "National Cyber Crime Reporting Portal"
        },
        "guides": [
            {
                "id": "spot_fake_internship",
                "title": "How to Identify Fake Internships",
                "category": "Detection",
                "summary": "Key structural indicators differentiating legitimate corporate opportunities from advance-fee traps.",
                "points": [
                    "Direct selection without technical or behavioral evaluation (instant offer letter).",
                    "Demands for registration, application, documentation, or security deposit fees.",
                    "Communications originating from free email services (e.g., @gmail.com) rather than corporate email servers.",
                    "Unusually high stipends for basic entry-level or unskilled tasks.",
                    "Unverifiable company registration or virtual office addresses."
                ]
            },
            {
                "id": "verify_recruiters",
                "title": "How to Verify Recruiter Credentials",
                "category": "Verification",
                "summary": "Step-by-step checklist before signing offer documents or sharing credentials.",
                "points": [
                    "Verify the recruiter's official LinkedIn profile and check their tenure and mutual industry connections.",
                    "Check the sender email domain MX/SPF records; legitimate HR emails originate from company domains.",
                    "Search the company name on the Ministry of Corporate Affairs (MCA) portal (mca.gov.in).",
                    "Contact the company's official reception desk or main switchboard listed on their registered website.",
                    "Check Glassdoor and AmbitionBox for reviews detailing recruitment processes."
                ]
            },
            {
                "id": "why_payments_are_scams",
                "title": "Why Upfront Recruitment Fees are Always Fraudulent",
                "category": "Financial Safety",
                "summary": "Understanding the economics of legitimate corporate hiring.",
                "points": [
                    "Corporations allocate dedicated recruitment budgets; candidates are never billed for selection costs.",
                    "Legitimate training expenses are absorbed by the employer as human capital investment.",
                    "The promise of '100% refund in your first paycheque' is a standard psychological trap to disarm skepticism.",
                    "Charging candidates for employment directly violates Ministry of Labour regulations."
                ]
            },
            {
                "id": "protect_sensitive_data",
                "title": "Protecting Aadhaar, PAN, OTPs & Banking Data",
                "category": "Data Privacy",
                "summary": "Preventing identity theft and unauthorized financial exploitation.",
                "points": [
                    "Never share Aadhaar card without masking the first 8 digits (use Masked Aadhaar from UIDAI).",
                    "Never share OTPs, UPI PINs, or debit/credit card CVVs with anyone claiming to be HR.",
                    "Only submit banking details (cancelled cheque / IFSC) after signing an authenticated offer letter with a verified employer.",
                    "If KYC documents were shared with a suspected imposter, consider locking your Aadhaar biometrics via mAadhaar."
                ]
            },
            {
                "id": "post_payment_actions",
                "title": "Emergency Steps If You Have Transferred Money",
                "category": "Incident Response",
                "summary": "Immediate actions to minimize financial loss and aid cyber forensics.",
                "points": [
                    "Call 1930 within the 'Golden Hour' (first 1-2 hours) to maximize chances of freezing the scammer's bank account.",
                    "File a formal complaint on cybercrime.gov.in with transaction UTR numbers and screenshots.",
                    "Notify your bank's fraud desk immediately and lodge a chargeback / dispute request.",
                    "Do NOT pay any subsequent 'clearance fees' or 'cancellation penalties' demanded by the scammer.",
                    "Submit the scammer's identifiers (phone, email, UPI) on OfferGraph to alert fellow job seekers."
                ]
            }
        ]
    }
