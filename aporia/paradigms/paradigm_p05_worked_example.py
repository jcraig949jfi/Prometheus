"""PARADIGM-P05 worked example — Analytic Continuation, executed.

The paradigm's move: extend a function beyond its natural domain; the extended
values carry global structure invisible in the defining series. Two legs, each
verified through INDEPENDENT computational paths (assume-wrong: agreement of
independent instruments is the certificate; no value is asserted from memory):

  A. CONTINUATION VALUES: zeta(-(2k-1)) for k=1..8 via mp.zeta (Euler-Maclaurin
     / Riemann-Siegel machinery) vs the Bernoulli formula -B_{2k}/(2k) via
     mp.bernoulli (a separate recurrence-based code path). The defining series
     sum n^{-s} DIVERGES at every one of these points — the values exist only
     through continuation, and two unrelated algorithms must land on them
     identically.
  B. LOCAL-TO-GLOBAL GLUE: partial Euler products prod_{p<=X}(1-p^-2)^-1
     (over sieved primes, nt_helpers) converge to the continued object's
     value zeta(2) = pi^2/6 computed independently from mp.pi.

Pre-stated readings (BEFORE run):
  CONTINUATION-EXACT  leg A: all 8 values agree to 25 significant digits;
                      leg B: |partial/target - 1| decreasing in X and < 1e-7
                      at X=1e7 (tail ~ 1/(X log X) scale, reported raw).
  PATH-DISAGREEMENT   any leg fails — instrument-first: dps discipline,
                      Bernoulli indexing (B_1 sign conventions), product
                      log-space accumulation.
"""
from __future__ import annotations
import json
import pathlib
import sys

import mpmath as mp
import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p05_results.json"
sys.path.insert(0, str(HERE.parent / "catalog_attacks"))
from nt_helpers import sieve_primes

mp.mp.dps = 30

# --- A: continuation values via two independent paths ------------------------
legA = []
worst = 0.0
for k in range(1, 9):
    s_point = -(2 * k - 1)
    via_zeta = mp.zeta(s_point)
    via_bernoulli = -mp.bernoulli(2 * k) / (2 * k)
    rel = float(abs(via_zeta - via_bernoulli) / abs(via_bernoulli))
    worst = max(worst, rel)
    legA.append({"s": s_point, "zeta_path": mp.nstr(via_zeta, 20),
                 "bernoulli_path": mp.nstr(via_bernoulli, 20), "rel_diff": rel})
    print(f"zeta({s_point}) = {mp.nstr(via_zeta, 12)}  vs  -B_{2*k}/{2*k} = "
          f"{mp.nstr(via_bernoulli, 12)}  rel {rel:.1e}", flush=True)
legA_ok = worst < 1e-25

# --- B: partial Euler products glue to the continued value -------------------
target = float(mp.pi ** 2 / 6)
primes = sieve_primes(10_000_000).astype(np.float64)
legB = []
prev = None
monotone = True
for X in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7):
    pp = primes[primes <= X]
    log_prod = -np.sum(np.log1p(-1.0 / pp ** 2))
    val = float(np.exp(log_prod))
    rel = abs(val / target - 1.0)
    if prev is not None and rel >= prev:
        monotone = False
    prev = rel
    legB.append({"X": X, "partial_product": val, "rel_to_pi2_6": rel})
    print(f"X={X:>9,}: prod={val:.12f}  |rel-1|={rel:.2e}", flush=True)
legB_ok = monotone and legB[-1]["rel_to_pi2_6"] < 1e-7

verdict = "CONTINUATION-EXACT" if (legA_ok and legB_ok) else "PATH-DISAGREEMENT"
print(f"legA worst rel {worst:.1e} ok={legA_ok}; legB monotone={monotone} "
      f"final {legB[-1]['rel_to_pi2_6']:.2e} ok={legB_ok} -> {verdict}", flush=True)

OUT.write_text(json.dumps({
    "protocol": "dual-path continuation certification (mp.zeta vs mp.bernoulli, 8 points, dps=30) + partial Euler products (nt_helpers sieve) gluing to pi^2/6",
    "legA": legA, "legA_worst_rel": worst,
    "legB": legB, "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
