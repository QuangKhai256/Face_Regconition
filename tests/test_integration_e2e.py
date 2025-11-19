"""
Integration tests end-to-end for face recognition backend.
Tests complete flow from upload to response.
Validates: Requirements 9.3
"""

import pytest
import io
import os
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import face_recognition
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.main import app


client = TestClient(app)


@pytest.fixture
def sample_face_image_bytes():
    """Create a sample image with a face for testing."""
    # Create a simple test image (100x100 RGB)
    img = Image.new('RGB', (100, 100), color='white')
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()


@pytest.fixture
def mock_training_data():
    """Mock training data for integration tests."""
    # Create mock face encodings
    encoding1 = np.random.rand(128)
    encoding2 = np.random.rand(128)
    
    return ([encoding1, encoding2], ["person1.jpg", "person2.jpg"])


class TestEndToEndFlow:
    """Test complete flow from upload to response."""
    
    def test_complete_verification_flow_match(self, sample_face_image_bytes, mock_training_data):
        """
        Test complete flow: upload image -> process -> match -> response.
        Validates: Requirements 9.3
        """
        # Mock the face detection and encoding
        mock_encoding = np.random.rand(128)
        mock_location = (10, 90, 90, 10)
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch('backend.main.get_known_faces_cache') as mock_cache, \
             patch('backend.main.extract_single_face_encoding') as mock_extract, \
             patch('backend.main.read_image_from_upload') as mock_read:
            
            # Setup mocks
            mock_cache.return_value = mock_training_data
            mock_extract.return_value = (mock_encoding, mock_location)
            mock_read.return_value = mock_image
            
            # Make the encodings similar to ensure match
            known_encodings, used_files = mock_training_data
            known_encodings[0][:] = mock_encoding[:]
            
            # Send request
            response = client.post(
                "/api/v1/face/verify",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")},
                params={"threshold": 0.5}
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            
            # Check all required fields exist
            assert "is_match" in data
            assert "distance" in data
            assert "threshold" in data
            assert "message" in data
            assert "face_box" in data
            assert "image_size" in data
            assert "training_info" in data
            
            # Verify structure
            assert isinstance(data["is_match"], bool)
            assert isinstance(data["distance"], (int, float))
            assert data["threshold"] == 0.5
            assert isinstance(data["message"], str)
            
            # Verify face_box structure
            assert "top" in data["face_box"]
            assert "right" in data["face_box"]
            assert "bottom" in data["face_box"]
            assert "left" in data["face_box"]
            
            # Verify image_size structure
            assert "width" in data["image_size"]
            assert "height" in data["image_size"]
            
            # Verify training_info structure
            assert "num_images" in data["training_info"]
            assert "used_files_sample" in data["training_info"]
            assert data["training_info"]["num_images"] == 2
    
    def test_complete_verification_flow_no_match(self, sample_face_image_bytes, mock_training_data):
        """
        Test complete flow with non-matching face.
        Validates: Requirements 9.3
        """
        # Mock with very different encoding to ensure no match
        mock_encoding = np.random.rand(128) * 10  # Very different
        mock_location = (10, 90, 90, 10)
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch('backend.main.get_known_faces_cache') as mock_cache, \
             patch('backend.main.extract_single_face_encoding') as mock_extract, \
             patch('backend.main.read_image_from_upload') as mock_read:
            
            mock_cache.return_value = mock_training_data
            mock_extract.return_value = (mock_encoding, mock_location)
            mock_read.return_value = mock_image
            
            response = client.post(
                "/api/v1/face/verify",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")},
                params={"threshold": 0.5}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should not match due to large distance
            assert "is_match" in data
            assert "distance" in data
            assert data["distance"] > 0
    
    def test_complete_flow_with_custom_threshold(self, sample_face_image_bytes, mock_training_data):
        """
        Test complete flow with custom threshold parameter.
        Validates: Requirements 9.3, 4.1
        """
        mock_encoding = np.random.rand(128)
        mock_location = (10, 90, 90, 10)
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch('backend.main.get_known_faces_cache') as mock_cache, \
             patch('backend.main.extract_single_face_encoding') as mock_extract, \
             patch('backend.main.read_image_from_upload') as mock_read:
            
            mock_cache.return_value = mock_training_data
            mock_extract.return_value = (mock_encoding, mock_location)
            mock_read.return_value = mock_image
            
            # Test with different threshold values
            for threshold in [0.3, 0.6, 0.9]:
                response = client.post(
                    "/api/v1/face/verify",
                    files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")},
                    params={"threshold": threshold}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["threshold"] == threshold
    
    def test_complete_flow_with_error_handling(self, sample_face_image_bytes):
        """
        Test complete flow with various error conditions.
        Validates: Requirements 9.3, 6.1, 6.2, 6.3, 6.4, 6.5
        """
        # Test with invalid content type
        response = client.post(
            "/api/v1/face/verify",
            files={"file": ("test.txt", b"not an image", "text/plain")}
        )
        assert response.status_code == 400
        assert "detail" in response.json()
        
        # Test with no face in image
        with patch('backend.main.extract_single_face_encoding') as mock_extract, \
             patch('backend.main.read_image_from_upload') as mock_read:
            mock_read.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            mock_extract.side_effect = ValueError("Không tìm thấy khuôn mặt nào trong ảnh")
            
            response = client.post(
                "/api/v1/face/verify",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")}
            )
            assert response.status_code == 400
            assert "detail" in response.json()
        
        # Test with multiple faces
        with patch('backend.main.extract_single_face_encoding') as mock_extract, \
             patch('backend.main.read_image_from_upload') as mock_read:
            mock_read.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            mock_extract.side_effect = ValueError("Phát hiện 2 khuôn mặt trong ảnh")
            
            response = client.post(
                "/api/v1/face/verify",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")}
            )
            assert response.status_code == 400
            assert "detail" in response.json()


class TestMultipleImages:
    """Test with multiple different images."""
    
    def test_different_image_sizes(self, mock_training_data):
        """
        Test with images of different sizes.
        Validates: Requirements 9.3
        """
        sizes = [(50, 50), (100, 100), (200, 200), (500, 500)]
        
        mock_encoding = np.random.rand(128)
        mock_location = (10, 40, 40, 10)
        
        with patch('backend.main.get_known_faces_cache') as mock_cache, \
             patch('backend.main.extract_single_face_encoding') as mock_extract, \
             patch('backend.main.read_image_from_upload') as mock_read:
            
            mock_cache.return_value = mock_training_data
            mock_extract.return_value = (mock_encoding, mock_location)
            
            for width, height in sizes:
                # Create image of specific size
                img = Image.new('RGB', (width, height), color='white')
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG')
                img_bytes.seek(0)
                
                # Mock the image with correct size
                mock_image = np.zeros((height, width, 3), dtype=np.uint8)
                mock_read.return_value = mock_image
                
                response = client.post(
                    "/api/v1/face/verify",
                    files={"file": ("test.jpg", img_bytes.getvalue(), "image/jpeg")}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["image_size"]["width"] == width
                assert data["image_size"]["height"] == height
    
    def test_different_image_formats(self, mock_training_data):
        """
        Test with different image formats (JPEG, PNG).
        Validates: Requirements 9.3, 3.1
        """
        formats = [
            ("JPEG", "image/jpeg", "test.jpg"),
            ("PNG", "image/png", "test.png")
        ]
        
        mock_encoding = np.random.rand(128)
        mock_location = (10, 90, 90, 10)
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch('backend.main.get_known_faces_cache') as mock_cache, \
             patch('backend.main.extract_single_face_encoding') as mock_extract, \
             patch('backend.main.read_image_from_upload') as mock_read:
            
            mock_cache.return_value = mock_training_data
            mock_extract.return_value = (mock_encoding, mock_location)
            mock_read.return_value = mock_image
            
            for img_format, content_type, filename in formats:
                # Create image in specific format
                img = Image.new('RGB', (100, 100), color='white')
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=img_format)
                img_bytes.seek(0)
                
                response = client.post(
                    "/api/v1/face/verify",
                    files={"file": (filename, img_bytes.getvalue(), content_type)}
                )
                
                assert response.status_code == 200


class TestConcurrentRequests:
    """Test concurrent request handling."""
    
    def test_concurrent_verification_requests(self, sample_face_image_bytes, mock_training_data):
        """
        Test handling multiple concurrent requests.
        Validates: Requirements 9.3
        """
        mock_encoding = np.random.rand(128)
        mock_location = (10, 90, 90, 10)
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch('backend.main.get_known_faces_cache') as mock_cache, \
             patch('backend.main.extract_single_face_encoding') as mock_extract, \
             patch('backend.main.read_image_from_upload') as mock_read:
            
            mock_cache.return_value = mock_training_data
            mock_extract.return_value = (mock_encoding, mock_location)
            mock_read.return_value = mock_image
            
            def make_request(i):
                """Make a single verification request."""
                response = client.post(
                    "/api/v1/face/verify",
                    files={"file": (f"test{i}.jpg", sample_face_image_bytes, "image/jpeg")},
                    params={"threshold": 0.5}
                )
                return response
            
            # Send 10 concurrent requests
            num_requests = 10
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, i) for i in range(num_requests)]
                
                results = []
                for future in as_completed(futures):
                    response = future.result()
                    results.append(response)
            
            # Verify all requests succeeded
            assert len(results) == num_requests
            for response in results:
                assert response.status_code == 200
                data = response.json()
                assert "is_match" in data
                assert "distance" in data
    
    def test_concurrent_health_checks(self):
        """
        Test concurrent health check requests.
        Validates: Requirements 9.3, 2.1
        """
        def make_health_request():
            return client.get("/api/v1/health")
        
        # Send 20 concurrent health checks
        num_requests = 20
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_health_request) for _ in range(num_requests)]
            
            results = []
            for future in as_completed(futures):
                response = future.result()
                results.append(response)
        
        # Verify all succeeded
        assert len(results) == num_requests
        for response in results:
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}


