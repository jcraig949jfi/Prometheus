"""WTP-04 perturbation axes (PREREG_WTP04 s3). Each axis moves ONE physics gene (or one coupled pair)
of a family representative outward; every other gene, including the WTP-03 calibrated economy, stays at
the representative's value. Level "native" (no change) is always run as the anchor.
Ordered axes list levels from benign to harsh; categorical axes (topology, sensing) have no order."""
import copy

INFO_COSTS = ("p_read", "p_write", "p_probe", "p_rollout")      # p_compute is the separate compute axis


def _set(path, v):
    def f(g):
        g = copy.deepcopy(g)
        d = g
        for k in path[:-1]:
            d = d[k]
        d[path[-1]] = v
        return g
    return f


def _mul(keys, m):
    def f(g):
        g = copy.deepcopy(g)
        for k in keys:
            g["resource"][k] = g["resource"][k] * m
        return g
    return f


def _drift(period):
    def f(g):
        g = copy.deepcopy(g)
        g["transition"]["drift"] = 0.0 if period is None else 0.3
        if period is not None:
            g["transition"]["drift_period"] = int(period)
        return g
    return f


def _topo(kind):
    """Topology without one-way edges (coupled pair, PREREG_WTP04 s3): one-way edges belong to irreversibility,
    and with them every non-lattice geometry trapped the organism in dev (DEGENERATE/topology)."""
    def f(g):
        g = copy.deepcopy(g)
        g["geometry"]["kind"] = kind
        g["irreversibility"]["oneway"] = 0.0
        return g
    return f


def _forget(rate):
    def f(g):
        g = copy.deepcopy(g)
        if g["memory"]["forget"] == "none" and rate > 0:
            g["memory"]["forget"] = "decay"
        g["memory"]["forget_rate"] = float(rate)
        return g
    return f


def _life(m):
    def f(g):
        g = copy.deepcopy(g)
        T = max(100, int(round(g["time"]["lifetime"] * m)))
        g["time"]["lifetime"] = g["time"]["lifetime2"] = T
        return g
    return f


# name -> (ordered, [(level label, transform)])
AXES = {
    "memory_ratio": (True, [(f"band={b}", _set(("memory", "band"), b)) for b in (0.5, 0.25, 0.1, 0.03, 0.01, 0.003)]),
    "change_timescale": (True, [("static", _drift(None))] + [(f"drift.3/p{p}", _drift(p)) for p in (800, 200, 50, 12)]),
    "information_cost": (True, [(f"x{m}", _mul(INFO_COSTS, m)) for m in (0.1, 1, 10, 100)]),
    "observation_noise": (True, [(f"sd={s}", _set(("observation", "noise_sd"), s)) for s in (0.0, 0.1, 0.3, 1.0, 3.0)]),
    "irreversibility": (True, [(f"door={d}", _set(("irreversibility", "door_close"), d)) for d in (0.0, 0.1, 0.3, 0.6)]),
    "credit_delay": (True, [(f"delay={d}", _set(("credit", "delay"), d)) for d in (0, 4, 16, 64)]),
    "topology": (False, [(k, _topo(k)) for k in ("tensor_index", "ring", "small_world", "erdos", "tree", "scale_free")]),
    "compute_cost": (True, [(f"x{m}", _mul(("p_compute",), m)) for m in (0.1, 1, 10, 100, 1000)]),
    "forgetting": (True, [(f"rate={r}", _forget(r)) for r in (0.0, 0.02, 0.1, 0.3)]),
    "active_sensing": (False, [(p, _set(("search", "policy"), p)) for p in ("random", "greedy", "novelty", "probe_greedy", "rollout")]),
    "recurrence_lifetime": (True, [(f"T x{m}", _life(m)) for m in (4, 2, 1, 0.5, 0.25)]),
}


def grid():
    """-> [(axis, level label, transform)], with ('native', 'native', identity) first."""
    out = [("native", "native", copy.deepcopy)]
    for ax, (_, levels) in AXES.items():
        out += [(ax, lab, f) for lab, f in levels]
    return out
