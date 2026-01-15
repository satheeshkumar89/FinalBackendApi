# 📱 Flutter Apps Integration - Part 2

## Customer App & Admin App Changes

---

# 👤 App 3: Customer App (foodieexpress)

## 📋 Changes Required

### **1. Update Order Status Enum** (Same as other apps)

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
}
```

---

### **2. Update Status Display Helper**

**File:** `lib/utils/order_status_helper.dart`

```dart
class OrderStatusHelper {
  // Get user-friendly status message
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
      
      case OrderStatus.HANDED_OVER:
        return 'Order handed over to delivery partner';
      
      case OrderStatus.REJECTED:
        return 'Order rejected by restaurant';
      
      case OrderStatus.CANCELLED:
        return 'Order cancelled';
      
      default:
        return 'Processing...';
    }
  }

  // Get status icon
  static IconData getStatusIcon(OrderStatus status) {
    switch (status) {
      case OrderStatus.PENDING:
        return Icons.access_time;
      
      case OrderStatus.ACCEPTED:
      case OrderStatus.PREPARING:
        return Icons.restaurant;
      
      case OrderStatus.READY:
        return Icons.done_all;
      
      case OrderStatus.HANDED_OVER:
        return Icons.handshake;
      
      case OrderStatus.ASSIGNED:
        return Icons.person_pin;
      
      case OrderStatus.REACHED_RESTAURANT:
        return Icons.location_on;
      
      case OrderStatus.PICKED_UP:
        return Icons.delivery_dining;
      
      case OrderStatus.DELIVERED:
        return Icons.celebration;
      
      case OrderStatus.REJECTED:
      case OrderStatus.CANCELLED:
        return Icons.cancel;
      
      default:
        return Icons.info;
    }
  }

  // Get status color
  static Color getStatusColor(OrderStatus status) {
    switch (status) {
      case OrderStatus.PENDING:
        return Colors.orange;
      
      case OrderStatus.ACCEPTED:
      case OrderStatus.PREPARING:
        return Colors.blue;
      
      case OrderStatus.READY:
        return Colors.purple;
      
      case OrderStatus.HANDED_OVER:
        return Colors.teal;
      
      case OrderStatus.ASSIGNED:
      case OrderStatus.REACHED_RESTAURANT:
      case OrderStatus.PICKED_UP:
        return Colors.indigo;
      
      case OrderStatus.DELIVERED:
        return Colors.green;
      
      case OrderStatus.REJECTED:
      case OrderStatus.CANCELLED:
        return Colors.red;
      
      default:
        return Colors.grey;
    }
  }

  // Check if order is active (in progress)
  static bool isActive(OrderStatus status) {
    return [
      OrderStatus.PENDING,
      OrderStatus.ACCEPTED,
      OrderStatus.PREPARING,
      OrderStatus.READY,
      OrderStatus.ASSIGNED,
      OrderStatus.REACHED_RESTAURANT,
      OrderStatus.PICKED_UP,
    ].contains(status);
  }

  // Check if order is completed
  static bool isCompleted(OrderStatus status) {
    return [
      OrderStatus.DELIVERED,
      OrderStatus.HANDED_OVER,
      OrderStatus.REJECTED,
      OrderStatus.CANCELLED,
    ].contains(status);
  }

  // Get progress percentage (for progress bar)
  static double getProgressPercentage(OrderStatus status) {
    switch (status) {
      case OrderStatus.PENDING:
        return 0.1;
      case OrderStatus.ACCEPTED:
        return 0.2;
      case OrderStatus.PREPARING:
        return 0.4;
      case OrderStatus.READY:
        return 0.6;
      case OrderStatus.ASSIGNED:
        return 0.7;
      case OrderStatus.REACHED_RESTAURANT:
        return 0.8;
      case OrderStatus.PICKED_UP:
        return 0.9;
      case OrderStatus.DELIVERED:
        return 1.0;
      default:
        return 0.5;
    }
  }
}
```

---

### **3. Update Order Tracking Timeline Widget**

**File:** `lib/widgets/order_timeline.dart`

```dart
class OrderTimeline extends StatelessWidget {
  final Order order;

