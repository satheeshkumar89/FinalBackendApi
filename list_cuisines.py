
from app.database import SessionLocal
from app.models import Cuisine

def list_cuisines():
    db = SessionLocal()
    try:
        cuisines = db.query(Cuisine).all()
        print("\n" + "="*30)
        print(f"{'ID':<5} | {'Cuisine Name':<20}")
        print("-" * 30)
        for c in cuisines:
            print(f"{c.id:<5} | {c.name:<20}")
        print("="*30 + "\n")
    finally:
        db.close()

if __name__ == "__main__":
    list_cuisines()
