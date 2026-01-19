"""
Complete Order Flow Test for Restaurant 2 (Phone: +919787792031)
Tests the entire order lifecycle from PENDING to DELIVERED
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://dharaifooddelivery.in"
RESTAURANT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6MiwicGhvbmVfbnVtYmVyIjoiKzkxOTc4Nzc5MjAzMSIsImV4cCI6MTc2ODgwOTM2Mn0.wXtnKzRDJHel_0f6cb4J-zWjI-rGXRa-2bopHodl7zE"

headers = {
    "Authorization": f"Bearer {RESTAURANT_TOKEN}",
    "accept": "application/json",
    "Content-Type": "application/json"
}

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_section(title):
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")

def check_orders(endpoint_name, endpoint_path):
    """Check orders at a specific endpoint"""
    print(f"\n📋 Checking {endpoint_name}...")
    try:
        response = requests.get(f"{BASE_URL}{endpoint_path}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('data', {}).get('orders', [])
            print(f"   ✓ Status: {response.status_code} OK")
            print(f"   ✓ Found {len(orders)} order(s)")
            
            for i, order in enumerate(orders, 1):
                print(f"\n   Order #{i}:")
                print(f"      • ID: {order.get('order_id')}")
                print(f"      • Status: {order.get('status')}")
                print(f"      • Amount: ₹{order.get('total_amount')}")
                print(f"      • Items: {order.get('item_count')}")
                print(f"      • Payment: {order.get('payment_method')}")
                
            return orders
        elif response.status_code == 500:
            print(f"   ✗ ERROR 500: Server Error (Deployment needed!)")
            return None
        else:
            print(f"   ✗ Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")
        return None

def update_order_status(order_id, action, action_name):
    """Update order status"""
    print(f"\n🔄 Testing: {action_name}")
    try:
        if action == "reject":
            payload = {"rejection_reason": "Test rejection"}
            response = requests.post(
                f"{BASE_URL}/orders/{order_id}/{action}",
                headers=headers,
                json=payload,
                timeout=10
            )
        else:
            response = requests.put(
                f"{BASE_URL}/orders/{order_id}/{action}",
                headers=headers,
                timeout=10
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success: {data.get('message')}")
            new_status = data.get('data', {}).get('status')
            print(f"   ✓ New Status: {new_status}")
            return True
        else:
            print(f"   ✗ Failed: Status {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")
        return False

def get_order_details(order_id):
    """Get detailed order information"""
    try:
        response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', {})
        return None
    except:
        return None

# ============================================================================
# MAIN TEST FLOW
# ============================================================================

print_header(f"🧪 TESTING COMPLETE ORDER FLOW")
print(f"Restaurant: Phone +919787792031 (Owner ID: 2)")
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Base URL: {BASE_URL}")

# Step 1: Check all order endpoints first
print_section("STEP 1: Check Current Orders Status")

new_orders = check_orders("New Orders (PENDING)", "/orders/new")
ongoing_orders = check_orders("Ongoing Orders", "/orders/ongoing")
completed_orders = check_orders("Completed Orders", "/orders/completed")

# Determine if we have an order to test with
test_order_id = None

if new_orders and len(new_orders) > 0:
    test_order_id = new_orders[0]['order_id']
    current_status = new_orders[0]['status']
    print(f"\n✅ Found new order to test with: Order ID {test_order_id} (Status: {current_status})")
elif ongoing_orders and len(ongoing_orders) > 0:
    test_order_id = ongoing_orders[0]['order_id']
    current_status = ongoing_orders[0]['status']
    print(f"\n✅ Found ongoing order to test with: Order ID {test_order_id} (Status: {current_status})")
else:
    print(f"\n⚠️  NO ORDERS FOUND!")
    print(f"\n💡 To test the complete flow:")
    print(f"   1. Place a new order from the customer app")
    print(f"   2. Use Restaurant ID that corresponds to phone +919787792031")
    print(f"   3. Then re-run this test script")
    print(f"\n❌ Cannot proceed with order flow test without an order.")
    exit(0)

# Step 2: Get full order details
print_section("STEP 2: Get Order Details")
order_details = get_order_details(test_order_id)
if order_details:
    print(f"   ✓ Order Number: {order_details.get('order_number')}")
    print(f"   ✓ Customer: {order_details.get('customer_name')}")
    print(f"   ✓ Phone: {order_details.get('customer_phone')}")
    print(f"   ✓ Current Status: {order_details.get('status')}")
    print(f"   ✓ Total Amount: ₹{order_details.get('total_amount')}")
    current_status = order_details.get('status')
else:
    print(f"   ✗ Could not fetch order details")
    current_status = "unknown"

# Step 3: Test Restaurant Flow
print_section("STEP 3: Testing Restaurant Order Flow")

restaurant_flow = [
    ("pending", "accept", "Accept Order (PENDING → ACCEPTED)"),
    ("accepted", "preparing", "Start Preparing (ACCEPTED → PREPARING)"),
    ("preparing", "ready", "Mark as Ready (PREPARING → READY)"),
    ("ready", "handover", "Hand Over to Delivery (READY → HANDED_OVER)")
]

print("\n📝 Restaurant Flow Sequence:")
for i, (from_status, action, description) in enumerate(restaurant_flow, 1):
    print(f"   {i}. {description}")

# Execute based on current status
print("\n🚀 Executing Flow Tests...")

for from_status, action, description in restaurant_flow:
    if current_status == from_status:
        success = update_order_status(test_order_id, action, description)
        if success:
            current_status = action  # Update to new status
            time.sleep(1)  # Brief pause between actions
            
            # Verify the order moved to the correct list
            if action == "accept":
                print("   📊 Verifying order moved to 'Ongoing' list...")
                ongoing = check_orders("Ongoing Orders", "/orders/ongoing")
            elif action == "handover":
                print("   📊 Verifying order moved to 'Completed' list...")
                completed = check_orders("Completed Orders", "/orders/completed")
        else:
            print(f"   ⚠️  Skipping remaining tests due to failure")
            break
    elif from_status in ["pending", "accepted", "preparing", "ready"]:
        # Already past this status
        print(f"\n⏭️  Skipping: {description} (already past this status)")

# Step 4: Summary
print_section("STEP 4: Final Verification")

final_new = check_orders("New Orders", "/orders/new")
final_ongoing = check_orders("Ongoing Orders", "/orders/ongoing")
final_completed = check_orders("Completed Orders", "/orders/completed")

# Final Summary
print_header("📊 TEST SUMMARY")

print(f"\n✅ Order ID Tested: {test_order_id}")

final_details = get_order_details(test_order_id)
if final_details:
    final_status = final_details.get('status')
    print(f"✅ Final Status: {final_status}")
    
    # Show timeline
    timeline = final_details.get('timeline', {})
    print(f"\n📅 Order Timeline:")
    if timeline.get('created_at'):
        print(f"   • Created: {timeline.get('created_at')}")
    if timeline.get('accepted_at'):
        print(f"   • Accepted: {timeline.get('accepted_at')}")
    if timeline.get('preparing_at'):
        print(f"   • Preparing: {timeline.get('preparing_at')}")
    if timeline.get('ready_at'):
        print(f"   • Ready: {timeline.get('ready_at')}")
    if timeline.get('handed_over_at'):
        print(f"   • Handed Over: {timeline.get('handed_over_at')}")

print(f"\n📈 Order Distribution:")
print(f"   • New Orders: {len(final_new) if final_new else 'N/A'}")
print(f"   • Ongoing Orders: {len(final_ongoing) if final_ongoing else 'N/A'}")
print(f"   • Completed Orders: {len(final_completed) if final_completed else 'N/A'}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETED")
print("=" * 80)

print("\n💡 Next Steps:")
print("   • For delivery flow testing, use the delivery partner app")
print("   • Delivery flow: ASSIGNED → REACHED_RESTAURANT → PICKED_UP → DELIVERED")
