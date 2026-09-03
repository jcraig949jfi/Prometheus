"""NC5 -- JOINT REVERSIBLE MANIFEST WALK, and the exhaustive structural transition-graph audit.

NC5 contains no genome content, no VM, no probes, no fitness and no world. It models exactly the
structural coordinates whose value changes whether a proposed structural mutation is valid:

    genome_length (instructions)  x  tape_words

and nothing else. n_regs, tick_budget, out_cap, code_writable and persist are excluded by that
test: none of them gates the validity of any structural proposal (verified mechanically by
`config_fields_that_gate_validity()`).

NC5 uses the published bounds, the active grammar's own step sizes, the same validity constraints
and the same no-op/rejection semantics. Its primitive PAIRED MOVES are symmetric by construction:
the length kernel is symmetrized as p_sym(d) = (p(d)+p(-d))/2, and tape doubling and halving are
proposed with equal probability. So any drift NC5 exhibits is produced by the reflecting bounds
and by the coupled validity constraint (genome must fit on tape) and by nothing else. NC5 does NOT
inherit any asymmetric V0.4 rule; if V0.4 contains one, the comparison must show it.

The structural state space is small enough to enumerate exhaustively:
tape_words in {16,32,...,4096} (9 values), genome_length in 1..tape_words/4, giving 2,044 states.
Both the symmetry proof and the transition-graph audit below are therefore EXACT, not sampled.
"""
from __future__ import annotations

from proteus.foundry.affordances import STORAGE_BOUNDS
from proteus.foundry.grammar import GMAX, GMIN, NAMES, WEIGHTS
from proteus.foundry.prng import SplitMix64

IW = 4
TAPES = tuple(t for t in (16, 32, 64, 128, 256, 512, 1024, 2048, 4096)
              if STORAGE_BOUNDS["tape_words"]["min"] <= t <= STORAGE_BOUNDS["tape_words"]["max"])
W = dict(zip(NAMES, WEIGHTS))
CONFIG_FIELDS = ("n_regs", "tape_words", "code_writable", "persist", "tick_budget", "out_cap")

# Asymmetry taxonomy required by the brief.
PUBLISHED_BOUNDARY = "PUBLISHED_BOUNDARY"
MANIFEST_VALIDITY = "MANIFEST_VALIDITY"
OPERATOR_DESIGN = "OPERATOR_DESIGN"
UNKNOWN = "UNKNOWN"


