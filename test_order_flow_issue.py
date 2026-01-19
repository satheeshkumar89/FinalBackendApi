"""
Test order flow: Create order and verify it appears for restaurant
"""
import requests
import json
import time

BASE_URL = "https://dharaifooddelivery.in"

# Customer token
CUSTOMER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6MiwicGhvbmVfbnVtYmVyIjoiKzkxOTU3ODc1Nzk0NCIsInJvbGUiOiJjdXN0b21lciIsImV4cCI6MTc2ODgxMTI4OX0.K7VyJf0UPpiEmEitcHtqXT8bDoCMc1wOIdvQj4t0jaA"

# Restaurant owner token (Owner ID: 5, Phone: +919786816188)
RESTAURANT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgxMTg1M30.FS7riXj2FPns1VS8CtPTmmlKDW4U-i8lCKhT4FCrZpY"

print("=" * 80)
print("ORDER FLOW TEST")
print("=" * 80)

# Step 1: Create order
print("\n📝 STEP 1: Creating Order...")
print("-" * 80)

order_payload = {
    "restaurant_id": 4,
    "address_id": 1,
    "payment_method": "online",
    "items": [
        {
            "menu_item_id": 20,
            "quantity": 1,
            "price": "253.00"
        }
    ]
}

print(f"Restaurant ID: 4")
print(f"Customer ID: 2")
print(f"Menu Item ID: 20")
print(f"Amount: ₹253.00")

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
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        print(f"✅ SUCCESS: Order created!")
        print(f"\nResponse:")
        print(json.dumps(data, indent=2))
        
        if data.get('data') and data['data'].get('order_id'):
            order_id = data['data']['order_id']
            print(f"\n🎯 Order ID: {order_id}")
        else:
            print("\n⚠️  Warning: No order_id in response")
            
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Exception: {str(e)}")

# Wait a moment for database to update
print("\n⏳ Waiting 2 seconds for order to be processed...")
time.sleep(2)

# Step 2: Check if order appears in restaurant's new orders
print("\n📋 STEP 2: Checking Restaurant's New Orders...")
print("-" * 80)
print(f"Checking for Restaurant Owner ID: 5 (Phone: +919786816188)")

try:
    response = requests.get(
        f"{BASE_URL}/orders/new",
        headers={
            "Authorization": f"Bearer {RESTAURANT_TOKEN}",
            "accept": "application/json"
        },
        timeout=10
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        orders = data.get('data', {}).get('orders', [])
        print(f"✅ SUCCESS: Found {len(orders)} new order(s)")
        
        if len(orders) > 0:
            print(f"\nNew Orders:")
            for i, order in enumerate(orders, 1):
                print(f"\n  Order #{i}:")
                print(f"    • Order ID: {order.get('order_id')}")
                print(f"    • Status: {order.get('status')}")
                print(f"    • Amount: ₹{order.get('total_amount')}")
                print(f"    • Items: {order.get('item_count')}")
                print(f"    • Created: {order.get('created_at')}")
        else:
            print("\n⚠️  NO ORDERS FOUND for this restaurant")
            
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Exception: {str(e)}")

# Step 3: Check restaurant ownership
print("\n🔍 STEP 3: Verifying Restaurant Ownership...")
print("-" * 80)

print("""
⚠️  IMPORTANT: For the order to appear, the restaurant owner must OWN that restaurant!

Relationship Check:
  • Order placed for: Restaurant ID 4
  • Checking orders for: Owner ID 5 (Phone: +919786816188)
  
❓ Does Owner ID 5 own Restaurant ID 4?

To verify, we need to check the database:
  SELECT id, owner_id, restaurant_name FROM restaurants WHERE id = 4;
  
If owner_id ≠ 5, that's why the order isn't showing up!
""")

# Step 4: Test the /orders/ongoing endpoint too
print("\n📊 STEP 4: Testing Other Endpoints...")
print("-" * 80)

endpoints = [
    ("/orders/ongoing", "Ongoing Orders"),
    ("/orders/completed", "Completed Orders")
]

for endpoint, name in endpoints:
    try:
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers={
                "Authorization": f"Bearer {RESTAURANT_TOKEN}",
                "accept": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('data', {}).get('orders', []))
            print(f"✅ {name}: {response.status_code} OK - {count} orders")
        elif response.status_code == 500:
            print(f"❌ {name}: {response.status_code} ERROR - DEPLOYMENT NEEDED!")
        else:
            print(f"⚠️  {name}: {response.status_code}")
            
    except Exception as e:
        print(f"❌ {name}: Exception - {str(e)}")

print("\n" + "=" * 80)
print("💡 DIAGNOSIS SUMMARY")
print("=" * 80)

print("""
If no orders are showing:

1. ❌ Restaurant ID Mismatch
   → The order was placed for Restaurant ID 4
   → But Owner ID 5 may not own Restaurant ID 4
   → Solution: Verify restaurant ownership in database

2. ❌ Endpoints Still Broken (500 error)
   → The /orders/ongoing and /orders/completed endpoints still return 500
   → Solution: Complete EC2 deployment with --no-cache rebuild

3. ❌ Order Creation Failed
   → Check customer/orders endpoint response
   → Verify menu_item_id 20 exists
   → Verify address_id 1 exists for customer

Next Steps:
  1. Run on EC2: grep -n "OrderStatusEnum.ACCEPTED.value" app/routers/orders.py
  2. If not found: git pull origin main
  3. Rebuild: sudo docker-compose down && sudo docker-compose build --no-cache && sudo docker-compose up -d
  4. Verify database: SELECT id, owner_id FROM restaurants WHERE id = 4;
""")

print("=" * 80)
