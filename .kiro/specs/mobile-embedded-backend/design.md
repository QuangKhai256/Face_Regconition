# Design Document

## Overview

Hệ thống nhận diện khuôn mặt embedded hoàn toàn chạy trên thiết bị di động Flutter, không cần server backend riêng. Toàn bộ logic xử lý (phát hiện khuôn mặt, trích xuất embedding, huấn luyện, nhận diện) được thực hiện native trên thiết bị thông qua:

1. **ML Kit Face Detection** (Google): Phát hiện khuôn mặt và bounding box
2. **TensorFlow Lite**: Trích xuất face embedding từ model pre-trained (FaceNet hoặc MobileFaceNet)
3. **Camera Plugin**: Truy cập camera thật của thiết bị
4. **Local Storage**: Lưu trữ ảnh, embeddings và model trên thiết bị

Kiến trúc này cho phép:
- Hoạt động hoàn toàn offline
- Bảo mật dữ liệu (không upload lên server)
- Tốc độ xử lý nhanh (không có network latency)
- Tiết kiệm chi phí (không cần server)

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────┐
│         Flutter Mobile App                  │
│                                             │
│  ┌─────────────┐  ┌──────────────┐        │
│  │   UI Layer  │  │ Camera Layer │        │
│  │  (Widgets)  │  │   (camera)   │        │
│  └──────┬──────┘  └──────┬───────┘        │
│         │                 │                 │
│  ┌──────▼─────────────────▼──────┐        │
│  │    Business Logic Layer        │        │
│  │  - Face Detection Service      │        │
│  │  - Embedding Service           │        │
│  │  - Training Service             │        │
│  │  - Verification Service         │        │
│  │  - Environment Check Service    │        │
│  └──────┬─────────────────┬───────┘        │
│         │                 │                 │
│  ┌──────▼──────┐   ┌─────▼────────┐       │
│  │  ML Layer   │   │ Storage Layer│       │
│  │  - ML Kit   │   │ - Files      │       │
│  │  - TF Lite  │   │ - Prefs      │       │
│  └─────────────┘   └──────────────┘       │
└─────────────────────────────────────────────┘
```

### Technology Stack

**Flutter Packages:**
- `camera`: ^0.10.0 - Camera access and preview
- `google_mlkit_face_detection`: ^0.9.0 - ML Kit face detection
- `tflite_flutter`: ^0.10.0 - TensorFlow Lite inference
- `path_provider`: ^2.0.0 - Access app directories
- `shared_preferences`: ^2.0.0 - Store simple data
- `image`: ^4.0.0 - Image processing
- `permission_handler`: ^11.0.0 - Handle permissions

**Native Dependencies:**
- Android: ML Kit Face Detection SDK, TensorFlow Lite AAR
- iOS: ML Kit Face Detection Pod, TensorFlow Lite Pod

**Pre-trained Model:**
- MobileFaceNet (TFLite format) - ~4MB, 128-d embeddings
- Alternative: FaceNet (TFLite format) - ~90MB, 512-d embeddings

## Components and Interfaces

### 1. Camera Service (`lib/services/camera_service.dart`)

**Responsibilities:**
- Initialize and manage camera controller
- Provide camera preview stream
- Capture images from camera
- Handle camera permissions

**Key Methods:**
```dart
class CameraService {
  Future<void> initialize() async
  Future<XFile?> captureImage() async
  Future<void> dispose() async
  CameraController get controller
  bool get isInitialized
}
```

### 2. Face Detection Service (`lib/services/face_detection_service.dart`)

**Responsibilities:**
- Detect faces using ML Kit
- Validate single face requirement
- Extract face bounding box
- Draw bounding box on image

**Key Methods:**
```dart
class FaceDetectionService {
  Future<List<Face>> detectFaces(InputImage image) async
  Future<FaceDetectionResult> detectSingleFace(File imageFile) async
  Rect getFaceBoundingBox(Face face)
  ui.Image drawBoundingBox(ui.Image image, Rect box, Color color) async
}

