# 🚀 Quick Reference - Order Status Flow

## 📱 App Integration Cheat Sheet

### Restaurant App 🏪

#### Order Lists
```dart
// GET /orders/new
final pendingOrders = await getOrders(status: 'PENDING');

// GET /orders/ongoing
final ongoingOrders = await getOrders(
  statuses: ['ACCEPTED', 'PREPARING', 'READY']
);

// GET /orders/completed
final completedOrders = await getOrders(
  statuses: ['HANDED_OVER', 'DELIVERED', 'REJECTED', 'CANCELLED']
);
```

#### Status Actions
```dart
// Step 1: Accept
PUT /orders/{id}/accept
PENDING → ACCEPTED

// Step 2: Start Preparing
PUT /orders/{id}/preparing
ACCEPTED → PREPARING

// Step 3: Mark Ready
PUT /orders/{id}/ready  
PREPARING → READY

// Step 4: Hand Over (DONE)
PUT /orders/{id}/handover
READY → HANDED_OVER

// Reject
POST /orders/{id}/reject
PENDING → REJECTED
```

---

### Delivery Boy App 🚴

#### Order Lists
```dart
// GET /delivery-partner/orders/available
final availableOrders = await getOrders(status: 'READY');

// GET /delivery-partner/orders/active
final activeOrders = await getOrders(
  statuses: ['ASSIGNED', 'REACHED_RESTAURANT', 'PICKED_UP']
);

// GET /delivery-partner/orders/completed
final completedOrders = await getOrders(status: 'DELIVERED');
```

#### Status Actions
```dart
// Step 1: Accept
POST /delivery-partner/orders/{id}/accept
READY → ASSIGNED

// Step 2: Reached
POST /delivery-partner/orders/{id}/reached
ASSIGNED → REACHED_RESTAURANT

// Step 3: Pickup
POST /delivery-partner/orders/{id}/pickup
REACHED_RESTAURANT → PICKED_UP

// Step 4: Deliver (DONE)
POST /delivery-partner/orders/{id}/complete
PICKED_UP → DELIVERED
```

---

### Customer App 👤

#### Status Display
```dart
String getStatusMessage(String status) {
  switch (status) {
    case 'PENDING':
      return 'Waiting for restaurant confirmation';
    case 'ACCEPTED':
      return 'Restaurant is preparing your order';
    case 'PREPARING':
      return 'Your food is being prepared';
    case 'READY':
      return 'Food is ready, waiting for delivery partner';
    case 'ASSIGNED':
      return 'Delivery partner assigned';
    case 'REACHED_RESTAURANT':
      return 'Delivery partner is picking up your order';
    case 'PICKED_UP':
      return 'Order is on the way!';
    case 'DELIVERED':
      return 'Order delivered';
    case 'HANDED_OVER':
      return 'Order handed over to delivery partner';
    case 'REJECTED':
      return 'Order rejected by restaurant';
    case 'CANCELLED':
      return 'Order cancelled';
    default:
      return 'Processing...';
  }
}
```

---

## 🔔 Socket.IO Events

### Event Names
```javascript
{
  'new_order': 'PENDING',
  'order_accepted': 'ACCEPTED',
  'preparing': 'PREPARING',
  'ready': 'READY',
  'handed_over': 'HANDED_OVER',
  'delivery_assigned': 'ASSIGNED',
  'delivery_reached': 'REACHED_RESTAURANT',
  'pickedup': 'PICKED_UP',
  'delivered': 'DELIVERED',
  'order_rejected': 'REJECTED',
  'order_cancelled': 'CANCELLED'
}
```

### Rooms
```javascript
// Join rooms on connect
socket.emit('join', {
  room: 'restaurant_123',     // For restaurant
  room: 'delivery_partner_456', // For delivery partner
  room: 'customer_789',       // For customer
  room: 'available_delivery_partners' // For all online partners
});

// Listen for events
socket.on('order_update', (data) => {
  print('Status: ${data['status']}');
  print('Event: ${data['event_type']}');
});
```

