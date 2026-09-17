"""Reproducible construction of AC-01 controls.  Construction only: nothing here runs or scores a compressor.

PC1  Abelian rewriting universe (U-A1) -- built by universe.enumerate; coordinates withheld (presentations.exponent_vector is diagnostic).
PC2  Cloned actions -- presentations.rules_for(name, with_clones=True); plumbing test (clones must merge).
PC3  Synthetic structured tensor with poor flattened matrix rank but very low structured rank (Kronecker construction below).
NC1-A  Degree-preserving topology shuffle of the legal graph.
NC1-B  Consequence permutation: legal graph intact, D values permuted among live entries within each target column
       (exact per-column marginals preserved).
NC2    Long-horizon near-clones: catalogue extracted from the enumerated universe (metrics.trap_analysis examples and
       nc2_catalog below).
"""
from __future__ import annotations
import numpy as np


# ----------------------------------------------------------------------------- NC1-A
def degree_preserving_shuffle(src: np.ndarray, dst: np.ndarray, seed: int, swaps_per_edge: int = 10):
    """Edge-swap (configuration-model) shuffle preserving every in- and out-degree; no self-loops, no multi-edges.
    Intended for the distinct-successor graph.  O(E * swaps_per_edge) Python; fine for E <= a few million."""
    rng = np.random.default_rng(seed)
    s = src.astype(np.int64).copy(); d = dst.astype(np.int64).copy()
    E = len(s)
    present = set(zip(s.tolist(), d.tolist()))
    n_target = E * swaps_per_edge; done = 0; attempts = 0
    pairs = rng.integers(0, E, size=(n_target * 2, 2))
    for i, j in pairs:
        attempts += 1
        if done >= n_target:
            break
        a, b, c, e = int(s[i]), int(d[i]), int(s[j]), int(d[j])
        if a == e or c == b or (a, e) in present or (c, b) in present:
            continue
        present.discard((a, b)); present.discard((c, e)); present.add((a, e)); present.add((c, b))
        d[i], d[j] = e, b; done += 1
    return s, d, {"swaps_done": done, "attempts": attempts}


# ----------------------------------------------------------------------------- NC1-B
def consequence_permutation(D: np.ndarray, seed: int, unreach: int = -1) -> np.ndarray:
    """Permute the live values of each target column among that column's live entries.  Marginals exact."""
    rng = np.random.default_rng(seed)
    out = D.copy()
    for j in range(D.shape[1]):
        live = np.nonzero(D[:, j] != unreach)[0]
        out[live, j] = D[rng.permutation(live), j]
    return out


# ----------------------------------------------------------------------------- PC3
def pc3_kronecker(n: int, seed: int) -> dict:
    """T[i1,i2,i3,i4] = A[i1,i2] * B[i3,i4] with A, B random full-rank n x n.
    naive matrix flattening rows=(i1,i3), cols=(i2,i4): rank n^2 (Kronecker product of full-rank matrices)
    structured flattening rows=(i1,i2), cols=(i3,i4): rank 1
    TT ranks in index order (1,2,3,4): (n, 1, n) -- low only at the middle cut; the point of the control is that a
    single "wrong-coordinates" flattening reports full rank for a tensor with an exact 2-parameter-block description."""
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n)); B = rng.standard_normal((n, n))
    T = np.einsum("ab,cd->abcd", A, B)
    naive = T.transpose(0, 2, 1, 3).reshape(n * n, n * n)
    structured = T.reshape(n * n, n * n)
    return {"T": T, "naive_flattening": naive, "structured_flattening": structured,
            "expected": {"naive_rank": n * n, "structured_rank": 1, "tt_ranks_1234": [n, 1, n], "params_exact": 2 * n * n, "params_dense": n ** 4}}


# ----------------------------------------------------------------------------- NC2
def nc2_catalog(U: dict, max_items: int = 1000) -> list[dict]:
    """All (state, target) cases where a latent trap action and a non-trap action share the local signature
    (rule family, len(successor), outdeg(successor)).  Thin wrapper on metrics.trap_analysis examples with a larger cap."""
    from ..universe.metrics import trap_analysis
    return trap_analysis(U, max_examples=max_items)["examples"]
