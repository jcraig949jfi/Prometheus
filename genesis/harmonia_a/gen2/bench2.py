#!/usr/bin/env python
"""
HARMONIA A GEN-2 -- the ruler problem: adversarial battery + candidates.

Constructs the frozen battery cells on real Gen-1 circuit objects (plus
synthesized truth-table objects where the ruler's representation-blindness
makes circuit origin irrelevant and the population is scarce), classifies
every cell under the four candidate rulers, and re-scores all Gen-1 NAT
rows under R_VEC by regenerating the Gen-1 edit streams deterministically.

Rulers see BEHAVIOR ONLY (a pair of 1024-bit functions). FAULT is a
declared class this substrate cannot exercise.
"""

import json
import sys

import numpy as np

N = 10
DOM = 1 << N
G = 24
EPS_TRIV = 0.025          # half the population balance-band floor (0.05)
LOCAL_BAND = 0.25
GEN1 = "../gen1/results/objects.jsonl"

INPUT_COLS = ((np.arange(DOM)[:, None] >> np.arange(N)) & 1).astype(bool)


# ---------------- Gen-0/1 verbatim circuit layer (provenance: gen1/bench1.py)

def gate_eval(op, a, b):
    if op == 0:
        return a & b
    if op == 1:
        return a | b
    if op == 2:
        return a ^ b
    return ~(a & b)


def eval_wires(gates, perm=None):
    wires = [INPUT_COLS[:, perm[i] if perm is not None else i]
             for i in range(N)]
    for op, a, b in gates:
        wires.append(gate_eval(op, wires[a], wires[b]))
    return wires


def circuit_edit_space(gates):
    edits = []
    for gi, (op, a, b) in enumerate(gates):
        for new_op in range(4):
            if new_op != op:
                edits.append(("op", gi, new_op))
        nw = N + gi
        for slot in (0, 1):
            cur = (a, b)[slot]
            for w in range(nw):
                if w != cur:
                    edits.append(("wire", gi, (slot, w)))
    return edits


def apply_edit(gates, edit):
    kind, gi, payload = edit
    out = list(gates)
    op, a, b = out[gi]
    if kind == "op":
        out[gi] = (payload, a, b)
    else:
        slot, w = payload
        out[gi] = (op, w, b) if slot == 0 else (op, a, w)
    return out


def rng_for(*key):
    return np.random.default_rng(np.random.SeedSequence(list(key)))


# ---------------- behavior helpers

def minmass(f):
    m = float(f.mean())
    return min(m, 1.0 - m)


def minority_support(f):
    """Deterministic tie rule: mean <= 0.5 -> ones-support."""
    return f if f.mean() <= 0.5 else ~f


def d_of(f, g):
    return float(np.count_nonzero(f != g)) / DOM


def surv_of(f, g):
    S, T = minority_support(f), minority_support(g)
    u = np.count_nonzero(S | T)
    return float(np.count_nonzero(S & T)) / u if u else 1.0


# ---------------- candidate rulers: (f, f') -> class string

def r_ham(f, g):
    d = d_of(f, g)
    if d == 0.0:
        return "NEUTRAL"
    return "SMALL" if d <= LOCAL_BAND else "LARGE"


def r_rel(f, g):
    d = d_of(f, g)
    if d == 0.0:
        return "NEUTRAL"
    s = d / max(minmass(f), 1.0 / DOM)
    if s >= 1.0:
        return "DESTRUCTION"
    return "SMALL" if s <= 0.5 else "LARGE"


def r_nmi(f, g):
    if np.array_equal(f, g):
        return "NEUTRAL"
    # mutual information over uniform x, in bits
    p = np.zeros((2, 2))
    p[0, 0] = np.mean(~f & ~g)
    p[0, 1] = np.mean(~f & g)
    p[1, 0] = np.mean(f & ~g)
    p[1, 1] = np.mean(f & g)
    pf, pg = p.sum(1), p.sum(0)
    mi = 0.0
    for i in range(2):
        for j in range(2):
            if p[i, j] > 0:
                mi += p[i, j] * np.log2(p[i, j] / (pf[i] * pg[j]))
    hmax = 0.0
    for q in (pf, pg):
        h = -sum(x * np.log2(x) for x in q if x > 0)
        hmax = max(hmax, h)
    u = 1.0 - (mi / hmax if hmax > 0 else 0.0)
    if u <= 1e-9:
        return "NEUTRAL"           # deterministic relation (incl. complement)
    if u >= 0.9:
        return "DESTRUCTION"
    return "SMALL" if u <= 0.5 else "LARGE"


