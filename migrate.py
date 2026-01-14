"""
Database initialization and migration script
This script creates all tables and seeds initial data
"""

from app.database import engine, Base, SessionLocal
from app.models import Cuisine, RestaurantTypeEnum
import sys
import os
from sqlalchemy import text


def patch_existing_tables():
    """Add missing columns to existing tables that Base.metadata.create_all misses"""
    print("Checking for missing columns and patching existing tables...")
    try:
        with engine.connect() as connection:
            # 1. Patch orders table for released_at
            print("Checking orders table for missing columns...")
            is_sqlite = connection.engine.name == "sqlite"
            try:
                if is_sqlite:
                    result = connection.execute(text("PRAGMA table_info(orders)"))
                    columns = [row[1] for row in result.fetchall()]
                    if 'released_at' not in columns:
                        print("⚠️ Adding missing 'released_at' column to 'orders' (SQLite)...")
                        connection.execute(text("ALTER TABLE orders ADD COLUMN released_at DATETIME NULL"))
                else:
                    result = connection.execute(text("SHOW COLUMNS FROM orders LIKE 'released_at'"))
                    if not result.fetchone():
                        print("⚠️ Adding missing 'released_at' column to 'orders' (MySQL)...")
                        connection.execute(text("ALTER TABLE orders ADD COLUMN released_at DATETIME NULL"))
            except Exception as e:
                print(f"  - Note: Could not patch orders: {e}")

            # 2. Patch device_tokens table
            print("Checking device_tokens table for missing columns...")
            try:
                if is_sqlite:
                    result = connection.execute(text("PRAGMA table_info(device_tokens)"))
                    columns = [row[1] for row in result.fetchall()]
                    if 'customer_id' not in columns:
                        print("⚠️ Adding missing 'customer_id' column to 'device_tokens' (SQLite)...")
                        connection.execute(text("ALTER TABLE device_tokens ADD COLUMN customer_id INT NULL"))
                    if 'delivery_partner_id' not in columns:
                        print("⚠️ Adding missing 'delivery_partner_id' column to 'device_tokens' (SQLite)...")
                        connection.execute(text("ALTER TABLE device_tokens ADD COLUMN delivery_partner_id INT NULL"))
                else:
                    # customer_id
                    result = connection.execute(text("SHOW COLUMNS FROM device_tokens LIKE 'customer_id'"))
                    if not result.fetchone():
                        print("⚠️ Adding missing 'customer_id' column to 'device_tokens' (MySQL)...")
                        connection.execute(text("ALTER TABLE device_tokens ADD COLUMN customer_id INT NULL"))
                    
                    # delivery_partner_id
                    result = connection.execute(text("SHOW COLUMNS FROM device_tokens LIKE 'delivery_partner_id'"))
                    if not result.fetchone():
                        print("⚠️ Adding missing 'delivery_partner_id' column to 'device_tokens' (MySQL)...")
                        connection.execute(text("ALTER TABLE device_tokens ADD COLUMN delivery_partner_id INT NULL"))

                # Ensure owner_id is nullable
                print("Ensuring owner_id is nullable in 'device_tokens'...")
                if is_sqlite:
                    # SQLite doesn't support MODIFY COLUMN easily, usually it's nullable by default if not specified otherwise
                    pass 
                else:
                    connection.execute(text("ALTER TABLE device_tokens MODIFY COLUMN owner_id INT NULL"))
            except Exception as e:
                print(f"  - Note: Could not patch device_tokens: {e}")

            # 3. Patch delivery_partners table for location and other missing columns
            print("Checking delivery_partners table for missing columns...")
            delivery_partner_columns = [
                ("latitude", "DECIMAL(10, 8) NULL"),
                ("longitude", "DECIMAL(11, 8) NULL"),
                ("vehicle_type", "VARCHAR(50) NULL"),
                ("license_number", "VARCHAR(50) NULL"),
                ("rating", "DECIMAL(3, 2) DEFAULT 5.0"),
                ("profile_photo", "VARCHAR(500) NULL"),
                ("is_online", "BOOLEAN DEFAULT FALSE"),
                ("is_registered", "BOOLEAN DEFAULT FALSE"),
                ("verification_status", "ENUM('pending', 'submitted', 'under_review', 'approved', 'rejected') DEFAULT 'pending'"),
                ("verification_notes", "TEXT NULL"),
                ("last_online_at", "DATETIME NULL"),
                ("last_offline_at", "DATETIME NULL")
            ]

            for col_name, col_type in delivery_partner_columns:
                try:
                    if is_sqlite:
                        # SQLite check
                        result = connection.execute(text(f"PRAGMA table_info(delivery_partners)"))
                        columns = [row[1] for row in result.fetchall()]
                        if col_name not in columns:
                            print(f"⚠️ Adding missing '{col_name}' column to 'delivery_partners' (SQLite)...")
                            connection.execute(text(f"ALTER TABLE delivery_partners ADD COLUMN {col_name} {col_type}"))
                    else:
                        # MySQL check
                        result = connection.execute(text(f"SHOW COLUMNS FROM delivery_partners LIKE '{col_name}'"))
                        if not result.fetchone():
                            print(f"⚠️ Adding missing '{col_name}' column to 'delivery_partners' (MySQL)...")
                            connection.execute(text(f"ALTER TABLE delivery_partners ADD COLUMN {col_name} {col_type}"))
                except Exception as col_e:
                    print(f"  - Note: Could not add {col_name}: {col_e}")

            connection.execute(text("COMMIT"))
            print("✅ Database tables patched successfully")
    except Exception as e:
        print(f"✗ Error patching tables: {e}")
        # Continue anyway as create_all might handle some parts


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_cuisines():
    """Seed initial cuisine data"""
    print("Seeding cuisine data...")
    
    cuisines = [
        {"name": "North Indian", "icon": "🍛"},
        {"name": "South Indian", "icon": "🥘"},
        {"name": "Chinese", "icon": "🥡"},
        {"name": "Italian", "icon": "🍝"},
        {"name": "Mexican", "icon": "🌮"},
        {"name": "Continental", "icon": "🍽️"},
        {"name": "Bakery", "icon": "🍰"},
        {"name": "Fast Food", "icon": "🍔"},
        {"name": "Street Food", "icon": "🌭"},
        {"name": "Desserts", "icon": "🍨"},
        {"name": "Beverages", "icon": "🥤"},
        {"name": "Healthy", "icon": "🥗"},
        {"name": "Seafood", "icon": "🦞"},
        {"name": "BBQ", "icon": "🍖"},
        {"name": "Pizza", "icon": "🍕"},
    ]
    
    db = SessionLocal()
    try:
        for cuisine_data in cuisines:
            # Check if cuisine already exists
            existing = db.query(Cuisine).filter(
                Cuisine.name == cuisine_data["name"]
            ).first()
            
            if not existing:
                cuisine = Cuisine(**cuisine_data)
                db.add(cuisine)
        
        db.commit()
        print(f"✓ Seeded {len(cuisines)} cuisines")
    except Exception as e:
        print(f"✗ Error seeding cuisines: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main migration function"""
    print("=" * 50)
    print("FastFoodie Database Migration")
    print("=" * 50)
    
    try:
        create_tables()
        patch_existing_tables() # Added this call
        seed_cuisines()
        
        print("\n" + "=" * 50)
        print("✓ Migration completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