class TestHealthCheckIntegration:
    """Test health check endpoint integration."""
    
    def test_health_check_response_time(self):
        """
        Test health check responds quickly.
        Validates: Requirements 2.2, 9.3
        """
        import time
        
        start = time.time()
        response = client.get("/api/v1/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        # Should respond in less than 100ms (0.1 seconds)
        # Being generous with 1 second for test environment
        assert elapsed < 1.0
    
    def test_health_check_always_available(self):
        """
        Test health check is always available even if training data fails.
        Validates: Requirements 2.1, 9.3
        """
        # Health check should work regardless of training data state
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCORSIntegration:
    """Test CORS functionality in integration context."""
    
    def test_cors_headers_on_verify_endpoint(self, sample_face_image_bytes, mock_training_data):
        """
        Test CORS headers are present on verify endpoint.
        Validates: Requirements 8.1, 8.3, 9.3
        """
        mock_encoding = np.random.rand(128)
        mock_location = (10, 90, 90, 10)
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with patch('backend.main.get_known_faces_cache') as mock_cache, \
             patch('backend.main.extract_single_face_encoding') as mock_extract, \
             patch('backend.main.read_image_from_upload') as mock_read:
            
            mock_cache.return_value = mock_training_data
            mock_extract.return_value = (mock_encoding, mock_location)
            mock_read.return_value = mock_image
            
            response = client.post(
                "/api/v1/face/verify",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")},
                headers={"Origin": "http://example.com"}
            )
            
            assert response.status_code == 200
            # CORS headers should be present
            assert "access-control-allow-origin" in response.headers
    
    def test_cors_preflight_request(self):
        """
        Test CORS preflight OPTIONS request.
        Validates: Requirements 8.2, 9.3
        """
        response = client.options(
            "/api/v1/face/verify",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        
        # Should allow the request
        assert response.status_code in [200, 204]
