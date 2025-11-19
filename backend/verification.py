"""
Verification module for face recognition.
Handles model loading and embedding comparison for face verification.
"""

import os
import logging
import numpy as np
from typing import Tuple

logger = logging.getLogger(__name__)


def load_trained_model() -> np.ndarray:
    """
    Load mean embedding từ file đã huấn luyện.
    
    Returns:
        mean_embedding: Mean face embedding (128-d vector)
        
    Raises:
        FileNotFoundError: Nếu file mô hình không tồn tại
        
    Validates: Requirements 3.1, 3.2
    """
    model_path = "models/user_embedding_mean.npy"
    
    logger.info(f"Đang tải mô hình từ '{model_path}'...")
    
    # Kiểm tra file tồn tại
    if not os.path.exists(model_path):
        logger.error(f"File mô hình '{model_path}' không tồn tại")
        raise FileNotFoundError(
            f"File mô hình '{model_path}' không tồn tại. "
            f"Vui lòng huấn luyện mô hình trước khi nhận diện."
        )
    
    # Load mean embedding
    try:
        mean_embedding = np.load(model_path)
        logger.info(f"Đã tải mô hình thành công. Shape: {mean_embedding.shape}")
        
        # Validate shape
        if mean_embedding.shape != (128,):
            logger.error(f"Shape của mô hình không hợp lệ: {mean_embedding.shape}, expected (128,)")
            raise ValueError(
                f"File mô hình có shape không hợp lệ: {mean_embedding.shape}. "
                f"Expected shape (128,). Vui lòng huấn luyện lại mô hình."
            )
        
        return mean_embedding
        
    except Exception as e:
        logger.error(f"Lỗi khi tải mô hình: {str(e)}")
        raise



def compare_embeddings(
    embedding1: np.ndarray,
    embedding2: np.ndarray,
    threshold: float
) -> Tuple[bool, float]:
    """
    So sánh hai face embeddings bằng khoảng cách Euclidean.
    
    Args:
        embedding1: Face embedding thứ nhất (128-d vector)
        embedding2: Face embedding thứ hai (128-d vector)
        threshold: Ngưỡng để xác định khớp (0.0 - 1.0)
        
    Returns:
        - is_match: True nếu distance <= threshold, False nếu không
        - distance: Khoảng cách Euclidean giữa hai embeddings
        
    Validates: Requirements 3.5, 3.6, 3.7
    """
    # Tính khoảng cách Euclidean
    # distance = sqrt(sum((embedding1[i] - embedding2[i])^2))
    distance = float(np.linalg.norm(embedding1 - embedding2))
    
    logger.debug(f"Khoảng cách Euclidean: {distance:.4f}, threshold: {threshold}")
    
    # So sánh với threshold
    is_match = distance <= threshold
    
    return is_match, distance
