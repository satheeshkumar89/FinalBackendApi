import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Restaurant token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgyNjk1Mn0.k4KKPh0a4Snzirv8Z_p-7IaA39adQLWrvWVk96iZhHg"

def check_restaurant():
    # Get profile of the restaurant (ID 5)
    r = requests.get(f"{BASE_URL}/profile", headers={"Authorization": f"Bearer {TOKEN}"})
    print(f"Restaurant Status: {json.dumps(r.json(), indent=2)}")

if __name__ == "__main__":
    check_restaurant()
