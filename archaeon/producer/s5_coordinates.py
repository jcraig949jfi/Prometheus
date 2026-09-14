"""Fossil metabolism S5 -- observable myopia coordinates.

Every function here is a function of the EVIDENCE STATE alone: the fossils
(bits, score) and the probe alphabet {0,1}^L. None takes a target, an
outcome, a producer proposal, a winner or a future score; the tests assert
the signatures and the leakage audit in the readout repeats it.

Candidates (defined before the comparative batch; the preregistration
names ONE as the primary coordinate and the others are reported):

  entropy_disagreement   the one-step ER-optimal class (min sum n_d^2, the
      S3/S4 objective) and the one-step entropy-optimal class (max H(d)
      under the uniform prior) are DISJOINT over all 2^L probes. Rationale
      from first principles: identification time is governed by entropy
      accounting (a probe with k outcomes yields at most log2 k bits and
      E[probes] >= H(prior)/max bits per probe), whereas the ER objective
      is a collision (Renyi-2) quantity that rewards many small cells at
      the price of one large cell. Where the two objectives disagree about
      the best probe, the count-greedy producer is choosing against the
      identification-relevant quantity and is predicted to be myopic.
  entropy_deficit_bits   H_max - H(ER-optimal probe): the bits the
      count-greedy probe forgoes at this state (0 when the classes meet).
  two_block_proxy        the state has exactly two unresolved count-known
      blocks, both of size >= 3 (the product structure where strict
      two-step myopia was first found exactly).
  two_step_gap           exact two-step count gap: min over the ER-optimal
      class of the expected remaining after the best second probe, minus
      the global two-step optimum (>0 iff no one-step optimal probe is
      two-step optimal). Exact, expensive (all 2^L x outcomes x 2^L).

All are computed by enumeration at L <= 12 (the S5 worlds are tiny by
design). Returns are plain numbers/bools plus the classes for the audit.
"""
from __future__ import annotations

import math
from typing import Dict, List, Sequence

import numpy as np

from . import fossil_inference as FI
from .s5_producers import _as_int, _dist_matrix


def _feasible_ints(fossils: Sequence[FI.Fossil]) -> np.ndarray:
    return np.array(sorted(_as_int(t) for t in FI.enumerate_targets(list(fossils))), dtype=np.int64)


def _counts(L: int, S: np.ndarray) -> np.ndarray:
    M = _dist_matrix(L)[:, S]
    return np.stack([(M == e).sum(1) for e in range(L + 1)], axis=1)


def one_step_classes(fossils: Sequence[FI.Fossil]) -> Dict[str, object]:
    L = fossils[0].length
    if L > 12:
        raise ValueError("S5 coordinates are enumerative: L <= 12")
    S = _feasible_ints(fossils); N = len(S); n = _counts(L, S)
    er = (n.astype(np.int64) ** 2).sum(1)
    P = n / N
    with np.errstate(divide="ignore", invalid="ignore"):
        H = -(np.where(P > 0, P * np.log2(np.where(P > 0, P, 1.0)), 0.0)).sum(1)
    er_class = np.flatnonzero(er == er.min()); h_class = np.flatnonzero(np.abs(H - H.max()) < 1e-12)
    return {"N": N, "er_min": float(er.min() / N), "er_class_size": int(len(er_class)), "H_max": float(H.max()), "h_class_size": int(len(h_class)),
            "H_of_er_class_best": float(H[er_class].max()), "er_of_h_class_best": float(er[h_class].min() / N),
            "classes_intersect": bool(len(set(er_class.tolist()) & set(h_class.tolist())) > 0), "max_cell_frac_er_probe": float(n[er_class[0]].max() / N)}


def entropy_disagreement(fossils: Sequence[FI.Fossil]) -> bool:
    return not one_step_classes(fossils)["classes_intersect"]


def entropy_deficit_bits(fossils: Sequence[FI.Fossil]) -> float:
    c = one_step_classes(fossils)
    return float(c["H_max"] - c["H_of_er_class_best"])


def two_block_proxy(fossils: Sequence[FI.Fossil]) -> bool:
    st = FI.infer(fossils)
    unres = [b for b in st.count_known_blocks] + [b for b in st.ambiguous_blocks]
    return len(unres) == 2 and min(b["size"] for b in unres) >= 3


def two_step_gap(fossils: Sequence[FI.Fossil]) -> float:
    L = fossils[0].length; S = _feasible_ints(fossils); N = len(S); D = _dist_matrix(L); n = _counts(L, S)
    er = (n.astype(np.int64) ** 2).sum(1); cache: Dict[bytes, int] = {}
    def best1(Sx):
        k = Sx.tobytes(); v = cache.get(k)
        if v is None:
            v = int((_counts(L, Sx).astype(np.int64) ** 2).sum(1).min()); cache[k] = v
        return v
    v2 = np.zeros(1 << L, dtype=np.int64)
    for q in range(1 << L):
        tot = 0
        for e in range(L + 1):
            if n[q, e] == 0: continue
            tot += 1 if n[q, e] == 1 else best1(S[D[q, S] == e])
        v2[q] = tot
    G = np.flatnonzero(er == er.min())
    return float((int(v2[G].min()) - int(v2.min())) / N)


def all_coordinates(fossils: Sequence[FI.Fossil], with_two_step: bool = True) -> Dict[str, object]:
    c = one_step_classes(fossils)
    out = {"entropy_disagreement": not c["classes_intersect"], "entropy_deficit_bits": float(c["H_max"] - c["H_of_er_class_best"]), "two_block_proxy": two_block_proxy(fossils),
           "log2N": math.log2(c["N"]), "er_class_size": c["er_class_size"], "h_class_size": c["h_class_size"], "max_cell_frac_er_probe": c["max_cell_frac_er_probe"]}
    if with_two_step:
        out["two_step_gap"] = two_step_gap(fossils)
    return out
