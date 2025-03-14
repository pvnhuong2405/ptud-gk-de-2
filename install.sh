#!/bin/bash

# Kiểm tra xem môi trường ảo đã tồn tại chưa
if [ -d "ptud" ]; then
  echo "Môi trường ảo đã tồn tại. Bỏ qua bước tạo mới."
else
  echo "Đang tạo môi trường ảo..."
  python3 -m venv ptud
fi

# Kích hoạt môi trường ảo
echo "Đang kích hoạt môi trường ảo..."
source ptud/bin/activate

# Kiểm tra xem tệp requirements.txt có tồn tại không
if [ -f "requirements.txt" ]; then
  echo "Đang cài đặt các gói phụ thuộc..."
  pip install -r requirements.txt
else
  echo "Tệp requirements.txt không tìm thấy. Vui lòng chắc chắn rằng tệp này có trong thư mục."
  exit 1
fi

# Thiết lập cơ sở dữ liệu
echo "Đang thiết lập cơ sở dữ liệu..."
flask init-db

# Chạy ứng dụng Flask
echo "Đang chạy ứng dụng Flask..."
flask run

# In ra hướng dẫn truy cập ứng dụng và tài khoản admin mặc định
echo "Ứng dụng đã chạy tại http://127.0.0.1:5000"
echo "Tài khoản Admin mặc định:"
echo "- Email: pvnhuong2405@gmail.com"
echo "- Mật khẩu: admin123"
