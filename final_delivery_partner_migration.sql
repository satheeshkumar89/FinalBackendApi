-- Final Robust Migration for delivery_partners table
-- This script safely adds all columns required by the current model if they are missing.

SET @dbname = DATABASE();
SET @tablename = 'delivery_partners';

-- Procedure to add a column if it doesn't exist
DELIMITER //
CREATE PROCEDURE AddColumnIfMissing(
    IN col_name VARCHAR(255),
    IN col_def TEXT,
    IN after_col VARCHAR(255)
)
BEGIN
    IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND COLUMN_NAME = col_name
    ) THEN
        SET @sql = CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', col_name, ' ', col_def, ' AFTER ', after_col);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        SELECT CONCAT('Column ', col_name, ' added.') AS status;
    ELSE
        SELECT CONCAT('Column ', col_name, ' already exists.') AS status;
    END IF;
END //
DELIMITER ;

-- Add columns one by one in correct order
CALL AddColumnIfMissing('email', 'VARCHAR(255) NULL', 'full_name');
CALL AddColumnIfMissing('vehicle_number', 'VARCHAR(20) NULL', 'phone_number');
CALL AddColumnIfMissing('vehicle_type', 'VARCHAR(50) NULL', 'vehicle_number');
CALL AddColumnIfMissing('license_number', 'VARCHAR(50) NULL', 'vehicle_type');
CALL AddColumnIfMissing('rating', 'DECIMAL(3, 2) DEFAULT 5.0', 'license_number');
CALL AddColumnIfMissing('profile_photo', 'VARCHAR(500) NULL', 'rating');
CALL AddColumnIfMissing('is_online', 'BOOLEAN DEFAULT FALSE', 'is_active');
CALL AddColumnIfMissing('is_registered', 'BOOLEAN DEFAULT FALSE', 'is_online');
CALL AddColumnIfMissing('verification_status', "ENUM('pending', 'submitted', 'under_review', 'approved', 'rejected') DEFAULT 'pending'", 'is_registered');
CALL AddColumnIfMissing('verification_notes', 'TEXT NULL', 'verification_status');
CALL AddColumnIfMissing('last_online_at', 'DATETIME NULL', 'verification_notes');
CALL AddColumnIfMissing('last_offline_at', 'DATETIME NULL', 'last_online_at');
CALL AddColumnIfMissing('latitude', 'DECIMAL(10, 8) NULL', 'last_offline_at');
CALL AddColumnIfMissing('longitude', 'DECIMAL(11, 8) NULL', 'latitude');

-- Clean up
DROP PROCEDURE AddColumnIfMissing;

-- Verify
DESCRIBE delivery_partners;
SELECT 'Final migration completed!' AS status;
