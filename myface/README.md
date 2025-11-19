# Thư mục Ảnh Huấn luyện (Training Images)

## Mục đích
Thư mục này chứa ảnh khuôn mặt của bạn để backend học và nhận diện.

## Hướng dẫn Chuẩn bị Ảnh

### Yêu cầu Bắt buộc
- ✅ **Định dạng**: JPG, JPEG, hoặc PNG
- ✅ **Số lượng khuôn mặt**: CHỈ MỘT khuôn mặt trong mỗi ảnh
- ✅ **Số lượng ảnh**: Tối thiểu 5 ảnh, khuyến nghị 7-10 ảnh
- ✅ **Kích thước khuôn mặt**: Chiếm ít nhất 30-40% khung hình
- ✅ **Ánh sáng**: Đủ sáng, không quá tối hoặc quá chói
- ✅ **Độ rõ nét**: Khuôn mặt nhìn rõ, không bị mờ

### Khuyến nghị Đa dạng hóa

#### 1. Góc chụp (5-7 ảnh)
- 📸 **Chính diện** (2-3 ảnh): Nhìn thẳng vào camera
- 📸 **Nghiêng trái** (1 ảnh): Xoay mặt sang trái ~20-30 độ
- 📸 **Nghiêng phải** (1 ảnh): Xoay mặt sang phải ~20-30 độ
- 📸 **Từ trên xuống** (1 ảnh): Camera cao hơn mặt một chút
- 📸 **Từ dưới lên** (1 ảnh): Camera thấp hơn mặt một chút

#### 2. Điều kiện Ánh sáng
- ☀️ Ánh sáng tự nhiên (trong nhà gần cửa sổ)
- 💡 Ánh sáng đèn (trong nhà)
- 🌤️ Ngoài trời (không quá chói)

#### 3. Biểu cảm
- 😐 Mặt bình thường (3-4 ảnh)
- 🙂 Mỉm cười nhẹ (2-3 ảnh)
- 😊 Cười tươi (1 ảnh)

#### 4. Phụ kiện (nếu thường xuyên sử dụng)
- 👓 Đeo kính (2-3 ảnh nếu bạn thường đeo kính)
- 🎩 Mũ/nón (tùy chọn, nếu thường đeo)

### Ví dụ Cấu trúc Thư mục

```
myface/
├── front_normal_1.jpg      # Chính diện, mặt bình thường
├── front_normal_2.jpg      # Chính diện, mặt bình thường
├── front_smile.jpg         # Chính diện, mỉm cười
├── left_angle.jpg          # Nghiêng trái
├── right_angle.jpg         # Nghiêng phải
├── with_glasses_1.jpg      # Đeo kính, chính diện
├── with_glasses_2.jpg      # Đeo kính, nghiêng
├── outdoor.jpg             # Ngoài trời
└── indoor_light.jpg        # Trong nhà, ánh sáng tự nhiên
```

## Cách Chụp Ảnh Tốt

### ✅ NÊN
- ✅ Chụp trong điều kiện ánh sáng tốt
- ✅ Khuôn mặt chiếm 40-50% khung hình
- ✅ Nhìn thẳng vào camera (với ảnh chính diện)
- ✅ Giữ camera ở tầm mắt
- ✅ Nền đơn giản, không quá rối
- ✅ Sử dụng camera tốt (điện thoại hiện đại là đủ)

### ❌ KHÔNG NÊN
- ❌ Chụp trong điều kiện quá tối
- ❌ Chụp ngược sáng (đèn/cửa sổ phía sau)
- ❌ Khuôn mặt quá nhỏ trong ảnh
- ❌ Khuôn mặt bị che khuất nhiều (khẩu trang, tay, tóc)
- ❌ Ảnh bị mờ hoặc rung
- ❌ Góc chụp quá nghiêng (> 45 độ)
- ❌ Có nhiều người trong ảnh

## Quy trình Chụp Ảnh Nhanh

