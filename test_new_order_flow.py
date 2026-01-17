#!/usr/bin/env python3
"""
Test script for the new delivery partner order flow endpoints.
Tests the enhanced /reached endpoint and verifies filters.
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "https://dharaifooddelivery.in"
# BASE_URL = "http://localhost:8000"  # Uncomment for local testing

class DeliveryPartnerAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.partner_id: Optional[int] = None
        
    def send_otp(self, phone_number: str):
        """Send OTP to delivery partner phone."""
        url = f"{self.base_url}/delivery-partner/auth/send-otp"
        payload = {"phone_number": phone_number}
        
        print(f"\n📱 Sending OTP to {phone_number}...")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OTP sent successfully")
            if "otp" in data.get("data", {}):
                print(f"🔑 OTP: {data['data']['otp']}")
                return data['data']['otp']
        else:
            print(f"❌ Failed: {response.text}")
        return None
    
    def verify_otp(self, phone_number: str, otp: str):
        """Verify OTP and get access token."""
        url = f"{self.base_url}/delivery-partner/auth/verify-otp"
        payload = {"phone_number": phone_number, "otp_code": otp}
        
        print(f"\n🔐 Verifying OTP...")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.partner_id = data["delivery_partner"]["id"]
            print(f"✅ Logged in successfully")
            print(f"👤 Delivery Partner ID: {self.partner_id}")
            print(f"🎫 Token: {self.token[:50]}...")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
    
    def get_headers(self):
        """Get authorization headers."""
        if not self.token:
            raise Exception("Not authenticated! Please login first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_available_orders(self):
        """Get all available orders (READY status)."""
        url = f"{self.base_url}/delivery-partner/orders/available"
        
        print(f"\n📋 Fetching available orders...")
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ Found {len(orders)} available orders")
            
            for idx, order in enumerate(orders[:5], 1):  # Show first 5
                print(f"\n  {idx}. Order #{order['order_number']}")
                print(f"     ID: {order['id']}")
                print(f"     Restaurant: {order['restaurant_name']}")
                print(f"     Status: {order['status']}")
                print(f"     Amount: ${order['total_amount']}")
                
                # Verify status is READY
                if order['status'] != 'ready':
                    print(f"     ⚠️  WARNING: Order has status '{order['status']}' instead of 'ready'")
            
            return orders
        else:
            print(f"❌ Failed: {response.text}")
            return []
    
    def get_active_orders(self):
        """Get all active orders assigned to this partner."""
        url = f"{self.base_url}/delivery-partner/orders/active"
        
        print(f"\n📋 Fetching active orders...")
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ Found {len(orders)} active orders")
            
            for idx, order in enumerate(orders[:5], 1):
                print(f"\n  {idx}. Order #{order['order_number']}")
                print(f"     ID: {order['id']}")
                print(f"     Status: {order['status']}")
                print(f"     Amount: ${order['total_amount']}")
                
                # Verify status is in active statuses
                active_statuses = ['assigned', 'reached_restaurant', 'picked_up']
                if order['status'] not in active_statuses:
                    print(f"     ⚠️  WARNING: Unexpected status '{order['status']}'")
            
            return orders
        else:
            print(f"❌ Failed: {response.text}")
            return []
    
    def mark_reached_restaurant(self, order_id: int):
        """Mark that delivery partner has reached the restaurant."""
        url = f"{self.base_url}/delivery-partner/orders/{order_id}/reached"
        
        print(f"\n🏪 Marking reached restaurant for order {order_id}...")
        response = requests.post(url, headers=self.get_headers(), json={})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            print(f"   Order ID: {data['data']['order_id']}")
            print(f"   New Status: {data['data']['status']}")
            
            if data['data']['status'] != 'reached_restaurant':
                print(f"   ⚠️  WARNING: Expected status 'reached_restaurant' but got '{data['data']['status']}'")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
    
    def mark_picked_up(self, order_id: int):
        """Mark order as picked up from restaurant."""
        url = f"{self.base_url}/delivery-partner/orders/{order_id}/picked-up"
        
        print(f"\n📦 Marking order {order_id} as picked up...")
        response = requests.post(url, headers=self.get_headers(), json={})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            print(f"   Order ID: {data['data']['order_id']}")
            print(f"   New Status: {data['data']['status']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
    
    def mark_complete(self, order_id: int):
        """Mark order as delivered."""
        url = f"{self.base_url}/delivery-partner/orders/{order_id}/complete"
        
        print(f"\n✅ Marking order {order_id} as delivered...")
        response = requests.post(url, headers=self.get_headers(), json={})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            print(f"   Order ID: {data['data']['order_id']}")
            print(f"   New Status: {data['data']['status']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False


def main():
    """Main test function."""
    print("=" * 70)
    print("  Delivery Partner API Tester - New Order Flow")
    print("=" * 70)
    
    tester = DeliveryPartnerAPITester(BASE_URL)
    
    # Step 1: Login
    phone = input("\n📱 Enter delivery partner phone number: ")
    otp = tester.send_otp(phone)
    
    if not otp:
        otp = input("🔑 Enter OTP manually: ")
    
    if not tester.verify_otp(phone, otp):
        print("\n❌ Authentication failed. Exiting.")
        return
    
    # Step 2: Test filters
    print("\n" + "=" * 70)
    print("  TESTING FILTERS")
    print("=" * 70)
    
    available_orders = tester.get_available_orders()
    active_orders = tester.get_active_orders()
    
    # Step 3: Test new flow (if we have available orders)
    if available_orders:
        print("\n" + "=" * 70)
        print("  TESTING NEW FLOW: READY → REACHED_RESTAURANT")
        print("=" * 70)
        
        test_order = available_orders[0]
        print(f"\n🎯 Testing with Order #{test_order['order_number']} (ID: {test_order['id']})")
        
        choice = input(f"\nDo you want to test the /reached endpoint with this order? (y/n): ")
        
        if choice.lower() == 'y':
            # Test the enhanced /reached endpoint
            if tester.mark_reached_restaurant(test_order['id']):
                print("\n✅ Successfully tested READY → REACHED_RESTAURANT transition")
                
                # Verify it appears in active orders now
                print("\n🔄 Verifying order moved to active orders...")
                tester.get_active_orders()
                
                # Optional: Continue with full flow
                cont = input("\nContinue with full flow? (pickup → complete) (y/n): ")
                if cont.lower() == 'y':
                    if tester.mark_picked_up(test_order['id']):
                        if tester.mark_complete(test_order['id']):
                            print("\n🎉 Full flow completed successfully!")
    else:
        print("\n⚠️  No available orders to test with")
    
    print("\n" + "=" * 70)
    print("  TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
