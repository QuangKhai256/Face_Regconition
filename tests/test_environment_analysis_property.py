"""
Property-based tests for environment analysis module.
Tests universal properties that should hold across all inputs.
"""

import numpy as np
import cv2
from hypothesis import given, strategies as st, settings
from backend.face_processor import analyze_environment


# Strategy for generating valid images
@st.composite
def valid_image_with_face(draw):
    """Generate a valid BGR image with a face box."""
    # Generate smaller image dimensions to avoid Hypothesis buffer limits
    width = draw(st.integers(min_value=50, max_value=200))
    height = draw(st.integers(min_value=50, max_value=200))
    
    # Generate random image using numpy directly
    # This is more efficient than using Hypothesis lists
    mean_brightness = draw(st.integers(min_value=0, max_value=255))
    std_brightness = draw(st.integers(min_value=10, max_value=50))
    
    # Create image with controlled brightness distribution
    image_bgr = np.random.normal(mean_brightness, std_brightness, (height, width, 3))
    image_bgr = np.clip(image_bgr, 0, 255).astype(np.uint8)
    
    # Generate valid face box within image bounds
    # Ensure face box is at least 10x10 pixels
    face_width = draw(st.integers(min_value=10, max_value=width))
    face_height = draw(st.integers(min_value=10, max_value=height))
    
    left = draw(st.integers(min_value=0, max_value=width - face_width))
    top = draw(st.integers(min_value=0, max_value=height - face_height))
    right = left + face_width
    bottom = top + face_height
    
    face_box = (top, right, bottom, left)
    
    return image_bgr, face_box


# Feature: face-recognition-complete, Property 2: Environment metrics calculation
@settings(max_examples=100)
@given(valid_image_with_face())
def test_property_environment_metrics_calculation(image_and_face):
    """
    Property 2: Environment metrics calculation
    For any image with exactly one face, the system should calculate 
    brightness (0-255), blur_score (Laplacian variance), and face_size_ratio (0.0-1.0),
    and all three metrics should be present in the response.
    
    Validates: Requirements 1.4, 3.4
    """
    image_bgr, face_box = image_and_face
    
    # Call analyze_environment
    result = analyze_environment(image_bgr, face_box)
    
    # Check that all required metrics are present
    assert "brightness" in result, "brightness metric missing"
    assert "blur_score" in result, "blur_score metric missing"
    assert "face_size_ratio" in result, "face_size_ratio metric missing"
    
    # Check brightness is in valid range (0-255)
    assert 0 <= result["brightness"] <= 255, \
        f"brightness {result['brightness']} out of range [0, 255]"
    
    # Check blur_score is non-negative (variance is always >= 0)
    assert result["blur_score"] >= 0, \
        f"blur_score {result['blur_score']} is negative"
    
    # Check face_size_ratio is in valid range (0.0-1.0)
    assert 0.0 <= result["face_size_ratio"] <= 1.0, \
        f"face_size_ratio {result['face_size_ratio']} out of range [0.0, 1.0]"
    
    # Verify face_size_ratio calculation
    top, right, bottom, left = face_box
    face_area = (bottom - top) * (right - left)
    image_height, image_width = image_bgr.shape[:2]
    image_area = image_height * image_width
    expected_ratio = face_area / image_area
    
    # Allow small floating point error
    assert abs(result["face_size_ratio"] - expected_ratio) < 1e-6, \
        f"face_size_ratio calculation incorrect: {result['face_size_ratio']} != {expected_ratio}"



# Feature: face-recognition-complete, Property 3: Environment threshold consistency
@settings(max_examples=100)
@given(valid_image_with_face())
def test_property_environment_threshold_consistency(image_and_face):
    """
    Property 3: Environment threshold consistency
    For any image with calculated environment metrics, the flags 
    (is_too_dark, is_too_bright, is_too_blurry, is_face_too_small) should be 
    set correctly based on the thresholds: brightness < 60 for too dark, 
    brightness > 200 for too bright, blur_score < 100 for too blurry, 
    face_size_ratio < 0.10 for too small.
    
    Validates: Requirements 1.5, 1.6, 1.7, 1.8
    """
    image_bgr, face_box = image_and_face
    
    # Call analyze_environment
    result = analyze_environment(image_bgr, face_box)
    
    # Check that all flags are present
    assert "is_too_dark" in result, "is_too_dark flag missing"
    assert "is_too_bright" in result, "is_too_bright flag missing"
    assert "is_too_blurry" in result, "is_too_blurry flag missing"
    assert "is_face_too_small" in result, "is_face_too_small flag missing"
    assert "warnings" in result, "warnings list missing"
    
    # Verify threshold logic for is_too_dark
    expected_too_dark = result["brightness"] < 60
    assert result["is_too_dark"] == expected_too_dark, \
        f"is_too_dark should be {expected_too_dark} for brightness {result['brightness']}"
    
    # Verify threshold logic for is_too_bright
    expected_too_bright = result["brightness"] > 200
    assert result["is_too_bright"] == expected_too_bright, \
        f"is_too_bright should be {expected_too_bright} for brightness {result['brightness']}"
    
    # Verify threshold logic for is_too_blurry
    expected_too_blurry = result["blur_score"] < 100
    assert result["is_too_blurry"] == expected_too_blurry, \
        f"is_too_blurry should be {expected_too_blurry} for blur_score {result['blur_score']}"
    
    # Verify threshold logic for is_face_too_small
    expected_too_small = result["face_size_ratio"] < 0.10
    assert result["is_face_too_small"] == expected_too_small, \
        f"is_face_too_small should be {expected_too_small} for face_size_ratio {result['face_size_ratio']}"
    
    # Verify warnings list consistency
    warnings = result["warnings"]
    assert isinstance(warnings, list), "warnings should be a list"
    
    # Check that warnings are generated for each flag
    if result["is_too_dark"]:
        assert any("tối" in w.lower() for w in warnings), \
            "Warning for too dark should be present"
    
    if result["is_too_bright"]:
        assert any("sáng" in w.lower() for w in warnings), \
            "Warning for too bright should be present"
    
    if result["is_too_blurry"]:
        assert any("mờ" in w.lower() for w in warnings), \
            "Warning for too blurry should be present"
    
    if result["is_face_too_small"]:
        assert any("nhỏ" in w.lower() for w in warnings), \
            "Warning for too small should be present"
    
    # Verify that if no flags are set, warnings list is empty
    if not (result["is_too_dark"] or result["is_too_bright"] or 
            result["is_too_blurry"] or result["is_face_too_small"]):
        assert len(warnings) == 0, \
            "Warnings list should be empty when no flags are set"
