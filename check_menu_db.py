import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import MenuItem

def check_menu_db():
    db = SessionLocal()
    try:
        items = db.query(MenuItem).filter(MenuItem.restaurant_id == 1).all()
        print(f"Total items for Restaurant 1: {len(items)}")
        for i in items:
            print(f"ID: {i.id}, Name: {i.name}, IsAvailable: {i.is_available}")
    finally:
        db.close()

if __name__ == "__main__":
    check_menu_db()
