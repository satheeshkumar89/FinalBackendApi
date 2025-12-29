# 🚀 Deploying Delivery Partner API to EC2

## Latest Code Status
✅ **Commit**: `88e9512` - Complete Delivery Partner System - Registration, Admin Approval, Location Tracking & 24 APIs

## Prerequisites Check

Before deploying, ensure:
1. ☐ EC2 instance (52.22.224.42) is **RUNNING** in AWS Console
2. ☐ Security Group allows SSH (port 22) from your IP
3. ☐ Security Group allows HTTP (port 8000) for API access
4. ☐ SSH key is accessible: `/Users/satheeshkumar/Downloads/dharaifood.pem`

---

## Method 1: Automated Deployment (Recommended)

### Step 1: Test SSH Connection
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "echo 'Connection successful'"
```

**If this fails:**
- Check EC2 instance status in AWS Console
- Verify your current IP is allowed in Security Group (port 22)
- Try from AWS Console's "EC2 Instance Connect" first

### Step 2: Pull Latest Code
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 \
  "cd fastfoodie-backend && git pull origin main"
```

### Step 3: Rebuild and Deploy
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 \
  "cd fastfoodie-backend && sudo docker-compose down && sudo docker-compose up --build -d"
```

### Step 4: Verify Deployment
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 \
  "sudo docker-compose -f ~/fastfoodie-backend/docker-compose.yml ps"
```

### Step 5: Check Logs
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 \
  "sudo docker logs fastfoodie_api --tail 100"
```

---

## Method 2: Manual Deployment (Via AWS Console)

If SSH from terminal fails, use **EC2 Instance Connect** from AWS Console:

### Step 1: Connect via AWS Console
1. Go to AWS EC2 Console
2. Select your instance
3. Click **Connect** → **EC2 Instance Connect**
4. Click **Connect** button

### Step 2: Run Deployment Commands
Once connected to the terminal:

```bash
# Navigate to project
cd fastfoodie-backend

# Pull latest code
git pull origin main

# Stop current containers
sudo docker-compose down

# Rebuild and start containers
sudo docker-compose up --build -d

# Check status
sudo docker-compose ps

# View logs
sudo docker logs fastfoodie_api --tail 50
```

---

## Method 3: One-Line Deployment

**Combined command (run after SSH is working):**
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 \
  "cd fastfoodie-backend && \
   git pull origin main && \
   sudo docker-compose down && \
   sudo docker-compose up --build -d && \
   sudo docker-compose ps && \
   sudo docker logs fastfoodie_api --tail 30"
```

---

## Verification Steps

### 1. API Documentation
Open in browser: `http://52.22.224.42:8000/docs`

### 2. Test Delivery Partner Endpoints

**Register Delivery Partner:**
```bash
curl -X POST "http://52.22.224.42:8000/delivery-partner/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Partner",
    "email": "partner@test.com",
    "phone": "+911234567890",
    "vehicle_type": "BIKE"
  }'
```

**Get Pending Approvals (Admin):**
```bash
curl -X GET "http://52.22.224.42:8000/admin/delivery-partners/pending" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 3. Check All Containers
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 \
  "sudo docker ps -a"
```

---

## New Delivery Partner APIs Deployed

The following 24 APIs are now available:

### Registration & Authentication
- `POST /delivery-partner/register` - Register new partner
- `POST /delivery-partner/login` - Partner login
- `GET /delivery-partner/profile` - Get profile
- `PUT /delivery-partner/profile` - Update profile

### Admin Approval System
- `GET /admin/delivery-partners/pending` - List pending approvals
- `GET /admin/delivery-partners/{partner_id}/details` - View details
- `POST /admin/delivery-partners/{partner_id}/approve` - Approve partner
- `POST /admin/delivery-partners/{partner_id}/reject` - Reject partner

### Location Tracking
- `POST /delivery-partner/location/update` - Update current location
- `GET /delivery-partner/location/history` - Get location history
- `GET /admin/delivery-partners/{partner_id}/location/current` - Track partner

### Status Management
- `POST /delivery-partner/status/toggle` - Go online/offline
- `GET /delivery-partner/status` - Check current status

### Order Management
- `GET /delivery-partner/orders/available` - View available orders
- `POST /delivery-partner/orders/{order_id}/accept` - Accept order
- `GET /delivery-partner/orders/active` - View active deliveries
- `GET /delivery-partner/orders/{order_id}` - Order details
- `POST /delivery-partner/orders/{order_id}/pickup` - Mark picked up
- `POST /delivery-partner/orders/{order_id}/deliver` - Complete delivery

### Statistics & Earnings
- `GET /delivery-partner/stats` - View statistics
- `GET /delivery-partner/earnings` - View earnings

### Additional APIs
- `GET /delivery-partner/orders/history` - Delivery history
- `POST /delivery-partner/documents/upload` - Upload documents
- `GET /admin/delivery-partners/all` - List all partners (admin)

---

## Troubleshooting

### SSH Connection Issues

**Problem:** Connection timeout
**Solutions:**
1. Check EC2 instance state (should be "running")
2. Verify Security Group inbound rules for port 22
3. Check if instance IP has changed
4. Use AWS Systems Manager Session Manager as alternative
5. Try EC2 Instance Connect from AWS Console

### Docker Container Issues

**Check if containers are running:**
```bash
sudo docker-compose ps
```

**View detailed logs:**
```bash
sudo docker logs fastfoodie_api --tail 200 -f
```

**Restart specific container:**
```bash
sudo docker-compose restart api
```

**Rebuild from scratch:**
```bash
sudo docker-compose down -v
sudo docker-compose up --build -d
```

### Database Migration Issues

**Run migrations manually:**
```bash
sudo docker-compose exec api python migrate.py
```

### Port 8000 Not Accessible

1. Check Security Group allows inbound on port 8000
2. Verify container is running: `sudo docker ps`
3. Check if port is bound: `sudo netstat -tulpn | grep 8000`

---

## Rollback Instructions

If deployment fails, rollback to previous version:

```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 \
  "cd fastfoodie-backend && \
   git log --oneline -5 && \
   git checkout <previous-commit-hash> && \
   sudo docker-compose up --build -d"
```

---

## Post-Deployment Checklist

- [ ] API docs accessible at `http://52.22.224.42:8000/docs`
- [ ] All containers running (`sudo docker-compose ps`)
- [ ] No errors in logs (`sudo docker logs fastfoodie_api`)
- [ ] Database connected successfully
- [ ] Test delivery partner registration endpoint
- [ ] Test admin approval endpoints
- [ ] Test location tracking endpoints
- [ ] Verify Firebase notifications working
- [ ] Check Redis is running for caching

---

## Quick Status Check

Run this to get full status:
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 << 'EOF'
echo "=== Git Status ==="
cd fastfoodie-backend && git log -1 --oneline
echo -e "\n=== Docker Containers ==="
sudo docker-compose ps
echo -e "\n=== API Logs (last 20 lines) ==="
sudo docker logs fastfoodie_api --tail 20
echo -e "\n=== Disk Usage ==="
df -h
echo -e "\n=== Memory Usage ==="
free -h
EOF
```

---

## Support

If you need assistance:
1. Check application logs first
2. Verify all containers are healthy
3. Ensure Security Groups are properly configured
4. Test API endpoints using Postman or curl
