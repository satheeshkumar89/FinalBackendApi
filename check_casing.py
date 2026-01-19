import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Delivery token
d_url = f"{BASE_URL}/delivery-partner/auth/verify-otp"
dr = requests.post(d_url, json={"phone_number": "+919000000001", "otp_code": "123456"})
dt = dr.json().get('access_token')

def check_status(status_query):
    # This is a trick: we can't query directly, but we can see if available list changes if we had access.
    # But I can't change the code. 
    pass

# Let's try to fetch Order 62's status with exact casing
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgyNjk1Mn0.k4KKPh0a4Snzirv8Z_p-7IaA39adQLWrvWVk96iZhHg"
r = requests.get(f"{BASE_URL}/orders/62", headers={"Authorization": f"Bearer {TOKEN}"})
d = r.json().get('data', {})
print(f"RAW STATUS FROM DB: '{d.get('status')}'")
