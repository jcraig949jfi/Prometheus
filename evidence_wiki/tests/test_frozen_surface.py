"""The Campaign 4 observation surface is frozen: the code's identities must
equal the pinned file (order s7). A drift here is the test failing, which is
the point -- a change is then a named decision with a version transition,
not a silent edit.

    positive   pinned == live
    cheat      a changed threshold changes the surface digest
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from ew import frozen_surface as fs  # noqa: E402


def test_pinned_surface_equals_live_code():
    pinned = json.loads(fs.PINNED.read_text(encoding="utf-8"))
    live = fs.live()
    live["surface_digest"] = fs.digest(live)
    diffs = {k: (pinned.get(k), live.get(k)) for k in set(pinned) | set(live) if pinned.get(k) != live.get(k)}
    assert not diffs, f"frozen surface drifted: {json.dumps(diffs, default=str)[:800]}"


def test_cheat_threshold_change_moves_the_digest(monkeypatch):
    from ew import projections as pj
    before = fs.digest(fs.live())
    monkeypatch.setattr(pj, "SUMMIT_MIN", 0.5)
    after = fs.digest(fs.live())
    assert before != after
