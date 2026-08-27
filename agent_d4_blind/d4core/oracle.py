"""Omniscient offline navigation oracle. ANALYSIS ONLY.

Knows the empirical phenotype graph (every observed transition from every
component of the run). Used solely to attribute navigation failure to
topology (no observed path exists) vs search weakness (path exists, M0
missed it). Its output never reaches any navigator — enforced structurally:
this module is imported only by the pipeline's analysis stage, after all
navigation rows are final.
"""
from __future__ import annotations

from collections import deque

from .navigators import EdgeStore


def oracle_reachability(sub, store: EdgeStore, targets, eps_hit: float) -> dict:
    adj: dict = {}
    for a, b in store.edges:
        if a != b:
            adj.setdefault(a, set()).add(b)
    # BFS from the union of actual navigation start phenotypes
    starts = set(store.nav_start_pkeys)
    reachable = set(starts)
    q = deque(starts)
    while q:
        v = q.popleft()
        for w in adj.get(v, ()):
            if w not in reachable:
                reachable.add(w)
                q.append(w)
    per_target = []
    strata: dict = {}
    for t in targets:
        goal_hit = False
        tfp = t["fp"]
        for pk in reachable:
            f = store.fp_by_pkey.get(pk)
            if f is not None and sub.d1(f, tfp) <= eps_hit:
                goal_hit = True
                break
        per_target.append({"target_id": t["target_id"], "stratum": t["stratum"],
                           "oracle_reachable": goal_hit})
        s = strata.setdefault(t["stratum"], [0, 0])
        s[0] += int(goal_hit)
        s[1] += 1
    return {
        "n_starts": len(starts),
        "n_reachable_pkeys": len(reachable),
        "n_graph_nodes": len(set(store.fp_by_pkey.keys())),
        "per_target": per_target,
        "strata_reach": {k: v[0] / v[1] for k, v in strata.items()},
        "pooled_reach": (sum(p["oracle_reachable"] for p in per_target) / len(per_target))
        if per_target else 0.0,
    }
