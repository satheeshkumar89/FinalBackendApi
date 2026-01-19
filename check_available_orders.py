import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Delivery partner token (Might be expired, will check)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZWxpdmVyeV9wYXJ0bmVyX2lkIjoxLCJwaG9uZV9udW1iZXIiOiIrOTE4NjY4MTA5NzEyIiwicm9sZSI6ImRlbGl2ZXJ5X3BhcnRuZXIiLCJleHAiOjE3Njg4MTQxNjl9.zvx7-wQlfCx9thUVWHxYeF1gYu9XqtDvLO-kIZ2jMAg"

def test_available_orders():
    url = f"{BASE_URL}/delivery-partner/orders/available"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    
    print(f"Testing GET {url}")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            orders = response.json()
            print(f"Total Available Orders: {len(orders)}")
            for order in orders:
                if order.get('id') == 47:
                    print("✅ Found Order 47 in available orders!")
                    return
            print("❌ Order 47 NOT found in available orders.")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_available_orders()
