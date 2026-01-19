import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Order, OrderStatusEnum

def check_db():
    db = SessionLocal()
    try:
        # Check specific order 62
        order62 = db.query(Order).filter(Order.id == 62).first()
        if order62:
            print(f"Order 62: Status='{order62.status}', PartnerID={order62.delivery_partner_id}, CreatedAt={order62.created_at}")
        else:
            print("Order 62 not found")

        # List all unassigned orders with 'ready' or 'handed_over' status
        print("\n--- Unassigned Ready/HandedOver Orders ---")
        unassigned = db.query(Order).filter(
            Order.status.in_([OrderStatusEnum.READY.value, OrderStatusEnum.HANDED_OVER.value]),
            Order.delivery_partner_id == None
        ).all()
        print(f"Count: {len(unassigned)}")
        for o in unassigned:
            print(f"ID: {o.id}, Status: {o.status}, RestaurantID: {o.restaurant_id}")

        # List all orders assigned to our test partner +919000000001 (ID 1 usually)
        print("\n--- Recent Orders ---")
        recent = db.query(Order).order_by(Order.id.desc()).limit(10).all()
        for o in recent:
            print(f"ID: {o.id}, Status: '{o.status}', PartnerID: {o.delivery_partner_id}")

    finally:
        db.close()

if __name__ == "__main__":
    check_db()
