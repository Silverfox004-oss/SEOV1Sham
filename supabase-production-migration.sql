-- supabase-production-migration.sql
-- Migration for Production Upgrade 
-- Run this in the Supabase SQL Editor

-- 1. Add IP Address for Rate Limiting
ALTER TABLE public.scans
ADD COLUMN IF NOT EXISTS ip_address TEXT;

-- 2. Add Performance Metrics (PageSpeed Insights)
ALTER TABLE public.scans
ADD COLUMN IF NOT EXISTS performance_score INTEGER,
ADD COLUMN IF NOT EXISTS lcp TEXT,
ADD COLUMN IF NOT EXISTS cls TEXT,
ADD COLUMN IF NOT EXISTS fcp TEXT;

-- 3. Create Indexes for new queries
CREATE INDEX IF NOT EXISTS idx_scans_ip_address ON public.scans(ip_address);
CREATE INDEX IF NOT EXISTS idx_scans_performance ON public.scans(performance_score);
