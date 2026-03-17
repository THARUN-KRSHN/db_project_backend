import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from supabase import create_client, Client
from dotenv import load_dotenv
from database import get_db
from models import User

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Supabase environment variables are missing. Please create a .env file inside the 'backend' folder and configure SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_ROLE_KEY.")

# Supabase JWT secret — this is the JWT secret from your Supabase project settings
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", SUPABASE_ANON_KEY)

# Public Supabase client (for login/register)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Admin Supabase client (for creating staff users)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the Supabase JWT token and extract user ID."""
    token = credentials.credentials
    try:
        auth_response = supabase.auth.get_user(token)
        if not auth_response or not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user not found",
            )
        return auth_response.user.id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


def get_current_user(
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user from the database."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database",
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require the current user to be an admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_staff_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require the current user to be either staff or admin."""
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff or admin access required",
        )
    return current_user
