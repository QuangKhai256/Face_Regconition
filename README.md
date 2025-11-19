# Face Recognition Complete System

Hệ thống nhận diện khuôn mặt cá nhân hoàn chỉnh với ba giai đoạn: thu thập dữ liệu, huấn luyện mô hình, và nhận diện khuôn mặt. Bao gồm Backend API (FastAPI), Frontend Web (Streamlit), và Mobile App (Flutter).

## Tính năng

- ✅ **Thu thập dữ liệu** với kiểm tra môi trường tự động (độ sáng, độ mờ, kích thước mặt)
- ✅ **Huấn luyện mô hình** cá nhân từ dữ liệu đã thu thập
- ✅ **Nhận diện khuôn mặt** với threshold tùy chỉnh
- ✅ REST API với FastAPI
- ✅ Frontend Web với Streamlit
- ✅ Mobile App với Flutter
- ✅ Hỗ trợ CORS cho web và mobile
- ✅ Xử lý lỗi chi tiết bằng tiếng Việt
- ✅ Response JSON đầy đủ thông tin

## 📚 Tài liệu Hướng dẫn

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference đầy đủ với code examples
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Hướng dẫn test chi tiết
- **[myface/README.md](myface/README.md)** - Hướng dẫn chuẩn bị ảnh huấn luyện
- **[INSTALLATION_NOTES.md](INSTALLATION_NOTES.md)** - Hướng dẫn cài đặt (Windows)

## Yêu cầu Hệ thống

- Python 3.8+
- Windows/Linux/MacOS
- Camera hoặc ảnh để test

## Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd Face_Regconition
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

**Lưu ý**: Trên Windows, nếu gặp lỗi khi cài `dlib`, xem file `INSTALLATION_NOTES.md` để biết hướng dẫn chi tiết.

### 3. Chuẩn bị ảnh huấn luyện

Thêm 5-7 ảnh khuôn mặt của bạn vào thư mục `myface/`:

```bash
myface/
├── front_1.jpg
├── front_2.jpg
├── left_angle.jpg
├── right_angle.jpg
├── with_glasses.jpg
└── ...
```

**Yêu cầu ảnh:**
- Chỉ có MỘT khuôn mặt trong mỗi ảnh
- Định dạng: JPG, JPEG, hoặc PNG
- Khuôn mặt chiếm 30-40% khung hình
- Ánh sáng đủ, không quá tối

Xem hướng dẫn chi tiết trong `myface/README.md`

### 4. Chạy backend

```bash
# Development mode (auto-reload)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Backend sẽ chạy tại: http://localhost:8000

## API Documentation

### Endpoints

#### 1. Health Check
```
GET /api/v1/health
```

**Response:**
```json
{
  "status": "ok"
}
```

#### 2. Thu thập Dữ liệu (Collection)
```
POST /api/v1/collect
Content-Type: multipart/form-data
Body: file (image file)
```

**Parameters:**
- `file` (required): File ảnh (JPG, JPEG, PNG)

**Response (Success):**
```json
{
  "message": "Ảnh đã được lưu thành công",
  "saved_path": "data/raw/user/user_20251119_143052.jpg",
  "total_images": 5,
  "environment_info": {
    "brightness": 145.5,
    "is_too_dark": false,
    "is_too_bright": false,
    "blur_score": 250.3,
    "is_too_blurry": false,
    "face_size_ratio": 0.25,
    "is_face_too_small": false,
    "warnings": []
  }
}
```

**Response (Poor Environment - HTTP 400):**
```json
{
  "detail": "Môi trường không đạt yêu cầu: Ảnh quá tối (brightness=45.2 < 60), Ảnh quá mờ (blur_score=85.3 < 100)"
}
```

#### 3. Huấn luyện Mô hình (Training)
```
POST /api/v1/train
```

**Response (Success):**
```json
{
  "message": "Huấn luyện thành công",
  "num_images": 10,
  "num_embeddings": 10
}
```

**Response (Error - HTTP 400):**
```json
{
  "detail": "Thư mục data/raw/user/ không tồn tại hoặc rỗng. Vui lòng thu thập ảnh trước."
}
```

#### 4. Nhận diện Khuôn mặt (Verification)
```
POST /api/v1/face/verify?threshold=0.5
Content-Type: multipart/form-data
Body: file (image file)
```

**Parameters:**
- `file` (required): File ảnh (JPG, JPEG, PNG)
- `threshold` (optional): Ngưỡng so sánh 0.0-1.0, mặc định 0.5

**Response (Success):**
```json
{
  "is_match": true,
  "distance": 0.35,
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
  "environment_info": {
    "brightness": 145.5,
    "is_too_dark": false,
    "is_too_bright": false,
    "blur_score": 250.3,
    "is_too_blurry": false,
    "face_size_ratio": 0.25,
    "is_face_too_small": false,
    "warnings": []
  }
}
```

**Response (Error):**
```json
{
  "detail": "Không tìm thấy khuôn mặt nào trong ảnh..."
}
```

### Interactive API Docs

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Detailed Documentation

📖 Xem file **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** để biết:
- Chi tiết đầy đủ về tất cả endpoints
- Tất cả error codes và messages
- Code examples cho nhiều ngôn ngữ/frameworks
- Best practices và optimization tips
- Security considerations

## Testing

### Quick Test với Python Script

```bash
# Test cơ bản (health check + error cases)
python test_api_manual.py

