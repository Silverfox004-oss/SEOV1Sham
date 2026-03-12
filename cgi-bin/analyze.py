#!/usr/bin/env python3
"""
Alianza Search Readiness Analyzer — CGI Backend
Fetches a URL, analyzes HTML for SEO/AI/Voice/Local search readiness,
stores results in SQLite + Supabase, returns JSON.
"""

import json
import os
import re
import sqlite3
import sys
import uuid
import urllib.request
import urllib.error
import urllib.parse
import ssl
import json
import os
import re
import sqlite3
import sys
import uuid
import urllib.request
import urllib.error
import urllib.parse
import ssl
import time
from html.parser import HTMLParser
from datetime import datetime, timezone, timedelta

# ============================================
# SUPABASE CONFIG
# ============================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://jcwvrrazmceccbzaythk.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impjd3ZycmF6bWNlY2NiemF5dGhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0ODUyMDksImV4cCI6MjA4ODA2MTIwOX0.-rSx5NwfwPmZHhSDLcMxntLBPRFdio8txKFWXIw16_g")

# Other API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
VALUESERP_API_KEY = os.environ.get("VALUESERP_API_KEY", "")

def supabase_request(path, method="GET", data=None, params=None):
    """Make a request to Supabase REST API. Returns parsed JSON or None on error."""
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    ctx = ssl.create_default_context()

    try:
        resp = urllib.request.urlopen(req, timeout=8, context=ctx)
        resp_body = resp.read().decode("utf-8")
        return json.loads(resp_body) if resp_body.strip() else None
    except Exception:
        return None


def supabase_upsert(table, data, on_conflict=""):
    """Upsert a row into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation,resolution=merge-duplicates",
    }
    if on_conflict:
        url += f"?on_conflict={on_conflict}"

    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context()

    try:
        resp = urllib.request.urlopen(req, timeout=8, context=ctx)
        resp_body = resp.read().decode("utf-8")
        return json.loads(resp_body) if resp_body.strip() else None
    except Exception:
        return None


def supabase_insert(table, data):
    """Insert a row into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context()

    try:
        resp = urllib.request.urlopen(req, timeout=8, context=ctx)
        resp_body = resp.read().decode("utf-8")
        return json.loads(resp_body) if resp_body.strip() else None
    except Exception:
        return None


def supabase_select(table, params):
    """Select rows from Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{urllib.parse.urlencode(params)}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    req = urllib.request.Request(url, headers=headers, method="GET")
    ctx = ssl.create_default_context()

    try:
        resp = urllib.request.urlopen(req, timeout=8, context=ctx)
        return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return []


def supabase_update(table, data, match_col, match_val):
    """Update rows in Supabase matching a condition."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{match_col}=eq.{urllib.parse.quote(str(match_val))}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="PATCH")
    ctx = ssl.create_default_context()

    try:
        resp = urllib.request.urlopen(req, timeout=8, context=ctx)
        resp_body = resp.read().decode("utf-8")
        return json.loads(resp_body) if resp_body.strip() else None
    except Exception:
        return None


# ============================================
# INDUSTRY DETECTION
# ============================================

INDUSTRY_KEYWORDS = {
    "hvac": ["hvac", "heating", "air conditioning", "furnace", "cooling", "heat pump", "ductwork", "thermostat"],
    "plumbing": ["plumbing", "plumber", "drain", "sewer", "water heater", "pipe", "faucet", "toilet"],
    "electrical": ["electrician", "electrical", "wiring", "circuit", "panel", "outlet", "lighting"],
    "landscaping": ["landscaping", "lawn care", "lawn", "mowing", "garden", "tree service", "irrigation", "weed control", "fertilization", "turf", "sod"],
    "dental": ["dental", "dentist", "orthodontist", "teeth", "oral", "braces", "implant", "cosmetic dentistry"],
    "legal": ["attorney", "lawyer", "law firm", "legal", "litigation", "personal injury", "criminal defense", "family law"],
    "medical": ["medical", "doctor", "physician", "clinic", "healthcare", "hospital", "patient", "surgery"],
    "accounting": ["accounting", "accountant", "cpa", "tax", "bookkeeping", "payroll", "audit", "financial planning"],
    "real_estate": ["real estate", "realtor", "property", "homes for sale", "mortgage", "listing", "broker"],
    "roofing": ["roofing", "roofer", "roof repair", "shingle", "gutter", "roof replacement"],
    "cleaning": ["cleaning", "maid", "janitorial", "carpet cleaning", "pressure washing", "house cleaning"],
    "pest_control": ["pest control", "exterminator", "termite", "rodent", "bed bug", "mosquito"],
    "auto": ["auto repair", "mechanic", "auto body", "oil change", "brake", "transmission", "car wash"],
}

def detect_industry(title, meta_desc, all_text, domain):
    """Detect business industry from page content."""
    combined = (title + " " + meta_desc + " " + all_text[:3000] + " " + domain).lower()
    scores = {}
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            count = combined.count(kw)
            if count > 0:
                score += count
        if score > 0:
            scores[industry] = score

    if scores:
        return max(scores, key=scores.get)
    return "unknown"


def extract_business_name(title, domain):
    """Extract business name from title tag."""
    if not title:
        return domain
    # Split on common delimiters and take the first part
    for sep in [" | ", " - ", " — ", " :: ", " >> "]:
        if sep in title:
            return title.split(sep)[0].strip()
    return title[:60].strip()


# ============================================
# OUTREACH EMAIL GENERATION
# ============================================

def generate_outreach_email(result, scan_type="self", competitor_result=None, primary_domain=None):
    """Generate personalized outreach email based on scan results.
    scan_type: 'self' for someone who scanned their own site, 'competitor' for a site scanned by a competitor.
    Returns dict with 'subject' and 'body' keys.
    """
    domain = urllib.parse.urlparse(result["url"]).netloc.lower().replace("www.", "")
    business_name = extract_business_name(result["summary"].get("title", ""), domain)
    scores = result["scores"]
    overall = round((scores["traditional_seo"] + scores["ai_search"] +
                     scores["voice_search"] + scores["local_search"]) / 4)

    # Collect failing checks (status == 'fail') across all categories
    failing_checks = []
    for category, checks in result.get("checks", {}).items():
        for check in checks:
            if check.get("status") == "fail":
                failing_checks.append(check.get("label", ""))

    top_fails = failing_checks[:3]
    fails_text = ""
    if top_fails:
        fails_text = "\n".join(f"  - {f}" for f in top_fails)

    if scan_type == "self":
        subject = f"Your Search Readiness Score: {overall}/100 — Here's How to Improve"
        body = f"""Hi {business_name} team,

You just ran a Search Readiness scan on your website — and we wanted to reach out with a quick breakdown of what we found.

Your scores:
  - Traditional SEO: {scores['traditional_seo']}/100
  - AI Search Readiness: {scores['ai_search']}/100
  - Voice Search: {scores['voice_search']}/100
  - Local Search: {scores['local_search']}/100

Overall Score: {overall}/100

The good news? Most of these issues are fixable — and the impact on your business can be huge.
"""
        if top_fails:
            body += f"""Here are the top things holding your site back right now:
{fails_text}

"""
        body += f"""At Alianza Connects, we help home service and local businesses like yours fix exactly these kinds of problems — fast.

Our plans:
  - Foundations ($1,500/mo): Fix the basics — on-page SEO, local schema, Google Business Profile, citations.
  - Growth ($2,500/mo): Everything in Foundations PLUS AI search optimization, content strategy, and voice search setup.

Most of our clients see a noticeable increase in calls and web traffic within 60 days.

Want to set up a free 20-minute call to talk through your results? Just reply to this email or grab time here.

Best,
The Alianza Connects Team
hello@alianzaconnects.com | alianzaconnects.com
"""

    else:  # competitor scan
        competitor_score = 0
        competitor_domain = primary_domain or ""
        if competitor_result:
            c_scores = competitor_result["scores"]
            competitor_score = round((c_scores["traditional_seo"] + c_scores["ai_search"] +
                                      c_scores["voice_search"] + c_scores["local_search"]) / 4)
            competitor_domain = urllib.parse.urlparse(competitor_result["url"]).netloc.lower().replace("www.", "")

        subject = f"Your competitor is watching — and they scored {competitor_score}/100 vs your {overall}/100"
        score_diff = competitor_score - overall
        if score_diff > 0:
            diff_text = f"Right now, they're ahead of you by {score_diff} points."
        elif score_diff < 0:
            diff_text = f"You're actually ahead by {abs(score_diff)} points — but they're clearly paying attention to your business."
        else:
            diff_text = "You're tied — but they're actively researching how to get ahead of you."

        body = f"""Hi {business_name} team,

Here's something you should know: a competitor in your industry just scanned your website using our Search Readiness tool.

{diff_text}

Your search readiness scores:
  - Traditional SEO: {scores['traditional_seo']}/100
  - AI Search Readiness: {scores['ai_search']}/100
  - Voice Search: {scores['voice_search']}/100
  - Local Search: {scores['local_search']}/100

Your Overall Score: {overall}/100
"""
        if competitor_result:
            c_scores = competitor_result["scores"]
            body += f"""Their Overall Score: {competitor_score}/100
"""
        if top_fails:
            body += f"""
Areas where you're falling behind:
{fails_text}

"""
        body += f"""The businesses that win in local search aren't the biggest — they're the ones that show up first. And right now, there's a gap we can help you close.

Alianza Connects helps local businesses fix their search presence fast:
  - Foundations ($1,500/mo): SEO basics, local schema, Google Business Profile.
  - Growth ($2,500/mo): AI search, voice optimization, content strategy.

Want to see your full report and talk through a game plan? Reply here or grab a free 20-minute slot.

Best,
The Alianza Connects Team
hello@alianzaconnects.com | alianzaconnects.com
"""

    return {"subject": subject, "body": body}


# ============================================
# SUPABASE SYNC
# ============================================

