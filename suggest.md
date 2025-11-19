# ỨNG DỤNG PYTHON NHẬN DIỆN KHUÔN MẶT CÁ NHÂN  
## Backend dùng chung cho **Web** và **Mobile**

> File tài liệu: `face_recognition_backend_guide.md`  
> Nội dung: Thiết kế + mã nguồn **backend Python** (REST API) sử dụng được cho cả web app và mobile app.  
> Công nghệ: Python, face_recognition, OpenCV, FastAPI.

---

## 1. MỤC TIÊU

Xây dựng một **backend Python** có khả năng:

- Nhận diện **đúng khuôn mặt của sinh viên (chính bạn)** từ ảnh gửi lên qua HTTP.
- Cung cấp **REST API** để:
  - Web app (Streamlit / React / bất kỳ framework nào) gọi được.
  - Mobile app (Flutter / React Native / Android gốc, ...) gọi được.
- Xử lý:
  - Ảnh từ camera (mobile chụp, web chụp) hoặc ảnh từ thư viện.
  - So sánh khuôn mặt mới với dữ liệu huấn luyện (ảnh trong thư mục `myface/`).
- Trả về:
  - Thông tin nhận diện dạng **JSON**:
    - Có phải là bạn hay không (`is_match`).
    - Khoảng cách (`distance`).
    - Ngưỡng so sánh (`threshold`).
    - Vị trí khuôn mặt (`face_box`).
    - Thông điệp dễ hiểu (`message`).
- Có xử lý **exception** rõ ràng, backend ổn định, dễ debug.

---

## 2. YÊU CẦU KỸ THUẬT

### 2.1. Ngôn ngữ & thư viện chính

- **Python** (khuyến nghị 3.8 – 3.11).
- Nhận diện khuôn mặt:
  - `face_recognition`
- Xử lý ảnh:
  - `opencv-python` (OpenCV – `cv2`)
  - `numpy`
- Web backend (REST API):
  - `fastapi`
  - `uvicorn`
  - `python-multipart` (để nhận file upload)
- Phụ trợ:
  - `Pillow` (nếu cần xử lý ảnh thêm, không bắt buộc).

### 2.2. Gợi ý cài đặt môi trường

```bash
# 1. Tạo virtual environment (khuyến khích)
python -m venv .venv
.\.venv\Scriptsctivate    # Windows
# source .venv/bin/activate # Linux / macOS

# 2. Nâng cấp pip
python -m pip install --upgrade pip

# 3. Cài thư viện cần thiết
pip install face-recognition opencv-python fastapi uvicorn[standard] python-multipart numpy pillow
```

> Lưu ý:  
> - `face_recognition` cần `dlib`, trên Windows có thể phải cài thêm CMake / Build Tools.  
> - Nếu cài bị lỗi, có thể dùng WSL/Ubuntu hoặc tìm file `.whl` phù hợp.

---

## 3. CÁC BƯỚC THỰC HIỆN (BÁM ĐÚNG FORM ĐỀ BÀI)

### Bước 1 – Cài đặt công cụ

- Cài **Python**.
- Cài thư viện:
  - `face_recognition`
  - `opencv-python`
  - `fastapi`, `uvicorn`, `python-multipart`
- Kiểm tra nhanh:

```bash
python -c "import face_recognition, cv2, fastapi, numpy; print('OK')"
```

---

### Bước 2 – Chuẩn bị dữ liệu khuôn mặt

1. Chụp **5–10 ảnh** khuôn mặt của **chính bạn**:
   - Ảnh rõ, khuôn mặt chiếm phần lớn khung hình.
   - Đa dạng: nhìn thẳng, hơi nghiêng trái/phải, có/không đeo kính, ánh sáng khác nhau.
2. Tạo cấu trúc thư mục dự án:

```text
project_folder/
├─ backend/
│  └─ main.py          # file backend FastAPI
└─ myface/             # ảnh dùng làm dữ liệu nhận diện của riêng bạn
   ├─ img1.jpg
   ├─ img2.jpg
   └─ ...
```

3. Đảm bảo **chỉ chứa khuôn mặt của bạn**, mỗi ảnh **1 khuôn mặt** để tránh nhiễu.

---

### Bước 3 – Tạo dữ liệu nhận diện (face embedding)

Backend sẽ:

1. Đọc **toàn bộ ảnh** trong thư mục `myface/`.
2. Với mỗi ảnh:
   - Tìm vị trí khuôn mặt.
   - Trích xuất **face embedding** (vector 128 chiều) bằng `face_recognition.face_encodings`.
