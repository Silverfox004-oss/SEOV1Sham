"""
Backend rate limiter — 1 free scan per verified email or phone per month.
Tracks by contact identity (email or phone), not by IP.
"""

import os
import sqlite3
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data.db")

# 30 days in seconds
WINDOW_SECONDS = 30 * 24 * 60 * 60


def _get_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS scan_limits (
            identity TEXT NOT NULL,
            identity_type TEXT NOT NULL,
            scanned_at REAL NOT NULL
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_scan_limits_identity ON scan_limits (identity, scanned_at)")
    db.commit()
    return db


def check_rate_limit(email="", phone=""):
    """
    Check if this email or phone has already used their free scan this month.
    Returns (allowed: bool, days_remaining: int).
    Both email and phone are required fields, but we check both —
    if either has been used in the last 30 days, they're rate-limited.
    """
    if not email and not phone:
        return True, 0  # No identity to check against

    now = time.time()
    cutoff = now - WINDOW_SECONDS

    try:
        db = _get_db()

        # Clean entries older than 30 days
        db.execute("DELETE FROM scan_limits WHERE scanned_at < ?", (cutoff,))
        db.commit()

        # Check if either email or phone was used recently
        for identity, id_type in [(email.lower(), "email"), (phone, "phone")]:
            if not identity:
                continue
            row = db.execute(
                "SELECT scanned_at FROM scan_limits WHERE identity = ? AND scanned_at >= ? ORDER BY scanned_at DESC LIMIT 1",
                (identity, cutoff)
            ).fetchone()
            if row:
                days_remaining = max(1, int((row[0] + WINDOW_SECONDS - now) / 86400) + 1)
                db.close()
                return False, days_remaining

        # Record this scan for both email and phone
        for identity, id_type in [(email.lower(), "email"), (phone, "phone")]:
            if identity:
                db.execute(
                    "INSERT INTO scan_limits (identity, identity_type, scanned_at) VALUES (?, ?, ?)",
                    (identity, id_type, now)
                )
        db.commit()
        db.close()
        return True, 0

    except Exception:
        return True, 0