def sync_to_supabase(result, parser, scan_type="self", primary_domain=None,
                     competitor_domain=None, competitor_result=None,
                     contact_name="", contact_email="", contact_phone="", contact_role="",
                     client_ip="unknown"):
    """Write scan results to Supabase: upsert lead, insert scan, insert checks.

    scan_type: 'self' (default) or 'competitor'.
    primary_domain: the domain that initiated the scan (used when scan_type='competitor').
    competitor_domain: the domain being scanned as a competitor.
    competitor_result: the result dict for the competing site (used to build outreach).
    """
    try:
        domain = urllib.parse.urlparse(result["url"]).netloc.lower().replace("www.", "")
        now = datetime.now(timezone.utc).isoformat()
        overall = round(
            (result["scores"]["traditional_seo"] + result["scores"]["ai_search"] +
             result["scores"]["voice_search"] + result["scores"]["local_search"]) / 4
        )
        industry = detect_industry(
            result["summary"].get("title", ""),
            result["summary"].get("meta_description", ""),
            getattr(parser, "all_text", ""),
            domain
        )
        business_name = extract_business_name(result["summary"].get("title", ""), domain)

        # Generate outreach email based on scan type (only generate the relevant type)
        outreach_self = None
        outreach_competitor = None

        if scan_type == "self":
            outreach_self_data = generate_outreach_email(result, scan_type="self")
            outreach_self = json.dumps(outreach_self_data)
        elif scan_type == "competitor":
            outreach_competitor_data = generate_outreach_email(
                result, scan_type="competitor",
                competitor_result=competitor_result,
                primary_domain=primary_domain
            )
            outreach_competitor = json.dumps(outreach_competitor_data)

        # 1. Check if lead exists
        existing = supabase_select("leads", {
            "select": "id,scan_count",
            "domain": f"eq.{domain}",
        })

        if existing and len(existing) > 0:
            lead = existing[0]
            lead_id = lead["id"]
            new_count = (lead.get("scan_count", 0) or 0) + 1
            update_data = {
                "scan_count": new_count,
                "last_seen": now,
                "latest_overall_score": overall,
                "latest_seo_score": result["scores"]["traditional_seo"],
                "latest_ai_score": result["scores"]["ai_search"],
                "latest_voice_score": result["scores"]["voice_search"],
                "latest_local_score": result["scores"]["local_search"],
                "industry": industry,
                "business_name": business_name,
                "contact_name": contact_name,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "contact_role": contact_role,
            }
            # Only include the relevant outreach field
            if scan_type == "self":
                update_data["outreach_self"] = outreach_self
            elif scan_type == "competitor":
                update_data["outreach_competitor"] = outreach_competitor
            # If this is a competitor scan, mark source and scanned_by
            if scan_type == "competitor":
                update_data["source"] = "competitor"
                if primary_domain:
                    update_data["scanned_by_domain"] = primary_domain
            supabase_update("leads", update_data, "domain", domain)
        else:
            # Insert new lead
            insert_data = {
                "domain": domain,
                "business_name": business_name,
                "industry": industry,
                "status": "new",
                "scan_count": 1,
                "first_seen": now,
                "last_seen": now,
                "latest_overall_score": overall,
                "latest_seo_score": result["scores"]["traditional_seo"],
                "latest_ai_score": result["scores"]["ai_search"],
                "latest_voice_score": result["scores"]["voice_search"],
                "latest_local_score": result["scores"]["local_search"],
                "contact_name": contact_name,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "contact_role": contact_role,
            }
            # Only include the relevant outreach field
            if scan_type == "self":
                insert_data["outreach_self"] = outreach_self
            elif scan_type == "competitor":
                insert_data["outreach_competitor"] = outreach_competitor
            # Tag competitor leads with source and who scanned them
            if scan_type == "competitor":
                insert_data["source"] = "competitor"
                if primary_domain:
                    insert_data["scanned_by_domain"] = primary_domain
            lead_result = supabase_insert("leads", insert_data)
            lead_id = lead_result[0]["id"] if lead_result else None

        # 2. Insert scan record
        scan_data = {
            "report_id": result["report_id"],
            "lead_id": lead_id,
            "ip_address": client_ip,
            "domain": domain,
            "url": result["url"],
            "final_url": result.get("final_url", ""),
            "scanned_at": now,
            "response_time_ms": int(result.get("response_time", 0) * 1000),
            "overall_score": overall,
            "seo_score": result["scores"]["traditional_seo"],
            "ai_score": result["scores"]["ai_search"],
            "voice_score": result["scores"]["voice_search"],
            "local_score": result["scores"]["local_search"],
            "scan_type": scan_type,
            "primary_domain": primary_domain or "",
            "competitor_domain": competitor_domain or "",
            "title": result["summary"].get("title", "")[:500],
            "meta_description": result["summary"].get("meta_description", "")[:500],
            "word_count": result["summary"].get("word_count", 0),
            "images_total": result["summary"].get("images", 0),
            "images_with_alt": getattr(parser, "images_with_alt", 0),
            "schema_types": result["summary"].get("schema_types", []),
            "is_https": result["summary"].get("is_https", False),
            "has_viewport": bool(getattr(parser, "meta_viewport", "")),
            "has_canonical": bool(getattr(parser, "canonical", "")),
            "has_og_tags": bool(getattr(parser, "og_title", "") or getattr(parser, "og_description", "")),
            "has_twitter_card": bool(getattr(parser, "twitter_card", "")),
            "has_json_ld": len(getattr(parser, "json_ld_blocks", [])) > 0,
            "has_local_schema": any("LocalBusiness" in str(b) for b in getattr(parser, "json_ld_blocks", [])),
            "has_faq_schema": any("FAQPage" in str(b) for b in getattr(parser, "json_ld_blocks", [])),
            "has_phone": getattr(parser, "phone_in_content", False),
            "has_address": getattr(parser, "address_in_content", False),
            "has_maps_embed": getattr(parser, "has_maps_embed", False),
            "has_contact_link": getattr(parser, "has_contact_link", False),
            "full_report": result,
        }
        scan_result = supabase_insert("scans", scan_data)
        scan_id = scan_result[0]["id"] if scan_result else None

        # 3. Insert individual checks
        if scan_id:
            for category, checks in result.get("checks", {}).items():
                for check in checks:
                    supabase_insert("scan_checks", {
                        "scan_id": scan_id,
                        "report_id": result["report_id"],
                        "domain": domain,
                        "category": category,
                        "check_label": check.get("label", ""),
                        "status": check.get("status", "warn"),
                        "detail": check.get("detail", ""),
                        "fix_title": check.get("fix_title", "") or "",
                        "fix_why": check.get("fix_why", "") or "",
                        "impact": check.get("impact", "") or "",
                        "checked_at": now,
                    })
    except Exception:
        # Supabase sync should never break the scanner response
        pass


