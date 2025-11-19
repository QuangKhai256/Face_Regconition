# Design Document

## Overview

Hệ thống nhận diện khuôn mặt cá nhân được thiết kế theo kiến trúc client-server với ba thành phần chính:

1. **Backend API (FastAPI)**: Xử lý logic nghiệp vụ, thu thập dữ liệu, huấn luyện mô hình và nhận diện khuôn mặt
2. **Frontend Web (Streamlit)**: Giao diện web đơn giản cho người dùng desktop
3. **Mobile App (Flutter)**: Ứng dụng di động cho người dùng smartphone

Hệ thống hoạt động theo ba giai đoạn tuần tự:
- **Enrollment Phase**: Thu thập 5-10 ảnh khuôn mặt với kiểm tra chất lượng môi trường
- **Training Phase**: Trích xuất face embeddings và tính embedding trung bình
- **Verification Phase**: So sánh embedding mới với embedding đã huấn luyện

## Architecture

### High-Level Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  Frontend Web   │         │   Mobile App    │
│   (Streamlit)   │         │    (Flutter)    │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │      HTTP/REST API        │
         └───────────┬───────────────┘
                     │
         ┌───────────▼───────────┐
         │   Backend API Server  │
         │      (FastAPI)        │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   File System         │
         │  - data/raw/user/     │
         │  - models/            │
         └───────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.8-3.11
- FastAPI - REST API framework
- uvicorn - ASGI server
- face_recognition - Face detection and embedding extraction
- opencv-python (cv2) - Image processing and environment analysis
- numpy - Numerical computations

**Frontend Web:**
- Python 3.8-3.11
- Streamlit - Web UI framework
- requests - HTTP client
- opencv-python - Image processing

**Mobile:**
- Flutter SDK 3.x
- Dart language
- http package - HTTP client
- image_picker package - Camera and gallery access

## Components and Interfaces

### Backend Components

#### 1. API Endpoints Module (`backend/main.py`)

**Responsibilities:**
- Define REST API endpoints
- Handle HTTP requests/responses
- Coordinate between modules
- Configure CORS and middleware

**Key Functions:**
- `health_check()`: Health check endpoint
- `collect_face_image()`: Thu thập ảnh với kiểm tra môi trường
- `train_model_endpoint()`: Huấn luyện mô hình
- `verify_face()`: Nhận diện khuôn mặt

#### 2. Environment Analysis Module

**Responsibilities:**
- Analyze image quality
- Calculate brightness, blur score, face size ratio
- Generate warnings for poor conditions

**Key Functions:**
- `analyze_environment(image_bgr, face_box) -> Dict`: Phân tích môi trường
  - Input: Image BGR array, face bounding box
  - Output: Dictionary với brightness, blur_score, face_size_ratio, warnings
  - Logic:
    - Brightness = mean(grayscale_pixels)
    - Blur score = variance(Laplacian(grayscale))
    - Face size ratio = face_area / image_area
    - Generate warnings based on thresholds

#### 3. Face Processing Module

**Responsibilities:**
- Load and decode images
- Detect faces
- Extract face embeddings

**Key Functions:**
- `load_image_bgr_from_bytes(file_bytes) -> np.ndarray`: Decode image
- `extract_single_face_embedding(image_rgb) -> (embedding, face_box)`: Extract face
  - Validates exactly one face
  - Returns 128-d embedding and bounding box

#### 4. Training Module

**Responsibilities:**
- Load training images
- Extract embeddings from all images
- Calculate mean embedding
- Save model files

**Key Functions:**
- `train_personal_model() -> (num_images, num_embeddings)`: Train model
  - Reads all images from data/raw/user/
  - Extracts embeddings
  - Calculates mean
  - Saves to models/

#### 5. Verification Module

**Responsibilities:**
- Load trained model
- Compare embeddings
- Calculate distance

**Key Functions:**
- `load_trained_model() -> np.ndarray`: Load mean embedding
- Compare embeddings using Euclidean distance

### Frontend Web Components

#### 1. Main App (`web/web_app.py`)

**Responsibilities:**
- Render Streamlit UI
- Handle user interactions
- Call backend APIs
- Display results

