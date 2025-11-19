# Requirements Document

## Introduction

Hệ thống nhận diện khuôn mặt cá nhân hoàn chỉnh với ba giai đoạn: thu thập dữ liệu khuôn mặt, huấn luyện mô hình cá nhân, và nhận diện khuôn mặt. Hệ thống bao gồm backend API (FastAPI), frontend web (Streamlit), và mobile app (Flutter). Điểm đặc biệt là hệ thống có khả năng kiểm tra môi trường xung quanh (độ sáng, độ mờ, kích thước khuôn mặt) để đảm bảo chất lượng dữ liệu huấn luyện và cảnh báo người dùng khi nhận diện.

## Glossary

- **Backend**: Hệ thống API server sử dụng FastAPI để xử lý các yêu cầu thu thập, huấn luyện và nhận diện khuôn mặt
- **Frontend Web**: Giao diện web sử dụng Streamlit để người dùng tương tác với hệ thống
- **Mobile App**: Ứng dụng di động sử dụng Flutter để người dùng tương tác với hệ thống
- **Enrollment Phase**: Giai đoạn thu thập dữ liệu khuôn mặt của người dùng
- **Training Phase**: Giai đoạn huấn luyện mô hình từ dữ liệu đã thu thập
- **Verification Phase**: Giai đoạn nhận diện và xác thực khuôn mặt
- **Face Embedding**: Vector đặc trưng 128 chiều đại diện cho khuôn mặt
- **Environment Check**: Kiểm tra môi trường xung quanh (độ sáng, độ mờ, kích thước mặt)
- **Brightness**: Độ sáng trung bình của ảnh (0-255)
- **Blur Score**: Điểm đánh giá độ mờ của ảnh sử dụng phương sai Laplacian
- **Face Size Ratio**: Tỷ lệ diện tích khuôn mặt so với diện tích ảnh
- **Distance**: Khoảng cách Euclidean giữa hai face embeddings
- **Threshold**: Ngưỡng khoảng cách để xác định hai khuôn mặt có khớp hay không

## Requirements

### Requirement 1: Thu thập dữ liệu khuôn mặt với kiểm tra môi trường

**User Story:** Là người dùng, tôi muốn thu thập ảnh khuôn mặt của mình với kiểm tra chất lượng tự động, để đảm bảo dữ liệu huấn luyện có chất lượng tốt.

#### Acceptance Criteria

1. WHEN người dùng gửi ảnh đến endpoint thu thập THEN Backend SHALL phát hiện và xác nhận có đúng một khuôn mặt trong ảnh
2. WHEN Backend phát hiện không có khuôn mặt nào THEN Backend SHALL trả về lỗi HTTP 400 với thông báo hướng dẫn người dùng
3. WHEN Backend phát hiện nhiều hơn một khuôn mặt THEN Backend SHALL trả về lỗi HTTP 400 với thông báo yêu cầu chỉ một người trong khung hình
4. WHEN Backend phát hiện một khuôn mặt THEN Backend SHALL tính toán các chỉ số môi trường bao gồm brightness, blur score và face size ratio
5. WHEN brightness nhỏ hơn 60 THEN Backend SHALL đánh dấu ảnh là quá tối và thêm cảnh báo vào danh sách warnings
6. WHEN brightness lớn hơn 200 THEN Backend SHALL đánh dấu ảnh là quá sáng và thêm cảnh báo vào danh sách warnings
7. WHEN blur score nhỏ hơn 100 THEN Backend SHALL đánh dấu ảnh là quá mờ và thêm cảnh báo vào danh sách warnings
8. WHEN face size ratio nhỏ hơn 0.10 THEN Backend SHALL đánh dấu ảnh có khuôn mặt quá nhỏ và thêm cảnh báo vào danh sách warnings
9. WHEN ảnh bị đánh dấu là quá tối hoặc quá mờ hoặc khuôn mặt quá nhỏ THEN Backend SHALL từ chối lưu ảnh và trả về HTTP 400 với danh sách cảnh báo
10. WHEN ảnh đạt yêu cầu môi trường THEN Backend SHALL lưu ảnh vào thư mục data/raw/user với tên file chứa timestamp
11. WHEN ảnh được lưu thành công THEN Backend SHALL trả về HTTP 200 với thông tin đường dẫn file, tổng số ảnh đã thu thập và environment_info

### Requirement 2: Huấn luyện mô hình cá nhân từ dữ liệu đã thu thập

**User Story:** Là người dùng, tôi muốn huấn luyện mô hình nhận diện từ các ảnh đã thu thập, để hệ thống có thể nhận diện khuôn mặt của tôi.

