"""cheatlib self-controls.

Base role s2: every change ships with a POSITIVE control and a CHEAT
control where the change is measured; a NEGATIVE control is welcome but
does not substitute.

    NEGATIVE  the library does not invent signal where there is none
    POSITIVE  the library detects a real leak when one is present
    CHEAT     the measurement channel can observe the thing claimed --
              fired here against a KNOWN population (the April Nemesis
              ledger, where the constant responder is known to score
              0.674) so that a control which has gone silent is visible.

Nemesis constraint 5: a cheat control that has never fired is not a
control. test_cheat_* below is that firing, and it is pinned to an exact
number so that a change which quietly disarms it fails here.
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "roles" / "Nemesis" / "science"))

from cheatlib import (  # noqa: E402
    DegenerateConstant, MajorityClass, PayloadReader,
    chance_floor, score_responder, shrink,
    borrow_real_path, token_from_file, filler, absent_marker,
)

APRIL_LEDGER = "agents/nemesis/adversarial/adversarial_results.jsonl"


def _april_records():
    """The April ledger, read from the COMMITTED blob, not the working tree.

    Reading the blob means this fixture cannot be altered by an edit to the
    checkout, and it works in a sparse worktree where the file is absent.
    """
    r = subprocess.run(["git", "show", "HEAD:" + APRIL_LEDGER],
                       cwd=str(REPO), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        pytest.skip("April ledger blob not reachable from HEAD")
    return [json.loads(l) for l in r.stdout.splitlines() if l.strip()]


# --- NEGATIVE ---------------------------------------------------------------

def test_negative_constant_responder_scores_near_zero_on_a_flat_population():
    """No majority class to exploit, so a constant answer earns almost nothing."""
    answers = [str(i) for i in range(100)]
    items = [{"correct": a} for a in answers]
    hits, eligible, rate = score_responder(
        DegenerateConstant("0"), items, lambda it: it["correct"])
    assert eligible == 100
    assert hits == 1 and rate == 0.01


def test_negative_chance_floor_reports_the_flat_case_honestly():
    cf = chance_floor([str(i) for i in range(50)])
    assert cf.eligible == 50 and cf.distinct_answers == 50
    assert cf.majority_rate == pytest.approx(0.02)


def test_negative_payload_reader_returns_none_when_there_is_no_leak():
    r = PayloadReader(lambda it: it["not_a_field"], "missing")
    assert r.respond({"q": "x"}) is None


# --- POSITIVE ---------------------------------------------------------------

def test_positive_payload_reader_ties_the_answer_when_the_leak_is_real():
    """A population whose items carry their own answer is scored 1.0 by a
    reader that does no reasoning at all."""
    items = [{"q": "hard question %d" % i, "truth": "ans%d" % i} for i in range(40)]
    hits, eligible, rate = score_responder(
        PayloadReader(lambda it: it["truth"], "truth"), items, lambda it: it["truth"])
    assert (hits, eligible, rate) == (40, 40, 1.0)


def test_positive_majority_class_finds_the_real_imbalance():
    answers = ["yes"] * 70 + ["no"] * 30
    mc = MajorityClass(answers)
    assert mc.value == "yes"
    items = [{"correct": a} for a in answers]
    _, _, rate = score_responder(mc, items, lambda it: it["correct"])
    assert rate == pytest.approx(0.70)


def test_positive_shrink_reaches_the_known_minimum():
    """A candidate crosses while its length is >= 5; shrink must find 5."""
    crosses = lambda s: len(s) >= 5
    reductions = [("drop_one_char", lambda s: s[:-1] if len(s) > 1 else None)]
    out = shrink("x" * 40, crosses, reductions, cost=len)
    assert out.final_cost == 5 and out.start_cost == 40
    assert len(out.steps) == 35


# --- CHEAT ------------------------------------------------------------------

def test_cheat_constant_responder_fires_at_0674_on_the_april_ledger():
    """THE FIRING FIXTURE (Nemesis constraint 5).

    On this seat's own April ledger a three-word constant string scores
    0.674 and 292 of 294 tools score below it. The number is pinned so
    that a change which disarms the cheat control fails HERE rather than
    going quiet in a campaign.
    """
    recs = _april_records()
    assert len(recs) == 92, "April ledger is 92 records, got %d" % len(recs)
    correct = [r["correct"] for r in recs]
    cf = chance_floor(correct, [len(r["candidates"]) for r in recs])
    assert cf.majority_value == "Not enough information"
    assert cf.majority_rate == pytest.approx(62 / 92)
    assert round(cf.majority_rate, 3) == 0.674

    items = [{"correct": c} for c in correct]
    hits, eligible, rate = score_responder(
        MajorityClass(correct), items, lambda it: it["correct"])
    assert (hits, eligible) == (62, 92)
    assert rate == pytest.approx(cf.majority_rate)


def test_cheat_the_april_tool_population_mostly_loses_to_the_constant():
    """The instrument under test in April was beaten by cheatlib's cheapest
    member. Pinned so the claim cannot rot silently."""
    recs = _april_records()
    tools = sorted({t for r in recs for t in r["tool_results"]})
    assert len(tools) == 294
    n = len(recs)
    acc = {t: sum(1 for r in recs if r["tool_results"].get(t, {}).get("correct")) / n
           for t in tools}
    floor = 62 / 92
    beaten = [t for t in tools if acc[t] <= floor]
    assert len(beaten) == 292, "expected 292 tools at or below the floor, got %d" % len(beaten)


def test_cheat_forgeries_satisfy_their_predicates_without_meaning():
    rng = random.Random(20260911)
    target = REPO / "roles" / "base-role" / "RESPONSIBILITIES.md"
    if not target.is_file():
        pytest.skip("base role file not present in this sparse worktree")

    tok = token_from_file(target, rng, length=1)
    assert tok is not None and len(tok) == 1
    assert tok in target.read_text(encoding="utf-8", errors="replace")

    assert len(filler(20, rng)) == 20
    marker = absent_marker(rng)
    assert marker.startswith("nemz") and len(marker) == 28

    p = borrow_real_path([str(target)], rng)
    assert Path(p).is_file()


def test_cheat_absent_marker_really_is_absent_from_the_tracked_tree():
    """The forgery's guarantee is checked against the real search, not asserted."""
    rng = random.Random(7)
    marker = absent_marker(rng)
    r = subprocess.run(["git", "grep", "--cached", "-l", "-F", "--", marker],
                       cwd=str(REPO), capture_output=True, text=True, timeout=300)
    assert r.returncode == 1 and r.stdout.strip() == ""


# --- the library refuses to lie about its own inputs ------------------------

def test_chance_floor_refuses_an_empty_population():
    with pytest.raises(ValueError):
        chance_floor([])


def test_shrink_refuses_a_candidate_that_does_not_cross():
    with pytest.raises(ValueError):
        shrink("x", lambda s: False, [], cost=len)
