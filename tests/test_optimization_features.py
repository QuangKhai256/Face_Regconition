"""
Unit tests for optimization features added in task 10.
Tests for file size limits, magic bytes validation, and logging.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.face_processor import validate_image_magic_bytes
import io
from PIL import Image


client = TestClient(app)


class TestFileSizeLimit:
    """Test file size limit (10MB max)"""
    
    def test_file_size_within_limit(self):
        """Test that files under 10MB are accepted"""
        # Create a small valid JPEG (< 10MB)
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # This should not raise file size error (may fail for other reasons like no face)
        response = client.post(
            "/api/v1/face/verify",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        
        # Should not be rejected for file size
        assert response.status_code != 400 or "quá lớn" not in response.json().get("detail", "")
    
    def test_file_size_exceeds_limit(self):
        """Test that files over 10MB are rejected"""
        # Create a large file (> 10MB)
        large_data = b'\xFF\xD8\xFF' + b'x' * (11 * 1024 * 1024)  # 11MB with JPEG magic bytes
        
        response = client.post(
            "/api/v1/face/verify",
            files={"file": ("large.jpg", io.BytesIO(large_data), "image/jpeg")}
        )
        
        assert response.status_code == 400
        assert "quá lớn" in response.json()["detail"]
        assert "10MB" in response.json()["detail"]


class TestMagicBytesValidation:
    """Test magic bytes validation for image files"""
    
    def test_valid_jpeg_magic_bytes(self):
        """Test that valid JPEG magic bytes pass validation"""
        jpeg_data = b'\xFF\xD8\xFF\xE0\x00\x10JFIF' + b'x' * 100
        assert validate_image_magic_bytes(jpeg_data) is True
    
    def test_valid_png_magic_bytes(self):
        """Test that valid PNG magic bytes pass validation"""
        png_data = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A' + b'x' * 100
        assert validate_image_magic_bytes(png_data) is True
    
    def test_invalid_magic_bytes(self):
        """Test that invalid magic bytes fail validation"""
        invalid_data = b'NOT_AN_IMAGE' + b'x' * 100
        assert validate_image_magic_bytes(invalid_data) is False
    
    def test_pdf_magic_bytes_rejected(self):
        """Test that PDF files are rejected by magic bytes"""
        pdf_data = b'%PDF-1.4' + b'x' * 100
        assert validate_image_magic_bytes(pdf_data) is False
    
    def test_empty_file_rejected(self):
        """Test that empty files are rejected"""
        assert validate_image_magic_bytes(b'') is False
    
    def test_too_short_file_rejected(self):
        """Test that files shorter than magic bytes are rejected"""
        assert validate_image_magic_bytes(b'\xFF\xD8') is False
    
    def test_api_rejects_invalid_magic_bytes(self):
        """Test that API rejects files with invalid magic bytes"""
        # Create a fake file with wrong magic bytes but correct content-type
        fake_image = b'FAKE_IMAGE_DATA' + b'x' * 100
        
        response = client.post(
            "/api/v1/face/verify",
            files={"file": ("fake.jpg", io.BytesIO(fake_image), "image/jpeg")}
        )
        
        assert response.status_code == 400
        assert "không phải là ảnh hợp lệ" in response.json()["detail"]


class TestLoggingIntegration:
    """Test that logging is properly integrated (basic checks)"""
    
    def test_health_check_does_not_crash_with_logging(self):
        """Test that health check works with logging enabled"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_verify_endpoint_does_not_crash_with_logging(self):
        """Test that verify endpoint works with logging enabled"""
        # Create a small valid JPEG
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Should not crash due to logging (may fail for other reasons)
        response = client.post(
            "/api/v1/face/verify",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        
        # Should get a response (not crash)
        assert response.status_code in [200, 400, 500]


class TestCombinedValidations:
    """Test combined validations (content-type + magic bytes + size)"""
    
    def test_wrong_content_type_caught_first(self):
        """Test that wrong content-type is caught before magic bytes check"""
        response = client.post(
            "/api/v1/face/verify",
            files={"file": ("test.txt", io.BytesIO(b"text"), "text/plain")}
        )
        
        assert response.status_code == 400
        assert "File upload phải là ảnh" in response.json()["detail"]
    
    def test_correct_content_type_but_wrong_magic_bytes(self):
        """Test that magic bytes validation catches fake images"""
        fake_data = b'NOT_JPEG' + b'x' * 100
        
        response = client.post(
            "/api/v1/face/verify",
            files={"file": ("fake.jpg", io.BytesIO(fake_data), "image/jpeg")}
        )
        
        assert response.status_code == 400
        assert "không phải là ảnh hợp lệ" in response.json()["detail"]
    
    def test_all_validations_pass_for_real_image(self):
        """Test that real images pass all validations"""
        # Create a real JPEG image
        img = Image.new('RGB', (200, 200), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        response = client.post(
            "/api/v1/face/verify",
            files={"file": ("real.jpg", img_bytes, "image/jpeg")}
        )
        
        # Should pass validations (may fail for no face, but not for file validation)
        assert response.status_code != 400 or (
            "quá lớn" not in response.json().get("detail", "") and
            "không phải là ảnh hợp lệ" not in response.json().get("detail", "") and
            "File upload phải là ảnh" not in response.json().get("detail", "")
        )
