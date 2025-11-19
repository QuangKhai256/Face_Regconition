# Tài liệu Thiết kế

## Tổng quan

Hệ thống backend nhận diện khuôn mặt được xây dựng trên kiến trúc REST API sử dụng FastAPI framework. Hệ thống hoạt động theo mô hình client-server, trong đó backend xử lý toàn bộ logic nhận diện khuôn mặt và cung cấp API cho các client (web/mobile) gọi đến.

Quy trình hoạt động chính:
1. **Khởi động**: Backend tải và xử lý ảnh huấn luyện từ thư mục `myface/`, trích xuất face embeddings và lưu vào cache
2. **Xác thực**: Client gửi ảnh khuôn mặt qua HTTP POST, backend so sánh với dữ liệu đã học và trả về kết quả JSON
3. **Phản hồi**: Backend trả về thông tin chi tiết bao gồm kết quả khớp/không khớp, khoảng cách, vị trí khuôn mặt

## Kiến trúc

### Kiến trúc tổng thể

```
┌─────────────────┐         HTTP/REST API          ┌──────────────────┐
│   Web Client    │◄──────────────────────────────►│                  │
│  (Browser/SPA)  │                                 │                  │
└─────────────────┘                                 │                  │
                                                    │   FastAPI        │
┌─────────────────┐         HTTP/REST API          │   Backend        │
│  Mobile Client  │◄──────────────────────────────►│                  │
│ (iOS/Android)   │                                 │                  │
└─────────────────┘                                 └────────┬─────────┘
                                                             │
                                                             │
                                                    ┌────────▼─────────┐
                                                    │  face_recognition│
                                                    │     Library      │
                                                    │   (dlib-based)   │
                                                    └────────┬─────────┘
                                                             │
                                                    ┌────────▼─────────┐
                                                    │   Training Data  │
                                                    │   (myface/*.jpg) │
                                                    └──────────────────┘
```

### Kiến trúc module

```
backend/
├── main.py                 # FastAPI application & endpoints
├── face_processor.py       # Face recognition logic
├── data_loader.py          # Training data loading & caching
├── models.py               # Pydantic models for request/response
└── exceptions.py           # Custom exceptions
```

## Các thành phần và giao diện

### 1. Data Loader Module

**Trách nhiệm**: Tải và xử lý ảnh huấn luyện, tạo face embeddings

**Giao diện chính**:
```python
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
    pass

@lru_cache(maxsize=1)
def get_known_faces_cache() -> Tuple[List[np.ndarray], List[str]]:
    """
    Cached version của load_known_face_encodings để tránh tải lại.
    """
    pass
```

**Chi tiết xử lý**:
- Quét thư mục `myface/` tìm file có extension `.jpg`, `.jpeg`, `.png`
- Với mỗi ảnh:
  - Sử dụng `face_recognition.load_image_file()` để đọc ảnh
  - Tìm vị trí khuôn mặt bằng `face_recognition.face_locations()`
  - Bỏ qua ảnh nếu không có hoặc có nhiều hơn 1 khuôn mặt
  - Trích xuất embedding bằng `face_recognition.face_encodings()`
- Sử dụng `@lru_cache` để cache kết quả

### 2. Face Processor Module

**Trách nhiệm**: Xử lý ảnh upload và thực hiện so sánh khuôn mặt

**Giao diện chính**:
```python
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
    pass

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
    pass

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
    pass
```

**Chi tiết xử lý**:
- Sử dụng OpenCV (`cv2.imdecode`) để decode bytes thành ảnh
- Chuyển đổi từ BGR sang RGB (face_recognition yêu cầu RGB)
- Validate chỉ có đúng 1 khuôn mặt trong ảnh
- Tính khoảng cách Euclidean giữa embeddings bằng `face_recognition.face_distance()`
- So sánh khoảng cách nhỏ nhất với threshold

### 3. API Endpoints

**Endpoint 1: Health Check**
```
GET /api/v1/health
Response: 200 OK
{
  "status": "ok"
}
```

**Endpoint 2: Face Verification**
```
POST /api/v1/face/verify?threshold=0.5
Content-Type: multipart/form-data
Body: file (image file)

Response: 200 OK
{
  "is_match": true,
  "distance": 0.43,
  "threshold": 0.5,
  "message": "Đây là KHUÔN MẶT CỦA BẠN (khoảng cách = 0.430 ≤ ngưỡng 0.500).",
  "face_box": {
    "top": 100,
    "right": 200,
    "bottom": 220,
    "left": 80
  },
  "image_size": {
    "width": 640,
    "height": 480
  },
  "training_info": {
    "num_images": 7,
    "used_files_sample": ["img1.jpg", "img2.jpg", ...]
  }
}
```

