import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
# Restaurant owner token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgxODUzNn0.Ks8SFxfROssCsEf1sF-VIZ_BWvbqcsZ5eQetPezyDd0"
ORDER_ID = 47

def test_handover():
    url = f"{BASE_URL}/orders/{ORDER_ID}/handover"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    
    print(f"Testing PUT {url}")
    try:
        response = requests.put(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_handover()
