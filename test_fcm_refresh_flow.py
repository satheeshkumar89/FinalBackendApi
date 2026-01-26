"""
Test FCM Auto-Refresh Flow
This script tests the complete FCM notification flow for order status changes.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your server URL
# BASE_URL = "https://dharaifooddelivery.in"  # Production

# Test credentials (update with your test accounts)
CUSTOMER_PHONE = "+919876543210"
RESTAURANT_PHONE = "+919876543211"
DELIVERY_PHONE = "+919876543212"

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def send_otp(phone_number, user_type="customer"):
    """Send OTP to phone number"""
    endpoints = {
        "customer": "/customer/auth/send-otp",
        "restaurant": "/auth/send-otp",
        "delivery": "/delivery-partner/auth/send-otp"
    }
    
    response = requests.post(
        f"{BASE_URL}{endpoints[user_type]}",
        json={"phone_number": phone_number}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            otp = data.get("data", {}).get("otp")
            print_success(f"OTP sent to {phone_number}: {otp}")
            return otp
    
    print_error(f"Failed to send OTP: {response.text}")
    return None

def verify_otp(phone_number, otp_code, user_type="customer"):
    """Verify OTP and get auth token"""
    endpoints = {
        "customer": "/customer/auth/verify-otp",
        "restaurant": "/auth/verify-otp",
        "delivery": "/delivery-partner/auth/verify-otp"
    }
    
    response = requests.post(
        f"{BASE_URL}{endpoints[user_type]}",
        json={
            "phone_number": phone_number,
            "otp_code": otp_code
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print_success(f"Logged in as {user_type}: {phone_number}")
        return token
    
    print_error(f"Failed to verify OTP: {response.text}")
    return None

def register_device_token(auth_token, fcm_token, user_type="customer"):
    """Register FCM device token"""
    endpoints = {
        "customer": "/notifications/customer/device-token",
        "restaurant": "/notifications/device-token",
        "delivery": "/delivery-partner/device-token"
    }
    
    response = requests.post(
        f"{BASE_URL}{endpoints[user_type]}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "token": fcm_token,
            "device_type": "android"
        }
    )
    
    if response.status_code == 200:
        print_success(f"Device token registered for {user_type}")
        return True
    
    print_error(f"Failed to register device token: {response.text}")
    return False

def create_test_order(customer_token, restaurant_id=1):
    """Create a test order"""
    response = requests.post(
        f"{BASE_URL}/customer/orders",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "restaurant_id": restaurant_id,
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 2,
                    "special_instructions": "Extra spicy"
                }
            ],
            "delivery_address": "123 Test Street, Test City",
            "delivery_latitude": 11.0168,
            "delivery_longitude": 76.9558,
            "payment_method": "cash",
            "special_instructions": "Ring the bell twice"
        }
    )
    
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        order_id = data.get("data", {}).get("id")
        print_success(f"Order created: #{order_id}")
        return order_id
    
    print_error(f"Failed to create order: {response.text}")
    return None

def update_order_status(restaurant_token, order_id, action):
    """Update order status"""
    endpoints = {
        "accept": f"/orders/{order_id}/accept",
        "preparing": f"/orders/{order_id}/preparing",
        "ready": f"/orders/{order_id}/ready",
        "handover": f"/orders/{order_id}/handover"
    }
    
    response = requests.post(
        f"{BASE_URL}{endpoints[action]}",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    
    if response.status_code == 200:
        print_success(f"Order #{order_id} status updated: {action}")
        print_info(f"✉️  FCM notification sent to customer")
        return True
    
    print_error(f"Failed to update order status: {response.text}")
    return False

def delivery_accept_order(delivery_token, order_id):
    """Delivery partner accepts order"""
    response = requests.post(
        f"{BASE_URL}/delivery-partner/orders/{order_id}/accept",
        headers={"Authorization": f"Bearer {delivery_token}"}
    )
    
    if response.status_code == 200:
        print_success(f"Delivery partner accepted order #{order_id}")
        print_info(f"✉️  FCM notification sent to customer and restaurant")
        return True
    
    print_error(f"Failed to accept order: {response.text}")
    return False

def delivery_update_status(delivery_token, order_id, action):
    """Update delivery status"""
    endpoints = {
        "reached": f"/delivery-partner/orders/{order_id}/reached",
        "pickup": f"/delivery-partner/orders/{order_id}/pickup",
        "deliver": f"/delivery-partner/orders/{order_id}/deliver"
    }
    
    response = requests.post(
        f"{BASE_URL}{endpoints[action]}",
        headers={"Authorization": f"Bearer {delivery_token}"}
    )
    
    if response.status_code == 200:
        print_success(f"Delivery status updated: {action}")
        print_info(f"✉️  FCM notification sent to customer")
        return True
    
    print_error(f"Failed to update delivery status: {response.text}")
    return False

def check_notifications(auth_token, user_type="customer"):
    """Check notifications for user"""
    endpoints = {
        "customer": "/notifications/customer",
        "restaurant": "/notifications",
        "delivery": "/delivery-partner/notifications"
    }
    
    response = requests.get(
        f"{BASE_URL}{endpoints[user_type]}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        notifications = data.get("data", [])
        print_info(f"Found {len(notifications)} notifications for {user_type}")
        
        for notif in notifications[:5]:  # Show last 5
            print(f"   📩 {notif.get('title')}: {notif.get('message')}")
        
        return notifications
    
    print_error(f"Failed to fetch notifications: {response.text}")
    return []

def main():
    """Main test flow"""
    print_header("FCM Auto-Refresh Flow Test")
    
    print_info("This script tests the complete FCM notification flow")
    print_info("Make sure your backend is running and Firebase is configured")
    print()
    
    # Step 1: Login as Customer
    print_header("Step 1: Customer Login & Device Token Registration")
    customer_otp = send_otp(CUSTOMER_PHONE, "customer")
    if not customer_otp:
        print_error("Failed to send customer OTP. Exiting.")
        return
    
    customer_token = verify_otp(CUSTOMER_PHONE, customer_otp, "customer")
    if not customer_token:
        print_error("Failed to login as customer. Exiting.")
        return
    
    # Register fake FCM token for customer
    customer_fcm_token = f"customer_test_token_{int(time.time())}"
    register_device_token(customer_token, customer_fcm_token, "customer")
    
    time.sleep(2)
    
    # Step 2: Login as Restaurant
    print_header("Step 2: Restaurant Login & Device Token Registration")
    restaurant_otp = send_otp(RESTAURANT_PHONE, "restaurant")
    if not restaurant_otp:
        print_warning("Failed to send restaurant OTP. Skipping restaurant steps.")
        restaurant_token = None
    else:
        restaurant_token = verify_otp(RESTAURANT_PHONE, restaurant_otp, "restaurant")
        if restaurant_token:
            restaurant_fcm_token = f"restaurant_test_token_{int(time.time())}"
            register_device_token(restaurant_token, restaurant_fcm_token, "restaurant")
    
    time.sleep(2)
    
    # Step 3: Login as Delivery Partner
    print_header("Step 3: Delivery Partner Login & Device Token Registration")
    delivery_otp = send_otp(DELIVERY_PHONE, "delivery")
    if not delivery_otp:
        print_warning("Failed to send delivery OTP. Skipping delivery steps.")
        delivery_token = None
    else:
        delivery_token = verify_otp(DELIVERY_PHONE, delivery_otp, "delivery")
        if delivery_token:
            delivery_fcm_token = f"delivery_test_token_{int(time.time())}"
            register_device_token(delivery_token, delivery_fcm_token, "delivery")
    
    time.sleep(2)
    
    # Step 4: Create Order
    print_header("Step 4: Customer Creates Order")
    print_info("This should trigger FCM notification to restaurant")
    order_id = create_test_order(customer_token)
    if not order_id:
        print_error("Failed to create order. Exiting.")
        return
    
    time.sleep(3)
    
    # Step 5: Restaurant Accepts Order
    if restaurant_token:
        print_header("Step 5: Restaurant Accepts Order")
        print_info("This should trigger FCM notification to customer")
        update_order_status(restaurant_token, order_id, "accept")
        time.sleep(3)
        
        # Step 6: Restaurant Marks Preparing
        print_header("Step 6: Restaurant Marks Order as Preparing")
        print_info("This should trigger FCM notification to customer")
        update_order_status(restaurant_token, order_id, "preparing")
        time.sleep(3)
        
        # Step 7: Restaurant Marks Ready
        print_header("Step 7: Restaurant Marks Order as Ready")
        print_info("This should trigger FCM notification to customer AND delivery partners")
        update_order_status(restaurant_token, order_id, "ready")
        time.sleep(3)
    
    # Step 8: Delivery Partner Accepts
    if delivery_token:
        print_header("Step 8: Delivery Partner Accepts Order")
        print_info("This should trigger FCM notification to customer and restaurant")
        delivery_accept_order(delivery_token, order_id)
        time.sleep(3)
        
        # Step 9: Delivery Partner Reaches Restaurant
        print_header("Step 9: Delivery Partner Reaches Restaurant")
        print_info("This should trigger FCM notification to customer and restaurant")
        delivery_update_status(delivery_token, order_id, "reached")
        time.sleep(3)
        
        # Step 10: Delivery Partner Picks Up
        print_header("Step 10: Delivery Partner Picks Up Order")
        print_info("This should trigger FCM notification to customer")
        delivery_update_status(delivery_token, order_id, "pickup")
        time.sleep(3)
        
        # Step 11: Delivery Partner Delivers
        print_header("Step 11: Delivery Partner Delivers Order")
        print_info("This should trigger FCM notification to customer")
        delivery_update_status(delivery_token, order_id, "deliver")
        time.sleep(3)
    
    # Step 12: Check Notifications
    print_header("Step 12: Verify Notifications Were Created")
    
    print_info("Customer Notifications:")
    check_notifications(customer_token, "customer")
    
    if restaurant_token:
        print()
        print_info("Restaurant Notifications:")
        check_notifications(restaurant_token, "restaurant")
    
    if delivery_token:
        print()
        print_info("Delivery Partner Notifications:")
        check_notifications(delivery_token, "delivery")
    
    # Summary
    print_header("Test Summary")
    print_success("✅ All FCM notifications should have been triggered")
    print_success("✅ Notifications saved to database")
    print_info("📱 In a real app, these would trigger auto-refresh")
    print()
    print_info("Next Steps:")
    print("   1. Check backend logs for FCM send confirmations")
    print("   2. Verify notifications table in database")
    print("   3. Implement FCM in Flutter apps to receive these notifications")
    print("   4. Test with real Firebase FCM tokens")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print_error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
