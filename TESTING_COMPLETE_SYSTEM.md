# Hướng dẫn Test Hệ thống Hoàn chỉnh

## Tổng quan

Hệ thống Face Recognition bao gồm 3 thành phần:
1. **Backend API** (FastAPI) - Port 8000
2. **Frontend Web** (Streamlit) - Port 8501
3. **Mobile App** (Flutter) - Android/iOS

## Kiểm tra Trước khi Test

### 1. Kiểm tra Backend
```bash
# Kiểm tra Python dependencies
python -c "import fastapi; import face_recognition; import cv2; print('Backend OK')"

# Chạy backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Mở trình duyệt: http://localhost:8000/docs
- Bạn sẽ thấy Swagger UI với các endpoints
- Test endpoint `/api/v1/health` → Phải trả về `{"status": "ok"}`

### 2. Kiểm tra Frontend Web
```bash
# Cài đặt dependencies (nếu chưa có)
pip install streamlit requests opencv-python pillow

# Kiểm tra import
python -c "import streamlit; import requests; import cv2; print('Web dependencies OK')"

# Chạy web app
streamlit run web/web_app.py
```

Mở trình duyệt: http://localhost:8501
- Bạn sẽ thấy giao diện với 3 tabs

### 3. Kiểm tra Mobile App
```bash
# Di chuyển vào thư mục mobile
cd mobile

# Kiểm tra Flutter
flutter doctor

# Kiểm tra dependencies
flutter pub get

# Chạy trên emulator/device
flutter run
```

## Test Workflow Hoàn chỉnh

### Bước 1: Khởi động Backend
```bash
# Terminal 1: Chạy backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Kiểm tra:**
- Terminal hiển thị: "Application startup complete"
- Không có lỗi
- Truy cập http://localhost:8000/docs thành công

---

## Test trên WEB APP

### Bước 2: Khởi động Web App
```bash
# Terminal 2: Chạy web app
streamlit run web/web_app.py
```

**Kiểm tra:**
- Trình duyệt tự động mở http://localhost:8501
- Hiển thị giao diện với 3 tabs

### Bước 3: Test Thu thập Dữ liệu (Web)

**Tab 1: Thu thập dữ liệu**

1. **Test Upload ảnh:**
   - Chọn "Upload ảnh từ máy"
   - Click "Browse files"
   - Chọn ảnh khuôn mặt của bạn
   - Click "Gửi ảnh để thu thập"
   
   **Kết quả mong đợi:**
   - ✅ Hiển thị "Ảnh đã được lưu thành công"
   - ✅ Hiển thị đường dẫn file đã lưu
   - ✅ Hiển thị tổng số ảnh đã thu thập
   - ✅ Hiển thị thông tin môi trường (độ sáng, độ mờ, tỷ lệ khuôn mặt)

2. **Test Chụp từ webcam:**
   - Chọn "Chụp từ webcam"
   - Click "📷 Chụp ảnh từ webcam"
   - Cho phép truy cập camera
   - Click "Gửi ảnh để thu thập"
   
   **Kết quả mong đợi:**
   - ✅ Webcam mở và chụp ảnh
   - ✅ Hiển thị ảnh đã chụp
   - ✅ Lưu thành công

3. **Test Môi trường kém:**
   - Upload ảnh quá tối/mờ/khuôn mặt nhỏ
   
   **Kết quả mong đợi:**
   - ❌ Hiển thị lỗi "Môi trường không đạt yêu cầu"
   - ⚠️ Hiển thị cảnh báo cụ thể (quá tối, quá mờ, etc.)

4. **Lặp lại 5-10 lần:**
   - Thu thập ít nhất 5 ảnh với góc độ khác nhau
   - Kiểm tra số lượng tăng dần: 1, 2, 3, 4, 5...

### Bước 4: Test Huấn luyện Mô hình (Web)

**Tab 2: Huấn luyện mô hình**

1. Click "🚀 Bắt đầu huấn luyện"
   
   **Kết quả mong đợi:**
   - ✅ Hiển thị "Huấn luyện thành công"
   - ✅ Hiển thị số ảnh đã đọc (≥ 5)
   - ✅ Hiển thị số embeddings đã sử dụng
   - ✅ Hiển thị animation balloons 🎈

2. **Kiểm tra file đã tạo:**
   ```bash
   # Kiểm tra thư mục models
   dir models
   ```
   
   **Phải có 2 files:**
   - `user_embeddings.npy`
   - `user_embedding_mean.npy`

### Bước 5: Test Nhận diện Khuôn mặt (Web)

