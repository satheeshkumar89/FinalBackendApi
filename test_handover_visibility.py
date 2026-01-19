import requests
import json
import time
from datetime import datetime

BASE_URL = "https://dharaifooddelivery.in"

def req(method, path, token=None, payload=None):
    url = f"{BASE_URL}{path}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    if method == "GET":
        response = requests.get(url, headers=headers, timeout=10)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=payload, timeout=10)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=payload, timeout=10)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers, timeout=10)
    
    print(f"{method} {path} -> {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {data}")
        return response.status_code, data
    except:
        return response.status_code, None

def get_token(role, phone):
    print(f"\n[{role.upper()}] Getting token for {phone}...")
    if role == "customer":
        prefix = "/customer/auth"
    elif role == "delivery":
        prefix = "/delivery-partner/auth"
    else:
        prefix = "/auth"
    
    status, res = req("POST", f"{prefix}/send-otp", payload={"phone_number": phone})
    if status != 200:
        return None
    otp = res.get("data", {}).get("otp") or "123456"
    status, res = req("POST", f"{prefix}/verify-otp", payload={"phone_number": phone, "otp_code": otp})
    return res.get("access_token")

def test_handover_visibility():
    print("=== TESTING HANDOVER VISIBILITY IN ACTIVE ORDERS ===")
    
    delivery_token = get_token("delivery", "+919000000001")
    customer_token = get_token("customer", "+919578757944")
    restaurant_token = get_token("restaurant", "+919786816188")
    
    if not all([delivery_token, customer_token, restaurant_token]):
        print("Failed to get tokens")
        return

    # 1. Place Order
    print("\n[STEP 1] Placing order...")
    req("DELETE", "/customer/cart", customer_token)
    req("POST", "/customer/cart/add", customer_token, {"restaurant_id": 4, "menu_item_id": 20, "quantity": 1})
    status, order_res = req("POST", "/customer/orders", customer_token, {"restaurant_id": 4, "address_id": 1, "payment_method": "online"})
    order_id = order_res['data']['order_id']
    print(f"Order ID: {order_id}")

    # 2. Restaurant Accepts and Marks as Ready
    print("\n[STEP 2] Restaurant accepts and marks as ready...")
    req("PUT", f"/orders/{order_id}/accept", restaurant_token)
    req("PUT", f"/orders/{order_id}/ready", restaurant_token)

    # 2.5 Check Available Orders - Should be there
    print("\n[STEP 2.5] Checking available orders (after ready)...")
    status, available = req("GET", "/delivery-partner/orders/available", delivery_token)
    found = any(o['id'] == order_id for o in (available if isinstance(available, list) else available.get('data', [])))
    print(f"Order {order_id} in available list: {found}")

    # 3. Delivery Partner Accepts
    print("\n[STEP 3] Delivery partner accepts...")
    req("POST", f"/delivery-partner/orders/{order_id}/accept", delivery_token)

    # 4. Check Active Orders - Should be there (status 'assigned')
    print("\n[STEP 4] Checking active orders (after accept)...")
    status, active = req("GET", "/delivery-partner/orders/active", delivery_token)
    found = any(o['id'] == order_id for o in (active if isinstance(active, list) else active.get('data', [])))
    print(f"Order {order_id} in active list: {found}")

    # 5. Restaurant Marks as Hand Over
    print("\n[STEP 5] Restaurant marks as Hand Over...")
    req("PUT", f"/orders/{order_id}/handover", restaurant_token)

    # 6. Check Active Orders AGAIN - Should STILL be there (status 'handed_over')
    print("\n[STEP 6] Checking active orders (after handover)...")
    status, active = req("GET", "/delivery-partner/orders/active", delivery_token)
    active_list = active if isinstance(active, list) else active.get('data', [])
    found = False
    for o in active_list:
        if o['id'] == order_id:
            found = True
            print(f"Order {order_id} found! Status: {o['status']}")
            break
    
    if found:
        print("=== TEST SUCCESSFUL: Order remained visible after handover! ===")
    else:
        print("=== TEST FAILED: Order disappeared after handover! ===")

if __name__ == "__main__":
    test_handover_visibility()
