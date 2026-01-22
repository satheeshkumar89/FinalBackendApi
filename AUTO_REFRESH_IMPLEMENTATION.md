# Automatic Order Refresh - All 4 Apps Implementation Guide

## Overview

Your backend **already sends FCM (Firebase Cloud Messaging) notifications** for every order status change. This guide shows how to implement automatic refresh in all 4 Flutter apps.

---

## How It Works

```
Order Status Changes → Backend sends FCM → Flutter App receives → Auto Refresh UI
```

### Backend Notifications (Already Implemented ✅)

Every order status change triggers FCM notifications to:
- ✅ **Customer** - Order updates
- ✅ **Restaurant Owner** - New orders and status changes
- ✅ **Delivery Partner** - Order assignments and updates
- ✅ **Admin** (via topic subscription)

---

## Flutter App Implementation

### Step 1: FCM Setup (All Apps)

**Add to `pubspec.yaml`:**
```yaml
dependencies:
  firebase_core: ^3.8.1
  firebase_messaging: ^15.1.5
```

**Initialize Firebase in `main.dart`:**
```dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

// Background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print("Background message: ${message.notification?.title}");
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  
  // Set background message handler
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  
  runApp(MyApp());
}
```

---

### Step 2: FCM Service (Create for Each App)

**Create `lib/services/fcm_service.dart`:**

```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'dart:convert';

class FCMService {
  final FirebaseMessaging _fcm = FirebaseMessaging.instance;
  
  // Callback for order refresh
  Function(String orderId, String status)? onOrderUpdate;
  
  Future<void> initialize() async {
    // Request permission (iOS)
    NotificationSettings settings = await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('✅ FCM Permission granted');
      
      // Get FCM token
      String? token = await _fcm.getToken();
      print('📱 FCM Token: $token');
      
      // Send token to backend
      if (token != null) {
        await _sendTokenToBackend(token);
      }
      
      // Listen for token refresh
      _fcm.onTokenRefresh.listen(_sendTokenToBackend);
      
      // Setup message handlers
      _setupMessageHandlers();
    }
  }
  
  void _setupMessageHandlers() {
    // Foreground messages (app is open)
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('📩 Foreground message received');
      _handleMessage(message);
    });
    
    // Background messages (app is in background, user taps notification)
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('📩 Background message opened');
      _handleMessage(message);
    });
    
    // Check if app was opened from terminated state
    _fcm.getInitialMessage().then((RemoteMessage? message) {
      if (message != null) {
        print('📩 App opened from terminated state');
        _handleMessage(message);
      }
    });
  }
  
  void _handleMessage(RemoteMessage message) {
    print('Message data: ${message.data}');
    
    final data = message.data;
    final notificationType = data['notification_type'] ?? '';
    final orderId = data['order_id'] ?? '';
    final status = data['status'] ?? '';
    
    // Trigger refresh based on notification type
    if (notificationType == 'order_update' || 
        notificationType == 'new_order' ||
        notificationType == 'new_available_order') {
      
      // Call the refresh callback
      if (onOrderUpdate != null && orderId.isNotEmpty) {
        onOrderUpdate!(orderId, status);
      }
    }
  }
  
  Future<void> _sendTokenToBackend(String token) async {
    // TODO: Replace with your API endpoint
    // For Customer App: POST /customer/device-token
    // For Restaurant App: POST /restaurant/device-token
    // For Delivery App: POST /delivery-partner/device-token
    
    try {
      // Example:
      // await ApiService.registerDeviceToken(token);
      print('📤 Sending token to backend: $token');
    } catch (e) {
      print('❌ Error sending token: $e');
    }
  }
}
```

---

### Step 3: Implement Auto-Refresh in Each App

#### **Customer App** (foodieexpress)

**In `order_tracking_screen.dart`:**

