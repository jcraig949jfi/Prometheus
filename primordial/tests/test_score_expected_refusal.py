"""H-R5-4: EXPECTED_REFUSAL_OBSERVED is a campaign label over the real judge's refusal; the judge is untouched."""
from __future__ import annotations

import copy
import json

import pytest

from primordial.score import expected_refusal as ER

PILOT = {"campaign_stage": "PILOT"}
SHORT = {"runs_total": 16, "rng_family_count": 2, "runs_per_family": 8}
FULL = {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8,
        "n_per_family": {"4200": 8, "2101": 8, "3303": 8, "5501": 8}}


@pytest.mark.parametrize("env,sample,judge,label", [
    (PILOT, SHORT, {"verdict": "INELIGIBLE", "why": "CANDIDATE_N"}, "EXPECTED_REFUSAL_OBSERVED"),
    ({"campaign_stage": "SMOKE"}, SHORT, {"clause_a_r4": {"verdict": "INELIGIBLE", "why": "BASELINE_N"}},
     "EXPECTED_REFUSAL_OBSERVED"),
    ({"campaign_stage": "REPLICATION"}, {**FULL, "n_per_family": {"4200": 29, "2101": 1, "3303": 1, "5501": 1}},
     {"verdict": "INELIGIBLE", "why": "CANDIDATE_N"}, "EXPECTED_REFUSAL_OBSERVED"),
    (PILOT, SHORT, {"verdict": "INELIGIBLE", "why": "READOUT_MISMATCH"}, "UNEXPECTED_REFUSAL_REASON"),
    (PILOT, SHORT, {"verdict": "PASS", "progress": 0.97}, "EXPECTED_REFUSAL_MISSING"),
    (PILOT, SHORT, {"verdict": "FAIL"}, "EXPECTED_REFUSAL_MISSING"),
    ({"campaign_stage": "PRODUCTION"}, SHORT, {"verdict": "INELIGIBLE", "why": "CANDIDATE_N"}, "NOT_APPLICABLE"),
    (PILOT, FULL, {"verdict": "PASS"}, "NOT_APPLICABLE"),
    (None, SHORT, {"verdict": "INELIGIBLE", "why": "CANDIDATE_N"}, "NOT_APPLICABLE"),
])
def test_labels(env, sample, judge, label):
    before = copy.deepcopy(judge)
    out = ER.classify(env, sample, judge)
    assert out["label"] == label and out["scientific_verdict"] is False
    assert judge == before                                                   # the judge's result is not touched


def test_short_fields_use_the_judge_minimum():
    from primordial.ops import qd_ledger as Q
    assert ER._minimum() == (Q.BASELINE_MIN_RUNS, Q.BASELINE_MIN_FAMILIES, Q.BASELINE_MIN_PER_FAMILY)
    assert ER.undersampled(SHORT) == ["runs_total", "rng_family_count"]
    assert ER.undersampled({}) == ["runs_total", "rng_family_count", "runs_per_family"]
    assert ER.undersampled(FULL) == []


def _doc():
    vs = {v: {"verdict": "SURVIVED", "cull_reason": None, "floor": 100.0}
          for v in ("four_policy|CULL", "four_policy|HOLD", "gate_in|CULL", "gate_in|HOLD")}
    return {"schema": "worlds_r4/v1", "q1_floor_policy": "gate_in", "q2_policy": "HOLD", "cells": [
        {"world": "w1", "pressure": "train8_held64", "floor": 100.0, "gate_held64": 100.0,
         "baseline": {"median": 200.0, "ci95": [180.0, 220.0], "bytes": 64, "n_runs": 8}, "verdicts": vs}]}


def test_the_real_judge_is_identical_across_stages_and_its_refusal_is_labelled():
    """Gate items 3/4: campaign_stage never reaches the judge; an 8-run baseline gets the real BASELINE_N."""
    from primordial.ops import qd_ledger as Q
    results = {}
    for stage in ("SMOKE", "PILOT", "PRODUCTION", "REPLICATION"):
        res = Q.check([], "w1", "train8_held64", 195.0, 0.0, 32, 8, doc=_doc())
        results[stage] = json.dumps(res, sort_keys=True, default=str)
        label = ER.classify({"campaign_stage": stage}, {"runs_total": 8, "rng_family_count": 1, "runs_per_family": 8},
                            res)["label"]
        assert label == ("NOT_APPLICABLE" if stage == "PRODUCTION" else "EXPECTED_REFUSAL_OBSERVED")
        assert res["clause_a_r4"]["why"] == "BASELINE_N"
    assert len(set(results.values())) == 1


def test_emit_writes_real_labels_only():
    class R:
        def __init__(self):
            self.x = []

        def xadd(self, key, fields):
            self.x.append((key, fields))
            return "1-0"
    r = R()
    obs = ER.classify(PILOT, SHORT, {"verdict": "INELIGIBLE", "why": "CANDIDATE_N"})
    assert ER.emit(obs, "B", "B-R5-pilot", r=r) == "1-0"
    key, fields = r.x[0]
    assert key == "pm:events" and fields["event"] == "EXPECTED_REFUSAL_OBSERVED"
    assert json.loads(fields["json"])["exp_id"] == "B-R5-pilot"
    assert ER.emit(ER.classify(PILOT, FULL, {"verdict": "PASS"}), "B", "x", r=r) is None and len(r.x) == 1
