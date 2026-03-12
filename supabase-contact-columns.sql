-- Add contact info columns to leads table
ALTER TABLE leads ADD COLUMN IF NOT EXISTS contact_name TEXT DEFAULT '';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS contact_email TEXT DEFAULT '';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS contact_phone TEXT DEFAULT '';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS contact_role TEXT DEFAULT '';
