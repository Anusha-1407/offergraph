import pytest
from fastapi import HTTPException, UploadFile
import io
from backend.app.routers.analyze import extract_text_from_file, sanitize_text

class TestSecurityControls:
    def test_xss_sanitization(self):
        malicious = "Hello <script>alert('XSS')</script> Apex Technologies <iframe src='evil.com'></iframe>"
        cleaned = sanitize_text(malicious)
        assert "<script>" not in cleaned
        assert "<iframe>" not in cleaned
        assert "Apex Technologies" in cleaned

    def test_null_byte_injection(self):
        malicious = "Apex Technologies\x00malicious_payload"
        cleaned = sanitize_text(malicious)
        assert "\x00" not in cleaned

    def test_unsupported_file_extension_rejection(self):
        fake_file = UploadFile(
            filename="malware.exe",
            file=io.BytesIO(b"MZ\x90\x00...")
        )
        with pytest.raises(HTTPException) as exc_info:
            extract_text_from_file(fake_file)
        assert exc_info.value.status_code == 400
        assert "Unsupported file format" in exc_info.value.detail

    def test_oversized_file_rejection(self):
        # 6MB file (exceeds 5MB limit)
        oversized_content = b"A" * (6 * 1024 * 1024)
        fake_file = UploadFile(
            filename="huge_offer.txt",
            file=io.BytesIO(oversized_content)
        )
        with pytest.raises(HTTPException) as exc_info:
            extract_text_from_file(fake_file)
        assert exc_info.value.status_code == 413
        assert "exceeds maximum allowed size" in exc_info.value.detail

    def test_corrupted_pdf_header_validation(self):
        # Not a valid PDF magic header
        corrupted = UploadFile(
            filename="fake.pdf",
            file=io.BytesIO(b"NOT_A_REAL_PDF_HEADER")
        )
        with pytest.raises(HTTPException) as exc_info:
            extract_text_from_file(corrupted)
        assert exc_info.value.status_code == 400
        assert "Corrupted or invalid PDF" in exc_info.value.detail
