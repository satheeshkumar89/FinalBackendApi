import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# New owner 5 token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgyOTc5OX0.oLPxK8QiJ9Gt-ucxMj0x9BJDxcxeggECj6SYVj5OKxM"

def check_64():
    r = requests.get(f"{BASE_URL}/orders/64", headers={"Authorization": f"Bearer {TOKEN}"})
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    check_64()
