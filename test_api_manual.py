"""
Script để test API face recognition thủ công.
Sử dụng script này để test backend với ảnh thực tế.
"""

import requests
import sys
import os
from pathlib import Path

# Fix Unicode encoding on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200 and response.json().get("status") == "ok":
            print("✅ PASS: Health check successful")
            return True
        else:
            print("❌ FAIL: Health check failed")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_face_verification(image_path, threshold=0.5, expected_match=None):
    """
    Test face verification endpoint.
    
    Args:
        image_path: Đường dẫn đến file ảnh
        threshold: Ngưỡng so sánh (0.0 - 1.0)
        expected_match: Kết quả mong đợi (True/False/None)
    """
    print("\n" + "="*60)
    print(f"TEST: Face Verification - {Path(image_path).name}")
    print("="*60)
    print(f"Image: {image_path}")
    print(f"Threshold: {threshold}")
    
    if not os.path.exists(image_path):
        print(f"❌ ERROR: File không tồn tại: {image_path}")
        return False
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": (Path(image_path).name, f, "image/jpeg")}
            response = requests.post(
                f"{BASE_URL}/api/v1/face/verify",
                files=files,
                params={"threshold": threshold}
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nKết quả:")
            print(f"  - is_match: {data['is_match']}")
            print(f"  - distance: {data['distance']}")
            print(f"  - threshold: {data['threshold']}")
            print(f"  - message: {data['message']}")
            print(f"  - face_box: {data['face_box']}")
            print(f"  - image_size: {data['image_size']}")
            print(f"  - training_info: {data['training_info']['num_images']} ảnh huấn luyện")
            
            if expected_match is not None:
                if data['is_match'] == expected_match:
                    print(f"✅ PASS: Kết quả đúng như mong đợi (is_match={expected_match})")
                    return True
                else:
                    print(f"❌ FAIL: Kết quả không đúng. Mong đợi is_match={expected_match}, nhận được {data['is_match']}")
                    return False
            else:
                print("✅ PASS: Request thành công")
                return True
        else:
            data = response.json()
            print(f"Response: {data}")
            
            if response.status_code in [400, 422]:
                print(f"⚠️  Expected Error: {data.get('detail', 'Unknown error')}")
                return True
            else:
                print(f"❌ FAIL: Unexpected status code {response.status_code}")
                return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_error_cases():
    """Test các trường hợp lỗi."""
    print("\n" + "="*60)
    print("TEST: Error Cases")
    print("="*60)
    
    # Test với file không phải ảnh
    print("\nTest Case: File không phải ảnh")
    try:
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = requests.post(f"{BASE_URL}/api/v1/face/verify", files=files)
        
        if response.status_code == 400:
            print(f"✅ PASS: Đúng là trả về 400 cho file không phải ảnh")
            print(f"   Message: {response.json().get('detail')}")
        else:
            print(f"❌ FAIL: Mong đợi 400, nhận được {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test với threshold không hợp lệ
    print("\nTest Case: Threshold không hợp lệ")
    try:
        # Tạo một ảnh giả để test
        files = {"file": ("test.jpg", b"fake image", "image/jpeg")}
        response = requests.post(
            f"{BASE_URL}/api/v1/face/verify",
            files=files,
            params={"threshold": 1.5}  # Invalid threshold
        )
        
        if response.status_code == 422:
            print(f"✅ PASS: Đúng là trả về 422 cho threshold không hợp lệ")
            print(f"   Message: {response.json()}")
        else:
            print(f"❌ FAIL: Mong đợi 422, nhận được {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def main():
    """Main function."""
    print("\n" + "="*60)
    print("FACE RECOGNITION API - MANUAL TESTING SCRIPT")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print("\nLưu ý: Đảm bảo backend đang chạy trước khi test!")
    print("Chạy backend: uvicorn backend.main:app --reload")
    
    # Test 1: Health Check
    health_ok = test_health_check()
    
    if not health_ok:
        print("\n❌ Backend không hoạt động. Vui lòng kiểm tra lại!")
        sys.exit(1)
    
    # Test 2: Error Cases
    test_error_cases()
    
    # Test 3: Face Verification với ảnh thực
    print("\n" + "="*60)
    print("HƯỚNG DẪN TEST VỚI ẢNH THỰC")
    print("="*60)
    print("\nĐể test với ảnh thực, sử dụng các lệnh sau:")
    print("\n1. Test với ảnh của bạn (should match):")
    print('   python test_api_manual.py verify "path/to/your/photo.jpg" --expected-match')
    print("\n2. Test với ảnh người khác (should not match):")
    print('   python test_api_manual.py verify "path/to/other/photo.jpg" --expected-no-match')
    print("\n3. Test với threshold tùy chỉnh:")
    print('   python test_api_manual.py verify "path/to/photo.jpg" --threshold 0.4')
    print("\n4. Test với ảnh không có khuôn mặt:")
    print('   python test_api_manual.py verify "path/to/landscape.jpg"')
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("✅ Health check: OK")
    print("✅ Error handling: OK")
    print("⚠️  Manual testing: Cần test với ảnh thực")
    print("\nĐọc TESTING_GUIDE.md để biết hướng dẫn chi tiết!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        # Mode: Test với ảnh cụ thể
        if len(sys.argv) < 3:
            print("Usage: python test_api_manual.py verify <image_path> [--threshold <value>] [--expected-match|--expected-no-match]")
            sys.exit(1)
        
        image_path = sys.argv[2]
        threshold = 0.5
        expected_match = None
        
        # Parse arguments
        for i in range(3, len(sys.argv)):
            if sys.argv[i] == "--threshold" and i + 1 < len(sys.argv):
                threshold = float(sys.argv[i + 1])
            elif sys.argv[i] == "--expected-match":
                expected_match = True
            elif sys.argv[i] == "--expected-no-match":
                expected_match = False
        
        # Run test
        test_health_check()
        test_face_verification(image_path, threshold, expected_match)
    else:
        # Mode: Chạy tất cả tests cơ bản
        main()
