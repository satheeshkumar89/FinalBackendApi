# 🚀 Docker Deployment Guide for AWS EC2

This guide follows your requested workflow using Docker Compose.

## Prerequisites
- EC2 Instance Running (Amazon Linux 2023 or Ubuntu).
- SSH Access.

---

## Step 1: Connect to your EC2 Instance
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42
```

---

## Step 2: Install Docker & Git
Run these commands inside your EC2 instance:

```bash
# Update system
sudo yum update -y

# Install Git and Docker
sudo yum install git docker -y

# Start Docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose version
```
*(Note: You might need to log out and log back in for the user group changes to take effect)*

---

## Step 3: Clone & Setup Project
```bash
# Clone the repository
git clone https://github.com/satheeshkumar89/fastfoodie-backend.git

# Enter directory
cd fastfoodie-backend

# Create .env file (Important for Docker)
cp .env.example .env
nano .env
```
*Edit the `.env` file to add your AWS keys if needed. The database credentials in `docker-compose.yml` are already set to defaults, so you might not need to change DB settings unless you want to.*

---

## Step 4: Run with Docker Compose
```bash
# Build and start containers in background
sudo docker-compose up --build -d
```

---

## Step 5: Manage Application
**Check Logs:**
```bash
# View logs for the API container
sudo docker logs -f fastfoodie_api
```
*(Press `Ctrl+C` to exit logs)*

**Restart Application:**
```bash
sudo docker restart fastfoodie_api
```

**Stop Application:**
```bash
sudo docker-compose down
```

---

## Step 6: Access the API
Your API will be running on port **8000**.
URL: `http://52.22.224.42:8000/docs`

*(Ensure Port 8000 is open in your EC2 Security Group)*