# ============================================
# HTML PARSER
# ============================================

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.meta_description = ""
        self.meta_viewport = ""
        self.meta_robots = ""
        self.canonical = ""
        self.og_title = ""
        self.og_description = ""
        self.og_image = ""
        self.twitter_card = ""
        self.headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}
        self.current_heading = None
        self.current_heading_text = ""
        self.images_total = 0
        self.images_with_alt = 0
        self.internal_links = 0
        self.external_links = 0
        self.has_contact_link = False
        self.json_ld_blocks = []
        self.schema_types = []
        self.in_json_ld = False
        self.json_ld_text = ""
        self.semantic_tags = set()
        self.semantic_tag_list = {"article", "section", "nav", "main", "header", "footer", "aside"}
        self.word_count = 0
        self.paragraph_count = 0
        self.in_p = False
        self.p_text = ""
        self.all_text = ""
        self.has_faq_heading = False
        self.question_headings = 0
        self.hreflang_tags = []
        self.geo_meta = False
        self.has_maps_embed = False
        self.speakable_schema = False
        self.last_modified_meta = ""
        self.date_meta = ""
        self.base_url = ""
        self.phone_in_content = False
        self.address_in_content = False
        self.has_schema_scripts = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "title":
            self.in_title = True
            self.title = ""

        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")

            if name == "description":
                self.meta_description = content
            elif name == "viewport":
                self.meta_viewport = content
            elif name == "robots":
                self.meta_robots = content
            elif name == "geo.position" or name == "geo.region" or name == "icbm":
                self.geo_meta = True
            elif name == "last-modified" or name == "date":
                self.date_meta = content
            elif prop == "og:title":
                self.og_title = content
            elif prop == "og:description":
                self.og_description = content
            elif prop == "og:image":
                self.og_image = content
            elif name == "twitter:card" or prop == "twitter:card":
                self.twitter_card = content

        elif tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            href = attrs_dict.get("href", "")
            hreflang = attrs_dict.get("hreflang", "")
            if rel == "canonical":
                self.canonical = href
            if hreflang:
                self.hreflang_tags.append(hreflang)

        elif tag in self.headings:
            self.current_heading = tag
            self.current_heading_text = ""

        elif tag == "img":
            self.images_total += 1
            alt = attrs_dict.get("alt", None)
            if alt is not None and alt.strip():
                self.images_with_alt += 1

        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href:
                if href.startswith("http") and self.base_url and self.base_url not in href:
                    self.external_links += 1
                else:
                    self.internal_links += 1
                if "/contact" in href.lower() or "contact" in href.lower():
                    self.has_contact_link = True

        elif tag == "script":
            stype = attrs_dict.get("type", "").lower()
            if stype == "application/ld+json":
                self.in_json_ld = True
                self.json_ld_text = ""

        elif tag == "iframe":
            src = attrs_dict.get("src", "")
            if "google.com/maps" in src or "maps.google" in src:
                self.has_maps_embed = True

        elif tag == "p":
            self.in_p = True
            self.p_text = ""

        if tag in self.semantic_tag_list:
            self.semantic_tags.add(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

        elif tag in self.headings and self.current_heading == tag:
            text = self.current_heading_text.strip()
            self.headings[tag].append(text)
            # Check for question patterns
            if text and ("?" in text or text.lower().startswith(("what ", "how ", "why ", "when ", "where ", "who ", "can ", "do ", "does ", "is ", "are "))):
                self.question_headings += 1
                if tag in ("h2", "h3"):
                    self.has_faq_heading = True
            self.current_heading = None

        elif tag == "script" and self.in_json_ld:
            self.in_json_ld = False
            try:
                parsed = json.loads(self.json_ld_text)
                self.json_ld_blocks.append(parsed)
                self.has_schema_scripts += 1
            except (json.JSONDecodeError, ValueError):
                pass

        elif tag == "p" and self.in_p:
            self.in_p = False
            text = self.p_text.strip()
            if len(text) > 20:
                self.paragraph_count += 1
                words = text.split()
                self.word_count += len(words)
                self.all_text += " " + text

    def handle_data(self, data):
        if self.in_title:
            self.title += data

        if self.current_heading:
            self.current_heading_text += data

        if self.in_json_ld:
            self.json_ld_text += data

        if self.in_p:
            self.p_text += data

        # Also accumulate text for phone/address detection
        stripped = data.strip()
        if stripped:
            self.all_text += " " + stripped


# (Caching and rate-limiting removed for simplicity — every scan is always fresh)


# ============================================
# API INTEGRATIONS (PageSpeed, LLM, SERP)
# ============================================

def get_pagespeed_scores(url):
    """
    Fetch mobile performance metrics from Google PageSpeed Insights API.
    Provides strict 0-100 scores + Core Web Vitals.
    Falls back to a heuristic estimation if API key is missing or call fails.
    """
    api_key = os.environ.get("GOOGLE_PSI_API_KEY", "")
    
    fallback = {
        "score": 65,  # Heuristic fallback
        "metrics": {
            "lcp": "2.5s",
            "cls": "0.1",
            "fcp": "1.8s"
        },
        "from_api": False
    }

    if not api_key:
        return fallback

    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={urllib.parse.quote(url)}&strategy=mobile&key={api_key}"
    
    try:
        req = urllib.request.Request(api_url)
        ctx = ssl.create_default_context()
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = json.loads(resp.read().decode("utf-8"))
        
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        metrics = lighthouse.get("audits", {})
        
        score = int(categories.get("performance", {}).get("score", 0.65) * 100)
        
        lcp = metrics.get("largest-contentful-paint", {}).get("displayValue", "Unknown")
        cls = metrics.get("cumulative-layout-shift", {}).get("displayValue", "Unknown")
        fcp = metrics.get("first-contentful-paint", {}).get("displayValue", "Unknown")
        
        return {
            "score": score,
            "metrics": {"lcp": lcp, "cls": cls, "fcp": fcp},
            "from_api": True
        }
    except Exception as e:
        print(f"PageSpeed API Error: {e}", file=sys.stderr)
        return fallback


def calculate_geo_ai_readiness(html, parser, title):
    """
    Implements 9 GEO-optim Research Strategies (Princeton/CMU 2023)
    plus original AI heuristics to calculate generative engine readiness.
    Produces a 0-100 score + specific checks.
    """
    checks = []
    points = 0
    text = parser.all_text
    
    # Check 1: Cite Sources (External authority links)
    if parser.external_links > 0:
        points += 10
        checks.append({
            "label": "External Citations", "status": "pass",
            "detail": f"Found {parser.external_links} external links to reference sources",
            "fix_title": None, "fix_why": None, "impact": "High"
        })
    else:
        checks.append({
            "label": "External Citations", "status": "warn",
            "detail": "No external links found",
            "fix_title": "Cite reputable sources",
            "fix_why": "Linking to authoritative domains (gov, edu) signals trust to AI models.",
            "impact": "High"
        })

    # Check 2: Quotations (`<blockquote>`)
    if "<blockquote>" in html.lower() or '"' in text[:1000]:
        points += 8
        checks.append({"label": "Quotations", "status": "pass", "detail": "Contains quotes or blockquotes"})
    else:
        checks.append({
            "label": "Quotations", "status": "warn", "detail": "No clear quotes found",
            "fix_title": "Add expert quotes", "fix_why": "Including quotes adds authoritative voices which AI engines prefer.",
            "impact": "Medium"
        })

    # Check 3: Statistics Emphasis
    if re.search(r'\d+%|\d+\s*(percent|million|billion|\$|data|research)', text, re.IGNORECASE):
        points += 10
        checks.append({"label": "Statistics Presence", "status": "pass", "detail": "Contains data points and numbers"})
    else:
        checks.append({
            "label": "Statistics Presence", "status": "warn", "detail": "No clear data/stats found",
            "fix_title": "Include relevant statistics", "fix_why": "AI engines prioritize content backed by data and numbers.",
            "impact": "High"
        })

    # Check 4: Easy-to-understand (Readability)
    readability = calculate_readability(text)
    if readability["avg_sentence_len"] <= 20 and readability["avg_sentence_len"] > 0:
        points += 10
        checks.append({"label": "Readability", "status": "pass", "detail": f"Avg sentence length: {readability['avg_sentence_len']} words"})
    else:
        checks.append({
            "label": "Readability", "status": "warn", "detail": f"Avg sentence length: {readability['avg_sentence_len']} words",
            "fix_title": "Simplify sentence structures", "fix_why": "Generative engines favor clear, concise sentences (under 20 words avg).",
            "impact": "Medium"
        })

    # Check 5: Vocabulary Richness (Type-Token Ratio)
    words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
    ttr = len(set(words)) / len(words) if words else 0
    if ttr >= 0.4:
        points += 7
        checks.append({"label": "Vocabulary Richness", "status": "pass", "detail": f"Type-Token Ratio: {ttr:.2f} (Good diversity)"})
    else:
        checks.append({
            "label": "Vocabulary Richness", "status": "warn", "detail": f"Type-Token Ratio: {ttr:.2f} (Somewhat repetitive)",
            "fix_title": "Use more diverse vocabulary", "fix_why": "Repetitive phrasing hurts LLM understanding. Use synonyms and clear terminology.",
            "impact": "Low"
        })

    # Check 6: Argumentative/Persuasive Structure (Calls to action)
    if re.search(r'\b(in conclusion|to summarize|therefore|because|schedule|call today|contact us)\b', text, re.IGNORECASE):
        points += 8
        checks.append({"label": "Persuasive Structure", "status": "pass", "detail": "Contains clear conclusions/CTAs"})

    # Check 7: Voice/Q&A patterns (Original heuristics)
    if parser.has_faq_heading or parser.question_headings > 0:
        points += 25
        checks.append({"label": "Q&A Patterns", "status": "pass", "detail": f"Found {parser.question_headings} conversational question headings"})
    else:
        checks.append({
            "label": "Q&A Patterns", "status": "fail", "detail": "No conversational question formats found",
            "fix_title": "Add an FAQ section", "fix_why": "AI engines use Q&A formats to directly answer user queries.",
            "impact": "High"
        })

    # Check 8: Voice Schema
    has_voice_schema = any("faqpage" in st.lower() or "howto" in st.lower() or "speakable" in st.lower() for st in parser.schema_types if isinstance(st, str))
    if has_voice_schema:
        points += 22
        checks.append({"label": "Voice Schema", "status": "pass", "detail": "Found FAQ/HowTo/Speakable schema"})

    return min(100, points), checks


def analyze_content_quality_llm(text, title, industry):
    """
    Sends content to GPT-4o-mini to calculate E-E-A-T (Experience, Expertise, 
    Authority, Trust) sub-scores and provide strict, evidence-based recommendations.
    """
    if not OPENAI_API_KEY:
        return {
            "experience_score": 60, "expertise_score": 65,
            "authority_score": 50, "trust_score": 75,
            "strengths": ["Basic content structure exists", "Mobile friendly baseline"],
            "weaknesses": ["Lacks author credentials", "Generic phrasing limits authority"],
            "recommendations": ["Add specific case studies", "Include team bios to build trust"],
            "from_api": False
        }

    # Truncate text to fit context window comfortably
    truncated_text = text[:15000]

    prompt = f"""
    You are an elite, highly critical technical SEO and E-E-A-T auditor evaluating a small business website in the '{industry}' industry.
    Google's E-E-A-T guidelines (Experience, Expertise, Authoritativeness, Trustworthiness) are critical for modern search viability.
    
    Evaluate the following website based ONLY on the evidence provided in the text. Be strict. Do not inflate scores.
    If there is no explicit proof of experience (e.g., "years in business", photos of actual work), score Experience low.
    If there are no clear author credentials or industry certifications, score Expertise low.
    If there are no clear trust signals (e.g., physical address, specific guarantees, visible phone number, policies), score Trust low.

    Title: {title}
    Content Snippet: {truncated_text}

    Return ONLY a valid JSON object with absolute NO markdown formatting (no ```json):
    {{
        "experience_score": [0-100],
        "expertise_score": [0-100],
        "authority_score": [0-100],
        "trust_score": [0-100],
        "strengths": ["string", "string"],
        "weaknesses": ["string", "string"],
        "recommendations": ["string", "string"]
    }}
    Make strengths, weaknesses, and recommendations highly professional, specific to this exact business, and actionable. Do not use generic filler.
    """

    try:
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            data=json.dumps({
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": { "type": "json_object" }
            }).encode("utf-8")
        )
        ctx = ssl.create_default_context()
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        resp_data = json.loads(resp.read().decode("utf-8"))
        
        content = resp_data["choices"][0]["message"]["content"]
        result = json.loads(content)
        result["from_api"] = True
        return result
    except Exception as e:
        print(f"OpenAI E-E-A-T Error: {e}", file=sys.stderr)
        return {
            "experience_score": 60, "expertise_score": 60,
            "authority_score": 60, "trust_score": 60,
            "strengths": ["Content parsed successfully"],
            "weaknesses": ["Unable to run deep AI analysis at this time"],
            "recommendations": ["Try scanning again later for full E-E-A-T breakdown"],
            "from_api": False
        }


