# iOS Setup Instructions

This project currently supports Android only. If you need to add iOS support, follow these steps:

## 1. Create iOS Project

Run the following command to add iOS support:
```bash
flutter create --platforms=ios .
```

## 2. Configure Permissions in Info.plist

Add the following permissions to `ios/Runner/Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Cần quyền camera để chụp ảnh khuôn mặt</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Cần quyền thư viện ảnh để lưu ảnh</string>
```

## 3. Install CocoaPods Dependencies

```bash
cd ios
pod install
cd ..
```

## 4. Build for iOS

```bash
flutter build ios
```

## Note

The current implementation focuses on Android development. iOS support can be added later if needed.