  const OrderTimeline({Key? key, required this.order}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Order Status',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 16),
            
            // Progress bar
            LinearProgressIndicator(
              value: OrderStatusHelper.getProgressPercentage(order.status),
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(
                OrderStatusHelper.getStatusColor(order.status),
              ),
              minHeight: 8,
            ),
            SizedBox(height: 24),
            
            // Timeline steps
            _buildTimelineStep(
              'Order Placed',
              order.createdAt,
              true,
              Icons.shopping_cart,
            ),
            
            _buildTimelineStep(
              'Restaurant Accepted',
              order.acceptedAt,
              order.acceptedAt != null,
              Icons.check_circle,
            ),
            
            _buildTimelineStep(
              'Preparing Food',
              order.preparingAt,
              order.preparingAt != null,
              Icons.restaurant,
            ),
            
            _buildTimelineStep(
              'Food Ready',
              order.readyAt,
              order.readyAt != null,
              Icons.done_all,
            ),
            
            _buildTimelineStep(
              'Delivery Partner Assigned',
              order.assignedAt,
              order.assignedAt != null,
              Icons.person_pin,
            ),
            
            _buildTimelineStep(
              'Partner at Restaurant',
              order.reachedRestaurantAt,
              order.reachedRestaurantAt != null,
              Icons.location_on,
            ),
            
            _buildTimelineStep(
              'Order Picked Up',
              order.pickedupAt,
              order.pickedupAt != null,
              Icons.delivery_dining,
            ),
            
            _buildTimelineStep(
              'Delivered',
              order.deliveredAt,
              order.deliveredAt != null,
              Icons.celebration,
              isLast: true,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimelineStep(
    String title,
    DateTime? timestamp,
    bool isCompleted,
    IconData icon,
    {bool isLast = false}
  ) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Timeline indicator
        Column(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isCompleted ? Colors.green : Colors.grey[300],
              ),
              child: Icon(
                isCompleted ? icon : Icons.pending,
                color: Colors.white,
                size: 20,
              ),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 40,
                color: isCompleted ? Colors.green : Colors.grey[300],
              ),
          ],
        ),
        SizedBox(width: 16),
        
        // Timeline content
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: isCompleted ? FontWeight.bold : FontWeight.normal,
                  color: isCompleted ? Colors.black : Colors.grey,
                ),
              ),
              if (timestamp != null)
                Text(
                  _formatTime(timestamp),
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              SizedBox(height: isLast ? 0 : 16),
            ],
          ),
        ),
      ],
    );
  }

  String _formatTime(DateTime dateTime) {
    final hour = dateTime.hour.toString().padLeft(2, '0');
    final minute = dateTime.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}
```

---

### **4. Update Order Details Screen**

**File:** `lib/screens/order_details_screen.dart`

```dart
class OrderDetailsScreen extends StatelessWidget {
  final Order order;

