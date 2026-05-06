"""
Substrate-Tester Fire #1 — Lane 1 (CLAIM-flood) + Lane 7 (precision-gradient)

Generates 100 random palindromic polynomial CLAIMs (lane 1) and runs a
single borderline INCONCLUSIVE entry through 5 precision levels (lane 7).
Reports throughput, verdict distribution, per-falsifier kill counts, and
precision-gradient stability metrics.

Author: substrate-tester (Charon-aligned), 2026-05-06
"""

from __future__ import annotations

import json
import random
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")

# ---------------------------------------------------------------------------
# Lane 1 — CLAIM-flood
# ---------------------------------------------------------------------------


def random_palindromic_coeffs(half_len: int, coef_range: tuple[int, int], rng: random.Random) -> list[int]:
    """Build palindromic polynomial of degree 2*half_len from random half-coeffs."""
    half = [rng.randint(coef_range[0], coef_range[1]) for _ in range(half_len)]
    return half + half[::-1][1:]  # length 2*half_len - 1


def palindrome_from_half(half: list[int]) -> list[int]:
    """Standard palindrome: [a0, a1, ..., a_{n-1}, a_n, a_{n-1}, ..., a_1, a_0]."""
    return half + list(reversed(half[:-1]))


def fast_mahler_numpy(coeffs_ascending: list[int]) -> float:
    """Quick Mahler measure via numpy roots — for upfront band-routing only."""
    import numpy as np
    if len(coeffs_ascending) < 2:
        return float("nan")
    # numpy.roots expects descending
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


