import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Order, Restaurant

def check_orders_db():
    db = SessionLocal()
    try:
        orders = db.query(Order).order_by(Order.id.desc()).limit(1).all()
        for o in orders:
            print(f"Order #{o.id}, Status: {o.status}, Restaurant ID: {o.restaurant_id}")
            res = db.query(Restaurant).filter(Restaurant.id == o.restaurant_id).first()
            if res:
                print(f"Restaurant Name: {res.restaurant_name}")
            else:
                print("Restaurant NOT found in DB!")
    finally:
        db.close()

if __name__ == "__main__":
    check_orders_db()
