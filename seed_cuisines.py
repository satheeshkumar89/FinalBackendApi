"""
Seed Cuisines Script

This script seeds the database with predefined cuisines.
Run this after creating the cuisines table.

Usage:
    python seed_cuisines.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal
from app.models import Cuisine

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
    "Rasmalai", "Kheer", "Indian Sweets", "Mithai", "Laddoo", "Barfi", "Festival Specials",
    "Diwali Sweets", "Ramzan Special", "Haleem", "Special Thali", "Seasonal Specials", "Chef Special",
    "Family Pack", "Kids Menu", "Party Pack", "Large Meals", "Budget Meals", "Value Combos",
    "Premium Cuisine", "Gourmet", "Fine Dining", "Cloud Kitchen", "Home Chef", "Local Favorites",
    "Newly Added", "Trending", "Popular Nearby", "Exclusive", "Signature Items", "Recommended",
    "Hot & Spicy", "Cold Drinks", "Tea Shop", "Coffee House", "Milk Bar", "Fresh Juice Shop",
    "Desi Chinese", "Arabian", "African", "Fusion Food", "Global Fusion", "Street Chinese",
    "Pasta House", "BBQ Nation Style", "Sizzlers", "Wrap House", "Bowl Meals", "Beverage Shop",
    "Snack Bar", "Indian Chinese", "Non-Veg Starters", "Veg Starters", "Fried Snacks", "Pakoda",
    "Bhajji", "Fresh Fruits", "Fruit Bowls"
]

def seed_cuisines():
    """Seed the database with predefined cuisines"""
    db = SessionLocal()
    
    try:
        print("🌱 Starting cuisine seeding...")
        
        # Check if cuisines already exist
        existing_count = db.query(Cuisine).count()
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing cuisines. Checking for missing ones...")
            # Skip clearing to preserve existing data (like from tests)
            # If you want to clear, uncomment the following block.
            # Note: This might fail if there are foreign key constraints (e.g. restaurant_cuisines)
            # You might need to delete related records first or use CASCADE


        # Insert cuisines
        added_count = 0
        skipped_count = 0
        
        for index, name in enumerate(CUISINES, start=1):
            # Check if exists by name
            existing = db.query(Cuisine).filter(Cuisine.name == name).first()
            if existing:
                skipped_count += 1
                continue
                
            cuisine = Cuisine(
                name=name,
                is_active=True
                # id will be auto-incremented, but if we cleared the table, it continues.
                # If we want specific IDs we can set them, but usually auto-increment is fine.
                # The user asked for "with id", so we will rely on the DB to assign them 
                # or we can force them if the table is empty.
                # For simplicity and safety, we let DB handle ID, but we print them.
            )
            db.add(cuisine)
            added_count += 1
        
        db.commit()
        print(f"✅ Successfully seeded {added_count} new cuisines (Skipped {skipped_count} existing).")
        
        # Display sample
        print("\n📋 Sample Cuisines:")
        all_cuisines = db.query(Cuisine).limit(10).all()
        for c in all_cuisines:
            print(f"   {c.id:3d}. {c.name}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding cuisines: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_cuisines()
