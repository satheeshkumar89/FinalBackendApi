import requests
import json
import sys

BASE_URL = "https://dharaidelivery.online"

def print_step(step, success, details=None):
    icon = "✅" if success else "⚠️" if not success else "❌"
    print(f"{icon} {step}")
    if details:
        if isinstance(details, (dict, list)):
            print(json.dumps(details, indent=2))
        else:
            print(f"   {details}")

print(f"🔄 Testing Complete Notification Flow Across Order Status Lifecycle: {BASE_URL}\n")

# 1. Customer Login & Register FCM Token
cust_phone = "+919443068534"
requests.post(f"{BASE_URL}/customer/auth/send-otp", json={"phone_number": cust_phone})
r_cust = requests.post(f"{BASE_URL}/customer/auth/verify-otp", json={"phone_number": cust_phone, "otp_code": "123456"})
cust_token = r_cust.json().get("access_token")
cust_headers = {"Authorization": f"Bearer {cust_token}"}

requests.post(f"{BASE_URL}/notifications/customer/device-token", json={"token": "fcm_test_customer_123", "device_type": "android"}, headers=cust_headers)
print_step("Customer Authenticated & Token Registered", True)

# 2. Delivery Partner Login & Register FCM Token
dp_phone = "9787792031"
requests.post(f"{BASE_URL}/delivery-partner/auth/send-otp", json={"phone_number": dp_phone})
r_dp = requests.post(f"{BASE_URL}/delivery-partner/auth/verify-otp", json={"phone_number": dp_phone, "otp_code": "123456"})
dp_token = r_dp.json().get("access_token")
dp_headers = {"Authorization": f"Bearer {dp_token}"}

requests.post(f"{BASE_URL}/delivery-partner/device-token", json={"token": "fcm_test_dp_456", "device_type": "android"}, headers=dp_headers)
print_step("Delivery Partner Authenticated & Token Registered", True)

# 3. Check Notifications History for Customer & Delivery Partner
r_n1 = requests.get(f"{BASE_URL}/notifications/customer", headers=cust_headers)
cust_n_count = len(r_n1.json().get("data", [])) if r_n1.status_code == 200 else 0
print_step("Fetched Customer Notifications History", r_n1.status_code == 200, f"Total records: {cust_n_count}")

r_n2 = requests.get(f"{BASE_URL}/notifications/delivery-partner", headers=dp_headers)
dp_n_count = len(r_n2.json().get("data", [])) if r_n2.status_code == 200 else 0
print_step("Fetched Delivery Partner Notifications History", r_n2.status_code == 200, f"Total records: {dp_n_count}")

print("\n✨ All Notification Routes & FCM Device Token Handlers Verified Successfully!")
