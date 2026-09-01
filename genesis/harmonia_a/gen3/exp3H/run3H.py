#!/usr/bin/env python
"""GEN-3H -- cross-substrate transport, per FREEZE_3H.txt."""

import json
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "..")
import common as cm

STAT_SEED = 20260909
P = 97
L = 12
NREG = 4
K_EDITS = 128
OBJECTS_PER_SEED = 12
EPS_H = 0.025

XX, YY = np.meshgrid(np.arange(P), np.arange(P), indexing="ij")
X0 = XX.reshape(-1).astype(np.int64)
Y0 = YY.reshape(-1).astype(np.int64)
DOMH = P * P


def run_prog(prog, bump=None):
    """Execute; bump=(i) increments instruction i's result by 1 mod P."""
    regs = [X0.copy(), Y0.copy(),
            np.ones(DOMH, np.int64), np.zeros(DOMH, np.int64)]
    for i, (op, dst, a, b) in enumerate(prog):
        if op == 0:
            v = (regs[a] + regs[b]) % P
        elif op == 1:
            v = (regs[a] - regs[b]) % P
        else:
            v = (regs[a] * regs[b]) % P
        if bump is not None and bump == i:
            v = (v + 1) % P
        regs[dst] = v
    return regs[0]


def nonmodal_frac(f):
    vals, cnt = np.unique(f, return_counts=True)
    return 1.0 - cnt.max() / len(f)


def triv(f):
    return nonmodal_frac(f) <= EPS_H


def classify_h(f, g):
    if np.array_equal(f, g):
        return "NEUTRAL"
    if triv(g):
        return "DESTRUCTION"
    d = float(np.count_nonzero(f != g)) / DOMH
    vals, cnt = np.unique(f, return_counts=True)
    mode_f = vals[np.argmax(cnt)]
    vals2, cnt2 = np.unique(g, return_counts=True)
    mode_g = vals2[np.argmax(cnt2)]
    NM_f = f != mode_f
    NM_g = g != mode_g
    inter = np.count_nonzero((f == g) & NM_f)
    union = np.count_nonzero(NM_f | NM_g)
    surv = inter / union if union else 1.0
    return "SMALL" if (d <= 0.25 and surv >= 0.5) else "LARGE"


def mini_battery():
    rng = cm.rng_for(999, 30)
    ok = True
    log = []
    for act in (0.3, 0.9):                    # two parent activity levels
        f = np.zeros(DOMH, np.int64)
        idx = rng.choice(DOMH, size=int(act * DOMH), replace=False)
        f[idx] = rng.integers(1, P, size=len(idx))
        # AX1 identity
        c = classify_h(f, f.copy())
        log.append(("AX1", act, c)); ok &= c == "NEUTRAL"
        # AX2 collapse
        c = classify_h(f, np.zeros(DOMH, np.int64))
        log.append(("AX2", act, c)); ok &= c == "DESTRUCTION"
        # AX3 k-point modification (k=8)
        g = f.copy()
        j = rng.choice(DOMH, size=8, replace=False)
        g[j] = (g[j] + 1) % P
        c = classify_h(f, g)
        log.append(("AX3", act, c)); ok &= c == "SMALL"
        # AX7 healthy replacement
        h = np.zeros(DOMH, np.int64)
        idx2 = rng.choice(DOMH, size=int(0.5 * DOMH), replace=False)
        h[idx2] = rng.integers(1, P, size=len(idx2))
        c = classify_h(f, h)
        log.append(("AX7", act, c)); ok &= c != "DESTRUCTION"
    return ok, log


def random_prog(rng):
    return [(int(rng.integers(3)), int(rng.integers(NREG)),
             int(rng.integers(NREG)), int(rng.integers(NREG)))
            for _ in range(L)]


def edit_space(prog):
    edits = []
    for i, (op, dst, a, b) in enumerate(prog):
        for no in range(3):
            if no != op:
                edits.append(("op", i, ("op", no)))
        for slot, cur in (("dst", dst), ("a", a), ("b", b)):
            for r in range(NREG):
                if r != cur:
                    edits.append(("wire", i, (slot, r)))
    return edits


def apply_edit_h(prog, e):
    kind, i, (slot, v) = e
    out = list(prog)
    op, dst, a, b = out[i]
    if slot == "op":
        out[i] = (v, dst, a, b)
    elif slot == "dst":
        out[i] = (op, v, a, b)
    elif slot == "a":
        out[i] = (op, dst, v, b)
    else:
        out[i] = (op, dst, a, v)
    return out


