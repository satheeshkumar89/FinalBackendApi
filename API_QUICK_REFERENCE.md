# Quick API Reference - Delivery Partner Order Flow

## 🔑 Authentication
```bash
# 1. Send OTP
POST /delivery-partner/auth/send-otp
{"phone_number": "+1234567890"}

# 2. Verify OTP
POST /delivery-partner/auth/verify-otp
{"phone_number": "+1234567890", "otp_code": "123456"}
# Returns: {"access_token": "...", "delivery_partner": {...}}
```

## 📦 Order Endpoints

### Get Available Orders (READY only)
```bash
GET /delivery-partner/orders/available
Authorization: Bearer {token}

Response: [
  {
    "id": 123,
    "order_number": "ORD-2026-001",
    "restaurant_name": "Pizza Palace",
    "customer_name": "John Doe",
    "customer_phone": "+1234567890",
    "delivery_address": "123 Main St",
    "total_amount": 25.99,
    "status": "ready",  # ← Always "ready"
    "created_at": "2026-01-15T10:00:00Z"
  }
]
```

### Get Active Orders
```bash
GET /delivery-partner/orders/active
Authorization: Bearer {token}

Response: [
  {
    "id": 124,
    "status": "reached_restaurant",  # ← Can be assigned, reached_restaurant, or picked_up
    ...
  }
]
```

## 🚀 Order Actions

### 1️⃣ Reached Restaurant (NEW - Auto-assigns from READY)
```bash
POST /delivery-partner/orders/123/reached
Authorization: Bearer {token}

# Works with:
# - READY status → Auto-assigns partner + changes to REACHED_RESTAURANT
# - ASSIGNED status → Just changes to REACHED_RESTAURANT

Response: {
  "success": true,
  "message": "Reached restaurant successfully",
  "data": {
    "order_id": 123,
    "status": "reached_restaurant"
  }
}
```

### 2️⃣ Pickup Order
```bash
POST /delivery-partner/orders/123/picked-up
Authorization: Bearer {token}

# Requires: REACHED_RESTAURANT status
# Changes to: PICKED_UP

Response: {
  "success": true,
  "message": "Order picked up successfully",
  "data": {
    "order_id": 123,
    "status": "picked_up"
  }
}
```

### 3️⃣ Complete Delivery
```bash
POST /delivery-partner/orders/123/complete
Authorization: Bearer {token}

# Requires: PICKED_UP status
# Changes to: DELIVERED

Response: {
  "success": true,
  "message": "Order marked as delivered successfully",
  "data": {
    "order_id": 123,
    "status": "delivered"
  }
}
```

### 🚫 Cancel Order
```bash
POST /delivery-partner/orders/123/cancel
Authorization: Bearer {token}

# Releases order back to available pool
# Cannot cancel after PICKED_UP status
```

## 🔄 Status Flow

```
Available Orders:
  READY (no partner assigned)
    ↓ POST /reached (auto-assigns)
    
Active Orders:
  REACHED_RESTAURANT
    ↓ POST /picked-up
  PICKED_UP
    ↓ POST /complete
    
Completed Orders:
  DELIVERED
```

## ⚠️ Common Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| 400 - Order already accepted | Another partner claimed it | Choose different order |
| 403 - Not assigned to you | Order belongs to someone else | Check active orders |
| 400 - Invalid status | Wrong order status | Check current status |
| 401 - Unauthorized | Token expired/invalid | Login again |

## 🧪 Test Flow

```bash
# 1. Login
TOKEN=$(curl -X POST .../auth/verify-otp -d '...' | jq -r '.access_token')

# 2. Get available order
ORDER_ID=$(curl -H "Authorization: Bearer $TOKEN" .../orders/available | jq -r '.[0].id')

# 3. Mark reached (auto-assigns)
curl -X POST -H "Authorization: Bearer $TOKEN" .../orders/$ORDER_ID/reached

# 4. Pickup
curl -X POST -H "Authorization: Bearer $TOKEN" .../orders/$ORDER_ID/picked-up

# 5. Complete
curl -X POST -H "Authorization: Bearer $TOKEN" .../orders/$ORDER_ID/complete
```

## 📱 Flutter App Constants

```dart
// Use these URLs in Flutter app
static const String reachedRestaurant = '/delivery-partner/orders/{orderId}/reached';
static const String pickupOrder = '/delivery-partner/orders/{orderId}/picked-up';
static const String completeOrder = '/delivery-partner/orders/{orderId}/complete';
```

---

**Base URL**: `https://dharaifooddelivery.in`  
**API Version**: v1  
**Status**: ✅ Production Ready
