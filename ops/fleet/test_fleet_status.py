"""Each flag must be able to fire and to stay silent (guard-that-cannot-fire rule)."""
import datetime as dt
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("fleet_status", Path(__file__).with_name("fleet_status.py"))
fs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fs)
NOW = dt.datetime(2026, 9, 30, 12, 0, tzinfo=dt.timezone.utc)
FRESH = {"mwo_id": "MWO-0004", "updated_at_utc": "2026-09-30T11:00:00Z", "state": "ACTIVE", "current": "x"}


def test_fresh_seat_has_no_flags():
    assert fs.flags_for(FRESH, "MWO-0004", NOW, 12) == []


def test_each_flag_fires():
    assert any(f.startswith("STALE_MWO") for f in fs.flags_for(dict(FRESH, mwo_id="MWO-0001"), "MWO-0004", NOW, 12))
    assert any(f.startswith("STALE_UPDATE") for f in fs.flags_for(dict(FRESH, updated_at_utc="2026-09-29T01:00:00Z"), "MWO-0004", NOW, 12))
    assert any(f.startswith("STALE_UPDATE") for f in fs.flags_for(dict(FRESH, updated_at_utc=None), "MWO-0004", NOW, 12))
    noq = dict(FRESH); del noq["current"]
    assert "NO_QUEUE" in fs.flags_for(noq, "MWO-0004", NOW, 12)
    assert "IDLE_HOLD" in fs.flags_for(dict(FRESH, state="HOLD"), "MWO-0004", NOW, 12)
    assert "IDLE_HOLD" not in fs.flags_for(dict(FRESH, state="HOLD", blocked_on=["x"]), "MWO-0004", NOW, 12)
