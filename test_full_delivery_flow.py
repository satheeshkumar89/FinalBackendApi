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
        prefix = "/auth" # Restaurant/Owner
    
    status, res = req("POST", f"{prefix}/send-otp", payload={"phone_number": phone})
    if status != 200:
        print(f"Failed to send OTP: {res}")
        return None
    
    otp = res.get("data", {}).get("otp")
    if not otp:
        otp = "123456"
        
    status, res = req("POST", f"{prefix}/verify-otp", payload={"phone_number": phone, "otp_code": otp})
    if status != 200 or not res.get("access_token"):
        print(f"Failed to verify OTP: {res}")
        return None
    
    return res.get("access_token")

def test_flow():
    print("=== STARTING FULL ORDER FLOW TEST ===")
    
    delivery_token = get_token("delivery", "+919000000001")
    customer_token = get_token("customer", "+919578757944")
    restaurant_token = get_token("restaurant", "+919786816188")
    
    if not delivery_token or not customer_token or not restaurant_token:
        print("Cannot proceed without tokens")
        return

    # 0. Ensure Delivery Boy is Online
    print("\n[DELIVERY] Setting status to online...")
    req("POST", "/delivery-partner/status/toggle", delivery_token, {"is_online": True})

    # 1. Place Order (Customer)
    print("\n[CUSTOMER] Preparing cart...")
    req("DELETE", "/customer/cart", customer_token)
    cart_payload = {
        "restaurant_id": 4,
        "menu_item_id": 20,
        "quantity": 1
    }
    status, cart_res = req("POST", "/customer/cart/add", customer_token, cart_payload)
    if status != 200:
        print(f"Failed to add to cart: {cart_res}")
        return

    print("[CUSTOMER] Placing order...")
    order_payload = {
        "restaurant_id": 4, 
        "address_id": 1,
        "payment_method": "online"
    }
    status, order_res = req("POST", "/customer/orders", customer_token, order_payload)
    if status not in [200, 201] or not order_res.get('data', {}).get('order_id'):
        print(f"Failed to place order: {order_res}")
        return
    order_id = order_res['data']['order_id']
    print(f"Order ID: {order_id}")

    # 2. Accept Order (Restaurant)
    print("\n[RESTAURANT] Accepting order...")
    req("PUT", f"/orders/{order_id}/accept", restaurant_token)

    # 3. Preparing -> Ready (Restaurant)
    print("\n[RESTAURANT] Preparing order...")
    req("PUT", f"/orders/{order_id}/preparing", restaurant_token)
    print("\n[RESTAURANT] Mark as Ready...")
    req("PUT", f"/orders/{order_id}/ready", restaurant_token)

    # 4. Hand Over (Restaurant)
    print("\n[RESTAURANT] Handing over order...")
    req("PUT", f"/orders/{order_id}/handover", restaurant_token)
    
    print("\n[CHECK] Verifying order remains in ongoing list for restaurant...")
    status, ongoing = req("GET", "/orders/ongoing", restaurant_token)
    found_ongoing = False
    if ongoing and ongoing.get("data"):
        for o in ongoing["data"]["orders"]:
            if o["order_id"] == order_id:
                found_ongoing = True
                print(f"Order {order_id} is still in ongoing list. Good!")
                break
    if not found_ongoing:
        print(f"Order {order_id} DISAPPEARED from ongoing list! BUG!")

    # 5. Check Available Orders (Delivery Boy)
    print("\n[DELIVERY] Checking available orders...")
    time.sleep(1)
    status, available = req("GET", "/delivery-partner/orders/available", delivery_token)
    found = False
    # For available orders, it's a list directly usually or in 'data'
    orders_list = available if isinstance(available, list) else available.get("data", [])
    if orders_list:
        for o in orders_list:
            if o['id'] == order_id:
                found = True
                print(f"Order {order_id} found in available list!")
                break
    if not found:
        print(f"Order {order_id} NOT found in available list.")

    # 6. Accept Order (Delivery Boy)
    print("\n[DELIVERY] Accepting order...")
    status, res = req("POST", f"/delivery-partner/orders/{order_id}/accept", delivery_token)
    if status == 200:
        print("Order accepted by Delivery Partner.")
        
        # Check restaurant status update
        print("\n[CHECK] Verifying restaurant status updated to ASSIGNED...")
        status, details = req("GET", f"/orders/{order_id}", restaurant_token)
        if details and details.get('data', {}).get('status') == 'assigned':
            print("Status updated to assigned in restaurant app. Good!")
        else:
            print(f"Status mismatch: {details.get('data', {}).get('status') if details else 'N/A'}")
    else:
        print(f"Failed to accept: {res}")

    # 7. Reached Restaurant (Delivery Boy)
    print("\n[DELIVERY] Reached restaurant...")
    req("POST", f"/delivery-partner/orders/{order_id}/reached", delivery_token)
    
    print("\n[CHECK] Verifying restaurant status updated to REACHED_RESTAURANT (reached_restaurant)...")
    status, details = req("GET", f"/orders/{order_id}", restaurant_token)
    if details and details.get('data', {}).get('status') == 'reached_restaurant':
        print("Status updated to reached_restaurant in restaurant app. Good!")

    # 8. Picked Up (Delivery Boy)
    print("\n[DELIVERY] Picking up order...")
    req("POST", f"/delivery-partner/orders/{order_id}/pickup", delivery_token)
    
    print("\n[CHECK] Verifying restaurant status updated to PICKED_UP (picked_up)...")
    status, details = req("GET", f"/orders/{order_id}", restaurant_token)
    if details and details.get('data', {}).get('status') == 'picked_up':
        print("Status updated to picked_up in restaurant app. Good!")

    # 9. Complete Delivery (Delivery Boy)
    print("\n[DELIVERY] Completing delivery...")
    req("POST", f"/delivery-partner/orders/{order_id}/complete", delivery_token)

    # 10. Final Verification
    print("\n[VERIFICATION] Checking final status...")
    status, final = req("GET", f"/orders/{order_id}", restaurant_token)
    if final:
        status_val = final.get('data', {}).get('status')
        print(f"Final order status: {status_val}")
        if status_val == "delivered":
            print("=== TEST SUCCESSFUL ===")
            
            # Check completed list
            print("\n[CHECK] Verifying order is in completed list...")
            status, completed = req("GET", "/orders/completed", restaurant_token)
            found_comp = False
            if completed and completed.get("data"):
                for o in completed["data"]["orders"]:
                    if o["order_id"] == order_id:
                        found_comp = True
                        break
            if found_comp:
                print("Order found in completed list. Good!")
            else:
                print("Order NOT found in completed list.")
        else:
            print(f"=== TEST FAILED: Status is {status_val} ===")

if __name__ == "__main__":
    test_flow()
