import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Delivery token
d_url = f"{BASE_URL}/delivery-partner/auth/verify-otp"
dr = requests.post(d_url, json={"phone_number": "+919000000001", "otp_code": "123456"})
dt = dr.json().get('access_token')

def toggle_online():
    if not dt: return print("No token")
    # Toggle online
    r = requests.post(f"{BASE_URL}/delivery-partner/status/toggle", 
                     headers={"Authorization": f"Bearer {dt}"},
                     json={"is_online": True})
    print(f"Toggle Status: {r.status_code} {r.json()}")
    
    # Update location (Set to match the restaurant in Bangalore)
    # Mass Biryani is in Bangalore (from curl address)
    r2 = requests.post(f"{BASE_URL}/delivery-partner/location",
                      headers={"Authorization": f"Bearer {dt}"},
                      json={"latitude": 12.9716, "longitude": 77.5946})
    print(f"Location Update: {r2.status_code} {r2.json()}")
    
    # Check Available
    ra = requests.get(f"{BASE_URL}/delivery-partner/orders/available", headers={"Authorization": f"Bearer {dt}"})
    print(f"Available Orders: {json.dumps(ra.json(), indent=2)}")

if __name__ == "__main__":
    toggle_online()
