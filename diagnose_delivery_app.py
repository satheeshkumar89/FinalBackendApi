import requests
import json

BASE_URL = "https://dharaifooddelivery.in"

def get_token(role, phone):
    if role == "customer":
        prefix = "/customer/auth"
    elif role == "delivery":
        prefix = "/delivery-partner/auth"
    else:
        prefix = "/auth"
    
    # Try with Dev OTP
    status, res = req("POST", f"{prefix}/verify-otp", payload={"phone_number": phone, "otp_code": "123456"})
    if status == 200:
        return res.get("access_token")
    
    # Try sending OTP first
    req("POST", f"{prefix}/send-otp", payload={"phone_number": phone})
    status, res = req("POST", f"{prefix}/verify-otp", payload={"phone_number": phone, "otp_code": "123456"})
    return res.get("access_token")

def req(method, path, token=None, payload=None):
    url = f"{BASE_URL}{path}"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if method == "GET": response = requests.get(url, headers=headers)
    elif method == "POST": response = requests.post(url, headers=headers, json=payload)
    elif method == "PUT": response = requests.put(url, headers=headers, json=payload)
    
    try: return response.status_code, response.json()
    except: return response.status_code, response.text

def diagnose():
    # 1. Check Available Orders (Unassigned)
    print("\n--- CHECKING AVAILABLE ORDERS (UNASSIGNED) ---")
    d_token = get_token("delivery", "+919000000001")
    if not d_token:
        print("Failed to get delivery token")
        return
        
    s, data = req("GET", "/delivery-partner/orders/available", d_token)
    print(f"Status: {s}")
    orders = data if isinstance(data, list) else data.get('data', [])
    print(f"Total Available: {len(orders)}")
    for o in orders:
        print(f"ID: {o['id']}, Status: {o['status']}, Restaurant: {o['restaurant_name']}")

    # 2. Check Active Orders (Assigned to this partner)
    print("\n--- CHECKING ACTIVE ORDERS (ASSIGNED TO THIS PARTNER) ---")
    s, data = req("GET", "/delivery-partner/orders/active", d_token)
    print(f"Status: {s}")
    active = data if isinstance(data, list) else data.get('data', [])
    print(f"Total Active: {len(active)}")
    for o in active:
        print(f"ID: {o['id']}, Status: {o['status']}, Restaurant: {o['restaurant_name']}")

if __name__ == "__main__":
    diagnose()
