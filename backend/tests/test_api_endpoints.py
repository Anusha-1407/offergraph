import pytest
from backend.app.database import SessionLocal, Base, engine
from backend.app.seed import seed_database
from backend.app.routers.dashboard import get_dashboard_stats, get_recent_reports
from backend.app.routers.safety import get_safety_resources
from backend.app.routers.graph import get_graph
from backend.app.routers.reports import create_report, list_reports, get_report_detail
from backend.app.routers.chat import send_chat_message
from backend.app.routers.analyze import analyze_offer
from backend.app.schemas import ReportCreate, ChatMessageRequest

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db, force_reset=False)
    yield db
    db.close()

class TestAPIEndpoints:
    def test_dashboard_stats(self, db_session):
        stats = get_dashboard_stats(db_session)
        assert stats["total_reports"] >= 8
        assert stats["connected_entities"] > 0
        assert stats["suspicious_clusters_count"] > 0
        assert "High Risk" in stats["risk_distribution"]

    def test_recent_reports(self, db_session):
        reports = get_recent_reports(5, db_session)
        assert len(reports) > 0
        assert "risk_score" in reports[0]
        assert "company_name" in reports[0]

    def test_safety_resources(self):
        safety = get_safety_resources()
        assert safety["emergency_contacts"]["helpline"] == "1930"
        assert "cybercrime.gov.in" in safety["emergency_contacts"]["portal_url"]
        assert len(safety["guides"]) >= 4

    def test_graph_elements(self, db_session):
        graph = get_graph(None, db_session)
        assert len(graph["elements"]["nodes"]) > 0
        assert len(graph["elements"]["edges"]) > 0
        assert graph["stats"]["total_nodes"] > 0

    def test_report_creation_and_graph_linkage(self, db_session):
        payload = ReportCreate(
            company_name="Apex Technologies",
            recruiter_name="Pooja Sharma",
            recruiter_email="pooja.hr@gmail.com",
            phone_number="+91 9876543210", # Reuses shared phone to link to Report 1 & 2
            upi_id="apexpay@okhdfcbank",
            job_role="Data Science Intern",
            description="Demanded ₹1200 laptop deposit fee upfront.",
            report_type="Registration fee scam"
        )
        res = create_report(payload, db_session)
        assert res["status"] == "success"
        assert res["report_id"] > 0
        assert res["risk_category"] == "High Risk"

        # Verify connected entities
        detail = get_report_detail(res["report_id"], db_session)
        assert len(detail["connected_entities"]) >= 3

    def test_chatbot_tool_execution(self, db_session):
        req = ChatMessageRequest(message="Has 9876543210 appeared in previous reports?")
        res = send_chat_message(req, db_session)
        assert len(res.tool_calls_executed) > 0
        assert any("get_connected_reports" in tc or "search_entity" in tc for tc in res.tool_calls_executed)
        assert len(res.message) > 50

    def test_analyze_offer(self, db_session):
        sample = """
        Congratulations! You have been selected for a Software Development Internship at Apex Technologies.
        Pay ₹999 as a registration fee to confirm your position via UPI to apexpay@okhdfcbank.
        WhatsApp your receipt to +91 9876543210 or email recruiter.apexjobs@gmail.com within 24 hours.
        """
        analysis = analyze_offer(text=sample, file=None, db=db_session)
        assert analysis.risk_score >= 60.0
        assert analysis.risk_category == "High Risk"
        assert len(analysis.matched_previous_reports) > 0
        assert len(analysis.suspicious_indicators) >= 2
