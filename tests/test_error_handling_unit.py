"""
Unit tests for error handling.
Tests specific error scenarios and edge cases.
"""

import os
import shutil
import tempfile
import pytest
from fastapi.testclient import TestClient
import io
from PIL import Image, ImageDraw
from unittest.mock import patch, MagicMock
import numpy as np

from backend.main import app

client = TestClient(app)


def create_simple_image(format='JPEG', size=(200, 200)):
    """Helper to create a simple test image"""
    img = Image.new('RGB', size, color='blue')
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


class TestErrorHandlingUnit:
    """Unit tests for error handling scenarios."""
    
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
    
    # ========================================================================
    # Test xử lý thư mục myface/ không tồn tại
    # Validates: Requirements 1.5
    # ========================================================================
    
    def test_myface_directory_not_exists(self, temp_myface_dir):
        """
        Test xử lý thư mục myface/ không tồn tại.
        **Validates: Requirements 1.5**
        """
        # Clear cache
        from backend.data_loader import get_known_faces_cache
        get_known_faces_cache.cache_clear()
        
        # Remove myface directory
        if os.path.exists("myface"):
            shutil.rmtree("myface")
        
        # Mock face_recognition to simulate finding a face in the uploaded image
        # This way we get past the face detection and hit the training data loading error
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_fr.face_locations.return_value = [(50, 150, 150, 50)]
            mock_fr.face_encodings.return_value = [np.random.rand(128)]
            
            img_bytes = create_simple_image()
            files = {
                "file": ("test.jpg", img_bytes, "image/jpeg")
            }
            
            response = client.post("/api/v1/face/verify", files=files)
            
            # Should get 500 error when trying to load training data
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "không tồn tại" in data["detail"].lower()
        
        # Restore directory
        os.makedirs("myface", exist_ok=True)
    
    # ========================================================================
    # Test xử lý thư mục myface/ rỗng
    # Validates: Requirements 1.5
    # ========================================================================
    
    def test_myface_directory_empty(self, temp_myface_dir):
        """
        Test xử lý thư mục myface/ rỗng.
        **Validates: Requirements 1.5**
        """
        # Clear cache
        from backend.data_loader import get_known_faces_cache
        get_known_faces_cache.cache_clear()
        
        # Ensure directory is empty
        assert len(os.listdir(temp_myface_dir)) == 0
        
        # Mock face_recognition to simulate finding a face in the uploaded image
        with patch('backend.face_processor.face_recognition') as mock_fr:
            mock_fr.face_locations.return_value = [(50, 150, 150, 50)]
            mock_fr.face_encodings.return_value = [np.random.rand(128)]
            
            img_bytes = create_simple_image()
            files = {
                "file": ("test.jpg", img_bytes, "image/jpeg")
            }
            
            response = client.post("/api/v1/face/verify", files=files)
            
            # Empty directory raises ValueError, which returns 400
            # (Requirement 1.5 says ValueError, Requirement 7.2 says ValueError -> 400)
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "không tìm thấy ảnh hợp lệ" in data["detail"].lower() or \
                   "không thể trích xuất" in data["detail"].lower()
    
    # ========================================================================
    # Test xử lý file upload không hợp lệ
    # Validates: Requirements 6.1
    # ========================================================================
    
    def test_invalid_file_upload_content_type(self):
        """
        Test xử lý file upload không hợp lệ (content-type).
        **Validates: Requirements 6.1**
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
    
    def test_invalid_file_upload_pdf(self):
        """
        Test xử lý file upload PDF.
        **Validates: Requirements 6.1**
        """
        files = {
            "file": ("test.pdf", io.BytesIO(b"PDF content"), "application/pdf")
        }
        
        response = client.post("/api/v1/face/verify", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "ảnh" in data["detail"].lower() or ".jpg" in data["detail"].lower()
    
    # ========================================================================
    # Test xử lý ảnh bị hỏng
    # Validates: Requirements 6.2
    # ========================================================================
    
    def test_corrupted_image_data(self):
        """
        Test xử lý ảnh bị hỏng.
        **Validates: Requirements 6.2**
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
    
    def test_empty_image_data(self):
        """
        Test xử lý ảnh rỗng.
        **Validates: Requirements 6.2**
        """
        files = {
            "file": ("test.jpg", io.BytesIO(b""), "image/jpeg")
        }
        
        response = client.post("/api/v1/face/verify", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_partially_corrupted_image(self):
        """
        Test xử lý ảnh bị hỏng một phần.
        **Validates: Requirements 6.2**
        """
        # Create a valid image then corrupt it
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        
        # Corrupt the data by truncating it
        corrupted_data = img_bytes.getvalue()[:50]
        
        files = {
            "file": ("test.jpg", io.BytesIO(corrupted_data), "image/jpeg")
        }
        
        response = client.post("/api/v1/face/verify", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    # ========================================================================
    # Test xử lý ảnh không có khuôn mặt
    # Validates: Requirements 6.3
    # ========================================================================
    
    def test_image_with_no_face(self):
        """
        Test xử lý ảnh không có khuôn mặt.
        **Validates: Requirements 6.3**
        """
        # Create a simple image without face
        img_bytes = create_simple_image()
        files = {
            "file": ("test.jpg", img_bytes, "image/jpeg")
        }
        
        response = client.post("/api/v1/face/verify", files=files)
        
        # Should get 400 error
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "không tìm thấy khuôn mặt" in data["detail"].lower()
    
    def test_landscape_image_no_face(self):
        """
        Test xử lý ảnh phong cảnh không có khuôn mặt.
        **Validates: Requirements 6.3**
        """
        # Create a landscape image
        img = Image.new('RGB', (800, 600), color='green')
        draw = ImageDraw.Draw(img)
        # Draw some landscape elements (trees, sky, etc.)
        draw.rectangle([0, 0, 800, 300], fill='skyblue')  # Sky
        draw.rectangle([0, 300, 800, 600], fill='green')  # Ground
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {
            "file": ("landscape.jpg", img_bytes, "image/jpeg")
        }
        
        response = client.post("/api/v1/face/verify", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "không tìm thấy khuôn mặt" in data["detail"].lower()
    
    # ========================================================================
    # Test xử lý ảnh có nhiều khuôn mặt
    # Validates: Requirements 6.4
    # ========================================================================
    
    def test_image_with_multiple_faces_mocked(self):
        """
        Test xử lý ảnh có nhiều khuôn mặt (mocked).
        **Validates: Requirements 6.4**
        """
        img_bytes = create_simple_image()
        files = {
            "file": ("test.jpg", img_bytes, "image/jpeg")
        }
        
        # Mock face_recognition to return multiple faces
        with patch('backend.face_processor.face_recognition') as mock_fr:
            # Mock face_locations to return 3 faces
            mock_fr.face_locations.return_value = [
                (50, 150, 150, 50),
                (50, 300, 150, 200),
                (200, 150, 300, 50)
            ]
            
            response = client.post("/api/v1/face/verify", files=files)
            
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            error_msg = data["detail"]
            assert "khuôn mặt" in error_msg.lower()
            assert "chỉ một" in error_msg.lower() or "CHỈ MỘT" in error_msg
    
    # ========================================================================
    # Test xử lý threshold không hợp lệ
    # Validates: Requirements 4.4
    # ========================================================================
    
    def test_threshold_below_zero(self):
        """
        Test xử lý threshold < 0.
        **Validates: Requirements 4.4**
        """
        img_bytes = create_simple_image()
        files = {
            "file": ("test.jpg", img_bytes, "image/jpeg")
        }
        
        response = client.post("/api/v1/face/verify?threshold=-0.5", files=files)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_threshold_above_one(self):
        """
        Test xử lý threshold > 1.
        **Validates: Requirements 4.4**
        """
        img_bytes = create_simple_image()
        files = {
            "file": ("test.jpg", img_bytes, "image/jpeg")
        }
        
        response = client.post("/api/v1/face/verify?threshold=2.0", files=files)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_threshold_invalid_string(self):
        """
        Test xử lý threshold với giá trị string không hợp lệ.
        **Validates: Requirements 4.4**
        """
        img_bytes = create_simple_image()
        files = {
            "file": ("test.jpg", img_bytes, "image/jpeg")
        }
        
        response = client.post("/api/v1/face/verify?threshold=invalid", files=files)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    # ========================================================================
    # Additional error handling tests
    # ========================================================================
    
    def test_missing_file_parameter(self):
        """
        Test xử lý khi thiếu file parameter.
        **Validates: Requirements 7.3**
        """
        response = client.post("/api/v1/face/verify")
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_error_response_format_consistency(self):
        """
        Test tất cả error responses có format nhất quán.
        **Validates: Requirements 7.3**
        """
        # Test multiple error scenarios
        error_scenarios = [
            # Invalid content type
            {
                "files": {"file": ("test.txt", io.BytesIO(b"text"), "text/plain")},
                "expected_status": 400
            },
            # Invalid threshold
            {
                "files": {"file": ("test.jpg", create_simple_image(), "image/jpeg")},
                "params": "?threshold=-1",
                "expected_status": 422
            },
            # Corrupted image
            {
                "files": {"file": ("test.jpg", io.BytesIO(b"bad"), "image/jpeg")},
                "expected_status": 400
            }
        ]
        
        for scenario in error_scenarios:
            url = "/api/v1/face/verify"
            if "params" in scenario:
                url += scenario["params"]
            
            response = client.post(url, files=scenario["files"])
            
            # Check status code
            assert response.status_code == scenario["expected_status"]
            
            # Check JSON format
            assert response.headers.get("content-type", "").startswith("application/json")
            
            # Check detail field
            data = response.json()
            assert "detail" in data
            assert isinstance(data["detail"], str)
    
    def test_vietnamese_error_messages(self):
        """
        Test thông báo lỗi bằng tiếng Việt.
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
        """
        # Test invalid content type
        files = {"file": ("test.txt", io.BytesIO(b"text"), "text/plain")}
        response = client.post("/api/v1/face/verify", files=files)
        assert response.status_code == 400
        data = response.json()
        # Should contain Vietnamese characters or words
        assert any(word in data["detail"].lower() for word in ["ảnh", "file", "upload"])
        
        # Test corrupted image
        files = {"file": ("test.jpg", io.BytesIO(b"bad"), "image/jpeg")}
        response = client.post("/api/v1/face/verify", files=files)
        assert response.status_code == 400
        data = response.json()
        assert "đọc" in data["detail"].lower() or "ảnh" in data["detail"].lower()
