"""
Alianza Search Readiness Scanner — External API Integrations
PageSpeed Insights, OpenAI E-E-A-T analysis, ValueSerp SERP tracking.
"""

import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

from config import OPENAI_API_KEY, VALUESERP_API_KEY, GOOGLE_PSI_API_KEY


def get_pagespeed_scores(url):
    """
    Fetch mobile performance metrics from Google PageSpeed Insights API.
    Falls back to a heuristic estimation if API key is missing or call fails.
    """
    fallback = {
        "score": 65,
        "metrics": {"lcp": "2.5s", "cls": "0.1", "fcp": "1.8s"},
        "from_api": False
    }

    if not GOOGLE_PSI_API_KEY:
        return fallback

    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={urllib.parse.quote(url)}&strategy=mobile&key={GOOGLE_PSI_API_KEY}"

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


def analyze_content_quality_llm(text, title, industry):
    """
    Sends content to GPT-4o-mini to calculate E-E-A-T sub-scores.
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
                "response_format": {"type": "json_object"}
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
    Uses OpenAI to generate highly-relevant search queries for SERP tracking.
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
            position = 999
            top_competitors = []

            for item in organic:
                item_pos = item.get("position", 999)
                item_domain = item.get("domain", "")
                if not item_domain:
                    item_domain = urllib.parse.urlparse(item.get("link", "")).netloc.lower()
                item_domain = item_domain.lower().replace("www.", "")

                if len(top_competitors) < 3 and item_domain != domain:
                    top_competitors.append(item_domain)

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

        time.sleep(0.3)

    visibility = int((page1_count / len(queries)) * 100) if queries else 0

    return {
        "enabled": True,
        "rankings": rankings,
        "visibility_score": visibility
    }
