# App Mobile – Flutter  
## Thu thập khuôn mặt, huấn luyện & nhận diện, hiển thị cảnh báo môi trường

---

## 1. Mục tiêu app mobile

App mobile đóng vai trò **client** cho backend, hỗ trợ người dùng bằng điện thoại:

1. **Bước THU THẬP khuôn mặt:**
   - Chụp ảnh bằng camera hoặc chọn ảnh từ gallery.
   - Gửi ảnh lên `/api/v1/collect`.
   - Backend kiểm tra môi trường (ánh sáng, mờ, kích thước mặt, số người).
   - Nếu môi trường kém → trả lỗi, app hiển thị cảnh báo để người dùng chụp lại.

2. **Bước HUẤN LUYỆN mô hình cá nhân:**
   - Nút “Huấn luyện mô hình” → gọi `/api/v1/train`.

3. **Bước NHẬN DIỆN + kiểm tra môi trường:**
   - Gửi ảnh selfie mới lên `/api/v1/face/verify`.
   - Backend trả:
     - `is_match`, `distance`, `message`.
     - `environment_info` (brightness, blur_score, face_size_ratio, warnings).
   - App hiển thị kết quả + cảnh báo môi trường.

---

## 2. Công nghệ

- Flutter SDK (3.x).
- Package:
  - `http` – gọi API backend.
  - `image_picker` – chụp ảnh / chọn ảnh.

`pubspec.yaml` (trích):

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0
  image_picker: ^1.0.7
