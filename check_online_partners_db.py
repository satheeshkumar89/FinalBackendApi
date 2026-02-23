
from app.database import SessionLocal
from app.models import DeliveryPartner

def check_online_partners():
    db = SessionLocal()
    try:
        online_count = db.query(DeliveryPartner).filter(DeliveryPartner.is_online == True).count()
        print(f"Online Delivery Partners: {online_count}")
        
        partners = db.query(DeliveryPartner).filter(DeliveryPartner.is_online == True).all()
        for p in partners:
            print(f"Partner: {p.full_name} | ID: {p.id} | Phone: {p.phone_number} | Online: {p.is_online}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_online_partners()
