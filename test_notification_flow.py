import requests
import json
import sys

BASE_URL = "https://dharaidelivery.online"

def print_step(step, success, details=None):
    icon = "✅" if success else "❌"
    print(f"{icon} {step}")
    if details:
        if isinstance(details, (dict, list)):
            print(json.dumps(details, indent=2))
        else:
            print(f"   {details}")

print(f"🚀 Testing Full Notification Flow against: {BASE_URL}\n")

# 1. Health Check
try:
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    print_step("Server Health Check", resp.status_code == 200, resp.json() if resp.status_code == 200 else resp.text)
except Exception as e:
    print_step("Server Health Check", False, str(e))
    sys.exit(1)

# 2. Test Customer Authentication & Device Token Registration
print("\n--- 1. Customer Auth & Device Token ---")
cust_phone = "+919443068534"
cust_headers = {}
try:
    r = requests.post(f"{BASE_URL}/customer/auth/send-otp", json={"phone_number": cust_phone})
    print_step("Customer Send OTP", r.status_code == 200)
    
    r = requests.post(f"{BASE_URL}/customer/auth/verify-otp", json={"phone_number": cust_phone, "otp_code": "123456"})
    print_step("Customer Verify OTP", r.status_code == 200)
    if r.status_code == 200:
        token = r.json().get("access_token")
        cust_headers = {"Authorization": f"Bearer {token}"}
        
        # Register Customer Device Token
        r_tok = requests.post(
            f"{BASE_URL}/notifications/customer/device-token", 
            json={"token": "fcm_test_customer_token_999", "device_type": "android"},
            headers=cust_headers
        )
        print_step("Customer Register FCM Token", r_tok.status_code == 200, r_tok.json())
except Exception as e:
    print_step("Customer Auth Flow", False, str(e))

# 3. Test Delivery Partner Auth & Device Token Registration
print("\n--- 2. Delivery Partner Auth & Device Token ---")
dp_phone = "9787792031"
dp_headers = {}
try:
    r = requests.post(f"{BASE_URL}/delivery-partner/auth/send-otp", json={"phone_number": dp_phone})
    print_step("Delivery Partner Send OTP", r.status_code == 200)
    
    r = requests.post(f"{BASE_URL}/delivery-partner/auth/verify-otp", json={"phone_number": dp_phone, "otp_code": "123456"})
    print_step("Delivery Partner Verify OTP", r.status_code == 200)
    if r.status_code == 200:
        token = r.json().get("access_token")
        dp_headers = {"Authorization": f"Bearer {token}"}
        
        # Register Delivery Partner Device Token
        r_tok = requests.post(
            f"{BASE_URL}/delivery-partner/device-token", 
            json={"token": "fcm_test_dp_token_888", "device_type": "android"},
            headers=dp_headers
        )
        print_step("Delivery Partner Register FCM Token (/delivery-partner/device-token)", r_tok.status_code == 200, r_tok.json())
        
        r_tok2 = requests.post(
            f"{BASE_URL}/notifications/delivery-partner/device-token", 
            json={"token": "fcm_test_dp_token_888", "device_type": "android"},
            headers=dp_headers
        )
        print_step("Delivery Partner Register FCM Token (/notifications/delivery-partner/device-token)", r_tok2.status_code == 200, r_tok2.json())
except Exception as e:
    print_step("Delivery Partner Auth Flow", False, str(e))

# 4. Fetch Notifications Endpoint Check
print("\n--- 3. Fetch Notifications Endpoints Check ---")
try:
    r = requests.get(f"{BASE_URL}/notifications/customer", headers=cust_headers)
    print_step("Get Customer Notifications", r.status_code == 200, f"Retrieved {len(r.json().get('data', []))} notifications")
    
    r = requests.get(f"{BASE_URL}/notifications/delivery-partner", headers=dp_headers)
    print_step("Get Delivery Partner Notifications", r.status_code == 200, f"Retrieved {len(r.json().get('data', []))} notifications")
except Exception as e:
    print_step("Fetch Notifications Check", False, str(e))

print("\n✨ Notification Flow Test Completed!")