```

Chạy:

```bash
flutter pub get
```

---

## 3. Kiến trúc màn hình

### Màn hình `HomeScreen`

- AppBar: “FaceID Mobile”.
- Các thành phần chính:
  - Ảnh đã chọn/chụp (nếu có).
  - Slider điều chỉnh `threshold`.
  - Nhóm nút:
    - “Chụp ảnh” – dùng camera.
    - “Chọn ảnh” – từ gallery.
    - “📥 Gửi làm dữ liệu huấn luyện” – gọi `/collect`.
    - “🧠 Huấn luyện mô hình” – gọi `/train`.
    - “🔍 Nhận diện” – gọi `/face/verify`.
  - Khối hiển thị:
    - `_status` – trạng thái tổng quát (thành công/thất bại/match/not match).
    - `_detail` – thông điệp chi tiết (cả cảnh báo môi trường từ backend).
    - `_distance` – distance nếu có.

App không tự xử lý môi trường, mà **tin vào backend**. Khi backend trả lỗi môi trường (HTTP 400, `detail` mô tả), app show ra. Khi nhận diện, backend trả `environment_info`, app hiển thị trong `_detail`.

---

## 4. Mã ví dụ `mobile/lib/main.dart`

```dart
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FaceID Mobile',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  /// Địa chỉ backend:
  /// - Android emulator: dùng 10.0.2.2
  /// - Thiết bị thật: thay bằng IP LAN của máy chạy backend, ví dụ 192.168.1.10
  final String baseUrl = 'http://10.0.2.2:8000';

  final ImagePicker _picker = ImagePicker();
  File? _selectedImage;

  double _threshold = 0.6;

  bool _loading = false;
  String? _status;
  String? _detail;
  double? _distance;

  Future<void> _pickImage(ImageSource source) async {
    final XFile? pickedFile = await _picker.pickImage(source: source);
    if (pickedFile != null) {
      setState(() {
        _selectedImage = File(pickedFile.path);
        _status = null;
        _detail = null;
        _distance = null;
      });
    }
  }

  Future<void> _sendToCollect() async {
    if (_selectedImage == null) return;

    setState(() {
      _loading = true;
      _status = 'Đang gửi ảnh huấn luyện...';
      _detail = null;
      _distance = null;
    });

    try {
      final uri = Uri.parse('$baseUrl/api/v1/collect');
      final request = http.MultipartRequest('POST', uri)
        ..files.add(
          await http.MultipartFile.fromPath('file', _selectedImage!.path),
        );

      final response = await request.send();
      final respStr = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        final data = jsonDecode(respStr);
        setState(() {
          _status = 'Gửi dữ liệu huấn luyện thành công ✅';
          _detail = data['message']?.toString() ?? 'Đã thêm một ảnh huấn luyện.';
        });
      } else {
        String errorMessage = 'Lỗi /collect: ${response.statusCode}';
        try {
          final data = jsonDecode(respStr);
          if (data['detail'] != null) {
            errorMessage = data['detail'].toString();
          }
        } catch (_) {}
        setState(() {
          _status = 'Gửi dữ liệu huấn luyện thất bại ❌';
          _detail = errorMessage;
        });
      }
    } catch (e) {
      setState(() {
        _status = 'Lỗi kết nối khi gửi ảnh huấn luyện ❌';
        _detail = e.toString();
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  Future<void> _callTrain() async {
    setState(() {
      _loading = true;
      _status = 'Đang huấn luyện mô hình...';
      _detail = null;
      _distance = null;
    });

    try {
      final uri = Uri.parse('$baseUrl/api/v1/train');
      final resp = await http.post(uri);

      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        setState(() {
          _status = 'Huấn luyện mô hình thành công ✅';
          _detail = data['message']?.toString() ??
              'Huấn luyện xong, mô hình đã sẵn sàng.';
        });
      } else {
        String errorMessage = 'Lỗi /train: ${resp.statusCode}';
        try {
          final data = jsonDecode(resp.body);
          if (data['detail'] != null) {
            errorMessage = data['detail'].toString();
          }
        } catch (_) {}
        setState(() {
          _status = 'Huấn luyện mô hình thất bại ❌';
          _detail = errorMessage;
        });
      }
    } catch (e) {
      setState(() {
        _status = 'Lỗi kết nối khi huấn luyện ❌';
        _detail = e.toString();
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  Future<void> _verifyFace() async {
    if (_selectedImage == null) return;

    setState(() {
      _loading = true;
      _status = 'Đang nhận diện khuôn mặt...';
      _detail = null;
      _distance = null;
    });

    try {
      final uri = Uri.parse(
        '$baseUrl/api/v1/face/verify?threshold=$_threshold',
      );

      final request = http.MultipartRequest('POST', uri)
        ..files.add(
          await http.MultipartFile.fromPath('file', _selectedImage!.path),
        );

      final response = await request.send();
      final respStr = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        final data = jsonDecode(respStr);

        final bool? isMatch = data['is_match'] as bool?;
        final double? distance =
            (data['distance'] as num?)?.toDouble();
        final String? message = data['message'] as String?;

        // Lấy thêm environment_info nếu muốn show chi tiết hơn
        final env = data['environment_info'];

        String envText = '';
        if (env != null) {
          envText = '\n\n[Thông tin môi trường]\n${jsonEncode(env)}';
        }

        setState(() {
          _distance = distance;
          _detail = (message ?? '') + envText;
          if (isMatch == true) {
            _status = '✅ KHUÔN MẶT CỦA BẠN';
          } else {
            _status = '❌ KHÔNG KHỚP VỚI MÔ HÌNH';
          }
        });
      } else {
        String errorMessage = 'Lỗi /face/verify: ${response.statusCode}';
        try {
          final data = jsonDecode(respStr);
          if (data['detail'] != null) {
            errorMessage = data['detail'].toString();
          }
        } catch (_) {}
        setState(() {
          _status = 'Nhận diện thất bại ❌';
          _detail = errorMessage;
        });
      }
    } catch (e) {
      setState(() {
        _status = 'Lỗi kết nối khi nhận diện ❌';
        _detail = e.toString();
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  Color _statusColor() {
    if (_status == null) return Colors.grey;
    if (_status!.contains('✅')) return Colors.green;
    if (_status!.contains('❌')) return Colors.red;
    return Colors.blue;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FaceID Mobile'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              'App mobile dùng để THU THẬP dữ liệu khuôn mặt, '
              'GỌI HUẤN LUYỆN và NHẬN DIỆN (kèm cảnh báo môi trường).',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                const Text('Ngưỡng (threshold):'),
                Expanded(
                  child: Slider(
                    min: 0.3,
                    max: 1.5,
                    value: _threshold,
                    divisions: 60,
                    label: _threshold.toStringAsFixed(2),
                    onChanged: (v) {
                      setState(() {
                        _threshold = v;
                      });
                    },
                  ),
                ),
              ],
            ),
            Text(
              'distance ≤ ${_threshold.toStringAsFixed(2)} ⇒ coi là **BẠN**',
              style: const TextStyle(fontSize: 12),
            ),
            const SizedBox(height: 16),
            if (_selectedImage != null)
              Column(
                children: [
                  Image.file(
                    _selectedImage!,
                    height: 260,
                    fit: BoxFit.cover,
                  ),
                  const SizedBox(height: 8),
                ],
              )
            else
              Container(
                height: 260,
                color: Colors.grey.shade200,
                child: const Center(
                  child: Text('Chưa chọn ảnh'),
                ),
              ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        _loading ? null : () => _pickImage(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Chụp ảnh'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        _loading ? null : () => _pickImage(ImageSource.gallery),
                    icon: const Icon(Icons.photo),
                    label: const Text('Chọn ảnh'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        _loading || _selectedImage == null ? null : _sendToCollect,
                    icon: const Icon(Icons.cloud_upload),
                    label: const Text('Gửi làm dữ liệu huấn luyện'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _loading ? null : _callTrain,
                    icon: const Icon(Icons.psychology),
                    label: const Text('Huấn luyện mô hình'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        _loading || _selectedImage == null ? null : _verifyFace,
                    icon: const Icon(Icons.search),
                    label: const Text('Nhận diện khuôn mặt'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            if (_status != null)
              Text(
                _status!,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: _statusColor(),
                ),
                textAlign: TextAlign.center,
              ),
            if (_detail != null) ...[
              const SizedBox(height: 8),
              Text(
                _detail!,
                textAlign: TextAlign.center,
              ),
            ],
            if (_distance != null) ...[
              const SizedBox(height: 8),
              Text('distance: ${_distance!.toStringAsFixed(4)}'),
            ],
          ],
        ),
      ),
    );
  }
}
```

---

## 5. Cách chạy app mobile

```bash
cd mobile
flutter pub get
flutter run
```

- Nếu dùng emulator Android:
  - Giữ `baseUrl = 'http://10.0.2.2:8000'`.
- Nếu dùng device thật:
  - Đổi `baseUrl` thành IP LAN của máy chạy backend.

---

## 6. Tóm tắt cho báo cáo

- App mobile **không tự dùng ảnh có sẵn**, mà có **bước thu thập khuôn mặt riêng**.
- Khi thu thập, nếu môi trường chưa đạt (tối/mờ/mặt nhỏ/nhiều người), backend trả lỗi → app hiển thị chi tiết, yêu cầu người dùng chụp lại.
- Khi nhận diện, app cho phép xem luôn thông tin `environment_info` để người dùng hiểu **vì sao kết quả có thể chưa tốt** (ví dụ do ảnh mờ, tối,…).  