### 4. Models (Pydantic)

```python
class FaceBox(BaseModel):
    top: int
    right: int
    bottom: int
    left: int

class ImageSize(BaseModel):
    width: int
    height: int

class TrainingInfo(BaseModel):
    num_images: int
    used_files_sample: List[str]

class VerifyResponse(BaseModel):
    is_match: bool
    distance: float
    threshold: float
    message: str
    face_box: FaceBox
    image_size: ImageSize
    training_info: TrainingInfo
```

## Mô hình dữ liệu

### Face Embedding
- **Định dạng**: numpy array với shape (128,)
- **Kiểu dữ liệu**: float64
- **Mô tả**: Vector đặc trưng 128 chiều đại diện cho khuôn mặt, được tạo bởi mô hình deep learning của dlib

### Training Data Cache
- **Cấu trúc**: Tuple[List[np.ndarray], List[str]]
- **Phần tử 1**: Danh sách face embeddings
- **Phần tử 2**: Danh sách tên file tương ứng
- **Caching**: Sử dụng `@lru_cache(maxsize=1)` để cache trong memory

### Image Data Flow
```
Upload bytes → OpenCV decode → BGR array → RGB array → Face detection → Face encoding
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Valid image files are loaded successfully
*For any* directory containing image files with extensions .jpg, .jpeg, or .png where each image contains exactly one face, the data loader should successfully extract face embeddings from all valid images.
**Validates: Requirements 1.1, 1.2**

### Property 2: Face embeddings are cached
*For any* sequence of calls to get training data, after the first call loads the data, all subsequent calls should return the cached data without reloading from disk.
**Validates: Requirements 1.4, 9.1, 9.2**

### Property 3: Content-type validation
*For any* file upload with content-type not in {image/jpeg, image/jpg, image/png}, the API should reject the request with HTTP 400.
**Validates: Requirements 3.1**

### Property 4: Face embedding extraction from valid images
*For any* valid image containing exactly one face, the system should successfully extract a 128-dimensional face embedding vector.
**Validates: Requirements 3.2**

### Property 5: Distance comparison with all training embeddings
*For any* uploaded face image and training data, the system should compute distances to all training embeddings and use the minimum distance for the match decision.
**Validates: Requirements 3.3, 3.4**

### Property 6: Threshold-based matching decision
*For any* computed distance and threshold value, if distance ≤ threshold then is_match should be true, otherwise is_match should be false.
**Validates: Requirements 3.5, 3.6**

### Property 7: Custom threshold parameter
*For any* valid threshold value provided as query parameter, the system should use that value instead of the default for comparison.
**Validates: Requirements 4.1**

### Property 8: Threshold range validation
*For any* threshold value outside the range [0.0, 1.0], the API should return HTTP 422 validation error.
**Validates: Requirements 4.3**

### Property 9: Response contains all required fields
*For any* successful face verification request, the JSON response should contain all required fields: is_match, distance, threshold, message, face_box, image_size, and training_info.
**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7**

### Property 10: Error responses use JSON format
*For any* HTTP error response (4xx or 5xx), the response should be in JSON format with a "detail" field containing the error message.
**Validates: Requirements 7.3**

### Property 11: Exception handling prevents crashes
*For any* exception that occurs during request processing, the system should catch it and return an appropriate HTTP error response instead of crashing.
**Validates: Requirements 7.4**

### Property 12: CORS allows all origins
*For any* HTTP request from any origin, the backend should include appropriate CORS headers allowing the request.
**Validates: Requirements 8.1, 8.3**

## Xử lý lỗi

### Phân loại lỗi

**1. Client Errors (HTTP 400)**
- File không phải định dạng ảnh hợp lệ
- Ảnh không đọc được hoặc bị hỏng
- Ảnh không chứa khuôn mặt
- Ảnh chứa nhiều hơn 1 khuôn mặt
- Không trích xuất được face embedding

**2. Validation Errors (HTTP 422)**
- Threshold nằm ngoài khoảng [0.0, 1.0]
- Thiếu file trong request

**3. Server Errors (HTTP 500)**
- Lỗi khi tải dữ liệu huấn luyện
- Lỗi nội bộ trong quá trình xử lý
- Exception không mong đợi

### Chiến lược xử lý

```python
try:
    # Processing logic
    pass
except FileNotFoundError as e:
    raise HTTPException(status_code=500, detail=str(e))
except ValueError as e:
    # Client errors - invalid input
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    # Unexpected errors
    raise HTTPException(
        status_code=500,
        detail=f"Lỗi nội bộ: {str(e)}"
    )
