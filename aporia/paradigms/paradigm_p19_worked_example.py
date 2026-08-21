"""PARADIGM-P19 worked example — Cross-Region Operator Transport, executed.

The paradigm (definition recovered from report_10, the taxonomy carries only
the confirmation line): carry an OPERATOR from its home region to a foreign
region as a first-class act, with the calibration surviving — or failing —
measurably. Executable instance with a DERIVED decline constant:

  HOME REGION: integers. The PNT instrument pi(x) ~ x/ln x (li-based,
    nt_helpers) — calibrated on home data (pi(1e6), pi(1e7) via sieve).
  FOREIGN REGION: F_2[x]. The analog of primes is monic irreducibles; the
    TRUE count at degree n is the Gauss/Mobius formula
    N(n) = (1/n) sum_{d|n} mu(d) 2^(n/d)  — computed by definition AND
    cross-gated by brute-force factorization census for n <= 12 (two routes).
  CORRECT TRANSPORT: the measure must transport too — x <-> 2^n and
    ln x <-> n ln 2 give prediction 2^n/n. Ratio N(n)/(2^n/n) -> 1.
  NAIVE TRANSPORT (the decline leg, failure factor DERIVED IN ADVANCE):
    plugging x = 2^n into the home instrument x/ln x gives 2^n/(n ln 2) —
    over-predicting by 1/ln 2. In the ratio direction AS MEASURED
    (true/naive) the derived failure constant is ln 2 = 0.693147.
    DIRECTION LESSON (caught by the first run): the first draft derived the
    constant in the naive/true direction (1.4427) while the code measured
    true/naive — even decline constants need direction discipline; the
    magnitude was right, the orientation was not.

Pre-stated readings (BEFORE run):
  TRANSPORT-CALIBRATES  brute-force census == Mobius formula for all n <= 12
                        (exact); correct-transport ratio within 2% of 1 at
                        n = 20; naive-transport ratio within 2% of ln 2 =
                        0.693147 (direction: true/naive, as coded).
  TRANSPORT-BROKEN      instrument-first: polynomial factorization encoding,
                        Mobius indexing, the ln 2 constant's placement.
"""
from __future__ import annotations
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p19_results.json"
sys.path.insert(0, str(HERE.parent / "catalog_attacks"))
from nt_helpers import sieve_primes


def mobius(n):
    m, p, cnt = n, 2, 0
    while p * p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0:
                return 0
            cnt += 1
        p += 1
    if m > 1:
        cnt += 1
    return -1 if cnt % 2 else 1


def n_irreducibles(n):
    return sum(mobius(d) * 2 ** (n // d) for d in divisors(n)) // n


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


# --- brute-force census over F_2[x], n <= 12 (two-route gate) ----------------
def poly_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r

MAXN = 12
irred_census = {}
for n in range(1, MAXN + 1):
    count = 0
    for poly in range(1 << n, 1 << (n + 1)):        # monic degree-n as bitmask
        reducible = False
        for d in range(1, n // 2 + 1):              # any nontrivial divisor of
            for f in range(1 << d, 1 << (d + 1)):   # degree <= n/2 proves it
                rem = poly
                fd = f.bit_length() - 1
                while rem and rem.bit_length() - 1 >= fd:
                    rem ^= f << (rem.bit_length() - 1 - fd)
                if rem == 0:
                    reducible = True
                    break
            if reducible:
                break
        count += (not reducible)
    irred_census[n] = count

formula = {n: n_irreducibles(n) for n in range(1, MAXN + 1)}
match = all(irred_census[n] == formula[n] for n in irred_census)
print("n, census, Mobius formula:", flush=True)
for n in irred_census:
    print(f"  {n:2d}  {irred_census[n]:6d}  {formula[n]:6d}  "
          f"{'OK' if irred_census[n] == formula[n] else 'MISMATCH'}", flush=True)
assert match, "two-route gate FAILS — factorization or Mobius fault"

# --- transport ratios at n = 20 ----------------------------------------------
n = 20
true_n = n_irreducibles(n)
correct = true_n / (2 ** n / n)
naive = true_n / (2 ** n / (n * math.log(2)))
derived_fail = math.log(2)   # true/naive direction — see the direction lesson above
print(f"n=20: N={true_n:,}; correct-transport ratio {correct:.6f} (target 1); "
      f"naive ratio {naive:.6f} vs derived failure constant {derived_fail:.6f}", flush=True)

ok = (match and abs(correct - 1) < 0.02 and abs(naive - derived_fail) / derived_fail < 0.02)
verdict = "TRANSPORT-CALIBRATES" if ok else "TRANSPORT-BROKEN"
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "PNT instrument transported integers -> F_2[x]: Mobius formula cross-gated by brute factorization census (n<=12), correct measure-transport (2^n/n) vs naive transport with the DERIVED failure constant 1/ln2",
    "census_vs_formula": {str(k): [irred_census[k], formula[k]] for k in irred_census},
    "n20_true": true_n, "correct_ratio": correct, "naive_ratio": naive,
    "derived_failure_constant": derived_fail, "verdict": verdict},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
