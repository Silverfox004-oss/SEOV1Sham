
1. How to get VALUESERP_API_KEY
This is your ValueSerp API key for SERP tracking.

Go to ValueSerp: Visit https://app.valueserp.com/
Sign Up: Create a free account (100 free trial requests included).
Get API Key: After signing in, your API key is displayed on the dashboard.
This is your VALUESERP_API_KEY.

(Note: Google Custom Search JSON API has been deprecated. We now use ValueSerp for all SERP analysis.)







# 🚀 Alianza Connects Search Readiness Platform - Production Upgrade Guide

**For: Antigravity Claude Sonnet 4.6**  
**Project:** Search Readiness Scanner Upgrade  
**Current Status:** Functional Prototype (7/10)  
**Target Status:** Production-Ready Professional Application (9.5/10)  
**Target Cost:** $0.03-0.05 per scan  
**Use Case:** Internal tool for Alianza Connects clients (NOT public SaaS)  
**Architecture:** Python 3 stdlib-only CGI + Supabase + S3/CloudFront + LLM APIs

---

## 🔌 REQUIRED API & PLATFORM INTEGRATIONS

**Complete this checklist to ensure all necessary platforms are integrated:**

### ✅ **Core Infrastructure (Already Configured)**
- [x] **Supabase** - PostgreSQL database + REST API
  - Purpose: Store leads, scans, checks, contact info
  - Cost: $0/month (Free tier) or $25/month (Pro - recommended for production)
  - Status: ✅ Already integrated

- [x] **Cloudflare R2** - Static file hosting + CDN
  - Purpose: Host frontend (HTML/CSS/JS), serve PDF reports
  - Cost: $0 (10GB storage + 10M ops free tier covers your app)
  - Status: need to setup

- [x] **Cloudflare Workers + R2** - Serverless backend replacement
  - Purpose: Run all py logic (form processing → SEO analysis → 
  - report generation to R2)
  - Cost: $0 (100K requests/day free)
  - Status: 🔄 Replace CGI server - Convert Python → JS Worker (1hr)

### 🔄 **APIs to Integrate (REQUIRED)**

- [ ] **Google PageSpeed Insights API v5**
  - **Purpose:** Real performance scores (Performance, Accessibility, Best Practices, SEO)
  - **What it provides:** Core Web Vitals (LCP, FID, CLS), Lighthouse scores
  - **Cost:** FREE (25,000 requests/day, no API key required)
  - **Cost per scan:** $0.00 (with smart caching: 80% cache hit rate)
  - **API Endpoint:** `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`
  - **Integration Priority:** 🔴 HIGH - Major competitive advantage
  - **Setup Steps:**
    1. No API key needed for basic use
    2. Optional: Get API key from Google Cloud Console for higher quotas
    3. Implement in `analyze.py` as `get_pagespeed_scores(url)`

- [ ] **OpenAI API (GPT-4o-mini)** - For E-E-A-T & Content Quality Analysis
  - **Purpose:** AI-powered content quality scoring, E-E-A-T evaluation, readability analysis, comparison and all other where its needed
  - **What it analyzes:**
    - Expertise signals (author credentials, citations, depth)
    - Experience indicators (first-hand accounts, case studies)
    - Authoritativeness (brand mentions, industry terminology)
    - Trustworthiness (privacy policy, contact info, security)
    - Content tone, clarity, and conversational quality
  - **Model:** gpt-4o-mini (cheap + fast)
  - **Cost:** $0.150 per 1M input tokens, $0.600 per 1M output tokens
  - **Cost per scan:** ~$0.008-0.012 (5,000 tokens input + 500 tokens output)
  - **API Endpoint:** `https://api.openai.com/v1/chat/completions`
  - **Integration Priority:** 🔴 CRITICAL - Your differentiator vs competitors
  - **Setup Steps:**
    1. Get API key from https://platform.openai.com/api-keys
    2. Set environment variable: `OPENAI_API_KEY=sk-...`
    3. Implement in `analyze.py` as `analyze_content_quality_llm()`

- [ ] **Anthropic Claude API (Claude Sonnet 4)** - Backup/Alternative for E-E-A-T Analysis
  - **Purpose:** Alternative LLM for content analysis (optional backup if OpenAI fails)
  - **What it analyzes:** Same as OpenAI (E-E-A-T, tone, clarity)
  - **Model:** claude-sonnet-4-20250514
  - **Cost:** $3.00 per 1M input tokens, $15.00 per 1M output tokens
  - **Cost per scan:** ~$0.015-0.025 (more expensive than GPT-4o-mini)
  - **API Endpoint:** `https://api.anthropic.com/v1/messages`
  - **Integration Priority:** 🟡 OPTIONAL - Use only if OpenAI rate-limited
  - **Setup Steps:**
    1. Get API key from https://console.anthropic.com/
    2. Set environment variable: `ANTHROPIC_API_KEY=sk-ant-...`
    3. Implement as fallback in `analyze_content_quality_llm()`

- [ ] **Google Custom Search JSON API** - For SERP Position Tracking
  - **Purpose:** Check where client's website ranks for target keywords and what it can rank or other possible features in can provide for this platform report
  - **What it provides:**
    - Search engine ranking positions (1-10 or "not ranked")
    - Featured snippet detection
    - Competitor comparison (who ranks above/below)
    - Local pack presence
  - **Why it's critical for your clients:**
    - Shows actual search visibility (not just "SEO score")
    - Identifies ranking opportunities ("You're #11 - one spot from page 1!")
    - Proves ROI over time ("Moved from #15 to #3 in 3 months")
    - Competitive intelligence ("Competitor X ranks #1 because they have FAQ schema")
  - **Cost:** FREE (100 searches/day) or $5 per 1,000 searches
  - **Cost per scan:** ~$0.01 (4 queries × $2.50/1000)
  - **API Endpoint:** `https://api.valueserp.com/search`
  - **Integration Priority:** 🔴 HIGH - Default feature for all client reports
  - **Setup Steps:**
    1. Sign up at https://app.valueserp.com/
    2. Get API key from dashboard
    3. Set environment variable:
       - `VALUESERP_API_KEY=your_api_key_here`

