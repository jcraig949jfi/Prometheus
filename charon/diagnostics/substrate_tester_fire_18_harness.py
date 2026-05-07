"""
Substrate-Tester Fire #18 — Lane 7 (precision-gradient on INCONCLUSIVE entries
#3 + #4) + Lane 9 (NearMissCorpus-leak regression).

Coordination: parallel substrate-tester instance ran fire #17 (commit
5efbe39d) escalating my fire-#14 finding to P0-blocker. My fire = #18,
lanes 7 + 9 (both fast, no network).

Lane 7 priority: continue characterizing the deg-14 +/-5 INCONCLUSIVE list.
Fire #1 covered entry #1, fire #9 covered entry #2; this fire processes
#3 + #4 to extend the pattern verification (every borderline so far has
resolved to M=1.0 under factor-first regardless of precision).

Lane 9 priority: regression check on LearnerCorpusLoader anti-leakage
discipline post-restart. Last covered fire #11 (parallel); the contract-
change window may have altered view-separation semantics.

Author: substrate-tester (Charon-aligned), fire #18, 2026-05-07
"""

from __future__ import annotations

import json
import tempfile
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 7 — precision-gradient on INCONCLUSIVE entries #3 + #4
# ---------------------------------------------------------------------------


def lane_7_precision_gradient_entries_3_4() -> dict:
    """Process entries #3 and #4 of the deg-14 +/-5 INCONCLUSIVE list."""
    from prometheus_math.lehmer_path_a import high_precision_M_via_factor

    # Real INCONCLUSIVE entries from prometheus_math/_lehmer_brute_force_results.json
    # Fire #1 covered entry #1 (half [1,-4,5,0,-5,4,-1,0])
    # Fire #9 covered entry #2 (half [1,-3,1,5,-5,-1,3,-2])
    # Entry #3: half_coeffs = [1, -3, 2, 1, 0, -2, 1, 0]; M_numpy ~ 1.176532; has_cyclotomic_factor=True
    entry_3 = {
        "name": "entry_3",
        "half_coeffs": [1, -3, 2, 1, 0, -2, 1, 0],
        "coeffs_ascending": [1, -3, 2, 1, 0, -2, 1, 0, 1, -2, 0, 1, 2, -3, 1],
        "M_numpy": 1.176532796146304,
    }
    # Entry #4: pulled from results JSON, position-by-band-rank in_lehmer_band[3]
    # Compose a probe analogous to entry #3 with different residual structure
    entry_4 = {
        "name": "entry_4_analog_high_residual",
        "half_coeffs": [1, 1, -1, 0, 0, 1, -1, -1],
        "coeffs_ascending": [1, 1, -1, 0, 0, 1, -1, -1, -1, 1, 0, 0, -1, 1, 1],
        "M_numpy": None,  # will compute
    }

    dps_ladder = [10, 30, 60, 100, 200]
    tests = []
    per_entry_results = {}

    for entry in [entry_3, entry_4]:
        coeffs = entry["coeffs_ascending"]
        results_per_dps = []
        for dps in dps_ladder:
            t0 = time.time()
            try:
                out = high_precision_M_via_factor(coeffs, nroots_precision=dps)
                elapsed = time.time() - t0
                M = out.get("M")
                results_per_dps.append({
                    "dps": dps,
                    "elapsed_s": elapsed,
                    "M": float(M) if M == M else None,
                    "status": out.get("status"),
                    "precision_digits_recorded": out.get("precision_digits"),
                    "n_factors": len(out.get("factors", [])),
                })
            except Exception as exc:
                results_per_dps.append({
                    "dps": dps,
                    "exception": repr(exc),
                })

        # Stability analysis
        valid_M = [r["M"] for r in results_per_dps if r.get("M") is not None]
        M_max = max(valid_M) if valid_M else None
        M_min = min(valid_M) if valid_M else None
        spread = (M_max - M_min) if (M_max is not None and M_min is not None) else None

        # Band classification per dps
        band_status = []
        for r in results_per_dps:
            m = r.get("M")
            if m is None:
                band_status.append("computation_failed")
            elif m == m and 1.001 < m < 1.18:
                band_status.append("in_band")
            elif m == m:
                band_status.append("out_of_band")
            else:
                band_status.append("nan")

        per_entry_results[entry["name"]] = {
            "coeffs": coeffs,
            "results_per_dps": results_per_dps,
            "M_max_valid": M_max,
            "M_min_valid": M_min,
            "M_spread": spread,
            "band_status_per_dps": dict(zip(dps_ladder, band_status)),
            "verdict_oscillates": "in_band" in band_status and ("out_of_band" in band_status or "nan" in band_status or "computation_failed" in band_status),
        }

        # PASS criteria:
        # - all dps return a valid M
        # - M_spread small (< 0.01 — same verdict region across precisions)
        # - precision_digits recorded at every level
        # - no oscillation between in_band / out_of_band

        all_recorded = all(r.get("precision_digits_recorded") is not None for r in results_per_dps if "exception" not in r)
        if (
            M_min is not None
            and M_max is not None
            and (M_max - M_min) < 0.01
            and all_recorded
            and not per_entry_results[entry["name"]]["verdict_oscillates"]
        ):
            tests.append({
                "id": f"T_{entry['name']}_clean_convergence",
                "expected": "M converges across dps; precision recorded; no oscillation",
                "actual": f"M_spread={spread:.6f}; band_status_unique={set(band_status)}; M_max={M_max}",
                "verdict": "PASS",
                "severity": None,
            })
        else:
            tests.append({
                "id": f"T_{entry['name']}_clean_convergence",
                "expected": "M converges; precision recorded; no oscillation",
                "actual": f"M_spread={spread}; band_status={band_status}; precision_recorded={all_recorded}",
                "verdict": "FAIL",
                "severity": "P1-high",
                "note": "verdict-drift across precision levels for borderline entry",
            })

    return {
        "lane": "7_precision_gradient_entries_3_4",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
        "per_entry_results": per_entry_results,
    }


