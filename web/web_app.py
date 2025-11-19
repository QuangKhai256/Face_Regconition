"""
Streamlit Web Application for Face Recognition System
Frontend web interface for collecting, training, and verifying faces
"""

import streamlit as st
import requests
import cv2
import numpy as np
from typing import Dict, Optional, Tuple
import io
from PIL import Image

# Backend URL configuration
BACKEND_URL = "http://localhost:8000"


# ============================================================================
# API Client Functions
# ============================================================================

def call_collect_api(image_bytes: bytes) -> Dict:
    """
    Gọi API thu thập dữ liệu khuôn mặt.
    
    Args:
        image_bytes: Dữ liệu ảnh dạng bytes
        
    Returns:
        Dict: Response JSON từ API
        
    Raises:
        requests.exceptions.RequestException: Lỗi khi gọi API
        
    Validates: Requirements 5.3
    """
    try:
        # Tạo multipart form data
        files = {
            'file': ('image.jpg', image_bytes, 'image/jpeg')
        }
        
        # Gọi POST /api/v1/collect
        response = requests.post(
            f"{BACKEND_URL}/api/v1/collect",
            files=files,
            timeout=30
        )
        
        # Parse JSON response
        response_data = response.json()
        
        # Kiểm tra status code
        if response.status_code == 200:
            return {
                'success': True,
                'data': response_data
            }
        else:
            # Xử lý lỗi từ backend
            error_detail = response_data.get('detail', 'Lỗi không xác định')
            return {
                'success': False,
                'error': error_detail,
                'status_code': response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Lỗi kết nối đến backend: {str(e)}",
            'status_code': None
        }


def call_train_api() -> Dict:
    """
    Gọi API huấn luyện mô hình.
    
    Returns:
        Dict: Response JSON từ API
        
    Raises:
        requests.exceptions.RequestException: Lỗi khi gọi API
        
    Validates: Requirements 5.5
    """
    try:
        # Gọi POST /api/v1/train
        response = requests.post(
            f"{BACKEND_URL}/api/v1/train",
            timeout=60  # Training có thể mất nhiều thời gian hơn
        )
        
        # Parse JSON response
        response_data = response.json()
        
        # Kiểm tra status code
        if response.status_code == 200:
            return {
                'success': True,
                'data': response_data
            }
        else:
            # Xử lý lỗi từ backend
            error_detail = response_data.get('detail', 'Lỗi không xác định')
            return {
                'success': False,
                'error': error_detail,
                'status_code': response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Lỗi kết nối đến backend: {str(e)}",
            'status_code': None
        }


def call_verify_api(image_bytes: bytes, threshold: float) -> Dict:
    """
    Gọi API nhận diện khuôn mặt.
    
    Args:
        image_bytes: Dữ liệu ảnh dạng bytes
        threshold: Ngưỡng so sánh (0.0 - 1.0)
        
    Returns:
        Dict: Response JSON từ API
        
    Raises:
        requests.exceptions.RequestException: Lỗi khi gọi API
        
    Validates: Requirements 5.7
    """
    try:
        # Tạo multipart form data
        files = {
            'file': ('image.jpg', image_bytes, 'image/jpeg')
        }
        
        # Tạo query parameters
        params = {
            'threshold': threshold
        }
        
        # Gọi POST /api/v1/face/verify
        response = requests.post(
            f"{BACKEND_URL}/api/v1/face/verify",
            files=files,
            params=params,
            timeout=30
        )
        
        # Parse JSON response
        response_data = response.json()
        
        # Kiểm tra status code
        if response.status_code == 200:
            return {
                'success': True,
                'data': response_data
            }
        else:
            # Xử lý lỗi từ backend
            error_detail = response_data.get('detail', 'Lỗi không xác định')
            return {
                'success': False,
                'error': error_detail,
                'status_code': response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Lỗi kết nối đến backend: {str(e)}",
            'status_code': None
        }


