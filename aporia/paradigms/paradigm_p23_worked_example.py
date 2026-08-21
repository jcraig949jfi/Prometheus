"""PARADIGM-P23 worked example — Recursive Self-Compression, executed.

The paradigm's move: an instance simulates a strictly smaller instance of
itself WITH STRICT SAVINGS; iteration compounds the saving into qualitatively
new power (MIP* = RE's engine, at toy scale). Executable instance: Strassen
recursion as capability bootstrapping —

  ONE level: 2x2 block matmul delegates to 7 (not 8) half-size instances
  (the P15-verified rank-7 decomposition). Strict saving: 7 < 8.
  ITERATION: M(2^k) = 7^k multiplications; the compounded saving IS a new
  asymptotic exponent log2(7) ~ 2.807 < 3 — capability (a better exponent)
  that NO single level possesses, created by self-delegation.

Legs (two-route + derived decline):
  A. CORRECTNESS: recursive Strassen on random integer matrices equals naive
     matmul EXACTLY (integer arithmetic) for n = 2,4,...,64.
  B. COUNT LAW: measured multiplication counts equal 7^k EXACTLY per level.
  C. EXPONENT: log2 M(2^k)/k -> log2 7 = 2.807355 (derived comparator).
  D. DECLINE (derived): the same recursion with the naive 8-multiplication
     block "compression" measures exponent EXACTLY 3 — iteration without
     strict saving bootstraps nothing; the decline value is derived (3) and
     direction-stated (equal to, not above, the naive exponent).

Pre-stated readings (BEFORE run):
  COMPRESSION-BOOTSTRAPS  A exact for all sizes; B: counts == 7^k; C within
                          1e-9 of log2 7 at k=6 (counts are exact so the
                          'fit' is exact arithmetic); D: exponent == 3.
  RECURSION-FAULT         instrument-first: block splitting indices, the
                          seven Strassen combinations (P15's committed
                          triples are the reference), base-case counting.
"""
from __future__ import annotations
import json
import math
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p23_results.json"
rng = np.random.default_rng(20260892)

MUL_COUNT = {"n": 0}


def strassen(A, B, use_seven=True):
    n = A.shape[0]
    if n == 1:
        MUL_COUNT["n"] += 1
        return A * B
    h = n // 2
    a11, a12, a21, a22 = A[:h, :h], A[:h, h:], A[h:, :h], A[h:, h:]
    b11, b12, b21, b22 = B[:h, :h], B[:h, h:], B[h:, :h], B[h:, h:]
    if use_seven:
        m1 = strassen(a11 + a22, b11 + b22, True)
        m2 = strassen(a21 + a22, b11, True)
        m3 = strassen(a11, b12 - b22, True)
        m4 = strassen(a22, b21 - b11, True)
        m5 = strassen(a11 + a12, b22, True)
        m6 = strassen(a21 - a11, b11 + b12, True)
        m7 = strassen(a12 - a22, b21 + b22, True)
        c11 = m1 + m4 - m5 + m7
        c12 = m3 + m5
        c21 = m2 + m4
        c22 = m1 - m2 + m3 + m6
    else:                                    # the decline leg: 8-mult "compression"
        c11 = strassen(a11, b11, False) + strassen(a12, b21, False)
        c12 = strassen(a11, b12, False) + strassen(a12, b22, False)
        c21 = strassen(a21, b11, False) + strassen(a22, b21, False)
        c22 = strassen(a21, b12, False) + strassen(a22, b22, False)
    return np.block([[c11, c12], [c21, c22]])


rows = []
ok_correct = ok_counts = True
for k in range(1, 7):
    n = 2 ** k
    A = rng.integers(-9, 10, (n, n))
    B = rng.integers(-9, 10, (n, n))
    MUL_COUNT["n"] = 0
    C = strassen(A, B, True)
    m7 = MUL_COUNT["n"]
    ok_correct &= bool(np.array_equal(C, A @ B))
    ok_counts &= (m7 == 7 ** k)
    MUL_COUNT["n"] = 0
    strassen(A, B, False)
    m8 = MUL_COUNT["n"]
    rows.append({"k": k, "n": n, "muls_7": m7, "muls_8": m8,
                 "exp_7": round(math.log2(m7) / k, 9), "exp_8": round(math.log2(m8) / k, 9)})
    print(f"k={k} n={n:3d}: strassen muls {m7:8,d} (=7^k: {m7 == 7**k}), "
          f"naive-block {m8:8,d}; exponents {math.log2(m7)/k:.6f} / {math.log2(m8)/k:.6f}",
          flush=True)

final_exp7 = rows[-1]["exp_7"]
final_exp8 = rows[-1]["exp_8"]
target = math.log2(7)
ok = (ok_correct and ok_counts and abs(final_exp7 - target) < 1e-9 and abs(final_exp8 - 3.0) < 1e-12)
verdict = "COMPRESSION-BOOTSTRAPS" if ok else "RECURSION-FAULT"
print(f"exponent (7-branch) {final_exp7:.9f} vs derived log2(7) {target:.9f}; "
      f"decline (8-branch) {final_exp8} vs derived 3 -> {verdict}", flush=True)

OUT.write_text(json.dumps({
    "protocol": "recursive Strassen vs naive-block recursion on random integer matrices (exact equality gate), exact count law 7^k, exponent vs derived log2(7), decline leg deriving exponent 3, seed 20260892",
    "rows": rows, "derived_log2_7": target, "verdict": verdict,
    "meta_note": "MIP*=RE-scale bootstrapping (protocol self-simulation to RE) is proof-engineering beyond a pass; the executable engine — strict per-level saving compounding to a new exponent — is what this demonstrates"},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
