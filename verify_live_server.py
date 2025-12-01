import requests
import json
import sys

BASE_URL = "https://dharaifooddelivery.in"
# BASE_URL = "http://localhost:8000" # Uncomment to test local

def print_step(step, success, details=None):
    icon = "✅" if success else "❌"
    print(f"{icon} {step}")
    if details:
        if isinstance(details, dict) or isinstance(details, list):
            print(json.dumps(details, indent=2))
        else:
            print(f"   {details}")

print(f"🔍 Testing Live Server: {BASE_URL}\n")

# 1. Check Server Health (Docs)
try:
    resp = requests.get(f"{BASE_URL}/docs", timeout=10)
    print_step("Server Reachable (Docs)", resp.status_code == 200)
except Exception as e:
    print_step("Server Reachable", False, str(e))
    sys.exit(1)

# 2. Owner Auth (Send OTP)
phone = "+919999999999"
print("\n--- 1. Authentication ---")
try:
    resp = requests.post(f"{BASE_URL}/auth/send-otp", json={"phone_number": phone})
    print_step("Send OTP", resp.status_code == 200, resp.json() if resp.status_code != 200 else None)
    
    # Verify OTP (Backdoor 123456)
    resp = requests.post(f"{BASE_URL}/auth/verify-otp", json={"phone_number": phone, "otp_code": "123456"})
    if resp.status_code != 200:
        # Try with 'otp' field just in case old code is running
        resp = requests.post(f"{BASE_URL}/auth/verify-otp", json={"phone_number": phone, "otp": "123456"})
    
    print_step("Verify OTP", resp.status_code == 200)
    
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"   Token: {token[:10]}...")
        
        # 3. Check Owner Details
        print("\n--- 2. Owner Details ---")
        resp = requests.get(f"{BASE_URL}/owner/details", headers=headers)
        print_step("Get Owner Details", resp.status_code == 200, resp.json())
        
        # 4. Check Restaurant Details (The Problem Area)
        print("\n--- 3. Restaurant Details ---")
        resp = requests.get(f"{BASE_URL}/restaurant/details", headers=headers)
        print_step("Get Restaurant Details", resp.status_code == 200, resp.json() if resp.status_code != 200 else "OK")
        
        if resp.status_code == 200:
            rest_id = resp.json()["data"]["id"]
            
            # 5. Check Menu (The other Problem Area)
            print("\n--- 4. Menu ---")
            resp = requests.get(f"{BASE_URL}/menu/items/grouped", headers=headers)
            print_step("Get Menu Grouped", resp.status_code == 200, resp.json() if resp.status_code != 200 else "OK")
            
        else:
            print("   ⚠️ Skipping Menu check because Restaurant Details failed.")

except Exception as e:
    print(f"❌ Test Failed: {e}")
