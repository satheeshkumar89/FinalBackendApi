# 🌐 Nginx Domain Setup Guide for dharaidelivery.online

This guide will help you configure nginx to host your FastFoodie backend on `https://dharaidelivery.online`.

## 📋 Prerequisites

- ✅ Domain: `dharaidelivery.online` 
- ✅ EC2 instance with public IP
- ✅ Nginx installed on EC2
- ✅ FastAPI backend running on port 8000 (via Docker)

---

## 🎯 Step-by-Step Setup

### Step 1: Point Domain to EC2 IP

1. **Get your EC2 Public IP:**
   ```bash
   ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "curl -s ifconfig.me"
   ```

2. **Configure DNS Records:**
   - Go to your domain registrar's DNS management panel
   - Add/Update these DNS records:
   
   | Type | Name | Value | TTL |
   |------|------|-------|-----|
   | A | @ | `YOUR_EC2_PUBLIC_IP` | 300 |
   | A | www | `YOUR_EC2_PUBLIC_IP` | 300 |

3. **Verify DNS propagation** (wait 5-10 minutes):
   ```bash
   nslookup dharaidelivery.online
   nslookup www.dharaidelivery.online
   ```

---

### Step 2: Update EC2 Security Group

Ensure your EC2 security group allows these ports:

| Port | Protocol | Source | Description |
|------|----------|--------|-------------|
| 22 | TCP | Your IP | SSH |
| 80 | TCP | 0.0.0.0/0 | HTTP |
| 443 | TCP | 0.0.0.0/0 | HTTPS |
| 8000 | TCP | 127.0.0.1 | FastAPI (localhost only) |

**Important:** Port 8000 should only be accessible from localhost for security!

---

### Step 3: Install Certbot (SSL Certificate)

SSH into your EC2 instance:
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42
```

Then run:
```bash
# Install Certbot and nginx plugin
sudo yum install -y certbot python3-certbot-nginx

# OR for Ubuntu/Debian:
# sudo apt-get update
# sudo apt-get install -y certbot python3-certbot-nginx
```

---

### Step 4: Upload Nginx Configuration

**From your local machine**, copy the nginx config to EC2:

```bash
scp -i "/Users/satheeshkumar/Downloads/dharaifood.pem" \
  /Users/satheeshkumar/.gemini/antigravity/scratch/fastfoodie-backend/nginx-dharaidelivery.conf \
  ec2-user@52.22.224.42:~/nginx-dharaidelivery.conf
```

---

### Step 5: Configure Nginx on EC2

SSH into EC2 and run:

```bash
# Move config to nginx directory
sudo mv ~/nginx-dharaidelivery.conf /etc/nginx/sites-available/dharaidelivery

# Create sites-enabled directory if it doesn't exist
sudo mkdir -p /etc/nginx/sites-enabled

# Remove default config (if exists)
sudo rm -f /etc/nginx/sites-enabled/default

# Create symlink
sudo ln -sf /etc/nginx/sites-available/dharaidelivery /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t
```

**Expected output:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

### Step 6: Obtain SSL Certificate

**IMPORTANT:** Before running this, ensure:
- DNS is pointing to your EC2 IP
- Port 80 and 443 are open in security group
- Nginx is NOT running yet (we'll start it after)

```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Obtain SSL certificate
sudo certbot certonly --standalone -d dharaidelivery.online -d www.dharaidelivery.online --email your-email@example.com --agree-tos --non-interactive

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

**Alternative method** (if nginx is already running):
```bash
# Create webroot directory for ACME challenge
sudo mkdir -p /var/www/certbot

# Obtain certificate using webroot
sudo certbot certonly --webroot -w /var/www/certbot \
  -d dharaidelivery.online -d www.dharaidelivery.online \
  --email your-email@example.com --agree-tos --non-interactive
```

---

### Step 7: Update Nginx Config with SSL

The configuration file `nginx-dharaidelivery.conf` already includes SSL settings. Just reload nginx:

```bash
# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

---

### Step 8: Set Up SSL Auto-Renewal

Certbot certificates expire every 90 days. Set up auto-renewal:

```bash
# Test renewal process
sudo certbot renew --dry-run

# Add cron job for auto-renewal
echo "0 0,12 * * * root certbot renew --quiet --post-hook 'systemctl reload nginx'" | sudo tee -a /etc/crontab
```

---

### Step 9: Verify Backend is Running

Ensure your FastAPI backend is running on port 8000:

```bash
# Check Docker containers
sudo docker-compose -f ~/fastfoodie-backend/docker-compose.yml ps

# Check if backend responds
curl http://localhost:8000/docs

