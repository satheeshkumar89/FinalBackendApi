# ✅ Domain Setup Checklist - dharaidelivery.online

Use this checklist to track your progress setting up the domain.

---

## 📋 Pre-Setup Checklist

- [ ] **Domain purchased:** dharaidelivery.online
- [ ] **EC2 instance running:** Get public IP
- [ ] **Backend running:** FastAPI on port 8000
- [ ] **Docker containers up:** MySQL + FastAPI
- [ ] **SSH access working:** Can connect to EC2

---

## 🌐 DNS Configuration

- [ ] **Get EC2 Public IP**
  ```bash
  ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "curl -s ifconfig.me"
  ```
  **IP:** ________________

- [ ] **Add A record for root domain**
  - Type: A
  - Name: @
  - Value: [Your EC2 IP]
  - TTL: 300

- [ ] **Add A record for www subdomain**
  - Type: A
  - Name: www
  - Value: [Your EC2 IP]
  - TTL: 300

- [ ] **Verify DNS propagation** (wait 5-10 minutes)
  ```bash
  nslookup dharaidelivery.online
  nslookup www.dharaidelivery.online
  ```

---

## 🔒 AWS Security Group

- [ ] **Open Port 80 (HTTP)**
  - Type: HTTP
  - Port: 80
  - Source: 0.0.0.0/0

- [ ] **Open Port 443 (HTTPS)**
  - Type: HTTPS
  - Port: 443
  - Source: 0.0.0.0/0

- [ ] **Keep Port 22 (SSH)**
  - Type: SSH
  - Port: 22
  - Source: Your IP only

- [ ] **Close Port 8000 to public**
  - Remove any rule allowing 8000 from 0.0.0.0/0
  - Backend should only be accessible via nginx

---

## 📤 Upload Files to EC2

- [ ] **Upload nginx configuration**
  ```bash
  scp -i "/Users/satheeshkumar/Downloads/dharaifood.pem" \
    nginx-dharaidelivery.conf \
    ec2-user@52.22.224.42:~/
  ```

- [ ] **Upload setup script**
  ```bash
  scp -i "/Users/satheeshkumar/Downloads/dharaifood.pem" \
    setup-nginx.sh \
    ec2-user@52.22.224.42:~/
  ```

- [ ] **Verify files uploaded**
  ```bash
  ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "ls -lh ~/*.conf ~/*.sh"
  ```

---

## 🔧 EC2 Setup

- [ ] **SSH into EC2**
  ```bash
  ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42
  ```

- [ ] **Install Certbot**
  ```bash
  sudo yum install -y certbot python3-certbot-nginx
  ```

- [ ] **Run automated setup script**
  ```bash
  chmod +x setup-nginx.sh
  sudo ./setup-nginx.sh
  ```
  
  **OR** follow manual steps below:

---

## 🔧 Manual Setup (Alternative to Script)

- [ ] **Move nginx config**
  ```bash
  sudo mv ~/nginx-dharaidelivery.conf /etc/nginx/sites-available/dharaidelivery
  sudo mkdir -p /etc/nginx/sites-enabled
  sudo ln -sf /etc/nginx/sites-available/dharaidelivery /etc/nginx/sites-enabled/
  ```

- [ ] **Test nginx config**
  ```bash
  sudo nginx -t
  ```

- [ ] **Start nginx**
  ```bash
  sudo systemctl start nginx
  sudo systemctl enable nginx
  ```

- [ ] **Obtain SSL certificate**
  ```bash
  sudo certbot certonly --nginx \
    -d dharaidelivery.online \
    -d www.dharaidelivery.online \
    --email YOUR_EMAIL@example.com \
    --agree-tos \
    --non-interactive
  ```

- [ ] **Reload nginx with SSL**
  ```bash
  sudo nginx -t
  sudo systemctl reload nginx
  ```

- [ ] **Set up auto-renewal**
  ```bash
  echo "0 0,12 * * * root certbot renew --quiet --post-hook 'systemctl reload nginx'" | sudo tee -a /etc/crontab
  ```

---

## ✅ Verification Tests

### Test 1: DNS Resolution
- [ ] **Test domain resolves**
  ```bash
  nslookup dharaidelivery.online
  ```
  Should return your EC2 IP

### Test 2: HTTP Redirect
- [ ] **Test HTTP redirects to HTTPS**
  ```bash
  curl -I http://dharaidelivery.online
  ```
  Should return `301 Moved Permanently` with `Location: https://...`

### Test 3: HTTPS Works
- [ ] **Test HTTPS connection**
  ```bash
  curl -I https://dharaidelivery.online
  ```
  Should return `200 OK`

### Test 4: API Accessible
- [ ] **Test API docs endpoint**
  ```bash
  curl https://dharaidelivery.online/docs
  ```
  Should return HTML with "FastAPI"

### Test 5: Backend Running
- [ ] **Check backend is responding**
  ```bash
  ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "curl -I http://localhost:8000/docs"
  ```
  Should return `200 OK`

