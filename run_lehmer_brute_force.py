"""Standalone CLI runner for the Lehmer brute-force enumerator.

This script lives OUTSIDE the prometheus_math package so that Windows
multiprocessing children (spawn mode) re-import only this lightweight
module — NOT the full prometheus_math package, which transitively
imports cypari/PARI and allocates ~1 GB per process.

The script orchestrates the brute force in two phases:

1. Parallel enumeration via ``_lehmer_brute_force_worker.process_shard_worker``
   across N workers. Each worker imports only numpy + techne.lib.mahler_measure.
   Workers return raw band candidates (M_numpy, half_coeffs).

2. Single-process verification of the band candidates: mpmath recheck,
   cyclotomic-factor classification, Mossinghoff cross-check, verdict.
   This phase imports the full prometheus_math (and its cyclotomic /
   sympy machinery) ONCE in the parent.

Usage
-----
    python run_lehmer_brute_force.py \
        --workers 12 \
        --output prometheus_math/_lehmer_brute_force_results.json
"""
from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Brute-force Lehmer-band enumeration on the deg-14 "
                    "reciprocal palindromic subspace."
    )
    parser.add_argument("--lo", type=int, default=-5)
    parser.add_argument("--hi", type=int, default=5)
    parser.add_argument("--band", type=float, default=1.18)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--output", type=str,
                        default="prometheus_math/_lehmer_brute_force_results.json")
    parser.add_argument("--all-c0", action="store_true",
                        help="Disable c_0 > 0 sign canonicalisation.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    coef_range = (int(args.lo), int(args.hi))
    band_upper = float(args.band)
    c0_positive_only = not args.all_c0
    progress = not args.quiet
    output_path = Path(args.output)

    # ------------------------------------------------------------------
    # Phase 0 — sanity check (lightweight import)
    # ------------------------------------------------------------------
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Import worker (lightweight: numpy + techne only) for sharding helpers.
    from _lehmer_brute_force_worker import process_shard_worker
    # The worker itself doesn't have shard counting; replicate it inline.

    inner_count = coef_range[1] - coef_range[0] + 1
    if c0_positive_only:
        c0_count = sum(1 for c in range(coef_range[0], coef_range[1] + 1)
                       if c > 0)
    else:
        c0_count = sum(1 for c in range(coef_range[0], coef_range[1] + 1)
                       if c != 0)
    n_shards = c0_count * inner_count
    n_total = c0_count * (inner_count ** 7)

    if args.workers is None:
        num_workers = max(1, (os.cpu_count() or 1) - 1)
    else:
        num_workers = int(args.workers)
    num_workers = min(num_workers, n_shards)

    if progress:
        print(f"[lehmer_brute_force] subspace size: {n_total:,} polys")
        print(f"[lehmer_brute_force] shards: {n_shards}, workers: {num_workers}")
        print(f"[lehmer_brute_force] band: M in (1+1e-6, {band_upper})")

    # ------------------------------------------------------------------
    # Sanity check: Lehmer's polynomial reproduces correctly.
    # We do this in the parent (lightweight: just numpy + mpmath).
    # ------------------------------------------------------------------
    from techne.lib.mahler_measure import mahler_measure as _mm
    LEHMER_M = 1.1762808182599175
    lehmer_desc = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    M_np = float(_mm(lehmer_desc))
    np_err = abs(M_np - LEHMER_M)
    try:
        import mpmath as mp_
        mp_.mp.dps = 30
        roots = mp_.polyroots([mp_.mpf(c) for c in lehmer_desc],
                              maxsteps=300, extraprec=50)
        M_mp = abs(mp_.mpf(lehmer_desc[0]))
        for r in roots:
            if abs(r) > 1:
                M_mp = M_mp * abs(r)
        M_mp = float(M_mp)
    except Exception:
        M_mp = float("nan")
    mp_err = abs(M_mp - LEHMER_M) if M_mp == M_mp else float("nan")
    sanity = {
        "lehmer_M_expected": LEHMER_M,
        "lehmer_M_numpy": M_np,
        "lehmer_M_mpmath": M_mp,
        "numpy_abs_err": np_err,
        "mpmath_abs_err": mp_err,
        "pass_numpy": bool(np_err < 1e-9),
        "pass_mpmath": bool(M_mp == M_mp and mp_err < 1e-12),
    }
    if not sanity["pass_numpy"]:
        raise RuntimeError(
            f"Lehmer sanity check FAILED: numpy err = {np_err:.3e}"
        )
    if progress:
        print(f"[lehmer_brute_force] Lehmer sanity: numpy err={np_err:.2e}, "
              f"mpmath err={mp_err:.2e} -- OK")

    # ------------------------------------------------------------------
    # Phase 1 — parallel enumeration (workers ONLY import numpy + techne)
    # ------------------------------------------------------------------
    t_start = time.perf_counter()
    shard_args = [
        (i, n_shards, coef_range, band_upper, c0_positive_only)
        for i in range(n_shards)
    ]
    band_raw: list = []
    polys_processed_total = 0
    if num_workers == 1:
        for sa in shard_args:
            res = process_shard_worker(sa)
            polys_processed_total += res["polys_processed"]
            band_raw.extend(res["in_band"])
            if progress:
                print(
                    f"[shard {res['shard_idx'] + 1}/{n_shards}] "
                    f"polys={res['polys_processed']} "
                    f"in_band={len(res['in_band'])}"
                )
    else:
        with mp.Pool(num_workers) as pool:
            for res in pool.imap_unordered(process_shard_worker, shard_args):
                polys_processed_total += res["polys_processed"]
                band_raw.extend(res["in_band"])
                if progress:
                    print(
                        f"[shard {res['shard_idx'] + 1}/{n_shards}] "
                        f"polys={res['polys_processed']} "
                        f"in_band={len(res['in_band'])}",
                        flush=True,
                    )

    enum_time = time.perf_counter() - t_start
    if progress:
        print(
            f"[lehmer_brute_force] enumeration done in {enum_time:.1f}s; "
            f"polys_processed={polys_processed_total:,} "
            f"raw_band_count={len(band_raw)}"
        )

    # ------------------------------------------------------------------
    # Phase 2 — verification + classification (single process)
    # ------------------------------------------------------------------
    if progress:
        print("[lehmer_brute_force] Phase 2: verifying band candidates...")
    # Heavy import: pulls in prometheus_math (PARI gets loaded once here).
    from prometheus_math.lehmer_brute_force import (
        mpmath_recheck,
        is_irreducible_rational_root,
        is_reducible_to_cyclotomic_factor,
        lookup_in_mossinghoff,
        build_palindrome_descending,
        descending_to_ascending,
        verdict_from_band,
        DEGREE,
    )

    verified: list = []
    for hc, M_np in band_raw:
        try:
            M_mp = mpmath_recheck(hc, dps=30)
        except Exception:
            M_mp = float("nan")
        is_cyc = False
        if M_mp == M_mp and abs(M_mp - 1.0) < 1e-10:
            is_cyc = True
        elif math.isnan(M_mp) and abs(M_np - 1.0) < 1e-9:
            is_cyc = True
        if is_cyc:
            continue
        if M_mp == M_mp and M_mp >= band_upper:
            continue

        try:
            has_cyc_factor, residual_M = is_reducible_to_cyclotomic_factor(
                hc, M_np,
            )
        except Exception:
            has_cyc_factor, residual_M = (False, None)
        is_irred = is_irreducible_rational_root(hc)
        in_moss, moss_label = lookup_in_mossinghoff(
            hc, M_mp if M_mp == M_mp else M_np,
        )
        asc = descending_to_ascending(build_palindrome_descending(hc))
        verified.append({
            "half_coeffs": list(hc),
            "coeffs_ascending": asc,
            "M_numpy": float(M_np),
            "M_mpmath": float(M_mp),
            "is_cyclotomic": bool(is_cyc),
            "has_cyclotomic_factor": bool(has_cyc_factor),
            "residual_M_after_cyclotomic_factor": (
                float(residual_M) if residual_M is not None else None
            ),
            "is_irreducible_rational_root": is_irred,
            "in_mossinghoff": bool(in_moss),
            "mossinghoff_label": moss_label,
        })

    verdict = verdict_from_band(verified)
    wall_time = time.perf_counter() - t_start

    result = {
        "subspace": "deg14_palindromic_coeffs_pm5_c0_positive"
                    if c0_positive_only
                    else "deg14_palindromic_coeffs_pm5",
        "coef_range": [int(coef_range[0]), int(coef_range[1])],
        "band_upper": float(band_upper),
        "total_polynomials": int(n_total),
        "after_dedup": int(n_total),
        "polys_processed": int(polys_processed_total),
        "raw_band_count": int(len(band_raw)),
        "in_lehmer_band": verified,
        "wall_time_seconds": float(wall_time),
        "enumeration_time_seconds": float(enum_time),
        "verification_time_seconds": float(wall_time - enum_time),
        "verdict": verdict,
        "metadata": {
            "degree": DEGREE,
            "c0_positive_only": bool(c0_positive_only),
            "num_shards": int(n_shards),
            "num_workers": int(num_workers),
            "lehmer_constant": LEHMER_M,
            "sanity_check": sanity,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)

    print()
    print("=" * 60)
    print(f"Verdict: {verdict}")
    print(f"Polys processed: {polys_processed_total:,}")
    print(f"Wall time: {wall_time:.1f}s "
          f"(enumeration={enum_time:.1f}s, verify={wall_time - enum_time:.1f}s)")
    print(f"Raw band: {len(band_raw)}, verified non-cyclotomic: "
          f"{len(verified)}")
    in_moss = sum(1 for e in verified if e["in_mossinghoff"])
    has_cyc = sum(1 for e in verified if e["has_cyclotomic_factor"])
    print(f"  In Mossinghoff: {in_moss}")
    print(f"  Reducible via cyclotomic factor: {has_cyc}")
    novel = sum(
        1 for e in verified
        if not e["in_mossinghoff"]
        and not e["has_cyclotomic_factor"]
        and not e["is_cyclotomic"]
    )
    print(f"  Novel (not in catalog, not cyclotomic-reducible): {novel}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
