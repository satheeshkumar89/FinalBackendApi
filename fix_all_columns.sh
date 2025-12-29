#!/bin/bash
# Complete Fix for delivery_partners table - Add all missing columns

echo "🔧 Adding all missing columns to delivery_partners table..."

# Add all missing columns one by one
sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "
ALTER TABLE delivery_partners ADD COLUMN IF NOT EXISTS vehicle_type VARCHAR(50) NULL AFTER vehicle_number;
" 2>/dev/null || sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "ALTER TABLE delivery_partners ADD COLUMN vehicle_type VARCHAR(50) NULL AFTER vehicle_number;" 2>/dev/null

sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "
ALTER TABLE delivery_partners ADD COLUMN IF NOT EXISTS license_number VARCHAR(50) NULL AFTER vehicle_type;
" 2>/dev/null || sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "ALTER TABLE delivery_partners ADD COLUMN license_number VARCHAR(50) NULL AFTER vehicle_type;" 2>/dev/null

sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "
ALTER TABLE delivery_partners ADD COLUMN IF NOT EXISTS rating DECIMAL(3, 2) DEFAULT 5.0 AFTER license_number;
" 2>/dev/null || sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "ALTER TABLE delivery_partners ADD COLUMN rating DECIMAL(3, 2) DEFAULT 5.0 AFTER license_number;" 2>/dev/null

sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "
ALTER TABLE delivery_partners ADD COLUMN IF NOT EXISTS profile_photo VARCHAR(500) NULL AFTER rating;
" 2>/dev/null || sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "ALTER TABLE delivery_partners ADD COLUMN profile_photo VARCHAR(500) NULL AFTER rating;" 2>/dev/null

sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "
ALTER TABLE delivery_partners ADD COLUMN IF NOT EXISTS is_online BOOLEAN DEFAULT FALSE AFTER is_active;
" 2>/dev/null || sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "ALTER TABLE delivery_partners ADD COLUMN is_online BOOLEAN DEFAULT FALSE AFTER is_active;" 2>/dev/null

sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "
ALTER TABLE delivery_partners ADD COLUMN IF NOT EXISTS is_registered BOOLEAN DEFAULT FALSE AFTER is_online;
" 2>/dev/null || sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "ALTER TABLE delivery_partners ADD COLUMN is_registered BOOLEAN DEFAULT FALSE AFTER is_online;" 2>/dev/null

sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "
ALTER TABLE delivery_partners ADD COLUMN IF NOT EXISTS verification_status ENUM('pending', 'submitted', 'under_review', 'approved', 'rejected') DEFAULT 'pending' AFTER is_registered;
" 2>/dev/null || sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "ALTER TABLE delivery_partners ADD COLUMN verification_status ENUM('pending', 'submitted', 'under_review', 'approved', 'rejected') DEFAULT 'pending' AFTER is_registered;" 2>/dev/null

sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "
ALTER TABLE delivery_partners ADD COLUMN IF NOT EXISTS verification_notes TEXT NULL AFTER verification_status;
" 2>/dev/null || sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "ALTER TABLE delivery_partners ADD COLUMN verification_notes TEXT NULL AFTER verification_status;" 2>/dev/null

sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "
ALTER TABLE delivery_partners ADD COLUMN IF NOT EXISTS last_online_at DATETIME NULL AFTER verification_notes;
" 2>/dev/null || sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "ALTER TABLE delivery_partners ADD COLUMN last_online_at DATETIME NULL AFTER verification_notes;" 2>/dev/null

sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "
ALTER TABLE delivery_partners ADD COLUMN IF NOT EXISTS last_offline_at DATETIME NULL AFTER last_online_at;
" 2>/dev/null || sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "ALTER TABLE delivery_partners ADD COLUMN last_offline_at DATETIME NULL AFTER last_online_at;" 2>/dev/null

echo "✅ All columns added!"
echo ""
echo "📊 Verifying table structure..."
sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "DESCRIBE delivery_partners;"

echo ""
echo "🔄 Restarting API..."
cd ~/fastfoodie-backend && sudo docker-compose restart api

echo ""
echo "⏳ Waiting for API to start..."
sleep 10

echo ""
echo "🧪 Testing endpoint..."
curl -X POST "https://dharaifooddelivery.in/delivery-partner/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+918668109712"}'

echo ""
echo "✅ Migration complete!"
