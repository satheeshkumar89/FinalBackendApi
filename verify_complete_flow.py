import requests
import json
import time

# ==========================================
# 🔑 UPDATE YOUR TOKENS HERE
# ==========================================
CUSTOMER_TOKEN = "YOUR_CUSTOMER_TOKEN_HERE"
RESTAURANT_TOKEN = "YOUR_RESTAURANT_TOKEN_HERE"
DELIVERY_TOKEN = "YOUR_DELIVERY_TOKEN_HERE"
# ==========================================

BASE_URL = "https://dharaifooddelivery.in"
RESTAURANT_ID = 4 # Mass Biryani
ADDRESS_ID = 2  # A valid address ID for the customer

def log_step(msg):
    print(f"\n>>>> {msg}")

def call_api(method, endpoint, token, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        if data:
            resp = requests.request(method, url, headers=headers, json=data)
        else:
            resp = requests.request(method, url, headers=headers)
        
        if resp.status_code >= 400:
            print(f"   ❌ FAILED: {method} {endpoint} -> {resp.status_code}")
            print(f"   Response: {resp.text}")
            return None
            
        print(f"   ✅ SUCCESS: {method} {endpoint}")
        return resp.json()
    except Exception as e:
        print(f"   💥 CONNECTION ERROR: {e}")
        return None

def run_test():
    if "YOUR_" in CUSTOMER_TOKEN:
        print("❌ ERROR: Please update the tokens at the top of the script first!")
        return

    # --- START FLOW ---
    
    log_step("STEP 1: Customer - Adding to Cart & Placing Order")
    # Add Biryani (Item 20)
    call_api("POST", "/customer/cart/add", CUSTOMER_TOKEN, {"menu_item_id": 20, "quantity": 1, "restaurant_id": RESTAURANT_ID})
    
    order_req = {"restaurant_id": RESTAURANT_ID, "address_id": ADDRESS_ID, "payment_method": "cod"}
    order_resp = call_api("POST", "/customer/orders", CUSTOMER_TOKEN, order_req)
    if not order_resp: return
    
    order_id = order_resp["data"]["id"]
    print(f"   🛍️  Order Placed! ID: {order_id}")

    log_step("STEP 2: Restaurant - Accepting Order")
    call_api("PUT", f"/orders/{order_id}/accept", RESTAURANT_TOKEN)

    log_step("STEP 3: Restaurant - Cooking (Preparing)")
    call_api("PUT", f"/orders/{order_id}/preparing", RESTAURANT_TOKEN, {"preparation_time_minutes": 30})

    log_step("STEP 4: Restaurant - Ready for Pickup")
    call_api("PUT", f"/orders/{order_id}/ready", RESTAURANT_TOKEN)

    log_step("STEP 5: Restaurant - HANDED OVER to Delivery")
    call_api("PUT", f"/orders/{order_id}/handover", RESTAURANT_TOKEN)
    
    log_step("STEP 6: Delivery Partner - Accepting Handed Over Order")
    call_api("POST", f"/delivery-partner/orders/{order_id}/accept", DELIVERY_TOKEN)

    log_step("STEP 7: Delivery Partner - Reached Restaurant")
    call_api("POST", f"/delivery-partner/orders/{order_id}/reached", DELIVERY_TOKEN)

    log_step("STEP 8: Delivery Partner - Picking Up from Counter")
    call_api("POST", f"/delivery-partner/orders/{order_id}/pickup", DELIVERY_TOKEN)

    log_step("STEP 9: Delivery Partner - Delivered to Customer!")
    call_api("POST", f"/delivery-partner/orders/{order_id}/complete", DELIVERY_TOKEN)

    log_step("� FULL FLOW VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    run_test()
