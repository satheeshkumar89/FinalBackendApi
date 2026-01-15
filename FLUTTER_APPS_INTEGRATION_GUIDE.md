# 📱 Flutter Apps Integration Guide - Order Status Update

## 🎯 Overview

This guide explains **exactly what to do** in each of the 4 Flutter apps to implement the new order status flow.

---

## 📊 New Order Flow Summary

### Backend Status Flow:
```
PENDING → ACCEPTED → PREPARING → READY → ASSIGNED → REACHED_RESTAURANT → PICKED_UP → DELIVERED
```

### Restaurant App Flow (4 Steps):
```
1. Accept (PENDING → ACCEPTED)
2. Start Preparing (ACCEPTED → PREPARING)
3. Mark Ready (PREPARING → READY)
4. Hand Over (READY → HANDED_OVER) ✅ DONE
```

### Delivery Boy App Flow (4 Steps):
```
1. Accept (READY → ASSIGNED)
2. Reached Hotel (ASSIGNED → REACHED_RESTAURANT)
3. Pickup Order (REACHED_RESTAURANT → PICKED_UP)
4. Deliver (PICKED_UP → DELIVERED) ✅ DONE
```

---

# 🏪 App 1: Restaurant Partner App (DFDRestaurantPartner)

## 📋 Changes Required

### **1. Update Order Status Enum**

**File:** `lib/models/order.dart` or `lib/core/constants/enums.dart`

```dart
enum OrderStatus {
  PENDING,           // NEW - replaces "NEW"
  ACCEPTED,
  PREPARING,
  READY,
  HANDED_OVER,       // NEW - Step 4: Restaurant Done
  ASSIGNED,          // NEW - Delivery partner accepted
  REACHED_RESTAURANT,// NEW - Delivery partner at restaurant
  PICKED_UP,
  DELIVERED,
  REJECTED,
  CANCELLED,
}

// Helper to convert from API string
extension OrderStatusExtension on OrderStatus {
  static OrderStatus fromString(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return OrderStatus.PENDING;
      case 'accepted':
        return OrderStatus.ACCEPTED;
      case 'preparing':
        return OrderStatus.PREPARING;
      case 'ready':
        return OrderStatus.READY;
      case 'handed_over':
        return OrderStatus.HANDED_OVER;
      case 'assigned':
        return OrderStatus.ASSIGNED;
      case 'reached_restaurant':
        return OrderStatus.REACHED_RESTAURANT;
      case 'picked_up':
        return OrderStatus.PICKED_UP;
      case 'delivered':
        return OrderStatus.DELIVERED;
      case 'rejected':
        return OrderStatus.REJECTED;
      case 'cancelled':
        return OrderStatus.CANCELLED;
      default:
        return OrderStatus.PENDING;
    }
  }
  
  String toApiString() {
    return this.toString().split('.').last.toLowerCase();
  }
}
```

---

### **2. Update Order Model**

**File:** `lib/models/order.dart`

```dart
class Order {
  final int id;
  final String orderNumber;
  final OrderStatus status;
  final double totalAmount;
  final String customerName;
  final String customerPhone;
  final DateTime createdAt;
  
  // NEW: Add timeline fields
  final DateTime? acceptedAt;
  final DateTime? preparingAt;
  final DateTime? readyAt;
  final DateTime? handedOverAt;      // NEW
  final DateTime? assignedAt;         // NEW
  final DateTime? reachedRestaurantAt; // NEW
  final DateTime? pickedupAt;
  final DateTime? deliveredAt;
  
  Order({
    required this.id,
    required this.orderNumber,
    required this.status,
    required this.totalAmount,
    required this.customerName,
    required this.customerPhone,
    required this.createdAt,
    this.acceptedAt,
    this.preparingAt,
    this.readyAt,
    this.handedOverAt,
    this.assignedAt,
    this.reachedRestaurantAt,
    this.pickedupAt,
    this.deliveredAt,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['order_id'] ?? json['id'],
      orderNumber: json['order_number'] ?? '',
      status: OrderStatusExtension.fromString(json['status'] ?? 'pending'),
      totalAmount: double.parse(json['total_amount'].toString()),
      customerName: json['customer_name'] ?? '',
      customerPhone: json['customer_phone'] ?? '',
      createdAt: DateTime.parse(json['created_at']),
      acceptedAt: json['accepted_at'] != null ? DateTime.parse(json['accepted_at']) : null,
      preparingAt: json['preparing_at'] != null ? DateTime.parse(json['preparing_at']) : null,
      readyAt: json['ready_at'] != null ? DateTime.parse(json['ready_at']) : null,
      handedOverAt: json['handed_over_at'] != null ? DateTime.parse(json['handed_over_at']) : null,
      assignedAt: json['assigned_at'] != null ? DateTime.parse(json['assigned_at']) : null,
      reachedRestaurantAt: json['reached_restaurant_at'] != null ? DateTime.parse(json['reached_restaurant_at']) : null,
      pickedupAt: json['pickedup_at'] != null ? DateTime.parse(json['pickedup_at']) : null,
      deliveredAt: json['delivered_at'] != null ? DateTime.parse(json['delivered_at']) : null,
    );
  }
}
```