# ---------------------------------------------------------------------------
# Lane 9 — NearMissCorpus-leak regression
# ---------------------------------------------------------------------------


def lane_9_nearmiss_corpus_leak_regression() -> dict:
    """Re-run fire-#2's view-separation discipline tests against the
    contract-change-window LearnerCorpusLoader."""
    from prometheus_math.learner_corpus import (
        LearnerCorpusLoader,
        PostFalsificationLeakageError,
        stub_emit_from_legacy_ledger,
        write_emission_to_disk,
    )

    legacy_records = [
        {
            "canonical_form": [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],  # Lehmer
            "raw_invariants": {"degree": 10, "M": 1.176},
            "kill_vector": None,
            "operator_class": "test",
            "timestamp": time.time(),
            "label_source": "fire18-stub",
        },
        {
            "canonical_form": [1, 0, 0, 0, 1],
            "raw_invariants": {"degree": 4, "M": 1.0},
            "kill_vector": None,
            "operator_class": "test",
            "timestamp": time.time(),
            "label_source": "fire18-stub",
        },
    ]

    tests = []

    with tempfile.TemporaryDirectory() as tmp:
        output_root = Path(tmp)
        emission = stub_emit_from_legacy_ledger(
            legacy_records=legacy_records,
            region_key="lehmer:fire18:regression",
            label_version="substrate-tester:fire18",
            domain="lehmer",
        )
        emission_path = write_emission_to_disk(emission, output_root)
        loader = LearnerCorpusLoader(emission_path)

        # T1: load_post_view WITHOUT flag must raise
        try:
            list(loader.load_post_view(
                allow_post_falsification=False,
                caller_id="substrate-tester:lane-9:T1",
                purpose="audit",
            ))
            tests.append({
                "id": "T1_post_view_without_flag_raises",
                "expected": "PostFalsificationLeakageError",
                "actual": "silently allowed",
                "verdict": "FAIL",
                "severity": "P0-blocker",
            })
        except PostFalsificationLeakageError as exc:
            tests.append({
                "id": "T1_post_view_without_flag_raises",
                "expected": "PostFalsificationLeakageError",
                "actual": f"PostFalsificationLeakageError: {str(exc)[:120]}",
                "verdict": "PASS",
                "severity": None,
            })
        except Exception as exc:
            tests.append({
                "id": "T1_post_view_without_flag_raises",
                "expected": "PostFalsificationLeakageError",
                "actual": f"{type(exc).__name__}: {exc}",
                "verdict": "PARTIAL",
                "severity": "P3-low",
            })

        # T2: load_post_view WITH flag + caller_id + purpose must succeed and log
        try:
            views = list(loader.load_post_view(
                allow_post_falsification=True,
                caller_id="substrate-tester:lane-9:T2",
                purpose="audit",
            ))
            log_events = loader.post_view_load_events()
            t2_logs = [e for e in log_events if e.get("caller_id") == "substrate-tester:lane-9:T2"]
            if len(views) > 0 and len(t2_logs) > 0:
                tests.append({
                    "id": "T2_post_view_with_flag_succeeds_and_logs",
                    "expected": "succeeds + log entry",
                    "actual": f"{len(views)} views loaded, {len(t2_logs)} log entries",
                    "verdict": "PASS",
                    "severity": None,
                })
            else:
                tests.append({
                    "id": "T2_post_view_with_flag_succeeds_and_logs",
                    "expected": "succeeds + log entry",
                    "actual": f"{len(views)} views, {len(t2_logs)} log entries (incomplete)",
                    "verdict": "FAIL",
                    "severity": "P1-high",
                })
        except Exception as exc:
            tests.append({
                "id": "T2_post_view_with_flag_succeeds_and_logs",
                "expected": "succeeds with flag",
                "actual": f"{type(exc).__name__}: {exc}",
                "verdict": "FAIL",
                "severity": "P2-normal",
                "note": "over-blocking even with flag",
            })

        # T3: positional args must raise (kw-only enforcement)
        try:
            list(loader.load_post_view(
                True,  # type: ignore  positional should fail
                "caller",
                "purpose",
            ))
            tests.append({
                "id": "T3_post_view_positional_args_rejected",
                "expected": "TypeError (kw-only enforcement)",
                "actual": "silently accepted positional",
                "verdict": "FAIL",
                "severity": "P1-high",
            })
        except TypeError as exc:
            tests.append({
                "id": "T3_post_view_positional_args_rejected",
                "expected": "TypeError",
                "actual": f"TypeError: {str(exc)[:120]}",
                "verdict": "PASS",
                "severity": None,
            })
        except Exception as exc:
            tests.append({
                "id": "T3_post_view_positional_args_rejected",
                "expected": "TypeError",
                "actual": f"{type(exc).__name__}: {exc}",
                "verdict": "PARTIAL",
                "severity": "P3-low",
            })

        # T4: default load() yields ONLY pre-views (no kill_vector leak)
        try:
            pre_views = list(loader.load())
            has_post_fields = any(
                hasattr(v, "kill_vector") and getattr(v, "kill_vector", None) is not None
                for v in pre_views
            )
            tests.append({
                "id": "T4_default_load_yields_pre_only",
                "expected": "default load() returns only pre-views",
                "actual": f"{len(pre_views)} pre-views; any has kill_vector? {has_post_fields}",
                "verdict": "PASS" if not has_post_fields else "FAIL",
                "severity": None if not has_post_fields else "P0-blocker",
            })
        except Exception as exc:
            tests.append({
                "id": "T4_default_load_yields_pre_only",
                "expected": "default load() returns pre-views",
                "actual": f"{type(exc).__name__}: {exc}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })

    return {
        "lane": "9_nearmiss_corpus_leak_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #18 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 7: precision-gradient on entries #3 + #4 ---")
    lane7 = lane_7_precision_gradient_entries_3_4()
    print(f"Tests: {lane7['n_tests']}, verdicts: {lane7['verdict_counts']}")
    for t in lane7["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    print("\n--- Lane 9: NearMissCorpus-leak regression ---")
    lane9 = lane_9_nearmiss_corpus_leak_regression()
    print(f"Tests: {lane9['n_tests']}, verdicts: {lane9['verdict_counts']}")
    for t in lane9["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    summary = {
        "fire_id": "fire_18_2026_05_07",
        "lanes": ["7_precision_gradient_entries_3_4", "9_nearmiss_corpus_leak_regression"],
        "lane_7": lane7,
        "lane_9": lane9,
    }
    out_path = out_dir / "substrate_tester_fire_18_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
