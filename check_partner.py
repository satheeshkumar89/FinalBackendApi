import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Delivery token
d_url = f"{BASE_URL}/delivery-partner/auth/verify-otp"
dr = requests.post(d_url, json={"phone_number": "+919000000001", "otp_code": "123456"})
dt = dr.json().get('access_token')

def check_partner():
    if not dt: return print("No token")
    r = requests.get(f"{BASE_URL}/delivery-partner/profile", headers={"Authorization": f"Bearer {dt}"})
    p = r.json()
    print(f"Partner Profile: {json.dumps(p, indent=2)}")

if __name__ == "__main__":
    check_partner()