class FaceDetectionResult {
  final bool success;
  final Face? face;
  final String? errorMessage;
  final int faceCount;
}
```

### 3. Environment Check Service (`lib/services/environment_service.dart`)

**Responsibilities:**
- Calculate brightness from image
- Calculate blur score (Laplacian variance)
- Calculate face size ratio
- Generate warnings

**Key Methods:**
```dart
class EnvironmentService {
  Future<EnvironmentInfo> analyzeEnvironment(
    File imageFile,
    Rect faceBoundingBox
  ) async
  
  double _calculateBrightness(img.Image image)
  double _calculateBlurScore(img.Image image)
  double _calculateFaceSizeRatio(Rect faceBox, Size imageSize)
}

class EnvironmentInfo {
  final double brightness;
  final bool isTooDark;
  final bool isTooBright;
  final double blurScore;
  final bool isTooBlurry;
  final double faceSizeRatio;
  final bool isFaceTooSmall;
  final List<String> warnings;
}
```

**Thresholds:**
- Brightness: < 60 (too dark), > 200 (too bright)
- Blur score: < 100 (too blurry)
- Face size ratio: < 0.10 (too small)

### 4. Embedding Service (`lib/services/embedding_service.dart`)

**Responsibilities:**
- Load TensorFlow Lite model
- Preprocess face images for model input
- Extract face embeddings
- Cache model in memory

**Key Methods:**
```dart
class EmbeddingService {
  Future<void> loadModel() async
  Future<List<double>> extractEmbedding(File imageFile, Rect faceBox) async
  Future<void> dispose() async
  
  // Private methods
  Uint8List _preprocessImage(img.Image face)
  List<double> _runInference(Uint8List input)
}
```

**Model Input:**
- Size: 112x112 or 160x160 (depends on model)
- Format: RGB normalized to [0, 1] or [-1, 1]
- Output: 128-d or 512-d float vector

### 5. Training Service (`lib/services/training_service.dart`)

**Responsibilities:**
- Load training images from storage
- Extract embeddings from all images
- Calculate mean embedding
- Save mean embedding to storage

**Key Methods:**
```dart
class TrainingService {
  Future<TrainingResult> trainModel() async
  Future<List<File>> _loadTrainingImages() async
  Future<List<double>> _calculateMeanEmbedding(
    List<List<double>> embeddings
  ) async
  Future<void> _saveMeanEmbedding(List<double> meanEmbedding) async
}

class TrainingResult {
  final bool success;
  final int numImages;
  final int numEmbeddings;
  final String? errorMessage;
}
```

### 6. Verification Service (`lib/services/verification_service.dart`)

**Responsibilities:**
- Load trained mean embedding
- Compare new embedding with mean
- Calculate Euclidean distance
- Determine match based on threshold

**Key Methods:**
```dart
class VerificationService {
  Future<List<double>?> loadMeanEmbedding() async
  Future<VerificationResult> verify(
    File imageFile,
    Rect faceBox,
    double threshold
  ) async
  
  double _calculateEuclideanDistance(
    List<double> embedding1,
    List<double> embedding2
  )
}

class VerificationResult {
  final bool isMatch;
  final double distance;
  final double threshold;
  final String message;
}
```

**Distance Calculation:**
```
distance = sqrt(sum((e1[i] - e2[i])^2 for i in 0..127))
```

### 7. Storage Service (`lib/services/storage_service.dart`)

**Responsibilities:**
- Save/load training images
- Save/load mean embedding
- Manage app directories
- Handle file operations

**Key Methods:**
```dart
class StorageService {
  Future<String> getTrainingImagesDir() async
  Future<File> saveTrainingImage(File imageFile) async
  Future<List<File>> loadTrainingImages() async
  Future<void> deleteAllTrainingImages() async
  
  Future<void> saveMeanEmbedding(List<double> embedding) async
  Future<List<double>?> loadMeanEmbedding() async
  Future<bool> hasMeanEmbedding() async
  
