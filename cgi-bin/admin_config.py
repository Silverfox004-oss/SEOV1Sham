#!/usr/bin/env python3
"""
Admin Config Endpoint — serves Supabase connection info to the admin dashboard.
Only exposes the anon key (which is safe for client-side use with RLS).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import SUPABASE_URL, SUPABASE_KEY

print("Content-Type: application/json")
print("Cache-Control: no-cache")
print()

if SUPABASE_URL and SUPABASE_KEY:
    print(json.dumps({
        "supabase_url": SUPABASE_URL,
        "supabase_key": SUPABASE_KEY
    }))
else:
    print(json.dumps({
        "error": "Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY environment variables."
    }))
