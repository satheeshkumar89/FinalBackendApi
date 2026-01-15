# 📊 Order Status Flow - Visual Guide

## 🔄 Complete Order Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORDER CREATED                            │
│                    Status: PENDING 📝                           │
│                  Waiting for restaurant                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼ Restaurant Accepts          ▼ Restaurant Rejects
┌───────────────────┐         ┌──────────────────┐
│  ACCEPTED ✅     │         │   REJECTED ❌    │
│  Restaurant       │         │   TERMINAL       │
│  Step 1           │         └──────────────────┘
└────────┬──────────┘
         │
         ▼ Start Preparing
┌───────────────────┐
│  PREPARING 👨‍🍳   │
│  Restaurant       │
│  Step 2           │
└────────┬──────────┘
         │
         ▼ Food Ready
┌───────────────────┐
│  READY 🍽️        │
│  Restaurant       │
│  Step 3           │
└────────┬──────────┘
         │
         ├─────────────────────────────┐
         │                             │
         ▼ Delivery Partner Accepts    ▼ Restaurant Hands Over (Optional)
┌───────────────────┐         ┌──────────────────┐
│  ASSIGNED 🚴     │         │  HANDED_OVER ✋  │
│  Delivery         │         │  TERMINAL        │
│  Step 1           │         │  (Restaurant)    │
└────────┬──────────┘         └──────────────────┘
         │
         ▼ Partner at Restaurant
┌───────────────────┐
│  REACHED_         │
│  RESTAURANT 📍   │
│  Delivery         │
│  Step 2           │
└────────┬──────────┘
         │
         ▼ Pickup Order
┌───────────────────┐
│  PICKED_UP 📦    │
│  Delivery         │
│  Step 3           │
└────────┬──────────┘
         │
         ▼ Deliver to Customer
┌───────────────────┐
│  DELIVERED 🎉    │
│  TERMINAL         │
│  Delivery         │
│  Step 4           │
└───────────────────┘
```

---

## 🏪 Restaurant Partner View

### My Orders - Current State

```
┌─────────────────────────────────────────┐
│  📱 NEW ORDERS TAB                      │
├─────────────────────────────────────────┤
│  Status: PENDING                        │
│                                         │
│  🔔 Order #1234                         │
│  📦 3 items • ₹450                      │
│  🕐 2 mins ago                          │
│  [Accept] [Reject]                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🔥 ONGOING ORDERS TAB                  │
├─────────────────────────────────────────┤
│  Status: ACCEPTED, PREPARING, READY     │
│                                         │
│  ✅ Order #1233 - ACCEPTED              │
│  [Start Preparing]                      │
│                                         │
│  👨‍🍳 Order #1232 - PREPARING            │
│  ⏱️ Est. 12 mins                        │
│  [Mark Ready]                           │
│                                         │
│  🍽️ Order #1231 - READY                │
│  [Hand Over to Delivery]                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  ✅ COMPLETED ORDERS TAB                │
├─────────────────────────────────────────┤
│  Status: HANDED_OVER, DELIVERED,        │
│          REJECTED, CANCELLED            │
│                                         │
│  ✋ Order #1230 - HANDED_OVER           │
│  🎉 Order #1229 - DELIVERED             │
│  ❌ Order #1228 - REJECTED              │
└─────────────────────────────────────────┘
```

### Restaurant Workflow Buttons

```
Step 1: [Accept Order] 
        PENDING → ACCEPTED
        
Step 2: [Start Preparing]
        ACCEPTED → PREPARING
        
Step 3: [Mark Ready]
        PREPARING → READY
        
Step 4: [Hand Over to Delivery]
        READY → HANDED_OVER ✅ DONE
