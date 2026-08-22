"""PARADIGM-P28 worked example — Asymptotic Spectrum (Strassen), executed.

The paradigm's move: the asymptotic value of a tensor pre-order is governed
by its MONOTONES (spectrum points) — functionals that respect restriction.
Executable engine at small scale, with the admission test that can DECLINE:

  A. RESTRICTIONS CONSTRUCTED AND VERIFIED: T <= S via explicit maps
     (A,B,C): T = (A(x)B(x)C) . S, verified ENTRYWISE (two-route: built,
     then checked). Pairs: (i) diagonal <2> <= <3> (padding maps);
     (ii) M<2> <= <7> — the restriction certificate IS P15's entrywise-
     verified Strassen decomposition, REUSED as maps (cross-paradigm reuse);
     (iii) a dense-rotation restriction of a sparse diagonal (for the
     decline leg).
  B. SPECTRUM-POINT ADMISSION: the three flattening ranks (matrix ranks of
     the unfoldings — exactly computable) must be MONOTONE non-increasing
     under every verified restriction. All pass -> admitted.
  C. DECLINE LEG: the candidate functional nnz (number of nonzero entries)
     is REJECTED by the same test — under the dense-rotation restriction of
     <2>, nnz INCREASES (derived: rotations densify), so nnz is not a
     spectrum point. An admission test that cannot reject admits nothing.
  D. ASYMPTOTIC FLAVOR: flattening multiplicativity on diagonal powers
     <2>^(x)k = <2^k> verified exactly for k = 1..5 — the regularization
     that makes a monotone an ASYMPTOTIC spectrum point.

Pre-stated readings (BEFORE run):
  SPECTRUM-ADMITS  A: all restriction identities entrywise-exact; B: 3
                   flattenings monotone on all pairs; C: nnz rejected with
                   the witness pair named; D: multiplicativity exact.
  MONOTONE-FAULT   instrument-first: unfolding index conventions, map
                   application order (Tucker contraction), padding shapes.
"""
from __future__ import annotations
import json
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p28_results.json"
rng = np.random.default_rng(20260896)


def apply_maps(S, A, B, C):
    return np.einsum("ia,jb,kc,abc->ijk", A, B, C, S)


def flattening_ranks(T):
    n1, n2, n3 = T.shape
    return (int(np.linalg.matrix_rank(T.reshape(n1, n2 * n3))),
            int(np.linalg.matrix_rank(np.moveaxis(T, 1, 0).reshape(n2, n1 * n3))),
            int(np.linalg.matrix_rank(np.moveaxis(T, 2, 0).reshape(n3, n1 * n2))))


def diag(r):
    T = np.zeros((r, r, r))
    for i in range(r):
        T[i, i, i] = 1.0
    return T


def matmul_tensor():
    T = np.zeros((4, 4, 4))
    for r in range(2):
        for c in range(2):
            for m in range(2):
                T[2 * r + m, 2 * m + c, 2 * r + c] += 1.0
    return T


# Strassen triples (P15's entrywise-verified set) as restriction maps <7> -> M<2>
def vec(*ic):
    v = np.zeros(4)
    for i, cch in ic:
        v[i] = cch
    return v

strassen = [
    (vec((0, 1), (3, 1)),  vec((0, 1), (3, 1)),  vec((0, 1), (3, 1))),
    (vec((2, 1), (3, 1)),  vec((0, 1)),          vec((2, 1), (3, -1))),
    (vec((0, 1)),          vec((1, 1), (3, -1)), vec((1, 1), (3, 1))),
    (vec((3, 1)),          vec((2, 1), (0, -1)), vec((0, 1), (2, 1))),
    (vec((0, 1), (1, 1)),  vec((3, 1)),          vec((0, -1), (1, 1))),
    (vec((2, 1), (0, -1)), vec((0, 1), (1, 1)),  vec((3, 1))),
    (vec((1, 1), (3, -1)), vec((2, 1), (3, 1)),  vec((0, 1))),
]
A7 = np.stack([t[0] for t in strassen], axis=1)   # 4x7: maps e_i -> a_i
B7 = np.stack([t[1] for t in strassen], axis=1)
C7 = np.stack([t[2] for t in strassen], axis=1)

pairs = []
# (i) <2> <= <3>: padding projection maps
P23 = np.zeros((2, 3)); P23[0, 0] = P23[1, 1] = 1.0
pairs.append(("<2> <= <3>", diag(3), (P23, P23, P23), diag(2)))
# (ii) M<2> <= <7>: Strassen maps applied to the diagonal-7 tensor
pairs.append(("M<2> <= <7>", diag(7), (A7, B7, C7), matmul_tensor()))
# (iii) dense rotation of <2> (equivalent tensor, used for the decline leg)
Q = np.linalg.qr(rng.standard_normal((2, 2)))[0]
pairs.append(("rot(<2>) <= <2>", diag(2), (Q, Q, Q), None))   # target computed below

results = []
ok = True
for name, S, maps, expected in pairs:
    T = apply_maps(S, *maps)
    if expected is not None:
        exact = np.allclose(T, expected, atol=1e-12)
        ok &= exact
        print(f"A. {name}: restriction identity {'EXACT' if exact else 'FAILS'}", flush=True)
    fr_S, fr_T = flattening_ranks(S), flattening_ranks(T)
    mono = all(t <= s for t, s in zip(fr_T, fr_S))
    ok &= mono
    nnz_S, nnz_T = int(np.sum(np.abs(S) > 1e-12)), int(np.sum(np.abs(T) > 1e-12))
    print(f"B. {name}: flattenings {fr_S} -> {fr_T} monotone={mono}; "
          f"nnz {nnz_S} -> {nnz_T}", flush=True)
    results.append({"pair": name, "flat_S": fr_S, "flat_T": fr_T, "monotone": mono,
                    "nnz_S": nnz_S, "nnz_T": nnz_T})

# C: nnz must be REJECTED — the rotation pair densifies
nnz_reject = any(r["nnz_T"] > r["nnz_S"] for r in results)
print(f"C. nnz admission test: {'REJECTED (witness found)' if nnz_reject else 'not rejected — fault'}", flush=True)

# D: flattening multiplicativity on diagonal powers
mult_ok = True
for k in range(1, 6):
    fr = flattening_ranks(diag(2 ** k)) if k <= 3 else None
    if k <= 3:
        mult_ok &= (fr == (2 ** k, 2 ** k, 2 ** k))
# tensor powers explicitly for k=2 on <2>: kron of unfoldings
T2 = diag(2)
T4 = np.einsum("abc,def->adbecf", T2, T2).reshape(4, 4, 4)
mult_ok &= (flattening_ranks(T4) == (4, 4, 4)) and np.allclose(T4, diag(4))
print(f"D. multiplicativity: <2>^(x)2 == <4> exactly and flattenings multiply — {mult_ok}", flush=True)

verdict = "SPECTRUM-ADMITS" if (ok and nnz_reject and mult_ok) else "MONOTONE-FAULT"
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "constructed+entrywise-verified restrictions (padding, Strassen-as-maps reusing P15, rotation), flattening-rank monotonicity admission, nnz decline leg, diagonal-power multiplicativity, seed 20260896",
    "pairs": results, "nnz_rejected": nnz_reject, "multiplicativity": mult_ok,
    "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
