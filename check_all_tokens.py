from app.database import SessionLocal
from app.models import DeviceToken
import json

def check_all_tokens():
    db = SessionLocal()
    try:
        all_tokens = db.query(DeviceToken).all()
        print(f"Total tokens in DB: {len(all_tokens)}")
        for t in all_tokens:
            role = "Unknown"
            if t.owner_id: role = f"Owner {t.owner_id}"
            elif t.customer_id: role = f"Customer {t.customer_id}"
            elif t.delivery_partner_id: role = f"Partner {t.delivery_partner_id}"
            print(f"Token {t.token[:20]}... Role: {role}, Active: {t.is_active}")
    finally:
        db.close()

if __name__ == "__main__":
    check_all_tokens()
