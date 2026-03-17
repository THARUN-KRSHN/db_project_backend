from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ─── Auth Schemas ────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: Optional[str] = None
    role: str
    shop_id: Optional[UUID] = None
    shop_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StaffCreate(BaseModel):
    email: str
    password: str
    full_name: str


# ─── Shop Schemas ────────────────────────────────────────────────

class ShopCreate(BaseModel):
    shop_name: str
    category: Optional[str] = None
    logo: Optional[str] = None
    show_price: bool = True
    show_stock: bool = True


class ShopUpdate(BaseModel):
    shop_name: Optional[str] = None
    category: Optional[str] = None
    logo: Optional[str] = None
    show_price: Optional[bool] = None
    show_stock: Optional[bool] = None


class ShopResponse(BaseModel):
    shop_id: UUID
    shop_name: str
    category: Optional[str] = None
    logo: Optional[str] = None
    show_price: bool
    show_stock: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Product Schemas ─────────────────────────────────────────────

class ProductCreate(BaseModel):
    product_name: str
    description: Optional[str] = None
    price: float
    quantity: int = 0
    threshold: int = 10


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    threshold: Optional[int] = None


class ProductResponse(BaseModel):
    product_id: UUID
    shop_id: UUID
    product_name: str
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    threshold: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Sale Schemas ────────────────────────────────────────────────

class SaleItemCreate(BaseModel):
    product_id: UUID
    quantity: int


class SaleCreate(BaseModel):
    items: List[SaleItemCreate]


class SaleItemResponse(BaseModel):
    sale_item_id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    sale_id: UUID
    shop_id: UUID
    staff_id: UUID
    staff_name: Optional[str] = None
    sale_date: datetime
    total_amount: float
    items: List[SaleItemResponse] = []

    class Config:
        from_attributes = True


# ─── Dashboard Schemas ───────────────────────────────────────────

class DashboardSummary(BaseModel):
    total_revenue: float
    total_sales: int
    total_products: int
    low_stock_count: int


class DailySales(BaseModel):
    date: str
    total: float
    count: int


class TopProduct(BaseModel):
    product_id: UUID
    product_name: str
    total_sold: int
    total_revenue: float


class LowStockProduct(BaseModel):
    product_id: UUID
    product_name: str
    quantity: int
    threshold: int
