# DINEOPS API - Testing Guide & Examples

## Overview
This guide provides curl commands and examples for testing the DINEOPS API endpoints.

## Prerequisites
- Server running: `python manage.py runserver`
- Base URL: `http://localhost:8000`

---

## 1. Health Check

### Check Server Status
```bash
curl -X GET http://localhost:8000/health/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:00:00Z"
}
```

---

## 2. User Authentication

### Register New User
```bash
curl -X POST http://localhost:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePassword123!"
  }'
```

**Expected Response (201 Created):**
```json
{
  "status": true,
  "code": 201,
  "msg": "Registration successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "email": "newuser@example.com",
      "is_staff": false
    }
  }
}
```

### Login User
```bash
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "john_doe",
    "password": "password123"
  }'
```

**Alternative: Login with Email**
```bash
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "john@example.com",
    "password": "password123"
  }'
```

**Expected Response (200 OK):**
```json
{
  "status": true,
  "code": 200,
  "msg": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "email": "john@example.com",
      "user_name": "john_doe",
      "is_staff": true
    }
  }
}
```

**Error Response - Invalid Credentials (401 Unauthorized):**
```json
{
  "status": false,
  "code": 401,
  "msg": "Username or password is incorrect",
  "errors": {
    "detail": "Username or password is incorrect"
  }
}
```

**Error Response - Account Locked (403 Forbidden):**
```json
{
  "status": false,
  "code": 403,
  "msg": "Account locked due to too many failed login attempts",
  "errors": {
    "detail": "Account locked due to too many failed login attempts"
  }
}
```

### Get User Profile (Authenticated)
```bash
# Replace YOUR_TOKEN with the actual access token from login response
curl -X GET http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "status": true,
  "code": 200,
  "msg": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "john@example.com",
    "is_staff": true,
    "is_active": true,
    "created_at": "2026-01-12T10:00:00Z"
  }
}
```

**Error Response - No Token (401 Unauthorized):**
```json
{
  "status": false,
  "code": 401,
  "msg": "Authentication credentials were not provided.",
  "errors": {
    "detail": "Authentication credentials were not provided."
  }
}
```

### Logout User
```bash
curl -X POST http://localhost:8000/api/v1/users/logout/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "status": true,
  "code": 200,
  "msg": "Logout successful"
}
```

---

## 3. Staff Management

### List Roles
```bash
curl -X GET http://localhost:8000/api/v1/staff/roles/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "status": true,
  "code": 200,
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Manager",
        "permissions": ["view_order", "create_order"]
      },
      {
        "id": 2,
        "name": "Waiter",
        "permissions": ["view_order"]
      }
    ]
  }
}
```

### Create Role
```bash
curl -X POST http://localhost:8000/api/v1/staff/roles/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chef",
    "permissions": ["view_order", "update_order"]
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": 3,
  "name": "Chef",
  "permissions": ["view_order", "update_order"]
}
```

---

## 4. Menu Management

### List Menu Items
```bash
curl -X GET http://localhost:8000/api/v1/menu/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "status": true,
  "code": 200,
  "data": {
    "count": 10,
    "next": "http://localhost:8000/api/v1/menu/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Margherita Pizza",
        "category": 1,
        "description": "Classic pizza with tomato, mozzarella, and basil",
        "is_active": true,
        "created_at": "2026-01-12T10:00:00Z"
      }
    ]
  }
}
```

### Create Menu Item
```bash
curl -X POST http://localhost:8000/api/v1/menu/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Caesar Salad",
    "category": 2,
    "description": "Fresh lettuce with parmesan and croutons",
    "is_active": true
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": 11,
  "name": "Caesar Salad",
  "category": 2,
  "description": "Fresh lettuce with parmesan and croutons",
  "is_active": true,
  "created_at": "2026-01-12T10:05:00Z"
}
```

### Retrieve Menu Item
```bash
curl -X GET http://localhost:8000/api/v1/menu/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "name": "Margherita Pizza",
  "category": 1,
  "description": "Classic pizza with tomato, mozzarella, and basil",
  "is_active": true,
  "variants": [
    {
      "id": 1,
      "size": "Small",
      "price": 8.99
    },
    {
      "id": 2,
      "size": "Large",
      "price": 14.99
    }
  ],
  "created_at": "2026-01-12T10:00:00Z"
}
```

### Update Menu Item
```bash
curl -X PUT http://localhost:8000/api/v1/menu/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Margherita Pizza Updated",
    "description": "Classic pizza with fresh ingredients",
    "is_active": true
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "name": "Margherita Pizza Updated",
  "category": 1,
  "description": "Classic pizza with fresh ingredients",
  "is_active": true,
  "created_at": "2026-01-12T10:00:00Z"
}
```

