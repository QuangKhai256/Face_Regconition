"""
Face recognition logic module.
Handles face processing and comparison functions.
"""

import numpy as np
import cv2
import face_recognition
from typing import Tuple, List


def read_image_from_upload(file_bytes: bytes) -> np.ndarray:
    """
    Chuyển đổi bytes từ upload thành numpy array (BGR format).
    
    Args:
        file_bytes: Dữ liệu ảnh dạng bytes
        
    Returns:
        image_bgr: Ảnh dạng numpy array (BGR)
        
    Raises:
        ValueError: Nếu không đọc được ảnh
    """
    try:
        # Chuyển bytes thành numpy array
        nparr = np.frombuffer(file_bytes, np.uint8)
        
        # Decode thành ảnh BGR
        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image_bgr is None:
            raise ValueError("Không đọc được ảnh từ dữ liệu upload. Đảm bảo file là ảnh hợp lệ.")
        
        return image_bgr
        
    except Exception as e:
        raise ValueError(f"Không đọc được ảnh từ dữ liệu upload: {str(e)}")


def extract_single_face_encoding(
    image_rgb: np.ndarray
) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """
    Trích xuất face embedding từ ảnh chứa đúng 1 khuôn mặt.
    
    Args:
        image_rgb: Ảnh dạng RGB numpy array
        
    Returns:
        - encoding: Face embedding (128-d vector)
        - location: Tọa độ khuôn mặt (top, right, bottom, left)
        
    Raises:
        ValueError: Nếu không có hoặc có nhiều hơn 1 khuôn mặt
    """
    # Tìm vị trí khuôn mặt
    face_locations = face_recognition.face_locations(image_rgb)
    
    # Validate số lượng khuôn mặt
    if len(face_locations) == 0:
        raise ValueError(
            "Không tìm thấy khuôn mặt nào trong ảnh. "
            "Hãy để mặt của bạn chiếm phần lớn khung hình và đảm bảo ánh sáng đủ."
        )
    
    if len(face_locations) > 1:
        raise ValueError(
            f"Phát hiện {len(face_locations)} khuôn mặt trong ảnh. "
            f"Vui lòng để CHỈ MỘT người trong ảnh để xác thực chính xác."
        )
    
    # Trích xuất face embedding
    face_encodings = face_recognition.face_encodings(image_rgb, face_locations)
    
    if len(face_encodings) == 0:
        raise ValueError(
            "Không trích xuất được vector đặc trưng cho khuôn mặt. "
            "Hãy thử với ảnh rõ nét hơn."
        )
    
    return face_encodings[0], face_locations[0]


def compare_with_known_faces(
    unknown_encoding: np.ndarray,
    known_encodings: List[np.ndarray],
    threshold: float
) -> Tuple[bool, float]:
    """
    So sánh khuôn mặt mới với dữ liệu đã học.
    
    Args:
        unknown_encoding: Face embedding của ảnh cần xác thực
        known_encodings: Danh sách face embeddings từ training data
        threshold: Ngưỡng để xác định khớp
        
    Returns:
        - is_match: True nếu khớp, False nếu không
        - best_distance: Khoảng cách nhỏ nhất tìm được
    """
    # Tính khoảng cách Euclidean với tất cả face embeddings
    distances = face_recognition.face_distance(known_encodings, unknown_encoding)
    
    # Lấy khoảng cách nhỏ nhất
    best_distance = float(np.min(distances))
    
    # So sánh với threshold
    is_match = best_distance <= threshold
    
    return is_match, best_distance