# Test với ảnh cụ thể
python test_api_manual.py verify "path/to/your/photo.jpg" --expected-match

# Test với threshold tùy chỉnh
python test_api_manual.py verify "path/to/photo.jpg" --threshold 0.4
```

### Test với cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Face verification
curl -X POST "http://localhost:8000/api/v1/face/verify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/photo.jpg"
```

### Test với Postman

1. Import collection hoặc tạo request mới
2. POST `http://localhost:8000/api/v1/face/verify`
3. Body → form-data → key: "file", type: File
4. Chọn ảnh và Send

### Hướng dẫn Test Chi tiết

Xem file `TESTING_GUIDE.md` để biết:
- Cách chuẩn bị ảnh huấn luyện
- Test cases đầy đủ
- Troubleshooting
- Tips tăng độ chính xác

### Automated Tests

```bash
# Chạy tất cả tests
pytest

# Chạy tests cụ thể
pytest tests/test_integration_e2e.py -v

# Chạy với coverage
pytest --cov=backend tests/
```

## Cấu trúc Dự án

```
Face_Regconition/
├── backend/                 # Backend API (FastAPI)
│   ├── main.py             # FastAPI application & endpoints
│   ├── data_loader.py      # Load training data (legacy)
│   ├── face_processor.py   # Face recognition & environment analysis
│   ├── training.py         # Training module
│   ├── verification.py     # Verification module
│   ├── models.py           # Pydantic models
│   └── exceptions.py       # Exception handlers
├── web/                    # Frontend Web (Streamlit)
│   └── web_app.py          # Streamlit application
├── mobile/                 # Mobile App (Flutter)
│   ├── lib/
│   │   └── main.dart       # Flutter main application
│   ├── android/            # Android configuration
│   └── pubspec.yaml        # Flutter dependencies
├── data/                   # Data directory
│   └── raw/
│       └── user/           # Collected training images
├── models/                 # Trained models
│   ├── user_embeddings.npy      # All embeddings
│   └── user_embedding_mean.npy  # Mean embedding
├── tests/                  # Test suite
│   ├── test_integration_*.py    # Integration tests
│   ├── test_*_property.py       # Property-based tests
│   └── test_*_unit.py           # Unit tests
├── .kiro/specs/            # Specification documents
│   └── face-recognition-complete/
│       ├── requirements.md  # Requirements document
│       ├── design.md        # Design document
│       └── tasks.md         # Implementation tasks
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Chạy Các Thành phần

### Backend API
```bash
# Development mode (auto-reload)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Web (Streamlit)
```bash
# Cài đặt dependencies
pip install streamlit requests opencv-python

# Chạy web app
streamlit run web/web_app.py
```

