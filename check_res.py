import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Restaurant token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgyNjk1Mn0.k4KKPh0a4Snzirv8Z_p-7IaA39adQLWrvWVk96iZhHg"

def check_owner():
    # The /profile endpoint for owner might be /auth/profile or /owner/profile
    # Let's check main.py
    pass

if __name__ == "__main__":
    # Just try /orders/ongoing again and print everything
    r = requests.get(f"{BASE_URL}/orders/ongoing", headers={"Authorization": f"Bearer {TOKEN}"})
    print(json.dumps(r.json(), indent=2))