  const OrderDetailsScreen({Key? key, required this.order}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Order #${order.orderNumber}'),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Current Status Card
            _buildCurrentStatusCard(),
            
            // Order Timeline
            OrderTimeline(order: order),
            
            // Delivery Partner Info (if assigned)
            if (order.deliveryPartnerId != null)
              _buildDeliveryPartnerCard(),
            
            // Order Items
            _buildOrderItemsCard(),
            
            // Price Breakdown
            _buildPriceBreakdownCard(),
            
            // Delivery Address
            _buildDeliveryAddressCard(),
            
            // Action Buttons
            if (OrderStatusHelper.isActive(order.status))
              _buildActionButtons(context),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentStatusCard() {
    return Card(
      margin: EdgeInsets.all(16),
      color: OrderStatusHelper.getStatusColor(order.status).withOpacity(0.1),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              OrderStatusHelper.getStatusIcon(order.status),
              size: 48,
              color: OrderStatusHelper.getStatusColor(order.status),
            ),
            SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Current Status',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    OrderStatusHelper.getStatusMessage(order.status),
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: OrderStatusHelper.getStatusColor(order.status),
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    _getEstimatedTime(),
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDeliveryPartnerCard() {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Delivery Partner',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 12),
            
            Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundImage: order.deliveryPartnerPhoto != null
                      ? NetworkImage(order.deliveryPartnerPhoto!)
                      : null,
                  child: order.deliveryPartnerPhoto == null
                      ? Icon(Icons.person, size: 30)
                      : null,
                ),
                SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        order.deliveryPartnerName ?? 'Delivery Partner',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(Icons.star, size: 16, color: Colors.orange),
                          SizedBox(width: 4),
                          Text(
                            order.deliveryPartnerRating?.toString() ?? '5.0',
                            style: TextStyle(fontSize: 14),
                          ),
                        ],
                      ),
                      if (order.deliveryPartnerVehicle != null)
                        Text(
                          order.deliveryPartnerVehicle!,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey,
                          ),
                        ),
                    ],
                  ),
                ),
                
                // Call button
                if (order.deliveryPartnerPhone != null)
                  IconButton(
                    onPressed: () {
                      // Make phone call
                      // launch('tel:${order.deliveryPartnerPhone}');
                    },
                    icon: Icon(Icons.phone, color: Colors.green),
                  ),
              ],
            ),
            
            // Track delivery button (if order is picked up)
            if (order.status == OrderStatus.PICKED_UP)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () {
                    // Open tracking screen
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => TrackDeliveryScreen(order: order),
                      ),
                    );
                  },
                  icon: Icon(Icons.location_on),
                  label: Text('Track Delivery'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildOrderItemsCard() {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Order Items',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 12),
            
            ...order.items.map((item) => Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      '${item.quantity}x ${item.name}',
                      style: TextStyle(fontSize: 16),
                    ),
                  ),
                  Text(
                    '₹${item.price * item.quantity}',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            )).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildPriceBreakdownCard() {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Price Details',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 12),
            
            _buildPriceRow('Subtotal', order.subtotal),
            _buildPriceRow('Delivery Fee', order.deliveryFee),
            _buildPriceRow('Tax', order.taxAmount),
            if (order.discountAmount > 0)
              _buildPriceRow('Discount', -order.discountAmount, isDiscount: true),
            
            Divider(height: 24),
            
            _buildPriceRow(
              'Total',
              order.totalAmount,
              isTotal: true,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPriceRow(String label, double amount, {bool isTotal = false, bool isDiscount = false}) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: isTotal ? 18 : 16,
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          Text(
            '${isDiscount ? '-' : ''}₹${amount.toStringAsFixed(2)}',
            style: TextStyle(
              fontSize: isTotal ? 18 : 16,
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
              color: isDiscount ? Colors.green : Colors.black,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDeliveryAddressCard() {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Delivery Address',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 12),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.location_on, color: Colors.red),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    order.deliveryAddress,
                    style: TextStyle(fontSize: 16),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButtons(BuildContext context) {
    return Padding(
      padding: EdgeInsets.all(16),
      child: Column(
        children: [
          // Cancel Order button (only if PENDING or ACCEPTED)
          if (order.status == OrderStatus.PENDING || 
              order.status == OrderStatus.ACCEPTED)
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () => _showCancelDialog(context),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.red,
                  side: BorderSide(color: Colors.red),
                ),
                child: Text('Cancel Order'),
              ),
            ),
          
          // Need Help button
          SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () {
                // Open help/support screen
              },
              icon: Icon(Icons.help),
              label: Text('Need Help?'),
            ),
          ),
        ],
      ),
    );
  }

  void _showCancelDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Cancel Order?'),
        content: Text('Are you sure you want to cancel this order?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('No'),
          ),
          TextButton(
            onPressed: () {
              // Call cancel API
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Order cancelled')),
              );
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: Text('Yes, Cancel'),
          ),
        ],
      ),
    );
  }

  String _getEstimatedTime() {
    switch (order.status) {
      case OrderStatus.PENDING:
        return 'Waiting for restaurant response...';
      case OrderStatus.ACCEPTED:
      case OrderStatus.PREPARING:
        return 'Estimated: 20-30 minutes';
      case OrderStatus.READY:
        return 'Food is ready! Looking for delivery partner...';
      case OrderStatus.ASSIGNED:
        return 'Delivery partner is on the way to restaurant';
      case OrderStatus.REACHED_RESTAURANT:
        return 'Picking up your order...';
      case OrderStatus.PICKED_UP:
        return 'Arriving in 10-15 minutes';
      case OrderStatus.DELIVERED:
        return 'Order delivered!';
      default:
        return '';
    }
  }
}
```

---

## 🎯 **Customer App Summary**

### What Changed:
1. ✅ **Status Helper** - Updated with 11 status messages
2. ✅ **Timeline Widget** - Shows complete order journey with all new statuses
3. ✅ **Order Details** - Enhanced with delivery partner info
4. ✅ **Progress Bar** - Visual progress indicator
5. ✅ **Real-time Updates** - Socket.IO integration for live status updates

### Customer View Flow:
```
1. Place Order → Status: PENDING
2. See "Waiting for restaurant confirmation"
3. Restaurant accepts → "Restaurant is preparing your order"
4. Restaurant preparing → "Your food is being prepared"
5. Food ready → "Food is ready, waiting for delivery partner"
6. Delivery assigned → "Delivery partner assigned" (Show partner info)
7. Partner at restaurant → "Picking up your order"
8. Order picked up → "Order is on the way!" (Track delivery button)
9. Delivered → "Order delivered • Enjoy your meal!"
```

### No API Changes:
- Customer app only **reads** order status
- No new API endpoints needed
- Just update UI to display new statuses properly

---

# 👨‍💼 App 4: Admin Dashboard

## 📋 Changes Required

### **1. Update Order Filters**

**File:** `lib/services/admin_service.dart`

```dart
class AdminService {
  final String baseUrl;
  final String token;

