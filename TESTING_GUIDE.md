# Hướng dẫn Test Thực tế với Ảnh Huấn luyện

## Mục đích
Tài liệu này hướng dẫn cách chuẩn bị ảnh huấn luyện và test backend face recognition với dữ liệu thực tế.

## Bước 1: Chuẩn bị Ảnh Huấn luyện

### 1.1 Tạo thư mục myface/
```bash
# Thư mục myface/ đã được tạo sẵn trong dự án
# Nếu chưa có, tạo bằng lệnh:
mkdir myface
```

### 1.2 Chụp và chuẩn bị ảnh
Bạn cần chuẩn bị **5-7 ảnh** của chính bạn với các yêu cầu sau:

**Yêu cầu về ảnh:**
- ✅ Định dạng: JPG, JPEG, hoặc PNG
- ✅ Chỉ có **MỘT** khuôn mặt trong mỗi ảnh
- ✅ Khuôn mặt chiếm ít nhất 30-40% khung hình
- ✅ Ánh sáng đủ, không quá tối hoặc quá sáng
- ✅ Khuôn mặt nhìn rõ, không bị che khuất nhiều

**Đa dạng hóa ảnh huấn luyện:**
1. **Góc chụp khác nhau:**
   - Ảnh chính diện (nhìn thẳng vào camera)
   - Ảnh nghiêng nhẹ sang trái (~15-30 độ)
   - Ảnh nghiêng nhẹ sang phải (~15-30 độ)
   - Ảnh nhìn từ trên xuống nhẹ
   - Ảnh nhìn từ dưới lên nhẹ

2. **Điều kiện ánh sáng:**
   - Ảnh trong nhà với ánh sáng tự nhiên
   - Ảnh ngoài trời
   - Ảnh với ánh sáng đèn

3. **Biểu cảm:**
   - Mặt bình thường
   - Mỉm cười nhẹ
   - Nghiêm túc

4. **Phụ kiện (tùy chọn):**
   - Ảnh đeo kính (nếu bạn thường đeo kính)
   - Ảnh không đeo kính

### 1.3 Đặt tên file
Đặt tên file rõ ràng, ví dụ:
```
myface/
├── front_1.jpg
├── front_2.jpg
├── left_angle.jpg
├── right_angle.jpg
├── with_glasses.jpg
├── outdoor.jpg
└── smile.jpg
```

### 1.4 Kiểm tra ảnh
Trước khi chạy backend, hãy kiểm tra:
- [ ] Mỗi ảnh chỉ có 1 khuôn mặt
- [ ] Khuôn mặt nhìn rõ ràng
- [ ] Có ít nhất 5 ảnh
- [ ] Các ảnh có góc chụp đa dạng

## Bước 2: Chạy Backend

### 2.1 Cài đặt dependencies (nếu chưa)
```bash
pip install -r requirements.txt
```

### 2.2 Khởi động server
```bash
# Development mode
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Hoặc production mode
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2.3 Kiểm tra server đã chạy
Mở trình duyệt và truy cập:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

Bạn sẽ thấy:
```json
{"status": "ok"}
```

## Bước 3: Test với Postman

### 3.1 Cài đặt Postman
Tải và cài đặt Postman từ: https://www.postman.com/downloads/

### 3.2 Test Health Check
1. Tạo request mới
2. Method: GET
3. URL: `http://localhost:8000/api/v1/health`
4. Click "Send"
5. Kết quả mong đợi: `{"status": "ok"}`

### 3.3 Test Face Verification - Ảnh của bạn (Should Match)

**Test Case 1: Ảnh của bạn với threshold mặc định**
1. Tạo request mới
2. Method: POST
3. URL: `http://localhost:8000/api/v1/face/verify`
4. Tab "Body" → chọn "form-data"
5. Thêm key "file" với type "File"
6. Chọn một ảnh của bạn (không phải ảnh trong myface/)
7. Click "Send"

