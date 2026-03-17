from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Product, Shop
from schemas import ProductResponse

router = APIRouter(prefix="/public", tags=["Public Inventory"])


@router.get("/shop/{shop_name}/inventory", response_model=list[ProductResponse])
def get_public_inventory(
    shop_name: str,
    q: str = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Public endpoint — no authentication required.
    Returns product listing for a shop by name.
    Customers can view product availability and search products.
    """
    shop = db.query(Shop).filter(Shop.shop_name == shop_name).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop '{shop_name}' not found",
        )

    query = db.query(Product).filter(Product.shop_id == shop.shop_id)

    if q:
        query = query.filter(Product.product_name.ilike(f"%{q}%"))

    products = query.order_by(Product.product_name).all()
    return products


@router.get("/shop/{shop_name}", response_model=dict)
def get_public_shop_info(
    shop_name: str,
    db: Session = Depends(get_db),
):
    """
    Public endpoint — get basic shop information.
    """
    shop = db.query(Shop).filter(Shop.shop_name == shop_name).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop '{shop_name}' not found",
        )
    return {
        "shop_name": shop.shop_name,
        "category": shop.category,
        "logo": shop.logo,
    }
