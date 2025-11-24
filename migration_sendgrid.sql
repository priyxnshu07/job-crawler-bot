-- Migration: Add SendGrid columns to users table
-- Run this SQL in your Render PostgreSQL database

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS sendgrid_api_key TEXT,
ADD COLUMN IF NOT EXISTS from_email TEXT;

-- Optional: Remove old SMTP columns (uncomment if you want to clean up)
-- ALTER TABLE users 
-- DROP COLUMN IF EXISTS email_smtp_server,
-- DROP COLUMN IF EXISTS email_smtp_port,
-- DROP COLUMN IF EXISTS email_username,
-- DROP COLUMN IF EXISTS email_password;
