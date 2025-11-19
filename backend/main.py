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
import os
from datetime import datetime
from typing import Dict

from backend.models import (
    VerifyResponse, 
    FaceBox, 
    ImageSize, 
    TrainingInfo,
    CollectResponse,
    EnvironmentInfo,
    TrainResponse
)
from backend.data_loader import get_known_faces_cache
from backend.face_processor import (
    read_image_from_upload,
    extract_single_face_encoding,
    compare_with_known_faces,
    validate_image_magic_bytes,
    analyze_environment
)
from backend.training import train_personal_model
from backend.verification import load_trained_model, compare_embeddings
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
    Tạo thư mục cần thiết và tải dữ liệu huấn luyện vào cache.
    Validates: Requirements 7.1, 7.2
    """
    try:
        logger.info("Đang khởi động Face Recognition Backend...")
        
        # Tạo thư mục cần thiết
        os.makedirs("data/raw/user", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        logger.info("Đã tạo thư mục data/raw/user và models")
        
        # Tải dữ liệu huấn luyện vào cache (nếu có)
        try:
            known_encodings, used_files = get_known_faces_cache()
            logger.info(f"Đã tải {len(known_encodings)} ảnh huấn luyện thành công: {used_files}")
        except (FileNotFoundError, ValueError) as e:
            logger.warning(f"Chưa có dữ liệu huấn luyện: {str(e)}")
        
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


@app.post("/api/v1/collect", response_model=CollectResponse)
async def collect_face_image(
    file: UploadFile = File(...)
):
    """
    Endpoint thu thập dữ liệu khuôn mặt với kiểm tra môi trường.
    
    Args:
        file: File ảnh upload (jpg, jpeg, png)
        
    Returns:
        CollectResponse: Kết quả thu thập với thông tin môi trường
        
    Validates: Requirements 1.1-1.11, 4.1-4.6, 7.3
    """
    logger.info(f"Nhận request thu thập dữ liệu: filename={file.filename}, content_type={file.content_type}")
    
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
    logger.info("Đang đọc và decode ảnh...")
    image_bgr = read_image_from_upload(file_bytes)
    
    # Chuyển đổi BGR sang RGB (face_recognition yêu cầu RGB)
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    # Trích xuất face embedding và location
    logger.info("Đang trích xuất face embedding...")
    unknown_encoding, face_location = extract_single_face_encoding(image_rgb)
    logger.info(f"Đã trích xuất face embedding thành công. Face location: {face_location}")
    
    # Phân tích môi trường
    logger.info("Đang phân tích môi trường...")
    env_info = analyze_environment(image_bgr, face_location)
    logger.info(f"Kết quả phân tích môi trường: brightness={env_info['brightness']:.1f}, "
                f"blur_score={env_info['blur_score']:.1f}, "
                f"face_size_ratio={env_info['face_size_ratio']:.3f}")
    
    # Kiểm tra môi trường có đạt yêu cầu không
    # Từ chối nếu quá tối, quá mờ, hoặc khuôn mặt quá nhỏ
    if env_info['is_too_dark'] or env_info['is_too_blurry'] or env_info['is_face_too_small']:
        logger.warning(f"Môi trường không đạt yêu cầu. Warnings: {env_info['warnings']}")
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Môi trường không đạt yêu cầu để thu thập dữ liệu.",
                "environment_info": env_info
            }
        )
    
    # Môi trường tốt - lưu ảnh
    # Tạo thư mục nếu chưa tồn tại
    data_dir = "data/raw/user"
    os.makedirs(data_dir, exist_ok=True)
    
    # Tạo tên file với timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_{timestamp}.jpg"
    filepath = os.path.join(data_dir, filename)
    
    # Lưu ảnh
    cv2.imwrite(filepath, image_bgr)
    logger.info(f"Đã lưu ảnh thành công: {filepath}")
    
    # Đếm tổng số ảnh đã thu thập
    image_files = [
        f for f in os.listdir(data_dir)
        if os.path.isfile(os.path.join(data_dir, f)) and
        f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    total_images = len(image_files)
    
    # Tạo response
    response = CollectResponse(
        message=f"Đã thu thập ảnh thành công! Tổng số ảnh: {total_images}",
        saved_path=filepath,
        total_images=total_images,
        environment_info=EnvironmentInfo(**env_info)
    )
    
    logger.info(f"Thu thập hoàn tất thành công. Tổng số ảnh: {total_images}")
    return response


@app.post("/api/v1/train", response_model=TrainResponse)
async def train_model_endpoint():
    """
    Endpoint huấn luyện mô hình cá nhân từ dữ liệu đã thu thập.
    
    Returns:
        TrainResponse: Kết quả huấn luyện với số lượng ảnh và embeddings
        
    Validates: Requirements 2.1, 2.2, 2.8
    """
    logger.info("Nhận request huấn luyện mô hình")
    
    # Kiểm tra thư mục data/raw/user/ tồn tại và không rỗng
    data_dir = "data/raw/user"
    
    if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
        logger.error(f"Thư mục '{data_dir}/' không tồn tại")
        raise HTTPException(
            status_code=400,
            detail=f"Thư mục '{data_dir}/' không tồn tại. Vui lòng thu thập ảnh trước khi huấn luyện."
        )
    
    # Kiểm tra thư mục có ảnh không
    valid_extensions = {'.jpg', '.jpeg', '.png'}
    image_files = [
        f for f in os.listdir(data_dir)
        if os.path.isfile(os.path.join(data_dir, f)) and
        os.path.splitext(f.lower())[1] in valid_extensions
    ]
    
    if len(image_files) == 0:
        logger.error(f"Không tìm thấy ảnh nào trong thư mục '{data_dir}/'")
        raise HTTPException(
            status_code=400,
            detail=f"Không tìm thấy ảnh nào trong thư mục '{data_dir}/'. Vui lòng thu thập ảnh trước khi huấn luyện."
        )
    
    logger.info(f"Tìm thấy {len(image_files)} ảnh trong thư mục '{data_dir}/'")
    
    # Gọi hàm huấn luyện
    # FileNotFoundError và ValueError sẽ được xử lý bởi exception handlers
    try:
        num_images, num_embeddings = train_personal_model()
        
        # Tạo response
        response = TrainResponse(
            message=f"Huấn luyện hoàn tất thành công! Đã sử dụng {num_embeddings}/{num_images} ảnh.",
            num_images=num_images,
            num_embeddings=num_embeddings
        )
        
        logger.info(f"Huấn luyện hoàn tất: {num_images} ảnh, {num_embeddings} embeddings")
        return response
        
    except (FileNotFoundError, ValueError) as e:
        # Re-raise để exception handler xử lý
        logger.error(f"Lỗi khi huấn luyện: {str(e)}")
        raise


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
    
    # Phân tích môi trường
    logger.info("Đang phân tích môi trường...")
    env_info = analyze_environment(image_bgr, face_location)
    logger.info(f"Kết quả phân tích môi trường: brightness={env_info['brightness']:.1f}, "
                f"blur_score={env_info['blur_score']:.1f}, "
                f"face_size_ratio={env_info['face_size_ratio']:.3f}")
    
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
        environment_info=EnvironmentInfo(**env_info),
        training_info=TrainingInfo(
            num_images=len(used_files),
            used_files_sample=used_files[:10]  # Chỉ lấy 10 file đầu tiên
        )
    )
    
    logger.info(f"Xác thực hoàn tất thành công: {message}")
    return response
