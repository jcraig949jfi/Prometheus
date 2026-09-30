"""frontier/4: suppression enforcement echoes aggregate per decision tuple (Archaeon #735), and nothing else merges."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from atlas.harvest import frontier as F  # noqa: E402

STATE = {"verdict": "CLIFF_SURVIVES", "falsifier_status": "FALSIFIER_FAILED", "neighbourhood_exhausted": False}


def _ev(at, sup="PROTEUS-46", t="C4-cliff.T1", lid="LIN-cb15a0ad", state=STATE):
    p = {"suppression": sup, "transformation": t, "source_state": dict(state)}
    return {"kind": "BLOCKED_BY_SUPPRESSION", "lineage_id": lid, "at": at, "payload": p}, p


def _feed(rows):
    echoes = {}
    for line, (ev, p) in rows:
        F._echo(echoes, ev, p, line)
    return echoes


def test_identical_retries_become_one_decision_with_count_range_and_runs():
    rows = [(10, _ev("2026-09-19T01:00Z"))] + [(n, _ev("2026-09-21T21:{:02d}Z".format(n % 60))) for n in range(20, 25)] \
        + [(40, _ev("2026-09-22T19:00Z"))]
    e = _feed(rows)
    assert len(e) == 1
    a = next(iter(e.values()))
    assert a["n"] == 7 and a["first_line"] == 10 and a["last_line"] == 40
    assert a["runs"] == [[10, 10], [20, 24], [40, 40]]
    assert a["first_at"] == "2026-09-19T01:00Z" and a["last_at"] == "2026-09-22T19:00Z"


def test_distinguishing_fields_keep_decisions_apart():   # CHEAT control: aggregation must not erase a real difference
    rows = [(1, _ev("a")), (2, _ev("b", sup="PROTEUS-47")), (3, _ev("c", t="X.T2")), (4, _ev("d", lid="LIN-other")),
            (5, _ev("e", state={**STATE, "neighbourhood_exhausted": True}))]
    assert len(_feed(rows)) == 5


def test_source_state_key_order_does_not_split_a_decision():
    reordered = {k: STATE[k] for k in reversed(list(STATE))}
    assert len(_feed([(1, _ev("a")), (2, _ev("b", state=reordered))])) == 1
