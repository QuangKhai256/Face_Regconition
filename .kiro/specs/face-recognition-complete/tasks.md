# Implementation Plan

- [x] 1. Thiết lập cấu trúc project và cấu hình cơ bản





  - Tạo cấu trúc thư mục: backend/, web/, mobile/, data/raw/user/, models/
  - Cấu hình requirements.txt với các dependencies cần thiết
  - Tạo file __init__.py cho các module Python
  - _Requirements: 7.1, 7.2, 8.2, 8.3, 8.4_

- [x] 2. Implement Backend - Environment Analysis Module





  - Viết hàm `analyze_environment(image_bgr, face_box)` để tính brightness, blur_score, face_size_ratio
  - Implement logic kiểm tra thresholds (is_too_dark, is_too_bright, is_too_blurry, is_face_too_small)
  - Generate warnings list dựa trên các flags
  - _Requirements: 1.4, 1.5, 1.6, 1.7, 1.8, 3.4_

- [x] 2.1 Write property test for environment metrics calculation


  - **Property 2: Environment metrics calculation**
  - **Validates: Requirements 1.4, 3.4**

- [x] 2.2 Write property test for environment threshold consistency


  - **Property 3: Environment threshold consistency**
  - **Validates: Requirements 1.5, 1.6, 1.7, 1.8**

- [x] 3. Implement Backend - Face Processing Module








  - Viết hàm `load_image_bgr_from_bytes(file_bytes)` để decode image từ bytes
  - Viết hàm `extract_single_face_embedding(image_rgb)` để detect face và extract embedding
  - Validate đúng 1 khuôn mặt, raise ValueError nếu 0 hoặc nhiều hơn 1
  - _Requirements: 1.1, 1.2, 1.3, 2.3, 3.3_

- [x] 3.1 Write property test for single face detection


  - **Property 1: Single face detection validation**
  - **Validates: Requirements 1.1**

- [x] 3.2 Write property test for embedding dimensions


  - **Property 7: Training extracts 128-d embeddings**
  - **Validates: Requirements 2.3**

- [x] 4. Implement Backend - File Validation Module





  - Viết hàm `validate_image_magic_bytes(file_bytes)` để check JPEG/PNG magic bytes
  - Implement validation cho content-type
  - Implement validation cho file size (max 10MB)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 4.1 Write property test for content-type validation


  - **Property 15: Content-type validation**
  - **Validates: Requirements 4.1**

- [x] 4.2 Write property test for file size validation


  - **Property 16: File size validation**
  - **Validates: Requirements 4.3**

- [x] 4.3 Write property test for magic bytes validation


  - **Property 17: Magic bytes validation**
  - **Validates: Requirements 4.5**

- [x] 5. Implement Backend - Collection Endpoint (/api/v1/collect)








- [x] 5.1 Create collection endpoint structure

  - Tạo endpoint POST /api/v1/collect nhận UploadFile
  - Setup basic route handler
  - _Requirements: 1.1, 7.3_

- [x] 5.2 Implement file validation in collection endpoint

  - Validate file (content-type, size, magic bytes)
  - Return appropriate errors nếu validation fails
  - _Requirements: 4.1-4.6_

- [x] 5.3 Implement image processing in collection endpoint

  - Decode image và extract face embedding
  - Analyze environment và check thresholds
  - _Requirements: 1.1-1.8_

- [x] 5.4 Implement collection logic and response

  - Nếu môi trường kém → return HTTP 400 với warnings
  - Nếu môi trường tốt → save image với timestamp filename
  - Return response với saved_path, total_images, environment_info
  - _Requirements: 1.9, 1.10, 1.11_

- [x] 5.5 Write property test for collection rejection
  - **Property 4: Collection rejection for poor environment**
  - **Validates: Requirements 1.9**

- [x] 5.6 Write property test for collection success







  - **Property 5: Collection success for good environment**
  - **Validates: Requirements 1.10, 1.11, 7.3**

- [x] 6. Implement Backend - Training Module





- [x] 6.1 Create training data loading function


  - Viết hàm `train_personal_model()` để đọc images từ data/raw/user/
  - Implement logic để list và validate image files
  - _Requirements: 2.1_

- [x] 6.2 Implement embedding extraction in training

  - Extract embeddings từ mỗi ảnh hợp lệ (skip ảnh invalid)
  - Handle errors cho từng ảnh
  - _Requirements: 2.3, 2.4_


- [x] 6.3 Implement mean calculation and model saving


  - Tính mean embedding từ tất cả embeddings
  - Save embeddings array vào models/user_embeddings.npy
  - Save mean embedding vào models/user_embedding_mean.npy
  - Return (num_images, num_embeddings)
  - _Requirements: 2.5, 2.6, 2.7, 7.4, 7.5_

