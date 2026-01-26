# Auto-Refresh Flow Diagram

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     FASTFOODIE BACKEND                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Order Status Changes (Any Endpoint)                     │  │
│  │  - Customer places order                                 │  │
│  │  - Restaurant accepts/prepares/ready                     │  │
│  │  - Delivery partner picks up/delivers                    │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│                       ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  NotificationService.send_order_update()                 │  │
│  │  - Saves notification to database                        │  │
│  │  - Triggers FCM push notification                        │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│                       ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Firebase Cloud Messaging (FCM)                          │  │
│  │  - Sends to device tokens in database                    │  │
│  │  - Broadcasts to admin_updates topic                     │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────────┘
                        │
                        │ FCM Push Notification
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Customer App │ │ Restaurant App│ │ Delivery App  │
│               │ │               │ │               │
│  FCMService   │ │  FCMService   │ │  FCMService   │
│      │        │ │      │        │ │      │        │
│      ▼        │ │      ▼        │ │      ▼        │
│ onOrderUpdate │ │ onNewOrder    │ │ onRefreshOrders│
│      │        │ │      │        │ │      │        │
│      ▼        │ │      ▼        │ │      ▼        │
│ _refreshOrder()│ │_refreshOrders()│ │_refreshOrders()│
│      │        │ │      │        │ │      │        │
│      ▼        │ │      ▼        │ │      ▼        │
│  setState()   │ │  setState()   │ │  setState()   │
│      │        │ │      │        │ │      │        │
│      ▼        │ │      ▼        │ │      ▼        │
│  UI Updates   │ │  UI Updates   │ │  UI Updates   │
│  Automatically│ │  Automatically│ │  Automatically│
└───────────────┘ └───────────────┘ └───────────────┘
```

---

## 🔄 Order Status Flow with Auto-Refresh

```
Customer Places Order
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ Status: PENDING                                     │
│ ✅ Backend sends FCM to:                            │
│    - Restaurant Owner (new_order)                   │
│    - Admin (admin_updates topic)                    │
│ 📱 Restaurant App auto-refreshes "New Orders"       │
└─────────────────────────────────────────────────────┘
        │
        ▼
Restaurant Accepts Order
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ Status: ACCEPTED                                    │
│ ✅ Backend sends FCM to:                            │
│    - Customer (order_update)                        │
│    - Admin (admin_updates topic)                    │
│ 📱 Customer App auto-refreshes order tracking       │
└─────────────────────────────────────────────────────┘
        │
        ▼
Restaurant Prepares Food
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ Status: PREPARING                                   │
│ ✅ Backend sends FCM to:                            │
│    - Customer (order_update)                        │
│    - Admin (admin_updates topic)                    │
│ 📱 Customer App shows "Chef is cooking"             │
└─────────────────────────────────────────────────────┘
        │
        ▼
Restaurant Marks Ready
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ Status: READY                                       │
│ ✅ Backend sends FCM to:                            │
│    - Customer (order_update)                        │
│    - All nearby delivery partners (new_available)   │
│    - Admin (admin_updates topic)                    │
│ 📱 Customer App shows "Food is ready"               │
│ 📱 Delivery App auto-refreshes "Available Orders"   │
└─────────────────────────────────────────────────────┘
        │
        ▼
Delivery Partner Accepts
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ Status: ASSIGNED                                    │
│ ✅ Backend sends FCM to:                            │
│    - Customer (order_update)                        │
│    - Restaurant Owner (order_update)                │
│    - Admin (admin_updates topic)                    │
│ 📱 Customer App shows "Partner assigned"            │
│ 📱 Restaurant App updates order status              │
└─────────────────────────────────────────────────────┘
        │
        ▼
Delivery Partner Reaches Restaurant
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ Status: REACHED_RESTAURANT                          │
│ ✅ Backend sends FCM to:                            │
│    - Customer (order_update)                        │
│    - Restaurant Owner (order_update)                │
│    - Admin (admin_updates topic)                    │
│ 📱 All apps auto-refresh                            │
└─────────────────────────────────────────────────────┘
        │
        ▼
Restaurant Hands Over to Partner
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ Status: HANDED_OVER                                 │
│ ✅ Backend sends FCM to:                            │
│    - Customer (order_update)                        │
│    - Delivery Partner (order_update)                │
│    - Admin (admin_updates topic)                    │
│ 📱 All apps auto-refresh                            │
└─────────────────────────────────────────────────────┘
        │
        ▼
Delivery Partner Picks Up
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ Status: PICKED_UP                                   │
│ ✅ Backend sends FCM to:                            │
│    - Customer (order_update)                        │
│    - Restaurant Owner (order_update)                │
│    - Admin (admin_updates topic)                    │
│ 📱 Customer App shows "Partner is on the way"       │
└─────────────────────────────────────────────────────┘
        │
        ▼
