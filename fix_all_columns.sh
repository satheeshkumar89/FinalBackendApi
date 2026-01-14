#!/bin/bash
# Complete Fix for delivery_partners table - Add all missing columns including Location
# This fixes: Unknown column 'delivery_partners.latitude' in 'SELECT'

echo "🔧 Adding all missing columns to delivery_partners table..."

# Helper to run SQL one by one (to avoid stopping on errors if column already exists)
run_sql() {
    sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "$1" 2>/dev/null
}

echo "Adding vehicle_type..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN vehicle_type VARCHAR(50) NULL AFTER vehicle_number;"

echo "Adding license_number..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN license_number VARCHAR(50) NULL AFTER vehicle_type;"

echo "Adding rating..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN rating DECIMAL(3, 2) DEFAULT 5.0 AFTER license_number;"

echo "Adding profile_photo..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN profile_photo VARCHAR(500) NULL AFTER rating;"

echo "Adding is_online..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN is_online BOOLEAN DEFAULT FALSE AFTER is_active;"

echo "Adding is_registered..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN is_registered BOOLEAN DEFAULT FALSE AFTER is_online;"

echo "Adding verification_status..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN verification_status ENUM('pending', 'submitted', 'under_review', 'approved', 'rejected') DEFAULT 'pending' AFTER is_registered;"

echo "Adding verification_notes..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN verification_notes TEXT NULL AFTER verification_status;"

echo "Adding last_online_at..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN last_online_at DATETIME NULL AFTER verification_notes;"

echo "Adding last_offline_at..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN last_offline_at DATETIME NULL AFTER last_online_at;"

echo "Adding latitude..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN latitude DECIMAL(10, 8) NULL AFTER last_offline_at;"

echo "Adding longitude..."
run_sql "ALTER TABLE delivery_partners ADD COLUMN longitude DECIMAL(11, 8) NULL AFTER latitude;"

echo "✅ All columns checked/added!"
echo ""
echo "📊 Verifying table structure..."
sudo docker exec fastfoodie_mysql mysql -u root -prootpassword fastfoodie -e "DESCRIBE delivery_partners;"

echo ""
echo "🔄 Restarting API..."
cd ~/fastfoodie-backend && sudo docker-compose restart api

echo ""
echo "⏳ Waiting for API to start..."
sleep 5

echo ""
echo "🧪 Testing endpoint..."
curl -X POST "https://dharaifooddelivery.in/delivery-partner/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+918668109712"}'

echo ""
echo "✅ Migration complete!"
