"""Equilibrium analysis for V0.6: stationary solvers, currents, cycle basis, references.

Everything here operates on a kernel supplied as {state: {state: probability}}. It never touches
the grammar. Three design points the V0.6 brief demands:

  * at least two NUMERICALLY INDEPENDENT stationary solvers plus an external empirical check;
  * a noise model built from replicated kernel estimation rather than a single same-kernel max;
  * a cycle basis (spanning tree + fundamental cycles) rather than a 3-cycle census.

Float accumulation uses math.fsum wherever a sum feeds an adjudicated quantity, so the result does
not depend on CPython's sum() semantics -- the V0.5 cross-runtime defect.
"""
from __future__ import annotations

import math
import random
from collections import Counter, defaultdict, deque

# --------------------------------------------------------------- structure


def communicating_classes(P, states):
    """Tarjan SCC over the directed support, iterative."""
    idx = {s: i for i, s in enumerate(states)}
    adj = [[] for _ in states]
    for s in states:
        for j, p in P[s].items():
            if p > 0 and j != s and j in idx:
                adj[idx[s]].append(idx[j])
    n = len(states)
    index = [None] * n
    low = [0] * n
    on = [False] * n
    stack, out = [], []
    counter = [0]
    for root in range(n):
        if index[root] is not None:
            continue
        work = [(root, 0)]
        while work:
            v, pi = work[-1]
            if pi == 0:
                index[v] = low[v] = counter[0]
                counter[0] += 1
                stack.append(v)
                on[v] = True
            recurse = False
            for i in range(pi, len(adj[v])):
                w = adj[v][i]
                if index[w] is None:
                    work[-1] = (v, i + 1)
                    work.append((w, 0))
                    recurse = True
                    break
                if on[w]:
                    low[v] = min(low[v], index[w])
            if recurse:
                continue
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on[w] = False
                    comp.append(states[w])
                    if w == v:
                        break
                out.append(comp)
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
    return out


def closed_classes(P, classes):
    member = {}
    for k, comp in enumerate(classes):
        for s in comp:
            member[s] = k
    return [not any(member.get(j) not in (k, None) and p > 0
                    for s in comp for j, p in P[s].items())
            for k, comp in enumerate(classes)]


# --------------------------------------------------------------- stationary solvers


def _rows(P, states):
    idx = {s: i for i, s in enumerate(states)}
    return idx, [[(idx[j], p) for j, p in P[s].items() if j in idx and p > 0] for s in states]


def residual_l1(P, states, pi):
    """||pi P - pi||_1, computed with fsum so it is solver- and runtime-independent."""
    idx, rows = _rows(P, states)
    acc = [[] for _ in states]
    for i, row in enumerate(rows):
        v = pi[states[i]]
        if v == 0.0:
            continue
        for j, p in row:
            acc[j].append(v * p)
    return math.fsum(abs(math.fsum(acc[j]) - pi[states[j]]) for j in range(len(states)))


def stationary_power(P, states, tol=1e-14, max_iters=2_000_000):
    """Method 1: power iteration with fsum normalisation and an L1 residual target."""
    idx, rows = _rows(P, states)
    n = len(states)
    pi = [1.0 / n] * n
    it = 0
    for it in range(1, max_iters + 1):
        nxt = [0.0] * n
        for i, row in enumerate(rows):
            v = pi[i]
            if v == 0.0:
                continue
            for j, p in row:
                nxt[j] += v * p
        tot = math.fsum(nxt)
        if tot > 0:
            nxt = [x / tot for x in nxt]
        d = math.fsum(abs(a - b) for a, b in zip(nxt, pi))
        pi = nxt
        if d < tol:
            break
    out = {s: pi[idx[s]] for s in states}
    return out, {"method": "power_iteration", "iterations": it, "last_l1_change": d,
                 "residual_l1": residual_l1(P, states, out)}


def stationary_gauss_seidel(P, states, tol=1e-14, max_iters=200_000):
    """Method 2: Gauss-Seidel style in-place sweeps on pi_j = sum_i pi_i P_ij.

    Numerically independent of method 1: it updates in place in a fixed order and uses the
    incoming-edge representation, so the arithmetic path differs entirely.
    """
    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    incoming = [[] for _ in states]
    self_p = [0.0] * n
    for s in states:
        i = idx[s]
        for j, p in P[s].items():
            if j not in idx or p <= 0:
                continue
            if j == s:
                self_p[i] = p
            else:
                incoming[idx[j]].append((i, p))
    pi = [1.0 / n] * n
    it = 0
    for it in range(1, max_iters + 1):
        prev = list(pi)
        for j in range(n):
            s = math.fsum(pi[i] * p for i, p in incoming[j])
            denom = 1.0 - self_p[j]
            pi[j] = (s / denom) if denom > 1e-300 else pi[j]
        tot = math.fsum(pi)
        if tot > 0:
            pi = [x / tot for x in pi]
        d = math.fsum(abs(a - b) for a, b in zip(pi, prev))
        if d < tol:
            break
    out = {s: pi[idx[s]] for s in states}
    return out, {"method": "gauss_seidel", "iterations": it, "last_l1_change": d,
                 "residual_l1": residual_l1(P, states, out)}


