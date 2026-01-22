#!/usr/bin/env python3
"""
Script to check restaurant images in the database
"""

import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'fastfoodie'),
    'cursorclass': pymysql.cursors.DictCursor
}

def check_restaurant_images():
    """Check which restaurants have images"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("RESTAURANT IMAGES CHECK")
    print("=" * 80)
    
    # Get all restaurants
    cursor.execute("""
        SELECT 
            r.id,
            r.restaurant_name,
            r.is_active,
            r.is_open,
            COUNT(d.id) as doc_count
        FROM restaurants r
        LEFT JOIN documents d ON r.id = d.restaurant_id AND d.document_type = 'restaurant_photo'
        GROUP BY r.id
        ORDER BY r.id
    """)
    
    restaurants = cursor.fetchall()
    
    print(f"\nTotal Restaurants: {len(restaurants)}\n")
    
    for r in restaurants:
        print(f"ID: {r['id']} | {r['restaurant_name']}")
        print(f"  Active: {r['is_active']} | Open: {r['is_open']}")
        print(f"  Photos: {r['doc_count']}")
        
        # Get actual photo URLs
        cursor.execute("""
            SELECT file_url, file_name, uploaded_at
            FROM documents
            WHERE restaurant_id = %s AND document_type = 'restaurant_photo'
        """, (r['id'],))
        
        photos = cursor.fetchall()
        if photos:
            for photo in photos:
                print(f"    📷 {photo['file_url']}")
                print(f"       Uploaded: {photo['uploaded_at']}")
        else:
            print(f"    ❌ NO PHOTO - Restaurant will show placeholder")
        
        print("-" * 80)
    
    conn.close()

def add_restaurant_image(restaurant_id, image_url):
    """Add a restaurant banner image"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        # Check if restaurant exists
        cursor.execute("SELECT restaurant_name FROM restaurants WHERE id = %s", (restaurant_id,))
        restaurant = cursor.fetchone()
        
        if not restaurant:
            print(f"❌ Restaurant ID {restaurant_id} not found")
            return
        
        # Check if photo already exists
        cursor.execute("""
            SELECT id FROM documents 
            WHERE restaurant_id = %s AND document_type = 'restaurant_photo'
        """, (restaurant_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute("""
                UPDATE documents 
                SET file_url = %s, file_name = 'banner.jpg'
                WHERE id = %s
            """, (image_url, existing['id']))
            print(f"✅ Updated photo for {restaurant['restaurant_name']}")
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO documents (restaurant_id, document_type, file_url, file_name)
                VALUES (%s, 'restaurant_photo', %s, 'banner.jpg')
            """, (restaurant_id, image_url))
            print(f"✅ Added photo for {restaurant['restaurant_name']}")
        
        conn.commit()
        print(f"   URL: {image_url}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2:
        # Add image mode: python check_restaurant_images.py <restaurant_id> <image_url>
        restaurant_id = int(sys.argv[1])
        image_url = sys.argv[2]
        add_restaurant_image(restaurant_id, image_url)
    else:
        # Check mode
        check_restaurant_images()
        
        print("\n" + "=" * 80)
        print("HOW TO ADD RESTAURANT IMAGES")
        print("=" * 80)
        print("\nMethod 1: Using this script")
        print("  python check_restaurant_images.py <restaurant_id> <image_url>")
        print("\nMethod 2: Using API (Restaurant Partner App)")
        print("  POST /restaurant/documents/upload")
        print("  - Upload actual image file")
        print("\nMethod 3: Direct database insert")
        print("  INSERT INTO documents (restaurant_id, document_type, file_url, file_name)")
        print("  VALUES (1, 'restaurant_photo', 'https://...', 'banner.jpg');")
        print("\n" + "=" * 80)
