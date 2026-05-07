"""Substrate-Tester Fire #11 harness — Lane 9 (NearMissCorpus-leak
regression) + Lane 6 (undecidable-canonicalization regression).

Coordination note: Fire #10 was performed by a parallel substrate-tester
instance (commit db0c157d on 2026-05-07). That fire covered Lane 4
(ST003 regression PASS) + Lane 13 (canon-fuzz PASS). My fire = #11.

Lane 9 priority: last covered fire #2; never re-probed despite the
contract-change window. Confirms anti-leakage discipline holds.

Lane 6 priority: last covered fire #4; relevant after T020 / T030 / T023
contract-change window — confirms the decidability flag discipline still
holds across the registry shape changes.

Outputs:
  charon/diagnostics/substrate_tester_fire_11_results.json
"""
from __future__ import annotations

import json
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Lane 9 — NearMissCorpus-leak regression
# ---------------------------------------------------------------------------


def lane_9_near_miss_corpus_leak() -> Dict[str, Any]:
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
            "operator_class": "test_lane9_fire11",
            "timestamp": time.time(),
            "label_source": "fire-11-lane9-test",
        }
        emission = stub_emit_from_legacy_ledger(
            legacy_records=[record],
            region_key="lehmer:fire-11:lane-9-test",
            label_version="substrate-tester:fire-11",
            domain="lehmer",
        )
        emission_path = write_emission_to_disk(emission, out)
        loader = LearnerCorpusLoader(emission_path)

        # T1: post_view default (allow_post_falsification=False) must reject
        try:
            views = loader.load_post_view(
                allow_post_falsification=False,
                caller_id="fire11",
                purpose="leak-regression",
            )
            tests.append({
                "id": "T1_post_view_default_rejects",
                "expected": "PostFalsificationLeakageError",
                "actual": f"silently returned views",
                "verdict": "FAIL",
                "severity": "P0-blocker",
            })
        except PostFalsificationLeakageError as exc:
            tests.append({
                "id": "T1_post_view_default_rejects",
                "expected": "PostFalsificationLeakageError",
                "actual": f"raised: {str(exc)[:100]}",
                "verdict": "PASS",
            })

        # T2: positional args rejected (kw-only enforcement)
        try:
            _ = loader.load_post_view(True, "caller", "purpose")  # noqa
            tests.append({
                "id": "T2_post_view_positional_args_rejected",
                "expected": "TypeError (kw-only)",
                "actual": "silently accepted positional args",
                "verdict": "FAIL",
                "severity": "P1-high",
            })
        except TypeError as exc:
            tests.append({
                "id": "T2_post_view_positional_args_rejected",
                "expected": "TypeError",
                "actual": f"TypeError: {str(exc)[:100]}",
                "verdict": "PASS",
            })

        # T3: load_post_view with allow=True succeeds + audit log
        try:
            views = list(loader.load_post_view(
                allow_post_falsification=True,
                caller_id="fire11",
                purpose="lane9-audit-test",
            ))
            tests.append({
                "id": "T3_post_view_allow_true_succeeds",
                "expected": "loaded successfully",
                "actual": f"loaded {len(views)} views with allow=True",
                "verdict": "PASS",
            })
        except Exception as exc:  # noqa: BLE001
            tests.append({
                "id": "T3_post_view_allow_true_succeeds",
                "expected": "loaded successfully",
                "actual": f"raised: {type(exc).__name__}: {exc}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })

        # T4: default loader.load() returns pre-views; no kill_vector field
        try:
            views = list(loader.load())
            if not views:
                tests.append({
                    "id": "T4_default_load_pre_view_no_leak",
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
                        "id": "T4_default_load_pre_view_no_leak",
                        "expected": "no post-falsification fields in pre-view",
                        "actual": "post-falsification fields present in pre-view",
                        "verdict": "FAIL",
                        "severity": "P0-blocker",
                    })
                else:
                    tests.append({
                        "id": "T4_default_load_pre_view_no_leak",
                        "expected": "leak-safe default load",
                        "actual": f"loaded {len(views)} pre-views; no leak fields",
                        "verdict": "PASS",
                    })
        except Exception as exc:  # noqa: BLE001
            tests.append({
                "id": "T4_default_load_pre_view_no_leak",
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
# Lane 6 — undecidable-canonicalization regression
# ---------------------------------------------------------------------------


def lane_6_undecidable_canonicalization() -> Dict[str, Any]:
    from sigma_kernel.coordinate_chart import (
        CanonicalizationProtocol,
        VALID_DECIDABILITY,
        all_charts,
    )
    # Trigger registration side-effects so all_charts() returns shipped charts.
    import sigma_kernel.coordinate_charts  # noqa: F401

    tests: List[Dict[str, Any]] = []

    # T1: construct CanonicalizationProtocol with decidability_status='undecidable'
    try:
        proto = CanonicalizationProtocol(
            impl="novikov_word_problem",
            decidability_status="undecidable",
            choice_dependencies=("normal_form_choice",),
            version="1.0.0",
        )
        tests.append({
            "id": "T1_undecidable_construction",
            "expected": "construction succeeds",
            "actual": (
                f"impl={proto.impl!r}, decidability={proto.decidability_status!r}"
            ),
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T1_undecidable_construction",
            "expected": "construction succeeds",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # T2: invalid decidability_status raises ValueError
    try:
        _ = CanonicalizationProtocol(
            impl="bogus",
            decidability_status="maybe",
            choice_dependencies=(),
            version="1.0.0",
        )
        tests.append({
            "id": "T2_invalid_decidability_rejected",
            "expected": "ValueError",
            "actual": "silently constructed",
            "verdict": "FAIL",
            "severity": "P1-high",
        })
    except ValueError as exc:
        tests.append({
            "id": "T2_invalid_decidability_rejected",
            "expected": "ValueError naming valid options",
            "actual": f"ValueError: {str(exc)[:140]}",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T2_invalid_decidability_rejected",
            "expected": "ValueError",
            "actual": f"raised wrong type: {type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # T3: apply() on registry-only entry raises NotImplementedError
    try:
        proto = CanonicalizationProtocol(
            impl="registry_only",
            decidability_status="undecidable",
            choice_dependencies=(),
            version="1.0.0",
            canonicalize=None,  # explicit registry-only
        )
        try:
            _ = proto.apply("input")
            tests.append({
                "id": "T3_apply_without_impl_raises",
                "expected": "NotImplementedError",
                "actual": "silently returned",
                "verdict": "FAIL",
                "severity": "P0-blocker",
            })
        except NotImplementedError as exc:
            tests.append({
                "id": "T3_apply_without_impl_raises",
                "expected": "NotImplementedError",
                "actual": f"NotImplementedError: {str(exc)[:140]}",
                "verdict": "PASS",
            })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T3_apply_without_impl_raises",
            "expected": "construction + apply both work",
            "actual": f"unexpected exception during construction: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # T4: registered Lehmer chart's canonicalization is decidable
    try:
        charts = all_charts()
        lehmer_chart = next(
            (c for c in charts if c.domain == "lehmer"), None,
        )
        if lehmer_chart is None:
            tests.append({
                "id": "T4_lehmer_chart_decidable",
                "expected": "Lehmer chart registered with decidable canonicalizer",
                "actual": "no Lehmer chart in registry",
                "verdict": "FAIL",
                "severity": "P0-blocker",
            })
        else:
            canon = lehmer_chart.canonicalization
            if canon.decidability_status == "decidable":
                tests.append({
                    "id": "T4_lehmer_chart_decidable",
                    "expected": "decidable",
                    "actual": (
                        f"impl={canon.impl!r}, decidability={canon.decidability_status!r}"
                    ),
                    "verdict": "PASS",
                })
            else:
                tests.append({
                    "id": "T4_lehmer_chart_decidable",
                    "expected": "decidable",
                    "actual": f"decidability_status={canon.decidability_status!r}",
                    "verdict": "FAIL",
                    "severity": "P1-high",
                })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T4_lehmer_chart_decidable",
            "expected": "Lehmer chart accessible",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # T5: VALID_DECIDABILITY tuple still contains the expected three values
    expected_set = {"decidable", "undecidable", "conditional"}
    actual_set = set(VALID_DECIDABILITY)
    if actual_set == expected_set:
        tests.append({
            "id": "T5_valid_decidability_tuple_unchanged",
            "expected": str(sorted(expected_set)),
            "actual": str(sorted(actual_set)),
            "verdict": "PASS",
        })
    else:
        tests.append({
            "id": "T5_valid_decidability_tuple_unchanged",
            "expected": str(sorted(expected_set)),
            "actual": str(sorted(actual_set)),
            "verdict": "FAIL",
            "severity": "P1-high",
            "note": "VALID_DECIDABILITY contract changed since fire #4 baseline",
        })

    return {
        "lane": "6_undecidable_canonicalization_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 11,
        "lanes": [9, 6],
        "note": (
            "Fire #10 was performed by a parallel substrate-tester instance "
            "(commit db0c157d). My fire = #11."
        ),
        "lane_9": lane_9_near_miss_corpus_leak(),
        "lane_6": lane_6_undecidable_canonicalization(),
    }
    out_path = Path("charon/diagnostics/substrate_tester_fire_11_results.json")
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 9: {summary['lane_9']['verdict_counts']}")
    print(f"Lane 6: {summary['lane_6']['verdict_counts']}")
    return summary


if __name__ == "__main__":
    run()