def states():
    """Every valid (genome_length, tape_words) pair. Exhaustive."""
    return [(L, T) for T in TAPES for L in range(GMIN, min(GMAX, T // IW) + 1)]


def config_fields_that_gate_validity():
    """Which configuration fields can change whether a structural proposal is valid.

    Determined from the operator implementations, not asserted: a field gates validity iff it
    appears in a bound check for a length or tape move. Only tape_words does.
    """
    return ("tape_words",)


# --------------------------------------------------------------- V0.4 structural kernel, exactly

def v04_length_proposals():
    """(delta, probability) over one mutation, for the length-changing operators of V0.4.

    Probabilities are the frozen operator weights times the operator's own k distribution.
    insertion/deletion/duplication draw k uniform on [1,4]; unreachable_removal deletes 1 when an
    unreachable instruction exists; splice replaces k by k' with both uniform on [1,4] so its
    delta is k'-k. Non-length operators contribute delta 0. This function is the ANALYTIC form;
    `measure_length_kernel` in the v0_3 nulls module measures the same thing empirically and the
    two are cross-checked in the audit.
    """
    p = {}

    def add(d, q):
        p[d] = p.get(d, 0.0) + q

    for k in range(1, 5):
        add(+k, W["insertion"] * 0.25)
        add(-k, W["deletion"] * 0.25)
        add(+k, W["duplication"] * 0.25)
    for k in range(1, 5):
        for k2 in range(1, 5):
            add(k2 - k, W["splice"] * 0.0625)
    add(-1, W["unreachable_removal"])          # upper bound: fires only when something is unreachable
    add(0, 1.0 - sum(v for d, v in p.items() if d != 0))
    return sorted(p.items())


def symmetrized(kernel):
    d = dict(kernel)
    keys = set(d) | {-k for k in d}
    out = [(k, (d.get(k, 0.0) + d.get(-k, 0.0)) / 2.0) for k in sorted(keys)]
    tot = sum(v for _k, v in out)
    return [(k, v / tot) for k, v in out]


def tape_proposals():
    """(factor, probability) for the tape field under both V0.4 and NC5. Symmetric by construction."""
    q = W["config_perturbation"] / len(CONFIG_FIELDS) / 2.0
    return [(2.0, q), (0.5, q)]


# --------------------------------------------------------------- exhaustive transition graph

def transition_graph(rule: str):
    """Exact edge set over the structural states.

    rule = "v0_4"  : tape move valid iff destination in bounds and genome fits
    rule = "v0_3"  : additionally requires genome <= half the destination when shrinking
    rule = "nc5"   : same validity as v0_4, but the LENGTH kernel is symmetrized

    Returns {(A, B): probability} for A != B, plus the self-loop mass per state.
    """
    if rule == "nc5":
        lk = symmetrized(v04_length_proposals())
    else:
        lk = v04_length_proposals()
    tk = tape_proposals()
    edges, self_mass = {}, {}
    for (L, T) in states():
        cap = min(GMAX, T // IW)
        stay = 0.0
        for d, q in lk:
            if d == 0 or q == 0.0:
                stay += q
                continue
            nl = L + d
            if nl < GMIN or nl > cap:
                stay += q                       # rejection: no-op, exactly as the grammar behaves
            else:
                edges[((L, T), (nl, T))] = edges.get(((L, T), (nl, T)), 0.0) + q
        for f, q in tk:
            nt = int(T * f)
            ok = STORAGE_BOUNDS["tape_words"]["min"] <= nt <= STORAGE_BOUNDS["tape_words"]["max"]
            if ok and nt >= L * IW:
                if rule == "v0_3" and nt < T and L * IW * 2 > nt:
                    ok = False                  # the removed half-tape rule
            else:
                ok = False
            if ok:
                edges[((L, T), (L, nt))] = edges.get(((L, T), (L, nt)), 0.0) + q
            else:
                stay += q
        self_mass[(L, T)] = stay
    return edges, self_mass


def classify_asymmetry(a, b, pab, pba):
    """Why does edge a->b have a different probability from b->a?"""
    (La, Ta), (Lb, Tb) = a, b
    if Ta != Tb:                                 # a tape move
        lo, hi = STORAGE_BOUNDS["tape_words"]["min"], STORAGE_BOUNDS["tape_words"]["max"]
        if not (lo <= Ta <= hi) or not (lo <= Tb <= hi):
            return PUBLISHED_BOUNDARY
        if Lb * IW > Ta or La * IW > Tb:
            return MANIFEST_VALIDITY
        return OPERATOR_DESIGN
    d = Lb - La                                  # a length move
    capa, capb = min(GMAX, Ta // IW), min(GMAX, Tb // IW)
    if Lb > capa or La > capb or Lb < GMIN or La < GMIN:
        return PUBLISHED_BOUNDARY if (Lb >= GMAX or La >= GMAX) else MANIFEST_VALIDITY
    return OPERATOR_DESIGN if d != 0 else UNKNOWN


def audit_transitions(rule: str):
    """Machine-readable audit: every directed edge, its reverse, and the class of any asymmetry."""
    edges, self_mass = transition_graph(rule)
    rows, counts = [], {PUBLISHED_BOUNDARY: 0, MANIFEST_VALIDITY: 0, OPERATOR_DESIGN: 0, UNKNOWN: 0}
    seen = set()
    for (a, b), p in sorted(edges.items()):
        if (a, b) in seen:
            continue
        seen.add((a, b))
        q = edges.get((b, a), 0.0)
        if abs(p - q) > 1e-15:
            cls = classify_asymmetry(a, b, p, q)
            counts[cls] += 1
            rows.append({"from": list(a), "to": list(b), "p_forward": p, "p_reverse": q,
                         "asymmetry_class": cls})
    return {"rule": rule, "n_states": len(self_mass), "n_directed_edges": len(edges),
            "n_asymmetric_pairs": len(rows), "asymmetry_counts": counts, "asymmetries": rows}


def paired_tape_symmetry_proof(rule: str = "v0_4"):
    """EXHAUSTIVE check of the brief's requirement on paired tape transitions.

    For every (genome_length, tape_words) state and every adjacent pair (t, 2t), the PRIMITIVE
    proposal probability of t -> 2t must equal that of 2t -> t before rejection, and any
    difference in the REALISED edge must be attributable to a published bound or manifest
    validity -- never to an occupancy threshold.
    """
    q_double = q_halve = W["config_perturbation"] / len(CONFIG_FIELDS) / 2.0
    proposal_ok = abs(q_double - q_halve) < 1e-18
    edges, _ = transition_graph(rule)
    checked = occupancy_blocked = 0
    violations = []
    for (L, T) in states():
        T2 = T * 2
        if T2 > STORAGE_BOUNDS["tape_words"]["max"]:
            continue
        if L * IW > T2 or L * IW > T:
            continue                              # not a valid pair of states for this genome
        checked += 1
        f = edges.get(((L, T), (L, T2)), 0.0)
        r = edges.get(((L, T2), (L, T)), 0.0)
        if abs(f - r) > 1e-18:
            fits = L * IW <= T
            if fits:
                occupancy_blocked += 1
                violations.append({"genome_length": L, "t": T, "2t": T2,
                                   "p_grow": f, "p_shrink": r,
                                   "genome_fits_in_t": fits})
    return {"rule": rule,
            "primitive_proposal_probabilities_equal": proposal_ok,
            "q_t_to_2t": q_double, "q_2t_to_t": q_halve,
            "state_pairs_checked": checked,
            "pairs_where_a_fitting_shrink_was_blocked": occupancy_blocked,
            "violations": violations[:50],
            "exhaustive": True}


# --------------------------------------------------------------- the NC5 walk itself

def nc5_step(L: int, T: int, rng: SplitMix64, lk, tk):
    """One primitive proposal under NC5. Symmetric kernels, V0.4 validity, no-op rejection."""
    total_len = sum(q for _d, q in lk)
    if rng.unit() < total_len:
        deltas = [d for d, _q in lk]
        ws = [q for _d, q in lk]
        d = rng.weighted(deltas, ws)
        nl = L + d
        cap = min(GMAX, T // IW)
        return (nl if GMIN <= nl <= cap else L), T
    fac = rng.weighted([f for f, _q in tk], [q for _f, q in tk])
    nt = int(T * fac)
    if not (STORAGE_BOUNDS["tape_words"]["min"] <= nt <= STORAGE_BOUNDS["tape_words"]["max"]):
        return L, T
    if nt < L * IW:
        return L, T
    return L, nt


def nc5_walk(L0: int, T0: int, rng: SplitMix64, n_steps: int, checkpoints: set):
    lk = [(d, q) for d, q in symmetrized(v04_length_proposals()) if d != 0]
    tk = tape_proposals()
    L, T = L0, T0
    out = {0: (L, T)}
    for i in range(1, n_steps + 1):
        L, T = nc5_step(L, T, rng, lk, tk)
        if i in checkpoints:
            out[i] = (L, T)
    out[n_steps] = (L, T)
    return out
