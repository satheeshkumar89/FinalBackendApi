# 📱 4 Apps Integration - Quick Visual Guide

## 🎯 What to Do in Each App

---

## 🏪 App 1: Restaurant Partner App

### Files to Change: 5-6 Files

```
📁 lib/
├── 📄 models/order.dart
│   └── Add: PENDING, HANDED_OVER, ASSIGNED, REACHED_RESTAURANT statuses
│   └── Add: handed_over_at, assigned_at, reached_restaurant_at timestamps
│
├── 📄 services/order_service.dart
│   └── Add: handOverOrder(int orderId) method
│   └── Update: getNewOrders() - returns PENDING status
│   └── Update: getOngoingOrders() - returns ACCEPTED, PREPARING, READY
│
├── 📄 bloc/orders_bloc.dart
│   └── Add: HandOverOrder event
│   └── Add: _onHandOverOrder() handler
│
├── 📄 widgets/order_card.dart
│   └── Add: "Hand Over" button for READY status
│   └── Update: _buildActionButtons() with 4 steps
│
└── 📄 screens/orders_screen.dart
    └── Update: Tab filters (New, Ongoing, Completed)
```

### UI Flow:
```
┌─────────────────────────────────────┐
│ NEW ORDERS TAB                      │
├─────────────────────────────────────┤
│ Status: PENDING                     │
│ ┌─────────────────────────────────┐ │
│ │ Order #1234                     │ │
│ │ [Accept] [Reject]               │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              ↓ Accept
┌─────────────────────────────────────┐
│ ONGOING ORDERS TAB                  │
├─────────────────────────────────────┤
│ Status: ACCEPTED                    │
│ ┌─────────────────────────────────┐ │
│ │ Order #1234                     │ │
│ │ [Start Preparing]               │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              ↓ Start Preparing
┌─────────────────────────────────────┐
│ ONGOING ORDERS TAB                  │
├─────────────────────────────────────┤
│ Status: PREPARING                   │
│ ┌─────────────────────────────────┐ │
│ │ Order #1234                     │ │
│ │ [Mark Ready]                    │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              ↓ Mark Ready
┌─────────────────────────────────────┐
│ ONGOING ORDERS TAB                  │
├─────────────────────────────────────┤
│ Status: READY                       │
│ ┌─────────────────────────────────┐ │
│ │ Order #1234                     │ │
│ │ [Hand Over to Delivery] ← NEW   │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              ↓ Hand Over
┌─────────────────────────────────────┐
│ COMPLETED ORDERS TAB                │
├─────────────────────────────────────┤
│ Status: HANDED_OVER ✅              │
│ ┌─────────────────────────────────┐ │
│ │ Order #1234 - Completed         │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Code Example:
```dart
// In order_service.dart
Future<void> handOverOrder(int orderId) async {
  final response = await http.put(
    Uri.parse('$baseUrl/orders/$orderId/handover'),
    headers: {'Authorization': 'Bearer $token'},
  );
  if (response.statusCode != 200) {
    throw Exception('Failed to hand over order');
  }
}

// In order_card.dart
if (order.status == OrderStatus.READY) {
  return ElevatedButton.icon(
    onPressed: () => _handOverOrder(context, order.id),
    icon: Icon(Icons.handshake),
    label: Text('Hand Over to Delivery Partner'),
  );
}
```

---

## 🚴 App 2: Delivery Boy App

### Files to Change: 5-6 Files

```
📁 lib/
├── 📄 models/order.dart
│   └── Same as Restaurant App
│
├── 📄 services/delivery_service.dart
│   └── Add: markReachedRestaurant(int orderId) method
│   └── Add: pickupOrder(int orderId) method
│   └── Update: getAvailableOrders() - returns READY only
│   └── Update: getActiveOrders() - returns ASSIGNED, REACHED_RESTAURANT, PICKED_UP
│
├── 📄 bloc/delivery_orders_bloc.dart
│   └── Add: MarkReachedRestaurant event
│   └── Add: PickupOrder event
│   └── Add: handlers for both events
│
├── 📄 widgets/delivery_order_card.dart
│   └── Add: "I've Reached" button for ASSIGNED status
│   └── Add: "Pickup Order" button for REACHED_RESTAURANT status
│   └── Update: _buildActionButtons() with 4 steps
│
└── 📄 screens/delivery_screen.dart
    └── Update: Tab filters (Available, Active, History)
