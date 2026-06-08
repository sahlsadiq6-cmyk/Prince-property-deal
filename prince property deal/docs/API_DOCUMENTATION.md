# Prince Property - API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
All protected endpoints require JWT token in header:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### 1. Sign Up
**POST** `/auth/signup`

Request:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

Response (201):
```json
{
  "message": "User registered successfully. Please check your email to verify.",
  "user_id": 1,
  "email": "john@example.com"
}
```

### 2. Login
**POST** `/auth/login`

Request:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

Response (200):
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "role": "user"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Verify Email
**GET** `/auth/verify-email/<token>`

Response (200):
```json
{
  "message": "Email verified successfully"
}
```

### 4. Forgot Password
**POST** `/auth/forgot-password`

Request:
```json
{
  "email": "john@example.com"
}
```

Response (200):
```json
{
  "message": "If email exists, password reset link has been sent"
}
```

### 5. Reset Password
**POST** `/auth/reset-password/<token>`

Request:
```json
{
  "password": "NewPassword123!"
}
```

Response (200):
```json
{
  "message": "Password reset successful"
}
```

### 6. Refresh Token
**POST** `/auth/refresh-token`

Request:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Response (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 7. Get Current User
**GET** `/auth/me`

*Requires Authentication*

Response (200):
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "bio": "Real estate enthusiast",
    "profile_picture": "https://...",
    "role": "user",
    "is_verified": true,
    "created_at": "2024-01-15T10:30:00",
    "last_login": "2024-01-20T15:45:00"
  }
}
```

---

## Property Endpoints

### 1. Get All Properties
**GET** `/properties`

Query Parameters:
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10)
- `city` (string): Filter by city
- `min_price` (float): Minimum price
- `max_price` (float): Maximum price
- `type` (string): Property type
- `bedrooms` (int): Number of bedrooms
- `status` (string): Property status

Example: `/properties?city=New York&min_price=100000&max_price=500000&page=1`

Response (200):
```json
{
  "data": [
    {
      "id": 1,
      "title": "Luxury Downtown Apartment",
      "description": "Beautiful 3-bedroom apartment...",
      "price": 250000,
      "property_type": "apartment",
      "bedrooms": 3,
      "bathrooms": 2,
      "square_feet": 1500,
      "address": "123 Main St",
      "city": "New York",
      "main_image": "https://...",
      "views": 1234
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 10,
    "total": 500,
    "pages": 50,
    "has_next": true,
    "has_prev": false
  }
}
```

### 2. Get Single Property
**GET** `/properties/<id>`

Response (200):
```json
{
  "data": {
    "id": 1,
    "title": "Luxury Downtown Apartment",
    "description": "Beautiful 3-bedroom apartment...",
    "price": 250000,
    "property_type": "apartment",
    "bedrooms": 3,
    "bathrooms": 2,
    "square_feet": 1500,
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "year_built": 2020,
    "condition": "excellent",
    "features": {
      "pool": true,
      "garage": true,
      "garden": false
    },
    "main_image": "https://...",
    "images": ["https://...", "https://..."],
    "views": 1234,
    "owner": {
      "id": 1,
      "name": "John Smith",
      "phone": "+1234567890",
      "email": "john@example.com"
    },
    "reviews": [
      {
        "id": 1,
        "rating": 5,
        "comment": "Great property!",
        "user": "Jane Doe",
        "created_at": "2024-01-15T10:30:00"
      }
    ],
    "average_rating": 4.8,
    "created_at": "2024-01-10T08:00:00"
  }
}
```

### 3. Create Property
**POST** `/properties`

*Requires Authentication*

Request:
```json
{
  "title": "Luxury Downtown Apartment",
  "description": "Beautiful 3-bedroom apartment...",
  "price": 250000,
  "property_type": "apartment",
  "bedrooms": 3,
  "bathrooms": 2,
  "square_feet": 1500,
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "year_built": 2020,
  "condition": "excellent",
  "features": {
    "pool": true,
    "garage": true
  },
  "images": ["https://...", "https://..."]
}
```

Response (201):
```json
{
  "message": "Property created successfully",
  "property_id": 123
}
```

### 4. Update Property
**PUT** `/properties/<id>`

*Requires Authentication & Ownership*

### 5. Delete Property
**DELETE** `/properties/<id>`

*Requires Authentication & Ownership*

### 6. Create Inquiry
**POST** `/properties/<id>/inquire`

Request:
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+1987654321",
  "message": "I'm interested in this property"
}
```

Response (201):
```json
{
  "message": "Inquiry submitted successfully",
  "inquiry_id": 45
}
```

### 7. Add Review
**POST** `/properties/<id>/review`

*Requires Authentication*

Request:
```json
{
  "rating": 5,
  "comment": "Excellent property and great agent!"
}
```

Response (201):
```json
{
  "message": "Review added successfully",
  "review_id": 78
}
```

---

## User Endpoints

### 1. Get User Profile
**GET** `/users/profile/<user_id>`

Response (200):
```json
{
  "data": {
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "bio": "Real estate enthusiast",
    "profile_picture": "https://...",
    "role": "user",
    "properties_count": 5,
    "member_since": "2024-01-10T08:00:00",
    "is_verified": true
  }
}
```

### 2. Update Profile
**PUT** `/users/profile`

*Requires Authentication*

Request:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "bio": "Real estate professional",
  "profile_picture": "https://..."
}
```

### 3. Get User Properties
**GET** `/users/properties`

*Requires Authentication*

### 4. Get User Public Properties
**GET** `/users/<user_id>/properties`

### 5. Change Password
**POST** `/users/change-password`

*Requires Authentication*

Request:
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!"
}
```

