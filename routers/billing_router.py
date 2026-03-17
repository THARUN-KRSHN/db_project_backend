from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from models import Sale, SaleItem, Product, User
from schemas import SaleCreate, SaleResponse, SaleItemResponse
from auth import require_staff_or_admin

router = APIRouter(prefix="/sales", tags=["Billing & Sales"])


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    payload: SaleCreate,
    current_user: User = Depends(require_staff_or_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new sale with items.
    Stock reduction is handled by a database trigger on sale_items INSERT.
    """
    if not current_user.shop_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No shop associated with this user",
        )

    if not payload.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sale must have at least one item",
        )

    try:
        # Validate all products and calculate totals
        total_amount = 0.0
        sale_items_data = []

        for item in payload.items:
            product = (
                db.query(Product)
                .filter(
                    Product.product_id == item.product_id,
                    Product.shop_id == current_user.shop_id,
                )
                .first()
            )
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item.product_id} not found",
                )
            if product.quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.product_name}. Available: {product.quantity}",
                )

            subtotal = product.price * item.quantity
            total_amount += subtotal
            sale_items_data.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": product.price,
                "subtotal": subtotal,
                "product_name": product.product_name,
            })

        # Create sale record
        sale = Sale(
            shop_id=current_user.shop_id,
            staff_id=current_user.user_id,
            total_amount=total_amount,
        )
        db.add(sale)
        db.flush()  # Get sale_id

        # Create sale items — the DB trigger will reduce stock
        for item_data in sale_items_data:
            sale_item = SaleItem(
                sale_id=sale.sale_id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                subtotal=item_data["subtotal"],
            )
            db.add(sale_item)

        db.commit()
        db.refresh(sale)

        # Build response with item details
        response_items = []
        for item_data in sale_items_data:
            response_items.append(SaleItemResponse(
                sale_item_id=sale.sale_id,  # Placeholder, actual IDs set after commit
                product_id=item_data["product_id"],
                product_name=item_data["product_name"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                subtotal=item_data["subtotal"],
            ))

        return SaleResponse(
            sale_id=sale.sale_id,
            shop_id=sale.shop_id,
            staff_id=sale.staff_id,
            staff_name=current_user.full_name,
            sale_date=sale.sale_date,
            total_amount=sale.total_amount,
            items=response_items,
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sale creation error: {str(e)}",
        )


@router.get("/", response_model=list[SaleResponse])
def list_sales(
    current_user: User = Depends(require_staff_or_admin),
    db: Session = Depends(get_db),
):
    """List all sales for the user's shop, most recent first."""
    if not current_user.shop_id:
        return []

    sales = (
        db.query(Sale)
        .filter(Sale.shop_id == current_user.shop_id)
        .order_by(Sale.sale_date.desc())
        .limit(100)
        .all()
    )

    result = []
    for sale in sales:
        staff = db.query(User).filter(User.user_id == sale.staff_id).first()
        items = []
        for si in sale.items:
            product = db.query(Product).filter(Product.product_id == si.product_id).first()
            items.append(SaleItemResponse(
                sale_item_id=si.sale_item_id,
                product_id=si.product_id,
                product_name=product.product_name if product else "Deleted Product",
                quantity=si.quantity,
                unit_price=si.unit_price,
                subtotal=si.subtotal,
            ))
        result.append(SaleResponse(
            sale_id=sale.sale_id,
            shop_id=sale.shop_id,
            staff_id=sale.staff_id,
            staff_name=staff.full_name if staff else "Unknown",
            sale_date=sale.sale_date,
            total_amount=sale.total_amount,
            items=items,
        ))

    return result


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: str,
    current_user: User = Depends(require_staff_or_admin),
    db: Session = Depends(get_db),
):
    """Get a single sale with all items (invoice view)."""
    sale = (
        db.query(Sale)
        .filter(
            Sale.sale_id == sale_id,
            Sale.shop_id == current_user.shop_id,
        )
        .first()
    )
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    staff = db.query(User).filter(User.user_id == sale.staff_id).first()
    items = []
    for si in sale.items:
        product = db.query(Product).filter(Product.product_id == si.product_id).first()
        items.append(SaleItemResponse(
            sale_item_id=si.sale_item_id,
            product_id=si.product_id,
            product_name=product.product_name if product else "Deleted Product",
            quantity=si.quantity,
            unit_price=si.unit_price,
            subtotal=si.subtotal,
        ))

    return SaleResponse(
        sale_id=sale.sale_id,
        shop_id=sale.shop_id,
        staff_id=sale.staff_id,
        staff_name=staff.full_name if staff else "Unknown",
        sale_date=sale.sale_date,
        total_amount=sale.total_amount,
        items=items,
    )
