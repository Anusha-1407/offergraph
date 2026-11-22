import datetime
from sqlalchemy.orm import Session
from .models import User, Report, Entity, ReportEntity, AnalysisHistory
from .services.extraction_service import (
    normalize_phone, normalize_email, normalize_domain, normalize_upi
)
from .database import engine, Base, SessionLocal

def seed_database(db: Session, force_reset: bool = False):
    """
    Populates synthetic demonstration data for hackathon presentation.
    All data is clearly labelled: SYNTHETIC DEMONSTRATION DATA — NOT REAL COMPLAINTS.
    """
    # Create tables if they do not exist
    Base.metadata.create_all(bind=engine)

    if force_reset:
        db.query(ReportEntity).delete()
        db.query(Entity).delete()
        db.query(Report).delete()
        db.query(AnalysisHistory).delete()
        db.query(User).delete()
        db.commit()
    elif db.query(Report).count() > 0:
        return # Already seeded

    # Seed Default User
    demo_user = User(
        name="Security Investigator",
        email="analyst@offergraph.internal",
        created_at=datetime.datetime.utcnow()
    )
    db.add(demo_user)
    db.commit()

    # Synthetic Companies (Fictional demonstration entities)
    companies = {
        "Apex Technologies": "apex technologies",
        "Nexis Cloud Solutions": "nexis cloud solutions",
        "Zenith Data Systems": "zenith data systems",
        "Global Cyber Infotech": "global cyber infotech",
        "FastTrack Hire Pvt Ltd": "fasttrack hire pvt ltd"
    }

    # Synthetic Recruiters (Fictional names)
    recruiters = {
        "Vikram Malhotra": "vikram malhotra",
        "Pooja Sharma": "pooja sharma",
        "Amit Verma": "amit verma",
        "Neha Kapoor": "neha kapoor",
        "Suresh Nair": "suresh nair"
    }

    # Synthetic Shared Identifiers
    phones = {
        "9876543210": normalize_phone("9876543210"), # Shared between Report 1 & 2
        "9123456789": normalize_phone("9123456789"), # Shared between Report 4 & 8
        "9988776655": normalize_phone("9988776655"), # Report 3
        "9711223344": normalize_phone("9711223344"), # Report 5 & 6
        "9822334455": normalize_phone("9822334455"), # Report 7
        "9633221100": normalize_phone("9633221100")  # Report 8
    }

    emails = {
        "recruiter.apexjobs@gmail.com": normalize_email("recruiter.apexjobs@gmail.com"), # Shared between Report 2 & 3
        "onboarding@cloudtech-careers.online": normalize_email("onboarding@cloudtech-careers.online"), # Report 5 & 6
        "hr.apextech@yahoo.com": normalize_email("hr.apextech@yahoo.com"), # Report 1
        "careers@nexishire.tech": normalize_email("careers@nexishire.tech") # Report 4
    }

    domains = {
        "cloudtech-careers.online": normalize_domain("cloudtech-careers.online"), # Shared between Report 5 & 6
        "apextech-careers.site": normalize_domain("apextech-careers.site"),       # Shared between Report 1 & 2
        "zenithdata-hiring.xyz": normalize_domain("zenithdata-hiring.xyz")        # Report 7
    }

    upis = {
        "apexpay@okhdfcbank": normalize_upi("apexpay@okhdfcbank"), # Shared between Report 1 & 4
        "hiredesk@ybl": normalize_upi("hiredesk@ybl"),             # Shared between Report 3 & 7
        "cloudonboard@paytm": normalize_upi("cloudonboard@paytm")  # Shared between Report 5 & 6
    }

    # Helper function to get or create Entity
    entity_cache = {}
    def get_or_create(etype: str, display: str, norm: str) -> Entity:
        key = (etype, norm)
        if key in entity_cache:
            return entity_cache[key]
        e = db.query(Entity).filter(Entity.entity_type == etype, Entity.normalized_value == norm).first()
        if not e:
            e = Entity(entity_type=etype, display_value=display, normalized_value=norm)
            db.add(e)
            db.flush()
        entity_cache[key] = e
        return e

    # Synthetic Incident Reports
    # Mark all clearly: SYNTHETIC DEMONSTRATION DATA — NOT REAL COMPLAINTS
    reports_data = [
        {
            "company": "Apex Technologies",
            "recruiter": "Vikram Malhotra",
            "role": "Software Engineering Intern",
            "score": 85.0,
            "category": "High Risk",
            "type": "Registration fee scam",
            "desc": "[SYNTHETIC DEMONSTRATION DATA — NOT REAL COMPLAINTS] Candidate received an unsolicited offer letter demanding a mandatory ₹999 registration fee via UPI to apexpay@okhdfcbank before joining. Recruiter contacted via +91 9876543210 and hr.apextech@yahoo.com.",
            "entities": [
                ("company", "Apex Technologies", companies["Apex Technologies"], "MENTIONS_COMPANY"),
                ("recruiter", "Vikram Malhotra", recruiters["Vikram Malhotra"], "REPRESENTS_RECRUITER"),
                ("phone", "+91 98765 43210", phones["9876543210"], "USES_PHONE"),
                ("email", "hr.apextech@yahoo.com", emails["hr.apextech@yahoo.com"], "CONTAINS_EMAIL"),
                ("domain", "apextech-careers.site", domains["apextech-careers.site"], "MENTIONS_DOMAIN"),
                ("upi", "apexpay@okhdfcbank", upis["apexpay@okhdfcbank"], "CONTAINS_UPI")
            ]
        },
        {
            "company": "Apex Technologies",
            "recruiter": "Pooja Sharma",
            "role": "Frontend Developer Intern",
            "score": 75.0,
            "category": "High Risk",
            "type": "Security deposit request",
            "desc": "[SYNTHETIC DEMONSTRATION DATA — NOT REAL COMPLAINTS] Selected without technical round. Required ₹1,500 'refundable laptop asset insurance' within 24 hours. The recruiter used the same WhatsApp number (+91 9876543210) as Report #1, but contacted from recruiter.apexjobs@gmail.com.",
            "entities": [
                ("company", "Apex Technologies", companies["Apex Technologies"], "MENTIONS_COMPANY"),
                ("recruiter", "Pooja Sharma", recruiters["Pooja Sharma"], "REPRESENTS_RECRUITER"),
                ("phone", "+91 98765 43210", phones["9876543210"], "USES_PHONE"), # Shared with Report 1
                ("email", "recruiter.apexjobs@gmail.com", emails["recruiter.apexjobs@gmail.com"], "CONTAINS_EMAIL"), # Shared with Report 3
                ("domain", "apextech-careers.site", domains["apextech-careers.site"], "MENTIONS_DOMAIN") # Shared with Report 1
            ]
        },
        {
            "company": "Zenith Data Systems",
            "recruiter": "Pooja Sharma",
            "role": "Data Analyst Intern",
            "score": 70.0,
            "category": "High Risk",
            "type": "Training fee scam",
            "desc": "[SYNTHETIC DEMONSTRATION DATA — NOT REAL COMPLAINTS] Offered ₹45,000/month stipend for fresher. Demanded ₹2,500 training kit fee paid to UPI wired to hiredesk@ybl. Communicated from recruiter.apexjobs@gmail.com and +91 9988776655.",
            "entities": [
                ("company", "Zenith Data Systems", companies["Zenith Data Systems"], "MENTIONS_COMPANY"),
                ("recruiter", "Pooja Sharma", recruiters["Pooja Sharma"], "REPRESENTS_RECRUITER"),
                ("phone", "+91 99887 76655", phones["9988776655"], "USES_PHONE"),
                ("email", "recruiter.apexjobs@gmail.com", emails["recruiter.apexjobs@gmail.com"], "CONTAINS_EMAIL"), # Shared with Report 2
                ("upi", "hiredesk@ybl", upis["hiredesk@ybl"], "CONTAINS_UPI") # Shared with Report 7
            ]
        },
        {
            "company": "Nexis Cloud Solutions",
            "recruiter": "Amit Verma",
            "role": "Cloud DevOps Intern",
            "score": 80.0,
            "category": "High Risk",
            "type": "Registration fee scam",
            "desc": "[SYNTHETIC DEMONSTRATION DATA — NOT REAL COMPLAINTS] Impersonating cloud consultant. Demanded ₹1,200 server provisioning fee paid to apexpay@okhdfcbank (identical payment destination as Apex Technologies in Report #1). Contact phone: +91 9123456789.",
            "entities": [
                ("company", "Nexis Cloud Solutions", companies["Nexis Cloud Solutions"], "MENTIONS_COMPANY"),
                ("recruiter", "Amit Verma", recruiters["Amit Verma"], "REPRESENTS_RECRUITER"),
                ("phone", "+91 91234 56789", phones["9123456789"], "USES_PHONE"), # Shared with Report 8
                ("email", "careers@nexishire.tech", emails["careers@nexishire.tech"], "CONTAINS_EMAIL"),
                ("upi", "apexpay@okhdfcbank", upis["apexpay@okhdfcbank"], "CONTAINS_UPI") # Shared with Report 1
            ]
        },
        {
            "company": "Global Cyber Infotech",
            "recruiter": "Neha Kapoor",
            "role": "Cybersecurity Analyst Intern",
            "score": 90.0,
            "category": "High Risk",
            "type": "Data theft attempt",
            "desc": "[SYNTHETIC DEMONSTRATION DATA — NOT REAL COMPLAINTS] Required applicant to upload unmasked Aadhaar, PAN card, and bank passbook to suspicious web portal cloudtech-careers.online before any interview. Fee of ₹499 demanded for 'background check' to cloudonboard@paytm. Recruiter phone: +91 9711223344.",
            "entities": [
                ("company", "Global Cyber Infotech", companies["Global Cyber Infotech"], "MENTIONS_COMPANY"),
                ("recruiter", "Neha Kapoor", recruiters["Neha Kapoor"], "REPRESENTS_RECRUITER"),
                ("phone", "+91 97112 23344", phones["9711223344"], "USES_PHONE"), # Shared with Report 6
                ("domain", "cloudtech-careers.online", domains["cloudtech-careers.online"], "MENTIONS_DOMAIN"), # Shared with Report 6
                ("upi", "cloudonboard@paytm", upis["cloudonboard@paytm"], "CONTAINS_UPI"), # Shared with Report 6
                ("email", "onboarding@cloudtech-careers.online", emails["onboarding@cloudtech-careers.online"], "CONTAINS_EMAIL")
            ]
        },
        {
            "company": "FastTrack Hire Pvt Ltd",
            "recruiter": "Neha Kapoor",
            "role": "Full Stack Intern",
            "score": 85.0,
            "category": "High Risk",
            "type": "Training fee scam",
            "desc": "[SYNTHETIC DEMONSTRATION DATA — NOT REAL COMPLAINTS] Same infrastructure as Global Cyber Infotech. Host site cloudtech-careers.online, phone +91 9711223344, and UPI destination cloudonboard@paytm. Demanded ₹1,800 mandatory induction fee.",
            "entities": [
                ("company", "FastTrack Hire Pvt Ltd", companies["FastTrack Hire Pvt Ltd"], "MENTIONS_COMPANY"),
                ("recruiter", "Neha Kapoor", recruiters["Neha Kapoor"], "REPRESENTS_RECRUITER"),
                ("phone", "+91 97112 23344", phones["9711223344"], "USES_PHONE"), # Shared with Report 5
                ("domain", "cloudtech-careers.online", domains["cloudtech-careers.online"], "MENTIONS_DOMAIN"), # Shared with Report 5
                ("upi", "cloudonboard@paytm", upis["cloudonboard@paytm"], "CONTAINS_UPI") # Shared with Report 5
            ]
        },
        {
            "company": "Zenith Data Systems",
            "recruiter": "Suresh Nair",
            "role": "AI Research Trainee",
            "score": 75.0,
            "category": "High Risk",
            "type": "Registration fee scam",
            "desc": "[SYNTHETIC DEMONSTRATION DATA — NOT REAL COMPLAINTS] False claims of partnership with premier institutes. Demanded ₹950 assessment fee paid to hiredesk@ybl (shared payment recipient with Report #3). Domain: zenithdata-hiring.xyz, Phone: +91 9822334455.",
            "entities": [
                ("company", "Zenith Data Systems", companies["Zenith Data Systems"], "MENTIONS_COMPANY"),
                ("recruiter", "Suresh Nair", recruiters["Suresh Nair"], "REPRESENTS_RECRUITER"),
                ("phone", "+91 98223 34455", phones["9822334455"], "USES_PHONE"),
                ("domain", "zenithdata-hiring.xyz", domains["zenithdata-hiring.xyz"], "MENTIONS_DOMAIN"),
                ("upi", "hiredesk@ybl", upis["hiredesk@ybl"], "CONTAINS_UPI") # Shared with Report 3
            ]
        },
        {
            "company": "Nexis Cloud Solutions",
            "recruiter": "Amit Verma",
            "role": "Python Backend Intern",
            "score": 65.0,
            "category": "High Risk",
            "type": "Security deposit request",
            "desc": "[SYNTHETIC DEMONSTRATION DATA — NOT REAL COMPLAINTS] Demanded ₹800 badge printing and security clearance fee within 12 hours. Shared recruiter phone +91 9123456789 with Report #4. Alternate number +91 9633221100 provided.",
            "entities": [
                ("company", "Nexis Cloud Solutions", companies["Nexis Cloud Solutions"], "MENTIONS_COMPANY"),
                ("recruiter", "Amit Verma", recruiters["Amit Verma"], "REPRESENTS_RECRUITER"),
                ("phone", "+91 91234 56789", phones["9123456789"], "USES_PHONE"), # Shared with Report 4
                ("phone", "+91 96332 21100", phones["9633221100"], "USES_PHONE")
            ]
        }
    ]

    # Insert Reports and Link Entities
    base_time = datetime.datetime.utcnow() - datetime.timedelta(days=14)
    for idx, rep in enumerate(reports_data):
        created_time = base_time + datetime.timedelta(days=idx, hours=idx * 2)
        r = Report(
            company_name=rep["company"],
            recruiter_name=rep["recruiter"],
            description=rep["desc"],
            job_role=rep["role"],
            risk_score=rep["score"],
            risk_category=rep["category"],
            report_type=rep["type"],
            verification_status="Community Corroborated" if idx < 4 else "Unverified Submission",
            created_at=created_time
        )
        db.add(r)
        db.flush()

        for etype, display, norm, rel in rep["entities"]:
            ent = get_or_create(etype, display, norm)
            # check duplicate edge
            existing_rel = db.query(ReportEntity).filter(
                ReportEntity.report_id == r.id,
                ReportEntity.entity_id == ent.id,
                ReportEntity.relationship_type == rel
            ).first()
            if not existing_rel:
                db.add(ReportEntity(report_id=r.id, entity_id=ent.id, relationship_type=rel))

    db.commit()
    print("Database seeded with synthetic demonstration data successfully.")

if __name__ == "__main__":
    db = SessionLocal()
    seed_database(db, force_reset=True)
    db.close()
