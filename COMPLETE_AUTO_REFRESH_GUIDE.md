# Complete Auto-Refresh Implementation Guide
## All 4 Apps - Order Status Notifications

---

## 🎯 Overview

Your **backend is already fully configured** to send FCM (Firebase Cloud Messaging) notifications for every order status change. This guide shows you exactly how to implement automatic refresh in all 4 Flutter apps.

### ✅ Backend Status (Already Implemented)

Your backend automatically sends FCM notifications to:
- ✅ **Customer App** - When order status changes
- ✅ **Restaurant App** - When new orders arrive or status changes
- ✅ **Delivery Partner App** - When new orders are available or assigned
- ✅ **Admin App** - Via FCM topic subscription (`admin_updates`)

### 📱 Device Token Registration Endpoints (Already Available)

- **Customer**: `POST /notifications/customer/device-token`
- **Restaurant**: `POST /notifications/device-token`
- **Delivery Partner**: `POST /delivery-partner/device-token`

---

## 🔧 Implementation Steps

### Step 1: Add Firebase Dependencies (All Apps)

**File: `pubspec.yaml`**

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # Existing dependencies...
  
  # Add these for FCM
  firebase_core: ^3.8.1
  firebase_messaging: ^15.1.5
```

Run:
```bash
flutter pub get
```

---

### Step 2: Initialize Firebase (All Apps)

**File: `lib/main.dart`**

```dart
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:your_app/services/fcm_service.dart'; // You'll create this

// IMPORTANT: This must be a top-level function for background messages
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print("📩 Background message received: ${message.notification?.title}");
  print("📩 Data: ${message.data}");
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp();
  
  // Set background message handler
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  
  runApp(MyApp());
}

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final FCMService _fcmService = FCMService();
  
  @override
  void initState() {
    super.initState();
    _initializeFCM();
  }
  
  Future<void> _initializeFCM() async {
    await _fcmService.initialize();
  }
  
  @override
  Widget build(BuildContext context) {
    // Your existing app code
    return MaterialApp(
      // ...
    );
  }
}
```

---

### Step 3: Create FCM Service (All Apps)

**File: `lib/services/fcm_service.dart`**

```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:your_app/services/api_service.dart'; // Your existing API service
import 'package:your_app/utils/storage.dart'; // Your storage utility

class FCMService {
  final FirebaseMessaging _fcm = FirebaseMessaging.instance;
  
  // Callback functions for different notification types
  Function(String orderId, String status)? onOrderUpdate;
  Function()? onNewOrder;
  Function()? onRefreshOrders;
  
  Future<void> initialize() async {
    print('🔔 Initializing FCM Service...');
    
    // Request permission (iOS)
    NotificationSettings settings = await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );
    
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('✅ FCM Permission granted');
      
      // Get FCM token
      String? token = await _fcm.getToken();
      if (token != null) {
        print('📱 FCM Token: ${token.substring(0, 20)}...');
        await _sendTokenToBackend(token);
      }
      
      // Listen for token refresh
      _fcm.onTokenRefresh.listen((newToken) {
        print('🔄 FCM Token refreshed');
        _sendTokenToBackend(newToken);
      });
      