---

## Messaging Endpoints

### 1. Get Messages
**GET** `/messages`

*Requires Authentication*

### 2. Get Conversation
**GET** `/messages/conversation/<user_id>`

*Requires Authentication*

### 3. Send Message
**POST** `/messages/send/<receiver_id>`

*Requires Authentication*

Request:
```json
{
  "content": "Hello! I'm interested in your property."
}
```

### 4. Mark Message as Read
**PUT** `/messages/<message_id>/mark-read`

*Requires Authentication*

---

## Contact Endpoint

### Submit Contact Form
**POST** `/contact`

Request:
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+1987654321",
  "subject": "Property Inquiry",
  "message": "I would like more information about..."
}
```

Response (201):
```json
{
  "message": "Your message has been received. We will contact you soon.",
  "contact_id": 5
}
```

---

## Admin Endpoints

### 1. Get Dashboard
**GET** `/admin/dashboard`

*Requires Admin Authentication*

### 2. Get All Users
**GET** `/admin/users`

*Requires Admin Authentication*

### 3. Get Contacts
**GET** `/admin/contacts`

*Requires Admin Authentication*

### 4. Reply to Contact
**POST** `/admin/contacts/<contact_id>/reply`

*Requires Admin Authentication*

### 5. Get Inquiries
**GET** `/admin/inquiries`

*Requires Admin Authentication*

### 6. Get All Properties
**GET** `/admin/properties`

*Requires Admin Authentication*

### 7. Feature Property
**PUT** `/admin/properties/<property_id>/feature`

*Requires Admin Authentication*

Request:
```json
{
  "is_featured": true
}
```

---

## Error Responses

### Bad Request (400)
```json
{
  "message": "Missing required fields"
}
```

### Unauthorized (401)
```json
{
  "message": "Invalid or expired token"
}
```

### Forbidden (403)
```json
{
  "message": "Unauthorized access"
}
```

### Not Found (404)
```json
{
  "message": "Resource not found"
}
```

### Conflict (409)
```json
{
  "message": "Email already registered"
}
```

### Internal Server Error (500)
```json
{
  "message": "Internal server error"
}
```

---

## Rate Limiting

- Sign Up: 10 requests per hour
- Login: 5 requests per minute
- Contact Form: 5 requests per hour
- Property Review: 10 requests per day
- Forgot Password: 3 requests per hour

---

## Best Practices

1. Always validate input on client side before sending
2. Store tokens securely (use httpOnly cookies if possible)
3. Handle token expiration and refresh
4. Use HTTPS in production
5. Implement proper error handling
6. Cache responses when appropriate
7. Implement pagination for large datasets
8. Use query parameters for filtering
9. Follow RESTful principles
10. Document your API changes

---

For more information, visit: https://princeproperties.com/api-docs
