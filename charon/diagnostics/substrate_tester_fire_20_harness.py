"""
Substrate-Tester Fire #20 — Lane 5 (large-scale-enumeration), full-cap.

Coordination: parallel substrate-tester instance ran fire #19
(commit 126461fb, Lane 4 + Lane 1 retirement). My fire = #20.

Lane 5 priority: overdue (last covered fire #6 at deg-12 +/-5). This
fire targets deg-10 +/-5 palindromic = 805,255 polys — a different scale
to produce comparison data:
  fire #6 deg-12 +/-5: 113 in-band hits / 8,857,805 polys = 1.27e-5
  fire #20 deg-10 +/-5: ? in-band hits / 805,255 polys (this fire)
  baseline deg-14 +/-5: 253 in-band hits / 97,435,855 polys = 2.6e-6

Author: substrate-tester (Charon-aligned), fire #20, 2026-05-07
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


def lane_5_large_scale_enumeration() -> dict:
    """Run deg-10 +/-5 palindromic brute-force; characterize substrate
    behavior at smaller scale than fire #6's deg-12 +/-5 baseline.
    """
    from prometheus_math.lehmer_brute_force_general import (
        run_brute_force_general,
        enumerate_total_size,
    )

    degree = 10
    coef_range = (-5, 5)
    n_expected = enumerate_total_size(degree, coef_range, c0_positive_only=True)

    print(f"  Expected enumeration size: {n_expected:,} polynomials")
    print(f"  Starting deg-{degree} +/-{coef_range[1]} palindromic brute-force...")

    t0 = time.time()
    progress_log = []
    last_progress_t = [t0]

    def on_progress(shard_idx: int, n_shards: int, polys_processed: int):
        now = time.time()
        if now - last_progress_t[0] > 15:  # log every 15s for smaller run
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

    tests = []

    if crashed:
        tests.append({
            "id": "T1_completion",
            "expected": "deg-10 +/-5 enumeration completes",
            "actual": f"crashed after {wall_clock:.1f}s: {crash_reason}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
        return {
            "lane": "5_large_scale_enumeration",
            "degree": degree,
            "coef_range": list(coef_range),
            "n_expected": n_expected,
            "wall_clock_seconds": wall_clock,
            "crashed": True,
            "crash_reason": crash_reason,
            "n_tests": len(tests),
            "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
            "tests": tests,
        }

    n_processed = result["n_polys_processed"]
    in_band_count = result["in_band_count"]
    in_band_list = result.get("in_band", [])
    rate = n_processed / wall_clock if wall_clock > 0 else 0
    n_shards = result.get("n_shards", 0)

    # T1: completion
    tests.append({
        "id": "T1_completion",
        "expected": "deg-10 +/-5 enumeration completes",
        "actual": f"completed in {wall_clock:.1f}s; {n_processed:,} polys @ {rate:,.0f}/s",
        "verdict": "PASS",
        "severity": None,
    })

    # T2: count match
    if n_processed == n_expected:
        tests.append({
            "id": "T2_enumeration_count_matches_expected",
            "expected": f"n_polys_processed == {n_expected:,}",
            "actual": f"{n_processed:,} (match)",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T2_enumeration_count_matches_expected",
            "expected": f"n_polys_processed == {n_expected:,}",
            "actual": f"{n_processed:,} (delta={n_processed-n_expected})",
            "verdict": "FAIL",
            "severity": "P2-normal",
        })

    # T3: throughput >= 10K polys/sec
    if rate >= 10_000:
        tests.append({
            "id": "T3_throughput_reasonable",
            "expected": ">=10K polys/sec",
            "actual": f"{rate:,.0f} polys/sec",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T3_throughput_reasonable",
            "expected": ">=10K polys/sec",
            "actual": f"{rate:,.0f} polys/sec",
            "verdict": "FAIL",
            "severity": "P2-normal",
        })

    # T4: in_band candidates surface
    if in_band_count > 0:
        # Predicted hit rate for deg-10 +/-5 from cross-degree pattern
        # deg-14 ±5: 2.6e-6
        # deg-12 ±5: 1.27e-5 (~5x of deg-14)
        # deg-10 ±5: predicted ~6e-5 (~5x of deg-12) → ~50 hits
        observed_rate = in_band_count / n_processed
        tests.append({
            "id": "T4_band_candidates_surface",
            "expected": "in_band_count > 0",
            "actual": f"in_band_count={in_band_count}; rate={observed_rate:.2e}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T4_band_candidates_surface",
            "expected": "in_band_count > 0",
            "actual": "0 band hits",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # T5: shard summary well-formed
    per_shard = result.get("per_shard_summary", [])
    if len(per_shard) == n_shards and all(
        "shard_idx" in s and "polys_processed" in s for s in per_shard
    ):
        tests.append({
            "id": "T5_shard_summary_well_formed",
            "expected": f"per_shard_summary has {n_shards} entries",
            "actual": f"{len(per_shard)} entries, schema valid",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T5_shard_summary_well_formed",
            "expected": f"{n_shards} entries",
            "actual": f"{len(per_shard)} entries",
            "verdict": "FAIL",
            "severity": "P2-normal",
        })

    return {
        "lane": "5_large_scale_enumeration",
        "degree": degree,
        "coef_range": list(coef_range),
        "n_expected": n_expected,
        "n_processed": n_processed,
        "wall_clock_seconds": wall_clock,
        "throughput_per_sec": rate,
        "in_band_count": in_band_count,
        "in_band_first_5": in_band_list[:5] if in_band_list else [],
        "n_shards": n_shards,
        "progress_log": progress_log,
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
        "scale_comparison": {
            "deg_14_pm_5_baseline": {"n": 97_435_855, "hits": 253, "rate": 253/97_435_855},
            "deg_12_pm_5_fire_6": {"n": 8_857_805, "hits": 113, "rate": 113/8_857_805},
            "deg_10_pm_5_fire_20": {"n": n_processed, "hits": in_band_count, "rate": in_band_count/n_processed if n_processed > 0 else 0},
        },
    }


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #20 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("--- Lane 5: large-scale-enumeration (deg-10 +/-5 palindromic) ---")

    lane5 = lane_5_large_scale_enumeration()

    print()
    print(f"Tests: {lane5['n_tests']}, verdicts: {lane5['verdict_counts']}")
    for t in lane5["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    print()
    print("Scale-comparison data:")
    for k, v in lane5.get("scale_comparison", {}).items():
        print(f"  {k}: n={v['n']:,}, hits={v['hits']}, rate={v['rate']:.2e}")

    summary = {
        "fire_id": "fire_20_2026_05_07",
        "lanes": ["5_large_scale_enumeration"],
        "lane_5": lane5,
    }
    out_path = out_dir / "substrate_tester_fire_20_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
