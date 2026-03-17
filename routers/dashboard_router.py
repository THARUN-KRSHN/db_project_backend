from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from database import get_db
from models import Sale, SaleItem, Product, User
from schemas import DashboardSummary, DailySales, TopProduct, LowStockProduct
from auth import require_admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get overall dashboard summary — total revenue, sales count, product count, low stock."""
    if not admin.shop_id:
        raise HTTPException(status_code=400, detail="No shop found")

    # Total revenue — SQL aggregation
    total_revenue = (
        db.query(func.coalesce(func.sum(Sale.total_amount), 0.0))
        .filter(Sale.shop_id == admin.shop_id)
        .scalar()
    )

    # Total sales count
    total_sales = (
        db.query(func.count(Sale.sale_id))
        .filter(Sale.shop_id == admin.shop_id)
        .scalar()
    )

    # Total products
    total_products = (
        db.query(func.count(Product.product_id))
        .filter(Product.shop_id == admin.shop_id)
        .scalar()
    )

    # Low stock count — products below threshold
    low_stock_count = (
        db.query(func.count(Product.product_id))
        .filter(
            Product.shop_id == admin.shop_id,
            Product.quantity <= Product.threshold,
        )
        .scalar()
    )

    return DashboardSummary(
        total_revenue=float(total_revenue),
        total_sales=total_sales,
        total_products=total_products,
        low_stock_count=low_stock_count,
    )


@router.get("/daily-sales", response_model=list[DailySales])
def get_daily_sales(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get daily sales for the last 30 days.
    Uses SQL GROUP BY on sale_date for aggregation.
    """
    if not admin.shop_id:
        raise HTTPException(status_code=400, detail="No shop found")

    # Raw SQL for clear GROUP BY demonstration
    query = text("""
        SELECT
            DATE(sale_date) AS date,
            COALESCE(SUM(total_amount), 0) AS total,
            COUNT(*) AS count
        FROM sales
        WHERE shop_id = :shop_id
            AND sale_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(sale_date)
        ORDER BY date DESC
    """)

    result = db.execute(query, {"shop_id": str(admin.shop_id)}).fetchall()

    return [
        DailySales(
            date=str(row.date),
            total=float(row.total),
            count=row.count,
        )
        for row in result
    ]


@router.get("/top-products", response_model=list[TopProduct])
def get_top_products(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get top selling products.
    Uses SQL JOIN between sale_items and products with GROUP BY aggregation.
    """
    if not admin.shop_id:
        raise HTTPException(status_code=400, detail="No shop found")

    # Raw SQL demonstrating JOIN + GROUP BY + ORDER BY
    query = text("""
        SELECT
            p.product_id,
            p.product_name,
            COALESCE(SUM(si.quantity), 0) AS total_sold,
            COALESCE(SUM(si.subtotal), 0) AS total_revenue
        FROM products p
        JOIN sale_items si ON si.product_id = p.product_id
        JOIN sales s ON s.sale_id = si.sale_id
        WHERE p.shop_id = :shop_id
        GROUP BY p.product_id, p.product_name
        ORDER BY total_sold DESC
        LIMIT 10
    """)

    result = db.execute(query, {"shop_id": str(admin.shop_id)}).fetchall()

    return [
        TopProduct(
            product_id=row.product_id,
            product_name=row.product_name,
            total_sold=row.total_sold,
            total_revenue=float(row.total_revenue),
        )
        for row in result
    ]


@router.get("/low-stock", response_model=list[LowStockProduct])
def get_low_stock(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get products with stock at or below their threshold."""
    if not admin.shop_id:
        raise HTTPException(status_code=400, detail="No shop found")

    products = (
        db.query(Product)
        .filter(
            Product.shop_id == admin.shop_id,
            Product.quantity <= Product.threshold,
        )
        .order_by(Product.quantity.asc())
        .all()
    )

    return [
        LowStockProduct(
            product_id=p.product_id,
            product_name=p.product_name,
            quantity=p.quantity,
            threshold=p.threshold,
        )
        for p in products
    ]
