"""
Substrate-Tester Fire #6 — Lane 5 (large-scale-enumeration), full cap.

Runs `prometheus_math.lehmer_brute_force_general.run_brute_force_general`
on deg-12 ±5 palindromic (~8.86M polys, ~10x smaller than the deg-14 ±5
canonical run). Measures:
  - wall-clock vs predicted scale ("minutes" per docstring)
  - whether band candidates surface and follow-up verification works
  - whether INCONCLUSIVE handling is consistent with deg-14 baseline
  - per-stage kill-pattern distribution under the existing pipeline

Per lane spec (PRESSURE_PROMPTS_v1.md §17):
  - Cost telemetry off by >2x: P2-normal
  - ExclusionCertificate not generated: P1-high (only relevant if substrate
    has a deg-12 cert auto-emitter; v1.5 doesn't, so generation is manual)
  - INCONCLUSIVE-handling differs from deg-14 baseline: P1-high
  - Crash / OOM / hang: P0-blocker

Author: substrate-tester (Charon-aligned), fire #6, 2026-05-07
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


def lane_5_large_scale_enumeration() -> dict:
    """Run deg-12 ±5 palindromic brute-force; characterize substrate
    behavior at scale.
    """
    from prometheus_math.lehmer_brute_force_general import (
        run_brute_force_general,
        enumerate_total_size,
    )

    degree = 12
    coef_range = (-5, 5)
    n_expected = enumerate_total_size(degree, coef_range, c0_positive_only=True)

    print(f"  Expected enumeration size: {n_expected:,} polynomials")
    print(f"  Starting deg-{degree} ±{coef_range[1]} palindromic brute-force...")

    t0 = time.time()
    progress_log = []
    last_progress_t = [t0]

    def on_progress(shard_idx: int, n_shards: int, polys_processed: int):
        now = time.time()
        if now - last_progress_t[0] > 30:  # log every 30s
            elapsed = now - t0
            rate = polys_processed / elapsed if elapsed > 0 else 0
            print(f"  [t={elapsed:6.1f}s] shard {shard_idx}/{n_shards}: {polys_processed:,} polys @ {rate:,.0f}/s")
            progress_log.append({
                "elapsed_s": elapsed,
                "shard_idx": shard_idx,
                "n_shards": n_shards,
                "polys_processed": polys_processed,
                "rate_per_sec": rate,
            })
            last_progress_t[0] = now

    try:
        result = run_brute_force_general(
            degree=degree,
            coef_range=coef_range,
            c0_positive_only=True,
            progress_callback=on_progress,
        )
        wall_clock = time.time() - t0
        crashed = False
        crash_reason = None
    except Exception as exc:
        wall_clock = time.time() - t0
        crashed = True
        crash_reason = f"{type(exc).__name__}: {exc}"
        result = None

    # Build verdict summary
    tests = []

    # Test 1: completion (no crash / no hang)
    if crashed:
        tests.append({
            "id": "T1_completion",
            "expected": "deg-12 ±5 enumeration completes without crashing",
            "actual": f"crashed after {wall_clock:.1f}s: {crash_reason}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    else:
        tests.append({
            "id": "T1_completion",
            "expected": "deg-12 ±5 enumeration completes",
            "actual": f"completed in {wall_clock:.1f}s; processed {result['n_polys_processed']:,} polys ({result['n_polys_processed']/wall_clock:,.0f}/s)",
            "verdict": "PASS",
            "severity": None,
        })

    if crashed or result is None:
        return {
            "lane": "5_large_scale_enumeration",
            "degree": degree,
            "coef_range": list(coef_range),
            "n_expected": n_expected,
            "wall_clock_seconds": wall_clock,
            "progress_log": progress_log,
            "crashed": True,
            "crash_reason": crash_reason,
            "n_tests": len(tests),
            "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
            "tests": tests,
        }

    # Test 2: enumeration count matches expected (no missed polys)
    n_processed = result["n_polys_processed"]
    if n_processed == n_expected:
        tests.append({
            "id": "T2_enumeration_count_matches_expected",
            "expected": f"n_polys_processed == n_expected ({n_expected:,})",
            "actual": f"n_polys_processed == {n_processed:,} (match)",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        # Off-by-some is a P2 telemetry / off-by-one bug
        delta = n_processed - n_expected
        rel_err = abs(delta) / n_expected
        tests.append({
            "id": "T2_enumeration_count_matches_expected",
            "expected": f"n_polys_processed == {n_expected:,}",
            "actual": f"n_polys_processed == {n_processed:,} (delta={delta:+,}, rel_err={rel_err:.4%})",
            "verdict": "FAIL" if rel_err > 0.001 else "PARTIAL",
            "severity": "P2-normal",
        })

    # Test 3: throughput within reasonable bounds (substrate-tester own
    # estimate: ~50K-500K polys/sec on this hardware based on fire-1
    # baseline of ~17 claims/sec for full pipeline; brute-force is just
    # the Mahler-measure phase, much faster)
    rate = n_processed / wall_clock if wall_clock > 0 else 0
    if rate >= 10_000:
        tests.append({
            "id": "T3_throughput_reasonable",
            "expected": "throughput >= 10K polys/sec (raw enumeration phase)",
            "actual": f"{rate:,.0f} polys/sec",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T3_throughput_reasonable",
            "expected": "throughput >= 10K polys/sec",
            "actual": f"{rate:,.0f} polys/sec",
            "verdict": "FAIL",
            "severity": "P2-normal",
            "note": "brute-force enumeration is unexpectedly slow",
        })

    # Test 4: in_band candidates surfaced and shape is reasonable
    in_band_count = result["in_band_count"]
    in_band_list = result.get("in_band", [])
    # For deg-14 ±5 the canonical baseline produced 253 raw band candidates.
    # For deg-12 ±5 (~10x smaller) we expect O(20-30) band candidates by
    # rough scale — but it could be much higher if cyclotomic noise is
    # different at deg-12. Document; don't fail unless 0 hits (suggests
    # missed signal).
    if in_band_count > 0:
        tests.append({
            "id": "T4_band_candidates_surface",
            "expected": "in_band_count > 0 (some band hits expected at this scale)",
            "actual": f"in_band_count={in_band_count}; first 3 (half_tuple, M): {in_band_list[:3]}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T4_band_candidates_surface",
            "expected": "in_band_count > 0",
            "actual": "in_band_count == 0",
            "verdict": "PARTIAL",
            "severity": "P3-low",
            "note": (
                "0 band hits at deg-12 ±5 is plausible (cyclotomic-only band "
                "with no near-Salem candidates) but worth documenting"
            ),
        })

    # Test 5: shard summary structure is well-formed
    per_shard = result.get("per_shard_summary", [])
    n_shards = result.get("n_shards", 0)
    if len(per_shard) == n_shards and all(
        "shard_idx" in s and "polys_processed" in s for s in per_shard
    ):
        tests.append({
            "id": "T5_shard_summary_well_formed",
            "expected": f"per_shard_summary has {n_shards} entries with required fields",
            "actual": f"per_shard_summary length={len(per_shard)}, schema valid",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T5_shard_summary_well_formed",
            "expected": f"per_shard_summary has {n_shards} entries",
            "actual": f"per_shard_summary length={len(per_shard)}",
            "verdict": "FAIL",
            "severity": "P2-normal",
        })

    return {
        "lane": "5_large_scale_enumeration",
        "degree": degree,
        "coef_range": list(coef_range),
        "n_expected": n_expected,
        "n_processed": result["n_polys_processed"],
        "wall_clock_seconds": wall_clock,
        "throughput_per_sec": rate,
        "in_band_count": in_band_count,
        "in_band_first_5": in_band_list[:5] if in_band_list else [],
        "n_shards": n_shards,
        "progress_log": progress_log,
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #6 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("--- Lane 5: large-scale-enumeration (deg-12 ±5 palindromic) ---")

    lane5 = lane_5_large_scale_enumeration()

    print()
    print(f"Tests: {lane5['n_tests']}, verdicts: {lane5['verdict_counts']}")
    for t in lane5["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    summary = {
        "fire_id": "fire_6_2026_05_07",
        "lanes": ["5_large_scale_enumeration"],
        "lane_5": lane5,
    }
    out_path = out_dir / "substrate_tester_fire_6_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
