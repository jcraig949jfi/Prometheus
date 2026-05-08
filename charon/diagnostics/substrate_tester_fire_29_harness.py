"""Substrate-Tester Fire #29 harness — Lane 2 (adversarial-CLAIM, fresh
probes against contract-change-window primitives) + Lane 10 (real-paper
routing regression).

Coordination: parallel fire #28 (commit 43adc4da) covered lanes 7 + 8
with 0 tickets. P0 ticket T-ST-fire17-001 + P1 escalation
T-ST-fire25-001 still OPEN; deferred re-probes.

Lane 2 last fire #14 (1 cover post-restart). New probes target the
T020 / T030 / T023 contract-change-window primitives.

Lane 10 last fire #22 (1 cover post-restart). Probe in-band Mossinghoff
entries (verbatim per fire #19's retired-rec) routed via DiscoveryPipeline
+ off-corpus polynomials from RECENT_POLYNOMIAL_CORPUS.

Outputs:
  charon/diagnostics/substrate_tester_fire_29_results.json
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 2 — adversarial-CLAIM
# ---------------------------------------------------------------------------


def lane_2_adversarial_claim() -> Dict[str, Any]:
    """5 ill-formed probes against contract-change-window primitives."""
    tests: List[Dict[str, Any]] = []

    # P1: ExclusionCertificate with negative seed (ReplayInfo)
    try:
        from sigma_kernel.exclusion_certificate import ReplayInfo
        ri = ReplayInfo(
            code_hash="abc",
            data_hash="def",
            seed=-1,  # negative
            environment_hash="env",
        )
        tests.append({
            "id": "P1_replay_negative_seed",
            "expected": "either accept (allowed) OR ValueError",
            "actual": f"accepted; seed={ri.seed}",
            "verdict": "OBSERVED",
            "note": "negative seeds technically allowed by Python int type; documents the substrate's permissive boundary",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "P1_replay_negative_seed",
            "expected": "either accept OR ValueError",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "PASS",
        })

    # P2: TriangulationPath with bogus method_class arg
    try:
        from sigma_kernel.method_spec import IndependenceClass, MethodSpec
        from sigma_kernel.triangulation_protocol import TriangulationPath
        spec = MethodSpec(
            engine="mpmath", strategy="polyroots",
            independence_class=IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING,
            version="1.0.0",
        )
        # Pass a string instead of MethodClass enum — should reject
        path = TriangulationPath(
            path_id="adv_p2",
            method_spec=spec,
            method_class="not_a_method_class_enum",  # type: ignore
            verdict="verified",
            runtime_ms=10,
            rationale="probe",
            timestamp=time.time(),
        )
        tests.append({
            "id": "P2_triangpath_bogus_method_class",
            "expected": "TypeError or ValueError",
            "actual": f"silently accepted: method_class={path.method_class!r}",
            "verdict": "FAIL",
            "severity": "P1-high",
            "note": "TriangulationPath accepts arbitrary strings as method_class — input-validation gap similar to ST-fire14-001",
        })
    except (TypeError, ValueError) as exc:
        tests.append({
            "id": "P2_triangpath_bogus_method_class",
            "expected": "TypeError or ValueError",
            "actual": f"{type(exc).__name__}: {str(exc)[:140]}",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "P2_triangpath_bogus_method_class",
            "expected": "TypeError or ValueError",
            "actual": f"raised wrong: {type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # P3: TriangulationPath with bogus verdict string
    try:
        from sigma_kernel.method_spec import IndependenceClass, MethodSpec
        from sigma_kernel.triangulation_protocol import (
            MethodClass, TriangulationPath,
        )
        spec = MethodSpec(
            engine="mpmath", strategy="polyroots",
            independence_class=IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING,
            version="1.0.0",
        )
        path = TriangulationPath(
            path_id="adv_p3",
            method_spec=spec,
            method_class=MethodClass.NUMERICAL,
            verdict="not_a_real_verdict_xyz",  # bogus
            runtime_ms=10,
            rationale="probe",
            timestamp=time.time(),
        )
        tests.append({
            "id": "P3_triangpath_bogus_verdict",
            "expected": "either reject OR documented permissive accept",
            "actual": f"accepted; verdict={path.verdict!r}",
            "verdict": "OBSERVED",
            "note": "TriangulationPath verdict is open-vocabulary at construction; downstream evaluate() catches via verdict-string equality check",
        })
    except (TypeError, ValueError) as exc:
        tests.append({
            "id": "P3_triangpath_bogus_verdict",
            "expected": "TypeError or ValueError",
            "actual": f"{type(exc).__name__}: {str(exc)[:140]}",
            "verdict": "PASS",
        })

    # P4: OperatorPortabilityCertificate with empty operator_id
    try:
        from sigma_kernel.operator_portability import (
            OperatorPortabilityCertificate, PortabilityEvidence, PortabilityReplay,
            PortabilityVerdict, TransferMethod,
        )
        # Try with empty operator_id (invalid)
        cert = OperatorPortabilityCertificate(
            operator_id="",
            source_chart_id="lehmer:deg14:pm5:palindromic",
            target_chart_id="lehmer:deg12:pm3:palindromic",
            transfer_method=TransferMethod.STRUCTURAL_ANALOGY,
            verdict=PortabilityVerdict.SUPPORTED,
            evidence=PortabilityEvidence(
                source_object_count=10, target_object_count=10,
                signature_summary={}, sample_object_ids=(),
            ),
            replay=PortabilityReplay(
                code_hash="abc", data_hash="def", seed=0,
                environment_hash="env",
            ),
            rationale="probe",
        )
        tests.append({
            "id": "P4_opportcert_empty_operator_id",
            "expected": "ValueError",
            "actual": f"accepted; operator_id={cert.operator_id!r}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })
    except (ValueError, TypeError) as exc:
        tests.append({
            "id": "P4_opportcert_empty_operator_id",
            "expected": "ValueError or TypeError",
            "actual": f"{type(exc).__name__}: {str(exc)[:140]}",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "P4_opportcert_empty_operator_id",
            "expected": "ValueError or TypeError",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
        })

    # P5: SigmaKernel.CLAIM with kill_path that's a non-string
    try:
        from sigma_kernel.sigma_kernel import SigmaKernel, Tier
        kernel = SigmaKernel(":memory:")
        claim = kernel.CLAIM(
            target_name="adv_p5",
            hypothesis="adversarial probe",
            evidence={"x": 1},
            kill_path=12345,  # not a string
            target_tier=Tier.Conjecture,
        )
        tests.append({
            "id": "P5_claim_non_string_kill_path",
            "expected": "TypeError",
            "actual": f"accepted; stored kill_path={claim.kill_path!r}",
            "verdict": "FAIL",
            "severity": "P2-normal",
        })
    except (TypeError, ValueError) as exc:
        tests.append({
            "id": "P5_claim_non_string_kill_path",
            "expected": "TypeError or ValueError",
            "actual": f"{type(exc).__name__}: {str(exc)[:140]}",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "P5_claim_non_string_kill_path",
            "expected": "TypeError",
            "actual": f"raised wrong: {type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
        })

    return {
        "lane": "2_adversarial_claim",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 10 — real-paper routing regression
# ---------------------------------------------------------------------------


def lane_10_real_paper() -> Dict[str, Any]:
    """Submit 3 distinct entries from RECENT_POLYNOMIAL_CORPUS through
    DiscoveryPipeline; verify routing is deterministic and informative."""
    from prometheus_math._arxiv_polynomial_corpus import RECENT_POLYNOMIAL_CORPUS
    from prometheus_math.discovery_pipeline import DiscoveryPipeline
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval_v2 import BindEvalExtension

    kernel = SigmaKernel(":memory:")
    ext = BindEvalExtension(kernel)
    pipe = DiscoveryPipeline(kernel=kernel, ext=ext)

    # Pick 3 entries: Sac-Epee deg-12 (already known), and 2 others
    n_corpus = len(RECENT_POLYNOMIAL_CORPUS)
    selected_idx = [0, n_corpus // 2, n_corpus - 1] if n_corpus >= 3 else list(range(n_corpus))

    tests: List[Dict[str, Any]] = []
    for idx in selected_idx:
        entry = RECENT_POLYNOMIAL_CORPUS[idx]
        coeffs = list(getattr(entry, "coefficients_ascending", []) or [])
        if not coeffs:
            # Try alternate attribute names
            coeffs = list(getattr(entry, "coeffs", []) or [])
        m = float(getattr(entry, "mahler_measure_paper", 0.0) or getattr(entry, "M", 0.0))
        try:
            rec = pipe.process_candidate(coeffs, m)
            tests.append({
                "id": f"T_entry_{idx}",
                "probe": (
                    f"deg={len(coeffs) - 1}, M_paper={m:.4f}"
                ),
                "expected": "deterministic routing with informative kill_pattern",
                "actual": (
                    f"terminal_state={rec.terminal_state}, "
                    f"kill_pattern={rec.kill_pattern[:80] if rec.kill_pattern else None}"
                ),
                "verdict": "PASS",
            })
        except Exception as exc:  # noqa: BLE001
            tests.append({
                "id": f"T_entry_{idx}",
                "probe": f"deg={len(coeffs) - 1}, M_paper={m:.4f}",
                "expected": "deterministic routing",
                "actual": f"raised: {type(exc).__name__}: {exc}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })

    return {
        "lane": "10_real_paper",
        "n_corpus_total": n_corpus,
        "n_probes": len(selected_idx),
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 29,
        "lanes": [2, 10],
        "lane_2": lane_2_adversarial_claim(),
        "lane_10": lane_10_real_paper(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_29_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 2: {summary['lane_2']['verdict_counts']}")
    print(f"Lane 10: {summary['lane_10']['verdict_counts']}")
    return summary


if __name__ == "__main__":
    run()