3. Lưu các vector này vào bộ nhớ (cache) để dùng cho mọi request.

Vector 128 chiều của mỗi ảnh chính là **“dấu vân tay khuôn mặt”**.  
Backend gộp nhiều vector lại để tăng độ chính xác.

---

### Bước 4 – Xây dựng chức năng so sánh khuôn mặt

Khi **web app** hoặc **mobile app** gửi ảnh lên (qua API):

1. Backend đọc dữ liệu ảnh (bytes) và giải mã thành `numpy array` (BGR – OpenCV).
2. Chuyển sang RGB, tìm đúng 1 khuôn mặt, trích vector đặc trưng.
3. So sánh với các vector đã học (từ `myface/`) bằng:

   ```python
   distances = face_recognition.face_distance(known_encodings, unknown_encoding)
   best_distance = np.min(distances)
   ```

4. Kết luận:
   - Nếu `best_distance <= threshold` → **nhận diện đúng (là bạn)**.
   - Nếu `best_distance > threshold` → **không phải bạn**.

Ngưỡng `threshold` được truyền qua query param (vd: `?threshold=0.5`) hoặc dùng mặc định.

---

### Bước 5 – Xây dựng giao diện người dùng (WEB & MOBILE)

- **Backend** không hiển thị giao diện trực tiếp; nó cung cấp API để:
  - Web app (vd: Streamlit / React / Vue / Django template) gửi ảnh → nhận JSON kết quả.
  - Mobile app (vd: Flutter / React Native / Kotlin / Swift) gửi ảnh → nhận JSON kết quả.

#### Gợi ý cho web (ví dụ Streamlit):

- Web app:
  - Cho phép user upload ảnh hoặc chụp từ webcam.
  - Gọi API `POST /api/v1/face/verify` (gửi file ảnh).
  - Nhận JSON, hiển thị:
    - “Đây là bạn” hoặc “Không phải bạn”.
    - Khoảng cách + ngưỡng.
    - (Tuỳ chọn) vẽ bounding box ở phía frontend.

#### Gợi ý cho mobile:

- Mobile app:
  - Chụp ảnh từ camera hoặc chọn từ gallery.
  - Gửi ảnh đó lên API backend.
  - Nhận JSON kết quả và hiển thị trên UI:
    - Icon ✅ / ❌.
    - Thông điệp: “Khớp khuôn mặt” / “Không khớp”.

---

### Bước 6 – Kiểm thử

Kiểm thử đầy đủ như yêu cầu:

- Nhìn thẳng vào camera (hoặc chụp ảnh thẳng) → **phải nhận diện đúng**.
- Nghiêng trái / nghiêng phải → vẫn nên giữ được độ chính xác.
- Đeo kính, thay đổi ánh sáng → vẫn nhận diện được trong đa số tình huống.
- Cho người khác xuất hiện:
  - Kết quả phải là **“Không phải bạn”**.
- Kiểm thử khi:
  - Không có mặt trong ảnh.
  - Có nhiều mặt trong ảnh.
  - Ảnh bị mờ / tối → xem backend trả exception như thế nào.

---

## 4. THIẾT KẾ BACKEND API DÙNG CHUNG CHO WEB & MOBILE

### 4.1. Cấu trúc API

- `GET /api/v1/health`
  - Kiểm tra backend còn sống.
  - Trả về: `{ "status": "ok" }`

- `POST /api/v1/face/verify?threshold=0.5`
  - Nhận 1 file ảnh khuôn mặt (form-data, field name: `file`).
  - Tham số:
    - `threshold` (float, optional) – ngưỡng so sánh (mặc định 0.5).
  - Trả về JSON:

    ```json
    {
      "is_match": true,
      "distance": 0.43,
      "threshold": 0.5,
      "message": "Đây là khuôn mặt của bạn.",
      "face_box": {
        "top": 100,
        "right": 200,
        "bottom": 220,
        "left": 80
      },
      "image_size": {
        "width": 640,
        "height": 480
      },
      "training_info": {
        "num_images": 7
      }
    }
    ```

- Tất cả HTTP error (404, 422, 500, ...) sẽ trả JSON với `{ "detail": "..." }`.

### 4.2. Kiến trúc tổng thể

- Backend không phụ thuộc vào UI:
  - Bất kỳ client nào (web, mobile, Postman, curl) đều gọi API như nhau.
- Lợi ích:
  - Thỏa yêu cầu “backend dùng cho cả web và app mobile”.
  - Dễ mở rộng thêm các client khác sau này.

