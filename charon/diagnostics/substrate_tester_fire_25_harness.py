"""Substrate-Tester Fire #25 harness — Lane 17 (mutation-testing on a
fresh frozen-dataclass-heavy target) + Lane 8 (ExclusionCertificate
regression).

Coordination: parallel fire #24 (commit 20fa34eb) covered lanes 16 + 4
with 0 tickets. P0 ticket T-ST-fire17-001 still OPEN; deferred re-probe.

Lane 17: probe substrate-wide hypothesis from ST-fire15-001
(@dataclass(frozen=True) frozen-ness untested across the codebase). Fire
#7 found gap on OperatorPortabilityCertificate (ST-fire1-001); fire #15
found gap on CoordinateChart (ST-fire15-001). This fire targets
sigma_kernel/exclusion_certificate.py — another frozen-dataclass-heavy
module. If a third independent gap surfaces on the same pattern, the
hypothesis is substrate-wide-confirmed and ticket priority should
escalate from P2 to P1.

Lane 8: regression on ExclusionCertificate cert-extension discipline
(last fires #8 + #11 + #16). Verifies the cert primitive contract holds
across continued substrate evolution.

Outputs:
  charon/diagnostics/substrate_tester_fire_25_results.json
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 17 — mutation-testing on exclusion_certificate.py
# ---------------------------------------------------------------------------


def lane_17_mutation_on_exclusion_cert() -> Dict[str, Any]:
    target = "sigma_kernel/exclusion_certificate.py"
    test_cmd = "python -m pytest sigma_kernel/test_exclusion_certificate.py -q --tb=no"
    max_mutations = 8

    t0 = time.time()
    proc = subprocess.run(
        [
            "python", "-m", "prometheus_math.mutation_testing",
            "--target", target,
            "--test-cmd", test_cmd,
            "--max-mutations", str(max_mutations),
            "--timeout", "60",
        ],
        cwd=str(REPO),
        capture_output=True, text=True, timeout=900,
        env={"PYTHONPATH": str(REPO), **os.environ},
    )
    elapsed = time.time() - t0

    progress_lines = [
        line for line in (proc.stderr or "").splitlines()
        if "[mutation" in line
    ]

    summary_line = ""
    score = None
    n_killed = n_survived = n_errored = n_skipped = 0
    for line in progress_lines:
        if "score=" in line:
            summary_line = line
            try:
                m = re.search(r"score=([\d.]+)", line)
                if m: score = float(m.group(1))
                m = re.search(r"killed=(\d+)", line)
                if m: n_killed = int(m.group(1))
                m = re.search(r"survived=(\d+)", line)
                if m: n_survived = int(m.group(1))
                m = re.search(r"errored=(\d+)", line)
                if m: n_errored = int(m.group(1))
                m = re.search(r"skipped=(\d+)", line)
                if m: n_skipped = int(m.group(1))
            except Exception:
                pass

    mutations: List[Dict[str, str]] = []
    for line in progress_lines:
        if "/" in line and "@" in line and "(" in line and "s)" in line:
            try:
                parts = line.split()
                idx_part = parts[1].rstrip("]")
                idx = idx_part.split("/")[0]
                verdict = parts[2]
                site = parts[4] if len(parts) > 4 else ""
                mutations.append({"idx": idx, "verdict": verdict, "site": site})
            except Exception:
                continue

    # Probe substrate-wide hypothesis: did a frozen-dataclass mutation survive?
    frozen_dataclass_survivor = None
    for m in mutations:
        if m["verdict"] == "survived" and "boolean_not" in m["site"]:
            # Heuristic: likely candidate; verify by reading the line
            line_no = int(m["site"].split(":")[1]) if ":" in m["site"] else 0
            if 0 < line_no:
                try:
                    src_text = (REPO / target).read_text(encoding="utf-8")
                    src_line = src_text.splitlines()[line_no - 1]
                    if "@dataclass(frozen=True)" in src_line:
                        frozen_dataclass_survivor = {
                            "site": m["site"],
                            "line_no": line_no,
                            "src_line": src_line.strip(),
                        }
                        break
                except Exception:
                    pass

    return {
        "lane": "17_mutation_on_exclusion_certificate",
        "target": target,
        "max_mutations_requested": max_mutations,
        "wall_clock_seconds": elapsed,
        "rc": proc.returncode,
        "summary_line": summary_line,
        "score": score,
        "n_killed": n_killed,
        "n_survived": n_survived,
        "n_errored": n_errored,
        "n_skipped": n_skipped,
        "mutations": mutations,
        "frozen_dataclass_survivor": frozen_dataclass_survivor,
        "stderr_tail": (proc.stderr or "")[-1500:] if proc.returncode != 0 else "",
    }


# ---------------------------------------------------------------------------
# Lane 8 — ExclusionCertificate-extension regression
# ---------------------------------------------------------------------------


def lane_8_cert_extension_regression() -> Dict[str, Any]:
    from sigma_kernel.exclusion_certificate import (
        Boundary, CertificateRegistry, CertificateRegistrationError,
        CertificateCollisionError, CertificateStrength, CertificateType,
        ExclusionCertificate, ExclusionClaim, RegionSpec,
        ReplayInfo, TriangulationPathRef, VerifierSet,
    )
    from sigma_kernel.method_spec import IndependenceClass, MethodSpec

    spec = MethodSpec(
        engine="mpmath", strategy="polyroots",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        version="1.0.0",
    )

    def _make_cert(chart_id: str, claim_label: str = "cl",
                   strength: CertificateStrength = CertificateStrength.BOUNDED_COMPLETE) -> ExclusionCertificate:
        return ExclusionCertificate(
            region_spec=RegionSpec(coordinate_chart_id=chart_id, constraints={}, bounds=None),
            exclusion_claim=ExclusionClaim(
                excluded_property=claim_label,
                result_class="lehmer_band",
                reason="exhaustive enumeration",
            ),
            certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
            strength=strength,
            verifier_set=VerifierSet(methods=(spec,)),
            replay=ReplayInfo(code_hash="abc", data_hash="def", seed=0, environment_hash="env"),
        )

    tests: List[Dict[str, Any]] = []

    reg = CertificateRegistry()
    cert_a = _make_cert("test:fire25:scope_a", "claim_a_fire25")

    # T1: register fresh cert
    try:
        reg.register(cert_a, require_chart=False)
        tests.append({
            "id": "T1_register_fresh",
            "expected": "registers cleanly",
            "actual": f"cid={cert_a.certificate_id[:16]}",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T1_register_fresh",
            "expected": "registers cleanly",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # T2: re-register => CollisionError (T020 contract)
    try:
        reg.register(cert_a, require_chart=False)
        tests.append({
            "id": "T2_collision_raises",
            "expected": "CertificateCollisionError",
            "actual": "silently registered",
            "verdict": "FAIL",
            "severity": "P1-high",
        })
    except CertificateCollisionError:
        tests.append({
            "id": "T2_collision_raises",
            "expected": "CertificateCollisionError",
            "actual": "raised CertificateCollisionError",
            "verdict": "PASS",
        })
    except CertificateRegistrationError:
        tests.append({
            "id": "T2_collision_raises",
            "expected": "CertificateCollisionError",
            "actual": "raised CertificateRegistrationError (subclass; backward compat)",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T2_collision_raises",
            "expected": "CertificateCollisionError",
            "actual": f"raised wrong: {type(exc).__name__}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # T3: COMPLETE without triangulation_history rejected (Aporia v2.3 hard rule)
    try:
        _ = _make_cert("test:fire25:scope_b", strength=CertificateStrength.COMPLETE)
        tests.append({
            "id": "T3_complete_requires_triangulation",
            "expected": "ValueError",
            "actual": "silently constructed",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })
    except ValueError:
        tests.append({
            "id": "T3_complete_requires_triangulation",
            "expected": "ValueError",
            "actual": "ValueError raised (Aporia v2.3 hard rule enforced)",
            "verdict": "PASS",
        })

    # T4: replace=True succeeds
    try:
        reg.register(cert_a, require_chart=False, replace=True)
        tests.append({
            "id": "T4_replace_true_succeeds",
            "expected": "replace=True overrides",
            "actual": "succeeds",
            "verdict": "PASS",
        })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T4_replace_true_succeeds",
            "expected": "replace=True overrides",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # T5: by_id lookup
    try:
        retrieved = reg.by_id(cert_a.certificate_id)
        if retrieved is not None and retrieved.certificate_id == cert_a.certificate_id:
            tests.append({
                "id": "T5_by_id_lookup",
                "expected": "lookup returns cert",
                "actual": f"retrieved cid={retrieved.certificate_id[:16]}",
                "verdict": "PASS",
            })
        else:
            tests.append({
                "id": "T5_by_id_lookup",
                "expected": "lookup returns cert",
                "actual": f"got None or wrong cert: {retrieved}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })
    except Exception as exc:  # noqa: BLE001
        tests.append({
            "id": "T5_by_id_lookup",
            "expected": "lookup works",
            "actual": f"raised: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    return {
        "lane": "8_cert_extension_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 25,
        "lanes": [17, 8],
        "lane_17": lane_17_mutation_on_exclusion_cert(),
        "lane_8": lane_8_cert_extension_regression(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_25_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    l17 = summary["lane_17"]
    print(f"Lane 17: score={l17['score']}, killed={l17['n_killed']}, survived={l17['n_survived']}")
    if l17.get("frozen_dataclass_survivor"):
        print(f"  FROZEN-DATACLASS SURVIVOR: {l17['frozen_dataclass_survivor']['src_line'][:80]}")
    print(f"Lane 8: {summary['lane_8']['verdict_counts']}")
    return summary


if __name__ == "__main__":
    run()
