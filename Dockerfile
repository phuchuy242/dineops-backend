# ===========================
# STAGE 1: Build dependencies
# ===========================
FROM python:3.11-slim as builder

# Metadata
LABEL maintainer="DineOps Team"
LABEL description="DineOps Backend API - Django REST Framework"

# Set environment variables để tránh tạo .pyc files và buffer output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies cần thiết cho mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create và set working directory
WORKDIR /app

# Copy requirements để tận dụng Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===========================
# STAGE 2: Runtime
# ===========================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install chỉ runtime dependencies (không cần build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Tạo user non-root để tăng security
RUN useradd -m -u 1000 dineops && \
    mkdir -p /app && \
    chown -R dineops:dineops /app

WORKDIR /app

# Copy Python packages từ builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY --chown=dineops:dineops . .

# Tạo thư mục cho static files và media
RUN mkdir -p /app/staticfiles /app/mediafiles && \
    chown -R dineops:dineops /app/staticfiles /app/mediafiles

# Switch sang non-root user
USER dineops

# Expose port 8000
EXPOSE 8000

# Health check (disabled temporarily - uncomment when /health/ endpoint is fixed)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
#     CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=5)" || exit 1

# Entrypoint script để run migrations và start server
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120"]

