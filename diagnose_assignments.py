import requests
import json

BASE_URL = "https://dharaifooddelivery.in"

def req(method, path, token=None, payload=None):
    url = f"{BASE_URL}{path}"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    if token: headers["Authorization"] = f"Bearer {token}"
    if method == "GET": response = requests.get(url, headers=headers)
    elif method == "POST": response = requests.post(url, headers=headers, json=payload)
    try: return response.status_code, response.json()
    except: return response.status_code, response.text

def diagnose_all():
    # We use the restaurant token provided by the user to see all ongoing orders
    res_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgyNjk1Mn0.k4KKPh0a4Snzirv8Z_p-7IaA39adQLWrvWVk96iZhHg"
    
    print("\n--- FETCHING ALL ONGOING ORDERS FROM RESTAURANT SIDE ---")
    s, data = req("GET", "/orders/ongoing", res_token)
    if s != 200:
        print(f"Failed to fetch ongoing orders: {s} {data}")
        return
        
    orders = data.get('data', {}).get('orders', [])
    print(f"Total Ongoing: {len(orders)}")
    
    for o in orders:
        order_id = o['order_id']
        status = o['status']
        print(f"\nChecking Delivery Details for Order #{order_id} (Status: {status})")
        
        # We need a way to see the delivery_partner_id. 
        # The /orders/{id} endpoint might have it.
        s2, details = req("GET", f"/orders/{order_id}", res_token)
        if s2 == 200:
            d = details.get('data', {})
            # Note: The response schema might not have partner_id directly, 
            # but let's see what's there.
            print(f"Details: {json.dumps(d, indent=2)[:500]}")
            # Try to find partner info
            if 'delivery_partner_id' in d: # If owner can see it
                print(f"  Partner ID: {d['delivery_partner_id']}")
            elif 'delivery_partner' in d:
                print(f"  Partner: {d['delivery_partner'].get('full_name') if d['delivery_partner'] else 'NONE'}")
        else:
            print(f"  Could not fetch details: {s2}")

if __name__ == "__main__":
    diagnose_all()
