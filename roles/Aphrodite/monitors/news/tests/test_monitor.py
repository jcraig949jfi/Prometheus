"""The operator's limits for the news monitor, as tests (APHRODITE-12, 2026-09-18)."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import monitor as M  # noqa: E402

TARGETS = {"theory": {"T0", "T4"}, "question": {"O1", "D3"}, "design": {"RSI_PROGRAM_v2.md"},
           "precedent": {"RSI_PROGRAM_v2.md"}, "text": {"_": "swe-bench osworld hyperagents"}}


def cand(i, admit=True, **kw):
    c = {"title": f"t{i}", "url": f"https://example.org/p{i}", "dedupe_key": f"2609.9{i:04d}",
         "primary_source_read": True, "admit": admit, "target_type": "theory", "target_id": "T4",
         "change": "changes T4"}
    c.update(kw)
    return c


def test_limits_constants_are_the_operators():
    assert (M.MAX_INSPECT, M.MAX_ADMIT, M.EXPIRY_DAYS, M.BOUND_EMPTY) == (8, 3, 30, 4)


def test_inspect_cap_truncates_to_8():
    r = M.validate({"candidates": [cand(i, admit=False) for i in range(12)]}, set(), TARGETS)
    assert len(r["candidates"]) == 8 and any("truncated" in v for v in r["violations"])


def test_admit_cap_is_3():
    r = M.validate({"candidates": [cand(i) for i in range(6)]}, set(), TARGETS)
    assert len(r["admitted"]) == 3


def test_primary_source_required():
    r = M.validate({"candidates": [cand(1, primary_source_read=False)]}, set(), TARGETS)
    assert not r["admitted"] and "primary source" in r["candidates"][0]["not_admitted_because"]


def test_dedupe_against_library():
    r = M.validate({"candidates": [cand(1, dedupe_key="2609.17817v2")]}, {"2609.17817"}, TARGETS)
    assert not r["admitted"] and "duplicate" in r["candidates"][0]["not_admitted_because"]


def test_must_change_a_named_existing_item():
    bad = [cand(1, target_id="T99"), cand(2, target_type="vibes"), cand(3, target_type="benchmark",
           target_id="NoSuchBench"), cand(4, change="")]
    r = M.validate({"candidates": bad}, set(), TARGETS)
    assert not r["admitted"] and len(r["candidates"]) == 4
    ok = [cand(5, target_type="question", target_id="O1"), cand(6, target_type="benchmark", target_id="OSWorld"),
          cand(7, target_type="precedent", target_id="RSI_PROGRAM_v2.md s0")]
    assert len(M.validate({"candidates": ok}, set(), TARGETS)["admitted"]) == 3


def test_expiry_after_30_days():
    today = dt.date(2026, 10, 30)
    cs = [{"dedupe_key": "a", "first_seen": "2026-09-30"}, {"dedupe_key": "b", "first_seen": "2026-10-01"}]
    keep, n = M.expire(cs, today)
    assert [c["dedupe_key"] for c in keep] == ["b"] and n == 1


def test_pause_after_4_consecutive_empty_and_reset_on_admission():
    s = {}
    for i in range(3):
        s = M.step_state(s, 0, f"t{i}", True)
        assert not s.get("paused")
    s2 = M.step_state(s, 1, "t3", True)
    assert s2["consecutive_empty"] == 0 and not s2.get("paused")
    s = M.step_state(s, 0, "t3", True)
    assert s["paused"] and s["pause_reported"] is False and s["consecutive_empty"] == 4


def test_error_pass_counts_as_empty():
    s = {}
    for i in range(4):
        s = M.step_state(s, 0, f"t{i}", False)
    assert s["paused"] and "last_input_at" not in s


def test_pause_is_reported_once_flag_survives_further_steps():
    s = {"consecutive_empty": 3}
    s = M.step_state(s, 0, "t", True)
    s["pause_reported"] = True
    s = M.step_state(s, 0, "t2", True)
    assert s["paused"] and s["pause_reported"] is True