---

### **3. Update API Service**

**File:** `lib/services/order_service.dart`

```dart
class OrderService {
  final String baseUrl;
  final String token;

  OrderService({required this.baseUrl, required this.token});

  // UPDATED: Get new/pending orders
  Future<List<Order>> getNewOrders() async {
    final response = await http.get(
      Uri.parse('$baseUrl/orders/new'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final orders = (data['data']['orders'] as List)
          .map((order) => Order.fromJson(order))
          .toList();
      return orders;
    } else {
      throw Exception('Failed to load new orders');
    }
  }

  // UPDATED: Get ongoing orders (only restaurant's active orders)
  Future<List<Order>> getOngoingOrders() async {
    final response = await http.get(
      Uri.parse('$baseUrl/orders/ongoing'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final orders = (data['data']['orders'] as List)
          .map((order) => Order.fromJson(order))
          .toList();
      return orders;
    } else {
      throw Exception('Failed to load ongoing orders');
    }
  }

  // Step 1: Accept Order
  Future<void> acceptOrder(int orderId) async {
    final response = await http.put(
      Uri.parse('$baseUrl/orders/$orderId/accept'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to accept order');
    }
  }

  // Step 2: Start Preparing
  Future<void> startPreparing(int orderId) async {
    final response = await http.put(
      Uri.parse('$baseUrl/orders/$orderId/preparing'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to update order status');
    }
  }

  // Step 3: Mark Ready
  Future<void> markReady(int orderId) async {
    final response = await http.put(
      Uri.parse('$baseUrl/orders/$orderId/ready'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to mark order as ready');
    }
  }

  // NEW - Step 4: Hand Over to Delivery Partner
  Future<void> handOverOrder(int orderId) async {
    final response = await http.put(
      Uri.parse('$baseUrl/orders/$orderId/handover'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to hand over order');
    }
  }

  // Reject Order
  Future<void> rejectOrder(int orderId, String reason) async {
    final response = await http.post(
      Uri.parse('$baseUrl/orders/$orderId/reject'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({'rejection_reason': reason}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to reject order');
    }
  }
}
```

---

### **4. Update Orders Bloc/Provider**

**File:** `lib/bloc/orders_bloc.dart` or `lib/providers/orders_provider.dart`

```dart
// Using Bloc pattern
class OrdersBloc extends Bloc<OrdersEvent, OrdersState> {
  final OrderService orderService;

  OrdersBloc({required this.orderService}) : super(OrdersInitial()) {
    on<LoadNewOrders>(_onLoadNewOrders);
    on<LoadOngoingOrders>(_onLoadOngoingOrders);
    on<AcceptOrder>(_onAcceptOrder);
    on<StartPreparing>(_onStartPreparing);
    on<MarkReady>(_onMarkReady);
    on<HandOverOrder>(_onHandOverOrder);  // NEW
  }

  Future<void> _onLoadNewOrders(
    LoadNewOrders event,
    Emitter<OrdersState> emit,
  ) async {
    emit(OrdersLoading());
    try {
      final orders = await orderService.getNewOrders();
      emit(NewOrdersLoaded(orders));
    } catch (e) {
      emit(OrdersError(e.toString()));
    }
  }

  Future<void> _onLoadOngoingOrders(
    LoadOngoingOrders event,
    Emitter<OrdersState> emit,
  ) async {
    emit(OrdersLoading());
    try {
      final orders = await orderService.getOngoingOrders();
      emit(OngoingOrdersLoaded(orders));
    } catch (e) {
      emit(OrdersError(e.toString()));
    }
  }

  Future<void> _onAcceptOrder(
    AcceptOrder event,
    Emitter<OrdersState> emit,
  ) async {
    try {
      await orderService.acceptOrder(event.orderId);
      add(LoadNewOrders());  // Refresh list
      add(LoadOngoingOrders());  // Refresh ongoing list
    } catch (e) {
      emit(OrdersError(e.toString()));
    }
  }

  Future<void> _onStartPreparing(
    StartPreparing event,
    Emitter<OrdersState> emit,
  ) async {
    try {
      await orderService.startPreparing(event.orderId);
      add(LoadOngoingOrders());  // Refresh list
    } catch (e) {
      emit(OrdersError(e.toString()));
    }
  }

  Future<void> _onMarkReady(
    MarkReady event,
    Emitter<OrdersState> emit,
  ) async {
    try {
      await orderService.markReady(event.orderId);
      add(LoadOngoingOrders());  // Refresh list
    } catch (e) {
      emit(OrdersError(e.toString()));
    }
  }

  // NEW: Hand Over Order (Step 4)
  Future<void> _onHandOverOrder(
    HandOverOrder event,
    Emitter<OrdersState> emit,
  ) async {
    try {
      await orderService.handOverOrder(event.orderId);
      add(LoadOngoingOrders());  // Refresh ongoing
      add(LoadCompletedOrders());  // Refresh completed
    } catch (e) {
      emit(OrdersError(e.toString()));
    }
  }
}
```

