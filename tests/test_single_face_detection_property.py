"""
Property-based tests for single face detection validation.
Tests Property 1 from the design document.
"""

import numpy as np
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import patch

from backend.face_processor import extract_single_face_embedding


class TestSingleFaceDetectionProperty:
    """Property-based tests for single face detection validation."""
    
    @settings(max_examples=100, deadline=None)
    @given(
        image_width=st.integers(min_value=100, max_value=800),
        image_height=st.integers(min_value=100, max_value=800),
        num_faces=st.integers(min_value=0, max_value=5)
    )
    def test_property_single_face_detection_validation(self, image_width, image_height, num_faces):
        """
        **Feature: face-recognition-complete, Property 1: Single face detection validation**
        **Validates: Requirements 1.1**
        
        For any image sent to the collect or verify endpoint, the system should correctly 
        identify whether there is exactly zero, one, or multiple faces, and respond 
        appropriately (reject if not exactly one).
        """
        # Create a mock RGB image
        mock_image_rgb = np.random.randint(0, 256, (image_height, image_width, 3), dtype=np.uint8)
        
        # Mock face_recognition to return the specified number of faces
        with patch('backend.face_processor.face_recognition') as mock_fr:
            # Generate face locations based on num_faces
            if num_faces == 0:
                face_locations = []
            else:
                face_locations = []
                for i in range(num_faces):
                    # Generate valid face box coordinates
                    top = 50 + i * 20
                    bottom = min(top + 100, image_height - 10)
                    left = 50 + i * 20
                    right = min(left + 100, image_width - 10)
                    
                    # Ensure valid box
                    if bottom > top and right > left:
                        face_locations.append((top, right, bottom, left))
            
            mock_fr.face_locations.return_value = face_locations
            
            # Generate mock encodings for valid faces
            if num_faces == 1:
                mock_encoding = np.random.rand(128)
                mock_fr.face_encodings.return_value = [mock_encoding]
            else:
                mock_fr.face_encodings.return_value = []
            
            # Test the behavior based on number of faces
            if num_faces == 0:
                # Should raise ValueError for no faces
                with pytest.raises(ValueError) as exc_info:
                    extract_single_face_embedding(mock_image_rgb)
                
                error_msg = str(exc_info.value)
                assert "Không tìm thấy khuôn mặt" in error_msg, \
                    "Error message should indicate no face found"
            
            elif num_faces == 1:
                # Should successfully extract embedding
                embedding, location = extract_single_face_embedding(mock_image_rgb)
                
                assert isinstance(embedding, np.ndarray), \
                    "Should return numpy array for embedding"
                assert embedding.shape == (128,), \
                    f"Embedding should be 128-dimensional, got {embedding.shape}"
                assert location == face_locations[0], \
                    "Location should match the detected face"
            
            else:  # num_faces > 1
                # Should raise ValueError for multiple faces
                with pytest.raises(ValueError) as exc_info:
                    extract_single_face_embedding(mock_image_rgb)
                
                error_msg = str(exc_info.value)
                assert "khuôn mặt trong ảnh" in error_msg, \
                    "Error message should indicate multiple faces"
                assert "CHỈ MỘT" in error_msg, \
                    "Error message should emphasize only one face allowed"
    
    @settings(max_examples=100, deadline=None)
    @given(
        image_width=st.integers(min_value=100, max_value=800),
        image_height=st.integers(min_value=100, max_value=800)
    )
    def test_property_exactly_one_face_succeeds(self, image_width, image_height):
        """
        **Feature: face-recognition-complete, Property 1: Single face detection validation**
        **Validates: Requirements 1.1**
        
        For any image with exactly one face, the system should successfully extract 
        the face embedding without raising an error.
        """
        # Create a mock RGB image
        mock_image_rgb = np.random.randint(0, 256, (image_height, image_width, 3), dtype=np.uint8)
        
        # Mock face_recognition to return exactly one face
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_location = (50, image_width - 50, image_height - 50, 50)
            mock_encoding = np.random.rand(128)
            
            mock_fr.face_locations.return_value = [mock_location]
            mock_fr.face_encodings.return_value = [mock_encoding]
            
            # Should not raise any exception
            embedding, location = extract_single_face_embedding(mock_image_rgb)
            
            # Verify successful extraction
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape == (128,)
            assert location == mock_location
    
    @settings(max_examples=100, deadline=None)
    @given(
        num_faces=st.integers(min_value=2, max_value=10)
    )
    def test_property_multiple_faces_rejected(self, num_faces):
        """
        **Feature: face-recognition-complete, Property 1: Single face detection validation**
        **Validates: Requirements 1.1, 1.3**
        
        For any image with more than one face, the system should reject it with 
        a ValueError indicating multiple faces detected.
        """
        # Create a mock RGB image
        mock_image_rgb = np.random.randint(0, 256, (400, 400, 3), dtype=np.uint8)
        
        # Mock face_recognition to return multiple faces
        with patch('backend.face_processor.face_recognition') as mock_fr:
            # Generate multiple face locations
            face_locations = [
                (50 + i * 30, 150 + i * 30, 150 + i * 30, 50 + i * 30)
                for i in range(num_faces)
            ]
            
            mock_fr.face_locations.return_value = face_locations
            mock_fr.face_encodings.return_value = []
            
            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                extract_single_face_embedding(mock_image_rgb)
            
            error_msg = str(exc_info.value)
            assert "khuôn mặt trong ảnh" in error_msg
            assert str(num_faces) in error_msg or "CHỈ MỘT" in error_msg
    
    @settings(max_examples=100, deadline=None)
    @given(
        image_width=st.integers(min_value=100, max_value=800),
        image_height=st.integers(min_value=100, max_value=800)
    )
    def test_property_no_face_rejected(self, image_width, image_height):
        """
        **Feature: face-recognition-complete, Property 1: Single face detection validation**
        **Validates: Requirements 1.1, 1.2**
        
        For any image with no faces, the system should reject it with a ValueError 
        indicating no face found.
        """
        # Create a mock RGB image
        mock_image_rgb = np.random.randint(0, 256, (image_height, image_width, 3), dtype=np.uint8)
        
        # Mock face_recognition to return no faces
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_fr.face_locations.return_value = []
            
            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                extract_single_face_embedding(mock_image_rgb)
            
            error_msg = str(exc_info.value)
            assert "Không tìm thấy khuôn mặt" in error_msg
