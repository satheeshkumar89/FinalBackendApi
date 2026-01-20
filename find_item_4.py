import requests
import json

BASE_URL = "https://dharaifooddelivery.in"

def get_token(role, phone):
    prefix = "/customer/auth" if role == "customer" else "/delivery-partner/auth"
    if role == "restaurant": prefix = "/auth"
    
    r = requests.post(f"{BASE_URL}{prefix}/verify-otp", json={"phone_number": phone, "otp_code": "123456"})
    if r.status_code == 200:
        return r.json().get("access_token")
    return None

def find_item_for_res_4():
    token = get_token("customer", "+919578757944")
    if not token: return
    
    r = requests.get(f"{BASE_URL}/customer/restaurants/4", headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    menu = data.get('data', {}).get('menu', [])
    if menu:
        print(f"Restaurant 4 Item ID: {menu[0]['id']}, Name: {menu[0]['name']}")
    else:
        print("No menu found for restaurant 4")

if __name__ == "__main__":
    find_item_for_res_4()
