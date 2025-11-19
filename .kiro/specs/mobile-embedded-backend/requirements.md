# Requirements Document

## Introduction

Tích hợp backend nhận diện khuôn mặt trực tiếp vào Flutter mobile app để chạy hoàn toàn offline trên thiết bị di động. Thay vì gọi API đến server Python riêng biệt, toàn bộ logic xử lý khuôn mặt (phát hiện, trích xuất embedding, huấn luyện, nhận diện) sẽ chạy native trên thiết bị thông qua plugin Flutter hoặc thư viện ML native (ML Kit, TensorFlow Lite). Camera sẽ sử dụng camera thật của thiết bị, không phải demo.

## Glossary

- **Flutter Plugin**: Package Flutter cho phép gọi code native (Kotlin/Java cho Android, Swift/Objective-C cho iOS)
- **ML Kit**: Thư viện machine learning của Google cho mobile, hỗ trợ face detection
- **TensorFlow Lite**: Framework ML nhẹ cho mobile và embedded devices
- **Face Detection**: Phát hiện vị trí khuôn mặt trong ảnh
- **Face Recognition**: Nhận diện và so khớp khuôn mặt với dữ liệu đã lưu
- **Embedding**: Vector đặc trưng đại diện cho khuôn mặt (thường 128 hoặc 512 chiều)
- **Camera Plugin**: Plugin Flutter để truy cập camera thiết bị (camera package)
- **Local Storage**: Lưu trữ dữ liệu cục bộ trên thiết bị (SharedPreferences, SQLite, file system)
- **Native Code**: Code Kotlin/Java (Android) hoặc Swift/Objective-C (iOS)

## Requirements

### Requirement 1: Camera thật trên thiết bị di động

**User Story:** Là người dùng, tôi muốn sử dụng camera thật của điện thoại để chụp ảnh khuôn mặt, để thu thập dữ liệu và nhận diện trong thực tế.

#### Acceptance Criteria

1. WHEN người dùng nhấn nút chụp ảnh THEN Mobile App SHALL mở camera preview thật của thiết bị
2. WHEN camera preview hiển thị THEN Mobile App SHALL cho phép người dùng xem real-time video feed
3. WHEN người dùng nhấn nút chụp THEN Mobile App SHALL capture frame hiện tại từ camera
4. WHEN ảnh được chụp THEN Mobile App SHALL hiển thị ảnh preview để người dùng xác nhận
5. WHEN người dùng xác nhận ảnh THEN Mobile App SHALL lưu ảnh vào bộ nhớ tạm để xử lý
6. WHEN người dùng từ chối ảnh THEN Mobile App SHALL quay lại camera preview để chụp lại

### Requirement 2: Phát hiện khuôn mặt trên thiết bị

**User Story:** Là người dùng, tôi muốn app tự động phát hiện khuôn mặt trong ảnh ngay trên điện thoại, để không cần kết nối internet hay server.

#### Acceptance Criteria

1. WHEN Mobile App nhận ảnh từ camera THEN Mobile App SHALL sử dụng ML Kit Face Detection để phát hiện khuôn mặt
2. WHEN ML Kit phát hiện không có khuôn mặt THEN Mobile App SHALL hiển thị thông báo "Không phát hiện khuôn mặt"
3. WHEN ML Kit phát hiện nhiều hơn một khuôn mặt THEN Mobile App SHALL hiển thị thông báo "Phát hiện nhiều khuôn mặt, vui lòng chỉ một người"
4. WHEN ML Kit phát hiện đúng một khuôn mặt THEN Mobile App SHALL trả về bounding box của khuôn mặt
5. WHEN phát hiện thành công THEN Mobile App SHALL vẽ bounding box lên ảnh preview để người dùng thấy

### Requirement 3: Kiểm tra chất lượng môi trường trên thiết bị

**User Story:** Là người dùng, tôi muốn app kiểm tra chất lượng ảnh (độ sáng, độ mờ) ngay trên điện thoại, để biết ảnh có đủ tốt để sử dụng không.

#### Acceptance Criteria

1. WHEN Mobile App phát hiện một khuôn mặt THEN Mobile App SHALL tính toán brightness từ ảnh grayscale
2. WHEN brightness nhỏ hơn 60 THEN Mobile App SHALL cảnh báo "Ảnh quá tối, vui lòng tăng ánh sáng"
3. WHEN brightness lớn hơn 200 THEN Mobile App SHALL cảnh báo "Ảnh quá sáng, vui lòng giảm ánh sáng"
4. WHEN Mobile App phát hiện một khuôn mặt THEN Mobile App SHALL tính toán blur score bằng Laplacian variance
5. WHEN blur score nhỏ hơn 100 THEN Mobile App SHALL cảnh báo "Ảnh bị mờ, vui lòng giữ máy chắc hơn"
6. WHEN Mobile App phát hiện một khuôn mặt THEN Mobile App SHALL tính toán face size ratio
7. WHEN face size ratio nhỏ hơn 0.10 THEN Mobile App SHALL cảnh báo "Khuôn mặt quá nhỏ, vui lòng đến gần hơn"
8. WHEN có bất kỳ cảnh báo nào THEN Mobile App SHALL hiển thị danh sách cảnh báo cho người dùng

