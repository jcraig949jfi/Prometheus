"""Termination evidence for a one-way universe.

Deterministic argument for U_A3_ONEWAY_BRAID (cancel + xyx -> yxy):
  measure mu(w) = (len(w), #x(w)) in lexicographic order.
  cancel: len drops by 2.  relator: len unchanged, #x drops by 1 (xyx has two x, yxy has one).
  Every action strictly decreases mu, mu is bounded below, so every rewrite sequence is finite.
  The argument does not mention the cap L: termination is intrinsic to the orientation.  The cap only makes the
  state space finite; it is not what stops rewriting (nothing in U-A3 can increase length anyway).
Executable evidence: (1) every nominal edge decreases mu; (2) no self-loops; (3) every strongly connected
component of the distinct-successor graph is a singleton; (4) longest directed path (height) by DP.
"""
from __future__ import annotations
import collections
import numpy as np


def measure_check(U: dict) -> dict:
    W, LEN = U["W"], U["LEN"].astype(np.int64)
    nx = (W == 0).sum(axis=1).astype(np.int64)  # code 0 == 'x'
    src, dst = U["src"], U["dst"]
    dec = (LEN[dst] < LEN[src]) | ((LEN[dst] == LEN[src]) & (nx[dst] < nx[src]))
    return {"measure": "(len, #x) lexicographic", "edges": int(len(src)), "measure_violations": int((~dec).sum()), "nx": nx}


def scc_evidence(U: dict) -> dict:
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components
    NS = U["NS"]; dsrc, ddst = U["dsrc"], U["ddst"]
    A = csr_matrix((np.ones(len(dsrc), dtype=np.int8), (dsrc, ddst)), shape=(NS, NS))
    ncomp, labels = connected_components(A, directed=True, connection="strong")
    sizes = np.bincount(labels)
    hist = collections.Counter(sizes.tolist())
    return {"self_loops": int((dsrc == ddst).sum()), "strongly_connected_components": int(ncomp),
            "scc_size_histogram": {str(k): int(v) for k, v in sorted(hist.items())}, "largest_scc": int(sizes.max()),
            "cycles_present": bool(sizes.max() > 1 or (dsrc == ddst).any())}


def heights(U: dict, nx: np.ndarray) -> np.ndarray:
    """Longest directed path from each state (tree-lookahead exhaustion depth), by iterative relaxation
    height[s] = 1 + max(height[succ]) until a fixed point.  Valid for any DAG (the SCC check guarantees one);
    the number of sweeps equals the maximum height + 1, each sweep O(E)."""
    NS = U["NS"]; dsrc, ddst = U["dsrc"], U["ddst"]
    height = np.zeros(NS, dtype=np.int32)
    for _ in range(10000):
        new = np.zeros(NS, dtype=np.int32)
        np.maximum.at(new, dsrc, height[ddst] + 1)
        if np.array_equal(new, height):
            return height
        height = new
    raise RuntimeError("height relaxation did not converge: graph is not a DAG")


def termination_evidence(U: dict) -> dict:
    m = measure_check(U); nx = m.pop("nx")
    s = scc_evidence(U)
    h = heights(U, nx)
    hh = collections.Counter(h.tolist())
    out = {**m, **s, "terminal_states": int((U["outdeg"] == 0).sum()), "max_height_longest_path": int(h.max()),
           "height_histogram": {str(k): int(v) for k, v in sorted(hh.items())},
           "termination_intrinsic": m["measure_violations"] == 0,
           "verdict": ("TERMINATING (intrinsic (len,#x) measure verified on every edge; DAG confirmed)" if (m["measure_violations"] == 0 and not s["cycles_present"])
                       else "TERMINATING (DAG confirmed; the (len,#x) measure does not apply to this rule set)" if not s["cycles_present"]
                       else "NOT TERMINATING: cycles present")}
    return out, h
