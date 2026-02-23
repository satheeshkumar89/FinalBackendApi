#!/bin/bash

# FastFoodie Nginx Setup Script for dharaidelivery.online
# This script automates the nginx configuration on EC2

set -e  # Exit on error

echo "🚀 FastFoodie Nginx Setup for dharaidelivery.online"
echo "=================================================="
echo ""

# Configuration
DOMAIN="dharaidelivery.online"
WWW_DOMAIN="www.dharaidelivery.online"
EMAIL="your-email@example.com"  # UPDATE THIS!
BACKEND_PORT="8000"
CONFIG_NAME="dharaidelivery"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running on EC2
if [ ! -f /etc/nginx/nginx.conf ]; then
    print_error "Nginx not found! Please install nginx first."
    echo "Run: sudo yum install -y nginx"
    exit 1
fi

print_success "Nginx is installed"

# Step 1: Check if backend is running
echo ""
echo "Step 1: Checking if FastAPI backend is running..."
if curl -s http://localhost:${BACKEND_PORT}/docs > /dev/null; then
    print_success "Backend is running on port ${BACKEND_PORT}"
else
    print_warning "Backend is not responding on port ${BACKEND_PORT}"
    echo "Please ensure your FastAPI backend is running before continuing."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Install Certbot if not installed
echo ""
echo "Step 2: Checking Certbot installation..."
if ! command -v certbot &> /dev/null; then
    print_warning "Certbot not found. Installing..."
    sudo yum install -y certbot python3-certbot-nginx || sudo apt-get install -y certbot python3-certbot-nginx
    print_success "Certbot installed"
else
    print_success "Certbot is already installed"
fi

# Step 3: Create nginx configuration
echo ""
echo "Step 3: Creating nginx configuration..."

# Check if config file exists in home directory
if [ ! -f ~/nginx-${CONFIG_NAME}.conf ]; then
    print_error "Configuration file not found: ~/nginx-${CONFIG_NAME}.conf"
    echo "Please upload the configuration file first using:"
    echo "scp -i \"path/to/key.pem\" nginx-dharaidelivery.conf ec2-user@YOUR_IP:~/"
    exit 1
fi

# Move config to nginx directory
sudo cp ~/nginx-${CONFIG_NAME}.conf /etc/nginx/sites-available/${CONFIG_NAME}
print_success "Configuration copied to /etc/nginx/sites-available/${CONFIG_NAME}"

# Create sites-enabled directory if it doesn't exist
sudo mkdir -p /etc/nginx/sites-enabled

# Remove default config
if [ -f /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
    print_success "Removed default nginx configuration"
fi

# Create symlink
sudo ln -sf /etc/nginx/sites-available/${CONFIG_NAME} /etc/nginx/sites-enabled/
print_success "Created symlink in sites-enabled"

# Step 4: Test nginx configuration (will fail if SSL certs don't exist yet)
echo ""
echo "Step 4: Testing nginx configuration..."
if sudo nginx -t 2>&1 | grep -q "ssl_certificate"; then
    print_warning "SSL certificates not found yet (expected at this stage)"
    
    # Create temporary config without SSL for certbot
    echo "Creating temporary HTTP-only configuration for SSL certificate generation..."
    
    sudo tee /etc/nginx/sites-available/${CONFIG_NAME}-temp > /dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} ${WWW_DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://127.0.0.1:${BACKEND_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/${CONFIG_NAME}-temp /etc/nginx/sites-enabled/${CONFIG_NAME}
    
    if sudo nginx -t; then
        print_success "Temporary nginx configuration is valid"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
else
    print_success "Nginx configuration is valid"
fi

# Step 5: Reload nginx
echo ""
echo "Step 5: Reloading nginx..."
sudo systemctl reload nginx || sudo systemctl start nginx
sudo systemctl enable nginx
print_success "Nginx reloaded and enabled"

# Step 6: Obtain SSL certificate
echo ""
echo "Step 6: Obtaining SSL certificate..."
print_warning "Make sure your domain ${DOMAIN} is pointing to this server's IP!"
echo "Current server IP:"
curl -s ifconfig.me
echo ""

read -p "Is your domain pointing to this IP? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Please update your DNS records first, then run this script again."
    exit 1
fi

# Create webroot directory
sudo mkdir -p /var/www/certbot

# Obtain certificate
if [ ! -d "/etc/letsencrypt/live/${DOMAIN}" ]; then
    print_warning "Obtaining SSL certificate for ${DOMAIN} and ${WWW_DOMAIN}..."
    
    # Update email if needed
    if [ "$EMAIL" = "your-email@example.com" ]; then
        read -p "Enter your email address for SSL certificate: " EMAIL
    fi
    
    sudo certbot certonly --webroot -w /var/www/certbot \
        -d ${DOMAIN} -d ${WWW_DOMAIN} \
        --email ${EMAIL} \
        --agree-tos \
        --non-interactive \
        --quiet
    
    if [ $? -eq 0 ]; then
        print_success "SSL certificate obtained successfully"
    else
        print_error "Failed to obtain SSL certificate"
        echo "Please check:"
        echo "1. DNS is pointing to this server"
        echo "2. Port 80 is accessible from the internet"
        echo "3. No firewall blocking port 80"
        exit 1
    fi
else
    print_success "SSL certificate already exists"
fi

# Step 7: Switch to full SSL configuration
echo ""
echo "Step 7: Activating full SSL configuration..."
sudo ln -sf /etc/nginx/sites-available/${CONFIG_NAME} /etc/nginx/sites-enabled/${CONFIG_NAME}

if sudo nginx -t; then
    print_success "SSL configuration is valid"
    sudo systemctl reload nginx
    print_success "Nginx reloaded with SSL configuration"
else
    print_error "SSL configuration test failed"
    exit 1
fi

# Step 8: Set up auto-renewal
echo ""
echo "Step 8: Setting up SSL certificate auto-renewal..."
if ! sudo crontab -l 2>/dev/null | grep -q "certbot renew"; then
    (sudo crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | sudo crontab -
    print_success "Auto-renewal cron job added"
else
    print_success "Auto-renewal already configured"
fi

# Step 9: Test the setup
echo ""
echo "Step 9: Testing the setup..."

# Test HTTP redirect
echo -n "Testing HTTP → HTTPS redirect... "
if curl -s -I http://${DOMAIN} | grep -q "301"; then
    print_success "HTTP redirect working"
else
    print_warning "HTTP redirect may not be working"
fi

# Test HTTPS
echo -n "Testing HTTPS... "
if curl -s -k -I https://${DOMAIN} | grep -q "200\|301\|302"; then
    print_success "HTTPS is working"
else
    print_warning "HTTPS may not be working properly"
fi

# Final summary
echo ""
echo "=================================================="
echo "🎉 Setup Complete!"
echo "=================================================="
echo ""
echo "Your FastFoodie backend is now accessible at:"
echo "  🌐 https://${DOMAIN}"
echo "  📚 API Docs: https://${DOMAIN}/docs"
echo ""
echo "Next steps:"
echo "  1. Test API: curl https://${DOMAIN}/docs"
echo "  2. Update mobile apps to use https://${DOMAIN}"
echo "  3. Monitor logs: sudo tail -f /var/log/nginx/dharaidelivery-error.log"
echo ""
echo "Useful commands:"
echo "  • Reload nginx: sudo systemctl reload nginx"
echo "  • View logs: sudo tail -f /var/log/nginx/dharaidelivery-access.log"
echo "  • Renew SSL: sudo certbot renew"
echo "  • Test config: sudo nginx -t"
echo ""
print_success "All done! 🚀"
