import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Restaurant

def check_res_owner():
    db = SessionLocal()
    try:
        res = db.query(Restaurant).filter(Restaurant.id == 5).first()
        if res:
            print(f"Restaurant 5: {res.restaurant_name}, Owner ID: {res.owner_id}")
        else:
            print("Restaurant 5 not found")
    finally:
        db.close()

if __name__ == "__main__":
    check_res_owner()
