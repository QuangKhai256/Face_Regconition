# Backend – Hệ thống nhận diện khuôn mặt cá nhân  
## Có BƯỚC THU THẬP KHUÔN MẶT + KIỂM TRA MÔI TRƯỜNG + HUẤN LUYỆN MÔ HÌNH

---

## 1. Mục tiêu backend

Backend chịu trách nhiệm:

1. **Thu thập dữ liệu khuôn mặt** (ENROLLMENT PHASE)  
   - Web / mobile gửi ảnh lên endpoint `/api/v1/collect`.  
   - Backend:
     - Kiểm tra **môi trường xung quanh** (độ sáng, độ mờ, kích thước mặt, số lượng người).  
     - Nếu đạt yêu cầu → lưu ảnh vào thư mục dữ liệu huấn luyện.

2. **Huấn luyện mô hình nhận diện cá nhân**  
   - Endpoint `/api/v1/train`.  
   - Đọc toàn bộ ảnh đã thu thập, trích xuất embedding, tính **vector trung bình** đại diện cho khuôn mặt của bạn.

3. **Nhận diện khuôn mặt online**  
   - Endpoint `/api/v1/face/verify`.  
   - Kiểm tra môi trường xung quanh khi nhận diện.  
   - Trả về:
     - `is_match`, `distance`, `threshold`, `message`.  
     - `environment_info`: thông tin về độ sáng, độ mờ, kích thước mặt, cảnh báo môi trường.  

> Như vậy project có **3 giai đoạn rõ ràng**:  
> **Thu thập khuôn mặt → Huấn luyện mô hình → Nhận diện & kiểm tra môi trường.**

---

## 2. Yêu cầu kỹ thuật

### 2.1. Công nghệ

- Python 3.8–3.11.
- Thư viện:
  - `fastapi`, `uvicorn[standard]` – backend API.
  - `face_recognition` – trích xuất đặc trưng (embedding).
  - `opencv-python` (`cv2`) – xử lý ảnh, tính độ sáng/độ mờ.
  - `numpy` – xử lý ma trận, tính trung bình embedding.
  - `python-multipart` – nhận file ảnh.

### 2.2. Cài đặt

```bash
python -m venv .venv
.\.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # Linux/macOS

python -m pip install --upgrade pip

pip install fastapi uvicorn[standard] face-recognition opencv-python numpy python-multipart
```

---

## 3. Cấu trúc thư mục

```text
project_folder/
├─ backend/
│  └─ main.py                    # File backend FastAPI
├─ web/
│  └─ web_app.py                 # Frontend web (Streamlit)
├─ mobile/
│  └─ lib/
│     └─ main.dart               # App Flutter
├─ data/
│  └─ raw/
│     └─ user/                   # Ảnh khuôn mặt của bạn (thu thập)
└─ models/
   ├─ user_embeddings.npy        # Toàn bộ embedding huấn luyện
   └─ user_embedding_mean.npy    # Embedding trung bình (mô hình cá nhân)
```

---

## 4. Kiểm tra môi trường xung quanh (Environment Check)

Khi **thu thập dữ liệu** và **nhận diện**, backend sẽ:

1. Phát hiện khuôn mặt (bắt buộc phải có **1 khuôn mặt duy nhất**).  
2. Tính một số chỉ số môi trường:

   - **Độ sáng (brightness)**:  
     - Trung bình giá trị pixel (0–255).  
     - `is_too_dark = brightness < 60`  
     - `is_too_bright = brightness > 200`

   - **Độ mờ (blur)** – dùng phương sai Laplacian:
     - `blur_score = var(Laplacian(gray))`  
     - `is_too_blurry = blur_score < 100.0`

   - **Kích thước khuôn mặt trong khung hình**:
     - `face_size_ratio = diện_tích_khung_mặt / diện_tích_ảnh`  
     - `is_face_too_small = face_size_ratio < 0.1`

3. Nếu **THU THẬP DỮ LIỆU** (`/collect`):  
   - Nếu ảnh **quá tối / quá mờ / mặt quá nhỏ / nhiều người** → **từ chối** với HTTP 400 và thông báo hướng dẫn chụp lại.  
   - Mục tiêu: chỉ lưu những ảnh **chất lượng tốt** vào tập huấn luyện.

4. Nếu **NHẬN DIỆN** (`/face/verify`):  
   - Luôn trả về kết quả nhận diện (nếu có thể).  
   - Kèm theo `environment_info` để frontend/mobile hiển thị cảnh báo:
     - Ví dụ: “Ảnh hơi tối, nên đứng gần nguồn sáng hơn”.

