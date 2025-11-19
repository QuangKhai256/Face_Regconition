# Implementation Plan

- [x] 1. Thiết lập cấu trúc project và cấu hình cơ bản





  - Tạo cấu trúc thư mục: backend/, web/, mobile/, data/raw/user/, models/
  - Cấu hình requirements.txt với các dependencies cần thiết
  - Tạo file __init__.py cho các module Python
  - _Requirements: 7.1, 7.2, 8.2, 8.3, 8.4_

- [ ] 2. Implement Backend - Environment Analysis Module
  - Viết hàm `analyze_environment(image_bgr, face_box)` để tính brightness, blur_score, face_size_ratio
  - Implement logic kiểm tra thresholds (is_too_dark, is_too_bright, is_too_blurry, is_face_too_small)
  - Generate warnings list dựa trên các flags
  - _Requirements: 1.4, 1.5, 1.6, 1.7, 1.8, 3.4_

- [ ] 2.1 Write property test for environment metrics calculation
  - **Property 2: Environment metrics calculation**
  - **Validates: Requirements 1.4, 3.4**

- [ ] 2.2 Write property test for environment threshold consistency
  - **Property 3: Environment threshold consistency**
  - **Validates: Requirements 1.5, 1.6, 1.7, 1.8**

- [ ] 3. Implement Backend - Face Processing Module
  - Viết hàm `load_image_bgr_from_bytes(file_bytes)` để decode image từ bytes
  - Viết hàm `extract_single_face_embedding(image_rgb)` để detect face và extract embedding
  - Validate đúng 1 khuôn mặt, raise ValueError nếu 0 hoặc nhiều hơn 1
  - _Requirements: 1.1, 1.2, 1.3, 2.3, 3.3_

- [ ] 3.1 Write property test for single face detection
  - **Property 1: Single face detection validation**
  - **Validates: Requirements 1.1**

- [ ] 3.2 Write property test for embedding dimensions
  - **Property 7: Training extracts 128-d embeddings**
  - **Validates: Requirements 2.3**

- [ ] 4. Implement Backend - File Validation Module
  - Viết hàm `validate_image_magic_bytes(file_bytes)` để check JPEG/PNG magic bytes
  - Implement validation cho content-type
  - Implement validation cho file size (max 10MB)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [ ] 4.1 Write property test for content-type validation
  - **Property 15: Content-type validation**
  - **Validates: Requirements 4.1**

- [ ] 4.2 Write property test for file size validation
  - **Property 16: File size validation**
  - **Validates: Requirements 4.3**

- [ ] 4.3 Write property test for magic bytes validation
  - **Property 17: Magic bytes validation**
  - **Validates: Requirements 4.5**

- [ ] 5. Implement Backend - Collection Endpoint (/api/v1/collect)
  - Tạo endpoint POST /api/v1/collect nhận UploadFile
  - Validate file (content-type, size, magic bytes)
  - Decode image và extract face embedding
  - Analyze environment và check thresholds
  - Nếu môi trường kém → return HTTP 400 với warnings
  - Nếu môi trường tốt → save image với timestamp filename
  - Return response với saved_path, total_images, environment_info
  - _Requirements: 1.1-1.11, 4.1-4.6, 7.3_

- [ ] 5.1 Write property test for collection rejection
  - **Property 4: Collection rejection for poor environment**
  - **Validates: Requirements 1.9**

- [ ] 5.2 Write property test for collection success
  - **Property 5: Collection success for good environment**
  - **Validates: Requirements 1.10, 1.11, 7.3**

- [ ] 6. Implement Backend - Training Module
  - Viết hàm `train_personal_model()` để đọc images từ data/raw/user/
  - Extract embeddings từ mỗi ảnh hợp lệ (skip ảnh invalid)
  - Tính mean embedding từ tất cả embeddings
  - Save embeddings array vào models/user_embeddings.npy
  - Save mean embedding vào models/user_embedding_mean.npy
  - Return (num_images, num_embeddings)
  - _Requirements: 2.1, 2.3, 2.4, 2.5, 2.6, 2.7, 7.4, 7.5_

- [ ] 6.1 Write property test for training reads all images
  - **Property 6: Training reads all valid images**
  - **Validates: Requirements 2.1**

