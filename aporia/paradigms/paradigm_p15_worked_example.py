"""PARADIGM-P15 worked example — Tensor and Multilinear Decomposition, executed.

The paradigm's move: decompose multi-index arrays into structured sums; the
rank IS the hidden structure. Two exact legs:

  A. STRASSEN RANK-7, VERIFIED ENTRYWISE: the 2x2 matrix-multiplication
     tensor T in C^4 x C^4 x C^4 (built from the bilinear map DEFINITION:
     T[i,j,k] = 1 iff matmul entry k receives product of entries i and j)
     is reconstructed EXACTLY (64/64 integer entries) from (a) the naive
     rank-8 decomposition and (b) Strassen's rank-7 decomposition — the
     strict rank drop that seeded fast matrix multiplication.
  B. KRUSKAL CERTIFICATE, COMPUTED — AND CORRECTLY DECLINING: Kruskal's
     uniqueness condition kA + kB + kC >= 2R + 2 (k-ranks computed by
     DEFINITION — max k such that every k columns are linearly independent,
     checked over all subsets). For Strassen's factors (R=7 in dimension 4):
     max possible k-rank sum is 12 < 16, so the certificate CANNOT certify
     uniqueness — which is CORRECT: matmul decompositions are famously
     non-unique (the report-00052 frontier is precisely about when
     uniqueness holds; here it provably does not apply). A certificate that
     declines where uniqueness genuinely fails is evidence the certificate
     is real (P13's detector lesson, decomposition edition).

Pre-stated readings (BEFORE run):
  RANK7-VERIFIED   both reconstructions exact (64/64), and the Kruskal sum
                   for Strassen's factors < 16 (declines, as theory demands).
  MISMATCH         instrument-first: index conventions in the matmul tensor
                   (the classic trap — row-major vs column-major pairing),
                   sign errors in Strassen's 7 triples.
"""
from __future__ import annotations
import json
import pathlib
from itertools import combinations

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p15_results.json"

# --- the matmul tensor from its DEFINITION -----------------------------------
# index a 2x2 matrix entry (r,c) as 2*r+c; T[i,j,k]=1 iff C[k] += A[i]*B[j]
T = np.zeros((4, 4, 4), dtype=int)
for r in range(2):
    for c in range(2):
        for m in range(2):
            i = 2 * r + m          # A[r,m]
            j = 2 * m + c          # B[m,c]
            k = 2 * r + c          # C[r,c]
            T[i, j, k] += 1
assert T.sum() == 8, "definition gate: 8 multiplications in naive matmul"
print(f"matmul tensor built from definition: {T.sum()} ones — gate PASS", flush=True)

# --- naive rank-8 ------------------------------------------------------------
naive = []
for r in range(2):
    for c in range(2):
        for m in range(2):
            a = np.zeros(4, dtype=int); a[2 * r + m] = 1
            b = np.zeros(4, dtype=int); b[2 * m + c] = 1
            cc = np.zeros(4, dtype=int); cc[2 * r + c] = 1
            naive.append((a, b, cc))

def reconstruct(triples):
    R = np.zeros((4, 4, 4), dtype=int)
    for a, b, c in triples:
        R += np.einsum("i,j,k->ijk", a, b, c)
    return R

rec8 = reconstruct(naive)
ok8 = np.array_equal(rec8, T)
print(f"naive rank-8 reconstruction: {'EXACT 64/64' if ok8 else 'MISMATCH'}", flush=True)

# --- Strassen rank-7 (the seven classic triples; A,B,C entries indexed 0..3 as
#     [ [0,1],[2,3] ]; derived from M1..M7 with C = sums of M's) ---------------
def vec(*idx_coeffs):
    v = np.zeros(4, dtype=int)
    for i, c in idx_coeffs:
        v[i] = c
    return v

strassen = [
    (vec((0, 1), (3, 1)),  vec((0, 1), (3, 1)),  vec((0, 1), (3, 1))),          # M1=(A11+A22)(B11+B22) -> C11,C22
    (vec((2, 1), (3, 1)),  vec((0, 1)),          vec((2, 1), (3, -1))),         # M2=(A21+A22)B11 -> C21, -C22
    (vec((0, 1)),          vec((1, 1), (3, -1)), vec((1, 1), (3, 1))),          # M3=A11(B12-B22) -> C12, C22
    (vec((3, 1)),          vec((2, 1), (0, -1)), vec((0, 1), (2, 1))),          # M4=A22(B21-B11) -> C11, C21
    (vec((0, 1), (1, 1)),  vec((3, 1)),          vec((0, -1), (1, 1))),         # M5=(A11+A12)B22 -> -C11, C12
    (vec((2, 1), (0, -1)), vec((0, 1), (1, 1)),  vec((3, 1))),                  # M6=(A21-A11)(B11+B12) -> C22
    (vec((1, 1), (3, -1)), vec((2, 1), (3, 1)),  vec((0, 1))),                  # M7=(A12-A22)(B21+B22) -> C11
]
rec7 = reconstruct(strassen)
ok7 = np.array_equal(rec7, T)
print(f"Strassen rank-7 reconstruction: {'EXACT 64/64' if ok7 else 'MISMATCH'}", flush=True)
if not ok7:
    diff = np.argwhere(rec7 != T)
    print("  first diffs:", [(tuple(d), int(rec7[tuple(d)]), int(T[tuple(d)])) for d in diff[:5]], flush=True)

# --- Kruskal certificate by definition ---------------------------------------
def k_rank(M):
    n = M.shape[1]
    k = 0
    for r in range(1, n + 1):
        if all(np.linalg.matrix_rank(M[:, list(c)]) == r for c in combinations(range(n), r)):
            k = r
        else:
            break
    return k

A = np.stack([t[0] for t in strassen], axis=1)
B = np.stack([t[1] for t in strassen], axis=1)
C = np.stack([t[2] for t in strassen], axis=1)
kA, kB, kC = k_rank(A), k_rank(B), k_rank(C)
R = 7
bound = 2 * R + 2
print(f"Kruskal: kA={kA}, kB={kB}, kC={kC}, sum={kA+kB+kC} vs 2R+2={bound} -> "
      f"{'certifies' if kA+kB+kC >= bound else 'DECLINES (correct: matmul decompositions are non-unique)'}", flush=True)

verdict = "RANK7-VERIFIED" if (ok8 and ok7 and kA + kB + kC < bound) else "MISMATCH"
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "matmul tensor from definition; naive rank-8 and Strassen rank-7 exact entrywise reconstruction; Kruskal k-ranks by definition (all-subsets) with the certificate correctly declining",
    "tensor_ones": int(T.sum()), "rank8_exact": bool(ok8), "rank7_exact": bool(ok7),
    "kruskal": {"kA": kA, "kB": kB, "kC": kC, "sum": kA + kB + kC, "bound_2R2": bound,
                "certifies_uniqueness": bool(kA + kB + kC >= bound)},
    "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
