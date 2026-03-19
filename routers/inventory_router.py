from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Product, User
from schemas import ProductCreate, ProductUpdate, ProductResponse
from auth import require_admin, get_current_user, require_staff_or_admin

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def add_product(
    payload: ProductCreate,
    user: User = Depends(require_staff_or_admin),
    db: Session = Depends(get_db),
):
    """Add a new product to the shop's inventory. Admin or Staff."""
    if not user.shop_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create a shop first",
        )

    product = Product(
        shop_id=user.shop_id,
        product_name=payload.product_name,
        description=payload.description,
        image=payload.image,
        price=payload.price,
        quantity=payload.quantity,
        threshold=payload.threshold,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=list[ProductResponse])
def list_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all products for the user's shop."""
    if not current_user.shop_id:
        return []
    products = (
        db.query(Product)
        .filter(Product.shop_id == current_user.shop_id)
        .order_by(Product.product_name)
        .all()
    )
    return products


@router.get("/search", response_model=list[ProductResponse])
def search_products(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search products by name within the user's shop."""
    if not current_user.shop_id:
        return []
    products = (
        db.query(Product)
        .filter(
            Product.shop_id == current_user.shop_id,
            Product.product_name.ilike(f"%{q}%"),
        )
        .order_by(Product.product_name)
        .all()
    )
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single product by ID."""
    product = (
        db.query(Product)
        .filter(
            Product.product_id == product_id,
            Product.shop_id == current_user.shop_id,
        )
        .first()
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    user: User = Depends(require_staff_or_admin),
    db: Session = Depends(get_db),
):
    """Update a product. Admin or Staff."""
    product = (
        db.query(Product)
        .filter(
            Product.product_id == product_id,
            Product.shop_id == user.shop_id,
        )
        .first()
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if payload.product_name is not None:
        product.product_name = payload.product_name
    if payload.description is not None:
        product.description = payload.description
    if payload.image is not None:
        product.image = payload.image
    if payload.price is not None:
        product.price = payload.price
    if payload.quantity is not None:
        product.quantity = payload.quantity
    if payload.threshold is not None:
        product.threshold = payload.threshold

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a product from inventory. Admin only."""
    product = (
        db.query(Product)
        .filter(
            Product.product_id == product_id,
            Product.shop_id == admin.shop_id,
        )
        .first()
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    db.delete(product)
    db.commit()