Web app sẽ mở tại: http://localhost:8501

### Mobile App (Flutter)
```bash
# Di chuyển vào thư mục mobile
cd mobile

# Cài đặt dependencies
flutter pub get

# Chạy trên emulator/device
flutter run

# Build APK (Android)
flutter build apk

# Build iOS
flutter build ios
```

**Lưu ý cho Mobile:**
- Cấu hình địa chỉ Backend trong `mobile/lib/main.dart`
- Android emulator: `http://10.0.2.2:8000`
- iOS simulator: `http://localhost:8000`
- Thiết bị thật: `http://YOUR_COMPUTER_IP:8000`

## Cách Sử dụng

### Quy trình Hoàn chỉnh

#### 1. Khởi động Backend
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend sẽ chạy tại: http://localhost:8000

#### 2. Thu thập Dữ liệu (Collection Phase)
Thu thập 5-10 ảnh khuôn mặt của bạn:

**Sử dụng Frontend Web:**
```bash
streamlit run web/web_app.py
```
- Mở tab "Thu thập dữ liệu"
- Chụp hoặc upload ảnh
- Hệ thống sẽ kiểm tra chất lượng tự động

**Sử dụng API trực tiếp:**
```bash
curl -X POST "http://localhost:8000/api/v1/collect" \
  -F "file=@path/to/your/photo.jpg"
```

**Yêu cầu ảnh:**
- Chỉ có MỘT khuôn mặt trong mỗi ảnh
- Độ sáng: 60-200 (không quá tối/sáng)
- Blur score: > 100 (không quá mờ)
- Khuôn mặt chiếm ≥ 10% khung hình

#### 3. Huấn luyện Mô hình (Training Phase)
Sau khi thu thập đủ ảnh:

**Sử dụng Frontend Web:**
- Chuyển sang tab "Huấn luyện mô hình"
- Nhấn "Bắt đầu huấn luyện"

**Sử dụng API:**
```bash
curl -X POST "http://localhost:8000/api/v1/train"
```

Hệ thống sẽ:
- Đọc tất cả ảnh từ `data/raw/user/`
- Trích xuất face embeddings (128-d vectors)
- Tính embedding trung bình
- Lưu vào `models/user_embedding_mean.npy`

#### 4. Nhận diện Khuôn mặt (Verification Phase)
Sau khi huấn luyện xong:

**Sử dụng Frontend Web:**
- Chuyển sang tab "Nhận diện khuôn mặt"
- Chụp hoặc upload ảnh cần nhận diện
- Điều chỉnh threshold nếu cần

**Sử dụng API:**
```bash
curl -X POST "http://localhost:8000/api/v1/face/verify?threshold=0.5" \
  -F "file=@path/to/verify/photo.jpg"
```

**Sử dụng Mobile App:**
```bash
cd mobile
flutter run
```

### 5. Tích hợp vào Ứng dụng
Xem phần **Ví dụ Tích hợp** bên dưới để biết cách gọi API từ JavaScript (web) và Flutter (mobile)

## Ví dụ Tích hợp

### JavaScript (Web)

#### Vanilla JavaScript

```javascript
// Hàm gọi API verify
async function verifyFace(imageFile, threshold = 0.5) {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  try {
    const response = await fetch(
      `http://localhost:8000/api/v1/face/verify?threshold=${threshold}`,
      {
        method: 'POST',
        body: formData,
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Lỗi khi xác thực khuôn mặt');
    }
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Sử dụng với input file
document.getElementById('fileInput').addEventListener('change', async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  try {
    const result = await verifyFace(file);
    
    if (result.is_match) {
      console.log('✅ Xác thực thành công!');
      console.log(`Khoảng cách: ${result.distance}`);
    } else {
      console.log('❌ Không khớp');
      console.log(`Khoảng cách: ${result.distance}`);
    }
    
    console.log('Message:', result.message);
  } catch (error) {
    console.error('Lỗi:', error.message);
  }
});
```

#### React Example

```jsx
import React, { useState } from 'react';