**Key Sections:**
- Tab 1: Thu thập dữ liệu (upload/webcam → /collect)
- Tab 2: Huấn luyện mô hình (button → /train)
- Tab 3: Nhận diện (upload/webcam → /verify)

**Key Functions:**
- `call_collect_api(image_bytes)`: Call /collect endpoint
- `call_train_api()`: Call /train endpoint
- `call_verify_api(image_bytes, threshold)`: Call /verify endpoint
- `draw_box(image, face_box, is_match)`: Draw bounding box on image
- `capture_frame_from_webcam()`: Capture from webcam

### Mobile App Components

#### 1. Main App (`mobile/lib/main.dart`)

**Responsibilities:**
- Render Flutter UI
- Handle camera/gallery
- Call backend APIs
- Display results

**Key Widgets:**
- Image display area
- Threshold slider
- Action buttons (camera, gallery, collect, train, verify)
- Status and detail text displays

**Key Functions:**
- `_pickImage(ImageSource)`: Pick image from camera or gallery
- `_sendToCollect()`: Call /collect endpoint
- `_callTrain()`: Call /train endpoint
- `_verifyFace()`: Call /verify endpoint

## Data Models

### API Request/Response Models

#### EnvironmentInfo
```python
{
  "brightness": float,           # 0-255
  "is_too_dark": bool,           # brightness < 60
  "is_too_bright": bool,         # brightness > 200
  "blur_score": float,           # variance of Laplacian
  "is_too_blurry": bool,         # blur_score < 100
  "face_size_ratio": float,      # 0.0-1.0
  "is_face_too_small": bool,     # ratio < 0.10
  "warnings": List[str]          # Human-readable warnings
}
```

#### CollectResponse
```python
{
  "message": str,
  "saved_path": str,
  "total_images": int,
  "environment_info": EnvironmentInfo
}
```

#### TrainResponse
```python
{
  "message": str,
  "num_images": int,
  "num_embeddings": int
}
```

#### VerifyResponse
```python
{
  "is_match": bool,
  "distance": float,
  "threshold": float,
  "message": str,
  "face_box": {
    "top": int,
    "right": int,
    "bottom": int,
    "left": int
  },
  "image_size": {
    "width": int,
    "height": int
  },
  "environment_info": EnvironmentInfo
}
```

### File System Data Models

#### Training Images
- Location: `data/raw/user/`
- Format: `user_YYYYMMDD_HHMMSS.jpg`
- Content: JPEG images with single face

#### Model Files
- `models/user_embeddings.npy`: NumPy array shape (N, 128) - all embeddings
- `models/user_embedding_mean.npy`: NumPy array shape (128,) - mean embedding

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, I identified several areas where properties can be consolidated:

1. **Environment threshold properties (1.5, 1.6, 1.7, 1.8)** can be combined into a single comprehensive property about environment analysis correctness
2. **Threshold comparison properties (3.6, 3.7)** are two sides of the same logic and can be combined
3. **Model file saving properties (2.6, 2.7, 7.4, 7.5)** are redundant and can be tested with round-trip properties
4. **Response structure properties** can be consolidated to avoid testing each field separately

### Properties

Property 1: Single face detection validation
*For any* image sent to the collect or verify endpoint, the system should correctly identify whether there is exactly zero, one, or multiple faces, and respond appropriately (reject if not exactly one)
**Validates: Requirements 1.1**

Property 2: Environment metrics calculation
*For any* image with exactly one face, the system should calculate brightness (0-255), blur_score (Laplacian variance), and face_size_ratio (0.0-1.0), and all three metrics should be present in the response
**Validates: Requirements 1.4, 3.4**

Property 3: Environment threshold consistency
*For any* image with calculated environment metrics, the flags (is_too_dark, is_too_bright, is_too_blurry, is_face_too_small) should be set correctly based on the thresholds: brightness < 60 for too dark, brightness > 200 for too bright, blur_score < 100 for too blurry, face_size_ratio < 0.10 for too small
**Validates: Requirements 1.5, 1.6, 1.7, 1.8**

Property 4: Collection rejection for poor environment
*For any* image where is_too_dark OR is_too_blurry OR is_face_too_small is true, the collect endpoint should return HTTP 400 and should NOT save the image to disk
**Validates: Requirements 1.9**