def generate_serp_test_queries(industry, business_name, domain, title="", text=""):
    """
    Uses OpenAI to analyze the actual website content and generate 3 highly-relevant, 
    high-intent localized search queries that this specific business should be ranking for.
    Always appends a 4th query which is the branded search term.
    """
    brand = business_name if business_name != domain else domain.split('.')[0]
    fallback_queries = [f"{industry} services near me", f"best {industry} company", brand]

    if not OPENAI_API_KEY:
        return fallback_queries

    prompt = f"""
    You are an expert SEO strategist. Analyze the following local business website and generate EXACTLY 3 high-intent, high-value search queries (keywords) that potential customers would type into Google to find THIS SPECIFIC business.
    
    The keywords MUST be highly relevant to their exact niche, service offerings, and geographic location if mentioned in the text.
    Do NOT generate generic industry terms if the business specializes in something specific.
    Example: If it's a pediatric dentist in Austin, output "pediatric dentist austin tx", NOT just "dentist near me".
    
    Website Domain: {domain}
    Website Title: {title}
    Website Content Snippet: {text[:5000]}
    
    Return ONLY a valid JSON array of 3 strings, with absolutely NO markdown formatting (no ```json):
    ["keyword 1", "keyword 2", "keyword 3"]
    """

    try:
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            data=json.dumps({
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }).encode("utf-8")
        )
        ctx = ssl.create_default_context()
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        resp_data = json.loads(resp.read().decode("utf-8"))
        
        content = resp_data["choices"][0]["message"]["content"]
        queries = json.loads(content)
        
        if isinstance(queries, list) and len(queries) > 0:
            # Clean up and append brand
            queries = [str(q).lower().strip() for q in queries[:3]]
            if brand.lower() not in queries:
                queries.append(brand.lower())
            return queries
        else:
            return fallback_queries
    except Exception as e:
        print(f"OpenAI SERP Query Error: {e}", file=sys.stderr)
        return fallback_queries



def run_serp_analysis(domain, industry, business_name, title="", text=""):
    """
    Check rankings using ValueSerp API.
    Returns positions for test queries.
    """
    if not VALUESERP_API_KEY:
        return {
            "enabled": False,
            "message": "ValueSerp API not configured. Set VALUESERP_API_KEY env var.",
            "rankings": [],
            "visibility_score": 0
        }

    queries = generate_serp_test_queries(industry, business_name, domain, title, text)
    rankings = []
    page1_count = 0

    for query in queries:
        try:
            params = urllib.parse.urlencode({
                "api_key": VALUESERP_API_KEY,
                "q": query,
                "num": 10,
                "output": "json"
            })
            url = f"https://api.valueserp.com/search?{params}"
            req = urllib.request.Request(url)
            ctx = ssl.create_default_context()
            resp = urllib.request.urlopen(req, timeout=10, context=ctx)
            data = json.loads(resp.read().decode("utf-8"))

            organic = data.get("organic_results", [])
            position = 999  # Not found on page 1
            top_competitors = []

            for item in organic:
                item_pos = item.get("position", 999)
                item_domain = item.get("domain", "")
                if not item_domain:
                    item_domain = urllib.parse.urlparse(item.get("link", "")).netloc.lower()
                item_domain = item_domain.lower().replace("www.", "")

                # Collect top competitors (first 3 that aren't us)
                if len(top_competitors) < 3 and item_domain != domain:
                    top_competitors.append(item_domain)

                # Find our position
                if item_domain == domain and position == 999:
                    position = item_pos

            if position <= 10:
                page1_count += 1

            rankings.append({
                "query": query,
                "position": position if position != 999 else "Not Top 10",
                "competitors": top_competitors[:2]
            })

        except Exception as e:
            print(f"SERP Error for '{query}': {e}", file=sys.stderr)
            rankings.append({
                "query": query,
                "position": "Error",
                "competitors": []
            })

        # Respect API rate limits
        time.sleep(0.3)

    visibility = int((page1_count / len(queries)) * 100) if queries else 0

    return {
        "enabled": True,
        "rankings": rankings,
        "visibility_score": visibility
    }


# ============================================
# ANALYSIS ENGINE
# ============================================

def fetch_page(url):
    """Fetch URL with retries, UA rotation, and exponential backoff. Returns (html, response_time, headers, final_url)"""
    import time
    import ssl
    import random

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]

    max_retries = 3
    base_delay = 1.0

    html_bytes = None
    elapsed = 0
    headers = {}
    final_url = url
    resp = None
    last_error = None

    for attempt in range(max_retries):
        try:
            ua = random.choice(USER_AGENTS)
            req_headers = {
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "identity",
                "Cache-Control": "no-cache",
                "Upgrade-Insecure-Requests": "1"
            }

            req = urllib.request.Request(url, headers=req_headers)
            
            # Default strict context
            ctx = ssl.create_default_context()
            
            # On retry 2, try relaxing SSL if that was the issue
            if attempt == 1 and isinstance(last_error, urllib.error.URLError) and "CERTIFICATE_VERIFY_FAILED" in str(last_error):
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

            start = time.time()
            resp = urllib.request.urlopen(req, timeout=15, context=ctx)
            html_bytes = resp.read(800000)  # max 800KB
            elapsed = time.time() - start
            headers = dict(resp.headers)
            final_url = resp.url
            break  # Success

        except urllib.error.HTTPError as e:
            last_error = e
            # Don't retry 404s
            if e.code in (404, 410):
                raise Exception(f"HTTP {e.code}: Page not found")
            # For 403/429/503/500, retry with backoff
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0.1, 0.5)
                time.sleep(delay)
            else:
                raise Exception(f"Failed after {max_retries} attempts. Last error: HTTP {e.code}")
                
        except (urllib.error.URLError, Exception) as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0.1, 0.5)
                time.sleep(delay)
            else:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")

    if not html_bytes:
        raise Exception("Empty response received")

    # Try to detect encoding
    content_type = headers.get("Content-Type", "")
    encoding = "utf-8"
    if "charset=" in content_type.lower():
        try:
            encoding = content_type.lower().split("charset=")[-1].strip().split(";")[0]
        except Exception:
            pass

    try:
        html = html_bytes.decode(encoding, errors="replace")
    except (LookupError, UnicodeDecodeError):
        html = html_bytes.decode("utf-8", errors="replace")

    return html, elapsed, headers, final_url


def analyze_schema(json_ld_blocks):
    """Analyze JSON-LD structured data blocks."""
    schema_types = []
    has_local_business = False
    has_organization = False
    has_faq_schema = False
    has_howto_schema = False
    has_speakable = False
    nap_in_schema = {"name": False, "address": False, "phone": False}
    schema_completeness = 0

    def walk_schema(obj):
        nonlocal has_local_business, has_organization, has_faq_schema, has_howto_schema, has_speakable, nap_in_schema, schema_completeness

        if isinstance(obj, list):
            for item in obj:
                walk_schema(item)
            return

        if not isinstance(obj, dict):
            return

        stype = obj.get("@type", "")
        if isinstance(stype, list):
            stypes = stype
        else:
            stypes = [stype]

        for t in stypes:
            t_lower = t.lower()
            if t and t not in schema_types:
                schema_types.append(t)

            if "localbusiness" in t_lower or "homeandconstructionbusiness" in t_lower or any(x in t_lower for x in ["plumber", "hvac", "electrician", "dentist", "lawyer", "attorney", "physician", "restaurant", "store"]):
                has_local_business = True
            if "organization" in t_lower:
                has_organization = True
            if "faqpage" in t_lower:
                has_faq_schema = True
            if "howto" in t_lower:
                has_howto_schema = True

        if "speakable" in obj:
            has_speakable = True

        # Check NAP
        if obj.get("name"):
            nap_in_schema["name"] = True
        if obj.get("address") or obj.get("areaServed"):
            nap_in_schema["address"] = True
        if obj.get("telephone") or obj.get("phone"):
            nap_in_schema["phone"] = True

        # Recurse into nested objects
        for key, val in obj.items():
            if isinstance(val, (dict, list)):
                walk_schema(val)

    for block in json_ld_blocks:
        walk_schema(block)

    # Count completeness
    total_fields = 0
    filled_fields = 0
    for block in json_ld_blocks:
        if isinstance(block, dict):
            for key, val in block.items():
                if not key.startswith("@"):
                    total_fields += 1
                    if val:
                        filled_fields += 1

    if total_fields > 0:
        schema_completeness = round((filled_fields / total_fields) * 100)

    return {
        "types": schema_types,
        "has_local_business": has_local_business,
        "has_organization": has_organization,
        "has_faq_schema": has_faq_schema,
        "has_howto_schema": has_howto_schema,
        "has_speakable": has_speakable,
        "nap": nap_in_schema,
        "completeness": schema_completeness,
        "count": len(json_ld_blocks),
    }


def check_phone_address(text):
    """Detect phone numbers and addresses in text content."""
    phone_pattern = re.compile(r'[\(]?\d{3}[\)]?[\s\-\.]?\d{3}[\s\-\.]?\d{4}')
    # Simple address: number + street name patterns
    address_pattern = re.compile(r'\d+\s+[\w\s]+(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Court|Ct|Suite|Ste|Highway|Hwy)\b', re.IGNORECASE)

    has_phone = bool(phone_pattern.search(text))
    has_address = bool(address_pattern.search(text))

    return has_phone, has_address