function FaceVerification() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(
        'http://localhost:8000/api/v1/face/verify?threshold=0.5',
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Xác thực Khuôn mặt</h2>
      
      <input
        type="file"
        accept="image/jpeg,image/jpg,image/png"
        onChange={handleFileChange}
        disabled={loading}
      />

      {loading && <p>Đang xử lý...</p>}

      {error && (
        <div style={{ color: 'red' }}>
          <strong>Lỗi:</strong> {error}
        </div>
      )}

      {result && (
        <div>
          <h3>Kết quả:</h3>
          <p>
            <strong>Trạng thái:</strong>{' '}
            {result.is_match ? '✅ Khớp' : '❌ Không khớp'}
          </p>
          <p><strong>Khoảng cách:</strong> {result.distance.toFixed(3)}</p>
          <p><strong>Ngưỡng:</strong> {result.threshold}</p>
          <p><strong>Thông báo:</strong> {result.message}</p>
          <p>
            <strong>Số ảnh huấn luyện:</strong>{' '}
            {result.training_info.num_images}
          </p>
        </div>
      )}
    </div>
  );
}

export default FaceVerification;
```

#### Axios Example

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Health check
export async function checkHealth() {
  const response = await axios.get(`${API_BASE_URL}/health`);
  return response.data;
}

// Face verification
export async function verifyFace(imageFile, threshold = 0.5) {
  const formData = new FormData();
  formData.append('file', imageFile);

  try {
    const response = await axios.post(
      `${API_BASE_URL}/face/verify`,
      formData,
      {
        params: { threshold },
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data.detail);
    } else if (error.request) {
      // No response received
      throw new Error('Không thể kết nối đến server');
    } else {
      throw error;
    }
  }
}

// Usage
async function example() {
  // Check if backend is running
  const health = await checkHealth();
  console.log('Backend status:', health.status);

  // Verify face
  const fileInput = document.getElementById('fileInput');
  const file = fileInput.files[0];
  
  const result = await verifyFace(file, 0.5);
  console.log('Verification result:', result);
}
```

### Flutter (Mobile)

#### Setup Dependencies

Thêm vào `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  image_picker: ^1.0.4
```

#### API Service