- [ ] **Alternative SERP API: ValueSERP** (If Google CSE quota insufficient)
  - **Purpose:** More robust SERP tracking with better local pack detection
  - **Advantages over Google CSE:**
    - Returns local pack results (Google CSE doesn't)
    - Includes AI Overviews/Featured Snippets
    - More detailed competitor data
  - **Cost:** $30/month for 5,000 searches or pay-as-you-go at $0.006/search
  - **Cost per scan:** ~$0.018-0.030 (3-5 keyword checks)
  - **API Endpoint:** `https://api.valueserp.com/search`
  - **Integration Priority:** 🟢 OPTIONAL - Upgrade if Google CSE limited
  - **Setup Steps:**
    1. Sign up at https://www.valueserp.com/
    2. Get API key from dashboard
    3. Set environment variable: `VALUESERP_API_KEY=...`

### 📊 **Optional Analytics & Monitoring**

- [ ] **Sentry** - Error tracking and monitoring
  - **Purpose:** Track bugs, API failures, crashes in production
  - **Cost:** FREE (5,000 events/month)
  - **Cost per scan:** $0.00
  - **Setup:** https://sentry.io/signup/
  - **Integration Priority:** 🟢 NICE TO HAVE

- [ ] **UptimeRobot** - Uptime monitoring
  - **Purpose:** Alert if scanner goes down
  - **Cost:** FREE (50 monitors)
  - **Setup:** https://uptimerobot.com/
  - **Integration Priority:** 🟢 NICE TO HAVE

---

## 💰 COST BREAKDOWN PER SCAN

**Target: $0.03-0.05 per scan**

### Per-Scan Cost Analysis:

```
🟢 FREE (with smart caching):
├─ PageSpeed Insights API:        $0.000  (free tier, cached 80% of time)
├─ Supabase database queries:      $0.000  (free tier or negligible in Pro)
└─ CGI compute:                     $0.000  (fixed monthly cost)

💰 PAID APIs:
├─ OpenAI GPT-4o-mini (E-E-A-T):   $0.010  (5K input + 500 output tokens)
├─ Google Custom Search (SERP):    $0.020  (4 keywords × $0.005 each)
└─ Cache miss overhead:            +$0.005 (20% of scans hit PageSpeed API at peak)

TOTAL PER SCAN:                    $0.035  ✅ Within target!

With optimizations:
- Smart caching (80% hit rate):    $0.030
- Batch processing:                $0.028
- Claude fallback only:            $0.032  (if OpenAI down)
```

### Monthly Cost Projections:

```
At 100 scans/month:
  API costs:        $3.00-3.50
  Infrastructure:   $5-10 (Supabase Pro + Cloudfare)
  Total:           ~$10-20/month

At 500 scans/month:s
  API costs:        $10-15.50
  Infrastructure:   $5-10
  Total:           ~$20-25/month

At 1,000 scans/month:
  API costs:        $30-35
  Infrastructure:   $5-10
  Total:           ~$30-35/month max
```

**Note:** All infrastructure costs are FIXED - only API costs scale with usage.

---

## 📊 CURRENT STATE ANALYSIS

### ✅ What's Working (Keep These)
- **Database Schema:** Excellent (Supabase + SQLite fallback)
- **PDF Reports:** Professional quality, ready for production
- **Scoring Engine:** Accurate (66% SEO, 50% AI, 55% Voice, 32% Local for childrensrelief.org test)
- **Frontend UX:** Clean, responsive, good loading states
- **Architecture:** Smart (Python stdlib only, no external dependencies)

### ❌ Critical Production Blockers
1. **fetch_page():** Single User-Agent, no retry logic → 40% failure rate
2. **No Rate Limiting:** Vulnerable to abuse, unlimited scans
3. **No Caching:** Wastes resources, slow for repeat scans
4. **No Performance Metrics:** Missing PageSpeed/Core Web Vitals
5. **Basic GEO Scoring:** Lacks entity extraction, Q&A detection, voice optimization

### 🎯 Target Metrics
- **Success Rate:** 40% → 92% (enhanced fetch)
- **API Costs:** Reduce 80% (smart caching)
- **Competitive Edge:** Add PageSpeed API, enhanced GEO, SERP tracking

---

## 🏗️ IMPLEMENTATION PLAN

### **PHASE 1: CRITICAL FIXES (Week 1)**
**Priority:** 🔴 MUST COMPLETE BEFORE LAUNCH

#### Task 1.1: Enhanced fetch_page() with Anti-Bot Protection
**File:** `analyze.py` (Lines ~680-720)  
**Current Problem:** Static User-Agent, no retries, fails on Cloudflare/bot detection  
**Solution:** User-Agent rotation, exponential backoff, SSL error handling

**Implementation:**
```python
# REPLACE EXISTING fetch_page() FUNCTION WITH THIS:

def fetch_page(url, timeout=15):
    """
    Enhanced page fetching with anti-bot protection and retry logic.
    
    NEW FEATURES:
    - User-Agent rotation (4 different browsers)
    - Exponential backoff retry (3 attempts: 1s → 2s → 4s delays)
    - SSL error handling (try secure first, fallback to relaxed)
    - HTTP 403/429/503 retry logic
    - Random jitter to avoid bot detection patterns
    
    Args:
        url: Target URL to fetch
        timeout: Request timeout in seconds (default: 15)
    
    Returns:
        tuple: (html, response_time_ms, headers_dict, final_url)
    
    Raises:
        ValueError: If all 3 retry attempts fail
    """
    import random
    import time
    
    # User-Agent rotation - defeats basic bot detection
    # Using real Chrome/Firefox/Safari fingerprints from 2024-2026
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
    ]
    
    # Enhanced headers - mimic real browser behavior
    headers = {
        'User-Agent': random.choice(user_agents),  # Randomized each request
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    # Retry loop with exponential backoff
    for attempt in range(3):
        try:
            # Build request
            req = urllib.request.Request(url, headers=headers)
            start = time.time()
            
            # Try with default SSL verification (secure)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                html_bytes = response.read(800000)  # Limit to 800KB
                elapsed = time.time() - start
                
                # Decode HTML with encoding detection
                content_type = response.headers.get("Content-Type", "")
                encoding = "utf-8"
                if "charset=" in content_type:
                    encoding = content_type.split("charset=")[-1].strip().split(";")[0]
                
                try:
                    html = html_bytes.decode(encoding, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    html = html_bytes.decode("utf-8", errors="replace")
                
                return html, int(elapsed * 1000), dict(response.headers), response.url
                
        except ssl.SSLError as e:
            # SSL error - try with relaxed SSL verification
            if attempt < 2:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                req = urllib.request.Request(url, headers=headers)
                start = time.time()
                
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
                    html_bytes = response.read(800000)
                    elapsed = time.time() - start
                    html = html_bytes.decode("utf-8", errors="replace")
                    return html, int(elapsed * 1000), dict(response.headers), response.url
            else:
                raise ValueError(f"SSL Error after {attempt + 1} attempts: {str(e)}")
                
        except urllib.error.HTTPError as e:
            # Retry on 403 (Forbidden), 429 (Rate Limit), 503 (Service Unavailable)
            if attempt < 2 and e.code in (403, 429, 503):
                # Exponential backoff with random jitter
                # Attempt 1: 1-2s, Attempt 2: 2-3s, Attempt 3: 4-5s
                wait_time = (2 ** attempt) + random.random()
                time.sleep(wait_time)
                continue  # Retry with different User-Agent
            else:
                raise ValueError(f"HTTP {e.code} after {attempt + 1} attempts: {e.reason}")
                
        except urllib.error.URLError as e:
            # Network errors - retry with backoff
            if attempt < 2:
                wait_time = (2 ** attempt) + random.random()
                time.sleep(wait_time)
                continue
            else:
                raise ValueError(f"Network Error after {attempt + 1} attempts: {str(e)}")
        
        except Exception as e:
            # Unexpected errors
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            else:
                raise ValueError(f"Unexpected error after {attempt + 1} attempts: {str(e)}")
    
    # All retries failed
    raise ValueError("Failed to fetch page after 3 attempts with exponential backoff")
```

**Testing Requirements:**
- Test on 50 different sites (including Cloudflare-protected sites)
- Verify retry logic triggers on 403/429 errors
- Confirm User-Agent rotation (check request logs)
- Success rate should increase from 40% → 90%+

**Expected Impact:**
- ✅ 40% → 92% success rate
- ✅ Handles Cloudflare basic protection
- ✅ Graceful SSL error handling
- ✅ Better bot evasion

---

#### Task 1.2: Rate Limiting System
**File:** `analyze.py` (Add new functions + modify CGI handler)  
**Current Problem:** No limits, vulnerable to abuse, unlimited API costs  
**Solution:** IP-based rate limiting (5 scans per IP per 24 hours)

**Database Migration First:**
```sql
-- Run in Supabase SQL Editor:
-- File: supabase-rate-limit-migration.sql

-- Add IP address tracking to scans table
ALTER TABLE scans ADD COLUMN IF NOT EXISTS ip_address TEXT DEFAULT '';

-- Create index for fast IP lookups
CREATE INDEX IF NOT EXISTS idx_scans_ip_address ON scans(ip_address);

-- Verify migration
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'scans' AND column_name = 'ip_address';
```

**Implementation:**
```python
# ADD THIS FUNCTION TO analyze.py (around line 200, after supabase helpers)

def check_rate_limit(ip_address, max_scans=5, window_hours=24):
    """
    Enforce rate limiting: max 5 scans per IP per 24 hours.
    
    Args:
        ip_address: Client IP address
        max_scans: Maximum allowed scans (default: 5)
        window_hours: Time window in hours (default: 24)
    
    Returns:
        dict: {
            'allowed': bool,
            'remaining': int (scans left),
            'reset_time': datetime or None,
            'message': str (user-friendly message)
        }
    """
    from datetime import datetime, timedelta, timezone
    
    # Calculate cutoff time (24 hours ago)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    cutoff_iso = cutoff.isoformat()
    
    # Query recent scans from this IP
    try:
        recent_scans = supabase_select('scans', {
            'ip_address': f'eq.{ip_address}',
            'scanned_at': f'gte.{cutoff_iso}',
            'select': 'scanned_at'
        })
        
        if recent_scans is None:
            recent_scans = []
    except Exception:
        # Database error - allow scan but log
        return {
            'allowed': True,
            'remaining': max_scans,
            'reset_time': None,
            'message': 'Rate limit check skipped (database error)'
        }
    
    scan_count = len(recent_scans)
    
    if scan_count >= max_scans:
        # Find when oldest scan will expire
        oldest_scan = min(recent_scans, key=lambda x: x['scanned_at'])
        oldest_time = datetime.fromisoformat(oldest_scan['scanned_at'].replace('Z', '+00:00'))
        reset_time = oldest_time + timedelta(hours=window_hours)
        
        hours_until_reset = (reset_time - datetime.now(timezone.utc)).total_seconds() / 3600
        
        return {
            'allowed': False,
            'remaining': 0,
            'reset_time': reset_time,
            'message': f'Daily scan limit reached. Resets in {int(hours_until_reset)} hours.'
        }
    
    return {
        'allowed': True,
        'remaining': max_scans - scan_count,
        'reset_time': None,
        'message': f'{max_scans - scan_count} scans remaining today'
    }


def get_client_ip():
    """
    Extract client IP address from CGI environment.
    
    Checks for:
    1. X-Forwarded-For (if behind proxy/CDN)
    2. X-Real-IP (nginx proxy)
    3. REMOTE_ADDR (direct connection)
    
    Returns:
        str: Client IP address or 'unknown'
    """
    # Check for proxy headers first (CloudFront, nginx, etc.)
    forwarded = os.environ.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        # X-Forwarded-For can be comma-separated list
        # First IP is the original client
        return forwarded.split(',')[0].strip()
    
    # Check X-Real-IP (nginx)
    real_ip = os.environ.get('HTTP_X_REAL_IP', '')
    if real_ip:
        return real_ip
    
    # Fallback to direct connection IP
    return os.environ.get('REMOTE_ADDR', 'unknown')
```

**Modify CGI Handler:**
```python
# FIND THE MAIN CGI HANDLER (around line 1800-2000)
# ADD RATE LIMITING CHECK BEFORE RUN_ANALYSIS

# In the "if method == 'POST':" section, add this BEFORE running analysis:

# Extract client IP
client_ip = get_client_ip()

# Check rate limit
rate_limit = check_rate_limit(client_ip)

if not rate_limit['allowed']:
    # Return rate limit error
    result = {
        'error': 'rate_limit_exceeded',
        'message': rate_limit['message'],
        'remaining': 0,
        'reset_time': rate_limit['reset_time'].isoformat() if rate_limit['reset_time'] else None
    }
    print("Content-Type: application/json")
    print()
    print(json.dumps(result, indent=2))
    sys.exit(0)

# If allowed, continue with analysis...
# Make sure to pass ip_address to run_analysis and save it in scans table
```

**Update run_analysis() to accept and store IP:**
```python
# MODIFY run_analysis() signature (around line 900):

def run_analysis(url, scan_type="self", primary_domain=None, competitor_domain=None,
                 competitor_result=None, contact_name="", contact_email="",
                 contact_phone="", contact_role="", ip_address="unknown"):  # ADD THIS
    """Main analysis function. Returns scores and checks."""
    
    # ... existing code ...
    
    # IMPORTANT: Make sure ip_address is passed to sync_to_supabase()
    # Find the sync_to_supabase() call and add ip_address parameter


# MODIFY sync_to_supabase() to store IP (around line 300):

def sync_to_supabase(result, scan_type="self", primary_domain=None, 
                     competitor_domain=None, contact_name="", contact_email="",
                     contact_phone="", contact_role="", ip_address="unknown"):  # ADD THIS
    """Write scan results to Supabase."""
    
    # ... existing code ...
    
    # When inserting scan, add ip_address:
    scan_data = {
        "report_id": report_id,
        "lead_id": lead_record[0]["id"],
        "domain": domain,
        "url": result["url"],
        # ... other fields ...
        "ip_address": ip_address,  # ADD THIS LINE
        # ... rest of fields ...
    }
```

**Testing Requirements:**
- Make 6 scans from same IP - verify 6th is blocked
- Test with different IPs - verify independent limits
- Test CloudFront X-Forwarded-For header parsing
- Verify reset time calculation

**Expected Impact:**
- ✅ Prevents abuse (max 5 scans/IP/day)
- ✅ Protects API budgets
- ✅ Fair usage for legitimate users

---

#### Task 1.3: Smart Caching System
**File:** `analyze.py` (Add new functions)  
**Current Problem:** Every scan fetches fresh, wastes API calls, slow UX  
**Solution:** Return cached results if scan is <24hr old (configurable by score)

**Implementation:**
```python
# ADD THESE FUNCTIONS TO analyze.py (around line 250, after rate limiting)

def should_rescan(url, hours=24):
    """
    Determine if URL needs rescanning based on:
    1. Time since last scan
    2. Previous score (poor scores get rescanned faster)
    
    Args:
        url: URL to check
        hours: Default cache window (default: 24)
    
    Returns:
        dict: {
            'needs_rescan': bool,
            'reason': str,
            'last_scan': datetime or None,
            'cached_report_id': str or None
        }
    """
    from datetime import datetime, timedelta, timezone
    
    # Query most recent scan for this URL
    try:
        recent_scans = supabase_select('scans', {
            'url': f'eq.{url}',
            'order': 'scanned_at.desc',
            'limit': '1',
            'select': 'report_id,scanned_at,overall_score,full_report'
        })
        
        if not recent_scans or recent_scans is None:
            return {
                'needs_rescan': True,
                'reason': 'Never scanned before',
                'last_scan': None,
                'cached_report_id': None
            }
        
        recent = recent_scans[0]
        scan_time = datetime.fromisoformat(recent['scanned_at'].replace('Z', '+00:00'))
        age_hours = (datetime.now(timezone.utc) - scan_time).total_seconds() / 3600
        overall_score = recent.get('overall_score', 0)
        
        # Dynamic cache window based on score
        if overall_score < 50:
            cache_window = 12  # Poor sites: rescan after 12 hours
            score_category = 'poor'
        elif overall_score < 70:
            cache_window = 24  # Mediocre sites: rescan after 24 hours
            score_category = 'mediocre'
        else:
            cache_window = 72  # Good sites: rescan after 3 days
            score_category = 'good'
        
        if age_hours < cache_window:
            return {
                'needs_rescan': False,
                'reason': f'Recent scan ({int(age_hours)}h ago, score: {overall_score}, {score_category})',
                'last_scan': scan_time,
                'cached_report_id': recent['report_id'],
                'cached_report': recent.get('full_report', {})
            }
        
        return {
            'needs_rescan': True,
            'reason': f'Cache expired ({int(age_hours)}h > {cache_window}h window for {score_category} sites)',
            'last_scan': scan_time,
            'cached_report_id': None
        }
        
    except Exception as e:
        # Database error - proceed with scan
        return {
            'needs_rescan': True,
            'reason': f'Cache check failed: {str(e)}',
            'last_scan': None,
            'cached_report_id': None
        }


def get_cached_report(report_id):
    """
    Retrieve full cached report by report_id.
    
    Args:
        report_id: Report ID from scans table
    
    Returns:
        dict: Full report JSON or None
    """
    try:
        scans = supabase_select('scans', {
            'report_id': f'eq.{report_id}',
            'select': 'full_report'
        })
        
        if scans and len(scans) > 0:
            return scans[0].get('full_report', {})
        
        return None
    except Exception:
        return None
```

**Modify CGI Handler to Use Cache:**
```python
# IN THE POST HANDLER (around line 1850), ADD CACHE CHECK BEFORE run_analysis():

# Parse request body
body = sys.stdin.read()
payload = json.loads(body) if body else {}
url = payload.get('url', '')
contact_name = payload.get('contact_name', '')
contact_email = payload.get('contact_email', '')
# ... other fields ...

# NEW: Check cache before expensive analysis
cache_check = should_rescan(url)

if not cache_check['needs_rescan']:
    # Return cached report
    cached_report = cache_check.get('cached_report', {})
    
    if cached_report:
        # Add cache metadata
        cached_report['from_cache'] = True
        cached_report['cache_age_hours'] = int(
            (datetime.now(timezone.utc) - cache_check['last_scan']).total_seconds() / 3600
        )
        cached_report['cache_reason'] = cache_check['reason']
        
        result = cached_report
    else:
        # Cache metadata exists but report missing - rescan
        result = run_analysis(url, contact_name=contact_name, ...)
else:
    # Cache miss or expired - run fresh analysis
    result = run_analysis(url, contact_name=contact_name, ...)
    result['from_cache'] = False
```

**Frontend Update (app.js):**
```javascript
// FIND THE renderDashboard() FUNCTION
// ADD CACHE INDICATOR IF from_cache = true

if (data.from_cache) {
    // Show cache notice at top of dashboard
    const cacheNotice = `
        <div style="background: rgba(59, 130, 246, 0.1); 
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    padding: 12px 16px; 
                    border-radius: 8px; 
                    margin-bottom: 20px;
                    font-size: 14px;
                    color: #3B82F6;">
            ℹ️ <strong>Cached Results</strong> - 
            This report is ${data.cache_age_hours} hours old. 
            ${data.cache_reason || 'Using recent scan to save time.'}
        </div>
    `;
    
    // Insert at top of dashboard
    dashboard.insertAdjacentHTML('afterbegin', cacheNotice);
}
```

**Testing Requirements:**
- Scan same URL twice within 1 hour - verify second returns cache
- Scan poor site (score <50) - verify 12hr cache window
- Scan good site (score 70+) - verify 72hr cache window
- Test cache expiration logic

**Expected Impact:**
- ✅ 80% reduction in API calls
- ✅ <1s response for cached scans (vs 5-8s fresh)
- ✅ Lower costs when PageSpeed API added

---

### **PHASE 2: PERFORMANCE METRICS (Week 2)**
**Priority:** 🟡 HIGH VALUE - Major competitive advantage

#### Task 2.1: Google PageSpeed Insights API Integration
**File:** `analyze.py` (Add new functions)  
**Value:** Real performance data (competitors don't have this)

**Implementation:**
```python
# ADD THIS FUNCTION TO analyze.py (around line 800, before run_analysis)

def get_pagespeed_scores(url, strategy='mobile'):
    """
    Fetch real performance scores from Google PageSpeed Insights API.
    
    API: FREE (25,000 requests/day, no API key required for basic use)
    Docs: https://developers.google.com/speed/docs/insights/v5/get-started
    
    Args:
        url: Target URL to analyze
        strategy: 'mobile' or 'desktop' (default: mobile)
    
    Returns:
        dict: {
            'performance': int (0-100),
            'accessibility': int (0-100),
            'best_practices': int (0-100),
            'seo': int (0-100),
            'fcp': float (First Contentful Paint in seconds),
            'lcp': float (Largest Contentful Paint in seconds),
            'cls': float (Cumulative Layout Shift),
            'tti': float (Time to Interactive in seconds),
            'speed_index': float (Speed Index in seconds)
        } or None on error
    """
    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    # Build query parameters
    params = {
        'url': url,
        'strategy': strategy,
        'category': ['performance', 'accessibility', 'best-practices', 'seo']
    }
    
    try:
        # Build full URL
        query_string = urllib.parse.urlencode(params, doseq=True)
        full_url = f"{api_url}?{query_string}"
        
        # Make request (30s timeout - PageSpeed can be slow)
        req = urllib.request.Request(full_url)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
        
        # Extract category scores
        categories = data.get('lighthouseResult', {}).get('categories', {})
        audits = data.get('lighthouseResult', {}).get('audits', {})
        
        # Parse scores (multiply by 100 to get 0-100 range)
        performance = int(categories.get('performance', {}).get('score', 0) * 100)
        accessibility = int(categories.get('accessibility', {}).get('score', 0) * 100)
        best_practices = int(categories.get('best-practices', {}).get('score', 0) * 100)
        seo = int(categories.get('seo', {}).get('score', 0) * 100)
        
        # Extract Core Web Vitals (convert milliseconds to seconds)
        fcp = audits.get('first-contentful-paint', {}).get('numericValue', 0) / 1000
        lcp = audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000
        cls = audits.get('cumulative-layout-shift', {}).get('numericValue', 0)
        tti = audits.get('interactive', {}).get('numericValue', 0) / 1000
        speed_index = audits.get('speed-index', {}).get('numericValue', 0) / 1000
        
        return {
            'performance': performance,
            'accessibility': accessibility,
            'best_practices': best_practices,
            'seo': seo,
            'fcp': round(fcp, 2),
            'lcp': round(lcp, 2),
            'cls': round(cls, 3),
            'tti': round(tti, 2),
            'speed_index': round(speed_index, 2),
            'strategy': strategy,
            'api': 'PageSpeed Insights v5'
        }
        
    except urllib.error.HTTPError as e:
        # PageSpeed API error (rate limit, invalid URL, etc.)
        return None
        
    except Exception as e:
        # Network error, timeout, or parsing error
        return None


def estimate_performance_score(html, response_time_ms, parser):
    """
    Fallback performance estimation when PageSpeed API fails or is unavailable.
    
    Uses heuristics based on:
    - Response time (from fetch_page)
    - HTML size
    - Resource count (scripts, images)
    - Render-blocking resources
    
    Args:
        html: Raw HTML string
        response_time_ms: Response time in milliseconds
        parser: PageParser instance with image counts, etc.
    
    Returns:
        dict: Estimated scores (0-100)
    """
    score = 100
    warnings = []
    
    # 1. Response time penalty
    if response_time_ms > 3000:  # 3+ seconds
        score -= 30
        warnings.append(f"Slow response time: {response_time_ms}ms")
    elif response_time_ms > 1500:  # 1.5-3 seconds
        score -= 15
        warnings.append(f"Moderate response time: {response_time_ms}ms")
    
    # 2. HTML size penalty
    html_size = len(html)
    if html_size > 2_000_000:  # 2MB+
        score -= 20
        warnings.append(f"Large HTML: {html_size / 1_000_000:.1f}MB")
    elif html_size > 1_000_000:  # 1-2MB
        score -= 10
        warnings.append(f"Large HTML: {html_size / 1_000_000:.1f}MB")
    
    # 3. Script count (blocks rendering)
    script_count = html.count('<script')
    if script_count > 20:
        score -= 15
        warnings.append(f"Many scripts: {script_count}")
    elif script_count > 10:
        score -= 10
        warnings.append(f"Moderate scripts: {script_count}")
    
    # 4. Render-blocking resources in <head>
    head_section = html.split('</head>')[0] if '</head>' in html else html[:5000]
    blocking_scripts = head_section.count('<script src')
    if blocking_scripts > 5:
        score -= 10
        warnings.append(f"Render-blocking scripts in head: {blocking_scripts}")
    
    # 5. Image optimization
    if parser.images_total > 30 and 'loading="lazy"' not in html:
        score -= 10
        warnings.append(f"Many images without lazy loading: {parser.images_total}")
    
    # 6. Check for performance optimizations
    if 'preload' in html or 'prefetch' in html:
        score += 5  # Bonus for resource hints
    
    if 'async' in html or 'defer' in html:
        score += 5  # Bonus for async scripts
    
    return {
        'estimated_performance': max(0, min(100, score)),
        'warnings': warnings,
        'method': 'heuristic_estimation',
        'confidence': 'medium'
    }
```

**Integrate into run_analysis():**
```python
# IN run_analysis() FUNCTION (around line 950), ADD AFTER HTML PARSING:

# Fetch PageSpeed scores (try API first, fallback to estimation)
pagespeed = get_pagespeed_scores(url, strategy='mobile')

if pagespeed:
    # API succeeded - use real data
    performance_data = {
        'source': 'pagespeed_api',
        'performance_score': pagespeed['performance'],
        'accessibility_score': pagespeed['accessibility'],
        'best_practices_score': pagespeed['best_practices'],
        'seo_score_api': pagespeed['seo'],  # Different from our SEO score
        'core_web_vitals': {
            'lcp': pagespeed['lcp'],
            'fcp': pagespeed['fcp'],
            'cls': pagespeed['cls'],
            'tti': pagespeed['tti'],
            'speed_index': pagespeed['speed_index']
        },
        'passes_cwv': (
            pagespeed['lcp'] <= 2.5 and 
            pagespeed['cls'] <= 0.1
        )
    }
else:
    # API failed - use estimation
    estimated = estimate_performance_score(html, response_time, parser)
    performance_data = {
        'source': 'estimation',
        'performance_score': estimated['estimated_performance'],
        'warnings': estimated['warnings'],
        'note': 'PageSpeed API unavailable - using heuristic estimation'
    }

# Add to result
result['performance'] = performance_data
```

**Update Database Schema:**
```sql
-- Run in Supabase SQL Editor:
-- File: supabase-performance-migration.sql

-- Add performance columns to scans table
ALTER TABLE scans ADD COLUMN IF NOT EXISTS performance_score INTEGER DEFAULT 0;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS accessibility_score INTEGER DEFAULT 0;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS best_practices_score INTEGER DEFAULT 0;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS lcp DECIMAL(5,2) DEFAULT 0;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS cls DECIMAL(5,3) DEFAULT 0;
ALTER TABLE scans ADD COLUMN IF NOT EXISTS fcp DECIMAL(5,2) DEFAULT 0;

-- Create index for performance queries
CREATE INDEX IF NOT EXISTS idx_scans_performance ON scans(performance_score);
```

**Testing Requirements:**
- Test PageSpeed API on 10 URLs - verify scores match Google's tool
- Test fallback estimation when API times out
- Verify Core Web Vitals calculation
- Test caching prevents duplicate API calls

**Expected Impact:**
- ✅ Real performance data (competitors only estimate)
- ✅ Core Web Vitals = Google ranking factor
- ✅ $0 API cost with smart caching (25K free/day)

---

#### Task 2.2: LLM-Powered E-E-A-T & GEO Analysis (HYBRID APPROACH)
**File:** `analyze.py` (Replace basic checks with LLM analysis + heuristics)  
**Value:** AI-powered content quality analysis (your competitive edge)

**HYBRID APPROACH:** Combine heuristic checks (fast, free) with LLM analysis (deep, accurate)

**Implementation:**
```python
# ADD THESE FUNCTIONS TO analyze.py (around line 850)

def analyze_content_quality_llm(url, content, parser, schema):
    """
    LLM-powered content quality and E-E-A-T analysis.
    
    Uses OpenAI GPT-4o-mini (primary) or Claude Sonnet 4 (fallback)
    to evaluate content against Google's E-E-A-T guidelines.
    
    E-E-A-T = Experience, Expertise, Authoritativeness, Trustworthiness
    
    Args:
        url: Website URL being analyzed
        content: Main text content (first 5000 chars)
        parser: PageParser instance with HTML metadata
        schema: Schema.org analysis results
    
    Returns:
        dict: {
            'eeat_score': int (0-100),
            'experience_score': int (0-100),
            'expertise_score': int (0-100),
            'authoritativeness_score': int (0-100),
            'trustworthiness_score': int (0-100),
            'readability_score': int (0-100),
            'geo_readiness': int (0-100),
            'voice_optimization': int (0-100),
            'tone_quality': str ('professional', 'conversational', 'technical', etc.),
            'strengths': list of strings,
            'weaknesses': list of strings,
            'recommendations': list of dicts with 'title', 'why', 'impact'
        }
    """
    import os
    
    # Get API key from environment
    openai_key = os.environ.get('OPENAI_API_KEY', '')
    claude_key = os.environ.get('ANTHROPIC_API_KEY', '')
    
    if not openai_key and not claude_key:
        # No LLM API configured - return heuristic fallback
        return calculate_geo_ai_readiness_heuristic(parser, schema, content)
    
    # Prepare content summary for LLM
    content_summary = {
        'url': url,
        'title': parser.title,
        'meta_description': parser.meta_description,
        'headings': {
            'h1': parser.headings.get('h1', [])[:3],
            'h2': parser.headings.get('h2', [])[:5],
        },
        'word_count': parser.word_count,
        'has_schema': bool(schema.get('types')),
        'schema_types': schema.get('types', [])[:5],
        'has_author': bool(re.search(r'(author|by |written by)', content, re.I)),
        'has_date': bool(parser.date_meta or re.search(r'\d{4}-\d{2}-\d{2}', content)),
        'main_content': content[:5000],  # First 5000 chars
    }
    
    # Build comprehensive prompt
    prompt = f"""You are an expert SEO analyst specializing in Google's E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) guidelines and GEO (Generative Engine Optimization) for AI search engines like ChatGPT, Perplexity, and Gemini.

Analyze this webpage content and evaluate:

1. **EXPERIENCE (0-100):** Does the content show first-hand experience? Real examples, case studies, personal insights?
2. **EXPERTISE (0-100):** Does the author demonstrate subject matter expertise? Technical depth, industry knowledge?
3. **AUTHORITATIVENESS (0-100):** Is this a recognized authority? Citations, credentials, brand reputation?
4. **TRUSTWORTHINESS (0-100):** Is the content trustworthy? Privacy policy, contact info, transparency, accuracy?
5. **READABILITY (0-100):** Is the writing clear and accessible? Appropriate vocabulary, sentence structure, tone?
6. **GEO READINESS (0-100):** How well-optimized for AI search engines? Structured data, Q&A format, entity clarity?
7. **VOICE OPTIMIZATION (0-100):** How suitable for voice assistants? Conversational tone, direct answers, speakable content?

**Website Data:**
- URL: {content_summary['url']}
- Title: {content_summary['title']}
- Meta Description: {content_summary['meta_description']}
- H1 Headings: {', '.join(content_summary['headings']['h1']) if content_summary['headings']['h1'] else 'None'}
- H2 Headings: {', '.join(content_summary['headings']['h2'][:3]) if content_summary['headings']['h2'] else 'None'}
- Word Count: {content_summary['word_count']}
- Schema Types: {', '.join(content_summary['schema_types']) if content_summary['schema_types'] else 'None'}
- Has Author Info: {content_summary['has_author']}
- Has Publishing Date: {content_summary['has_date']}

**Main Content (first 5000 characters):**
{content_summary['main_content']}

**IMPORTANT:** Return ONLY valid JSON in this exact format (no markdown, no explanation):
{{
  "eeat_score": 75,
  "experience_score": 70,
  "expertise_score": 80,
  "authoritativeness_score": 75,
  "trustworthiness_score": 85,
  "readability_score": 90,
  "geo_readiness": 65,
  "voice_optimization": 60,
  "tone_quality": "professional",
  "strengths": [
    "Clear author credentials demonstrate expertise",
    "Strong use of industry-specific terminology",
    "Privacy policy and contact information build trust"
  ],
  "weaknesses": [
    "Limited first-hand experience or case studies",
    "No FAQ section for voice/AI search",
    "Missing speakable schema markup"
  ],
  "recommendations": [
    {{
      "title": "Add case studies or client examples",
      "why": "First-hand experience signals boost E-E-A-T scores and make content more trustworthy",
      "impact": "High"
    }},
    {{
      "title": "Create FAQ section with question-answer format",
      "why": "AI search engines prefer Q&A format for easy extraction and voice responses",
      "impact": "High"
    }},
    {{
      "title": "Add SpeakableSpecification schema markup",
      "why": "Voice assistants use speakable schema to identify content suitable for reading aloud",
      "impact": "Medium"
    }}
  ]
}}"""
    
    # Try OpenAI first (cheaper, faster)
    if openai_key:
        try:
            result = call_openai_api(prompt, openai_key)
            if result:
                return result
        except Exception as e:
            # OpenAI failed, try Claude if available
            pass
    
    # Fallback to Claude
    if claude_key:
        try:
            result = call_claude_api(prompt, claude_key)
            if result:
                return result
        except Exception as e:
            pass
    
    # Both APIs failed - use heuristic fallback
    return calculate_geo_ai_readiness_heuristic(parser, schema, content)


def call_openai_api(prompt, api_key):
    """
    Call OpenAI GPT-4o-mini API for content analysis.
    
    Cost: ~$0.010 per call (5K input + 500 output tokens)
    """
    api_url = "https://api.openai.com/v1/chat/completions"
    
    payload = {
        "model": "gpt-4o-mini",  # Cheap + fast model
        "messages": [
            {
                "role": "system",
                "content": "You are an expert SEO analyst. Return only valid JSON, no markdown."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,  # Lower temp = more consistent
        "max_tokens": 1000,
    }
    
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode())
        
        # Extract response text
        text = data['choices'][0]['message']['content']
        
        # Clean markdown fences if present
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        # Parse JSON
        result = json.loads(text.strip())
        
        # Validate required fields
        required_fields = ['eeat_score', 'readability_score', 'geo_readiness', 'strengths', 'weaknesses', 'recommendations']
        if all(field in result for field in required_fields):
            return result
        
        return None
        
    except Exception as e:
        return None


def call_claude_api(prompt, api_key):
    """
    Call Anthropic Claude Sonnet 4 API for content analysis.
    
    Cost: ~$0.020 per call (more expensive than GPT-4o-mini)
    """
    api_url = "https://api.anthropic.com/v1/messages"
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
    }
    
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode())
        
        # Extract response text
        text = data['content'][0]['text']
        
        # Clean markdown fences
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        # Parse JSON
        result = json.loads(text.strip())
        
        # Validate
        required_fields = ['eeat_score', 'readability_score', 'geo_readiness']
        if all(field in result for field in required_fields):
            return result
        
        return None
        
    except Exception as e:
        return None


def calculate_geo_ai_readiness_heuristic(parser, schema, all_text):
    """
    Enhanced GEO (Generative Engine Optimization) scoring.
    
    Evaluates content for AI search engines (ChatGPT, Perplexity, Gemini)
    and voice assistants (Alexa, Siri, Google Assistant).
    
    Scoring Factors:
    1. Voice-optimized structured data (30 pts)
    2. Question-answer format (25 pts)
    3. Clear heading hierarchy (20 pts)
    4. Entity density (15 pts)
    5. Citation-friendly formatting (10 pts)
    
    Args:
        parser: PageParser instance with parsed HTML data
        schema: Schema analysis dict from analyze_schema()
        all_text: Full page text content
    
    Returns:
        dict: {
            'score': int (0-100),
            'checks': list of check dicts,
            'top_entities': list of detected entities,
            'qa_patterns': list of question patterns found
        }
    """
    score = 0
    checks = []
    
    # 1. VOICE-OPTIMIZED STRUCTURED DATA (30 points)
    # Check for schemas that voice assistants and AI prefer
    voice_schemas = ['FAQPage', 'HowTo', 'SpeakableSpecification', 'QAPage']
    schema_types = schema.get('types', [])
    
    has_voice_schema = any(t in schema_types for t in voice_schemas)
    
    if has_voice_schema:
        voice_schema_list = [t for t in schema_types if t in voice_schemas]
        score += 30
        checks.append({
            'label': 'Voice-Optimized Schema',
            'status': 'pass',
            'detail': f"Has {', '.join(voice_schema_list)} schema",
            'points': 30,
            'impact': 'High',
            'fix_title': None,
            'fix_why': None
        })
    elif schema_types:
        score += 15
        checks.append({
            'label': 'Basic Structured Data',
            'status': 'warn',
            'detail': f"Has schema but missing FAQ/HowTo/Speakable",
            'points': 15,
            'impact': 'Medium',
            'fix_title': 'Add voice-optimized schema markup',
            'fix_why': 'FAQPage, HowTo, and Speakable schemas help voice assistants and AI extract your content.'
        })
    else:
        checks.append({
            'label': 'Voice-Optimized Schema',
            'status': 'fail',
            'detail': 'No structured data found',
            'points': 0,
            'impact': 'High',
            'fix_title': 'Add FAQPage or HowTo schema',
            'fix_why': 'Voice assistants and AI need structured data to understand and cite your content.'
        })
    
    # 2. QUESTION-ANSWER FORMAT (25 points)
    # AI engines love Q&A format - matches how users ask questions
    qa_patterns = re.findall(
        r'(?:what|how|why|when|where|who|which|best|top)\s+'
        r'(?:is|are|do|does|can|could|should|would|will)\s+'
        r'[^?]{10,150}\?',
        all_text.lower(),
        re.IGNORECASE
    )
    
    qa_count = len(qa_patterns)
    
    if qa_count >= 5:
        score += 25
        checks.append({
            'label': 'AI-Friendly Q&A Format',
            'status': 'pass',
            'detail': f'Found {qa_count} question patterns',
            'points': 25,
            'impact': 'High',
            'fix_title': None,
            'fix_why': None
        })
    elif qa_count >= 2:
        score += 15
        checks.append({
            'label': 'Q&A Format',
            'status': 'warn',
            'detail': f'Found {qa_count} questions (aim for 5+)',
            'points': 15,
            'impact': 'Medium',
            'fix_title': 'Add more Q&A content',
            'fix_why': 'AI engines prefer content that directly answers common questions. Add 3-5 more FAQ items.'
        })
    else:
        checks.append({
            'label': 'Q&A Format',
            'status': 'fail',
            'detail': 'No question-format content found',
            'points': 0,
            'impact': 'High',
            'fix_title': 'Create FAQ section with Q&A format',
            'fix_why': 'AI engines like ChatGPT and Perplexity prefer content in question-answer format.'
        })
    
    # 3. CLEAR HEADING HIERARCHY (20 points)
    # Proper H1→H2→H3 structure helps AI understand content organization
    h1_count = len(parser.headings.get('h1', []))
    has_h2h3 = bool(parser.headings.get('h2') or parser.headings.get('h3'))
    
    if h1_count == 1 and has_h2h3:
        score += 20
        checks.append({
            'label': 'Clear Heading Structure',
            'status': 'pass',
            'detail': 'Single H1 with proper H2/H3 hierarchy',
            'points': 20,
            'impact': 'Medium',
            'fix_title': None,
            'fix_why': None
        })
    elif has_h2h3:
        score += 10
        checks.append({
            'label': 'Heading Structure',
            'status': 'warn',
            'detail': f'{h1_count} H1 tags (should be exactly 1)',
            'points': 10,
            'impact': 'Low',
            'fix_title': 'Use exactly one H1 tag per page',
            'fix_why': 'AI engines prefer a clear content hierarchy starting with a single H1.'
        })
    else:
        checks.append({
            'label': 'Heading Structure',
            'status': 'fail',
            'detail': 'Missing or poor heading hierarchy',
            'points': 0,
            'impact': 'Medium',
            'fix_title': 'Add proper heading structure (H1 → H2 → H3)',
            'fix_why': 'Clear headings help AI understand your content organization and extract key topics.'
        })
    
    # 4. ENTITY DENSITY (15 points)
    # Proper nouns (locations, names, brands) give AI context
    # Extract capitalized words/phrases
    entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', all_text)
    
    # Filter out common words
    exclusions = {'The', 'This', 'These', 'That', 'Those', 'There', 'Here', 
                  'When', 'Where', 'What', 'Why', 'How', 'Who', 'Which',
                  'AI', 'LLM', 'GPT', 'API', 'URL', 'HTML', 'CSS', 'SEO'}
    entities = [e for e in entities if e not in exclusions]
    
    unique_entities = list(set(entities))
    entity_count = len(unique_entities)
    
    if entity_count >= 20:
        entity_score = 15
        status = 'pass'
    elif entity_count >= 10:
        entity_score = 10
        status = 'warn'
    else:
        entity_score = 5
        status = 'warn'
    
    score += entity_score
    checks.append({
        'label': 'Entity Context',
        'status': status,
        'detail': f'{entity_count} unique entities (locations, names, brands)',
        'points': entity_score,
        'impact': 'Medium',
        'fix_title': 'Add more specific references' if entity_count < 20 else None,
        'fix_why': 'AI engines use entities (names, locations, brands) to understand context and relevance.' if entity_count < 20 else None
    })
    
    # 5. CITATION-FRIENDLY FORMATTING (10 points)
    # Lists and tables are easy for AI to extract and cite
    has_lists = bool(re.search(r'<(ul|ol)', all_text, re.IGNORECASE))
    has_tables = bool(re.search(r'<table', all_text, re.IGNORECASE))
    
    if has_lists or has_tables:
        score += 10
        format_types = []
        if has_lists:
            format_types.append('lists')
        if has_tables:
            format_types.append('tables')
        
        checks.append({
            'label': 'Citation-Friendly Formatting',
            'status': 'pass',
            'detail': f'Has {" and ".join(format_types)} for easy AI extraction',
            'points': 10,
            'impact': 'Low',
            'fix_title': None,
            'fix_why': None
        })
    else:
        checks.append({
            'label': 'Citation-Friendly Formatting',
            'status': 'warn',
            'detail': 'No lists or tables found',
            'points': 0,
            'impact': 'Low',
            'fix_title': 'Format key information as lists or tables',
            'fix_why': 'AI engines prefer structured content (lists, tables) for easy extraction and citation.'
        })
    
    return {
        'score': min(100, score),
        'checks': checks,
        'top_entities': unique_entities[:10],  # Top 10 entities
        'qa_patterns': qa_patterns[:5],  # First 5 Q&A patterns
        'entity_count': entity_count,
        'qa_count': qa_count
    }
```

**Integrate into run_analysis():**
```python
# REPLACE THE EXISTING AI SEARCH SCORING SECTION (around line 1100)
# WITH A CALL TO THE NEW FUNCTION:

# Calculate enhanced GEO/AI readiness
geo_result = calculate_geo_ai_readiness(parser, schema, parser.all_text)

# Use the enhanced checks instead of basic ones
ai_checks = geo_result['checks']
ai_score = geo_result['score']

# Add extra metadata to result
result['geo_analysis'] = {
    'top_entities': geo_result['top_entities'],
    'qa_patterns_found': geo_result['qa_count'],
    'entity_count': geo_result['entity_count']
}
```

**Update PDF Report Template (report.py):**
```python
# ADD GEO INSIGHTS SECTION TO PDF (around line 200 in report.py)

if data.get('geo_analysis'):
    geo = data['geo_analysis']
    
    geo_insights = f"""
    <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin-top: 20px;">
        <h3 style="margin-top: 0;">🤖 AI Search Insights</h3>
        <ul style="margin: 0; padding-left: 20px;">
            <li><strong>Entities Detected:</strong> {geo['entity_count']} 
                (e.g., {', '.join(geo['top_entities'][:3])})</li>
            <li><strong>Q&A Patterns:</strong> {geo['qa_patterns_found']} question-answer pairs found</li>
            <li><strong>AI Citation Readiness:</strong> 
                {'High' if geo['qa_patterns_found'] >= 5 else 'Medium' if geo['qa_patterns_found'] >= 2 else 'Low'}
            </li>
        </ul>
    </div>
    """
    
    # Insert into PDF template
```

**Testing Requirements:**
- Test on FAQ pages - verify high Q&A scores
- Test on pages with speakable schema - verify 30pt bonus
- Test entity extraction - verify excludes common words
- Compare with competitors' tools - verify superior insights

**Expected Impact:**
- ✅ More accurate GEO scoring than competitors
- ✅ Voice optimization detection (unique feature)
- ✅ Entity analysis shows content richness

---

#### Task 3.1: SERP Position Tracking (DEFAULT FEATURE)
**File:** `analyze.py` (New default feature for all client scans)  
**Value:** Show clients their actual search visibility (not just scores)

**What SERP Tracking Does for Your Clients:**

SERP (Search Engine Results Page) tracking is the **most valuable feature** for your clients because it shows REAL business impact:

**1. Actual Visibility Measurement:**
- Instead of: "Your SEO score is 66/100" (abstract, meaningless to clients)
- Show them: "You rank #7 for 'HVAC repair near me' in New York" (concrete, actionable)

**2. Competitive Intelligence:**
- "Your competitor ABC Plumbing ranks #3 - they have FAQ schema which you're missing"
- "You're #11 for 'plumber NYC' - one spot away from page 1!"
- "You rank #1 for 'emergency plumber Manhattan' - keep optimizing this!"

**3. Opportunity Identification:**
- Low-hanging fruit: "You're #11-15 for these 3 keywords - small improvements could get you on page 1"
- Missing opportunities: "You don't rank at all for 'drain cleaning NYC' but your competitors do"
- Strengths to protect: "You rank #1-3 for these keywords - maintain this content"

**4. ROI Proof Over Time:**
- Month 1: "You rank #15 for 'plumber NYC'"
- Month 3: "You moved up to #8 (+7 positions)"
- Month 6: "You're now #3 (+12 positions total)"
- This proves the value of your SEO work

**5. Local Pack Presence:**
- "You appear in Google's Local Pack (top 3 map results) for 2 out of 5 keywords"
- "Competitors in local pack have complete Google Business Profiles - you're missing hours/photos"

**How It Works:**
1. For each client, identify their top 5-10 target keywords based on industry
2. Check their actual ranking position for each keyword (1-100)
3. Identify if they appear in Featured Snippets, Local Pack, or AI Overviews
4. Compare against top competitors
5. Show trend over time (if rescanned)

**Example SERP Report Output:**

```
🎯 SEARCH VISIBILITY ANALYSIS

Your Rankings for "HVAC repair New York":
┌─────────────────────────────────────────────────────────┐
│ Keyword                         | Your Rank | Competitors│
├─────────────────────────────────────────────────────────┤
│ "hvac repair near me"           | #7        | ABC (#3)   │
│ "air conditioning service NYC"  | #12       | XYZ (#5)   │
│ "furnace repair Manhattan"      | Not found | ABC (#8)   │
│ "emergency HVAC New York"       | #4        | None       │
│ "AC installation Brooklyn"      | #15       | XYZ (#2)   │
└─────────────────────────────────────────────────────────┘

📊 Summary:
- Found in top 10: 2 out of 5 keywords (40%)
- Average position when ranked: #7.7
- Best ranking: #4 (emergency HVAC)
- Biggest opportunity: "furnace repair" (not ranked, competitors are)

💡 Quick Wins:
1. Add FAQ section about "air conditioning service" to move from #12 → #8
2. Create content for "furnace repair Manhattan" (missing, competitors rank)
3. Optimize "emergency HVAC" page (already #4, could reach #1)
```

**Implementation:**
```python
# ADD SERP TRACKING TO analyze.py (around line 2000)

def get_serp_position(domain, query, location='United States'):
    """
    Check where domain ranks for a specific search query.
    
    Uses Google Custom Search JSON API or ValueSERP.
    
    Args:
        domain: Domain to check (e.g., 'example.com')
        query: Search query (e.g., 'plumber near me')
        location: Search location (default: 'United States')
    
    Returns:
        dict: {
            'position': int or None (1-100 or None if not found),
            'title': str (result title),
            'snippet': str (result description),
            'url': str (actual ranking URL),
            'query': str (search query used),
            'in_local_pack': bool,
            'has_featured_snippet': bool,
            'in_ai_overview': bool,
            'competitors_above': list of domains ranking higher
        }
    """
    # Get API credentials from environment
    google_api_key = os.environ.get('GOOGLE_CSE_API_KEY', '')
    google_cx = os.environ.get('GOOGLE_CSE_CX', '')
    valueserp_key = os.environ.get('VALUESERP_API_KEY', '')
    
    # Try Google Custom Search first (free 100/day)
    if google_api_key and google_cx:
        result = check_serp_google_cse(domain, query, google_api_key, google_cx)
        if result:
            return result
    
    # Fallback to ValueSERP if Google quota exceeded
    if valueserp_key:
        result = check_serp_valueserp(domain, query, valueserp_key, location)
        if result:
            return result
    
    # No SERP API configured
    return None


def check_serp_google_cse(domain, query, api_key, cx):
    """
    Use Google Custom Search API to check rankings.
    
    Limitations:
    - 100 free searches/day
    - Doesn't return local pack results
    - Only shows top 10 results per query
    """
    search_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': cx,
        'q': query,
        'num': 10,  # Get top 10 results
    }
    
    try:
        query_string = urllib.parse.urlencode(params)
        full_url = f"{search_url}?{query_string}"
        
        req = urllib.request.Request(full_url)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        # Find domain in results
        competitors_above = []
        
        for idx, item in enumerate(data.get('items', []), 1):
            item_domain = urllib.parse.urlparse(item['link']).netloc.replace('www.', '')
            
            if domain.lower() in item_domain.lower():
                # Found our domain!
                return {
                    'position': idx,
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'query': query,
                    'found': True,
                    'in_local_pack': False,  # Google CSE doesn't show this
                    'has_featured_snippet': (idx == 1 and 'featured' in str(item).lower()),
                    'competitors_above': competitors_above,
                    'api_source': 'google_cse'
                }
            else:
                # Track competitors ranking above us
                competitors_above.append({
                    'position': idx,
                    'domain': item_domain,
                    'title': item.get('title', '')
                })
        
        # Not found in top 10
        return {
            'position': None,
            'query': query,
            'found': False,
            'message': f'Not ranked in top 10 for "{query}"',
            'competitors_above': competitors_above[:3],  # Top 3 competitors
            'api_source': 'google_cse'
        }
        
    except Exception as e:
        return None


def check_serp_valueserp(domain, query, api_key, location):
    """
    Use ValueSERP API for more detailed SERP data.
    
    Advantages:
    - Returns local pack results
    - Shows AI Overviews / Featured Snippets
    - Can check up to 100 results (not just 10)
    - More reliable than Google CSE
    
    Cost: $0.006 per search (pay-as-you-go)
    """
    api_url = "https://api.valueserp.com/search"
    
    params = {
        'api_key': api_key,
        'q': query,
        'location': location,
        'google_domain': 'google.com',
        'gl': 'us',
        'hl': 'en',
        'num': '100',  # Get top 100 results
        'output': 'json'
    }
    
    try:
        query_string = urllib.parse.urlencode(params)
        full_url = f"{api_url}?{query_string}"
        
        req = urllib.request.Request(full_url)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
        
        # Check local pack first
        local_results = data.get('local_results', {}).get('places', [])
        for idx, place in enumerate(local_results, 1):
            place_domain = urllib.parse.urlparse(place.get('link', '')).netloc.replace('www.', '')
            if domain.lower() in place_domain.lower():
                return {
                    'position': idx,
                    'title': place.get('title', ''),
                    'snippet': place.get('description', ''),
                    'url': place.get('link', ''),
                    'query': query,
                    'found': True,
                    'in_local_pack': True,  # ✅ This is gold for local businesses!
                    'local_pack_position': idx,
                    'api_source': 'valueserp'
                }
        
        # Check organic results
        organic_results = data.get('organic_results', [])
        competitors_above = []
        
        for idx, result in enumerate(organic_results, 1):
            result_domain = urllib.parse.urlparse(result.get('link', '')).netloc.replace('www.', '')
            
            if domain.lower() in result_domain.lower():
                return {
                    'position': idx,
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'url': result.get('link', ''),
                    'query': query,
                    'found': True,
                    'in_local_pack': False,
                    'has_featured_snippet': (idx == 1 and result.get('snippet_highlighted_words')),
                    'competitors_above': competitors_above[:3],
                    'api_source': 'valueserp'
                }
            else:
                competitors_above.append({
                    'position': idx,
                    'domain': result_domain,
                    'title': result.get('title', '')
                })
        
        # Not found
        return {
            'position': None,
            'query': query,
            'found': False,
            'competitors_above': competitors_above[:5],
            'api_source': 'valueserp'
        }
        
    except Exception as e:
        return None


def generate_serp_test_queries(industry, business_name=None, location=None):
    """
    Generate industry-specific search queries for SERP testing.
    
    Returns 5-8 most relevant queries for each industry.
    
    Args:
        industry: Business industry (e.g., 'plumbing', 'hvac', 'dental')
        business_name: Optional business name for branded queries
        location: Optional location (e.g., 'New York', 'Brooklyn')
    
    Returns:
        list: List of search queries to test (5-8 queries)
    """
    # Industry-specific high-intent queries
    query_templates = {
        'plumbing': [
            'plumber near me',
            'emergency plumbing services',
            'drain cleaning',
            'water heater repair',
            'pipe repair'
        ],
        'hvac': [
            'HVAC repair near me',
            'air conditioning service',
            'furnace repair',
            'AC installation',
            'heating and cooling'
        ],
        'electrical': [
            'electrician near me',
            'electrical repair',
            'circuit breaker replacement',
            'electrical panel upgrade'
        ],
        'landscaping': [
            'landscaping services',
            'lawn care near me',
            'tree removal',
            'landscape design'
        ],
        'roofing': [
            'roofer near me',
            'roof repair',
            'roof replacement',
            'roof leak repair'
        ],
        'dental': [
            'dentist near me',
            'dental implants',
            'teeth whitening',
            'emergency dentist'
        ],
        'legal': [
            'lawyer near me',
            'personal injury attorney',
            'family law attorney',
            'criminal defense lawyer'
        ],
        'medical': [
            'doctor near me',
            'urgent care',
            'family physician',
            'primary care doctor'
        ],
        'accounting': [
            'accountant near me',
            'CPA services',
            'tax preparation',
            'bookkeeping services'
        ],
        'real_estate': [
            'real estate agent',
            'homes for sale',
            'realtor near me',
            'property for sale'
        ],
        'pest_control': [
            'pest control near me',
            'exterminator',
            'termite treatment',
            'bed bug removal'
        ],
        'cleaning': [
            'cleaning service near me',
            'house cleaning',
            'maid service',
            'carpet cleaning'
        ],
        'auto': [
            'auto repair near me',
            'mechanic',
            'oil change',
            'brake repair'
        ],
    }
    
    # Get base queries for industry
    queries = query_templates.get(industry, [
        f'{industry} near me',
        f'best {industry}',
        f'{industry} services'
    ])
    
    # Add location if provided
    if location:
        queries = [f"{q} {location}" if "near me" not in q else q for q in queries]
    
    # Add branded query if business name provided
    if business_name:
        queries.insert(0, business_name)  # Check branded search first
    
    return queries[:8]  # Return top 8 most relevant


def run_serp_analysis(url, industry, business_name=None, location=None):
    """
    Run complete SERP analysis for a client website.
    
    This is a DEFAULT FEATURE (not premium) - run for every client scan.
    
    Args:
        url: Client website URL
        industry: Business industry
        business_name: Optional business name
        location: Optional location for local searches
    
    Returns:
        dict: {
            'queries_tested': list of queries,
            'positions': dict (query → result),
            'found_count': int,
            'total_queries': int,
            'average_position': float or None,
            'visibility_score': int (0-100),
            'in_local_pack_count': int,
            'top_ranking': dict (best ranking query),
            'biggest_opportunity': dict (not ranking but competitors are),
            'quick_wins': list of actionable recommendations
        }
    """
    domain = urllib.parse.urlparse(url).netloc.replace('www.', '')
    
    # Generate test queries
    queries = generate_serp_test_queries(industry, business_name, location)
    
    results = {
        'queries_tested': queries,
        'positions': {},
        'found_count': 0,
        'total_queries': len(queries),
        'in_local_pack_count': 0,
        'detailed_results': []
    }
    
    positions_found = []
    local_pack_keywords = []
    not_ranking = []
    
    # Test each query
    for query in queries:
        serp_result = get_serp_position(domain, query, location)
        
        if serp_result and serp_result.get('found'):
            results['positions'][query] = serp_result['position']
            positions_found.append(serp_result['position'])
            results['found_count'] += 1
            
            if serp_result.get('in_local_pack'):
                results['in_local_pack_count'] += 1
                local_pack_keywords.append(query)
            
            results['detailed_results'].append({
                'query': query,
                'position': serp_result['position'],
                'in_local_pack': serp_result.get('in_local_pack', False),
                'competitors_above': serp_result.get('competitors_above', [])
            })
        else:
            results['positions'][query] = None
            not_ranking.append({
                'query': query,
                'competitors': serp_result.get('competitors_above', []) if serp_result else []
            })
    
    # Calculate metrics
    if positions_found:
        results['average_position'] = round(sum(positions_found) / len(positions_found), 1)
        
        # Visibility score: weighted by position
        # Position 1 = 100 points, Position 2 = 90, Position 3 = 80, etc.
        visibility_scores = [max(0, 110 - (pos * 10)) for pos in positions_found]
        results['visibility_score'] = int(sum(visibility_scores) / len(queries))
        
        # Find best ranking
        best_idx = positions_found.index(min(positions_found))
        results['top_ranking'] = {
            'query': queries[best_idx],
            'position': min(positions_found)
        }
    else:
        results['average_position'] = None
        results['visibility_score'] = 0
        results['top_ranking'] = None
    
    # Identify biggest opportunity (not ranking but competitors are)
    if not_ranking:
        # Find queries where competitors rank but client doesn't
        opportunities = [nr for nr in not_ranking if nr['competitors']]
        if opportunities:
            results['biggest_opportunity'] = opportunities[0]
    
    # Generate quick wins
    results['quick_wins'] = generate_serp_quick_wins(results)
    
    return results


def generate_serp_quick_wins(serp_results):
    """
    Generate actionable recommendations based on SERP results.
    
    Returns:
        list: List of quick win recommendations with title, why, impact
    """
    quick_wins = []
    
    # Quick win 1: Keywords ranking #11-20 (one page away from page 1)
    near_page_one = [
        {'query': q, 'position': p} 
        for q, p in serp_results['positions'].items() 
        if p and 11 <= p <= 20
    ]
    
    if near_page_one:
        query = near_page_one[0]['query']
        position = near_page_one[0]['position']
        quick_wins.append({
            'title': f'Move "{query}" from #{position} to page 1',
            'why': f'You\'re just {position - 10} spots away from page 1. Small optimizations (add FAQ, improve title) could push you up.',
            'impact': 'High',
            'type': 'near_page_one'
        })
    
    # Quick win 2: Not in local pack but should be
    if serp_results['in_local_pack_count'] < serp_results['found_count']:
        quick_wins.append({
            'title': 'Optimize Google Business Profile for local pack',
            'why': f'You rank organically but appear in local pack for only {serp_results["in_local_pack_count"]} keywords. Complete GBP could 3x your visibility.',
            'impact': 'High',
            'type': 'local_pack'
        })
    
    # Quick win 3: Biggest opportunity (not ranking but competitors are)
    if serp_results.get('biggest_opportunity'):
        opp = serp_results['biggest_opportunity']
        quick_wins.append({
            'title': f'Create content for "{opp["query"]}"',
            'why': f'Competitors rank for this but you don\'t. High search volume, low competition opportunity.',
            'impact': 'High',
            'type': 'content_gap'
        })
    
    return quick_wins[:3]  # Return top 3 quick wins
```

**Integrate into run_analysis():**
```python
# IN run_analysis() FUNCTION (around line 1500), ADD SERP ANALYSIS:

# Run SERP analysis (default for all clients)
serp_analysis = run_serp_analysis(
    url,
    result.get('industry', 'unknown'),
    business_name=extract_business_name(parser.title, domain),
    location=None  # Could extract from address if available
)

# Add to result
result['serp_analysis'] = serp_analysis
```

---

## 📄 HUMAN-TOUCH REPORT OUTPUTS

**Critical: Reports must feel personal and actionable, not robotic**

### Report Writing Guidelines:

**1. Use Conversational Language:**
```
❌ BAD (Robotic):
"Meta description optimization required. Current character count: 0. Recommended range: 150-160."

✅ GOOD (Human):
"You're missing a meta description - this is the text that appears under your link in Google search results. Without one, Google picks random text from your page, which usually looks unprofessional. Add a compelling 150-160 character summary to improve click-through rates."
```

**2. Explain WHY, Not Just WHAT:**
```
❌ BAD:
"Add FAQ schema"

✅ GOOD:
"Add FAQ schema to your website. Here's why it matters: When someone asks Siri or Google Assistant a question, these voice assistants pull answers from FAQ sections. Without FAQ schema, you're invisible to voice search - which is 50% of all searches in 2026."
```

**3. Show Business Impact:**
```
❌ BAD:
"Your page speed is 45/100"

✅ GOOD:
"Your website takes 6.2 seconds to load - that's slow enough that 53% of mobile visitors will abandon before seeing your content. Every second of delay costs you potential customers. The good news: fixing just 3 issues (image compression, render-blocking scripts, unused CSS) could cut this to under 3 seconds."
```

**4. Make Recommendations Specific:**
```
❌ BAD:
"Improve content quality"

✅ GOOD:
"Add 2-3 case studies or customer success stories to your homepage. Right now, your content talks about what you do, but doesn't show proof. Real examples like 'How we fixed Mrs. Johnson's furnace in 2 hours during a blizzard' build trust and improve your E-E-A-T score (Google's measure of expertise)."
```

**5. SERP Results - Show Competitive Context:**
```
✅ GOOD SERP REPORTING:

"📍 Local Search Visibility:

Good news: You rank #4 for 'emergency HVAC New York' - you're on page 1!

Opportunity: You rank #12 for 'HVAC repair NYC' (page 2). Your competitor ABC Heating ranks #3 because they have:
  • A dedicated FAQ section (you don't)
  • 50+ Google reviews (you have 12)
  • Complete business hours on Google (yours are missing)

Quick Win: Add a FAQ section answering the 5 most common HVAC questions. This alone could move you from #12 to #8 within 30 days."
```

### PDF Report Structure (Human-Friendly):

**Section 1: Executive Summary (Non-Technical)**
```
"Your website scored 51/100 overall - there's definitely room for improvement, but the good news is we've identified exactly what to fix and in what order.

Think of this like a health checkup for your website. You're not 'sick', but you could be healthier. The prescription is clear and most issues can be fixed in 2-4 weeks."
```

**Section 2: What's Working Well (Start Positive)**
```
"✅ What You're Doing Right:

• Your website loads over HTTPS (secure connection) - this protects your visitors' data
• You have 316 words of content - enough for search engines to understand your page
• Phone number and address are visible - customers can easily contact you
• You're ranking #4 for 'emergency plumber Manhattan' - that's page 1!"
```

**Section 3: Priority Fixes (Actionable, Ordered by Impact)**
```
"🎯 What to Fix First (Highest Impact):

1. Add a Meta Description (5 minutes, High Impact)
   What it is: The text that shows up under your link in Google
   Why it matters: Google is currently showing random text. You're losing 30-40% of potential clicks.
   How to fix: Write a compelling 155-character summary. Example: 'Family-owned plumbing in NYC since 1985. 24/7 emergency service, licensed & insured. Call now: (555) 123-4567'

2. Add FAQ Schema (30 minutes, High Impact)
   What it is: Special code that tells Google 'this is a Q&A section'
   Why it matters: Voice assistants (Siri, Alexa) ONLY pull from FAQ sections. Without it, you're invisible to voice search.
   How to fix: [Link to FAQ schema generator] or hire a developer for $150-300"
```

**Section 4: Search Rankings (Show Real Visibility)**
```
"📊 Where You Actually Show Up in Google:

We tested 5 keywords people use to find businesses like yours:

'emergency plumber NYC' → You rank #4 ⭐ (Page 1)
'plumber near me' → You rank #12 ⚠️ (Page 2)  
'drain cleaning Manhattan' → Not ranking ❌
'24 hour plumber' → You rank #7 ⭐ (Page 1)
'pipe repair NYC' → You rank #18 ⚠️ (Page 2)

Summary: You're visible for emergency keywords but invisible for maintenance keywords. This means you're missing 60% of potential customers."
```

**Section 5: Competitive Analysis (Show Who's Beating Them)**
```
"🥊 How You Compare to Competitors:

ABC Plumbing (ranks #3 overall):
  ✅ Has FAQ section (you don't)
  ✅ Has 50+ Google reviews (you have 12)
  ✅ Blog with 20+ articles (you have 0)
  ❌ Slower website than yours (6s vs your 4s)

Takeaway: You have a faster website (technical SEO is better), but they have better content and social proof. Focus on content and reviews to compete."
```

**Section 6: Next Steps (Clear Action Plan)**
```
"🚀 Your 30-Day Action Plan:

Week 1: Quick wins (2-3 hours total)
  □ Add meta description
  □ Fix image alt tags (19 images missing descriptions)
  □ Add FAQ section (10 common questions)

Week 2-3: Content improvements (5-8 hours)
  □ Write 3 blog posts about common plumbing problems
  □ Add customer testimonials to homepage
  □ Create service area page (list neighborhoods you serve)

Week 4: Technical fixes (hire developer, $300-500)
  □ Add FAQ schema markup
  □ Add LocalBusiness schema
  □ Fix heading hierarchy

Expected Results: Moving from overall score 51 → 75+, rankings from #12-18 → #5-8 for key terms."
```

### LLM Analysis Integration in Report:

**Show E-E-A-T Insights (Human-Readable)**:
```
"🤖 AI Analysis (What ChatGPT/Perplexity See):

We analyzed your content using the same AI that powers ChatGPT and Google's search. Here's what it found:

Expertise Score: 70/100
  ✅ Strong: You use industry-specific terms correctly
  ⚠️ Weak: No author bio or credentials visible
  💡 Fix: Add a short 'About Us' section mentioning years of experience, licenses, certifications

Trustworthiness Score: 85/100
  ✅ Strong: Privacy policy and contact info clearly visible
  ✅ Strong: HTTPS security enabled
  ⚠️ Weak: No customer reviews or social proof on homepage
  💡 Fix: Embed your Google reviews widget (free tool: [link])

GEO Readiness: 65/100 (How likely AI will recommend you)
  ✅ Strong: Clear contact information
  ⚠️ Weak: No Q&A format content (AI engines prefer questions and direct answers)
  ❌ Critical: Missing FAQ section - this is how AI assistants find answers
  
What this means: If someone asks ChatGPT 'who are good plumbers in NYC?', you probably won't be mentioned. Competitors with FAQ sections have a 3x higher chance of being recommended."
```

---
    """
    Check where domain ranks for a specific search query.
    
    Uses Google Custom Search JSON API (100 queries/day free).
    Alternative: ValueSERP API ($30/month for 5,000 searches).
    
    Args:
        domain: Domain to check (e.g., 'example.com')
        query: Search query (e.g., 'plumber near me')
        location: Search location (default: 'United States')
    
    Returns:
        dict: {
            'position': int or None (1-10 or None if not found),
            'title': str (result title),
            'snippet': str (result description),
            'url': str (result URL),
            'query': str (search query used)
        } or None on error
    """
    # Get API credentials from environment
    api_key = os.environ.get('GOOGLE_CSE_API_KEY', '')
    cx = os.environ.get('GOOGLE_CSE_CX', '')  # Custom Search Engine ID
    
    if not api_key or not cx:
        # API not configured - return None
        return None
    
    search_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': cx,
        'q': query,
        'num': 10,  # Get top 10 results
        'gl': 'us' if location == 'United States' else 'us',
    }
    
    try:
        # Build request URL
        query_string = urllib.parse.urlencode(params)
        full_url = f"{search_url}?{query_string}"
        
        req = urllib.request.Request(full_url)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        # Search for domain in results
        for idx, item in enumerate(data.get('items', []), 1):
            if domain.lower() in item['link'].lower():
                return {
                    'position': idx,
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'query': query,
                    'found': True
                }
        
        # Not found in top 10
        return {
            'position': None,
            'query': query,
            'found': False,
            'message': f'Not found in top 10 for "{query}"'
        }
        
    except Exception as e:
        return None


def generate_serp_test_queries(industry, location=None):
    """
    Generate industry-specific search queries for SERP testing.
    
    Args:
        industry: Business industry (e.g., 'plumbing', 'hvac', 'dental')
        location: Optional location (e.g., 'New York')
    
    Returns:
        list: List of search queries to test
    """
    # Industry-specific query templates
    query_templates = {
        'plumbing': [
            'plumber near me',
            'emergency plumbing services',
            'best plumber',
            'drain cleaning services',
            'water heater repair'
        ],
        'hvac': [
            'HVAC repair near me',
            'air conditioning service',
            'furnace repair',
            'AC installation',
            'heating and cooling'
        ],
        'electrical': [
            'electrician near me',
            'electrical repair',
            'circuit breaker replacement',
            'electrical panel upgrade',
            'emergency electrician'
        ],
        'landscaping': [
            'landscaping services',
            'lawn care near me',
            'tree removal',
            'landscape design',
            'irrigation repair'
        ],
        'dental': [
            'dentist near me',
            'dental implants',
            'teeth whitening',
            'emergency dentist',
            'cosmetic dentistry'
        ],
        'legal': [
            'lawyer near me',
            'personal injury attorney',
            'family law attorney',
            'criminal defense lawyer',
            'estate planning attorney'
        ],
        'medical': [
            'doctor near me',
            'urgent care',
            'family physician',
            'medical clinic',
            'primary care doctor'
        ],
        # Add more industries...
    }
    
    queries = query_templates.get(industry, [
        f'{industry} near me',
        f'best {industry}',
        f'{industry} services'
    ])
    
    # Add location if provided
    if location:
        queries = [f"{q} {location}" for q in queries]
    
    return queries[:5]  # Return top 5 most relevant


def run_premium_serp_analysis(url, industry, location=None):
    """
    Premium feature: Test visibility across major search engines.
    
    This is a PAID FEATURE - charge $99-149 for premium reports.
    Uses Google Custom Search API (100 free/day, then $5 per 1K).
    
    Args:
        url: Website URL to analyze
        industry: Business industry
        location: Optional location for local searches
    
    Returns:
        dict: {
            'queries_tested': list,
            'average_position': float or None,
            'positions': dict (query → position),
            'visibility_score': int (0-100),
            'found_count': int,
            'total_queries': int
        }
    """
    domain = urllib.parse.urlparse(url).netloc.replace('www.', '')
    
    # Generate test queries
    queries = generate_serp_test_queries(industry, location)
    
    results = {
        'queries_tested': queries,
        'positions': {},
        'found_count': 0,
        'total_queries': len(queries)
    }
    
    positions_found = []
    
    # Test each query
    for query in queries:
        serp_result = get_serp_position(domain, query)
        
        if serp_result and serp_result.get('found'):
            results['positions'][query] = serp_result['position']
            positions_found.append(serp_result['position'])
            results['found_count'] += 1
        else:
            results['positions'][query] = None
    
    # Calculate metrics
    if positions_found:
        results['average_position'] = sum(positions_found) / len(positions_found)
        
        # Visibility score: 100 if rank #1, 90 if #2, etc.
        # Average across all found positions
        visibility_scores = [max(0, 100 - (pos - 1) * 10) for pos in positions_found]
        results['visibility_score'] = int(sum(visibility_scores) / len(visibility_scores))
    else:
        results['average_position'] = None
        results['visibility_score'] = 0
    
    return results
```

**Add Premium Tier Flag:**
```python
# IN run_analysis() FUNCTION, ADD PREMIUM PARAMETER:

def run_analysis(url, scan_type="self", primary_domain=None, competitor_domain=None,
                 competitor_result=None, contact_name="", contact_email="",
                 contact_phone="", contact_role="", ip_address="unknown",
                 premium_tier=False):  # ADD THIS
    """
    Main analysis function.
    
    Args:
        ...
        premium_tier: bool - If True, run premium features (SERP tracking)
    """
    
    # ... existing analysis code ...
    
    # PREMIUM FEATURES (only if premium_tier=True)
    if premium_tier:
        # Run SERP position analysis
        serp_analysis = run_premium_serp_analysis(
            url, 
            result.get('industry', 'unknown'),
            location=None  # Could extract from address
        )
        
        result['premium'] = {
            'serp_analysis': serp_analysis,
            'tier': 'premium'
        }
    
    return result
```

**Pricing Strategy:**
```python
# IN CGI HANDLER, CHECK FOR PREMIUM REQUESTS:

# Check if user requested premium tier
# This could come from:
# 1. Payment verification (Stripe webhook)
# 2. Premium user email check
# 3. One-time premium token

premium_token = payload.get('premium_token', '')
is_premium = verify_premium_access(contact_email, premium_token)

# Run analysis with premium flag
result = run_analysis(
    url,
    # ... other args ...
    premium_tier=is_premium
)

# If not premium but SERP data in result, charge user
if result.get('premium') and not is_premium:
    # Return paywall message
    result = {
        'error': 'premium_required',
        'message': 'SERP tracking requires premium tier ($149)',
        'upgrade_url': 'https://alianzaconnects.com/premium'
    }
```



**Testing Requirements:**
- Set up Google Custom Search API credentials
- Test SERP detection on known ranking pages
- Verify "not found" handling
- Test industry-specific query generation

---

## 📋 QUALITY ASSURANCE CHECKLIST

### **Pre-Launch Testing (Do Before Each Phase)**

#### Phase 1 (Critical Fixes):
- [ ] Test enhanced fetch_page() on 50 diverse sites
- [ ] Verify retry logic triggers on 403/429/503 errors
- [ ] Confirm User-Agent rotation (check server logs)
- [ ] Test rate limiting: 6th scan blocked, resets after 24hr
- [ ] Test caching: 2nd scan within 1hr returns cache
- [ ] Verify cache expiration (12hr/24hr/72hr based on score)
- [ ] Test IP extraction from X-Forwarded-For headers

#### Phase 2 (Performance):
- [ ] PageSpeed API returns scores for 10 test URLs
- [ ] Fallback estimation works when API times out
- [ ] Core Web Vitals (LCP, CLS, FCP) display correctly
- [ ] Enhanced GEO scoring detects Q&A patterns
- [ ] Entity extraction excludes common words
- [ ] Voice schema detection (FAQPage, HowTo, Speakable)

#### Phase 3 (Premium):
- [ ] SERP tracking finds known ranking pages
- [ ] Industry query generation works for all 13 industries
- [ ] Premium tier paywall blocks non-premium users
- [ ] Premium reports show SERP data in PDF

---

## 🚀 DEPLOYMENT GUIDE

### **Environment Setup**

**Required Environment Variables:**
```bash
# In your hosting environment (EC2, DigitalOcean, etc.):

# Supabase (already configured)
SUPABASE_URL=https://jcwvrrazmceccbzaythk.supabase.co
SUPABASE_KEY=eyJ...

# Optional: Google Custom Search (for premium SERP tracking)
GOOGLE_CSE_API_KEY=your_api_key_here
GOOGLE_CSE_CX=your_custom_search_engine_id

# Optional: Stripe (for premium tier payments)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### **Deployment Steps**

**Week 1 Deployment (Critical Fixes):**
```bash
# 1. Run database migrations
psql -h db.jcwvrrazmceccbzaythk.supabase.co -U postgres -d postgres < supabase-rate-limit-migration.sql

# 2. Upload enhanced analyze.py to CGI server
scp analyze.py user@server:/var/www/cgi-bin/analyze.py
chmod +x /var/www/cgi-bin/analyze.py

# 3. Test basic functionality
curl -X POST https://your-domain.com/cgi-bin/analyze.py \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "contact_email": "test@test.com"}'

# 4. Monitor logs for errors
tail -f /var/log/apache2/error.log
```

**Week 2 Deployment (Performance):**
```bash
# 1. Run performance migrations
psql -h db.jcwvrrazmceccbzaythk.supabase.co -U postgres -d postgres < supabase-performance-migration.sql

# 2. Update analyze.py with PageSpeed integration
scp analyze.py user@server:/var/www/cgi-bin/analyze.py

# 3. Update frontend (app.js) to show performance scores
scp app.js user@server:/var/www/html/app.js

# 4. Test PageSpeed API
# Should return performance scores
```

**Week 3-4 Deployment (Premium):**
```bash
# 1. Set environment variables
export GOOGLE_CSE_API_KEY=your_key
export GOOGLE_CSE_CX=your_cx

# 2. Deploy premium-enabled analyze.py
scp analyze.py user@server:/var/www/cgi-bin/analyze.py

# 3. Update report.py for premium PDF sections
scp report.py user@server:/var/www/cgi-bin/report.py

# 4. Test premium tier
# Add ?premium_token=test to request
```

---

## 📊 SUCCESS METRICS

### **Track These KPIs:**

**Technical Metrics:**
```
Week 1:
- Scan success rate: Target 90%+ (from 40%)
- Average response time: Target <3s
- Rate limit effectiveness: 0 abuse cases
- Cache hit rate: Target 60%+

Week 2:
- PageSpeed API success rate: Target 95%
- Performance score accuracy: Match Google's tool ±5%
- GEO scoring completeness: All checks pass

Week 3-4:
- Premium conversion rate: Target 5-10%
- SERP tracking accuracy: 100% for top 10 results
```



## 🐛 TROUBLESHOOTING GUIDE

### **Common Issues & Fixes**

**Issue: fetch_page() still fails on some sites**
```python
# Symptom: 403 errors even with retry logic
# Cause: Advanced bot detection (Akamai, PerimeterX)
# Solution: Add residential proxy support

# Quick fix:
# Use ScraperAPI (paid service) as fallback
# $49/month for 5,000 requests
```

**Issue: PageSpeed API rate limit hit**
```python
# Symptom: "Quota exceeded" error
# Cause: Too many API calls (25K/day limit)
# Solution: Increase cache window

# In should_rescan(), change:
cache_window = 72  # From 24 hours to 3 days
```

**Issue: SERP tracking returns no results**
```python
# Symptom: All queries return "not found"
# Cause: Custom Search Engine not configured correctly
# Solution: Verify CSE setup

# 1. Go to https://programmablesearchengine.google.com/
# 2. Ensure "Search the entire web" is enabled
# 3. Get correct CX ID from search engine page
```

**Issue: Database connection timeout**
```python
# Symptom: "timeout expired" on supabase_select
# Cause: Supabase free tier throttling
# Solution: Upgrade to Supabase Pro ($25/month)

# Or implement retry:
def supabase_select_with_retry(table, params, retries=3):
    for i in range(retries):
        try:
            return supabase_select(table, params)
        except Exception as e:
            if i < retries - 1:
                time.sleep(2 ** i)
                continue
            raise
```

---



## 🎯 IMPLEMENTATION CHECKLIST

### **Core Infrastructure Setup:**

- [ ] Supabase database running and accessible
- [ ] Cloudfare configured for static files
- [ ] Cloudfare with Python 3.9+ support
- [ ] Environment variables configured (see API Integration section)

### **API Keys & Credentials:**

- [ ] SUPABASE_URL and SUPABASE_KEY set
- [ ] OPENAI_API_KEY configured (for E-E-A-T analysis)
- [ ] ANTHROPIC_API_KEY configured (optional backup)
- [ ] GOOGLE_CSE_API_KEY and GOOGLE_CSE_CX configured (for SERP tracking)
- [ ] VALUESERP_API_KEY configured (optional, for enhanced SERP data)

### **Phase 1: Critical Production Fixes**

- [ ] Enhanced fetch_page() implemented (retry logic, User-Agent rotation, SSL handling)
- [ ] Rate limiting system implemented (5 scans/IP/24hr)
- [ ] Database migration completed (ip_address column added to scans table)
- [ ] Smart caching system implemented (12hr/24hr/72hr based on score)
- [ ] get_client_ip() function extracts IP from headers correctly
- [ ] All tests passing (50+ diverse websites tested)
- [ ] Success rate increased from 40% → 90%+

### **Phase 2: LLM & Performance Integration**

- [ ] Google PageSpeed Insights API integrated
- [ ] estimate_performance_score() fallback implemented
- [ ] Core Web Vitals (LCP, CLS, FCP) displaying in reports
- [ ] OpenAI E-E-A-T analysis integrated (analyze_content_quality_llm)
- [ ] Claude API fallback implemented
- [ ] Heuristic fallback working when both LLMs fail
- [ ] Database schema updated (performance columns added)
- [ ] Cost per scan verified at $0.03-0.05 range

### **Phase 3: SERP & Reporting**

- [ ] SERP tracking implemented (get_serp_position)
- [ ] Google Custom Search API working
- [ ] Industry query generation tested (all 13 industries)
- [ ] run_serp_analysis() returns competitive intelligence
- [ ] generate_serp_quick_wins() provides actionable recommendations
- [ ] ValueSERP fallback configured (if using)
- [ ] SERP results integrated into PDF reports with human-touch language

### **Report Quality Assurance:**

- [ ] PDF reports use conversational, non-technical language
- [ ] All recommendations explain WHY (business impact), not just WHAT
- [ ] E-E-A-T insights presented in human-readable format
- [ ] SERP analysis shows competitive context (who's ranking, why)
- [ ] Quick wins are specific and actionable
- [ ] Reports include positive feedback ("What's Working Well" section)
- [ ] Action plans are clear with time estimates
- [ ] No robotic or template-like language in reports

### **Testing Completed:**

- [ ] Test on 50+ diverse websites (various industries, sizes, CMS platforms)
- [ ] Verify fetch_page() retry logic on Cloudflare-protected sites
- [ ] Test rate limiting: 6th scan from same IP gets blocked
- [ ] Test caching: Second scan within 24hr returns cached results
- [ ] Verify PageSpeed API scores match Google's tool (±5 points)
- [ ] Test LLM analysis on 10 sites - verify quality and cost
- [ ] Test SERP tracking finds known ranking pages
- [ ] Verify total cost per scan is $0.03-0.05

### **Deployment:**

- [ ] All database migrations run successfully on production Supabase
- [ ] analyze.py deployed to CGI server (/var/www/cgi-bin/ or equivalent)
- [ ] report.py updated with human-touch report templates
- [ ] Frontend (app.js) updated to show performance, E-E-A-T, and SERP data
- [ ] Environment variables set on production server
- [ ] Error logging configured (Sentry or similar)
- [ ] Uptime monitoring enabled (UptimeRobot or similar)
- [ ] Cost monitoring dashboard set up (track API usage)

### **Documentation:**

- [ ] API integration guide for future developers
- [ ] Environment setup documentation
- [ ] Cost monitoring and optimization guide
- [ ] Troubleshooting guide for common issues
- [ ] Report writing guidelines documented

---

## 📞 SUPPORT & QUESTIONS

**If Antigravity Claude Encounters Issues:**

1. **Syntax Errors:** Check Python 3.9+ compatibility
2. **Database Errors:** Verify Supabase credentials still valid
3. **API Errors:** Check API quotas not exceeded
4. **Logic Errors:** Reference this document for context
5. **Unclear Requirements:** Default to simplest implementation

**Testing Commands:**
```bash
# Test analyze.py locally
python3 analyze.py

# Test with curl
curl -X POST http://localhost/cgi-bin/analyze.py \
  -H "Content-Type: application/json" \
  -d '{"url": "https://childrensrelief.org"}'

# Monitor logs
tail -f /var/log/apache2/error.log
```

---

## 🚀 READY TO BUILD

**This document contains:**
- ✅ Complete implementation specifications
- ✅ Production-ready code examples
- ✅ Database migrations
- ✅ Testing requirements
- ✅ Deployment instructions
- ✅ Troubleshooting guide
- ✅ Monetization strategy

**Antigravity Claude: You have everything needed to upgrade this prototype to a professional, production-ready application. Follow the 3-phase plan, implement each task sequentially, and test thoroughly. Good luck! 🎯**

---

**Document Version:** 1.0  
**Last Updated:** March 11, 2026  
**Prepared For:** Antigravity Claude Sonnet 4.6  
**Project:** Alianza Connects Search Readiness Platform Production Upgrade