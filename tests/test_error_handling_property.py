"""
Property-based tests for error handling.
Tests universal properties about error responses and exception handling.
"""

import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
import io
from PIL import Image

from backend.main import app

client = TestClient(app)


# ============================================================================
# Property 10: Error responses use JSON format
# **Feature: face-recognition-backend, Property 10: Error responses use JSON format**
# **Validates: Requirements 7.3**
# ============================================================================

@given(
    content_type=st.sampled_from([
        "text/plain",
        "application/pdf",
        "application/xml",
        "video/mp4",
        "audio/mpeg"
    ])
)
@settings(max_examples=100)
def test_property_error_responses_use_json_format(content_type):
    """
    Property 10: Error responses use JSON format
    
    *For any* HTTP error response (4xx or 5xx), the response should be in JSON 
    format with a "detail" field containing the error message.
    
    **Feature: face-recognition-backend, Property 10: Error responses use JSON format**
    **Validates: Requirements 7.3**
    """
    # Create a file with invalid content type to trigger error
    files = {
        "file": ("test.file", io.BytesIO(b"test data"), content_type)
    }
    
    response = client.post("/api/v1/face/verify", files=files)
    
    # Should be an error response
    assert response.status_code >= 400, f"Expected error status code, got {response.status_code}"
    
    # Should be JSON format
    assert response.headers.get("content-type", "").startswith("application/json"), \
        f"Expected JSON content-type, got {response.headers.get('content-type')}"
    
    # Should have detail field
    data = response.json()
    assert "detail" in data, f"Response should have 'detail' field, got {data}"
    assert isinstance(data["detail"], str), f"Detail should be string, got {type(data['detail'])}"


@given(
    threshold=st.floats(min_value=-10.0, max_value=-0.01) | st.floats(min_value=1.01, max_value=10.0)
)
@settings(max_examples=100)
def test_property_validation_errors_use_json_format(threshold):
    """
    Property 10 (validation variant): Validation error responses use JSON format
    
    *For any* validation error (HTTP 422), the response should be in JSON format 
    with a "detail" field.
    
    **Feature: face-recognition-backend, Property 10: Error responses use JSON format**
    **Validates: Requirements 7.3**
    """
    # Create a simple image
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    files = {
        "file": ("test.jpg", img_bytes, "image/jpeg")
    }
    
    # Use invalid threshold to trigger validation error
    response = client.post(f"/api/v1/face/verify?threshold={threshold}", files=files)
    
    # Should be validation error
    assert response.status_code == 422, f"Expected 422 for invalid threshold, got {response.status_code}"
    
    # Should be JSON format
    assert response.headers.get("content-type", "").startswith("application/json"), \
        f"Expected JSON content-type, got {response.headers.get('content-type')}"
    
    # Should have detail field
    data = response.json()
    assert "detail" in data, f"Response should have 'detail' field, got {data}"


@given(
    corrupted_data=st.binary(min_size=1, max_size=100)
)
@settings(max_examples=100)
def test_property_value_errors_use_json_format(corrupted_data):
    """
    Property 10 (ValueError variant): ValueError responses use JSON format
    
    *For any* corrupted image data that triggers ValueError, the response should 
    be HTTP 400 in JSON format with a "detail" field.
    
    **Feature: face-recognition-backend, Property 10: Error responses use JSON format**
    **Validates: Requirements 7.3**
    """
    files = {
        "file": ("test.jpg", io.BytesIO(corrupted_data), "image/jpeg")
    }
    
    response = client.post("/api/v1/face/verify", files=files)
    
    # Should be error response (likely 400 for ValueError)
    assert response.status_code >= 400, f"Expected error status code, got {response.status_code}"
    
    # Should be JSON format
    assert response.headers.get("content-type", "").startswith("application/json"), \
        f"Expected JSON content-type, got {response.headers.get('content-type')}"
    
    # Should have detail field
    data = response.json()
    assert "detail" in data, f"Response should have 'detail' field, got {data}"
    assert isinstance(data["detail"], str), f"Detail should be string, got {type(data['detail'])}"



# ============================================================================
# Property 11: Exception handling prevents crashes
# **Feature: face-recognition-backend, Property 11: Exception handling prevents crashes**
# **Validates: Requirements 7.4**
# ============================================================================

