"""
Debug test for collection endpoint
"""
import io
import numpy as np
import cv2
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.main import app

client = TestClient(app)

def test_simple_collection():
    """Simple test to debug collection endpoint"""
    # Create a simple image
    image_bgr = np.full((200, 200, 3), 100, dtype=np.uint8)
    
    # Add pattern for blur score
    for i in range(0, 200, 2):
        for j in range(0, 200, 2):
            if (i + j) % 4 == 0:
                image_bgr[i:i+2, j:j+2] = 150
            else:
                image_bgr[i:i+2, j:j+2] = 50
    
    # Encode as JPEG
    success, encoded = cv2.imencode('.jpg', image_bgr)
    image_bytes = encoded.tobytes()
    
    # Mock face detection
    face_box = (50, 150, 150, 50)
    
    with patch('backend.main.extract_single_face_encoding') as mock_extract, \
         patch('backend.main.analyze_environment') as mock_analyze:
        
        mock_encoding = np.random.rand(128)
        mock_extract.return_value = (mock_encoding, face_box)
        
        mock_analyze.return_value = {
            'brightness': 100.0,
            'is_too_dark': False,
            'is_too_bright': False,
            'blur_score': 120.0,
            'is_too_blurry': False,
            'face_size_ratio': 0.25,
            'is_face_too_small': False,
            'warnings': []
        }
        
        # Create file upload
        files = {
            "file": ("test.jpg", io.BytesIO(image_bytes), "image/jpeg")
        }
        
        # Call endpoint
        print("Calling endpoint...")
        response = client.post("/api/v1/collect", files=files)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        assert response.status_code == 200

if __name__ == "__main__":
    test_simple_collection()
    print("Test passed!")
