"""Substrate-Tester Fire #9 harness — Lane 1 (CLAIM-flood, stratified
in-band sampler) + Lane 7 (precision-gradient, different borderline).

Per fire #8 standing recommendation: re-baseline Lane 1 with a stratified
in-band sampler so F1/F6/F9/F11 actually fire (instead of fire #1's 99%
out-of-band). Pick a different borderline coefficient set than fire #1
used (which was [1,-4,5,0,-5,4,-1,0]) so Lane 7 covers fresh ground.

Outputs:
  charon/diagnostics/substrate_tester_fire_9_results.json
"""
from __future__ import annotations

import json
import random
import time
from collections import Counter
from pathlib import Path
from typing import List, Tuple


def fast_mahler_numpy(coeffs_ascending: List[int]) -> float:
    """Quick Mahler measure via numpy roots — for upfront band-routing only."""
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


def palindrome_from_half(half: List[int]) -> List[int]:
    return list(half) + list(reversed(half[:-1]))


# ---------------------------------------------------------------------------
# Lane 1 — CLAIM-flood with stratified in-band sampler
# ---------------------------------------------------------------------------


def stratified_in_band_sampler(
    n_target: int, half_len: int, coef_range: Tuple[int, int],
    rng: random.Random, max_attempts: int = 50000,
) -> List[Tuple[List[int], float]]:
    """Rejection-sampling on M in (1.001, 1.18). Returns list of (coeffs, M)
    pairs that fall in the Salem band."""
    out: List[Tuple[List[int], float]] = []
    attempts = 0
    while len(out) < n_target and attempts < max_attempts:
        attempts += 1
        half = [rng.randint(coef_range[0], coef_range[1]) for _ in range(half_len)]
        if half[0] == 0:
            half[0] = rng.choice([-1, 1])
        coeffs = palindrome_from_half(half)
        try:
            m = fast_mahler_numpy(coeffs)
        except Exception:
            continue
        if m != m or m == float("inf"):  # nan/inf
            continue
        if 1.001 <= m <= 1.18:
            out.append((coeffs, m))
    return out