# ============================================================================
# Image Processing Functions
# ============================================================================

def draw_box(image_bgr: np.ndarray, face_box: Dict, is_match: bool) -> np.ndarray:
    """
    Vẽ bounding box lên ảnh.
    
    Args:
        image_bgr: Ảnh BGR từ OpenCV
        face_box: Dictionary chứa top, right, bottom, left
        is_match: True nếu khớp (màu xanh), False nếu không khớp (màu đỏ)
        
    Returns:
        np.ndarray: Ảnh đã vẽ bounding box
        
    Validates: Requirements 5.8
    """
    # Copy ảnh để không thay đổi ảnh gốc
    image_with_box = image_bgr.copy()
    
    # Lấy tọa độ
    top = face_box['top']
    right = face_box['right']
    bottom = face_box['bottom']
    left = face_box['left']
    
    # Chọn màu: xanh lá nếu khớp, đỏ nếu không khớp
    # OpenCV sử dụng BGR format
    if is_match:
        color = (0, 255, 0)  # Xanh lá (Green)
        label = "MATCH"
    else:
        color = (0, 0, 255)  # Đỏ (Red)
        label = "NO MATCH"
    
    # Vẽ rectangle
    cv2.rectangle(
        image_with_box,
        (left, top),
        (right, bottom),
        color,
        2  # Độ dày của đường viền
    )
    
    # Vẽ label
    # Tạo background cho text
    cv2.rectangle(
        image_with_box,
        (left, top - 30),
        (right, top),
        color,
        -1  # Fill
    )
    
    # Vẽ text
    cv2.putText(
        image_with_box,
        label,
        (left + 6, top - 6),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),  # Màu trắng
        2
    )
    
    return image_with_box


def capture_frame_from_webcam() -> Optional[np.ndarray]:
    """
    Chụp một frame từ webcam.
    
    Returns:
        Optional[np.ndarray]: Ảnh BGR từ webcam, hoặc None nếu lỗi
        
    Validates: Requirements 5.8
    """
    try:
        # Mở webcam (device 0)
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("Không thể mở webcam. Vui lòng kiểm tra kết nối.")
            return None
        
        # Đọc một frame
        ret, frame = cap.read()
        
        # Giải phóng webcam
        cap.release()
        
        if not ret:
            st.error("Không thể đọc frame từ webcam.")
            return None
        
        return frame
        
    except Exception as e:
        st.error(f"Lỗi khi chụp từ webcam: {str(e)}")
        return None


# ============================================================================
# Helper Functions
# ============================================================================

def convert_pil_to_bytes(pil_image: Image.Image) -> bytes:
    """
    Chuyển đổi PIL Image thành bytes.
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        bytes: Dữ liệu ảnh dạng bytes (JPEG format)
    """
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr.read()


def convert_bgr_to_rgb(image_bgr: np.ndarray) -> np.ndarray:
    """
    Chuyển đổi ảnh từ BGR sang RGB.
    
    Args:
        image_bgr: Ảnh BGR từ OpenCV
        
    Returns:
        np.ndarray: Ảnh RGB
    """
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)


def display_environment_info(env_info: Dict):
    """
    Hiển thị thông tin môi trường.
    
    Args:
        env_info: Dictionary chứa thông tin môi trường
    """
    st.subheader("📊 Thông tin môi trường")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Độ sáng", f"{env_info['brightness']:.1f}")
        if env_info['is_too_dark']:
            st.warning("⚠️ Quá tối")
        elif env_info['is_too_bright']:
            st.warning("⚠️ Quá sáng")
        else:
            st.success("✅ Tốt")
    
    with col2:
        st.metric("Độ mờ", f"{env_info['blur_score']:.1f}")
        if env_info['is_too_blurry']:
            st.warning("⚠️ Quá mờ")
        else:
            st.success("✅ Tốt")
    
    with col3:
        st.metric("Tỷ lệ khuôn mặt", f"{env_info['face_size_ratio']:.2%}")
        if env_info['is_face_too_small']:
            st.warning("⚠️ Quá nhỏ")
        else:
            st.success("✅ Tốt")
    
    # Hiển thị warnings nếu có
    if env_info['warnings']:
        st.warning("**Cảnh báo:**")
        for warning in env_info['warnings']:
            st.write(f"- {warning}")


