-- Complete Migration for delivery_partners table
-- Adds all missing columns to match the current model

-- Check current structure first
SELECT 'Current table structure:' as info;
DESCRIBE delivery_partners;

-- Add missing columns (each with IF NOT EXISTS check via ALTER TABLE)
-- Note: MySQL doesn't support IF NOT EXISTS for ADD COLUMN, so we'll add them one by one

-- Add vehicle_type if missing
ALTER TABLE delivery_partners ADD COLUMN vehicle_type VARCHAR(50) NULL AFTER vehicle_number;

-- Add license_number if missing  
ALTER TABLE delivery_partners ADD COLUMN license_number VARCHAR(50) NULL AFTER vehicle_type;

-- Add rating if missing
ALTER TABLE delivery_partners ADD COLUMN rating DECIMAL(3, 2) DEFAULT 5.0 AFTER license_number;

-- Add profile_photo if missing
ALTER TABLE delivery_partners ADD COLUMN profile_photo VARCHAR(500) NULL AFTER rating;

-- Add is_online if missing
ALTER TABLE delivery_partners ADD COLUMN is_online BOOLEAN DEFAULT FALSE AFTER is_active;

-- Add is_registered if missing
ALTER TABLE delivery_partners ADD COLUMN is_registered BOOLEAN DEFAULT FALSE AFTER is_online;

-- Add verification_status if missing (using ENUM)
ALTER TABLE delivery_partners ADD COLUMN verification_status ENUM('pending', 'submitted', 'under_review', 'approved', 'rejected') DEFAULT 'pending' AFTER is_registered;

-- Add verification_notes if missing
ALTER TABLE delivery_partners ADD COLUMN verification_notes TEXT NULL AFTER verification_status;

-- Add last_online_at if missing
ALTER TABLE delivery_partners ADD COLUMN last_online_at DATETIME NULL AFTER verification_notes;

-- Add last_offline_at if missing
ALTER TABLE delivery_partners ADD COLUMN last_offline_at DATETIME NULL AFTER last_online_at;

-- Verify final structure
SELECT 'Updated table structure:' as info;
DESCRIBE delivery_partners;

SELECT 'Migration completed!' as status;
