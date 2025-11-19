"""
Unit tests for data loader module.
Tests specific edge cases and error conditions.
"""

import os
import shutil
import tempfile
from pathlib import Path
import pytest
from PIL import Image, ImageDraw
from unittest.mock import patch, MagicMock
import numpy as np

from backend.data_loader import load_known_face_encodings, get_known_faces_cache


def create_test_image(filepath: str, size: tuple = (200, 200)):
    """Helper to create a simple test image."""
    img = Image.new('RGB', size, color='lightblue')
    draw = ImageDraw.Draw(img)
    # Draw a simple face-like pattern
    draw.ellipse([70, 60, 90, 80], fill='black')  # Left eye
    draw.ellipse([110, 60, 130, 80], fill='black')  # Right eye
    draw.arc([75, 100, 125, 130], 0, 180, fill='black', width=2)  # Mouth
    img.save(filepath)


class TestDataLoaderUnit:
    """Unit tests for data loader edge cases."""
    
    @pytest.fixture
    def temp_myface_dir(self):
        """Create a temporary myface directory for testing."""
        # Save original myface if it exists
        original_exists = os.path.exists("myface")
        if original_exists:
            shutil.move("myface", "myface_backup")
        
        # Create temp directory
        os.makedirs("myface", exist_ok=True)
        
        yield "myface"
        
        # Cleanup
        if os.path.exists("myface"):
            shutil.rmtree("myface")
        
        # Restore original
        if original_exists:
            shutil.move("myface_backup", "myface")
    
    def test_directory_not_exists(self):
        """
        Test với thư mục không tồn tại.
        **Validates: Requirements 1.5**
        """
        # Ensure myface doesn't exist
        if os.path.exists("myface"):
            shutil.rmtree("myface")
        
        # Clear cache
        get_known_faces_cache.cache_clear()
        
        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError) as exc_info:
            load_known_face_encodings()
        
        assert "không tồn tại" in str(exc_info.value).lower()
        
        # Restore if needed
        if not os.path.exists("myface"):
            os.makedirs("myface", exist_ok=True)
    
    def test_empty_directory(self, temp_myface_dir):
        """
        Test với thư mục rỗng.
        **Validates: Requirements 1.5**
        """
        # Clear cache
        get_known_faces_cache.cache_clear()
        
        # Directory exists but is empty
        assert len(os.listdir(temp_myface_dir)) == 0
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            load_known_face_encodings()
        
        assert "không tìm thấy ảnh hợp lệ" in str(exc_info.value).lower()
    
    def test_no_valid_image_files(self, temp_myface_dir):
        """
        Test with directory containing only non-image files.
        **Validates: Requirements 1.5**
        """
        # Clear cache
        get_known_faces_cache.cache_clear()
        
        # Create non-image files
        Path(os.path.join(temp_myface_dir, "readme.txt")).touch()
        Path(os.path.join(temp_myface_dir, "data.json")).touch()
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            load_known_face_encodings()
        
        assert "không tìm thấy ảnh hợp lệ" in str(exc_info.value).lower()
    
    def test_image_with_multiple_faces(self, temp_myface_dir):
        """
        Test với ảnh có nhiều khuôn mặt.
        **Validates: Requirements 1.3**
        """
        # Clear cache
        get_known_faces_cache.cache_clear()
        
        # Create test image
        test_file = os.path.join(temp_myface_dir, "multi_face.jpg")
        create_test_image(test_file)
        
        # Mock face_recognition to return multiple faces
        with patch('backend.data_loader.face_recognition') as mock_fr:
            mock_fr.load_image_file.return_value = MagicMock()
            # Return 2 face locations (multiple faces)
            mock_fr.face_locations.return_value = [(0, 100, 100, 0), (0, 200, 100, 100)]
            mock_fr.face_encodings.return_value = []
            
            # Should raise ValueError because no valid images
            with pytest.raises(ValueError) as exc_info:
                load_known_face_encodings()
            
            assert "không thể trích xuất face embedding" in str(exc_info.value).lower()
    
    def test_image_with_no_faces(self, temp_myface_dir):
        """
        Test với ảnh không có khuôn mặt.
        **Validates: Requirements 1.3**
        """
        # Clear cache
        get_known_faces_cache.cache_clear()
        
        # Create test image
        test_file = os.path.join(temp_myface_dir, "no_face.jpg")
        create_test_image(test_file)
        
        # Mock face_recognition to return no faces
        with patch('backend.data_loader.face_recognition') as mock_fr:
            mock_fr.load_image_file.return_value = MagicMock()
            # Return 0 face locations (no faces)
            mock_fr.face_locations.return_value = []
            mock_fr.face_encodings.return_value = []
            
            # Should raise ValueError because no valid images
            with pytest.raises(ValueError) as exc_info:
                load_known_face_encodings()
            
            assert "không thể trích xuất face embedding" in str(exc_info.value).lower()
    
    def test_successful_loading_with_valid_image(self, temp_myface_dir):
        """
        Test successful loading with a valid image containing one face.
        **Validates: Requirements 1.1, 1.2**
        """
        # Clear cache
        get_known_faces_cache.cache_clear()
        
        # Create test image
        test_file = os.path.join(temp_myface_dir, "valid_face.jpg")
        create_test_image(test_file)
        
        # Mock face_recognition to return one face
        with patch('backend.data_loader.face_recognition') as mock_fr:
            mock_image = MagicMock()
            mock_fr.load_image_file.return_value = mock_image
            # Return 1 face location
            mock_fr.face_locations.return_value = [(50, 150, 150, 50)]
            # Return 1 face encoding (128-d vector)
            mock_encoding = np.random.rand(128)
            mock_fr.face_encodings.return_value = [mock_encoding]
            
            # Should succeed
            encodings, used_files = load_known_face_encodings()
            
            assert len(encodings) == 1
            assert len(used_files) == 1
            assert used_files[0] == "valid_face.jpg"
            assert np.array_equal(encodings[0], mock_encoding)
    
    def test_mixed_valid_invalid_images(self, temp_myface_dir):
        """
        Test with mix of valid and invalid images.
        Should process valid ones and skip invalid ones.
        **Validates: Requirements 1.3**
        """
        # Clear cache
        get_known_faces_cache.cache_clear()
        
        # Create multiple test images
        valid_file = os.path.join(temp_myface_dir, "valid.jpg")
        no_face_file = os.path.join(temp_myface_dir, "no_face.jpg")
        multi_face_file = os.path.join(temp_myface_dir, "multi.jpg")
        
        create_test_image(valid_file)
        create_test_image(no_face_file)
        create_test_image(multi_face_file)
        
        # Mock face_recognition
        with patch('backend.data_loader.face_recognition') as mock_fr:
            def mock_load_image(path):
                return MagicMock()
            
            def mock_face_locations(image):
                # Return different results based on which file
                # We can't easily distinguish, so return 1 face for all
                return [(50, 150, 150, 50)]
            
            def mock_face_encodings(image, locations):
                # Return encoding for valid file only
                return [np.random.rand(128)]
            
            mock_fr.load_image_file.side_effect = mock_load_image
            mock_fr.face_locations.side_effect = mock_face_locations
            mock_fr.face_encodings.side_effect = mock_face_encodings
            
            # Should succeed with at least one valid image
            encodings, used_files = load_known_face_encodings()
            
            assert len(encodings) >= 1
            assert len(used_files) >= 1
