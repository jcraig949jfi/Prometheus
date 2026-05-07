"""Substrate-Tester Fire #19 harness — Lane 4 (T-ST003 third regression)
+ Lane 1 (CLAIM-flood with MULTI-coefficient-flip Mossinghoff perturbation).

Coordination: parallel fire #18 ran (commit 1e1af5d7) covering lanes 7 +
9. P0 ticket T-ST-fire17-001 still OPEN — Techne hasn't fixed yet.

Lane 4: third post-restart regression on T-ST003 fix (silent sentinel
-> KeyError). Fires #3 (pre-window) + #10 (parallel) + #19 (this).
Confirms fix is durable across multiple restarts and contract-change
window.

Lane 1: closes the long-standing probe-design iteration from fires #1,
#9, #14. The single-coef-flip Mossinghoff perturbation in fire #14
yielded 0 in-band perturbations from 200 attempts. Hypothesis: multi-
coef-flip (2-3 coefs at once) explores a wider perturbation neighborhood
and may yield in-band hits.

Outputs:
  charon/diagnostics/substrate_tester_fire_19_results.json
"""
from __future__ import annotations

import json
import random
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 4 — T-ST003 third regression
# ---------------------------------------------------------------------------


def lane_4_st003_third_regression() -> Dict[str, Any]:
    from prometheus_math.learner_corpus import (
        get_raw_invariant_keys,
        RAW_INVARIANTS_PER_DOMAIN,
    )

    tests: List[Dict[str, Any]] = []

    # T1: unknown domain MUST raise
    try:
        keys = get_raw_invariant_keys("nonexistent_xyz_fire19")
        tests.append({
            "id": "T1_unknown_domain_raises",
            "expected": "KeyError raised (T-ST003 fix)",
            "actual": f"silently returned {keys} — REGRESSION",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except KeyError as exc:
        tests.append({
            "id": "T1_unknown_domain_raises",
            "expected": "KeyError raised",
            "actual": f"KeyError: {str(exc)[:140]}",
            "verdict": "PASS",
            "note": "T-ST003 fix sticks across third regression check (fires #3, #10, #19)",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T1_unknown_domain_raises",
            "expected": "KeyError raised",
            "actual": f"raised wrong exception: {type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P2-normal",
        })

    # T2: registered domain still works (no over-blocking)
    for domain in ("lehmer", "bsd_rank"):
        try:
            keys = get_raw_invariant_keys(domain)
            if isinstance(keys, tuple) and len(keys) > 0:
                tests.append({
                    "id": f"T2_{domain}_registered",
                    "expected": f"{domain} returns registered key tuple",
                    "actual": f"{len(keys)} keys; sample {keys[:3]}",
                    "verdict": "PASS",
                })
            else:
                tests.append({
                    "id": f"T2_{domain}_registered",
                    "expected": f"{domain} returns valid keys",
                    "actual": f"suspicious: {keys}",
                    "verdict": "FAIL",
                    "severity": "P0-blocker",
                })
        except Exception as exc:  # noqa: BLE001
            tests.append({
                "id": f"T2_{domain}_registered",
                "expected": f"{domain} returns valid keys",
                "actual": f"raised: {type(exc).__name__}: {exc}",
                "verdict": "FAIL",
                "severity": "P0-blocker",
                "note": "T-ST003 fix over-blocks legitimate domain values",
            })

    # T3: the registry itself has expected disjoint structure
    try:
        bsd_keys = set(get_raw_invariant_keys("bsd_rank"))
        lehmer_keys = set(get_raw_invariant_keys("lehmer"))
        overlap = bsd_keys & lehmer_keys
        tests.append({
            "id": "T3_domain_keys_disjoint",
            "expected": "bsd_rank and lehmer raw_invariants are disjoint",
            "actual": (
                f"overlap={overlap if overlap else 'none'}; "
                f"|bsd|={len(bsd_keys)}, |lehmer|={len(lehmer_keys)}"
            ),
            "verdict": "PASS" if not overlap else "FAIL",
            "severity": "P2-normal" if overlap else None,
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T3_domain_keys_disjoint",
            "expected": "registries accessible",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    return {
        "lane": "4_st003_third_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 1 — multi-coef-flip Mossinghoff perturbation
# ---------------------------------------------------------------------------


def fast_mahler_numpy(coeffs_ascending: List[int]) -> float:
    import numpy as np
    if len(coeffs_ascending) < 2:
        return float("nan")
    roots = np.roots(list(reversed(coeffs_ascending)))
    leading = abs(coeffs_ascending[-1])
    if leading == 0:
        return float("nan")
    prod = float(leading)
    for r in roots:
        m = abs(r)
        if m > 1.0:
            prod *= m
    return prod


def lane_1_multi_coef_flip(seed: int) -> Dict[str, Any]:
    from prometheus_math.lehmer_brute_force_path_c import load_mossinghoff_catalog

    rng = random.Random(seed)
    catalog = load_mossinghoff_catalog()

    # Filter to in-band entries. Catalog schema uses `mahler_measure` and `coeffs`.
    def _entry_M(e: dict) -> float:
        try:
            return float(e.get("mahler_measure", 0.0))
        except (TypeError, ValueError):
            return 0.0

    def _entry_coeffs(e: dict) -> list:
        return list(e.get("coeffs", []) or e.get("coeffs_ascending", []))

    in_band_entries = [e for e in catalog if 1.001 <= _entry_M(e) <= 1.18]

    # Take up to 5 small-degree in-band entries as perturbation seeds
    sorted_in_band = sorted(in_band_entries, key=lambda e: len(_entry_coeffs(e)))[:5]

    # Multi-coef-flip: flip 2 OR 3 coefficients by ±1 each, attempt 100 perturbations per seed
    n_attempts_per_seed = 100
    perturbations_in_band: List[Tuple[List[int], float, str]] = []
    perturbations_total = 0
    for seed_entry in sorted_in_band:
        coeffs_orig = _entry_coeffs(seed_entry)
        if len(coeffs_orig) < 4:
            continue
        for _ in range(n_attempts_per_seed):
            perturbations_total += 1
            n_flips = rng.choice([2, 3])  # multi-coef
            perturbed = list(coeffs_orig)
            indices = rng.sample(range(len(perturbed)), min(n_flips, len(perturbed)))
            for i in indices:
                perturbed[i] = perturbed[i] + rng.choice([-1, 1])
            try:
                m = fast_mahler_numpy(perturbed)
            except Exception:
                continue
            if m != m or m == float("inf"):
                continue
            if 1.001 <= m <= 1.18:
                perturbations_in_band.append(
                    (perturbed, m, str(_entry_M(seed_entry)))
                )

    return {
        "lane": "1_multi_coef_flip_mossinghoff",
        "n_in_band_seeds_loaded": len(in_band_entries),
        "n_seeds_used_for_perturbation": len(sorted_in_band),
        "n_attempts_total": perturbations_total,
        "n_perturbations_in_band": len(perturbations_in_band),
        "in_band_yield_rate": (
            len(perturbations_in_band) / perturbations_total
            if perturbations_total else 0.0
        ),
        "sample_in_band_perturbations": [
            {"coeffs": p[0], "M": p[1], "seed_M": p[2]}
            for p in perturbations_in_band[:5]
        ],
        "fire_14_yield_for_comparison": "0 / 200 (single-coef-flip)",
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    SEED = 20260507_19
    summary = {
        "fire": 19,
        "lanes": [4, 1],
        "lane_4": lane_4_st003_third_regression(),
        "lane_1": lane_1_multi_coef_flip(SEED),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_19_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 4: {summary['lane_4']['verdict_counts']}")
    l1 = summary["lane_1"]
    print(f"Lane 1: {l1['n_perturbations_in_band']}/{l1['n_attempts_total']} in-band "
          f"(yield {l1['in_band_yield_rate']:.4f}; fire-14 was 0/200)")
    return summary


if __name__ == "__main__":
    run()
