# 🔄 Order Status Flow - Complete API Documentation

## 📊 New Order Status Flow

### Status Overview

| Status | Description | Who Sets It | Next Status |
|--------|-------------|-------------|-------------|
| **PENDING** | Order created, waiting for restaurant | System (on order creation) | ACCEPTED or REJECTED |
| **ACCEPTED** | Restaurant accepted order | Restaurant | PREPARING |
| **PREPARING** | Restaurant is preparing food | Restaurant | READY |
| **READY** | Food is ready for pickup | Restaurant | ASSIGNED (when delivery partner accepts) |
| **ASSIGNED** | Delivery partner assigned | Delivery Partner | REACHED_RESTAURANT |
| **REACHED_RESTAURANT** | Delivery partner at restaurant | Delivery Partner | PICKED_UP |
| **PICKED_UP** | Order picked up from restaurant | Delivery Partner | DELIVERED |
| **DELIVERED** | Order delivered to customer | Delivery Partner | - (Terminal) |
| **HANDED_OVER** | Restaurant handed over to delivery | Restaurant (optional) | - (Terminal) |
| **REJECTED** | Restaurant rejected order | Restaurant | - (Terminal) |
| **CANCELLED** | Order cancelled | Customer/System | - (Terminal) |

---

## 🏪 Restaurant Partner APIs

### Workflow Steps:
1. **Accept Order** → Status: PENDING → ACCEPTED
2. **Start Preparing** → Status: ACCEPTED → PREPARING
3. **Mark Ready** → Status: PREPARING → READY
4. **Hand Over to Delivery** → Status: READY → HANDED_OVER (Done for restaurant)

### Get Pending Orders
```http
GET /orders/new
Authorization: Bearer {restaurant_token}
```

**Description:** Get all orders with status `PENDING` waiting for restaurant acceptance.

**Response:**
```json
{
  "success": true,
  "message": "New orders retrieved successfully",
  "data": {
    "orders": [
      {
        "order_id": 123,
        "item_count": 3,
        "total_amount": "450.00",
        "created_at": "2026-01-15T10:30:00",
        "payment_method": "upi",
        "status": "pending"
      }
    ]
  }
}
```

### Get Ongoing Orders
```http
GET /orders/ongoing
Authorization: Bearer {restaurant_token}
```

**Description:** Get all orders with status `ACCEPTED`, `PREPARING`, `READY`.

**Response:**
```json
{
  "success": true,
  "message": "Ongoing orders retrieved successfully",
  "data": {
    "orders": [...]
  }
}
```

### Get Completed Orders
```http
GET /orders/completed
Authorization: Bearer {restaurant_token}
```

**Description:** Get all orders with status `HANDED_OVER`, `DELIVERED`, `REJECTED`, `CANCELLED`.

### Step 1: Accept Order
```http
PUT /orders/{order_id}/accept
Authorization: Bearer {restaurant_token}
```

**Status Change:** `PENDING` → `ACCEPTED`

**Response:**
```json
{
  "success": true,
  "message": "Order marked as accepted",
  "data": {
    "order_id": 123,
    "status": "accepted",
    "accepted_at": "2026-01-15T10:35:00"
  }
}
```

### Step 2: Start Preparing
```http
PUT /orders/{order_id}/preparing
Authorization: Bearer {restaurant_token}
```

**Status Change:** `ACCEPTED` → `PREPARING`

**Response:**
```json
{
  "success": true,
  "message": "Order marked as preparing",
  "data": {
    "order_id": 123,
    "status": "preparing",
    "preparing_at": "2026-01-15T10:36:00"
  }
}
```

### Step 3: Mark Ready
```http
PUT /orders/{order_id}/ready
Authorization: Bearer {restaurant_token}
```

**Status Change:** `PREPARING` → `READY`

**Response:**
```json
{
  "success": true,
  "message": "Order marked as ready",
  "data": {
    "order_id": 123,
    "status": "ready",
    "ready_at": "2026-01-15T10:50:00"
  }
}
```

### Step 4: Hand Over to Delivery
```http
PUT /orders/{order_id}/handover
Authorization: Bearer {restaurant_token}
```

**Status Change:** `READY` → `HANDED_OVER`

**Response:**
```json
{
  "success": true,
  "message": "Order marked as handed_over",
  "data": {
    "order_id": 123,
    "status": "handed_over",
    "handed_over_at": "2026-01-15T11:00:00"
  }
}
```

**Note:** This marks the order as complete from the restaurant's perspective.

### Reject Order
```http
POST /orders/{order_id}/reject
Authorization: Bearer {restaurant_token}
Content-Type: application/json

{
  "rejection_reason": "Item out of stock"
}
```

**Status Change:** `PENDING` → `REJECTED`

---

## 🚴 Delivery Partner APIs