def lane_1_claim_flood(n_probes: int = 100, seed: int = 20260506) -> dict:
    """Lane 1: CLAIM-flood. Submits n_probes random palindromic polys."""
    from prometheus_math.discovery_pipeline import DiscoveryPipeline
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval_v2 import BindEvalExtension

    rng = random.Random(seed)

    # Build claim mix:
    # - 70 truly random palindromes (most M will be way out-of-band)
    # - 25 near-band targeted (constructed to perturb cyclotomic structure)
    # - 5 known structural cases (Lehmer-like, cyclotomic, identity)
    probes: list[list[int]] = []

    # 70 random degree-10 palindromes, half = 6 coeffs each
    for _ in range(70):
        half = [rng.randint(-5, 5) for _ in range(6)]
        if half[0] == 0:
            half[0] = 1  # ensure non-zero leading
        probes.append(palindrome_from_half(half))

    # 25 near-band targeted: known difficult half-shapes from the deg-14 ±5
    # brute-force INCONCLUSIVE list (real borderline). We re-use 5 patterns
    # × 5 small perturbations.
    seed_halves = [
        [1, -4, 5, 0, -5, 4, -1, 0],
        [1, -3, 1, 5, -5, -1, 3, -2],
        [1, -3, 2, 1, 0, -2, 1, 0],
        [1, 1, -1, 0, 0, 1, -1, -1],
        [1, 0, 1, -1, 1, -1, 0, 1],
    ]
    for h in seed_halves:
        for _ in range(5):
            perturbed = list(h)
            i = rng.randint(0, len(h) - 1)
            perturbed[i] = perturbed[i] + rng.choice([-1, 1])
            probes.append(palindrome_from_half(perturbed))

    # 5 structural: Lehmer's polynomial (deg 10), cyclotomic Phi_5, etc.
    # Lehmer's polynomial: x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1
    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    probes.append(lehmer)
    # Phi_3 = x^2 + x + 1 (degree 2 palindromic, M=1)
    probes.append([1, 1, 1])
    # Phi_5 = x^4 + x^3 + x^2 + x + 1
    probes.append([1, 1, 1, 1, 1])
    # x^4 - 1 (not palindrome strictly but close)
    probes.append([1, 0, 0, 0, -1])
    # Trivial palindromic dummy
    probes.append([1, 0, 0, 0, 1])

    # Assemble pipeline
    kernel = SigmaKernel()
    ext = BindEvalExtension(kernel)
    pipe = DiscoveryPipeline(kernel=kernel, ext=ext)

    # Run flood
    t0 = time.time()
    records = []
    errors = []
    for idx, coeffs in enumerate(probes):
        try:
            m = fast_mahler_numpy(coeffs)
            if m != m or m == float("inf"):  # nan/inf check
                m = 0.5  # force out-of-band routing
            rec = pipe.process_candidate(coeffs, m)
            records.append({
                "idx": idx,
                "coeffs": coeffs,
                "M": m,
                "terminal_state": rec.terminal_state,
                "kill_pattern": rec.kill_pattern,
            })
        except Exception as exc:
            errors.append({"idx": idx, "coeffs": coeffs, "error": repr(exc)})
    elapsed = time.time() - t0
    throughput = len(records) / elapsed if elapsed > 0 else 0.0

    # Tabulate
    state_counts = Counter(r["terminal_state"] for r in records)
    kill_pattern_counts = Counter(
        r["kill_pattern"].split(":")[0] if r["kill_pattern"] else "no-kill-pattern"
        for r in records
    )

    return {
        "lane": "1_claim_flood",
        "n_probes": len(probes),
        "n_completed": len(records),
        "n_errors": len(errors),
        "wall_clock_seconds": elapsed,
        "throughput_per_second": throughput,
        "terminal_state_counts": dict(state_counts),
        "kill_pattern_root_counts": dict(kill_pattern_counts),
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Lane 7 — precision-gradient
# ---------------------------------------------------------------------------


def lane_7_precision_gradient() -> dict:
    """Lane 7: precision-gradient. Pick one borderline INCONCLUSIVE entry,
    run high_precision_M_via_factor at 5 dps levels.
    """
    from prometheus_math.lehmer_path_a import high_precision_M_via_factor

    # Real INCONCLUSIVE entry from deg-14 ±5 brute-force (1st of 17):
    # half = [1, -4, 5, 0, -5, 4, -1, 0]
    coeffs_ascending = [1, -4, 5, 0, -5, 4, -1, 0, -1, 4, -5, 0, 5, -4, 1]

    dps_ladder = [10, 30, 60, 100, 200]
    results = []
    for dps in dps_ladder:
        t0 = time.time()
        try:
            out = high_precision_M_via_factor(
                coeffs_ascending=coeffs_ascending,
                nroots_precision=dps,
            )
            elapsed = time.time() - t0
            results.append({
                "dps": dps,
                "elapsed_s": elapsed,
                "M": float(out.get("M")) if out.get("M") == out.get("M") else None,
                "status": out.get("status"),
                "error": out.get("error"),
                "precision_digits_recorded": out.get("precision_digits"),
                "n_factors": len(out.get("factors", [])),
            })
        except Exception as exc:
            results.append({"dps": dps, "exception": repr(exc)})

    # Stability analysis
    valid_M = [r["M"] for r in results if r.get("M") is not None]
    M_max = max(valid_M) if valid_M else None
    M_min = min(valid_M) if valid_M else None
    spread = (M_max - M_min) if (M_max is not None and M_min is not None) else None

    # Critical-bug checks per lane spec:
    # - dps=200 should produce a single stable verdict (M)
    # - dps=10 may differ but should not silently agree with dps=200
    # - All should report precision_dps in the verdict record
    # - PROMOTE at dps=10 followed by KILL at dps=200 = critical bug
    bugs = []
    dps_recorded = [r.get("precision_digits_recorded") for r in results]
    if any(p is None for p in dps_recorded):
        bugs.append({
            "type": "dps_not_recorded",
            "severity": "P1-high",
            "description": f"precision_digits not recorded in {sum(1 for p in dps_recorded if p is None)} of {len(results)} runs",
            "results_with_missing_dps": [r for r in results if r.get("precision_digits_recorded") is None],
        })

    # Check for verdict oscillation: if some dps say PROMOTE-shape (M < 1.18 in band)
    # and others say KILL-shape (M out of band or NaN)
    band_status = []
    for r in results:
        m = r.get("M")
        if m is None:
            band_status.append("computation_failed")
        elif m == m and 1.001 < m < 1.18:
            band_status.append("in_band")
        elif m == m:
            band_status.append("out_of_band")
        else:
            band_status.append("nan")
    band_set = set(band_status)
    if "in_band" in band_set and ("out_of_band" in band_set or "nan" in band_set):
        bugs.append({
            "type": "verdict_oscillation_across_precision",
            "severity": "P0-blocker",
            "description": "in-band classification changes across precision levels without precision-aware caveat",
            "band_status_per_dps": dict(zip(dps_ladder, band_status)),
        })

    return {
        "lane": "7_precision_gradient",
        "candidate_coeffs_ascending": coeffs_ascending,
        "candidate_label": "INCONCLUSIVE deg-14 ±5 entry #1 (M_numpy ≈ 1.00314)",
        "results_per_dps": results,
        "M_max_valid": M_max,
        "M_min_valid": M_min,
        "M_spread": spread,
        "band_status_per_dps": dict(zip(dps_ladder, band_status)),
        "bugs_detected": bugs,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #1 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 1: CLAIM-flood ---")
    lane1 = lane_1_claim_flood(n_probes=100, seed=20260506)
    print(json.dumps(
        {k: v for k, v in lane1.items() if k != "errors"},
        indent=2, default=str
    ))

    print("\n--- Lane 7: precision-gradient ---")
    lane7 = lane_7_precision_gradient()
    print(json.dumps(
        {k: v for k, v in lane7.items() if k not in ("results_per_dps",)},
        indent=2, default=str
    ))
    for r in lane7["results_per_dps"]:
        print(f"  dps={r.get('dps')}: elapsed={r.get('elapsed_s'):.3f}s M={r.get('M')} status={r.get('status')} dps_rec={r.get('precision_digits_recorded')}" if r.get('elapsed_s') is not None else f"  dps={r.get('dps')}: EXC")

    summary = {
        "fire_id": "fire_1_2026_05_06",
        "lanes": ["1_claim_flood", "7_precision_gradient"],
        "lane_1": lane1,
        "lane_7": lane7,
    }
    out_path = out_dir / "substrate_tester_fire_1_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
