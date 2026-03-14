"""
Backend rate limiter using SQLite.
Tracks requests per IP and enforces configurable limits.
Import and call check_rate_limit() at the top of your CGI handler.
"""

import os
import sqlite3
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data.db")

# Defaults: 5 scans per IP per 10-minute window
MAX_REQUESTS = int(os.environ.get("RATE_LIMIT_MAX", "5"))
WINDOW_SECONDS = int(os.environ.get("RATE_LIMIT_WINDOW", "600"))


def _get_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS rate_limits (
            ip TEXT NOT NULL,
            ts REAL NOT NULL
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_rate_ip_ts ON rate_limits (ip, ts)")
    db.commit()
    return db


def check_rate_limit(ip=None):
    """
    Check if the given IP is within rate limits.
    Returns (allowed: bool, retry_after: int seconds).
    """
    if not ip:
        ip = os.environ.get("REMOTE_ADDR", "unknown")

    if ip in ("127.0.0.1", "::1", "unknown"):
        return True, 0

    now = time.time()
    cutoff = now - WINDOW_SECONDS

    try:
        db = _get_db()

        # Clean old entries
        db.execute("DELETE FROM rate_limits WHERE ts < ?", (cutoff,))

        # Count recent requests
        row = db.execute(
            "SELECT COUNT(*) FROM rate_limits WHERE ip = ? AND ts >= ?",
            (ip, cutoff)
        ).fetchone()
        count = row[0] if row else 0

        if count >= MAX_REQUESTS:
            # Find oldest entry to calculate retry_after
            oldest = db.execute(
                "SELECT MIN(ts) FROM rate_limits WHERE ip = ? AND ts >= ?",
                (ip, cutoff)
            ).fetchone()
            retry_after = int((oldest[0] + WINDOW_SECONDS) - now) + 1 if oldest and oldest[0] else WINDOW_SECONDS
            db.close()
            return False, max(1, retry_after)

        # Record this request
        db.execute("INSERT INTO rate_limits (ip, ts) VALUES (?, ?)", (ip, now))
        db.commit()
        db.close()
        return True, 0

    except Exception:
        # If rate limiting fails, allow the request
        return True, 0
