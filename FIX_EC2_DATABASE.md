# 🔧 Fix EC2 Database - Add Missing Email Column

## Problem
```
Error: Unknown column 'delivery_partners.email' in 'SELECT'
```

The code expects an `email` column in the `delivery_partners` table, but it doesn't exist in the EC2 database.

## Solution: Add the Missing Column

---

### Method 1: Using AWS Console (Easiest)

**Step 1: Connect to EC2**
1. Go to AWS EC2 Console
2. Select your instance (52.22.224.42)
3. Click **Connect** → **EC2 Instance Connect** → **Connect**

**Step 2: Access MySQL Container**
```bash
# Enter the MySQL container
sudo docker exec -it fastfoodie_mysql mysql -u root -prootpassword fastfoodie
```

**Step 3: Run the Migration**
```sql
-- Add email column
ALTER TABLE delivery_partners 
ADD COLUMN email VARCHAR(255) NULL
AFTER full_name;

-- Verify it was added
DESCRIBE delivery_partners;

-- Exit MySQL
EXIT;
```

**Step 4: Restart API Container**
```bash
sudo docker-compose restart api
```

**Step 5: Test the API**
```bash
# Test delivery partner OTP endpoint
curl -X POST "https://dharaifooddelivery.in/delivery-partner/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "8668109712"}'
```

---

### Method 2: Using SQL File (Alternative)

**Step 1: Upload SQL file to EC2**

From your Mac terminal:
```bash
# Upload the migration file
scp -i "/Users/satheeshkumar/Downloads/dharaifood.pem" \
  fix_delivery_partner_email.sql \
  ec2-user@52.22.224.42:~/fastfoodie-backend/
```

**Step 2: Connect to EC2 and Run Migration**
```bash
# Connect to EC2
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42

# Go to project directory
cd fastfoodie-backend

# Run the migration
sudo docker exec -i fastfoodie_mysql mysql -u root -prootpassword fastfoodie < fix_delivery_partner_email.sql

# Restart API
sudo docker-compose restart api

# Check logs
sudo docker logs fastfoodie_api --tail 50
```

---

### Method 3: One-Line Fix (From Mac Terminal)

If SSH works, run this single command:

```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 \
  "sudo docker exec -i fastfoodie_mysql mysql -u root -prootpassword fastfoodie \
  -e \"ALTER TABLE delivery_partners ADD COLUMN email VARCHAR(255) NULL AFTER full_name;\" \
  && sudo docker-compose -f ~/fastfoodie-backend/docker-compose.yml restart api \
  && echo 'Migration completed!'"
```

---

## Verification

### 1. Check Table Structure
```bash
sudo docker exec -it fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "DESCRIBE delivery_partners;"
```

You should see:
```
+---------------------+--------------+------+-----+
| Field               | Type         | Null | Key |
+---------------------+--------------+------+-----+
| id                  | int          | NO   | PRI |
| full_name           | varchar(255) | NO   |     |
| email               | varchar(255) | YES  |     |  <--- THIS IS NEW
| phone_number        | varchar(15)  | NO   | UNI |
| ...                 | ...          | ...  | ... |
+---------------------+--------------+------+-----+
```

### 2. Test API Endpoint
```bash
curl -X POST "https://dharaifooddelivery.in/delivery-partner/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "8668109712"}'
```

**Expected Success Response:**
```json
{
  "message": "OTP sent successfully",
  "phone_number": "8668109712"
}
```

### 3. Check API Logs
```bash
sudo docker logs fastfoodie_api --tail 100 | grep -i error
```

Should show no database errors.

---

## Why This Happened

The `delivery_partners` table on EC2 was created with an older schema. When you deployed the new code with the Admin Approval System, it added the `email` field to the model, but the database table wasn't automatically updated.

**What we fixed:**
- ✅ Added `email VARCHAR(255)` column
- ✅ Made it nullable (NULL) so existing records aren't affected
- ✅ Positioned it after `full_name` for consistency

---

## Complete Delivery Partner Table Schema

After running the migration, your `delivery_partners` table should have:

```sql
CREATE TABLE delivery_partners (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NULL,                          -- NEWLY ADDED
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    vehicle_number VARCHAR(20) NULL,
    vehicle_type VARCHAR(50) NULL,
    license_number VARCHAR(50) NULL,
    rating DECIMAL(3, 2) DEFAULT 5.0,
    profile_photo VARCHAR(500) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_online BOOLEAN DEFAULT FALSE,
    is_registered BOOLEAN DEFAULT FALSE,
    verification_status ENUM(...) DEFAULT 'pending',
    verification_notes TEXT NULL,
    last_online_at DATETIME NULL,
    last_offline_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);
```

---

## Troubleshooting

### Error: "Can't connect to database"
```bash
# Check if MySQL container is running
sudo docker ps | grep mysql

# If not running, start it
sudo docker-compose up -d mysql
```

### Error: "Access denied"
```bash
# Verify database credentials in docker-compose.yml
cat docker-compose.yml | grep -A 5 MYSQL
```

### Migration Already Applied?
```bash
# Check if email column exists
sudo docker exec -it fastfoodie_mysql mysql -u root -prootpassword fastfoodie \
  -e "SHOW COLUMNS FROM delivery_partners LIKE 'email';"

# If it returns a row, the column already exists (no action needed)
```

---

## Next Steps After Fix

1. ✅ Test delivery partner registration API
2. ✅ Test OTP sending for delivery partners
3. ✅ Test admin approval workflow
4. ✅ Test location tracking endpoints

---

## Need Help?

If you encounter any issues:
1. Check Docker containers: `sudo docker ps`
2. View MySQL logs: `sudo docker logs fastfoodie_mysql`
3. View API logs: `sudo docker logs fastfoodie_api`
4. Check database connection: `sudo docker exec fastfoodie_mysql mysqladmin -u root -prootpassword ping`