### Test 6: Docker Containers
- [ ] **Check containers are running**
  ```bash
  ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "sudo docker ps"
  ```
  Should show `fastfoodie_api` and `fastfoodie_mysql`

### Test 7: SSL Certificate
- [ ] **Check SSL certificate is valid**
  ```bash
  ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "sudo certbot certificates"
  ```
  Should show certificate for dharaidelivery.online

### Test 8: Browser Test
- [ ] **Open in browser:** https://dharaidelivery.online/docs
  - Should show 🔒 (secure)
  - Should display FastAPI Swagger UI
  - No SSL warnings

### Test 9: WebSocket Test
- [ ] **Test Socket.IO endpoint**
  ```bash
  curl -I https://dharaidelivery.online/socket.io/
  ```
  Should return response (not 404)

### Test 10: Logs Check
- [ ] **Check nginx logs for errors**
  ```bash
  ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "sudo tail -50 /var/log/nginx/dharaidelivery-error.log"
  ```
  Should have no critical errors

---

## 📱 Update Mobile Apps

After domain is verified working:

### Customer App
- [ ] **Update API base URL**
  - File: `lib/config/api_config.dart` (or similar)
  - Old: `http://52.22.224.42:8000`
  - New: `https://dharaidelivery.online`

### Restaurant App
- [ ] **Update API base URL**
  - File: `lib/config/api_config.dart` (or similar)
  - Old: `http://52.22.224.42:8000`
  - New: `https://dharaidelivery.online`

### Delivery Partner App
- [ ] **Update API base URL**
  - File: `lib/config/api_config.dart` (or similar)
  - Old: `http://52.22.224.42:8000`
  - New: `https://dharaidelivery.online`

### Admin App
- [ ] **Update API base URL**
  - File: `lib/config/api_config.dart` (or similar)
  - Old: `http://52.22.224.42:8000`
  - New: `https://dharaidelivery.online`

---

## 🧪 End-to-End Testing

- [ ] **Customer app can:**
  - [ ] Login/Register
  - [ ] Browse restaurants
  - [ ] Place order
  - [ ] Track order in real-time
  - [ ] Receive push notifications

- [ ] **Restaurant app can:**
  - [ ] Login
  - [ ] View new orders
  - [ ] Accept/Reject orders
  - [ ] Update order status
  - [ ] Upload menu images

- [ ] **Delivery Partner app can:**
  - [ ] Login
  - [ ] View available orders
  - [ ] Accept delivery
  - [ ] Update location
  - [ ] Complete delivery

- [ ] **Admin app can:**
  - [ ] Login
  - [ ] View all orders
  - [ ] Manage restaurants
  - [ ] View analytics

---

## 🔍 Monitoring Setup

- [ ] **Set up log monitoring**
  ```bash
  # Add to your local machine for easy log viewing
  alias nginx-logs="ssh -i '/Users/satheeshkumar/Downloads/dharaifood.pem' ec2-user@52.22.224.42 'sudo tail -f /var/log/nginx/dharaidelivery-access.log'"
  alias backend-logs="ssh -i '/Users/satheeshkumar/Downloads/dharaifood.pem' ec2-user@52.22.224.42 'sudo docker logs -f fastfoodie_api'"
  ```

- [ ] **Test SSL expiry monitoring**
  ```bash
  ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "sudo certbot certificates"
  ```
  Note expiry date: ________________

- [ ] **Verify auto-renewal cron job**
  ```bash
  ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "sudo crontab -l | grep certbot"
  ```

---

## 📝 Documentation

- [ ] **Document the new URL**
  - Update README.md with new domain
  - Update API documentation
  - Update any hardcoded URLs in code

- [ ] **Share with team**
  - [ ] Backend URL: https://dharaidelivery.online
  - [ ] API Docs: https://dharaidelivery.online/docs
  - [ ] SSL Status: Valid until [expiry date]

---

## 🎉 Final Verification

- [ ] **All mobile apps working with new domain**
- [ ] **HTTPS working without warnings**
- [ ] **Real-time features working (WebSocket)**
- [ ] **Image uploads working**
- [ ] **Push notifications working**
- [ ] **No errors in logs**
- [ ] **SSL certificate auto-renewal configured**
- [ ] **Monitoring set up**

---

## 📞 Support Contacts

**If you encounter issues:**

1. **Check logs:**
   - Nginx: `/var/log/nginx/dharaidelivery-error.log`
   - Backend: `sudo docker logs fastfoodie_api`

2. **Common issues:**
   - DNS not propagating → Wait 10-30 minutes
   - 502 Bad Gateway → Backend not running
   - SSL errors → Certificate not obtained
   - Connection refused → Security group blocking

3. **Quick fixes:**
   ```bash
   # Restart nginx
   sudo systemctl restart nginx
   
   # Restart backend
   cd ~/fastfoodie-backend
   sudo docker-compose restart
   
   # Renew SSL
   sudo certbot renew --force-renewal
   ```

---

## 🚀 You're Live!

Once all checkboxes are ✅, your FastFoodie backend is live at:

**🌐 https://dharaidelivery.online**

Congratulations! 🎉
