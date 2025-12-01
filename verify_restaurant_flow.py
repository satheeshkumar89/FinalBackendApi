import sys
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal, engine
from app.models import Category, Cuisine, Owner, Restaurant, Customer

# Initialize Client
client = TestClient(app)

def print_step(step, success, details=None):
    icon = "✅" if success else "❌"
    print(f"{icon} {step}")
    if details:
        if isinstance(details, dict) or isinstance(details, list):
            print(json.dumps(details, indent=2))
        else:
            print(f"   {details}")
    if not success:
        print("🛑 Stopping execution due to failure.")
        sys.exit(1)

def seed_initial_data():
    print("\n🌱 Seeding Initial Data (Categories & Cuisines)...")
    db = SessionLocal()
    try:
        # Seed Category
        if not db.query(Category).filter_by(name="Starters").first():
            cat = Category(name="Starters", display_order=1, is_active=True)
            db.add(cat)
            print("   - Added Category: Starters")
        
        # Seed Cuisine
        if not db.query(Cuisine).filter_by(name="North Indian").first():
            cuisine = Cuisine(name="North Indian", is_active=True)
            db.add(cuisine)
            print("   - Added Cuisine: North Indian")
        
        db.commit()
        
        # Get IDs
        cat_id = db.query(Category).filter_by(name="Starters").first().id
        cuisine_id = db.query(Cuisine).filter_by(name="North Indian").first().id
        return cat_id, cuisine_id
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)
    finally:
        db.close()

# --- EXECUTION START ---

# 0. Seed Data
cat_id, cuisine_id = seed_initial_data()

# 1. Owner Authentication
print("\n--- 1. Owner Authentication ---")
owner_phone = "+919999999999"
resp = client.post("/auth/send-otp", json={"phone_number": owner_phone})
print_step("Send OTP (Owner)", resp.status_code == 200)

resp = client.post("/auth/verify-otp", json={"phone_number": owner_phone, "otp_code": "123456"})
print_step("Verify OTP (Owner)", resp.status_code == 200)
owner_data = resp.json()
owner_token = owner_data["access_token"]
owner_headers = {"Authorization": f"Bearer {owner_token}"}
print(f"   Owner Token: {owner_token[:10]}...")

# 2. Owner Profile
print("\n--- 2. Owner Profile ---")
profile_data = {"full_name": "Test Owner", "email": "owner@test.com"}
resp = client.put("/owner/details", json=profile_data, headers=owner_headers)
print_step("Update Owner Profile", resp.status_code == 200)

# 3. Restaurant Setup
print("\n--- 3. Restaurant Setup ---")
restaurant_data = {
    "restaurant_name": "Spice Garden",
    "restaurant_type": "restaurant",
    "fssai_license_number": "12345678901234",
    "opening_time": "09:00",
    "closing_time": "22:00"
}
resp = client.post("/restaurant/create", json=restaurant_data, headers=owner_headers)
print_step("Create Restaurant", resp.status_code == 200)
restaurant_id = resp.json()["data"]["id"]

# Add Address
address_data = {
    "address_line_1": "123 Food Street",
    "address_line_2": "Near Tech Park",
    "city": "Bangalore",
    "state": "Karnataka",
    "pincode": "560001",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "landmark": "Opposite Mall"
}
resp = client.post("/restaurant/address", json=address_data, headers=owner_headers)
print_step("Add Restaurant Address", resp.status_code == 200)

# Add Cuisines
cuisine_data = {"cuisine_ids": [cuisine_id]}
resp = client.post("/restaurant/cuisines", json=cuisine_data, headers=owner_headers)
print_step("Add Restaurant Cuisines", resp.status_code == 200)

# 4. Menu Management
print("\n--- 4. Menu Management ---")
item_data = {
    "name": "Paneer Butter Masala",
    "description": "Rich creamy gravy",
    "price": 280.0,
    "category_id": cat_id,
    "is_vegetarian": True,
    "preparation_time": 25,
    "is_available": True
}
resp = client.post("/menu/item/add", json=item_data, headers=owner_headers)
print_step("Add Menu Item", resp.status_code == 200)
menu_item_id = resp.json()["data"]["id"]

# Get Menu
resp = client.get("/menu/items", headers=owner_headers)
print_step("Get Menu Items", resp.status_code == 200 and len(resp.json()["data"]["items"]) > 0)

# 5. Go Online
print("\n--- 5. Go Online ---")
resp = client.put("/restaurant/status?is_open=true", headers=owner_headers)
print_step("Set Restaurant Online", resp.status_code == 200 and resp.json()["data"]["is_open"] == True)

# 6. Dashboard Check
print("\n--- 6. Dashboard Check ---")
resp = client.get("/dashboard/today-summary", headers=owner_headers)
print_step("Get Dashboard Summary", resp.status_code == 200)

# 7. Customer Flow (Place Order)
print("\n--- 7. Customer Flow (Place Order) ---")
cust_phone = "+918888888888"
client.post("/customer/auth/send-otp", json={"phone_number": cust_phone})
resp = client.post("/customer/auth/verify-otp", json={"phone_number": cust_phone, "otp_code": "123456"})
print_step("Customer Login", resp.status_code == 200)
cust_token = resp.json()["access_token"]
cust_headers = {"Authorization": f"Bearer {cust_token}"}

# Add to Cart
cart_data = {
    "restaurant_id": restaurant_id,
    "menu_item_id": menu_item_id,
    "quantity": 2
}
resp = client.post("/customer/cart/add", json=cart_data, headers=cust_headers)
print_step("Add to Cart", resp.status_code == 200)

# Place Order
order_req = {
    "restaurant_id": restaurant_id,
    "payment_method": "upi",
    "address_id": 0 # Use dummy address
}
resp = client.post("/customer/orders", json=order_req, headers=cust_headers)
print_step("Place Order", resp.status_code == 200)
order_id = resp.json()["data"]["order_id"]
print(f"   Order ID: {order_id}")

# 8. Restaurant Order Management
print("\n--- 8. Restaurant Order Management ---")
# Get New Orders
resp = client.get("/orders/new", headers=owner_headers)
print_step("Get New Orders", resp.status_code == 200)
orders_list = resp.json()["data"]["orders"]
found_order = any(o["order_id"] == order_id for o in orders_list)
print_step("Verify Order in List", found_order)

# Accept Order
resp = client.put(f"/orders/{order_id}/accept", headers=owner_headers)
print_step("Accept Order", resp.status_code == 200)

# Check Status
resp = client.get(f"/orders/{order_id}", headers=owner_headers)
status = resp.json()["data"]["status"]
print_step("Verify Status is 'accepted'", status == "accepted")

print("\n🎉 All Systems Operational! The Restaurant Partner Flow is working correctly.")