- [x] 6.4 Write property test for training reads all images


  - **Property 6: Training reads all valid images**
  - **Validates: Requirements 2.1**

- [x] 6.5 Write property test for training skips invalid images


  - **Property 8: Training skips invalid images**
  - **Validates: Requirements 2.4**

- [x] 6.6 Write property test for mean embedding calculation


  - **Property 9: Mean embedding calculation**
  - **Validates: Requirements 2.5**

- [x] 6.7 Write property test for model persistence round-trip


  - **Property 10: Model persistence round-trip**
  - **Validates: Requirements 2.6, 2.7, 7.4, 7.5**

- [x] 7. Implement Backend - Training Endpoint (/api/v1/train)





- [x] 7.1 Create training endpoint structure


  - Tạo endpoint POST /api/v1/train
  - Check thư mục data/raw/user/ tồn tại và không rỗng
  - _Requirements: 2.1, 2.2_

- [x] 7.2 Implement training execution and response

  - Gọi train_personal_model()
  - Handle errors (no images, extraction failures)
  - Return response với num_images, num_embeddings
  - _Requirements: 2.2, 2.8_

- [x] 7.3 Write property test for training response structure


  - **Property 11: Training response structure**
  - **Validates: Requirements 2.8**

- [x] 8. Implement Backend - Verification Module





- [x] 8.1 Create model loading function


  - Viết hàm `load_trained_model()` để load mean embedding từ file
  - Handle file not found errors
  - _Requirements: 3.1, 3.2_

- [x] 8.2 Implement embedding comparison function


  - Viết hàm `compare_embeddings(embedding1, embedding2, threshold)` để tính Euclidean distance
  - Implement logic so sánh distance với threshold
  - _Requirements: 3.5, 3.6, 3.7_

- [x] 8.3 Write property test for Euclidean distance calculation


  - **Property 12: Euclidean distance calculation**
  - **Validates: Requirements 3.5**

- [x] 8.4 Write property test for threshold comparison


  - **Property 13: Threshold comparison consistency**
  - **Validates: Requirements 3.6, 3.7**
- [x] 9. Implement Backend - Verification Endpoint (/api/v1/face/verify)

- [x] 9. Implement Backend - Verification Endpoint (/api/v1/face/verify)





- [x] 9.1 Create verification endpoint structure


  - Tạo endpoint POST /api/v1/face/verify với parameter threshold
  - Validate file upload
  - Check model file tồn tại
  - _Requirements: 3.1, 3.2_

- [x] 9.2 Implement face extraction and environment analysis


  - Extract face embedding từ ảnh mới
  - Analyze environment
  - _Requirements: 3.3, 3.4_

- [x] 9.3 Implement verification logic and response


  - Load trained model và compare embeddings
  - Calculate distance và determine is_match
  - Return response với is_match, distance, threshold, message, face_box, image_size, environment_info
  - _Requirements: 3.5, 3.6, 3.7, 3.8, 3.9_

- [x] 9.4 Write property test for verification response completeness


  - **Property 14: Verification response completeness**
  - **Validates: Requirements 3.8, 3.9**

- [x] 10. Implement Backend - Supporting Infrastructure






- [x] 10.1 Create Pydantic models

  - Tạo model EnvironmentInfo với các fields: brightness, is_too_dark, is_too_bright, blur_score, is_too_blurry, face_size_ratio, is_face_too_small, warnings
  - Tạo model FaceBox với top, right, bottom, left
  - Tạo model ImageSize với width, height
  - Tạo model CollectResponse
  - Tạo model TrainResponse
  - Tạo model VerifyResponse
  - _Requirements: 1.11, 2.8, 3.8, 3.9_

- [x] 10.2 Implement error handlers

  - Tạo exception handlers cho ValueError (HTTP 400)
  - Tạo exception handlers cho FileNotFoundError (HTTP 500)
  - Tạo exception handlers cho HTTPException
  - Tạo exception handlers cho generic Exception (HTTP 500)
  - Ensure tất cả errors return JSON với field "detail"
  - _Requirements: 1.2, 1.3, 1.9, 2.2, 3.2, 4.2, 4.4, 4.6_

- [x] 10.3 Implement health check and CORS

  - Tạo endpoint GET /api/v1/health return {"status": "ok"}
  - Configure CORS middleware cho phép all origins, methods, headers
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 10.4 Setup main application

  - Tạo FastAPI app instance với title, description, version
  - Register tất cả endpoints
  - Register exception handlers
  - Add CORS middleware
  - Implement startup event để ensure directories exist
  - _Requirements: 7.1, 7.2, 8.2, 8.3, 8.4_