---

### **5. Update UI - Order Card Widget**

**File:** `lib/widgets/order_card.dart`

```dart
class OrderCard extends StatelessWidget {
  final Order order;
  final VoidCallback onRefresh;

  const OrderCard({
    Key? key,
    required this.order,
    required this.onRefresh,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.all(8),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Order header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Order #${order.orderNumber}',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                _buildStatusChip(order.status),
              ],
            ),
            SizedBox(height: 12),
            
            // Customer info
            Text('Customer: ${order.customerName}'),
            Text('Phone: ${order.customerPhone}'),
            Text('Amount: ₹${order.totalAmount.toStringAsFixed(2)}'),
            Text(
              'Time: ${_formatTime(order.createdAt)}',
              style: TextStyle(color: Colors.grey),
            ),
            
            SizedBox(height: 16),
            
            // Action buttons based on status
            _buildActionButtons(context, order),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusChip(OrderStatus status) {
    Color color;
    String text;
    
    switch (status) {
      case OrderStatus.PENDING:
        color = Colors.orange;
        text = 'Pending';
        break;
      case OrderStatus.ACCEPTED:
        color = Colors.blue;
        text = 'Accepted';
        break;
      case OrderStatus.PREPARING:
        color = Colors.purple;
        text = 'Preparing';
        break;
      case OrderStatus.READY:
        color = Colors.green;
        text = 'Ready';
        break;
      case OrderStatus.HANDED_OVER:
        color = Colors.teal;
        text = 'Handed Over';
        break;
      default:
        color = Colors.grey;
        text = status.toString().split('.').last;
    }
    
    return Chip(
      label: Text(text, style: TextStyle(color: Colors.white)),
      backgroundColor: color,
    );
  }

  Widget _buildActionButtons(BuildContext context, Order order) {
    switch (order.status) {
      case OrderStatus.PENDING:
        // Step 1: Accept or Reject
        return Row(
          children: [
            Expanded(
              child: ElevatedButton(
                onPressed: () => _acceptOrder(context, order.id),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                child: Text('Accept Order'),
              ),
            ),
            SizedBox(width: 8),
            Expanded(
              child: OutlinedButton(
                onPressed: () => _showRejectDialog(context, order.id),
                style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                child: Text('Reject'),
              ),
            ),
          ],
        );

      case OrderStatus.ACCEPTED:
        // Step 2: Start Preparing
        return SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () => _startPreparing(context, order.id),
            icon: Icon(Icons.restaurant),
            label: Text('Start Preparing'),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.blue),
          ),
        );

      case OrderStatus.PREPARING:
        // Step 3: Mark Ready
        return SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () => _markReady(context, order.id),
            icon: Icon(Icons.check_circle),
            label: Text('Mark Ready for Pickup'),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.purple),
          ),
        );

      case OrderStatus.READY:
        // Step 4: Hand Over (NEW)
        return SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () => _handOverOrder(context, order.id),
            icon: Icon(Icons.handshake),
            label: Text('Hand Over to Delivery Partner'),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
          ),
        );

      default:
        return SizedBox.shrink();
    }
  }

  void _acceptOrder(BuildContext context, int orderId) {
    context.read<OrdersBloc>().add(AcceptOrder(orderId));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Order accepted successfully!')),
    );
  }

  void _startPreparing(BuildContext context, int orderId) {
    context.read<OrdersBloc>().add(StartPreparing(orderId));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Started preparing order!')),
    );
  }

  void _markReady(BuildContext context, int orderId) {
    context.read<OrdersBloc>().add(MarkReady(orderId));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Order marked as ready!')),
    );
  }

  // NEW: Hand Over action
  void _handOverOrder(BuildContext context, int orderId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Hand Over Order'),
        content: Text('Have you handed over this order to the delivery partner?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<OrdersBloc>().add(HandOverOrder(orderId));
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Order handed over successfully!'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            child: Text('Confirm'),
          ),
        ],
      ),
    );
  }

  void _showRejectDialog(BuildContext context, int orderId) {
    // Implementation for reject dialog
  }

  String _formatTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inMinutes < 60) {
      return '${difference.inMinutes} mins ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} hours ago';
    } else {
      return '${dateTime.day}/${dateTime.month}/${dateTime.year}';
    }
  }
}
```

