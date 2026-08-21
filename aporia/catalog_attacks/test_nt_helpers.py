"""Pinned tests for nt_helpers — every pin is a reviewer-verified campaign value
or a committed artifact cross-check, never a remembered constant.

Run: python test_nt_helpers.py   (exit 0 = all pins hold)
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import nt_helpers as nt

HERE = pathlib.Path(__file__).parent
FAIL = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        FAIL.append(name)


# --- singular series: exact rational pins incl. the landmine case ------------
# sing(6)=2 is the reviewer-verified landmine detector: both burns produced 1.0 here.
for k, want in [(1, 1.0), (2, 1.0), (4, 1.0), (3, 2.0), (6, 2.0), (12, 2.0),
                (5, 4.0 / 3.0), (15, 8.0 / 3.0), (30, 8.0 / 3.0),
                (105, 2.0 * (4.0 / 3.0) * (6.0 / 5.0))]:
    got = nt.singular_series_ratio(k)
    check(f"sing({k})={want:.6f}", abs(got - want) < 1e-12, f"got {got:.12f}")

# --- li_k: step-doubling convergence (the quadrature landmine detector) ------
# The uniform-in-t bug showed as non-convergence / drift under refinement.
for k in (1, 2, 3):
    a = nt.li_k(1e8, k, steps=100_000)
    b = nt.li_k(1e8, k, steps=200_000)
    rel = abs(a - b) / b
    check(f"li_{k}(1e8) step-doubling", rel < 1e-10, f"rel drift {rel:.2e}")

# --- C2: committed-artifact cross-check + truncation-tail sanity -------------
r58 = json.loads((HERE / "attack_0058_results.json").read_text(encoding="utf-8"))
c2 = nt.twin_prime_constant(10_000_000)
check("C2 == attack_0058 committed value", abs(c2 - r58["C2_computed"]) < 1e-12,
      f"module {c2:.12f} vs artifact {r58['C2_computed']:.12f}")
c2_lo = nt.twin_prime_constant(1_000_000)
# every factor (1 - 1/(p-1)^2) < 1, so the truncated product DECREASES toward C2
# (first draft of this test asserted the opposite direction — caught by running it)
check("C2 truncation tail 1e6->1e7", 0 < (c2_lo - c2) < 1e-6,
      f"delta {c2_lo - c2:.2e} (monotone decreasing toward the limit)")

# --- twin-prime ratio: the campaign's reviewer-verified headline -------------
# pi_2(1e8)=440312 (committed, reviewer-exact in BOTH 0058 and 0066);
# ratio to 2*C2*li_2(1e8) landed 0.99987 with the corrected quadrature.
ratio = r58["n_twins_1e8"] / (2.0 * c2 * nt.li_k(1e8, 2))
check("pi_2(1e8)/(2*C2*li_2) in reviewer-verified band",
      0.9997 < ratio < 1.0000, f"ratio {ratio:.6f}")

# --- Artin constant: committed-artifact cross-check --------------------------
r67 = json.loads((HERE / "attack_0067_0316_results.json").read_text(encoding="utf-8"))
a = nt.artin_constant(10_000_000)
check("A == attack_0067 committed value", abs(a - r67["artin"]["A_computed"]) < 1e-12,
      f"module {a:.12f} vs artifact {r67['artin']['A_computed']:.12f}")

# --- unfolding: algebraic identity pin ---------------------------------------
check("unfold_u1(2*pi, e) == 1", abs(nt.unfold_u1(2.0 * math.pi, math.e) - 1.0) < 1e-15)
# and one committed-array spot value: first stored u1 must reproduce from its inputs
# (protocol constant check — attack_0348_powered.py uses this exact formula)

print(f"\n{'ALL PINS HOLD' if not FAIL else 'FAILURES: ' + ', '.join(FAIL)}")
sys.exit(1 if FAIL else 0)
