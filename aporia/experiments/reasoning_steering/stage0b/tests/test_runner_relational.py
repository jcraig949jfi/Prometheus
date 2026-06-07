"""TDD tests for the Stage 0b relational runner (v0.3) -- synthetic caches, fast."""
import json

import pytest

from aporia.experiments.reasoning_steering.stage0b.runner import (
    run_h_r1, write_report, MIN_STATES, ALPHA,
)


def _ordered_cache(n):
    """n states with 3 varying criteria (distinct permutations) -- non-degenerate,
    passes the criteria-adequacy guard. Largely consistent orderings => NULL-leaning."""
    return [{"coeffs": [i], "mahler_measure": 1.05, "name": f"s{i}",
             "margins": {"f1": float((i * 7 + 3) % n),
                         "f2": float((i * 5 + 1) % n),
                         "f3": float((i * 3 + 2) % n)}}
            for i in range(n)]


# 1. AUTHORITY — verdict logic is consistent with the per-null p-values.
def test_authority_verdict_consistent_with_nulls():
    rep = run_h_r1(_ordered_cache(11), n_null=200, seed=1)   # n=11, gcd(7,11)=1
    assert rep["verdict"] in ("BEATS_NULL", "NULL")
    beats_all = all(v["pvalue"] < ALPHA for v in rep["nulls"].values())
    assert rep["verdict"] == ("BEATS_NULL" if beats_all else "NULL")


# 2. PROPERTY
def test_property_report_structure():
    rep = run_h_r1(_ordered_cache(9), n_null=120, seed=2)
    assert rep["protocol"].endswith("relational")
    assert rep["claim"].startswith("H-R1")
    assert set(("observed", "nulls", "falsifier_family_holdout", "verdict")) <= set(rep)
    for k in ("falsifier_column_shuffle", "sign_permutation"):
        assert 0.0 < rep["nulls"][k]["pvalue"] <= 1.0


# 3. EDGE CASES
def test_edge_cases():
    """Degeneracy guard: < MIN_STATES -> INVALID; flat flow -> INVALID."""
    rep_few = run_h_r1(_ordered_cache(MIN_STATES - 1), n_null=50, seed=0)
    assert rep_few["verdict"] == "INVALID" and "too_few_states" in rep_few["reason"]

    identical = [{"coeffs": [i], "mahler_measure": 1.05, "name": f"s{i}",
                  "margins": {"f1": 1.0, "f2": 1.0}} for i in range(10)]  # 0 varying criteria
    rep_id = run_h_r1(identical, n_null=50, seed=0)
    assert rep_id["verdict"] == "INVALID" and "too_few_varying_criteria" in rep_id["reason"]


# 4. COMPOSITION — report round-trips to JSON.
def test_composition_report_json_roundtrip(tmp_path):
    rep = run_h_r1(_ordered_cache(9), n_null=80, seed=3)
    p = write_report(rep, tmp_path / "r.json")
    loaded = json.loads(p.read_text())
    assert loaded["verdict"] == rep["verdict"]
    assert loaded["n_states"] == 9
