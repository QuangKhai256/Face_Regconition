"""
Pydantic models for request/response
This file contains data models for API requests and responses
"""
from typing import List
from pydantic import BaseModel


class FaceBox(BaseModel):
    """
    Tọa độ vị trí khuôn mặt trong ảnh.
    Validates: Requirements 5.5
    """
    top: int
    right: int
    bottom: int
    left: int


class ImageSize(BaseModel):
    """
    Kích thước của ảnh.
    Validates: Requirements 5.6
    """
    width: int
    height: int


class TrainingInfo(BaseModel):
    """
    Thông tin về dữ liệu huấn luyện đã sử dụng.
    Validates: Requirements 5.7
    """
    num_images: int
    used_files_sample: List[str]


class VerifyResponse(BaseModel):
    """
    Response hoàn chỉnh cho API xác thực khuôn mặt.
    Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
    """
    is_match: bool
    distance: float
    threshold: float
    message: str
    face_box: FaceBox
    image_size: ImageSize
    training_info: TrainingInfo