---

## 📊 Status Enum (Models)

### Dart/Flutter
```dart
enum OrderStatus {
  PENDING,
  ACCEPTED,
  PREPARING,
  READY,
  HANDED_OVER,
  ASSIGNED,
  REACHED_RESTAURANT,
  PICKED_UP,
  DELIVERED,
  REJECTED,
  CANCELLED,
  RELEASED // Deprecated
}

// Convert from API
OrderStatus fromString(String status) {
  return OrderStatus.values.firstWhere(
    (e) => e.toString().split('.').last == status.toUpperCase(),
    orElse: () => OrderStatus.PENDING
  );
}
```

### Python
```python
from enum import Enum

class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    READY = "ready"
    HANDED_OVER = "handed_over"
    ASSIGNED = "assigned"
    REACHED_RESTAURANT = "reached_restaurant"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    RELEASED = "released"  # Deprecated
```

---

## 🎨 Status Colors & Icons

### Color Scheme
```dart
Color getStatusColor(String status) {
  switch (status) {
    case 'PENDING':
      return Colors.orange;
    case 'ACCEPTED':
    case 'PREPARING':
    case 'READY':
      return Colors.blue;
    case 'ASSIGNED':
    case 'REACHED_RESTAURANT':
    case 'PICKED_UP':
      return Colors.purple;
    case 'DELIVERED':
      return Colors.green;
    case 'HANDED_OVER':
      return Colors.teal;
    case 'REJECTED':
    case 'CANCELLED':
      return Colors.red;
    default:
      return Colors.grey;
  }
}
```

### Icon Set
```dart
IconData getStatusIcon(String status) {
  switch (status) {
    case 'PENDING':
      return Icons.access_time;
    case 'ACCEPTED':
      return Icons.check_circle;
    case 'PREPARING':
      return Icons.restaurant;
    case 'READY':
      return Icons.done_all;
    case 'HANDED_OVER':
      return Icons.handshake;
    case 'ASSIGNED':
      return Icons.delivery_dining;
    case 'REACHED_RESTAURANT':
      return Icons.location_on;
    case 'PICKED_UP':
      return Icons.shopping_bag;
    case 'DELIVERED':
      return Icons.celebration;
    case 'REJECTED':
    case 'CANCELLED':
      return Icons.cancel;
    default:
      return Icons.help;
  }
}
```

---

## 📝 API Response Examples

### Order Summary
```json
{
  "order_id": 123,
  "order_number": "ORD20260115103000",
  "status": "assigned",
  "total_amount": "450.00",
  "created_at": "2026-01-15T10:30:00",
  "customer_name": "John Doe",
  "restaurant_name": "Pizza Palace",
  "delivery_partner_id": 456
}
```

### Order Details with Timeline
```json
{
  "order_id": 123,
  "status": "picked_up",
  "timeline": {
    "created_at": "2026-01-15T10:30:00",
    "accepted_at": "2026-01-15T10:32:00",
    "preparing_at": "2026-01-15T10:35:00",
    "ready_at": "2026-01-15T10:50:00",
    "handed_over_at": null,
    "assigned_at": "2026-01-15T10:52:00",
    "reached_restaurant_at": "2026-01-15T11:00:00",
    "pickedup_at": "2026-01-15T11:03:00",
    "delivered_at": null
  }
}
```

---

## 🧪 Test Scenarios

### Restaurant Happy Path
```bash
# 1. Get pending orders
GET /orders/new

# 2. Accept order
PUT /orders/123/accept

# 3. Start preparing
PUT /orders/123/preparing

# 4. Mark ready
PUT /orders/123/ready

# 5. Hand over
PUT /orders/123/handover
```