      // Setup message handlers
      _setupMessageHandlers();
    } else if (settings.authorizationStatus == AuthorizationStatus.denied) {
      print('❌ FCM Permission denied');
    } else {
      print('⚠️ FCM Permission not determined');
    }
  }
  
  void _setupMessageHandlers() {
    // 1. Foreground messages (app is open and active)
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('📩 Foreground message received');
      print('   Title: ${message.notification?.title}');
      print('   Body: ${message.notification?.body}');
      print('   Data: ${message.data}');
      
      _handleMessage(message);
      
      // Optionally show local notification
      // _showLocalNotification(message);
    });
    
    // 2. Background messages (app is in background, user taps notification)
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('📩 Background message opened');
      _handleMessage(message);
    });
    
    // 3. Check if app was opened from terminated state
    _fcm.getInitialMessage().then((RemoteMessage? message) {
      if (message != null) {
        print('📩 App opened from terminated state');
        _handleMessage(message);
      }
    });
  }
  
  void _handleMessage(RemoteMessage message) {
    final data = message.data;
    final notificationType = data['notification_type'] ?? '';
    final orderId = data['order_id'] ?? '';
    final status = data['status'] ?? '';
    
    print('🔔 Handling notification type: $notificationType');
    
    // Trigger appropriate callback based on notification type
    switch (notificationType) {
      case 'order_update':
        print('🔄 Order update: $orderId -> $status');
        if (onOrderUpdate != null && orderId.isNotEmpty) {
          onOrderUpdate!(orderId, status);
        }
        if (onRefreshOrders != null) {
          onRefreshOrders!();
        }
        break;
        
      case 'new_order':
        print('🆕 New order received');
        if (onNewOrder != null) {
          onNewOrder!();
        }
        if (onRefreshOrders != null) {
          onRefreshOrders!();
        }
        break;
        
      case 'new_available_order':
        print('🆕 New available order for delivery');
        if (onRefreshOrders != null) {
          onRefreshOrders!();
        }
        break;
        
      case 'admin_order_refresh':
        print('🔄 Admin order refresh');
        if (onRefreshOrders != null) {
          onRefreshOrders!();
        }
        break;
        
      default:
        print('⚠️ Unknown notification type: $notificationType');
        // Still trigger refresh as fallback
        if (onRefreshOrders != null) {
          onRefreshOrders!();
        }
    }
  }
  
  Future<void> _sendTokenToBackend(String token) async {
    try {
      // Get auth token from storage
      final authToken = await Storage.getAuthToken(); // Your storage method
      if (authToken == null) {
        print('⚠️ No auth token found, skipping FCM token registration');
        return;
      }
      
      // Determine endpoint based on app type
      String endpoint = _getDeviceTokenEndpoint();
      
      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}$endpoint'),
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
      } else {
        print('❌ Failed to register device token: ${response.statusCode}');
        print('   Response: ${response.body}');
      }
    } catch (e) {
      print('❌ Error sending token to backend: $e');
    }
  }
  
  String _getDeviceTokenEndpoint() {
    // Override this method in each app
    // Customer App: '/notifications/customer/device-token'
    // Restaurant App: '/notifications/device-token'
    // Delivery Partner App: '/delivery-partner/device-token'
    throw UnimplementedError('Override this method in each app');
  }
  
  // Subscribe to topic (for Admin app)
  Future<void> subscribeToTopic(String topic) async {
    try {
      await _fcm.subscribeToTopic(topic);
      print('✅ Subscribed to topic: $topic');
    } catch (e) {
      print('❌ Error subscribing to topic: $e');
    }
  }
  
  // Unsubscribe from topic
  Future<void> unsubscribeFromTopic(String topic) async {
    try {
      await _fcm.unsubscribeFromTopic(topic);
      print('✅ Unsubscribed from topic: $topic');
    } catch (e) {
      print('❌ Error unsubscribing from topic: $e');
    }
  }
}
```

---

## 📱 App-Specific Implementations

### 1️⃣ Customer App (foodieexpress)

**Create: `lib/services/customer_fcm_service.dart`**

```dart
import 'package:foodieexpress/services/fcm_service.dart';

class CustomerFCMService extends FCMService {
  @override
  String _getDeviceTokenEndpoint() {
    return '/notifications/customer/device-token';
  }
}
```

**In `lib/screens/order_tracking_screen.dart`:**

```dart
import 'package:foodieexpress/services/customer_fcm_service.dart';

class OrderTrackingScreen extends StatefulWidget {
  final String orderId;
  const OrderTrackingScreen({required this.orderId});
  
  @override
  State<OrderTrackingScreen> createState() => _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends State<OrderTrackingScreen> {
  final CustomerFCMService _fcmService = CustomerFCMService();
  Order? _order;
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadOrder();
    _setupFCMListener();
  }
  
  void _setupFCMListener() {
    // Listen for order updates
    _fcmService.onOrderUpdate = (orderId, status) {
      if (orderId == widget.orderId) {
        print('🔄 Auto-refreshing order $orderId with status: $status');
        _refreshOrder();
      }
    };
  }
  
