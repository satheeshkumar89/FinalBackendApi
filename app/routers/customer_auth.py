from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SendOTPRequest, VerifyOTPRequest, CustomerTokenResponse, APIResponse, CustomerResponse
from app.services.otp_service import create_otp, verify_otp, send_otp_sms
from app.services.jwt_service import create_access_token
from app.models import Customer
import os

router = APIRouter(prefix="/customer/auth", tags=["Customer Authentication"])


@router.post("/send-otp", response_model=APIResponse)
def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """Send OTP to customer phone number"""
    try:
        # Check if customer exists
        customer = db.query(Customer).filter(Customer.phone_number == request.phone_number).first()
        customer_id = customer.id if customer else None
        
        # Create OTP
        otp = create_otp(db, request.phone_number, customer_id=customer_id)
        
        # Send OTP via SMS
        send_otp_sms(request.phone_number, otp.otp_code)
        
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


@router.post("/verify-otp", response_model=CustomerTokenResponse)
def verify_otp_endpoint(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP and return JWT token for customer"""
    # Verify OTP
    is_valid = verify_otp(db, request.phone_number, request.otp_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Get or create customer
    customer = db.query(Customer).filter(Customer.phone_number == request.phone_number).first()
    
    if not customer:
        # Create new customer with minimal info
        customer = Customer(
            phone_number=request.phone_number,
            full_name="",  # Will be updated later
            email=None  # Will be updated later
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    
    # Create access token
    access_token = create_access_token(
        data={"customer_id": customer.id, "phone_number": customer.phone_number, "role": "customer"}
    )
    
    return CustomerTokenResponse(
        access_token=access_token,
        token_type="bearer",
        customer=CustomerResponse.from_orm(customer)
    )


@router.post("/firebase-verify", response_model=CustomerTokenResponse)
def verify_firebase_token_endpoint(request: dict, db: Session = Depends(get_db)):
    """Verify Firebase ID token and return JWT token for customer"""
    from app.services.firebase_service import FirebaseService
    
    id_token = request.get('id_token')
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="id_token is required"
        )
        
    # Verify Firebase token
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
    
    # Get or create customer
    customer = db.query(Customer).filter(Customer.phone_number == phone_number).first()
    
    if not customer:
        # Create new customer with minimal info
        customer = Customer(
            phone_number=phone_number,
            full_name="",  # Will be updated later
            email=None  # Will be updated later
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    
    # Create access token
    access_token = create_access_token(
        data={"customer_id": customer.id, "phone_number": customer.phone_number, "role": "customer"}
    )
    
    return CustomerTokenResponse(
        access_token=access_token,
        token_type="bearer",
        customer=CustomerResponse.from_orm(customer)
    )


@router.post("/logout", response_model=APIResponse)
def logout():
    """Logout customer"""
    return APIResponse(
        success=True,
        message="Logged out successfully",
        data=None
    )
