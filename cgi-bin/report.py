#!/usr/bin/env python3
"""
Alianza Search Readiness — PDF Report Endpoint
GET ?id=REPORT_ID                          → single-site branded HTML report (print → PDF)
GET ?id=REPORT_ID&competitor_id=OTHER_ID   → side-by-side comparison report

Content-Type: text/html
The page auto-triggers window.print() via JS and uses @media print CSS so the
browser's native print dialog produces a clean, branded PDF with no extra chrome.
"""

import json
import os
import re
import sqlite3
import sys
import urllib.parse
import urllib.request
import ssl
from datetime import datetime, timezone

# ============================================
# SUPABASE CONFIG  (mirrored from analyze.py)
# ============================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://jcwvrrazmceccbzaythk.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

DB_PATH = "data.db"


# ============================================
# HELPERS
# ============================================

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            report_id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS pdf_downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT NOT NULL,
            competitor_id TEXT,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip TEXT
        )
    """)
    db.commit()
    return db


def track_pdf_download(report_id, competitor_id=None):
    """Record a PDF download event in SQLite and Supabase."""
    try:
        ip = os.environ.get("REMOTE_ADDR", "")
        db = get_db()
        db.execute(
            "INSERT INTO pdf_downloads (report_id, competitor_id, ip) VALUES (?, ?, ?)",
            (report_id, competitor_id or "", ip)
        )
        db.commit()
        db.close()
    except Exception:
        pass

    # Also push to Supabase
    try:
        sb_url = f"{SUPABASE_URL}/rest/v1/pdf_downloads"
        sb_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        sb_data = {
            "report_id": report_id,
            "competitor_id": competitor_id or "",
            "ip": os.environ.get("REMOTE_ADDR", ""),
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
        }
        sb_body = json.dumps(sb_data).encode("utf-8")
        req = urllib.request.Request(sb_url, data=sb_body, headers=sb_headers, method="POST")
        ctx = ssl.create_default_context()
        urllib.request.urlopen(req, timeout=5, context=ctx)
    except Exception:
        pass


def fetch_report(report_id):
    """Load a report JSON from SQLite. Returns dict or None."""
    try:
        db = get_db()
        row = db.execute(
            "SELECT data FROM reports WHERE report_id = ?", (report_id,)
        ).fetchone()
        db.close()
        if row:
            return json.loads(row[0])
    except Exception:
        pass
    return None


def esc(s):
    """HTML-escape a string."""
    if not s:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def score_color(score):
    """Return a CSS hex color for a score 0-100."""
    if score >= 70:
        return "#22c55e"   # green
    if score >= 45:
        return "#f59e0b"   # amber
    return "#ef4444"       # red


def score_grade(score):
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def status_icon(status):
    if status == "pass":
        return '<span class="icon-pass">&#10003;</span>'
    if status == "fail":
        return '<span class="icon-fail">&#10007;</span>'
    return '<span class="icon-warn">&#9888;</span>'


def status_label(status):
    labels = {"pass": "Pass", "fail": "Fail", "warn": "Warning"}
    return labels.get(status, status.title())


def format_date(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except Exception:
        return iso_str[:10] if iso_str else "Unknown"


CATEGORY_NAMES = {
    "traditional_seo": "Traditional SEO",
    "ai_search": "AI Search",
    "voice_search": "Voice Search",
    "local_search": "Local Search",
}

CATEGORY_DESC = {
    "traditional_seo": "How well Google's classic algorithm can read and rank your site.",
    "ai_search": "How well AI assistants (ChatGPT, Perplexity, Gemini) can understand and cite your business.",
    "voice_search": "How likely voice assistants are to read your content as the chosen answer.",
    "local_search": "How visible you are in local map packs and 'near me' searches.",
}


# ============================================
# GAUGE SVG
# ============================================

def gauge_svg(score, color, size=90):
    """Return a simple SVG arc gauge for a score 0-100."""
    r = 36
    cx = size // 2
    cy = size // 2
    stroke_width = 8
    circumference = 3.14159 * r  # half-circle arc
    arc_length = circumference * (score / 100)
    gap = circumference - arc_length
    return (
        f'<svg width="{size}" height="{size // 2 + 18}" viewBox="0 0 {size} {size // 2 + 18}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<path d="M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}" '
        f'fill="none" stroke="#e5e7eb" stroke-width="{stroke_width}" stroke-linecap="round"/>'
        f'<path d="M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}" '
        f'fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" '
        f'stroke-dasharray="{arc_length:.1f} {gap + 1:.1f}"/>'
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" '
        f'font-size="18" font-weight="700" fill="{color}" font-family="Plus Jakarta Sans, sans-serif">'
        f'{score}</text>'
        f'</svg>'
    )


# ============================================
# REPORT HTML BUILDER
# ============================================

def build_checks_table(checks_by_category):
    """Build HTML table rows for all checks across categories."""
    rows = ""
    for cat_key, cat_name in CATEGORY_NAMES.items():
        checks = checks_by_category.get(cat_key, [])
        if not checks:
            continue
        rows += f'<tr class="cat-header"><td colspan="3">{esc(cat_name)}</td></tr>\n'
        for c in checks:
            status = c.get("status", "warn")
            rows += (
                f'<tr class="check-row status-{esc(status)}">'
                f'<td class="check-icon">{status_icon(status)}</td>'
                f'<td class="check-label">{esc(c.get("label",""))}</td>'
                f'<td class="check-detail">{esc(c.get("detail",""))}'
            )
            if c.get("fix_title") and status != "pass":
                rows += (
                    f'<br><span class="fix-title">Fix: {esc(c["fix_title"])}</span>'
                )
            rows += "</td></tr>\n"
    return rows


def build_recommendations(checks_by_category, max_recs=6):
    """Return top failing/warning checks as recommendation items."""
    items = []
    for cat_key, cat_name in CATEGORY_NAMES.items():
        for c in checks_by_category.get(cat_key, []):
            if c.get("status") in ("fail", "warn") and c.get("fix_title"):
                items.append({
                    "category": cat_name,
                    "label": c.get("label", ""),
                    "fix_title": c.get("fix_title", ""),
                    "fix_why": c.get("fix_why", ""),
                    "impact": c.get("impact", ""),
                    "status": c.get("status", "warn"),
                })
    # Sort: fail first, then by impact (High > Medium > Low)
    impact_order = {"High": 0, "Medium": 1, "Low": 2, "": 3}
    items.sort(key=lambda x: (0 if x["status"] == "fail" else 1,
                               impact_order.get(x.get("impact", ""), 3)))
    return items[:max_recs] # type: ignore



def render_single_report(data, is_comparison=False, competitor_data=None, side="primary"):
    """Render the body content for a single report. Used standalone and inside comparison."""
    scores = data.get("scores", {})
    summary = data.get("summary", {})
    checks = data.get("checks", {})
    url = data.get("url", "")
    domain = urllib.parse.urlparse(url).netloc.replace("www.", "")
    analyzed_at = format_date(data.get("analyzed_at", ""))
    overall = round(
        (scores.get("traditional_seo", 0) + scores.get("ai_search", 0) +
         scores.get("voice_search", 0) + scores.get("local_search", 0)) / 4
    )
    o_color = score_color(overall)
    o_grade = score_grade(overall)

    html = ""

    # Score summary bar
    html += '<div class="score-summary">\n'
    html += f'  <div class="overall-score" style="border-color:{o_color}">\n'
    html += f'    <div class="overall-number" style="color:{o_color}">{overall}</div>\n'
    html += f'    <div class="overall-grade" style="color:{o_color}">Grade {o_grade}</div>\n'
    html += '    <div class="overall-label">Overall Score</div>\n'
    html += '  </div>\n'
    html += '  <div class="category-scores">\n'
    for cat_key, cat_name in CATEGORY_NAMES.items():
        s = scores.get(cat_key, 0)
        c = score_color(s)
        html += f'  <div class="cat-score-item">\n'
        html += f'    {gauge_svg(s, c)}\n'
        html += f'    <div class="cat-name">{esc(cat_name)}</div>\n'
        html += f'  </div>\n'
    html += '  </div>\n'
    html += '</div>\n'

    # Page summary
    title = summary.get("title", domain)
    meta_desc = summary.get("meta_description", "")
    word_count = summary.get("word_count", 0)
    schema_types = summary.get("schema_types", [])
    is_https = summary.get("is_https", False)

    html += '<div class="page-summary">\n'
    html += f'  <div class="summary-item"><span>Title</span><strong>{esc(title[:80])}</strong></div>\n'
    if meta_desc:
        html += f'  <div class="summary-item"><span>Meta Description</span><strong>{esc(meta_desc[:120])}</strong></div>\n'
    html += f'  <div class="summary-item"><span>Word Count</span><strong>{word_count}</strong></div>\n'
    html += f'  <div class="summary-item"><span>HTTPS</span><strong>{"Yes ✓" if is_https else "No ✗"}</strong></div>\n'
    if schema_types:
        html += f'  <div class="summary-item"><span>Schema Types</span><strong>{esc(", ".join(schema_types[:5]))}</strong></div>\n'
    html += '</div>\n'

    # Checks table
    html += '<h2 class="section-title">Detailed Check Results</h2>\n'
    html += '<p style="font-size:11px;color:#6b7280;margin-top:-6px;max-width:80%">These checks evaluate how well your site signals its structure and quality to search engines, AI models, and voice assistants.</p>\n'
    html += '<table class="checks-table">\n'
    html += '  <thead><tr><th></th><th>Check</th><th>Detail</th></tr></thead>\n'
    html += '  <tbody>\n'
    html += build_checks_table(checks)
    html += '  </tbody>\n'
    html += '</table>\n'

    # Performance
    perf = data.get("performance", {})
    if perf and perf.get("metrics"):
        m = perf["metrics"]
        html += '<h2 class="section-title page-break-before">Speed &amp; Core Web Vitals</h2>\n'
        html += '<p style="font-size:11px;color:#6b7280;margin-top:-6px;max-width:80%">Google explicitly ranks sites higher if they load quickly and maintain visual stability.</p>\n'
        html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;text-align:center;margin-bottom:20px;">'
        def cwv_color(val, lim1, lim2):
            try:
                v = float(val)
                if v > lim2: return "#ef4444"
                if v > lim1: return "#f59e0b"
                return "#22c55e"
            except: return "#6b7280"
        
        tc_lcp = cwv_color(m.get('lcp', '0'), 2.5, 4.0)
        tc_cls = cwv_color(m.get('cls', '0'), 0.1, 0.25)
        tc_fcp = cwv_color(m.get('fcp', '0'), 1.8, 3.0)
        
        html += f'<div style="background:#f8fafc;padding:12px;border:1px solid #e5e7eb;border-bottom:3px solid {tc_lcp};"><div style="font-size:20px;font-weight:700;">{esc(m.get("lcp"))}</div><div style="font-size:9pt;color:#6b7280">LCP</div></div>'
        html += f'<div style="background:#f8fafc;padding:12px;border:1px solid #e5e7eb;border-bottom:3px solid {tc_cls};"><div style="font-size:20px;font-weight:700;">{esc(m.get("cls"))}</div><div style="font-size:9pt;color:#6b7280">CLS</div></div>'
        html += f'<div style="background:#f8fafc;padding:12px;border:1px solid #e5e7eb;border-bottom:3px solid {tc_fcp};"><div style="font-size:20px;font-weight:700;">{esc(m.get("fcp"))}</div><div style="font-size:9pt;color:#6b7280">FCP</div></div>'
        html += '</div>'

    # E-E-A-T Analysis
    eeat = data.get("eeat_analysis", {})
    if eeat and eeat.get("experience_score") is not None:
        html += '<h2 class="section-title">E-E-A-T Quality Analysis</h2>\n'
        html += '<p style="font-size:11px;color:#6b7280;margin-top:-6px;max-width:80%">Experience, Expertise, Authoritativeness, and Trustworthiness are critical for modern SEO, especially in YMYL (Your Money or Your Life) topics.</p>\n'
        
        html += '<div style="display:grid;grid-template-columns:100px 1fr 30px;gap:8px;font-size:11px;font-weight:600;margin-bottom:16px;">'
        for key, name in [("experience", "Experience"), ("expertise", "Expertise"), ("authority", "Authority"), ("trust", "Trust")]:
            val = eeat.get(f"{key}_score", 0)
            color = score_color(val)
            html += f'<span>{name}</span><div style="background:#e5e7eb;height:8px;margin-top:6px;"><div style="background:{color};width:{val}%;height:100%;"></div></div><span>{val}</span>'
        html += '</div>'

        if eeat.get("strengths"):
            html += '<strong style="font-size:11px">Strengths:</strong><ul style="font-size:11px;color:#22c55e;padding-left:14px;margin-bottom:8px;">'
            for s in eeat["strengths"][:3]: html += f'<li>{esc(s)}</li>'
            html += '</ul>'
            
        if eeat.get("weaknesses"):
            html += '<strong style="font-size:11px">Weaknesses:</strong><ul style="font-size:11px;color:#ef4444;padding-left:14px;margin-bottom:16px;">'
            for w in eeat["weaknesses"][:3]: html += f'<li>{esc(w)}</li>'
            html += '</ul>'

    # SERP
    serp = data.get("serp_analysis", {})
    if serp and serp.get("rankings"):
        html += '<h2 class="section-title page-break-before">SERP Keyword Visibility</h2>\n'
        html += '<p style="font-size:11px;color:#6b7280;margin-top:-6px;max-width:80%">Live Google search rankings for competitive queries. Keywords below #10 might represent "content gaps" where competitors outrank you.</p>\n'
        html += '<table class="checks-table" style="margin-bottom:20px;">'
        html += '<thead><tr><th>Query</th><th>Position</th><th>Top Competitors</th></tr></thead><tbody>'
        for r in serp["rankings"]:
            pos_badge = f'<span style="background:{"#dcfce7;color:#166534" if r["position"] <= 10 else "#f1f5f9;color:#64748b"};padding:2px 6px;border-radius:8px;font-size:10px;font-weight:700;">{r["position"]}</span>'
            comps = "<br>".join([esc(c) for c in r.get("competitors", [])[:3]]) if r.get("competitors") else "-"
            html += f'<tr class="check-row"><td><strong>{esc(r["query"])}</strong></td><td>{pos_badge}</td><td style="font-size:10px;color:#475569">{comps}</td></tr>'
        html += '</tbody></table>'

    # Recommendations
    recs = build_recommendations(checks)
    if recs:
        html += '<h2 class="section-title page-break-before">What To Do Next</h2>\n'
        html += '<div class="recommendations">\n'
        for i, rec in enumerate(recs, 1):
            impact_class = f"impact-{rec['impact'].lower()}" if rec.get("impact") else ""
            html += f'  <div class="rec-item {impact_class}">\n'
            html += f'    <div class="rec-num">{i}</div>\n'
            html += f'    <div class="rec-content">\n'
            html += f'      <div class="rec-title">{esc(rec["fix_title"])}</div>\n'
            html += f'      <div class="rec-category">{esc(rec["category"])}'
            if rec.get("impact"):
                html += f' &middot; Impact: {esc(rec["impact"])}'
            html += f'</div>\n'
            if rec.get("fix_why"):
                html += f'      <div class="rec-why">{esc(rec["fix_why"])}</div>\n'
            html += '    </div>\n'
            html += '  </div>\n'
        html += '</div>\n'

    return html


def render_comparison_table(primary_data, competitor_data):
    """Side-by-side score comparison table for comparison reports."""
    p_scores = primary_data.get("scores", {})
    c_scores = competitor_data.get("scores", {})

    p_url = primary_data.get("url", "")
    c_url = competitor_data.get("url", "")
    p_domain = urllib.parse.urlparse(p_url).netloc.replace("www.", "")
    c_domain = urllib.parse.urlparse(c_url).netloc.replace("www.", "")

    p_overall = round(
        (p_scores.get("traditional_seo", 0) + p_scores.get("ai_search", 0) +
         p_scores.get("voice_search", 0) + p_scores.get("local_search", 0)) / 4
    )
    c_overall = round(
        (c_scores.get("traditional_seo", 0) + c_scores.get("ai_search", 0) +
         c_scores.get("voice_search", 0) + c_scores.get("local_search", 0)) / 4
    )

    def cell(p_val, c_val):
        p_color = score_color(p_val)
        c_color = score_color(c_val)
        winner = "primary" if p_val >= c_val else "competitor"
        p_bold = "font-weight:700;" if winner == "primary" else ""
        c_bold = "font-weight:700;" if winner == "competitor" else ""
        diff = p_val - c_val
        diff_str = f"+{diff}" if diff > 0 else str(diff) if diff < 0 else "="
        diff_class = "diff-pos" if diff > 0 else "diff-neg" if diff < 0 else "diff-tie"
        return (
            f'<td style="color:{p_color};{p_bold}">{p_val}</td>'
            f'<td class="diff-col {diff_class}">{diff_str}</td>'
            f'<td style="color:{c_color};{c_bold}">{c_val}</td>'
        )

    html = '<h2 class="section-title">Score Comparison</h2>\n'
    html += '<table class="comparison-table">\n'
    html += (
        f'<thead><tr>'
        f'<th>Category</th>'
        f'<th>{esc(p_domain)}</th>'
        f'<th>Diff</th>'
        f'<th>{esc(c_domain)}</th>'
        f'</tr></thead>\n'
        f'<tbody>\n'
    )
    html += (
        f'<tr class="overall-row"><td><strong>Overall</strong></td>'
        f'{cell(p_overall, c_overall)}'
        f'</tr>\n'
    )
    for cat_key, cat_name in CATEGORY_NAMES.items():
        p_val = p_scores.get(cat_key, 0)
        c_val = c_scores.get(cat_key, 0)
        html += f'<tr><td>{esc(cat_name)}</td>{cell(p_val, c_val)}</tr>\n'
    html += '</tbody></table>\n'
    return html


def build_full_page(report_data, competitor_data=None, report_id="", competitor_id=""):
    """Assemble the complete HTML page."""
    url = report_data.get("url", "")
    domain = urllib.parse.urlparse(url).netloc.replace("www.", "")
    analyzed_at = format_date(report_data.get("analyzed_at", ""))
    is_comparison = competitor_data is not None

    if is_comparison:
        c_url = competitor_data.get("url", "")
        c_domain = urllib.parse.urlparse(c_url).netloc.replace("www.", "")
        page_title = f"Comparison: {esc(domain)} vs {esc(c_domain)}"
        subtitle = f"Search Readiness Comparison Report"
    else:
        page_title = f"Search Readiness Report: {esc(domain)}"
        subtitle = f"Analyzed on {esc(analyzed_at)}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title}</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
/* ===== BASE ===== */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: 'Plus Jakarta Sans', 'Helvetica Neue', Arial, sans-serif;
  font-size: 13px;
  line-height: 1.55;
  color: #1f2937;
  background: #fff;
}}

/* ===== HEADER ===== */
.report-header {{
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  color: #111827;
  padding: 28px 36px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}}
.brand {{
  display: flex;
  align-items: center;
  gap: 10px;
}}
.brand-dot {{
  width: 10px; height: 10px;
  border-radius: 50%;
  background: #2563eb;
  display: inline-block;
}}
.brand-name {{
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: #111827;
}}
.brand-sub {{
  font-size: 11px;
  color: #6b7280;
  margin-top: 1px;
}}
.report-meta {{
  text-align: right;
  font-size: 11px;
  color: #64748b;
}}
.report-meta strong {{
  color: #111827;
  font-size: 13px;
  display: block;
  margin-bottom: 2px;
}}

/* ===== MAIN CONTENT ===== */
.report-body {{
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 36px;
}}

/* ===== SCORE SUMMARY ===== */
.score-summary {{
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 24px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 28px;
  border: 1px solid #e5e7eb;
}}
.overall-score {{
  text-align: center;
  border: 3px solid;
  border-radius: 50%;
  width: 90px;
  height: 90px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px;
}}
.overall-number {{
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}}
.overall-grade {{
  font-size: 11px;
  font-weight: 600;
  margin-top: 2px;
}}
.overall-label {{
  font-size: 9px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 1px;
}}
.category-scores {{
  display: flex;
  flex: 1;
  gap: 16px;
  justify-content: space-around;
}}
.cat-score-item {{
  text-align: center;
}}
.cat-name {{
  font-size: 10px;
  color: #6b7280;
  margin-top: 2px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}}

/* ===== PAGE SUMMARY ===== */
.page-summary {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 28px;
}}
.summary-item {{
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 11px;
}}
.summary-item span {{
  display: block;
  color: #6b7280;
  margin-bottom: 2px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  font-size: 10px;
  font-weight: 600;
}}
.summary-item strong {{
  color: #111827;
  font-size: 12px;
  word-break: break-word;
}}

/* ===== SECTION TITLES ===== */
.section-title {{
  font-size: 14px;
  font-weight: 700;
  color: #111827;
  margin: 28px 0 12px;
  padding-bottom: 6px;
  border-bottom: 2px solid #e5e7eb;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}

/* ===== CHECKS TABLE ===== */
.checks-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 11.5px;
  margin-bottom: 8px;
}}
.checks-table thead th {{
  background: #f1f5f9;
  color: #475569;
  padding: 8px 10px;
  text-align: left;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.checks-table thead th:first-child {{ width: 28px; }}
.checks-table thead th:nth-child(2) {{ width: 28%; }}
.cat-header td {{
  background: #f1f5f9;
  color: #374151;
  font-weight: 700;
  font-size: 11px;
  padding: 6px 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-top: 2px solid #e5e7eb;
}}
.check-row td {{
  padding: 7px 10px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: top;
}}
.check-row:nth-child(even) {{ background: #fafafa; }}
.check-icon {{ text-align: center; }}
.icon-pass {{ color: #22c55e; font-size: 14px; }}
.icon-fail {{ color: #ef4444; font-size: 14px; }}
.icon-warn {{ color: #f59e0b; font-size: 13px; }}
.check-label {{ font-weight: 600; color: #374151; }}
.check-detail {{ color: #6b7280; font-size: 11px; }}
.fix-title {{ color: #2563eb; font-size: 10.5px; margin-top: 3px; display: block; }}

/* ===== RECOMMENDATIONS ===== */
.recommendations {{ display: grid; gap: 12px; margin-bottom: 28px; }}
.rec-item {{
  display: flex;
  gap: 14px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-left: 4px solid #6b7280;
  border-radius: 8px;
  padding: 14px;
}}
.rec-item.impact-high {{ border-left-color: #ef4444; }}
.rec-item.impact-medium {{ border-left-color: #f59e0b; }}
.rec-item.impact-low {{ border-left-color: #22c55e; }}
.rec-num {{
  font-size: 18px;
  font-weight: 800;
  color: #d1d5db;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
  line-height: 1;
  margin-top: 2px;
}}
.rec-title {{ font-weight: 700; font-size: 12.5px; color: #111827; margin-bottom: 2px; }}
.rec-category {{ font-size: 10px; color: #6b7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 4px; }}
.rec-why {{ font-size: 11px; color: #6b7280; }}

/* ===== COMPARISON TABLE ===== */
.comparison-table {{
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 28px;
  font-size: 12px;
}}
.comparison-table th {{
  background: #f1f5f9;
  color: #475569;
  padding: 10px 14px;
  text-align: center;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.comparison-table th:first-child {{ text-align: left; }}
.comparison-table td {{
  padding: 10px 14px;
  text-align: center;
  border-bottom: 1px solid #f3f4f6;
  font-size: 14px;
  font-weight: 600;
}}
.comparison-table td:first-child {{ text-align: left; font-size: 12px; font-weight: 500; }}
.comparison-table .overall-row {{ background: #f8fafc; }}
.diff-col {{ font-size: 12px; color: #9ca3af; }}
.diff-pos {{ color: #22c55e !important; }}
.diff-neg {{ color: #ef4444!important; }}
.diff-tie {{ color: #9ca3af; }}

/* ===== CTA SECTION ===== */
.cta-section {{
  background: #f8fafc;
  color: #111827;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  padding: 24px 28px;
  margin: 32px 0 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}}
.cta-headline {{ font-size: 15px; font-weight: 700; margin-bottom: 4px; }}
.cta-sub {{ font-size: 12px; color: #475569; }}
.cta-plans {{ font-size: 11px; color: #64748b; margin-top: 8px; }}
.cta-contact {{ text-align: right; flex-shrink: 0; }}
.cta-contact a {{ color: #2563eb; text-decoration: none; font-size: 12px; font-weight: 600; }}

/* ===== FOOTER ===== */
.report-footer {{
  background: #f1f5f9;
  border-top: 1px solid #e5e7eb;
  padding: 14px 36px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
  color: #9ca3af;
}}
.footer-brand {{ font-weight: 700; color: #6b7280; }}

/* ===== PRINT BUTTON (screen only) ===== */
.print-bar {{
  background: #2563eb;
  color: #fff;
  text-align: center;
  padding: 12px;
  font-size: 13px;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 100;
  cursor: pointer;
}}
.print-bar:hover {{ background: #1d4ed8; }}

/* ===== PRINT STYLES ===== */
@media print {{
  @page {{
    size: A4;
    margin: 12mm 14mm;
  }}
  body {{ font-size: 10pt; }}
  .print-bar {{ display: none !important; }}
  .report-header {{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    background: #f8fafc !important;
    border-bottom: 1px solid #e5e7eb !important;
    padding: 18px 24px;
  }}
  .report-body {{ padding: 20px 24px; }}
  .score-summary {{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    background: #f8fafc !important;
    break-inside: avoid;
  }}
  .checks-table {{
    break-inside: auto;
    font-size: 9pt;
  }}
  .checks-table thead {{
    display: table-header-group;
  }}
  .check-row {{
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  .cat-header {{
    break-after: avoid;
    page-break-after: avoid;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    background: #f1f5f9 !important;
  }}
  .rec-item {{
    break-inside: avoid;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .rec-item.impact-high {{ border-left-color: #ef4444 !important; }}
  .rec-item.impact-medium {{ border-left-color: #f59e0b !important; }}
  .rec-item.impact-low {{ border-left-color: #22c55e !important; }}
  .icon-pass {{ color: #22c55e !important; }}
  .icon-fail {{ color: #ef4444 !important; }}
  .icon-warn {{ color: #f59e0b !important; }}
  .page-break-before {{
    break-before: page;
    page-break-before: always;
  }}
  .cta-section {{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    background: #0a0a0a !important;
  }}
  .comparison-table th {{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    background: #111827 !important;
  }}
  .checks-table thead th {{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    background: #111827 !important;
  }}
  .report-footer {{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    background: #f1f5f9 !important;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
  }}
  a {{ color: inherit !important; text-decoration: none; }}
}}
</style>
</head>
<body>

<!-- PRINT BAR (hidden in print) -->
<div class="print-bar" onclick="window.print()">
  &#x2193;&nbsp; Save as PDF &nbsp;&mdash;&nbsp; Click here or use File &rarr; Print, then choose &ldquo;Save as PDF&rdquo;
</div>

<!-- HEADER -->
<div class="report-header">
  <div class="brand">
    <span class="brand-dot"></span>
    <div>
      <div class="brand-name">Alianza Connects</div>
      <div class="brand-sub">Search Readiness Intelligence</div>
    </div>
  </div>
  <div class="report-meta">
    <strong>{page_title}</strong>
    {esc(subtitle)}
  </div>
</div>

<!-- BODY -->
<div class="report-body">
"""

    if is_comparison:
        html += render_comparison_table(report_data, competitor_data)
        # Primary site
        p_url = report_data.get("url", "")
        p_domain = urllib.parse.urlparse(p_url).netloc.replace("www.", "")
        c_url = competitor_data.get("url", "")
        c_domain = urllib.parse.urlparse(c_url).netloc.replace("www.", "")
        html += f'<h2 class="section-title">Your Site: {esc(p_domain)}</h2>\n'
        html += render_single_report(report_data, is_comparison=True,
                                     competitor_data=competitor_data)
        html += f'<h2 class="section-title page-break-before">Competitor: {esc(c_domain)}</h2>\n'
        html += render_single_report(competitor_data, is_comparison=True,
                                     competitor_data=report_data)
    else:
        html += render_single_report(report_data)

    # CTA
    html += """
<div class="cta-section">
  <div>
    <div class="cta-headline">Ready to improve your Search Readiness score?</div>
    <div class="cta-sub">Alianza Connects helps home service &amp; local businesses dominate local search, AI, and voice.</div>
    <div class="cta-plans">
      <strong>Foundations</strong> $1,500/mo &mdash; SEO basics, schema, Google Business Profile &nbsp;|&nbsp;
      <strong>Growth</strong> $2,500/mo &mdash; AI search, voice, content strategy
    </div>
  </div>
  <div class="cta-contact">
    <a href="mailto:hello@alianzaconnects.com">hello@alianzaconnects.com</a><br>
    <a href="https://alianzaconnects.com">alianzaconnects.com</a>
  </div>
</div>
"""

    html += "</div><!-- /report-body -->\n"

    # FOOTER
    now_str = datetime.now().strftime("%B %d, %Y")
    html += f"""
<div class="report-footer">
  <span>Powered by <span class="footer-brand">Alianza Connects</span> &mdash; hello@alianzaconnects.com &mdash; alianzaconnects.com</span>
  <span>Generated {esc(now_str)}</span>
</div>

<script>
// Auto-trigger print dialog after a short delay so fonts load
(function() {{
  if (window.location.search.indexOf('print=1') !== -1) {{
    setTimeout(function() {{ window.print(); }}, 600);
  }}
}})();
</script>
</body>
</html>"""

    return html


