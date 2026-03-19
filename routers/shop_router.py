from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from models import Shop, User
from schemas import ShopCreate, ShopUpdate, ShopResponse
from auth import require_admin, get_current_user, require_staff_or_admin
import os
import shutil
import uuid

router = APIRouter(prefix="/shops", tags=["Shop Management"])


@router.post("/logo", response_model=dict)
def upload_shop_logo(
    file: UploadFile = File(...),
    admin: User = Depends(require_admin),
):
    """Upload a shop logo. Admin only."""
    # Ensure directory exists
    os.makedirs("static/logos", exist_ok=True)
    
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = f"static/logos/{filename}"
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
            
    return {"url": f"/static/logos/{filename}"}


@router.post("/", response_model=ShopResponse, status_code=status.HTTP_201_CREATED)
def create_shop(
    payload: ShopCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new shop. Only admins without a shop can create one."""
    if admin.shop_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a shop",
        )

    # Check if shop name is unique
    existing = db.query(Shop).filter(Shop.shop_name == payload.shop_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shop name already taken",
        )

    try:
        shop = Shop(
            shop_name=payload.shop_name,
            category=payload.category,
            logo=payload.logo,
            show_price=payload.show_price,
            show_stock=payload.show_stock,
        )
        db.add(shop)
        db.flush()

        # Link admin to the shop
        admin.shop_id = shop.shop_id
        db.commit()
        db.refresh(shop)

        return shop

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Shop creation error: {str(e)}",
        )


@router.get("/mine", response_model=ShopResponse)
def get_my_shop(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's shop details."""
    if not current_user.shop_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shop found for this user",
        )
    shop = db.query(Shop).filter(Shop.shop_id == current_user.shop_id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found",
        )
    return shop


@router.get("/{shop_id}", response_model=ShopResponse)
def get_shop(
    shop_id: str,
    db: Session = Depends(get_db),
):
    """Get shop details by ID."""
    shop = db.query(Shop).filter(Shop.shop_id == shop_id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found",
        )
    return shop


@router.put("/{shop_id}", response_model=ShopResponse)
def update_shop(
    shop_id: str,
    payload: ShopUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update shop details. Only the shop's admin can update."""
    if str(admin.shop_id) != shop_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own shop",
        )

    shop = db.query(Shop).filter(Shop.shop_id == shop_id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found",
        )

    if payload.shop_name is not None:
        # Check uniqueness
        existing = db.query(Shop).filter(
            Shop.shop_name == payload.shop_name,
            Shop.shop_id != shop_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Shop name already taken",
            )
        shop.shop_name = payload.shop_name

    if payload.category is not None:
        shop.category = payload.category
    if payload.logo is not None:
        shop.logo = payload.logo
    if payload.show_price is not None:
        shop.show_price = payload.show_price
    if payload.show_stock is not None:
        shop.show_stock = payload.show_stock

    db.commit()
    db.refresh(shop)
    return shop