```

---

## 🚴 Delivery Boy View

### My Orders - Current State

```
┌─────────────────────────────────────────┐
│  🎯 AVAILABLE ORDERS TAB                │
├─────────────────────────────────────────┤
│  Status: READY                          │
│  (Within 5km of me)                     │
│                                         │
│  🍽️ Order #1234                         │
│  🏪 Pizza Palace (2.3 km)               │
│  💰 ₹450 • Delivery: ₹30                │
│  [Accept Delivery]                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🔥 ACTIVE ORDERS TAB                   │
├─────────────────────────────────────────┤
│  Status: ASSIGNED, REACHED_RESTAURANT,  │
│          PICKED_UP                      │
│                                         │
│  🚴 Order #1233 - ASSIGNED              │
│  📍 Navigate to restaurant (2.3 km)     │
│  [I've Reached Restaurant]              │
│                                         │
│  📍 Order #1232 - REACHED_RESTAURANT    │
│  ⏱️ Waiting for order...                │
│  [Pickup Order]                         │
│                                         │
│  📦 Order #1231 - PICKED_UP             │
│  📍 Navigate to customer (3.1 km)       │
│  [Mark as Delivered]                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  ✅ COMPLETED ORDERS TAB                │
├─────────────────────────────────────────┤
│  Status: DELIVERED                      │
│                                         │
│  🎉 Order #1230 - Delivered             │
│  💰 Earned: ₹30                         │
│  🕐 30 mins ago                         │
└─────────────────────────────────────────┘
```

### Delivery Partner Workflow Buttons

```
Step 1: [Accept Delivery]
        READY → ASSIGNED
        
Step 2: [I've Reached Restaurant]
        ASSIGNED → REACHED_RESTAURANT
        
Step 3: [Pickup Order]
        REACHED_RESTAURANT → PICKED_UP
        
Step 4: [Mark as Delivered]
        PICKED_UP → DELIVERED ✅ DONE
```

---

## 👤 Customer View

### Order Tracking Timeline

```
┌─────────────────────────────────────────┐
│  📦 Order #1234                         │
│  🕐 Placed 15 mins ago                  │
├─────────────────────────────────────────┤
│                                         │
│  ✅ Order Placed                        │
│     2026-01-15 10:30 AM                 │
│     Status: PENDING                     │
│                                         │
│  ✅ Restaurant Accepted                 │
│     2026-01-15 10:32 AM                 │
│     Status: ACCEPTED                    │
│                                         │
│  🔄 Preparing Your Food                 │
│     2026-01-15 10:35 AM                 │
│     Status: PREPARING                   │
│     ⏱️ Estimated: 15 mins               │
│                                         │
│  ⏳ Food Ready for Pickup               │
│     Status: READY                       │
│     Waiting for delivery partner...     │
│                                         │
│  ⏳ Delivery Partner Assigned           │
│     Status: ASSIGNED                    │
│     👤 Rajesh Kumar                     │
│     🚴 On the way to restaurant         │
│                                         │
│  ⏳ Picking Up Your Order               │
│     Status: REACHED_RESTAURANT          │
│     Partner at restaurant               │
│                                         │
│  ⏳ On the Way!                         │
│     Status: PICKED_UP                   │
│     📍 Track delivery partner           │
│     🕐 ETA: 12 mins                     │
│                                         │
│  ⏳ Delivered                           │
│     Status: DELIVERED                   │
│     🎉 Enjoy your meal!                 │
│                                         │
└─────────────────────────────────────────┘
```

### Customer Status Messages

| Status | Message | Icon |
|--------|---------|------|
| PENDING | "Waiting for restaurant confirmation" | ⏳ |
| ACCEPTED | "Restaurant is preparing your order" | ✅ |
| PREPARING | "Your food is being prepared" | 👨‍🍳 |
| READY | "Food is ready, waiting for delivery partner" | 🍽️ |
| ASSIGNED | "Delivery partner assigned" | 🚴 |
| REACHED_RESTAURANT | "Delivery partner is picking up your order" | 📍 |
| PICKED_UP | "Order is on the way!" | 📦 |
| DELIVERED | "Order delivered • Enjoy your meal!" | 🎉 |
| HANDED_OVER | "Order handed over to delivery partner" | ✋ |
| REJECTED | "Order rejected by restaurant" | ❌ |
| CANCELLED | "Order cancelled" | ❌ |

---

## 📊 Admin Dashboard View

### Order Status Distribution

```
┌─────────────────────────────────────────┐
│  📊 REAL-TIME ORDERS                    │
├─────────────────────────────────────────┤
│                                         │
│  📝 Pending Orders: 5                   │
│     (Awaiting restaurant acceptance)    │
│                                         │
│  🔥 Active Orders: 12                   │
│     - Accepted: 3                       │
│     - Preparing: 5                      │
│     - Ready: 4                          │
│                                         │
│  🚴 In Delivery: 8                      │
│     - Assigned: 2                       │
│     - At Restaurant: 3                  │
│     - En Route: 3                       │
│                                         │
│  ✅ Completed Today: 45                 │
│     - Delivered: 42                     │
│     - Handed Over: 3                    │
│                                         │
│  ❌ Failed Today: 3                     │
│     - Rejected: 2                       │
│     - Cancelled: 1                      │
│                                         │
│  💰 Today's Revenue: ₹15,450            │
│  📈 Average Order Value: ₹367           │
│                                         │
└─────────────────────────────────────────┘
```

### Order Flow Analytics

```
┌─────────────────────────────────────────┐
│  ⏱️ AVERAGE TIME PER STATUS             │
├─────────────────────────────────────────┤
│                                         │
│  PENDING → ACCEPTED                     │
│  ████░░░░░ 2.5 mins                     │
│                                         │
│  ACCEPTED → PREPARING                   │
│  ██░░░░░░░ 1.2 mins                     │
│                                         │
│  PREPARING → READY                      │
│  ████████░ 15.3 mins                    │
│                                         │
│  READY → ASSIGNED                       │
│  ████░░░░░ 3.8 mins                     │
│                                         │
│  ASSIGNED → REACHED_RESTAURANT          │
│  ██████░░░ 8.2 mins                     │
│                                         │
│  REACHED_RESTAURANT → PICKED_UP         │
│  ███░░░░░░ 2.1 mins                     │
│                                         │
│  PICKED_UP → DELIVERED                  │
│  ███████░░ 12.7 mins                    │
│                                         │
│  🎯 Total Average: 45.8 mins            │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔔 Notification Flow

### Who Gets Notified When?

```
STATUS CHANGE          → NOTIFIED PARTIES
────────────────────────────────────────────
PENDING (Created)      → Restaurant 🏪

ACCEPTED              → Customer 👤
                      → Available Delivery Partners 🚴

PREPARING             → Customer 👤

READY                 → Customer 👤
                      → Nearby Delivery Partners 🚴

ASSIGNED              → Restaurant 🏪
                      → Customer 👤

REACHED_RESTAURANT    → Restaurant 🏪
                      → Customer 👤

PICKED_UP             → Restaurant 🏪
                      → Customer 👤

DELIVERED             → Restaurant 🏪
                      → Customer 👤
                      → Delivery Partner 🚴

HANDED_OVER           → Customer 👤
                      → Delivery Partner 🚴

REJECTED              → Customer 👤

CANCELLED             → Restaurant 🏪
                      → Delivery Partner 🚴
```

---

## 📱 Real-Time Updates (Socket.IO)

### Event Flow

```
Restaurant App ←─────→ Backend Server ←─────→ Delivery App
       ↑                    ↕                      ↑
       │              Customer App                 │
       │                    ↑                      │
       └────────────────────┴──────────────────────┘
              All apps receive real-time updates
```

### Room Structure

```
Rooms:
  ├─ restaurant_{id}           → Restaurant-specific events
  ├─ delivery_partner_{id}     → Delivery partner-specific events
  ├─ customer_{id}             → Customer-specific events
  └─ available_delivery_partners → Broadcast to all online partners
```

---

## ✅ Status Validation Rules

### Valid Transitions Matrix

```
FROM Status          → TO Status              ✅/❌
─────────────────────────────────────────────────────
PENDING              → ACCEPTED               ✅
PENDING              → REJECTED               ✅
ACCEPTED             → PREPARING              ✅
ACCEPTED             → CANCELLED              ✅
PREPARING            → READY                  ✅
PREPARING            → CANCELLED              ✅
READY                → ASSIGNED               ✅
READY                → HANDED_OVER            ✅
READY                → CANCELLED              ✅
ASSIGNED             → REACHED_RESTAURANT     ✅
REACHED_RESTAURANT   → PICKED_UP              ✅
PICKED_UP            → DELIVERED              ✅

# Invalid transitions:
PREPARING            → ACCEPTED               ❌
PICKED_UP            → READY                  ❌
DELIVERED            → (any)                  ❌
REJECTED             → (any)                  ❌
```

---

**Last Updated:** 2026-01-15  
**Version:** 2.0  
**For:** FastFoodie Multi-App Order Management
