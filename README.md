
# ATTT
# Chạy backend
1. clone dự án 
2. chạy tải thư viện :composer install
3. tạo file .env

# Database Config
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=kt2
DB_USER=root
DB_PASS=

# JWT Config
JWT_SECRET=KiemTra2Web_DAB8F19C23E4A56B78C90D12E34F56G7
JWT_EXPIRATION=3600

4. tạo database tên : kt2
tạo 2 bảng:

CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `role` VARCHAR(20) DEFAULT 'user'
);

5. chạy backend: php -S localhost:8000 -t public

