-- Migration to add location columns to delivery_partners table
-- This fixes the error: Unknown column 'delivery_partners.latitude' in 'SELECT'

-- Check if table exists
SELECT 'Adding latitude and longitude columns to delivery_partners...' AS status;

-- Add latitude column if it doesn't exist
SET @dbname = DATABASE();
SET @tablename = 'delivery_partners';
SET @columnname = 'latitude';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'SELECT "Column latitude already exists" AS status',
  'ALTER TABLE delivery_partners ADD COLUMN latitude DECIMAL(10, 8) NULL AFTER last_offline_at'
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add longitude column if it doesn't exist
SET @columnname = 'longitude';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  'SELECT "Column longitude already exists" AS status',
  'ALTER TABLE delivery_partners ADD COLUMN longitude DECIMAL(11, 8) NULL AFTER latitude'
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Verify final structure
DESCRIBE delivery_partners;

SELECT 'Migration completed successfully!' AS status;
