# DINEOPS Backend - Setup & Configuration Guide

## Quick Start

### 1. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Environment Configuration
Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# Database Configuration (SQLite for development)
DB_ENGINE=django.db.backends.sqlite3
# OR MySQL
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=dineops_db
# DB_USER=root
# DB_PASSWORD=your_password
# DB_HOST=127.0.0.1
# DB_PORT=3306

# Security
ALLOWED_HOSTS=127.0.0.1,localhost

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# JWT Configuration
JWT_ACCESS_TOKEN_HOURS=8

# Login Security
LOGIN_MAX_ATTEMPTS=5
LOGIN_LOCKOUT_SECONDS=300
```

### 3. Database Setup
```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`

## API Endpoints

### Authentication
- **POST** `/api/v1/users/register/` - Register new user
- **POST** `/api/v1/users/login/` - Login and get JWT token
- **POST** `/api/v1/users/logout/` - Logout
- **GET** `/api/v1/users/profile/` - Get user profile (requires auth)

### Admin
- **GET/POST** `/admin/` - Django admin panel

### Health Check
- **GET** `/health/` - Health check endpoint

## Authentication

### Login
```bash
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "your_username",
    "password": "your_password"
  }'
```

Response:
```json
{
  "status": true,
  "code": 200,
  "msg": "Login successful",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "user_name": "username",
      "is_staff": false
    }
  }
}
```

### Using JWT Token
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/v1/users/profile/
```

## Development Workflow

### Code Quality
```bash
# Format code with Black
black apps/ config/ core/

# Sort imports with isort
isort apps/ config/ core/

# Lint with ruff
ruff check apps/ config/ core/

# Type checking with mypy
mypy apps/ config/ core/
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov=config --cov=core

# Run specific app tests
pytest apps/users/tests.py
```

### Database Migrations
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration plan
python manage.py migrate --plan

# Check migration status
python manage.py showmigrations
```

## Project Structure

```
dineops-backend/
├── manage.py                 # Django management script
├── config/                   # Project configuration
│   ├── settings/
│   │   ├── base.py          # Base settings
│   │   ├── dev.py           # Development settings
│   │   ├── prod.py          # Production settings
│   │   └── local.py         # Local overrides (optional)
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI application
│   ├── asgi.py              # ASGI application
│   └── health.py            # Health check endpoint
├── apps/                     # Django applications
│   ├── users/               # User authentication
│   ├── menu/                # Menu & products
│   ├── orders/              # Order management
│   ├── staff/               # Staff management
│   ├── tables/              # Table management
│   ├── inventory/           # Inventory management
│   ├── payments/            # Payment processing
│   ├── reports/             # Reporting
│   ├── restaurants/         # Restaurant config
│   ├── sessions/            # Session management
│   ├── ingredient/          # Ingredient management
│   └── dishingredient/      # Dish ingredients
├── core/                     # Core utilities
│   ├── exceptions.py        # Custom exceptions
│   ├── responses.py         # Response formatting
│   ├── middleware.py        # Custom middleware
│   ├── mixins.py            # Mixins for views
│   └── fields.py            # Custom fields
├── requirements.txt         # Production dependencies
└── requirements-dev.txt     # Development dependencies
```

## Security Best Practices

### Production Deployment
1. **Generate secure SECRET_KEY**
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **Set DEBUG=False** in production

3. **Use HTTPS** - Set SECURE_SSL_REDIRECT=True

4. **Configure ALLOWED_HOSTS** with your domain

5. **Update CORS settings** for your frontend domain

6. **Use strong database password** for MySQL/PostgreSQL

7. **Enable HSTS** for production (automatic when DEBUG=False)

### Development Notes
- Default settings are optimized for local development
- All security features are disabled when DEBUG=True
- Use `.env` file for sensitive configuration
- Never commit sensitive data to version control

## Troubleshooting

### ModuleNotFoundError
If you get import errors, ensure:
1. Virtual environment is activated
2. Dependencies are installed: `pip install -r requirements.txt`
3. PYTHONPATH includes project root

### Database Errors
If database connection fails:
1. Check `.env` configuration
2. Verify database server is running
3. Check database credentials
4. Run migrations: `python manage.py migrate`

### Port Already in Use
If port 8000 is busy:
```bash
python manage.py runserver 8001
```

### Migration Conflicts
If migration conflicts occur:
1. Check migration status: `python manage.py showmigrations`
2. Reset database if in development: `python manage.py migrate zero`
3. Apply migrations: `python manage.py migrate`

## Support

For issues or questions, refer to:
- Django Documentation: https://docs.djangoproject.com/
- DRF Documentation: https://www.django-rest-framework.org/
- Simple JWT: https://github.com/jpadilla/django-rest-framework-simplejwt/