# Check nginx can reach backend
curl -I http://localhost:8000
```

---

### Step 10: Test Your Domain

1. **Test HTTP → HTTPS redirect:**
   ```bash
   curl -I http://dharaidelivery.online
   ```
   Should return `301 Moved Permanently` with `Location: https://...`

2. **Test HTTPS:**
   ```bash
   curl -I https://dharaidelivery.online
   ```
   Should return `200 OK`

3. **Test API endpoint:**
   ```bash
   curl https://dharaidelivery.online/docs
   ```

4. **Open in browser:**
   - Visit: `https://dharaidelivery.online/docs`
   - You should see the FastAPI Swagger documentation

---

## 🔍 Troubleshooting

### Issue: "502 Bad Gateway"

**Cause:** Nginx can't reach the backend on port 8000.

**Solution:**
```bash
# Check if backend is running
sudo docker ps | grep fastfoodie_api

# Check backend logs
sudo docker logs fastfoodie_api --tail 100

# Restart backend
cd ~/fastfoodie-backend
sudo docker-compose restart
```

---

### Issue: "SSL Certificate Error"

**Cause:** Certbot couldn't obtain certificate.

**Solution:**
```bash
# Check DNS is pointing to EC2
nslookup dharaidelivery.online

# Check port 80 is accessible
curl -I http://dharaidelivery.online

# Try obtaining certificate again
sudo certbot certonly --standalone -d dharaidelivery.online -d www.dharaidelivery.online
```

---

### Issue: "Connection Timeout"

**Cause:** Security group not allowing traffic.

**Solution:**
1. Go to AWS Console → EC2 → Security Groups
2. Find your instance's security group
3. Ensure inbound rules allow:
   - Port 80 from 0.0.0.0/0
   - Port 443 from 0.0.0.0/0

---

### Issue: WebSocket/Socket.IO Not Working

**Cause:** Nginx not properly configured for WebSocket upgrade.

**Solution:**
The provided config already includes WebSocket support. Verify:
```bash
# Check nginx config includes socket.io location
sudo grep -A 10 "location /socket.io/" /etc/nginx/sites-available/dharaidelivery

# Test WebSocket connection
curl -I https://dharaidelivery.online/socket.io/
```

---

## 📊 Monitoring & Logs

### View Nginx Logs
```bash
# Access log
sudo tail -f /var/log/nginx/dharaidelivery-access.log

# Error log
sudo tail -f /var/log/nginx/dharaidelivery-error.log
```

### View Backend Logs
```bash
sudo docker logs -f fastfoodie_api
```

### Check Nginx Status
```bash
sudo systemctl status nginx
```

---

## 🔐 Security Best Practices

✅ **Implemented in the config:**
- HTTPS redirect for all HTTP traffic
- Modern TLS 1.2 and 1.3 only
- Strong cipher suites
- HSTS header (forces HTTPS)
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- 20MB upload limit for images

✅ **Additional recommendations:**
1. Keep nginx and certbot updated
2. Monitor SSL certificate expiry
3. Use fail2ban to prevent brute force attacks
4. Regularly review nginx logs

---

## 🚀 Quick Reference Commands

```bash
# Restart nginx
sudo systemctl restart nginx

# Reload nginx (no downtime)
sudo systemctl reload nginx

# Test nginx config
sudo nginx -t

# View nginx status
sudo systemctl status nginx

# Renew SSL certificate
sudo certbot renew

# View certificate info
sudo certbot certificates
```

---

## ✅ Success Checklist

After completing all steps, verify:

- [ ] Domain resolves to EC2 IP
- [ ] HTTP redirects to HTTPS
- [ ] HTTPS works with valid SSL certificate
- [ ] API docs accessible at `https://dharaidelivery.online/docs`
- [ ] No SSL warnings in browser
- [ ] WebSocket connections work (for real-time order updates)
- [ ] Can upload images (test with restaurant/menu image upload)
- [ ] Backend logs show no errors

---

## 📞 Next Steps

Once your domain is live:

1. **Update mobile apps** to use `https://dharaidelivery.online` instead of IP address
2. **Update Firebase/FCM configuration** with new domain
3. **Test all API endpoints** from mobile apps
4. **Monitor logs** for any issues
5. **Set up monitoring** (optional: CloudWatch, Datadog, etc.)

---

## 🆘 Need Help?

If you encounter issues:
1. Check nginx error logs: `sudo tail -100 /var/log/nginx/dharaidelivery-error.log`
2. Check backend logs: `sudo docker logs fastfoodie_api --tail 100`
3. Verify DNS: `nslookup dharaidelivery.online`
4. Test backend directly: `curl http://localhost:8000/docs`
