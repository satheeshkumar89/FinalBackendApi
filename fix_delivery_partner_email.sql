-- Migration to add missing email column to delivery_partners table
-- Run this on EC2 database

-- Add email column (nullable to allow existing records)
ALTER TABLE delivery_partners 
ADD COLUMN email VARCHAR(255) NULL
AFTER full_name;

-- Add index on email for faster lookups (optional but recommended)
-- CREATE INDEX idx_delivery_partners_email ON delivery_partners(email);

-- Verify the change
DESCRIBE delivery_partners;

SELECT 'Migration completed successfully!' as status;
