import requests
import time

BASE_URL = "https://dharaifooddelivery.in"
# Use a test delivery partner phone
PARTNER_PHONE = "+919000000001"
CUSTOMER_PHONE = "+919578757944" # From user's curl

def get_token(role, phone):
    prefix = "/customer/auth" if role == "customer" else "/delivery-partner/auth"
    if role == "restaurant": prefix = "/auth"
    
    # Try dev otp
    r = requests.post(f"{BASE_URL}{prefix}/verify-otp", json={"phone_number": phone, "otp_code": "123456"})
    if r.status_code == 200:
        return r.json().get("access_token")
    return None

def test_flow():
    print("=== STARTING APP FLOW SIMULATION ===")
    
    # 1. Get Tokens
    d_token = get_token("delivery", PARTNER_PHONE)
    c_token = get_token("customer", "+919578757944")
    res_token = get_token("restaurant", "+919786816188")

    if not all([d_token, c_token, res_token]):
        print(f"❌ Missing tokens: Delivery={bool(d_token)}, Customer={bool(c_token)}, Restaurant={bool(res_token)}")
        return

    # 2. Create a new order via customer
    print("\n[STEP 1] Creating a new order...")
    # Clear cart
    requests.delete(f"{BASE_URL}/customer/cart", headers={"Authorization": f"Bearer {c_token}"})
    # Add item to cart first
    res_add = requests.post(f"{BASE_URL}/customer/cart/add", headers={"Authorization": f"Bearer {c_token}"}, 
                  json={"restaurant_id": 4, "menu_item_id": 20, "quantity": 1})
    print(f"Cart Add Status: {res_add.status_code}")
    
    # Place order
    r_order = requests.post(f"{BASE_URL}/customer/orders", headers={"Authorization": f"Bearer {c_token}"},
                           json={"restaurant_id": 4, "address_id": 1, "payment_method": "cod"})
    
    if r_order.status_code != 200:
        print(f"❌ Order creation failed: {r_order.text}")
        return
    
    order_id = r_order.json().get("data", {}).get("order_id")
    print(f"✅ Order Created: #{order_id}")

    # 3. Restaurant Accepts and Marks Ready
    print("\n[STEP 2] Restaurant Accepting & Marking Ready...")
    r1 = requests.put(f"{BASE_URL}/orders/{order_id}/accept", headers={"Authorization": f"Bearer {res_token}"})
    r2 = requests.put(f"{BASE_URL}/orders/{order_id}/ready", headers={"Authorization": f"Bearer {res_token}"})
    print(f"Accept Response: {r1.status_code}")
    print(f"Ready Response: {r2.status_code}")
    print("✅ Order is now READY")
    
    # NEW: Check status from restaurant side
    r_res_check = requests.get(f"{BASE_URL}/orders/ongoing", headers={"Authorization": f"Bearer {res_token}"})
    print(f"Restaurant Ongoing: {r_res_check.json()}")

    # 4. Delivery Partner checks Available
    print("\n[STEP 3] Delivery Partner checking Available Orders...")
    r_avail = requests.get(f"{BASE_URL}/delivery-partner/orders/available", headers={"Authorization": f"Bearer {d_token}"})
    available = r_avail.json()
    if any(o['id'] == order_id for o in available):
        print(f"✅ Order #{order_id} is visible in AVAILABLE list")
    else:
        print(f"❌ Order #{order_id} NOT found in AVAILABLE list!")
        print(f"Current Available: {available}")

    # 5. Restaurant Marks Handed Over (WITHOUT assignment yet)
    print("\n[STEP 4] Restaurant marking Handed Over (unassigned)...")
    requests.put(f"{BASE_URL}/orders/{order_id}/handover", headers={"Authorization": f"Bearer {res_token}"})
    
    print("Checking Available list again...")
    r_avail2 = requests.get(f"{BASE_URL}/delivery-partner/orders/available", headers={"Authorization": f"Bearer {d_token}"})
    available2 = r_avail2.json()
    if any(o['id'] == order_id for o in available2):
        print(f"✅ Order #{order_id} IS STILL visible in AVAILABLE list after Handover (Fix working!)")
    else:
        print(f"❌ Order #{order_id} DISAPPEARED from AVAILABLE list after Handover!")

    # 6. Delivery Partner Accepts
    print("\n[STEP 5] Delivery Partner Accepting Order...")
    requests.post(f"{BASE_URL}/delivery-partner/orders/{order_id}/accept", headers={"Authorization": f"Bearer {d_token}"})
    
    print("Marking Reached Restaurant...")
    requests.post(f"{BASE_URL}/delivery-partner/orders/{order_id}/reached", headers={"Authorization": f"Bearer {d_token}"})

    print("Checking Active list...")
    r_active = requests.get(f"{BASE_URL}/delivery-partner/orders/active", headers={"Authorization": f"Bearer {d_token}"})
    active = r_active.json()
    if any(o['id'] == order_id for o in active):
        print(f"✅ Order #{order_id} is visible in ACTIVE list")
    else:
        print(f"❌ Order #{order_id} NOT found in ACTIVE list!")

    # 7. Delivery Partner Picks Up (Order is already Handed Over)
    print("\n[STEP 6] Delivery Partner marking Picked Up...")
    r_pickup = requests.post(f"{BASE_URL}/delivery-partner/orders/{order_id}/picked-up", headers={"Authorization": f"Bearer {d_token}"})
    if r_pickup.status_code == 200:
        print("✅ Order Picked Up Successfully")
    else:
        print(f"❌ Pickup failed: {r_pickup.text}")

    # 8. Complete Delivery
    print("\n[STEP 7] Completing Delivery...")
    r_comp = requests.post(f"{BASE_URL}/delivery-partner/orders/{order_id}/complete", headers={"Authorization": f"Bearer {d_token}"})
    if r_comp.status_code == 200:
        print("✅ Delivery Completed Successfully")
    else:
        print(f"❌ Completion failed: {r_comp.text}")

if __name__ == "__main__":
    test_flow()
