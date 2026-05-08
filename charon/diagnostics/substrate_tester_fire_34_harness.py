"""Substrate-Tester Fire #34 harness — Lane 1 (Tier 3 kill_path
regression + verbatim Mossinghoff probe) + Lane 6 (undecidable-
canonicalization regression).

Coordination: my fire #33 was last. P0 verified. ST-fire33-001 P3
residue OPEN. No new parallel.

Lane 1 — verifies the Tier 3 contract change (commit 71652470,
T-ST-fire29-002 closure): SigmaKernel.CLAIM should now raise TypeError
on non-string kill_path. Plus a small verbatim Mossinghoff probe per
the long-standing Lane 1 retired-rec.

Lane 6 — regression check that decidability-flag discipline still
holds across all post-restart + post-mini-window fires.

Outputs:
  charon/diagnostics/substrate_tester_fire_34_results.json
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 1 — Tier 3 kill_path regression + verbatim Mossinghoff probe
# ---------------------------------------------------------------------------


def lane_1_tier3_kill_path_and_mossinghoff() -> Dict[str, Any]:
    from sigma_kernel.sigma_kernel import SigmaKernel, Tier

    tests: List[Dict[str, Any]] = []

    # Part A: Tier 3 regression — kill_path validation
    kernel = SigmaKernel(":memory:")

    # T1: valid string kill_path accepted
    try:
        claim = kernel.CLAIM(
            target_name="t1_valid",
            hypothesis="h",
            evidence={"x": 1},
            kill_path="out_of_band:M=1.5_outside_(1.001,1.18)",
            target_tier=Tier.Conjecture,
        )
        tests.append({
            "id": "T1_valid_string_kill_path_accepted",
            "expected": "accepted",
            "actual": f"accepted; kill_path={claim.kill_path[:50]}",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T1_valid_string_kill_path_accepted",
            "expected": "accepted",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
            "note": "Tier 3 fix OVER-BLOCKS valid strings",
        })

    # T2: int kill_path rejected (Tier 3 contract)
    kernel2 = SigmaKernel(":memory:")
    try:
        kernel2.CLAIM(
            target_name="t2_int",
            hypothesis="h",
            evidence={"x": 1},
            kill_path=12345,  # type: ignore
            target_tier=Tier.Conjecture,
        )
        tests.append({
            "id": "T2_int_kill_path_rejected",
            "expected": "TypeError",
            "actual": "silently accepted — REGRESSION!",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except TypeError as exc:
        tests.append({
            "id": "T2_int_kill_path_rejected",
            "expected": "TypeError",
            "actual": f"TypeError: {str(exc)[:140]}",
            "verdict": "PASS",
            "note": "Tier 3 contract change #5 holds",
        })

    # T3: None kill_path rejected
    kernel3 = SigmaKernel(":memory:")
    try:
        kernel3.CLAIM(
            target_name="t3_none",
            hypothesis="h",
            evidence={"x": 1},
            kill_path=None,  # type: ignore
            target_tier=Tier.Conjecture,
        )
        tests.append({
            "id": "T3_none_kill_path_rejected",
            "expected": "TypeError",
            "actual": "silently accepted — REGRESSION!",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except TypeError as exc:
        tests.append({
            "id": "T3_none_kill_path_rejected",
            "expected": "TypeError",
            "actual": f"TypeError: {str(exc)[:100]}",
            "verdict": "PASS",
        })

    # Part B: verbatim Mossinghoff probe (per fire #19 retired-rec —
    # use VERBATIM in-band entries, not perturbations)
    try:
        from prometheus_math.discovery_pipeline import DiscoveryPipeline
        from prometheus_math.lehmer_brute_force_path_c import (
            load_mossinghoff_catalog,
        )
        from sigma_kernel.bind_eval_v2 import BindEvalExtension

        catalog = load_mossinghoff_catalog()
        # Filter to in-band entries with degree <= 14 (manageable)
        def _M(e):
            try: return float(e.get("mahler_measure", 0.0))
            except (TypeError, ValueError): return 0.0
        in_band = [
            e for e in catalog
            if 1.001 <= _M(e) <= 1.18
            and len(e.get("coeffs", [])) <= 15
        ]
        # Take 3 verbatim
        sorted_in_band = sorted(in_band, key=lambda e: len(e.get("coeffs", [])))[:3]

        kernel_pipe = SigmaKernel(":memory:")
        ext = BindEvalExtension(kernel_pipe)
        pipe = DiscoveryPipeline(kernel=kernel_pipe, ext=ext)

        routing_outcomes = []
        for entry in sorted_in_band:
            coeffs = list(entry.get("coeffs", []))
            m = _M(entry)
            try:
                rec = pipe.process_candidate(coeffs, m)
                routing_outcomes.append({
                    "M": m,
                    "deg": len(coeffs) - 1,
                    "terminal_state": rec.terminal_state,
                    "kill_pattern": (rec.kill_pattern[:80] if rec.kill_pattern else None),
                })
            except Exception as exc:  # noqa: BLE001
                routing_outcomes.append({
                    "M": m, "deg": len(coeffs) - 1,
                    "error": f"{type(exc).__name__}: {str(exc)[:120]}",
                })

        tests.append({
            "id": "T4_verbatim_mossinghoff_probes",
            "expected": "deterministic routing for all 3",
            "actual": f"routed {len(routing_outcomes)} probes; outcomes: {routing_outcomes}",
            "verdict": "PASS" if all("error" not in r for r in routing_outcomes) else "PARTIAL",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T4_verbatim_mossinghoff_probes",
            "expected": "Mossinghoff catalog load + 3 probes routed",
            "actual": f"setup raised: {type(exc).__name__}: {str(exc)[:140]}",
            "verdict": "ERROR",
            "severity": "P3-low",
        })

    return {
        "lane": "1_tier3_kill_path_and_mossinghoff",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 6 — undecidable-canonicalization regression
# ---------------------------------------------------------------------------


def lane_6_regression() -> Dict[str, Any]:
    from sigma_kernel.coordinate_chart import (
        CanonicalizationProtocol,
        VALID_DECIDABILITY,
        all_charts,
    )
    import sigma_kernel.coordinate_charts  # noqa: F401

    tests: List[Dict[str, Any]] = []

    # T1: VALID_DECIDABILITY tuple unchanged
    expected = {"decidable", "undecidable", "conditional"}
    actual = set(VALID_DECIDABILITY)
    tests.append({
        "id": "T1_valid_decidability_tuple_unchanged",
        "expected": str(sorted(expected)),
        "actual": str(sorted(actual)),
        "verdict": "PASS" if actual == expected else "FAIL",
        "severity": None if actual == expected else "P1-high",
    })

    # T2: undecidable construction works
    try:
        proto = CanonicalizationProtocol(
            impl="word_problem_finitely_presented_groups",
            decidability_status="undecidable",
            choice_dependencies=("normal_form_choice",),
            version="1.0.0",
        )
        tests.append({
            "id": "T2_undecidable_construction",
            "expected": "succeeds",
            "actual": f"impl={proto.impl!r}, ds={proto.decidability_status!r}",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T2_undecidable_construction",
            "expected": "succeeds",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # T3: invalid decidability_status raises ValueError
    try:
        _ = CanonicalizationProtocol(
            impl="bogus_fire34",
            decidability_status="not_a_valid_status",
            choice_dependencies=(),
            version="1.0.0",
        )
        tests.append({
            "id": "T3_invalid_decidability_rejected",
            "expected": "ValueError",
            "actual": "silently constructed",
            "verdict": "FAIL",
            "severity": "P1-high",
        })
    except ValueError as exc:
        tests.append({
            "id": "T3_invalid_decidability_rejected",
            "expected": "ValueError",
            "actual": f"ValueError: {str(exc)[:100]}",
            "verdict": "PASS",
        })

    # T4: registered Lehmer chart still decidable
    try:
        charts = all_charts()
        lehmer = next((c for c in charts if c.domain == "lehmer"), None)
        if lehmer and lehmer.canonicalization.decidability_status == "decidable":
            tests.append({
                "id": "T4_lehmer_chart_decidable",
                "expected": "decidable",
                "actual": f"impl={lehmer.canonicalization.impl!r}, ds=decidable",
                "verdict": "PASS",
            })
        else:
            tests.append({
                "id": "T4_lehmer_chart_decidable",
                "expected": "decidable",
                "actual": f"chart present={lehmer is not None}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T4_lehmer_chart_decidable",
            "expected": "Lehmer chart accessible + decidable",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
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
        "fire": 34,
        "lanes": [1, 6],
        "lane_1": lane_1_tier3_kill_path_and_mossinghoff(),
        "lane_6": lane_6_regression(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_34_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1: {summary['lane_1']['verdict_counts']}")
    print(f"Lane 6: {summary['lane_6']['verdict_counts']}")
    return summary


if __name__ == "__main__":
    run()