def stationary_empirical(P, states, steps, seed):
    """Method 3: long-run empirical occupancy. An external check with its own sampling error."""
    rnd = random.Random(seed)
    keys = {s: list(P[s].keys()) for s in states}
    cw = {}
    for s in states:
        acc, c = 0.0, []
        for j in keys[s]:
            acc += P[s][j]
            c.append(acc)
        cw[s] = c
    cur = states[0]
    occ = Counter()
    for _ in range(steps):
        u = rnd.random() * cw[cur][-1]
        ks, c = keys[cur], cw[cur]
        lo, hi = 0, len(c) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if u <= c[mid]:
                hi = mid
            else:
                lo = mid + 1
        cur = ks[lo]
        occ[cur] += 1
    return {s: occ[s] / steps for s in states}, {"method": "empirical_occupancy", "steps": steps}


def compare_pi(a, b, states):
    l1 = math.fsum(abs(a[s] - b[s]) for s in states)
    mx = max(abs(a[s] - b[s]) for s in states)
    rel = max(abs(a[s] - b[s]) / max(a[s], 1e-300) for s in states)
    return {"l1": l1, "max_abs": mx, "max_rel": rel}


def spectral_gap(P, states, pi, iters=600):
    """SLEM estimate by deflated power iteration; 1 - |lambda_2| is the gap."""
    idx, rows = _rows(P, states)
    n = len(states)
    v = [((i * 2654435761) % 100003) / 100003.0 - 0.5 for i in range(n)]
    piv = [pi[s] for s in states]
    lam = 0.0
    for _ in range(iters):
        m = math.fsum(x * y for x, y in zip(v, piv))
        v = [x - m for x in v]
        nxt = [0.0] * n
        for i, row in enumerate(rows):
            x = v[i]
            if x == 0.0:
                continue
            for j, p in row:
                nxt[j] += x * p
        nrm = math.sqrt(math.fsum(x * x for x in nxt))
        if nrm < 1e-300:
            return {"slem": 0.0, "spectral_gap": 1.0}
        lam = nrm
        v = [x / nrm for x in nxt]
    return {"slem": lam, "spectral_gap": 1.0 - lam}


# --------------------------------------------------------------- currents


def currents(P, pi, states):
    """J(i,j) for every connected unordered pair, i != j."""
    seen = set()
    out = []
    for i in states:
        for j in P[i]:
            if j == i or j not in pi:
                continue
            key = (i, j) if i <= j else (j, i)
            if key in seen:
                continue
            seen.add(key)
            a, b = key
            fab = pi[a] * P[a].get(b, 0.0)
            fba = pi[b] * P[b].get(a, 0.0)
            out.append({"i": a, "j": b, "f_ij": fab, "f_ji": fba, "J": fab - fba,
                        "one_way": (P[a].get(b, 0.0) > 0) != (P[b].get(a, 0.0) > 0)})
    return out


def current_summary(cur, pi):
    js = [abs(r["J"]) for r in cur]
    tot = math.fsum(js)
    return {"n_pairs": len(cur), "total_abs": tot, "mean_abs": tot / max(1, len(cur)),
            "max_abs": max(js) if js else 0.0,
            "one_way_pairs": sum(1 for r in cur if r["one_way"])}


def entropy_production(P, pi, states):
    """Stationary entropy production; one-way edges reported, never smoothed."""
    terms = []
    one_way = []
    by_edge = []
    for i in states:
        for j, pij in P[i].items():
            if j == i or pij <= 0 or j not in pi:
                continue
            f = pi[i] * pij
            pji = P[j].get(i, 0.0)
            if pji <= 0:
                one_way.append({"i": i, "j": j, "forward_flux": f})
                continue
            b = pi[j] * pji
            t = f * math.log(f / b)
            terms.append(t)
            by_edge.append(((i, j), t))
    return {"sigma": math.fsum(terms), "n_terms": len(terms),
            "one_way_edges": len(one_way),
            "one_way_flux_total": math.fsum(e["forward_flux"] for e in one_way),
            "one_way_examples": [{"i": list(e["i"]), "j": list(e["j"]),
                                  "forward_flux": e["forward_flux"]} for e in one_way[:25]],
            "_by_edge": by_edge}