```dart
// lib/services/face_recognition_service.dart
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

class FaceRecognitionService {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  // Cho Android emulator: 'http://10.0.2.2:8000/api/v1'
  // Cho iOS simulator: 'http://localhost:8000/api/v1'
  // Cho thiết bị thật: 'http://YOUR_COMPUTER_IP:8000/api/v1'

  /// Kiểm tra trạng thái backend
  Future<Map<String, dynamic>> checkHealth() async {
    final response = await http.get(Uri.parse('$baseUrl/health'));
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Backend không hoạt động');
    }
  }

  /// Xác thực khuôn mặt
  Future<VerificationResult> verifyFace(
    File imageFile, {
    double threshold = 0.5,
  }) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/face/verify?threshold=$threshold'),
    );

    // Thêm file vào request
    request.files.add(
      await http.MultipartFile.fromPath(
        'file',
        imageFile.path,
      ),
    );

    // Gửi request
    var streamedResponse = await request.send();
    var response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final data = json.decode(utf8.decode(response.bodyBytes));
      return VerificationResult.fromJson(data);
    } else {
      final error = json.decode(utf8.decode(response.bodyBytes));
      throw Exception(error['detail'] ?? 'Lỗi không xác định');
    }
  }
}

/// Model cho kết quả xác thực
class VerificationResult {
  final bool isMatch;
  final double distance;
  final double threshold;
  final String message;
  final FaceBox faceBox;
  final ImageSize imageSize;
  final TrainingInfo trainingInfo;

  VerificationResult({
    required this.isMatch,
    required this.distance,
    required this.threshold,
    required this.message,
    required this.faceBox,
    required this.imageSize,
    required this.trainingInfo,
  });

  factory VerificationResult.fromJson(Map<String, dynamic> json) {
    return VerificationResult(
      isMatch: json['is_match'],
      distance: json['distance'].toDouble(),
      threshold: json['threshold'].toDouble(),
      message: json['message'],
      faceBox: FaceBox.fromJson(json['face_box']),
      imageSize: ImageSize.fromJson(json['image_size']),
      trainingInfo: TrainingInfo.fromJson(json['training_info']),
    );
  }
}

class FaceBox {
  final int top;
  final int right;
  final int bottom;
  final int left;

  FaceBox({
    required this.top,
    required this.right,
    required this.bottom,
    required this.left,
  });

  factory FaceBox.fromJson(Map<String, dynamic> json) {
    return FaceBox(
      top: json['top'],
      right: json['right'],
      bottom: json['bottom'],
      left: json['left'],
    );
  }
}

class ImageSize {
  final int width;
  final int height;

  ImageSize({required this.width, required this.height});

  factory ImageSize.fromJson(Map<String, dynamic> json) {
    return ImageSize(
      width: json['width'],
      height: json['height'],
    );
  }
}

class TrainingInfo {
  final int numImages;
  final List<String> usedFilesSample;

  TrainingInfo({
    required this.numImages,
    required this.usedFilesSample,
  });

  factory TrainingInfo.fromJson(Map<String, dynamic> json) {
    return TrainingInfo(
      numImages: json['num_images'],
      usedFilesSample: List<String>.from(json['used_files_sample']),
    );
  }
}
```

#### UI Example

```dart
// lib/screens/face_verification_screen.dart
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../services/face_recognition_service.dart';

class FaceVerificationScreen extends StatefulWidget {
  @override
  _FaceVerificationScreenState createState() => _FaceVerificationScreenState();
}

class _FaceVerificationScreenState extends State<FaceVerificationScreen> {
  final FaceRecognitionService _service = FaceRecognitionService();
  final ImagePicker _picker = ImagePicker();
  
  File? _selectedImage;
  VerificationResult? _result;
  bool _isLoading = false;
  String? _error;

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? image = await _picker.pickImage(source: source);
      
      if (image != null) {
        setState(() {
          _selectedImage = File(image.path);
          _result = null;
          _error = null;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Lỗi khi chọn ảnh: $e';
      });
    }
  }

  Future<void> _verifyFace() async {
    if (_selectedImage == null) return;

    setState(() {
      _isLoading = true;
      _error = null;
      _result = null;
    });

    try {
      final result = await _service.verifyFace(_selectedImage!);
      setState(() {
        _result = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Xác thực Khuôn mặt'),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image preview
            if (_selectedImage != null)
              Container(
                height: 300,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Image.file(_selectedImage!, fit: BoxFit.contain),
              ),
            
            SizedBox(height: 16),
            
            // Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _pickImage(ImageSource.camera),
                    icon: Icon(Icons.camera_alt),
                    label: Text('Chụp ảnh'),
                  ),
                ),
                SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _pickImage(ImageSource.gallery),
                    icon: Icon(Icons.photo_library),
                    label: Text('Chọn ảnh'),
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 16),
            
            // Verify button
            ElevatedButton(
              onPressed: _selectedImage != null && !_isLoading
                  ? _verifyFace
                  : null,
              child: _isLoading
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text('Xác thực'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(vertical: 16),
              ),
            ),
            
            SizedBox(height: 24),
            
            // Error message
            if (_error != null)
              Card(
                color: Colors.red[50],
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    _error!,
                    style: TextStyle(color: Colors.red[900]),
                  ),
                ),
              ),
            
            // Result
            if (_result != null)
              Card(
                color: _result!.isMatch ? Colors.green[50] : Colors.orange[50],
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _result!.isMatch ? '✅ Khớp' : '❌ Không khớp',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: _result!.isMatch
                              ? Colors.green[900]
                              : Colors.orange[900],
                        ),
                      ),
                      SizedBox(height: 12),
                      _buildResultRow(
                        'Khoảng cách',
                        _result!.distance.toStringAsFixed(3),
                      ),
                      _buildResultRow(
                        'Ngưỡng',
                        _result!.threshold.toStringAsFixed(3),
                      ),
                      _buildResultRow(
                        'Số ảnh huấn luyện',
                        _result!.trainingInfo.numImages.toString(),
                      ),
                      SizedBox(height: 8),
                      Text(
                        _result!.message,
                        style: TextStyle(fontStyle: FontStyle.italic),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontWeight: FontWeight.w500)),
          Text(value),
        ],
      ),
    );
  }
}
```

