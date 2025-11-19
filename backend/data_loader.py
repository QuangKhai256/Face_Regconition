"""
Training data loading and caching module.
Handles loading face embeddings from training images in the myface/ directory.
"""

import os
import logging
from functools import lru_cache
from typing import List, Tuple
import numpy as np
import face_recognition

logger = logging.getLogger(__name__)


def load_known_face_encodings() -> Tuple[List[np.ndarray], List[str]]:
    """
    Tải tất cả ảnh từ thư mục myface/ và trích xuất face embeddings.
    
    Returns:
        - known_encodings: Danh sách face embeddings (128-d vectors)
        - used_files: Danh sách tên file đã xử lý thành công
        
    Raises:
        - FileNotFoundError: Nếu thư mục myface/ không tồn tại
        - ValueError: Nếu không tìm thấy ảnh hợp lệ nào
    """
    myface_dir = "myface"
    logger.info(f"Đang tải dữ liệu huấn luyện từ thư mục '{myface_dir}/'...")
    
    # Kiểm tra thư mục tồn tại
    if not os.path.exists(myface_dir):
        logger.error(f"Thư mục '{myface_dir}/' không tồn tại")
        raise FileNotFoundError(f"Thư mục '{myface_dir}/' không tồn tại. Vui lòng tạo thư mục và thêm ảnh huấn luyện.")
    
    if not os.path.isdir(myface_dir):
        logger.error(f"'{myface_dir}/' không phải là thư mục")
        raise FileNotFoundError(f"'{myface_dir}/' không phải là thư mục.")
    
    # Các extension hợp lệ
    valid_extensions = {'.jpg', '.jpeg', '.png'}
    
    known_encodings = []
    used_files = []
    
    # Quét thư mục và filter file theo extension
    image_files = [
        f for f in os.listdir(myface_dir)
        if os.path.isfile(os.path.join(myface_dir, f)) and
        os.path.splitext(f.lower())[1] in valid_extensions
    ]
    
    if not image_files:
        logger.error(f"Không tìm thấy ảnh hợp lệ nào trong thư mục '{myface_dir}/'")
        raise ValueError(f"Không tìm thấy ảnh hợp lệ nào trong thư mục '{myface_dir}/'. "
                        f"Vui lòng thêm ảnh với định dạng .jpg, .jpeg, hoặc .png")
    
    logger.info(f"Tìm thấy {len(image_files)} file ảnh: {image_files}")
    
    # Xử lý từng ảnh
    for filename in image_files:
        filepath = os.path.join(myface_dir, filename)
        
        try:
            # Tải ảnh
            image = face_recognition.load_image_file(filepath)
            
            # Tìm vị trí khuôn mặt
            face_locations = face_recognition.face_locations(image)
            
            # Bỏ qua ảnh nếu không có hoặc có nhiều hơn 1 khuôn mặt
            if len(face_locations) == 0:
                logger.warning(f"Không tìm thấy khuôn mặt trong '{filename}'. Bỏ qua.")
                continue
            elif len(face_locations) > 1:
                logger.warning(f"Phát hiện {len(face_locations)} khuôn mặt trong '{filename}'. Bỏ qua.")
                continue
            
            # Trích xuất face embedding
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if len(face_encodings) > 0:
                known_encodings.append(face_encodings[0])
                used_files.append(filename)
                logger.info(f"Đã tải thành công: {filename}")
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý '{filename}': {str(e)}. Bỏ qua.")
            continue
    
    # Kiểm tra có ít nhất 1 ảnh hợp lệ
    if len(known_encodings) == 0:
        logger.error(f"Không thể trích xuất face embedding từ bất kỳ ảnh nào trong '{myface_dir}/'")
        raise ValueError(f"Không thể trích xuất face embedding từ bất kỳ ảnh nào trong '{myface_dir}/'. "
                        f"Đảm bảo mỗi ảnh chứa đúng một khuôn mặt rõ ràng.")
    
    logger.info(f"Đã tải {len(known_encodings)} ảnh huấn luyện thành công.")
    return known_encodings, used_files


@lru_cache(maxsize=1)
def get_known_faces_cache() -> Tuple[List[np.ndarray], List[str]]:
    """
    Cached version của load_known_face_encodings để tránh tải lại.
    
    Returns:
        - known_encodings: Danh sách face embeddings (128-d vectors)
        - used_files: Danh sách tên file đã xử lý thành công
    """
    return load_known_face_encodings()
