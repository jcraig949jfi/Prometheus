"""PARADIGM-P08 worked example — Probabilistic Method, executed.

The paradigm's move: prove an object EXISTS by showing a random construction
produces it with positive probability. Three legs, raw beside derived:

  A. DERIVED EXPECTATION: E[# monochromatic K_4] in a uniform 2-coloring of
     K_10 = C(10,4) * 2^(1-C(4,2)) = 210/32 = 6.5625 — derived from linearity,
     integer arithmetic in-code, no memory.
  B. MONTE CARLO MATCH: 20,000 sampled colorings; empirical mean must match
     the derived expectation within 3 standard errors (raw distribution
     printed beside the derived number — the P80 rule as a test).
  C. EXISTENCE MADE CONSTRUCTIVE: for K_8 and K_6-freeness the derived
     expectation is C(8,6)*2^(1-15) = 28/16384 ~ 0.0017 < 1, so colorings
     with NO monochromatic K_6 exist (the union-bound argument); sample until
     one is found (expected ~1 draw) and VERIFY it by exhaustive check over
     all C(8,6)=28 six-subsets. The witness is committed in the results file.

Pre-stated readings (BEFORE run):
  METHOD-DEMONSTRATED  |MC mean - 6.5625| < 3*SE  AND  a verified witness
                       found within 100 draws.
  MISMATCH             either leg fails — instrument-first: edge indexing,
                       subset enumeration, coloring encoding.
"""
from __future__ import annotations
import json
import pathlib
from itertools import combinations
from math import comb

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p08_results.json"
rng = np.random.default_rng(20260884)

# --- A: derived expectation ---------------------------------------------------
E_derived = comb(10, 4) * 2 ** (1 - comb(4, 2))     # 210 * 2^-5
E_exact = comb(10, 4) / 2 ** 5
print(f"A. derived E[mono K4 in K10] = C(10,4)*2^(1-6) = {E_exact} (= {comb(10,4)}/32)", flush=True)

# --- B: Monte Carlo -----------------------------------------------------------
n, k, trials = 10, 4, 20_000
edges = list(combinations(range(n), 2))
eidx = {e: i for i, e in enumerate(edges)}
subsets = list(combinations(range(n), k))
sub_edges = [[eidx[(a, b)] for a, b in combinations(s, 2)] for s in subsets]
counts = np.empty(trials)
for t in range(trials):
    col = rng.integers(0, 2, len(edges))
    c = 0
    for se in sub_edges:
        v = col[se]
        if v.all() or not v.any():
            c += 1
    counts[t] = c
mc_mean = counts.mean()
se = counts.std(ddof=1) / np.sqrt(trials)
z = abs(mc_mean - E_exact) / se
print(f"B. MC mean {mc_mean:.4f} vs derived {E_exact} (SE {se:.4f}, z={z:.2f}); "
      f"raw count distribution: {dict(zip(*np.unique(counts, return_counts=True)))}"[:300], flush=True)
legB_ok = z < 3

# --- C: existence made constructive ------------------------------------------
n2, k2 = 8, 6
E2 = comb(n2, k2) / 2 ** comb(k2, 2)
print(f"C. derived E[mono K6 in K8] = {comb(n2,k2)}/2^{comb(k2,2)} = {E2:.6f} < 1 -> existence", flush=True)
edges2 = list(combinations(range(n2), 2))
eidx2 = {e: i for i, e in enumerate(edges2)}
sub2 = [[eidx2[(a, b)] for a, b in combinations(s, 2)] for s in combinations(range(n2), k2)]
witness = None
draws = 0
while witness is None and draws < 100:
    draws += 1
    col = rng.integers(0, 2, len(edges2))
    if not any(col[se].all() or not col[se].any() for se in sub2):
        witness = col.tolist()
assert witness is not None, "no witness in 100 draws — instrument-first"
# independent exhaustive verification of the witness
w = np.array(witness)
mono = sum(1 for se in sub2 if w[se].all() or not w[se].any())
assert mono == 0, f"witness verification FAILED: {mono} mono K6s"
print(f"C. witness found on draw {draws}, verified exhaustively over all "
      f"{len(sub2)} six-subsets: 0 monochromatic", flush=True)

verdict = "METHOD-DEMONSTRATED" if (legB_ok and witness) else "MISMATCH"
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "derived expectation (linearity, exact) + 20k Monte Carlo (3SE gate) + constructive existence for (K8, K6-free) with exhaustive witness verification, seed 20260884",
    "E_derived_K10_K4": E_exact, "mc_mean": float(mc_mean), "mc_se": float(se),
    "z": float(z), "E_derived_K8_K6": E2, "witness_draws": draws,
    "witness_coloring": witness, "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