### Requirement 4: Thu thập và lưu trữ ảnh huấn luyện trên thiết bị

**User Story:** Là người dùng, tôi muốn thu thập nhiều ảnh khuôn mặt và lưu trên điện thoại, để chuẩn bị dữ liệu huấn luyện.

#### Acceptance Criteria

1. WHEN người dùng xác nhận ảnh đạt chất lượng THEN Mobile App SHALL lưu ảnh vào thư mục app private storage
2. WHEN lưu ảnh THEN Mobile App SHALL đặt tên file theo format "user_YYYYMMDD_HHMMSS.jpg"
3. WHEN lưu ảnh thành công THEN Mobile App SHALL cập nhật counter tổng số ảnh đã thu thập
4. WHEN người dùng mở màn hình thu thập THEN Mobile App SHALL hiển thị số ảnh đã thu thập
5. WHEN người dùng muốn xóa dữ liệu THEN Mobile App SHALL cung cấp nút xóa tất cả ảnh huấn luyện

### Requirement 5: Trích xuất face embedding trên thiết bị

**User Story:** Là người dùng, tôi muốn app tự động trích xuất đặc trưng khuôn mặt ngay trên điện thoại, để không phụ thuộc vào server.

#### Acceptance Criteria

1. WHEN Mobile App cần trích xuất embedding THEN Mobile App SHALL sử dụng TensorFlow Lite model hoặc ML Kit Face Recognition
2. WHEN model được load THEN Mobile App SHALL cache model trong memory để tái sử dụng
3. WHEN Mobile App nhận ảnh có một khuôn mặt THEN Mobile App SHALL trích xuất face embedding vector
4. WHEN trích xuất thành công THEN Mobile App SHALL trả về embedding vector với số chiều cố định (128 hoặc 512)
5. WHEN trích xuất thất bại THEN Mobile App SHALL log lỗi và thông báo người dùng

### Requirement 6: Huấn luyện mô hình cá nhân trên thiết bị

**User Story:** Là người dùng, tôi muốn huấn luyện mô hình nhận diện từ các ảnh đã thu thập ngay trên điện thoại, để có mô hình cá nhân hóa.

#### Acceptance Criteria

1. WHEN người dùng nhấn nút huấn luyện THEN Mobile App SHALL đọc tất cả ảnh từ thư mục lưu trữ
2. WHEN không có ảnh nào THEN Mobile App SHALL hiển thị thông báo "Chưa có dữ liệu, vui lòng thu thập ảnh trước"
3. WHEN có ảnh THEN Mobile App SHALL trích xuất embedding từ mỗi ảnh
4. WHEN trích xuất xong THEN Mobile App SHALL tính toán embedding trung bình từ tất cả embeddings
5. WHEN tính toán xong THEN Mobile App SHALL lưu embedding trung bình vào local storage (SharedPreferences hoặc file)
6. WHEN lưu thành công THEN Mobile App SHALL hiển thị thông báo "Huấn luyện thành công với X ảnh"
7. WHEN huấn luyện xong THEN Mobile App SHALL đánh dấu trạng thái "đã huấn luyện" để enable tính năng nhận diện

### Requirement 7: Nhận diện khuôn mặt trên thiết bị

**User Story:** Là người dùng, tôi muốn nhận diện khuôn mặt từ ảnh mới ngay trên điện thoại, để xác thực danh tính offline.

#### Acceptance Criteria

1. WHEN người dùng nhấn nút nhận diện THEN Mobile App SHALL kiểm tra đã có mô hình đã huấn luyện chưa
2. WHEN chưa có mô hình THEN Mobile App SHALL hiển thị thông báo "Chưa huấn luyện mô hình, vui lòng huấn luyện trước"
3. WHEN có mô hình THEN Mobile App SHALL trích xuất embedding từ ảnh mới
4. WHEN có embedding mới THEN Mobile App SHALL tính khoảng cách Euclidean với embedding trung bình đã lưu
5. WHEN khoảng cách <= threshold THEN Mobile App SHALL hiển thị "Khớp ✓" với màu xanh
6. WHEN khoảng cách > threshold THEN Mobile App SHALL hiển thị "Không khớp ✗" với màu đỏ
7. WHEN nhận diện xong THEN Mobile App SHALL hiển thị khoảng cách, threshold và cảnh báo môi trường
8. WHEN nhận diện xong THEN Mobile App SHALL vẽ bounding box lên ảnh với màu tương ứng kết quả

