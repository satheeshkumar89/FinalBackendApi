import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Order, DeliveryPartner

def find_partner():
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == 62).first()
        if order:
            print(f"Order 62 Status: {order.status}")
            print(f"Assigned Partner ID: {order.delivery_partner_id}")
            if order.delivery_partner_id:
                p = db.query(DeliveryPartner).filter(DeliveryPartner.id == order.delivery_partner_id).first()
                if p:
                    print(f"Partner Name: {p.full_name}, Phone: {p.phone_number}")
                else:
                    print("Partner not found in DB!")
            else:
                print("Order 62 is TRULY unassigned in the DB.")
        else:
            print("Order 62 not found.")
            
    finally:
        db.close()

if __name__ == "__main__":
    find_partner()
