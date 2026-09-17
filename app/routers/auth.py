from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SendOTPRequest, VerifyOTPRequest, TokenResponse, APIResponse, OwnerResponse
from app.services.otp_service import create_otp, verify_otp, send_otp_sms
from app.services.jwt_service import create_access_token
from app.models import Owner
from datetime import timedelta

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
        
        # Add OTP to response in development mode
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
def verify_otp_endpoint(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP and return JWT token"""
    # Verify OTP
    is_valid = verify_otp(db, request.phone_number, request.otp_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Get or create owner with phone variant lookup & safe unique email
    clean_phone = request.phone_number.strip() if request.phone_number else ""
    phone_without_cc = clean_phone.replace("+91", "").strip()

    owner = db.query(Owner).filter(
        (Owner.phone_number == clean_phone) | (Owner.phone_number == phone_without_cc) | (Owner.phone_number == f"+91{phone_without_cc}")
    ).first()
    
    if not owner:
        import uuid
        unique_email = f"owner_{phone_without_cc}_{uuid.uuid4().hex[:6]}@fastfoodie.com"
        owner = Owner(
            phone_number=clean_phone,
            full_name="Restaurant Owner",
            email=unique_email
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
    
    # Create access token
    access_token = create_access_token(
        data={"owner_id": owner.id, "phone_number": owner.phone_number}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        owner=OwnerResponse.from_orm(owner)
    )


@router.post("/resend-otp", response_model=APIResponse)
def resend_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """Resend OTP to phone number"""
    return send_otp(request, db)


@router.post("/logout", response_model=APIResponse)
def logout():
    """
    Logout user.
    
    Since we use stateless JWTs, the client should discard the token.
    This endpoint is provided for API completeness and future token blacklisting.
    """
    return APIResponse(
        success=True,
        message="Logged out successfully",
        data=None
    )
