"""
Diagnostic script to check orders for Restaurant 2 (phone: 9787792031)
"""
import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "https://dharaifooddelivery.in"

# Restaurant 2 owner token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6MiwicGhvbmVfbnVtYmVyIjoiKzkxOTc4Nzc5MjAzMSIsImV4cCI6MTc2ODgwOTM2Mn0.wXtnKzRDJHel_0f6cb4J-zWjI-rGXRa-2bopHodl7zE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

print("=" * 80)
print("DIAGNOSTIC REPORT: Restaurant 2 Orders")
print("Phone Number: +919787792031")
print("Owner ID: 2")
print(f"Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Test all three endpoints
endpoints = {
    "New Orders (PENDING)": "/orders/new",
    "Ongoing Orders (ACCEPTED/PREPARING/READY)": "/orders/ongoing",
    "Completed Orders (HANDED_OVER/DELIVERED/REJECTED/CANCELLED)": "/orders/completed"
}

all_orders = []

for name, endpoint in endpoints.items():
    print(f"\n📋 Testing: {name}")
    print(f"   Endpoint: {endpoint}")
    print("-" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('data', {}).get('orders', [])
            print(f"   ✓ Success: Found {len(orders)} orders")
            
            if len(orders) > 0:
                print(f"\n   Orders Details:")
                for i, order in enumerate(orders, 1):
                    print(f"   {i}. Order ID: {order.get('order_id')}")
                    print(f"      Status: {order.get('status')}")
                    print(f"      Amount: ₹{order.get('total_amount')}")
                    print(f"      Items: {order.get('item_count')}")
                    print(f"      Created: {order.get('created_at')}")
                    print(f"      Payment: {order.get('payment_method')}")
                    all_orders.append(order)
            else:
                print(f"   ⚠️  No orders found in this category")
                
        elif response.status_code == 500:
            print(f"   ✗ ERROR 500: Internal Server Error")
            print(f"   Response: {response.text}")
            print(f"   ⚠️  This endpoint is still broken - deployment needed!")
            
        else:
            print(f"   ✗ Error {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"   ✗ Request timed out")
    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")

print("\n" + "=" * 80)
print(f"SUMMARY: Total orders found across all endpoints: {len(all_orders)}")
print("=" * 80)

# Additional diagnostic info
print("\n📊 Additional Diagnostics:")
print("-" * 80)

# Check if we can access the API at all
print("\n1. Testing API health...")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    if response.status_code == 200:
        print("   ✓ API is accessible")
    else:
        print(f"   ⚠️  API returned status {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot reach API: {e}")

# Check token validity
print("\n2. Testing authentication token...")
try:
    # Try any authenticated endpoint
    response = requests.get(f"{BASE_URL}/orders/new", headers=headers, timeout=5)
    if response.status_code == 401:
        print("   ✗ Token is invalid or expired")
    elif response.status_code in [200, 500]:
        print("   ✓ Token is valid")
    else:
        print(f"   ? Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 80)
print("💡 RECOMMENDATIONS:")
print("-" * 80)

if len(all_orders) == 0:
    print("❌ NO ORDERS FOUND - Possible reasons:")
    print("   1. No orders have been placed for this restaurant yet")
    print("   2. Orders exist but with unexpected status values")
    print("   3. Database migration issue - old status values not converted")
    print("   4. Restaurant ID mismatch")
    print("\n   ➡️  Next steps:")
    print("      • Check if order was placed successfully (customer side)")
    print("      • Verify restaurant_id in the database")
    print("      • Run database migration to fix old status values")
else:
    print(f"✓ Found {len(all_orders)} orders")
    
print("\n   ⚠️  DEPLOYMENT NEEDED:")
print("      The fix has been committed and pushed to GitHub.")
print("      SSH to EC2 is timing out - manual deployment required:")
print("      1. SSH: ssh -i dharaifood.pem ec2-user@52.22.224.42")
print("      2. cd fastfoodie-backend && git pull origin main")
print("      3. sudo docker-compose down && sudo docker-compose up --build -d")

print("=" * 80)
