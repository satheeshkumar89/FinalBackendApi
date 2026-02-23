
from app.database import SessionLocal
from app.models import DeviceToken, Notification
import json

def check_notifs():
    db = SessionLocal()
    try:
        token_count = db.query(DeviceToken).count()
        active_token_count = db.query(DeviceToken).filter(DeviceToken.is_active == True).count()
        
        print(f"Total Device Tokens: {token_count}")
        print(f"Active Device Tokens: {active_token_count}")
        
        tokens = db.query(DeviceToken).limit(5).all()
        for t in tokens:
            print(f"Token: {t.token[:20]}... | Owner: {t.owner_id} | Customer: {t.customer_id} | Partner: {t.delivery_partner_id} | Active: {t.is_active}")
            
        notif_count = db.query(Notification).count()
        print(f"Total Notifications in DB: {notif_count}")
        
        latest_notifs = db.query(Notification).order_by(Notification.created_at.desc()).limit(5).all()
        for n in latest_notifs:
            print(f"Notif: {n.title} | {n.message} | Created: {n.created_at}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_notifs()