---

### **6. Update Orders Screen**

**File:** `lib/screens/orders_screen.dart`

```dart
class OrdersScreen extends StatefulWidget {
  @override
  _OrdersScreenState createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    
    // Load orders for each tab
    context.read<OrdersBloc>().add(LoadNewOrders());
    context.read<OrdersBloc>().add(LoadOngoingOrders());
    context.read<OrdersBloc>().add(LoadCompletedOrders());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Orders'),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: 'New', icon: Icon(Icons.notifications)),
            Tab(text: 'Ongoing', icon: Icon(Icons.restaurant)),
            Tab(text: 'Completed', icon: Icon(Icons.check_circle)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // Tab 1: New/Pending Orders (PENDING status only)
          _buildNewOrdersTab(),
          
          // Tab 2: Ongoing Orders (ACCEPTED, PREPARING, READY)
          _buildOngoingOrdersTab(),
          
          // Tab 3: Completed Orders (HANDED_OVER, DELIVERED, etc.)
          _buildCompletedOrdersTab(),
        ],
      ),
    );
  }

  Widget _buildNewOrdersTab() {
    return BlocBuilder<OrdersBloc, OrdersState>(
      builder: (context, state) {
        if (state is OrdersLoading) {
          return Center(child: CircularProgressIndicator());
        } else if (state is NewOrdersLoaded) {
          if (state.orders.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.inbox, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('No pending orders', style: TextStyle(fontSize: 18)),
                ],
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () async {
              context.read<OrdersBloc>().add(LoadNewOrders());
            },
            child: ListView.builder(
              itemCount: state.orders.length,
              itemBuilder: (context, index) {
                return OrderCard(
                  order: state.orders[index],
                  onRefresh: () {
                    context.read<OrdersBloc>().add(LoadNewOrders());
                  },
                );
              },
            ),
          );
        } else if (state is OrdersError) {
          return Center(child: Text('Error: ${state.message}'));
        }
        return Container();
      },
    );
  }

  Widget _buildOngoingOrdersTab() {
    return BlocBuilder<OrdersBloc, OrdersState>(
      builder: (context, state) {
        if (state is OrdersLoading) {
          return Center(child: CircularProgressIndicator());
        } else if (state is OngoingOrdersLoaded) {
          if (state.orders.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.restaurant_menu, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('No ongoing orders', style: TextStyle(fontSize: 18)),
                ],
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () async {
              context.read<OrdersBloc>().add(LoadOngoingOrders());
            },
            child: ListView.builder(
              itemCount: state.orders.length,
              itemBuilder: (context, index) {
                return OrderCard(
                  order: state.orders[index],
                  onRefresh: () {
                    context.read<OrdersBloc>().add(LoadOngoingOrders());
                  },
                );
              },
            ),
          );
        } else if (state is OrdersError) {
          return Center(child: Text('Error: ${state.message}'));
        }
        return Container();
      },
    );
  }

  Widget _buildCompletedOrdersTab() {
    // Similar implementation for completed orders
    return BlocBuilder<OrdersBloc, OrdersState>(
      builder: (context, state) {
        if (state is CompletedOrdersLoaded) {
          return ListView.builder(
            itemCount: state.orders.length,
            itemBuilder: (context, index) {
              return OrderCard(
                order: state.orders[index],
                onRefresh: () {
                  context.read<OrdersBloc>().add(LoadCompletedOrders());
                },
              );
            },
          );
        }
        return Container();
      },
    );
  }
}
```

