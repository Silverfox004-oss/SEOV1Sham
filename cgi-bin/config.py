"""
Alianza Search Readiness Scanner — Configuration
Loads environment variables from .env file and provides config constants.
"""

import os


def _load_env_file():
    """Load .env file from project root if it exists."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


_load_env_file()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
VALUESERP_API_KEY = os.environ.get("VALUESERP_API_KEY", "")
GOOGLE_PSI_API_KEY = os.environ.get("GOOGLE_PSI_API_KEY", "")
