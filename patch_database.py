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
            print("Checking orders table for missing columns...")
            orders_columns = {
                "customer_id": "INT NULL",
                "delivery_partner_id": "INT NULL",
                "payment_method": "VARCHAR(50) NULL",
                "payment_status": "VARCHAR(50) DEFAULT 'pending'",
                "special_instructions": "TEXT NULL",
                "estimated_delivery_time": "DATETIME NULL",
                "accepted_at": "DATETIME NULL",
                "preparing_at": "DATETIME NULL",
                "ready_at": "DATETIME NULL",
                "handed_over_at": "DATETIME NULL",
                "assigned_at": "DATETIME NULL",
                "reached_restaurant_at": "DATETIME NULL",
                "pickedup_at": "DATETIME NULL",
                "delivered_at": "DATETIME NULL",
                "released_at": "DATETIME NULL",
                "rejected_at": "DATETIME NULL",
                "rejection_reason": "TEXT NULL",
                "completed_at": "DATETIME NULL",
                "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
                "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            }
            for col_name, col_type in orders_columns.items():
                try:
                    result = connection.execute(text(f"SHOW COLUMNS FROM orders LIKE '{col_name}'"))
                    if not result.fetchone():
                        print(f"⚠️ Column '{col_name}' missing from orders. Adding it...")
                        connection.execute(text(f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}"))
                        print(f"✅ Added '{col_name}' column to orders.")
                except Exception as e:
                    print(f"❌ Error patching orders column '{col_name}': {e}")

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

            # --- 3c. Patch menu_items table ---
            print("Checking menu_items table for category_id...")
            try:
                if not connection.execute(text("SHOW COLUMNS FROM menu_items LIKE 'category_id'")).fetchone():
                    print("⚠️ Column 'category_id' missing from menu_items. Adding it...")
                    connection.execute(text("ALTER TABLE menu_items ADD COLUMN category_id INT NULL"))
                    print("✅ Added 'category_id' column to menu_items.")

                if not connection.execute(text("SHOW COLUMNS FROM menu_items LIKE 'discount_price'")).fetchone():
                    print("⚠️ Column 'discount_price' missing from menu_items. Adding it...")
                    connection.execute(text("ALTER TABLE menu_items ADD COLUMN discount_price DECIMAL(10,2) DEFAULT 0.00"))
                    print("✅ Added 'discount_price' column to menu_items.")

                if not connection.execute(text("SHOW COLUMNS FROM menu_items LIKE 'is_bestseller'")).fetchone():
                    print("⚠️ Column 'is_bestseller' missing from menu_items. Adding it...")
                    connection.execute(text("ALTER TABLE menu_items ADD COLUMN is_bestseller BOOLEAN DEFAULT FALSE"))
                    print("✅ Added 'is_bestseller' column to menu_items.")

                if not connection.execute(text("SHOW COLUMNS FROM menu_items LIKE 'rating'")).fetchone():
                    print("⚠️ Column 'rating' missing from menu_items. Adding it...")
                    connection.execute(text("ALTER TABLE menu_items ADD COLUMN rating DECIMAL(3,2) DEFAULT 0.00"))
                    print("✅ Added 'rating' column to menu_items.")
            except Exception as e:
                print(f"❌ Error patching menu_items: {e}")

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

            # --- 6. Check and Seed Cuisines table ---
            print("Checking cuisines table...")
            try:
                # Check table exists
                res = connection.execute(text("SHOW TABLES LIKE 'cuisines'"))
                if res.fetchone():
                    count_res = connection.execute(text("SELECT COUNT(*) FROM cuisines")).fetchone()
                    if count_res and count_res[0] == 0:
                        print("⚠️ Cuisines table is empty! Seeding default cuisines...")
                        CUISINES = [
                            "Starters", "Main Course", "Breads", "Rice & Biryani", "Desserts", "Beverages", "Snacks", "Combos",
                            "North Indian", "South Indian", "Andhra", "Chettinad", "Kerala", "Tamil", "Hyderabadi", "Udupi",
                            "Bengali", "Assamese", "Oriya", "Rajasthani", "Gujarati", "Kashmiri", "Punjabi", "Maharashtrian",
                            "Goan", "Bihari", "Awadhi", "Lucknowi", "Mughlai", "Tandoor", "Kebab", "Grill", "Biryani",
                            "Chinese", "Asian", "Pan Asian", "Thai", "Korean", "Japanese", "Sushi", "Indo-Chinese",
                            "Vietnamese", "Singaporean", "Noodles", "Ramen", "Dumplings", "Momos", "Bakery", "Cakes",
                            "Pastries", "Ice Cream", "Waffles", "Brownies", "Cookies", "Cupcakes", "Shakes",
                            "Smoothies", "Juices", "Milkshakes", "Tea", "Coffee", "Mocktails", "Soda", "Lassi",
                            "Falooda", "Juice Bar", "Italian", "Pizza", "Pasta", "Risotto", "Garlic Bread", "Mexican",
                            "Tacos", "Burritos", "Nachos", "Quesadilla", "Continental", "European", "Mediterranean",
                            "Lebanese", "Turkish", "Greek", "Middle Eastern", "Shawarma", "Falafel", "American", "Fast Food",
                            "Burgers", "Hot Dogs", "Steak", "BBQ", "Barbecue", "Seafood", "Fish", "Prawns", "Crab",
                            "Sushi Seafoods", "Healthy Food", "Diet Food", "Protein Bowls", "Salads", "Keto", "Vegan",
                            "Vegetarian", "Pure Veg", "Satvik", "Organic Food", "Street Food", "Chaat", "Pani Puri",
                            "Vada Pav", "Dabeli", "Rolls", "Kathi Rolls", "Frankie", "Wraps", "Sandwiches", "Grilled Sandwich",
                            "Sub Sandwich", "Paratha", "Roti", "Rice Bowls", "Thali", "Combo Meals", "Meals", "Lunchbox",
                            "Home Food", "Homestyle", "Dosa", "Idli", "Vada", "Appam", "Pongal", "Poori", "Chapati Meals",
                            "Breakfast", "Brunch", "Quick Bites", "Bento Boxes", "Wings", "Fried Chicken",
                            "Popcorn Chicken", "Birria", "Soup", "Appetizers", "Tiffins", "Halwa", "Gulab Jamun",
                            "Rasmalai", "Kheer", "Indian Sweets", "Mithai", "Laddoo", "Barfi", "Festival Specials"
                        ]
                        for c_name in CUISINES:
                            connection.execute(text("INSERT INTO cuisines (name, is_active) VALUES (:name, 1)"), {"name": c_name})
                        print(f"✅ Seeded {len(CUISINES)} default cuisines.")
                    else:
                        print(f"✅ Cuisines table already has {count_res[0]} entries.")
            except Exception as e:
                print(f"❌ Error checking/seeding cuisines table: {e}")

            # --- 7. Fix NULL values in menu_items table ---
            print("Checking menu_items table for NULL values...")
            try:
                connection.execute(text("UPDATE menu_items SET discount_price = 0.00 WHERE discount_price IS NULL"))
                connection.execute(text("UPDATE menu_items SET is_bestseller = 0 WHERE is_bestseller IS NULL"))
                connection.execute(text("UPDATE menu_items SET rating = 0.00 WHERE rating IS NULL"))
                connection.execute(text("UPDATE menu_items SET is_vegetarian = 1 WHERE is_vegetarian IS NULL"))
                connection.execute(text("UPDATE menu_items SET is_available = 1 WHERE is_available IS NULL"))
                print("✅ Fixed NULL values in menu_items table.")
            except Exception as e:
                print(f"❌ Error updating menu_items NULLs: {e}")

            # --- 8. Normalize verification_status values ---
            print("Normalizing verification_status values...")
            try:
                connection.execute(text("UPDATE delivery_partners SET verification_status = LOWER(verification_status) WHERE verification_status IS NOT NULL"))
                connection.execute(text("UPDATE restaurants SET verification_status = LOWER(verification_status) WHERE verification_status IS NOT NULL"))
                print("✅ Normalized verification_status values to lowercase.")
            except Exception as e:
                print(f"❌ Error normalizing verification_status: {e}")

            # Final Commit for MySQL behavior
            connection.execute(text("COMMIT"))
            print("\nDatabase patch completed successfully.")

    except Exception as e:
        print(f"❌ Failed to connect or execute: {e}")
        sys.exit(1)

if __name__ == "__main__":
    patch_database()