def r_vec(f, g):
    if np.array_equal(f, g):
        return "NEUTRAL"
    if minmass(g) <= EPS_TRIV:
        return "DESTRUCTION"
    d = d_of(f, g)
    return "SMALL" if (d <= LOCAL_BAND and surv_of(f, g) >= 0.5) else "LARGE"


RULERS = dict(R_HAM=r_ham, R_REL=r_rel, R_NMI=r_nmi, R_VEC=r_vec)


# ---------------- object pools

def load_gen1_objects():
    objs = []
    for line in open(GEN1):
        o = json.loads(line)
        gates = [tuple(g) for g in o["gates"]]
        f = eval_wires(gates)[-1].copy()
        objs.append(dict(id=f"g1_{o['seed']}_{o['level']}_{o['obj']}",
                         gates=gates, f=f, bal=float(f.mean())))
    return objs


def synth_object(rng, lo, hi):
    """Direct truth-table object with minority mass in [lo, hi]; rulers are
    representation-blind so circuit origin is unnecessary for pair cells."""
    m = float(rng.uniform(lo, hi))
    k = int(round(m * DOM))
    f = np.zeros(DOM, bool)
    f[rng.choice(DOM, size=k, replace=False)] = True
    return dict(id=f"synth_m{k}", gates=None, f=f, bal=float(f.mean()))


def build_pools():
    g1 = load_gen1_objects()
    balanced = [o for o in g1 if 0.45 <= o["bal"] <= 0.55][:20]
    unbal = [o for o in g1 if 0.05 <= o["bal"] <= 0.15
             or 0.85 <= o["bal"] <= 0.95][:20]
    rng = rng_for(777, 1)
    while len(balanced) < 20:
        balanced.append(synth_object(rng, 0.45, 0.55))
    while len(unbal) < 20:
        unbal.append(synth_object(rng, 0.055, 0.15))
    # N1 pair needs an object with minmass in [0.055, 0.0625]
    n1 = next((o for o in unbal
               if 0.055 <= minmass(o["f"]) <= 0.0625), None)
    if n1 is None:
        n1 = synth_object(rng, 0.057, 0.061)
        unbal.append(n1)
    return balanced, unbal, n1, sum(o["gates"] is not None for o in balanced)


# ---------------- battery cells

def flip_k(f, k, rng):
    g = f.copy()
    idx = rng.choice(DOM, size=k, replace=False)
    g[idx] = ~g[idx]
    return g


