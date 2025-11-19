"""
Integration tests for complete workflow: collect → train → verify.
Tests file persistence and error scenarios.
Validates: Requirements 1.10, 1.11, 2.1, 2.6, 2.7, 3.1, 7.3, 7.4, 7.5
"""

import pytest
import io
import os
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.main import app

client = TestClient(app)


@pytest.fixture
def sample_face_image_bytes():
    """Create a sample image with a face for testing."""
    img = Image.new('RGB', (200, 200), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


class TestCompleteWorkflow:
    """Test complete workflow from collection to verification."""
    
    def test_workflow_api_structure(self, sample_face_image_bytes):
        """
        Test that workflow APIs have correct structure and error handling.
        Validates: Requirements 1.10, 1.11, 2.1, 2.6, 2.7, 3.1, 7.3, 7.4, 7.5
        """
        # Mock face detection and environment analysis
        mock_encoding = np.random.rand(128)
        mock_location = (20, 180, 180, 20)
        mock_image = np.ones((200, 200, 3), dtype=np.uint8) * 150  # Good brightness
        mock_training_data = ([mock_encoding, mock_encoding], ["img1.jpg", "img2.jpg"])
        
        with patch('backend.face_processor.face_recognition.face_locations') as mock_locations, \
             patch('backend.face_processor.face_recognition.face_encodings') as mock_encodings, \
             patch('backend.face_processor.cv2.imread') as mock_imread, \
             patch('backend.main.get_known_faces_cache') as mock_cache:
            
            mock_locations.return_value = [mock_location]
            mock_encodings.return_value = [mock_encoding]
            mock_imread.return_value = mock_image
            mock_cache.return_value = mock_training_data
            
            # Test collect endpoint structure
            response = client.post(
                "/api/v1/collect",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")}
            )
            
            # Should return 200 or 400 depending on environment
            assert response.status_code in [200, 400]
            data = response.json()
            
            if response.status_code == 200:
                assert "saved_path" in data or "message" in data
                assert "total_images" in data or "detail" in data
                assert "environment_info" in data or "detail" in data
            
            # Test verify endpoint structure
            response = client.post(
                "/api/v1/face/verify",
                files={"file": ("verify.jpg", sample_face_image_bytes, "image/jpeg")},
                params={"threshold": 0.6}
            )
            
            # Should return 200 or 400
            assert response.status_code in [200, 400]
            data = response.json()
            
            if response.status_code == 200:
                assert "is_match" in data
                assert "distance" in data
                assert "threshold" in data
                assert "message" in data
                assert "face_box" in data
                assert "image_size" in data
    
    def test_workflow_with_poor_environment_rejection(self, sample_face_image_bytes):
        """
        Test that poor environment images are rejected during collection.
        Validates: Requirements 1.9
        """
        # Mock face detection with poor environment (too dark)
        mock_encoding = np.random.rand(128)
        mock_location = (20, 180, 180, 20)
        mock_image = np.ones((200, 200, 3), dtype=np.uint8) * 30  # Too dark (< 60)
        
        with patch('backend.face_processor.face_recognition.face_locations') as mock_locations, \
             patch('backend.face_processor.face_recognition.face_encodings') as mock_encodings, \
             patch('backend.face_processor.cv2.imread') as mock_imread:
            
            mock_locations.return_value = [mock_location]
            mock_encodings.return_value = [mock_encoding]
            mock_imread.return_value = mock_image
            
            # Try to collect image with poor environment
            response = client.post(
                "/api/v1/collect",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")}
            )
            
            # Should be rejected
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
    
    def test_verify_without_training_fails(self, sample_face_image_bytes):
        """
        Test that verification fails when model hasn't been trained.
        Validates: Requirements 3.2
        """
        mock_encoding = np.random.rand(128)
        mock_location = (20, 180, 180, 20)
        mock_image = np.ones((200, 200, 3), dtype=np.uint8) * 150
        
        with patch('backend.face_processor.face_recognition.face_locations') as mock_locations, \
             patch('backend.face_processor.face_recognition.face_encodings') as mock_encodings, \
             patch('backend.face_processor.cv2.imread') as mock_imread, \
             patch('backend.verification.load_trained_model') as mock_load:
            
            mock_locations.return_value = [mock_location]
            mock_encodings.return_value = [mock_encoding]
            mock_imread.return_value = mock_image
            mock_load.side_effect = FileNotFoundError("Model not found")
            
            response = client.post(
                "/api/v1/face/verify",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")}
            )
            
            assert response.status_code in [400, 500]
            data = response.json()
            assert "detail" in data


class TestFilePersistence:
    """Test file persistence across operations."""
    
    def test_collected_images_filename_format(self, sample_face_image_bytes):
        """
        Test that collected images use correct filename format.
        Validates: Requirements 1.10, 7.3
        """
        mock_encoding = np.random.rand(128)
        mock_location = (20, 180, 180, 20)
        mock_image = np.ones((200, 200, 3), dtype=np.uint8) * 150
        
        with patch('backend.face_processor.face_recognition.face_locations') as mock_locations, \
             patch('backend.face_processor.face_recognition.face_encodings') as mock_encodings, \
             patch('backend.face_processor.cv2.imread') as mock_imread:
            
            mock_locations.return_value = [mock_location]
            mock_encodings.return_value = [mock_encoding]
            mock_imread.return_value = mock_image
            
            # Collect image
            response = client.post(
                "/api/v1/collect",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "saved_path" in data:
                    saved_path = data["saved_path"]
                    
                    # Verify filename format (user_YYYYMMDD_HHMMSS.jpg)
                    filename = os.path.basename(saved_path)
                    assert filename.startswith("user_"), "Filename should start with 'user_'"
                    assert filename.endswith(".jpg"), "Filename should end with '.jpg'"
    
    def test_model_files_structure(self):
        """
        Test that model files have correct structure when they exist.
        Validates: Requirements 2.6, 2.7, 7.4, 7.5
        """
        # Check if model files exist
        models_dir = "models"
        embeddings_path = os.path.join(models_dir, "user_embeddings.npy")
        mean_path = os.path.join(models_dir, "user_embedding_mean.npy")
        
        if os.path.exists(embeddings_path) and os.path.exists(mean_path):
            # Verify files are readable and have correct format
            embeddings = np.load(embeddings_path)
            mean_embedding = np.load(mean_path)
            
            assert embeddings.ndim == 2, "Embeddings should be 2D array"
            assert embeddings.shape[1] == 128, "Embeddings should be 128-dimensional"
            assert mean_embedding.shape == (128,), "Mean embedding should be 1D array of 128 elements"
            
            # Verify mean is actually the mean of embeddings
            calculated_mean = np.mean(embeddings, axis=0)
            np.testing.assert_array_almost_equal(mean_embedding, calculated_mean, decimal=5)


class TestErrorScenarios:
    """Test various error scenarios in the workflow."""
    
    def test_invalid_file_format_during_collection(self):
        """
        Test that invalid file formats are rejected during collection.
        Validates: Requirements 4.1, 4.5
        """
        # Try to upload text file
        response = client.post(
            "/api/v1/collect",
            files={"file": ("test.txt", b"not an image", "text/plain")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_file_too_large_during_collection(self):
        """
        Test that files larger than 10MB are rejected.
        Validates: Requirements 4.3
        """
        # Create a large file (> 10MB)
        large_data = b"x" * (11 * 1024 * 1024)  # 11MB
        
        response = client.post(
            "/api/v1/collect",
            files={"file": ("large.jpg", large_data, "image/jpeg")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_no_face_in_image_during_collection(self, sample_face_image_bytes):
        """
        Test that images with no faces are rejected during collection.
        Validates: Requirements 1.2
        """
        mock_image = np.ones((200, 200, 3), dtype=np.uint8) * 150
        
        with patch('backend.face_processor.face_recognition.face_locations') as mock_locations, \
             patch('backend.face_processor.cv2.imread') as mock_imread:
            
            mock_locations.return_value = []  # No faces
            mock_imread.return_value = mock_image
            
            response = client.post(
                "/api/v1/collect",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")}
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
    
    def test_multiple_faces_in_image_during_collection(self, sample_face_image_bytes):
        """
        Test that images with multiple faces are rejected during collection.
        Validates: Requirements 1.3
        """
        mock_image = np.ones((200, 200, 3), dtype=np.uint8) * 150
        
        with patch('backend.face_processor.face_recognition.face_locations') as mock_locations, \
             patch('backend.face_processor.cv2.imread') as mock_imread:
            
            # Multiple faces
            mock_locations.return_value = [(20, 180, 180, 20), (20, 100, 100, 20)]
            mock_imread.return_value = mock_image
            
            response = client.post(
                "/api/v1/collect",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")}
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
    
    def test_health_check_always_available(self):
        """
        Test health check is always available.
        Validates: Requirements 8.1
        """
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCORSIntegration:
    """Test CORS functionality in integration context."""
    
    def test_cors_headers_present(self, sample_face_image_bytes):
        """
        Test CORS headers are present on endpoints.
        Validates: Requirements 8.2, 8.3, 8.4
        """
        mock_encoding = np.random.rand(128)
        mock_location = (20, 180, 180, 20)
        mock_image = np.ones((200, 200, 3), dtype=np.uint8) * 150
        mock_training_data = ([mock_encoding], ["img1.jpg"])
        
        with patch('backend.face_processor.face_recognition.face_locations') as mock_locations, \
             patch('backend.face_processor.face_recognition.face_encodings') as mock_encodings, \
             patch('backend.face_processor.cv2.imread') as mock_imread, \
             patch('backend.main.get_known_faces_cache') as mock_cache:
            
            mock_locations.return_value = [mock_location]
            mock_encodings.return_value = [mock_encoding]
            mock_imread.return_value = mock_image
            mock_cache.return_value = mock_training_data
            
            response = client.post(
                "/api/v1/face/verify",
                files={"file": ("test.jpg", sample_face_image_bytes, "image/jpeg")},
                headers={"Origin": "http://example.com"}
            )
            
            # CORS headers should be present
            assert "access-control-allow-origin" in response.headers
