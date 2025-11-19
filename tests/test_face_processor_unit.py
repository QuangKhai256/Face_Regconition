"""
Unit tests for face processor module.
Tests specific edge cases and error conditions.
"""

import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from backend.face_processor import (
    read_image_from_upload,
    extract_single_face_encoding,
    compare_with_known_faces
)


class TestFaceProcessorUnit:
    """Unit tests for face processor edge cases."""
    
    def test_read_image_from_valid_bytes(self):
        """
        Test đọc ảnh từ bytes hợp lệ.
        **Validates: Requirements 6.2**
        """
        # Create a simple valid JPEG bytes
        # This is a minimal 1x1 pixel JPEG
        valid_jpeg_bytes = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
            0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
            0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
            0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C,
            0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D,
            0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20,
            0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27,
            0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34,
            0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4,
            0x00, 0x14, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0xFF, 0xDA, 0x00, 0x08,
            0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0x7F, 0xFF,
            0xD9
        ])
        
        # Should successfully decode
        image_bgr = read_image_from_upload(valid_jpeg_bytes)
        
        assert isinstance(image_bgr, np.ndarray), "Should return numpy array"
        assert len(image_bgr.shape) == 3, "Should be 3D array (H, W, C)"
        assert image_bgr.shape[2] == 3, "Should have 3 color channels (BGR)"
    
    def test_read_image_from_invalid_bytes(self):
        """
        Test đọc ảnh từ bytes không hợp lệ.
        **Validates: Requirements 6.2**
        """
        # Invalid bytes that cannot be decoded as image
        invalid_bytes = b"This is not an image"
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            read_image_from_upload(invalid_bytes)
        
        assert "Không đọc được ảnh" in str(exc_info.value)
    
    def test_extract_face_no_face_detected(self):
        """
        Test xử lý ảnh không có khuôn mặt.
        **Validates: Requirements 6.3**
        """
        # Create a mock RGB image
        mock_image_rgb = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        
        # Mock face_recognition to return no faces
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_fr.face_locations.return_value = []
            
            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                extract_single_face_encoding(mock_image_rgb)
            
            assert "Không tìm thấy khuôn mặt" in str(exc_info.value)
    
    def test_extract_face_multiple_faces_detected(self):
        """
        Test xử lý ảnh có nhiều khuôn mặt.
        **Validates: Requirements 6.4**
        """
        # Create a mock RGB image
        mock_image_rgb = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        
        # Mock face_recognition to return multiple faces
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_fr.face_locations.return_value = [
                (50, 150, 150, 50),
                (50, 300, 150, 200),
                (200, 150, 300, 50)
            ]
            
            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                extract_single_face_encoding(mock_image_rgb)
            
            error_msg = str(exc_info.value)
            assert "khuôn mặt trong ảnh" in error_msg
            assert "CHỈ MỘT" in error_msg
    
    def test_extract_face_no_encoding_extracted(self):
        """
        Test xử lý khi không trích xuất được face encoding.
        **Validates: Requirements 6.5**
        """
        # Create a mock RGB image
        mock_image_rgb = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        
        # Mock face_recognition
        with patch('backend.face_processor.face_recognition') as mock_fr:
            # Return one face location but no encodings
            mock_fr.face_locations.return_value = [(50, 150, 150, 50)]
            mock_fr.face_encodings.return_value = []
            
            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                extract_single_face_encoding(mock_image_rgb)
            
            assert "Không trích xuất được vector đặc trưng" in str(exc_info.value)
    
    def test_extract_face_success(self):
        """
        Test successful face extraction with one face.
        **Validates: Requirements 3.2**
        """
        # Create a mock RGB image
        mock_image_rgb = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        
        # Mock face_recognition
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_location = (50, 150, 150, 50)
            mock_encoding = np.random.rand(128)
            
            mock_fr.face_locations.return_value = [mock_location]
            mock_fr.face_encodings.return_value = [mock_encoding]
            
            # Should succeed
            encoding, location = extract_single_face_encoding(mock_image_rgb)
            
            assert isinstance(encoding, np.ndarray)
            assert encoding.shape == (128,)
            assert location == mock_location
    
    def test_compare_faces_match(self):
        """
        Test comparison when faces match (distance <= threshold).
        **Validates: Requirements 3.5**
        """
        unknown_encoding = np.random.rand(128)
        known_encodings = [np.random.rand(128) for _ in range(3)]
        threshold = 0.5
        
        # Mock face_recognition.face_distance to return distances with min < threshold
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_distances = np.array([0.3, 0.6, 0.7])  # min = 0.3 < 0.5
            mock_fr.face_distance.return_value = mock_distances
            
            is_match, best_distance = compare_with_known_faces(
                unknown_encoding, known_encodings, threshold
            )
            
            assert is_match is True
            assert best_distance == 0.3
    
    def test_compare_faces_no_match(self):
        """
        Test comparison when faces don't match (distance > threshold).
        **Validates: Requirements 3.6**
        """
        unknown_encoding = np.random.rand(128)
        known_encodings = [np.random.rand(128) for _ in range(3)]
        threshold = 0.5
        
        # Mock face_recognition.face_distance to return distances with min > threshold
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_distances = np.array([0.6, 0.7, 0.8])  # min = 0.6 > 0.5
            mock_fr.face_distance.return_value = mock_distances
            
            is_match, best_distance = compare_with_known_faces(
                unknown_encoding, known_encodings, threshold
            )
            
            assert is_match is False
            assert best_distance == 0.6
    
    def test_compare_faces_exact_threshold(self):
        """
        Test comparison when distance equals threshold (should match).
        **Validates: Requirements 3.5**
        """
        unknown_encoding = np.random.rand(128)
        known_encodings = [np.random.rand(128)]
        threshold = 0.5
        
        # Mock face_recognition.face_distance to return distance exactly at threshold
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_distances = np.array([0.5])  # exactly at threshold
            mock_fr.face_distance.return_value = mock_distances
            
            is_match, best_distance = compare_with_known_faces(
                unknown_encoding, known_encodings, threshold
            )
            
            # distance <= threshold, so should match
            assert is_match is True
            assert best_distance == 0.5
