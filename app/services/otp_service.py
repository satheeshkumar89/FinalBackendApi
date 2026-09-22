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
    """Create and save numeric OTP to database, then trigger 2Factor Text SMS delivery"""
    # Invalidate any existing OTPs for this phone number
    db.query(OTP).filter(
        OTP.phone_number == phone_number,
        OTP.is_verified == False
    ).update({"is_verified": True})
    
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    
    # Store numeric OTP code in MySQL database
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
    
    # Send 2Factor Text SMS containing this numeric otp_code
    send_otp_sms(phone_number, otp_code)
    
    return otp


def verify_otp(db: Session, phone_number: str, otp_code: str) -> bool:
    """Verify OTP code - supports local DB and master OTPs"""
    from datetime import timezone

    if not otp_code:
        return False

    clean_otp = str(otp_code).strip()

    # Master Static OTP check for easy testing and app reviews
    if clean_otp in ["123456", "1234", "000000", "0000"]:
        return True

    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    clean_phone = phone_number.strip() if phone_number else ""
    phone_without_cc = clean_phone.replace("+91", "").strip()

    otp = db.query(OTP).filter(
        (OTP.phone_number == clean_phone) | (OTP.phone_number == phone_without_cc) | (OTP.phone_number == f"+91{phone_without_cc}"),
        OTP.is_verified == False,
        OTP.expires_at > current_time
    ).order_by(OTP.created_at.desc()).first()

    if otp and (otp.otp_code == clean_otp):
        otp.is_verified = True
        db.commit()
        return True

    return False


def send_otp_sms(phone_number: str, otp_code: str = None) -> str:
    """
    Send OTP via Renflair SMS Gateway API (with 2Factor fallback)
    Delivers Text SMS directly to user's Inbox
    """
    renflair_key = getattr(settings, "RENFLAIR_API_KEY", "b79d4a459b11c754c20adc1e8f688ff1").strip()
    clean_phone = phone_number.replace("+91", "").replace("-", "").replace(" ", "").strip()
    
    # 1. Primary Route: Renflair SMS API
    if renflair_key:
        try:
            url = f"https://sms.renflair.in/V1.php?API={renflair_key}&PHONE={clean_phone}&OTP={otp_code}"
            response = requests.get(url, timeout=10)
            print(f"📡 [Renflair SMS API] GET {url}")
            print(f"HTTP STATUS: {response.status_code}")
            print(f"RENFLAIR RESPONSE: {response.text}")
            
            try:
                data = response.json()
                if data.get("status") == "SUCCESS":
                    print(f"✅ [Renflair SMS] Sent Text SMS OTP {otp_code} to {clean_phone}")
                    return "SUCCESS"
                else:
                    print(f"⚠️ [Renflair SMS] Response: {data.get('message')}. Retrying with 2Factor...")
            except Exception:
                if "SUCCESS" in response.text.upper():
                    print(f"✅ [Renflair SMS] Sent Text SMS OTP {otp_code} to {clean_phone}")
                    return "SUCCESS"
        except Exception as e:
            print(f"❌ [Renflair SMS] Exception while sending to {clean_phone}: {e}")

    # 2. Secondary Route: 2Factor SMS API Fallback
    twofactor_key = getattr(settings, "TWOFACTOR_API_KEY", "").strip()
    if twofactor_key:
        try:
            url = f"https://2factor.in/API/V1/{twofactor_key}/SMS/{clean_phone}/{otp_code}/OTP_LOGIN"
            response = requests.get(url, timeout=10)
            print(f"📡 [2Factor API] GET {url}")
            print(f"HTTP STATUS: {response.status_code}")
            print(f"2FACTOR RESPONSE: {response.text}")
            
            data = response.json()
            if data.get("Status") == "Success":
                session_id = data.get("Details")
                print(f"✅ [2Factor SMS] Sent Text SMS OTP {otp_code} to {clean_phone} (Session: {session_id})")
                return session_id
        except Exception as e:
            print(f"❌ [2Factor SMS] Exception while sending to {clean_phone}: {e}")

    # Fallback / Development mode logging
    print(f"\n{'='*60}")
    print(f"📱 SMS OTP for {clean_phone}: {otp_code}")
    print(f"{'='*60}\n")
    return None

