# Kế hoạch Triển khai

- [x] 1. Thiết lập cấu trúc dự án và môi trường





  - Tạo cấu trúc thư mục backend với các module chính
  - Tạo file requirements.txt với các thư viện cần thiết
  - Tạo thư mục myface/ để chứa ảnh huấn luyện
  - Tạo file .gitignore để loại trừ các file không cần thiết
  - _Requirements: 1.1_

- [x] 2. Triển khai module Data Loader





  - Viết hàm load_known_face_encodings() để tải và xử lý ảnh huấn luyện
  - Implement logic quét thư mục myface/ và filter file theo extension
  - Implement logic trích xuất face embedding từ mỗi ảnh
  - Xử lý các trường hợp ảnh không hợp lệ (0 hoặc nhiều khuôn mặt)
  - Implement caching với @lru_cache decorator
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2.1 Viết property test cho data loader


  - **Property 1: Valid image files are loaded successfully**
  - **Validates: Requirements 1.1, 1.2**

- [x] 2.2 Viết property test cho caching behavior


  - **Property 2: Face embeddings are cached**
  - **Validates: Requirements 1.4, 9.1, 9.2**

- [x] 2.3 Viết unit tests cho data loader


  - Test với thư mục không tồn tại
  - Test với thư mục rỗng
  - Test với ảnh có nhiều khuôn mặt
  - Test với ảnh không có khuôn mặt
  - _Requirements: 1.3, 1.5_

- [x] 3. Triển khai module Face Processor





  - Viết hàm read_image_from_upload() để đọc ảnh từ bytes
  - Viết hàm extract_single_face_encoding() để trích xuất embedding
  - Viết hàm compare_with_known_faces() để so sánh khuôn mặt
  - Implement validation cho số lượng khuôn mặt trong ảnh
  - Implement logic tính khoảng cách và so sánh với threshold
  - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 6.3, 6.4, 6.5_

- [x] 3.1 Viết property test cho face embedding extraction


  - **Property 4: Face embedding extraction from valid images**
  - **Validates: Requirements 3.2**

- [x] 3.2 Viết property test cho distance comparison

  - **Property 5: Distance comparison with all training embeddings**
  - **Validates: Requirements 3.3, 3.4**

- [x] 3.3 Viết property test cho threshold-based matching

  - **Property 6: Threshold-based matching decision**
  - **Validates: Requirements 3.5, 3.6**

- [x] 3.4 Viết unit tests cho face processor


  - Test đọc ảnh từ bytes hợp lệ
  - Test đọc ảnh từ bytes không hợp lệ
  - Test xử lý ảnh không có khuôn mặt
  - Test xử lý ảnh có nhiều khuôn mặt
  - _Requirements: 6.2, 6.3, 6.4, 6.5_

- [x] 4. Triển khai Pydantic models





  - Tạo model FaceBox cho tọa độ khuôn mặt
  - Tạo model ImageSize cho kích thước ảnh
  - Tạo model TrainingInfo cho thông tin huấn luyện
  - Tạo model VerifyResponse cho response hoàn chỉnh
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 5. Triển khai FastAPI application và endpoints





  - Khởi tạo FastAPI app với metadata
  - Cấu hình CORS middleware
  - Implement endpoint GET /api/v1/health
  - Implement endpoint POST /api/v1/face/verify
  - Implement xử lý file upload với validation content-type
  - Implement xử lý query parameter threshold với validation
  - _Requirements: 2.1, 3.1, 4.1, 4.2, 4.3, 4.4, 8.1, 8.2, 8.3_

- [x] 5.1 Viết property test cho content-type validation


  - **Property 3: Content-type validation**
  - **Validates: Requirements 3.1**

- [x] 5.2 Viết property test cho custom threshold parameter


  - **Property 7: Custom threshold parameter**
  - **Validates: Requirements 4.1**

- [x] 5.3 Viết property test cho threshold range validation


  - **Property 8: Threshold range validation**
  - **Validates: Requirements 4.3**

- [x] 5.4 Viết property test cho response completeness


  - **Property 9: Response contains all required fields**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7**

- [x] 5.5 Viết property test cho CORS headers


  - **Property 12: CORS allows all origins**
  - **Validates: Requirements 8.1, 8.3**


- [x] 5.6 Viết unit tests cho API endpoints

  - Test health check endpoint trả về đúng format
  - Test verify endpoint với ảnh hợp lệ
  - Test verify endpoint với file không phải ảnh
  - Test verify endpoint với threshold mặc định
  - Test verify endpoint với threshold tùy chỉnh
  - Test CORS preflight request
  - _Requirements: 2.1, 4.2, 8.2_

- [ ] 6. Triển khai xử lý lỗi và exception handling
  - Implement custom exception handlers cho FastAPI
  - Implement xử lý FileNotFoundError với HTTP 500
  - Implement xử lý ValueError với HTTP 400
  - Implement xử lý generic Exception với HTTP 500
  - Đảm bảo tất cả error responses có format JSON với trường "detail"
  - Viết thông báo lỗi bằng tiếng Việt
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4_

- [ ] 6.1 Viết property test cho error response format
  - **Property 10: Error responses use JSON format**
  - **Validates: Requirements 7.3**

- [ ] 6.2 Viết property test cho exception handling
  - **Property 11: Exception handling prevents crashes**
  - **Validates: Requirements 7.4**

- [ ] 6.3 Viết unit tests cho error handling
  - Test xử lý thư mục myface/ không tồn tại
  - Test xử lý thư mục myface/ rỗng
  - Test xử lý file upload không hợp lệ
  - Test xử lý ảnh bị hỏng
  - Test xử lý ảnh không có khuôn mặt
  - Test xử lý ảnh có nhiều khuôn mặt
  - Test xử lý threshold không hợp lệ
  - _Requirements: 1.5, 6.1, 6.2, 6.3, 6.4, 6.5, 4.4_

- [ ] 7. Checkpoint - Đảm bảo tất cả tests pass
  - Đảm bảo tất cả tests pass, hỏi người dùng nếu có vấn đề phát sinh.

- [ ] 8. Tạo ảnh huấn luyện mẫu và test thực tế
  - Tạo thư mục myface/ với 5-7 ảnh mẫu
  - Chạy backend và test với Postman hoặc curl
  - Test với ảnh của chính người dùng (should match)
  - Test với ảnh người khác (should not match)
  - Test với các góc chụp khác nhau
  - Test với ảnh đeo kính
  - _Requirements: 3.5, 3.6_

- [ ] 8.1 Viết integration tests end-to-end
  - Test flow hoàn chỉnh từ upload đến response
  - Test với nhiều ảnh khác nhau
  - Test concurrent requests
  - _Requirements: 9.3_

- [ ] 9. Tạo tài liệu và hướng dẫn sử dụng
  - Tạo README.md với hướng dẫn cài đặt
  - Viết hướng dẫn chạy backend
  - Viết ví dụ gọi API từ JavaScript (web)
  - Viết ví dụ gọi API từ Flutter (mobile)
  - Viết hướng dẫn chuẩn bị ảnh huấn luyện
  - Document các error codes và messages
  - _Requirements: All_

- [ ] 10. Tối ưu hóa và cải thiện
  - Thêm logging cho các operations quan trọng
  - Thêm giới hạn kích thước file upload (max 10MB)
  - Thêm validation cho file bằng magic bytes
  - Cân nhắc thêm rate limiting
  - Optimize performance nếu cần
  - _Requirements: 9.3_

- [ ] 11. Final Checkpoint - Kiểm tra tổng thể
  - Đảm bảo tất cả tests pass, hỏi người dùng nếu có vấn đề phát sinh.