### Delivery Partner Happy Path
```bash
# 1. Get available orders
GET /delivery-partner/orders/available

# 2. Accept delivery
POST /delivery-partner/orders/123/accept

# 3. Mark reached
POST /delivery-partner/orders/123/reached

# 4. Pickup order
POST /delivery-partner/orders/123/pickup

# 5. Deliver
POST /delivery-partner/orders/123/complete
```

---

## ⚡ Quick Fixes

### Common Issues

#### 1. Order not showing in list
```
Problem: Order has wrong status
Fix: Check order.status matches filter criteria
Restaurant Ongoing: ACCEPTED, PREPARING, READY
Delivery Active: ASSIGNED, REACHED_RESTAURANT, PICKED_UP
```

#### 2. Can't update status
```
Problem: Invalid state transition
Fix: Check current status before update
Use: GET /orders/{id} to verify current status
```

#### 3. Notifications not working
```
Problem: Not joined to Socket.IO room
Fix: Emit 'join' event with correct room name
restaurant_{id} / delivery_partner_{id} / customer_{id}
```

---

## 📊 Database Queries

### Get orders by status (SQL)
```sql
-- Pending orders
SELECT * FROM orders WHERE status = 'pending' AND restaurant_id = ?;

-- Restaurant ongoing
SELECT * FROM orders 
WHERE restaurant_id = ? 
AND status IN ('accepted', 'preparing', 'ready');

-- Delivery partner active
SELECT * FROM orders 
WHERE delivery_partner_id = ? 
AND status IN ('assigned', 'reached_restaurant', 'picked_up');
```

### Update status with timestamp
```sql
-- Restaurant accepts
UPDATE orders 
SET status = 'accepted', accepted_at = CURRENT_TIMESTAMP 
WHERE id = ? AND status = 'pending';

-- Delivery partner picks up
UPDATE orders 
SET status = 'picked_up', pickedup_at = CURRENT_TIMESTAMP 
WHERE id = ? AND status = 'reached_restaurant';
```

---

## 🔍 Debugging Tips

### Check order status flow
```python
# In Python/Django shell
order = Order.objects.get(id=123)
print(f"Current Status: {order.status}")
print(f"Created: {order.created_at}")
print(f"Accepted: {order.accepted_at}")
print(f"Preparing: {order.preparing_at}")
print(f"Ready: {order.ready_at}")
print(f"Assigned: {order.assigned_at}")
print(f"Reached: {order.reached_restaurant_at}")
print(f"Picked Up: {order.pickedup_at}")
print(f"Delivered: {order.delivered_at}")
```

### Validate status transition
```python
VALID_TRANSITIONS = {
    'pending': ['accepted', 'rejected'],
    'accepted': ['preparing', 'cancelled'],
    'preparing': ['ready', 'cancelled'],
    'ready': ['assigned', 'handed_over', 'cancelled'],
    'assigned': ['reached_restaurant'],
    'reached_restaurant': ['picked_up'],
    'picked_up': ['delivered']
}

def can_transition(current, new):
    return new in VALID_TRANSITIONS.get(current, [])
```

---

## 🎯 Status Filter Helpers

### Restaurant Lists
```dart
// New orders
orders.where((o) => o.status == 'PENDING')

// Ongoing orders
orders.where((o) => ['ACCEPTED', 'PREPARING', 'READY'].contains(o.status))

// Completed orders
orders.where((o) => ['HANDED_OVER', 'DELIVERED', 'REJECTED', 'CANCELLED'].contains(o.status))
```

### Delivery Partner Lists
```dart
// Available orders
orders.where((o) => o.status == 'READY' && o.deliveryPartnerId == null)

// Active orders
orders.where((o) => ['ASSIGNED', 'REACHED_RESTAURANT', 'PICKED_UP'].contains(o.status))

// History
orders.where((o) => o.status == 'DELIVERED')
```

---

**Quick Ref Version:** 2.0  
**Last Updated:** 2026-01-15  
**Print this page for easy reference!**