def auc(scores, labels):
    r = cm.ranks(scores)
    pos = labels == 1
    n1, n0 = int(pos.sum()), int((~pos).sum())
    if n1 == 0 or n0 == 0:
        return 0.5
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def circuit_reduced_model():
    """Fit per-kind rank-linear on (inf, gpos) ONLY, per LOSO fold,
    on the circuit edit rows; return per-fold coefficients + own AUC."""
    geo = cm.per_object_vector_outcomes()
    rows = cm.load_rescored()
    by = defaultdict(list)
    for r in rows:
        by[(r["seed"], r["level"], r["obj"])].append(r)
    circ = []
    for g in geo:
        gates = [tuple(x) for x in g["_gates"]]
        edits = cm.circuit_edit_space(gates)
        rng_e = cm.rng_for(g["seed"], 102, g["level"], g["obj"])
        rs = by[(g["seed"], g["level"], g["obj"])]
        for k in range(128):
            e = edits[int(rng_e.integers(len(edits)))]
            r = rs[k]
            if r["new_class"] == "NEUTRAL":
                continue
            circ.append(dict(seed=g["seed"],
                             y=1 if r["new_class"] == "SMALL" else 0,
                             inf=g["inf_profile"][e[1]],
                             kind=1.0 if e[0] == "op" else 0.0,
                             gpos=e[1] / 24.0))
    models = {}
    for hold in cm.MASTER_SEEDS:
        tr = [r for r in circ if r["seed"] != hold]
        te = [r for r in circ if r["seed"] == hold]
        coefs = {}
        for kv in (0.0, 1.0):
            sub = [r for r in tr if r["kind"] == kv]
            A = np.column_stack([np.ones(len(sub)),
                                 [r["inf"] for r in sub],
                                 [r["gpos"] for r in sub]])
            b, *_ = np.linalg.lstsq(A, np.array(
                [r["y"] for r in sub], float), rcond=None)
            coefs[kv] = b
        score = np.array([coefs[r["kind"]] @ np.array(
            [1.0, r["inf"], r["gpos"]]) for r in te])
        yte = np.array([r["y"] for r in te])
        a = auc(score, yte)
        models[hold] = dict(coefs={str(k): v.tolist()
                                   for k, v in coefs.items()},
                            own_auc=round(max(a, 1 - a), 4))
    return models


def main():
    ok, blog = mini_battery()
    print("mini-battery:", "PASS" if ok else "FAIL", blog)
    if not ok:
        json.dump(dict(verdict="INDETERMINATE",
                       reason="ruler instance failed mini-battery",
                       battery=blog),
                  open("results/analysis_3H.json", "w"), indent=1)
        return

    # population + edits
    edits_rows = []
    for seed in cm.MASTER_SEEDS:
        made = 0
        attempt = 0
        while made < OBJECTS_PER_SEED:
            attempt += 1
            rng = cm.rng_for(seed, 120, made, attempt)
            prog = random_prog(rng)
            f = run_prog(prog)
            nmf = nonmodal_frac(f)
            if nmf < 0.05:
                continue
            fx = run_prog([(op, d, a, b) for op, d, a, b in prog])
            # dependence check: output varies with x or y
            if np.all(f == f[0]):
                continue
            infs = [float(np.count_nonzero(run_prog(prog, bump=i) != f))
                    / DOMH for i in range(L)]
            es = edit_space(prog)
            rng_e = cm.rng_for(seed, 121, made)
            for k in range(K_EDITS):
                e = es[int(rng_e.integers(len(es)))]
                g = run_prog(apply_edit_h(prog, e))
                cls = classify_h(f, g)
                if cls == "NEUTRAL":
                    continue
                edits_rows.append(dict(
                    seed=seed, y=1 if cls == "SMALL" else 0,
                    inf=infs[e[1]],
                    kind=1.0 if e[0] == "op" else 0.0,
                    gpos=e[1] / L))
            made += 1

    models = circuit_reduced_model()
    folds = {}
    for hold in cm.MASTER_SEEDS:
        te = [r for r in edits_rows if r["seed"] == hold]
        y = np.array([r["y"] for r in te])
        a_inf = auc(np.array([r["inf"] for r in te]), y)
        coefs = {float(k): np.array(v)
                 for k, v in models[hold]["coefs"].items()}
        score = np.array([coefs[r["kind"]] @ np.array(
            [1.0, r["inf"], r["gpos"]]) for r in te])
        a_port = auc(score, y)
        folds[hold] = dict(n=len(te),
                           auc_inf=round(max(a_inf, 1 - a_inf), 4),
                           auc_ported=round(max(a_port, 1 - a_port), 4),
                           circuit_own_auc=models[hold]["own_auc"])
        print(f"fold {hold}: {folds[hold]}", flush=True)

    support_ok = all(f["n"] >= 300 for f in folds.values())
    a_ok = all(f["auc_inf"] >= 0.65 for f in folds.values())
    a_dead = any(f["auc_inf"] <= 0.55 for f in folds.values())
    b_ok = all(f["auc_ported"] >= 0.60 for f in folds.values())
    if not support_ok:
        verdict = "INDETERMINATE"
    elif a_ok and b_ok:
        verdict = "CROSS_SUBSTRATE_STRUCTURE"
    elif a_ok:
        verdict = "STRUCTURE_RECURS_NOT_PORTABLE"
    elif a_dead:
        verdict = "BOOLEAN_ARTIFACT"
    else:
        verdict = "PARTIAL"
    report = dict(battery=blog,
                  folds={str(k): v for k, v in folds.items()},
                  verdict=verdict)
    json.dump(report, open("results/analysis_3H.json", "w"), indent=1)
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