### Phương án 1: Tự chụp với điện thoại
1. Mở camera selfie trên điện thoại
2. Tìm nơi có ánh sáng tốt (gần cửa sổ hoặc đèn)
3. Giữ điện thoại ở tầm mắt, cách mặt ~50cm
4. Chụp 2-3 ảnh chính diện
5. Xoay mặt sang trái, chụp 1 ảnh
6. Xoay mặt sang phải, chụp 1 ảnh
7. Nếu đeo kính, chụp thêm 2 ảnh với kính
8. Chuyển ảnh vào thư mục này

### Phương án 2: Nhờ người khác chụp
1. Đứng ở nơi có ánh sáng tốt
2. Nhờ người khác giữ camera ở tầm mắt bạn
3. Chụp theo các góc độ khác nhau
4. Chuyển ảnh vào thư mục này

### Phương án 3: Sử dụng webcam
1. Ngồi trước máy tính có webcam
2. Mở ứng dụng Camera (Windows) hoặc Photo Booth (Mac)
3. Điều chỉnh ánh sáng và vị trí
4. Chụp theo các góc độ khác nhau
5. Lưu ảnh vào thư mục này

## Kiểm tra Ảnh Trước khi Sử dụng

### Checklist
- [ ] Có ít nhất 5 ảnh trong thư mục
- [ ] Mỗi ảnh chỉ có 1 khuôn mặt
- [ ] Khuôn mặt nhìn rõ ràng
- [ ] Có ảnh chính diện
- [ ] Có ảnh nghiêng trái/phải
- [ ] Ánh sáng đủ trong tất cả ảnh
- [ ] Định dạng file đúng (.jpg, .jpeg, .png)

### Công cụ Kiểm tra
Sau khi chuẩn bị ảnh, chạy backend và kiểm tra log:
```bash
uvicorn backend.main:app --reload
```

Backend sẽ hiển thị:
- ✅ Số lượng ảnh đã load thành công
- ⚠️ Ảnh nào bị bỏ qua (và lý do)

## Troubleshooting

### "Không tìm thấy ảnh hợp lệ nào"
**Nguyên nhân:**
- Thư mục myface/ rỗng
- Không có file .jpg, .jpeg, .png
- Tất cả ảnh đều có 0 hoặc nhiều hơn 1 khuôn mặt

**Giải pháp:**
- Thêm ít nhất 5 ảnh vào thư mục
- Kiểm tra định dạng file
- Đảm bảo mỗi ảnh chỉ có 1 khuôn mặt

### "Ảnh bị bỏ qua: Không tìm thấy khuôn mặt"
**Nguyên nhân:**
- Khuôn mặt quá nhỏ
- Ánh sáng quá tối
- Khuôn mặt bị che khuất
- Góc chụp quá nghiêng

**Giải pháp:**
- Chụp lại ảnh với khuôn mặt lớn hơn
- Cải thiện ánh sáng
- Đảm bảo khuôn mặt không bị che

### "Ảnh bị bỏ qua: Phát hiện nhiều khuôn mặt"
**Nguyên nhân:**
- Có nhiều người trong ảnh
- Có ảnh/poster người khác trong background

**Giải pháp:**
- Chụp lại với chỉ 1 người
- Chọn nền đơn giản

## Tips để Tăng Độ chính xác

1. **Số lượng ảnh**: Càng nhiều càng tốt (7-15 ảnh)
2. **Đa dạng**: Nhiều góc độ và điều kiện ánh sáng khác nhau
3. **Chất lượng**: Ảnh rõ nét, khuôn mặt lớn
4. **Cập nhật**: Thêm ảnh mới định kỳ (mỗi 3-6 tháng)
5. **Phụ kiện**: Nếu thường đeo kính, thêm ảnh có kính

## Bảo mật

⚠️ **Lưu ý Quan trọng:**
- Ảnh trong thư mục này chứa dữ liệu sinh trắc học của bạn
- Không chia sẻ thư mục này công khai
- Thêm `myface/` vào `.gitignore` nếu dùng Git
- Backend chỉ lưu face embeddings (vector 128 chiều), không lưu ảnh gốc

## Bắt đầu

1. Thêm 5-7 ảnh của bạn vào thư mục này
2. Chạy backend: `uvicorn backend.main:app --reload`
3. Kiểm tra log để xem số ảnh đã load
4. Test API với ảnh mới
5. Điều chỉnh nếu cần

**Chúc bạn thành công! 🎉**
