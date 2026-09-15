"""H-R4-2: F12 reads worlds_r4.json (active variant only) and scores clause A per SWARM_R4 s4."""
from __future__ import annotations

import json

import pytest

from primordial.score import clause_a_r4 as CA

VARIANTS = ("four_policy|CULL", "four_policy|HOLD", "gate_in|CULL", "gate_in|HOLD")


def _cell(world, pressure, active, other=None, floor=100.0, base_median=200.0, base_bytes=64):
    vs = {v: dict(other or {"verdict": "CULLED", "cull_reason": "WEAK_WORLD", "floor": floor}) for v in VARIANTS}
    vs["gate_in|HOLD"] = active
    return {"world": world, "pressure": pressure, "floor": floor, "gate_held64": floor,
            "baseline": {"median": base_median, "ci95": [base_median - 20, base_median + 20], "bytes": base_bytes,
                         "n_runs": 8}, "verdicts": vs}


@pytest.fixture
def doc():
    return {"schema": "worlds_r4/v1", "q1_floor_policy": "gate_in", "q2_policy": "HOLD", "cells": [
        _cell("w1", "train8_held64", {"verdict": "SURVIVED", "cull_reason": None, "floor": 100.0}),
        _cell("w1", "train128_held64", {"verdict": "HELD", "cull_reason": None, "floor": 170.0}),
        _cell("w3", "train8_held64", {"verdict": "CULLED", "cull_reason": "BASELINE", "floor": 122.6}),
        _cell("w9", "train8_held64", {"verdict": "CULLED", "cull_reason": "NOT_REACHED", "floor": 50.0}),
        # non-survivable, HELD vs CULLED waits for the train128 learner: PENDING in HOLD variants,
        # CULLED with cull_reason PENDING in CULL variants (G 1789440338587-0)
        _cell("w7", "train128_held64", {"verdict": "PENDING", "cull_reason": None, "floor": 1400.0},
              other={"verdict": "CULLED", "cull_reason": "PENDING", "floor": 110.0}),
        # four_policy variants say SURVIVED here; the active gate_in|HOLD says CULLED
        _cell("w4", "train8_held64", {"verdict": "CULLED", "cull_reason": "WEAK_WORLD", "floor": 107.75},
              other={"verdict": "SURVIVED", "cull_reason": None, "floor": 90.0}),
    ]}


def test_screen_reads_the_active_variant_only(doc):
    assert CA.screen_of(doc, "w1", "train8_held64")["status"] == "SURVIVED"
    assert CA.screen_of(doc, "w1", "train128_held64")["status"] == "HELD"
    assert CA.screen_of(doc, "w3", "train8_held64")["status"] == "CULLED"
    assert CA.screen_of(doc, "w9", "train8_held64")["status"] == "NOT_REACHED"
    assert CA.screen_of(doc, "w4", "train8_held64")["status"] == "CULLED"
    assert CA.screen_of(doc, "w7", "train8_held64")["status"] == "UNSCREENED"
    assert CA.screen_of(doc, "w7", "train128_held64")["status"] == "PENDING"
    cull = dict(doc, q2_policy="CULL")
    assert CA.screen_of(cull, "w7", "train128_held64")["status"] == "CULLED"   # cull_reason PENDING: still CULLED
    assert CA.screen_of(None, "w1", "train8_held64")["status"] == "UNSCREENED"
    assert CA.screen_of(doc, "w1", "train8_held64")["floor"] == 100.0       # floor from the file, not derived


@pytest.mark.parametrize("median,nbytes,verdict", [
    (194.0, 32, "FAIL"),            # progress 0.94
    (195.0, 32, "PASS"),            # progress 0.95 exactly
    (99.0, 32, "BELOW_FLOOR"),      # progress -0.01
    (200.0, 64, "FAIL"),            # progress 1.0 but a bytes tie is not fewer bytes
    (250.0, 65, "FAIL"),            # above baseline at more bytes
])
def test_s4_planted_candidates(doc, median, nbytes, verdict):
    got = CA.s4_verdict(CA.screen_of(doc, "w1", "train8_held64"), median, nbytes, 8)
    assert got["verdict"] == verdict
    assert got["progress"] == pytest.approx((median - 100.0) / 100.0)


def test_s4_ineligible_off_the_survivor_list_and_on_gates(doc):
    for w, p, why in (("w7", "train8_held64", "UNSCREENED"), ("w3", "train8_held64", "CULLED"),
                      ("w1", "train128_held64", "HELD"), ("w9", "train8_held64", "NOT_REACHED"),
                      ("w7", "train128_held64", "PENDING")):
        got = CA.s4_verdict(CA.screen_of(doc, w, p), 10**6, 1, 8)
        assert got == {"verdict": "INELIGIBLE", "why": why}
    scr = CA.screen_of(doc, "w1", "train8_held64")
    assert CA.s4_verdict(scr, 199.0, 1, 7)["verdict"] == "INELIGIBLE"
    assert CA.s4_verdict(scr, 199.0, 1, 8, oracle_clean=False)["why"] == "oracles not clean"
    assert CA.s4_verdict(scr, 199.0, 1, 8, cheats_fail=False)["verdict"] == "INELIGIBLE"