---

## 5. Thiết kế API

| Method | URL                     | Chức năng                                      |
|--------|-------------------------|------------------------------------------------|
| GET    | `/api/v1/health`        | Kiểm tra backend hoạt động                     |
| POST   | `/api/v1/collect`       | **Thu thập** ảnh khuôn mặt (kiểm tra môi trường) |
| POST   | `/api/v1/train`         | Huấn luyện mô hình cá nhân                     |
| POST   | `/api/v1/face/verify`   | Nhận diện + kiểm tra môi trường                |

---

## 6. Mã nguồn backend – `backend/main.py`

```python
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict, Any

import cv2
import numpy as np
import face_recognition
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


# =========================
# CẤU HÌNH THƯ MỤC & FILE
# =========================
DATA_USER_DIR = Path("data/raw/user")
MODEL_DIR = Path("models")
MODEL_EMBEDDINGS_PATH = MODEL_DIR / "user_embeddings.npy"
MODEL_MEAN_PATH = MODEL_DIR / "user_embedding_mean.npy"

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png")


def ensure_directories():
    DATA_USER_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


ensure_directories()


# =========================
# HÀM TIỆN ÍCH CHUNG
# =========================
def load_image_bgr_from_bytes(file_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(file_bytes, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise ValueError("Không đọc được ảnh từ dữ liệu upload. Hãy kiểm tra lại định dạng file.")
    return image_bgr


def extract_single_face_embedding(image_rgb: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """
    Tìm đúng 1 khuôn mặt và trả về:
    - embedding 128 chiều
    - vị trí (top, right, bottom, left)
    """
    face_locations = face_recognition.face_locations(image_rgb)

    if len(face_locations) == 0:
        raise ValueError(
            "Không tìm thấy khuôn mặt nào. Hãy để mặt bạn chiếm phần lớn khung hình,"
            " không bị che khuất."
        )
    if len(face_locations) > 1:
        raise ValueError(
            f"Phát hiện {len(face_locations)} khuôn mặt. "
            "Vui lòng chỉ để MỘT người trong khung hình khi thu thập/nhận diện."
        )

    encodings = face_recognition.face_encodings(image_rgb, known_face_locations=face_locations)
    if not encodings:
        raise ValueError(
            "Không trích xuất được vector đặc trưng cho khuôn mặt. Ảnh có thể quá mờ/tối."
        )

    return encodings[0], face_locations[0]


def analyze_environment(image_bgr: np.ndarray, face_box: Tuple[int, int, int, int]) -> Dict[str, Any]:
    """
    Phân tích môi trường xung quanh dựa trên ảnh và bounding box khuôn mặt.
    Trả về:
    - brightness, is_too_dark, is_too_bright
    - blur_score, is_too_blurry
    - face_size_ratio, is_face_too_small
    - warnings: list các cảnh báo dạng text
    """
    (top, right, bottom, left) = face_box

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Độ sáng trung bình
    brightness = float(np.mean(gray))

    # Độ mờ sử dụng Laplacian
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    blur_score = float(lap.var())

    # Kích thước mặt trong khung
    h, w = gray.shape[:2]
    face_area = max((bottom - top), 1) * max((right - left), 1)
    frame_area = max(w * h, 1)
    face_size_ratio = float(face_area / frame_area)

    is_too_dark = brightness < 60.0
    is_too_bright = brightness > 200.0
    is_too_blurry = blur_score < 100.0
    is_face_too_small = face_size_ratio < 0.10  # < 10% diện tích ảnh

    warnings = []

    if is_too_dark:
        warnings.append("Ảnh khá tối. Nên đứng gần nguồn sáng hơn hoặc bật thêm đèn.")
    if is_too_bright:
        warnings.append("Ảnh quá sáng/gắt. Nên tránh nguồn sáng chiếu thẳng vào mặt.")
    if is_too_blurry:
        warnings.append("Ảnh bị mờ. Hãy giữ máy/camera cố định và tránh rung tay.")
    if is_face_too_small:
        warnings.append("Khuôn mặt quá nhỏ trong khung hình. Hãy tiến lại gần camera.")

    return {
        "brightness": brightness,
        "is_too_dark": is_too_dark,
        "is_too_bright": is_too_bright,
        "blur_score": blur_score,
        "is_too_blurry": is_too_blurry,
        "face_size_ratio": face_size_ratio,
        "is_face_too_small": is_face_too_small,
        "warnings": warnings,
    }


def save_training_image(file_bytes: bytes) -> Path:
    """
    Lưu ảnh huấn luyện (sau khi đã kiểm tra môi trường).
    """
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_{now_str}.jpg"
    out_path = DATA_USER_DIR / filename

    nparr = np.frombuffer(file_bytes, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise ValueError("Không đọc được ảnh khi lưu. Định dạng ảnh không hợp lệ.")

    cv2.imwrite(str(out_path), image_bgr)
    return out_path


# =========================
# HUẤN LUYỆN MÔ HÌNH CÁ NHÂN
# =========================
def train_personal_model() -> Tuple[int, int]:
    """
    - Đọc ảnh từ data/raw/user/
    - Trích xuất embedding cho mỗi ảnh hợp lệ
    - Tính embedding trung bình
    - Lưu models/user_embeddings.npy & models/user_embedding_mean.npy
    """
    image_paths: List[Path] = []
    for p in DATA_USER_DIR.iterdir():
        if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS:
            image_paths.append(p)

    if not image_paths:
        raise ValueError(
            "Không có ảnh huấn luyện nào trong 'data/raw/user/'. "
            "Hãy thu thập ảnh trước bằng /api/v1/collect."
        )

    embeddings = []

    for img_path in image_paths:
        try:
            image = face_recognition.load_image_file(str(img_path))
        except Exception as e:
            print(f"Lỗi khi đọc ảnh {img_path}: {e}")
            continue

        try:
            embedding, _ = extract_single_face_embedding(image)
            embeddings.append(embedding)
        except ValueError as ve:
            print(f"Bỏ qua ảnh {img_path}: {ve}")
        except Exception as e:
            print(f"Lỗi không xác định với ảnh {img_path}: {e}")

    if not embeddings:
        raise ValueError(
            "Không trích xuất được embedding từ bất kỳ ảnh huấn luyện nào. "
            "Kiểm tra lại chất lượng ảnh trong 'data/raw/user/'."
        )

    embeddings_arr = np.stack(embeddings, axis=0)  # (N, 128)
    mean_embedding = np.mean(embeddings_arr, axis=0)  # (128,)

    np.save(MODEL_EMBEDDINGS_PATH, embeddings_arr)
    np.save(MODEL_MEAN_PATH, mean_embedding)

    return len(image_paths), embeddings_arr.shape[0]


def load_trained_model() -> np.ndarray:
    if not MODEL_MEAN_PATH.exists():
        raise FileNotFoundError(
            "Chưa có mô hình huấn luyện. Hãy gọi /api/v1/train sau khi thu thập đủ ảnh."
        )
    mean_embedding = np.load(MODEL_MEAN_PATH)
    return mean_embedding


# =========================
# KHỞI TẠO FASTAPI
# =========================
app = FastAPI(
    title="Face Recognition Backend – Personal Training",
    description=(
        "Backend nhận diện khuôn mặt cá nhân: có bước THU THẬP dữ liệu, "
        "KIỂM TRA MÔI TRƯỜNG, HUẤN LUYỆN mô hình, và NHẬN DIỆN online."
    ),
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Prod nên giới hạn domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ENDPOINTS
# =========================
@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/v1/collect")
async def collect_face_image(
    file: UploadFile = File(
        ...,
        description="Ảnh khuôn mặt dùng cho HUẤN LUYỆN (.jpg/.jpeg/.png). "
                    "Backend sẽ kiểm tra môi trường trước khi lưu."
    )
):
    """
    THU THẬP DỮ LIỆU HUẤN LUYỆN:
    - Kiểm tra môi trường (ánh sáng, mờ, kích thước mặt, số người).
    - Nếu OK thì mới lưu ảnh vào data/raw/user/.
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="File phải là ảnh (.jpg, .jpeg, .png).")

    try:
        file_bytes = await file.read()
        image_bgr = load_image_bgr_from_bytes(file_bytes)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # Bắt buộc phải có 1 khuôn mặt để thu thập
        embedding, face_box = extract_single_face_embedding(image_rgb)

        # Phân tích môi trường
        env_info = analyze_environment(image_bgr, face_box)

        # Nếu môi trường quá kém thì từ chối lưu
        if env_info["is_too_dark"] or env_info["is_too_blurry"] or env_info["is_face_too_small"]:
            warnings_text = " ".join(env_info["warnings"])
            raise HTTPException(
                status_code=400,
                detail=(
                    "Môi trường chưa phù hợp để thu thập dữ liệu. "
                    + warnings_text
                ),
            )

        # Nếu ok → lưu ảnh
        saved_path = save_training_image(file_bytes)

    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi nội bộ khi thu thập dữ liệu: {e}")

    total_images = len([p for p in DATA_USER_DIR.iterdir() if p.is_file()])

    return JSONResponse(
        content={
            "message": "Đã lưu ảnh huấn luyện (môi trường đạt yêu cầu).",
            "saved_path": str(saved_path),
            "total_images": total_images,
            "environment_info": env_info,
        }
    )


@app.post("/api/v1/train")
def train_model_endpoint():
    """
    HUẤN LUYỆN MÔ HÌNH CÁ NHÂN:
    - Đọc ảnh trong data/raw/user/
    - Tạo embedding & tính embedding trung bình
    - Lưu vào thư mục models/
    """
    try:
        num_images, num_embeddings = train_personal_model()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fe:
        raise HTTPException(status_code=500, detail=str(fe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi nội bộ khi huấn luyện: {e}")

    return JSONResponse(
        content={
            "message": "Huấn luyện mô hình khuôn mặt cá nhân thành công.",
            "num_images": num_images,
            "num_embeddings": num_embeddings,
        }
    )


@app.post("/api/v1/face/verify")
async def verify_face(
    file: UploadFile = File(
        ...,
        description="Ảnh khuôn mặt cần NHẬN DIỆN (.jpg/.jpeg/.png). "
                    "Backend sẽ kiểm tra môi trường và trả về cảnh báo nếu có."
    ),
    threshold: float = Query(
        0.6,
        ge=0.0,
        le=2.0,
        description="Ngưỡng khoảng cách để xem là cùng một người (mặc định 0.6).",
    ),
):
    """
    NHẬN DIỆN KHUÔN MẶT:
    - Tải mô hình (embedding trung bình).
    - Trích xuất embedding từ ảnh hiện tại.
    - Tính distance, so với threshold.
    - Phân tích môi trường (độ sáng, mờ, kích thước mặt) và trả về environment_info.
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="File phải là ảnh (.jpg, .jpeg, .png).")

    # Tải mô hình
    try:
        mean_embedding = load_trained_model()
    except FileNotFoundError as fe:
        raise HTTPException(status_code=400, detail=str(fe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi nội bộ khi tải mô hình: {e}")

    # Đọc ảnh
    try:
        file_bytes = await file.read()
        image_bgr = load_image_bgr_from_bytes(file_bytes)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi nội bộ khi xử lý ảnh upload: {e}")

    # Trích xuất embedding + vị trí mặt
    try:
        unknown_embedding, face_location = extract_single_face_embedding(image_rgb)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi nội bộ khi trích xuất embedding: {e}")

    # Phân tích môi trường
    env_info = analyze_environment(image_bgr, face_location)

    # Tính distance
    distance = float(np.linalg.norm(unknown_embedding - mean_embedding))
    is_match = distance <= threshold

    if is_match:
        message = (
            f"Đây có khả năng là KHUÔN MẶT CỦA BẠN "
            f"(distance = {distance:.4f} ≤ threshold {threshold:.4f})."
        )
    else:
        message = (
            f"Khuôn mặt này KHÔNG KHỚP với mô hình cá nhân "
            f"(distance = {distance:.4f} > threshold {threshold:.4f})."
        )

    # Chuẩn bị response
    top, right, bottom, left = face_location
    h, w = image_bgr.shape[:2]

    response_data = {
        "is_match": is_match,
        "distance": distance,
        "threshold": threshold,
        "message": message,
        "face_box": {
            "top": int(top),
            "right": int(right),
            "bottom": int(bottom),
            "left": int(left),
        },
        "image_size": {
            "width": int(w),
            "height": int(h),
        },
        "environment_info": env_info,
    }

    return JSONResponse(content=response_data)
```

---

## 7. Cách chạy backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

- Health check: `GET http://localhost:8000/api/v1/health`
- Swagger UI: `http://localhost:8000/docs`

---

## 8. Tóm tắt cho báo cáo

- **Project KHÔNG chỉ dùng model sẵn để demo**, mà có:
  1. **Bước thu thập khuôn mặt** (enrollment) qua `/collect`, có **kiểm tra môi trường**.
  2. **Bước huấn luyện mô hình cá nhân** qua `/train`.
  3. **Bước nhận diện + đánh giá môi trường hiện tại** qua `/face/verify`.

- Kiểm tra môi trường gồm:
  - Độ sáng, độ mờ, kích thước khuôn mặt, số lượng khuôn mặt.
  - Môi trường kém → không lưu ảnh huấn luyện; khi nhận diện → hiển thị cảnh báo cho người dùng.  
