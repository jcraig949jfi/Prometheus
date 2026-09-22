"""Exhaustive enumeration of Universe A for a presentation and length cap L.

Produces the universal directed graph (every word of length <= L is a state), the nominal action edges,
the distinct-successor edges, and the exact directed shortest-distance chart D[s, t] to every target,
computed by layered BFS over the REVERSED distinct-successor graph (distance-to-target, not distance-from).

UNREACH = -1 is the distinguished unreachable value in D.
"""
from __future__ import annotations
import json, os, time
import numpy as np
from .directed_rewriting import transitions, csr, distinct_edges, layered_bfs, offsets, sha256_arrays, index_word
from .presentations import rules_for

UNREACH = -1


def target_set(L: int, max_len: int = 2) -> list[int]:
    """The 21 words of length <= 2, as state indices (index order == length-major, value-minor)."""
    return list(range(int(offsets(L)[max_len + 1])))


def build(name: str, L: int, with_clones: bool = False, target_max_len: int = 2, targets: list[int] | None = None) -> dict:
    """`targets` overrides the default target set (list of state indices); used by diagnostics only."""
    t0 = time.perf_counter()
    rules = rules_for(name, with_clones)
    tr = transitions(L, rules)
    NS = tr["NS"]
    src, dst = tr["src"], tr["dst"]
    dsrc, ddst = distinct_edges(src, dst)
    t1 = time.perf_counter()
    fwd_indptr, fwd_indices = csr(dsrc, ddst, NS)
    rev_indptr, rev_indices = csr(ddst, dsrc, NS)
    outdeg_nominal = np.bincount(src, minlength=NS).astype(np.int32)
    outdeg = np.bincount(dsrc, minlength=NS).astype(np.int32)
    targets = list(targets) if targets is not None else target_set(L, target_max_len)
    T = len(targets)
    D = np.full((NS, T), UNREACH, dtype=np.int16)
    for j, t in enumerate(targets):
        col = np.full(NS, -1, dtype=np.int16)
        layered_bfs(rev_indptr, rev_indices, t, NS, col)
        D[:, j] = col
    t2 = time.perf_counter()
    return {
        "name": name, "L": L, "with_clones": with_clones, "rules": rules, "NS": NS,
        "src": src, "dst": dst, "rule": tr["rule"], "pos": tr["pos"], "W": tr["W"], "LEN": tr["LEN"],
        "dsrc": dsrc, "ddst": ddst, "fwd": (fwd_indptr, fwd_indices), "rev": (rev_indptr, rev_indices),
        "outdeg": outdeg, "outdeg_nominal": outdeg_nominal, "targets": targets, "D": D,
        "t_enumerate": t1 - t0, "t_distances": t2 - t1,
    }


def graph_hash(U: dict) -> dict:
    return {
        "edges_nominal_sha256": sha256_arrays(U["src"], U["dst"], U["rule"], U["pos"]),
        "edges_distinct_sha256": sha256_arrays(U["dsrc"], U["ddst"]),
        "D_sha256": sha256_arrays(U["D"]),
        "targets": [index_word(t, U["L"]) for t in U["targets"]],
        "rules": [r.name for r in U["rules"]],
    }


def save(U: dict, data_dir: str) -> str:
    os.makedirs(data_dir, exist_ok=True)
    tag = f"{U['name']}_L{U['L']}" + ("_clones" if U["with_clones"] else "")
    path = os.path.join(data_dir, tag + ".npz")
    np.savez(path, src=U["src"], dst=U["dst"], rule=U["rule"], pos=U["pos"], dsrc=U["dsrc"], ddst=U["ddst"],
             D=U["D"], targets=np.array(U["targets"]), LEN=U["LEN"])
    with open(os.path.join(data_dir, tag + ".hash.json"), "w") as f:
        json.dump(graph_hash(U), f, indent=1)
    return path
