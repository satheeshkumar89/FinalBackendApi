# 📋 Order Status Flow Update Plan

## 🎯 Objective
Update the order status flow for all 4 apps (Restaurant, Delivery Boy, Customer, Admin) to match the new clean workflow.

## 📊 New Status Flow

### Final Clean Table:

| Step | Hotel (Restaurant) | Delivery Boy |
|------|-------------------|--------------|
| 1 | Order Received → Accept | Order Received → Accept |
| 2 | Preparing (Time Update) | Hotel Reached |
| 3 | Order Ready | Pickup Order |
| 4 | Order Handed Over (Done) | Order Delivered (Done) |

## 🔄 Status Mapping

### New Order Status Enum:
```python
class OrderStatusEnum(str, enum.Enum):
    # Initial Status
    PENDING = "pending"                    # Order created, waiting for restaurant
    
    # Restaurant Statuses
    ACCEPTED = "accepted"                  # Restaurant accepted order
    PREPARING = "preparing"                # Restaurant is preparing food
    READY = "ready"                        # Food is ready for pickup
    HANDED_OVER = "handed_over"            # Restaurant handed over to delivery partner
    
    # Delivery Partner Statuses  
    ASSIGNED = "assigned"                  # Delivery partner assigned/accepted
    REACHED_RESTAURANT = "reached_restaurant"  # Delivery partner at restaurant
    PICKED_UP = "picked_up"                # Order picked up from restaurant
    DELIVERED = "delivered"                # Order delivered to customer
    
    # Terminal Statuses
    REJECTED = "rejected"                  # Restaurant rejected order
    CANCELLED = "cancelled"                # Order cancelled
```

## 📱 App-Specific Views

### 1. Restaurant App
**Endpoints:**
- `GET /orders/new` - Orders with status: `PENDING`
- `PUT /orders/accept/{id}` - Accept order → Status: `ACCEPTED`
- `PUT /orders/preparing/{id}` - Start preparing → Status: `PREPARING`
- `PUT /orders/ready/{id}` - Food ready → Status: `READY`
- `PUT /orders/handover/{id}` - Hand over to delivery → Status: `HANDED_OVER`
- `PUT /orders/reject/{id}` - Reject order → Status: `REJECTED`

**Order List Views:**
- **New Orders**: `PENDING`
- **Ongoing Orders**: `ACCEPTED`, `PREPARING`, `READY`
- **Completed Orders**: `HANDED_OVER`, `REJECTED`, `CANCELLED`

### 2. Delivery Boy App
**Endpoints:**
- `GET /delivery-partner/orders/available` - Orders with status: `READY` (within 5km)
- `PUT /delivery-partner/orders/accept/{id}` - Accept delivery → Status: `ASSIGNED`
- `PUT /delivery-partner/orders/reached/{id}` - Reached restaurant → Status: `REACHED_RESTAURANT`
- `PUT /delivery-partner/orders/pickup/{id}` - Pickup order → Status: `PICKED_UP`
- `PUT /delivery-partner/orders/deliver/{id}` - Deliver order → Status: `DELIVERED`

**Order List Views:**
- **Available Orders**: `READY` (within proximity)
- **Active Orders**: `ASSIGNED`, `REACHED_RESTAURANT`, `PICKED_UP`
- **Completed Orders**: `DELIVERED`

### 3. Customer App
**Endpoints:**
- `GET /customer/orders` - All customer orders
- `GET /customer/orders/{id}` - Order details with tracking

**Order Status Display:**
- `PENDING` → "Waiting for restaurant confirmation"
- `ACCEPTED` → "Restaurant is preparing your order"
- `PREPARING` → "Your food is being prepared"
- `READY` → "Food is ready, waiting for delivery partner"
- `ASSIGNED` → "Delivery partner assigned"
- `REACHED_RESTAURANT` → "Delivery partner is picking up your order"
- `PICKED_UP` → "Order is on the way"
- `DELIVERED` → "Order delivered"
- `REJECTED` → "Order rejected by restaurant"
- `CANCELLED` → "Order cancelled"

### 4. Admin App
**Endpoints:**
- `GET /admin/orders` - All orders with filters
- `GET /admin/orders/stats` - Order statistics

**Stats by Status:**
- Pending orders
- Active orders (all in-progress statuses)
- Completed orders
- Revenue by status

## 🗄️ Database Changes

### Order Model Updates:
```python
# Add new timestamp fields
reached_restaurant_at = Column(DateTime(timezone=True), nullable=True)
handed_over_at = Column(DateTime(timezone=True), nullable=True)
assigned_at = Column(DateTime(timezone=True), nullable=True)

# Update existing fields (rename if needed)
# pickedup_at stays the same
# delivered_at stays the same
```

## 🔔 Notification Updates

### Restaurant Notifications:
- `new_order` → When order is `PENDING`
- `order_accepted` → When delivery partner accepts (`ASSIGNED`)
- `delivery_partner_reached` → When status is `REACHED_RESTAURANT`
- `order_picked_up` → When status is `PICKED_UP`

### Delivery Partner Notifications:
- `order_ready` → When restaurant marks `READY`
- `order_assigned` → When they accept order
- `pickup_reminder` → If taking too long at `ASSIGNED`

### Customer Notifications:
- `order_accepted` → Restaurant accepted
- `preparing` → Food being prepared  
- `ready` → Food ready
- `delivery_assigned` → Delivery partner assigned
- `on_the_way` → Order picked up
- `delivered` → Order delivered

## 🚀 Implementation Steps

### Phase 1: Backend Updates
1. ✅ Update `OrderStatusEnum` in `models.py`
2. ✅ Add new timestamp columns to Order model
3. ✅ Create database migration script
4. ✅ Update restaurant order endpoints
5. ✅ Update delivery partner order endpoints
6. ✅ Update customer order endpoints
7. ✅ Update admin order endpoints

### Phase 2: Notification Updates
1. ✅ Update notification service for new statuses
2. ✅ Update Socket.IO events
3. ✅ Update FCM notification logic

### Phase 3: Testing
1. ✅ Test restaurant flow
2. ✅ Test delivery partner flow
3. ✅ Test customer app display
4. ✅ Test admin dashboard
5. ✅ Test real-time notifications

### Phase 4: Deployment
1. ✅ Run database migration on production
2. ✅ Deploy backend updates
3. ✅ Update API documentation
4. ✅ Notify frontend teams of changes

## 📝 API Documentation Updates

Create comprehensive API docs for:
- Restaurant partner endpoints
- Delivery partner endpoints  
- Customer endpoints
- Admin endpoints

Include:
- Status transition rules
- Required fields for each status
- Error handling
- Real-time event names

## ✅ Success Criteria

1. Clear separation between restaurant and delivery partner workflows
2. Each status has a specific meaning and action
3. Real-time updates work seamlessly
4. All 4 apps can track order progress accurately
5. Proper error handling for invalid status transitions
6. Complete audit trail with timestamps

---

**Next Step:** Implement backend changes starting with the model updates.
