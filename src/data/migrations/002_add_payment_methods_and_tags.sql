-- Migration 002: Add Payment Methods and Tags
-- Adds payment_method and tags columns to transactions table non-destructively

ALTER TABLE transactions ADD COLUMN payment_method TEXT DEFAULT 'Cash';
ALTER TABLE transactions ADD COLUMN tags TEXT DEFAULT '';

