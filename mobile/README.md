# FaceID Mobile App

Flutter mobile application for face recognition system.

## Features

- Capture or select images from camera/gallery
- Send images for training data collection
- Train face recognition model
- Verify faces with adjustable threshold
- Display environment quality warnings

## Setup

### Prerequisites

- Flutter SDK 3.0 or higher
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

### Installation

1. Install dependencies:
```bash
cd mobile
flutter pub get
```

2. Configure backend URL:
   - For Android emulator: Use `http://10.0.2.2:8000` (default)
   - For real device: Change `baseUrl` in `lib/main.dart` to your LAN IP
     Example: `http://192.168.1.100:8000`

3. Run the app:
```bash
flutter run
```

## Backend Connection

### Android Emulator
The app is configured to use `http://10.0.2.2:8000` which maps to `localhost:8000` on the host machine.

### Real Android Device
1. Connect your device and computer to the same WiFi network
2. Find your computer's LAN IP address:
   - Windows: `ipconfig` (look for IPv4 Address)
   - macOS/Linux: `ifconfig` or `ip addr`
3. Update `baseUrl` in `lib/main.dart`:
   ```dart
   final String baseUrl = 'http://YOUR_LAN_IP:8000';
   ```

## Permissions

The app requires the following permissions:
- Camera access (for taking photos)
- Storage access (for selecting photos from gallery)
- Internet access (for API communication)

Permissions are requested automatically when needed.

## Usage

1. **Collect Training Data**:
   - Tap "Chụp ảnh" to take a photo or "Chọn ảnh" to select from gallery
   - Tap "Gửi làm dữ liệu huấn luyện" to send to backend
   - Repeat 5-10 times with different angles and lighting

2. **Train Model**:
   - After collecting enough images, tap "Huấn luyện mô hình"
   - Wait for training to complete

3. **Verify Face**:
   - Adjust threshold slider (0.3-1.0, default 0.6)
   - Select or capture an image
   - Tap "Nhận diện" to verify
   - View results with match status and distance

## Troubleshooting

### Cannot connect to backend
- Ensure backend is running on port 8000
- Check firewall settings
- Verify IP address is correct for real devices
- For emulator, ensure you're using `http://10.0.2.2:8000`

### Camera permission denied
- Go to device Settings > Apps > FaceID Mobile > Permissions
- Enable Camera and Storage permissions

### Build errors
- Run `flutter clean` then `flutter pub get`
- Ensure Flutter SDK is up to date: `flutter upgrade`
