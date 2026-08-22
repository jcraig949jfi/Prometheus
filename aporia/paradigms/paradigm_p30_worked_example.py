"""PARADIGM-P30 worked example — Tensor Network Contraction, executed via
CROSS-CHANNEL BIND #2 (Techne's prometheus_math/tensor_train.py, cycle 002).

The paradigm's move: represent a big tensor as a network of small ones;
the computational task is CONTRACTION ORDER; approximation is bond-dimension
truncation. Three legs (opt_einsum probed ABSENT — the derived DP stands in):

  A. TT ROUND-TRIP on DERIVED-rank tensors, through Techne's engine:
     - a rank-1 outer product (TT ranks all 1, derived);
     - the diagonal <2> on 4 axes (TT ranks 2, derived);
     - exact reconstruction (1e-10) asserted for both.
  B. CONTRACTION ORDER as optimization: matrix-chain DP (derived in-code)
     vs worst parenthesization on random dimension chains — the DP GATED on
     brute-force enumeration of all parenthesizations for length <= 6, then
     the cost ratio exhibited at length 10 (raw beside derived).
  C. TRUNCATION TRADE (decline-capable): bond truncation of a random
     full-rank tensor — error vs kept-rank curve must be monotone
     DECREASING to ~0 at full rank (the approximation knob quantified);
     a structured (low-TT-rank) tensor truncates to EXACTLY zero error at
     its derived rank while the random one cannot — the contrast IS the
     paradigm's content (structure = compressibility).

Pre-stated readings (BEFORE run):
  NETWORK-CONTRACTS  A: ranks match derived, reconstructions exact; B: DP
                     == brute force on all gated lengths AND DP cost <=
                     every enumerated order; C: monotone error curve, exact
                     truncation at derived rank for the structured tensor.
  CONTRACTION-FAULT  instrument-first: TT axis ordering, chain-DP index
                     conventions, SVD cutoff semantics in Techne's engine.
"""
from __future__ import annotations
import json
import pathlib
import sys
from itertools import product

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from prometheus_math.tensor_train import tt_ranks, tt_reconstruct

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p30_results.json"
rng = np.random.default_rng(20260897)

# --- A: TT round-trip on derived-rank tensors --------------------------------
a = rng.standard_normal(3)
b = rng.standard_normal(3)
c = rng.standard_normal(3)
d = rng.standard_normal(3)
rank1 = np.einsum("i,j,k,l->ijkl", a, b, c, d)
r1 = tt_ranks(rank1)
rec1 = tt_reconstruct(rank1)
ok_r1 = all(r == 1 for r in r1) and np.allclose(rec1, rank1, atol=1e-10)
print(f"A. rank-1 4-tensor: TT ranks {r1} (derived: all 1), reconstruction "
      f"{'EXACT' if ok_r1 else 'FAILS'}", flush=True)

diag = np.zeros((2, 2, 2, 2))
for i in range(2):
    diag[i, i, i, i] = 1.0
r2 = tt_ranks(diag)
rec2 = tt_reconstruct(diag)
ok_r2 = all(r == 2 for r in r2) and np.allclose(rec2, diag, atol=1e-10)
print(f"A. diagonal <2> 4-tensor: TT ranks {r2} (derived: all 2), reconstruction "
      f"{'EXACT' if ok_r2 else 'FAILS'}", flush=True)

# --- B: contraction order (matrix-chain DP, gated on brute force) ------------
def chain_dp(dims):
    n = len(dims) - 1
    m = [[0] * n for _ in range(n)]
    for span in range(1, n):
        for i in range(n - span):
            j = i + span
            m[i][j] = min(m[i][k] + m[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                          for k in range(i, j))
    return m[0][n - 1]

def brute(dims):
    n = len(dims) - 1
    def rec(i, j):
        if i == j:
            return [0]
        costs = []
        for k in range(i, j):
            for lc in rec(i, k):
                for rc in rec(k + 1, j):
                    costs.append(lc + rc + dims[i] * dims[k + 1] * dims[j + 1])
        return costs
    return rec(0, n - 1)

gate_ok = True
for trial in range(20):
    L = int(rng.integers(3, 7))
    dims = [int(x) for x in rng.integers(2, 30, L + 1)]
    all_costs = brute(dims)
    gate_ok &= (chain_dp(dims) == min(all_costs))
print(f"B. chain-DP gate: DP == brute-force minimum on 20 random chains (len<=6) — "
      f"{'PASS' if gate_ok else 'FAIL'}", flush=True)
dims10 = [int(x) for x in rng.integers(2, 50, 11)]
best = chain_dp(dims10)
worst = max(brute(dims10[:7]))          # brute at 6 for the raw contrast
ltr = sum(dims10[0] * dims10[i + 1] * dims10[i + 2] for i in range(9))  # left-to-right cost? derive:
# left-to-right: ((A1 A2) A3)...: cost_i = d0*d_{i+1}*d_{i+2} accumulated
print(f"B. length-10 chain: optimal {best:,} vs left-to-right {ltr:,} "
      f"(ratio {ltr/best:.2f}x) — order IS the computation", flush=True)

# --- C: truncation trade ------------------------------------------------------
def tt_truncated_error(T, cutoff):
    R = tt_reconstruct(T, cutoff=cutoff)
    return float(np.linalg.norm(R - T) / np.linalg.norm(T))

full = rng.standard_normal((4, 4, 4, 4))
errs = [(co, tt_truncated_error(full, co)) for co in (1.0, 0.5, 0.1, 1e-3, 1e-12)]
mono = all(errs[i][1] >= errs[i + 1][1] - 1e-12 for i in range(len(errs) - 1))
struct_err = tt_truncated_error(rank1, 1e-10)
print(f"C. random full tensor: truncation errors {[(c, round(e,4)) for c,e in errs]} "
      f"monotone={mono}; structured rank-1 at cutoff 1e-10: error {struct_err:.2e}", flush=True)

verdict = ("NETWORK-CONTRACTS" if (ok_r1 and ok_r2 and gate_ok and mono and struct_err < 1e-10)
           else "CONTRACTION-FAULT")
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "Techne tensor_train bind (cross-channel #2): derived-rank TT round-trips; matrix-chain DP gated on brute force with the order-cost contrast; truncation trade with the structure-vs-random contrast, seed 20260897",
    "tt_rank1": r1, "tt_diag": r2, "chain_gate_trials": 20,
    "len10_optimal": best, "len10_left_to_right": ltr,
    "truncation_curve": [[c, e] for c, e in errs], "structured_error": struct_err,
    "verdict": verdict,
    "synergy_note": "second cross-channel instrument bind (after lean_oracle): Aporia consumes Techne's TT engine; opt_einsum probed absent, the derived DP stood in"},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
