from sqlalchemy import create_engine, text
import os
import sys

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://fastfoodie_user:fastfoodie_pass@localhost:3306/fastfoodie")

def patch_database():
    print(f"Connecting to database: {DATABASE_URL}")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Checking if customer_id column exists in otps table...")
            try:
                # Check if column exists
                result = connection.execute(text("SHOW COLUMNS FROM otps LIKE 'customer_id'"))
                if result.fetchone():
                    print("✅ Column 'customer_id' already exists in 'otps' table.")
                else:
                    print("⚠️ Column 'customer_id' missing. Adding it now...")
                    connection.execute(text("ALTER TABLE otps ADD COLUMN customer_id INT NULL"))
                    connection.execute(text("ALTER TABLE otps ADD CONSTRAINT fk_otps_customer_id FOREIGN KEY (customer_id) REFERENCES customers(id)"))
                    connection.commit()
                    print("✅ Successfully added 'customer_id' column and foreign key.")
            except Exception as e:
                print(f"❌ Error checking/adding column: {e}")
                
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")

if __name__ == "__main__":
    patch_database()
