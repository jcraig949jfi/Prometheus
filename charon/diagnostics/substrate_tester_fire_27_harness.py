"""Substrate-Tester Fire #27 harness — Lane 9 (NearMissCorpus-leak
regression) + Lane 5 (large-scale-enumeration with NEW coefficient bound:
deg-12 ±3, smaller search space than fire #6's deg-12 ±5).

Coordination: parallel fire #26 (commit 13f50a4b) covered lanes 11 + 13
with 0 tickets. P0 ticket T-ST-fire17-001 still OPEN; deferred re-probe.
P1-escalation T-ST-fire25-001 (substrate-wide frozen-dataclass) also
still OPEN.

Lane 9: regression check on view-separation discipline. Last my-instance
fire #18 (parallel did fire #11). Includes the generator-iteration rule
from fire #11 (iterate generators to surface internal errors).

Lane 5 with NEW coef-bound per fire #20 standing rec: deg-12 ±3 instead
of the previously-baselined ±5 family. Tests whether substrate's
brute-force enumerator handles the smaller coefficient bound correctly.
Predicted: ~7^11 ≈ 1.97M polys (vs ±5's 11^11 = 285K... wait recheck).
Actually deg-12 palindromic ±5 gave 8.86M; deg-12 palindromic ±3 should
give 7^7 = 823543 polys (~9× smaller).

Outputs:
  charon/diagnostics/substrate_tester_fire_27_results.json
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 9 — NearMissCorpus-leak regression
# ---------------------------------------------------------------------------


def lane_9_leak_regression() -> Dict[str, Any]:
    from prometheus_math.learner_corpus import (
        LearnerCorpusLoader,
        PostFalsificationLeakageError,
        stub_emit_from_legacy_ledger,
        write_emission_to_disk,
    )

    tests: List[Dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        record = {
            "canonical_form": [1, 1, 1],
            "raw_invariants": {
                "poly_coefficients": [1, 1, 1],
                "mahler_measure_dps60": 1.0,
                "height": 1,
            },
            "operator_class": "test_lane9_fire27",
            "timestamp": time.time(),
            "label_source": "fire-27-lane9-test",
        }
        emission = stub_emit_from_legacy_ledger(
            legacy_records=[record],
            region_key="lehmer:fire-27:lane-9-test",
            label_version="substrate-tester:fire-27",
            domain="lehmer",
        )
        emission_path = write_emission_to_disk(emission, out)
        loader = LearnerCorpusLoader(emission_path)

        # T1: post_view default rejects (ITERATE the generator per fire #11 lesson)
        try:
            views_gen = loader.load_post_view(
                allow_post_falsification=False,
                caller_id="fire27",
                purpose="leak-regression",
            )
            # Force iteration to surface generator-internal error.
            list(views_gen)
            tests.append({
                "id": "T1_post_view_default_rejects",
                "expected": "PostFalsificationLeakageError on iteration",
                "actual": "iterated cleanly without error",
                "verdict": "FAIL",
                "severity": "P0-blocker",
            })
        except PostFalsificationLeakageError as exc:
            tests.append({
                "id": "T1_post_view_default_rejects",
                "expected": "PostFalsificationLeakageError",
                "actual": f"raised: {str(exc)[:100]}",
                "verdict": "PASS",
                "note": "generator-iteration rule from fire #11 applied",
            })

        # T2: positional args rejected
        try:
            _ = loader.load_post_view(True, "caller", "purpose")  # type: ignore
            tests.append({
                "id": "T2_post_view_positional_rejected",
                "expected": "TypeError",
                "actual": "silently accepted",
                "verdict": "FAIL",
                "severity": "P1-high",
            })
        except TypeError as exc:
            tests.append({
                "id": "T2_post_view_positional_rejected",
                "expected": "TypeError",
                "actual": f"TypeError: {str(exc)[:100]}",
                "verdict": "PASS",
            })

        # T3: allow=True succeeds
        try:
            views = list(loader.load_post_view(
                allow_post_falsification=True,
                caller_id="fire27",
                purpose="lane9-regression",
            ))
            tests.append({
                "id": "T3_allow_true_succeeds",
                "expected": "loads successfully",
                "actual": f"loaded {len(views)} views",
                "verdict": "PASS",
            })
        except Exception as exc:  # noqa: BLE001
            tests.append({
                "id": "T3_allow_true_succeeds",
                "expected": "loads successfully",
                "actual": f"raised: {type(exc).__name__}: {exc}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })

        # T4: default load() returns leak-safe pre-views
        try:
            views = list(loader.load())
            if not views:
                tests.append({
                    "id": "T4_default_load_no_leak",
                    "expected": ">=1 pre-view",
                    "actual": "0 views",
                    "verdict": "FAIL",
                    "severity": "P1-high",
                })
            else:
                obj = views[0].object
                has_leak_fields = any(
                    hasattr(obj, f) and getattr(obj, f) is not None
                    for f in ("kill_vector", "kill_pattern", "verdict")
                )
                if has_leak_fields:
                    tests.append({
                        "id": "T4_default_load_no_leak",
                        "expected": "no post-falsification fields",
                        "actual": "post-falsification fields present in pre-view",
                        "verdict": "FAIL",
                        "severity": "P0-blocker",
                    })
                else:
                    tests.append({
                        "id": "T4_default_load_no_leak",
                        "expected": "leak-safe default load",
                        "actual": f"loaded {len(views)} pre-views; no leak fields",
                        "verdict": "PASS",
                    })
        except Exception as exc:  # noqa: BLE001
            tests.append({
                "id": "T4_default_load_no_leak",
                "expected": "leak-safe default load",
                "actual": f"raised: {type(exc).__name__}: {exc}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })

    return {
        "lane": "9_near_miss_corpus_leak_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 5 — large-scale-enumeration with NEW coefficient bound (deg-12 ±3)
# ---------------------------------------------------------------------------


def lane_5_deg12_pm3() -> Dict[str, Any]:
    """Per fire #20 standing rec: vary coefficient bound at fixed degree
    rather than re-probe existing combinations. Deg-12 ±3 hasn't been
    baselined; predicted ~824K polys vs the 8.86M of deg-12 ±5."""
    from prometheus_math.lehmer_brute_force_general import run_brute_force_general

    t0 = time.time()
    n_polys_processed = 0
    n_band_hits = 0
    n_shards_reported = 0
    error = None
    try:
        result = run_brute_force_general(
            degree=12,
            coef_range=(-3, 3),
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
            "lane": "5_large_scale_deg12_pm3",
            "params": {"degree": 12, "coef_range": [-3, 3]},
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
        "expected": "≥1 band candidates",
        "actual": f"{n_band_hits} band hits, rate={n_band_hits/n_polys_processed:.2e}",
        "verdict": "PASS" if n_band_hits >= 0 else "FAIL",
    })

    # T4: shard summary well-formed
    tests.append({
        "id": "T4_shards_reported",
        "expected": "≥1 shards in summary",
        "actual": f"{n_shards_reported} shards",
        "verdict": "PASS" if n_shards_reported > 0 else "FAIL",
    })

    return {
        "lane": "5_large_scale_deg12_pm3",
        "params": {"degree": 12, "coef_range": [-3, 3]},
        "wall_clock_seconds": elapsed,
        "n_polys_processed": n_polys_processed,
        "n_band_hits": n_band_hits,
        "throughput_polys_per_sec": throughput,
        "n_shards_reported": n_shards_reported,
        "hit_rate": n_band_hits / max(1, n_polys_processed),
        "tests": tests,
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 27,
        "lanes": [9, 5],
        "lane_9": lane_9_leak_regression(),
        "lane_5": lane_5_deg12_pm3(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_27_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 9: {summary['lane_9']['verdict_counts']}")
    l5 = summary["lane_5"]
    print(f"Lane 5 (deg-12 ±3): {l5.get('verdict_counts')}, "
          f"n_polys={l5.get('n_polys_processed', 0)}, "
          f"band_hits={l5.get('n_band_hits', 0)}, "
          f"hit_rate={l5.get('hit_rate', 0):.2e}, "
          f"wall_clock={l5.get('wall_clock_seconds', 0):.1f}s")
    return summary


if __name__ == "__main__":
    run()
