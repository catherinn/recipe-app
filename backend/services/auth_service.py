from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from google.oauth2 import id_token
from google.auth.transport import requests
from config import get_settings
from fastapi import HTTPException, status
import httpx
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


async def verify_google_token(token: str) -> Optional[dict]:
    """
    Verify Google ID token and return user info.
    """
    # Validate settings at runtime
    if not settings.google_client_id:
        logger.error("GOOGLE_CLIENT_ID not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google authentication is not configured. Please set GOOGLE_CLIENT_ID environment variable."
        )

    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.google_client_id
        )

        # Token is valid, extract user info
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name'),
            'picture_url': idinfo.get('picture')
        }
    except ValueError as e:
        # Invalid token
        logger.warning(f"Google token validation failed: {e}")
        return None
    except Exception as e:
        # Other errors
        logger.error(f"Google token verification error: {e}")
        return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create JWT access token.
    """
    # Validate settings at runtime
    if not settings.jwt_secret_key:
        logger.error("JWT_SECRET_KEY not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured. Please set JWT_SECRET_KEY environment variable."
        )

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT access token.
    """
    if not settings.jwt_secret_key:
        logger.error("JWT_SECRET_KEY not configured")
        return None

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None
