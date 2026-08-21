"""PARADIGM-P13 worked example — Tropical / Degeneration Methods, executed.

The paradigm's move: replace smooth geometry with a piecewise-linear shadow at
the boundary; the degeneration remembers enough to reconstruct. Executable
instance at the paradigm's root: PUISEUX VALUATION DEGENERATION — for a matrix
A(t) with entries c_ij * t^(v_ij) (generic constants c_ij, integer valuations
v_ij), the valuation of det A(t) as t -> 0 equals the TROPICAL determinant
  trop_det(v) = min over permutations sigma of sum_i v_{i,sigma(i)}
whenever the minimizing permutation is unique (genericity). The smooth object
(a determinant) degenerates to a combinatorial one (an assignment problem) and
the shadow remembers the leading behavior exactly.

Derivations, not transcriptions (P82 rule): the tropical determinant is
computed by brute force over all permutations (its DEFINITION); the valuation
of det A(t) is measured as the log-log slope of |det| at t = 1e-3, 1e-4 —
a two-point slope is exact here because det is a polynomial in t whose lowest
term dominates at small t.

Gates:
  - hand-checkable 2x2 first: v = [[0,1],[1,0]], c=1: det = t^0 - t^2 wait —
    A = [[1, t],[t, 1]], det = 1 - t^2, valuation 0 = min(0+0, 1+1). Asserted.
  - non-generic cases (minimizing permutation tied) are DETECTED from the
    tropical side and SKIPPED WITH COUNT — ties allow cancellation and the
    correspondence honestly does not apply (the skip census is reported, not
    hidden).

Pre-stated readings (BEFORE run):
  SHADOW-REMEMBERS  measured valuation == tropical determinant EXACTLY
                    (slope rounded to nearest int) for every generic sample
                    among 60 random 4x4 draws; tie-skips counted separately.
  SHADOW-FORGETS    any generic-case mismatch — instrument-first: slope
                    measurement floor (float underflow at high valuations),
                    permutation sign cancellation among equal-valuation terms.
"""
from __future__ import annotations
import json
import math
import pathlib
from itertools import permutations

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p13_results.json"
rng = np.random.default_rng(20260886)


def trop_det(v):
    best = None
    best_count = 0
    n = len(v)
    for sig in permutations(range(n)):
        s = sum(v[i][sig[i]] for i in range(n))
        if best is None or s < best:
            best, best_count = s, 1
        elif s == best:
            best_count += 1
    return best, best_count


def measured_valuation(v, c):
    n = len(v)
    vals = []
    for t in (1e-3, 1e-4):
        A = np.array([[c[i][j] * t ** v[i][j] for j in range(n)] for i in range(n)])
        d = abs(np.linalg.det(A))
        vals.append(math.log(d) / math.log(t) if d > 0 else float("inf"))
    slope = (vals[1] * math.log(1e-4) - vals[0] * math.log(1e-3)) / (math.log(1e-4) - math.log(1e-3))
    # two-point exact slope: log|det| = val*log t + log|leading|; solve val
    lt1, lt2 = math.log(1e-3), math.log(1e-4)
    ld1 = vals[0] * lt1
    ld2 = vals[1] * lt2
    return (ld2 - ld1) / (lt2 - lt1)


# --- gate: hand-checkable 2x2 -------------------------------------------------
g_v = [[0, 1], [1, 0]]
g_c = [[1.0, 1.0], [1.0, 1.0]]
td, ties = trop_det(g_v)
mv = measured_valuation(g_v, g_c)
assert td == 0 and round(mv) == 0, f"2x2 gate FAILS: trop {td}, measured {mv}"
print(f"gate 2x2: tropical det {td}, measured valuation {mv:.4f} — PASS", flush=True)

# --- 60 random 4x4 draws ------------------------------------------------------
N = 60
generic_ok = 0
generic_bad = 0
tie_skips = 0
examples = []
for k in range(N):
    v = rng.integers(0, 6, (4, 4)).tolist()
    td, count = trop_det(v)
    if count > 1:
        tie_skips += 1                      # honest skip: correspondence needs genericity
        continue
    c = (rng.uniform(1.0, 2.0, (4, 4)) * rng.choice([-1, 1], (4, 4))).tolist()
    mv = measured_valuation(v, c)
    match = round(mv) == td
    generic_ok += match
    generic_bad += (not match)
    if len(examples) < 4:
        examples.append({"v": v, "trop_det": td, "measured": round(mv, 4), "match": bool(match)})
print(f"60 draws: generic {generic_ok + generic_bad} (match {generic_ok}, "
      f"mismatch {generic_bad}), tie-skips {tie_skips}", flush=True)
verdict = "SHADOW-REMEMBERS" if generic_bad == 0 and generic_ok > 0 else "SHADOW-FORGETS"
print(f"-> {verdict}", flush=True)

OUT.write_text(json.dumps({
    "protocol": "Puiseux valuation degeneration: measured det valuation (two-point exact slope at t=1e-3,1e-4) vs brute-force tropical determinant, 60 random 4x4 draws, unique-minimizer genericity gate with tie-skip census, seed 20260886",
    "gate_2x2": {"trop": 0, "measured": round(mv, 6)},
    "generic_matches": generic_ok, "generic_mismatches": generic_bad,
    "tie_skips": tie_skips, "examples": examples, "verdict": verdict},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
