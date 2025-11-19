# Tài liệu Yêu cầu

## Giới thiệu

Hệ thống backend Python nhận diện khuôn mặt cá nhân cung cấp REST API cho phép ứng dụng web và mobile xác thực danh tính người dùng thông qua hình ảnh khuôn mặt. Hệ thống sử dụng công nghệ face recognition để so sánh khuôn mặt trong ảnh upload với dữ liệu đã được huấn luyện trước.

## Thuật ngữ

- **Backend**: Hệ thống máy chủ xử lý logic nhận diện khuôn mặt
- **Face Embedding**: Vector đặc trưng 128 chiều đại diện cho khuôn mặt
- **Threshold**: Ngưỡng khoảng cách để xác định hai khuôn mặt có khớp nhau hay không
- **Training Data**: Tập ảnh khuôn mặt được sử dụng để tạo face embedding tham chiếu
- **Client**: Ứng dụng web hoặc mobile gọi API của backend
- **Face Location**: Tọa độ vị trí khuôn mặt trong ảnh (top, right, bottom, left)

## Yêu cầu

### Yêu cầu 1: Khởi tạo và tải dữ liệu huấn luyện

**User Story:** Là một quản trị viên hệ thống, tôi muốn backend tự động tải và xử lý ảnh huấn luyện khi khởi động, để hệ thống sẵn sàng nhận diện khuôn mặt.

#### Tiêu chí chấp nhận

1. WHEN the Backend khởi động THEN the Backend SHALL đọc tất cả ảnh từ thư mục `myface/` với định dạng jpg, jpeg, hoặc png
2. WHEN the Backend xử lý một ảnh huấn luyện THEN the Backend SHALL trích xuất đúng một face embedding từ ảnh đó
3. IF một ảnh huấn luyện chứa không có hoặc nhiều hơn một khuôn mặt THEN the Backend SHALL bỏ qua ảnh đó và ghi log cảnh báo
4. WHEN the Backend hoàn tất tải dữ liệu THEN the Backend SHALL lưu trữ tất cả face embeddings trong bộ nhớ cache
5. IF thư mục `myface/` không tồn tại hoặc không chứa ảnh hợp lệ nào THEN the Backend SHALL ném FileNotFoundError hoặc ValueError với thông báo rõ ràng

### Yêu cầu 2: API kiểm tra trạng thái hệ thống

**User Story:** Là một nhà phát triển client, tôi muốn kiểm tra backend có đang hoạt động hay không, để đảm bảo kết nối trước khi gửi yêu cầu nhận diện.

#### Tiêu chí chấp nhận

1. WHEN the Client gửi GET request đến `/api/v1/health` THEN the Backend SHALL trả về HTTP 200 với JSON `{"status": "ok"}`
2. WHEN the Backend nhận request health check THEN the Backend SHALL phản hồi trong vòng 100 milliseconds

### Yêu cầu 3: API xác thực khuôn mặt

**User Story:** Là một người dùng ứng dụng, tôi muốn upload ảnh khuôn mặt của mình để hệ thống xác nhận danh tính, để truy cập vào các tính năng được bảo vệ.

#### Tiêu chí chấp nhận

1. WHEN the Client gửi POST request đến `/api/v1/face/verify` với file ảnh THEN the Backend SHALL chấp nhận file với content-type là image/jpeg, image/jpg, hoặc image/png
2. WHEN the Backend nhận ảnh hợp lệ THEN the Backend SHALL chuyển đổi ảnh sang định dạng RGB và trích xuất face embedding
3. WHEN the Backend trích xuất face embedding từ ảnh upload THEN the Backend SHALL so sánh với tất cả face embeddings trong training data
4. WHEN the Backend tính khoảng cách giữa các face embeddings THEN the Backend SHALL sử dụng khoảng cách nhỏ nhất để xác định kết quả
5. IF khoảng cách nhỏ nhất nhỏ hơn hoặc bằng threshold THEN the Backend SHALL trả về `is_match: true`
6. IF khoảng cách nhỏ nhất lớn hơn threshold THEN the Backend SHALL trả về `is_match: false`

### Yêu cầu 4: Xử lý tham số threshold

**User Story:** Là một nhà phát triển client, tôi muốn điều chỉnh ngưỡng so sánh khuôn mặt, để tối ưu độ chính xác cho từng trường hợp sử dụng.

#### Tiêu chí chấp nhận

1. WHEN the Client gửi request với query parameter `threshold` THEN the Backend SHALL sử dụng giá trị threshold đó cho việc so sánh
2. WHEN the Client không cung cấp threshold THEN the Backend SHALL sử dụng giá trị mặc định 0.5
3. WHEN the Client cung cấp threshold THEN the Backend SHALL chỉ chấp nhận giá trị từ 0.0 đến 1.0
4. IF threshold nằm ngoài khoảng hợp lệ THEN the Backend SHALL trả về HTTP 422 với thông báo lỗi validation

