from app.database import SessionLocal
from app.models import DeviceToken, DeliveryPartner
import json

def check_tokens():
    db = SessionLocal()
    try:
        partners = db.query(DeliveryPartner).filter(DeliveryPartner.is_online == True).all()
        print(f"Online partners: {len(partners)}")
        for p in partners:
            tokens = db.query(DeviceToken).filter(DeviceToken.delivery_partner_id == p.id, DeviceToken.is_active == True).all()
            print(f"Partner {p.id} ({p.full_name}, {p.phone_number}): {len(tokens)} active tokens")
            for t in tokens:
                print(f"  - Token: {t.token[:20]}... (Type: {t.device_type})")
        
        all_tokens = db.query(DeviceToken).filter(DeviceToken.is_active == True).all()
        print(f"\nTotal active tokens: {len(all_tokens)}")
        for t in all_tokens:
            role = "Unknown"
            if t.owner_id: role = f"Owner {t.owner_id}"
            elif t.customer_id: role = f"Customer {t.customer_id}"
            elif t.delivery_partner_id: role = f"Partner {t.delivery_partner_id}"
            print(f"Token {t.token[:20]}... Role: {role}")

    finally:
        db.close()

if __name__ == "__main__":
    check_tokens()
