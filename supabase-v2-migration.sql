-- =============================================
-- ALIANZA SEARCH READINESS — V2 MIGRATION
-- Run this in Supabase > SQL Editor > New Query
-- Adds: competitor tracking, PDF downloads, outreach templates
-- =============================================

-- 1. ADD NEW COLUMNS TO LEADS TABLE
-- source: 'scanner' (self-scanned) or 'competitor' (scanned by someone else)
-- scanned_by_domain: if competitor, which domain scanned them
ALTER TABLE leads ADD COLUMN IF NOT EXISTS scanned_by_domain TEXT DEFAULT '';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS outreach_self TEXT DEFAULT '';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS outreach_competitor TEXT DEFAULT '';

-- 2. ADD COMPETITOR TRACKING TO SCANS TABLE
ALTER TABLE scans ADD COLUMN IF NOT EXISTS scan_type TEXT DEFAULT 'self';
ALTER TABLE scans ADD COLUMN IF NOT EXISTS primary_domain TEXT DEFAULT '';
ALTER TABLE scans ADD COLUMN IF NOT EXISTS competitor_domain TEXT DEFAULT '';

-- 3. PDF DOWNLOADS TABLE
CREATE TABLE IF NOT EXISTS pdf_downloads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  report_id TEXT NOT NULL,
  domain TEXT DEFAULT '',
  competitor_id TEXT DEFAULT '',
  scan_type TEXT DEFAULT 'self',
  ip TEXT DEFAULT '',
  downloaded_at TIMESTAMPTZ DEFAULT now(),
  comparison_domain TEXT DEFAULT '',
  file_name TEXT DEFAULT ''
);

-- Enable RLS + allow all
ALTER TABLE pdf_downloads ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE policyname = 'Allow all access' AND tablename = 'pdf_downloads'
  ) THEN
    CREATE POLICY "Allow all access" ON pdf_downloads FOR ALL USING (true) WITH CHECK (true);
  END IF;
END $$;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_pdf_downloads_domain ON pdf_downloads(domain);
CREATE INDEX IF NOT EXISTS idx_pdf_downloads_report_id ON pdf_downloads(report_id);
CREATE INDEX IF NOT EXISTS idx_pdf_downloads_downloaded_at ON pdf_downloads(downloaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_scan_type ON scans(scan_type);
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