```

### Thông báo lỗi

Tất cả thông báo lỗi được viết bằng tiếng Việt, rõ ràng và hướng dẫn người dùng cách khắc phục:
- "File upload phải là ảnh (.jpg, .jpeg, .png)."
- "Không tìm thấy khuôn mặt nào trong ảnh. Hãy để mặt của bạn chiếm phần lớn khung hình..."
- "Phát hiện N khuôn mặt trong ảnh. Vui lòng để CHỈ MỘT người trong ảnh..."

## Chiến lược kiểm thử

### Unit Testing

Sử dụng **pytest** làm framework testing chính.

**Test coverage**:
1. **Data Loader Tests**
   - Test tải ảnh từ thư mục hợp lệ
   - Test xử lý thư mục không tồn tại
   - Test xử lý thư mục rỗng
   - Test bỏ qua ảnh có 0 hoặc nhiều khuôn mặt

2. **Face Processor Tests**
   - Test đọc ảnh từ bytes
   - Test chuyển đổi BGR sang RGB
   - Test trích xuất embedding từ ảnh hợp lệ
   - Test xử lý ảnh không có khuôn mặt
   - Test xử lý ảnh có nhiều khuôn mặt

3. **API Endpoint Tests**
   - Test health check endpoint
   - Test verify endpoint với ảnh hợp lệ
   - Test verify endpoint với các loại lỗi
   - Test threshold parameter
   - Test CORS headers

### Property-Based Testing

Sử dụng **Hypothesis** làm thư viện property-based testing cho Python.

**Cấu hình**: Mỗi property test chạy tối thiểu 100 iterations để đảm bảo coverage.

**Property tests** (chi tiết trong tasks):
- Property 1: Valid image files loading
- Property 2: Caching behavior
- Property 3: Content-type validation
- Property 4: Face embedding extraction
- Property 5: Distance comparison
- Property 6: Threshold-based decision
- Property 7: Custom threshold usage
- Property 8: Threshold validation
- Property 9: Response completeness
- Property 10: Error response format
- Property 11: Exception handling
- Property 12: CORS headers

**Test data generation strategies**:
- Sử dụng ảnh mẫu thật từ thư mục test fixtures
- Generate random threshold values trong và ngoài range hợp lệ
- Generate random file content-types
- Tạo mock embeddings với numpy arrays ngẫu nhiên

### Integration Testing

- Test end-to-end flow từ upload ảnh đến nhận response
- Test với ảnh thật từ camera/gallery
- Test performance với ảnh có kích thước khác nhau
- Test concurrent requests

### Edge Cases Testing

Các edge cases quan trọng cần test:
- Ảnh có kích thước rất nhỏ (< 100x100)
- Ảnh có kích thước rất lớn (> 10MB)
- Ảnh bị xoay, lật
- Ảnh có độ sáng rất thấp/cao
- Ảnh bị mờ
- Khuôn mặt bị che một phần (kính, khẩu trang)
- Threshold ở các giá trị biên (0.0, 1.0)
- Training data chỉ có 1 ảnh
- Training data có nhiều ảnh (> 50)

## Cân nhắc về bảo mật

1. **File Upload Security**
   - Giới hạn kích thước file upload (max 10MB)
   - Validate file type bằng content-type và magic bytes
   - Không lưu file upload lên disk

2. **CORS Configuration**
   - Trong production nên giới hạn allowed origins
   - Hiện tại cho phép tất cả origins cho mục đích development

3. **Rate Limiting**
   - Nên implement rate limiting để tránh abuse
   - Khuyến nghị: 10 requests/minute per IP

4. **Data Privacy**
   - Face embeddings không thể reverse về ảnh gốc
   - Không log ảnh người dùng
   - Training data nên được bảo vệ

## Cân nhắc về hiệu năng

1. **Caching Strategy**
   - Training data được cache trong memory
   - Không cần reload cho mỗi request
   - Trade-off: Memory usage vs Speed

2. **Image Processing**
   - Sử dụng OpenCV cho xử lý ảnh nhanh
   - Không resize ảnh trước khi xử lý (face_recognition tự xử lý)

3. **Concurrent Requests**
   - FastAPI hỗ trợ async/await
   - Face recognition operations là CPU-bound
   - Có thể scale bằng multiple workers (uvicorn --workers N)

4. **Expected Performance**
   - Health check: < 10ms
   - Face verification: 500ms - 2s (tùy kích thước ảnh)
   - Training data loading: 1-5s (chỉ khi khởi động)

## Deployment

### Requirements
```
Python >= 3.8
face-recognition
opencv-python
fastapi
uvicorn[standard]
python-multipart
numpy
```

### Running the server
```bash
# Development
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn backend.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Docker Support (Optional)
```dockerfile
FROM python:3.10-slim
RUN apt-get update && apt-get install -y cmake build-essential
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
