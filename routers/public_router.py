from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Product, Shop
from schemas import ProductResponse

router = APIRouter(prefix="/public", tags=["Public Inventory"])


@router.get("/shops", response_model=list[dict])
def list_shops(db: Session = Depends(get_db)):
    """List all shops available on the platform."""
    shops = db.query(Shop).all()
    return [
        {
            "shop_name": s.shop_name,
            "category": s.category,
            "logo": s.logo,
            "show_price": s.show_price,
            "show_stock": s.show_stock,
        } for s in shops
    ]


@router.get("/shop/{shop_name}/inventory", response_model=list[dict])
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

    # Apply visibility toggles
    results = []
    for p in products:
        item = {
            "product_id": p.product_id,
            "shop_id": p.shop_id,
            "product_name": p.product_name,
            "description": p.description,
            "price": p.price if shop.show_price else None,
            "quantity": p.quantity if shop.show_stock else None,
            "created_at": p.created_at,
        }
        results.append(item)

    return results


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
        "show_price": shop.show_price,
        "show_stock": shop.show_stock,
    }