# ============================================================================
# Main Application
# ============================================================================

def main():
    """
    Main function for Streamlit web application.
    """
    # Cấu hình trang
    st.set_page_config(
        page_title="Face Recognition System",
        page_icon="👤",
        layout="wide"
    )
    
    st.title("👤 Hệ thống Nhận diện Khuôn mặt")
    st.markdown("---")
    
    # Tạo tabs
    tab1, tab2, tab3 = st.tabs([
        "📸 Thu thập dữ liệu",
        "🎓 Huấn luyện mô hình",
        "🔍 Nhận diện khuôn mặt"
    ])
    
    # Tab 1: Thu thập dữ liệu
    with tab1:
        st.header("📸 Thu thập dữ liệu khuôn mặt")
        st.write("Upload ảnh hoặc chụp từ webcam để thu thập dữ liệu huấn luyện.")
        
        # Chọn phương thức
        method = st.radio(
            "Chọn phương thức:",
            ["Upload ảnh từ máy", "Chụp từ webcam"],
            key="collect_method"
        )
        
        image_bytes = None
        
        if method == "Upload ảnh từ máy":
            uploaded_file = st.file_uploader(
                "Chọn ảnh khuôn mặt",
                type=['jpg', 'jpeg', 'png'],
                key="collect_upload"
            )
            
            if uploaded_file is not None:
                image_bytes = uploaded_file.read()
                st.image(image_bytes, caption="Ảnh đã chọn", use_column_width=True)
        
        else:  # Chụp từ webcam
            if st.button("📷 Chụp ảnh từ webcam", key="collect_capture"):
                with st.spinner("Đang chụp ảnh..."):
                    frame = capture_frame_from_webcam()
                    
                    if frame is not None:
                        # Chuyển BGR sang RGB để hiển thị
                        frame_rgb = convert_bgr_to_rgb(frame)
                        st.image(frame_rgb, caption="Ảnh đã chụp", use_column_width=True)
                        
                        # Chuyển thành bytes
                        _, buffer = cv2.imencode('.jpg', frame)
                        image_bytes = buffer.tobytes()
        
        # Nút gửi
        if image_bytes is not None:
            if st.button("✅ Gửi ảnh để thu thập", key="collect_submit"):
                with st.spinner("Đang xử lý..."):
                    result = call_collect_api(image_bytes)
                    
                    if result['success']:
                        data = result['data']
                        st.success(data['message'])
                        
                        # Hiển thị thông tin
                        st.info(f"📁 Đường dẫn: {data['saved_path']}")
                        st.info(f"📊 Tổng số ảnh đã thu thập: {data['total_images']}")
                        
                        # Hiển thị environment info
                        display_environment_info(data['environment_info'])
                    else:
                        st.error(f"❌ Lỗi: {result['error']}")
                        
                        # Nếu có environment_info trong error detail
                        if isinstance(result['error'], dict) and 'environment_info' in result['error']:
                            display_environment_info(result['error']['environment_info'])
    
    # Tab 2: Huấn luyện mô hình
    with tab2:
        st.header("🎓 Huấn luyện mô hình")
        st.write("Huấn luyện mô hình nhận diện từ các ảnh đã thu thập.")
        
        st.info("💡 Đảm bảo bạn đã thu thập ít nhất 5-10 ảnh khuôn mặt trước khi huấn luyện.")
        
        if st.button("🚀 Bắt đầu huấn luyện", key="train_button"):
            with st.spinner("Đang huấn luyện mô hình... Vui lòng đợi."):
                result = call_train_api()
                
                if result['success']:
                    data = result['data']
                    st.success(data['message'])
                    
                    # Hiển thị thông tin
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Số ảnh đã đọc", data['num_images'])
                    with col2:
                        st.metric("Số embeddings đã sử dụng", data['num_embeddings'])
                    
                    st.balloons()
                else:
                    st.error(f"❌ Lỗi: {result['error']}")
    
    # Tab 3: Nhận diện khuôn mặt
    with tab3:
        st.header("🔍 Nhận diện khuôn mặt")
        st.write("Upload ảnh hoặc chụp từ webcam để nhận diện khuôn mặt.")
        
        # Threshold slider
        threshold = st.slider(
            "Ngưỡng so sánh (threshold)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Ngưỡng càng thấp thì yêu cầu càng chặt chẽ"
        )
        
        # Chọn phương thức
        method = st.radio(
            "Chọn phương thức:",
            ["Upload ảnh từ máy", "Chụp từ webcam"],
            key="verify_method"
        )
        
        image_bytes = None
        original_image = None
        
        if method == "Upload ảnh từ máy":
            uploaded_file = st.file_uploader(
                "Chọn ảnh khuôn mặt",
                type=['jpg', 'jpeg', 'png'],
                key="verify_upload"
            )
            
            if uploaded_file is not None:
                image_bytes = uploaded_file.read()
                original_image = Image.open(io.BytesIO(image_bytes))
                st.image(image_bytes, caption="Ảnh đã chọn", use_column_width=True)
        
        else:  # Chụp từ webcam
            if st.button("📷 Chụp ảnh từ webcam", key="verify_capture"):
                with st.spinner("Đang chụp ảnh..."):
                    frame = capture_frame_from_webcam()
                    
                    if frame is not None:
                        # Chuyển BGR sang RGB để hiển thị
                        frame_rgb = convert_bgr_to_rgb(frame)
                        st.image(frame_rgb, caption="Ảnh đã chụp", use_column_width=True)
                        
                        # Chuyển thành bytes
                        _, buffer = cv2.imencode('.jpg', frame)
                        image_bytes = buffer.tobytes()
                        
                        # Lưu original image
                        original_image = Image.fromarray(frame_rgb)
        
        # Nút nhận diện
        if image_bytes is not None:
            if st.button("🔍 Nhận diện khuôn mặt", key="verify_submit"):
                with st.spinner("Đang nhận diện..."):
                    result = call_verify_api(image_bytes, threshold)
                    
                    if result['success']:
                        data = result['data']
                        
                        # Hiển thị kết quả
                        if data['is_match']:
                            st.success(f"✅ {data['message']}")
                        else:
                            st.error(f"❌ {data['message']}")
                        
                        # Hiển thị metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Khoảng cách", f"{data['distance']:.3f}")
                        with col2:
                            st.metric("Ngưỡng", f"{data['threshold']:.3f}")
                        
                        # Vẽ bounding box lên ảnh
                        if original_image is not None:
                            # Chuyển PIL sang BGR
                            image_bgr = cv2.cvtColor(
                                np.array(original_image),
                                cv2.COLOR_RGB2BGR
                            )
                            
                            # Vẽ box
                            image_with_box = draw_box(
                                image_bgr,
                                data['face_box'],
                                data['is_match']
                            )
                            
                            # Chuyển BGR sang RGB để hiển thị
                            image_with_box_rgb = convert_bgr_to_rgb(image_with_box)
                            
                            st.image(
                                image_with_box_rgb,
                                caption="Kết quả nhận diện",
                                use_column_width=True
                            )
                        
                        # Hiển thị environment info
                        display_environment_info(data['environment_info'])
                        
                    else:
                        st.error(f"❌ Lỗi: {result['error']}")


if __name__ == "__main__":
    main()