#### Acceptance Criteria

1. WHEN người dùng gọi endpoint huấn luyện THEN Backend SHALL đọc tất cả ảnh từ thư mục data/raw/user
2. WHEN thư mục data/raw/user không tồn tại hoặc rỗng THEN Backend SHALL trả về lỗi HTTP 400 với thông báo yêu cầu thu thập ảnh trước
3. WHEN Backend đọc mỗi ảnh huấn luyện THEN Backend SHALL trích xuất face embedding 128 chiều từ ảnh đó
4. WHEN một ảnh không chứa đúng một khuôn mặt THEN Backend SHALL bỏ qua ảnh đó và ghi log cảnh báo
5. WHEN Backend trích xuất được ít nhất một embedding THEN Backend SHALL tính toán embedding trung bình từ tất cả embeddings
6. WHEN Backend tính toán xong THEN Backend SHALL lưu tất cả embeddings vào file models/user_embeddings.npy
7. WHEN Backend tính toán xong THEN Backend SHALL lưu embedding trung bình vào file models/user_embedding_mean.npy
8. WHEN huấn luyện hoàn tất THEN Backend SHALL trả về HTTP 200 với số lượng ảnh đã đọc và số lượng embeddings đã sử dụng

### Requirement 3: Nhận diện khuôn mặt với kiểm tra môi trường

**User Story:** Là người dùng, tôi muốn nhận diện khuôn mặt từ ảnh mới với thông tin về chất lượng môi trường, để biết kết quả nhận diện có đáng tin cậy hay không.

#### Acceptance Criteria

1. WHEN người dùng gửi ảnh đến endpoint nhận diện THEN Backend SHALL kiểm tra file models/user_embedding_mean.npy có tồn tại
2. WHEN file mô hình không tồn tại THEN Backend SHALL trả về lỗi HTTP 400 với thông báo yêu cầu huấn luyện mô hình trước
3. WHEN Backend nhận ảnh THEN Backend SHALL trích xuất face embedding và vị trí khuôn mặt từ ảnh
4. WHEN Backend trích xuất embedding THEN Backend SHALL tính toán các chỉ số môi trường giống như giai đoạn thu thập
5. WHEN Backend có embedding từ ảnh mới THEN Backend SHALL tính khoảng cách Euclidean giữa embedding mới và embedding trung bình đã huấn luyện
6. WHEN khoảng cách nhỏ hơn hoặc bằng threshold THEN Backend SHALL đánh dấu is_match là true
7. WHEN khoảng cách lớn hơn threshold THEN Backend SHALL đánh dấu is_match là false
8. WHEN Backend hoàn tất nhận diện THEN Backend SHALL trả về response chứa is_match, distance, threshold, message, face_box, image_size và environment_info
9. WHEN environment_info chứa cảnh báo THEN Backend SHALL bao gồm danh sách warnings trong response để frontend hiển thị

### Requirement 4: Validation và xử lý lỗi cho file upload

**User Story:** Là người dùng, tôi muốn hệ thống kiểm tra file upload hợp lệ, để tránh lỗi khi gửi file không đúng định dạng.

#### Acceptance Criteria

1. WHEN người dùng upload file THEN Backend SHALL kiểm tra content-type phải là image/jpeg, image/jpg hoặc image/png
2. WHEN content-type không hợp lệ THEN Backend SHALL trả về HTTP 400 với thông báo yêu cầu file ảnh
3. WHEN Backend nhận file THEN Backend SHALL kiểm tra kích thước file không vượt quá 10MB
4. WHEN file vượt quá 10MB THEN Backend SHALL trả về HTTP 400 với thông báo file quá lớn
5. WHEN Backend nhận file THEN Backend SHALL kiểm tra magic bytes để xác nhận file là ảnh thật
6. WHEN magic bytes không khớp với JPEG hoặc PNG THEN Backend SHALL trả về HTTP 400 với thông báo file không phải ảnh hợp lệ

### Requirement 5: Frontend Web với Streamlit

**User Story:** Là người dùng, tôi muốn giao diện web dễ sử dụng để thu thập, huấn luyện và nhận diện khuôn mặt, để tương tác với hệ thống một cách trực quan.

#### Acceptance Criteria