  Future<void> _loadOrder() async {
    setState(() => _isLoading = true);
    try {
      final order = await ApiService.getOrderDetails(widget.orderId);
      setState(() {
        _order = order;
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading order: $e');
      setState(() => _isLoading = false);
    }
  }
  
  Future<void> _refreshOrder() async {
    try {
      final order = await ApiService.getOrderDetails(widget.orderId);
      setState(() {
        _order = order;
      });
      
      // Show snackbar for status change
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Order status updated: ${order.status}'),
          duration: Duration(seconds: 2),
        ),
      );
    } catch (e) {
      print('Error refreshing order: $e');
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: Text('Order Tracking')),
        body: Center(child: CircularProgressIndicator()),
      );
    }
    
    return Scaffold(
      appBar: AppBar(title: Text('Order #${_order?.orderNumber}')),
      body: RefreshIndicator(
        onRefresh: _refreshOrder,
        child: SingleChildScrollView(
          physics: AlwaysScrollableScrollPhysics(),
          child: Column(
            children: [
              // Your order tracking UI
              OrderTimeline(order: _order),
              // ... rest of your UI
            ],
          ),
        ),
      ),
    );
  }
}
```

**In `lib/screens/order_history_screen.dart`:**

```dart
class OrderHistoryScreen extends StatefulWidget {
  @override
  State<OrderHistoryScreen> createState() => _OrderHistoryScreenState();
}

