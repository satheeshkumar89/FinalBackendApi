import enum
from sqlalchemy import create_engine, text
import os

DATABASE_URL = "mysql+pymysql://fastfoodie_user:fastfoodie_pass@localhost:3306/fastfoodie"

def fix_casing():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Normalizing all order statuses to lowercase...")
        conn.execute(text("UPDATE orders SET status = LOWER(status)"))
        conn.commit()
        print("Done.")

if __name__ == "__main__":
    fix_casing()