# ============================================
# CGI ENTRY POINT
# ============================================

def main():
    method = os.environ.get("REQUEST_METHOD", "GET")
    query_string = os.environ.get("QUERY_STRING", "")
    params = urllib.parse.parse_qs(query_string)

    report_id = params.get("id", [None])[0]
    competitor_id = params.get("competitor_id", [None])[0]

    if not report_id:
        print("Status: 400")
        print("Content-Type: text/html; charset=utf-8")
        print()
        print("<html><body><p>Missing ?id=REPORT_ID parameter.</p></body></html>")
        return

    report_data = fetch_report(report_id)
    if not report_data:
        print("Status: 404")
        print("Content-Type: text/html; charset=utf-8")
        print()
        print("<html><body><p>Report not found. It may have expired or the ID is incorrect.</p></body></html>")
        return

    competitor_data = None
    if competitor_id:
        competitor_data = fetch_report(competitor_id)
        # If competitor not found, degrade gracefully to single report

    # Track download
    track_pdf_download(report_id, competitor_id)

    # Build HTML page
    page_html = build_full_page(
        report_data,
        competitor_data=competitor_data,
        report_id=report_id,
        competitor_id=competitor_id or "",
    )

    print("Content-Type: text/html; charset=utf-8")
    print()
    sys.stdout.write(page_html)


if __name__ == "__main__":
    main()
