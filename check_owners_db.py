import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Owner

def check_owners_db():
    db = SessionLocal()
    try:
        owners = db.query(Owner).all()
        print(f"Total Owners: {len(owners)}")
        for o in owners:
            print(f"ID: {o.id}, Name: {o.full_name}, Phone: {o.phone_number}")
    finally:
        db.close()

if __name__ == "__main__":
    check_owners_db()