Delivery Partner Delivers
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ Status: DELIVERED                                   │
│ ✅ Backend sends FCM to:                            │
│    - Customer (order_update)                        │
│    - Restaurant Owner (order_update)                │
│    - Delivery Partner (order_update)                │
│    - Admin (admin_updates topic)                    │
│ 📱 Customer App shows "Delivered! Rate your order"  │
│ 📱 Delivery App moves to "Completed"                │
└─────────────────────────────────────────────────────┘
```

---

## 📱 FCM Message Flow

### 1. Customer App Flow

```
FCM Notification Received
        │
        ▼
FirebaseMessaging.onMessage (Foreground)
        │
        ▼
FCMService._handleMessage()
        │
        ▼
Check notification_type == "order_update"
        │
        ▼
Call onOrderUpdate(orderId, status)
        │
        ▼
Screen checks: if (orderId == widget.orderId)
        │
        ▼
Call _refreshOrder()
        │
        ▼
API: GET /customer/orders/{orderId}
        │
        ▼
setState() with new order data
        │
        ▼
UI Updates Automatically! ✨
```

### 2. Restaurant App Flow

```
FCM Notification Received
        │
        ▼
FirebaseMessaging.onMessage (Foreground)
        │
        ▼
FCMService._handleMessage()
        │
        ▼
Check notification_type == "new_order"
        │
        ▼
Call onNewOrder()
        │
        ▼
_refreshNewOrders()
        │
        ▼
API: GET /orders/new
        │
        ▼
setState() with new orders list
        │
        ▼
Play notification sound 🔔
        │
        ▼
Show badge count
        │
        ▼
UI Updates Automatically! ✨
```

### 3. Delivery Partner App Flow

```
FCM Notification Received
        │
        ▼
FirebaseMessaging.onMessage (Foreground)
        │
        ▼
FCMService._handleMessage()
        │
        ▼
Check notification_type == "new_available_order"
        │
        ▼
Call onRefreshOrders()
        │
        ▼
_refreshAvailableOrders()
        │
        ▼
API: GET /delivery-partner/orders/available
        │
        ▼
setState() with new orders list
        │
        ▼
Show notification: "New order available!"
        │
        ▼
UI Updates Automatically! ✨
```

### 4. Admin App Flow

```
FCM Topic Notification Received
        │
        ▼
Topic: "admin_updates"
        │
        ▼
FirebaseMessaging.onMessage (Foreground)
        │
        ▼
FCMService._handleMessage()
        │
        ▼
Check notification_type == "admin_order_refresh"
        │
        ▼
Call onRefreshOrders()
        │
        ▼
_refreshAllOrders()
        │
        ▼
API: GET /admin/orders
        │
        ▼
setState() with updated orders
        │
        ▼
UI Updates Automatically! ✨
```

---

## 🎯 Key Components

### Backend Components (Already Implemented ✅)

1. **NotificationService** (`app/services/notification_service.py`)
   - `send_order_update()` - Main notification trigger
   - `create_notification()` - Saves to DB + sends FCM
   - `_send_fcm_push()` - Sends to device tokens
   - `_broadcast_to_topic()` - Sends to admin topic

2. **Device Token Endpoints**
   - `POST /notifications/customer/device-token`
   - `POST /notifications/device-token` (Restaurant)
   - `POST /delivery-partner/device-token`

3. **Database Tables**
   - `notifications` - Stores notification history
   - `device_tokens` - Stores FCM tokens for each user

### Flutter Components (To Implement)

1. **FCMService** (`lib/services/fcm_service.dart`)
   - `initialize()` - Setup FCM
   - `_setupMessageHandlers()` - Listen for messages
   - `_handleMessage()` - Process notifications
   - `_sendTokenToBackend()` - Register device token

2. **App-Specific Services**
   - `CustomerFCMService` - Customer app
   - `RestaurantFCMService` - Restaurant app
   - `DeliveryFCMService` - Delivery partner app

3. **Screen Integration**
   - Setup FCM listener in `initState()`
   - Set callback: `_fcmService.onOrderUpdate = ...`
   - Implement `_refreshOrder()` method
   - Call `setState()` to update UI

---

## 🔐 Security Flow

```
1. User logs in
        │
        ▼
2. App gets FCM token from Firebase
        │
        ▼
3. App sends token to backend with auth header
        │
        ▼
4. Backend validates JWT token
        │
        ▼
5. Backend saves device token to database
   - Links to customer_id / owner_id / delivery_partner_id
        │
        ▼