  Future<void> saveThreshold(double threshold) async
  Future<double> loadThreshold() async
}
```

**Storage Locations:**
- Training images: `<app_documents>/training_images/user_YYYYMMDD_HHMMSS.jpg`
- Mean embedding: `<app_documents>/model/mean_embedding.json`
- Threshold: SharedPreferences key `face_threshold`

### 8. UI Components

#### Main App (`lib/main.dart`)
- Bottom navigation with 3 tabs
- Theme configuration
- Permission handling

#### Collection Screen (`lib/screens/collection_screen.dart`)
- Camera preview
- Capture button
- Image counter
- Delete all button
- Environment warnings display

#### Training Screen (`lib/screens/training_screen.dart`)
- Image count display
- Model status indicator
- Train button
- Progress indicator

#### Verification Screen (`lib/screens/verification_screen.dart`)
- Camera preview
- Threshold slider
- Verify button
- Result display (match/no match)
- Distance and warnings display

## Data Models

### Face Detection Models

```dart
class FaceDetectionResult {
  final bool success;
  final Face? face;  // ML Kit Face object
  final String? errorMessage;
  final int faceCount;
}
```

### Environment Models

```dart
class EnvironmentInfo {
  final double brightness;        // 0-255
  final bool isTooDark;           // < 60
  final bool isTooBright;         // > 200
  final double blurScore;         // Laplacian variance
  final bool isTooBlurry;         // < 100
  final double faceSizeRatio;     // 0.0-1.0
  final bool isFaceTooSmall;      // < 0.10
  final List<String> warnings;
  
