"""
Correct Order Flow Test
Step 1: Add items to cart
Step 2: Place order from cart
Step 3: Verify order appears for restaurant
"""
import requests
import json
import time

BASE_URL = "https://dharaifooddelivery.in"

# Customer token (Customer ID: 2)
CUSTOMER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6MiwicGhvbmVfbnVtYmVyIjoiKzkxOTU3ODc1Nzk0NCIsInJvbGUiOiJjdXN0b21lciIsImV4cCI6MTc2ODgxMTI4OX0.K7VyJf0UPpiEmEitcHtqXT8bDoCMc1wOIdvQj4t0jaA"

# Restaurant owner token (Owner ID: 5)
RESTAURANT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgxMTg1M30.FS7riXj2FPns1VS8CtPTmmlKDW4U-i8lCKhT4FCrZpY"

RESTAURANT_ID = 4
MENU_ITEM_ID = 20
ADDRESS_ID = 1

print("=" * 80)
print("CORRECT ORDER FLOW TEST")
print("=" * 80)
print(f"Restaurant ID: {RESTAURANT_ID}")
print(f"Menu Item ID: {MENU_ITEM_ID}")
print(f"Customer ID: 2")

# Step 1: Clear cart first
print("\n🗑️  STEP 1: Clearing Cart...")
print("-" * 80)

try:
    response = requests.delete(
        f"{BASE_URL}/customer/cart/clear",
        headers={
            "Authorization": f"Bearer {CUSTOMER_TOKEN}",
            "accept": "application/json"
        },
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 404]:
        print("✅ Cart cleared")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"⚠️  {str(e)}")

# Step 2: Add item to cart
print("\n🛒 STEP 2: Adding Item to Cart...")
print("-" * 80)

cart_payload = {
    "menu_item_id": MENU_ITEM_ID,
    "quantity": 1,
    "restaurant_id": RESTAURANT_ID
}

try:
    response = requests.post(
        f"{BASE_URL}/customer/cart/items",
        headers={
            "Authorization": f"Bearer {CUSTOMER_TOKEN}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=cart_payload,
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"✅ Item added to cart")
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Failed: {response.text[:500]}")
        print("\n⚠️  Cannot proceed without item in cart")
        exit(1)
        
except Exception as e:
    print(f"❌ Exception: {str(e)}")
    exit(1)

# Step 3: View cart
print("\n👀 STEP 3: Viewing Cart...")
print("-" * 80)

try:
    response = requests.get(
        f"{BASE_URL}/customer/cart",
        headers={
            "Authorization": f"Bearer {CUSTOMER_TOKEN}",
            "accept": "application/json"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        cart_data = data.get('data', {})
        items = cart_data.get('items', [])
        print(f"✅ Cart has {len(items)} item(s)")
        print(f"Total: ₹{cart_data.get('total', 0)}")
    else:
        print(f"Status: {response.status_code}")
        
except Exception as e:
    print(f"⚠️  {str(e)}")

# Step 4: Place order
print("\n📝 STEP 4: Placing Order...")
print("-" * 80)

order_payload = {
    "address_id": ADDRESS_ID,
    "payment_method": "online",
    "special_instructions": "Test order from API"
}

try:
    response = requests.post(
        f"{BASE_URL}/customer/orders",
        headers={
            "Authorization": f"Bearer {CUSTOMER_TOKEN}",
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json=order_payload,
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"✅ SUCCESS: Order placed!")
        print(f"\nResponse:")
        print(json.dumps(data, indent=2))
        
        order_data = data.get('data', {})
        order_id = order_data.get('order_id') or order_data.get('id')
        order_number = order_data.get('order_number')
        
        if order_id:
            print(f"\n🎯 Order ID: {order_id}")
            print(f"📋 Order Number: {order_number}")
        
    else:
        print(f"❌ FAILED: {response.text[:500]}")
        exit(1)
        
except Exception as e:
    print(f"❌ Exception: {str(e)}")
    exit(1)

# Wait for order to be processed
print("\n⏳ Waiting 2 seconds...")
time.sleep(2)

# Step 5: Check restaurant's new orders
print("\n📋 STEP 5: Checking Restaurant's New Orders...")
print("-" * 80)

try:
    response = requests.get(
        f"{BASE_URL}/orders/new",
        headers={
            "Authorization": f"Bearer {RESTAURANT_TOKEN}",
            "accept": "application/json"
        },
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        orders = data.get('data', {}).get('orders', [])
        print(f"✅ Found {len(orders)} new order(s)")
        
        if len(orders) > 0:
            print(f"\nNew Orders:")
            for i, order in enumerate(orders, 1):
                print(f"\n  Order #{i}:")
                print(f"    • Order ID: {order.get('order_id')}")
                print(f"    • Status: {order.get('status')}")
                print(f"    • Amount: ₹{order.get('total_amount')}")
                print(f"    • Items: {order.get('item_count')}")
                print(f"    • Payment: {order.get('payment_method')}")
                print(f"    • Created: {order.get('created_at')}")
        else:
            print("\n⚠️  NO ORDERS FOUND!")
            print("\n   This means Owner ID 5 does NOT own Restaurant ID 4")
            print("   Check database: SELECT id, owner_id, restaurant_name FROM restaurants WHERE id = 4;")
            
    else:
        print(f"❌ Failed: {response.text[:300]}")
        
except Exception as e:
    print(f"❌ Exception: {str(e)}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETED")
print("=" * 80)

print("""
If the order doesn't appear:
  → Owner ID 5 does not own Restaurant ID 4
  → The order went to a different restaurant owner
  → Solution: Use the correct restaurant_id or correct owner token
""")
