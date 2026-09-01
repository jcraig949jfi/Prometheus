#!/usr/bin/env python
"""Gen-3 campaign shared machinery. Verbatim ports of the frozen Gen-1/2
implementations (stats) and Gen-2b ruler. Hash journaled at charter
issuance; edits require a journaled amendment naming affected experiments."""

import gzip
import json
from collections import defaultdict

import numpy as np

N = 10
DOM = 1 << N
G = 24
EPS_TRIV = 0.025
LOCAL_BAND = 0.25
MASTER_SEEDS = (11, 22, 33, 44, 55)
GEN1_OBJECTS = "../../gen1/results/objects.jsonl"
GEN1_RESCORED = "../../gen2/results/gen1_rescored_v2.jsonl.gz"

INPUT_COLS = ((np.arange(DOM)[:, None] >> np.arange(N)) & 1).astype(bool)


# ---------------- circuit layer (gen1/bench1.py verbatim)

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


# ---------------- R_VEC2 ruler (gen2/bench2b.py verbatim)

def minmass(f):
    m = float(f.mean())
    return min(m, 1.0 - m)


def d_of(f, g):
    return float(np.count_nonzero(f != g)) / DOM


def jaccard(a, b):
    u = np.count_nonzero(a | b)
    return float(np.count_nonzero(a & b)) / u if u else 1.0


def surv_sym(f, g):
    return min(jaccard(f, g), jaccard(~f, ~g))


def r_vec2(f, g):
    if np.array_equal(f, g):
        return "NEUTRAL"
    if minmass(g) <= EPS_TRIV:
        return "DESTRUCTION"
    d = d_of(f, g)
    return "SMALL" if (d <= LOCAL_BAND and surv_sym(f, g) >= 0.5) else "LARGE"


# ---------------- stats (gen1/analyze1.py + gen2 verbatim)

def ranks(x):
    x = np.asarray(x, float)
    vals, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt) - cnt
    avg = csum + (cnt - 1) / 2.0
    return avg[inv]


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    den = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den > 0 else 0.0


def partial_spearman(x, y, Z):
    rx, ry = ranks(x), ranks(y)
    if Z.shape[1] == 0:
        return spearman(x, y)
    RZ = np.column_stack([ranks(Z[:, j]) for j in range(Z.shape[1])])
    A = np.column_stack([np.ones(len(rx)), RZ])
    bx, *_ = np.linalg.lstsq(A, rx, rcond=None)
    by, *_ = np.linalg.lstsq(A, ry, rcond=None)
    ex, ey = rx - A @ bx, ry - A @ by
    den = np.sqrt((ex ** 2).sum() * (ey ** 2).sum())
    return float((ex * ey).sum() / den) if den > 0 else 0.0


def eta2(levels, y):
    y = np.asarray(y, float)
    gm = y.mean()
    ssb = sum(len(y[levels == l]) * (y[levels == l].mean() - gm) ** 2
              for l in np.unique(levels))
    sst = ((y - gm) ** 2).sum()
    return float(ssb / sst) if sst > 0 else 0.0


def perm_p_eta2(levels, y, seeds, rng, n_perm=1000):
    obs = eta2(levels, y)
    hits = 0
    for _ in range(n_perm):
        lp = levels.copy()
        for s in np.unique(seeds):
            m = seeds == s
            lp[m] = rng.permutation(levels[m])
        if eta2(lp, y) >= obs:
            hits += 1
    return obs, (hits + 1) / (n_perm + 1)


# ---------------- data loading

def load_gen1_objects():
    return [json.loads(l) for l in open(GEN1_OBJECTS)]


def load_rescored():
    with gzip.open(GEN1_RESCORED, "rt") as fh:
        return [json.loads(l) for l in fh]


def per_object_vector_outcomes(min_nonneutral=5):
    """Per Gen-1 object: R_VEC2 class masses + conditional shares."""
    objs = load_gen1_objects()
    rows = load_rescored()
    by = defaultdict(list)
    for r in rows:
        by[(r["seed"], r["level"], r["obj"])].append(r)
    out = []
    for o in objs:
        rs = by[(o["seed"], o["level"], o["obj"])]
        n = len(rs)
        cnt = defaultdict(int)
        for r in rs:
            cnt[r["new_class"]] += 1
        nn = n - cnt["NEUTRAL"]
        rec = dict(o)
        rec["balance_dev"] = abs(o["balance"] - 0.5)
        rec.update(mass_N=cnt["NEUTRAL"] / n, mass_S=cnt["SMALL"] / n,
                   mass_L=cnt["LARGE"] / n, mass_D=cnt["DESTRUCTION"] / n,
                   n_nonneutral=nn,
                   small_share=(cnt["SMALL"] / nn
                                if nn >= min_nonneutral else None),
                   destr_share=(cnt["DESTRUCTION"] / nn
                                if nn >= min_nonneutral else None))
        del rec["gates"]
        rec["_gates"] = o["gates"]
        out.append(rec)
    return out
