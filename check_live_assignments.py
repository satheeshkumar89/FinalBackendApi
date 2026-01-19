import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Restaurant token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgyNjk1Mn0.k4KKPh0a4Snzirv8Z_p-7IaA39adQLWrvWVk96iZhHg"

def req(path):
    url = f"{BASE_URL}{path}"
    headers = {"accept": "application/json", "Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json()

def check_unassigned():
    print("\n--- CHECKING ALL ONGOING ORDERS AND THEIR ASSIGNMENTS ---")
    data = req("/orders/ongoing")
    orders = data.get('data', {}).get('orders', [])
    
    unassigned_count = 0
    assigned_count = 0
    
    for o in orders:
        oid = o['order_id']
        status = o['status']
        
        # We need a way to see if there's a delivery partner.
        # Let's try the customer tracking endpoint? No, probably need customer token.
        # Let's try the generic /orders/{id}
        d = req(f"/orders/{oid}")
        details = d.get('data', {})
        
        # In a well-structured API, the details should show partner info.
        partner = details.get('delivery_partner')
        partner_id = details.get('delivery_partner_id')
        
        if not partner and not partner_id:
            print(f"ID: {oid} - Status: {status} - UNASSIGNED")
            unassigned_count += 1
        else:
            print(f"ID: {oid} - Status: {status} - Assigned to Partner ID: {partner_id or partner.get('id')}")
            assigned_count += 1
            
    print(f"\nSummary: {unassigned_count} Unassigned, {assigned_count} Assigned")

if __name__ == "__main__":
    check_unassigned()
