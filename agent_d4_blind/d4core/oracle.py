"""Omniscient offline navigation oracle. ANALYSIS ONLY.

Knows the empirical single-parent phenotype graph (crossover edges excluded:
they are population-dependent two-parent events and would let the oracle
"hop" between regions no single trajectory can connect). Used solely to
attribute navigation failure to topology (no observed path existed for that
episode) vs search weakness (a path existed, M0 missed it). Output never
reaches any navigator.

v3 repair: reachability is PER EPISODE. v1/v2 ran BFS from the union of all
runs' starts, which in a fragmented space with broad ab-initio support
always contains a start near any target (some run began on its island) even
though every single episode was trapped. Now: reverse BFS from each
target's hit-ball; an episode counts as oracle-reachable iff ITS OWN start
lies in the ball's basin.
"""
from __future__ import annotations

from collections import deque

from .navigators import EdgeStore


def oracle_reachability(sub, store: EdgeStore, targets, eps_hit: float,
                        nav_rows) -> dict:
    # v4: navigators only traverse and score VIABLE phenotypes, so the
    # oracle graph is restricted to viable endpoints and the hit-ball to
    # viable members; otherwise attribution is inflated toward
    # "reachable" through states no navigator can use.
    viable_pk = {pk for pk, f in store.fp_by_pkey.items() if sub.viable(f)}
    radj: dict = {}
    for a, b in store.edges:
        if a != b and a in viable_pk and b in viable_pk:
            radj.setdefault(b, set()).add(a)
    starts_by_target: dict = {}
    for r in nav_rows:
        sts = r.get("start_pkeys") or ([r["start_pkey"]] if r.get("start_pkey") is not None else [])
        if sts:
            starts_by_target.setdefault(r["target_id"], []).append(sts)
    all_pkeys = [(pk, store.fp_by_pkey[pk]) for pk in viable_pk]
    per_target = []
    strata: dict = {}
    for t in targets:
        tfp = t["fp"]
        ball = [pk for pk, f in all_pkeys if sub.d1(f, tfp) <= eps_hit]
        basin = set(ball)
        q = deque(ball)
        while q:
            v = q.popleft()
            for w in radj.get(v, ()):
                if w not in basin:
                    basin.add(w)
                    q.append(w)
        # an episode counts if ANY of its starts (initial, restarts, fresh
        # injections) lies in the basin
        eps_starts = starts_by_target.get(t["target_id"], [])
        frac = (sum(1 for sts in eps_starts if any(s in basin for s in sts))
                / len(eps_starts) if eps_starts else 0.0)
        per_target.append({"target_id": t["target_id"], "stratum": t["stratum"],
                           "ball_size": len(ball), "basin_size": len(basin),
                           "episode_reach_frac": frac})
        s = strata.setdefault(t["stratum"], [])
        s.append(frac)
    return {
        "n_graph_nodes": len(all_pkeys),
        "per_target": per_target,
        "strata_reach": {k: sum(v) / len(v) for k, v in strata.items()},
        "pooled_reach": (sum(p["episode_reach_frac"] for p in per_target)
                         / len(per_target)) if per_target else 0.0,
    }