### Delete Menu Item
```bash
curl -X DELETE http://localhost:8000/api/v1/menu/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (204 No Content)**

---

## 5. Order Management

### List Orders
```bash
curl -X GET http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "status": true,
  "code": 200,
  "data": {
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "table": 5,
        "status": "pending",
        "total": 45.99,
        "items_count": 3,
        "created_at": "2026-01-12T10:00:00Z"
      }
    ]
  }
}
```

### Create Order
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "table": 5,
    "items": [
      {
        "product": 1,
        "quantity": 2,
        "variant": 2
      },
      {
        "product": 3,
        "quantity": 1,
        "toppings": [1, 2]
      }
    ]
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": 6,
  "table": 5,
  "status": "pending",
  "total": 45.99,
  "items": [
    {
      "id": 1,
      "product": 1,
      "quantity": 2,
      "variant": 2,
      "price": 14.99
    }
  ],
  "created_at": "2026-01-12T10:05:00Z"
}
```

### Get Order Details
```bash
curl -X GET http://localhost:8000/api/v1/orders/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "table": 5,
  "status": "pending",
  "total": 45.99,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Margherita Pizza"
      },
      "quantity": 2,
      "variant": {
        "id": 2,
        "size": "Large",
        "price": 14.99
      },
      "toppings": []
    }
  ],
  "created_at": "2026-01-12T10:00:00Z",
  "updated_at": "2026-01-12T10:15:00Z"
}
```

### Update Order Status
```bash
curl -X PATCH http://localhost:8000/api/v1/orders/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "table": 5,
  "status": "completed",
  "total": 45.99,
  "updated_at": "2026-01-12T10:20:00Z"
}
```

### Cancel Order
```bash
curl -X DELETE http://localhost:8000/api/v1/orders/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (204 No Content)**

---

## 6. Table Management

### List Tables
```bash
curl -X GET http://localhost:8000/api/v1/tables/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "table_number": 1,
      "capacity": 4,
      "status": "available",
      "location": "Main Hall"
    },
    {
      "id": 5,
      "table_number": 5,
      "capacity": 2,
      "status": "occupied",
      "location": "Outdoor Patio"
    }
  ]
}
```

---

## 7. Common HTTP Status Codes

### Success Responses
- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **204 No Content** - Request successful, no content to return

### Client Error Responses
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **429 Too Many Requests** - Rate limit exceeded

### Server Error Responses
- **500 Internal Server Error** - Server error
- **502 Bad Gateway** - Gateway error
- **503 Service Unavailable** - Service temporarily unavailable

---

## 8. Authentication Token Management

### How to Get a Token
```bash
# Login to get token
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "john_doe",
    "password": "password123"
  }' | jq '.data.access_token'
```

### How to Use Token
```bash
# Save token to variable
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"user_name":"john_doe","password":"password123"}' | jq -r '.data.access_token')

# Use token in requests
curl -X GET http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer $TOKEN"
```

### Token Lifetime
- **Access Token:** 8 hours (configurable)
- **Refresh Token:** None (stateless authentication)
- **Note:** Once token expires, user must login again

---

## 9. Error Handling Examples

### Invalid Credentials
```bash
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "john_doe",
    "password": "wrongpassword"
  }'
```

**Response (401 Unauthorized):**
```json
{
  "status": false,
  "code": 401,
  "errors": {
    "detail": "Username or password is incorrect"
  }
}
```

### Missing Authentication
```bash
curl -X GET http://localhost:8000/api/v1/users/profile/
```

**Response (401 Unauthorized):**
```json
{
  "status": false,
  "code": 401,
  "errors": {
    "detail": "Authentication credentials were not provided."
  }
}
```

### Invalid Token
```bash
curl -X GET http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer invalid_token_here"
```

**Response (401 Unauthorized):**
```json
{
  "status": false,
  "code": 401,
  "errors": {
    "detail": "Invalid token."
  }
}
```

### Resource Not Found
```bash
curl -X GET http://localhost:8000/api/v1/orders/99999/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (404 Not Found):**
```json
{
  "status": false,
  "code": 404,
  "errors": {
    "detail": "Not found."
  }
}
```

---

## 10. Testing with Postman

### Import Collection
1. Download Postman
2. Create new collection "DINEOPS API"
3. Add requests as shown above
4. Set environment variables:
   - `base_url`: http://localhost:8000
   - `token`: Your JWT token

### Environment Setup
```json
{
  "base_url": "http://localhost:8000",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Pre-request Script
```javascript
// Auto-refresh token if needed
if (pm.environment.get("token_expires") < new Date()) {
    // Request new token
}
```

---

## 11. Rate Limiting

### Account Lockout Rules
- **Max Failed Attempts:** 5
- **Lockout Duration:** 300 seconds (5 minutes)
- **Reset:** Automatic after lockout period or on successful login

### Login Attempt Tracking
```bash
# Attempt 1
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"user_name":"john","password":"wrong"}'

# After 5 failed attempts, account is locked
# Response after 5 attempts:
# "Account locked due to too many failed login attempts"
```

---

## 12. Performance Testing

### Load Testing with Apache Bench
```bash
# Install: apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health/

# Test with authentication
ab -n 100 -c 5 -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/orders/
```

### Load Testing with Locust
```bash
# Install: pip install locust

# Create locustfile.py
# Run: locust -f locustfile.py --host=http://localhost:8000
```

---

## Support

For API issues or questions:
1. Check endpoint documentation
2. Verify authentication token
3. Review response status codes
4. Check server logs
5. Contact development team

---

**Last Updated:** January 12, 2026  
**API Version:** v1  
**Status:** Ready for Testing

