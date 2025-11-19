"""
Script kiểm tra nhanh hệ thống Face Recognition
Kiểm tra Backend, Web dependencies, và Mobile setup
"""

import sys
import subprocess

def check_module(module_name, display_name=None):
    """Kiểm tra xem module có được cài đặt không"""
    if display_name is None:
        display_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {display_name} - OK")
        return True
    except ImportError:
        print(f"❌ {display_name} - CHƯA CÀI ĐẶT")
        return False

def check_backend():
    """Kiểm tra Backend dependencies"""
    print("\n" + "="*50)
    print("KIỂM TRA BACKEND")
    print("="*50)
    
    modules = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("face_recognition", "Face Recognition"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("pydantic", "Pydantic"),
    ]
    
    all_ok = True
    for module, name in modules:
        if not check_module(module, name):
            all_ok = False
    
    if all_ok:
        print("\n✅ Backend dependencies: OK")
        print("Chạy backend: uvicorn backend.main:app --reload")
    else:
        print("\n❌ Thiếu dependencies. Cài đặt:")
        print("pip install -r requirements.txt")
    
    return all_ok

def check_web():
    """Kiểm tra Web App dependencies"""
    print("\n" + "="*50)
    print("KIỂM TRA WEB APP")
    print("="*50)
    
    modules = [
        ("streamlit", "Streamlit"),
        ("requests", "Requests"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
    ]
    
    all_ok = True
    for module, name in modules:
        if not check_module(module, name):
            all_ok = False
    
    if all_ok:
        print("\n✅ Web App dependencies: OK")
        print("Chạy web app: streamlit run web/web_app.py")
    else:
        print("\n❌ Thiếu dependencies. Cài đặt:")
        print("pip install streamlit requests opencv-python pillow")
    
    return all_ok

def check_mobile():
    """Kiểm tra Mobile App setup"""
    print("\n" + "="*50)
    print("KIỂM TRA MOBILE APP")
    print("="*50)
    
    try:
        result = subprocess.run(
            ["flutter", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Flutter - OK")
            print(f"Version: {result.stdout.split()[1]}")
            
            # Kiểm tra flutter doctor
            print("\nChạy flutter doctor...")
            doctor_result = subprocess.run(
                ["flutter", "doctor"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "No issues found" in doctor_result.stdout or "[√]" in doctor_result.stdout:
                print("✅ Flutter setup: OK")
                print("\nChạy mobile app:")
                print("cd mobile")
                print("flutter pub get")
                print("flutter run")
                return True
            else:
                print("⚠️ Flutter có một số vấn đề:")
                print(doctor_result.stdout)
                return False
        else:
            print("❌ Flutter - CHƯA CÀI ĐẶT")
            print("Cài đặt Flutter: https://flutter.dev/docs/get-started/install")
            return False
            
    except FileNotFoundError:
        print("❌ Flutter - CHƯA CÀI ĐẶT")
        print("Cài đặt Flutter: https://flutter.dev/docs/get-started/install")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️ Flutter command timeout")
        return False

def check_backend_running():
    """Kiểm tra xem Backend có đang chạy không"""
    print("\n" + "="*50)
    print("KIỂM TRA BACKEND ĐANG CHẠY")
    print("="*50)
    
    try:
        import requests
        response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
        
        if response.status_code == 200:
            print("✅ Backend đang chạy tại http://localhost:8000")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"⚠️ Backend phản hồi với status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend KHÔNG chạy")
        print("Khởi động backend: uvicorn backend.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print("⚠️ Backend timeout")
        return False
    except ImportError:
        print("⚠️ Không thể kiểm tra (thiếu module requests)")
        return False

def main():
    """Main function"""
    print("="*50)
    print("KIỂM TRA HỆ THỐNG FACE RECOGNITION")
    print("="*50)
    
    # Kiểm tra các thành phần
    backend_ok = check_backend()
    web_ok = check_web()
    mobile_ok = check_mobile()
    backend_running = check_backend_running()
    
    # Tổng kết
    print("\n" + "="*50)
    print("TỔNG KẾT")
    print("="*50)
    
    print(f"\n{'✅' if backend_ok else '❌'} Backend Dependencies")
    print(f"{'✅' if web_ok else '❌'} Web App Dependencies")
    print(f"{'✅' if mobile_ok else '❌'} Mobile App Setup")
    print(f"{'✅' if backend_running else '❌'} Backend Running")
    
    if backend_ok and web_ok and mobile_ok:
        print("\n🎉 TẤT CẢ THÀNH PHẦN ĐÃ SẴN SÀNG!")
        print("\nHướng dẫn chạy:")
        print("1. Backend: uvicorn backend.main:app --reload")
        print("2. Web App: streamlit run web/web_app.py")
        print("3. Mobile: cd mobile && flutter run")
        print("\nXem chi tiết: TESTING_COMPLETE_SYSTEM.md")
    else:
        print("\n⚠️ MỘT SỐ THÀNH PHẦN CHƯA SẴN SÀNG")
        print("Vui lòng cài đặt các dependencies còn thiếu")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