---

## 🎯 **Restaurant App Summary**

### What Changed:
1. ✅ **Status Enum** - Added PENDING, HANDED_OVER, ASSIGNED, REACHED_RESTAURANT
2. ✅ **Order Model** - Added 3 new timestamp fields
3. ✅ **API Service** - Added `handOverOrder()` method
4. ✅ **Bloc/Provider** - Added `HandOverOrder` event
5. ✅ **UI** - Added "Hand Over" button for READY status

### New Order Flow in UI:
```
New Tab (PENDING) → [Accept] button
Ongoing Tab (ACCEPTED) → [Start Preparing] button
Ongoing Tab (PREPARING) → [Mark Ready] button
Ongoing Tab (READY) → [Hand Over] button → Moves to Completed Tab
Completed Tab (HANDED_OVER) → Shows completed orders
```

---

# 🚴 App 2: Delivery Boy App (dharai_delivery_boy)

## 📋 Changes Required

### **1. Update Order Status Enum** (Same as Restaurant App)

```dart
enum OrderStatus {
  PENDING,
  ACCEPTED,
  PREPARING,
  READY,
  HANDED_OVER,
  ASSIGNED,           // NEW - I accepted the delivery
  REACHED_RESTAURANT, // NEW - I'm at the restaurant
  PICKED_UP,
  DELIVERED,
  REJECTED,
  CANCELLED,
}
```

---

### **2. Update API Service**

**File:** `lib/services/delivery_service.dart`

```dart
class DeliveryService {
  final String baseUrl;
  final String token;

  DeliveryService({required this.baseUrl, required this.token});

  // UPDATED: Get available orders (only READY status)
  Future<List<Order>> getAvailableOrders() async {
    final response = await http.get(
      Uri.parse('$baseUrl/delivery-partner/orders/available'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return (data as List).map((order) => Order.fromJson(order)).toList();
    } else {
      throw Exception('Failed to load available orders');
    }
  }

  // UPDATED: Get active orders (ASSIGNED, REACHED_RESTAURANT, PICKED_UP)
  Future<List<Order>> getActiveOrders() async {
    final response = await http.get(
      Uri.parse('$baseUrl/delivery-partner/orders/active'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return (data as List).map((order) => Order.fromJson(order)).toList();
    } else {
      throw Exception('Failed to load active orders');
    }
  }

  // Step 1: Accept Order for Delivery
  Future<void> acceptOrder(int orderId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/delivery-partner/orders/$orderId/accept'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to accept order');
    }
  }

  // NEW - Step 2: Mark Reached Restaurant
  Future<void> markReachedRestaurant(int orderId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/delivery-partner/orders/$orderId/reached'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to update status');
    }
  }

  // NEW - Step 3: Pickup Order
  Future<void> pickupOrder(int orderId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/delivery-partner/orders/$orderId/pickup'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to pickup order');
    }
  }

  // Step 4: Mark Delivered
  Future<void> markDelivered(int orderId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/delivery-partner/orders/$orderId/complete'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to mark as delivered');
    }
  }
}
```

---

### **3. Update Delivery Orders Bloc**

**File:** `lib/bloc/delivery_orders_bloc.dart`