@given(
    file_data=st.binary(min_size=0, max_size=1000),
    content_type=st.sampled_from([
        "image/jpeg",
        "image/jpg", 
        "image/png",
        "text/plain",
        "application/octet-stream"
    ]),
    threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_property_exception_handling_prevents_crashes(file_data, content_type, threshold):
    """
    Property 11: Exception handling prevents crashes
    
    *For any* exception that occurs during request processing, the system should 
    catch it and return an appropriate HTTP error response instead of crashing.
    
    **Feature: face-recognition-backend, Property 11: Exception handling prevents crashes**
    **Validates: Requirements 7.4**
    """
    files = {
        "file": ("test.file", io.BytesIO(file_data), content_type)
    }
    
    # This should never crash - should always return a response
    try:
        response = client.post(f"/api/v1/face/verify?threshold={threshold}", files=files)
        
        # Should get a response (not crash)
        assert response is not None, "Should receive a response, not crash"
        
        # Should have a valid HTTP status code
        assert 200 <= response.status_code < 600, \
            f"Should have valid HTTP status code, got {response.status_code}"
        
        # Should be JSON format
        assert response.headers.get("content-type", "").startswith("application/json"), \
            f"Response should be JSON, got {response.headers.get('content-type')}"
        
        # Should have parseable JSON body
        data = response.json()
        assert isinstance(data, dict), f"Response should be JSON dict, got {type(data)}"
        
    except Exception as e:
        # If we get here, the server crashed instead of handling the exception
        pytest.fail(f"Server crashed with exception instead of handling it: {e}")


@given(
    threshold=st.floats(allow_nan=True, allow_infinity=True) | 
              st.floats(min_value=-1000.0, max_value=1000.0)
)
@settings(max_examples=100)
def test_property_exception_handling_for_edge_case_thresholds(threshold):
    """
    Property 11 (threshold variant): Exception handling for edge case thresholds
    
    *For any* threshold value (including NaN, infinity, extreme values), the system 
    should handle it gracefully without crashing.
    
    **Feature: face-recognition-backend, Property 11: Exception handling prevents crashes**
    **Validates: Requirements 7.4**
    """
    # Create a simple image
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    files = {
        "file": ("test.jpg", img_bytes, "image/jpeg")
    }
    
    # This should never crash
    try:
        response = client.post(f"/api/v1/face/verify?threshold={threshold}", files=files)
        
        # Should get a response (not crash)
        assert response is not None, "Should receive a response, not crash"
        
        # Should have a valid HTTP status code
        assert 200 <= response.status_code < 600, \
            f"Should have valid HTTP status code, got {response.status_code}"
        
        # Should be JSON format
        data = response.json()
        assert isinstance(data, dict), f"Response should be JSON dict, got {type(data)}"
        
    except Exception as e:
        # If we get here, the server crashed instead of handling the exception
        pytest.fail(f"Server crashed with exception instead of handling it: {e}")


@given(
    num_requests=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=20)
def test_property_exception_handling_under_load(num_requests):
    """
    Property 11 (load variant): Exception handling under multiple requests
    
    *For any* sequence of requests (including error-triggering requests), the system 
    should handle all exceptions without crashing.
    
    **Feature: face-recognition-backend, Property 11: Exception handling prevents crashes**
    **Validates: Requirements 7.4**
    """
    # Send multiple requests that will trigger various errors
    for i in range(num_requests):
        # Alternate between different error-triggering scenarios
        if i % 3 == 0:
            # Invalid content type
            files = {"file": ("test.txt", io.BytesIO(b"text"), "text/plain")}
        elif i % 3 == 1:
            # Corrupted image
            files = {"file": ("test.jpg", io.BytesIO(b"corrupted"), "image/jpeg")}
        else:
            # Valid content type but random data
            files = {"file": ("test.png", io.BytesIO(b"random data"), "image/png")}
        
        try:
            response = client.post("/api/v1/face/verify", files=files)
            
            # Should get a response (not crash)
            assert response is not None, f"Request {i} should receive a response"
            assert 200 <= response.status_code < 600, \
                f"Request {i} should have valid status code, got {response.status_code}"
            
            # Should be JSON
            data = response.json()
            assert isinstance(data, dict), f"Request {i} should return JSON dict"
            
        except Exception as e:
            pytest.fail(f"Server crashed on request {i} instead of handling exception: {e}")
