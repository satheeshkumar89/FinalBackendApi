from sqlalchemy import create_engine, text
import os
import sys

# Try to get from environment first
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Try reading from .env file directly
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("DATABASE_URL="):
                    DATABASE_URL = line.split("=", 1)[1].strip()
                    # Remove quotes if present
                    if DATABASE_URL.startswith('"') and DATABASE_URL.endswith('"'):
                        DATABASE_URL = DATABASE_URL[1:-1]
                    if DATABASE_URL.startswith("'") and DATABASE_URL.endswith("'"):
                        DATABASE_URL = DATABASE_URL[1:-1]
                    break

# Fallback
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://fastfoodie_user:fastfoodie_pass@localhost:3306/fastfoodie"

def patch_database():
    print(f"Connecting to database: {DATABASE_URL}")
    try:
        # Create engine with connect_args to handle MySQL specifics if needed
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Successfully connected to database.")
            
            # --- 1. Fix Transactions ---
            # Set to autocommit or handle commits manually
            
            # --- 2. Patch orders table ---
            print("Checking orders table for released_at...")
            try:
                result = connection.execute(text("SHOW COLUMNS FROM orders LIKE 'released_at'"))
                if not result.fetchone():
                    print("⚠️ Column 'released_at' missing. Adding it...")
                    connection.execute(text("ALTER TABLE orders ADD COLUMN released_at DATETIME NULL"))
                    print("✅ Added 'released_at' column.")
                else:
                    print("✅ 'released_at' already exists.")
            except Exception as e:
                print(f"❌ Error patching orders: {e}")

            # --- 3. Patch otps table ---
            print("Checking otps table for customer_id and delivery_partner_id...")
            try:
                cols_to_add = ["customer_id", "delivery_partner_id"]
                for col in cols_to_add:
                    result = connection.execute(text(f"SHOW COLUMNS FROM otps LIKE '{col}'"))
                    if not result.fetchone():
                        print(f"⚠️ Column '{col}' missing from otps. Adding it...")
                        connection.execute(text(f"ALTER TABLE otps ADD COLUMN {col} INT NULL"))
                        print(f"✅ Added '{col}' column to otps.")
            except Exception as e:
                print(f"❌ Error patching otps: {e}")

            # --- 3b. Patch restaurants table ---
            print("Checking restaurants table for description and cost_for_two...")
            try:
                if not connection.execute(text("SHOW COLUMNS FROM restaurants LIKE 'description'")).fetchone():
                    print("⚠️ Column 'description' missing from restaurants. Adding it...")
                    connection.execute(text("ALTER TABLE restaurants ADD COLUMN description TEXT NULL"))
                    print("✅ Added 'description' column to restaurants.")

                if not connection.execute(text("SHOW COLUMNS FROM restaurants LIKE 'cost_for_two'")).fetchone():
                    print("⚠️ Column 'cost_for_two' missing from restaurants. Adding it...")
                    connection.execute(text("ALTER TABLE restaurants ADD COLUMN cost_for_two INT NULL"))
                    print("✅ Added 'cost_for_two' column to restaurants.")
            except Exception as e:
                print(f"❌ Error patching restaurants: {e}")

            # --- 4. Patch device_tokens table ---
            print("Checking device_tokens table...")
            try:
                # Add columns if missing
                colsToAdd = ["customer_id", "delivery_partner_id"]
                for col in colsToAdd:
                    res = connection.execute(text(f"SHOW COLUMNS FROM device_tokens LIKE '{col}'"))
                    if not res.fetchone():
                        print(f"⚠️ Column '{col}' missing. Adding...")
                        connection.execute(text(f"ALTER TABLE device_tokens ADD COLUMN {col} INT NULL"))

                print("Ensuring owner_id is nullable in device_tokens...")
                connection.execute(text("ALTER TABLE device_tokens MODIFY COLUMN owner_id INT NULL"))
                print("✅ Patched device_tokens.")
            except Exception as e:
                print(f"❌ Error patching device_tokens: {e}")

            # --- 5. Create notifications table ---
            print("Checking notifications table...")
            try:
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        owner_id INT NULL,
                        customer_id INT NULL,
                        delivery_partner_id INT NULL,
                        title VARCHAR(255) NOT NULL,
                        message TEXT NOT NULL,
                        notification_type VARCHAR(50),
                        order_id INT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("✅ Notifications table checked/created.")
            except Exception as e:
                print(f"❌ Error creating notifications table: {e}")

            # Final Commit for MySQL behavior
            connection.execute(text("COMMIT"))
            print("\nDatabase patch completed successfully.")

    except Exception as e:
        print(f"❌ Failed to connect or execute: {e}")
        sys.exit(1)

if __name__ == "__main__":
    patch_database()
