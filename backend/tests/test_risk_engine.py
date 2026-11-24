import pytest
from backend.app.services.risk_engine import RiskEngine
from backend.app.services.extraction_service import ExtractionService

class TestRiskEngine:
    def test_benign_message_scoring(self):
        text = "Hello, we would like to invite you for a 45-minute technical interview on Google Meet next Tuesday. Please let us know your availability."
        extracted = ExtractionService.extract_all(text)
        score, category, indicators = RiskEngine.evaluate(text, extracted)

        assert score < 30.0
        assert category == "Low Risk"
        assert len(indicators) == 0

    def test_high_risk_scam_message_scoring(self):
        text = """
        Congratulations! You have direct selection without any interview.
        Pay ₹999 registration fee immediately within 24 hours.
        Contact hr@gmail.com and share your Aadhaar card and PAN card.
        """
        extracted = ExtractionService.extract_all(text)
        score, category, indicators = RiskEngine.evaluate(text, extracted)

        assert score >= 60.0
        assert category == "High Risk"
        codes = [ind.code for ind in indicators]
        assert "PAYMENT_REQUEST" in codes
        assert "GUARANTEED_SELECTION" in codes
        assert "URGENT_PRESSURE" in codes

    def test_score_capped_at_100(self):
        # Accumulate many high points
        text = """
        Pay ₹999 registration fee. Refundable security deposit of ₹5000 required.
        Urgent deadline expires within 24 hours! Direct selection without any interview!
        Send OTP and password immediately. Upload Aadhaar card and PAN card.
        Contact hr.recruiter@gmail.com. Guaranteed ₹80,000 pm stipend for fresher!
        """
        extracted = ExtractionService.extract_all(text)
        score, category, indicators = RiskEngine.evaluate(text, extracted)

        assert score == 100.0 # Capped at 100
        assert category == "High Risk"
        assert len(indicators) >= 5