- [ ] 6.2 Write property test for training skips invalid images
  - **Property 8: Training skips invalid images**
  - **Validates: Requirements 2.4**

- [ ] 6.3 Write property test for mean embedding calculation
  - **Property 9: Mean embedding calculation**
  - **Validates: Requirements 2.5**

- [ ] 6.4 Write property test for model persistence round-trip
  - **Property 10: Model persistence round-trip**
  - **Validates: Requirements 2.6, 2.7, 7.4, 7.5**

- [ ] 7. Implement Backend - Training Endpoint (/api/v1/train)
  - Tạo endpoint POST /api/v1/train
  - Check thư mục data/raw/user/ tồn tại và không rỗng
  - Gọi train_personal_model()
  - Handle errors (no images, extraction failures)
  - Return response với num_images, num_embeddings
  - _Requirements: 2.1, 2.2, 2.8_

- [ ] 7.1 Write property test for training response structure
  - **Property 11: Training response structure**
  - **Validates: Requirements 2.8**

- [ ] 8. Implement Backend - Verification Module
  - Viết hàm `load_trained_model()` để load mean embedding từ file
  - Viết hàm `compare_embeddings(embedding1, embedding2, threshold)` để tính Euclidean distance
  - Implement logic so sánh distance với threshold
  - _Requirements: 3.1, 3.2, 3.5, 3.6, 3.7_

- [ ] 8.1 Write property test for Euclidean distance calculation
  - **Property 12: Euclidean distance calculation**
  - **Validates: Requirements 3.5**

- [ ] 8.2 Write property test for threshold comparison
  - **Property 13: Threshold comparison consistency**
  - **Validates: Requirements 3.6, 3.7**

- [ ] 9. Implement Backend - Verification Endpoint (/api/v1/face/verify)
  - Tạo endpoint POST /api/v1/face/verify với parameter threshold
  - Validate file upload
  - Check model file tồn tại
  - Extract face embedding từ ảnh mới
  - Analyze environment
  - Load trained model và compare embeddings
  - Calculate distance và determine is_match
  - Return response với is_match, distance, threshold, message, face_box, image_size, environment_info
  - _Requirements: 3.1-3.9_

- [ ] 9.1 Write property test for verification response completeness
  - **Property 14: Verification response completeness**
  - **Validates: Requirements 3.8, 3.9**

- [ ] 10. Implement Backend - Health Check và CORS
  - Tạo endpoint GET /api/v1/health return {"status": "ok"}
  - Configure CORS middleware cho phép all origins, methods, headers
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 11. Implement Backend - Error Handlers
  - Tạo exception handlers cho ValueError (HTTP 400)
  - Tạo exception handlers cho FileNotFoundError (HTTP 500)
  - Tạo exception handlers cho HTTPException
  - Tạo exception handlers cho generic Exception (HTTP 500)
  - Ensure tất cả errors return JSON với field "detail"
  - _Requirements: 1.2, 1.3, 1.9, 2.2, 3.2, 4.2, 4.4, 4.6_

- [ ] 12. Implement Backend - Pydantic Models
  - Tạo model EnvironmentInfo với các fields: brightness, is_too_dark, is_too_bright, blur_score, is_too_blurry, face_size_ratio, is_face_too_small, warnings
  - Tạo model FaceBox với top, right, bottom, left
  - Tạo model ImageSize với width, height
  - Tạo model CollectResponse
  - Tạo model TrainResponse
  - Tạo model VerifyResponse
  - _Requirements: 1.11, 2.8, 3.8, 3.9_

- [ ] 13. Implement Backend - Main Application Setup
  - Tạo FastAPI app instance với title, description, version
  - Register tất cả endpoints
  - Register exception handlers
  - Add CORS middleware
  - Implement startup event để ensure directories exist
  - _Requirements: 7.1, 7.2, 8.2, 8.3, 8.4_

- [ ] 14. Checkpoint - Backend Core Complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Implement Frontend Web - API Client Functions
  - Viết hàm `call_collect_api(image_bytes)` gọi POST /api/v1/collect
  - Viết hàm `call_train_api()` gọi POST /api/v1/train
  - Viết hàm `call_verify_api(image_bytes, threshold)` gọi POST /api/v1/face/verify
  - Handle errors và parse JSON responses
  - _Requirements: 5.3, 5.5, 5.7_

