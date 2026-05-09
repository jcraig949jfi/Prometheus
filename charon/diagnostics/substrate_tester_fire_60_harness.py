"""Substrate-Tester Fire #60 harness — Tier E RepresentationTheoreticInvariant.

5th of 5 meta-primitive test-suite stubs per Aporia ratification.
Closes the set begun in fires #47/#48/#58/#59.

Lane 1 — verify the Tier E stub collects + skips cleanly.
Lane 2 — verify ALL 5 meta-primitive stubs collect + skip cleanly
together (the 5-stub corpus integration check).
Lane 11 — canon-fuzz pytest fresh seed 20260509_04 (regression hygiene).

Outputs:
  charon/diagnostics/substrate_tester_fire_60_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


def lane_1_tier_E_stub() -> Dict[str, Any]:
    target = REPO / "sigma_kernel" / "tests" / "test_representation_theoretic_invariant_stub.py"
    if not target.exists():
        return {"lane": "1_tier_E_stub", "verdict": "FAIL", "reason": "stub file missing"}

    import sys as _sys
    proc = subprocess.run(
        [_sys.executable, "-m", "pytest", str(target), "-q", "--no-header"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " skipped" in line or " passed" in line or " failed" in line:
            summary_line = line.strip()

    text = target.read_text(encoding="utf-8")
    n_lines = text.count("\n")
    n_test_classes = text.count("class Test")
    n_test_methods = text.count("    def test_")

    return {
        "lane": "1_tier_E_stub",
        "target_path": str(target.relative_to(REPO)).replace("\\", "/"),
        "filed": True,
        "n_lines": n_lines,
        "n_test_classes": n_test_classes,
        "n_test_methods": n_test_methods,
        "pytest_collect_summary": summary_line,
        "pytest_returncode": proc.returncode,
        "design_coverage": [
            "TestPartitionContract (6): construction, validation, transpose involution, dominance order, content-addressed id",
            "TestIrreducibleRepresentationContract (4): lookup by partition, hook-length dimension formula, trivial rep, sign rep",
            "TestSymmetricFunctionContract (4): Schur basis, Hall inner product orthonormality, Littlewood-Richardson multiplication, omega involution",
            "TestPlethysmContract (2): construction, known small case s_2[s_2]=s_4+s_(2,2)",
            "TestKroneckerCoefficientContract (3): trivial, S_3 symmetry, non-negativity",
            "TestSchurPositivityCertificateContract (2): positive function passes, negative coefficient fails",
            "TestTierBTierEComposition (1): RepresentationTheoreticWitness consumes Tier E primitives (double-skipped)",
            "TestCatalogCoverageSmoke (2): Kronecker decision (#95), Foulkes setup (#98)",
        ],
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def lane_2_full_5_stub_corpus_integration() -> Dict[str, Any]:
    """Run all 5 meta-primitive stubs together; verify they all
    collect + skip cleanly. The 5-stub corpus integration check."""
    targets = [
        "sigma_kernel/tests/test_constructive_existence_witness_stub.py",  # B
        "sigma_kernel/tests/test_distribution_object_stub.py",             # D
        "sigma_kernel/tests/test_moment_polytope_stub.py",                 # C
        "sigma_kernel/tests/test_tensor_network_stub.py",                  # A
        "sigma_kernel/tests/test_representation_theoretic_invariant_stub.py",  # E (this fire)
    ]
    import sys as _sys
    proc = subprocess.run(
        [_sys.executable, "-m", "pytest"] + targets + ["-q", "--no-header"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " skipped" in line or " passed" in line or " failed" in line:
            summary_line = line.strip()
    return {
        "lane": "2_full_5_stub_corpus_integration",
        "n_stub_files": len(targets),
        "files": targets,
        "pytest_summary": summary_line,
        "pytest_returncode": proc.returncode,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def lane_11_canon_fuzz_smoke() -> Dict[str, Any]:
    seed = "20260509_04"
    import sys as _sys
    cmd = [
        _sys.executable, "-m", "pytest",
        "prometheus_math/tests/test_canonicalization_fuzz.py",
        "-q", "--no-header", "-x", f"--hypothesis-seed={seed}",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=240)
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " passed" in line or " failed" in line or " error" in line:
            summary_line = line.strip()
    return {
        "lane": "11_canon_fuzz_smoke", "seed": seed,
        "returncode": proc.returncode, "summary_line": summary_line,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 60,
        "posture": "Tier E test-suite stub (5th of 5 — CLOSES THE SET)",
        "lanes": [1, 2, 11],
        "lane_1": lane_1_tier_E_stub(),
        "lane_2": lane_2_full_5_stub_corpus_integration(),
        "lane_11": lane_11_canon_fuzz_smoke(),
        "stub_status_after_fire_60_COMPLETE_SET": {
            "Tier_A_TensorNetwork": "shipped fire #59 (15 tests)",
            "Tier_B_ConstructiveExistenceWitness_StructuredEquivalenceClass": "shipped fire #47 (21 tests)",
            "Tier_C_MomentPolytope_SecantVarietyEquation": "shipped fire #58 (17 tests)",
            "Tier_D_GenericityAlmostEverywhereCert": "shipped fire #48 (17 tests)",
            "Tier_E_RepresentationTheoreticInvariant": "shipped fire #60 (24 tests)",
            "total_stubbed_tests_for_techne": 94,
        },
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_60_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1 (Tier E stub): {summary['lane_1']['verdict']} - "
          f"{summary['lane_1']['n_test_classes']} classes, "
          f"{summary['lane_1']['n_test_methods']} tests, "
          f"{summary['lane_1']['pytest_collect_summary']}")
    print(f"Lane 2 (full 5-stub corpus): {summary['lane_2']['verdict']} - "
          f"{summary['lane_2']['pytest_summary']}")
    print(f"Lane 11: {summary['lane_11']['verdict']} ({summary['lane_11']['summary_line']})")
    print(f"5-STUB SET COMPLETE. Total stubbed contract tests for Techne pickup: 94.")
    return summary


if __name__ == "__main__":
    run()
