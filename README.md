🧠 Backend – CMS Order Online

Backend của dự án CMS Order Online được xây dựng bằng Django & Django REST Framework, cung cấp các API RESTful phục vụ cho hệ thống quản lý nhà hàng.

🎯 Mục tiêu

Quản lý người dùng, nhân viên, bàn, menu, đơn hàng và thanh toán

Thiết kế API chuẩn REST, dễ tích hợp với frontend/mobile

Cấu trúc module hoá, dễ nâng cấp và bảo trì

🛠 Công nghệ sử dụng

Python, Django

Django REST Framework

JWT Authentication

PostgreSQL / SQLite (tuỳ môi trường)

dotenv cho quản lý biến môi trường

🏗 Kiến trúc

Mỗi chức năng là một app độc lập (orders, menu, inventory, …)

Tách biệt rõ:

Business logic

API layer

Permissions & audit

Chuẩn hoá URL theo /api/<module>/

📦 Chức năng chính

Quản lý người dùng & phân quyền

Quản lý bàn & phiên phục vụ

Quản lý menu & tồn kho

Tạo và xử lý đơn hàng

Thanh toán & báo cáo

🔧 Môi trường

Development: requirements-dev.txt

Production: requirements.txt
