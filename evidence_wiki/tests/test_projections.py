"""Projections: the pinned copy of Archaeon's level rule, and rebuild
determinism, without a database.

    pin       level_of() equals archaeon/wse/reachability.py's on the cases
              that matter, including D3-006 (a training-only 0.9375 with
              held-out 0.53 is SHELF, not SUMMIT; an unconfirmed candidate
              with no held-out at all is SHELF)
    digest    the rebuild digest is order-independent and content-sensitive
    registry  every definition carries the fields the order requires
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from ew import projections as pj  # noqa: E402


def test_pinned_level_of_matches_archaeon_cases():
    assert pj.level_of(None) == "FLOOR"
    assert pj.level_of(0.21875, 0.0417) == "FLOOR"
    assert pj.level_of(0.53125, 0.53125) == "SHELF"
    assert pj.level_of(0.9375, 0.53) == "SHELF"          # D3-006: unconfirmed candidate
    assert pj.level_of(0.9375, None) == "SHELF"          # no held-out: candidate, not summit
    assert pj.level_of(1.0, 1.0) == "SUMMIT"
    assert pj.level_of(0.45, 0.1) == "SHELF" and pj.level_of(0.4499, 0.9) == "FLOOR"


def test_thresholds_are_the_pinned_ones():
    assert (pj.FOOTHOLD_MIN, pj.SHELF_MIN, pj.SUMMIT_MIN) == (0.5, 0.45, 0.90)
    d = pj.DEFINITIONS[("reach_level", "v1")]
    assert d["thresholds"]["SUMMIT_MIN"] == 0.90 and d["owner_seat"] == "Archaeon"


def test_rebuild_digest_order_independent_and_content_sensitive():
    rows = [("obs:a", {"x": 1}, ["CO-1"]), ("obs:b", {"x": 2}, ["CO-2"])]
    assert pj.rows_digest(rows) == pj.rows_digest(list(reversed(rows)))
    assert pj.rows_digest(rows) != pj.rows_digest([("obs:a", {"x": 1}, ["CO-1"]), ("obs:b", {"x": 3}, ["CO-2"])])


def test_every_definition_carries_required_fields():
    for key, d in pj.DEFINITIONS.items():
        for f in ("definition", "source_kinds", "thresholds", "owner_seat", "limitations"):
            assert d.get(f), (key, f)
        assert key in pj.BUILDERS
