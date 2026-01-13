from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import GoogleAuthRequest, TokenResponse, UserResponse, UserCreate
from services.auth_service import verify_google_token, create_access_token
from models import User
from datetime import timedelta

router = APIRouter()


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    auth_request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google ID token and return JWT access token.
    """
    # Verify Google token
    google_user = await verify_google_token(auth_request.id_token)

    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )

    # Check if user exists
    user = db.query(User).filter(User.google_id == google_user['google_id']).first()

    if not user:
        # Create new user
        user = User(
            google_id=google_user['google_id'],
            email=google_user['email'],
            name=google_user.get('name'),
            picture_url=google_user.get('picture_url')
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "google_id": user.google_id,
            "picture_url": user.picture_url,
            "created_at": user.created_at
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Get current authenticated user.
    """
    return current_user


# Dependency to get current user from JWT token
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from services.auth_service import decode_access_token

security = HTTPBearer()


async def get_current_user_dependency(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token.
    """
    token_data = decode_access_token(credentials.credentials)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user_id = token_data.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
