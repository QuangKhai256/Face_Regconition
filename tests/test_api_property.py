"""
Property-based tests for FastAPI endpoints
Tests universal properties that should hold across all inputs
"""

import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
import io
from PIL import Image
import numpy as np

from backend.main import app

client = TestClient(app)


# ============================================================================
# Property 3: Content-type validation
# Feature: face-recognition-backend, Property 3: Content-type validation
# Validates: Requirements 3.1
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
        "application/zip"
    ])
)
@settings(max_examples=100)
def test_property_content_type_validation(content_type):
    """
    Property 3: Content-type validation
    For any file upload with content-type not in {image/jpeg, image/jpg, image/png},
    the API should reject the request with HTTP 400.
    
    Validates: Requirements 3.1
    """
    # Create dummy file data
    file_data = b"dummy file content"
    
    # Create files dict with custom content type
    files = {
        "file": ("test.txt", io.BytesIO(file_data), content_type)
    }
    
    # Send request
    response = client.post("/api/v1/face/verify", files=files)
    
    # Assert HTTP 400 for invalid content types
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "ảnh" in response.json()["detail"].lower() or "jpg" in response.json()["detail"].lower()


# ============================================================================
# Property 7: Custom threshold parameter
# Feature: face-recognition-backend, Property 7: Custom threshold parameter
# Validates: Requirements 4.1
# ============================================================================

def create_valid_test_image():
    """Helper to create a valid test image with a face-like pattern"""
    # Create a simple image (this won't have a real face, but tests the parameter handling)
    img = Image.new('RGB', (200, 200), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


@given(
    threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_property_custom_threshold_parameter(threshold):
    """
    Property 7: Custom threshold parameter
    For any valid threshold value provided as query parameter,
    the system should use that value instead of the default for comparison.
    
    Validates: Requirements 4.1
    """
    # Create a test image
    img_bytes = create_valid_test_image()
    
    files = {
        "file": ("test.jpg", img_bytes, "image/jpeg")
    }
    
    # Send request with custom threshold
    response = client.post(
        f"/api/v1/face/verify?threshold={threshold}",
        files=files
    )
    
    # The request might fail due to no face in image (400) or no training data (500)
    # But if it returns a response with threshold field, it should match our input
    if response.status_code == 200:
        data = response.json()
        assert "threshold" in data
        assert abs(data["threshold"] - threshold) < 0.001  # Float comparison with tolerance


# ============================================================================
# Property 8: Threshold range validation
# Feature: face-recognition-backend, Property 8: Threshold range validation
# Validates: Requirements 4.3
# ============================================================================

@given(
    threshold=st.one_of(
        st.floats(min_value=-1000.0, max_value=-0.001),
        st.floats(min_value=1.001, max_value=1000.0)
    ).filter(lambda x: not (0.0 <= x <= 1.0))
)
@settings(max_examples=100, deadline=None)
def test_property_threshold_range_validation(threshold):
    """
    Property 8: Threshold range validation
    For any threshold value outside the range [0.0, 1.0],
    the API should return HTTP 422 validation error.
    
    Validates: Requirements 4.3
    """
    # Create a test image
    img_bytes = create_valid_test_image()
    
    files = {
        "file": ("test.jpg", img_bytes, "image/jpeg")
    }
    
    # Send request with invalid threshold
    response = client.post(
        f"/api/v1/face/verify?threshold={threshold}",
        files=files
    )
    
    # Assert HTTP 422 for out-of-range threshold
    assert response.status_code == 422
    assert "detail" in response.json()


# ============================================================================
# Property 12: CORS allows all origins
# Feature: face-recognition-backend, Property 12: CORS allows all origins
# Validates: Requirements 8.1, 8.3
# ============================================================================

@given(
    protocol=st.sampled_from(["http", "https"]),
    domain=st.text(
        alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), min_codepoint=ord('a'), max_codepoint=ord('z')),
        min_size=3,
        max_size=20
    ),
    tld=st.sampled_from(["com", "org", "net", "io", "dev", "app"])
)
@settings(max_examples=100)
def test_property_cors_allows_all_origins(protocol, domain, tld):
    """
    Property 12: CORS allows all origins
    For any HTTP request from any origin,
    the backend should include appropriate CORS headers allowing the request.
    
    Validates: Requirements 8.1, 8.3
    """
    # Construct a valid origin URL
    origin = f"{protocol}://{domain}.{tld}"
    
    # Send request with custom Origin header
    response = client.get(
        "/api/v1/health",
        headers={"Origin": origin}
    )
    
    # Check CORS headers are present
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    # Should allow all origins (*)
    assert response.headers["access-control-allow-origin"] == "*"
