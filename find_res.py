import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# New owner 5 token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgyOTc5OX0.oLPxK8QiJ9Gt-ucxMj0x9BJDxcxeggECj6SYVj5OKxM"

def find_res():
    # Fetch ongoing orders from restaurant side
    r = requests.get(f"{BASE_URL}/orders/ongoing", headers={"Authorization": f"Bearer {TOKEN}"})
    data = r.json()
    print(f"Ongoing orders: {json.dumps(data, indent=2)}")
    
    # Try to find a restaurant detail endpoint
    # The /auth/profile doesn't work, maybe /restaurant/profile?
    # Let's check schemas.py for RestaurantResponse
    pass

if __name__ == "__main__":
    find_res()
