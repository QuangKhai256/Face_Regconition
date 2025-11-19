# Frontend Web – Streamlit  
## Thu thập khuôn mặt, huấn luyện và nhận diện + hiển thị cảnh báo môi trường

---

## 1. Vai trò frontend web

Frontend web dùng **Streamlit** để:

1. Thực hiện **bước thu thập khuôn mặt** trước:  
   - Cho phép upload ảnh hoặc chụp từ webcam.  
   - Gửi ảnh sang `/api/v1/collect`.  
   - Nếu môi trường không đạt (quá tối, mờ, mặt quá nhỏ, nhiều người) → backend trả lỗi kèm hướng dẫn → hiển thị cho người dùng.

2. Gọi **huấn luyện mô hình**:
   - Nút “Huấn luyện mô hình” → gọi `/api/v1/train`.

3. **Nhận diện khuôn mặt + kiểm tra môi trường**:
   - Gửi ảnh lên `/api/v1/face/verify`.  
   - Kết quả trả về gồm:
     - `is_match`, `message`, `distance`.  
     - `environment_info` (brightness, blur_score, face_size_ratio, warnings).  
   - Frontend hiển thị khung mặt màu **xanh/đỏ** và danh sách cảnh báo môi trường.

---

## 2. Giao diện & luồng chức năng

Giao diện chia thành **3 tab**:

1. **📥 Thu thập dữ liệu**
   - Upload ảnh / chụp webcam.
   - Gửi tới `/collect`.
   - Hiển thị:
     - Thông báo thành công.
     - Số lượng ảnh đã thu thập (`total_images`).
     - Thông tin `environment_info` nếu có.
   - Nếu backend trả lỗi (HTTP 400) do môi trường:
     - In ra thông báo chi tiết để user chỉnh ánh sáng, khoảng cách, v.v.

2. **🧠 Huấn luyện mô hình**
   - Nút “Bắt đầu huấn luyện” → gọi `/train`.
   - Hiển thị số ảnh và số embedding sử dụng.

3. **🔍 Nhận diện khuôn mặt**
   - Upload ảnh / chụp webcam.
   - Gửi tới `/face/verify` với `threshold` do user chỉnh.
   - Hiển thị:
     - Ảnh với bounding box xanh (match) hoặc đỏ (not match).
     - Thông điệp kết quả (`message`).
     - Giá trị `distance`, `threshold`.
     - Khối **“Cảnh báo môi trường”** liệt kê các `warnings` từ `environment_info`.

---

## 3. Kết nối API backend

```python
BACKEND_BASE_URL = "http://localhost:8000"
VERIFY_URL = f"{BACKEND_BASE_URL}/api/v1/face/verify"
COLLECT_URL = f"{BACKEND_BASE_URL}/api/v1/collect"
TRAIN_URL = f"{BACKEND_BASE_URL}/api/v1/train"
```

---

## 4. Mã nguồn `web/web_app.py`