### Workflow Steps:
1. **Accept Order** → Status: READY → ASSIGNED
2. **Mark Reached Restaurant** → Status: ASSIGNED → REACHED_RESTAURANT
3. **Pickup Order** → Status: REACHED_RESTAURANT → PICKED_UP
4. **Deliver Order** → Status: PICKED_UP → DELIVERED (Done for delivery partner)

### Get Available Orders
```http
GET /delivery-partner/orders/available
Authorization: Bearer {delivery_partner_token}
```

**Description:** Get all orders with status `READY` that have no delivery partner assigned (within 5km proximity).

**Response:**
```json
[
  {
    "id": 123,
    "order_number": "ORD20260115103000",
    "restaurant_name": "Pizza Palace",
    "customer_name": "John Doe",
    "customer_phone": "+919876543210",
    "delivery_address": "123 Main St, City",
    "total_amount": "450.00",
    "status": "ready",
    "created_at": "2026-01-15T10:30:00",
    "estimated_delivery_time": "2026-01-15T11:30:00"
  }
]
```

### Get Active Orders
```http
GET /delivery-partner/orders/active
Authorization: Bearer {delivery_partner_token}
```

**Description:** Get all orders assigned to this delivery partner with status `ASSIGNED`, `REACHED_RESTAURANT`, `PICKED_UP`.

### Get Completed Orders
```http
GET /delivery-partner/orders/completed
Authorization: Bearer {delivery_partner_token}
```

**Description:** Get delivery history - all orders with status `DELIVERED`.

### Step 1: Accept Order
```http
POST /delivery-partner/orders/{order_id}/accept
Authorization: Bearer {delivery_partner_token}
```

**Status Change:** `READY` → `ASSIGNED`

**Response:**
```json
{
  "success": true,
  "message": "Order accepted for delivery successfully",
  "data": {
    "order_id": 123,
    "status": "assigned"
  }
}
```

**Requirements:**
- Order must be in `READY` status
- No delivery partner should be assigned yet
- Delivery partner must be online and within 5km

### Step 2: Mark Reached Restaurant
```http
POST /delivery-partner/orders/{order_id}/reached
Authorization: Bearer {delivery_partner_token}
```

**Status Change:** `ASSIGNED` → `REACHED_RESTAURANT`

**Response:**
```json
{
  "success": true,
  "message": "Reached restaurant successfully",
  "data": {
    "order_id": 123,
    "status": "reached_restaurant"
  }
}
```

**Requirements:**
- Order must be in `ASSIGNED` status
- Delivery partner must be assigned to this order

### Step 3: Pickup Order
```http
POST /delivery-partner/orders/{order_id}/pickup
Authorization: Bearer {delivery_partner_token}
```

**Status Change:** `REACHED_RESTAURANT` → `PICKED_UP`

**Response:**
```json
{
  "success": true,
  "message": "Order picked up successfully",
  "data": {
    "order_id": 123,
    "status": "picked_up"
  }
}
```

**Requirements:**
- Order must be in `REACHED_RESTAURANT` status
- Delivery partner must be at restaurant location

### Step 4: Deliver Order
```http
POST /delivery-partner/orders/{order_id}/complete
Authorization: Bearer {delivery_partner_token}
```

**Status Change:** `PICKED_UP` → `DELIVERED`

**Response:**
```json
{
  "success": true,
  "message": "Order marked as delivered successfully",
  "data": {
    "order_id": 123,
    "status": "delivered"
  }
}
```

**Requirements:**
- Order must be in `PICKED_UP` status
- Delivery partner must be at customer location

---

## 👤 Customer App Status Display

| Backend Status | Customer Display |
|---------------|------------------|
| `PENDING` | "Waiting for restaurant confirmation" |
| `ACCEPTED` | "Restaurant is preparing your order" |
| `PREPARING` | "Your food is being prepared" |
| `READY` | "Food is ready, waiting for delivery partner" |
| `ASSIGNED` | "Delivery partner assigned" |
| `REACHED_RESTAURANT` | "Delivery partner is picking up your order" |
| `PICKED_UP` | "Order is on the way!" |
| `DELIVERED` | "Order delivered" |
| `HANDED_OVER` | "Order handed over to delivery partner" |
| `REJECTED` | "Order rejected by restaurant" |
| `CANCELLED` | "Order cancelled" |

---

## 🔔 Real-Time Notifications

### Socket.IO Events

**Room Names:**
- `restaurant_{restaurant_id}` - Restaurant-specific events
- `delivery_partner_{partner_id}` - Delivery partner-specific events
- `customer_{customer_id}` - Customer-specific events
- `available_delivery_partners` - Broadcast to all online delivery partners

**Event Types:**

