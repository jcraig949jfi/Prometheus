"""The structural Markov kernel of the ACTIVE V0.4 grammar, and its equilibrium analysis.

Part II of the V0.5 brief. Nothing here changes the grammar; every number is a measurement of the
frozen v0.4 physics.

STATE. The structural state is (genome_length in instructions, tape_words). Only tape_words gates
structural validity (established in V0.4 and re-asserted here), so no other configuration
coordinate enters. The space is enumerated, not sampled.

KERNEL. P(i -> j) is MEASURED from the live operator rather than modelled: at each state a fresh
uniformly random genome is drawn and one mutation is applied under grammar.mutate, and the
resulting (genome_length, tape_words) is recorded. This marginalises over genome content, which is
the right object for a content-neutral structural analysis, and it removes the model/code gap that
V0.4's analytic NC5 kernel had to declare as a limitation. Self-loops from rejected or no-op
proposals are included, because a rejected proposal is a real transition of this chain.

The V0.4 ANALYTIC kernel is retained for comparison, so the packet can report where the analytic
form used by NC5 was wrong.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict

from proteus.foundry import grammar
from proteus.foundry.affordances import STORAGE_BOUNDS
from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import SCHEMA

IW = 4

# Attribution taxonomy required by brief section 14.
PUBLISHED_BOUNDARY = "PUBLISHED_BOUNDARY"
MANIFEST_VALIDITY_GEOMETRY = "MANIFEST_VALIDITY_GEOMETRY"
OPERATOR_WEIGHTING = "OPERATOR_WEIGHTING"
OPERATOR_STEP_SIZE = "OPERATOR_STEP_SIZE"
OPERATOR_IMPLEMENTATION = "OPERATOR_IMPLEMENTATION"
MULTI_OPERATOR_PATH = "MULTI-OPERATOR_PATH"
UNKNOWN = "UNKNOWN"


def state_space(tapes, max_len):
    """Every valid (L, T). Enumerated. `tapes` is the tape set the analysis covers."""
    return [(L, T) for T in tapes for L in range(1, min(max_len, T // IW) + 1)]


def _manifest(rng, L, T, n_regs=8, persist="none", writable=False, tick=64, cap=4):
    return {"schema_version": SCHEMA, "n_regs": n_regs, "tape_words": T,
            "genome": [rng.next_u32() for _ in range(IW * L)],
            "code_writable": writable, "persist": persist,
            "tick_budget": tick, "out_cap": cap}


def measure_kernel(states, samples, seed, tag="kernel"):
    """Empirical P(i -> j) from the LIVE operator, marginalised over uniform genome content.

    Returns (P, op_counts, trunc) where P[i] is {j: probability} including the self-loop.

    TRUNCATION, declared: when the analysis runs on a proper subset of the true structural space,
    a transition leaving that subset is folded into the SELF-LOOP, i.e. treated as a rejection.
    This adds an artificial reflecting boundary identical IN KIND to the real published boundary
    at tape 4096. It is applied identically to the active kernel and to the reversible reference,
    so the current comparison stays internally valid, and the escaping mass is reported per state
    in `trunc` so a reader can see exactly how much probability the truncation touched.
    """
    P = {}
    op_counts = defaultdict(Counter)
    trunc = {}
    inside = set(states)
    root = SplitMix64(seed_from("proteus.v0_5.kernel", seed, tag))
    for (L, T) in states:
        r = root.derive(L, T)
        c = Counter()
        escaped = 0
        for _ in range(samples):
            m = _manifest(r, L, T)
            mate = _manifest(r, L, T)
            child, rec = grammar.mutate(m, r, mate)
            j = (len(child["genome"]) // IW, child["tape_words"])
            if j not in inside:
                escaped += 1
                j = (L, T)                      # rejection semantics at the truncation boundary
            c[j] += 1
            op_counts[((L, T), j)][rec["operator"]] += 1
        P[(L, T)] = {j: n / samples for j, n in c.items()}
        trunc[(L, T)] = escaped / samples
    return P, {k: dict(v) for k, v in op_counts.items()}, trunc


def analytic_kernel(states):
    """The V0.4 analytic structural kernel, for comparison only (see proteus/v0_4/nc5.py)."""
    from proteus.v0_4 import nc5
    edges, self_mass = nc5.transition_graph("v0_4")
    P = {}
    inside = set(states)
    for s in states:
        row = {}
        esc = 0.0
        for (i, j), p in edges.items():
            if i != s:
                continue
            if j in inside:
                row[j] = row.get(j, 0.0) + p
            else:
                esc += p
        row[s] = row.get(s, 0.0) + self_mass.get(s, 0.0) + esc
        P[s] = row
    return P


def compare_kernels(Pa, Pb, states):
    """Total-variation distance per state between two kernels."""
    out = []
    for s in states:
        a, b = Pa.get(s, {}), Pb.get(s, {})
        keys = set(a) | set(b)
        tv = 0.5 * sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys)
        out.append({"state": list(s), "tv_distance": tv})
    out.sort(key=lambda d: -d["tv_distance"])
    return out


# ----------------------------------------------------------------- communicating structure

def communicating_classes(P, states):
    """Tarjan SCCs over the directed support of P (self-loops ignored for reachability)."""
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
    stack, order, out = [], [0], []
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
                u = work[-1][0]
                low[u] = min(low[u], low[v])
    del order
    return out


def closed_classes(P, classes, states):
    """A class is closed (recurrent) if no edge leaves it."""
    member = {}
    for k, comp in enumerate(classes):
        for s in comp:
            member[s] = k
    closed = []
    for k, comp in enumerate(classes):
        leaves = any(member.get(j) not in (k, None) and p > 0
                     for s in comp for j, p in P[s].items())
        closed.append(not leaves)
    return closed


# ----------------------------------------------------------------- stationary distribution

def stationary(P, states, iters=200000, tol=1e-14):
    """Power iteration for pi = pi P. Returns (pi, iterations_used, final_l1_change)."""
    n = len(states)
    idx = {s: i for i, s in enumerate(states)}
    rows = [[(idx[j], p) for j, p in P[s].items() if j in idx and p > 0] for s in states]
    pi = [1.0 / n] * n
    used, delta = 0, 0.0
    for it in range(iters):
        nxt = [0.0] * n
        for i, row in enumerate(rows):
            pv = pi[i]
            if pv == 0.0:
                continue
            for j, p in row:
                nxt[j] += pv * p
        tot = sum(nxt)
        if tot > 0:
            nxt = [x / tot for x in nxt]
        delta = sum(abs(a - b) for a, b in zip(nxt, pi))
        pi = nxt
        used = it + 1
        if delta < tol:
            break
    return {s: pi[idx[s]] for s in states}, used, delta


def second_eigenvalue_estimate(P, states, pi, iters=400):
    """Crude SLEM estimate by power iteration on the pi-orthogonal complement."""
    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    rows = [[(idx[j], p) for j, p in P[s].items() if j in idx and p > 0] for s in states]
    v = [((i * 2654435761) % 1000) / 1000.0 - 0.5 for i in range(n)]
    piv = [pi[s] for s in states]
    prev = 0.0
    for _ in range(iters):
        m = sum(a * b for a, b in zip(v, piv))
        v = [x - m for x in v]
        nxt = [0.0] * n
        for i, row in enumerate(rows):
            vv = v[i]
            if vv == 0.0:
                continue
            for j, p in row:
                nxt[j] += vv * p
        nrm = math.sqrt(sum(x * x for x in nxt))
        if nrm < 1e-300:
            return 0.0
        prev = nrm
        v = [x / nrm for x in nxt]
    return prev


# ----------------------------------------------------------------- currents

def currents(P, pi, states):
    """J(i,j) = pi_i P_ij - pi_j P_ji for every connected unordered pair, i != j."""
    seen = set()
    rows = []
    for i in states:
        for j, p in P[i].items():
            if j == i or j not in pi:
                continue
            key = (i, j) if i <= j else (j, i)
            if key in seen:
                continue
            seen.add(key)
            a, b = key
            fij = pi[a] * P[a].get(b, 0.0)
            fji = pi[b] * P[b].get(a, 0.0)
            rows.append({"i": list(a), "j": list(b), "flux_ij": fij, "flux_ji": fji,
                         "J": fij - fji,
                         "one_way": (P[a].get(b, 0.0) > 0) != (P[b].get(a, 0.0) > 0)})
    del p
    return rows


def attribute_edge(i, j, op_counts, tapes, max_len):
    """Attribution taxonomy for one directed edge (brief section 14)."""
    (La, Ta), (Lb, Tb) = i, j
    if Ta != Tb:
        lo, hi = STORAGE_BOUNDS["tape_words"]["min"], STORAGE_BOUNDS["tape_words"]["max"]
        if Tb * 2 > hi or Tb // 2 < lo or Ta * 2 > hi or Ta // 2 < lo:
            return PUBLISHED_BOUNDARY
        if Lb * IW > Ta or La * IW > Tb:
            return MANIFEST_VALIDITY_GEOMETRY
        return OPERATOR_IMPLEMENTATION
    cap_a = min(max_len, Ta // IW)
    if Lb > cap_a or Lb < 1 or La > cap_a or La < 1:
        return MANIFEST_VALIDITY_GEOMETRY
    ops_f = set(op_counts.get((i, j), {}))
    ops_r = set(op_counts.get((j, i), {}))
    if ops_f != ops_r and ops_f and ops_r:
        return OPERATOR_WEIGHTING
    if abs(Lb - La) > 4:
        return OPERATOR_STEP_SIZE
    if ops_f and not ops_r:
        return OPERATOR_IMPLEMENTATION
    return OPERATOR_WEIGHTING


def entropy_production(P, pi, states):
    """Stationary entropy-production rate. Zero-reverse edges are reported, never smoothed."""
    total = 0.0
    one_way = []
    n_terms = 0
    for i in states:
        for j, pij in P[i].items():
            if j == i or pij <= 0 or j not in pi:
                continue
            f = pi[i] * pij
            pji = P[j].get(i, 0.0)
            b = pi[j] * pji
            if b <= 0:
                one_way.append({"i": list(i), "j": list(j), "forward_flux": f})
                continue
            total += f * math.log(f / b)
            n_terms += 1
    return {"sigma": total, "n_terms": n_terms,
            "one_way_edges": len(one_way),
            "one_way_forward_flux_total": sum(e["forward_flux"] for e in one_way),
            "sigma_is_infinite_if_one_way_edges_carry_flux": bool(one_way),
            "one_way_examples": one_way[:25]}


# ----------------------------------------------------------------- reversible reference

def reversible_reference(P, pi, states):
    """A detailed-balance kernel on the SAME support with the SAME invariant distribution pi.

    Construction: Q(i,j) = (pi_i P_ij + pi_j P_ji) / (2 pi_i) for i != j, with the remainder on
    the self-loop. Then pi_i Q_ij = pi_j Q_ji exactly, so Q is reversible with respect to pi and
    leaves pi invariant. Local connectivity is preserved: Q_ij > 0 iff P_ij > 0 or P_ji > 0.

    This is a CONTROL. It is not tuned toward or away from any V0.4 result: it is the unique
    additive symmetrisation of the stationary flux, and the invariant distribution it targets is
    the measured pi of the active kernel, stated here as the brief requires.
    """
    Q = {}
    for i in states:
        row = {}
        nbrs = set(P[i]) | {j for j in states if i in P.get(j, {})}
        for j in nbrs:
            if j == i or j not in pi:
                continue
            f = pi[i] * P[i].get(j, 0.0)
            b = pi[j] * P[j].get(i, 0.0)
            if pi[i] > 0:
                q = (f + b) / (2.0 * pi[i])
                if q > 0:
                    row[j] = q
        s = sum(row.values())
        if s > 1.0:
            row = {k: v / s for k, v in row.items()}
            s = 1.0
        row[i] = 1.0 - s
        Q[i] = row
    return Q


def simulate(P, states, start, steps, rng, record_every=1):
    """Trajectory under an explicit kernel. Returns occupancy counters and transition tallies."""
    idx = {s: i for i, s in enumerate(states)}
    rows = {s: (list(P[s].keys()), list(P[s].values())) for s in states}
    cur = start
    occ = Counter()
    length_up = length_dn = tape_up = tape_dn = 0
    first_passage = {}
    for t in range(1, steps + 1):
        ks, ws = rows[cur]
        nxt = rng.weighted(ks, ws)
        if nxt != cur:
            if nxt[0] > cur[0]:
                length_up += 1
            elif nxt[0] < cur[0]:
                length_dn += 1
            if nxt[1] > cur[1]:
                tape_up += 1
            elif nxt[1] < cur[1]:
                tape_dn += 1
        cur = nxt
        if t % record_every == 0:
            occ[cur] += 1
        if cur not in first_passage:
            first_passage[cur] = t
    del idx
    return {"occupancy": occ, "length_up": length_up, "length_down": length_dn,
            "tape_up": tape_up, "tape_down": tape_dn,
            "states_visited": len(first_passage),
            "mean_first_passage_observed": (sum(first_passage.values()) / len(first_passage))
            if first_passage else None,
            "final": cur}