- [x] 11. Checkpoint - Backend Core Complete





  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Implement Frontend Web - Core Functions






- [x] 12.1 Create API client functions


  - Viết hàm `call_collect_api(image_bytes)` gọi POST /api/v1/collect
  - Viết hàm `call_train_api()` gọi POST /api/v1/train
  - Viết hàm `call_verify_api(image_bytes, threshold)` gọi POST /api/v1/face/verify
  - Handle errors và parse JSON responses
  - _Requirements: 5.3, 5.5, 5.7_


- [x] 12.2 Create image processing functions


  - Viết hàm `draw_box(image_bgr, face_box, is_match)` để vẽ bounding box
  - Viết hàm `capture_frame_from_webcam()` để chụp từ webcam
  - _Requirements: 5.8_

- [x] 13. Implement Frontend Web - UI Tabs






- [x] 13.1 Create Tab 1: Thu thập dữ liệu

  - Tạo Streamlit UI với tab "Thu thập dữ liệu"
  - Implement upload ảnh từ máy
  - Implement chụp ảnh từ webcam
  - Gọi call_collect_api() khi user submit
  - Hiển thị success message hoặc error với warnings
  - Hiển thị environment_info
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 13.2 Create Tab 2: Huấn luyện mô hình

  - Tạo tab "Huấn luyện mô hình"
  - Implement button "Bắt đầu huấn luyện"
  - Gọi call_train_api()
  - Hiển thị num_images và num_embeddings
  - _Requirements: 5.1, 5.5, 5.6_

- [x] 13.3 Create Tab 3: Nhận diện khuôn mặt

  - Tạo tab "Nhận diện khuôn mặt"
  - Implement slider để điều chỉnh threshold
  - Implement upload ảnh hoặc chụp webcam
  - Gọi call_verify_api()
  - Hiển thị ảnh với bounding box (xanh/đỏ)
  - Hiển thị message, distance, threshold
  - Hiển thị environment_info và warnings
  - _Requirements: 5.1, 5.7, 5.8, 5.9_

- [x] 13.4 Setup main app configuration

  - Setup Streamlit page config (title, icon, layout)
  - Tạo sidebar với threshold slider và instructions
  - Configure backend URL (http://localhost:8000)
  - _Requirements: 5.1_

- [x] 14. Implement Mobile App - Setup and Core Functions






- [x] 14.1 Create project setup


  - Tạo Flutter project structure
  - Configure pubspec.yaml với dependencies: http, image_picker
  - Setup main.dart với MaterialApp
  - _Requirements: 6.1_

- [x] 14.2 Create API client functions

  - Viết hàm `_sendToCollect()` gọi POST /api/v1/collect
  - Viết hàm `_callTrain()` gọi POST /api/v1/train
  - Viết hàm `_verifyFace()` gọi POST /api/v1/face/verify
  - Handle HTTP responses và parse JSON
  - Handle errors và hiển thị messages
  - _Requirements: 6.4, 6.6, 6.7_

- [x] 14.3 Create image picker functions

  - Viết hàm `_pickImage(ImageSource)` để chụp hoặc chọn ảnh
  - Handle camera permission
  - Handle gallery access
  - _Requirements: 6.2, 6.3_

- [x] 15. Implement Mobile App - UI and State





- [x] 15.1 Create UI components


  - Tạo AppBar với title "FaceID Mobile"
  - Tạo image display area
  - Tạo threshold slider
  - Tạo buttons: Chụp ảnh, Chọn ảnh, Gửi làm dữ liệu huấn luyện, Huấn luyện mô hình, Nhận diện
  - Tạo status và detail text displays
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.6, 6.7_

- [x] 15.2 Implement state management

  - Setup State với các biến: _selectedImage, _threshold, _loading, _status, _detail, _distance
  - Implement setState() calls để update UI
  - Implement loading states
  - _Requirements: 6.8_

- [x] 15.3 Configure backend connection

  - Configure baseUrl với http://10.0.2.2:8000 cho Android emulator
  - Add comment hướng dẫn thay đổi IP cho thiết bị thật
  - _Requirements: 6.9, 6.10_

- [x] 15.4 Implement error handling and display

  - Handle API errors và hiển thị error messages
  - Parse environment_info từ responses
  - Hiển thị warnings cho user
  - Color-code status messages (green/red)
  - _Requirements: 6.5, 6.8_

- [ ] 16. Final Testing and Documentation

- [ ] 16.1 Write integration tests
  - Test workflow: collect → train → verify
  - Test error scenarios
  - Test file persistence

- [ ] 16.2 Update documentation
  - Update README.md với hướng dẫn cài đặt và chạy
  - Document API endpoints
  - Add usage examples
  - Add troubleshooting guide

- [ ] 16.3 Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.
