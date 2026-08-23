"""Calibration-library smoke test — known-truth checks on prometheus_math / techne.lib.

Why this exists. On 2026-08-12 this seat found the calibration library STRANDED: 29 of
222 modules importable, behind three missing packages. On 2026-08-23 James approved the
install and reachability went to 242/244. But reachability is a weak test -- the audit's
own weaknesses section said so:

    "I did not execute a single mathematical function against a known answer, so
     'the calibration library works' is NOT_EXAMINED, not SURVIVES."

This file closes that gap, and closes it permanently. Under ruling R1 mathematics is the
program's calibration standard -- "an instrument earns deployment on the reasoning
landscape by first passing on the math landscape, where it can be scored without
argument." A calibration standard that is never scored against known truth is a costume.

Every value below is independently known mathematics, not a value produced by this repo:

  * Lehmer's polynomial has the smallest known Mahler measure > 1: 1.17628081825991...
  * x^2 - x - 1 has Mahler measure phi = 1.61803398874989...
  * x^2 - 1 is a product of cyclotomics, so its Mahler measure is exactly 1.
  * h(Q(i)) = 1, h(Q(sqrt(-5))) = 2, h(Q(sqrt(-23))) = 3   (classical class numbers)

Exit code is non-zero on any failure, so this is usable as a gate.

Usage:
  PYTHONPATH=. python harmonia/diagnostics/calibration_library_smoke.py

Harmonia C, 2026-08-23.
"""

from __future__ import annotations

import sys

TOL = 1e-7

# (label, callable-name, args, expected, comparison)
CHECKS = []


def _register():
    from techne.lib.mahler_measure import mahler_measure, is_cyclotomic
    from techne.lib.class_number import class_number

    CHECKS.extend([
        ("Mahler M(Lehmer)", lambda: mahler_measure(
            [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]), 1.17628081825991, "approx"),
        ("Mahler M(x^2-x-1) = phi", lambda: mahler_measure([1, -1, -1]),
         1.61803398874989, "approx"),
        ("Mahler M(x^2-1) = 1", lambda: mahler_measure([1, 0, -1]), 1.0, "approx"),
        ("is_cyclotomic(x^2-1)", lambda: bool(is_cyclotomic([1, 0, -1])), True, "exact"),
        ("h(Q(i)) = 1", lambda: class_number([1, 0, 1]), 1, "exact"),
        ("h(Q(sqrt(-5))) = 2", lambda: class_number([1, 0, 5]), 2, "exact"),
        ("h(Q(sqrt(-23))) = 3", lambda: class_number([1, 0, 23]), 3, "exact"),
    ])


def main():
    print("Calibration-library smoke test (known-truth, external to this repo)")
    print("=" * 72)
    try:
        _register()
    except Exception as exc:  # noqa: BLE001 - the whole point is to report it
        print(f"FAIL: calibration library not importable: {type(exc).__name__}: {exc}")
        print("\nIf this is a missing optional dependency, run:")
        print("  python harmonia/diagnostics/dependency_door_audit.py "
              "--pkg prometheus_math --pkg techne.lib")
        return 2

    failures = 0
    for label, fn, expected, mode in CHECKS:
        try:
            got = fn()
        except Exception as exc:  # noqa: BLE001
            print(f"  {label:<28} ERROR  {type(exc).__name__}: {exc}")
            failures += 1
            continue
        ok = (got == expected) if mode == "exact" else abs(got - expected) < TOL
        shown = f"{got:.11f}" if mode == "approx" else str(got)
        exp = f"{expected:.11f}" if mode == "approx" else str(expected)
        print(f"  {label:<28} {shown:>16}  expected {exp:>16}  "
              f"{'PASS' if ok else 'FAIL'}")
        failures += (not ok)

    print("-" * 72)
    print(f"{len(CHECKS) - failures}/{len(CHECKS)} passed")
    if failures:
        print("The calibration standard does not reproduce known mathematics on this "
              "host. Nothing measured against it should be trusted until this is green.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
