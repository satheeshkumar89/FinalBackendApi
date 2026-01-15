"""
Database Migration Script: Update Order Status Flow
Adds new timestamp columns and updates status enum values
"""

import sqlite3
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_sqlite():
    """Migrate SQLite database (local development)"""
    print("🔄 Migrating SQLite database...")
    
    conn = sqlite3.connect('fastfoodie.db')
    cursor = conn.cursor()
    
    try:
        # Add new timestamp columns
        print("  ✅ Adding new timestamp columns...")
        
        # Add handed_over_at
        try:
            cursor.execute("""
                ALTER TABLE orders 
                ADD COLUMN handed_over_at TIMESTAMP NULL
            """)
            print("    ✅ Added handed_over_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("    ⚠️  handed_over_at column already exists")
            else:
                raise
        
        # Add assigned_at
        try:
            cursor.execute("""
                ALTER TABLE orders 
                ADD COLUMN assigned_at TIMESTAMP NULL
            """)
            print("    ✅ Added assigned_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("    ⚠️  assigned_at column already exists")
            else:
                raise
        
        # Add reached_restaurant_at
        try:
            cursor.execute("""
                ALTER TABLE orders 
                ADD COLUMN reached_restaurant_at TIMESTAMP NULL
            """)
            print("    ✅ Added reached_restaurant_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("    ⚠️  reached_restaurant_at column already exists")
            else:
                raise
        
        conn.commit()
        
        # Update status values: NEW -> PENDING
        print("  ✅ Updating order statuses...")
        cursor.execute("""
            UPDATE orders 
            SET status = 'pending' 
            WHERE status = 'new'
        """)
        updated_count = cursor.rowcount
        print(f"    ✅ Updated {updated_count} orders from 'new' to 'pending'")
        
        conn.commit()
        
        # Show updated schema
        cursor.execute("PRAGMA table_info(orders)")
        columns = cursor.fetchall()
        print("\n  📋 Updated Order table columns:")
        for col in columns:
            if 'at' in col[1]:  # Show only timestamp columns
                print(f"    - {col[1]}: {col[2]}")
        
        print("\n✅ SQLite migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during SQLite migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate_mysql():
    """Migrate MySQL database (production)"""
    print("\n🔄 Migrating MySQL database...")
    
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'fastfoodie')
    }
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Add new timestamp columns
        print("  ✅ Adding new timestamp columns...")
        
        # Add handed_over_at
        try:
            cursor.execute("""
                ALTER TABLE orders 
                ADD COLUMN handed_over_at DATETIME NULL
            """)
            print("    ✅ Added handed_over_at column")
        except mysql.connector.Error as e:
            if "Duplicate column" in str(e):
                print("    ⚠️  handed_over_at column already exists")
            else:
                raise
        
        # Add assigned_at
        try:
            cursor.execute("""
                ALTER TABLE orders 
                ADD COLUMN assigned_at DATETIME NULL
            """)
            print("    ✅ Added assigned_at column")
        except mysql.connector.Error as e:
            if "Duplicate column" in str(e):
                print("    ⚠️  assigned_at column already exists")
            else:
                raise
        
        # Add reached_restaurant_at
        try:
            cursor.execute("""
                ALTER TABLE orders 
                ADD COLUMN reached_restaurant_at DATETIME NULL
            """)
            print("    ✅ Added reached_restaurant_at column")
        except mysql.connector.Error as e:
            if "Duplicate column" in str(e):
                print("    ⚠️  reached_restaurant_at column already exists")
            else:
                raise
        
        conn.commit()
        
        # Update status values: NEW -> PENDING
        print("  ✅ Updating order statuses...")
        cursor.execute("""
            UPDATE orders 
            SET status = 'pending' 
            WHERE status = 'new'
        """)
        updated_count = cursor.rowcount
        print(f"    ✅ Updated {updated_count} orders from 'new' to 'pending'")
        
        conn.commit()
        
        print("\n✅ MySQL migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during MySQL migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'conn' in locals():
            conn.close()


def main():
    """Run migrations based on environment"""
    print("=" * 60)
    print("📦 Order Status Flow Migration")
    print("=" * 60)
    
    # Check which database to migrate
    db_type = os.getenv('DATABASE_TYPE', 'sqlite')
    
    if db_type == 'sqlite':
        migrate_sqlite()
    elif db_type == 'mysql':
        migrate_mysql()
    else:
        print(f"❌ Unknown database type: {db_type}")
        print("   Set DATABASE_TYPE to 'sqlite' or 'mysql' in .env")
        return
    
    print("\n" + "=" * 60)
    print("✅ Migration completed successfully!")
    print("=" * 60)
    print("\n📝 Next Steps:")
    print("  1. Update restaurant order endpoints")
    print("  2. Update delivery partner order endpoints")
    print("  3. Update notification service")
    print("  4. Test the new order flow")
    print("  5. Deploy changes to production")


if __name__ == "__main__":
    main()