```dart
class OrderTrackingScreen extends StatefulWidget {
  final String orderId;
  const OrderTrackingScreen({required this.orderId});
  
  @override
  State<OrderTrackingScreen> createState() => _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends State<OrderTrackingScreen> {
  final FCMService _fcmService = FCMService();
  
  @override
  void initState() {
    super.initState();
    
    // Setup FCM listener for this order
    _fcmService.onOrderUpdate = (orderId, status) {
      if (orderId == widget.orderId) {
        print('🔄 Auto-refreshing order $orderId with status: $status');
        _refreshOrder();
      }
    };
  }
  
  Future<void> _refreshOrder() async {
    // Fetch latest order details from API
    setState(() {
      // Update UI with new data
    });
  }
  
  @override
  Widget build(BuildContext context) {
    // Your UI code
  }
}
```

**In `order_history_screen.dart`:**

```dart
class OrderHistoryScreen extends StatefulWidget {
  @override
  State<OrderHistoryScreen> createState() => _OrderHistoryScreenState();
}

class _OrderHistoryScreenState extends State<OrderHistoryScreen> {
  final FCMService _fcmService = FCMService();
  
  @override
  void initState() {
    super.initState();
    
    // Refresh order list when any order updates
    _fcmService.onOrderUpdate = (orderId, status) {
      print('🔄 Refreshing order list');
      _refreshOrders();
    };
  }
  
  Future<void> _refreshOrders() async {
    // Fetch latest orders from API
    setState(() {
      // Update order list
    });
  }
}
```

---

#### **Restaurant App** (DFDRestaurantPartner)

**In `new_orders_screen.dart`:**

```dart
class NewOrdersScreen extends StatefulWidget {
  @override
  State<NewOrdersScreen> createState() => _NewOrdersScreenState();
}

class _NewOrdersScreenState extends State<NewOrdersScreen> {
  final FCMService _fcmService = FCMService();
  
  @override
  void initState() {
    super.initState();
    
    // Auto-refresh when new order arrives
    _fcmService.onOrderUpdate = (orderId, status) {
      if (status == 'pending') {
        print('🔔 New order received! Auto-refreshing...');
        _refreshNewOrders();
        _playNotificationSound(); // Optional
      }
    };
  }
  
  Future<void> _refreshNewOrders() async {
    // Call GET /orders/new
    setState(() {
      // Update new orders list
    });
  }
}
```

**In `ongoing_orders_screen.dart`:**

```dart
class OngoingOrdersScreen extends StatefulWidget {
  @override
  State<OngoingOrdersScreen> createState() => _OngoingOrdersScreenState();
}

class _OngoingOrdersScreenState extends State<OngoingOrdersScreen> {
  final FCMService _fcmService = FCMService();
  
  @override
  void initState() {
    super.initState();
    
    _fcmService.onOrderUpdate = (orderId, status) {
      // Refresh ongoing orders when status changes
      print('🔄 Order $orderId status changed to $status');
      _refreshOngoingOrders();
    };
  }
  
  Future<void> _refreshOngoingOrders() async {
    // Call GET /orders/ongoing
    setState(() {
      // Update ongoing orders
    });
  }
}
```

---

#### **Delivery Partner App** (dharai_delivery_boy)

**In `available_orders_screen.dart`:**

```dart
class AvailableOrdersScreen extends StatefulWidget {
  @override
  State<AvailableOrdersScreen> createState() => _AvailableOrdersScreenState();
}

class _AvailableOrdersScreenState extends State<AvailableOrdersScreen> {
  final FCMService _fcmService = FCMService();
  
  @override
  void initState() {
    super.initState();
    
    // Refresh when new orders become available
    _fcmService.onOrderUpdate = (orderId, status) {
      if (status == 'ready' || status == 'handed_over') {
        print('🔔 New order available! Auto-refreshing...');
        _refreshAvailableOrders();
      }
    };
  }
  
  Future<void> _refreshAvailableOrders() async {
    // Call GET /delivery-partner/orders/available
    setState(() {
      // Update available orders
    });
  }
}
```

