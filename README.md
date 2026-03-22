<div align="center">

<img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
<img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase"/>
<img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render"/>

<br/><br/>

# 🏪 Smart Inventory & Billing System — Backend API

**A multi-tenant inventory and billing REST API built with FastAPI and Supabase PostgreSQL.**  
Each shop operates as an independent tenant with isolated data, role-based access control, and auto-triggered stock management.

<br/>

[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger%20UI-blue?style=flat-square&logo=swagger)](https://db-project-backend-2ull.onrender.com/docs)
[![Live API](https://img.shields.io/badge/Live%20API-Render-green?style=flat-square&logo=render)](https://db-project-backend-2ull.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Reference](#-api-reference)
- [DBMS Concepts](#-dbms-concepts-implemented)
- [Local Setup](#-local-setup)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment--render)
- [Error Handling](#-error-handling)
- [License](#-license)

---

## 🔍 Overview

The **Smart Multi-Tenant Inventory & Billing System** backend provides a complete REST API for retail shop management. Multiple shops can operate independently within a single hosted instance — each with its own admin, staff, inventory, and sales records.

### Key Capabilities

- 🔐 **JWT Authentication** with role-based access control (`admin` / `staff`)
- 🏢 **Multi-tenant isolation** enforced via Supabase Row-Level Security (RLS)
- 📦 **Full inventory CRUD** with indexed product search
- 🧾 **Billing engine** that auto-deducts stock via PostgreSQL database triggers
- 📊 **Analytics dashboard** powered by SQL joins and aggregations
- 🌐 **Public storefront** — customers browse inventory without logging in
- 📝 **Auto-generated docs** via Swagger UI at `/docs`

---

## 🛠 Tech Stack

| Layer | Technology |
|:---|:---|
| Framework | FastAPI (Python 3.10+) |
| ORM | SQLAlchemy |
| Database | Supabase PostgreSQL |
| Authentication | Supabase Auth + JWT |
| Password Hashing | bcrypt |
| ASGI Server | Uvicorn |
| Hosting | Render (free tier) |

---

## 📁 Project Structure

```
backend/
│
├── main.py                  # App entry point, CORS middleware, router registration
├── database.py              # SQLAlchemy engine and session factory
├── models.py                # ORM models — Shop, User, Product, Sale, SaleItem
├── schemas.py               # Pydantic request/response schemas
├── dependencies.py          # JWT validation, get_current_user, role guards
│
├── routers/
│   ├── auth_router.py       # Register, login, get profile, add staff
│   ├── shop_router.py       # Create shop, get shop, update details, logo upload
│   ├── inventory_router.py  # Product CRUD, search by name
│   ├── sales_router.py      # Create sale, list sales, get invoice
│   ├── dashboard_router.py  # Summary stats, daily sales, top products, low stock
│   └── public_router.py     # Public shop listing, public inventory view
│
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (not committed)
```

---

## 🗄 Database Schema

```
┌─────────────────────────────────────────────────────┐
│                        shops                        │
├──────────────┬──────────────────────────────────────┤
│ shop_id      │ UUID  PRIMARY KEY                    │
│ shop_name    │ VARCHAR                              │
│ category     │ VARCHAR                              │
│ logo         │ TEXT                                 │
│ show_price   │ BOOLEAN                              │
│ show_stock   │ BOOLEAN                              │
│ created_at   │ TIMESTAMP                            │
└──────────────┴──────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                        users                        │
├──────────────┬──────────────────────────────────────┤
│ user_id      │ UUID  PRIMARY KEY                    │
│ email        │ VARCHAR  UNIQUE                      │
│ password_hash│ TEXT                                 │
│ full_name    │ VARCHAR                              │
│ role         │ ENUM (admin, staff)                  │
│ shop_id      │ UUID  FK → shops                     │
└──────────────┴──────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                      products                       │
├──────────────┬──────────────────────────────────────┤
│ product_id   │ UUID  PRIMARY KEY                    │
│ shop_id      │ UUID  FK → shops                     │
│ product_name │ VARCHAR  (INDEXED)                   │
│ description  │ TEXT                                 │
│ price        │ DECIMAL                              │
│ quantity     │ INTEGER                              │
│ threshold    │ INTEGER                              │
└──────────────┴──────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                        sales                        │
├──────────────┬──────────────────────────────────────┤
│ sale_id      │ UUID  PRIMARY KEY                    │
│ shop_id      │ UUID  FK → shops                     │
│ staff_id     │ UUID  FK → users                     │
│ total_amount │ DECIMAL                              │
│ sale_date    │ TIMESTAMP                            │
└──────────────┴──────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                     sale_items                      │
├──────────────┬──────────────────────────────────────┤
│ sale_item_id │ UUID  PRIMARY KEY                    │
│ sale_id      │ UUID  FK → sales                     │
│ product_id   │ UUID  FK → products                  │
│ quantity     │ INTEGER                              │
│ subtotal     │ DECIMAL                              │
└──────────────┴──────────────────────────────────────┘
```

---

## 📡 API Reference

> **Base URL (Live):** `https://db-project-backend-2ull.onrender.com`  
> **Base URL (Local):** `http://localhost:8000`  
> **Interactive Docs:** `/docs` (Swagger UI)

### 🔑 Authentication — `/auth`

| Method | Endpoint | Description | Auth Required |
|:---:|:---|:---|:---:|
| `POST` | `/auth/register` | Register a new admin account | ❌ Public |
| `POST` | `/auth/login` | Login and receive JWT token | ❌ Public |
| `GET` | `/auth/me` | Get current user profile | ✅ Token |
| `POST` | `/auth/staff` | Create a staff cashier account | 🔒 Admin |
| `GET` | `/auth/staff` | List all staff for the shop | 🔒 Admin |

<details>
<summary><b>POST</b> /auth/register — Request Body</summary>

```json
{
  "email": "admin@myshop.com",
  "password": "securepassword123",
  "full_name": "Rajan Mathew"
}
```

</details>

<details>
<summary><b>POST</b> /auth/login — Response</summary>

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "a7c3e5f1-28b4-4d09-9e12-bc3a7d2f01aa",
    "email": "admin@myshop.com",
    "full_name": "Rajan Mathew",
    "role": "admin",
    "shop_id": null
  }
}
```

</details>

---

### 🏪 Shop Management — `/shops`

| Method | Endpoint | Description | Auth Required |
|:---:|:---|:---|:---:|
| `POST` | `/shops/` | Create a shop (one per admin) | 🔒 Admin |
| `GET` | `/shops/mine` | Get own shop details | ✅ Token |
| `GET` | `/shops/{shop_id}` | Get shop by ID | ✅ Token |
| `PUT` | `/shops/{shop_id}` | Update shop details | 🔒 Admin |
| `POST` | `/shops/logo` | Upload shop logo | 🔒 Admin |

<details>
<summary><b>POST</b> /shops/ — Request Body</summary>

```json
{
  "shop_name": "Kerala Electronics Hub",
  "category": "Electronics",
  "logo": "",
  "show_price": true,
  "show_stock": true
}
```

</details>

---

### 📦 Inventory — `/inventory`

| Method | Endpoint | Description | Auth Required |
|:---:|:---|:---|:---:|
| `GET` | `/inventory/` | List all products in the shop | ✅ Token |
| `POST` | `/inventory/` | Add a new product | 🔒 Admin |
| `GET` | `/inventory/search?q=` | Search products by name | ✅ Token |
| `GET` | `/inventory/{id}` | Get a single product | ✅ Token |
| `PUT` | `/inventory/{id}` | Update product details | 🔒 Admin |
| `DELETE` | `/inventory/{id}` | Delete a product | 🔒 Admin |

<details>
<summary><b>POST</b> /inventory/ — Request Body</summary>

```json
{
  "product_name": "Sony WH-1000XM5 Headphones",
  "description": "Wireless noise cancelling headphones",
  "price": 2499.00,
  "quantity": 30,
  "threshold": 5
}
```

</details>

---

### 🧾 Billing & Sales — `/sales`

| Method | Endpoint | Description | Auth Required |
|:---:|:---|:---|:---:|
| `POST` | `/sales/` | Record a sale — triggers stock deduction | ✅ Admin/Staff |
| `GET` | `/sales/` | List all sales for the shop | ✅ Token |
| `GET` | `/sales/{id}` | Get full invoice for a sale | ✅ Token |

<details>
<summary><b>POST</b> /sales/ — Request Body</summary>

```json
{
  "items": [
    { "product_id": "b91c3f2e-05a7-4d8b-83cc-f7a24d910e55", "quantity": 2 },
    { "product_id": "c04f7a9d-18b3-4e21-99d0-a3c85b14f722", "quantity": 1 }
  ]
}
```

> ⚡ Stock quantities are automatically reduced by a PostgreSQL **database trigger** the moment a sale item is inserted.

</details>

---

### 📊 Dashboard Analytics — `/dashboard`

| Method | Endpoint | Description | Auth Required |
|:---:|:---|:---|:---:|
| `GET` | `/dashboard/summary` | Revenue, sales count, product count, low-stock count | 🔒 Admin |
| `GET` | `/dashboard/daily-sales` | Sales grouped by day — last 30 days | 🔒 Admin |
| `GET` | `/dashboard/top-products` | Top 10 best-selling products | 🔒 Admin |
| `GET` | `/dashboard/low-stock` | Products below their threshold | 🔒 Admin |

<details>
<summary><b>GET</b> /dashboard/summary — Response</summary>

```json
{
  "total_revenue": 28450.75,
  "total_sales": 34,
  "total_products": 12,
  "low_stock_count": 2
}
```

</details>

---

### 🌐 Public Access — `/public`

| Method | Endpoint | Description | Auth Required |
|:---:|:---|:---|:---:|
| `GET` | `/public/shops` | List all registered shops | ❌ Public |
| `GET` | `/public/shop/{name}` | Get basic shop info by name | ❌ Public |
| `GET` | `/public/shop/{name}/inventory` | View shop's public inventory (supports `?q=` search) | ❌ Public |

---

## 🗃 DBMS Concepts Implemented

| Concept | Implementation |
|:---|:---|
| **Trigger** | Auto stock deduction on every `sale_items` insert |
| **Index** | `product_name` column indexed for fast search queries |
| **Foreign Keys** | All tables linked via `shop_id`, `sale_id`, `product_id` |
| **JOIN** | Dashboard analytics combine `sales`, `sale_items`, and `products` |
| **GROUP BY** | Daily sales and top product reports use aggregation |
| **Transactions** | Sale creation wraps multiple inserts in a single atomic transaction |
| **Normalization** | Database designed to Third Normal Form (3NF) |
| **Row-Level Security** | Supabase RLS policies enforce complete tenant data isolation |

---

## 🚀 Local Setup

### Prerequisites

- Python **3.10** or higher
- A [Supabase](https://supabase.com) project with PostgreSQL enabled
- Git

### 1. Clone the repository

```bash
git clone https://github.com/your-username/smart-inventory-backend.git
cd smart-inventory-backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root of the project:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SECRET_KEY=your-jwt-secret-key
```

> ⚠️ Use the **Session pooler** connection string (port **5432**) from Supabase → Settings → Database.  
> Avoid the Transaction pooler (port 6543) — it causes connection timeout errors with persistent FastAPI apps.

### 5. Start the development server

```bash
uvicorn main:app --reload
```

The API will be live at **`http://localhost:8000`**

Open **`http://localhost:8000/docs`** to explore the interactive Swagger UI.

---

## 🔧 Environment Variables

| Variable | Description |
|:---|:---|
| `DATABASE_URL` | PostgreSQL connection string from Supabase (Session pooler, port 5432) |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/public API key |
| `SECRET_KEY` | Secret key used for signing JWT tokens |

> 🔒 Never commit your `.env` file to version control. It is already listed in `.gitignore`.

---

## ☁️ Deployment — Render

### Steps

1. Push your code to a GitHub repository
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repository
4. Configure the service:

| Setting | Value |
|:---|:---|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port 10000` |
| **Environment** | Add all variables from the table above |

5. Click **Deploy**

### ⚠️ Important Notes

> **Cold Start Delay** — Render free tier servers sleep after 15 minutes of inactivity. The first request after a sleep period may take **30–90 seconds**. Use [UptimeRobot](https://uptimerobot.com) (free) to ping the server every 5 minutes and keep it awake.

> **Supabase Network Restrictions** — If you see `Connection timed out` errors on Render, go to Supabase → Settings → Database → **Network Restrictions** and allow all IPs (`0.0.0.0/0`), or switch to the Session pooler connection string (port 5432).

> **Paused Supabase Project** — Supabase free tier projects pause after 7 days of inactivity. Check your Supabase dashboard for a **Resume** button if the database suddenly becomes unreachable.

---

## ❗ Error Handling

All errors return a consistent JSON structure:

```json
{
  "detail": "Descriptive error message here"
}
```

| Code | Status | Meaning |
|:---:|:---|:---|
| `200` | OK | Request succeeded |
| `201` | Created | Resource successfully created |
| `204` | No Content | Deletion successful — no response body |
| `400` | Bad Request | Logic error — e.g. insufficient stock, shop already exists |
| `401` | Unauthorized | Token missing, expired, or invalid |
| `403` | Forbidden | Role does not have permission for this action |
| `404` | Not Found | Resource does not exist |
| `422` | Unprocessable Entity | Validation error — wrong field name or missing field |
| `500` | Internal Server Error | Unexpected server-side failure |

---

## 👥 User Roles

| Role | Access Level |
|:---|:---|
| **admin** | Full access — manage inventory, staff, analytics, and shop settings |
| **staff** | Billing only — create sales, search and view products |
| **customer** | Public read-only — browse shop inventory without an account |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License — Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies, subject to the condition that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

---

<div align="center">

**The entire backend is developed by Tharun Krishna C U**  
Department of Computer Science and Engineering

</div>
