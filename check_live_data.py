import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Use the restaurant token provided
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgyNjk1Mn0.k4KKPh0a4Snzirv8Z_p-7IaA39adQLWrvWVk96iZhHg"

def req(path):
    url = f"{BASE_URL}{path}"
    headers = {"accept": "application/json", "Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json()

def check_all_orders():
    print("\n[RESTAURANT] Ongoing Orders:")
    data = req("/orders/ongoing")
    orders = data.get('data', {}).get('orders', [])
    for o in orders:
        oid = o['order_id']
        status = o['status']
        # Fetch more details if possible
        d = req(f"/orders/{oid}")
        order_details = d.get('data', {})
        partner_info = order_details.get('delivery_partner_id', 'NONE')
        # If the schema doesn't have it, try to find in another way
        print(f"ID: {oid}, Status: {status}, Partner: {partner_info}")

    print("\n[DELIVERY] Available Orders (API Check):")
    # Need a delivery token
    # (Assuming bypass works)
    d_url = f"{BASE_URL}/delivery-partner/auth/verify-otp"
    dr = requests.post(d_url, json={"phone_number": "+919000000001", "otp_code": "123456"})
    dt = dr.json().get('access_token')
    
    if dt:
        da = requests.get(f"{BASE_URL}/delivery-partner/orders/available", headers={"Authorization": f"Bearer {dt}"})
        av = da.json()
        print(f"Available: {json.dumps(av, indent=2)}")
    else:
        print("Could not get delivery token")

if __name__ == "__main__":
    check_all_orders()