```dart
class DeliveryOrdersBloc extends Bloc<DeliveryOrdersEvent, DeliveryOrdersState> {
  final DeliveryService deliveryService;

  DeliveryOrdersBloc({required this.deliveryService}) : super(DeliveryOrdersInitial()) {
    on<LoadAvailableOrders>(_onLoadAvailableOrders);
    on<LoadActiveOrders>(_onLoadActiveOrders);
    on<AcceptDeliveryOrder>(_onAcceptOrder);
    on<MarkReachedRestaurant>(_onMarkReachedRestaurant);  // NEW
    on<PickupOrder>(_onPickupOrder);  // NEW
    on<MarkDelivered>(_onMarkDelivered);
  }

  Future<void> _onLoadAvailableOrders(
    LoadAvailableOrders event,
    Emitter<DeliveryOrdersState> emit,
  ) async {
    emit(DeliveryOrdersLoading());
    try {
      final orders = await deliveryService.getAvailableOrders();
      emit(AvailableOrdersLoaded(orders));
    } catch (e) {
      emit(DeliveryOrdersError(e.toString()));
    }
  }

  Future<void> _onLoadActiveOrders(
    LoadActiveOrders event,
    Emitter<DeliveryOrdersState> emit,
  ) async {
    emit(DeliveryOrdersLoading());
    try {
      final orders = await deliveryService.getActiveOrders();
      emit(ActiveOrdersLoaded(orders));
    } catch (e) {
      emit(DeliveryOrdersError(e.toString()));
    }
  }

  Future<void> _onAcceptOrder(
    AcceptDeliveryOrder event,
    Emitter<DeliveryOrdersState> emit,
  ) async {
    try {
      await deliveryService.acceptOrder(event.orderId);
      add(LoadAvailableOrders());  // Refresh available
      add(LoadActiveOrders());  // Refresh active
    } catch (e) {
      emit(DeliveryOrdersError(e.toString()));
    }
  }

  // NEW: Mark Reached Restaurant (Step 2)
  Future<void> _onMarkReachedRestaurant(
    MarkReachedRestaurant event,
    Emitter<DeliveryOrdersState> emit,
  ) async {
    try {
      await deliveryService.markReachedRestaurant(event.orderId);
      add(LoadActiveOrders());  // Refresh active orders
    } catch (e) {
      emit(DeliveryOrdersError(e.toString()));
    }
  }

  // NEW: Pickup Order (Step 3)
  Future<void> _onPickupOrder(
    PickupOrder event,
    Emitter<DeliveryOrdersState> emit,
  ) async {
    try {
      await deliveryService.pickupOrder(event.orderId);
      add(LoadActiveOrders());  // Refresh active orders
    } catch (e) {
      emit(DeliveryOrdersError(e.toString()));
    }
  }

  Future<void> _onMarkDelivered(
    MarkDelivered event,
    Emitter<DeliveryOrdersState> emit,
  ) async {
    try {
      await deliveryService.markDelivered(event.orderId);
      add(LoadActiveOrders());  // Refresh active
      add(LoadCompletedOrders());  // Refresh completed
    } catch (e) {
      emit(DeliveryOrdersError(e.toString()));
    }
  }
}

// NEW Events
class MarkReachedRestaurant extends DeliveryOrdersEvent {
  final int orderId;
  MarkReachedRestaurant(this.orderId);
}

class PickupOrder extends DeliveryOrdersEvent {
  final int orderId;
  PickupOrder(this.orderId);
}
```

---

### **4. Update UI - Delivery Order Card**

**File:** `lib/widgets/delivery_order_card.dart`