### Yêu cầu 5: Định dạng phản hồi JSON

**User Story:** Là một nhà phát triển client, tôi muốn nhận được thông tin chi tiết về kết quả nhận diện dưới dạng JSON, để hiển thị cho người dùng và xử lý logic ứng dụng.

#### Tiêu chí chấp nhận

1. WHEN the Backend hoàn tất xác thực khuôn mặt THEN the Backend SHALL trả về JSON chứa trường `is_match` kiểu boolean
2. WHEN the Backend trả về kết quả THEN the Backend SHALL bao gồm trường `distance` với giá trị khoảng cách tính được
3. WHEN the Backend trả về kết quả THEN the Backend SHALL bao gồm trường `threshold` với giá trị ngưỡng đã sử dụng
4. WHEN the Backend trả về kết quả THEN the Backend SHALL bao gồm trường `message` với thông điệp mô tả kết quả bằng tiếng Việt
5. WHEN the Backend trả về kết quả THEN the Backend SHALL bao gồm trường `face_box` với tọa độ top, right, bottom, left của khuôn mặt
6. WHEN the Backend trả về kết quả THEN the Backend SHALL bao gồm trường `image_size` với width và height của ảnh
7. WHEN the Backend trả về kết quả THEN the Backend SHALL bao gồm trường `training_info` với số lượng ảnh huấn luyện đã sử dụng

### Yêu cầu 6: Xử lý lỗi ảnh không hợp lệ

**User Story:** Là một người dùng, tôi muốn nhận được thông báo rõ ràng khi ảnh upload không phù hợp, để biết cách khắc phục.

#### Tiêu chí chấp nhận

1. IF ảnh upload không phải định dạng jpg, jpeg, hoặc png THEN the Backend SHALL trả về HTTP 400 với message "File upload phải là ảnh (.jpg, .jpeg, .png)."
2. IF ảnh upload không đọc được hoặc bị hỏng THEN the Backend SHALL trả về HTTP 400 với message "Không đọc được ảnh từ dữ liệu upload..."
3. IF ảnh upload không chứa khuôn mặt nào THEN the Backend SHALL trả về HTTP 400 với message "Không tìm thấy khuôn mặt nào trong ảnh..."
4. IF ảnh upload chứa nhiều hơn một khuôn mặt THEN the Backend SHALL trả về HTTP 400 với message "Phát hiện N khuôn mặt trong ảnh. Vui lòng để CHỈ MỘT người trong ảnh..."
5. IF không trích xuất được face embedding từ ảnh THEN the Backend SHALL trả về HTTP 400 với message "Không trích xuất được vector đặc trưng cho khuôn mặt..."

### Yêu cầu 7: Xử lý lỗi hệ thống

**User Story:** Là một quản trị viên, tôi muốn hệ thống xử lý các lỗi nội bộ một cách an toàn, để tránh crash và dễ dàng debug.

#### Tiêu chí chấp nhận

1. IF xảy ra lỗi khi tải dữ liệu huấn luyện THEN the Backend SHALL trả về HTTP 500 với thông báo lỗi chi tiết
2. IF xảy ra lỗi nội bộ trong quá trình xử lý ảnh THEN the Backend SHALL trả về HTTP 500 với message bắt đầu bằng "Lỗi nội bộ..."
3. WHEN the Backend trả về lỗi HTTP THEN the Backend SHALL sử dụng định dạng JSON với trường `detail` chứa thông báo lỗi
4. WHEN xảy ra exception THEN the Backend SHALL không crash mà xử lý exception và trả về HTTP response phù hợp

### Yêu cầu 8: Hỗ trợ CORS cho client đa nền tảng

**User Story:** Là một nhà phát triển web, tôi muốn gọi API từ trình duyệt mà không bị chặn bởi CORS policy, để tích hợp backend vào ứng dụng web.

#### Tiêu chí chấp nhận

1. WHEN the Client từ bất kỳ origin nào gửi request THEN the Backend SHALL cho phép request đó thông qua CORS middleware
2. WHEN the Backend nhận preflight request THEN the Backend SHALL trả về các CORS headers phù hợp
3. WHEN the Backend cấu hình CORS THEN the Backend SHALL cho phép tất cả HTTP methods và headers

### Yêu cầu 9: Hiệu năng và cache

**User Story:** Là một quản trị viên hệ thống, tôi muốn dữ liệu huấn luyện được cache, để tránh tải lại mỗi khi có request và tăng tốc độ phản hồi.

#### Tiêu chí chấp nhận

1. WHEN the Backend tải dữ liệu huấn luyện lần đầu THEN the Backend SHALL lưu kết quả vào cache
2. WHEN the Backend nhận request xác thực khuôn mặt THEN the Backend SHALL sử dụng dữ liệu từ cache thay vì tải lại
3. WHEN the Backend xử lý request xác thực THEN the Backend SHALL hoàn tất trong vòng 2 giây cho ảnh có kích thước dưới 5MB