**Tab 3: Nhận diện khuôn mặt**

1. **Test với ảnh của bạn (Should Match):**
   - Điều chỉnh threshold = 0.5
   - Upload ảnh khuôn mặt của bạn
   - Click "🔍 Nhận diện khuôn mặt"
   
   **Kết quả mong đợi:**
   - ✅ Hiển thị "Đây là KHUÔN MẶT CỦA BẠN"
   - ✅ Màu xanh lá
   - ✅ Bounding box màu xanh quanh khuôn mặt
   - ✅ Khoảng cách < threshold
   - ✅ Hiển thị thông tin môi trường

2. **Test với ảnh người khác (Should NOT Match):**
   - Upload ảnh khuôn mặt người khác
   - Click "🔍 Nhận diện khuôn mặt"
   
   **Kết quả mong đợi:**
   - ❌ Hiển thị "KHÔNG PHẢI khuôn mặt của bạn"
   - ❌ Màu đỏ
   - ❌ Bounding box màu đỏ
   - ❌ Khoảng cách > threshold

3. **Test điều chỉnh Threshold:**
   - Thử các giá trị: 0.3, 0.5, 0.7
   - Kiểm tra kết quả thay đổi

4. **Test Error Cases:**
   - Upload ảnh không có khuôn mặt → Lỗi
   - Upload ảnh có nhiều người → Lỗi
   - Upload file không phải ảnh → Lỗi

---

## Test trên MOBILE APP

### Bước 6: Khởi động Mobile App

**Chuẩn bị:**
1. Đảm bảo Backend đang chạy (port 8000)
2. Kiểm tra địa chỉ IP:
   - Android Emulator: `http://10.0.2.2:8000` (đã cấu hình sẵn)
   - Thiết bị thật: Cần thay đổi IP trong `mobile/lib/main.dart`

**Chạy app:**
```bash
cd mobile
flutter run
```

**Chọn device:**
- Chọn Android emulator hoặc thiết bị thật
- App sẽ build và cài đặt

### Bước 7: Test Thu thập Dữ liệu (Mobile)

1. **Test Chụp ảnh:**
   - Click "Chụp ảnh"
   - Cho phép quyền camera
   - Chụp ảnh khuôn mặt
   - Click "Gửi làm dữ liệu huấn luyện"
   
   **Kết quả mong đợi:**
   - ✅ Trạng thái: "Thành công"
   - ✅ Hiển thị tổng số ảnh
   - ✅ Hiển thị đường dẫn file

2. **Test Chọn ảnh từ gallery:**
   - Click "Chọn ảnh"
   - Chọn ảnh từ gallery
   - Click "Gửi làm dữ liệu huấn luyện"
   
   **Kết quả mong đợi:**
   - ✅ Tương tự như trên

3. **Test Môi trường kém:**
   - Chọn ảnh quá tối/mờ
   - Click "Gửi làm dữ liệu huấn luyện"
   
   **Kết quả mong đợi:**
   - ❌ Trạng thái: "Lỗi" (màu đỏ)
   - ⚠️ Hiển thị cảnh báo môi trường

4. **Thu thập 5-10 ảnh:**
   - Lặp lại với góc độ khác nhau

### Bước 8: Test Huấn luyện Mô hình (Mobile)

1. Click "Huấn luyện mô hình"
   
   **Kết quả mong đợi:**
   - ✅ Trạng thái: "Huấn luyện thành công" (màu xanh)
   - ✅ Hiển thị số ảnh và số embeddings
   - ✅ Loading indicator trong quá trình huấn luyện

### Bước 9: Test Nhận diện Khuôn mặt (Mobile)

1. **Test với ảnh của bạn:**
   - Điều chỉnh ngưỡng = 0.6
   - Chụp hoặc chọn ảnh của bạn
   - Click "Nhận diện"
   
   **Kết quả mong đợi:**
   - ✅ Trạng thái: "Khớp ✓" (màu xanh)
   - ✅ Hiển thị khoảng cách và ngưỡng
   - ✅ Hiển thị message chi tiết

2. **Test với ảnh người khác:**
   - Chọn ảnh người khác
   - Click "Nhận diện"
   
   **Kết quả mong đợi:**
   - ❌ Trạng thái: "Không khớp ✗" (màu đỏ)
   - ❌ Khoảng cách > ngưỡng

3. **Test điều chỉnh Threshold:**
   - Kéo slider từ 0.3 đến 1.0
   - Test với các giá trị khác nhau