def build_cells():
    balanced, unbal, n1obj, n_circ_bal = build_pools()
    cells = []
    rng = rng_for(777, 2)

    def add(cid, ctype, o, g, req):
        cells.append(dict(cell=cid, type=ctype, obj=o["id"],
                          parent_bal=round(o["bal"], 4),
                          mm_child=round(minmass(g), 4),
                          d=round(d_of(o["f"], g), 5),
                          surv=round(surv_of(o["f"], g), 4),
                          required=req,
                          classes={name: fn(o["f"], g)
                                   for name, fn in RULERS.items()}))

    for i, o in enumerate(balanced):
        for k in (1, 4, 8, 60):
            add(f"C1_k{k}_{i}", "balanced_flip", o,
                flip_k(o["f"], k, rng), {"must_be": "SMALL", "axiom": "AX3"})
        maj = o["f"].mean() > 0.5
        add(f"C2_{i}", "balanced_collapse", o,
            np.full(DOM, maj, bool), {"must_be": "DESTRUCTION",
                                      "axiom": "AX2"})
        add(f"C10_{i}", "healthy_replacement", o,
            synth_object(rng_for(777, 3, i), 0.45, 0.55)["f"],
            {"must_not_be": ["DESTRUCTION", "SMALL"], "axiom": "AX7+AX9"})
        add(f"C11_{i}", "complement", o, ~o["f"],
            {"must_not_be": ["NEUTRAL", "DESTRUCTION"], "axiom": "AX1c+AX7"})
        perm = rng.permutation(N)
        fp = o["f"][
            (INPUT_COLS[:, perm] << np.arange(N)).sum(1)]
        add(f"C9b_{i}", "input_permutation", o, fp,
            {"must_not_be_unless_equal": ["NEUTRAL"],
             "must_not_be": ["DESTRUCTION"], "axiom": "AX1c+AX7"})
        if o["gates"] is not None:
            # C5/C8: representation change / simplification, same behavior
            add(f"C5_{i}", "rep_change_identical", o, o["f"].copy(),
                {"must_be": "NEUTRAL", "axiom": "AX1"})

    for i, o in enumerate(unbal):
        for k in (1, 4, 8):
            add(f"C3_k{k}_{i}", "unbalanced_flip", o,
                flip_k(o["f"], k, rng), {"must_be": "SMALL", "axiom": "AX3"})
        maj = o["f"].mean() > 0.5
        add(f"C4_{i}", "unbalanced_collapse", o,
            np.full(DOM, maj, bool), {"must_be": "DESTRUCTION",
                                      "axiom": "AX2",
                                      "gen1_defect_cell": True})
        # C12: remove 80% of minority support (only if child stays nontrivial)
        S = minority_support(o["f"])
        idx = np.flatnonzero(S)
        if len(idx) * 0.2 / DOM > EPS_TRIV:
            g = o["f"].copy()
            drop = rng_for(777, 4, i).choice(
                idx, size=int(0.8 * len(idx)), replace=False)
            g[drop] = ~g[drop]
            add(f"C12_{i}", "partial_support_loss", o, g,
                {"must_not_be": ["SMALL"], "axiom": "AX8"})

    # necessity pairs
    b0 = balanced[0]
    add("N1_a", "same_d_flip", b0, flip_k(b0["f"], round(minmass(
        n1obj["f"]) * DOM), rng_for(777, 5)), {"must_be": "SMALL",
                                               "axiom": "AX3/N1"})
    maj = n1obj["f"].mean() > 0.5
    add("N1_b", "same_d_collapse", n1obj, np.full(DOM, maj, bool),
        {"must_be": "DESTRUCTION", "axiom": "AX2/N1"})
    tgt = flip_k(b0["f"], 1, rng_for(777, 6))
    add("N2_a", "same_target_near", b0, tgt, {"must_be": "SMALL",
                                              "axiom": "AX3/N2"})
    add("N2_b", "same_target_far", balanced[1], tgt.copy(),
        {"must_not_be": ["SMALL", "NEUTRAL", "DESTRUCTION"],
         "axiom": "AX9/N2"})
    return cells


# ---------------- Gen-1 re-score (deterministic edit-stream regeneration)

def rescore_gen1():
    rows_out = []
    for line in open(GEN1):
        o = json.loads(line)
        gates = [tuple(g) for g in o["gates"]]
        f = eval_wires(gates)[-1].copy()
        edits = circuit_edit_space(gates)
        rng = rng_for(o["seed"], 102, o["level"], o["obj"])
        kids = []
        for k in range(128):
            e = edits[int(rng.integers(len(edits)))]
            g = eval_wires(apply_edit(gates, e))[-1]
            kids.append(g)
            d = d_of(f, g)
            old = ("NEUTRAL" if d == 0.0
                   else "SMALL" if d <= LOCAL_BAND else "LARGE")
            rows_out.append(dict(seed=o["seed"], level=o["level"],
                                 obj=o["obj"], edit=k, d=round(d, 5),
                                 old_band=old, new_class=r_vec(f, g),
                                 mm_child=round(minmass(g), 4),
                                 surv=round(surv_of(f, g), 4)))
        # novelty (REPORT ONLY, unadjudicated): min distance to sibling children
        packed = np.array([np.packbits(k) for k in kids])
        for k in range(128):
            x = np.bitwise_xor(packed, packed[k])
            dists = np.array([bin(int.from_bytes(row.tobytes(), 'big')).count('1')
                              for row in x]) if False else \
                np.unpackbits(x, axis=1).sum(1)
            dists[k] = DOM + 1
            rows_out[-128 + k]["novelty_min_sib_d"] = round(
                float(dists.min()) / DOM, 5)
    return rows_out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    cells = build_cells()
    with open("results/cells.jsonl", "w") as fh:
        for c in cells:
            fh.write(json.dumps(c) + "\n")
    print(f"BATTERY: {len(cells)} cells")
    if mode == "cells":
        return
    rows = rescore_gen1()
    with open("results/gen1_rescored.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"RESCORE: {len(rows)} Gen-1 rows re-scored")


if __name__ == "__main__":
    main()