---

## 5. MÃ NGUỒN BACKEND HOÀN CHỈNH (`backend/main.py`)

> Đặt file này trong thư mục `backend/` cùng cấp với thư mục `myface/`.  
> Chạy backend với lệnh:
>
> ```bash
> uvicorn backend.main:app --reload
> ```

```python
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

import cv2
import face_recognition
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


# =========================
# CẤU HÌNH THƯ MỤC DỮ LIỆU
# =========================
DATA_DIR = Path("myface")  # Thư mục chứa ảnh khuôn mặt của BẠN
VALID_EXTENSIONS = (".jpg", ".jpeg", ".png")


# =========================
# HÀM TẢI & TẠO FACE EMBEDDING
# =========================
def load_known_face_encodings() -> Tuple[List[np.ndarray], List[str]]:
    """
    Đọc tất cả ảnh trong thư mục myface/, trích xuất face embedding.

    Returns:
        known_encodings: danh sách vector 128 chiều (numpy array).
        used_files: danh sách tên file đã dùng thành công.

    Raises:
        FileNotFoundError: nếu thư mục myface không tồn tại.
        ValueError: nếu không tìm được bất kỳ khuôn mặt hợp lệ nào.
    """
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Không tìm thấy thư mục dữ liệu khuôn mặt: '{DATA_DIR.resolve()}'"
        )

    known_encodings: List[np.ndarray] = []
    used_files: List[str] = []

    for filename in DATA_DIR.iterdir():
        if not filename.is_file():
            continue
        if not filename.suffix.lower() in VALID_EXTENSIONS:
            # Bỏ qua file không phải ảnh
            continue

        img_path = filename

        try:
            # face_recognition load_image_file trả về ảnh RGB
            image = face_recognition.load_image_file(str(img_path))
        except Exception as e:
            # Bắt lỗi đọc file ảnh (bị hỏng, không đọc được, ...)
            print(f"Lỗi khi đọc ảnh {img_path}: {e}")
            continue

        # Tìm vị trí khuôn mặt
        face_locations = face_recognition.face_locations(image)
        if len(face_locations) == 0:
            print(f"Không tìm thấy khuôn mặt trong ảnh: {img_path}")
            continue
        if len(face_locations) > 1:
            print(f"Ảnh {img_path} có {len(face_locations)} khuôn mặt, bỏ qua.")
            continue

        encodings = face_recognition.face_encodings(
            image, known_face_locations=face_locations
        )
        if not encodings:
            print(f"Không trích xuất được encoding từ ảnh: {img_path}")
            continue

        known_encodings.append(encodings[0])
        used_files.append(img_path.name)

    if not known_encodings:
        raise ValueError(
            "Không tìm được bất kỳ khuôn mặt hợp lệ nào trong thư mục 'myface/'. "
            "Hãy chắc chắn mỗi ảnh chỉ có 1 khuôn mặt rõ ràng của bạn."
        )

    return known_encodings, used_files


@lru_cache(maxsize=1)
def get_known_faces_cache() -> Tuple[List[np.ndarray], List[str]]:
    """
    Cache dữ liệu khuôn mặt để không phải tính lại nhiều lần.
    """
    return load_known_face_encodings()


# =========================
# HÀM XỬ LÝ KHUÔN MẶT ẢNH MỚI
# =========================
def extract_single_face_encoding(
    image_rgb: np.ndarray,
) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """
    Từ ảnh RGB, trích xuất encoding cho đúng 1 khuôn mặt.

    Returns:
        encoding: vector 128 chiều.
        location: (top, right, bottom, left).

    Raises:
        ValueError: nếu không tìm thấy khuôn mặt hoặc có nhiều hơn 1 khuôn mặt.
    """
    face_locations = face_recognition.face_locations(image_rgb)

    if len(face_locations) == 0:
        raise ValueError(
            "Không tìm thấy khuôn mặt nào trong ảnh. "
            "Hãy để mặt của bạn chiếm phần lớn khung hình và không bị che."
        )
    if len(face_locations) > 1:
        raise ValueError(
            f"Phát hiện {len(face_locations)} khuôn mặt trong ảnh. "
            "Vui lòng để CHỈ MỘT người trong ảnh khi nhận diện."
        )

    encodings = face_recognition.face_encodings(
        image_rgb, known_face_locations=face_locations
    )
    if not encodings:
        raise ValueError(
            "Không trích xuất được vector đặc trưng cho khuôn mặt. "
            "Có thể ảnh bị mờ, tối hoặc chất lượng quá thấp."
        )

    return encodings[0], face_locations[0]


def compare_with_known_faces(
    unknown_encoding: np.ndarray,
    known_encodings: List[np.ndarray],
    threshold: float,
) -> Tuple[bool, float]:
    """
    So sánh khuôn mặt mới với các encoding đã biết.
    """
    distances = face_recognition.face_distance(known_encodings, unknown_encoding)
    best_distance = float(np.min(distances))
    is_match = best_distance <= threshold
    return is_match, best_distance


def read_image_from_upload(file_bytes: bytes) -> np.ndarray:
    """
    Đọc ảnh từ bytes (UploadFile) sang OpenCV BGR.

    Raises:
        ValueError: nếu không đọc được ảnh.
    """
    nparr = np.frombuffer(file_bytes, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image_bgr is None:
        raise ValueError(
            "Không đọc được ảnh từ dữ liệu upload. "
            "Hãy kiểm tra lại định dạng file (jpg, jpeg, png)."
        )

    return image_bgr


# =========================
# KHỞI TẠO FASTAPI APP
# =========================
app = FastAPI(
    title="Face Recognition Backend",
    description=(
        "Backend nhận diện khuôn mặt cá nhân, dùng chung cho Web & Mobile.
"
        "Sử dụng Python, FastAPI, face_recognition, OpenCV."
    ),
    version="1.0.0",
)

# Cho phép CORS cho mọi nguồn (dùng cho demo, dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong môi trường production nên giới hạn domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# API ENDPOINTS
# =========================
@app.get("/api/v1/health")
def health_check():
    """
    Endpoint kiểm tra hệ thống còn hoạt động.
    """
    return {"status": "ok"}


@app.post("/api/v1/face/verify")
async def verify_face(
    file: UploadFile = File(..., description="Ảnh khuôn mặt (jpg/jpeg/png)"),
    threshold: float = Query(
        0.5,
        ge=0.0,
        le=1.0,
        description="Ngưỡng khoảng cách để xem là cùng một người (mặc định 0.5).",
    ),
):
    """
    Nhận ảnh khuôn mặt từ client (web/mobile), so sánh với dữ liệu trong `myface/`.
    """

    # 1. Kiểm tra loại file
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(
            status_code=400,
            detail="File upload phải là ảnh (.jpg, .jpeg, .png).",
        )

    # 2. Tải dữ liệu khuôn mặt đã biết
    try:
        known_encodings, used_files = get_known_faces_cache()
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=500, detail=str(fnf))
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi nội bộ khi tải dữ liệu khuôn mặt: {e}",
        )

    # 3. Đọc bytes ảnh upload
    try:
        file_bytes = await file.read()
        image_bgr = read_image_from_upload(file_bytes)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi nội bộ khi xử lý ảnh upload: {e}",
        )

    # 4. Chuyển sang RGB & trích xuất encoding
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    try:
        unknown_encoding, face_location = extract_single_face_encoding(image_rgb)
    except ValueError as ve:
        # Lỗi do nội dung ảnh (không có mặt, nhiều mặt, không trích xuất được encoding)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi nội bộ khi trích xuất đặc trưng khuôn mặt: {e}",
        )

    # 5. So sánh với dữ liệu đã học
    try:
        is_match, best_distance = compare_with_known_faces(
            unknown_encoding=unknown_encoding,
            known_encodings=known_encodings,
            threshold=threshold,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi nội bộ khi so sánh khuôn mặt: {e}",
        )

    # 6. Tạo message kết quả
    if is_match:
        message = (
            f"Đây là KHUÔN MẶT CỦA BẠN "
            f"(khoảng cách = {best_distance:.3f} ≤ ngưỡng {threshold:.3f})."
        )
    else:
        message = (
            f"Khuôn mặt này KHÔNG KHỚP với dữ liệu của bạn "
            f"(khoảng cách = {best_distance:.3f} > ngưỡng {threshold:.3f})."
        )

    # 7. Chuẩn bị dữ liệu trả về
    top, right, bottom, left = face_location
    height, width = image_bgr.shape[:2]

    response_data = {
        "is_match": is_match,
        "distance": best_distance,
        "threshold": threshold,
        "message": message,
        "face_box": {
            "top": int(top),
            "right": int(right),
            "bottom": int(bottom),
            "left": int(left),
        },
        "image_size": {
            "width": int(width),
            "height": int(height),
        },
        "training_info": {
            "num_images": len(known_encodings),
            "used_files_sample": used_files[:5],
        },
    }

    return JSONResponse(content=response_data)
```