4. **Test Cảnh báo môi trường:**
   - Chọn ảnh có môi trường kém
   - Click "Nhận diện"
   
   **Kết quả mong đợi:**
   - ⚠️ Hiển thị cảnh báo môi trường (màu cam)
   - ⚠️ Liệt kê các vấn đề cụ thể

---

## Test Cases Đặc biệt

### Test Error Handling

1. **Backend không chạy:**
   - Tắt backend
   - Thử gọi API từ web/mobile
   
   **Kết quả mong đợi:**
   - ❌ Hiển thị "Không thể kết nối đến server"

2. **File không hợp lệ:**
   - Upload file PDF/TXT
   
   **Kết quả mong đợi:**
   - ❌ Hiển thị "File upload phải là ảnh"

3. **File quá lớn:**
   - Upload file > 10MB
   
   **Kết quả mong đợi:**
   - ❌ Hiển thị "File quá lớn"

4. **Không có khuôn mặt:**
   - Upload ảnh phong cảnh
   
   **Kết quả mong đợi:**
   - ❌ Hiển thị "Không tìm thấy khuôn mặt"

5. **Nhiều khuôn mặt:**
   - Upload ảnh nhóm người
   
   **Kết quả mong đợi:**
   - ❌ Hiển thị "Phát hiện N khuôn mặt"

### Test Performance

1. **Thời gian xử lý:**
   - Thu thập: < 2 giây
   - Huấn luyện: < 10 giây (với 10 ảnh)
   - Nhận diện: < 2 giây

2. **Concurrent requests:**
   - Mở nhiều tab web
   - Gửi request đồng thời
   
   **Kết quả mong đợi:**
   - ✅ Tất cả request đều được xử lý

---

## Checklist Tổng hợp

### Backend ✅
- [ ] Health check hoạt động
- [ ] Collect endpoint hoạt động
- [ ] Train endpoint hoạt động
- [ ] Verify endpoint hoạt động
- [ ] Error handling đúng
- [ ] CORS được cấu hình

### Web App ✅
- [ ] Giao diện hiển thị đúng
- [ ] Upload ảnh hoạt động
- [ ] Chụp webcam hoạt động
- [ ] Thu thập dữ liệu thành công
- [ ] Huấn luyện thành công
- [ ] Nhận diện chính xác
- [ ] Hiển thị environment info
- [ ] Hiển thị bounding box
- [ ] Error messages rõ ràng

### Mobile App ✅
- [ ] App build và cài đặt thành công
- [ ] Giao diện hiển thị đúng
- [ ] Camera hoạt động
- [ ] Gallery picker hoạt động
- [ ] Kết nối backend thành công
- [ ] Thu thập dữ liệu thành công
- [ ] Huấn luyện thành công
- [ ] Nhận diện chính xác
- [ ] Threshold slider hoạt động
- [ ] Hiển thị cảnh báo môi trường
- [ ] Loading states hoạt động
- [ ] Error handling đúng

---

## Troubleshooting

### Web App không kết nối Backend
```bash
# Kiểm tra Backend đang chạy
curl http://localhost:8000/api/v1/health

# Kiểm tra CORS
# Xem console log trong browser
```

### Mobile App không kết nối Backend

**Android Emulator:**
```dart
// Trong mobile/lib/main.dart
final String baseUrl = 'http://10.0.2.2:8000';
```

**Thiết bị thật:**
1. Kiểm tra IP máy tính:
   ```bash
   ipconfig  # Windows
   ifconfig  # Linux/Mac
   ```

2. Thay đổi trong `mobile/lib/main.dart`:
   ```dart
   final String baseUrl = 'http://192.168.1.XXX:8000';
   ```

3. Đảm bảo cùng mạng WiFi

4. Tắt firewall hoặc cho phép port 8000

### Webcam không hoạt động
- Kiểm tra quyền truy cập camera
- Đóng các ứng dụng khác đang dùng camera
- Thử restart browser/app

---

## Kết luận

Sau khi hoàn thành tất cả test cases trên, bạn có thể xác nhận:

✅ **Backend API** hoạt động đầy đủ với 3 endpoints chính
✅ **Web App** hoạt động hoàn chỉnh với đầy đủ chức năng
✅ **Mobile App** hoạt động hoàn chỉnh trên Android/iOS
✅ **Workflow hoàn chỉnh**: Thu thập → Huấn luyện → Nhận diện
✅ **Error handling** đầy đủ và rõ ràng
✅ **Environment checking** hoạt động chính xác

Hệ thống đã sẵn sàng để sử dụng! 🎉
