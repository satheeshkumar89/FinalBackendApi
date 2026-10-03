from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import UserSession, Owner, Customer, DeliveryPartner
from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_token
)
from app.config import get_settings

settings = get_settings()


def create_user_session(
    db: Session,
    user_id: int,
    user_type: str,
    device_id: Optional[str] = None,
    device_name: Optional[str] = None,
    ip_address: Optional[str] = None,
    payload_claims: Optional[Dict[str, Any]] = None
) -> Tuple[str, str, int, UserSession]:
    """
    Creates JWT Access Token, Refresh Token, and stores UserSession record in DB.
    Returns: (access_token, refresh_token, expires_in_seconds, user_session)
    """
    claims = payload_claims.copy() if payload_claims else {}
    claims.update({
        "user_id": user_id,
        "user_type": user_type,
        "role": user_type
    })
    
    # Generate JWT tokens
    access_token = create_access_token(data=claims)
    refresh_token = create_refresh_token(data=claims)
    
    token_hash = hash_token(refresh_token)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Store session in DB
    session = UserSession(
        user_id=user_id,
        user_type=user_type,
        refresh_token_hash=token_hash,
        device_id=device_id,
        device_name=device_name or "Mobile App",
        ip_address=ip_address,
        expires_at=expires_at,
        created_at=datetime.utcnow(),
        last_used_at=datetime.utcnow(),
        is_active=True
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    return access_token, refresh_token, expires_in_seconds, session


def verify_and_refresh_session(
    db: Session,
    refresh_token: str,
    device_id: Optional[str] = None,
    device_name: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Tuple[str, str, int, UserSession]:
    """
    Validates refresh token, checks user_session active state in DB,
    performs Refresh Token Rotation (revokes old token, issues new pair).
    Returns: (new_access_token, new_refresh_token, expires_in_seconds, new_user_session)
    """
    payload = verify_token(refresh_token)
    if not payload or payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    token_hash = hash_token(refresh_token)
    session = db.query(UserSession).filter(
        UserSession.refresh_token_hash == token_hash,
        UserSession.is_active == True
    ).first()
    
    if not session or session.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked or logged out"
        )
    
    if session.expires_at < datetime.utcnow():
        session.is_active = False
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token session has expired. Please log in again."
        )
    
    # Revoke old session (Refresh Token Rotation for security)
    session.is_active = False
    session.revoked_at = datetime.utcnow()
    db.commit()
    
    # Prepare claim payload based on user_type
    user_id = session.user_id
    user_type = session.user_type
    
    claims = {
        "user_id": user_id,
        "user_type": user_type,
        "role": user_type
    }
    
    if user_type == "owner":
        claims["owner_id"] = user_id
    elif user_type == "customer":
        claims["customer_id"] = user_id
    elif user_type == "delivery_partner":
        claims["delivery_partner_id"] = user_id
    elif user_type == "admin":
        claims["admin_id"] = user_id

    # Create new rotated token pair & session
    dev_id = device_id or session.device_id
    dev_name = device_name or session.device_name
    
    return create_user_session(
        db=db,
        user_id=user_id,
        user_type=user_type,
        device_id=dev_id,
        device_name=dev_name,
        ip_address=ip_address,
        payload_claims=claims
    )


def revoke_user_session(db: Session, refresh_token: str) -> bool:
    """Revokes a specific session by refresh token"""
    if not refresh_token:
        return False
    token_hash = hash_token(refresh_token)
    session = db.query(UserSession).filter(UserSession.refresh_token_hash == token_hash).first()
    if session and session.is_active:
        session.is_active = False
        session.revoked_at = datetime.utcnow()
        db.commit()
        return True
    return False


def revoke_all_user_sessions(db: Session, user_id: int, user_type: str, keep_session_id: Optional[int] = None) -> int:
    """Revokes all active sessions for a user across all devices (except keep_session_id if provided)"""
    query = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.user_type == user_type,
        UserSession.is_active == True
    )
    if keep_session_id:
        query = query.filter(UserSession.id != keep_session_id)
        
    sessions = query.all()
    count = 0
    now = datetime.utcnow()
    for sess in sessions:
        sess.is_active = False
        sess.revoked_at = now
        count += 1
    db.commit()
    return count


def get_user_sessions(db: Session, user_id: int, user_type: str) -> List[UserSession]:
    """List active user sessions"""
    return db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.user_type == user_type,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).order_by(UserSession.last_used_at.desc()).all()
