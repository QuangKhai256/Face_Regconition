"""
Training module for face recognition model.
Handles training data loading, embedding extraction, and model persistence.
"""

import os
import logging
import numpy as np
import face_recognition
from typing import Tuple

logger = logging.getLogger(__name__)


def train_personal_model() -> Tuple[int, int]:
    """
    Huấn luyện mô hình cá nhân từ dữ liệu đã thu thập.
    
    Đọc tất cả ảnh từ thư mục data/raw/user/, trích xuất face embeddings,
    tính embedding trung bình, và lưu vào file models/.
    
    Returns:
        - num_images: Số lượng ảnh đã đọc
        - num_embeddings: Số lượng embeddings đã trích xuất thành công
        
    Raises:
        - FileNotFoundError: Nếu thư mục data/raw/user/ không tồn tại hoặc rỗng
        - ValueError: Nếu không trích xuất được embedding nào
        
    Validates: Requirements 2.1, 2.3, 2.4, 2.5, 2.6, 2.7, 7.4, 7.5
    """
    data_dir = "data/raw/user"
    models_dir = "models"
    
    logger.info(f"Bắt đầu huấn luyện mô hình từ thư mục '{data_dir}/'...")
    
    # Kiểm tra thư mục tồn tại
    if not os.path.exists(data_dir):
        logger.error(f"Thư mục '{data_dir}/' không tồn tại")
        raise FileNotFoundError(
            f"Thư mục '{data_dir}/' không tồn tại. "
            f"Vui lòng thu thập ảnh trước khi huấn luyện."
        )
    
    if not os.path.isdir(data_dir):
        logger.error(f"'{data_dir}/' không phải là thư mục")
        raise FileNotFoundError(f"'{data_dir}/' không phải là thư mục.")
    
    # Các extension hợp lệ
    valid_extensions = {'.jpg', '.jpeg', '.png'}
    
    # Quét thư mục và filter file theo extension
    image_files = [
        f for f in os.listdir(data_dir)
        if os.path.isfile(os.path.join(data_dir, f)) and
        os.path.splitext(f.lower())[1] in valid_extensions
    ]
    
    num_images = len(image_files)
    
    if num_images == 0:
        logger.error(f"Không tìm thấy ảnh nào trong thư mục '{data_dir}/'")
        raise FileNotFoundError(
            f"Không tìm thấy ảnh nào trong thư mục '{data_dir}/'. "
            f"Vui lòng thu thập ảnh trước khi huấn luyện."
        )
    
    logger.info(f"Tìm thấy {num_images} file ảnh: {image_files}")
    
    # Danh sách để lưu embeddings
    embeddings = []
    
    # Xử lý từng ảnh
    for filename in image_files:
        filepath = os.path.join(data_dir, filename)
        
        try:
            # Tải ảnh
            image = face_recognition.load_image_file(filepath)
            
            # Tìm vị trí khuôn mặt
            face_locations = face_recognition.face_locations(image)
            
            # Bỏ qua ảnh nếu không có hoặc có nhiều hơn 1 khuôn mặt
            if len(face_locations) == 0:
                logger.warning(
                    f"Không tìm thấy khuôn mặt trong '{filename}'. Bỏ qua."
                )
                continue
            elif len(face_locations) > 1:
                logger.warning(
                    f"Phát hiện {len(face_locations)} khuôn mặt trong '{filename}'. Bỏ qua."
                )
                continue
            
            # Trích xuất face embedding
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if len(face_encodings) > 0:
                embeddings.append(face_encodings[0])
                logger.info(f"Đã trích xuất embedding từ: {filename}")
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý '{filename}': {str(e)}. Bỏ qua.")
            continue
    
    num_embeddings = len(embeddings)
    
    # Kiểm tra có ít nhất 1 embedding
    if num_embeddings == 0:
        logger.error(
            f"Không thể trích xuất face embedding từ bất kỳ ảnh nào trong '{data_dir}/'"
        )
        raise ValueError(
            f"Không thể trích xuất face embedding từ bất kỳ ảnh nào trong '{data_dir}/'. "
            f"Đảm bảo mỗi ảnh chứa đúng một khuôn mặt rõ ràng."
        )
    
    logger.info(f"Đã trích xuất {num_embeddings} embeddings từ {num_images} ảnh.")
    
    # Chuyển list thành numpy array
    embeddings_array = np.array(embeddings)
    
    # Tính mean embedding
    mean_embedding = np.mean(embeddings_array, axis=0)
    logger.info(f"Đã tính mean embedding. Shape: {mean_embedding.shape}")
    
    # Tạo thư mục models nếu chưa tồn tại
    os.makedirs(models_dir, exist_ok=True)
    
    # Lưu tất cả embeddings
    embeddings_path = os.path.join(models_dir, "user_embeddings.npy")
    np.save(embeddings_path, embeddings_array)
    logger.info(f"Đã lưu embeddings vào: {embeddings_path}")
    
    # Lưu mean embedding
    mean_path = os.path.join(models_dir, "user_embedding_mean.npy")
    np.save(mean_path, mean_embedding)
    logger.info(f"Đã lưu mean embedding vào: {mean_path}")
    
    logger.info(f"Huấn luyện hoàn tất thành công!")
    return num_images, num_embeddings
