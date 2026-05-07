"""
Substrate-Tester Fire #16 — Lane 8 (ExclusionCertificate-extension regression)
+ Lane 13 (canonicalization-fuzz with fresh hypothesis seed).

Coordination: parallel substrate-tester instance ran fire #15 (commit
38ddf5b6, lanes 17 + 3). My fire = #16, lanes 8 + 13.

Lane 8 priority: regression on the COMPLETE-strength + triangulation_history
hard rule across the contract-change-window restart. Last covered fire #3
(direct lane probe) and fire #14 P1 (positive-direction adversarial test).
Verifies discipline holds with fresh substrate state and the prototype
Lehmer cert.

Lane 13 priority: re-run fuzzer with a NEW hypothesis seed (different from
fire #10's 20260507 and fire #13's seed) to expand explored input region.
Per lane spec: "the fuzz domain expands as Hypothesis explores."

Author: substrate-tester (Charon-aligned), fire #16, 2026-05-07
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 8 — ExclusionCertificate-extension regression
# ---------------------------------------------------------------------------


def lane_8_exclusion_certificate_regression() -> dict:
    """Regression check on cert primitive discipline post-restart.

    Tests:
      T1: prototype Lehmer cert still loads with COMPLETE strength + 4-path
          triangulation_history.
      T2: substrate refuses to construct COMPLETE cert with empty
          triangulation_history (fire-#14 P1 regression).
      T3: certificates_for_chart returns the registered Lehmer cert by chart_id.
      T4: distinct cert ids for distinct contents (no hash collision).
      T5: candidate inside cert scope still routes via DiscoveryPipeline normally
          (no cert-aware short-circuit) — fire-#3 finding regression.
    """
    from sigma_kernel.exclusion_certificate import (
        ExclusionCertificate, RegionSpec, ExclusionClaim,
        CertificateType, CertificateStrength, VerifierSet,
        ReplayInfo, Boundary,
        certificates_for_chart, get_certificate,
    )
    # Side-effect import: registers the prototype Lehmer cert
    from sigma_kernel.exclusion_certificates.lehmer_deg14 import (
        LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION as CERT,
    )

    tests = []

    # T1: cert is COMPLETE with non-empty triangulation_history
    if (
        CERT.strength == CertificateStrength.COMPLETE
        and len(CERT.triangulation_history) >= 2
    ):
        tests.append({
            "id": "T1_lehmer_cert_complete_with_triangulation",
            "expected": "strength=COMPLETE AND triangulation_history non-empty",
            "actual": f"strength={CERT.strength.name}, triangulation_paths={len(CERT.triangulation_history)}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T1_lehmer_cert_complete_with_triangulation",
            "expected": "strength=COMPLETE with non-empty triangulation_history",
            "actual": f"strength={CERT.strength.name}, paths={len(CERT.triangulation_history)}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })

    # T2: empty triangulation_history with COMPLETE strength must raise
    try:
        bad_cert = ExclusionCertificate(
            region_spec=RegionSpec(
                coordinate_chart_id="adversarial:fire16:t2",
                constraints={"degree": 14},
                bounds={"n_polynomials_enumerated": 1},
            ),
            exclusion_claim=ExclusionClaim(
                excluded_property="t2",
                result_class="adversarial",
                reason="t2 empty-triangulation regression check",
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
            "id": "T2_empty_triangulation_complete_rejected",
            "expected": "ValueError raised (Aporia v2.3 hard rule)",
            "actual": "silently constructed",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except (ValueError, AssertionError) as exc:
        tests.append({
            "id": "T2_empty_triangulation_complete_rejected",
            "expected": "ValueError raised",
            "actual": f"ValueError: {str(exc)[:140]}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        tests.append({
            "id": "T2_empty_triangulation_complete_rejected",
            "expected": "ValueError raised",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # T3: certificates_for_chart returns the registered cert
    chart_certs = certificates_for_chart("lehmer:deg14:pm5:palindromic")
    if any(c.region_spec.coordinate_chart_id == "lehmer:deg14:pm5:palindromic" for c in chart_certs):
        tests.append({
            "id": "T3_cert_lookup_by_chart",
            "expected": "Lehmer cert resolvable via certificates_for_chart",
            "actual": f"{len(chart_certs)} cert(s) registered for chart_id=lehmer:deg14:pm5:palindromic",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T3_cert_lookup_by_chart",
            "expected": "registered Lehmer cert returned",
            "actual": f"{len(chart_certs)} cert(s); none match expected chart_id",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # T4: distinct cert ids for distinct contents
    # Construct two minimal certs that differ only in excluded_property
    def _mk_diag_cert(prop: str) -> ExclusionCertificate:
        return ExclusionCertificate(
            region_spec=RegionSpec(
                coordinate_chart_id=f"adversarial:fire16:t4:{prop}",
                constraints={"degree": 14},
                bounds={"n_polynomials_enumerated": 1},
            ),
            exclusion_claim=ExclusionClaim(
                excluded_property=prop,
                result_class="diagnostic",
                reason="t4 hash distinctness",
            ),
            certificate_type=CertificateType.FAILED_SEARCH_ONLY,
            strength=CertificateStrength.DIAGNOSTIC_ONLY,
            verifier_set=VerifierSet(methods=(), independence_classes=frozenset()),
            replay=ReplayInfo(code_hash="x"*64, data_hash="y"*64, seed=0, environment_hash="z"*64),
            triangulation_history=(),
            initial_verdict="diag",
            upgrade_path_summary=(),
            boundary=Boundary(adjacent_regions=(), known_escape_hatches=()),
        )
    c1 = _mk_diag_cert("alpha")
    c2 = _mk_diag_cert("beta")
    if c1.certificate_id != c2.certificate_id:
        tests.append({
            "id": "T4_distinct_content_distinct_cert_id",
            "expected": "distinct contents yield distinct certificate_ids",
            "actual": f"c1.id={c1.certificate_id[:16]}..., c2.id={c2.certificate_id[:16]}...",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T4_distinct_content_distinct_cert_id",
            "expected": "distinct cert_ids",
            "actual": f"COLLISION: both {c1.certificate_id[:16]}...",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })

    # T5: in-scope candidate routes via normal pipeline (no cert short-circuit)
    from prometheus_math.discovery_pipeline import DiscoveryPipeline
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval_v2 import BindEvalExtension
    import numpy as np

    # Construct a deg-14 ±5 palindromic candidate with M out-of-band (cheap)
    novel_half = [1, 1, -2, 3, -3, 2, -1, 0]
    coeffs = novel_half + list(reversed(novel_half[:-1]))
    leading = abs(coeffs[-1]) if coeffs[-1] != 0 else 1
    M = float(leading)
    for r in np.roots(list(reversed(coeffs))):
        if abs(r) > 1.0:
            M *= abs(r)
    kernel = SigmaKernel()
    ext = BindEvalExtension(kernel)
    pipe = DiscoveryPipeline(kernel=kernel, ext=ext)
    rec = pipe.process_candidate(coeffs=coeffs, mahler_measure=M)
    kp = rec.kill_pattern or ""
    cert_referenced = "certificate" in kp.lower() or "exclusion_zone" in kp.lower()
    if not cert_referenced:
        tests.append({
            "id": "T5_in_scope_candidate_no_cert_shortcut",
            "expected": "candidate routes via normal pipeline",
            "actual": f"M={M:.4f}, terminal_state={rec.terminal_state}, kill_pattern={kp[:80]!r}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T5_in_scope_candidate_no_cert_shortcut",
            "expected": "no cert reference in kill_pattern",
            "actual": f"kill_pattern={kp[:120]!r} references certificate",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })

    return {
        "lane": "8_exclusion_certificate_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 13 — canonicalization-fuzz with fresh hypothesis seed
# ---------------------------------------------------------------------------


def lane_13_canonicalization_fuzz_fresh_seed() -> dict:
    """Re-run fuzzer with a hypothesis seed not used by fire #10 or #13."""
    test_path = REPO / "prometheus_math" / "tests" / "test_canonicalization_fuzz.py"
    if not test_path.exists():
        return {
            "lane": "13_canonicalization_fuzz",
            "status": "DORMANT",
            "reason": f"test file missing: {test_path}",
        }

    seed = "20260514"  # fresh seed (fire #10 used 20260507)
    t0 = time.time()
    proc = subprocess.run(
        [
            "python", "-m", "pytest", str(test_path),
            "--hypothesis-show-statistics",
            f"--hypothesis-seed={seed}",
            "-v", "--tb=short",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
        env={"PYTHONPATH": str(REPO), **os.environ},
    )
    elapsed = time.time() - t0

    stdout = proc.stdout
    test_lines = [l for l in stdout.splitlines() if " PASSED" in l or " FAILED" in l]
    n_passed = sum(1 for l in test_lines if " PASSED" in l)
    n_failed = sum(1 for l in test_lines if " FAILED" in l)

    summary_line = ""
    for line in stdout.splitlines():
        if ("passed" in line or "failed" in line) and "==" in line:
            summary_line = line.strip("=").strip()

    tests = []
    if proc.returncode == 0 and n_passed > 0 and n_failed == 0:
        tests.append({
            "id": "T1_fuzzer_clean_run_fresh_seed",
            "expected": "all 13 property tests pass with new seed",
            "actual": f"{n_passed} passed / 0 failed in {elapsed:.1f}s; summary: {summary_line!r}",
            "verdict": "PASS",
            "severity": None,
            "note": (
                f"Fresh hypothesis seed={seed}. Lane 13 has now run with seeds "
                "20260507 (fire #10) + parallel-instance-seed (fire #13) + "
                f"{seed} (fire #16). Each seed explores different input regions."
            ),
        })
    elif n_failed > 0:
        tests.append({
            "id": "T1_fuzzer_clean_run_fresh_seed",
            "expected": "all property tests pass",
            "actual": f"{n_passed} passed / {n_failed} FAILED",
            "verdict": "FAIL",
            "severity": "P1-high",
            "note": "Hypothesis property failure detected — substrate-grade canonicalization invariance violation.",
        })
    else:
        tests.append({
            "id": "T1_fuzzer_clean_run_fresh_seed",
            "expected": "fuzzer runs to completion",
            "actual": f"rc={proc.returncode}; n_passed={n_passed}; n_failed={n_failed}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    return {
        "lane": "13_canonicalization_fuzz",
        "status": "LIVE",
        "hypothesis_seed": seed,
        "wall_clock_seconds": elapsed,
        "rc": proc.returncode,
        "n_passed": n_passed,
        "n_failed": n_failed,
        "summary_line": summary_line,
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

    print("=== Substrate-Tester Fire #16 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 8: ExclusionCertificate-extension regression ---")
    lane8 = lane_8_exclusion_certificate_regression()
    print(f"Tests: {lane8['n_tests']}, verdicts: {lane8['verdict_counts']}")
    for t in lane8["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    print("\n--- Lane 13: canonicalization-fuzz fresh seed ---")
    lane13 = lane_13_canonicalization_fuzz_fresh_seed()
    print(f"Status: {lane13.get('status')}, verdicts: {lane13.get('verdict_counts')}")
    for t in lane13.get("tests", []):
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    summary = {
        "fire_id": "fire_16_2026_05_07",
        "lanes": ["8_exclusion_certificate_regression", "13_canonicalization_fuzz"],
        "lane_8": lane8,
        "lane_13": lane13,
    }
    out_path = out_dir / "substrate_tester_fire_16_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