def calculate_readability(text):
    """Simple readability check: average sentence length and word length."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    if not sentences:
        return {"avg_sentence_len": 0, "simple_words_pct": 0}

    total_words = 0
    short_words = 0
    for s in sentences:
        words = s.split()
        total_words += len(words)
        for w in words:
            if len(w) <= 6:
                short_words += 1

    avg_sentence_len = total_words / len(sentences) if sentences else 0
    simple_pct = (short_words / total_words * 100) if total_words > 0 else 0

    return {
        "avg_sentence_len": round(avg_sentence_len, 1),
        "simple_words_pct": round(simple_pct),
        "sentence_count": len(sentences),
    }


def is_clean_url(url):
    """Check if URL is clean (no query params, no fragments, readable path)."""
    parsed = urllib.parse.urlparse(url)
    has_params = bool(parsed.query)
    has_ugly = bool(re.search(r'[?&=#]', parsed.path))
    has_extension = bool(re.search(r'\.(php|asp|aspx|jsp|cgi)\b', parsed.path, re.IGNORECASE))
    return not has_params and not has_ugly and not has_extension


def run_analysis(url, scan_type="self", primary_domain=None, competitor_domain=None,
                 competitor_result=None, contact_name="", contact_email="",
                 contact_phone="", contact_role="", client_ip="unknown"):
    """Main analysis function. Returns scores and checks.

    scan_type: 'self' or 'competitor'. Passed through to Supabase sync.
    primary_domain: when scan_type='competitor', the domain that initiated the scan.
    competitor_domain: the domain being analysed as a competitor.
    competitor_result: pre-computed result for the primary site (used to enrich outreach).
    """

    # Fetch page
    html, response_time, headers, final_url = fetch_page(url)

    # Parse
    parser = PageParser()
    parser.base_url = urllib.parse.urlparse(url).netloc
    parser.feed(html)

    # Analyze schema
    schema = analyze_schema(parser.json_ld_blocks)

    # Check phone/address in content
    has_phone, has_address = check_phone_address(parser.all_text)
    # Store on parser so sync_to_supabase can access them
    parser.phone_in_content = has_phone
    parser.address_in_content = has_address

    # Readability
    readability = calculate_readability(parser.all_text)

    # HTTPS check
    is_https = url.lower().startswith("https://")

    # Clean URL
    clean_url = is_clean_url(final_url)

    # Last modified
    last_modified = headers.get("Last-Modified", "") or parser.date_meta

    # Heading hierarchy check
    def check_heading_hierarchy():
        """Check if headings follow proper nesting (no skipped levels)."""
        used = []
        for level in range(1, 7):
            tag = f"h{level}"
            if parser.headings[tag]:
                used.append(level)
        if not used:
            return True
        for i in range(1, len(used)):
            if used[i] - used[i-1] > 1:
                return False
        return True

    proper_hierarchy = check_heading_hierarchy()

    # Location keywords in title/headings
    location_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', parser.title + " " + " ".join(parser.headings.get("h1", [])))

    # Service area mentions
    all_text_str = str(parser.all_text)
    service_area_pattern = re.compile(r'(serving|service area|we serve|available in|locations?|areas? served)', re.IGNORECASE)
    has_service_area = bool(service_area_pattern.search(all_text_str[:5000]))

    # Industry Detection
    industry = detect_industry(
        parser.title,
        parser.meta_description,
        parser.all_text,
        urllib.parse.urlparse(url).netloc.lower()
    )
    business_name = extract_business_name(parser.title, urllib.parse.urlparse(url).netloc.lower())

    # =========================================
    # NEW API INTEGRATIONS (PageSpeed, LLM, SERP)
    # =========================================
    performance_data = get_pagespeed_scores(final_url)
    eeat_data = analyze_content_quality_llm(parser.all_text, parser.title, industry)
    geo_score, geo_checks = calculate_geo_ai_readiness(html, parser, parser.title)
    serp_data = run_serp_analysis(urllib.parse.urlparse(url).netloc.lower().replace("www.", ""), industry, business_name, parser.title, parser.all_text)

    # Extract quick website summary and location for the Hero UI
    website_summary = "A local business."
    detected_location = "Unknown Location"
    if OPENAI_API_KEY:
        try:
            summary_prompt = f"Summarize this business dynamically in 15 words or less based on this text:\n{parser.title}\n{all_text_str[:1000]}"
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                data=json.dumps({"model": "gpt-4o-mini", "messages": [{"role": "user", "content": summary_prompt}], "temperature": 0.3}).encode("utf-8")
            )
            ctx = ssl.create_default_context()
            resp = urllib.request.urlopen(req, timeout=5, context=ctx)
            website_summary = json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"].strip(' "')
            
            loc_prompt = f"Extract the primary city and state (e.g., 'Austin, TX') from this text. If none, reply 'Unknown Location'.\n{all_text_str[:3000]}"
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                data=json.dumps({"model": "gpt-4o-mini", "messages": [{"role": "user", "content": loc_prompt}], "temperature": 0.1}).encode("utf-8")
            )
            resp = urllib.request.urlopen(req, timeout=5, context=ctx)
            detected_location = json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"].strip(' "')
        except Exception:
            pass

    # Incorporate new GEO/AI score into AI Search Category
    ai_base_score = min(100, geo_score + 15) # Boosted base score


    # =========================================
    # TRADITIONAL SEO SCORE
    # =========================================
    seo_checks = []

    # Title tag present (15 pts)
    title = parser.title.strip()
    if title:
        seo_checks.append({
            "label": "Title Tag",
            "status": "pass",
            "detail": f"'{truncate_str(title, 60)}' ({len(title)} chars)",
            "points": 15,
            "fix_title": None,
            "fix_why": None,
            "impact": None,
        })
    else:
        seo_checks.append({
            "label": "Title Tag",
            "status": "fail",
            "detail": "Missing — no title tag found",
            "points": 0,
            "fix_title": "Add a descriptive title tag",
            "fix_why": "The title tag is the #1 on-page SEO factor and appears in search results as your clickable headline.",
            "impact": "High",
        })

    # Title length (5 pts)
    if title:
        if 30 <= len(title) <= 65:
            seo_checks.append({
                "label": "Title Length",
                "status": "pass",
                "detail": f"{len(title)} characters (ideal: 50-60)",
                "points": 5,
                "fix_title": None, "fix_why": None, "impact": None,
            })
        elif len(title) < 30:
            seo_checks.append({
                "label": "Title Length",
                "status": "warn",
                "detail": f"{len(title)} characters — too short (ideal: 50-60)",
                "points": 2,
                "fix_title": "Expand your title tag to 50-60 characters",
                "fix_why": "Short titles miss keyword opportunities and look incomplete in search results.",
                "impact": "Medium",
            })
        else:
            seo_checks.append({
                "label": "Title Length",
                "status": "warn",
                "detail": f"{len(title)} characters — may be truncated (ideal: 50-60)",
                "points": 2,
                "fix_title": "Shorten your title to under 60 characters",
                "fix_why": "Google truncates titles over ~60 characters, hiding important keywords.",
                "impact": "Medium",
            })

    # Meta description (15 pts)
    meta_desc = parser.meta_description.strip()
    if meta_desc:
        seo_checks.append({
            "label": "Meta Description",
            "status": "pass",
            "detail": f"'{truncate_str(meta_desc, 70)}' ({len(meta_desc)} chars)",
            "points": 15,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        seo_checks.append({
            "label": "Meta Description",
            "status": "fail",
            "detail": "Missing — no meta description found",
            "points": 0,
            "fix_title": "Add a compelling meta description (150-160 characters)",
            "fix_why": "Meta descriptions appear as the snippet in search results. Without one, Google picks random text.",
            "impact": "High",
        })

    # Meta description length (5 pts)
    if meta_desc:
        if 120 <= len(meta_desc) <= 170:
            seo_checks.append({
                "label": "Description Length",
                "status": "pass",
                "detail": f"{len(meta_desc)} characters (ideal: 150-160)",
                "points": 5,
                "fix_title": None, "fix_why": None, "impact": None,
            })
        else:
            seo_checks.append({
                "label": "Description Length",
                "status": "warn",
                "detail": f"{len(meta_desc)} characters (ideal: 150-160)",
                "points": 2,
                "fix_title": "Optimize meta description to 150-160 characters",
                "fix_why": "Too short wastes space; too long gets truncated in results.",
                "impact": "Low",
            })

    # H1 present (10 pts)
    h1_list = parser.headings.get("h1", [])
    if h1_list:
        seo_checks.append({
            "label": "H1 Tag",
            "status": "pass",
            "detail": f"'{truncate_str(h1_list[0], 50)}'",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        seo_checks.append({
            "label": "H1 Tag",
            "status": "fail",
            "detail": "Missing — no H1 heading found",
            "points": 0,
            "fix_title": "Add an H1 heading with your primary keyword",
            "fix_why": "The H1 tells search engines the main topic of your page.",
            "impact": "High",
        })

    # H1 count (5 pts)
    if len(h1_list) == 1:
        seo_checks.append({
            "label": "H1 Count",
            "status": "pass",
            "detail": "Exactly 1 H1 tag — ideal",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    elif len(h1_list) > 1:
        seo_checks.append({
            "label": "H1 Count",
            "status": "warn",
            "detail": f"{len(h1_list)} H1 tags found — should be exactly 1",
            "points": 2,
            "fix_title": "Use only one H1 tag per page",
            "fix_why": "Multiple H1s confuse search engines about your page's primary topic.",
            "impact": "Medium",
        })

    # Image alt tags (10 pts)
    if parser.images_total > 0:
        pct = round((parser.images_with_alt / parser.images_total) * 100)
        if pct >= 80:
            seo_checks.append({
                "label": "Image Alt Tags",
                "status": "pass",
                "detail": f"{parser.images_with_alt}/{parser.images_total} images have alt text ({pct}%)",
                "points": 10,
                "fix_title": None, "fix_why": None, "impact": None,
            })
        elif pct >= 50:
            seo_checks.append({
                "label": "Image Alt Tags",
                "status": "warn",
                "detail": f"{parser.images_with_alt}/{parser.images_total} images have alt text ({pct}%)",
                "points": 5,
                "fix_title": "Add descriptive alt text to all images",
                "fix_why": "Alt text helps search engines understand images and improves accessibility.",
                "impact": "Medium",
            })
        else:
            seo_checks.append({
                "label": "Image Alt Tags",
                "status": "fail",
                "detail": f"Only {parser.images_with_alt}/{parser.images_total} images have alt text ({pct}%)",
                "points": 2,
                "fix_title": "Add descriptive alt text to all images",
                "fix_why": "Search engines can't see images without alt text. You're missing SEO value and accessibility.",
                "impact": "Medium",
            })
    else:
        seo_checks.append({
            "label": "Image Alt Tags",
            "status": "pass",
            "detail": "No images found to check",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })

    # HTTPS (10 pts)
    if is_https:
        seo_checks.append({
            "label": "HTTPS/SSL",
            "status": "pass",
            "detail": "Site uses HTTPS — secure connection",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        seo_checks.append({
            "label": "HTTPS/SSL",
            "status": "fail",
            "detail": "Site does not use HTTPS",
            "points": 0,
            "fix_title": "Switch to HTTPS (SSL certificate)",
            "fix_why": "Google penalizes non-HTTPS sites. Browsers show 'Not Secure' warnings that scare visitors away.",
            "impact": "High",
        })

    # Canonical tag (5 pts)
    if parser.canonical:
        seo_checks.append({
            "label": "Canonical Tag",
            "status": "pass",
            "detail": f"Set to '{truncate_str(parser.canonical, 50)}'",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        seo_checks.append({
            "label": "Canonical Tag",
            "status": "warn",
            "detail": "Not found — helps prevent duplicate content issues",
            "points": 0,
            "fix_title": "Add a canonical tag pointing to your preferred URL",
            "fix_why": "Canonical tags prevent search engines from splitting your ranking power across duplicate pages.",
            "impact": "Low",
        })

    # OG tags (5 pts)
    has_og = bool(parser.og_title or parser.og_description or parser.og_image)
    if has_og:
        parts = []
        if parser.og_title: parts.append("og:title")
        if parser.og_description: parts.append("og:description")
        if parser.og_image: parts.append("og:image")
        seo_checks.append({
            "label": "Open Graph Tags",
            "status": "pass",
            "detail": f"Found: {', '.join(parts)}",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        seo_checks.append({
            "label": "Open Graph Tags",
            "status": "fail",
            "detail": "Missing — controls how your site appears when shared on social media",
            "points": 0,
            "fix_title": "Add Open Graph meta tags (og:title, og:description, og:image)",
            "fix_why": "Without OG tags, social shares look ugly and unprofessional — bad for clicks.",
            "impact": "Medium",
        })

    # Heading hierarchy (5 pts)
    if proper_hierarchy:
        seo_checks.append({
            "label": "Heading Hierarchy",
            "status": "pass",
            "detail": "Headings follow proper nesting order",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        seo_checks.append({
            "label": "Heading Hierarchy",
            "status": "warn",
            "detail": "Skipped heading levels detected — should nest H1 > H2 > H3",
            "points": 2,
            "fix_title": "Fix heading hierarchy (don't skip levels)",
            "fix_why": "Proper heading nesting helps search engines understand your content structure.",
            "impact": "Low",
        })

    # Clean URL (5 pts)
    if clean_url:
        seo_checks.append({
            "label": "Clean URL",
            "status": "pass",
            "detail": "URL is clean and readable",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        seo_checks.append({
            "label": "Clean URL",
            "status": "warn",
            "detail": "URL contains query parameters or non-clean patterns",
            "points": 2,
            "fix_title": "Use clean, descriptive URLs without parameters",
            "fix_why": "Clean URLs are easier for search engines to crawl and for users to understand.",
            "impact": "Low",
        })

    # Twitter card (5 pts)
    if parser.twitter_card:
        seo_checks.append({
            "label": "Twitter Card",
            "status": "pass",
            "detail": f"Type: {parser.twitter_card}",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        seo_checks.append({
            "label": "Twitter Card",
            "status": "warn",
            "detail": "Not found — improves appearance when shared on X/Twitter",
            "points": 0,
            "fix_title": "Add Twitter Card meta tags",
            "fix_why": "Twitter Card tags make your links look professional when shared on X.",
            "impact": "Low",
        })

    seo_score = sum(c["points"] for c in seo_checks)

    # =========================================
    # AI SEARCH READINESS SCORE
    # =========================================
    ai_checks = []

    # JSON-LD structured data (20 pts)
    if schema["count"] > 0:
        ai_checks.append({
            "label": "Structured Data (JSON-LD)",
            "status": "pass",
            "detail": f"{schema['count']} block(s) found — types: {', '.join(schema['types'][:5]) or 'Unknown'}",
            "points": 20,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        ai_checks.append({
            "label": "Structured Data (JSON-LD)",
            "status": "fail",
            "detail": "None detected — this is critical for AI discovery",
            "points": 0,
            "fix_title": "Add JSON-LD structured data to your website",
            "fix_why": "AI assistants rely on structured data to understand your business. Without it, AI cannot recommend you.",
            "impact": "High",
        })

    # Schema completeness (10 pts)
    if schema["count"] > 0:
        if schema["completeness"] >= 70:
            ai_checks.append({
                "label": "Schema Completeness",
                "status": "pass",
                "detail": f"{schema['completeness']}% of schema fields populated",
                "points": 10,
                "fix_title": None, "fix_why": None, "impact": None,
            })
        else:
            ai_checks.append({
                "label": "Schema Completeness",
                "status": "warn",
                "detail": f"Only {schema['completeness']}% of schema fields populated",
                "points": 5,
                "fix_title": "Fill in all structured data fields completely",
                "fix_why": "Incomplete schema provides less information for AI to work with.",
                "impact": "Medium",
            })

    # Entity clarity — Organization/LocalBusiness (15 pts)
    if schema["has_organization"] or schema["has_local_business"]:
        entity_type = "LocalBusiness" if schema["has_local_business"] else "Organization"
        ai_checks.append({
            "label": "Entity Identity",
            "status": "pass",
            "detail": f"{entity_type} schema detected — AI can identify your business",
            "points": 15,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        ai_checks.append({
            "label": "Entity Identity",
            "status": "fail",
            "detail": "No Organization or LocalBusiness schema — AI can't identify what your business is",
            "points": 0,
            "fix_title": "Add Organization or LocalBusiness schema markup",
            "fix_why": "Without entity markup, AI doesn't know who you are, what you do, or where you are.",
            "impact": "High",
        })

    # FAQ schema (10 pts)
    if schema["has_faq_schema"]:
        ai_checks.append({
            "label": "FAQ Schema",
            "status": "pass",
            "detail": "FAQPage schema detected — AI can read your Q&A content",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        ai_checks.append({
            "label": "FAQ Schema",
            "status": "fail",
            "detail": "Not found — FAQ schema helps AI answer questions about your business",
            "points": 0,
            "fix_title": "Add FAQPage schema with common customer questions",
            "fix_why": "FAQ schema feeds directly into AI answers and Google's FAQ rich results.",
            "impact": "High",
        })

    # HowTo schema (5 pts)
    if schema["has_howto_schema"]:
        ai_checks.append({
            "label": "HowTo Schema",
            "status": "pass",
            "detail": "HowTo schema detected",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        ai_checks.append({
            "label": "HowTo Schema",
            "status": "warn",
            "detail": "Not found — useful if you offer step-by-step services",
            "points": 0,
            "fix_title": "Consider adding HowTo schema for service processes",
            "fix_why": "HowTo schema can appear as rich results and helps AI explain your services.",
            "impact": "Low",
        })

    # Content quality — word count (10 pts)
    if parser.word_count >= 300:
        ai_checks.append({
            "label": "Content Depth",
            "status": "pass",
            "detail": f"{parser.word_count} words — sufficient content for AI analysis",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    elif parser.word_count >= 100:
        ai_checks.append({
            "label": "Content Depth",
            "status": "warn",
            "detail": f"{parser.word_count} words — thin content limits AI understanding",
            "points": 5,
            "fix_title": "Add more descriptive content (aim for 300+ words)",
            "fix_why": "AI needs enough text to understand what your business offers.",
            "impact": "Medium",
        })
    else:
        ai_checks.append({
            "label": "Content Depth",
            "status": "fail",
            "detail": f"Only {parser.word_count} words — very thin content",
            "points": 0,
            "fix_title": "Add substantial content describing your services (300+ words)",
            "fix_why": "With very little text, AI has almost nothing to learn about your business.",
            "impact": "High",
        })

    # Semantic HTML (10 pts)
    semantic_count = len(parser.semantic_tags)
    if semantic_count >= 4:
        ai_checks.append({
            "label": "Semantic HTML",
            "status": "pass",
            "detail": f"Using: {', '.join(sorted(parser.semantic_tags))}",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    elif semantic_count >= 2:
        ai_checks.append({
            "label": "Semantic HTML",
            "status": "warn",
            "detail": f"Partial: {', '.join(sorted(parser.semantic_tags))} — could use more semantic tags",
            "points": 5,
            "fix_title": "Use more semantic HTML tags (main, article, section, nav)",
            "fix_why": "Semantic HTML helps AI understand the structure and purpose of your content.",
            "impact": "Medium",
        })
    else:
        ai_checks.append({
            "label": "Semantic HTML",
            "status": "fail",
            "detail": "Minimal semantic HTML — page relies on generic divs",
            "points": 0,
            "fix_title": "Replace div-heavy structure with semantic HTML",
            "fix_why": "Without semantic tags, AI struggles to identify which content is most important.",
            "impact": "Medium",
        })

    # Content freshness (5 pts)
    if last_modified or parser.date_meta:
        ai_checks.append({
            "label": "Content Freshness",
            "status": "pass",
            "detail": f"Freshness signal detected: {last_modified or parser.date_meta}",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        ai_checks.append({
            "label": "Content Freshness",
            "status": "warn",
            "detail": "No date or last-modified signal found",
            "points": 0,
            "fix_title": "Add date metadata to signal content freshness",
            "fix_why": "AI and search engines prefer recently updated content.",
            "impact": "Low",
        })

    # Speakable schema (5 pts)
    if schema["has_speakable"]:
        ai_checks.append({
            "label": "Speakable Schema",
            "status": "pass",
            "detail": "Speakable schema detected — AI voice assistants can read your content",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        ai_checks.append({
            "label": "Speakable Schema",
            "status": "warn",
            "detail": "Not found — helps voice/AI assistants identify readable sections",
            "points": 0,
            "fix_title": "Add speakable schema to key content sections",
            "fix_why": "Speakable markup tells AI assistants which content to read aloud.",
            "impact": "Low",
        })

    # Q&A format (10 pts)
    if parser.question_headings >= 3:
        ai_checks.append({
            "label": "Q&A Content Format",
            "status": "pass",
            "detail": f"{parser.question_headings} question-format headings found",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    elif parser.question_headings >= 1:
        ai_checks.append({
            "label": "Q&A Content Format",
            "status": "warn",
            "detail": f"Only {parser.question_headings} question-format heading(s) — add more FAQ content",
            "points": 5,
            "fix_title": "Add more Q&A format content with questions as headings",
            "fix_why": "AI loves Q&A format because it directly matches how people ask questions.",
            "impact": "Medium",
        })
    else:
        ai_checks.append({
            "label": "Q&A Content Format",
            "status": "fail",
            "detail": "No question-format headings found",
            "points": 0,
            "fix_title": "Create FAQ content with questions as H2/H3 headings",
            "fix_why": "Questions in headings directly match AI search queries and voice questions.",
            "impact": "High",
        })

    ai_score = ai_base_score + sum(c.get("points", 0) for c in ai_checks if c.get("points", 0) < 0)
    ai_score = max(0, min(100, ai_score))

    # =========================================
    # VOICE SEARCH READINESS SCORE
    # =========================================
    voice_checks = []

    # FAQ-style content (20 pts)
    if parser.has_faq_heading and parser.question_headings >= 3:
        voice_checks.append({
            "label": "FAQ-Style Content",
            "status": "pass",
            "detail": f"{parser.question_headings} question headings found — great for voice answers",
            "points": 20,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    elif parser.question_headings >= 1:
        voice_checks.append({
            "label": "FAQ-Style Content",
            "status": "warn",
            "detail": f"{parser.question_headings} question heading(s) — add more for voice search",
            "points": 10,
            "fix_title": "Add more FAQ sections with questions people actually ask",
            "fix_why": "Voice assistants pick answers from Q&A content. More questions = more chances to be chosen.",
            "impact": "High",
        })
    else:
        voice_checks.append({
            "label": "FAQ-Style Content",
            "status": "fail",
            "detail": "No question-format headings — voice search needs Q&A content",
            "points": 0,
            "fix_title": "Create a FAQ section with common customer questions",
            "fix_why": "Voice assistants need question-and-answer format to select your content as THE answer.",
            "impact": "High",
        })

    # Conversational content (15 pts)
    if readability["simple_words_pct"] >= 65:
        voice_checks.append({
            "label": "Conversational Tone",
            "status": "pass",
            "detail": f"{readability['simple_words_pct']}% simple vocabulary — easy to read aloud",
            "points": 15,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    elif readability["simple_words_pct"] >= 45:
        voice_checks.append({
            "label": "Conversational Tone",
            "status": "warn",
            "detail": f"{readability['simple_words_pct']}% simple vocabulary — could be more conversational",
            "points": 8,
            "fix_title": "Simplify your writing — use shorter, everyday words",
            "fix_why": "Voice assistants prefer content that sounds natural when read aloud.",
            "impact": "Medium",
        })
    else:
        voice_checks.append({
            "label": "Conversational Tone",
            "status": "fail",
            "detail": f"Only {readability['simple_words_pct']}% simple vocabulary — too complex for voice",
            "points": 0,
            "fix_title": "Rewrite content in plain, everyday language",
            "fix_why": "Complex language gets skipped by voice search. Write like you talk.",
            "impact": "Medium",
        })

    # Speakable schema (10 pts)
    if schema["has_speakable"]:
        voice_checks.append({
            "label": "Speakable Schema",
            "status": "pass",
            "detail": "Speakable markup present — voice assistants know what to read",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        voice_checks.append({
            "label": "Speakable Schema",
            "status": "fail",
            "detail": "Missing — voice assistants can't identify what to read aloud",
            "points": 0,
            "fix_title": "Add speakable schema to your most important content",
            "fix_why": "Speakable markup directly tells voice assistants which text to speak.",
            "impact": "High",
        })

    # Page speed (15 pts)
    if response_time < 1.5:
        voice_checks.append({
            "label": "Page Response Speed",
            "status": "pass",
            "detail": f"{response_time:.1f}s response time — fast",
            "points": 15,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    elif response_time < 3.0:
        voice_checks.append({
            "label": "Page Response Speed",
            "status": "warn",
            "detail": f"{response_time:.1f}s response time — could be faster",
            "points": 8,
            "fix_title": "Improve page loading speed",
            "fix_why": "Voice search heavily favors fast-loading pages since users expect instant answers.",
            "impact": "Medium",
        })
    else:
        voice_checks.append({
            "label": "Page Response Speed",
            "status": "fail",
            "detail": f"{response_time:.1f}s response time — slow",
            "points": 0,
            "fix_title": "Significantly improve page loading speed",
            "fix_why": "Slow pages are almost never chosen for voice search results.",
            "impact": "High",
        })

    # Mobile viewport (10 pts)
    if parser.meta_viewport and "width" in parser.meta_viewport:
        voice_checks.append({
            "label": "Mobile Viewport",
            "status": "pass",
            "detail": "Viewport meta tag present — mobile-friendly",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        voice_checks.append({
            "label": "Mobile Viewport",
            "status": "fail",
            "detail": "No viewport meta tag — site may not be mobile-friendly",
            "points": 0,
            "fix_title": "Add a viewport meta tag for mobile responsiveness",
            "fix_why": "Most voice searches happen on mobile. A non-mobile site gets deprioritized.",
            "impact": "High",
        })

    # Content readability / short sentences (15 pts)
    if readability["avg_sentence_len"] > 0 and readability["avg_sentence_len"] <= 20:
        voice_checks.append({
            "label": "Sentence Length",
            "status": "pass",
            "detail": f"Average {readability['avg_sentence_len']} words per sentence — good for voice",
            "points": 15,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    elif readability["avg_sentence_len"] <= 30:
        voice_checks.append({
            "label": "Sentence Length",
            "status": "warn",
            "detail": f"Average {readability['avg_sentence_len']} words per sentence — slightly long",
            "points": 8,
            "fix_title": "Use shorter sentences (under 20 words on average)",
            "fix_why": "Voice assistants prefer concise answers that sound natural when spoken.",
            "impact": "Medium",
        })
    else:
        voice_checks.append({
            "label": "Sentence Length",
            "status": "fail",
            "detail": f"Average {readability['avg_sentence_len']} words per sentence — too long for voice",
            "points": 0,
            "fix_title": "Break long sentences into shorter, spoken-friendly ones",
            "fix_why": "Long sentences sound awkward when read aloud by voice assistants.",
            "impact": "Medium",
        })

    # Featured snippet optimization (15 pts) — short direct answers after questions
    # Check if there's content right after question headings
    if parser.question_headings >= 2 and parser.paragraph_count >= 3:
        voice_checks.append({
            "label": "Direct Answer Format",
            "status": "pass",
            "detail": f"{parser.question_headings} questions with content — good for featured snippets",
            "points": 15,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    elif parser.paragraph_count >= 3:
        voice_checks.append({
            "label": "Direct Answer Format",
            "status": "warn",
            "detail": "Content exists but lacks clear question-answer structure",
            "points": 7,
            "fix_title": "Structure content as questions followed by direct 1-2 sentence answers",
            "fix_why": "Voice search picks the ONE best answer. Clear Q&A format wins.",
            "impact": "High",
        })
    else:
        voice_checks.append({
            "label": "Direct Answer Format",
            "status": "fail",
            "detail": "Not enough content to provide direct answers",
            "points": 0,
            "fix_title": "Create clear question-and-answer content blocks",
            "fix_why": "Without direct answers, voice assistants have nothing to read back to users.",
            "impact": "High",
        })

    voice_score = min(100, sum(c["points"] for c in voice_checks))

    # =========================================
    # LOCAL SEARCH READINESS SCORE
    # =========================================
    local_checks = []

    # LocalBusiness or Organization schema with NAP (25 pts)
    if schema["has_local_business"]:
        nap_items = [k for k, v in schema["nap"].items() if v]
        local_checks.append({
            "label": "Local Business Schema",
            "status": "pass",
            "detail": f"LocalBusiness schema found with: {', '.join(nap_items) if nap_items else 'basic info'}",
            "points": 25,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    elif schema["has_organization"]:
        local_checks.append({
            "label": "Local Business Schema",
            "status": "warn",
            "detail": "Organization schema found but not LocalBusiness — upgrade for local search",
            "points": 12,
            "fix_title": "Upgrade from Organization to LocalBusiness schema",
            "fix_why": "LocalBusiness schema gives Google much more detail for local/map results.",
            "impact": "High",
        })
    else:
        local_checks.append({
            "label": "Local Business Schema",
            "status": "fail",
            "detail": "No local business or organization schema found",
            "points": 0,
            "fix_title": "Add LocalBusiness schema with full NAP (Name, Address, Phone)",
            "fix_why": "This is the #1 signal for appearing in Google's local map pack.",
            "impact": "High",
        })

    # NAP in schema (15 pts)
    if schema["has_local_business"] or schema["has_organization"]:
        nap_score_val = sum(1 for v in schema["nap"].values() if v)
        if nap_score_val == 3:
            local_checks.append({
                "label": "NAP in Schema",
                "status": "pass",
                "detail": "Name, Address, and Phone all present in schema",
                "points": 15,
                "fix_title": None, "fix_why": None, "impact": None,
            })
        elif nap_score_val >= 1:
            missing = [k for k, v in schema["nap"].items() if not v]
            local_checks.append({
                "label": "NAP in Schema",
                "status": "warn",
                "detail": f"Missing in schema: {', '.join(missing)}",
                "points": 7,
                "fix_title": f"Add missing {', '.join(missing)} to your schema markup",
                "fix_why": "Incomplete NAP data weakens your local search presence.",
                "impact": "High",
            })
        else:
            local_checks.append({
                "label": "NAP in Schema",
                "status": "fail",
                "detail": "Schema exists but has no NAP (Name/Address/Phone) data",
                "points": 0,
                "fix_title": "Add name, address, and telephone to your schema",
                "fix_why": "Search engines need your NAP data in structured format to show you in local results.",
                "impact": "High",
            })

    # Geo meta tags (5 pts)
    if parser.geo_meta:
        local_checks.append({
            "label": "Geo Meta Tags",
            "status": "pass",
            "detail": "Geographic meta tags detected",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        local_checks.append({
            "label": "Geo Meta Tags",
            "status": "warn",
            "detail": "No geo meta tags found — helpful for location targeting",
            "points": 0,
            "fix_title": "Add geo.position and geo.region meta tags",
            "fix_why": "Geo tags help search engines confirm your service area.",
            "impact": "Low",
        })

    # Phone visible on page (10 pts)
    if has_phone:
        local_checks.append({
            "label": "Phone Number Visible",
            "status": "pass",
            "detail": "Phone number detected in page content",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        local_checks.append({
            "label": "Phone Number Visible",
            "status": "fail",
            "detail": "No phone number found on page",
            "points": 0,
            "fix_title": "Add your phone number prominently on the page",
            "fix_why": "Local customers need to call you. A visible phone number is essential for local search.",
            "impact": "High",
        })

    # Address visible on page (10 pts)
    if has_address:
        local_checks.append({
            "label": "Address Visible",
            "status": "pass",
            "detail": "Street address detected in page content",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        local_checks.append({
            "label": "Address Visible",
            "status": "warn",
            "detail": "No street address detected on page",
            "points": 0,
            "fix_title": "Display your business address on the page",
            "fix_why": "A visible address confirms your location for local search rankings.",
            "impact": "Medium",
        })

    # Google Maps embed (10 pts)
    if parser.has_maps_embed:
        local_checks.append({
            "label": "Google Maps Embed",
            "status": "pass",
            "detail": "Google Maps embed detected",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        local_checks.append({
            "label": "Google Maps Embed",
            "status": "warn",
            "detail": "No Google Maps embed found — adds a strong local signal",
            "points": 0,
            "fix_title": "Embed a Google Map showing your business location",
            "fix_why": "A map embed reinforces your location to search engines and helps customers find you.",
            "impact": "Medium",
        })

    # Contact page link (10 pts)
    if parser.has_contact_link:
        local_checks.append({
            "label": "Contact Page Link",
            "status": "pass",
            "detail": "Link to contact page found",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        local_checks.append({
            "label": "Contact Page Link",
            "status": "warn",
            "detail": "No link to a contact page detected",
            "points": 0,
            "fix_title": "Add a clear link to your contact page",
            "fix_why": "A dedicated contact page with NAP info strengthens local search signals.",
            "impact": "Medium",
        })

    # Service area mentions (10 pts)
    if has_service_area:
        local_checks.append({
            "label": "Service Area Mentions",
            "status": "pass",
            "detail": "Service area language detected in content",
            "points": 10,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        local_checks.append({
            "label": "Service Area Mentions",
            "status": "warn",
            "detail": "No explicit service area mentions found",
            "points": 0,
            "fix_title": "Mention the cities and areas you serve in your content",
            "fix_why": "Listing service areas helps you rank for 'near me' searches in those locations.",
            "impact": "Medium",
        })

    # Hreflang (5 pts)
    if parser.hreflang_tags:
        local_checks.append({
            "label": "Hreflang Tags",
            "status": "pass",
            "detail": f"Hreflang tags found: {', '.join(parser.hreflang_tags[:3])}",
            "points": 5,
            "fix_title": None, "fix_why": None, "impact": None,
        })
    else:
        local_checks.append({
            "label": "Hreflang Tags",
            "status": "warn",
            "detail": "Not found — useful if you serve multilingual areas",
            "points": 2,
            "fix_title": "Consider adding hreflang tags if you serve multilingual communities",
            "fix_why": "Hreflang helps search engines show your site to the right language audience.",
            "impact": "Low",
        })

    local_score = min(100, sum(c["points"] for c in local_checks))

    # =========================================
    # BUILD RESULT
    # =========================================
    report_id = str(uuid.uuid4())[:12]

    result = {
        "report_id": report_id,
        "url": url,
        "final_url": final_url,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "response_time": round(response_time, 2),
        "scores": {
            "traditional_seo": min(100, seo_score),
            "ai_search": min(100, ai_score),
            "voice_search": min(100, voice_score),
            "local_search": min(100, local_score),
        },
        "checks": {
            "traditional_seo": [strip_internal(c) for c in seo_checks],
            "ai_search": [strip_internal(c) for c in ai_checks],
            "voice_search": [strip_internal(c) for c in voice_checks],
            "local_search": [strip_internal(c) for c in local_checks],
        },
        "summary": {
            "title": title,
            "meta_description": truncate_str(meta_desc, 160),
            "word_count": parser.word_count,
            "images": parser.images_total,
            "schema_types": schema["types"],
            "is_https": is_https,
            "website_summary": website_summary,
            "location": detected_location,
        },
        "performance": performance_data,
        "eeat_analysis": eeat_data,
        "serp_analysis": serp_data,
        "geo_analysis": {
            "score": geo_score,
            "checks": [strip_internal(c) for c in geo_checks]
        }
    }

    # Sync to Supabase
    sync_to_supabase(
        result, parser,
        scan_type=scan_type,
        primary_domain=primary_domain,
        competitor_domain=competitor_domain,
        competitor_result=competitor_result,
        contact_name=contact_name,
        contact_email=contact_email,
        contact_phone=contact_phone,
        contact_role=contact_role,
        client_ip=client_ip
    )

    return result


def strip_internal(check):
    """Remove the 'points' key from check for client output; keep fix info."""
    return {
        "label": check["label"],
        "status": check["status"],
        "detail": check["detail"],
        "fix_title": check.get("fix_title"),
        "fix_why": check.get("fix_why"),
        "impact": check.get("impact"),
    }


def truncate_str(s, length):
    if not s:
        return ""
    return s[:length] + "..." if len(s) > length else s


# ============================================
# CGI REQUEST HANDLER
# ============================================

def main():
    method = os.environ.get("REQUEST_METHOD", "GET")
    query_string = os.environ.get("QUERY_STRING", "")

    if method == "GET":
        # Retrieve a saved report from Supabase by report_id
        params = urllib.parse.parse_qs(query_string)
        report_id = params.get("id", [None])[0]

        if not report_id:
            print("Status: 400")
            print("Content-Type: application/json")
            print()
            print(json.dumps({"error": "Missing report ID. Provide ?id=REPORT_ID"}))
            return

        rows = supabase_select("scans", {
            "select": "full_report",
            "report_id": f"eq.{report_id}",
            "limit": 1
        })

        if not rows or not rows[0].get("full_report"):
            print("Status: 404")
            print("Content-Type: application/json")
            print()
            print(json.dumps({"error": "Report not found. It may have expired or the link is invalid."}))
            return

        print("Content-Type: application/json")
        print()
        print(json.dumps(rows[0]["full_report"]))
        return

    elif method == "POST":
        # Run analysis
        try:
            content_length = int(os.environ.get("CONTENT_LENGTH", 0))
            body = sys.stdin.read(content_length) if content_length else sys.stdin.read()
            payload = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            print("Status: 400")
            print("Content-Type: application/json")
            print()
            print(json.dumps({"error": "Invalid request body. Send JSON with a 'url' field."}))
            return

        url = payload.get("url", "").strip()
        if not url:
            print("Status: 400")
            print("Content-Type: application/json")
            print()
            print(json.dumps({"error": "Please provide a URL to analyze."}))
            return

        # Validate URL
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        parsed = urllib.parse.urlparse(url)
        if not parsed.netloc or "." not in parsed.netloc:
            print("Status: 400")
            print("Content-Type: application/json")
            print()
            print(json.dumps({"error": "That doesn't look like a valid website URL. Please include the full address (e.g., https://example.com)."}))
            return

        competitor_url = payload.get("competitor_url", "").strip()
        if competitor_url:
            # Normalise competitor URL
            if not competitor_url.startswith("http://") and not competitor_url.startswith("https://"):
                competitor_url = "https://" + competitor_url

        # Extract contact / lead info from form gate
        contact_name  = payload.get("contact_name",  "").strip()
        contact_email = payload.get("contact_email", "").strip()
        contact_phone = payload.get("contact_phone", "").strip()
        contact_role  = payload.get("contact_role",  "").strip()

        try:
            if competitor_url:
                # ---- Dual-URL analysis ----
                primary_domain = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
                competitor_domain = urllib.parse.urlparse(competitor_url).netloc.lower().replace("www.", "")

                # Run primary scan
                primary_result = run_analysis(
                    url,
                    scan_type="self",
                    primary_domain=primary_domain,
                    competitor_domain=competitor_domain,
                    contact_name=contact_name,
                    contact_email=contact_email,
                    contact_phone=contact_phone,
                    contact_role=contact_role,
                )

                # Run competitor scan
                competitor_result = run_analysis(
                    competitor_url,
                    scan_type="competitor",
                    primary_domain=primary_domain,
                    competitor_domain=competitor_domain,
                    competitor_result=primary_result,
                    contact_name=contact_name,
                    contact_email=contact_email,
                    contact_phone=contact_phone,
                    contact_role=contact_role,
                )

                # Build score comparison
                def _overall(r):
                    s = r["scores"]
                    return round((s["traditional_seo"] + s["ai_search"] +
                                  s["voice_search"] + s["local_search"]) / 4)

                p_overall = _overall(primary_result)
                c_overall = _overall(competitor_result)

                comparison = {
                    "primary_domain": primary_domain,
                    "competitor_domain": competitor_domain,
                    "score_diff": {
                        "overall": p_overall - c_overall,
                        "traditional_seo": primary_result["scores"]["traditional_seo"] - competitor_result["scores"]["traditional_seo"],
                        "ai_search": primary_result["scores"]["ai_search"] - competitor_result["scores"]["ai_search"],
                        "voice_search": primary_result["scores"]["voice_search"] - competitor_result["scores"]["voice_search"],
                        "local_search": primary_result["scores"]["local_search"] - competitor_result["scores"]["local_search"],
                    },
                    "primary_overall": p_overall,
                    "competitor_overall": c_overall,
                    "winner": primary_domain if p_overall >= c_overall else competitor_domain,
                }

                response = {
                    "primary": primary_result,
                    "competitor": competitor_result,
                    "comparison": comparison,
                }
                print("Content-Type: application/json")
                print()
                print(json.dumps(response))

            else:
                # ---- Single-URL analysis (original flow) ----
                result = run_analysis(
                    url,
                    contact_name=contact_name,
                    contact_email=contact_email,
                    contact_phone=contact_phone,
                    contact_role=contact_role,
                )
                print("Content-Type: application/json")
                print()
                print(json.dumps(result))

        except urllib.error.HTTPError as e:
            if e.code == 403:
                error_msg = "This website's security blocked our analysis. This sometimes happens with sites using aggressive firewalls. Try scanning a specific inner page instead (e.g., /about or /services)."
            elif e.code == 404:
                error_msg = "That page wasn't found (404). Please check the URL and try again."
            elif e.code >= 500:
                error_msg = f"The website's server returned an error (HTTP {e.code}). The site may be temporarily down."
            else:
                error_msg = f"The website returned an error (HTTP {e.code}). Please check the URL and try again."
            print("Status: 422")
            print("Content-Type: application/json")
            print()
            print(json.dumps({"error": error_msg}))
        except urllib.error.URLError as e:
            print("Status: 422")
            print("Content-Type: application/json")
            print()
            print(json.dumps({"error": "We couldn't reach this website. Please check the URL and make sure the site is accessible."}))
        except Exception as e:
            print("Status: 422")
            print("Content-Type: application/json")
            print()
            print(json.dumps({"error": f"Analysis failed: {str(e)[:200]}. Please try again."}))
        return

    else:
        print("Status: 405")
        print("Content-Type: application/json")
        print()
        print(json.dumps({"error": "Method not allowed"}))


if __name__ == "__main__":
    main()