# --------------------------------------------------------------- cycle basis


def cycle_basis(P, states):
    """Fundamental cycle basis from a BFS spanning tree of the undirected support."""
    nbr = defaultdict(set)
    for i in states:
        for j, p in P[i].items():
            if j != i and p > 0 and j in P:
                nbr[i].add(j)
                nbr[j].add(i)
    parent, seen, order = {}, set(), []
    for root in states:
        if root in seen:
            continue
        seen.add(root)
        parent[root] = None
        q = deque([root])
        while q:
            v = q.popleft()
            order.append(v)
            for w in sorted(nbr[v]):
                if w not in seen:
                    seen.add(w)
                    parent[w] = v
                    q.append(w)
    tree = set()
    for v, p in parent.items():
        if p is not None:
            tree.add((v, p) if v <= p else (p, v))
    cycles = []
    done = set()
    for v in states:
        for w in sorted(nbr[v]):
            e = (v, w) if v <= w else (w, v)
            if e in tree or e in done:
                continue
            done.add(e)
            # path to root for each endpoint
            def up(x):
                out = [x]
                while parent.get(x) is not None:
                    x = parent[x]
                    out.append(x)
                return out
            a, b = up(v), up(w)
            sa = {x: i for i, x in enumerate(a)}
            lca_i = None
            for i, x in enumerate(b):
                if x in sa:
                    lca_i = i
                    break
            if lca_i is None:
                continue
            cyc = a[:sa[b[lca_i]] + 1] + list(reversed(b[:lca_i]))
            if len(cyc) >= 3:
                cycles.append(cyc)
    return cycles, len(tree)


def cycle_affinity(P, cyc):
    """sum log(P_ij / P_ji) around the directed cycle. Zero for all cycles iff reversible."""
    a = 0.0
    for k in range(len(cyc)):
        x, y = cyc[k], cyc[(k + 1) % len(cyc)]
        f, r = P[x].get(y, 0.0), P[y].get(x, 0.0)
        if f <= 0 or r <= 0:
            return None
        a += math.log(f / r)
    return a


# --------------------------------------------------------------- references


def reversible_additive(P, pi, states):
    """Q(i,j) = (pi_i P_ij + pi_j P_ji) / (2 pi_i). Detailed balance exact; targets the given pi."""
    Q = {}
    incoming = defaultdict(set)
    for i in states:
        for j in P[i]:
            if j != i:
                incoming[j].add(i)
    for i in states:
        row = {}
        for j in set(P[i]) | incoming[i]:
            if j == i or j not in pi:
                continue
            f = pi[i] * P[i].get(j, 0.0)
            b = pi[j] * P[j].get(i, 0.0)
            if pi[i] > 0:
                q = (f + b) / (2.0 * pi[i])
                if q > 0:
                    row[j] = q
        s = math.fsum(row.values())
        if s > 1.0:
            row = {k: v / s for k, v in row.items()}
            s = 1.0
        row[i] = 1.0 - s
        Q[i] = row
    return Q


def reversible_metropolis(P, states, target=None):
    """Metropolis-Hastings on the SAME undirected support, targeting a declared measure.

    Proposal: uniform over the support neighbours of i, so q(i->j) = 1/k_i. Because k_i and k_j
    differ, the proposal is ASYMMETRIC and the acceptance must carry the Hastings ratio:

        a(i->j) = min(1, (tgt_j * q(j->i)) / (tgt_i * q(i->j)))
                = min(1, (tgt_j * k_i) / (tgt_i * k_j))

    Using the plain Metropolis form min(1, tgt_j/tgt_i) here is a BUG: it does not satisfy
    detailed balance on an irregular graph, and it made this control converge to something other
    than its declared target. That is exactly what a control must not do, and it was caught by
    test_metropolis_reference_targets_uniform_and_is_reversible before the production run.

    Default target is UNIFORM over the valid states -- declared, and independent of anything
    measured from the active process.
    """
    nbr = {i: sorted({j for j in P[i] if j != i}) for i in states}
    deg = {i: len(nbr[i]) for i in states}
    tgt = target or {s: 1.0 / len(states) for s in states}
    Q = {}
    for i in states:
        row = {}
        k = deg[i]
        stay = 0.0
        for j in nbr[i]:
            q = 1.0 / k
            if tgt[i] > 0 and deg[j] > 0:
                a = min(1.0, (tgt[j] * k) / (tgt[i] * deg[j]))
            else:
                a = 1.0
            if q * a > 0:
                row[j] = q * a
            stay += q * (1.0 - a)
        row[i] = stay + (0.0 if k else 1.0)
        Q[i] = row
    return Q, tgt
