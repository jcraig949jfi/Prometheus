"""Reproducible end-to-end verification script for Prometheus Verified Composition Sprints 1-5+.

Checks:
  1. Frozen `rso/` integrity (`git diff -- rso/` must be empty).
  2. Deterministic manifest SHA-256 reproducibility across all sprint benchmark suites.
  3. Full pytest suite across all `comp_sprint*` packages and frozen `rso/` adversarial/completeness tests.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def check_rso_unmodified() -> None:
    proc = subprocess.run(["git", "diff", "--stat", "--", "rso/"], cwd=ROOT, capture_output=True, text=True, check=True)
    if proc.stdout.strip():
        raise AssertionError(f"FROZEN rso/ WAS MODIFIED:\n{proc.stdout}")
    print("[PASS] Frozen rso/ integrity: 0 bytes modified")


def check_manifests() -> None:
    from comp_sprint2.s2a_benchmarks import build_s2a_benchmarks, s2a_manifest_sha256
    from comp_sprint2.s2b_benchmarks import build_s2b_benchmarks, s2b_manifest_sha256
    from comp_sprint2.s3a_benchmarks import build_s3a_benchmarks, s3a_manifest_sha256
    from comp_sprint2.s3b_benchmarks import build_s3b_benchmarks, s3b_manifest_sha256
    from comp_sprint3.s3_benchmarks import build_s3_benchmarks, s3_manifest_sha256
    from comp_sprint4.s4a_bv_benchmarks import build_s4a_bv_benchmarks, s4a_manifest_sha256
    from comp_sprint4.s4b_xag_benchmarks import build_s4b_xag_benchmarks, s4b_manifest_sha256
    from comp_sprint5_quantum.s5q_benchmarks import build_s5q_benchmarks, s5q_manifest_sha256
    from comp_sprint6_compound.s6_benchmarks import build_s6_benchmarks, s6_manifest_sha256
    from comp_sprint7_clifford_t.s7_benchmarks import build_s7_benchmarks, s7_manifest_sha256

    checks = [
        ("S2-A XAG", build_s2a_benchmarks, s2a_manifest_sha256),
        ("S2-B BV", build_s2b_benchmarks, s2b_manifest_sha256),
        ("S3-A XAG", build_s3a_benchmarks, s3a_manifest_sha256),
        ("S3-B BV", build_s3b_benchmarks, s3b_manifest_sha256),
        ("S3 Comp XAG", build_s3_benchmarks, s3_manifest_sha256),
        ("S4-A Det BV", build_s4a_bv_benchmarks, s4a_manifest_sha256),
        ("S4-B 9-11in XAG", build_s4b_xag_benchmarks, s4b_manifest_sha256),
        ("S5-Q Quantum CNOT", build_s5q_benchmarks, s5q_manifest_sha256),
        ("S6 Law4b XAG", build_s6_benchmarks, s6_manifest_sha256),
        ("S7 Clifford+T", build_s7_benchmarks, s7_manifest_sha256),
    ]
    for label, builder, hasher in checks:
        s1 = builder()
        s2 = builder()
        h1, h2 = hasher(s1), hasher(s2)
        assert h1 == h2, f"Non-deterministic manifest in {label}!"
        n = sum(len(v) for v in s1.values())
        print(f"[PASS] Manifest {label:18s}: {n:3d} tasks, sha256={h1[:16]}...")


def check_pytest() -> None:
    test_dirs = [
        "comp_sprint/tests",
        "comp_sprint2/tests",
        "comp_sprint3/tests",
        "comp_sprint4/tests",
        "comp_sprint5_quantum/tests",
        "rso/adversary/tests/test_attacks.py",
        "rso/adversary/tests/test_mutants.py",
        "rso/completeness/tests",
    ]
    for opt in ("comp_sprint6_compound/tests", "comp_sprint7_clifford_t/tests"):
        if (ROOT / opt).exists():
            test_dirs.append(opt)
    cmd = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q"] + test_dirs
    proc = subprocess.run(cmd, cwd=ROOT, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    print("[PASS] Full pytest verification passed!")


def main() -> None:
    check_rso_unmodified()
    check_manifests()
    check_pytest()
    print("\nALL PROMETHEUS VERIFIED COMPOSITION CHECKS PASSED.")


if __name__ == "__main__":
    main()
