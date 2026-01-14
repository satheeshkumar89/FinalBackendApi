from sqlalchemy import create_engine, text
import os

DATABASE_URL = "mysql+pymysql://fastfoodie_user:fastfoodie_pass@localhost:3306/fastfoodie"

# Try reading from .env file directly if exists
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                DATABASE_URL = line.split("=", 1)[1].strip()
                if DATABASE_URL.startswith('"') and DATABASE_URL.endswith('"'):
                    DATABASE_URL = DATABASE_URL[1:-1]
                if DATABASE_URL.startswith("'") and DATABASE_URL.endswith("'"):
                    DATABASE_URL = DATABASE_URL[1:-1]
                break

def check_structure():
    print(f"Connecting to: {DATABASE_URL}")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Checking delivery_partners structure...")
            result = connection.execute(text("DESCRIBE delivery_partners"))
            for row in result:
                print(row)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_structure()
