"""
Alianza Search Readiness Scanner — Supabase REST API Client
"""

import json
import ssl
import urllib.parse
import urllib.request

from config import SUPABASE_URL, SUPABASE_KEY


def supabase_request(path, method="GET", data=None, params=None):
    """Make a request to Supabase REST API. Returns parsed JSON or None on error."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
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
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
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
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
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
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
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
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
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