---

## 6. VÍ DỤ GỌI API TỪ WEB & MOBILE

### 6.1. Web (JavaScript Fetch)

```javascript
async function verifyFace(file) {
  const formData = new FormData();
  formData.append("file", file);

  const threshold = 0.5; // có thể cho người dùng chỉnh

  const response = await fetch(
    `http://localhost:8000/api/v1/face/verify?threshold=${threshold}`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Lỗi khi gọi API");
  }

  const data = await response.json();
  console.log("Kết quả nhận diện:", data);
  return data;
}
```

### 6.2. Mobile (ví dụ Flutter – pseudo code)

```dart
import 'package:http/http.dart' as http;

Future<void> verifyFaceFromFlutter(File imageFile) async {
  final uri = Uri.parse(
      'http://10.0.2.2:8000/api/v1/face/verify?threshold=0.5'); // Emulator Android

  final request = http.MultipartRequest('POST', uri)
    ..files.add(await http.MultipartFile.fromPath('file', imageFile.path));

  final response = await request.send();

  if (response.statusCode == 200) {
    final respStr = await response.stream.bytesToString();
    print('Kết quả: $respStr');
  } else {
    print('Lỗi: ${response.statusCode}');
  }
}
```

---

## 7. EXCEPTION & KIỂM THỬ (TỔNG HỢP)

### 7.1. Các exception chính

1. **Thiếu thư mục `myface/`**
   - Exception: `FileNotFoundError` trong `load_known_face_encodings`.
   - HTTP trả về: `500 Internal Server Error` + message:
     - `"Không tìm thấy thư mục dữ liệu khuôn mặt: '.../myface'"`.

2. **Không có ảnh hợp lệ trong `myface/`**
   - Exception: `ValueError` trong `load_known_face_encodings`.
   - HTTP 500:
     - `"Không tìm được bất kỳ khuôn mặt hợp lệ nào trong thư mục 'myface/'..."`.

3. **File upload không phải ảnh**
   - Nếu `content_type` không phải `image/jpeg` hoặc `image/png`:
   - HTTP 400:
     - `"File upload phải là ảnh (.jpg, .jpeg, .png)."`

4. **Ảnh upload không đọc được / bị lỗi**
   - `read_image_from_upload` ném `ValueError`:
   - HTTP 400:
     - `"Không đọc được ảnh từ dữ liệu upload..."`.

5. **Không tìm thấy khuôn mặt / nhiều khuôn mặt trong ảnh upload**
   - `extract_single_face_encoding` ném `ValueError`:
   - HTTP 400:
     - `"Không tìm thấy khuôn mặt nào trong ảnh..."` hoặc
     - `"Phát hiện N khuôn mặt trong ảnh..."`.

6. **Lỗi nội bộ khác (so sánh, trích xuất, đọc ảnh, ...)**
   - HTTP 500:
     - Message bắt đầu bằng `"Lỗi nội bộ..."` để sinh viên dễ debug.

### 7.2. Các trường hợp kiểm thử khuyến nghị

- Ảnh bạn nhìn thẳng, rõ → `is_match = true`.
- Ảnh bạn nghiêng trái / phải → vẫn true (nếu threshold hợp lý).
- Ảnh bạn đeo kính, ánh sáng khác → đa số vẫn true.
- Ảnh người khác → `is_match = false`.
- Ảnh chứa 2+ người → HTTP 400 + message warning.
- File không phải ảnh (vd: `.txt`) → HTTP 400.

---

## 8. GỢI Ý MỞ RỘNG & ĐIỂM CỘNG

- Thêm endpoint đăng ký user:
  - `POST /api/v1/users/{user_id}/faces` để upload ảnh huấn luyện.
- Lưu embedding ra file `.npy` hoặc database để tăng tốc khởi động.
- Thêm logging:
  - Lưu lịch sử nhận diện (thời gian, kết quả, client).
- Triển khai backend lên cloud (Render, Railway, Vercel, ...):
  - Mobile & web app có thể gọi mọi lúc, mọi nơi.

---

> ✅ Backend trong file `.md` này:
> - Đã sửa **hoàn toàn** theo hướng **backend dùng chung cho web & mobile**.  
> - Vẫn bám sát **form 6 bước** đề bài.  
> - Cung cấp **REST API rõ ràng, JSON response**, đầy đủ **exception** và gợi ý kiểm thử.  
> - Có mã nguồn FastAPI hoàn chỉnh để chạy trực tiếp.
