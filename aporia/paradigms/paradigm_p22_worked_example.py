"""PARADIGM-P22 worked example — Polynomial Method (Spectral on Signed Graphs).

The paradigm's move: CONSTRUCT a signed operator encoding the combinatorial
property, then read the bound off its spectrum via interlacing. Executable
instance: Huang's sensitivity-proof machinery at small n.

Huang's signed hypercube matrix: B_1 = [[0,1],[1,0]],
  B_n = [[B_{n-1}, I], [I, -B_{n-1}]].
Facts VERIFIED (not cited): B_n^2 = n*I (so eigenvalues are +-sqrt(n), each
with multiplicity 2^(n-1)); by Cauchy interlacing, ANY induced principal
submatrix on 2^(n-1)+1 vertices has lambda_max >= sqrt(n); since lambda_max
<= max degree of the underlying induced subgraph, every such subgraph has a
vertex of degree >= sqrt(n) — the sensitivity bound's engine.

Legs (raw beside derived, decline-capable):
  A. ALGEBRA GATE: B_n^2 == n*I exactly, n = 1..10 (integer arithmetic).
  B. SPECTRUM: eigenvalues +-sqrt(n) with equal multiplicities (numpy vs the
     derived values, 1e-9).
  C. INTERLACING AT THE THRESHOLD: for n in {4,...,8}, 40 random induced
     subsets of size 2^(n-1)+1: lambda_max >= sqrt(n) in EVERY sample, and
     the max-degree consequence holds in every sample.
  D. SHARPNESS / DECLINE: the natural half {vertices with first bit 0} has
     size 2^(n-1) (ONE fewer) and its induced signed matrix is +-B_{n-1}
     with lambda_max = sqrt(n-1) < sqrt(n) — the bound fails below the
     threshold by a DERIVED amount (sqrt(n-1)), verified numerically. The
     threshold is sharp and the instrument shows both sides.

Pre-stated readings (BEFORE run):
  INTERLACING-BITES  A exact for all n<=10; B to 1e-9; C: 200/200 samples
                     pass both the eigenvalue and the degree consequence;
                     D: half-cube lambda_max == sqrt(n-1) to 1e-9 (direction:
                     BELOW sqrt(n), stated).
  SPECTRAL-FAULT     instrument-first: recursive block construction, induced
                     submatrix indexing, degree counted in the UNDERLYING
                     graph (signs stripped).
"""
from __future__ import annotations
import json
import math
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p22_results.json"
rng = np.random.default_rng(20260890)


def huang(n):
    if n == 1:
        return np.array([[0, 1], [1, 0]], dtype=np.int64)
    B = huang(n - 1)
    m = B.shape[0]
    I = np.eye(m, dtype=np.int64)
    return np.block([[B, I], [I, -B]])


# --- A: algebra gate ----------------------------------------------------------
for n in range(1, 11):
    B = huang(n)
    assert np.array_equal(B @ B, n * np.eye(2 ** n, dtype=np.int64)), f"B_{n}^2 != {n}I"
print("A. B_n^2 = n*I exactly for n = 1..10 — PASS", flush=True)

# --- B: spectrum --------------------------------------------------------------
spec_ok = True
for n in range(1, 9):
    ev = np.sort(np.linalg.eigvalsh(huang(n).astype(float)))
    want = np.sort(np.concatenate([np.full(2 ** (n - 1), -math.sqrt(n)),
                                   np.full(2 ** (n - 1), math.sqrt(n))]))
    spec_ok &= bool(np.max(np.abs(ev - want)) < 1e-9)
print(f"B. eigenvalues +-sqrt(n) with equal multiplicities, n<=8: {'PASS' if spec_ok else 'FAIL'}", flush=True)

# --- C: interlacing at the threshold -----------------------------------------
c_pass = 0
c_total = 0
for n in range(4, 9):
    B = huang(n).astype(float)
    N = 2 ** n
    k = 2 ** (n - 1) + 1
    for _ in range(40):
        idx = rng.choice(N, size=k, replace=False)
        sub = B[np.ix_(idx, idx)]
        lam = float(np.max(np.linalg.eigvalsh(sub)))
        degs = np.abs(np.sign(sub)).sum(axis=1)          # underlying degrees (signs stripped)
        ok = lam >= math.sqrt(n) - 1e-9 and float(degs.max()) >= math.sqrt(n) - 1e-9
        c_pass += ok
        c_total += 1
print(f"C. threshold subsets (2^(n-1)+1): {c_pass}/{c_total} pass eigenvalue AND degree bound", flush=True)

# --- D: sharpness below the threshold ----------------------------------------
d_ok = True
d_vals = []
for n in range(4, 9):
    B = huang(n).astype(float)
    half = np.arange(2 ** (n - 1))                       # first-bit-0 half
    sub = B[np.ix_(half, half)]
    lam = float(np.max(np.linalg.eigvalsh(sub)))
    want = math.sqrt(n - 1)
    d_ok &= abs(lam - want) < 1e-9
    d_vals.append({"n": n, "half_lambda_max": round(lam, 9), "sqrt_n_minus_1": round(want, 9)})
    print(f"D. n={n}: half-cube lambda_max {lam:.6f} == sqrt(n-1) {want:.6f} < sqrt(n) {math.sqrt(n):.6f}", flush=True)

verdict = ("INTERLACING-BITES" if (spec_ok and c_pass == c_total and d_ok) else "SPECTRAL-FAULT")
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "Huang signed hypercube: exact B_n^2=nI gate (n<=10), spectrum check, 200 threshold-size induced subsets (eigenvalue + degree consequences), sharpness decline leg at size 2^(n-1) with derived value sqrt(n-1), seed 20260890",
    "threshold_samples_pass": c_pass, "threshold_samples_total": c_total,
    "sharpness": d_vals, "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