def lane_1_stratified_claim_flood(seed: int) -> dict:
    """Lane 1: CLAIM-flood with stratified in-band sampling.

    Goal: 100 probes total — 70 in-band (rejection-sampled) + 25 out-of-band
    + 5 structural anchors. This time F1/F6/F9/F11 should actually fire on
    a meaningful fraction of probes."""
    from prometheus_math.discovery_pipeline import DiscoveryPipeline
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval_v2 import BindEvalExtension

    rng = random.Random(seed)

    probes: List[Tuple[List[int], float]] = []

    # 70 in-band rejection-sampled; deg 10 (half_len=6) and deg 14 (half_len=8) mix
    in_band_deg10 = stratified_in_band_sampler(35, 6, (-5, 5), rng)
    in_band_deg14 = stratified_in_band_sampler(35, 8, (-5, 5), rng)
    probes.extend(in_band_deg10)
    probes.extend(in_band_deg14)

    # 25 out-of-band controls (random palindromes; expect mostly out-of-band)
    for _ in range(25):
        half = [rng.randint(-5, 5) for _ in range(6)]
        if half[0] == 0:
            half[0] = 1
        coeffs = palindrome_from_half(half)
        try:
            m = fast_mahler_numpy(coeffs)
            if m != m or m == float("inf"):
                m = 0.5
        except Exception:
            m = 0.5
        probes.append((coeffs, m))

    # 5 structural anchors with known M
    structural = [
        ([1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1], 1.176280818259917),  # Lehmer's polynomial
        ([1, 1, 1], 1.0),                                              # Phi_3
        ([1, 1, 1, 1, 1], 1.0),                                        # Phi_5
        ([1, 0, 0, 0, -1], 1.0),                                       # x^4 - 1
        ([1, 0, 0, 0, 1], 1.0),                                        # x^4 + 1
    ]
    probes.extend(structural)

    # Assemble pipeline
    kernel = SigmaKernel()
    ext = BindEvalExtension(kernel)
    pipe = DiscoveryPipeline(kernel=kernel, ext=ext)

    # Run flood
    t0 = time.time()
    records = []
    errors = []
    for idx, (coeffs, m) in enumerate(probes):
        try:
            rec = pipe.process_candidate(coeffs, m)
            records.append({
                "idx": idx,
                "coeffs": coeffs,
                "M": m,
                "terminal_state": rec.terminal_state,
                "kill_pattern": rec.kill_pattern,
            })
        except Exception as exc:
            errors.append({"idx": idx, "coeffs": coeffs, "error": repr(exc)[:200]})
    elapsed = time.time() - t0
    throughput = len(records) / elapsed if elapsed > 0 else 0.0

    state_counts = Counter(r["terminal_state"] for r in records)
    kill_pattern_root_counts = Counter(
        r["kill_pattern"].split(":")[0] if r["kill_pattern"] else "no-kill-pattern"
        for r in records
    )
    # Stratified breakdown: in-band vs out-of-band routing, by sampler stratum
    n_in_band_sampled = len(in_band_deg10) + len(in_band_deg14)
    n_in_band_routed = sum(
        1 for r in records[:n_in_band_sampled]
        if r["kill_pattern"] is None or not r["kill_pattern"].startswith("out_of_band")
    )

    return {
        "lane": "1_claim_flood_stratified",
        "n_probes_total": len(probes),
        "n_in_band_sampler_yielded": n_in_band_sampled,
        "n_in_band_routed_to_falsifier_panel": n_in_band_routed,
        "n_completed": len(records),
        "n_errors": len(errors),
        "wall_clock_seconds": elapsed,
        "throughput_per_second": throughput,
        "terminal_state_counts": dict(state_counts),
        "kill_pattern_root_counts": dict(kill_pattern_root_counts),
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Lane 7 — precision-gradient on a fresh borderline coefficient set
# ---------------------------------------------------------------------------


def lane_7_precision_gradient_fresh() -> dict:
    """Lane 7: precision-gradient. Pick a DIFFERENT INCONCLUSIVE entry than
    fire #1 covered (which was [1,-4,5,0,-5,4,-1,0])."""
    from prometheus_math.lehmer_path_a import high_precision_M_via_factor

    # Different INCONCLUSIVE entry from deg-14 ±5 brute-force.
    # Half = [1, -3, 1, 5, -5, -1, 3, -2] (entry #2 in the seed_halves
    # list from fire #1 — used in fire #1 only as a perturbation seed,
    # never run through high-precision factor itself)
    half = [1, -3, 1, 5, -5, -1, 3, -2]
    coeffs_ascending = palindrome_from_half(half)

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
                "status": out.get("status"),
                "M": str(out.get("M_clean") or out.get("M") or "n/a"),
                "precision_digits": out.get("precision_digits", out.get("dps")),
                "method": out.get("method"),
                "factorization_label": out.get("factorization_label"),
            })
        except Exception as exc:
            results.append({
                "dps": dps,
                "error": repr(exc)[:200],
            })

    # Substrate-grade properties to verify:
    M_values = [r.get("M") for r in results if "error" not in r]
    M_floats = []
    for v in M_values:
        try:
            if v in (None, "n/a"):
                M_floats.append(None)
            else:
                M_floats.append(float(str(v)))
        except (TypeError, ValueError):
            M_floats.append(None)
    M_finite = [v for v in M_floats if v is not None]
    M_spread = (max(M_finite) - min(M_finite)) if M_finite else 0.0
    converged_constant = len(set(M_finite)) <= 1 if M_finite else False
    band_status_at_each = [
        ("in_band" if (v is not None and 1.001 <= v <= 1.18)
         else "out_of_band" if v is not None
         else "no_value")
        for v in M_floats
    ]
    verdict_oscillation = len(set(band_status_at_each)) > 1

    return {
        "lane": "7_precision_gradient_fresh",
        "coeffs_ascending": coeffs_ascending,
        "dps_ladder": dps_ladder,
        "results": results,
        "M_values_at_each_dps": M_floats,
        "M_spread": M_spread,
        "converged_to_constant": converged_constant,
        "band_status_at_each_dps": band_status_at_each,
        "verdict_oscillates": verdict_oscillation,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> dict:
    SEED = 20260507_13  # fire-9-timestamp-derived
    summary = {
        "fire": 9,
        "lanes": [1, 7],
        "seed": SEED,
        "lane_1": lane_1_stratified_claim_flood(SEED),
        "lane_7": lane_7_precision_gradient_fresh(),
    }
    out_path = Path("charon/diagnostics/substrate_tester_fire_9_results.json")
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1: {summary['lane_1']['n_probes_total']} probes, "
          f"{summary['lane_1']['n_in_band_sampler_yielded']} in-band sampled, "
          f"{summary['lane_1']['n_errors']} errors, "
          f"throughput {summary['lane_1']['throughput_per_second']:.1f}/s")
    print(f"  terminal states: {summary['lane_1']['terminal_state_counts']}")
    print(f"  kill_pattern_root: {summary['lane_1']['kill_pattern_root_counts']}")
    print(f"Lane 7: M_spread={summary['lane_7']['M_spread']:.6f}, "
          f"converged={summary['lane_7']['converged_to_constant']}, "
          f"oscillates={summary['lane_7']['verdict_oscillates']}")
    return summary


if __name__ == "__main__":
    run()
