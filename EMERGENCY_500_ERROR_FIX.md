# 🚨 URGENT: Server is Returning 500 Errors

## Current Status
- `/orders/new` → 500 Internal Server Error
- `/orders/ongoing` → Likely 500 error
- `/orders/completed` → Likely 500 error

---

## 🔍 Root Cause

The server is still running **OLD CODE** or has a **runtime error** after deployment.

---

## ✅ IMMEDIATE ACTION REQUIRED (On EC2)

### Step 1: Check if code was pulled
```bash
cd ~/fastfoodie-backend
git log --oneline -3
```

**Expected to see:**
```
49b0cf9 CRITICAL FIX: Order creation status bug
fc64fe0 Add diagnostic and testing scripts
8313a3e Fix: MySQL compatibility issue with enum values
```

**If you DON'T see these commits:**
```bash
git pull origin main
```

---

### Step 2: Check if containers are running
```bash
sudo docker-compose ps
```

**Expected output:**
```
NAME                COMMAND                  SERVICE    STATUS
fastfoodie_api      "uvicorn..."            api        Up
fastfoodie_mysql    "docker-entrypoint..."   mysql      Up
```

**If containers are NOT running:**
```bash
sudo docker-compose up -d
```

---

### Step 3: Check application logs for errors
```bash
sudo docker logs fastfoodie_api --tail 100
```

**Look for:**
- ❌ `ERROR` messages
- ❌ `ImportError`
- ❌ `ModuleNotFoundError`
- ❌ `Exception` or `Traceback`
- ✅ `INFO: Application startup complete.`

**Common errors to look for:**
1. `ImportError: cannot import name 'OrderStatusEnum'`
2. `ModuleNotFoundError: No module named 'app.routers.customer'`
3. Database connection errors
4. Syntax errors in Python code

---

### Step 4: Force rebuild (if logs show errors)

```bash
# Stop all containers
sudo docker-compose down

# Remove old images (force clean rebuild)
sudo docker-compose build --no-cache

# Start containers
sudo docker-compose up -d

# Wait 10 seconds
sleep 10

# Check logs again
sudo docker logs fastfoodie_api --tail 50
```

---

### Step 5: Test locally on EC2

```bash
# Test from inside EC2 (bypasses nginx)
curl -X GET 'http://localhost:8000/orders/new' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgxMTg1M30.FS7riXj2FPns1VS8CtPTmmlKDW4U-i8lCKhT4FCrZpY' \
  -H 'accept: application/json'
```

**Expected:**
```json
{"success":true,"message":"New orders retrieved successfully","data":{"orders":[]}}
```

**If you get 500 error even from localhost, check logs immediately!**

---

### Step 6: Verify code changes are present

```bash
# Check if the fix is in the code
grep -n "OrderStatusEnum.PENDING" app/routers/customer.py

# Should show line 366 with:
# status=OrderStatusEnum.PENDING,
```

**If NOT found:**
```bash
# Code wasn't pulled! Pull it now:
git pull origin main
# Then rebuild containers (Step 4)
```

---

## 🔥 MOST LIKELY ISSUE

Based on the 500 error, **one of these is happening:**

1. **Code not pulled** - Still running old code
   - Solution: `git pull origin main` then rebuild

2. **Containers not rebuilt** - Running cached old code
   - Solution: `docker-compose build --no-cache`

3. **Application crashed** - Runtime error in new code
   - Solution: Check logs, fix error, rebuild

4. **Database connection lost** - MySQL container down
   - Solution: `docker-compose restart`

---

## 📋 CHECKLIST

Run these commands in order and share the output:

```bash
# 1. Check current commit
cd ~/fastfoodie-backend && git log --oneline -3

# 2. Check if fix is in code
grep -n "OrderStatusEnum.PENDING" app/routers/customer.py

# 3. Check container status
sudo docker-compose ps

# 4. Check application logs for errors
sudo docker logs fastfoodie_api --tail 100 2>&1 | grep -i "error\|exception\|traceback" -A 5

# 5. Test endpoint locally
curl -s -X GET 'http://localhost:8000/orders/new' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lcl9pZCI6NSwicGhvbmVfbnVtYmVyIjoiKzkxOTc4NjgxNjE4OCIsImV4cCI6MTc2ODgxMTg1M30.FS7riXj2FPns1VS8CtPTmmlKDW4U-i8lCKhT4FCrZpY' \
  -H 'accept: application/json'
```

---

## 🆘 QUICK FIX (If Nothing Works)

```bash
# Nuclear option - complete rebuild
cd ~/fastfoodie-backend
git fetch origin
git reset --hard origin/main
sudo docker-compose down -v
sudo docker-compose build --no-cache
sudo docker-compose up -d
sudo docker logs -f fastfoodie_api
```

Press Ctrl+C when you see "Application startup complete."

---

**Share the output of the checklist commands above so I can diagnose the specific issue!**
