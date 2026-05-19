# Web Bán Hàng Áo Quần

Ứng dụng web bán hàng thời trang được xây dựng bằng Python Flask, với các chức năng:

- Trang chủ hiển thị sản phẩm và sản phẩm nổi bật
- Tìm kiếm theo tên, danh mục hoặc mô tả
- Trang chi tiết sản phẩm với đánh giá
- Giỏ hàng và thanh toán mẫu
- Đăng ký / đăng nhập người dùng
- Quản trị sản phẩm (thêm, sửa, xóa) cho admin
- Cơ sở dữ liệu SQLite tự động khởi tạo

## Cài đặt

1. Tạo môi trường ảo Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Nếu muốn dùng MySQL / phpMyAdmin

- Tạo database mới, ví dụ `fashion_shop`
- Tạo user MySQL hoặc dùng `root`
- Trong phpMyAdmin, import bảng bằng file `schema_mysql.sql` nếu cần
- Hoặc dùng lệnh SQL:
  - `CREATE DATABASE fashion_shop;`
  - `USE fashion_shop;`

3. Cấu hình kết nối MySQL

Trên Windows PowerShell:

```powershell
$env:DB_TYPE='mysql'
$env:MYSQL_HOST='127.0.0.1'
$env:MYSQL_PORT='3306'
$env:MYSQL_USER='root'
$env:MYSQL_PASSWORD='yourpassword'
$env:MYSQL_DB='fashion_shop'
python app.py
```

4. Chạy ứng dụng khi dùng SQLite

```powershell
python app.py
```

5. Mở trình duyệt tại `http://127.0.0.1:5000`

## Tài khoản admin mẫu

- Email: `admin@shop.com`
- Mật khẩu: `admin123`

## Lưu ý

- Thay đổi `SECRET_KEY` trong `app.py` khi triển khai thật
- Ảnh hiển thị sử dụng URL Unsplash cho demo

## Kết nối MySQL / phpMyAdmin

Bạn có thể dùng phpMyAdmin để quản lý database MySQL và kết nối với project này.

1. Cài MySQL và phpMyAdmin, sau đó tạo database mới (ví dụ `fashion_shop`).
2. Trong phpMyAdmin, chọn database `fashion_shop` và import file `create_database_fashion_shop.sql` từ thư mục dự án.
3. Tạo user MySQL và cấp quyền cho database `fashion_shop`.
4. Thiết lập các biến môi trường như sau (trên PowerShell):

```powershell
$env:DB_TYPE = 'mysql'
$env:MYSQL_HOST = '127.0.0.1'
$env:MYSQL_PORT = '3306'
$env:MYSQL_USER = 'your_mysql_user'
$env:MYSQL_PASSWORD = 'your_mysql_password'
$env:MYSQL_DB = 'fashion_shop'
python app.py
```

5. Mở `http://127.0.0.1:5000` để sử dụng ứng dụng với MySQL.

> Nếu bạn không dùng phpMyAdmin, vẫn có thể dùng SQLite mặc định bằng cách chạy `python app.py` mà không cần thiết lập biến môi trường MySQL.
