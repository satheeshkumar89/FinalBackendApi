from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


import hashlib
import uuid

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token (short-lived)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "token_type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    """Create JWT refresh token (long-lived) with JTI for session tracking"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "token_type": "refresh",
        "jti": str(uuid.uuid4())
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def hash_token(token: str) -> str:
    """Hash token string for secure database lookup using SHA-256"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token(token: str):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None



def get_password_hash(password: str):
    """Hash password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)
