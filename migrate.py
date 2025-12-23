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
            result = connection.execute(text("SHOW COLUMNS FROM orders LIKE 'released_at'"))
            if not result.fetchone():
                print("⚠️ Adding missing 'released_at' column to 'orders' table...")
                connection.execute(text("ALTER TABLE orders ADD COLUMN released_at DATETIME NULL"))
            
            # 2. Patch device_tokens table
            # Try to add customer_id if missing
            result = connection.execute(text("SHOW COLUMNS FROM device_tokens LIKE 'customer_id'"))
            if not result.fetchone():
                print("⚠️ Adding missing 'customer_id' column to 'device_tokens' table...")
                connection.execute(text("ALTER TABLE device_tokens ADD COLUMN customer_id INT NULL"))
            
            # Try to add delivery_partner_id if missing
            result = connection.execute(text("SHOW COLUMNS FROM device_tokens LIKE 'delivery_partner_id'"))
            if not result.fetchone():
                print("⚠️ Adding missing 'delivery_partner_id' column to 'device_tokens' table...")
                connection.execute(text("ALTER TABLE device_tokens ADD COLUMN delivery_partner_id INT NULL"))

            # Ensure owner_id is nullable
            print("Ensuring owner_id is nullable in 'device_tokens'...")
            connection.execute(text("ALTER TABLE device_tokens MODIFY COLUMN owner_id INT NULL"))
            
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
