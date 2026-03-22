# Smart Multi-Tenant Inventory & Billing System - API Documentation

This documentation provides details on how to set up and run the system locally, along with a comprehensive reference of all available API endpoints.

---

## 1. Local Setup Guide

### 1.1 Backend Setup (FastAPI)
The backend is built with FastAPI and uses SQLAlchemy with a PostgreSQL database (hosted on Supabase).

**Prerequisites:**
- Python 3.10 or higher
- A Supabase project (for Auth and Database)

**Steps:**
1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure environment variables:**
    Create a `.env` file in the `backend/` folder with the following content:
    ```env
    SUPABASE_URL=your_supabase_project_url
    SUPABASE_ANON_KEY=your_supabase_anon_key
    SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
    DATABASE_URL=postgresql://postgres:password@db.your_project.supabase.co:5432/postgres
    ```
5.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

### 1.2 Frontend Setup (Next.js)
The frontend is built with Next.js and Tailwind CSS.

**Prerequisites:**
- Node.js 18 or higher
- npm or yarn

**Steps:**
1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Configure environment variables:**
    Create a `.env.local` file in the `frontend/` folder:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```
4.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:3000`.

---

## 2. Application Flow

The system follows a multi-tenant architecture where each **Admin** manages one **Shop**. **Staff** are associated with a specific shop.

1.  **Onboarding**: Admin registers (`POST /auth/register`) -> Logs in (`POST /auth/login`) -> Creates a Shop (`POST /shops/`).
2.  **Team Management**: Admin adds Staff members (`POST /auth/staff`).
3.  **Inventory Setup**: Admin or Staff adds products to the inventory (`POST /inventory/`).
4.  **Sales Operations**: Staff records sales (`POST /sales/`). Stock is automatically reduced via database triggers.
5.  **Analytics**: Admin monitors performance via the Dashboard (`GET /dashboard/summary`).
6.  **Public Access**: Customers can view a shop's public inventory without logging in (`GET /public/shop/{shop_name}/inventory`).

---

## 3. API Reference

### 3.1 Authentication (`/auth`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new Admin user. | No |
| `POST` | `/auth/login` | Login and receive a JWT token. | No |
| `GET` | `/auth/me` | Get the current user's profile. | Token |
| `POST` | `/auth/staff` | Create a staff account (Admin only). | Admin Token |
| `GET` | `/auth/staff` | List all staff members for the shop. | Admin Token |

### 3.2 Shop Management (`/shops`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/shops/` | Create a shop (Admin only, one per admin). | Admin Token |
| `GET` | `/shops/mine` | Get the current user's shop details. | Token |
| `GET` | `/shops/{shop_id}`| Get details for a specific shop by ID. | Token |
| `PUT` | `/shops/{shop_id}`| Update shop details (Admin only). | Admin Token |
| `POST` | `/shops/logo` | Upload a shop logo. | Admin Token |

### 3.3 Inventory Management (`/inventory`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/inventory/` | Add a new product to the shop. | Admin/Staff |
| `GET` | `/inventory/` | List all products in the shop. | Token |
| `GET` | `/inventory/search`| Search products by name. | Token |
| `GET` | `/inventory/{id}` | Get details for a specific product. | Token |
| `PUT` | `/inventory/{id}` | Update product details. | Admin/Staff |
| `DELETE`| `/inventory/{id}` | Remove a product (Admin only). | Admin Token |

### 3.4 Billing & Sales (`/sales`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/sales/` | Record a new sale. Triggers stock reduction. | Admin/Staff |
| `GET` | `/sales/` | List all sales for the shop. | Token |
| `GET` | `/sales/{id}` | Get detailed invoice for a sale. | Token |

### 3.5 Dashboard & Analytics (`/dashboard`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/dashboard/summary` | Get key metrics (Revenue, Sales, Stock). | Admin Token |
| `GET` | `/dashboard/daily-sales`| Get sales trajectory for last 30 days. | Admin Token |
| `GET` | `/dashboard/top-products`| Get top 10 best-selling products. | Admin Token |
| `GET` | `/dashboard/low-stock` | Get products below threshold. | Admin Token |

### 3.6 Public Access (`/public`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/public/shops` | List all shops on the platform. | No |
| `GET` | `/public/shop/{name}` | Get basic info for a shop by name. | No |
| `GET` | `/public/shop/{name}/inventory`| View a shop's availability. | No |

---

## 4. Error Handling
The API returns standard HTTP status codes:
- `200/201`: Success
- `401/403`: Authentication/Authorization issues
- `404`: Resource not found
- `400/422`: Validation or logic errors (e.g., insufficient stock)
- `500`: Internal server error

Errors follow this JSON format:
```json
{
  "detail": "Descriptive error message"
}
```

---

## 5. Deployment Note
While this document focuses on local execution, the system is designed to be easily deployed to platforms like **Render** or **Vercel**. Ensure all `.env` variables are correctly set in the environment settings of your deployment provider.
