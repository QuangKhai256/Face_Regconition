"""
FastAPI application and endpoints
Main application file containing REST API endpoints for face recognition
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import cv2
import numpy as np
import logging
from typing import Dict

from backend.models import VerifyResponse, FaceBox, ImageSize, TrainingInfo
from backend.data_loader import get_known_faces_cache
from backend.face_processor import (
    read_image_from_upload,
    extract_single_face_encoding,
    compare_with_known_faces,
    validate_image_magic_bytes
)
from backend.exceptions import (
    file_not_found_handler,
    value_error_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler
)

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Giới hạn kích thước file upload (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes


# Khởi tạo FastAPI app với metadata
app = FastAPI(
    title="Face Recognition Backend API",
    description="REST API cho nhận diện khuôn mặt cá nhân",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả HTTP methods
    allow_headers=["*"],  # Cho phép tất cả headers
)

# Đăng ký exception handlers
# Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4
app.add_exception_handler(FileNotFoundError, file_not_found_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.on_event("startup")
async def startup_event():
    """
    Khởi tạo hệ thống khi startup.
    Tải dữ liệu huấn luyện vào cache.
    """
    try:
        logger.info("Đang khởi động Face Recognition Backend...")
        known_encodings, used_files = get_known_faces_cache()
        logger.info(f"Đã tải {len(known_encodings)} ảnh huấn luyện thành công: {used_files}")
        logger.info("Hệ thống sẵn sàng nhận request.")
    except Exception as e:
        logger.error(f"Lỗi khi khởi động hệ thống: {str(e)}")
        raise


@app.get("/api/v1/health")
async def health_check():
    """
    Endpoint kiểm tra trạng thái hệ thống.
    Validates: Requirements 2.1
    """
    logger.debug("Health check request received")
    return {"status": "ok"}


@app.post("/api/v1/face/verify", response_model=VerifyResponse)
async def verify_face(
    file: UploadFile = File(...),
    threshold: float = Query(default=0.5, ge=0.0, le=1.0)
):
    """
    Endpoint xác thực khuôn mặt.
    
    Args:
        file: File ảnh upload (jpg, jpeg, png)
        threshold: Ngưỡng so sánh (0.0 - 1.0), mặc định 0.5
        
    Returns:
        VerifyResponse: Kết quả xác thực với thông tin chi tiết
        
    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 5.1-5.7
    """
    logger.info(f"Nhận request xác thực khuôn mặt: filename={file.filename}, content_type={file.content_type}, threshold={threshold}")
    
    # Validation content-type
    valid_content_types = {"image/jpeg", "image/jpg", "image/png"}
    if file.content_type not in valid_content_types:
        logger.warning(f"Content-type không hợp lệ: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail="File upload phải là ảnh (.jpg, .jpeg, .png)."
        )
    
    # Đọc file bytes
    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    # Kiểm tra kích thước file (max 10MB)
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"File quá lớn: {file_size} bytes (max: {MAX_FILE_SIZE} bytes)")
        raise HTTPException(
            status_code=400,
            detail=f"File quá lớn. Kích thước tối đa cho phép là {MAX_FILE_SIZE // (1024*1024)}MB."
        )
    
    logger.info(f"Kích thước file: {file_size} bytes")
    
    # Validation bằng magic bytes
    if not validate_image_magic_bytes(file_bytes):
        logger.warning("File không phải là ảnh hợp lệ (magic bytes validation failed)")
        raise HTTPException(
            status_code=400,
            detail="File không phải là ảnh hợp lệ. Vui lòng upload file ảnh thật (.jpg, .jpeg, .png)."
        )
    
    # Chuyển đổi bytes thành ảnh BGR
    # ValueError will be caught by exception handler
    logger.info("Đang đọc và decode ảnh...")
    image_bgr = read_image_from_upload(file_bytes)
    
    # Lấy kích thước ảnh
    height, width = image_bgr.shape[:2]
    logger.info(f"Kích thước ảnh: {width}x{height}")
    
    # Chuyển đổi BGR sang RGB (face_recognition yêu cầu RGB)
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    # Trích xuất face embedding và location
    # ValueError will be caught by exception handler
    logger.info("Đang trích xuất face embedding...")
    unknown_encoding, face_location = extract_single_face_encoding(image_rgb)
    logger.info(f"Đã trích xuất face embedding thành công. Face location: {face_location}")
    
    # Lấy dữ liệu huấn luyện từ cache
    # FileNotFoundError will be caught by exception handler
    known_encodings, used_files = get_known_faces_cache()
    logger.info(f"Đang so sánh với {len(known_encodings)} ảnh huấn luyện...")
    
    # So sánh với dữ liệu đã học
    is_match, best_distance = compare_with_known_faces(
        unknown_encoding,
        known_encodings,
        threshold
    )
    logger.info(f"Kết quả so sánh: is_match={is_match}, distance={best_distance:.3f}, threshold={threshold}")
    
    # Tạo message bằng tiếng Việt
    if is_match:
        message = (
            f"Đây là KHUÔN MẶT CỦA BẠN "
            f"(khoảng cách = {best_distance:.3f} ≤ ngưỡng {threshold:.3f})."
        )
    else:
        message = (
            f"Đây KHÔNG PHẢI khuôn mặt của bạn "
            f"(khoảng cách = {best_distance:.3f} > ngưỡng {threshold:.3f})."
        )
    
    # Tạo response
    top, right, bottom, left = face_location
    
    response = VerifyResponse(
        is_match=is_match,
        distance=round(best_distance, 3),
        threshold=threshold,
        message=message,
        face_box=FaceBox(
            top=top,
            right=right,
            bottom=bottom,
            left=left
        ),
        image_size=ImageSize(
            width=width,
            height=height
        ),
        training_info=TrainingInfo(
            num_images=len(used_files),
            used_files_sample=used_files[:10]  # Chỉ lấy 10 file đầu tiên
        )
    )
    
    logger.info(f"Xác thực hoàn tất thành công: {message}")
    return response
