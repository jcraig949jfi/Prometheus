"""Stage 0a runner — prove the instrument before any real failure data.

Assembles the decomposer + 4 synthetic controls + the §4 null battery + H-R2
localization into one validation harness and emits stage0_hodge_controls_report.json
with pass/fail per control. This is protocol v0.2 §5 step 0a: the gate that must
pass before Stage 0b/0c run on real data.

Run as a script to (re)generate the canonical report artifact:
    py -3.11 -m aporia.experiments.reasoning_steering.stage0.runner
"""
from __future__ import annotations

import json
from pathlib import Path

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0.controls import (
    no_cycle_graph,
    planted_cycle_graph,
    planted_hole_graph,
    operator_artifact_graph,
)
from aporia.experiments.reasoning_steering.stage0.nulls import run_null
from aporia.experiments.reasoning_steering.stage0.localization import localized_rank

__all__ = ["run_controls_0a", "write_report", "CANONICAL_REPORT_PATH"]

CANONICAL_REPORT_PATH = Path(__file__).with_name("stage0_hodge_controls_report.json")

_FLOOR_P = 0.1   # >  => "does not beat its null" (a floor); <  => beats the null


def _check(name, criterion, observed, passed):
    return {"name": name, "criterion": criterion, "observed": observed, "passed": bool(passed)}


def run_controls_0a(seed: int = 0, n_null_samples: int = 200) -> dict:
    """Validate the instrument against controls #5->#8 and return a report dict."""
    if n_null_samples < 1:
        raise ValueError("n_null_samples must be >= 1")
    checks = []

    # #5 no-cycle: the instrument must see nothing.
    cg5 = no_cycle_graph(12, seed=seed)
    d5 = hodge_decompose(cg5.G, cg5.flow)
    checks.append(_check(
        "control_5_no_cycle", "non_gradient_mass ~ 0 on a tree",
        {"non_gradient_mass": d5.non_gradient_mass},
        d5.non_gradient_mass < 1e-9,
    ))

    # #6 planted-cycle: recover curl.
    k6 = 4
    cg6 = planted_cycle_graph(k6, seed=seed)
    d6 = hodge_decompose(cg6.G, cg6.flow)
    checks.append(_check(
        "control_6_planted_cycle", "curl_rank == #triangles, harmonic_rank == 0, curl_mass > 0",
        {"n_planted": k6, "curl_rank": d6.curl_rank, "harmonic_rank": d6.harmonic_rank,
         "curl_mass": d6.curl_mass},
        d6.curl_rank == k6 and d6.harmonic_rank == 0 and d6.curl_mass > 0.0,
    ))

    # #7 planted-hole: recover harmonic.
    k7 = 3
    cg7 = planted_hole_graph(k7, hole_len=4, seed=seed)
    d7 = hodge_decompose(cg7.G, cg7.flow)
    checks.append(_check(
        "control_7_planted_hole", "harmonic_rank == #holes, curl_rank == 0, harmonic_mass > 0",
        {"n_planted": k7, "harmonic_rank": d7.harmonic_rank, "curl_rank": d7.curl_rank,
         "harmonic_mass": d7.harmonic_mass},
        d7.harmonic_rank == k7 and d7.curl_rank == 0 and d7.harmonic_mass > 0.0,
    ))

    # #8 operator-artifact: must NOT beat its own null (the floor) -- both nulls.
    cg8 = operator_artifact_graph({"A": 5, "B": 4, "C": 4, "D": 3}, n_nodes=10, seed=seed)
    res8_lbl = run_null(cg8, n_samples=n_null_samples, seed=seed, kind="operator_label_shuffle")
    res8_ep = run_null(cg8, n_samples=n_null_samples, seed=seed, kind="endpoint_permutation")
    checks.append(_check(
        "control_8_operator_artifact_floor",
        "operator-artifact does NOT beat its label-shuffle/endpoint-permutation null (p > floor)",
        {"label_shuffle_p": res8_lbl.pvalue, "endpoint_permutation_p": res8_ep.pvalue,
         "floor_p": _FLOOR_P},
        res8_lbl.pvalue > _FLOOR_P and res8_ep.pvalue > _FLOOR_P,
    ))

    # sensitivity: real planted structure BEATS the degree-preserving-rewire null.
    res_central = run_null(cg6, n_samples=n_null_samples, seed=seed, kind="degree_preserving_rewire")
    checks.append(_check(
        "planted_cycle_beats_rewire_null",
        "planted-cycle non_gradient_mass beats degree-preserving-rewire null (p < floor)",
        {"observed": res_central.observed, "null_mean": res_central.null_mean,
         "pvalue": res_central.pvalue, "floor_p": _FLOOR_P},
        res_central.observed > res_central.null_mean and res_central.pvalue < _FLOOR_P,
    ))

    # H-R2 localization: STABLE on a planted triangle well.
    cg_loc = planted_cycle_graph(1, seed=seed)
    lr = localized_rank(cg_loc.G, cg_loc.flow, well=0)
    checks.append(_check(
        "localization_stable_on_planted_well",
        "localized_rank STABLE with curl_rank 1 on a planted triangle well",
        {"status": lr.status, "curl_rank": lr.curl_rank, "harmonic_rank": lr.harmonic_rank},
        lr.status == "STABLE" and lr.curl_rank == 1,
    ))

    return {
        "protocol": "reasoning_steering_v0.2",
        "stage": "0a",
        "seed": seed,
        "n_null_samples": n_null_samples,
        "checks": checks,
        "all_passed": all(c["passed"] for c in checks),
    }


def write_report(report: dict, path) -> Path:
    path = Path(path)
    path.write_text(json.dumps(report, indent=2, sort_keys=True))
    return path


if __name__ == "__main__":
    rep = run_controls_0a(seed=0, n_null_samples=500)
    write_report(rep, CANONICAL_REPORT_PATH)
    print(f"all_passed={rep['all_passed']}  ->  {CANONICAL_REPORT_PATH}")
    for c in rep["checks"]:
        print(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['name']}")