#### Lưu ý cho Flutter

**Android:**
- Trong `AndroidManifest.xml`, thêm permissions:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
```

- Sử dụng `http://10.0.2.2:8000` thay vì `localhost` cho Android emulator

**iOS:**
- Trong `Info.plist`, thêm:
```xml
<key>NSCameraUsageDescription</key>
<string>Cần quyền truy cập camera để chụp ảnh xác thực</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Cần quyền truy cập thư viện ảnh</string>
```

**Network Security:**
- Cho development, cần cho phép HTTP (không phải HTTPS)
- Android: Thêm `android:usesCleartextTraffic="true"` trong `<application>` tag
- iOS: Cấu hình App Transport Security trong Info.plist

## Điều chỉnh Threshold

Threshold quyết định độ nghiêm ngặt của việc so sánh:

- **0.3-0.4**: Nghiêm ngặt, ít false positive
- **0.5** (mặc định): Cân bằng
- **0.6-0.7**: Linh hoạt, ít false negative

Điều chỉnh dựa trên kết quả test:
- Nếu ảnh của bạn không match → tăng threshold
- Nếu ảnh người khác match → giảm threshold

## Error Codes và Messages

### HTTP Status Codes

| Status Code | Loại lỗi | Mô tả |
|------------|-----------|-------|
| 200 | Success | Request thành công |
| 400 | Bad Request | Lỗi từ phía client (ảnh không hợp lệ, format sai, etc.) |
| 422 | Validation Error | Lỗi validation tham số (threshold ngoài range) |
| 500 | Internal Server Error | Lỗi nội bộ server |

### Error Messages Chi tiết

#### 1. Lỗi File Upload (HTTP 400)

**Message:** `"File upload phải là ảnh (.jpg, .jpeg, .png)."`
- **Nguyên nhân:** Content-type của file không phải image/jpeg, image/jpg, hoặc image/png
- **Giải pháp:** Đảm bảo upload file ảnh với định dạng đúng

**Message:** `"Không đọc được ảnh từ dữ liệu upload. Có thể file bị hỏng hoặc không phải ảnh hợp lệ."`
- **Nguyên nhân:** File bị corrupt hoặc không phải file ảnh thực sự
- **Giải pháp:** Kiểm tra file ảnh, thử mở bằng image viewer, hoặc chọn ảnh khác

#### 2. Lỗi Phát hiện Khuôn mặt (HTTP 400)

**Message:** `"Không tìm thấy khuôn mặt nào trong ảnh. Hãy để mặt của bạn chiếm phần lớn khung hình và đảm bảo ánh sáng đủ."`
- **Nguyên nhân:** Không có khuôn mặt trong ảnh hoặc khuôn mặt quá nhỏ/mờ
- **Giải pháp:** 
  - Chụp ảnh với khuôn mặt rõ ràng, chiếm 30-40% khung hình
  - Đảm bảo ánh sáng đủ
  - Không bị che khuất quá nhiều

**Message:** `"Phát hiện N khuôn mặt trong ảnh. Vui lòng để CHỈ MỘT người trong ảnh để xác thực chính xác."`
- **Nguyên nhân:** Có nhiều hơn 1 khuôn mặt trong ảnh
- **Giải pháp:** Chụp/chọn ảnh chỉ có 1 người