```

### UI Flow:
```
┌─────────────────────────────────────┐
│ AVAILABLE ORDERS TAB                │
├─────────────────────────────────────┤
│ Status: READY (within 5km)          │
│ ┌─────────────────────────────────┐ │
│ │ 🍕 Pizza Palace (2.3 km)        │ │
│ │ Order #1234 • ₹450              │ │
│ │ [Accept Delivery]               │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              ↓ Accept
┌─────────────────────────────────────┐
│ ACTIVE ORDERS TAB                   │
├─────────────────────────────────────┤
│ Status: ASSIGNED                    │
│ ┌─────────────────────────────────┐ │
│ │ Order #1234                     │ │
│ │ 📍 Navigate to restaurant       │ │
│ │ [I've Reached Restaurant] ← NEW │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              ↓ Reached
┌─────────────────────────────────────┐
│ ACTIVE ORDERS TAB                   │
├─────────────────────────────────────┤
│ Status: REACHED_RESTAURANT          │
│ ┌─────────────────────────────────┐ │
│ │ Order #1234                     │ │
│ │ ⏱️ Waiting for order...          │ │
│ │ [Pickup Order] ← NEW            │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              ↓ Pickup
┌─────────────────────────────────────┐
│ ACTIVE ORDERS TAB                   │
├─────────────────────────────────────┤
│ Status: PICKED_UP                   │
│ ┌─────────────────────────────────┐ │
│ │ Order #1234                     │ │
│ │ 📍 Navigate to customer         │ │
│ │ [Navigate] [Mark Delivered]     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              ↓ Deliver
┌─────────────────────────────────────┐
│ HISTORY TAB                         │
├─────────────────────────────────────┤
│ Status: DELIVERED ✅                │
│ ┌─────────────────────────────────┐ │
│ │ Order #1234 - Delivered         │ │
│ │ 💰 Earned: ₹30                  │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Code Example:
```dart
// In delivery_service.dart
Future<void> markReachedRestaurant(int orderId) async {
  final response = await http.post(
    Uri.parse('$baseUrl/delivery-partner/orders/$orderId/reached'),
    headers: {'Authorization': 'Bearer $token'},
  );
}

Future<void> pickupOrder(int orderId) async {
  final response = await http.post(
    Uri.parse('$baseUrl/delivery-partner/orders/$orderId/pickup'),
    headers: {'Authorization': 'Bearer $token'},
  );
}

// In delivery_order_card.dart
if (order.status == OrderStatus.ASSIGNED) {
  return ElevatedButton.icon(
    onPressed: () => _markReachedRestaurant(context, order.id),
    icon: Icon(Icons.location_on),
    label: Text('I\'ve Reached Restaurant'),
  );
}

if (order.status == OrderStatus.REACHED_RESTAURANT) {
  return ElevatedButton.icon(
    onPressed: () => _pickupOrder(context, order.id),
    icon: Icon(Icons.shopping_bag),
    label: Text('Pickup Order'),
  );
}
```

---

## 👤 App 3: Customer App

### Files to Change: 3-4 Files

```
📁 lib/
├── 📄 models/order.dart
│   └── Same as other apps
│
├── 📄 utils/order_status_helper.dart
│   └── Add: getStatusMessage() with 11 status messages
│   └── Add: getStatusIcon(), getStatusColor()
│   └── Add: getProgressPercentage()
│
├── 📄 widgets/order_timeline.dart
│   └── Update: Timeline with all 8 statuses
│   └── Add: Visual progress bar
│
└── 📄 screens/order_details_screen.dart
    └── Add: Delivery partner info card
    └── Update: Status display
    └── Add: Track delivery button
```

### UI Flow:
```
┌─────────────────────────────────────┐
│ ORDER #1234                         │
├─────────────────────────────────────┤
│ ⏳ Current Status                   │
│ Waiting for restaurant confirmation │
│ ████░░░░░░ 10%                      │
├─────────────────────────────────────┤
│ Order Timeline:                     │
│                                     │
│ ✅ Order Placed          10:30 AM  │
│ ⏳ Restaurant Accepted              │
│ ⏳ Preparing Food                   │
│ ⏳ Food Ready                       │
│ ⏳ Delivery Partner Assigned        │
│ ⏳ Partner at Restaurant            │
│ ⏳ Order Picked Up                  │
│ ⏳ Delivered                        │
└─────────────────────────────────────┘
              ↓ Time passes
┌─────────────────────────────────────┐
│ ORDER #1234                         │
├─────────────────────────────────────┤
│ 🚴 Current Status                   │
│ Order is on the way!                │
│ ████████░░ 90%                      │
├─────────────────────────────────────┤
│ Delivery Partner:                   │
│ ┌─────────────────────────────────┐ │
│ │ 👤 Rajesh Kumar                 │ │
│ │ ⭐ 4.8 • 🏍️ Bike               │ │
│ │ [📞 Call] [📍 Track Location]  │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ Timeline:                           │
│ ✅ Order Placed          10:30 AM  │
│ ✅ Restaurant Accepted    10:32 AM  │
│ ✅ Preparing Food         10:35 AM  │
│ ✅ Food Ready             10:50 AM  │
│ ✅ Delivery Assigned      10:52 AM  │
│ ✅ Partner at Restaurant  11:00 AM  │
│ ✅ Order Picked Up        11:03 AM  │
│ ⏳ Delivered                        │
└─────────────────────────────────────┘
```

### Code Example:
```dart
// In order_status_helper.dart
static String getStatusMessage(OrderStatus status) {
  switch (status) {
    case OrderStatus.PENDING:
      return 'Waiting for restaurant confirmation';
    case OrderStatus.ACCEPTED:
      return 'Restaurant is preparing your order';
    case OrderStatus.PREPARING:
      return 'Your food is being prepared';
    case OrderStatus.READY:
      return 'Food is ready, waiting for delivery partner';
    case OrderStatus.ASSIGNED:
      return 'Delivery partner assigned';
    case OrderStatus.REACHED_RESTAURANT:
      return 'Delivery partner is picking up your order';
    case OrderStatus.PICKED_UP:
      return 'Order is on the way!';
    case OrderStatus.DELIVERED:
      return 'Order delivered • Enjoy your meal!';
    // ... more statuses
  }
}

// In order_timeline.dart
_buildTimelineStep('Partner at Restaurant', order.reachedRestaurantAt, true);
_buildTimelineStep('Order Picked Up', order.pickedupAt, true);
```

---

## 👨‍💼 App 4: Admin Dashboard

### Files to Change: 3-4 Files

```
📁 lib/
├── 📄 models/order.dart
│   └── Same as other apps
│
├── 📄 services/admin_service.dart
│   └── Update: getOrders() with new status filters
│   └── Update: getDashboardStats()
│
├── 📄 widgets/admin_dashboard_stats.dart
│   └── Update: Stats cards with new categories
│   └── Add: "In Delivery" metric
│
└── 📄 screens/admin_orders_screen.dart
    └── Update: Filter chips
    └── Add: New status groups
```

### UI Flow:
```
┌─────────────────────────────────────────────────┐
│ DASHBOARD                                       │
├─────────────────────────────────────────────────┤
│ ┌───────────┐ ┌───────────┐ ┌───────────┐     │
│ │📝 Pending  │ │🔥 Active   │ │🚴 In Delivery│  │
│ │    5      │ │    12     │ │     8      │     │
│ │ Awaiting  │ │  Being    │ │  On the    │     │
│ │ accept    │ │ prepared  │ │    way     │     │
│ └───────────┘ └───────────┘ └───────────┘     │
│                                                 │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐     │
│ │✅ Completed│ │💰 Revenue  │ │❌ Failed   │    │
│ │    45     │ │ ₹15,450   │ │     3      │     │
│ │ Delivered │ │   Today   │ │ Rejected   │     │
│ └───────────┘ └───────────┘ └───────────┘     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ ORDERS                                          │
├─────────────────────────────────────────────────┤
│ Filters:                                        │
│ [All] [Pending] [Active] [In Delivery]         │
│ [Completed] [Failed]                            │
├─────────────────────────────────────────────────┤
│ Orders List:                                    │
│ ┌─────────────────────────────────────────────┐ │
│ │ #1234 • Pizza Palace • ASSIGNED             │ │
│ │ Delivery Partner: Rajesh • ₹450             │ │
│ └─────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────┐ │
│ │ #1235 • Burger King • PREPARING             │ │
│ │ Being prepared • ₹350                       │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Code Example:
```dart
// In admin_service.dart
Future<List<Order>> getOrdersByFilter(String filter) async {
  Map<String, List<String>> filterMap = {
    'pending': ['pending'],
    'active': ['accepted', 'preparing', 'ready'],
    'in_delivery': ['assigned', 'reached_restaurant', 'picked_up'],
    'completed': ['handed_over', 'delivered'],
    'failed': ['rejected', 'cancelled'],
  };
  
  return getOrders(statuses: filterMap[filter]);
}

// In admin_dashboard_stats.dart
_buildStatCard(
  'In Delivery',
  stats['in_delivery'] ?? 0,
  Icons.delivery_dining,
  Colors.purple,
  'On the way',
);
```

---

## 🎯 Quick Summary Table

| App | Files to Update | New Features | New API Calls |
|-----|----------------|--------------|---------------|
| **Restaurant** | 5-6 | Hand Over button | `PUT /orders/{id}/handover` |
| **Delivery Boy** | 5-6 | Reached + Pickup buttons | `POST /orders/{id}/reached`<br>`POST /orders/{id}/pickup` |
| **Customer** | 3-4 | 11 status messages, Timeline | None (read-only) |
| **Admin** | 3-4 | New filters & metrics | None (uses existing) |

---

## ✅ Testing Checklist

### For Each App:

**Step 1:** Update enum (same for all apps)
```dart
enum OrderStatus {
  PENDING,           // ← NEW (was NEW)
  ACCEPTED,
  PREPARING,
  READY,
  HANDED_OVER,       // ← NEW
  ASSIGNED,          // ← NEW
  REACHED_RESTAURANT,// ← NEW
  PICKED_UP,
  DELIVERED,
  REJECTED,
  CANCELLED,
}
```

**Step 2:** Update API service
- Restaurant: Add `handOverOrder()`
- Delivery: Add `markReachedRestaurant()`, `pickupOrder()`
- Customer: No changes
- Admin: Update filters

**Step 3:** Update bloc/provider
- Add new events
- Add new handlers

**Step 4:** Update UI components
- Add new buttons
- Update status displays
- Update filters

**Step 5:** Test end-to-end flow
- Create order → PENDING
- Restaurant accepts → ACCEPTED
- Restaurant prepares → PREPARING
- Restaurant marks ready → READY
- Delivery accepts → ASSIGNED
- Delivery reaches → REACHED_RESTAURANT
- Delivery picks up → PICKED_UP
- Delivery delivers → DELIVERED

**Step 6:** Test real-time updates
- Socket.IO events
- Push notifications
- Order list refreshes

---

## 🚀 Deployment Order

1. **Backend** (Already done ✅)
   - Database migrated
   - Endpoints updated
   - Ready for production

2. **Restaurant App**
   - Update code
   - Test locally
   - Build APK
   - Release

3. **Delivery Boy App**
   - Update code
   - Test locally
   - Build APK
   - Release

4. **Customer App**
   - Update code
   - Test locally
   - Build APK
   - Release

5. **Admin App**
   - Update code
   - Test locally
   - Build APK
   - Release (or web deploy)

---

## 📞 Need Help?

**Documentation:**
- `FLUTTER_APPS_INTEGRATION_GUIDE.md` - Complete code for Restaurant & Delivery
- `FLUTTER_APPS_PART2.md` - Complete code for Customer & Admin
- `QUICK_REFERENCE.md` - Quick code snippets
- `ORDER_STATUS_FLOW_API.md` - API documentation

**Quick Start:**
1. Open relevant guide file
2. Copy code examples
3. Paste into your app
4. Update variable names to match your app
5. Test!

---

**Last Updated:** 2026-01-15  
**Status:** ✅ Ready for Implementation  
**Estimated Time per App:** 2-4 hours
