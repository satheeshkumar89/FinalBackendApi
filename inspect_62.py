import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Use the restaurant token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgyNjk1Mn0.k4KKPh0a4Snzirv8Z_p-7IaA39adQLWrvWVk96iZhHg"

def req(path):
    url = f"{BASE_URL}{path}"
    headers = {"accept": "application/json", "Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json()

def inspect_order_62():
    print("Inspecting Order #62...")
    d = req("/orders/62")
    data = d.get('data', {})
    print(f"Status: {data.get('status')}")
    print(f"Delivery Partner ID: {data.get('delivery_partner_id')}")
    print(f"Delivery Partner Object: {data.get('delivery_partner')}")
    
    # Check what the delivery partner API sees for available
    d_url = f"{BASE_URL}/delivery-partner/auth/verify-otp"
    dr = requests.post(d_url, json={"phone_number": "+919000000001", "otp_code": "123456"})
    dt = dr.json().get('access_token')
    
    if dt:
        da = requests.get(f"{BASE_URL}/delivery-partner/orders/available", headers={"Authorization": f"Bearer {dt}"})
        print(f"Full Available Response: {da.json()}")
    else:
        print("No delivery token")

if __name__ == "__main__":
    inspect_order_62()
