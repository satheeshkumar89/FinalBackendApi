from sqlalchemy import create_engine, text
import os
import sys

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://fastfoodie_user:fastfoodie_pass@localhost:3306/fastfoodie")

CATEGORIES_LIST = [
    "North Indian", "South Indian", "Andhra", "Chettinad", "Kerala", "Tamil", "Hyderabadi", "Udupi",
    "Bengali", "Assamese", "Oriya", "Rajasthani", "Gujarati", "Kashmiri", "Punjabi", "Maharashtrian",
    "Goan", "Bihari", "Awadhi", "Lucknowi", "Mughlai", "Tandoor", "Kebab", "Grill", "Biryani",
    "Chinese", "Asian", "Pan Asian", "Thai", "Korean", "Japanese", "Sushi", "Indo-Chinese",
    "Vietnamese", "Singaporean", "Noodles", "Ramen", "Dumplings", "Momos",
    "Bakery", "Cakes", "Pastries", "Desserts", "Ice Cream", "Waffles", "Brownies", "Cookies", "Cupcakes",
    "Shakes", "Smoothies", "Juices", "Milkshakes", "Tea", "Coffee", "Beverages", "Mocktails", "Soda",
    "Lassi", "Falooda", "Juice Bar",
    "Italian", "Pizza", "Pasta", "Risotto", "Garlic Bread",
    "Mexican", "Tacos", "Burritos", "Nachos", "Quesadilla",
    "Continental", "European", "Mediterranean", "Lebanese", "Turkish", "Greek", "Middle Eastern",
    "Shawarma", "Falafel",
    "American", "Fast Food", "Burgers", "Hot Dogs", "Steak", "BBQ", "Barbecue",
    "Seafood", "Fish", "Prawns", "Crab", "Sushi Seafoods",
    "Healthy Food", "Diet Food", "Protein Bowls", "Salads", "Keto", "Vegan", "Vegetarian", "Pure Veg",
    "Satvik", "Organic Food",
    "Street Food", "Chaat", "Pani Puri", "Vada Pav", "Dabeli", "Rolls", "Kathi Rolls", "Frankie", "Wraps",
    "Sandwiches", "Grilled Sandwich", "Sub Sandwich",
    "Paratha", "Roti", "Rice Bowls", "Thali", "Combo Meals", "Meals", "Lunchbox", "Home Food", "Homestyle",
    "Dosa", "Idli", "Vada", "Appam", "Pongal", "Poori", "Chapati Meals",
    "Breakfast", "Brunch", "Snacks", "Quick Bites", "Bento Boxes",
    "Wings", "Fried Chicken", "Popcorn Chicken", "Birria",
    "Soup", "Appetizers", "Starters", "Tiffins",
    "Halwa", "Gulab Jamun", "Rasmalai", "Kheer", "Indian Sweets", "Mithai", "Laddoo", "Barfi",
    "Festival Specials", "Diwali Sweets", "Ramzan Special", "Haleem", "Special Thali", "Seasonal Specials",
    "Chef Special", "Family Pack", "Kids Menu", "Party Pack", "Large Meals", "Budget Meals", "Value Combos",
    "Premium Cuisine", "Gourmet", "Fine Dining", "Cloud Kitchen", "Home Chef", "Local Favorites",
    "Newly Added", "Trending", "Popular Nearby", "Exclusive", "Signature Items", "Recommended",
    "Hot & Spicy", "Cold Drinks", "Tea Shop", "Coffee House", "Milk Bar", "Fresh Juice Shop",
    "Desi Chinese", "Arabian", "African", "Fusion Food", "Global Fusion", "Street Chinese",
    "Pasta House", "BBQ Nation Style", "Sizzlers", "Wrap House", "Bowl Meals", "Beverage Shop",
    "Snack Bar", "Indian Chinese", "Non-Veg Starters", "Veg Starters", "Fried Snacks", "Pakoda",
    "Bhajji", "Fresh Fruits", "Fruit Bowls"
]

def seed_categories():
    print(f"Connecting to database: {DATABASE_URL}")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Seeding categories...")
            
            # Get existing categories to avoid duplicates
            result = connection.execute(text("SELECT name FROM categories"))
            existing_categories = {row[0].lower() for row in result.fetchall()}
            
            count = 0
            for category_name in CATEGORIES_LIST:
                if category_name.lower() not in existing_categories:
                    try:
                        connection.execute(
                            text("INSERT INTO categories (name, is_active, display_order, created_at) VALUES (:name, :is_active, :display_order, NOW())"),
                            {"name": category_name, "is_active": True, "display_order": 0}
                        )
                        count += 1
                        existing_categories.add(category_name.lower())
                    except Exception as e:
                        print(f"Skipping {category_name}: {e}")
            
            connection.commit()
            print(f"✅ Successfully added {count} new categories.")
            
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")

if __name__ == "__main__":
    seed_categories()