- [ ] 16. Implement Frontend Web - Image Processing Functions
  - Viết hàm `draw_box(image_bgr, face_box, is_match)` để vẽ bounding box
  - Viết hàm `capture_frame_from_webcam()` để chụp từ webcam
  - _Requirements: 5.8_

- [ ] 17. Implement Frontend Web - Tab 1: Thu thập dữ liệu
  - Tạo Streamlit UI với tab "Thu thập dữ liệu"
  - Implement upload ảnh từ máy
  - Implement chụp ảnh từ webcam
  - Gọi call_collect_api() khi user submit
  - Hiển thị success message hoặc error với warnings
  - Hiển thị environment_info
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 18. Implement Frontend Web - Tab 2: Huấn luyện mô hình
  - Tạo tab "Huấn luyện mô hình"
  - Implement button "Bắt đầu huấn luyện"
  - Gọi call_train_api()
  - Hiển thị num_images và num_embeddings
  - _Requirements: 5.1, 5.5, 5.6_

- [ ] 19. Implement Frontend Web - Tab 3: Nhận diện khuôn mặt
  - Tạo tab "Nhận diện khuôn mặt"
  - Implement slider để điều chỉnh threshold
  - Implement upload ảnh hoặc chụp webcam
  - Gọi call_verify_api()
  - Hiển thị ảnh với bounding box (xanh/đỏ)
  - Hiển thị message, distance, threshold
  - Hiển thị environment_info và warnings
  - _Requirements: 5.1, 5.7, 5.8, 5.9_

- [ ] 20. Implement Frontend Web - Main App Configuration
  - Setup Streamlit page config (title, icon, layout)
  - Tạo sidebar với threshold slider và instructions
  - Configure backend URL (http://localhost:8000)
  - _Requirements: 5.1_

- [ ] 21. Implement Mobile App - Project Setup
  - Tạo Flutter project structure
  - Configure pubspec.yaml với dependencies: http, image_picker
  - Setup main.dart với MaterialApp
  - _Requirements: 6.1_

- [ ] 22. Implement Mobile App - API Client Functions
  - Viết hàm `_sendToCollect()` gọi POST /api/v1/collect
  - Viết hàm `_callTrain()` gọi POST /api/v1/train
  - Viết hàm `_verifyFace()` gọi POST /api/v1/face/verify
  - Handle HTTP responses và parse JSON
  - Handle errors và hiển thị messages
  - _Requirements: 6.4, 6.6, 6.7_

- [ ] 23. Implement Mobile App - Image Picker Functions
  - Viết hàm `_pickImage(ImageSource)` để chụp hoặc chọn ảnh
  - Handle camera permission
  - Handle gallery access
  - _Requirements: 6.2, 6.3_

- [ ] 24. Implement Mobile App - UI Components
  - Tạo AppBar với title "FaceID Mobile"
  - Tạo image display area
  - Tạo threshold slider
  - Tạo buttons: Chụp ảnh, Chọn ảnh, Gửi làm dữ liệu huấn luyện, Huấn luyện mô hình, Nhận diện
  - Tạo status và detail text displays
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.6, 6.7_

- [ ] 25. Implement Mobile App - State Management
  - Setup State với các biến: _selectedImage, _threshold, _loading, _status, _detail, _distance
  - Implement setState() calls để update UI
  - Implement loading states
  - _Requirements: 6.8_

- [ ] 26. Implement Mobile App - Backend URL Configuration
  - Configure baseUrl với http://10.0.2.2:8000 cho Android emulator
  - Add comment hướng dẫn thay đổi IP cho thiết bị thật
  - _Requirements: 6.9, 6.10_

- [ ] 27. Implement Mobile App - Error Handling và Display
  - Handle API errors và hiển thị error messages
  - Parse environment_info từ responses
  - Hiển thị warnings cho user
  - Color-code status messages (green/red)
  - _Requirements: 6.5, 6.8_

- [ ] 28. Final Checkpoint - Integration Testing
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 29. Write integration tests for end-to-end workflows
  - Test workflow: collect → train → verify
  - Test error scenarios
  - Test file persistence

- [ ] 30. Update Documentation
  - Update README.md với hướng dẫn cài đặt và chạy
  - Document API endpoints
  - Add usage examples
  - Add troubleshooting guide
