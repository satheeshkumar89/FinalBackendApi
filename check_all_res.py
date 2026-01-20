import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Restaurant

def check_all_res():
    db = SessionLocal()
    try:
        res = db.query(Restaurant).all()
        print(f"Total Restaurants: {len(res)}")
        for r in res:
            print(f"ID: {r.id}, Name: {r.restaurant_name}, Owner ID: {r.owner_id}")
    finally:
        db.close()

if __name__ == "__main__":
    check_all_res()
