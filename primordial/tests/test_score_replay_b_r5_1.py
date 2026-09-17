"""H replay of B-R5-1: recomputes per-run values, pooled CI, progress and the judge; names every mismatching field."""
from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest

from primordial.metric.ci import median_ci
from primordial.score import replay_b_r5_1 as RP

GLEN = 4
FAMS = (4200, 2101, 3303, 5501)


def _factory(zero_w=False):
    """A planted family scorer: per-seed score = sum of the genome bytes (zero_w -> the abstain value 159)."""
    return lambda raw, seeds: 159.0 if zero_w else float(np.asarray(raw, np.int64).sum())


def _write(tmp_path, tamper=None):
    runs, held = [], {}
    for f in FAMS:
        for rs in range(8):
            g = bytes([f % 50, rs, 100, 30])                  # top1 by train fit
            other = bytes([1, 1, 1, 1])
            ep = tmp_path / f"e-{f}-{rs}.json"
            ep.write_text(json.dumps({"glen": GLEN, "elites": [[0, 50, g.hex(), "00"], [1, 10, other.hex(), "00"]]}),
                          encoding="utf-8")
            v = float(sum(g))
            held[f"{f}|{rs}"] = v
            runs.append({"kind": "run", "rng_family": f, "run_seed": rs, "elites": str(ep), "held64_per_seed": v,
                         "top_sha256": hashlib.sha256(g).hexdigest(), "train_fit": 50,
                         "control_obs_use": {"held64_w_zeroed": 159.0, "input_invariant_selected": 0}})
    vals = [held[f"{f}|{rs}"] for f in FAMS for rs in range(8)]
    med, (lo, hi) = float(np.median(vals)), median_ci(vals)
    floor, den = 100.0, 20.0
    cand = {"kind": "candidate", "runs_total": 32, "rng_family_count": 4, "runs_per_family": 8,
            "n_per_family": {str(f): 8 for f in FAMS}, "candidate_score": med, "candidate_ci95": [lo, hi],
            "floor": floor, "baseline": 120.0, "progress_above_floor": (med - floor) / den,
            "progress_ci95": [(lo - floor) / den, (hi - floor) / den], "held64_by_run": held, "bytes": GLEN,
            "oracle_clean": True, "verdict": "PASS", "judge": {"verdict": "PASS", "why": None, "progress": 1.5}}
    rows = runs[::-1] + [cand]                                 # written out of order: the replay sorts
    if tamper:
        tamper(rows)
    p = tmp_path / "b.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return p


ELIG = {"floor": 100.0, "progress_denominator": 20.0, "baseline": {"median": 120.0}, "floor_parts": {"abstain": 159.0}}


def _judge(expected):
    calls = []

    def judge(world, pressure, median, nbytes, runs, **kw):
        calls.append((median, kw))
        return expected
    return judge, calls


def _replay(p, judge_out=None):
    judge, calls = _judge(judge_out or {"verdict": "PASS", "why": None, "progress": 1.5})
    out = RP.replay(p, family=(_factory, GLEN), eligibility=ELIG, doc={}, judge=judge, invariant=lambda raw: 0)
    return out, calls


def test_agree_when_every_number_recomputes(tmp_path):
    out, calls = _replay(_write(tmp_path))
    assert out["outcome"] == "AGREE" and out["mismatches"] == []
    kw = calls[0][1]
    assert (kw["runs_total"], kw["rng_family_count"], kw["runs_per_family"]) == (32, 4, 8)
    assert kw["readout"] == "top1_train" and kw["n_per_family"] == {str(f): 8 for f in FAMS}
    assert [x["run_id"] for x in out["runs"]][:9] == [f"4200|{i}" for i in range(8)] + ["2101|0"]   # s9 order


@pytest.mark.parametrize("tamper,field", [
    (lambda rows: rows[0].update(held64_per_seed=rows[0]["held64_per_seed"] + 0.5), "held64_per_seed"),
    (lambda rows: rows[3].update(top_sha256="0" * 64), "top_sha256"),
    (lambda rows: rows[5]["control_obs_use"].update(held64_w_zeroed=150.0), "control_obs_use.held64_w_zeroed"),
    (lambda rows: rows[-1].update(candidate_ci95=[0.0, 1.0]), "candidate_ci95"),
    (lambda rows: rows[-1].update(progress_above_floor=9.9), "progress_above_floor"),
    (lambda rows: rows[-1].update(runs_per_family=4), "runs_per_family"),
])
def test_disagree_names_the_field(tmp_path, tamper, field):
    out, _ = _replay(_write(tmp_path, tamper))
    assert out["outcome"] == "DISAGREE" and field in [m["field"] for m in out["mismatches"]]


def test_a_judge_that_disagrees_is_reported(tmp_path):
    out, _ = _replay(_write(tmp_path), {"verdict": "INELIGIBLE", "why": "CANDIDATE_N", "progress": None})
    assert out["outcome"] == "DISAGREE" and {"judge.verdict", "judge.why", "verdict"} <= {m["field"] for m in out["mismatches"]}


def test_obs_use_control_must_drop_to_abstain_and_not_be_input_invariant(tmp_path):
    p = _write(tmp_path)
    judge, _ = _judge({"verdict": "PASS", "why": None, "progress": 1.5})
    out = RP.replay(p, family=(lambda zero_w=False: (lambda raw, s: 150.0) if zero_w else _factory(False), GLEN),
                    eligibility=ELIG, doc={}, judge=judge, invariant=lambda raw: 1)
    fields = {m["field"] for m in out["mismatches"]}
    assert {"obs_use.w_zeroed_equals_abstain", "obs_use.input_invariant_selected"} <= fields
