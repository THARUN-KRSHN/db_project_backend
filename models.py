import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, ForeignKey, Text, Index, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class Shop(Base):
    """Stores shop information. Each shop is a tenant in the multi-tenant system."""
    __tablename__ = "shops"

    shop_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100))
    logo = Column(Text)
    show_price = Column(Boolean, default=True)
    show_stock = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="shop", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="shop", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="shop", cascade="all, delete-orphan")


class User(Base):
    """Stores admin and staff accounts. Linked to Supabase Auth via user_id."""
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(255))
    role = Column(String(20), nullable=False, default="admin")  # admin | staff
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.shop_id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shop = relationship("Shop", back_populates="users")
    sales = relationship("Sale", back_populates="staff")

    @property
    def shop_name(self):
        return self.shop.shop_name if self.shop else None


class Product(Base):
    """Stores inventory items for a shop."""
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.shop_id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(255), nullable=False)
    description = Column(Text)
    image = Column(Text)  # URL or relative path to uploaded image
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    threshold = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes for optimized search
    __table_args__ = (
        Index("idx_product_shop", "shop_id"),
        Index("idx_product_name", "product_name"),
    )

    # Relationships
    shop = relationship("Shop", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")


class Sale(Base):
    """Stores billing transactions for a shop."""
    __tablename__ = "sales"

    sale_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.shop_id", ondelete="CASCADE"), nullable=False)
    staff_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False, default=0.0)

    __table_args__ = (
        Index("idx_sale_shop", "shop_id"),
        Index("idx_sale_date", "sale_date"),
    )

    # Relationships
    shop = relationship("Shop", back_populates="sales")
    staff = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    """Stores individual products within a sale (line items)."""
    __tablename__ = "sale_items"

    sale_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.sale_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