  bool get hasWarnings => warnings.isNotEmpty;
  bool get isAcceptable => !isTooDark && !isTooBlurry && !isFaceTooSmall;
}
```

### Training Models

```dart
class TrainingResult {
  final bool success;
  final int numImages;
  final int numEmbeddings;
  final String? errorMessage;
}
```

### Verification Models

```dart
class VerificationResult {
  final bool isMatch;
  final double distance;
  final double threshold;
  final String message;
  final EnvironmentInfo environmentInfo;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, I identified several areas where properties can be consolidated:

1. **Environment threshold properties (3.2, 3.3, 3.5, 3.7)** can be combined into a single comprehensive property about threshold logic
2. **Threshold comparison properties (7.5, 7.6)** are two sides of the same logic and should be combined
3. **Round-trip properties (1.5, 6.5, 8.3)** for different data types can be kept separate as they test different storage mechanisms
4. **Embedding dimension property (5.4)** is already specific enough

### Properties

Property 1: Image save/load round trip
*For any* valid image file, saving to storage and then loading it back should produce an image with identical content
**Validates: Requirements 1.5**

Property 2: Face detection returns result
*For any* image input, face detection should return a result indicating the number of faces detected (0, 1, or multiple)
**Validates: Requirements 2.1**

Property 3: Single face bounding box validity
*For any* image with exactly one detected face, the bounding box should have positive width and height, and coordinates should be within image bounds
**Validates: Requirements 2.4**

Property 4: Environment metrics calculation
*For any* image with a detected face, brightness should be in range [0, 255], blur score should be non-negative, and face size ratio should be in range [0.0, 1.0]
**Validates: Requirements 3.1, 3.4, 3.6**

Property 5: Environment threshold consistency
*For any* calculated environment metrics, the warning flags should be set correctly: isTooDark iff brightness < 60, isTooBright iff brightness > 200, isTooBlurry iff blurScore < 100, isFaceTooSmall iff faceSizeRatio < 0.10
**Validates: Requirements 3.2, 3.3, 3.5, 3.7**

Property 6: Training image filename format
*For any* saved training image, the filename should match the pattern "user_YYYYMMDD_HHMMSS.jpg" where YYYY is 4-digit year, MM is 2-digit month, DD is 2-digit day, HH is 2-digit hour, MM is 2-digit minute, SS is 2-digit second
**Validates: Requirements 4.2**

Property 7: Image counter consistency
*For any* sequence of image save operations, the total count should equal the number of successfully saved images
**Validates: Requirements 4.3**

Property 8: Embedding extraction success
*For any* image with exactly one face, embedding extraction should succeed and return a non-null embedding vector
**Validates: Requirements 5.3**

Property 9: Embedding dimension consistency
*For any* successfully extracted embedding, the vector length should be exactly 128 or exactly 512 (depending on the model used)
**Validates: Requirements 5.4**

Property 10: Training reads all images
*For any* set of images in the training directory, the training process should attempt to read all image files
**Validates: Requirements 6.1, 6.3**

Property 11: Mean embedding calculation
*For any* non-empty list of N embeddings each with dimension D, the calculated mean embedding should have dimension D, and each dimension should equal the arithmetic mean of that dimension across all input embeddings
**Validates: Requirements 6.4**

Property 12: Mean embedding persistence round trip
*For any* mean embedding vector, saving to storage and then loading it back should produce a vector with identical values (within floating point precision)
**Validates: Requirements 6.5**

Property 13: Model trained status
*For any* successful training operation, the model status should be marked as trained and verification should be enabled
**Validates: Requirements 6.7**

Property 14: Euclidean distance calculation
*For any* two embedding vectors of the same dimension D, the calculated Euclidean distance should equal sqrt(sum((e1[i] - e2[i])^2 for i in 0..D-1))
**Validates: Requirements 7.4**

Property 15: Threshold comparison consistency
*For any* calculated distance and threshold value, isMatch should be true if and only if distance <= threshold
**Validates: Requirements 7.5, 7.6**

Property 16: Threshold range validation
*For any* threshold value set by the user, the value should be within the range [0.3, 1.0]
**Validates: Requirements 8.2**

Property 17: Threshold persistence round trip
*For any* threshold value in the valid range, saving to SharedPreferences and then loading it back should produce the same value (within floating point precision)
**Validates: Requirements 8.3**

Property 18: Image resize constraint
*For any* image with width > 1920 or height > 1080, after resizing, both width and height should be <= their respective maximum values while maintaining aspect ratio
**Validates: Requirements 11.2**

## Error Handling

### Error Categories

**Camera Errors:**
- Camera permission denied
- Camera not available
- Camera initialization failed
- Image capture failed

**Face Detection Errors:**
- No face detected
- Multiple faces detected
- ML Kit not available
- Face detection failed

**Environment Check Errors:**
- Image too dark (brightness < 60)
- Image too bright (brightness > 200)
- Image too blurry (blur score < 100)
- Face too small (face size ratio < 0.10)

**Storage Errors:**
- Cannot create directory
- Cannot save file
- Cannot read file
- Storage full
- Permission denied

**Model Errors:**
- Model file not found
- Model loading failed
- Inference failed
- Invalid model output

**Training Errors:**
- No training images found
- Insufficient training data
- Embedding extraction failed
- Mean calculation failed

**Verification Errors:**
- Model not trained
- Embedding extraction failed
- Distance calculation failed

### Error Handling Strategy

1. **User-facing errors**: Show clear Vietnamese messages with actionable guidance
2. **Technical errors**: Log to console with stack trace for debugging
3. **Recoverable errors**: Allow user to retry operation
4. **Fatal errors**: Show error dialog and disable affected features
5. **Validation errors**: Show inline warnings without blocking

### Error Response Format

All errors use Flutter's standard exception handling:
```dart
try {
  // operation
} on CameraException catch (e) {
  // handle camera error
} on FileSystemException catch (e) {
  // handle storage error
} catch (e) {
  // handle unexpected error
}
```

## Testing Strategy

### Unit Testing

Unit tests will cover:
- Individual service methods in isolation
- Environment calculation functions
- Distance calculation
- Mean embedding calculation
- Filename format validation
- Threshold range validation

**Testing Framework**: flutter_test (built-in)

**Key Test Files**:
- `test/services/environment_service_test.dart`
- `test/services/embedding_service_test.dart`
- `test/services/training_service_test.dart`
- `test/services/verification_service_test.dart`
- `test/services/storage_service_test.dart`

**Mocking Strategy**:
- Mock file system operations
- Mock ML Kit responses
- Mock TFLite inference
- Use test images with known properties

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs.

**Testing Framework**: Dart has limited PBT support. We will use:
- `test` package with custom generators
- Or implement simple property testing with random inputs

**Configuration**: Each property test will run minimum 100 iterations

**Test Tagging Format**: Each PBT test must include a comment:
`// Feature: mobile-embedded-backend, Property {number}: {property_text}`

**Key Property Tests**:
- `test/property/environment_property_test.dart`: Test Properties 4, 5
- `test/property/storage_property_test.dart`: Test Properties 1, 6, 7, 12, 17
- `test/property/embedding_property_test.dart`: Test Properties 8, 9, 11, 14
- `test/property/verification_property_test.dart`: Test Properties 15, 16
- `test/property/image_processing_property_test.dart`: Test Property 18

**Generator Strategies**:
- Generate synthetic images with controlled properties
- Generate random embeddings with known dimensions
- Generate random threshold values
- Generate edge cases (empty lists, boundary values)

### Integration Testing

Integration tests will verify:
- End-to-end workflows (collect → train → verify)
- Camera integration
- ML Kit integration
- TFLite integration
- Storage persistence

**Testing Framework**: flutter_test with integration_test package

### Widget Testing

Widget tests will verify:
- UI renders correctly
- User interactions work
- Navigation flows
- Error messages display

### Manual Testing

Manual testing for:
- Real camera functionality
- Real face detection accuracy
- Performance on real devices
- Battery consumption
- User experience

## Performance Considerations

### Model Performance

**MobileFaceNet (Recommended):**
- Size: ~4MB
- Inference time: ~50-100ms on mid-range device
- Embedding dimension: 128
- Accuracy: Good for personal use

**FaceNet (Alternative):**
- Size: ~90MB
- Inference time: ~200-500ms on mid-range device
- Embedding dimension: 512
- Accuracy: Better but slower

### Optimization Strategies

1. **Model caching**: Load model once, keep in memory
2. **Image preprocessing**: Resize to model input size (112x112 or 160x160)
3. **Async operations**: Use isolates for heavy computations
4. **Lazy loading**: Load model only when needed
5. **Resource cleanup**: Dispose camera and model when not in use

### Memory Management

- Release camera when switching tabs
- Clear image cache after processing
- Dispose TFLite interpreter when done
- Limit training image count (recommend 5-20 images)

### Battery Optimization

- Use camera only when needed
- Avoid continuous face detection
- Process images on-demand, not real-time
- Release resources promptly

## Security Considerations

### Data Privacy

- All data stays on device (no server upload)
- Training images stored in app private directory
- Mean embedding stored locally
- No network communication required

### Storage Security

- Use app private storage (not accessible by other apps)
- Consider encrypting mean embedding file
- Provide option to delete all data

### Permission Handling

- Request camera permission with clear explanation
- Request storage permission if needed (Android < 10)
- Handle permission denial gracefully
- Provide settings link if permission permanently denied

## Deployment

### Development Setup

1. Install Flutter SDK 3.x
2. Add dependencies to `pubspec.yaml`:
```yaml
dependencies:
  camera: ^0.10.0
  google_mlkit_face_detection: ^0.9.0
  tflite_flutter: ^0.10.0
  path_provider: ^2.0.0
  shared_preferences: ^2.0.0
  image: ^4.0.0
  permission_handler: ^11.0.0
```

3. Download MobileFaceNet TFLite model
4. Add model to `assets/models/mobilefacenet.tflite`
5. Update `pubspec.yaml`:
```yaml
flutter:
  assets:
    - assets/models/mobilefacenet.tflite
```

6. Configure Android permissions in `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" 
                 android:maxSdkVersion="28" />
```

7. Configure iOS permissions in `ios/Runner/Info.plist`:
```xml
<key>NSCameraUsageDescription</key>
<string>Cần quyền camera để chụp ảnh khuôn mặt</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Cần quyền thư viện ảnh để lưu ảnh</string>
```

### Build and Run

**Debug:**
```bash
flutter run
```

**Release APK:**
```bash
flutter build apk --release
```

**Release App Bundle:**
```bash
flutter build appbundle --release
```

### Production Considerations

1. **Model optimization**: Use quantized TFLite model for smaller size
2. **Error tracking**: Integrate Firebase Crashlytics
3. **Analytics**: Track usage patterns (optional, privacy-conscious)
4. **Testing**: Test on multiple devices and Android versions
5. **Obfuscation**: Enable code obfuscation for release builds

## Future Enhancements

1. **Real-time face detection**: Detect faces in camera preview before capture
2. **Face liveness detection**: Prevent spoofing with photos
3. **Multiple users**: Support multiple user profiles
4. **Face landmarks**: Use landmarks for better alignment
5. **Quality feedback**: Real-time feedback on image quality
6. **Batch processing**: Process multiple images in parallel
7. **Model update**: Allow downloading updated models
8. **Cloud backup**: Optional encrypted cloud backup
9. **Face clustering**: Group similar faces together
10. **Advanced analytics**: Track recognition accuracy over time

## Model Selection and Integration

### Recommended Model: MobileFaceNet

**Why MobileFaceNet:**
- Optimized for mobile devices
- Small size (~4MB)
- Fast inference (~50-100ms)
- Good accuracy for personal use
- 128-d embeddings (smaller than FaceNet's 512-d)

**Model Source:**
- Pre-trained TFLite model available from various sources
- Can convert from PyTorch/TensorFlow using TFLite converter
- Example: https://github.com/sirius-ai/MobileFaceNet_TF

**Integration Steps:**
1. Download or convert MobileFaceNet to TFLite format
2. Place in `assets/models/mobilefacenet.tflite`
3. Load model using `tflite_flutter` package
4. Preprocess face image to 112x112 RGB
5. Normalize pixel values to [0, 1] or [-1, 1] (check model requirements)
6. Run inference to get 128-d embedding
7. Post-process: normalize embedding to unit length (L2 normalization)

**Input Format:**
- Size: 112x112
- Channels: RGB (3)
- Data type: float32
- Normalization: [0, 1] or [-1, 1]

**Output Format:**
- Shape: [1, 128]
- Data type: float32
- Post-processing: L2 normalize to unit length

### Alternative: ML Kit Face Recognition

**Pros:**
- Easier integration (no model file needed)
- Maintained by Google
- Good performance

**Cons:**
- Less control over embedding
- May not provide raw embeddings
- Requires Google Play Services

**Note**: As of 2024, ML Kit Face Detection provides face detection and landmarks, but not face recognition embeddings. For embeddings, TFLite with custom model is required.

## Architecture Decisions

### Why TensorFlow Lite over ML Kit for Recognition?

1. **Control**: Full control over model and embeddings
2. **Offline**: No dependency on Google Play Services
3. **Customization**: Can swap models as needed
4. **Portability**: Works on both Android and iOS

### Why Local Storage over Database?

1. **Simplicity**: Fewer dependencies
2. **Performance**: Direct file I/O is fast
3. **Privacy**: No database queries to intercept
4. **Size**: Small data volume doesn't need database

### Why Mean Embedding over All Embeddings?

1. **Efficiency**: Single comparison instead of N comparisons
2. **Storage**: Store one vector instead of N vectors
3. **Speed**: Faster verification
4. **Accuracy**: Mean reduces noise from individual images

**Trade-off**: Less robust to outliers, but acceptable for personal use with quality-controlled training data.
