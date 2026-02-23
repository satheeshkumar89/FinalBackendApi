# 📤 Upload Files to EC2 - Step by Step

## ⚠️ Important: Run These Commands from Your LOCAL MACHINE

**NOT from EC2!** If you're currently SSH'd into EC2, type `exit` first.

---

## 🎯 Quick Upload Commands

### Step 1: Open a NEW Terminal on Your Mac

Press `Cmd + T` to open a new terminal tab, or open a completely new terminal window.

### Step 2: Navigate to the Project Directory

```bash
cd /Users/satheeshkumar/.gemini/antigravity/scratch/fastfoodie-backend
```

### Step 3: Verify Files Exist

```bash
ls -lh nginx-dharaidelivery.conf setup-nginx.sh
```

You should see:
```
-rw-r--r--  nginx-dharaidelivery.conf
-rw-r--r--  setup-nginx.sh
```

### Step 4: Upload Files to EC2

**Note:** The EC2 instance appears to be using `ubuntu` user, not `ec2-user`. Let me provide both options:

#### Option A: If using ubuntu user (most likely)

```bash
scp -i "/Users/satheeshkumar/Downloads/dharaifood.pem" \
  nginx-dharaidelivery.conf setup-nginx.sh \
  ubuntu@52.22.224.42:~/
```

#### Option B: If using ec2-user

```bash
scp -i "/Users/satheeshkumar/Downloads/dharaifood.pem" \
  nginx-dharaidelivery.conf setup-nginx.sh \
  ec2-user@52.22.224.42:~/
```

### Step 5: Verify Upload

SSH into EC2 and check files:

```bash
# SSH into EC2
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ubuntu@52.22.224.42

# Check files are there
ls -lh ~/nginx-dharaidelivery.conf ~/setup-nginx.sh
```

---

## 🚀 After Upload - Run Setup

Once files are uploaded, run the setup script on EC2:

```bash
# Make script executable
chmod +x ~/setup-nginx.sh

# Run the setup script
sudo ./setup-nginx.sh
```

---

## 🔍 Troubleshooting

### Issue: "Permission denied (publickey)"

**Solution:** Check your PEM file permissions
```bash
chmod 400 "/Users/satheeshkumar/Downloads/dharaifood.pem"
```

### Issue: "No such file or directory" for PEM file

**Solution:** Verify PEM file exists
```bash
ls -l "/Users/satheeshkumar/Downloads/dharaifood.pem"
```

### Issue: "Connection refused" or "Connection timed out"

**Solution:** 
1. Check EC2 instance is running in AWS Console
2. Verify security group allows SSH (port 22) from your IP
3. Confirm the IP address is correct (52.22.224.42)

### Issue: Files not found after upload

**Solution:** Check you're in the right directory on EC2
```bash
pwd  # Should show /home/ubuntu or /home/ec2-user
ls -la  # List all files including hidden ones
```

---

## ✅ Success Indicators

You'll know it worked when:

1. ✅ `scp` command completes without errors
2. ✅ You see: `nginx-dharaidelivery.conf  100%  3.5KB`
3. ✅ You see: `setup-nginx.sh  100%  7.8KB`
4. ✅ Files exist on EC2: `ls -lh ~/*.conf ~/*.sh`

---

## 📝 Quick Reference

**Your EC2 Details:**
- IP: `52.22.224.42`
- User: `ubuntu` (based on your login prompt)
- PEM: `/Users/satheeshkumar/Downloads/dharaifood.pem`
- Project: `/Users/satheeshkumar/.gemini/antigravity/scratch/fastfoodie-backend`

**Upload Command (Copy-Paste Ready):**
```bash
cd /Users/satheeshkumar/.gemini/antigravity/scratch/fastfoodie-backend && \
scp -i "/Users/satheeshkumar/Downloads/dharaifood.pem" \
  nginx-dharaidelivery.conf setup-nginx.sh \
  ubuntu@52.22.224.42:~/
```

---

## 🎯 Next Steps After Upload

1. ✅ Upload files (you're doing this now)
2. SSH into EC2
3. Run setup script
4. Configure domain
5. Test HTTPS

Follow `NGINX_DOMAIN_SETUP.md` for detailed next steps!
