"""PARADIGM-P17 worked example — Variational / Extremal Principle, executed.

The paradigm's move: identify the object as the minimizer of a functional;
read its properties from optimality conditions. Executable instance: the
Rayleigh variational principle on a graph Laplacian, with an EXACT derived
comparator — for the path graph P_n the Laplacian eigenvalues are known in
closed form: lambda_k = 2 - 2*cos(k*pi/n), k = 0..n-1 (derived from the
discrete cosine eigenvectors; the derivation is checkable, not transcribed).

Three legs:
  A. COMPARATOR GATE: numpy.eigh eigenvalues must match the closed form to
     1e-10 (two independent routes to the spectrum).
  B. VARIATIONAL DESCENT: projected gradient descent on the Rayleigh quotient
     R(v) = v'Lv / v'v over the subspace orthogonal to the constant vector
     converges to lambda_1 (the algebraic connectivity) from random starts —
     the minimizer FOUND by optimization, not linear algebra.
  C. EULER-LAGRANGE CHECK: at convergence the residual ||Lv - R(v) v|| is
     small — the optimality condition IS the eigen-equation, verified.

Pre-stated readings (BEFORE run):
  EXTREMAL-CONFIRMS  leg A to 1e-10; leg B: all 5 random starts converge to
                     lambda_1 within 1e-8 relative; leg C: residual < 1e-6.
  EXTREMAL-FAILS     instrument-first: projection (deflation of the constant
                     eigenvector must be re-applied every step — drift back
                     toward lambda_0=0 is the classic failure), step size.
"""
from __future__ import annotations
import json
import math
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p17_results.json"
rng = np.random.default_rng(20260888)

n = 40
L = np.zeros((n, n))
for i in range(n - 1):
    L[i, i] += 1
    L[i + 1, i + 1] += 1
    L[i, i + 1] -= 1
    L[i + 1, i] -= 1

# --- A: derived closed form vs eigh ------------------------------------------
derived = np.sort(np.array([2 - 2 * math.cos(k * math.pi / n) for k in range(n)]))
numeric = np.sort(np.linalg.eigvalsh(L))
gap = float(np.max(np.abs(derived - numeric)))
assert gap < 1e-10, f"comparator gate FAILS: {gap}"
lam1 = derived[1]
print(f"A. closed form vs eigh: max|diff| = {gap:.2e} over {n} eigenvalues — PASS; "
      f"lambda_1 = {lam1:.10f}", flush=True)

# --- B: Rayleigh descent -----------------------------------------------------
ones = np.ones(n) / math.sqrt(n)
def project(v):
    v = v - (v @ ones) * ones
    return v / np.linalg.norm(v)

results_B = []
ok_B = True
for trial in range(5):
    v = project(rng.standard_normal(n))
    for it in range(20000):
        r = float(v @ L @ v)
        grad = 2 * (L @ v - r * v)
        v = project(v - 0.2 * grad)
    r = float(v @ L @ v)
    rel = abs(r - lam1) / lam1
    ok_B &= rel < 1e-8
    results_B.append(rel)
print(f"B. 5 random starts -> Rayleigh values within {max(results_B):.2e} relative of lambda_1", flush=True)

# --- C: Euler-Lagrange residual ----------------------------------------------
residual = float(np.linalg.norm(L @ v - r * v))
print(f"C. Euler-Lagrange residual ||Lv - R v|| = {residual:.2e}", flush=True)

verdict = ("EXTREMAL-CONFIRMS" if (gap < 1e-10 and ok_B and residual < 1e-6)
           else "EXTREMAL-FAILS")
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "path-graph P_40 Laplacian: derived closed-form spectrum vs eigh (gate), projected Rayleigh descent from 5 random starts to lambda_1, Euler-Lagrange residual at convergence, seed 20260888",
    "n": n, "comparator_gap": gap, "lambda_1": lam1,
    "descent_rel_errors": [float(f"{r:.3e}") for r in results_B],
    "euler_lagrange_residual": residual, "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