class _OrderHistoryScreenState extends State<OrderHistoryScreen> {
  final CustomerFCMService _fcmService = CustomerFCMService();
  List<Order> _orders = [];
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadOrders();
    _setupFCMListener();
  }
  
  void _setupFCMListener() {
    // Refresh order list when any order updates
    _fcmService.onRefreshOrders = () {
      print('🔄 Refreshing order list');
      _refreshOrders();
    };
  }
  
  Future<void> _loadOrders() async {
    setState(() => _isLoading = true);
    try {
      final orders = await ApiService.getCustomerOrders();
      setState(() {
        _orders = orders;
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading orders: $e');
      setState(() => _isLoading = false);
    }
  }
  
  Future<void> _refreshOrders() async {
    try {
      final orders = await ApiService.getCustomerOrders();
      setState(() {
        _orders = orders;
      });
    } catch (e) {
      print('Error refreshing orders: $e');
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Order History')),
      body: RefreshIndicator(
        onRefresh: _refreshOrders,
        child: _isLoading
            ? Center(child: CircularProgressIndicator())
            : ListView.builder(
                itemCount: _orders.length,
                itemBuilder: (context, index) {
                  return OrderCard(order: _orders[index]);
                },
              ),
      ),
    );
  }
}
```

---

### 2️⃣ Restaurant App (DFDRestaurantPartner)

**Create: `lib/services/restaurant_fcm_service.dart`**

```dart
import 'package:dfd_restaurant_partner/services/fcm_service.dart';

class RestaurantFCMService extends FCMService {
  @override
  String _getDeviceTokenEndpoint() {
    return '/notifications/device-token';
  }
}
```

**In `lib/screens/new_orders_screen.dart`:**

```dart
class NewOrdersScreen extends StatefulWidget {
  @override
  State<NewOrdersScreen> createState() => _NewOrdersScreenState();
}

class _NewOrdersScreenState extends State<NewOrdersScreen> {
  final RestaurantFCMService _fcmService = RestaurantFCMService();
  List<Order> _newOrders = [];
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadNewOrders();
    _setupFCMListener();
  }
  
  void _setupFCMListener() {
    // Auto-refresh when new order arrives
    _fcmService.onNewOrder = () {
      print('🔔 New order received! Auto-refreshing...');
      _refreshNewOrders();
      _playNotificationSound(); // Optional
    };
    
    _fcmService.onRefreshOrders = () {
      print('🔄 Refreshing new orders');
      _refreshNewOrders();
    };
  }
  
  Future<void> _loadNewOrders() async {
    setState(() => _isLoading = true);
    try {
      final orders = await ApiService.getNewOrders();
      setState(() {
        _newOrders = orders;
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading new orders: $e');
      setState(() => _isLoading = false);
    }
  }
  
  Future<void> _refreshNewOrders() async {
    try {
      final orders = await ApiService.getNewOrders();
      setState(() {
        _newOrders = orders;
      });
      
      // Show notification badge or alert
      if (orders.isNotEmpty) {
        _showNewOrderAlert(orders.length);
      }
    } catch (e) {
      print('Error refreshing new orders: $e');
    }
  }
  
  void _playNotificationSound() {
    // Implement sound/vibration
    // You can use audioplayers package
  }
  
  void _showNewOrderAlert(int count) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('🔔 You have $count new order(s)!'),
        backgroundColor: Colors.green,
        duration: Duration(seconds: 3),
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('New Orders'),
        actions: [
          if (_newOrders.isNotEmpty)
            Chip(
              label: Text('${_newOrders.length}'),
              backgroundColor: Colors.red,
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshNewOrders,
        child: _isLoading
            ? Center(child: CircularProgressIndicator())
            : _newOrders.isEmpty
                ? Center(child: Text('No new orders'))
                : ListView.builder(
                    itemCount: _newOrders.length,
                    itemBuilder: (context, index) {
                      return OrderCard(order: _newOrders[index]);
                    },
                  ),
      ),
    );
  }
}
```

**In `lib/screens/ongoing_orders_screen.dart`:**

```dart
class OngoingOrdersScreen extends StatefulWidget {
  @override
  State<OngoingOrdersScreen> createState() => _OngoingOrdersScreenState();
}

class _OngoingOrdersScreenState extends State<OngoingOrdersScreen> {
  final RestaurantFCMService _fcmService = RestaurantFCMService();
  List<Order> _ongoingOrders = [];
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadOngoingOrders();
    _setupFCMListener();
  }
  
  void _setupFCMListener() {
    _fcmService.onOrderUpdate = (orderId, status) {
      print('🔄 Order $orderId status changed to $status');
      _refreshOngoingOrders();
    };
    
    _fcmService.onRefreshOrders = () {
      _refreshOngoingOrders();
    };
  }
  
  Future<void> _loadOngoingOrders() async {
    setState(() => _isLoading = true);
    try {
      final orders = await ApiService.getOngoingOrders();
      setState(() {
        _ongoingOrders = orders;
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading ongoing orders: $e');
      setState(() => _isLoading = false);
    }
  }
  
  Future<void> _refreshOngoingOrders() async {
    try {
      final orders = await ApiService.getOngoingOrders();
      setState(() {
        _ongoingOrders = orders;
      });
    } catch (e) {
      print('Error refreshing ongoing orders: $e');
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Ongoing Orders')),
      body: RefreshIndicator(
        onRefresh: _refreshOngoingOrders,
        child: _isLoading
            ? Center(child: CircularProgressIndicator())
            : ListView.builder(
                itemCount: _ongoingOrders.length,
                itemBuilder: (context, index) {
                  return OrderCard(order: _ongoingOrders[index]);
                },
              ),
      ),
    );
  }
}
```

---

### 3️⃣ Delivery Partner App (dharai_delivery_boy)

**Create: `lib/services/delivery_fcm_service.dart`**

```dart
import 'package:dharai_delivery_boy/services/fcm_service.dart';

class DeliveryFCMService extends FCMService {
  @override
  String _getDeviceTokenEndpoint() {
    return '/delivery-partner/device-token';
  }
}
```

**In `lib/screens/available_orders_screen.dart`:**

```dart
class AvailableOrdersScreen extends StatefulWidget {
  @override
  State<AvailableOrdersScreen> createState() => _AvailableOrdersScreenState();
}

class _AvailableOrdersScreenState extends State<AvailableOrdersScreen> {
  final DeliveryFCMService _fcmService = DeliveryFCMService();
  List<Order> _availableOrders = [];
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadAvailableOrders();
    _setupFCMListener();
  }
  
  void _setupFCMListener() {
    // Refresh when new orders become available
    _fcmService.onRefreshOrders = () {
      print('🔔 New order available! Auto-refreshing...');
      _refreshAvailableOrders();
    };
    
    _fcmService.onOrderUpdate = (orderId, status) {
      if (status == 'ready' || status == 'handed_over') {
        print('🔔 Order $orderId is ready for pickup');
        _refreshAvailableOrders();
      }
    };
  }
  
  Future<void> _loadAvailableOrders() async {
    setState(() => _isLoading = true);
    try {
      final orders = await ApiService.getAvailableOrders();
      setState(() {
        _availableOrders = orders;
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading available orders: $e');
      setState(() => _isLoading = false);
    }
  }
  
  Future<void> _refreshAvailableOrders() async {
    try {
      final orders = await ApiService.getAvailableOrders();
      setState(() {
        _availableOrders = orders;
      });
      
      if (orders.isNotEmpty) {
        _showNewOrderNotification(orders.length);
      }
    } catch (e) {
      print('Error refreshing available orders: $e');
    }
  }
  
  void _showNewOrderNotification(int count) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('🚀 $count order(s) available for pickup!'),
        backgroundColor: Colors.orange,
        duration: Duration(seconds: 3),
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Available Orders')),
      body: RefreshIndicator(
        onRefresh: _refreshAvailableOrders,
        child: _isLoading
            ? Center(child: CircularProgressIndicator())
            : _availableOrders.isEmpty
                ? Center(child: Text('No available orders'))
                : ListView.builder(
                    itemCount: _availableOrders.length,
                    itemBuilder: (context, index) {
                      return OrderCard(order: _availableOrders[index]);
                    },
                  ),
      ),
    );
  }
}
```

**In `lib/screens/active_orders_screen.dart`:**

```dart
class ActiveOrdersScreen extends StatefulWidget {
  @override
  State<ActiveOrdersScreen> createState() => _ActiveOrdersScreenState();
}

class _ActiveOrdersScreenState extends State<ActiveOrdersScreen> {
  final DeliveryFCMService _fcmService = DeliveryFCMService();
  List<Order> _activeOrders = [];
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadActiveOrders();
    _setupFCMListener();
  }
  
  void _setupFCMListener() {
    _fcmService.onOrderUpdate = (orderId, status) {
      print('🔄 Active order updated: $orderId -> $status');
      _refreshActiveOrders();
    };
    
    _fcmService.onRefreshOrders = () {
      _refreshActiveOrders();
    };
  }
  
  Future<void> _loadActiveOrders() async {
    setState(() => _isLoading = true);
    try {
      final orders = await ApiService.getActiveOrders();
      setState(() {
        _activeOrders = orders;
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading active orders: $e');
      setState(() => _isLoading = false);
    }
  }
  
  Future<void> _refreshActiveOrders() async {
    try {
      final orders = await ApiService.getActiveOrders();
      setState(() {
        _activeOrders = orders;
      });
    } catch (e) {
      print('Error refreshing active orders: $e');
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Active Orders')),
      body: RefreshIndicator(
        onRefresh: _refreshActiveOrders,
        child: _isLoading
            ? Center(child: CircularProgressIndicator())
            : ListView.builder(
                itemCount: _activeOrders.length,
                itemBuilder: (context, index) {
                  return OrderCard(order: _activeOrders[index]);
                },
              ),
      ),
    );
  }
}
```

---

### 4️⃣ Admin App

**In `lib/main.dart`:**

```dart
class _MyAppState extends State<MyApp> {
  final FCMService _fcmService = FCMService();
  
  @override
  void initState() {
    super.initState();
    _initializeFCM();
  }
  
  Future<void> _initializeFCM() async {
    await _fcmService.initialize();
    
    // Subscribe to admin updates topic
    await _fcmService.subscribeToTopic('admin_updates');
  }
  
  // ... rest of your code
}
```

**In admin order screens:**

```dart
class AdminOrdersScreen extends StatefulWidget {
  @override
  State<AdminOrdersScreen> createState() => _AdminOrdersScreenState();
}

class _AdminOrdersScreenState extends State<AdminOrdersScreen> {
  final FCMService _fcmService = FCMService();
  
  @override
  void initState() {
    super.initState();
    _setupFCMListener();
  }
  
  void _setupFCMListener() {
    _fcmService.onRefreshOrders = () {
      print('🔄 Admin: Refreshing all orders');
      _refreshOrders();
    };
  }
  
  Future<void> _refreshOrders() async {
    // Refresh admin order list
  }
  
  // ... rest of your code
}
```

---

## 🧪 Testing Auto-Refresh

### Test Scenario 1: Customer App
1. Customer places order
2. Restaurant accepts order
3. **✅ Customer app should auto-refresh** and show "Order Confirmed"
4. No manual refresh needed!

### Test Scenario 2: Restaurant App
1. Customer places order
2. **✅ Restaurant app should auto-refresh** "New Orders" screen
3. Sound/vibration notification (optional)
4. Badge count updates

### Test Scenario 3: Delivery App
1. Restaurant marks order as "Ready"
2. **✅ Delivery app should auto-refresh** "Available Orders"
3. New order appears in the list
4. Notification shown

### Test Scenario 4: Admin App
1. Any order status changes
2. **✅ Admin app receives FCM via topic**
3. Order list refreshes automatically

---

## 📊 FCM Notification Payload Structure

Your backend sends this data with each FCM notification:

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

### Notification Types:
- `order_update` - Order status changed
- `new_order` - New order for restaurant
- `new_available_order` - New order available for delivery
- `admin_order_refresh` - Admin topic notification

---

## 🐛 Common Issues & Solutions

### Issue 1: Notifications not received
**Solutions:**
- ✅ Check FCM token is sent to backend
- ✅ Verify Firebase project setup in Firebase Console
- ✅ Check device permissions (Settings > Notifications)
- ✅ Ensure `google-services.json` (Android) or `GoogleService-Info.plist` (iOS) is added
- ✅ Check backend logs for FCM send errors

### Issue 2: App doesn't refresh
**Solutions:**
- ✅ Ensure `onOrderUpdate` or `onRefreshOrders` callback is set in `initState()`
- ✅ Check if `setState()` is called in refresh function
- ✅ Verify API is being called (check network logs)
- ✅ Check console logs for FCM message handling

### Issue 3: Multiple refreshes
**Solutions:**
- ✅ Debounce the refresh function (use `Timer` to delay)
- ✅ Check if order ID matches before refreshing
- ✅ Avoid setting multiple listeners

### Issue 4: Token not registered
**Solutions:**
- ✅ Ensure user is logged in before registering token
- ✅ Check auth token is valid
- ✅ Verify endpoint URL is correct
- ✅ Check backend response (200 OK)

---

## 🎯 Summary Checklist

### Backend (Already Done ✅)
- ✅ FCM notifications sent for all order status changes
- ✅ Device token registration endpoints available
- ✅ Notifications sent to customers, restaurants, delivery partners
- ✅ Admin topic broadcasting implemented

### Customer App
- [ ] Add Firebase dependencies
- [ ] Initialize Firebase in `main.dart`
- [ ] Create `CustomerFCMService`
- [ ] Implement auto-refresh in `OrderTrackingScreen`
- [ ] Implement auto-refresh in `OrderHistoryScreen`
- [ ] Register device token on login

### Restaurant App
- [ ] Add Firebase dependencies
- [ ] Initialize Firebase in `main.dart`
- [ ] Create `RestaurantFCMService`
- [ ] Implement auto-refresh in `NewOrdersScreen`
- [ ] Implement auto-refresh in `OngoingOrdersScreen`
- [ ] Register device token on login
- [ ] Add sound/vibration for new orders (optional)

### Delivery Partner App
- [ ] Add Firebase dependencies
- [ ] Initialize Firebase in `main.dart`
- [ ] Create `DeliveryFCMService`
- [ ] Implement auto-refresh in `AvailableOrdersScreen`
- [ ] Implement auto-refresh in `ActiveOrdersScreen`
- [ ] Register device token on login

### Admin App
- [ ] Add Firebase dependencies
- [ ] Initialize Firebase in `main.dart`
- [ ] Subscribe to `admin_updates` topic
- [ ] Implement auto-refresh in order screens

---

## 🚀 Expected Result

After implementation:
- ✅ **Customer App**: Automatically shows order status updates in real-time
- ✅ **Restaurant App**: New orders appear instantly without refresh
- ✅ **Delivery Partner App**: Available orders update automatically
- ✅ **Admin App**: All order changes visible in real-time
- ✅ **No Manual Refresh**: Users never need to pull-to-refresh
- ✅ **Instant Updates**: Status changes appear within 1-2 seconds

---

## 📞 Support

If you encounter any issues:
1. Check console logs for FCM messages
2. Verify device token is registered in backend database
3. Test with backend in development mode (OTP visible in response)
4. Check Firebase Console for message delivery status

**Your backend is ready! Just implement the Flutter side and you're done! 🎉**
