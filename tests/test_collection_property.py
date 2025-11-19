"""
Property-based tests for collection endpoint.
Tests universal properties for collection rejection and success.
"""

import pytest
import numpy as np
import cv2
import io
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.main import app

client = TestClient(app)


# Strategy for generating images with controlled environment properties
@st.composite
def image_with_environment(draw, poor_environment=False):
    """
    Generate a synthetic image with controlled environment properties.
    
    Args:
        poor_environment: If True, generate image with poor environment
                         (too dark, too blurry, or face too small)
    """
    # Generate image dimensions
    width = draw(st.integers(min_value=200, max_value=400))
    height = draw(st.integers(min_value=200, max_value=400))
    
    if poor_environment:
        # Generate poor environment conditions
        # Choose which condition to violate
        condition = draw(st.sampled_from(['too_dark', 'face_too_small']))
        
        if condition == 'too_dark':
            # Generate dark image (brightness < 60)
            brightness = draw(st.integers(min_value=0, max_value=59))
            face_size_ratio = draw(st.floats(min_value=0.10, max_value=0.50))
        else:  # face_too_small
            # Generate image with small face (face_size_ratio < 0.10)
            brightness = draw(st.integers(min_value=60, max_value=200))
            face_size_ratio = draw(st.floats(min_value=0.01, max_value=0.09))
    else:
        # Generate good environment conditions
        brightness = draw(st.integers(min_value=60, max_value=200))
        # Use 0.11 as min to avoid edge cases with 0.10 threshold
        face_size_ratio = draw(st.floats(min_value=0.11, max_value=0.50))
    
    # Create synthetic image with controlled brightness
    image_bgr = np.full((height, width, 3), brightness, dtype=np.uint8)
    
    # Add noise to make it more realistic and ensure sufficient blur score
    # For good environment, we need blur_score >= 100
    if not poor_environment:
        # Add stronger noise/texture to increase blur score (Laplacian variance)
        # Create a checkerboard pattern to maximize Laplacian variance
        # This ensures blur_score will be well above 100
        for i in range(0, height, 2):
            for j in range(0, width, 2):
                if (i + j) % 4 == 0:
                    image_bgr[i:i+2, j:j+2] = np.clip(brightness + 50, 0, 255)
                else:
                    image_bgr[i:i+2, j:j+2] = np.clip(brightness - 50, 0, 255)
        
        # Add additional random noise
        noise = np.random.randint(-30, 30, (height, width, 3), dtype=np.int16)
        image_bgr = np.clip(image_bgr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    else:
        # For poor environment, add minimal noise
        noise = np.random.randint(-10, 10, (height, width, 3), dtype=np.int16)
        image_bgr = np.clip(image_bgr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Calculate face box based on face_size_ratio
    face_area = int(width * height * face_size_ratio)
    face_width = int(np.sqrt(face_area))
    face_height = face_width
    
    # Ensure face fits in image
    face_width = min(face_width, width - 20)
    face_height = min(face_height, height - 20)
    
    left = (width - face_width) // 2
    top = (height - face_height) // 2
    right = left + face_width
    bottom = top + face_height
    
    face_box = (top, right, bottom, left)
    
    # Encode image as JPEG bytes
    success, encoded_image = cv2.imencode('.jpg', image_bgr)
    if not success:
        raise ValueError("Failed to encode image")
    
    image_bytes = encoded_image.tobytes()
    
    return image_bytes, face_box, brightness, face_size_ratio


# ============================================================================
# Property 4: Collection rejection for poor environment
# Feature: face-recognition-complete, Property 4: Collection rejection for poor environment
# Validates: Requirements 1.9
# ============================================================================

@given(image_with_environment(poor_environment=True))
@settings(max_examples=100, deadline=None)
def test_property_collection_rejection_for_poor_environment(image_data):
    """
    Property 4: Collection rejection for poor environment
    For any image where is_too_dark OR is_too_blurry OR is_face_too_small is true,
    the collect endpoint should return HTTP 400 and should NOT save the image to disk.
    
    Validates: Requirements 1.9
    """
    image_bytes, face_box, brightness, face_size_ratio = image_data
    
    # Mock face detection to return exactly one face
    with patch('backend.face_processor.face_recognition') as mock_fr:
        # Mock face_locations to return one face
        mock_fr.face_locations.return_value = [face_box]
        
        # Mock face_encodings to return a valid 128-d embedding
        mock_encoding = np.random.rand(128)
        mock_fr.face_encodings.return_value = [mock_encoding]
        
        # Count files before request
        import os
        data_dir = "data/raw/user"
        os.makedirs(data_dir, exist_ok=True)
        files_before = set(os.listdir(data_dir))
        
        # Create file upload
        files = {
            "file": ("test.jpg", io.BytesIO(image_bytes), "image/jpeg")
        }
        
        # Call collect endpoint
        response = client.post("/api/v1/collect", files=files)
        
        # Count files after request
        files_after = set(os.listdir(data_dir))
        new_files = files_after - files_before
        
        # Assert HTTP 400 for poor environment
        assert response.status_code == 400, \
            f"Expected 400 for poor environment (brightness={brightness:.1f}, " \
            f"face_size_ratio={face_size_ratio:.3f}), " \
            f"got {response.status_code}"
        
        # Assert no new files were saved
        assert len(new_files) == 0, \
            f"Image should not be saved for poor environment, but {len(new_files)} new files found"
        
        # Assert response contains detail
        assert "detail" in response.json(), \
            "Response should contain 'detail' field"



# ============================================================================
# Property 5: Collection success for good environment
# Feature: face-recognition-complete, Property 5: Collection success for good environment
# Validates: Requirements 1.10, 1.11, 7.3
# ============================================================================

@given(image_with_environment(poor_environment=False))
@settings(max_examples=100, deadline=5000)  # 100 examples with 5 second deadline per example
def test_property_collection_success_for_good_environment(image_data):
    """
    Property 5: Collection success for good environment
    For any image where all environment checks pass (not too dark, not too bright, 
    not too blurry, face not too small), the collect endpoint should return HTTP 200, 
    save the image with timestamp filename format, and return the correct total_images count.
    
    Validates: Requirements 1.10, 1.11, 7.3
    """
    image_bytes, face_box, brightness, face_size_ratio = image_data
    
    # Mock both extract_single_face_encoding and analyze_environment
    with patch('backend.main.extract_single_face_encoding') as mock_extract, \
         patch('backend.main.analyze_environment') as mock_analyze:
        # Mock to return a valid 128-d embedding and the face location
        mock_encoding = np.random.rand(128)
        mock_extract.return_value = (mock_encoding, face_box)
        
        # Mock analyze_environment to return good environment values as dictionary
        mock_analyze.return_value = {
            'brightness': brightness,
            'is_too_dark': False,
            'is_too_bright': False,
            'blur_score': 120,
            'is_too_blurry': False,
            'face_size_ratio': face_size_ratio,
            'is_face_too_small': False,
            'warnings': []
        }
        
        # Count files before request
        import os
        data_dir = "data/raw/user"
        os.makedirs(data_dir, exist_ok=True)
        files_before = os.listdir(data_dir)
        files_before_count = len([f for f in files_before if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        # Create file upload
        files = {
            "file": ("test.jpg", io.BytesIO(image_bytes), "image/jpeg")
        }
        
        try:
            # Call collect endpoint
            response = client.post("/api/v1/collect", files=files)
            
            # Count files after request
            files_after = os.listdir(data_dir)
            files_after_count = len([f for f in files_after if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            
            # Assert HTTP 200 for good environment
            assert response.status_code == 200, \
                f"Expected 200 for good environment (brightness={brightness:.1f}, " \
                f"face_size_ratio={face_size_ratio:.3f}), " \
                f"got {response.status_code}: {response.json()}"
            
            # Assert file count increased by 1 (one new file was saved)
            assert files_after_count == files_before_count + 1, \
                f"Expected 1 new file for good environment, but file count changed from {files_before_count} to {files_after_count}"
            
            # Assert response contains required fields
            response_data = response.json()
            assert "message" in response_data, "Response should contain 'message' field"
            assert "saved_path" in response_data, "Response should contain 'saved_path' field"
            assert "total_images" in response_data, "Response should contain 'total_images' field"
            assert "environment_info" in response_data, "Response should contain 'environment_info' field"
            
            # Assert total_images count is correct
            assert response_data["total_images"] == files_after_count, \
                f"total_images should be {files_after_count}, got {response_data['total_images']}"
            
            # Assert saved_path contains timestamp format (user_YYYYMMDD_HHMMSS.jpg)
            saved_path = response_data["saved_path"]
            assert "user_" in saved_path, "Saved path should contain 'user_' prefix"
            assert saved_path.endswith(".jpg"), "Saved path should end with '.jpg'"
            
            # Assert the new file exists
            new_files = set(files_after) - set(files_before)
            assert len(new_files) == 1, f"Expected exactly 1 new file, got {len(new_files)}"
            new_file = list(new_files)[0]
            assert os.path.exists(os.path.join(data_dir, new_file)), \
                f"New file {new_file} should exist in {data_dir}"
        finally:
            # Cleanup: remove the test file if it was created
            files_after = os.listdir(data_dir)
            new_files = set(files_after) - set(files_before)
            for new_file in new_files:
                try:
                    os.remove(os.path.join(data_dir, new_file))
                except:
                    pass
