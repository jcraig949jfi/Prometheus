"""Transformation-monoid universes (survivor gate).

State = a map f: [n] -> [n], encoded as the base-n integer of (f(0), ..., f(n-1)).  Action g: f -> g o f, i.e. the
generator is applied to the VALUES.  Every generator is legal in every state (out-degree constant); an action whose
result equals the state is a legal no-op (self-loop) and is excluded from the distinct-successor graph.
Targets (mechanical): the restricted-growth maps of a given rank (one canonical representative per set partition).
Truth-side quantities (kernel mask, rank, counts, block-size multiset, count-vector class) are computed here; only
the pairwise-free ones may enter the frozen observation language (see gate2/observation_monoid.py).
Symmetry used for eccentricities: g o (f o pi) = (g o f) o pi for any position permutation pi, so the forward region
and eccentricity of f depend only on its count vector (which values occur how often).
"""
from __future__ import annotations
import itertools
import numpy as np
from .directed_rewriting import csr, layered_bfs, sha256_arrays

UNREACH = -1


class Gen:
    __slots__ = ("name", "family", "lhs", "rhs")

    def __init__(self, name, family):
        self.name, self.family, self.lhs, self.rhs = name, family, "", ""


def rgs_maps(n: int, k: int) -> list[tuple]:
    out = []
    def rec(prefix, mx):
        if len(prefix) == n:
            if mx == k - 1:
                out.append(tuple(prefix))
            return
        for v in range(min(mx + 2, k)):
            rec(prefix + [v], max(mx, v))
    rec([0], 0)
    return out


def map_str(F_row) -> str:
    return "".join(str(int(v)) for v in F_row)


def build_monoid(name: str, n: int, gens: dict, target_rank: int = 2) -> dict:
    NS = n ** n
    pw = n ** np.arange(n - 1, -1, -1, dtype=np.int64)
    idx = np.arange(NS, dtype=np.int64)
    F = np.stack([(idx // pw[i]) % n for i in range(n)], axis=1).astype(np.int8)
    families = {}
    for gname, g in gens.items():
        families[gname] = "perm" if len(set(g.tolist())) == n else "rankdrop"
    rules = [Gen(gname, families[gname]) for gname in gens]
    srcs, dsts, rids = [], [], []
    for r, (gname, g) in enumerate(gens.items()):
        g = np.asarray(g, dtype=np.int64)
        dst = (g[F.astype(np.int64)] * pw).sum(axis=1)
        srcs.append(idx); dsts.append(dst); rids.append(np.full(NS, r, dtype=np.int8))
    src = np.concatenate(srcs); dst = np.concatenate(dsts); rid = np.concatenate(rids)
    pos = np.zeros(len(src), dtype=np.int8)
    keep = src != dst
    pairs = np.unique(np.stack([src[keep], dst[keep]], axis=1), axis=0)
    dsrc, ddst = pairs[:, 0], pairs[:, 1]
    fwd = csr(dsrc, ddst, NS); rev = csr(ddst, dsrc, NS)
    outdeg = np.bincount(dsrc, minlength=NS).astype(np.int32)
    outdeg_nominal = np.full(NS, len(gens), dtype=np.int32)
    targets = [int((np.array(t) * pw).sum()) for t in rgs_maps(n, target_rank)]
    D = np.full((NS, len(targets)), UNREACH, dtype=np.int16)
    for j, t in enumerate(targets):
        col = np.full(NS, -1, dtype=np.int16); layered_bfs(rev[0], rev[1], t, NS, col); D[:, j] = col
    # truth-side quantities
    C = np.stack([(F == v).sum(axis=1) for v in range(n)], axis=1).astype(np.int8)        # count vector (pairwise-free)
    rank = (C > 0).sum(axis=1).astype(np.int8)
    bs = -np.sort(-C.astype(np.int64), axis=1)                                             # block sizes, descending
    bs_id = (bs * ((n + 1) ** np.arange(n - 1, -1, -1))).sum(axis=1)                       # block-size multiset id
    cvec_id = (C.astype(np.int64) * ((n + 1) ** np.arange(n - 1, -1, -1))).sum(axis=1)     # count-vector class id
    pairs_ij = list(itertools.combinations(range(n), 2))
    kmask = np.zeros(NS, dtype=np.int32)                                                    # KERNEL (truth only)
    for p, (i, j) in enumerate(pairs_ij):
        kmask |= (F[:, i] == F[:, j]).astype(np.int32) << p
    return {"name": name, "n": n, "L": n, "NS": NS, "gens": {k: np.asarray(v).tolist() for k, v in gens.items()}, "rules": rules,
            "F": F, "src": src, "dst": dst, "rule": rid, "pos": pos, "dsrc": dsrc, "ddst": ddst, "fwd": fwd, "rev": rev,
            "outdeg": outdeg, "outdeg_nominal": outdeg_nominal, "targets": targets, "D": D,
            "C": C, "rank": rank, "bs_id": bs_id, "cvec_id": cvec_id, "kmask": kmask, "pairs_ij": pairs_ij,
            "self_loops_nominal": int((~keep).sum())}


def kernel_compatible(U: dict, states: np.ndarray, t: int) -> np.ndarray:
    """ker f refines ker t  <=>  every pair identified by f is identified by t.  TRUTH-SIDE ONLY."""
    return (U["kmask"][states] & ~U["kmask"][t]) == 0


def ecc_region_by_class(U: dict):
    """Forward-region size and BFS eccentricity for every state, via one BFS per count-vector class."""
    NS = U["NS"]; fi, fx = U["fwd"]
    cls, inv = np.unique(U["cvec_id"], return_inverse=True)
    reps = np.zeros(len(cls), dtype=np.int64); seen = np.zeros(len(cls), dtype=bool)
    for s in range(NS):
        c = inv[s]
        if not seen[c]:
            reps[c] = s; seen[c] = True
        if seen.all():
            break
    ecc_c = np.zeros(len(cls), dtype=np.int32); reg_c = np.zeros(len(cls), dtype=np.int64)
    for c, s in enumerate(reps.tolist()):
        dist = np.full(NS, -1, dtype=np.int16); layered_bfs(fi, fx, s, NS, dist)
        reg_c[c] = int((dist >= 0).sum()); ecc_c[c] = int(dist.max())
    return ecc_c[inv].astype(np.int32), reg_c[inv].astype(np.int64), len(cls)


def generated_monoid(U: dict) -> dict:
    """The submonoid generated from the identity map: size and rank distribution (the closed subset M)."""
    n = U["n"]; pw = n ** np.arange(n - 1, -1, -1, dtype=np.int64)
    ident = int((np.arange(n) * pw).sum())
    dist = np.full(U["NS"], -1, dtype=np.int16); layered_bfs(U["fwd"][0], U["fwd"][1], ident, U["NS"], dist)
    inM = dist >= 0
    ranks = U["rank"][inM]
    return {"size": int(inM.sum()), "max_word_length_from_identity": int(dist.max()),
            "rank_histogram": {int(r): int(c) for r, c in zip(*np.unique(ranks, return_counts=True))}}


def hashes(U: dict) -> dict:
    return {"edges_nominal_sha256": sha256_arrays(U["src"], U["dst"], U["rule"]), "edges_distinct_sha256": sha256_arrays(U["dsrc"], U["ddst"]),
            "D_sha256": sha256_arrays(U["D"]), "targets": [map_str(U["F"][t]) for t in U["targets"]], "gens": U["gens"]}
