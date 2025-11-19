"""
Unit tests for FastAPI endpoints
Tests specific examples and edge cases for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import io
from PIL import Image, ImageDraw

from backend.main import app

client = TestClient(app)


def create_simple_image(format='JPEG'):
    """Helper to create a simple test image"""
    img = Image.new('RGB', (200, 200), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=format)
    img_bytes.seek(0)
    return img_bytes


def create_face_like_image():
    """Create a simple image with a face-like pattern"""
    img = Image.new('RGB', (400, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple face-like oval
    draw.ellipse([100, 80, 300, 320], fill=(255, 220, 177), outline=(0, 0, 0))
    draw.ellipse([140, 150, 180, 190], fill=(50, 50, 50))  # Left eye
    draw.ellipse([220, 150, 260, 190], fill=(50, 50, 50))  # Right eye
    draw.ellipse([185, 200, 215, 240], fill=(200, 180, 160))  # Nose
    draw.arc([150, 240, 250, 290], start=0, end=180, fill=(100, 50, 50), width=3)  # Mouth
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


# ============================================================================
# Health Check Endpoint Tests
# Validates: Requirements 2.1
# ============================================================================

def test_health_check_returns_correct_format():
    """
    Test health check endpoint trả về đúng format.
    Validates: Requirements 2.1
    """
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_health_check_response_time():
    """
    Test health check phản hồi nhanh.
    Validates: Requirements 2.2
    """
    import time
    start = time.time()
    response = client.get("/api/v1/health")
    elapsed = time.time() - start
    
    assert response.status_code == 200
    # Should respond within 1 second (very generous for unit test)
    assert elapsed < 1.0


# ============================================================================
# Verify Endpoint - Content Type Tests
# Validates: Requirements 3.1
# ============================================================================

def test_verify_rejects_non_image_file():
    """
    Test verify endpoint với file không phải ảnh.
    Validates: Requirements 3.1, 6.1
    """
    # Create a text file
    text_data = b"This is not an image"
    files = {
        "file": ("test.txt", io.BytesIO(text_data), "text/plain")
    }
    
    response = client.post("/api/v1/face/verify", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "ảnh" in data["detail"].lower() or ".jpg" in data["detail"].lower()


def test_verify_accepts_jpeg_content_type():
    """Test verify endpoint chấp nhận image/jpeg"""
    img_bytes = create_simple_image('JPEG')
    files = {
        "file": ("test.jpg", img_bytes, "image/jpeg")
    }
    
    response = client.post("/api/v1/face/verify", files=files)
    
    # Should not reject based on content-type
    # If it's 400, it should be about face detection, not file type
    if response.status_code == 400:
        detail = response.json().get("detail", "")
        # Should not be the content-type error message
        assert "file upload phải là ảnh" not in detail.lower()


def test_verify_accepts_png_content_type():
    """Test verify endpoint chấp nhận image/png"""
    img_bytes = create_simple_image('PNG')
    files = {
        "file": ("test.png", img_bytes, "image/png")
    }
    
    response = client.post("/api/v1/face/verify", files=files)
    
    # Should not reject based on content-type
    # If it's 400, it should be about face detection, not file type
    if response.status_code == 400:
        detail = response.json().get("detail", "")
        # Should not be the content-type error message
        assert "file upload phải là ảnh" not in detail.lower()


# ============================================================================
# Verify Endpoint - Threshold Tests
# Validates: Requirements 4.1, 4.2, 4.3
# ============================================================================

def test_verify_uses_default_threshold():
    """
    Test verify endpoint với threshold mặc định.
    Validates: Requirements 4.2
    """
    img_bytes = create_face_like_image()
    files = {
        "file": ("test.jpg", img_bytes, "image/jpeg")
    }
    
    # Don't provide threshold parameter
    response = client.post("/api/v1/face/verify", files=files)
    
    # If successful, should use default threshold 0.5
    if response.status_code == 200:
        data = response.json()
        assert data["threshold"] == 0.5


def test_verify_uses_custom_threshold():
    """
    Test verify endpoint với threshold tùy chỉnh.
    Validates: Requirements 4.1
    """
    img_bytes = create_face_like_image()
    files = {
        "file": ("test.jpg", img_bytes, "image/jpeg")
    }
    
    custom_threshold = 0.7
    response = client.post(
        f"/api/v1/face/verify?threshold={custom_threshold}",
        files=files
    )
    
    # If successful, should use custom threshold
    if response.status_code == 200:
        data = response.json()
        assert data["threshold"] == custom_threshold


def test_verify_rejects_threshold_below_zero():
    """
    Test verify endpoint từ chối threshold < 0.
    Validates: Requirements 4.3, 4.4
    """
    img_bytes = create_simple_image()
    files = {
        "file": ("test.jpg", img_bytes, "image/jpeg")
    }
    
    response = client.post("/api/v1/face/verify?threshold=-0.1", files=files)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_verify_rejects_threshold_above_one():
    """
    Test verify endpoint từ chối threshold > 1.
    Validates: Requirements 4.3, 4.4
    """
    img_bytes = create_simple_image()
    files = {
        "file": ("test.jpg", img_bytes, "image/jpeg")
    }
    
    response = client.post("/api/v1/face/verify?threshold=1.5", files=files)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


# ============================================================================
# CORS Tests
# Validates: Requirements 8.1, 8.2, 8.3
# ============================================================================

def test_cors_headers_present():
    """
    Test CORS headers có mặt trong response.
    Validates: Requirements 8.1, 8.3
    
    Note: TestClient may not trigger CORS middleware the same way a real browser does.
    This test verifies the middleware is configured.
    """
    # Import to check middleware is configured
    from backend.main import app
    from fastapi.middleware.cors import CORSMiddleware
    
    # Check that CORS middleware is added
    cors_middleware_found = False
    for middleware in app.user_middleware:
        if middleware.cls == CORSMiddleware:
            cors_middleware_found = True
            # Check configuration
            options = middleware.options
            assert options.get("allow_origins") == ["*"]
            assert options.get("allow_methods") == ["*"]
            assert options.get("allow_headers") == ["*"]
            break
    
    assert cors_middleware_found, "CORS middleware not configured"


def test_cors_preflight_request():
    """
    Test CORS preflight request.
    Validates: Requirements 8.2
    
    Note: TestClient doesn't fully simulate browser CORS preflight behavior.
    In production, the CORS middleware handles OPTIONS requests automatically.
    This test verifies the middleware configuration allows preflight requests.
    """
    from backend.main import app
    from fastapi.middleware.cors import CORSMiddleware
    
    # Verify CORS middleware is configured to handle preflight
    for middleware in app.user_middleware:
        if middleware.cls == CORSMiddleware:
            options = middleware.options
            # Verify it allows all methods (including OPTIONS)
            assert options.get("allow_methods") == ["*"]
            return
    
    # If we get here, CORS middleware wasn't found
    assert False, "CORS middleware not configured"


def test_cors_allows_different_origins():
    """
    Test CORS cho phép nhiều origins khác nhau.
    
    Note: This test verifies the endpoint is accessible, but TestClient
    doesn't fully simulate browser CORS behavior.
    """
    origins = [
        "http://localhost:3000",
        "https://example.com",
        "https://app.example.com"
    ]
    
    for origin in origins:
        response = client.get(
            "/api/v1/health",
            headers={"Origin": origin}
        )
        
        # Should respond successfully
        assert response.status_code == 200


# ============================================================================
# Error Handling Tests
# Validates: Requirements 6.1, 6.2, 6.3, 6.4, 7.3
# ============================================================================

def test_verify_handles_corrupted_image():
    """
    Test xử lý ảnh bị hỏng.
    Validates: Requirements 6.2
    """
    # Create corrupted image data
    corrupted_data = b"not a valid image data at all"
    files = {
        "file": ("test.jpg", io.BytesIO(corrupted_data), "image/jpeg")
    }
    
    response = client.post("/api/v1/face/verify", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "đọc" in data["detail"].lower() or "ảnh" in data["detail"].lower()


def test_error_responses_use_json_format():
    """
    Test error responses sử dụng JSON format.
    Validates: Requirements 7.3
    """
    # Trigger an error with invalid content type
    files = {
        "file": ("test.txt", io.BytesIO(b"text"), "text/plain")
    }
    
    response = client.post("/api/v1/face/verify", files=files)
    
    assert response.status_code in [400, 422, 500]
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)


def test_missing_file_parameter():
    """Test xử lý khi thiếu file parameter"""
    response = client.post("/api/v1/face/verify")
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
