"""Substrate-Tester Fire #31 harness — Lane 5 (large-scale-enumeration
with NEW (degree, coef-bound) combo: deg-10 ±7).

Coordination: parallel fire #30 (commit 23483f0e) covered lanes 14 + 13
with 0 tickets. Loop resumed after user STOP/Document/Restart sequence.
P0 + P1-escalation tickets all still OPEN.

Lane 5 single-lane fire per "full cap; don't pair" rule. Extends the
cross-(degree, coef-bound) scaling matrix with deg-10 ±7. Predicted
~3.9M polys at ~30K polys/sec ≈ 2 min wall-clock.

Cumulative scaling matrix prior to this fire (5 data points):
  (14, ±5): 97.4M polys, 2.6e-6 hit rate
  (12, ±5): 8.86M polys, 1.3e-5 hit rate
  (10, ±5): 805K polys, 5.5e-5 hit rate
  (12, ±3): 353K polys, 0.0 hit rate
This fire adds:
  (10, ±7): predicted ~3.9M polys, hit rate TBD

Outputs:
  charon/diagnostics/substrate_tester_fire_31_results.json
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


def lane_5_deg10_pm7() -> Dict[str, Any]:
    from prometheus_math.lehmer_brute_force_general import run_brute_force_general

    t0 = time.time()
    n_polys_processed = 0
    n_band_hits = 0
    n_shards_reported = 0
    error = None
    try:
        result = run_brute_force_general(
            degree=10,
            coef_range=(-7, 7),
        )
        elapsed = time.time() - t0
        n_polys_processed = result.get("n_polys_processed", 0)
        n_band_hits = len(result.get("band_candidates", []))
        n_shards_reported = len(result.get("per_shard_summary", []))
    except Exception as exc:  # noqa: BLE001
        elapsed = time.time() - t0
        error = f"{type(exc).__name__}: {str(exc)[:200]}"

    tests: List[Dict[str, Any]] = []

    if error is not None:
        tests.append({
            "id": "T1_completion",
            "expected": "completes without crash",
            "actual": f"crashed: {error}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })
        return {
            "lane": "5_large_scale_deg10_pm7",
            "params": {"degree": 10, "coef_range": [-7, 7]},
            "wall_clock_seconds": elapsed,
            "n_polys_processed": n_polys_processed,
            "n_band_hits": n_band_hits,
            "n_shards_reported": n_shards_reported,
            "tests": tests,
            "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        }

    # T1: completes without crash
    tests.append({
        "id": "T1_completion",
        "expected": "completes without crash",
        "actual": f"completed in {elapsed:.1f}s",
        "verdict": "PASS",
    })

    # T2: throughput reasonable
    throughput = n_polys_processed / elapsed if elapsed > 0 else 0
    if throughput >= 10000:
        tests.append({
            "id": "T2_throughput",
            "expected": "≥ 10K polys/sec",
            "actual": f"{throughput:.0f} polys/sec",
            "verdict": "PASS",
        })
    else:
        tests.append({
            "id": "T2_throughput",
            "expected": "≥ 10K polys/sec",
            "actual": f"{throughput:.0f} polys/sec — below threshold",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # T3: band candidates surface
    tests.append({
        "id": "T3_band_hits_surface",
        "expected": "≥0 band candidates (informational)",
        "actual": f"{n_band_hits} band hits, rate={n_band_hits/n_polys_processed:.2e}",
        "verdict": "PASS",
    })

    # T4: shard summary well-formed
    tests.append({
        "id": "T4_shards_reported",
        "expected": "≥1 shards in summary",
        "actual": f"{n_shards_reported} shards",
        "verdict": "PASS" if n_shards_reported > 0 else "FAIL",
    })

    return {
        "lane": "5_large_scale_deg10_pm7",
        "params": {"degree": 10, "coef_range": [-7, 7]},
        "wall_clock_seconds": elapsed,
        "n_polys_processed": n_polys_processed,
        "n_band_hits": n_band_hits,
        "throughput_polys_per_sec": throughput,
        "n_shards_reported": n_shards_reported,
        "hit_rate": n_band_hits / max(1, n_polys_processed),
        "tests": tests,
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 31,
        "lanes": [5],
        "lane_5": lane_5_deg10_pm7(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_31_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    l5 = summary["lane_5"]
    print(f"Lane 5 (deg-10 ±7): {l5.get('verdict_counts')}, "
          f"n_polys={l5.get('n_polys_processed', 0)}, "
          f"band_hits={l5.get('n_band_hits', 0)}, "
          f"hit_rate={l5.get('hit_rate', 0):.2e}, "
          f"wall_clock={l5.get('wall_clock_seconds', 0):.1f}s, "
          f"throughput={l5.get('throughput_polys_per_sec', 0):.0f}/s")
    return summary


if __name__ == "__main__":
    run()