**Message:** `"Không trích xuất được vector đặc trưng cho khuôn mặt. Thử lại với ảnh rõ hơn."`
- **Nguyên nhân:** Phát hiện được khuôn mặt nhưng không trích xuất được embedding
- **Giải pháp:** Sử dụng ảnh chất lượng tốt hơn, rõ nét hơn

#### 3. Lỗi Validation (HTTP 422)

**Message:** `"value is not a valid float"` hoặc validation error cho threshold
- **Nguyên nhân:** Threshold không phải số hoặc nằm ngoài range [0.0, 1.0]
- **Giải pháp:** Sử dụng threshold trong khoảng 0.0 đến 1.0

**Message:** `"field required"` cho file parameter
- **Nguyên nhân:** Không có file trong request
- **Giải pháp:** Đảm bảo gửi file trong form-data với key "file"

#### 4. Lỗi Training Data (HTTP 500)

**Message:** `"Không tìm thấy thư mục myface/ hoặc thư mục không chứa ảnh hợp lệ nào."`
- **Nguyên nhân:** Thư mục myface/ không tồn tại hoặc rỗng
- **Giải pháp:** 
  - Tạo thư mục myface/
  - Thêm 5-7 ảnh khuôn mặt hợp lệ
  - Xem hướng dẫn trong myface/README.md

**Message:** `"Không tìm thấy ảnh hợp lệ nào trong thư mục myface/. Mỗi ảnh phải chứa đúng 1 khuôn mặt."`
- **Nguyên nhân:** Tất cả ảnh trong myface/ đều không hợp lệ (0 hoặc nhiều khuôn mặt)
- **Giải pháp:** Thêm ảnh với đúng 1 khuôn mặt trong mỗi ảnh

#### 5. Lỗi Nội bộ (HTTP 500)

**Message:** `"Lỗi nội bộ: [chi tiết lỗi]"`
- **Nguyên nhân:** Lỗi không mong đợi trong quá trình xử lý
- **Giải pháp:** 
  - Kiểm tra log server
  - Restart backend
  - Báo cáo issue nếu lỗi lặp lại

### Response Format

**Success Response:**
```json
{
  "is_match": true,
  "distance": 0.35,
  "threshold": 0.5,
  "message": "Đây là KHUÔN MẶT CỦA BẠN (khoảng cách = 0.350 ≤ ngưỡng 0.500).",
  "face_box": { "top": 100, "right": 300, "bottom": 400, "left": 100 },
  "image_size": { "width": 640, "height": 480 },
  "training_info": {
    "num_images": 7,
    "used_files_sample": ["img1.jpg", "img2.jpg"]
  }
}
```

**Error Response:**
```json
{
  "detail": "Không tìm thấy khuôn mặt nào trong ảnh..."
}
```

### Xử lý Lỗi trong Code

**JavaScript:**
```javascript
try {
  const result = await verifyFace(file);
  // Handle success
} catch (error) {
  if (error.message.includes('Không tìm thấy khuôn mặt')) {
    // Hướng dẫn người dùng chụp lại
  } else if (error.message.includes('phát hiện')) {
    // Yêu cầu chỉ 1 người trong ảnh
  } else {
    // Lỗi khác
  }
}
```

**Flutter:**
```dart
try {
  final result = await service.verifyFace(imageFile);
  // Handle success
} on Exception catch (e) {
  final errorMsg = e.toString();
  if (errorMsg.contains('Không tìm thấy khuôn mặt')) {
    // Show guidance to retake photo
  } else if (errorMsg.contains('phát hiện')) {
    // Ask for single person photo
  } else {
    // Handle other errors
  }
}
```

## Troubleshooting

### Backend không khởi động
- Kiểm tra Python version (>= 3.8)
- Kiểm tra đã cài đặt dependencies: `pip install -r requirements.txt`
- Xem log để biết lỗi cụ thể
- Đảm bảo port 8000 không bị chiếm bởi process khác

