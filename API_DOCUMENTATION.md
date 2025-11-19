# API Documentation - Face Recognition Backend

## Base URL

```
http://localhost:8000/api/v1
```

Cho production, thay `localhost:8000` bằng domain/IP của server.

## Authentication

Hiện tại API không yêu cầu authentication. Trong production, nên thêm:
- API Key authentication
- JWT tokens
- Rate limiting

## Endpoints

### 1. Health Check

Kiểm tra trạng thái backend.

**Endpoint:** `GET /health`

**Parameters:** Không có

**Response:**

```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200 OK`: Backend đang hoạt động bình thường

**Example cURL:**

```bash
curl http://localhost:8000/api/v1/health
```

**Example JavaScript:**

```javascript
const response = await fetch('http://localhost:8000/api/v1/health');
const data = await response.json();
console.log(data.status); // "ok"
```

---

### 2. Face Verification

Xác thực khuôn mặt bằng cách so sánh ảnh upload với training data.

**Endpoint:** `POST /face/verify`

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | Yes | - | File ảnh (JPG, JPEG, PNG) |
| `threshold` | Float | No | 0.5 | Ngưỡng so sánh (0.0 - 1.0) |

**Request Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/face/verify?threshold=0.5" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg"
```

**Success Response (200 OK):**

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
  "training_info": {
    "num_images": 7,
    "used_files_sample": [
      "front_1.jpg",
      "front_2.jpg",
      "left_angle.jpg"
    ]
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `is_match` | Boolean | `true` nếu khuôn mặt khớp, `false` nếu không |
| `distance` | Float | Khoảng cách Euclidean giữa embeddings (càng nhỏ càng giống) |
| `threshold` | Float | Ngưỡng đã sử dụng để so sánh |
| `message` | String | Thông báo kết quả bằng tiếng Việt |
| `face_box` | Object | Tọa độ khuôn mặt trong ảnh |
| `face_box.top` | Integer | Tọa độ y của cạnh trên (pixels) |
| `face_box.right` | Integer | Tọa độ x của cạnh phải (pixels) |
| `face_box.bottom` | Integer | Tọa độ y của cạnh dưới (pixels) |
| `face_box.left` | Integer | Tọa độ x của cạnh trái (pixels) |
| `image_size` | Object | Kích thước ảnh upload |
| `image_size.width` | Integer | Chiều rộng ảnh (pixels) |
| `image_size.height` | Integer | Chiều cao ảnh (pixels) |
| `training_info` | Object | Thông tin về training data |
| `training_info.num_images` | Integer | Số lượng ảnh huấn luyện đã sử dụng |
| `training_info.used_files_sample` | Array[String] | Danh sách tên file ảnh huấn luyện |

**Error Responses:**

#### 400 Bad Request - Invalid File Type

```json
{
  "detail": "File upload phải là ảnh (.jpg, .jpeg, .png)."
}
```

#### 400 Bad Request - Cannot Read Image

```json
{
  "detail": "Không đọc được ảnh từ dữ liệu upload. Có thể file bị hỏng hoặc không phải ảnh hợp lệ."
}
```

#### 400 Bad Request - No Face Found

```json
{
  "detail": "Không tìm thấy khuôn mặt nào trong ảnh. Hãy để mặt của bạn chiếm phần lớn khung hình và đảm bảo ánh sáng đủ."
}
```

#### 400 Bad Request - Multiple Faces

```json
{
  "detail": "Phát hiện 3 khuôn mặt trong ảnh. Vui lòng để CHỈ MỘT người trong ảnh để xác thực chính xác."
}
```

#### 400 Bad Request - Cannot Extract Embedding

```json
{
  "detail": "Không trích xuất được vector đặc trưng cho khuôn mặt. Thử lại với ảnh rõ hơn."
}
```

#### 422 Unprocessable Entity - Invalid Threshold

```json
{
  "detail": [
    {
      "loc": ["query", "threshold"],
      "msg": "ensure this value is less than or equal to 1.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

#### 422 Unprocessable Entity - Missing File

```json
{
  "detail": [
    {
      "loc": ["body", "file"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error - Training Data Error

```json
{
  "detail": "Không tìm thấy thư mục myface/ hoặc thư mục không chứa ảnh hợp lệ nào."
}
```

#### 500 Internal Server Error - Generic Error

```json
{
  "detail": "Lỗi nội bộ: [chi tiết lỗi cụ thể]"
}
```

---

## Interactive API Documentation

Backend cung cấp Swagger UI để test API trực tiếp:

**Swagger UI:** http://localhost:8000/docs

**ReDoc:** http://localhost:8000/redoc

## Code Examples

### JavaScript (Fetch API)

```javascript
async function verifyFace(imageFile, threshold = 0.5) {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch(
    `http://localhost:8000/api/v1/face/verify?threshold=${threshold}`,
    {
      method: 'POST',
      body: formData,
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}

// Usage
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];

try {
  const result = await verifyFace(file, 0.5);
  console.log('Match:', result.is_match);
  console.log('Distance:', result.distance);
  console.log('Message:', result.message);
} catch (error) {
  console.error('Error:', error.message);
}
```

### JavaScript (Axios)

```javascript
import axios from 'axios';

async function verifyFace(imageFile, threshold = 0.5) {
  const formData = new FormData();
  formData.append('file', imageFile);

  try {
    const response = await axios.post(
      'http://localhost:8000/api/v1/face/verify',
      formData,
      {
        params: { threshold },
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail);
    }
    throw error;
  }
}
```

### Python (requests)

```python
import requests

def verify_face(image_path, threshold=0.5):
    url = 'http://localhost:8000/api/v1/face/verify'
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        params = {'threshold': threshold}
        
        response = requests.post(url, files=files, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json()
            raise Exception(error['detail'])

# Usage
try:
    result = verify_face('path/to/image.jpg', threshold=0.5)
    print(f"Match: {result['is_match']}")
    print(f"Distance: {result['distance']}")
    print(f"Message: {result['message']}")
except Exception as e:
    print(f"Error: {e}")
```

### Flutter (Dart)

```dart
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> verifyFace(
  File imageFile, {
  double threshold = 0.5,
}) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('http://localhost:8000/api/v1/face/verify?threshold=$threshold'),
  );

  request.files.add(
    await http.MultipartFile.fromPath('file', imageFile.path),
  );

  var streamedResponse = await request.send();
  var response = await http.Response.fromStream(streamedResponse);

  if (response.statusCode == 200) {
    return json.decode(utf8.decode(response.bodyBytes));
  } else {
    final error = json.decode(utf8.decode(response.bodyBytes));
    throw Exception(error['detail']);
  }
}

// Usage
try {
  final result = await verifyFace(File('path/to/image.jpg'));
  print('Match: ${result['is_match']}');
  print('Distance: ${result['distance']}');
  print('Message: ${result['message']}');
} catch (e) {
  print('Error: $e');
}
```

### cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Face verification with default threshold
curl -X POST "http://localhost:8000/api/v1/face/verify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"

# Face verification with custom threshold
curl -X POST "http://localhost:8000/api/v1/face/verify?threshold=0.4" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"

# Pretty print JSON response
curl -X POST "http://localhost:8000/api/v1/face/verify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg" | jq
```

## Best Practices

### 1. Error Handling

Luôn xử lý errors một cách graceful:

```javascript
try {
  const result = await verifyFace(file);
  // Handle success
} catch (error) {
  // Parse error message
  const errorMsg = error.message;
  
  if (errorMsg.includes('Không tìm thấy khuôn mặt')) {
    // Guide user to retake photo with face visible
  } else if (errorMsg.includes('phát hiện')) {
    // Ask user to ensure only one person in photo
  } else if (errorMsg.includes('File upload phải là ảnh')) {
    // Validate file type before upload
  } else {
    // Generic error handling
  }
}
```

### 2. File Validation

Validate file trước khi upload:

```javascript
function validateImageFile(file) {
  // Check file type
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
  if (!validTypes.includes(file.type)) {
    throw new Error('Chỉ chấp nhận file JPG, JPEG, PNG');
  }
  
  // Check file size (max 10MB)
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    throw new Error('File quá lớn. Tối đa 10MB');
  }
  
  return true;
}
```

### 3. Loading States

Hiển thị loading state khi đang xử lý:

```javascript
async function handleVerification(file) {
  setLoading(true);
  setError(null);
  
  try {
    const result = await verifyFace(file);
    setResult(result);
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
}
```

### 4. Retry Logic

Implement retry cho network errors:

```javascript
async function verifyFaceWithRetry(file, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await verifyFace(file);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Only retry on network errors, not validation errors
      if (error.message.includes('network') || 
          error.message.includes('timeout')) {
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        continue;
      }
      
      throw error;
    }
  }
}
```

### 5. Threshold Optimization

Điều chỉnh threshold dựa trên use case:

```javascript
// Strict verification (banking, security)
const strictResult = await verifyFace(file, 0.35);

// Balanced (default)
const balancedResult = await verifyFace(file, 0.5);

// Lenient (user convenience)
const lenientResult = await verifyFace(file, 0.65);
```

## Rate Limiting

Hiện tại API không có rate limiting. Trong production, khuyến nghị:

- **Per IP**: 10 requests/minute
- **Per User**: 20 requests/minute
- **Burst**: 5 requests/second

## CORS

Backend đã cấu hình CORS cho phép tất cả origins trong development:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Trong production, nên giới hạn origins:

```python
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]
```

## Performance

### Expected Response Times

| Endpoint | Expected Time |
|----------|--------------|
| GET /health | < 10ms |
| POST /face/verify | 500ms - 2s |

Response time của `/face/verify` phụ thuộc vào:
- Kích thước ảnh upload
- Số lượng ảnh training
- CPU của server

### Optimization Tips

1. **Resize ảnh trước khi upload** (client-side):
   - Max width/height: 1920px
   - Giảm file size mà vẫn giữ chất lượng

2. **Compress ảnh**:
   - JPEG quality: 85-90%
   - Giảm bandwidth và tăng tốc upload

3. **Cache training data**:
   - Backend tự động cache
   - Không cần reload mỗi request

## Security Considerations

### 1. Data Privacy

- Face embeddings không thể reverse về ảnh gốc
- Backend không lưu ảnh upload lên disk
- Training data nên được bảo vệ

### 2. HTTPS

Trong production, luôn sử dụng HTTPS:

```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://api.yourdomain.com/api/v1'
  : 'http://localhost:8000/api/v1';
```

### 3. Input Validation

- Validate file type và size trước khi upload
- Sanitize user inputs
- Implement rate limiting

### 4. Authentication

Thêm authentication trong production:

```javascript
const response = await fetch(url, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
  body: formData,
});
```

## Troubleshooting

### Connection Refused

```
Error: connect ECONNREFUSED 127.0.0.1:8000
```

**Giải pháp:**
- Kiểm tra backend đang chạy
- Kiểm tra port 8000 không bị chiếm
- Kiểm tra firewall settings

### CORS Error

```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Giải pháp:**
- Backend đã cấu hình CORS cho tất cả origins
- Restart backend nếu vừa thay đổi config
- Kiểm tra browser console để biết chi tiết

### Timeout

```
Error: timeout of 30000ms exceeded
```

**Giải pháp:**
- Tăng timeout trong client
- Giảm kích thước ảnh upload
- Kiểm tra server performance

## Support

Nếu gặp vấn đề:
1. Kiểm tra API documentation này
2. Test với Swagger UI: http://localhost:8000/docs
3. Kiểm tra backend logs
4. Tạo issue trên GitHub với thông tin chi tiết

---

**Version:** 1.0.0  
**Last Updated:** 2024
