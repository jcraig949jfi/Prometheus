"""Substrate-Tester Fire #17 harness — Lane 3 T3+T4 retry (P0-escalation
probe) + Lane 7 (precision-gradient, third borderline coefficient set).

Fire #15 deferred Lane 3's T3+T4 due to a TriangulationPath signature
mismatch (used `summary`; the field is `rationale`). This fire retries
with the correct signature.

The escalation question: T-2026-05-07-ST-fire14-001 (P1, OPEN) reports
that MethodSpec silently accepts arbitrary IC strings. Fire #15 confirmed
the lookup failsafe (method_class_for_independence_class raises KeyError
on arbitrary strings). But: a caller can pass `method_class` explicitly
to TriangulationPath, bypassing the lookup. Does TriangulationProtocol's
evaluate() catch the smuggled-in arbitrary-IC path? If it doesn't and
upgrades anyway, T-ST-fire14-001 escalates to P0.

Lane 7 picks the THIRD distinct borderline INCONCLUSIVE coefficient set:
fire #1 used `[1,-4,5,0,-5,4,-1,0]`; fire #9 used `[1,-3,1,5,-5,-1,3,-2]`;
fire #17 uses `[1,-3,2,1,0,-2,1,0]`.

Outputs:
  charon/diagnostics/substrate_tester_fire_17_results.json
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 3 — TriangulationProtocol x fire-14 finding (T3+T4 retry)
# ---------------------------------------------------------------------------


def lane_3_p0_escalation_probe() -> Dict[str, Any]:
    """Definitively answer: does the substrate's TriangulationProtocol
    catch a smuggled-in arbitrary-IC path that bypasses the lookup at
    construction time by passing method_class explicitly?"""
    from sigma_kernel.method_spec import IndependenceClass, MethodSpec
    from sigma_kernel.triangulation_protocol import (
        MethodClass,
        TriangulationPath,
        TriangulationProtocol,
    )

    tests: List[Dict[str, Any]] = []

    # T1 (re-confirm): MethodSpec accepts arbitrary IC string (fire-14 finding).
    try:
        spec_arb = MethodSpec(
            engine="bogus_engine",
            strategy="bogus_strategy",
            independence_class="not_a_registered_class_xyz",  # type: ignore
            version="1.0.0",
        )
        tests.append({
            "id": "T1_methodspec_accepts_arbitrary_ic",
            "expected": "fire-14 finding reproduces",
            "actual": f"accepted; ic={spec_arb.independence_class!r}",
            "verdict": "CONFIRMED",
            "note": "T-2026-05-07-ST-fire14-001 still OPEN; reproduces",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T1_methodspec_accepts_arbitrary_ic",
            "expected": "fire-14 finding reproduces",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "RESOLVED",
            "note": "T-2026-05-07-ST-fire14-001 has been fixed; halt cascade",
        })
        return {
            "lane": "3_p0_escalation_probe",
            "tests": tests,
            "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
            "escalation_resolved": True,
        }

    # T2: build a real proof-bearing primary path.
    spec_primary = MethodSpec(
        engine="sympy",
        strategy="factor_list",
        independence_class=IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION,
        version="1.0.0",
    )
    spec_real_other = MethodSpec(
        engine="mpmath",
        strategy="polyroots",
        independence_class=IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING,
        version="1.0.0",
    )
    try:
        path_primary = TriangulationPath(
            path_id="path_primary",
            method_spec=spec_primary,
            method_class=MethodClass.PROOF_BEARING,
            verdict="verified",
            runtime_ms=10,
            rationale="primary proof-bearing path",
            timestamp=time.time(),
        )
        path_real_other = TriangulationPath(
            path_id="path_real_other",
            method_spec=spec_real_other,
            method_class=MethodClass.NUMERICAL,
            verdict="verified",
            runtime_ms=15,
            rationale="independent numerical path",
            timestamp=time.time(),
        )
        tests.append({
            "id": "T2_real_paths_construct",
            "expected": "real-IC paths construct cleanly",
            "actual": "constructed; primary + real_other",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T2_real_paths_construct",
            "expected": "real-IC paths construct cleanly",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "ERROR",
            "severity": "P2-normal",
        })
        return {
            "lane": "3_p0_escalation_probe",
            "tests": tests,
            "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        }

    # T3: smuggle in arbitrary-IC path by passing method_class explicitly.
    try:
        path_arb_ic = TriangulationPath(
            path_id="path_arb_ic",
            method_spec=spec_arb,
            method_class=MethodClass.NUMERICAL,  # caller-asserted, bypasses lookup
            verdict="verified",
            runtime_ms=20,
            rationale="arbitrary-IC path smuggled in via explicit method_class",
            timestamp=time.time(),
        )
        tests.append({
            "id": "T3_arb_ic_path_smuggle",
            "expected": "either reject OR produce a path the protocol later catches",
            "actual": "constructed cleanly with arbitrary-string IC",
            "verdict": "OBSERVED",
            "note": "construction is permissive; question is whether evaluate() catches it",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T3_arb_ic_path_smuggle",
            "expected": "construction OK or boundary rejection",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "PASS",
            "note": "TriangulationPath rejects arbitrary IC at construction (substrate safe)",
        })
        return {
            "lane": "3_p0_escalation_probe",
            "tests": tests,
            "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
            "escalation_resolved": False,
            "escalation_disposition": "fire-14 ticket stays at P1 — substrate has a construction-time failsafe",
        }

    # T4: THE KEY TEST. Run TriangulationProtocol.evaluate() with the
    # smuggled-in path. Does the protocol upgrade?
    try:
        protocol = TriangulationProtocol()
        result = protocol.evaluate([path_primary, path_real_other, path_arb_ic])
        verdict_str = (
            result.verdict.value if hasattr(result.verdict, "value")
            else str(result.verdict)
        )
        if result.upgrade_eligible:
            # P0 ESCALATION: arbitrary-IC path counted as independent in upgrade.
            tests.append({
                "id": "T4_protocol_evaluate_with_smuggled_path",
                "expected": "REJECT or INSUFFICIENT_INDEPENDENCE (substrate must not let arb-IC count as independent)",
                "actual": (
                    f"UPGRADED: verdict={verdict_str}, upgrade_eligible=True, "
                    f"summary={result.summary[:140]}"
                ),
                "verdict": "FAIL",
                "severity": "P0-blocker",
                "note": (
                    "T-2026-05-07-ST-fire14-001 ESCALATES TO P0: arbitrary-IC "
                    "path treated as independent in TriangulationProtocol upgrade. "
                    "Substrate's certification discipline can be bypassed by a "
                    "caller passing arbitrary independence_class strings."
                ),
            })
        else:
            tests.append({
                "id": "T4_protocol_evaluate_with_smuggled_path",
                "expected": "REJECT or INSUFFICIENT_INDEPENDENCE",
                "actual": (
                    f"verdict={verdict_str}, upgrade_eligible=False, "
                    f"summary={result.summary[:140]}"
                ),
                "verdict": "PASS",
                "note": (
                    "TriangulationProtocol robust against arbitrary-IC smuggling. "
                    "T-ST-fire14-001 stays at P1 — substrate has a downstream "
                    "evaluate-time failsafe in addition to the lookup failsafe."
                ),
            })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T4_protocol_evaluate_with_smuggled_path",
            "expected": "evaluate() returns or rejects cleanly",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "ERROR",
            "severity": "P2-normal",
        })

    return {
        "lane": "3_p0_escalation_probe",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 7 — precision-gradient, third borderline coefficient set
# ---------------------------------------------------------------------------


def lane_7_third_borderline() -> Dict[str, Any]:
    """Third independent INCONCLUSIVE coefficient set from the deg-14 ±5
    brute-force list. Fires #1, #9 covered entries #1, #2; this is #3."""
    from prometheus_math.lehmer_path_a import high_precision_M_via_factor

    half = [1, -3, 2, 1, 0, -2, 1, 0]
    coeffs_ascending = list(half) + list(reversed(half[:-1]))

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
                "method": out.get("method"),
                "factorization_label": out.get("factorization_label"),
            })
        except Exception as exc:  # noqa: BLE001
            results.append({"dps": dps, "error": repr(exc)[:200]})

    M_floats: List[Any] = []
    for r in results:
        if "error" in r:
            M_floats.append(None); continue
        v = r.get("M")
        try:
            M_floats.append(None if v in (None, "n/a") else float(str(v)))
        except (TypeError, ValueError):
            M_floats.append(None)
    M_finite = [v for v in M_floats if v is not None]
    M_spread = (max(M_finite) - min(M_finite)) if M_finite else 0.0
    band_status_per_dps = [
        ("in_band" if (v is not None and 1.001 <= v <= 1.18)
         else "out_of_band" if v is not None
         else "no_value")
        for v in M_floats
    ]
    verdict_oscillates = len(set(band_status_per_dps)) > 1

    return {
        "lane": "7_precision_gradient_third_borderline",
        "coeffs_ascending": coeffs_ascending,
        "dps_ladder": dps_ladder,
        "results": results,
        "M_values_at_each_dps": M_floats,
        "M_spread": M_spread,
        "converged_to_constant": len(set(M_finite)) <= 1 if M_finite else False,
        "band_status_at_each_dps": band_status_per_dps,
        "verdict_oscillates": verdict_oscillates,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 17,
        "lanes": [3, 7],
        "lane_3": lane_3_p0_escalation_probe(),
        "lane_7": lane_7_third_borderline(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_17_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 3: {summary['lane_3']['verdict_counts']}")
    if summary['lane_3'].get('escalation_disposition'):
        print(f"  disposition: {summary['lane_3']['escalation_disposition']}")
    l7 = summary['lane_7']
    print(f"Lane 7: M_spread={l7['M_spread']:.6f}, converged={l7['converged_to_constant']}, oscillates={l7['verdict_oscillates']}")
    print(f"  M values: {l7['M_values_at_each_dps']}")
    return summary


if __name__ == "__main__":
    run()
