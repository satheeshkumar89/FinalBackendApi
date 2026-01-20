import requests
import json

BASE_URL = "https://dharaifooddelivery.in"

def find_live_data():
    # 1. Get a customer token
    r = requests.post(f"{BASE_URL}/customer/auth/verify-otp", json={"phone_number": "+919578757944", "otp_code": "123456"})
    token = r.json().get("access_token")
    if not token:
        print("Could not get customer token")
        return

    # 2. List restaurants
    r = requests.get(f"{BASE_URL}/customer/home", headers={"Authorization": f"Bearer {token}"})
    home_data = r.json()
    print(f"Home Data: {json.dumps(home_data, indent=2)[:500]}")
    
    # Try to find a restaurant ID
    # Usually in data.popular_restaurants or something
    data = home_data.get('data', {})
    restaurants = data.get('restaurants', [])
    
    if restaurants:
        res_id = restaurants[0]['id']
        print(f"Using Restaurant ID: {res_id}")
        
        # 3. Get Menu
        r = requests.get(f"{BASE_URL}/customer/restaurants/{res_id}", headers={"Authorization": f"Bearer {token}"})
        menu_items = r.json().get('data', {}).get('menu', [])
        if menu_items:
            item_id = menu_items[0]['id']
            print(f"Using Menu Item ID: {item_id}")
            return res_id, item_id
    
    print("Could not find any live data")
    return None, None

if __name__ == "__main__":
    find_live_data()