Property 5: Collection success for good environment
*For any* image where all environment checks pass (not too dark, not too bright, not too blurry, face not too small), the collect endpoint should return HTTP 200, save the image with timestamp filename format, and return the correct total_images count
**Validates: Requirements 1.10, 1.11, 7.3**

Property 6: Training reads all valid images
*For any* set of images in data/raw/user/ directory, the training process should attempt to read all image files with valid extensions (.jpg, .jpeg, .png)
**Validates: Requirements 2.1**

Property 7: Training extracts 128-d embeddings
*For any* valid training image with exactly one face, the system should extract a face embedding with exactly 128 dimensions
**Validates: Requirements 2.3**

Property 8: Training skips invalid images
*For any* training image that does not contain exactly one face, the system should skip that image and continue processing other images without failing
**Validates: Requirements 2.4**

Property 9: Mean embedding calculation
*For any* non-empty list of 128-d embeddings, the calculated mean embedding should have 128 dimensions and each dimension should equal the arithmetic mean of that dimension across all input embeddings
**Validates: Requirements 2.5**

Property 10: Model persistence round-trip
*For any* set of embeddings and calculated mean embedding, after saving to models/user_embeddings.npy and models/user_embedding_mean.npy, loading them back should produce arrays with identical shapes and values (within floating point precision)
**Validates: Requirements 2.6, 2.7, 7.4, 7.5**

Property 11: Training response structure
*For any* successful training operation, the response should contain num_images (total images found) and num_embeddings (embeddings successfully extracted), where num_embeddings <= num_images
**Validates: Requirements 2.8**

Property 12: Euclidean distance calculation
*For any* two 128-d embeddings, the calculated distance should equal the square root of the sum of squared differences between corresponding dimensions
**Validates: Requirements 3.5**

Property 13: Threshold comparison consistency
*For any* calculated distance and threshold value, is_match should be true if and only if distance <= threshold
**Validates: Requirements 3.6, 3.7**

Property 14: Verification response completeness
*For any* successful verification operation, the response should contain all required fields: is_match (bool), distance (float), threshold (float), message (string), face_box (with top/right/bottom/left), image_size (with width/height), and environment_info (with all metrics and warnings)
**Validates: Requirements 3.8, 3.9**

Property 15: Content-type validation
*For any* file upload to collect or verify endpoints, if content-type is not in {image/jpeg, image/jpg, image/png}, the endpoint should return HTTP 400
**Validates: Requirements 4.1**

Property 16: File size validation
*For any* file upload with size > 10MB (10485760 bytes), the endpoint should return HTTP 400 with appropriate error message
**Validates: Requirements 4.3**

Property 17: Magic bytes validation
*For any* file upload, if the file's magic bytes do not match JPEG (0xFF 0xD8 0xFF) or PNG (0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A) signatures, the endpoint should return HTTP 400
**Validates: Requirements 4.5**

## Error Handling

### Error Categories

**Client Errors (HTTP 400):**
- Invalid file format (content-type, magic bytes)
- File too large (> 10MB)
- No face detected in image
- Multiple faces detected in image
- Poor environment conditions during collection (too dark, too blurry, face too small)
- Missing training data when calling train endpoint
- Missing trained model when calling verify endpoint

**Server Errors (HTTP 500):**
- File system errors (cannot create directories, cannot save files)
- Image decoding errors
- Face recognition library errors
- Unexpected exceptions

### Error Response Format

All errors return JSON with `detail` field:
```json
{
  "detail": "Human-readable error message in Vietnamese"
}
```

### Error Handling Strategy

1. **Validation errors**: Caught early, return HTTP 400 with clear guidance
2. **File system errors**: Logged with full stack trace, return HTTP 500
3. **Face detection errors**: Return HTTP 400 with instructions for better image
4. **Environment check failures**: Return HTTP 400 with specific warnings list

## Testing Strategy

### Unit Testing

Unit tests will cover:
- Individual functions in isolation (environment analysis, face detection, distance calculation)
- Edge cases (empty directories, missing files, invalid images)
- Error handling paths
- File I/O operations with mocked file system

**Testing Framework**: pytest

**Key Test Areas**:
- `test_environment_analysis_unit.py`: Test brightness, blur, face size calculations
- `test_face_detection_unit.py`: Test single face extraction logic
- `test_training_unit.py`: Test embedding extraction and mean calculation
- `test_file_operations_unit.py`: Test file saving and loading

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs.

