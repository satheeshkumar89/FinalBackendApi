
from app.database import SessionLocal
from app.models import Order
from datetime import datetime

def check_orders():
    db = SessionLocal()
    try:
        order_count = db.query(Order).count()
        print(f"Total Orders: {order_count}")
        
        latest_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
        for o in latest_orders:
            print(f"Order #{o.id} | Status: {o.status} | Created: {o.created_at}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_orders()
