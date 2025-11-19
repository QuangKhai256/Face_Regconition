"""
Property-based tests for face processor module.
"""

import numpy as np
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import patch, MagicMock

from backend.face_processor import (
    read_image_from_upload,
    extract_single_face_encoding,
    compare_with_known_faces
)


class TestFaceProcessorProperties:
    """Property-based tests for face processor."""
    
    @settings(max_examples=100, deadline=None)
    @given(
        image_width=st.integers(min_value=100, max_value=1000),
        image_height=st.integers(min_value=100, max_value=1000)
    )
    def test_property_training_extracts_128d_embeddings(self, image_width, image_height):
        """
        **Feature: face-recognition-complete, Property 7: Training extracts 128-d embeddings**
        **Validates: Requirements 2.3**
        
        For any valid training image with exactly one face, the system should extract 
        a face embedding with exactly 128 dimensions.
        """
        # Create a mock RGB image (simulating a training image)
        mock_image_rgb = np.random.randint(0, 256, (image_height, image_width, 3), dtype=np.uint8)
        
        # Mock face_recognition functions
        with patch('backend.face_processor.face_recognition') as mock_fr:
            # Mock to return exactly one face location (valid training image)
            mock_location = (50, image_width - 50, image_height - 50, 50)
            mock_fr.face_locations.return_value = [mock_location]
            
            # Mock to return one 128-d encoding
            mock_encoding = np.random.rand(128)
            mock_fr.face_encodings.return_value = [mock_encoding]
            
            # Extract face embedding (as would happen during training)
            embedding, location = extract_single_face_encoding(mock_image_rgb)
            
            # Property: The extracted embedding MUST be exactly 128 dimensions
            assert isinstance(embedding, np.ndarray), \
                "Embedding should be a numpy array"
            assert len(embedding.shape) == 1, \
                f"Embedding should be 1-dimensional vector, got shape {embedding.shape}"
            assert embedding.shape[0] == 128, \
                f"Embedding MUST be exactly 128 dimensions for training, got {embedding.shape[0]}"
            
            # Verify the embedding contains valid float values
            assert embedding.dtype in [np.float32, np.float64], \
                f"Embedding should contain float values, got {embedding.dtype}"
            
            # Verify location is also returned correctly
            assert location == mock_location, \
                "Face location should be returned along with embedding"
    
    @settings(max_examples=100, deadline=None)
    @given(
        image_width=st.integers(min_value=100, max_value=1000),
        image_height=st.integers(min_value=100, max_value=1000)
    )
    def test_property_face_embedding_extraction(self, image_width, image_height):
        """
        **Feature: face-recognition-backend, Property 4: Face embedding extraction from valid images**
        **Validates: Requirements 3.2**
        
        For any valid image containing exactly one face, the system should successfully
        extract a 128-dimensional face embedding vector.
        """
        # Create a mock RGB image
        mock_image_rgb = np.random.randint(0, 256, (image_height, image_width, 3), dtype=np.uint8)
        
        # Mock face_recognition functions
        with patch('backend.face_processor.face_recognition') as mock_fr:
            # Mock to return exactly one face location
            mock_location = (50, image_width - 50, image_height - 50, 50)  # top, right, bottom, left
            mock_fr.face_locations.return_value = [mock_location]
            
            # Mock to return one 128-d encoding
            mock_encoding = np.random.rand(128)
            mock_fr.face_encodings.return_value = [mock_encoding]
            
            # Extract face encoding
            encoding, location = extract_single_face_encoding(mock_image_rgb)
            
            # Verify the encoding is 128-dimensional
            assert isinstance(encoding, np.ndarray), "Encoding should be numpy array"
            assert encoding.shape == (128,), f"Encoding should be 128-dimensional, got {encoding.shape}"
            
            # Verify location is returned
            assert location == mock_location, "Location should match the detected face location"
            
            # Verify face_recognition functions were called
            mock_fr.face_locations.assert_called_once()
            mock_fr.face_encodings.assert_called_once()
    
    @settings(max_examples=100, deadline=None)
    @given(
        num_known_faces=st.integers(min_value=1, max_value=20),
        threshold=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_property_distance_comparison(self, num_known_faces, threshold):
        """
        **Feature: face-recognition-backend, Property 5: Distance comparison with all training embeddings**
        **Validates: Requirements 3.3, 3.4**
        
        For any uploaded face image and training data, the system should compute distances
        to all training embeddings and use the minimum distance for the match decision.
        """
        # Create mock embeddings
        unknown_encoding = np.random.rand(128)
        known_encodings = [np.random.rand(128) for _ in range(num_known_faces)]
        
        # Mock face_recognition.face_distance
        with patch('backend.face_processor.face_recognition') as mock_fr:
            # Generate random distances
            mock_distances = np.random.rand(num_known_faces)
            mock_fr.face_distance.return_value = mock_distances
            
            # Compare faces
            is_match, best_distance = compare_with_known_faces(
                unknown_encoding, known_encodings, threshold
            )
            
            # Verify face_distance was called with all known encodings
            mock_fr.face_distance.assert_called_once_with(known_encodings, unknown_encoding)
            
            # Verify best_distance is the minimum of all distances
            expected_min = float(np.min(mock_distances))
            assert best_distance == expected_min, \
                f"Best distance should be minimum of all distances: expected {expected_min}, got {best_distance}"
            
            # Verify is_match is based on the minimum distance
            expected_match = expected_min <= threshold
            assert is_match == expected_match, \
                f"Match decision should be based on minimum distance vs threshold"
    
    @settings(max_examples=100, deadline=None)
    @given(
        distance=st.floats(min_value=0.0, max_value=1.0),
        threshold=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_property_threshold_based_matching(self, distance, threshold):
        """
        **Feature: face-recognition-backend, Property 6: Threshold-based matching decision**
        **Validates: Requirements 3.5, 3.6**
        
        For any computed distance and threshold value, if distance ≤ threshold then
        is_match should be true, otherwise is_match should be false.
        """
        # Create mock embeddings
        unknown_encoding = np.random.rand(128)
        known_encodings = [np.random.rand(128)]
        
        # Mock face_recognition.face_distance to return our controlled distance
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_fr.face_distance.return_value = np.array([distance])
            
            # Compare faces
            is_match, best_distance = compare_with_known_faces(
                unknown_encoding, known_encodings, threshold
            )
            
            # Verify the threshold-based decision
            if distance <= threshold:
                assert is_match is True, \
                    f"When distance ({distance}) ≤ threshold ({threshold}), is_match should be True"
            else:
                assert is_match is False, \
                    f"When distance ({distance}) > threshold ({threshold}), is_match should be False"
            
            # Verify best_distance matches the input distance
            assert abs(best_distance - distance) < 1e-6, \
                f"Best distance should match the computed distance"
    
    def test_no_face_detected_raises_error(self):
        """
        Test that extract_single_face_encoding raises ValueError when no face is detected.
        **Validates: Requirements 6.3**
        """
        mock_image_rgb = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        
        with patch('backend.face_processor.face_recognition') as mock_fr:
            # Mock to return no face locations
            mock_fr.face_locations.return_value = []
            
            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                extract_single_face_encoding(mock_image_rgb)
            
            assert "Không tìm thấy khuôn mặt" in str(exc_info.value)
    
    def test_multiple_faces_raises_error(self):
        """
        Test that extract_single_face_encoding raises ValueError when multiple faces detected.
        **Validates: Requirements 6.4**
        """
        mock_image_rgb = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        
        with patch('backend.face_processor.face_recognition') as mock_fr:
            # Mock to return multiple face locations
            mock_fr.face_locations.return_value = [
                (50, 150, 150, 50),
                (50, 300, 150, 200)
            ]
            
            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                extract_single_face_encoding(mock_image_rgb)
            
            assert "khuôn mặt trong ảnh" in str(exc_info.value)
            assert "CHỈ MỘT" in str(exc_info.value)
