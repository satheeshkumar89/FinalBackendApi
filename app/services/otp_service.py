import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import OTP, Owner
from app.config import get_settings
from app.services.firebase_service import FirebaseService

settings = get_settings()


import requests

def generate_otp(length: int = 6) -> str:
    """Generate 6-digit random OTP code"""
    return "".join(random.choices(string.digits, k=length))


def create_otp(db: Session, phone_number: str, owner_id: int = None, customer_id: int = None, delivery_partner_id: int = None) -> OTP:
    """Create and save OTP to database, then trigger SMS delivery"""
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
        delivery_partner_id=delivery_partner_id,
        phone_number=phone_number,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    
    # Automatically send SMS OTP
    send_otp_sms(phone_number, otp_code)
    
    return otp


def verify_otp(db: Session, phone_number: str, otp_code: str) -> bool:
    """Verify OTP code - supports static master OTPs (123456, 1234, etc.)"""
    from datetime import timezone

    if not otp_code:
        return False

    clean_otp = str(otp_code).strip()

    # Master Static OTP check for easy testing and app reviews
    if clean_otp in ["123456", "1234", "000000", "0000"]:
        return True

    # Get current UTC time
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    clean_phone = phone_number.strip() if phone_number else ""
    phone_without_cc = clean_phone.replace("+91", "").strip()

    otp = db.query(OTP).filter(
        (OTP.phone_number == clean_phone) | (OTP.phone_number == phone_without_cc) | (OTP.phone_number == f"+91{phone_without_cc}"),
        OTP.otp_code == clean_otp,
        OTP.is_verified == False,
        OTP.expires_at > current_time
    ).first()
    
    if otp:
        otp.is_verified = True
        db.commit()
        return True
    return False


def send_otp_sms(phone_number: str, otp_code: str = None) -> bool:
    """
    Send OTP via 2Factor.in SMS Gateway API
    """
    api_key = getattr(settings, "TWOFACTOR_API_KEY", "").strip()
    clean_phone = phone_number.replace("+91", "").replace("-", "").replace(" ", "").strip()
    
    if api_key:
        try:
            # 2Factor TRAI DLT approved SMS OTP URL format: https://2factor.in/API/V1/{API_KEY}/SMS/{PHONE_NUMBER}/{OTP_CODE}/SERVER_OTP
            url = f"https://2factor.in/API/V1/{api_key}/SMS/{clean_phone}/{otp_code}/SERVER_OTP"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get("Status") == "Success":
                print(f"✅ [2Factor SMS] Sent DLT Text SMS OTP {otp_code} to {clean_phone} (Session: {data.get('Details')})")
                return True
            else:
                print(f"❌ [2Factor SMS] Failed for {clean_phone}: {data.get('Details')}")
        except Exception as e:
            print(f"❌ [2Factor SMS] Exception while sending to {clean_phone}: {e}")
            
    # Fallback / Development mode logging
    print(f"\n{'='*60}")
    print(f"📱 SMS OTP for {clean_phone}: {otp_code}")
    print(f"   (2Factor API Key missing in .env or fallback mode)")
    print(f"{'='*60}\n")
    return True

