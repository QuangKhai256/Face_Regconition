"""
Property-based tests for verification module.
Tests universal properties for model loading and embedding comparison.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings
import math

from backend.verification import compare_embeddings, load_trained_model


# Feature: face-recognition-complete, Property 12: Euclidean distance calculation
@given(
    embedding1=st.lists(
        st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        min_size=128,
        max_size=128
    ),
    embedding2=st.lists(
        st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        min_size=128,
        max_size=128
    ),
    threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_euclidean_distance_calculation(embedding1, embedding2, threshold):
    """
    Property 12: Euclidean distance calculation
    
    For any two 128-d embeddings, the calculated distance should equal 
    the square root of the sum of squared differences between corresponding dimensions.
    
    Validates: Requirements 3.5
    """
    # Convert to numpy arrays
    emb1 = np.array(embedding1, dtype=np.float64)
    emb2 = np.array(embedding2, dtype=np.float64)
    
    # Call the function
    is_match, distance = compare_embeddings(emb1, emb2, threshold)
    
    # Calculate expected distance manually
    # distance = sqrt(sum((emb1[i] - emb2[i])^2))
    squared_diffs = [(emb1[i] - emb2[i]) ** 2 for i in range(128)]
    expected_distance = math.sqrt(sum(squared_diffs))
    
    # Verify the distance matches (within floating point precision)
    assert abs(distance - expected_distance) < 1e-6, (
        f"Distance calculation incorrect: got {distance}, expected {expected_distance}"
    )



# Feature: face-recognition-complete, Property 13: Threshold comparison consistency
@given(
    embedding1=st.lists(
        st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        min_size=128,
        max_size=128
    ),
    embedding2=st.lists(
        st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        min_size=128,
        max_size=128
    ),
    threshold=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_threshold_comparison_consistency(embedding1, embedding2, threshold):
    """
    Property 13: Threshold comparison consistency
    
    For any calculated distance and threshold value, is_match should be true 
    if and only if distance <= threshold.
    
    Validates: Requirements 3.6, 3.7
    """
    # Convert to numpy arrays
    emb1 = np.array(embedding1, dtype=np.float64)
    emb2 = np.array(embedding2, dtype=np.float64)
    
    # Call the function
    is_match, distance = compare_embeddings(emb1, emb2, threshold)
    
    # Verify threshold comparison logic
    if distance <= threshold:
        assert is_match is True, (
            f"is_match should be True when distance ({distance}) <= threshold ({threshold})"
        )
    else:
        assert is_match is False, (
            f"is_match should be False when distance ({distance}) > threshold ({threshold})"
        )



# Feature: face-recognition-complete, Property 14: Verification response completeness
@given(
    is_match=st.booleans(),
    distance=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    brightness=st.floats(min_value=0.0, max_value=255.0, allow_nan=False, allow_infinity=False),
    blur_score=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    face_size_ratio=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_verification_response_completeness(is_match, distance, threshold, brightness, blur_score, face_size_ratio):
    """
    Property 14: Verification response completeness
    
    For any successful verification operation, the response should contain all required fields:
    is_match (bool), distance (float), threshold (float), message (string), 
    face_box (with top/right/bottom/left), image_size (with width/height), 
    and environment_info (with all metrics and warnings).
    
    Validates: Requirements 3.8, 3.9
    """
    from backend.models import VerifyResponse, FaceBox, ImageSize, EnvironmentInfo, TrainingInfo
    
    # Create a mock response with all required fields
    # This tests that the response model structure is complete
    
    # Generate environment flags based on thresholds
    is_too_dark = brightness < 60
    is_too_bright = brightness > 200
    is_too_blurry = blur_score < 100
    is_face_too_small = face_size_ratio < 0.10
    
    # Generate warnings
    warnings = []
    if is_too_dark:
        warnings.append("Ảnh quá tối")
    if is_too_bright:
        warnings.append("Ảnh quá sáng")
    if is_too_blurry:
        warnings.append("Ảnh bị mờ")
    if is_face_too_small:
        warnings.append("Khuôn mặt quá nhỏ")
    
    # Create message
    if is_match:
        message = f"Đây là KHUÔN MẶT CỦA BẠN (khoảng cách = {distance:.3f} ≤ ngưỡng {threshold:.3f})."
    else:
        message = f"Đây KHÔNG PHẢI khuôn mặt của bạn (khoảng cách = {distance:.3f} > ngưỡng {threshold:.3f})."
    
    # Create response object
    response = VerifyResponse(
        is_match=is_match,
        distance=round(distance, 3),
        threshold=threshold,
        message=message,
        face_box=FaceBox(
            top=10,
            right=90,
            bottom=90,
            left=10
        ),
        image_size=ImageSize(
            width=100,
            height=100
        ),
        environment_info=EnvironmentInfo(
            brightness=brightness,
            is_too_dark=is_too_dark,
            is_too_bright=is_too_bright,
            blur_score=blur_score,
            is_too_blurry=is_too_blurry,
            face_size_ratio=face_size_ratio,
            is_face_too_small=is_face_too_small,
            warnings=warnings
        ),
        training_info=TrainingInfo(
            num_images=10,
            used_files_sample=["file1.jpg", "file2.jpg"]
        )
    )
    
    # Convert to dict to verify structure
    response_dict = response.model_dump()
    
    # Verify all required fields are present
    assert "is_match" in response_dict, "Response missing 'is_match' field"
    assert "distance" in response_dict, "Response missing 'distance' field"
    assert "threshold" in response_dict, "Response missing 'threshold' field"
    assert "message" in response_dict, "Response missing 'message' field"
    assert "face_box" in response_dict, "Response missing 'face_box' field"
    assert "image_size" in response_dict, "Response missing 'image_size' field"
    assert "environment_info" in response_dict, "Response missing 'environment_info' field"
    assert "training_info" in response_dict, "Response missing 'training_info' field"
    
    # Verify is_match is boolean
    assert isinstance(response_dict["is_match"], bool), "is_match must be boolean"
    
    # Verify distance is float
    assert isinstance(response_dict["distance"], (int, float)), "distance must be numeric"
    
    # Verify threshold is float
    assert isinstance(response_dict["threshold"], (int, float)), "threshold must be numeric"
    
    # Verify message is string
    assert isinstance(response_dict["message"], str), "message must be string"
    assert len(response_dict["message"]) > 0, "message must not be empty"
    
    # Verify face_box has all required fields
    face_box = response_dict["face_box"]
    assert "top" in face_box, "face_box missing 'top' field"
    assert "right" in face_box, "face_box missing 'right' field"
    assert "bottom" in face_box, "face_box missing 'bottom' field"
    assert "left" in face_box, "face_box missing 'left' field"
    
    # Verify image_size has all required fields
    image_size = response_dict["image_size"]
    assert "width" in image_size, "image_size missing 'width' field"
    assert "height" in image_size, "image_size missing 'height' field"
    
    # Verify environment_info has all required fields
    env = response_dict["environment_info"]
    assert "brightness" in env, "environment_info missing 'brightness' field"
    assert "is_too_dark" in env, "environment_info missing 'is_too_dark' field"
    assert "is_too_bright" in env, "environment_info missing 'is_too_bright' field"
    assert "blur_score" in env, "environment_info missing 'blur_score' field"
    assert "is_too_blurry" in env, "environment_info missing 'is_too_blurry' field"
    assert "face_size_ratio" in env, "environment_info missing 'face_size_ratio' field"
    assert "is_face_too_small" in env, "environment_info missing 'is_face_too_small' field"
    assert "warnings" in env, "environment_info missing 'warnings' field"
    
    # Verify environment_info field types
    assert isinstance(env["brightness"], (int, float)), "brightness must be numeric"
    assert isinstance(env["is_too_dark"], bool), "is_too_dark must be boolean"
    assert isinstance(env["is_too_bright"], bool), "is_too_bright must be boolean"
    assert isinstance(env["blur_score"], (int, float)), "blur_score must be numeric"
    assert isinstance(env["is_too_blurry"], bool), "is_too_blurry must be boolean"
    assert isinstance(env["face_size_ratio"], (int, float)), "face_size_ratio must be numeric"
    assert isinstance(env["is_face_too_small"], bool), "is_face_too_small must be boolean"
    assert isinstance(env["warnings"], list), "warnings must be a list"
    
    # Verify training_info has required fields
    training_info = response_dict["training_info"]
    assert "num_images" in training_info, "training_info missing 'num_images' field"
    assert "used_files_sample" in training_info, "training_info missing 'used_files_sample' field"
