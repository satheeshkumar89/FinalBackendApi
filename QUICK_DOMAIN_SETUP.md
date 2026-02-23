# 🚀 Quick Setup Guide - dharaidelivery.online

## 📝 TL;DR - 5 Minute Setup

### Prerequisites
- ✅ Domain: `dharaidelivery.online` pointing to your EC2 IP
- ✅ EC2 Security Group: Ports 80, 443 open
- ✅ Backend running on port 8000

### Quick Commands

**1. Upload nginx config to EC2:**
```bash
scp -i "/Users/satheeshkumar/Downloads/dharaifood.pem" \
  nginx-dharaidelivery.conf \
  ec2-user@52.22.224.42:~/
```

**2. Upload and run setup script:**
```bash
# Upload script
scp -i "/Users/satheeshkumar/Downloads/dharaifood.pem" \
  setup-nginx.sh \
  ec2-user@52.22.224.42:~/

# SSH into EC2
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42

# Run setup script
chmod +x setup-nginx.sh
sudo ./setup-nginx.sh
```

**3. Done! Test it:**
```bash
curl https://dharaidelivery.online/docs
```

---

## 🎯 Manual Setup (Alternative)

If you prefer manual setup, follow these steps on EC2:

```bash
# 1. Install Certbot
sudo yum install -y certbot python3-certbot-nginx

# 2. Move nginx config
sudo mv ~/nginx-dharaidelivery.conf /etc/nginx/sites-available/dharaidelivery
sudo mkdir -p /etc/nginx/sites-enabled
sudo ln -sf /etc/nginx/sites-available/dharaidelivery /etc/nginx/sites-enabled/

# 3. Get SSL certificate (update email!)
sudo certbot certonly --nginx \
  -d dharaidelivery.online \
  -d www.dharaidelivery.online \
  --email YOUR_EMAIL@example.com \
  --agree-tos \
  --non-interactive

# 4. Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl enable nginx

# 5. Set up auto-renewal
echo "0 0,12 * * * root certbot renew --quiet --post-hook 'systemctl reload nginx'" | sudo tee -a /etc/crontab
```

---

## 🔍 Verification Checklist

After setup, verify everything works:

```bash
# ✅ Check DNS
nslookup dharaidelivery.online

# ✅ Check SSL certificate
curl -I https://dharaidelivery.online

# ✅ Check API docs
curl https://dharaidelivery.online/docs

# ✅ Check backend is running
sudo docker ps | grep fastfoodie_api

# ✅ Check nginx status
sudo systemctl status nginx

# ✅ Check logs for errors
sudo tail -50 /var/log/nginx/dharaidelivery-error.log
```

---

## 🆘 Troubleshooting

### 502 Bad Gateway
```bash
# Backend not running
sudo docker-compose -f ~/fastfoodie-backend/docker-compose.yml up -d

# Check backend logs
sudo docker logs fastfoodie_api --tail 100
```

### SSL Certificate Error
```bash
# Check certificate exists
sudo certbot certificates

# Renew certificate
sudo certbot renew --force-renewal
```

### Connection Refused
```bash
# Check security group allows ports 80, 443
# Check nginx is running
sudo systemctl status nginx

# Restart nginx
sudo systemctl restart nginx
```

---

## 📊 Monitoring Commands

```bash
# Watch access logs in real-time
sudo tail -f /var/log/nginx/dharaidelivery-access.log

# Watch error logs
sudo tail -f /var/log/nginx/dharaidelivery-error.log

# Watch backend logs
sudo docker logs -f fastfoodie_api

# Check SSL certificate expiry
sudo certbot certificates
```

---

## 🔄 Update Backend

When you push new code:

```bash
# Pull latest code
cd ~/fastfoodie-backend
git pull origin main

# Rebuild containers
sudo docker-compose down
sudo docker-compose up --build -d

# Check logs
sudo docker logs fastfoodie_api --tail 50
```

Nginx will automatically proxy to the updated backend!

---

## 📱 Update Mobile Apps

After domain is live, update these in your mobile apps:

**Old URL:**
```
http://52.22.224.42:8000
```

**New URL:**
```
https://dharaidelivery.online
```

Update in:
- Customer App: `lib/config/api_config.dart`
- Restaurant App: `lib/config/api_config.dart`
- Delivery Partner App: `lib/config/api_config.dart`
- Admin App: `lib/config/api_config.dart`

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ `https://dharaidelivery.online/docs` shows Swagger UI
2. ✅ Browser shows 🔒 (secure/SSL)
3. ✅ Mobile apps can connect and fetch data
4. ✅ Real-time order updates work (WebSocket)
5. ✅ Image uploads work
6. ✅ No errors in nginx logs

---

## 🎉 You're Done!

Your FastFoodie backend is now professionally hosted at:
**https://dharaidelivery.online**

Share this URL with your mobile apps and start testing! 🚀
