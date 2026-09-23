"""F-R6-3 (D6, gate item 19): a measured cost is filed against its refusal stub by code, and the close
tally reads open stubs from code. A filing closes exactly its stub, once; malformed filings are refused."""
from __future__ import annotations

import pytest

from primordial.fabric import envelope as EV
from primordial.tests._live import live_url

URL = live_url()


@pytest.fixture
def r(monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    monkeypatch.setenv("PM_LANE", "F")
    monkeypatch.setenv("PM_TAG", "t-r6-3")
    keys = [EV.EVENTS, EV.CANDIDATES, EV.FILED]
    r.delete(*keys)
    yield r
    r.delete(*keys)


def refuse(r, exp):
    v = EV.admit(EV.example(wall_budget_s=10 ** 5, predicate_id=f"P-{exp}"))
    return EV.refuse(r, "E", {"job_id": f"j-{exp}", "fn": "m:f", "exp_id": exp}, v, EV.example(wall_budget_s=10 ** 5))


def test_file_candidate_closes_its_stub(r):
    a, b = refuse(r, "clauseB"), refuse(r, "b2")
    assert a["stub_id"] and b["stub_id"] and a["stub_id"] != b["stub_id"]
    assert [s["stub_id"] for s in EV.open_candidates(r)] == [a["stub_id"], b["stub_id"]]
    got = EV.file_candidate(r, a["stub_id"], {"wall_s": 1440.0, "cpu_s": 3200.0}, "rows/E/E-R5-1.jsonl@cd691d3f0")
    assert got["ok"] and got["filing"]["lane"] == "F" and got["filing"]["tag"] == "t-r6-3"
    assert [s["stub_id"] for s in EV.open_candidates(r)] == [b["stub_id"]]
    filed = EV.filed_candidates(r)
    assert [s["exp_id"] for s in filed] == ["clauseB"] and filed[0]["filing"]["measured_cost"]["cpu_s"] == 3200.0
    assert [e["stub_id"] for e in EV.events(r, "CANDIDATE_FILED")] == [a["stub_id"]]


def test_file_candidate_refusals(r):
    a = refuse(r, "x")
    assert EV.file_candidate(r, "1-0", {"wall_s": 1}, "b")["reason"] == "NO_STUB"
    for bad in ({}, {"wall_s": -1}, {"wall_s": "10"}, {"ok": True}, ["wall_s", 1]):
        assert EV.file_candidate(r, a["stub_id"], bad, "basis")["reason"] == "BAD_COST", bad
    assert EV.file_candidate(r, a["stub_id"], {"wall_s": 1}, "  ")["reason"] == "NO_BASIS"
    assert EV.file_candidate(r, a["stub_id"], {"wall_s": 1}, "first")["ok"]
    again = EV.file_candidate(r, a["stub_id"], {"wall_s": 2}, "second")
    assert again["reason"] == "ALREADY_FILED" and again["filing"]["basis"] == "first"
    assert EV.open_candidates(r) == []


def test_stubless_refusal_returns_no_stub_id(r):
    ev = EV.refuse(r, "F", {"job_id": "j"}, {"event": "CODE_FINGERPRINT_MISMATCH", "reasons": ["X"], "stage": None,
                                             "ceiling": None}, None, stub=False)
    assert ev["stub_id"] is None and EV.open_candidates(r) == []
