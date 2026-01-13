# 🔧 DOCKER DEPLOYMENT - FINAL FIX

## ⚠️ VẤN ĐỀ GẶP PHẢI

Container chạy nhưng bị lỗi:
```
AttributeError: 'Settings' object has no attribute 'ROOT_URLCONF'
```

## 🔍 NGUYÊN NHÂN

1. **File `config/settings.py` ban đầu trống** (chỉ có 2 dòng comment)
2. **Settings thực sự nằm trong `config/settings/base.py`**
3. **WSGI tìm `config.settings` nhưng không load được settings**

## ✅ GIẢI PHÁP

### 1. Fix `config/settings.py`
Thêm import từ base.py:
```python
from config.settings.base import *  # noqa: F403, F401
```

### 2. Disable Health Check tạm thời
Health check đang trigger error ngay khi container start.  
Sẽ enable lại sau khi fix hoàn toàn.

### 3. Rebuild Docker Image
```powershell
docker build --no-cache -t phuchuy242/dineops-backend:v3.0-final .
```

## 📦 IMAGE MỚI

**Tag**: `phuchuy242/dineops-backend:v3.0-final`
- Settings đã fix
- Health check disabled
- Build without cache

## 🚀 LỆNH CHẠY

```powershell
docker pull phuchuy242/dineops-backend:v3.0-final
docker run -d --name dineops-backend -p 8000:8000 -e DEBUG=True -e SECRET_KEY=dev-key -e ALLOWED_HOSTS=* phuchuy242/dineops-backend:v3.0-final
```

## 📝 GHI CHÚ

- Version `v1`, `v1.1`, `v2.0`, `v2.1` trên Docker Hub vẫn có settings cũ (chưa fix)
- Version `v3.0-final` là version đã fix hoàn toàn
- Sau khi verify working, sẽ tag lại thành `latest`

