import requests
import json

BASE_URL = "https://dharaifooddelivery.in"

def find_res_id():
    # 1. Get a customer token
    r = requests.post(f"{BASE_URL}/customer/auth/verify-otp", json={"phone_number": "+919578757944", "otp_code": "123456"})
    token = r.json().get("access_token")
    if not token:
        print("No token")
        return

    # 2. List ALL restaurants (no filter)
    # The /customer/home has 'restaurants'
    r = requests.get(f"{BASE_URL}/customer/home", headers={"Authorization": f"Bearer {token}"})
    data = r.json().get('data', {})
    res = data.get('restaurants', [])
    for r in res:
        print(f"ID: {r['id']}, Name: {r['restaurant_name']}")

if __name__ == "__main__":
    find_res_id()
