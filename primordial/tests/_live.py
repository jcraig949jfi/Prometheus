"""Per-lane Redis database for live tests.

Eight builder sessions run this suite concurrently before pushing. Live fixtures
that shared one database (db 15, flushed by every run) wiped each other mid-test
(2026-09-14: W's and F's O5/F7 flakes). Each lane now gets its own database on the
substrate; db 0 is the live bus and is never used by tests.

The lane is read from the environment when this module is imported, i.e. before
any test monkeypatches PM_LANE. PM_TEST_DB overrides it.
"""
from __future__ import annotations

import os

SUBSTRATE = "redis://127.0.0.1:6390"
LANE_DB = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
           "P": 9, "Q": 10, "W": 11, "T": 12, "U": 13}
DEFAULT_DB = 14                      # no lane set (e.g. a human running pytest); 15 stays free
_SESSION_LANE = os.environ.get("PM_LANE", "")


def live_db() -> int:
    override = os.environ.get("PM_TEST_DB", "").strip()
    if override:
        db = int(override)
        if db == 0:
            raise ValueError("PM_TEST_DB=0 is the live bus")
        return db
    return LANE_DB.get(_SESSION_LANE, DEFAULT_DB)


def live_url() -> str:
    return f"{SUBSTRATE}/{live_db()}"