### Requirement 8: Cấu hình và quản lý threshold

**User Story:** Là người dùng, tôi muốn điều chỉnh ngưỡng nhận diện, để kiểm soát độ chặt chẽ của việc xác thực.

#### Acceptance Criteria

1. WHEN người dùng mở màn hình nhận diện THEN Mobile App SHALL hiển thị slider để điều chỉnh threshold
2. WHEN người dùng kéo slider THEN Mobile App SHALL cập nhật giá trị threshold từ 0.3 đến 1.0
3. WHEN người dùng thay đổi threshold THEN Mobile App SHALL lưu giá trị vào SharedPreferences
4. WHEN app khởi động lại THEN Mobile App SHALL load threshold đã lưu từ SharedPreferences
5. WHEN threshold thay đổi THEN Mobile App SHALL hiển thị giá trị hiện tại bên cạnh slider

### Requirement 9: UI/UX cho mobile app offline

**User Story:** Là người dùng, tôi muốn giao diện rõ ràng và dễ sử dụng cho các chức năng offline, để thao tác thuận tiện.

#### Acceptance Criteria

1. WHEN người dùng mở app THEN Mobile App SHALL hiển thị bottom navigation với 3 tab: Thu thập, Huấn luyện, Nhận diện
2. WHEN ở tab Thu thập THEN Mobile App SHALL hiển thị camera preview, nút chụp, số ảnh đã thu thập và nút xóa dữ liệu
3. WHEN ở tab Huấn luyện THEN Mobile App SHALL hiển thị số ảnh hiện có, nút huấn luyện và trạng thái mô hình
4. WHEN ở tab Nhận diện THEN Mobile App SHALL hiển thị camera preview, slider threshold, nút nhận diện và kết quả
5. WHEN đang xử lý THEN Mobile App SHALL hiển thị loading indicator và disable các nút
6. WHEN có lỗi THEN Mobile App SHALL hiển thị dialog hoặc snackbar với thông báo lỗi rõ ràng
7. WHEN có cảnh báo môi trường THEN Mobile App SHALL hiển thị danh sách cảnh báo với icon warning

### Requirement 10: Quyền truy cập camera và storage

**User Story:** Là người dùng, tôi muốn app yêu cầu quyền truy cập camera và storage một cách rõ ràng, để hiểu tại sao app cần các quyền này.

#### Acceptance Criteria

1. WHEN app khởi động lần đầu THEN Mobile App SHALL yêu cầu quyền CAMERA
2. WHEN app khởi động lần đầu THEN Mobile App SHALL yêu cầu quyền WRITE_EXTERNAL_STORAGE (nếu cần)
3. WHEN người dùng từ chối quyền camera THEN Mobile App SHALL hiển thị thông báo "Cần quyền camera để chụp ảnh"
4. WHEN người dùng từ chối quyền storage THEN Mobile App SHALL hiển thị thông báo "Cần quyền lưu trữ để lưu ảnh"
5. WHEN người dùng cấp quyền THEN Mobile App SHALL cho phép sử dụng đầy đủ tính năng

### Requirement 11: Performance và tối ưu hóa

**User Story:** Là người dùng, tôi muốn app chạy mượt mà và không tốn quá nhiều pin, để trải nghiệm tốt trên thiết bị di động.

#### Acceptance Criteria

1. WHEN app load model lần đầu THEN Mobile App SHALL cache model trong memory
2. WHEN xử lý ảnh THEN Mobile App SHALL resize ảnh xuống kích thước phù hợp (max 1920x1080) trước khi xử lý
3. WHEN trích xuất embedding THEN Mobile App SHALL hoàn thành trong vòng 2 giây trên thiết bị tầm trung
4. WHEN huấn luyện với 10 ảnh THEN Mobile App SHALL hoàn thành trong vòng 10 giây
5. WHEN không sử dụng camera THEN Mobile App SHALL release camera resource để tiết kiệm pin

### Requirement 12: Xử lý lỗi và fallback

**User Story:** Là người dùng, tôi muốn app xử lý lỗi một cách graceful, để không bị crash khi có vấn đề.

#### Acceptance Criteria

1. WHEN ML Kit không khả dụng THEN Mobile App SHALL hiển thị thông báo "Thiết bị không hỗ trợ tính năng này"
2. WHEN camera không khả dụng THEN Mobile App SHALL hiển thị thông báo "Không thể truy cập camera"
3. WHEN bộ nhớ đầy THEN Mobile App SHALL hiển thị thông báo "Bộ nhớ đầy, vui lòng xóa dữ liệu cũ"
4. WHEN xử lý ảnh bị lỗi THEN Mobile App SHALL log lỗi và cho phép người dùng thử lại
5. WHEN app crash THEN Mobile App SHALL lưu trạng thái và khôi phục khi mở lại
