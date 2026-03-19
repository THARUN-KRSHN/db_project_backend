from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Shop
from schemas import UserRegister, UserLogin, UserResponse, StaffCreate
from auth import supabase, supabase_admin, get_current_user, require_admin
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_admin(payload: UserRegister, db: Session = Depends(get_db)):
    """Register a new admin user via Supabase Auth and create local DB record."""
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
        })

        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. Email may already be in use.",
            )

        supabase_user_id = auth_response.user.id

        # Create user record in our database
        db_user = User(
            user_id=supabase_user_id,
            email=payload.email,
            full_name=payload.full_name,
            role="admin",
            shop_id=None,  # Admin creates shop in a separate step
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration error: {str(e)}",
        )


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Login via Supabase Auth and return JWT + user info."""
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })

        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Get user from our database
        db_user = db.query(User).filter(User.user_id == auth_response.user.id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database",
            )

        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "token_type": "bearer",
            "user": {
                "user_id": str(db_user.user_id),
                "email": db_user.email,
                "full_name": db_user.full_name,
                "role": db_user.role,
                "shop_id": str(db_user.shop_id) if db_user.shop_id else None,
                "shop_name": db_user.shop_name,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        # Check if it's a Supabase error (usually has a message)
        error_msg = str(e)
        if "invalid login credentials" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal login error: {error_msg}",
        )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user


@router.post("/staff", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_staff(
    payload: StaffCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin creates a staff account for their shop."""
    if not admin.shop_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must create a shop before adding staff",
        )

    try:
        # Create staff user in Supabase Auth using admin client
        auth_response = supabase_admin.auth.admin.create_user({
            "email": payload.email,
            "password": payload.password,
            "email_confirm": True,
        })

        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Staff creation failed",
            )

        # Create staff record in our database
        db_user = User(
            user_id=auth_response.user.id,
            email=payload.email,
            full_name=payload.full_name,
            role="staff",
            shop_id=admin.shop_id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Staff creation error: {str(e)}",
        )


@router.get("/staff", response_model=list[UserResponse])
def list_staff(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all staff members for the admin's shop."""
    if not admin.shop_id:
        return []
    staff = db.query(User).filter(
        User.shop_id == admin.shop_id,
        User.role == "staff",
    ).all()
    return staff
