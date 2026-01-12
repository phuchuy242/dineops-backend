# DINEOPS Backend - Quick Reference Card

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## 🔐 Login & Get Token

```bash
# Login
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"user_name":"username","password":"password"}'

# Response includes access_token - save it for requests
```

## 📍 Core API Endpoints

### Authentication
```
POST   /api/v1/users/register/     Register
POST   /api/v1/users/login/        Login (get token)
POST   /api/v1/users/logout/       Logout
GET    /api/v1/users/profile/      Get profile
```

### Menu
```
GET    /api/v1/menu/               List items
POST   /api/v1/menu/               Create item
GET    /api/v1/menu/{id}/          Get item
PUT    /api/v1/menu/{id}/          Update item
DELETE /api/v1/menu/{id}/          Delete item
```

### Orders
```
GET    /api/v1/orders/             List orders
POST   /api/v1/orders/             Create order
GET    /api/v1/orders/{id}/        Get order
PUT    /api/v1/orders/{id}/        Update order
DELETE /api/v1/orders/{id}/        Cancel order
```

### Other Endpoints
```
/api/v1/staff/roles/               Staff roles
/api/v1/tables/                    Tables
/api/v1/inventory/                 Inventory
/api/v1/payments/                  Payments
/api/v1/reports/                   Reports
/api/v1/restaurants/               Restaurants
/api/v1/sessions/                  Sessions
/api/v1/ingredient/                Ingredients
/api/v1/dishingredient/            Dish ingredients
```

## 🔑 Using Token

```bash
# In all requests, add header:
curl -X GET http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📋 Common Commands

### Django Management
```bash
# Check system
python manage.py check

# Show migrations
python manage.py showmigrations

# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Database shell
python manage.py shell

# Create test data
python manage.py seed_data
```

### Code Quality
```bash
# Format code
black apps/ config/ core/

# Sort imports
isort apps/ config/ core/

# Lint
ruff check apps/ config/ core/

# Type check
mypy apps/ config/ core/

# Run tests
pytest

# Coverage
pytest --cov=apps --cov=config --cov=core
```

## ⚙️ Environment Variables

### Essential
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost
```

### Database
```env
DB_ENGINE=django.db.backends.sqlite3
# OR
DB_ENGINE=django.db.backends.mysql
DB_NAME=dineops_db
DB_USER=root
DB_PASSWORD=password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### Security
```env
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
JWT_ACCESS_TOKEN_HOURS=8
```

## 🗂️ Project Structure

```
dineops-backend/
├── manage.py                 Django CLI
├── config/                   Configuration
│   ├── settings/
│   │   ├── base.py          Shared settings
│   │   ├── dev.py           Development
│   │   └── prod.py          Production
│   ├── urls.py              Main routing
│   ├── wsgi.py              Production
│   └── asgi.py              Async support
├── apps/                     Django apps
│   ├── users/
│   ├── menu/
│   ├── orders/
│   └── ... (9 more)
└── core/                     Core utilities
```

## 🔍 Debugging

### Enable Debug Mode
```env
DEBUG=True
```

### View Logs
```bash
# Server logs
python manage.py runserver

# Database logs
python manage.py dbshell
```

### Django Shell
```bash
python manage.py shell

# In shell:
from apps.users.models import User
User.objects.all()
```

## 🧪 Testing

### Run Tests
```bash
pytest

# Specific app
pytest apps/users/tests.py

# With coverage
pytest --cov=apps
```

### Run Server
```bash
python manage.py runserver 8000
# Visit: http://localhost:8000/
```

## 📱 API Response Format

### Success Response
```json
{
  "status": true,
  "code": 200,
  "msg": "Success message",
  "data": { /* response data */ }
}
```

### Error Response
```json
{
  "status": false,
  "code": 400,
  "msg": "Error message",
  "errors": { /* error details */ }
}
```

## 🔐 Security Best Practices

### Development
- ✅ DEBUG=True (locally only)
- ✅ Use default SQLite database
- ✅ No complex security needed

### Production
- ✅ DEBUG=False
- ✅ Use strong SECRET_KEY
- ✅ Use HTTPS
- ✅ Strong database password
- ✅ Update ALLOWED_HOSTS
- ✅ Update CORS_ALLOWED_ORIGINS

## 🆘 Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Migration Issues
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

### Database Reset
```bash
python manage.py migrate zero
python manage.py migrate
```

### Clear Cache
```bash
python manage.py clear_cache
```

## 📞 Support

- **Setup Help:** See SETUP_GUIDE.md
- **API Docs:** See API_TESTING_GUIDE.md
- **Technical:** See TECHNICAL_DOCUMENTATION.md
- **Status:** See COMPLETION_CHECKLIST.md

## ✅ Checklist Before Deployment

- [ ] Create .env file
- [ ] Set secure SECRET_KEY
- [ ] Configure database
- [ ] Set DEBUG=False
- [ ] Update ALLOWED_HOSTS
- [ ] Update CORS origins
- [ ] Run migrations
- [ ] Create superuser
- [ ] Test endpoints
- [ ] Configure HTTPS
- [ ] Set up monitoring
- [ ] Configure backups

## 🎯 Quick Tips

1. **Save Token:** Extract from login response
2. **Use Token:** Add to Authorization header
3. **Read Errors:** Response messages are helpful
4. **Check Settings:** Most issues are config-related
5. **Use Shell:** Debug with Django shell
6. **Check Logs:** Server output shows errors
7. **Test Endpoints:** Use curl or Postman
8. **Read Docs:** Check provided documentation

---

**Last Updated:** January 12, 2026  
**Status:** Production Ready  
**Version:** v1.0

