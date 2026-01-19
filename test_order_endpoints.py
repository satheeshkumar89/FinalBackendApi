"""
Test script to verify the order status filter fix
"""
import requests
import json

# Base URL
BASE_URL = "https://dharaifooddelivery.in"

# Your auth token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6MiwicGhvbmVfbnVtYmVyIjoiKzkxOTc4Nzc5MjAzMSIsImV4cCI6MTc2ODgwOTM2Mn0.wXtnKzRDJHel_0f6cb4J-zWjI-rGXRa-2bopHodl7zE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

print("Testing Order Endpoints...")
print("=" * 60)

# Test /orders/new
print("\n1. Testing /orders/new...")
try:
    response = requests.get(f"{BASE_URL}/orders/new", headers=headers)
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {data['message']}")
        print(f"   Orders count: {len(data['data']['orders'])}")
    else:
        print(f"   ✗ Error: {response.text}")
except Exception as e:
    print(f"   ✗ Exception: {str(e)}")

# Test /orders/ongoing
print("\n2. Testing /orders/ongoing...")
try:
    response = requests.get(f"{BASE_URL}/orders/ongoing", headers=headers)
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {data['message']}")
        print(f"   Orders count: {len(data['data']['orders'])}")
    else:
        print(f"   ✗ Error: {response.text}")
except Exception as e:
    print(f"   ✗ Exception: {str(e)}")

# Test /orders/completed
print("\n3. Testing /orders/completed...")
try:
    response = requests.get(f"{BASE_URL}/orders/completed", headers=headers)
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {data['message']}")
        print(f"   Orders count: {len(data['data']['orders'])}")
    else:
        print(f"   ✗ Error: {response.text}")
except Exception as e:
    print(f"   ✗ Exception: {str(e)}")

print("\n" + "=" * 60)
print("Test completed!")