1. WHEN người dùng mở web app THEN Frontend Web SHALL hiển thị ba tab: Thu thập dữ liệu, Huấn luyện mô hình và Nhận diện khuôn mặt
2. WHEN người dùng ở tab Thu thập dữ liệu THEN Frontend Web SHALL cung cấp hai cách: upload ảnh từ máy hoặc chụp từ webcam
3. WHEN người dùng gửi ảnh thu thập THEN Frontend Web SHALL gọi API /api/v1/collect và hiển thị kết quả hoặc lỗi
4. WHEN Backend trả về lỗi môi trường THEN Frontend Web SHALL hiển thị chi tiết cảnh báo để người dùng biết cách chụp lại
5. WHEN người dùng ở tab Huấn luyện THEN Frontend Web SHALL cung cấp nút để gọi API /api/v1/train
6. WHEN huấn luyện thành công THEN Frontend Web SHALL hiển thị số ảnh và số embeddings đã sử dụng
7. WHEN người dùng ở tab Nhận diện THEN Frontend Web SHALL cho phép upload ảnh hoặc chụp webcam và điều chỉnh threshold
8. WHEN nhận diện hoàn tất THEN Frontend Web SHALL hiển thị ảnh với bounding box màu xanh nếu khớp hoặc đỏ nếu không khớp
9. WHEN nhận diện hoàn tất THEN Frontend Web SHALL hiển thị message, distance, threshold và danh sách cảnh báo môi trường

### Requirement 6: Mobile App với Flutter

**User Story:** Là người dùng, tôi muốn ứng dụng di động để thu thập, huấn luyện và nhận diện khuôn mặt từ điện thoại, để sử dụng hệ thống mọi lúc mọi nơi.

#### Acceptance Criteria

1. WHEN người dùng mở mobile app THEN Mobile App SHALL hiển thị giao diện với các nút: Chụp ảnh, Chọn ảnh, Gửi làm dữ liệu huấn luyện, Huấn luyện mô hình và Nhận diện
2. WHEN người dùng nhấn Chụp ảnh THEN Mobile App SHALL mở camera để chụp ảnh
3. WHEN người dùng nhấn Chọn ảnh THEN Mobile App SHALL mở gallery để chọn ảnh có sẵn
4. WHEN người dùng nhấn Gửi làm dữ liệu huấn luyện THEN Mobile App SHALL gọi API /api/v1/collect với ảnh đã chọn
5. WHEN Backend trả về lỗi môi trường THEN Mobile App SHALL hiển thị thông báo lỗi chi tiết
6. WHEN người dùng nhấn Huấn luyện mô hình THEN Mobile App SHALL gọi API /api/v1/train
7. WHEN người dùng nhấn Nhận diện THEN Mobile App SHALL gọi API /api/v1/face/verify với threshold đã chọn
8. WHEN nhận diện hoàn tất THEN Mobile App SHALL hiển thị kết quả is_match, distance và environment_info
9. WHEN Mobile App chạy trên Android emulator THEN Mobile App SHALL sử dụng địa chỉ backend http://10.0.2.2:8000
10. WHEN Mobile App chạy trên thiết bị thật THEN Mobile App SHALL cho phép cấu hình địa chỉ IP LAN của máy chạy backend

### Requirement 7: Cấu trúc thư mục và quản lý dữ liệu

**User Story:** Là developer, tôi muốn cấu trúc thư mục rõ ràng để quản lý dữ liệu và mô hình, để dễ dàng bảo trì và mở rộng hệ thống.

#### Acceptance Criteria

1. WHEN hệ thống khởi động THEN Backend SHALL tạo thư mục data/raw/user nếu chưa tồn tại
2. WHEN hệ thống khởi động THEN Backend SHALL tạo thư mục models nếu chưa tồn tại
3. WHEN Backend lưu ảnh thu thập THEN Backend SHALL lưu vào thư mục data/raw/user với tên file có định dạng user_YYYYMMDD_HHMMSS.jpg
4. WHEN Backend lưu mô hình THEN Backend SHALL lưu tất cả embeddings vào models/user_embeddings.npy
5. WHEN Backend lưu mô hình THEN Backend SHALL lưu embedding trung bình vào models/user_embedding_mean.npy

### Requirement 8: API Health Check và CORS

**User Story:** Là developer, tôi muốn endpoint health check và cấu hình CORS, để kiểm tra trạng thái hệ thống và cho phép frontend/mobile kết nối.

#### Acceptance Criteria

1. WHEN client gọi GET /api/v1/health THEN Backend SHALL trả về HTTP 200 với status ok
2. WHEN Backend khởi động THEN Backend SHALL cấu hình CORS middleware cho phép tất cả origins
3. WHEN Backend khởi động THEN Backend SHALL cấu hình CORS cho phép tất cả HTTP methods
4. WHEN Backend khởi động THEN Backend SHALL cấu hình CORS cho phép tất cả headers
