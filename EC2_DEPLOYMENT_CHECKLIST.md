# 🚀 EC2 Deployment Checklist

## Current Issue
The `/orders/ongoing` and `/orders/completed` endpoints are still returning 500 errors after deployment.

## Root Cause
The latest code (with the MySQL enum fix) hasn't been pulled or the Docker container wasn't rebuilt.

---

## ✅ STEP-BY-STEP DEPLOYMENT (Run on EC2)

### Step 1: Verify Current State
```bash
cd ~/fastfoodie-backend
git status
git log --oneline -5
```

**Expected output should show:**
- Commit `fc64fe0` - Add diagnostic and testing scripts
- Commit `8313a3e` - **Fix: MySQL compatibility issue with enum values** ← This is the critical fix!

### Step 2: Pull Latest Code
```bash
cd ~/fastfoodie-backend
git pull origin main
```

**Expected output:**
```
Already up to date.
```
OR
```
Updating XXX..fc64fe0
```

### Step 3: Verify the Fix is in the Code
```bash
grep -A3 "OrderStatusEnum.ACCEPTED.value" ~/fastfoodie-backend/app/routers/orders.py
```

**Expected output should show:**
```python
OrderStatusEnum.ACCEPTED.value,
OrderStatusEnum.PREPARING.value,
OrderStatusEnum.READY.value
```

If you see this ✅, the code fix is present.  
If you see `OrderStatusEnum.ACCEPTED` (without `.value`) ❌, the code wasn't updated.

### Step 4: Rebuild Docker Containers
```bash
cd ~/fastfoodie-backend
sudo docker-compose down
sudo docker-compose up --build -d
```

**Wait for build to complete** (may take 1-2 minutes)

### Step 5: Verify Containers are Running
```bash
sudo docker-compose ps
```

**Expected output:**
```
NAME                COMMAND                  SERVICE             STATUS
fastfoodie_api      "uvicorn app.main:ap…"   api                 Up
fastfoodie_mysql    "docker-entrypoint.s…"   mysql               Up
```

### Step 6: Check Logs for Errors
```bash
sudo docker logs fastfoodie_api --tail 100
```

**Look for:**
- ✅ `INFO: Application startup complete.`
- ✅ `INFO: Uvicorn running on http://0.0.0.0:8000`
- ❌ Any `ERROR` or `Exception` messages

### Step 7: Test the Endpoints Directly on EC2
```bash
# Test from EC2 localhost
curl -X GET 'http://localhost:8000/orders/ongoing' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6MiwicGhvbmVfbnVtYmVyIjoiKzkxOTc4Nzc5MjAzMSIsImV4cCI6MTc2ODgwOTM2Mn0.wXtnKzRDJHel_0f6cb4J-zWjI-rGXRa-2bopHodl7zE' \
  -H 'accept: application/json'
```

**Expected result:**
```json
{"success":true,"message":"Ongoing orders retrieved successfully","data":{"orders":[]}}
```

**NOT:**
```
Internal Server Error
```

---

## 🔍 If Still Getting 500 Error After All Steps:

### Check Database Connection
```bash
sudo docker exec -it fastfoodie_mysql mysql -u root -p
# Password: rootpassword (from docker-compose.yml)
```

Then run:
```sql
USE fastfoodie;
SHOW COLUMNS FROM orders LIKE 'status';
SELECT DISTINCT status FROM orders;
EXIT;
```

This will show what status values exist in the database.

### Check Application Logs in Real-Time
```bash
sudo docker logs -f fastfoodie_api
```

Then test the endpoint again and watch for errors.

---

## 📊 Quick Status Check

After deployment, run this one-liner to check all endpoints:

```bash
echo "=== Testing /orders/new ===" && \
curl -s -X GET 'http://localhost:8000/orders/new' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6MiwicGhvbmVfbnVtYmVyIjoiKzkxOTc4Nzc5MjAzMSIsImV4cCI6MTc2ODgwOTM2Mn0.wXtnKzRDJHel_0f6cb4J-zWjI-rGXRa-2bopHodl7zE' \
  -H 'accept: application/json' | jq . && \
echo "" && echo "=== Testing /orders/ongoing ===" && \
curl -s -X GET 'http://localhost:8000/orders/ongoing' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6MiwicGhvbmVfbnVtYmVyIjoiKzkxOTc4Nzc5MjAzMSIsImV4cCI6MTc2ODgwOTM2Mn0.wXtnKzRDJHel_0f6cb4J-zWjI-rGXRa-2bopHodl7zE' \
  -H 'accept: application/json' | jq . && \
echo "" && echo "=== Testing /orders/completed ===" && \
curl -s -X GET 'http://localhost:8000/orders/completed' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6MiwicGhvbmVfbnVtYmVyIjoiKzkxOTc4Nzc5MjAzMSIsImV4cCI6MTc2ODgwOTM2Mn0.wXtnKzRDJHel_0f6cb4J-zWjI-rGXRa-2bopHodl7zE' \
  -H 'accept: application/json' | jq .
```

All three should return JSON with `"success":true`.

---

## ✅ Success Criteria

After following all steps, you should see:
- ✅ All three endpoints return 200 OK
- ✅ Response is JSON with `"success":true`
- ✅ No "Internal Server Error" messages
- ✅ Orders can be created and retrieved

---

## 🆘 If Nothing Works

Share the output of:
1. `git log --oneline -5`
2. `sudo docker logs fastfoodie_api --tail 200`
3. Database status query results
