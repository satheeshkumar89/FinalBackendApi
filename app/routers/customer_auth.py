from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.database import get_db
from app.schemas import (
    SendOTPRequest, VerifyOTPRequest, CustomerTokenResponse, APIResponse, CustomerResponse,
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
from app.models import Customer
from app.dependencies import get_current_customer

router = APIRouter(prefix="/customer/auth", tags=["Customer Authentication"])


@router.post("/send-otp", response_model=APIResponse)
def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """Send OTP to customer phone number"""
    try:
        customer = db.query(Customer).filter(Customer.phone_number == request.phone_number).first()
        customer_id = customer.id if customer else None
        
        otp = create_otp(db, request.phone_number, customer_id=customer_id)
        
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


@router.post("/verify-otp", response_model=CustomerTokenResponse)
def verify_otp_endpoint(
    request_data: VerifyOTPRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Verify OTP and return JWT access + refresh tokens for customer"""
    is_valid = verify_otp(db, request_data.phone_number, request_data.otp_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    customer = db.query(Customer).filter(Customer.phone_number == request_data.phone_number).first()
    
    is_new_user = False
    if not customer:
        is_new_user = True
        customer = Customer(
            phone_number=request_data.phone_number,
            full_name="",
            email=None
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    elif not customer.full_name or customer.full_name.strip() == "":
        is_new_user = True

    client_ip = req.client.host if req.client else None
    access_token, refresh_token, expires_in, session = create_user_session(
        db=db,
        user_id=customer.id,
        user_type="customer",
        device_id=request_data.device_id,
        device_name=request_data.device_name,
        ip_address=client_ip,
        payload_claims={"customer_id": customer.id, "phone_number": customer.phone_number, "role": "customer"}
    )
    
    return CustomerTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        is_new_user=is_new_user,
        customer=CustomerResponse.from_orm(customer)
    )


@router.post("/firebase-verify", response_model=CustomerTokenResponse)
def verify_firebase_token_endpoint(
    request_data: dict,
    req: Request,
    db: Session = Depends(get_db)
):
    """Verify Firebase ID token and return JWT access + refresh tokens for customer"""
    from app.services.firebase_service import FirebaseService
    
    id_token = request_data.get('id_token')
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="id_token is required"
        )
        
    result = FirebaseService.verify_firebase_token(id_token)
    
    if not result.get('success'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {result.get('error')}"
        )
        
    phone_number = result.get('phone_number')
    if not phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number not found in Firebase token"
        )
    
    customer = db.query(Customer).filter(Customer.phone_number == phone_number).first()
    
    is_new_user = False
    if not customer:
        is_new_user = True
        customer = Customer(
            phone_number=phone_number,
            full_name="",
            email=None
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    elif not customer.full_name or customer.full_name.strip() == "":
        is_new_user = True

    client_ip = req.client.host if req.client else None
    access_token, refresh_token, expires_in, session = create_user_session(
        db=db,
        user_id=customer.id,
        user_type="customer",
        device_id=request_data.get("device_id"),
        device_name=request_data.get("device_name"),
        ip_address=client_ip,
        payload_claims={"customer_id": customer.id, "phone_number": customer.phone_number, "role": "customer"}
    )
    
    return CustomerTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        is_new_user=is_new_user,
        customer=CustomerResponse.from_orm(customer)
    )


@router.post("/refresh", response_model=CustomerTokenResponse)
def refresh_customer_token(
    request_data: RefreshTokenRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Refresh customer JWT access + refresh tokens (Token Rotation)"""
    client_ip = req.client.host if req.client else None
    access_token, new_refresh_token, expires_in, session = verify_and_refresh_session(
        db=db,
        refresh_token=request_data.refresh_token,
        device_id=request_data.device_id,
        device_name=request_data.device_name,
        ip_address=client_ip
    )
    
    customer = db.query(Customer).filter(Customer.id == session.user_id).first()
    cust_resp = CustomerResponse.from_orm(customer) if customer else None

    return CustomerTokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        is_new_user=False,
        customer=cust_resp
    )


@router.post("/logout", response_model=APIResponse)
def logout(request_data: Optional[LogoutRequest] = None, db: Session = Depends(get_db)):
    """Logout customer and revoke session"""
    if request_data and request_data.refresh_token:
        revoke_user_session(db, request_data.refresh_token)
        
    return APIResponse(
        success=True,
        message="Logged out successfully and session revoked",
        data=None
    )


@router.get("/sessions", response_model=List[SessionResponse])
def get_active_customer_sessions(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """List active logged-in device sessions for customer"""
    sessions = get_user_sessions(db, current_customer.id, "customer")
    return [SessionResponse.from_orm(s) for s in sessions]


@router.delete("/sessions/all", response_model=APIResponse)
def logout_all_customer_devices(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Logout customer from all devices"""
    count = revoke_all_user_sessions(db, current_customer.id, "customer")
    return APIResponse(
        success=True,
        message=f"Logged out from {count} device(s) successfully",
        data={"revoked_count": count}
    )
