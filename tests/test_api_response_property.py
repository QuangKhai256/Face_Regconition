"""
Property-based test for API response completeness
Tests that responses contain all required fields
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from fastapi.testclient import TestClient
import io
from PIL import Image, ImageDraw
import numpy as np

from backend.main import app

client = TestClient(app)


def create_face_like_image():
    """
    Create a simple image with a face-like pattern.
    This creates a basic oval shape that might be detected as a face.
    """
    # Create white background
    img = Image.new('RGB', (400, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple face-like oval (skin tone)
    draw.ellipse([100, 80, 300, 320], fill=(255, 220, 177), outline=(0, 0, 0))
    
    # Draw eyes (dark circles)
    draw.ellipse([140, 150, 180, 190], fill=(50, 50, 50))
    draw.ellipse([220, 150, 260, 190], fill=(50, 50, 50))
    
    # Draw nose (small triangle-ish)
    draw.ellipse([185, 200, 215, 240], fill=(200, 180, 160))
    
    # Draw mouth
    draw.arc([150, 240, 250, 290], start=0, end=180, fill=(100, 50, 50), width=3)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


# ============================================================================
# Property 9: Response contains all required fields
# Feature: face-recognition-backend, Property 9: Response contains all required fields
# Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
# ============================================================================

@given(
    threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(
    max_examples=50, 
    deadline=5000,
    suppress_health_check=[HealthCheck.filter_too_much]
)
def test_property_response_completeness(threshold):
    """
    Property 9: Response contains all required fields
    For any successful face verification request,
    the JSON response should contain all required fields:
    is_match, distance, threshold, message, face_box, image_size, and training_info.
    
    Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
    """
    # Create a face-like test image
    img_bytes = create_face_like_image()
    
    files = {
        "file": ("test.jpg", img_bytes, "image/jpeg")
    }
    
    # Send request
    response = client.post(
        f"/api/v1/face/verify?threshold={threshold}",
        files=files
    )
    
    # Only test successful responses (200)
    # Skip if no training data or no face detected
    assume(response.status_code == 200)
    
    data = response.json()
    
    # Check all required top-level fields exist
    required_fields = [
        "is_match", "distance", "threshold", "message",
        "face_box", "image_size", "training_info"
    ]
    
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Validate field types and structure
    assert isinstance(data["is_match"], bool), "is_match must be boolean"
    assert isinstance(data["distance"], (int, float)), "distance must be numeric"
    assert isinstance(data["threshold"], (int, float)), "threshold must be numeric"
    assert isinstance(data["message"], str), "message must be string"
    
    # Validate face_box structure
    face_box = data["face_box"]
    assert isinstance(face_box, dict), "face_box must be dict"
    for coord in ["top", "right", "bottom", "left"]:
        assert coord in face_box, f"face_box missing {coord}"
        assert isinstance(face_box[coord], int), f"face_box.{coord} must be int"
    
    # Validate image_size structure
    image_size = data["image_size"]
    assert isinstance(image_size, dict), "image_size must be dict"
    assert "width" in image_size, "image_size missing width"
    assert "height" in image_size, "image_size missing height"
    assert isinstance(image_size["width"], int), "width must be int"
    assert isinstance(image_size["height"], int), "height must be int"
    
    # Validate training_info structure
    training_info = data["training_info"]
    assert isinstance(training_info, dict), "training_info must be dict"
    assert "num_images" in training_info, "training_info missing num_images"
    assert "used_files_sample" in training_info, "training_info missing used_files_sample"
    assert isinstance(training_info["num_images"], int), "num_images must be int"
    assert isinstance(training_info["used_files_sample"], list), "used_files_sample must be list"
    
    # Validate threshold matches input
    assert abs(data["threshold"] - threshold) < 0.001, "threshold should match input"
