import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Owner 5 token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgyNjk1Mn0.k4KKPh0a4Snzirv8Z_p-7IaA39adQLWrvWVk96iZhHg"

def find_res_id():
    # Try to find restaurant ID for the current owner
    # The /profile might show it
    r = requests.get(f"{BASE_URL}/profile", headers={"Authorization": f"Bearer {TOKEN}"})
    print(f"Profile: {r.status_code} {r.json()}")
    
    # Try get_current_restaurant logic (it's internal to backend)
    # But maybe there's a /restaurant endpoint?
    # Let's check main.py for routers.
    pass

if __name__ == "__main__":
    find_res_id()
    # Or just check ongoing again and look for common restaurant IDs?
    r = requests.get(f"{BASE_URL}/orders/ongoing", headers={"Authorization": f"Bearer {TOKEN}"})
    data = r.json()
    orders = data.get('data', {}).get('orders', [])
    if orders:
        # Fetch one order detail
        oid = orders[0]['order_id']
        r = requests.get(f"{BASE_URL}/orders/{oid}", headers={"Authorization": f"Bearer {TOKEN}"})
        print(f"Order Detail for {oid}: {r.json()}")