**Kết quả mong đợi:**
```json
{
  "is_match": true,
  "distance": 0.35,  // Giá trị nhỏ hơn 0.5
  "threshold": 0.5,
  "message": "Đây là KHUÔN MẶT CỦA BẠN (khoảng cách = 0.350 ≤ ngưỡng 0.500).",
  "face_box": {
    "top": 100,
    "right": 300,
    "bottom": 400,
    "left": 100
  },
  "image_size": {
    "width": 640,
    "height": 480
  },
  "training_info": {
    "num_images": 7,
    "used_files_sample": ["front_1.jpg", "front_2.jpg", ...]
  }
}
```

**Test Case 2: Ảnh của bạn với threshold tùy chỉnh**
1. Giống Test Case 1
2. URL: `http://localhost:8000/api/v1/face/verify?threshold=0.4`
3. Click "Send"

### 3.4 Test Face Verification - Ảnh người khác (Should NOT Match)

**Test Case 3: Ảnh người khác**
1. Tạo request mới
2. Method: POST
3. URL: `http://localhost:8000/api/v1/face/verify`
4. Tab "Body" → chọn "form-data"
5. Thêm key "file" với type "File"
6. Chọn ảnh của người khác (tải từ internet hoặc ảnh bạn bè)
7. Click "Send"

**Kết quả mong đợi:**
```json
{
  "is_match": false,
  "distance": 0.75,  // Giá trị lớn hơn 0.5
  "threshold": 0.5,
  "message": "Đây KHÔNG PHẢI khuôn mặt của bạn (khoảng cách = 0.750 > ngưỡng 0.500).",
  ...
}
```

### 3.5 Test với các góc chụp khác nhau

**Test Case 4: Ảnh nghiêng**
- Chụp ảnh của bạn với góc nghiêng (~30 độ)
- Upload và kiểm tra kết quả
- Mong đợi: `is_match: true` (nếu ảnh huấn luyện có góc tương tự)

**Test Case 5: Ảnh đeo kính**
- Chụp ảnh của bạn đeo kính
- Upload và kiểm tra kết quả
- Mong đợi: `is_match: true` (nếu ảnh huấn luyện có ảnh đeo kính)

### 3.6 Test Error Cases

**Test Case 6: Ảnh không có khuôn mặt**
- Upload ảnh phong cảnh hoặc vật thể
- Mong đợi: HTTP 400 với message "Không tìm thấy khuôn mặt nào trong ảnh..."

**Test Case 7: Ảnh có nhiều khuôn mặt**
- Upload ảnh có 2+ người
- Mong đợi: HTTP 400 với message "Phát hiện N khuôn mặt trong ảnh..."

**Test Case 8: File không phải ảnh**
- Upload file .txt hoặc .pdf
- Mong đợi: HTTP 400 với message "File upload phải là ảnh (.jpg, .jpeg, .png)."

## Bước 4: Test với cURL

### 4.1 Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### 4.2 Face Verification
```bash
# Test với ảnh của bạn
curl -X POST "http://localhost:8000/api/v1/face/verify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/photo.jpg"

# Test với threshold tùy chỉnh
curl -X POST "http://localhost:8000/api/v1/face/verify?threshold=0.4" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/photo.jpg"
```

### 4.3 Test với ảnh người khác
```bash
curl -X POST "http://localhost:8000/api/v1/face/verify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/other/person.jpg"
```

## Bước 5: Test với Python Script

Tạo file `test_manual.py`:

```python
import requests

# Test health check
response = requests.get("http://localhost:8000/api/v1/health")
print("Health Check:", response.json())

# Test face verification
with open("path/to/your/photo.jpg", "rb") as f:
    files = {"file": ("photo.jpg", f, "image/jpeg")}
    response = requests.post(
        "http://localhost:8000/api/v1/face/verify",
        files=files,
        params={"threshold": 0.5}
    )
    print("Verification Result:", response.json())
```

Chạy:
```bash
python test_manual.py
```

## Bước 6: Đánh giá Kết quả

