# Backend API Requirement Document

**Base URL:** `https://db-project-backend-2ull.onrender.com`

This document outlines the API endpoints, request/response formats, and authentication requirements for the Smart Multi-Tenant Inventory & Billing System.

---

## 1. General Information

### Authentication
Most endpoints require a **Bearer JWT Token** in the `Authorization` header.
- **Header:** `Authorization: Bearer <your_jwt_token>`
- **Public Endpoints:** `/auth/login`, `/auth/register`, `/public/*`, and `/` do not require authentication.

### Error Response Format
All errors follow a standard format with a detail message and a relevant HTTP status code.

```json
{
  "detail": "Error message description"
}
```

**Common Status Codes:**
- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `204 No Content`: Successful deletion.
- `400 Bad Request`: Client-side error (e.g., missing shop, insufficient stock).
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: User does not have sufficient permissions (e.g., staff trying to delete product).
- `404 Not Found`: Resource not found.
- `422 Unprocessable Entity`: Validation error in request body or parameters.
- `500 Internal Server Error`: Server-side error.

---

## 2. Authentication Module

### Register Admin
Register a new admin user and create a local database record.
- **URL:** `/auth/register`
- **Method:** `POST`
- **Request Body:**
```json
{
  "email": "admin@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```
- **Response (201 Created):**
```json
{
  "user_id": "uuid-string",
  "email": "admin@example.com",
  "full_name": "John Doe",
  "role": "admin",
  "shop_id": null,
  "shop_name": null,
  "created_at": "ISODateTime"
}
```

### Login
Login via Supabase Auth and receive a JWT token.
- **URL:** `/auth/login`
- **Method:** `POST`
- **Request Body:**
```json
{
  "email": "admin@example.com",
  "password": "securepassword123"
}
```
- **Response (200 OK):**
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "user_id": "uuid",
    "email": "admin@example.com",
    "full_name": "John Doe",
    "role": "admin",
    "shop_id": "uuid-or-null",
    "shop_name": "Shop Name"
  }
}
```

### Get Current User Profile
- **URL:** `/auth/me`
- **Method:** `GET`
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** `UserResponse` object.

### Add Staff (Admin Only)
- **URL:** `/auth/staff`
- **Method:** `POST`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
```json
{
  "email": "staff@example.com",
  "password": "staffpassword",
  "full_name": "Jane Staff"
}
```

---

## 3. Shop Management Module

### Create Shop (Admin Only)
- **URL:** `/shops/`
- **Method:** `POST`
- **Request Body:**
```json
{
  "shop_name": "My Great Shop",
  "category": "Retail",
  "logo": "url_to_logo",
  "show_price": true,
  "show_stock": true
}
```

### Get My Shop
- **URL:** `/shops/mine`
- **Method:** `GET`
- **Response (200 OK):** `ShopResponse` object.

### Upload Shop Logo
- **URL:** `/shops/logo`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Body:** `file` (binary)

---

## 4. Inventory Management Module

### List Products
- **URL:** `/inventory/`
- **Method:** `GET`
- **Response (200 OK):** Array of `ProductResponse` objects.

### Add Product
- **URL:** `/inventory/`
- **Method:** `POST`
- **Request Body:**
```json
{
  "product_name": "New Smartphone",
  "description": "Latest model",
  "price": 999.99,
  "quantity": 50,
  "threshold": 5
}
```

### Search Products
- **URL:** `/inventory/search`
- **Method:** `GET`
- **Query Params:** `q=search_term`

### Update/Delete Product
- **URL:** `/inventory/{product_id}`
- **Methods:** `PUT`, `DELETE`

---

## 5. Billing & Sales Module

### Create Sale
- **URL:** `/sales/`
- **Method:** `POST`
- **Description:** Records a sale and automatically reduces stock via DB triggers.
- **Request Body:**
```json
{
  "items": [
    {
      "product_id": "uuid-1",
      "quantity": 2
    },
    {
      "product_id": "uuid-2",
      "quantity": 1
    }
  ]
}
```

### List Sales / Get Sale Invoice
- **URL:** `/sales/` (List all) or `/sales/{sale_id}` (Single invoice)
- **Method:** `GET`

---

## 6. Dashboard Analytics

### Summary Stats
- **URL:** `/dashboard/summary`
- **Method:** `GET`
- **Response:** `{ total_revenue, total_sales, total_products, low_stock_count }`

### Daily Sales (Last 30 Days)
- **URL:** `/dashboard/daily-sales`
- **Method:** `GET`

### Top Selling Products
- **URL:** `/dashboard/top-products`
- **Method:** `GET`

---

## 7. Public Endpoints (Customers/Visitors)

### List All Registered Shops
- **URL:** `/public/shops`
- **Method:** `GET`

### Get Shop Public Inventory
- **URL:** `/public/shop/{shop_name}/inventory`
- **Method:** `GET`
- **Query Params:** `q` (optional search)

---

## Postman Collection Tips
1. **Environment Variables**: Set `baseUrl` and `token`.
2. **Authorization**: Use "Bearer Token" type in Postman and reference `{{token}}`.
3. **JSON Body**: Ensure `Content-Type: application/json` is set for POST/PUT requests.