6. When order status changes:
   - Backend queries device_tokens table
   - Finds all tokens for that user
   - Sends FCM to those tokens
        │
        ▼
7. App receives FCM notification
        │
        ▼
8. App auto-refreshes data from API
   - Uses stored auth token
   - Gets latest order data
        │
        ▼
9. UI updates automatically! ✨
```

---

## 📊 Database Schema

### device_tokens table

```sql
CREATE TABLE device_tokens (
    id INTEGER PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    device_type VARCHAR(10),  -- 'ios' or 'android'
    customer_id INTEGER,
    owner_id INTEGER,
    delivery_partner_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### notifications table

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    owner_id INTEGER,
    delivery_partner_id INTEGER,
    title VARCHAR(255),
    message TEXT,
    notification_type VARCHAR(50),
    order_id INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);
```

---

## 🧪 Testing Checklist

### Backend Testing (Already Working ✅)
- [x] FCM notifications sent on order status change
- [x] Device token registration endpoints work
- [x] Notifications saved to database
- [x] FCM multicast to multiple devices
- [x] Admin topic broadcasting

### Customer App Testing
- [ ] FCM token registered on login
- [ ] Order tracking screen auto-refreshes
- [ ] Order history screen auto-refreshes
- [ ] Notification shows when order status changes
- [ ] Works in foreground and background

### Restaurant App Testing
- [ ] FCM token registered on login
- [ ] New orders screen auto-refreshes
- [ ] Ongoing orders screen auto-refreshes
- [ ] Sound/vibration on new order (optional)
- [ ] Badge count updates

### Delivery Partner App Testing
- [ ] FCM token registered on login
- [ ] Available orders screen auto-refreshes
- [ ] Active orders screen auto-refreshes
- [ ] Notification shows for new available orders
- [ ] Works when app is in background

### Admin App Testing
- [ ] Subscribed to admin_updates topic
- [ ] Receives all order status changes
- [ ] Order list auto-refreshes
- [ ] Works in foreground and background

---

## 🚀 Performance Considerations

### Optimization Tips

1. **Debounce Refresh Calls**
   ```dart
   Timer? _debounceTimer;
   
   void _debouncedRefresh() {
     _debounceTimer?.cancel();
     _debounceTimer = Timer(Duration(milliseconds: 500), () {
       _refreshOrders();
     });
   }
   ```

2. **Avoid Duplicate Listeners**
   ```dart
   @override
   void dispose() {
     _fcmService.onOrderUpdate = null;
     _fcmService.onRefreshOrders = null;
     super.dispose();
   }
   ```

3. **Check if Widget is Mounted**
   ```dart
   Future<void> _refreshOrder() async {
     final order = await ApiService.getOrderDetails(widget.orderId);
     if (mounted) {
       setState(() {
         _order = order;
       });
     }
   }
   ```

4. **Use Singleton for FCMService**
   ```dart
   class FCMService {
     static final FCMService _instance = FCMService._internal();
     factory FCMService() => _instance;
     FCMService._internal();
     
     // ... rest of the code
   }
   ```

---

## 📞 Troubleshooting

### Problem: FCM token not registered
**Solution:**
```dart
// Check if token is being sent
print('FCM Token: $token');

// Check API response
print('Response: ${response.statusCode} - ${response.body}');

// Verify auth token exists
final authToken = await Storage.getAuthToken();
print('Auth Token: ${authToken != null ? "✅" : "❌"}');
```

### Problem: Notifications not received
**Solution:**
```dart
// Add debug logging in message handlers
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  print('📩 FOREGROUND MESSAGE RECEIVED');
  print('   Title: ${message.notification?.title}');
  print('   Body: ${message.notification?.body}');
  print('   Data: ${message.data}');
});
```

### Problem: UI not updating
**Solution:**
```dart
// Ensure setState is called
Future<void> _refreshOrder() async {
  print('🔄 Refreshing order...');
  final order = await ApiService.getOrderDetails(widget.orderId);
  print('✅ Order fetched: ${order.status}');
  
  setState(() {
    print('✅ setState called');
    _order = order;
  });
}
```

---

## 🎉 Success Metrics

After successful implementation, you should see:

✅ **Customer App**
- Order status updates appear within 1-2 seconds
- No manual refresh needed
- Smooth UI transitions

✅ **Restaurant App**
- New orders appear instantly
- Sound/vibration alerts (optional)
- Badge count updates automatically

✅ **Delivery Partner App**
- Available orders update in real-time
- Active orders refresh automatically
- Notifications show for new orders

✅ **Admin App**
- All order changes visible immediately
- Topic-based broadcasting works
- Dashboard updates in real-time

---

**Your backend is fully ready! Just implement the Flutter side following this guide! 🚀**
