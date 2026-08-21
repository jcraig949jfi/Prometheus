"""PARADIGM-P24 worked example — Quantitative Bound-Tightening, executed as a
COMPLETE toy pincer: Bertrand's postulate closed end-to-end.

The paradigm's move: an analytic argument works for n >= n0 (with n0 derived,
not assumed); computation closes [1, n0); the theorem falls to the pincer.
Executable instance — the Erdos machine for Bertrand (a prime in (n, 2n)):

  ANALYTIC LEG (threshold DERIVED in-code): if no prime lies in (n, 2n), then
  every prime factor of C(2n,n) is <= 2n/3 (Erdos's lemma: primes in
  (2n/3, n] do not divide C(2n,n) for n >= 3 — VERIFIED computationally on
  its finite range below), so
      C(2n,n) <= (2n)^sqrt(2n) * 4^(2n/3)
  (small primes p <= sqrt(2n): each contributes <= 2n; large primes appear
  to the first power and their product is <= the primorial bound 4^(2n/3),
  VERIFIED computationally on [1, 10^6] with the inductive general case
  cited). Against the lower bound C(2n,n) >= 4^n/(2n+1), the assumption
  fails once 4^(n/3) > (2n+1)(2n)^sqrt(2n) — the threshold n0 is COMPUTED
  as the largest n violating this (log arithmetic, exact comparisons).

  COMPUTATIONAL LEG: sieve to 2*n0; verify a prime in (n, 2n] for EVERY
  n <= n0 directly.

  PINCER: analytic for n > n0, computational for n <= n0 — Bertrand closed.

Gates: binomial lower bound verified exactly for n <= 500 (integer
arithmetic); the Erdos lemma verified by direct factorization for n <= 500;
the primorial bound verified to 1e6 with its induction cited as the analytic
content (honesty boundary stated in the artifact).

Pre-stated readings (BEFORE run):
  PINCER-CLOSES  all three finite-range gates exact; n0 lands in the
                 classical few-hundreds range; sieve leg 100% for n <= n0.
  PINCER-GAPS    instrument-first: log-inequality direction, lemma range
                 conventions, off-by-one at the threshold.
"""
from __future__ import annotations
import json
import math
import pathlib
import sys
from math import comb, isqrt

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p24_results.json"
sys.path.insert(0, str(HERE.parent / "catalog_attacks"))
from nt_helpers import sieve_primes

# --- gate 1: binomial lower bound, exact integers ----------------------------
for n in range(1, 501):
    assert comb(2 * n, n) * (2 * n + 1) >= 4 ** n, f"binom bound FAILS at {n}"
print("gate 1: C(2n,n) >= 4^n/(2n+1) exact for n <= 500 — PASS", flush=True)

# --- gate 2: Erdos lemma by direct factorization -----------------------------
primes_small = [int(p) for p in sieve_primes(1000)]
viol = []
for n in range(3, 501):
    c = comb(2 * n, n)
    for p in primes_small:
        if 2 * n / 3 < p <= n and c % p == 0:
            viol.append((n, p))
assert not viol, f"Erdos lemma FAILS: {viol[:5]}"
print("gate 2: primes in (2n/3, n] never divide C(2n,n), n in [3,500] — PASS", flush=True)

# --- gate 3: primorial bound to 1e6 ------------------------------------------
ps = sieve_primes(1_000_000).astype(float)
log_prim = 0.0
worst = 0.0
i = 0
import numpy as np
logs = np.log(ps)
cum = np.cumsum(logs)
ratio = cum / (ps * math.log(4))
worst = float(ratio.max())
assert worst <= 1.0, f"primorial bound FAILS: max ratio {worst}"
print(f"gate 3: prod(p<=x) <= 4^x verified to 1e6 (max log-ratio {worst:.4f}); "
      f"general case by induction — CITED as the analytic content", flush=True)

# --- derive n0: largest n with 4^(n/3) <= (2n+1)(2n)^sqrt(2n) ----------------
def assumption_survives(n):
    lhs = (n / 3) * math.log(4)
    rhs = math.log(2 * n + 1) + math.sqrt(2 * n) * math.log(2 * n)
    return lhs <= rhs

n0 = max(n for n in range(2, 20000) if assumption_survives(n))
assert not assumption_survives(n0 + 1) and all(not assumption_survives(m) for m in range(n0 + 1, n0 + 200))
print(f"analytic threshold DERIVED: n0 = {n0} (assumption self-destructs for all n > n0)", flush=True)

# --- computational leg: sieve closes [1, n0] ---------------------------------
P = set(int(p) for p in sieve_primes(2 * n0 + 10))
# convention flip caught at n=1: the postulate is n < p <= 2n (closed at 2n);
# the strict form excludes p=2 for n=1. Both conventions agree for n >= 2.
missing = [n for n in range(1, n0 + 1) if not any(n < p <= 2 * n for p in P)]
assert not missing, f"sieve leg FAILS at {missing[:5]}"
print(f"computational leg: a prime in (n, 2n] verified directly for EVERY n <= {n0} — PASS", flush=True)

verdict = "PINCER-CLOSES"
print(f"-> {verdict}: Bertrand's postulate closed by derived-analytic (n > {n0}) "
      f"+ computational (n <= {n0}) pincer", flush=True)
OUT.write_text(json.dumps({
    "protocol": "Erdos machine for Bertrand: three finite-range gates (binom bound exact n<=500; Erdos lemma by factorization n<=500; primorial bound to 1e6, induction cited), derived threshold n0, sieve closure below it",
    "n0_derived": n0, "primorial_max_log_ratio": worst,
    "verdict": verdict,
    "honesty_boundary": "the primorial bound's general case and the small-prime contribution bound rest on cited inductions verified here only on finite ranges — the pincer's ANALYTIC half is a faithful miniature, not a formal proof object; kernel-formalizing it is the P10-bind escalation"},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