def test_progress_ci_is_the_median_ci_mapped_through_the_formula(doc):
    from primordial.metric.ci import median_ci
    held = {str(i): 180.0 + 3 * i for i in range(8)}
    got = CA.s4_verdict(CA.screen_of(doc, "w1", "train8_held64"), 190.5, 32, 8, held=held)
    lo, hi = median_ci(list(held.values()))
    assert got["progress_ci"] == pytest.approx([(lo - 100) / 100, (hi - 100) / 100])


def _row(world, pressure, median, nbytes=32, exp="B-R4-1", runs=8):
    return {"cell": {"world": world, "pressure": pressure, "representation": "int2", "substrate": "numba",
                     "channel": "none"}, "cohort": "B", "status": "record", "exp_id": exp, "ts": 10.0,
            "fitness": {"held64_median": median, "iqr": 1.0, "n_runs": runs},
            "footprint": {"genome_bytes": nbytes}}


def test_compression_scores_only_survivors_confirmed_by_the_judge(doc):
    qd = [_row("w1", "train8_held64", 195.0, exp="pass"), _row("w1", "train8_held64", 194.0, exp="fail"),
          _row("w3", "train8_held64", 999.0, exp="culled"), _row("w1", "train128_held64", 999.0, exp="held"),
          _row("w7", "train8_held64", 999.0, exp="unscreened")]
    calls = []

    def judge(rows, world, pressure, median, iqr, nbytes, runs, held=None, doc=None):
        assert doc is not None                                        # F12 hands the judge its own file
        calls.append((world, pressure))
        scr = CA.screen_of(doc, world, pressure)
        return {"verdict": "PASS", "clause_a_r4": CA.s4_verdict(scr, median, nbytes, runs, held)}

    got = CA.compression_r4(qd, "B", (0, 100), doc, check=judge)
    assert calls == [("w1", "train8_held64")] * 2                    # never consulted off the survivor list
    assert got["value"] == 1 and got["scored"][0]["exp_id"] == "pass"
    assert got["verdicts"] == {"PASS": 1, "FAIL": 1, "INELIGIBLE(CULLED)": 1, "INELIGIBLE(HELD)": 1,
                               "INELIGIBLE(UNSCREENED)": 1}
    assert got["variant"] == "gate_in|HOLD" and got["mismatches"] == []


def test_compression_records_no_judge_and_mismatch_and_scores_neither(doc):
    qd = [_row("w1", "train8_held64", 195.0)]
    assert CA.compression_r4(qd, "B", (0, 100), doc, check=lambda *a, **k: {"verdict": "PASS"})["verdicts"] == {"NO_JUDGE": 1}
    wrong = lambda *a, **k: {"clause_a_r4": {"verdict": "PASS", "progress": 0.5}}
    got = CA.compression_r4(qd, "B", (0, 100), doc, check=wrong)
    assert got["value"] == 0 and got["verdicts"] == {"MISMATCH": 1} and got["mismatches"][0]["exp_id"] == "B-R4-1"
    none = CA.compression_r4(qd, "B", (0, 100), None, check=wrong)
    assert none["verdicts"] == {"INELIGIBLE(UNSCREENED)": 1} and none["variant"] is None


def test_pending_learner_alias_reads_pending(doc):
    for c in doc["cells"]:
        if (c["world"], c["pressure"]) == ("w7", "train128_held64"):
            c["verdicts"]["gate_in|HOLD"]["verdict"] = "PENDING_LEARNER"
    assert CA.screen_of(doc, "w7", "train128_held64")["status"] == "PENDING"


@pytest.mark.parametrize("world,pressure,median,nbytes", [
    ("w1", "train8_held64", 194.0, 32), ("w1", "train8_held64", 195.0, 32), ("w1", "train8_held64", 99.0, 32),
    ("w1", "train8_held64", 200.0, 64), ("w1", "train128_held64", 999.0, 1), ("w3", "train8_held64", 999.0, 1),
    ("w9", "train8_held64", 999.0, 1), ("w7", "train128_held64", 999.0, 1), ("w7", "train8_held64", 999.0, 1),
    ("w4", "train8_held64", 999.0, 1)])
def test_the_real_judge_agrees_with_the_screen_s4(doc, world, pressure, median, nbytes):
    """Independent check aimed at the claim: qd_ledger.check (G-R4-5, the only judge) and F12's s4 from the
    file's numbers give the same verdict and progress on every planted cell."""
    from primordial.ops import qd_ledger as Q
    mine = CA.s4_verdict(CA.screen_of(doc, world, pressure), median, nbytes, 8)
    judge = Q.check([], world, pressure, median, 0.0, nbytes, 8, doc=doc)["clause_a_r4"]
    assert CA._agrees(judge, mine), (judge, mine)


def test_load_worlds_roundtrip(tmp_path, doc):
    p = tmp_path / "worlds_r4.json"
    assert CA.load_worlds(p) is None
    p.write_text(json.dumps(doc), encoding="utf-8")
    assert CA.active_variant(CA.load_worlds(p)) == "gate_in|HOLD"