**Testing Framework**: Hypothesis (Python PBT library)

**Configuration**: Each property test will run minimum 100 iterations

**Test Tagging Format**: Each PBT test must include a comment:
`# Feature: face-recognition-complete, Property {number}: {property_text}`

**Key Property Tests**:
- `test_environment_thresholds_property.py`: Test Properties 2, 3
- `test_collection_validation_property.py`: Test Properties 1, 4, 5
- `test_training_embeddings_property.py`: Test Properties 6, 7, 8, 9, 10, 11
- `test_verification_logic_property.py`: Test Properties 12, 13, 14
- `test_file_validation_property.py`: Test Properties 15, 16, 17

**Generator Strategies**:
- Generate synthetic images with controlled properties (brightness, blur, number of faces)
- Generate valid and invalid file uploads
- Generate embeddings with known properties for distance testing
- Generate edge cases (empty arrays, boundary values)

### Integration Testing

Integration tests will verify:
- End-to-end workflows (collect → train → verify)
- API endpoint interactions
- File system persistence
- Frontend/Mobile API calls

### Manual Testing

Manual testing for:
- UI/UX of Streamlit web app
- UI/UX of Flutter mobile app
- Webcam capture functionality
- Real-world face recognition accuracy

## Performance Considerations

### Backend Performance

- **Face detection**: ~100-500ms per image (depends on image size and CPU)
- **Embedding extraction**: ~50-200ms per face
- **Training**: Linear with number of images (N images × ~200ms)
- **Verification**: ~200-300ms per request

### Optimization Strategies

1. **Caching**: Keep trained model in memory after first load
2. **Image resizing**: Resize large images before processing
3. **Async processing**: Use FastAPI async endpoints for I/O operations
4. **Batch processing**: Process multiple training images in parallel (future enhancement)

### Scalability Considerations

Current design is single-user, single-model:
- One model per backend instance
- No database, uses file system
- Suitable for personal use or small deployments

For multi-user scenarios, would need:
- Database for user management
- Multiple model storage (per user)
- Authentication and authorization
- Cloud storage for images and models

## Security Considerations

### Current Implementation

- **File validation**: Content-type, magic bytes, size limits
- **CORS**: Currently allows all origins (development mode)
- **No authentication**: Open API endpoints

### Production Recommendations

1. **CORS**: Restrict to specific frontend domains
2. **Authentication**: Add JWT or session-based auth
3. **Rate limiting**: Prevent abuse of API endpoints
4. **File scanning**: Add malware scanning for uploads
5. **HTTPS**: Use TLS for all communications
6. **Input sanitization**: Validate all user inputs
7. **Secure storage**: Encrypt sensitive data at rest

## Deployment

### Development Setup

**Backend:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install fastapi uvicorn[standard] face-recognition opencv-python numpy python-multipart
uvicorn backend.main:app --reload --port 8000
```

**Frontend Web:**
```bash
pip install streamlit requests opencv-python
streamlit run web/web_app.py
```

**Mobile:**
```bash
cd mobile
flutter pub get
flutter run
```

### Production Deployment

**Backend:**
- Use production ASGI server (uvicorn with workers, or gunicorn)
- Set up reverse proxy (nginx)
- Configure environment variables
- Set up logging and monitoring
- Use systemd or Docker for process management

**Frontend Web:**
- Deploy on cloud platform (Streamlit Cloud, Heroku, AWS)
- Configure backend URL via environment variable

**Mobile:**
- Build APK/IPA for distribution
- Configure production backend URL
- Submit to app stores if needed

## Future Enhancements

1. **Multi-user support**: Database, user accounts, per-user models
2. **Real-time video**: Continuous face recognition from video stream
3. **Face liveness detection**: Prevent spoofing with photos
4. **Model versioning**: Track and rollback model versions
5. **Analytics dashboard**: Track usage, accuracy metrics
6. **Batch operations**: Upload and process multiple images at once
7. **Cloud storage**: S3/GCS for images and models
8. **Notification system**: Alert users of recognition events
9. **Advanced environment checks**: Pose estimation, occlusion detection
10. **Model fine-tuning**: Allow users to add/remove training images and retrain
