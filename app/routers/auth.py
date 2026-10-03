from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import (
    SendOTPRequest, VerifyOTPRequest, TokenResponse, APIResponse, OwnerResponse,
    RefreshTokenRequest, LogoutRequest, SessionResponse
)
from app.services.otp_service import create_otp, verify_otp, send_otp_sms
from app.services.session_service import (
    create_user_session,
    verify_and_refresh_session,
    revoke_user_session,
    revoke_all_user_sessions,
    get_user_sessions
)
from app.models import Owner
from app.dependencies import get_current_owner

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/send-otp", response_model=APIResponse)
def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """Send OTP to phone number"""
    try:
        # Check if owner exists
        owner = db.query(Owner).filter(Owner.phone_number == request.phone_number).first()
        owner_id = owner.id if owner else None
        
        # Create OTP (creates DB record & sends SMS)
        otp = create_otp(db, request.phone_number, owner_id)
        
        # In development, include OTP in response
        import os
        response_data = {
            "phone_number": request.phone_number,
            "expires_in": "5 minutes"
        }
        
        if os.getenv('ENVIRONMENT', 'development') == 'development':
            response_data["otp"] = otp.otp_code
            response_data["note"] = "OTP included in response for development only"
        
        return APIResponse(
            success=True,
            message="OTP sent successfully",
            data=response_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp_endpoint(
    request_data: VerifyOTPRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Verify OTP and return JWT access + refresh tokens with session tracking"""
    is_valid = verify_otp(db, request_data.phone_number, request_data.otp_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    clean_phone = request_data.phone_number.strip() if request_data.phone_number else ""
    phone_without_cc = clean_phone.replace("+91", "").strip()

    owner = db.query(Owner).filter(
        (Owner.phone_number == clean_phone) | (Owner.phone_number == phone_without_cc) | (Owner.phone_number == f"+91{phone_without_cc}")
    ).first()
    
    is_new_user = False
    if not owner:
        import uuid
        is_new_user = True
        unique_email = f"owner_{phone_without_cc}_{uuid.uuid4().hex[:6]}@fastfoodie.com"
        owner = Owner(
            phone_number=clean_phone,
            full_name="Restaurant Owner",
            email=unique_email
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
    elif not owner.full_name or owner.full_name == "Restaurant Owner":
        is_new_user = True

    client_ip = req.client.host if req.client else None
    access_token, refresh_token, expires_in, session = create_user_session(
        db=db,
        user_id=owner.id,
        user_type="owner",
        device_id=request_data.device_id,
        device_name=request_data.device_name,
        ip_address=client_ip,
        payload_claims={"owner_id": owner.id, "phone_number": owner.phone_number}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        is_new_user=is_new_user,
        owner=OwnerResponse.from_orm(owner)
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(
    request_data: RefreshTokenRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """
    Exchange refresh token for a new Access + Refresh Token pair (Refresh Token Rotation)
    """
    client_ip = req.client.host if req.client else None
    access_token, new_refresh_token, expires_in, session = verify_and_refresh_session(
        db=db,
        refresh_token=request_data.refresh_token,
        device_id=request_data.device_id,
        device_name=request_data.device_name,
        ip_address=client_ip
    )
    
    owner = db.query(Owner).filter(Owner.id == session.user_id).first()
    owner_resp = OwnerResponse.from_orm(owner) if owner else None

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        is_new_user=False,
        owner=owner_resp
    )


@router.post("/resend-otp", response_model=APIResponse)
def resend_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """Resend OTP to phone number"""
    return send_otp(request, db)


@router.post("/logout", response_model=APIResponse)
def logout(request_data: Optional[LogoutRequest] = None, db: Session = Depends(get_db)):
    """Logout owner and revoke active device session"""
    if request_data and request_data.refresh_token:
        revoke_user_session(db, request_data.refresh_token)
        
    return APIResponse(
        success=True,
        message="Logged out successfully and session revoked",
        data=None
    )


@router.get("/sessions", response_model=List[SessionResponse])
def get_active_owner_sessions(
    current_owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    """List active logged-in device sessions for the current owner"""
    sessions = get_user_sessions(db, current_owner.id, "owner")
    return [SessionResponse.from_orm(s) for s in sessions]


@router.delete("/sessions/all", response_model=APIResponse)
def logout_all_devices(
    current_owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    """Logout from all devices"""
    count = revoke_all_user_sessions(db, current_owner.id, "owner")
    return APIResponse(
        success=True,
        message=f"Logged out from {count} device(s) successfully",
        data={"revoked_count": count}
    )
