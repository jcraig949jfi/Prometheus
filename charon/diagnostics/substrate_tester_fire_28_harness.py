"""
Substrate-Tester Fire #28 — Lane 7 (entries #6 + #7 of INCONCLUSIVE list)
+ Lane 8 (ExclusionCertificate regression).

Coordination: parallel substrate-tester ran fire #27 (commit 3552c650,
Lane 9 + Lane 5 deg-12 ±3 new combo). My fire = #28, lanes 7 + 8.

Lane 7 extends fires #1/#9/#18's cumulative INCONCLUSIVE-list characterization:
  fire #1: entry #0 half=[1,-4,5,0,-5,4,-1,0] -> M=1.0 (cyclotomic)
  fire #9: entry #1 half=[1,-3,1,5,-5,-1,3,-2] -> M=1.0 (cyclotomic)
  fire #18: entry #2 half=[1,-3,2,1,0,-2,1,0] -> M=1.17628 (Lehmer x cycl)
  fire #18: synthetic analog -> M=1.74 (Salem)
  fire #23 (parallel): entry #5 (Salem cluster)
  fire #28: entries #6 + #7 (this fire)

Entry #7 has M_numpy=1.176281 — predicted to extract Lehmer's polynomial
(same M-value as entry #2). Pattern verification.

Lane 8: fast regression on cert primitives — last my-instance fire #16.

Author: substrate-tester (Charon-aligned), fire #28, 2026-05-07
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


def lane_7_entries_6_7() -> dict:
    """Process entries #6 and #7 of the deg-14 ±5 INCONCLUSIVE list."""
    from prometheus_math.lehmer_path_a import high_precision_M_via_factor

    # 0-indexed entries from in_lehmer_band
    entries = [
        {
            "name": "entry_6",
            "half_coeffs": [1, -2, 0, 0, 2, 2, -3, 0],
            "M_numpy_quoted": 1.003249,
        },
        {
            "name": "entry_7",
            "half_coeffs": [1, -2, 1, 0, 0, -1, 1, 0],
            "M_numpy_quoted": 1.176281,  # Lehmer's M!
        },
    ]

    dps_ladder = [10, 30, 60, 100, 200]
    tests = []
    per_entry = {}

    for e in entries:
        half = e["half_coeffs"]
        # Build full palindrome: half + reversed(half[:-1])
        coeffs = half + list(reversed(half[:-1]))
        results = []
        for dps in dps_ladder:
            t0 = time.time()
            try:
                out = high_precision_M_via_factor(coeffs, nroots_precision=dps)
                elapsed = time.time() - t0
                M = out.get("M")
                results.append({
                    "dps": dps,
                    "elapsed_s": elapsed,
                    "M": float(M) if M == M else None,
                    "status": out.get("status"),
                    "precision_digits_recorded": out.get("precision_digits"),
                })
            except Exception as exc:
                results.append({"dps": dps, "exception": repr(exc)})

        valid_M = [r["M"] for r in results if r.get("M") is not None]
        M_max = max(valid_M) if valid_M else None
        M_min = min(valid_M) if valid_M else None
        spread = (M_max - M_min) if (M_max is not None and M_min is not None) else None

        # Classify outcome
        if M_min is None:
            outcome = "computation_failed"
        elif abs(M_min - 1.0) < 0.001:
            outcome = "pure_cyclotomic_M=1.0"
        elif abs(M_min - 1.17628) < 0.001:
            outcome = "lehmer_polynomial_extracted"
        elif M_min > 1.18:
            outcome = "salem_cluster"
        elif 1.001 < M_min < 1.18:
            outcome = "non_lehmer_in_band"
        else:
            outcome = f"unknown_M={M_min}"

        per_entry[e["name"]] = {
            "half_coeffs": half,
            "coeffs_ascending": coeffs,
            "M_numpy_quoted": e["M_numpy_quoted"],
            "results_per_dps": results,
            "M_max": M_max,
            "M_min": M_min,
            "M_spread": spread,
            "outcome": outcome,
        }

        # PASS criteria: clean convergence (spread < 0.001) + precision recorded
        all_recorded = all(
            r.get("precision_digits_recorded") is not None
            for r in results if "exception" not in r
        )
        if (
            M_min is not None and M_max is not None
            and (M_max - M_min) < 0.001
            and all_recorded
        ):
            tests.append({
                "id": f"T_{e['name']}_clean_convergence",
                "expected": "M converges across dps; precision recorded",
                "actual": f"M={M_min:.6f} (spread={spread:.6e}); outcome={outcome}",
                "verdict": "PASS",
                "severity": None,
            })
        else:
            tests.append({
                "id": f"T_{e['name']}_clean_convergence",
                "expected": "stable convergence",
                "actual": f"spread={spread}, outcome={outcome}, recorded={all_recorded}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })

    return {
        "lane": "7_entries_6_7",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
        "per_entry_results": per_entry,
    }


def lane_8_cert_regression_quick() -> dict:
    """Fast regression: 2 cert-primitive properties verified."""
    from sigma_kernel.exclusion_certificates.lehmer_deg14 import (
        LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION as CERT,
    )
    from sigma_kernel.exclusion_certificate import (
        ExclusionCertificate, RegionSpec, ExclusionClaim,
        CertificateType, CertificateStrength, VerifierSet,
        ReplayInfo, Boundary,
    )

    tests = []

    # T1: Lehmer cert COMPLETE with triangulation_history
    if (
        CERT.strength == CertificateStrength.COMPLETE
        and len(CERT.triangulation_history) >= 2
    ):
        tests.append({
            "id": "T1_lehmer_cert_complete",
            "expected": "strength=COMPLETE with non-empty triangulation_history",
            "actual": f"strength={CERT.strength.name}, paths={len(CERT.triangulation_history)}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T1_lehmer_cert_complete",
            "expected": "strength=COMPLETE with non-empty triangulation_history",
            "actual": f"strength={CERT.strength.name}, paths={len(CERT.triangulation_history)}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })

    # T2: empty triangulation_history with COMPLETE rejected
    try:
        bad = ExclusionCertificate(
            region_spec=RegionSpec(
                coordinate_chart_id="adversarial:fire28:t2",
                constraints={"degree": 14},
                bounds={"n_polynomials_enumerated": 1},
            ),
            exclusion_claim=ExclusionClaim(
                excluded_property="t2",
                result_class="adversarial",
                reason="t2",
            ),
            certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
            strength=CertificateStrength.COMPLETE,
            verifier_set=VerifierSet(methods=(), independence_classes=frozenset()),
            replay=ReplayInfo(code_hash="x"*64, data_hash="y"*64, seed=0, environment_hash="z"*64),
            triangulation_history=(),
            initial_verdict="t2",
            upgrade_path_summary=(),
            boundary=Boundary(adjacent_regions=(), known_escape_hatches=()),
        )
        tests.append({
            "id": "T2_empty_triangulation_rejected",
            "expected": "ValueError raised",
            "actual": "silently constructed",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except (ValueError, AssertionError) as exc:
        tests.append({
            "id": "T2_empty_triangulation_rejected",
            "expected": "ValueError raised",
            "actual": f"ValueError: {str(exc)[:100]}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        tests.append({
            "id": "T2_empty_triangulation_rejected",
            "expected": "ValueError raised",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    return {
        "lane": "8_cert_regression_quick",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #28 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 7: entries #6 + #7 of INCONCLUSIVE list ---")
    lane7 = lane_7_entries_6_7()
    print(f"Tests: {lane7['n_tests']}, verdicts: {lane7['verdict_counts']}")
    for t in lane7["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    print("\n--- Lane 8: cert regression ---")
    lane8 = lane_8_cert_regression_quick()
    print(f"Tests: {lane8['n_tests']}, verdicts: {lane8['verdict_counts']}")
    for t in lane8["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    summary = {
        "fire_id": "fire_28_2026_05_07",
        "lanes": ["7_entries_6_7", "8_cert_regression_quick"],
        "lane_7": lane7,
        "lane_8": lane8,
    }
    out_path = out_dir / "substrate_tester_fire_28_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