**In `active_orders_screen.dart`:**

```dart
class ActiveOrdersScreen extends StatefulWidget {
  @override
  State<ActiveOrdersScreen> createState() => _ActiveOrdersScreenState();
}

class _ActiveOrdersScreenState extends State<ActiveOrdersScreen> {
  final FCMService _fcmService = FCMService();
  
  @override
  void initState() {
    super.initState();
    
    _fcmService.onOrderUpdate = (orderId, status) {
      print('🔄 Active order updated: $orderId -> $status');
      _refreshActiveOrders();
    };
  }
  
  Future<void> _refreshActiveOrders() async {
    // Call GET /delivery-partner/orders/active
    setState(() {
      // Update active orders
    });
  }
}
```

---

## Step 4: Register Device Token with Backend

**Create `lib/services/api_service.dart` method:**

```dart
class ApiService {
  static Future<void> registerDeviceToken(String token) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/customer/device-token'), // Change per app
        headers: {
          'Authorization': 'Bearer $authToken',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'token': token,
          'device_type': Platform.isIOS ? 'ios' : 'android',
        }),
      );
      
      if (response.statusCode == 200) {
        print('✅ Device token registered successfully');
      }
    } catch (e) {
      print('❌ Error registering device token: $e');
    }
  }
}
```

**Call this in FCMService:**

```dart
Future<void> _sendTokenToBackend(String token) async {
  await ApiService.registerDeviceToken(token);
}
```

---

## Step 5: Testing Auto-Refresh

### Test Scenario 1: Customer App
1. Customer places order
2. Restaurant accepts order
3. **Customer app should auto-refresh** and show "Order Confirmed"

### Test Scenario 2: Restaurant App
1. Customer places order
2. **Restaurant app should auto-refresh** "New Orders" screen
3. Sound/vibration notification (optional)

### Test Scenario 3: Delivery App
1. Restaurant marks order as "Ready"
2. **Delivery app should auto-refresh** "Available Orders"
3. New order appears in the list

---

## Notification Payload Structure

The backend sends this data with each FCM notification:

```json
{
  "notification": {
    "title": "Order Confirmed! 🎉",
    "body": "Restaurant has accepted your order #74."
  },
  "data": {
    "notification_type": "order_update",
    "order_id": "74",
    "status": "accepted",
    "click_action": "FLUTTER_NOTIFICATION_CLICK"
  }
}
```

---

## Common Issues & Solutions

### Issue 1: Notifications not received
**Solution:**
- Check FCM token is sent to backend
- Verify Firebase project setup
- Check device permissions

### Issue 2: App doesn't refresh
**Solution:**
- Ensure `onOrderUpdate` callback is set
- Check if `setState()` is called
- Verify API is being called

### Issue 3: Multiple refreshes
**Solution:**
- Debounce the refresh function
- Check if order ID matches before refreshing

---

## Advanced: Real-time with WebSocket (Optional)

For even faster updates, you can combine FCM with WebSocket:

```dart
// In addition to FCM
final socket = io('https://dharaifooddelivery.in', <String, dynamic>{
  'transports': ['websocket'],
  'auth': {'token': authToken},
});

socket.on('order_update', (data) {
  print('WebSocket order update: $data');
  _refreshOrder();
});
```

---

## Summary

✅ **Backend**: Already sends FCM notifications for all order updates  
✅ **Customer App**: Auto-refresh order tracking and history  
✅ **Restaurant App**: Auto-refresh new orders and ongoing orders  
✅ **Delivery App**: Auto-refresh available and active orders  
✅ **Real-time**: Instant UI updates without manual refresh  

---

## Next Steps

1. ✅ Add `firebase_messaging` to all 4 apps
2. ✅ Create `FCMService` in each app
3. ✅ Implement `onOrderUpdate` callbacks in all screens
4. ✅ Register device tokens with backend
5. ✅ Test with real orders

**Result**: All 4 apps will automatically refresh when order status changes! 🎉
