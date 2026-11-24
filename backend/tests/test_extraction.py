import pytest
from backend.app.services.extraction_service import (
    ExtractionService, normalize_phone, mask_phone,
    normalize_email, mask_email, normalize_upi, mask_upi, normalize_domain
)

class TestExtractionService:
    def test_phone_normalization_and_masking(self):
        # Indian formats
        assert normalize_phone("+91 9876543210") == "9876543210"
        assert normalize_phone("09876543210") == "9876543210"
        assert normalize_phone("98765-43210") == "9876543210"
        assert normalize_phone("+91-9123456789") == "9123456789"
        
        # Masking
        masked = mask_phone("9876543210")
        assert masked == "+91 98****3210"
        assert "98" in masked and "3210" in masked

    def test_email_normalization_and_masking(self):
        assert normalize_email("  HR.Apex@Gmail.Com  ") == "hr.apex@gmail.com"
        masked = mask_email("recruiter@apexjobs.com")
        assert "@apexjobs.com" in masked
        assert masked.startswith("re")

    def test_upi_normalization_and_masking(self):
        assert normalize_upi("ApexPay@OkHdfcBank ") == "apexpay@okhdfcbank"
        masked = mask_upi("apexpay@okhdfcbank")
        assert "@okhdfcbank" in masked
        assert masked.startswith("ap****")

    def test_domain_normalization(self):
        assert normalize_domain("https://www.apextech-careers.site/apply") == "apextech-careers.site"
        assert normalize_domain("http://cloudtech.online:8080/test") == "cloudtech.online"
        assert normalize_domain("careers-fast.top") == "careers-fast.top"

    def test_extract_all_entities_from_message(self):
        sample = """
        Congratulations! You have been selected for a Full Stack Internship at Apex Technologies.
        Contact HR Lead Mr. Vikram Malhotra at +91 9876543210 or email recruiter.apexjobs@gmail.com.
        Pay registration fee of Rs. 999 to apexpay@okhdfcbank.
        Visit our portal https://apextech-careers.site.
        Stipend is Rs. 35,000 per month.
        """
        extracted = ExtractionService.extract_all(sample)

        assert "9876543210" in extracted["phone_numbers"]
        assert "recruiter.apexjobs@gmail.com" in extracted["recruiter_emails"]
        assert "apexpay@okhdfcbank" in extracted["upi_ids"]
        assert "apextech-careers.site" in extracted["domains"]
        assert len(extracted["payment_requests"]) > 0
        assert extracted["payment_requests"][0]["amount"] == 999
        assert "Apex Technologies" in extracted["company_name"]
