---
description: Deploy latest code to EC2 server
---

# Deploy to EC2 Server

This workflow deploys the latest code from the main branch to your EC2 server.

## Prerequisites
- EC2 instance is running
- SSH port (22) is accessible
- Docker and Docker Compose are installed on EC2

## Steps

### 1. Verify EC2 instance is running
Check AWS Console to ensure your EC2 instance with IP `52.22.224.42` is running. If the IP has changed, update the DEPLOY_TO_EC2.md file.

### 2. Test SSH connection
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "echo 'Connection successful'"
```

### 3. Pull latest code from GitHub
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "cd fastfoodie-backend && git pull origin main"
```

### 4. Rebuild and restart Docker containers
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "cd fastfoodie-backend && sudo docker-compose down && sudo docker-compose up --build -d"
```

### 5. Check container status
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "sudo docker-compose -f ~/fastfoodie-backend/docker-compose.yml ps"
```

### 6. View application logs
```bash
ssh -i "/Users/satheeshkumar/Downloads/dharaifood.pem" ec2-user@52.22.224.42 "sudo docker logs fastfoodie_api --tail 50"
```

### 7. Verify API is accessible
Open browser and visit: `http://52.22.224.42:8000/docs`

## Troubleshooting

**SSH Connection Timeout:**
- Check if EC2 instance is running in AWS Console
- Verify security group allows SSH (port 22) from your IP
- Confirm the public IP hasn't changed

**Docker Issues:**
- Check logs: `sudo docker logs fastfoodie_api`
- Restart containers: `sudo docker-compose restart`
- Check disk space: `df -h`

**Database Issues:**
- Check MySQL container: `sudo docker logs fastfoodie_mysql`
- Verify database is running: `sudo docker-compose ps`
