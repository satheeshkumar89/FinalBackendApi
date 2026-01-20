# Order Timestamps - Indian Standard Time (IST)

All order-related timestamps are now stored and displayed in **Indian Standard Time (IST)** - Asia/Kolkata timezone (UTC+5:30).

## Complete Order Timeline with IST Timestamps

### 1. Order Creation
- **Field**: `created_at`
- **When**: Customer places the order
- **Status**: `pending`
- **IST Format**: `20-01-2026 11:30 PM`

### 2. Restaurant Accepts Order
- **Field**: `accepted_at`
- **When**: Restaurant clicks "Accept Order"
- **Status**: `accepted`
- **IST Format**: `20-01-2026 11:32 PM`

### 3. Restaurant Starts Preparing
- **Field**: `preparing_at`
- **When**: Restaurant clicks "Start Preparing"
- **Status**: `preparing`
- **IST Format**: `20-01-2026 11:33 PM`

### 4. Food is Ready
- **Field**: `ready_at`
- **When**: Restaurant clicks "Food Ready"
- **Status**: `ready`
- **IST Format**: `20-01-2026 11:48 PM`

### 5. Restaurant Hands Over to Delivery Partner
- **Field**: `handed_over_at`
- **When**: Restaurant clicks "Hand Over"
- **Status**: `handed_over`
- **IST Format**: `20-01-2026 11:50 PM`

### 6. Delivery Partner Accepts Order
- **Field**: `assigned_at`
- **When**: Delivery partner clicks "Accept"
- **Status**: `assigned`
- **IST Format**: `20-01-2026 11:51 PM`

### 7. Delivery Partner Reaches Restaurant
- **Field**: `reached_restaurant_at`
- **When**: Delivery partner clicks "Reached Restaurant"
- **Status**: `reached_restaurant`
- **IST Format**: `20-01-2026 11:55 PM`

### 8. Delivery Partner Picks Up Order
- **Field**: `pickedup_at`
- **When**: Delivery partner clicks "Pick Up"
- **Status**: `picked_up`
- **IST Format**: `20-01-2026 11:56 PM`

### 9. Order Delivered to Customer
- **Field**: `delivered_at`
- **When**: Delivery partner clicks "Complete Delivery"
- **Status**: `delivered`
- **IST Format**: `21-01-2026 12:10 AM`

### 10. Order Completed
- **Field**: `completed_at`
- **When**: Same as delivered_at
- **Status**: `delivered`
- **IST Format**: `21-01-2026 12:10 AM`

---

## Additional Timestamps

### Order Rejection
- **Field**: `rejected_at`
- **When**: Restaurant rejects the order
- **Status**: `rejected`

### Delivery Partner Activity
- **Field**: `last_online_at`
- **When**: Delivery partner goes online
- **IST Format**: `20-01-2026 10:00 AM`

- **Field**: `last_offline_at`
- **When**: Delivery partner goes offline
- **IST Format**: `20-01-2026 08:00 PM`

---

## How Timestamps are Displayed in Apps

### Customer App
All timestamps shown in 12-hour format with AM/PM:
- "Order placed at: 11:30 PM"
- "Estimated delivery: 12:10 AM"

### Restaurant App
All timestamps shown in 12-hour format:
- "Order received: 11:30 PM"
- "Accepted at: 11:32 PM"

### Delivery Partner App
All timestamps shown in 12-hour format:
- "Assigned at: 11:51 PM"
- "Picked up at: 11:56 PM"

---

## Technical Implementation

### Backend Changes
1. Created `app/utils/timezone.py` with IST timezone utilities
2. Replaced all `datetime.utcnow()` calls with `get_ist_now()`
3. All timestamps now automatically use IST (UTC+5:30)

### Database Storage
- Timestamps are stored in IST timezone
- MySQL DATETIME fields store the IST time directly
- No conversion needed when reading from database

### API Response
All datetime fields in API responses are in IST:
```json
{
  "created_at": "2026-01-20T23:30:00+05:30",
  "accepted_at": "2026-01-20T23:32:00+05:30",
  "delivered_at": "2026-01-21T00:10:00+05:30"
}
```

---

## Time Calculations

### Today's Orders
- Start: Today 12:00 AM IST
- End: Today 11:59 PM IST

### Delivery Time Estimation
- Preparation time: 15-30 minutes
- Delivery time: 20-40 minutes
- All calculations done in IST

### Earnings Calculation
- Today: 12:00 AM to 11:59 PM IST
- This Week: Monday 12:00 AM to Sunday 11:59 PM IST
- This Month: 1st 12:00 AM to Last day 11:59 PM IST

---

## Testing Timezone

To verify IST is working correctly:

1. **Create a test order**
2. **Check the timestamps in database**:
   ```sql
   SELECT 
     order_number,
     created_at,
     accepted_at,
     delivered_at
   FROM orders 
   WHERE id = <order_id>;
   ```
3. **Verify the time matches IST** (not UTC)
4. **Check API response** - should show `+05:30` timezone offset

---

## Common IST Time Formats

### Display Format
- **Full**: `20-01-2026 11:30 PM`
- **Date Only**: `20-01-2026`
- **Time Only**: `11:30 PM`
- **ISO Format**: `2026-01-20T23:30:00+05:30`

### Database Format
- MySQL DATETIME: `2026-01-20 23:30:00`
- Stored directly in IST timezone
