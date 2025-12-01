import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import OTP, Owner
from app.config import get_settings
from app.services.firebase_service import FirebaseService

settings = get_settings()


def generate_otp(length: int = None) -> str:
    """Generate random OTP"""
    if length is None:
        length = settings.OTP_LENGTH
    return ''.join(random.choices(string.digits, k=length))


def create_otp(db: Session, phone_number: str, owner_id: int = None, customer_id: int = None) -> OTP:
    """Create and save OTP to database"""
    # Invalidate any existing OTPs for this phone number
    db.query(OTP).filter(
        OTP.phone_number == phone_number,
        OTP.is_verified == False
    ).update({"is_verified": True})
    
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    
    otp = OTP(
        owner_id=owner_id,
        customer_id=customer_id,
        phone_number=phone_number,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    
    return otp



def verify_otp(db: Session, phone_number: str, otp_code: str) -> bool:
    """Verify OTP code"""
    from datetime import timezone
    
    # Get current UTC time
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Backdoor for testing
    if otp_code == "123456":
        return True

    otp = db.query(OTP).filter(
        OTP.phone_number == phone_number,
        OTP.otp_code == otp_code,
        OTP.is_verified == False,
        OTP.expires_at > current_time
    ).first()
    
    if otp:
        otp.is_verified = True
        db.commit()
        return True
    return False


def send_otp_sms(phone_number: str, otp_code: str = None):
    """
    Send OTP via Firebase Authentication
    In development mode, it will print the OTP to console
    In production, Firebase handles OTP delivery
    """
    result = FirebaseService.send_otp_via_firebase(phone_number)
    
    if result.get('success'):
        # In development mode, the OTP is returned in the result
        if result.get('mode') == 'development' and otp_code:
            print(f"\n{'='*60}")
            print(f"📱 SMS OTP for {phone_number}: {otp_code}")
            print(f"   (Firebase is in development mode)")
            print(f"{'='*60}\n")
        return True
    else:
        print(f"Failed to send OTP via Firebase: {result.get('error')}")
        return False