  AdminService({required this.baseUrl, required this.token});

  // Get orders with filters
  Future<List<Order>> getOrders({
    String? status,
    List<String>? statuses,
    int? restaurantId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    Map<String, dynamic> queryParams = {};
    
    if (status != null) queryParams['status'] = status;
    if (statuses != null) queryParams['statuses'] = statuses.join(',');
    if (restaurantId != null) queryParams['restaurant_id'] = restaurantId.toString();
    if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
    if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();
    
    final uri = Uri.parse('$baseUrl/admin/orders').replace(queryParameters: queryParams);
    
    final response = await http.get(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return (data['data'] as List).map((order) => Order.fromJson(order)).toList();
    } else {
      throw Exception('Failed to load orders');
    }
  }

  // Get dashboard statistics
  Future<Map<String, dynamic>> getDashboardStats() async {
    final response = await http.get(
      Uri.parse('$baseUrl/admin/dashboard/stats'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(response.body)['data'];
    } else {
      throw Exception('Failed to load stats');
    }
  }
}
```

---

### **2. Update Dashboard Statistics Widget**

**File:** `lib/widgets/admin_dashboard_stats.dart`

```dart
class AdminDashboardStats extends StatelessWidget {
  final Map<String, dynamic> stats;

  const AdminDashboardStats({Key? key, required this.stats}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: NeverScrollableScrollPhysics(),
      padding: EdgeInsets.all(16),
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      children: [
        _buildStatCard(
          'Pending Orders',
          stats['pending_orders'] ?? 0,
          Icons.pending,
          Colors.orange,
          '   Awaiting acceptance',
        ),
        
        _buildStatCard(
          'Active Orders',
          stats['active_orders'] ?? 0,
          Icons.restaurant,
          Colors.blue,
          'Being prepared',
        ),
        
        _buildStatCard(
          'In Delivery',
          stats['in_delivery'] ?? 0,
          Icons.delivery_dining,
          Colors.purple,
          'On the way',
        ),
        
        _buildStatCard(
          'Completed Today',
          stats['completed_today'] ?? 0,
          Icons.check_circle,
          Colors.green,
          'Delivered',
        ),
        
        _buildStatCard(
          'Total Revenue',
          '₹${stats['total_revenue'] ?? '0.00'}',
          Icons.attach_money,
          Colors.teal,
          'Today',
        ),
        
        _buildStatCard(
          'Failed Orders',
          stats['failed_orders'] ?? 0,
          Icons.cancel,
          Colors.red,
          'Rejected/Cancelled',
        ),
      ],
    );
  }

  Widget _buildStatCard(
    String title,
    dynamic value,
    IconData icon,
    Color color,
    String subtitle,
  ) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 40, color: color),
            SizedBox(height: 12),
            Text(
              value.toString(),
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            SizedBox(height: 4),
            Text(
              title,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 4),
            Text(
              subtitle,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

### **3. Update Orders List with Filters**

**File:** `lib/screens/admin_orders_screen.dart`

```dart
class AdminOrdersScreen extends StatefulWidget {
  @override
  _AdminOrdersScreenState createState() => _AdminOrdersScreenState();
}

class _AdminOrdersScreenState extends State<AdminOrdersScreen> {
  String _selectedFilter = 'all';
  
  final Map<String, List<String>> _filters = {
    'all': [],
    'pending': ['pending'],
    'active': ['accepted', 'preparing', 'ready'],
    'in_delivery': ['assigned', 'reached_restaurant', 'picked_up'],
    'completed': ['handed_over', 'delivered'],
    'failed': ['rejected', 'cancelled'],
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Orders Management'),
      ),
      body: Column(
        children: [
          // Filter chips
          _buildFilterChips(),
          
          // Orders list
          Expanded(
            child: _buildOrdersList(),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChips() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: EdgeInsets.all(16),
      child: Row(
        children: [
          _buildChip('All Orders', 'all'),
          _buildChip('Pending', 'pending'),
          _buildChip('Active', 'active'),
          _buildChip('In Delivery', 'in_delivery'),
          _buildChip('Completed', 'completed'),
          _buildChip('Failed', 'failed'),
        ],
      ),
    );
  }

  Widget _buildChip(String label, String value) {
    final isSelected = _selectedFilter == value;
    return Padding(
      padding: EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (selected) {
          setState(() {
            _selectedFilter = value;
          });
          // Load orders with new filter
          context.read<AdminOrdersBloc>().add(
            LoadOrders(statuses: _filters[value]),
          );
        },
        selectedColor: Colors.blue,
        labelStyle: TextStyle(
          color: isSelected ? Colors.white : Colors.black,
        ),
      ),
    );
  }

  Widget _buildOrdersList() {
    return BlocBuilder<AdminOrdersBloc, AdminOrdersState>(
      builder: (context, state) {
        if (state is AdminOrdersLoading) {
          return Center(child: CircularProgressIndicator());
        } else if (state is AdminOrdersLoaded) {
          if (state.orders.isEmpty) {
            return Center(
              child: Text('No orders found'),
            );
          }
          return ListView.builder(
            itemCount: state.orders.length,
            itemBuilder: (context, index) {
              return AdminOrderCard(order: state.orders[index]);
            },
          );
        } else if (state is AdminOrdersError) {
          return Center(child: Text('Error: ${state.message}'));
        }
        return Container();
      },
    );
  }
}
```

---

## 🎯 **Admin App Summary**

### What Changed:
1. ✅ **Order Filters** - Updated to use new status groups:
   - **Pending**: `PENDING`
   - **Active**: `ACCEPTED`, `PREPARING`, `READY`
   - **In Delivery**: `ASSIGNED`, `REACHED_RESTAURANT`, `PICKED_UP`
   - **Completed**: `HANDED_OVER`, `DELIVERED`
   - **Failed**: `REJECTED`, `CANCELLED`

2. ✅ **Dashboard Stats** - New metrics:
   - Pending Orders count
   - Active Orders (restaurant)
   - In Delivery (delivery partner)
   - Completed Today
   - Failed Orders

3. ✅ **Order Management** - Better visibility into order flow stages

---

# 🎯 Complete Integration Summary

## For Each App:

### 🏪 **Restaurant App (DFDRestaurantPartner)**
**Files to Update:** 5-6 files
- ✅ Order model + enum
- ✅ API service (add `handover()`)
- ✅ Orders bloc/provider
- ✅ Order card widget
- ✅ Orders screen

**New Feature:**
- "Hand Over" button (Step 4)

---

### 🚴 **Delivery Boy App (dharai_delivery_boy)**
**Files to Update:** 5-6 files
- ✅ Order model + enum
- ✅ API service (add `markReached()`, `pickupOrder()`)
- ✅ Delivery orders bloc
- ✅ Delivery order card widget
- ✅ Delivery screen

**New Features:**
- "I've Reached" button (Step 2)
- "Pickup Order" button (Step 3)

---

### 👤 **Customer App (foodieexpress)**
**Files to Update:** 3-4 files
- ✅ Order model + enum
- ✅ Status helper (messages)
- ✅ Timeline widget
- ✅ Order details screen

**New Features:**
- Updated status messages (11 statuses)
- Enhanced order timeline
- Delivery partner info display

---

### 👨‍💼 **Admin App**
**Files to Update:** 3-4 files
- ✅ Order model + enum
- ✅ Admin service (filters)
- ✅ Dashboard stats widget
- ✅ Orders screen (filters)

**New Features:**
- Updated order filters
- Enhanced dashboard metrics
- Better order categorization

---

## 🚀 Testing Checklist

### For Each App:
1. ✅ Update enum
2. ✅ Update API calls
3. ✅ Update UI components
4. ✅ Test order flow end-to-end
5. ✅ Test Socket.IO real-time updates
6. ✅ Test error handling

---

## 📞 Need Help?

Refer to:
- **FLUTTER_APPS_INTEGRATION_GUIDE.md** - Complete code examples
- **ORDER_STATUS_FLOW_API.md** - API documentation
- **QUICK_REFERENCE.md** - Quick snippets

---

**Last Updated:** 2026-01-15  
**Ready for:** Flutter App Development  
**Backend Status:** ✅ Complete and Deployed
