"""
Property-based tests for file validation
Tests universal properties for content-type, file size, and magic bytes validation
"""

import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
import io

from backend.main import app

client = TestClient(app)


# ============================================================================
# Property 15: Content-type validation
# Feature: face-recognition-complete, Property 15: Content-type validation
# Validates: Requirements 4.1
# ============================================================================

@given(
    content_type=st.sampled_from([
        "text/plain",
        "text/html",
        "application/json",
        "application/pdf",
        "application/xml",
        "video/mp4",
        "video/mpeg",
        "audio/mpeg",
        "audio/wav",
        "application/octet-stream",
        "text/csv",
        "application/zip",
        "image/gif",  # Not supported
        "image/bmp",  # Not supported
        "image/webp",  # Not supported
        "image/svg+xml",  # Not supported
    ])
)
@settings(max_examples=100)
def test_property_content_type_validation(content_type):
    """
    Property 15: Content-type validation
    For any file upload to collect or verify endpoints, 
    if content-type is not in {image/jpeg, image/jpg, image/png}, 
    the endpoint should return HTTP 400.
    
    Validates: Requirements 4.1
    """
    # Create dummy file data
    file_data = b"dummy file content"
    
    # Create files dict with custom content type
    files = {
        "file": ("test.file", io.BytesIO(file_data), content_type)
    }
    
    # Test verify endpoint
    response = client.post("/api/v1/face/verify", files=files)
    
    # Assert HTTP 400 for invalid content types
    assert response.status_code == 400, f"Expected 400 for content-type {content_type}, got {response.status_code}"
    assert "detail" in response.json()
    detail = response.json()["detail"].lower()
    # Check that error message mentions image or file format
    assert any(keyword in detail for keyword in ["ảnh", "jpg", "jpeg", "png", "file", "upload"])


# ============================================================================
# Property 16: File size validation
# Feature: face-recognition-complete, Property 16: File size validation
# Validates: Requirements 4.3
# ============================================================================

@given(
    # Generate file sizes larger than 10MB
    file_size=st.integers(min_value=10*1024*1024 + 1, max_value=20*1024*1024)
)
@settings(max_examples=100, deadline=None)
def test_property_file_size_validation(file_size):
    """
    Property 16: File size validation
    For any file upload with size > 10MB (10485760 bytes), 
    the endpoint should return HTTP 400 with appropriate error message.
    
    Validates: Requirements 4.3
    """
    # Create file data of specified size
    file_data = b"x" * file_size
    
    # Create files dict with valid content type but oversized file
    files = {
        "file": ("test.jpg", io.BytesIO(file_data), "image/jpeg")
    }
    
    # Test verify endpoint
    response = client.post("/api/v1/face/verify", files=files)
    
    # Assert HTTP 400 for oversized files
    assert response.status_code == 400, f"Expected 400 for file size {file_size}, got {response.status_code}"
    assert "detail" in response.json()
    detail = response.json()["detail"].lower()
    # Check that error message mentions file size or "quá lớn" (too large)
    assert any(keyword in detail for keyword in ["lớn", "size", "10mb", "kích thước"])


# ============================================================================
# Property 17: Magic bytes validation
# Feature: face-recognition-complete, Property 17: Magic bytes validation
# Validates: Requirements 4.5
# ============================================================================

@given(
    # Generate random bytes that don't match JPEG or PNG magic bytes
    file_data=st.binary(min_size=100, max_size=1000).filter(
        lambda data: not (
            data.startswith(b'\xFF\xD8\xFF') or  # JPEG
            data.startswith(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A')  # PNG
        )
    )
)
@settings(max_examples=100, deadline=None)
def test_property_magic_bytes_validation(file_data):
    """
    Property 17: Magic bytes validation
    For any file upload, if the file's magic bytes do not match 
    JPEG (0xFF 0xD8 0xFF) or PNG (0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A) signatures, 
    the endpoint should return HTTP 400.
    
    Validates: Requirements 4.5
    """
    # Create files dict with valid content type but invalid magic bytes
    files = {
        "file": ("test.jpg", io.BytesIO(file_data), "image/jpeg")
    }
    
    # Test verify endpoint
    response = client.post("/api/v1/face/verify", files=files)
    
    # Assert HTTP 400 for invalid magic bytes
    assert response.status_code == 400, f"Expected 400 for invalid magic bytes, got {response.status_code}"
    assert "detail" in response.json()
    detail = response.json()["detail"].lower()
    # Check that error message mentions invalid image or magic bytes
    assert any(keyword in detail for keyword in ["hợp lệ", "valid", "ảnh", "image", "file"])
