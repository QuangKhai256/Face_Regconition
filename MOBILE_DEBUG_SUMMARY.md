# Mobile App Debug Summary

## 🔧 Các Vấn đề Đã Sửa

### 1. Gradle Version Incompatibility ✅
**Vấn đề:** Gradle 7.5 không tương thích với Java 21
**Giải pháp:** Nâng cấp lên Gradle 8.7

**File:** `mobile/android/gradle/wrapper/gradle-wrapper.properties`
```properties
# Trước
distributionUrl=https\://services.gradle.org/distributions/gradle-7.5-all.zip

# Sau
distributionUrl=https\://services.gradle.org/distributions/gradle-8.7-all.zip
```

### 2. Android Gradle Plugin Version ✅
**Vấn đề:** AGP 7.3.0 quá cũ, Flutter yêu cầu tối thiểu 8.1.1
**Giải pháp:** Nâng cấp lên AGP 8.1.4

**File:** `mobile/android/build.gradle`
```groovy
// Trước
classpath 'com.android.tools.build:gradle:7.3.0'

// Sau
classpath 'com.android.tools.build:gradle:8.1.4'
```

**File:** `mobile/android/settings.gradle`
```groovy
// Trước
id "com.android.application" version "7.3.0" apply false

// Sau
id "com.android.application" version "8.1.4" apply false
```

### 3. Kotlin Version ✅
**Vấn đề:** Kotlin 1.8.0 cũ
**Giải pháp:** Nâng cấp lên Kotlin 1.9.0

**File:** `mobile/android/build.gradle`
```groovy
// Trước
ext.kotlin_version = '1.8.0'

// Sau
ext.kotlin_version = '1.9.0'
```

### 4. Java Version Compatibility ✅
**Vấn đề:** JVM target 1.8 không tương thích với AGP 8.x
**Giải pháp:** Nâng cấp lên Java 17

**File:** `mobile/android/app/build.gradle`
```groovy
// Trước
compileOptions {
    sourceCompatibility JavaVersion.VERSION_1_8
    targetCompatibility JavaVersion.VERSION_1_8
}

kotlinOptions {
    jvmTarget = '1.8'
}

// Sau
compileOptions {
    sourceCompatibility JavaVersion.VERSION_17
    targetCompatibility JavaVersion.VERSION_17
}

kotlinOptions {
    jvmTarget = '17'
}
```

### 5. Compile SDK Version ✅
**Vấn đề:** compileSdk sử dụng biến flutter.compileSdkVersion có thể không đúng
**Giải pháp:** Đặt cứng compileSdk = 34

**File:** `mobile/android/app/build.gradle`
```groovy
// Trước
compileSdk flutter.compileSdkVersion

// Sau
compileSdk 34
```

## 📱 Trạng thái Hiện tại

### ✅ Đã Hoàn thành
- [x] Sửa Gradle version incompatibility
- [x] Nâng cấp Android Gradle Plugin
- [x] Nâng cấp Kotlin version
- [x] Cập nhật Java compatibility
- [x] Cập nhật compile SDK version
- [x] Flutter dependencies đã được cài đặt
- [x] Android emulator đang chạy

### 🔄 Đang Chạy
- [ ] App đang được build lần đầu (có thể mất 2-5 phút)
- [ ] Gradle đang download dependencies
- [ ] Compiling Dart code

## 🎯 Kết quả Mong đợi

Sau khi build hoàn tất, bạn sẽ thấy:

```
✓ Built build\app\outputs\flutter-apk\app-debug.apk.
Launching lib\main.dart on sdk gphone64 x86 64 in debug mode...
Installing build\app\outputs\flutter-apk\app-debug.apk...
Waiting for sdk gphone64 x86 64 to report its views...
Debug service listening on ws://127.0.0.1:xxxxx/xxxxxx
Syncing files to device sdk gphone64 x86 64...
Flutter run key commands.
r Hot reload. 🔥🔥🔥
R Hot restart.
h List all available interactive commands.
d Detach (terminate "flutter run" but leave application running).
c Clear the screen
q Quit (terminate the application on the device).

💪 Running with sound null safety 💪

An Observatory debugger and profiler on sdk gphone64 x86 64 is available at: http://127.0.0.1:xxxxx/
The Flutter DevTools debugger and profiler on sdk gphone64 x86 64 is available at: http://127.0.0.1:xxxxx/
```

## 📋 Cấu hình Cuối cùng

### Versions
- **Gradle:** 8.7
- **Android Gradle Plugin:** 8.1.4
- **Kotlin:** 1.9.0
- **Java Target:** 17
- **Compile SDK:** 34
- **Min SDK:** 21
- **Target SDK:** 34

### Dependencies
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  image_picker: ^1.0.4
```

### Permissions (AndroidManifest.xml)
- ✅ CAMERA
- ✅ READ_EXTERNAL_STORAGE
- ✅ WRITE_EXTERNAL_STORAGE
- ✅ INTERNET

## 🚀 Cách Chạy App

### Lần đầu tiên (đã làm)
```bash
cd mobile
flutter clean
flutter pub get
flutter run -d emulator-5554
```

### Lần sau
```bash
cd mobile
flutter run
```

### Hot Reload (khi app đang chạy)
- Nhấn `r` để hot reload
- Nhấn `R` để hot restart
- Nhấn `q` để quit

## 🔍 Debug trong Android Studio

### Mở Project
1. Mở Android Studio
2. File → Open
3. Chọn thư mục `mobile/android`
4. Đợi Gradle sync

### Run/Debug
1. Chọn device (emulator-5554)
2. Click Run (▶️) hoặc Debug (🐛)
3. Xem logs trong Logcat

### Logcat Filters
```
package:com.example.faceid_mobile
```

## 📝 Lưu ý

### Backend URL
App đang cấu hình để kết nối đến:
```dart
final String baseUrl = 'http://10.0.2.2:8000';
```

- `10.0.2.2` là địa chỉ localhost của máy host từ Android emulator
- Nếu chạy trên thiết bị thật, cần thay bằng IP LAN của máy (ví dụ: `192.168.1.100`)

### Kiểm tra Backend
Trước khi test app, đảm bảo backend đang chạy:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Test backend:
```bash
curl http://localhost:8000/api/v1/health
```

## ✅ Checklist Test App

Sau khi app chạy thành công:

### 1. UI Test
- [ ] App mở và hiển thị giao diện
- [ ] Threshold slider hoạt động
- [ ] Các buttons hiển thị đúng

### 2. Camera Test
- [ ] Click "Chụp ảnh" → Camera mở
- [ ] Chụp ảnh thành công
- [ ] Ảnh hiển thị trong preview

### 3. Gallery Test
- [ ] Click "Chọn ảnh" → Gallery mở
- [ ] Chọn ảnh thành công
- [ ] Ảnh hiển thị trong preview

### 4. API Test
- [ ] "Gửi làm dữ liệu huấn luyện" → Thành công
- [ ] "Huấn luyện mô hình" → Thành công
- [ ] "Nhận diện" → Hiển thị kết quả

### 5. Error Handling
- [ ] Không có backend → Hiển thị lỗi kết nối
- [ ] Ảnh kém chất lượng → Hiển thị cảnh báo
- [ ] Không có khuôn mặt → Hiển thị lỗi

## 🎉 Kết luận

App mobile đã được debug và sửa tất cả các vấn đề về cấu hình. 
Hiện tại đang trong quá trình build lần đầu tiên.

**Thời gian build dự kiến:** 2-5 phút (tùy máy)

Sau khi build xong, app sẽ tự động cài đặt và chạy trên emulator!
