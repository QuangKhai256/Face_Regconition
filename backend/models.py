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


class EnvironmentInfo(BaseModel):
    """
    Thông tin về môi trường xung quanh ảnh.
    Validates: Requirements 1.11, 2.8, 3.8, 3.9
    """
    brightness: float
    is_too_dark: bool
    is_too_bright: bool
    blur_score: float
    is_too_blurry: bool
    face_size_ratio: float
    is_face_too_small: bool
    warnings: List[str]


class CollectResponse(BaseModel):
    """
    Response cho API thu thập dữ liệu khuôn mặt.
    Validates: Requirements 1.11
    """
    message: str
    saved_path: str
    total_images: int
    environment_info: EnvironmentInfo


class TrainResponse(BaseModel):
    """
    Response cho API huấn luyện mô hình.
    Validates: Requirements 2.8
    """
    message: str
    num_images: int
    num_embeddings: int


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
