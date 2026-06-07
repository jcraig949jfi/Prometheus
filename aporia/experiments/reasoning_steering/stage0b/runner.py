"""Stage 0b relational H-R1 runner (v0.3).

Reads the cached per-state margin vectors, builds the relational comparison flow, runs
the UNCHANGED Stage-0a Hodge decomposer + the adapted null battery, applies the
degeneracy guard, and emits stage0b_relational_hodge_report.json.

Verdict:
  BEATS_NULL : non_gradient_mass beats ALL sampling nulls at ALPHA (real non-scalar
               structure above the saturation floor).
  NULL       : does not beat some null (consistent with scalar difficulty).
  INVALID    : too few states (< MIN_STATES) or a degenerate/flat flow.
GLOBAL H-R1 ONLY -- no localization, no rung-rank, no steering.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0b.flow import relational_flow
from aporia.experiments.reasoning_steering.stage0b.relational_nulls import (
    vectors_from_records, run_relational_null, run_relational_family_holdout,
)
from aporia.experiments.reasoning_steering.stage0b.cache import load_cache, CACHE_PATH

__all__ = ["run_h_r1", "write_report", "REPORT_PATH", "MIN_STATES", "ALPHA"]

REPORT_PATH = Path(__file__).with_name("stage0b_relational_hodge_report.json")
MIN_STATES = 8
MIN_VARYING_CRITERIA = 3   # < 3 criteria that vary => no room for non-transitivity
ALPHA = 0.05


def _n_varying_criteria(records) -> int:
    """Count criteria (margin keys) with >= 2 distinct values across the states."""
    names = set().union(*[set(r["margins"]) for r in records]) if records else set()
    n = 0
    for k in names:
        vals = {round(r["margins"][k], 9) for r in records if k in r["margins"]}
        if len(vals) >= 2:
            n += 1
    return n
# NOTE: degree_preserving_rewire is INAPPLICABLE to the complete comparison graph
# (no non-edges to swap into), so it is excluded here; it would only apply to a k-NN
# graph variant. The valid relational sampling nulls:
SAMPLING_NULLS = ("falsifier_column_shuffle", "sign_permutation")


def run_h_r1(records, n_null: int = 500, seed: int = 0) -> dict:
    n = len(records)
    base = {"protocol": "reasoning_steering_v0.3_relational", "stage": "0b",
            "claim": "H-R1 global non-conservativity", "n_states": n,
            "n_null": n_null, "seed": seed, "alpha": ALPHA}

    if n < MIN_STATES:
        return {**base, "verdict": "INVALID", "reason": f"too_few_states (<{MIN_STATES})"}

    n_varying = _n_varying_criteria(records)
    if n_varying < MIN_VARYING_CRITERIA:
        return {**base, "verdict": "INVALID",
                "reason": f"too_few_varying_criteria ({n_varying}<{MIN_VARYING_CRITERIA})",
                "n_varying_criteria": n_varying}

    vectors = vectors_from_records(records)
    G, flow = relational_flow(vectors)
    vals = np.array(list(flow.values()), dtype=float)
    if vals.size == 0 or float(np.max(np.abs(vals))) < 1e-12:
        return {**base, "verdict": "INVALID", "reason": "degenerate_zero_flow"}

    d = hodge_decompose(G, flow)
    nulls = {k: run_relational_null(records, k, n_null, seed) for k in SAMPLING_NULLS}
    holdout = run_relational_family_holdout(records)
    beats_all = all(res.pvalue < ALPHA for res in nulls.values())

    return {
        **base,
        "n_varying_criteria": n_varying,
        "observed": {
            "non_gradient_mass": d.non_gradient_mass,
            "gradient_mass": d.gradient_mass,
            "curl_mass": d.curl_mass,
            "harmonic_mass": d.harmonic_mass,
        },
        "nulls": {k: {"pvalue": r.pvalue, "null_mean": r.null_mean, "null_std": r.null_std}
                  for k, r in nulls.items()},
        "falsifier_family_holdout": holdout,
        "verdict": "BEATS_NULL" if beats_all else "NULL",
    }


def write_report(report: dict, path=REPORT_PATH) -> Path:
    path = Path(path)
    path.write_text(json.dumps(report, indent=2, sort_keys=True))
    return path


if __name__ == "__main__":
    recs = load_cache(CACHE_PATH)
    rep = run_h_r1(recs, n_null=500, seed=0)
    write_report(rep)
    print(f"verdict={rep['verdict']}  n_states={rep['n_states']}")
    if "observed" in rep:
        print(f"  non_gradient_mass={rep['observed']['non_gradient_mass']:.4f}")
        for k, v in rep["nulls"].items():
            print(f"  {k}: p={v['pvalue']:.4f} null_mean={v['null_mean']:.4f}")