| Event Name | Triggered When | Sent To |
|-----------|----------------|---------|
| `new_order` | Order created (PENDING) | Restaurant |
| `order_accepted` | Restaurant accepts | Customer, Available Delivery Partners |
| `preparing` | Restaurant starts preparing | Customer |
| `ready` | Food is ready | Customer, Nearby Delivery Partners |
| `handed_over` | Restaurant hands over | Customer |
| `delivery_assigned` | Delivery partner accepts | Restaurant, Customer |
| `delivery_reached` | Partner at restaurant | Restaurant, Customer |
| `pickedup` | Order picked up | Restaurant, Customer |
| `delivered` | Order delivered | Restaurant, Customer, Delivery Partner |
| `order_rejected` | Restaurant rejects | Customer |

---

## 🗄️ Database Timestamp Fields

```python
# Restaurant workflow timestamps
accepted_at          # When restaurant accepts
preparing_at         # When restaurant starts preparing
ready_at            # When food is ready
handed_over_at      # When restaurant hands over to delivery

# Delivery partner workflow timestamps
assigned_at                # When delivery partner accepts
reached_restaurant_at      # When delivery partner reaches restaurant
pickedup_at               # When delivery partner picks up order
delivered_at              # When order is delivered

# Other timestamps
created_at          # Order creation
rejected_at         # If rejected
completed_at        # When fully complete
```

---

## 📈 Admin Dashboard Metrics

### Order Status Metrics:
- **Pending Orders:** Orders in `PENDING` status
- **Active Orders:** Orders in `ACCEPTED`, `PREPARING`, `READY`
- **In Delivery:** Orders in `ASSIGNED`, `REACHED_RESTAURANT`, `PICKED_UP`
- **Completed:** Orders in `HANDED_OVER`, `DELIVERED`
- **Failed:** Orders in `REJECTED`, `CANCELLED`

---

## ✅ Status Transition Rules

### Valid Transitions:

```
PENDING → ACCEPTED (Restaurant accepts)
PENDING → REJECTED (Restaurant rejects)

ACCEPTED → PREPARING (Restaurant starts cooking)
PREPARING → READY (Food is ready)
READY → ASSIGNED (Delivery partner accepts)
READY → HANDED_OVER (Restaurant marks as handed over)

ASSIGNED → REACHED_RESTAURANT (Delivery partner at restaurant)
REACHED_RESTAURANT → PICKED_UP (Delivery partner picks up)
PICKED_UP → DELIVERED (Delivery partner delivers)

Any status → CANCELLED (Order cancelled)
```

### Invalid Transitions:
- Cannot skip steps in the workflow
- Cannot go backwards (e.g., PICKED_UP → READY)
- Once DELIVERED, REJECTED, or CANCELLED, status is final

---

## 🧪 Testing the New Flow

### Complete Order Flow Test:

1. **Create Order** → Status: `PENDING`
2. **Restaurant Accepts** → PUT `/orders/123/accept` → Status: `ACCEPTED`
3. **Start Preparing** → PUT `/orders/123/preparing` → Status: `PREPARING`
4. **Mark Ready** → PUT `/orders/123/ready` → Status: `READY`
5. **Delivery Partner Accepts** → POST `/delivery-partner/orders/123/accept` → Status: `ASSIGNED`
6. **Partner Reaches Restaurant** → POST `/delivery-partner/orders/123/reached` → Status: `REACHED_RESTAURANT`
7. **Partner Picks Up** → POST `/delivery-partner/orders/123/pickup` → Status: `PICKED_UP`
8. **Partner Delivers** → POST `/delivery-partner/orders/123/complete` → Status: `DELIVERED`

---

## 📱 Frontend Integration Notes

### Restaurant App:
- **New Orders Tab:** Show orders with status `PENDING`
- **Ongoing Orders Tab:** Show `ACCEPTED`, `PREPARING`, `READY`
- **Completed Orders Tab:** Show `HANDED_OVER`, `DELIVERED`, `REJECTED`

### Delivery Partner App:
- **Available Orders Tab:** Show orders with status `READY` (proximity-based)
- **Active Orders Tab:** Show `ASSIGNED`, `REACHED_RESTAURANT`, `PICKED_UP`
- **History Tab:** Show `DELIVERED` orders

### Customer App:
- Show order progress with timeline
- Real-time status updates via Socket.IO
- Display appropriate message for each status
- Track delivery partner location when status is `PICKED_UP`

---

## 🚀 Deployment Checklist

- [ ] Run database migration on local
- [√] Update models.py
- [√] Update order endpoints
- [√] Update delivery partner endpoints
- [√] Update dashboard service
- [ ] Update notification service
- [ ] Test all status transitions
- [ ] Update Flutter apps
- [ ] Run migration on production EC2
- [ ] Deploy backend to EC2
- [ ] Monitor logs for errors

---

**Last Updated:** 2026-01-15  
**Version:** 2.0  
**Status:** ✅ Backend Implementation Complete