```python
import cv2
import numpy as np
import requests
import streamlit as st

# =========================
# CẤU HÌNH BACKEND
# =========================
BACKEND_BASE_URL = "http://localhost:8000"
VERIFY_URL = f"{BACKEND_BASE_URL}/api/v1/face/verify"
COLLECT_URL = f"{BACKEND_BASE_URL}/api/v1/collect"
TRAIN_URL = f"{BACKEND_BASE_URL}/api/v1/train"


# =========================
# HÀM GỌI API BACKEND
# =========================
def call_collect_api(image_bytes: bytes):
    files = {"file": ("train.jpg", image_bytes, "image/jpeg")}
    try:
        resp = requests.post(COLLECT_URL, files=files, timeout=20)
    except requests.exceptions.RequestException as e:
        st.error(f"Không gọi được API /collect: {e}")
        return None, None

    if resp.status_code != 200:
        # Thường là lỗi môi trường hoặc lỗi dữ liệu
        try:
            data = resp.json()
            detail = data.get("detail", resp.text)
        except Exception:
            detail = resp.text
        st.error(f"Lỗi từ backend /collect ({resp.status_code}): {detail}")
        return None, detail

    return resp.json(), None


def call_train_api():
    try:
        resp = requests.post(TRAIN_URL, timeout=60)
    except requests.exceptions.RequestException as e:
        st.error(f"Không gọi được API /train: {e}")
        return None

    if resp.status_code != 200:
        try:
            data = resp.json()
            detail = data.get("detail", resp.text)
        except Exception:
            detail = resp.text
        st.error(f"Lỗi từ backend /train ({resp.status_code}): {detail}")
        return None

    return resp.json()


def call_verify_api(image_bytes: bytes, threshold: float):
    files = {"file": ("verify.jpg", image_bytes, "image/jpeg")}
    params = {"threshold": threshold}

    try:
        resp = requests.post(VERIFY_URL, files=files, params=params, timeout=20)
    except requests.exceptions.RequestException as e:
        st.error(f"Không gọi được API /face/verify: {e}")
        return None

    if resp.status_code != 200:
        try:
            data = resp.json()
            detail = data.get("detail", resp.text)
        except Exception:
            detail = resp.text
        st.error(f"Lỗi từ backend /face/verify ({resp.status_code}): {detail}")
        return None

    return resp.json()


# =========================
# HÀM XỬ LÝ ẢNH
# =========================
def draw_box(image_bgr: np.ndarray, face_box: dict, is_match: bool) -> np.ndarray:
    top = face_box.get("top", 0)
    right = face_box.get("right", 0)
    bottom = face_box.get("bottom", 0)
    left = face_box.get("left", 0)

    color = (0, 255, 0) if is_match else (0, 0, 255)
    label = "YOU" if is_match else "NOT YOU"

    cv2.rectangle(image_bgr, (left, top), (right, bottom), color, 2)
    cv2.putText(
        image_bgr,
        label,
        (left, max(top - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2,
        cv2.LINE_AA,
    )

    return image_bgr


def capture_frame_from_webcam() -> np.ndarray:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap.release()
        raise RuntimeError("Không mở được webcam. Hãy kiểm tra kết nối/quyền camera.")

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        raise RuntimeError("Không đọc được frame từ webcam.")

    return frame


# =========================
# GIAO DIỆN STREAMLIT
# =========================
def main():
    st.set_page_config(
        page_title="FaceID Web – Thu thập & Nhận diện với kiểm tra môi trường",
        page_icon="👤",
        layout="wide",
    )

    st.title("👤 FaceID Web – Thu thập & Nhận diện khuôn mặt (có kiểm tra môi trường)")

    with st.sidebar:
        st.header("⚙️ Cấu hình nhận diện")

        threshold = st.slider(
            "Ngưỡng (distance) để coi là cùng người",
            min_value=0.30,
            max_value=1.50,
            value=0.60,
            step=0.01,
        )
        st.markdown(
            f"- distance ≤ **{threshold:.2f}** ⇒ **KHUÔN MẶT CỦA BẠN**  \n"
            f"- distance > **{threshold:.2f}** ⇒ **KHÔNG KHỚP**"
        )

        st.info(
            "Nhớ chạy backend FastAPI trước: `uvicorn main:app --reload --port 8000`.\n"
            "Các tab bên dưới giúp bạn: thu thập dữ liệu → huấn luyện → nhận diện."
        )

    tab_collect, tab_train, tab_verify = st.tabs(
        ["📥 Thu thập dữ liệu", "🧠 Huấn luyện mô hình", "🔍 Nhận diện khuôn mặt"]
    )

    # -------------------------
    # TAB 1: THU THẬP DỮ LIỆU
    # -------------------------
    with tab_collect:
        st.subheader("📥 Thu thập dữ liệu HUẤN LUYỆN (khuôn mặt của bạn)")

        st.markdown(
            """
            Backend sẽ **kiểm tra môi trường xung quanh**:
            - Ảnh quá tối/ quá sáng  
            - Ảnh bị mờ  
            - Khuôn mặt quá nhỏ trong khung hình  
            - Có nhiều hơn 1 người  

            Nếu môi trường không đạt, ảnh sẽ **không được lưu** để tránh làm bẩn dữ liệu huấn luyện.
            """
        )

        col1, col2 = st.columns(2)

        # Upload ảnh
        with col1:
            st.markdown("**Cách 1: Upload ảnh từ máy**")
            upload_train = st.file_uploader(
                "Chọn ảnh khuôn mặt (.jpg/.jpeg/.png) để huấn luyện:",
                type=["jpg", "jpeg", "png"],
                key="train_upload",
            )
            if upload_train is not None:
                st.image(upload_train, caption="Ảnh tải lên (dùng để HUẤN LUYỆN)", use_column_width=True)
                if st.button("📥 Gửi ảnh này vào tập huấn luyện", key="btn_collect_upload"):
                    image_bytes = upload_train.read()
                    result, error = call_collect_api(image_bytes)
                    if result is not None:
                        st.success(result.get("message", "Đã thu thập ảnh."))
                        st.write(f"Số ảnh huấn luyện hiện có: {result.get('total_images', '?')}")

                        env = result.get("environment_info", {})
                        if env:
                            st.markdown("**Thông tin môi trường:**")
                            st.json(env)

        # Webcam
        with col2:
            st.markdown("**Cách 2: Chụp ảnh từ webcam**")
            if st.button("📸 Chụp & gửi ảnh từ webcam", key="btn_collect_webcam"):
                try:
                    frame_bgr = capture_frame_from_webcam()
                    st.image(
                        cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB),
                        caption="Ảnh chụp từ webcam (dùng cho HUẤN LUYỆN)",
                        use_column_width=True,
                    )
                    success, encoded_image = cv2.imencode(".jpg", frame_bgr)
                    if not success:
                        st.error("Không encode được ảnh từ webcam.")
                    else:
                        image_bytes = encoded_image.tobytes()
                        result, error = call_collect_api(image_bytes)
                        if result is not None:
                            st.success(result.get("message", "Đã thu thập ảnh."))
                            st.write(f"Số ảnh huấn luyện hiện có: {result.get('total_images', '?')}")
                            env = result.get("environment_info", {})
                            if env:
                                st.markdown("**Thông tin môi trường:**")
                                st.json(env)
                except RuntimeError as re:
                    st.error(f"Lỗi webcam: {re}")
                except Exception as e:
                    st.error(f"Lỗi không xác định khi thu thập từ webcam: {e}")

    # -------------------------
    # TAB 2: HUẤN LUYỆN MÔ HÌNH
    # -------------------------
    with tab_train:
        st.subheader("🧠 Huấn luyện mô hình khuôn mặt cá nhân")

        st.markdown(
            """
            Sau khi đã thu thập đủ **5–10 ảnh chất lượng tốt** (môi trường ok),  
            hãy nhấn nút bên dưới để **huấn luyện mô hình cá nhân** (tính embedding trung bình).
            """
        )

        if st.button("🧠 Bắt đầu HUẤN LUYỆN", key="btn_train_model"):
            result = call_train_api()
            if result is not None:
                st.success(result.get("message", "Huấn luyện thành công."))
                st.write(f"Số ảnh đọc được: {result.get('num_images', '?')}")
                st.write(f"Số embedding sử dụng: {result.get('num_embeddings', '?')}")

    # -------------------------
    # TAB 3: NHẬN DIỆN KHUÔN MẶT
    # -------------------------
    with tab_verify:
        st.subheader("🔍 Nhận diện khuôn mặt hiện tại (kèm kiểm tra môi trường)")

        st.markdown(
            """
            Bạn có thể:
            - Upload ảnh mới để kiểm tra.  
            - Hoặc chụp trực tiếp từ webcam.  

            Kết quả trả về gồm:
            - `is_match`, `message`, `distance`  
            - `environment_info` để biết ảnh có bị tối/mờ/mặt nhỏ không.
            """
        )

        col1, col2 = st.columns(2)

        # Nhận diện từ ảnh upload
        with col1:
            st.markdown("**Nhận diện từ ảnh upload**")
            uploaded_verify = st.file_uploader(
                "Chọn ảnh khuôn mặt (.jpg/.jpeg/.png) để nhận diện:",
                type=["jpg", "jpeg", "png"],
                key="verify_upload",
            )

            if uploaded_verify is not None:
                st.image(uploaded_verify, caption="Ảnh để nhận diện", use_column_width=True)
                if st.button("🔍 Nhận diện ảnh này", key="btn_verify_upload"):
                    image_bytes = uploaded_verify.read()
                    result = call_verify_api(image_bytes, threshold)
                    if result is not None:
                        is_match = result.get("is_match", False)
                        distance = result.get("distance", None)
                        message = result.get("message", "")
                        face_box = result.get("face_box", None)
                        env = result.get("environment_info", {})

                        nparr = np.frombuffer(image_bytes, np.uint8)
                        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if image_bgr is not None and face_box is not None:
                            image_bgr = draw_box(image_bgr, face_box, is_match)

                        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                        st.image(image_rgb, caption="Kết quả nhận diện", use_column_width=True)

                        if is_match:
                            st.success(message)
                        else:
                            st.warning(message)

                        if distance is not None:
                            st.markdown(f"- **distance:** `{distance:.4f}`")
                            st.markdown(f"- **threshold:** `{threshold:.4f}`")

                        if env:
                            st.markdown("### 🔎 Cảnh báo / Thông tin môi trường")
                            st.json(env)

        # Nhận diện từ webcam
        with col2:
            st.markdown("**Nhận diện từ webcam**")
            if st.button("🎥 Chụp & nhận diện từ webcam", key="btn_verify_webcam"):
                try:
                    frame_bgr = capture_frame_from_webcam()
                    st.image(
                        cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB),
                        caption="Ảnh chụp từ webcam (gốc)",
                        use_column_width=True,
                    )

                    success, encoded_image = cv2.imencode(".jpg", frame_bgr)
                    if not success:
                        st.error("Không encode được ảnh từ webcam.")
                    else:
                        image_bytes = encoded_image.tobytes()
                        result = call_verify_api(image_bytes, threshold)
                        if result is not None:
                            is_match = result.get("is_match", False)
                            distance = result.get("distance", None)
                            message = result.get("message", "")
                            face_box = result.get("face_box", None)
                            env = result.get("environment_info", {})

                            if face_box is not None:
                                frame_bgr = draw_box(frame_bgr, face_box, is_match)

                            st.image(
                                cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB),
                                caption="Kết quả nhận diện từ webcam",
                                use_column_width=True,
                            )

                            if is_match:
                                st.success(message)
                            else:
                                st.warning(message)

                            if distance is not None:
                                st.markdown(f"- **distance:** `{distance:.4f}`")
                                st.markdown(f"- **threshold:** `{threshold:.4f}`")

                            if env:
                                st.markdown("### 🔎 Cảnh báo / Thông tin môi trường")
                                st.json(env)
                except RuntimeError as re:
                    st.error(f"Lỗi webcam: {re}")
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi dùng webcam: {e}")


if __name__ == "__main__":
    main()
```

---

## 5. Cách chạy frontend web

```bash
cd web
streamlit run web_app.py
```

- Mặc định: `http://localhost:8501`
- Backend phải chạy ở: `http://localhost:8000`

---

## 6. Tóm tắt cho báo cáo

- Giao diện web **có BƯỚC THU THẬP dữ liệu khuôn mặt riêng**, không tự ý dùng ảnh có sẵn.
- Khi thu thập và nhận diện, frontend luôn hiển thị cảnh báo môi trường từ backend:
  - Độ sáng, độ mờ, kích thước mặt, v.v.
- Người dùng được hướng dẫn **điều chỉnh môi trường** để có dữ liệu & kết quả nhận diện tốt hơn.  