### 6.1 Checklist Test Cases
- [ ] Health check trả về status "ok"
- [ ] Ảnh của bạn (chính diện) → is_match: true
- [ ] Ảnh của bạn (góc nghiêng) → is_match: true
- [ ] Ảnh của bạn (đeo kính) → is_match: true
- [ ] Ảnh người khác → is_match: false
- [ ] Ảnh không có khuôn mặt → HTTP 400
- [ ] Ảnh có nhiều khuôn mặt → HTTP 400
- [ ] File không phải ảnh → HTTP 400
- [ ] Threshold tùy chỉnh hoạt động đúng
- [ ] Response có đầy đủ các trường bắt buộc

### 6.2 Điều chỉnh Threshold
Nếu kết quả không chính xác:

**False Negative (Ảnh của bạn nhưng không match):**
- Tăng threshold lên 0.6 hoặc 0.7
- Thêm nhiều ảnh huấn luyện đa dạng hơn

**False Positive (Ảnh người khác nhưng match):**
- Giảm threshold xuống 0.4 hoặc 0.3
- Đảm bảo ảnh huấn luyện chất lượng tốt

### 6.3 Cải thiện Độ chính xác
1. **Thêm ảnh huấn luyện:**
   - Tăng số lượng lên 10-15 ảnh
   - Đảm bảo đa dạng góc chụp và điều kiện ánh sáng

2. **Chất lượng ảnh:**
   - Sử dụng ảnh có độ phân giải cao (ít nhất 640x480)
   - Khuôn mặt chiếm 40-50% khung hình
   - Ánh sáng đều, không bị tối hoặc quá sáng

3. **Điều chỉnh threshold:**
   - Threshold thấp (0.3-0.4): Nghiêm ngặt hơn, ít false positive
   - Threshold cao (0.6-0.7): Linh hoạt hơn, ít false negative
   - Threshold mặc định (0.5): Cân bằng

## Bước 7: Test Performance

### 7.1 Test Response Time
```bash
# Đo thời gian response
time curl -X POST "http://localhost:8000/api/v1/face/verify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@photo.jpg"
```

Mong đợi: < 2 giây cho ảnh dưới 5MB

### 7.2 Test Concurrent Requests
Sử dụng tool như Apache Bench:
```bash
# Cài đặt Apache Bench (ab)
# Windows: Tải từ Apache website
# Linux: sudo apt-get install apache2-utils

# Test 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8000/api/v1/health
```

## Troubleshooting

### Lỗi: "Không tìm thấy thư mục myface/"
- Kiểm tra thư mục myface/ tồn tại trong thư mục gốc dự án
- Chạy backend từ đúng thư mục gốc

### Lỗi: "Không tìm thấy ảnh hợp lệ nào"
- Kiểm tra có ít nhất 1 ảnh trong myface/
- Kiểm tra định dạng file (.jpg, .jpeg, .png)
- Kiểm tra mỗi ảnh chỉ có 1 khuôn mặt

### Lỗi: "Không tìm thấy khuôn mặt nào trong ảnh"
- Khuôn mặt quá nhỏ trong ảnh
- Ánh sáng quá tối
- Khuôn mặt bị che khuất nhiều
- Góc chụp quá nghiêng (> 45 độ)

### Kết quả không chính xác
- Thêm nhiều ảnh huấn luyện đa dạng hơn
- Điều chỉnh threshold phù hợp
- Kiểm tra chất lượng ảnh huấn luyện

## Kết luận

Sau khi hoàn thành tất cả các test cases trên, bạn đã:
- ✅ Chuẩn bị ảnh huấn luyện đúng cách
- ✅ Chạy backend thành công
- ✅ Test với ảnh của chính bạn (should match)
- ✅ Test với ảnh người khác (should not match)
- ✅ Test với các góc chụp khác nhau
- ✅ Test với ảnh đeo kính
- ✅ Test các error cases
- ✅ Đánh giá và điều chỉnh threshold

Backend face recognition của bạn đã sẵn sàng để tích hợp vào ứng dụng web hoặc mobile!
