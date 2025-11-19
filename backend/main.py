"""
FastAPI application and endpoints
Main application file containing REST API endpoints for face recognition
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np

from backend.models import VerifyResponse, FaceBox, ImageSize, TrainingInfo
from backend.data_loader import get_known_faces_cache
from backend.face_processor import (
    read_image_from_upload,
    extract_single_face_encoding,
    compare_with_known_faces
)


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


@app.get("/api/v1/health")
async def health_check():
    """
    Endpoint kiểm tra trạng thái hệ thống.
    Validates: Requirements 2.1
    """
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
    # Validation content-type
    valid_content_types = {"image/jpeg", "image/jpg", "image/png"}
    if file.content_type not in valid_content_types:
        raise HTTPException(
            status_code=400,
            detail="File upload phải là ảnh (.jpg, .jpeg, .png)."
        )
    
    try:
        # Đọc file bytes
        file_bytes = await file.read()
        
        # Chuyển đổi bytes thành ảnh BGR
        image_bgr = read_image_from_upload(file_bytes)
        
        # Lấy kích thước ảnh
        height, width = image_bgr.shape[:2]
        
        # Chuyển đổi BGR sang RGB (face_recognition yêu cầu RGB)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        # Trích xuất face embedding và location
        unknown_encoding, face_location = extract_single_face_encoding(image_rgb)
        
        # Lấy dữ liệu huấn luyện từ cache
        known_encodings, used_files = get_known_faces_cache()
        
        # So sánh với dữ liệu đã học
        is_match, best_distance = compare_with_known_faces(
            unknown_encoding,
            known_encodings,
            threshold
        )
        
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
        
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi nội bộ: {str(e)}"
        )