### Thu thập dữ liệu bị từ chối
**"Môi trường không đạt yêu cầu":**
- **Ảnh quá tối**: Chụp ở nơi có ánh sáng tốt hơn
- **Ảnh quá sáng**: Tránh ánh sáng trực tiếp vào mặt
- **Ảnh quá mờ**: Giữ máy ảnh/điện thoại ổn định, không rung
- **Khuôn mặt quá nhỏ**: Di chuyển gần camera hơn

**"Không tìm thấy khuôn mặt":**
- Đảm bảo khuôn mặt rõ ràng trong khung hình
- Không bị che khuất quá nhiều (khẩu trang, tóc, tay)
- Ánh sáng đủ để nhìn rõ khuôn mặt

**"Phát hiện nhiều khuôn mặt":**
- Chỉ có 1 người trong khung hình
- Tránh ảnh có người khác ở phía sau

### Huấn luyện thất bại
**"Thư mục data/raw/user/ không tồn tại hoặc rỗng":**
- Thu thập ít nhất 5 ảnh trước khi huấn luyện
- Kiểm tra thư mục `data/raw/user/` có tồn tại

**"Không trích xuất được embedding nào":**
- Kiểm tra lại chất lượng ảnh đã thu thập
- Xóa ảnh kém chất lượng và thu thập lại

### Nhận diện không chính xác
**Ảnh của bạn không match:**
- Thêm nhiều ảnh huấn luyện đa dạng hơn (5-10 ảnh)
- Bao gồm nhiều góc độ, biểu cảm khác nhau
- Tăng threshold (0.6-0.7)
- Huấn luyện lại sau khi thêm ảnh

**Ảnh người khác bị match nhầm:**
- Giảm threshold (0.3-0.4)
- Thêm ảnh huấn luyện chất lượng cao
- Đảm bảo ảnh huấn luyện đa dạng

### Frontend Web không kết nối Backend
- Kiểm tra Backend đang chạy tại http://localhost:8000
- Kiểm tra CORS đã được cấu hình
- Xem console log để biết lỗi cụ thể

### Mobile App không kết nối Backend
**Android Emulator:**
- Sử dụng `http://10.0.2.2:8000` thay vì `localhost`

**iOS Simulator:**
- Sử dụng `http://localhost:8000`

**Thiết bị thật:**
- Sử dụng địa chỉ IP LAN của máy chạy Backend
- Ví dụ: `http://192.168.1.100:8000`
- Đảm bảo cùng mạng WiFi
- Tắt firewall hoặc cho phép port 8000

### Lỗi cài đặt dlib (Windows)
Xem `INSTALLATION_NOTES.md` để biết hướng dẫn chi tiết.

### Kiểm tra Log
```bash
# Xem log Backend
# Log sẽ hiển thị trên terminal khi chạy uvicorn

# Xem log chi tiết hơn
uvicorn backend.main:app --reload --log-level debug
```

## Performance

- Health check: < 10ms
- Face verification: 500ms - 2s (tùy kích thước ảnh)
- Training data loading: 1-5s (chỉ khi khởi động)

## Security

- Face embeddings không thể reverse về ảnh gốc
- Không lưu ảnh upload lên disk
- Nên giới hạn CORS origins trong production
- Khuyến nghị thêm rate limiting

## Roadmap

- [ ] Thêm authentication/authorization
- [ ] Hỗ trợ multiple users
- [ ] Database để lưu face embeddings
- [ ] Docker support
- [ ] Rate limiting
- [ ] Logging và monitoring

## License

[Thêm license của bạn]

## Contributors

[Thêm thông tin contributors]

## Support

Nếu gặp vấn đề:
1. Đọc `TESTING_GUIDE.md`
2. Đọc `myface/README.md`
3. Kiểm tra Issues trên GitHub
4. Tạo Issue mới với thông tin chi tiết

---

**Chúc bạn thành công với dự án! 🎉**
