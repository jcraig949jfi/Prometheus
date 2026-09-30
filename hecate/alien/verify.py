"""Mechanical ground truth: exhaustive property checks over the whole state
space, a mechanical analogue check against known templates, and nuisance
statistics for matching nulls. No model is consulted anywhere here.
"""

from __future__ import annotations

import zlib

import numpy as np

from hecate.alien.systems import all_states, dims_of, index, n_states, step


def table(p):
    """Full transition table as an int array over state indices."""
    dims = dims_of(p)
    states = all_states(dims)
    return np.array([index(step(p, s), dims) for s in states]), states, dims


# ---- property checks (each returns True/False over ALL states) -----------

def conserved_linear(p, w, mod, offset=0, tbl=None):
    """sum(w_i s_i) mod `mod` conserved (offset 0) or advanced by `offset`."""
    t, states, dims = tbl or table(p)
    for i, s in enumerate(states):
        s2 = states[t[i]]
        a = sum(wi * v for wi, v in zip(w, s)) % mod
        b = sum(wi * v for wi, v in zip(w, s2)) % mod
        if b != (a + offset) % mod:
            return False
    return True


def bijective(p, tbl=None):
    t, _, _ = tbl or table(p)
    return len(set(t.tolist())) == len(t)


def orbit_structure(p, tbl=None):
    """Attractors (cycles), their periods, max transient, fixed fraction."""
    t, _, _ = tbl or table(p)
    n = len(t)
    mark = np.zeros(n, dtype=int)        # 0 new, 1 on current path, 2 done
    oncycle = np.zeros(n, dtype=bool)
    periods = []
    for s0 in range(n):
        if mark[s0]:
            continue
        path, x = [], s0
        while mark[x] == 0:
            mark[x] = 1
            path.append(x)
            x = int(t[x])
        if mark[x] == 1:
            cyc = path[path.index(x):]
            periods.append(len(cyc))
            oncycle[cyc] = True
        for v in path:
            mark[v] = 2
    dist = _dist_to_cycle(t, set(np.nonzero(oncycle)[0].tolist()))
    return {"n_attractors": len(periods), "periods": sorted(periods),
            "max_transient": int(dist.max()),
            "fixed_fraction": float(np.mean(t == np.arange(n)))}


def _dist_to_cycle(t, cyc):
    n = len(t)
    dist = np.full(n, -1)
    for c in cyc:
        dist[c] = 0
    for s in range(n):
        path = []
        x = s
        while dist[x] == -1:
            path.append(x)
            x = t[x]
        d = dist[x]
        for v in reversed(path):
            d += 1
            dist[v] = d
    return dist


def commutes_with(p, sigma, tbl=None):
    """f(sigma(s)) == sigma(f(s)) for all s."""
    t, states, dims = tbl or table(p)
    for i, s in enumerate(states):
        if step(p, sigma(s)) != sigma(states[t[i]]):
            return False
    return True


def invariant_set(p, member, tbl=None):
    t, states, _ = tbl or table(p)
    return all(member(states[t[i]]) for i, s in enumerate(states) if member(s))


def is_affine(p, mod, tbl=None):
    """True iff f(s) = A s + b (mod `mod`) for some A, b (all components)."""
    t, states, dims = tbl or table(p)
    if len(set(dims)) != 1 or dims[0] != mod:
        return False
    n = len(dims)
    zero = tuple([0] * n)
    b = np.array(step(p, zero))
    A = np.zeros((n, n), dtype=int)
    for j in range(n):
        e = [0] * n
        e[j] = 1
        A[:, j] = (np.array(step(p, tuple(e))) - b) % mod
    for i, s in enumerate(states):
        if not np.array_equal((A @ np.array(s) + b) % mod, np.array(states[t[i]])):
            return False
    return True


def agreement(p, q, tbl_p=None):
    """Fraction of states on which two systems agree (same state space)."""
    tp, states, dims = tbl_p or table(p)
    tq, _, _ = table(q)
    return float(np.mean(tp == tq))


# ---- nuisance statistics ---------------------------------------------------

def nuisance(p, obs_text, tbl=None):
    t, states, dims = tbl or table(p)
    arr = np.array(states)
    nxt = arr[t]
    changed = float(np.mean(arr != nxt))
    circ = np.minimum((nxt - arr) % np.array(dims), (arr - nxt) % np.array(dims))
    ob = orbit_structure(p, (t, states, dims))
    raw = obs_text.encode("utf-8")
    return {
        "frac_components_changing": round(changed, 4),
        "mean_circular_step": round(float(np.mean(circ)), 4),
        "image_fraction": round(len(set(t.tolist())) / len(t), 4),
        "fixed_fraction": round(ob["fixed_fraction"], 4),
        "n_attractors": ob["n_attractors"],
        "max_period": max(ob["periods"]),
        "max_transient": ob["max_transient"],
        "obs_compression_ratio": round(len(zlib.compress(raw, 9)) / max(1, len(raw)), 4),
        "n_states": n_states(dims),
    }