```dart
class DeliveryOrderCard extends StatelessWidget {
  final Order order;
  final VoidCallback onRefresh;

  const DeliveryOrderCard({
    Key? key,
    required this.order,
    required this.onRefresh,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.all(8),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Order header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Order #${order.orderNumber}',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                _buildStatusChip(order.status),
              ],
            ),
            SizedBox(height: 12),
            
            // Restaurant info
            Row(
              children: [
                Icon(Icons.restaurant, size: 20, color: Colors.blue),
                SizedBox(width: 8),
                Text(
                  order.restaurantName ?? 'Restaurant',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
              ],
            ),
            SizedBox(height: 8),
            
            // Customer info
            Row(
              children: [
                Icon(Icons.person, size: 20, color: Colors.green),
                SizedBox(width: 8),
                Text('${order.customerName} • ${order.customerPhone}'),
              ],
            ),
            SizedBox(height: 8),
            
            // Address
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.location_on, size: 20, color: Colors.red),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    order.deliveryAddress,
                    style: TextStyle(fontSize: 14),
                  ),
                ),
              ],
            ),
            SizedBox(height: 8),
            
            // Amount
            Row(
              children: [
                Icon(Icons.attach_money, size: 20, color: Colors.orange),
                SizedBox(width: 8),
                Text(
                  '₹${order.totalAmount.toStringAsFixed(2)}',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 16),
            
            // Action buttons based on status
            _buildActionButtons(context, order),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusChip(OrderStatus status) {
    Color color;
    String text;
    IconData icon;
    
    switch (status) {
      case OrderStatus.READY:
        color = Colors.orange;
        text = 'Ready for Pickup';
        icon = Icons.restaurant;
        break;
      case OrderStatus.ASSIGNED:
        color = Colors.blue;
        text = 'Assigned to Me';
        icon = Icons.check_circle;
        break;
      case OrderStatus.REACHED_RESTAURANT:
        color = Colors.purple;
        text = 'At Restaurant';
        icon = Icons.location_on;
        break;
      case OrderStatus.PICKED_UP:
        color = Colors.green;
        text = 'On the Way';
        icon = Icons.delivery_dining;
        break;
      default:
        color = Colors.grey;
        text = status.toString().split('.').last;
        icon = Icons.info;
    }
    
    return Chip(
      avatar: Icon(icon, color: Colors.white, size: 18),
      label: Text(text, style: TextStyle(color: Colors.white)),
      backgroundColor: color,
    );
  }

  Widget _buildActionButtons(BuildContext context, Order order) {
    switch (order.status) {
      case OrderStatus.READY:
        // Step 1: Accept for Delivery
        return SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () => _acceptOrder(context, order),
            icon: Icon(Icons.check_circle),
            label: Text('Accept Delivery'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
              padding: EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        );

      case OrderStatus.ASSIGNED:
        // Step 2: Mark Reached Restaurant
        return SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () => _markReachedRestaurant(context, order.id),
            icon: Icon(Icons.location_on),
            label: Text('I\'ve Reached Restaurant'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
              padding: EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        );

      case OrderStatus.REACHED_RESTAURANT:
        // Step 3: Pickup Order
        return SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () => _pickupOrder(context, order.id),
            icon: Icon(Icons.shopping_bag),
            label: Text('Pickup Order'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.purple,
              padding: EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        );

      case OrderStatus.PICKED_UP:
        // Step 4: Mark Delivered
        return Column(
          children: [
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _navigateToCustomer(context, order),
                icon: Icon(Icons.navigation),
                label: Text('Navigate to Customer'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  padding: EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
            SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _markDelivered(context, order.id),
                icon: Icon(Icons.done_all),
                label: Text('Mark as Delivered'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
          ],
        );

      default:
        return SizedBox.shrink();
    }
  }

  void _acceptOrder(BuildContext context, Order order) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Accept Delivery?'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Restaurant: ${order.restaurantName}'),
            SizedBox(height: 8),
            Text('Customer: ${order.customerName}'),
            SizedBox(height: 8),
            Text('Amount: ₹${order.totalAmount.toStringAsFixed(2)}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<DeliveryOrdersBloc>().add(
                AcceptDeliveryOrder(order.id),
              );
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Order accepted! Navigate to restaurant.'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            child: Text('Accept'),
          ),
        ],
      ),
    );
  }

  // NEW: Mark Reached Restaurant
  void _markReachedRestaurant(BuildContext context, int orderId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Reached Restaurant?'),
        content: Text('Confirm that you have reached the restaurant.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<DeliveryOrdersBloc>().add(
                MarkReachedRestaurant(orderId),
              );
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Marked as reached. Wait for order pickup.'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
            child: Text('Confirm'),
          ),
        ],
      ),
    );
  }

  // NEW: Pickup Order
  void _pickupOrder(BuildContext context, int orderId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Pickup Order?'),
        content: Text('Confirm that you have picked up the order from restaurant.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<DeliveryOrdersBloc>().add(
                PickupOrder(orderId),
              );
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Order picked up! Navigate to customer.'),
                  backgroundColor: Colors.purple,
                ),
              );
            },
            child: Text('Confirm'),
          ),
        ],
      ),
    );
  }

  void _navigateToCustomer(BuildContext context, Order order) {
    // Open Google Maps or your navigation
    // Example: launch('google.navigation:q=${order.latitude},${order.longitude}');
  }

  void _markDelivered(BuildContext context, int orderId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Mark as Delivered?'),
        content: Text('Confirm that you have delivered the order to the customer.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<DeliveryOrdersBloc>().add(
                MarkDelivered(orderId),
              );
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Order delivered successfully! 🎉'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            child: Text('Delivered'),
          ),
        ],
      ),
    );
  }
}
```

---

### **5. Update Delivery Screen**

**File:** `lib/screens/delivery_screen.dart`

