-- =============================================
-- ALIANZA SEARCH READINESS — SUPABASE SCHEMA
-- Run this in Supabase > SQL Editor > New Query
-- =============================================

-- 1. LEADS TABLE
-- One row per unique domain. Tracks repeat visitors, pipeline status, industry.
CREATE TABLE IF NOT EXISTS leads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  domain TEXT NOT NULL UNIQUE,
  business_name TEXT DEFAULT '',
  industry TEXT DEFAULT 'unknown',
  status TEXT DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'pitched', 'negotiating', 'closed_won', 'closed_lost')),
  scan_count INTEGER DEFAULT 1,
  first_seen TIMESTAMPTZ DEFAULT now(),
  last_seen TIMESTAMPTZ DEFAULT now(),
  latest_overall_score INTEGER DEFAULT 0,
  latest_seo_score INTEGER DEFAULT 0,
  latest_ai_score INTEGER DEFAULT 0,
  latest_voice_score INTEGER DEFAULT 0,
  latest_local_score INTEGER DEFAULT 0,
  notes TEXT DEFAULT '',
  assigned_to TEXT DEFAULT '',
  source TEXT DEFAULT 'scanner'
);

-- 2. SCANS TABLE
-- Every individual scan. Links to lead by domain. Full score history.
CREATE TABLE IF NOT EXISTS scans (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  report_id TEXT NOT NULL UNIQUE,
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  domain TEXT NOT NULL,
  url TEXT NOT NULL,
  final_url TEXT DEFAULT '',
  scanned_at TIMESTAMPTZ DEFAULT now(),
  response_time_ms INTEGER DEFAULT 0,
  overall_score INTEGER DEFAULT 0,
  seo_score INTEGER DEFAULT 0,
  ai_score INTEGER DEFAULT 0,
  voice_score INTEGER DEFAULT 0,
  local_score INTEGER DEFAULT 0,
  title TEXT DEFAULT '',
  meta_description TEXT DEFAULT '',
  word_count INTEGER DEFAULT 0,
  images_total INTEGER DEFAULT 0,
  images_with_alt INTEGER DEFAULT 0,
  schema_types TEXT[] DEFAULT '{}',
  is_https BOOLEAN DEFAULT false,
  has_viewport BOOLEAN DEFAULT false,
  has_canonical BOOLEAN DEFAULT false,
  has_og_tags BOOLEAN DEFAULT false,
  has_twitter_card BOOLEAN DEFAULT false,
  has_json_ld BOOLEAN DEFAULT false,
  has_local_schema BOOLEAN DEFAULT false,
  has_faq_schema BOOLEAN DEFAULT false,
  has_phone BOOLEAN DEFAULT false,
  has_address BOOLEAN DEFAULT false,
  has_maps_embed BOOLEAN DEFAULT false,
  has_contact_link BOOLEAN DEFAULT false,
  full_report JSONB DEFAULT '{}'
);

-- 3. SCAN_CHECKS TABLE
-- Every individual check from every scan. Granular data for fulfillment team.
CREATE TABLE IF NOT EXISTS scan_checks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
  report_id TEXT NOT NULL,
  domain TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('traditional_seo', 'ai_search', 'voice_search', 'local_search')),
  check_label TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pass', 'fail', 'warn')),
  detail TEXT DEFAULT '',
  fix_title TEXT DEFAULT '',
  fix_why TEXT DEFAULT '',
  impact TEXT DEFAULT '' CHECK (impact IN ('', 'High', 'Medium', 'Low')),
  checked_at TIMESTAMPTZ DEFAULT now()
);

-- 4. INDEXES for performance
CREATE INDEX IF NOT EXISTS idx_leads_domain ON leads(domain);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_last_seen ON leads(last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_leads_scan_count ON leads(scan_count DESC);
CREATE INDEX IF NOT EXISTS idx_scans_domain ON scans(domain);
CREATE INDEX IF NOT EXISTS idx_scans_report_id ON scans(report_id);
CREATE INDEX IF NOT EXISTS idx_scans_lead_id ON scans(lead_id);
CREATE INDEX IF NOT EXISTS idx_scans_scanned_at ON scans(scanned_at DESC);
CREATE INDEX IF NOT EXISTS idx_scan_checks_scan_id ON scan_checks(scan_id);
CREATE INDEX IF NOT EXISTS idx_scan_checks_domain ON scan_checks(domain);
CREATE INDEX IF NOT EXISTS idx_scan_checks_status ON scan_checks(status);

-- 5. ENABLE ROW LEVEL SECURITY (but allow all for service role)
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE scan_checks ENABLE ROW LEVEL SECURITY;

-- Allow the anon key to read/write (for CGI backend)
CREATE POLICY "Allow all access" ON leads FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON scans FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON scan_checks FOR ALL USING (true) WITH CHECK (true);