```dart
class DeliveryScreen extends StatefulWidget {
  @override
  _DeliveryScreenState createState() => _DeliveryScreenState();
}

class _DeliveryScreenState extends State<DeliveryScreen> 
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    
    // Load orders
    context.read<DeliveryOrdersBloc>().add(LoadAvailableOrders());
    context.read<DeliveryOrdersBloc>().add(LoadActiveOrders());
    context.read<DeliveryOrdersBloc>().add(LoadCompletedOrders());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Deliveries'),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: 'Available', icon: Icon(Icons.local_dining)),
            Tab(text: 'Active', icon: Icon(Icons.delivery_dining)),
            Tab(text: 'History', icon: Icon(Icons.history)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // Tab 1: Available Orders (READY status only)
          _buildAvailableOrdersTab(),
          
          // Tab 2: Active Orders (ASSIGNED, REACHED_RESTAURANT, PICKED_UP)
          _buildActiveOrdersTab(),
          
          // Tab 3: Completed Orders (DELIVERED)
          _buildCompletedOrdersTab(),
        ],
      ),
    );
  }

  Widget _buildAvailableOrdersTab() {
    return BlocBuilder<DeliveryOrdersBloc, DeliveryOrdersState>(
      builder: (context, state) {
        if (state is DeliveryOrdersLoading) {
          return Center(child: CircularProgressIndicator());
        } else if (state is AvailableOrdersLoaded) {
          if (state.orders.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.inbox, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'No available orders nearby',
                    style: TextStyle(fontSize: 18),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Check back soon!',
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () async {
              context.read<DeliveryOrdersBloc>().add(LoadAvailableOrders());
            },
            child: ListView.builder(
              itemCount: state.orders.length,
              itemBuilder: (context, index) {
                return DeliveryOrderCard(
                  order: state.orders[index],
                  onRefresh: () {
                    context.read<DeliveryOrdersBloc>().add(LoadAvailableOrders());
                  },
                );
              },
            ),
          );
        } else if (state is DeliveryOrdersError) {
          return Center(child: Text('Error: ${state.message}'));
        }
        return Container();
      },
    );
  }

  Widget _buildActiveOrdersTab() {
    return BlocBuilder<DeliveryOrdersBloc, DeliveryOrdersState>(
      builder: (context, state) {
        if (state is DeliveryOrdersLoading) {
          return Center(child: CircularProgressIndicator());
        } else if (state is ActiveOrdersLoaded) {
          if (state.orders.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.delivery_dining, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'No active deliveries',
                    style: TextStyle(fontSize: 18),
                  ),
                ],
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () async {
              context.read<DeliveryOrdersBloc>().add(LoadActiveOrders());
            },
            child: ListView.builder(
              itemCount: state.orders.length,
              itemBuilder: (context, index) {
                return DeliveryOrderCard(
                  order: state.orders[index],
                  onRefresh: () {
                    context.read<DeliveryOrdersBloc>().add(LoadActiveOrders());
                  },
                );
              },
            ),
          );
        } else if (state is DeliveryOrdersError) {
          return Center(child: Text('Error: ${state.message}'));
        }
        return Container();
      },
    );
  }

  Widget _buildCompletedOrdersTab() {
    // Similar implementation for completed orders
    return BlocBuilder<DeliveryOrdersBloc, DeliveryOrdersState>(
      builder: (context, state) {
        if (state is CompletedOrdersLoaded) {
          return ListView.builder(
            itemCount: state.orders.length,
            itemBuilder: (context, index) {
              final order = state.orders[index];
              return ListTile(
                leading: Icon(Icons.check_circle, color: Colors.green),
                title: Text('Order #${order.orderNumber}'),
                subtitle: Text('Delivered • ₹${order.totalAmount}'),
                trailing: Text(
                  _formatDate(order.deliveredAt!),
                  style: TextStyle(color: Colors.grey),
                ),
              );
            },
          );
        }
        return Container();
      },
    );
  }

  String _formatDate(DateTime date) {
    // Format date implementation
    return '${date.day}/${date.month}/${date.year}';
  }
}
```

---

## 🎯 **Delivery Boy App Summary**

### What Changed:
1. ✅ **Available Orders** - Now shows only `READY` status
2. ✅ **Active Orders** - Shows `ASSIGNED`, `REACHED_RESTAURANT`, `PICKED_UP`
3. ✅ **New Endpoints** - Added 2 new API calls: `markReachedRestaurant()`, `pickupOrder()`
4. ✅ **New Buttons** - Added "I've Reached" and "Pickup Order" buttons
5. ✅ **4-Step Flow** - Clear progression through all 4 steps

### New Order Flow in UI:
```
Available Tab (READY) → [Accept Delivery] → Moves to Active Tab

Active Tab (ASSIGNED) → [I've Reached Restaurant]
Active Tab (REACHED_RESTAURANT) → [Pickup Order]
Active Tab (PICKED_UP) → [Navigate] + [Mark Delivered]

History Tab (DELIVERED) → Shows completed deliveries
```

---

*Continued in next message for Customer App and Admin App...*
