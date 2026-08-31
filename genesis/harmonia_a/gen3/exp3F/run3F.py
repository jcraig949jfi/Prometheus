#!/usr/bin/env python
"""GEN-3F -- representation invariance, per FREEZE_3F.txt."""

import json
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "..")
import common as cm

STAT_SEED = 20260907
K_EDITS = 128
FE = ("inf", "balance_dev", "inf_density", "s_live", "gpos")


def nandify(gates):
    """Gate-by-gate NAND expansion; returns new gate list (same wire
    convention: inputs 0..9, gate i output = wire 10+i)."""
    out = []
    wire_map = {}          # old wire -> new wire

    def nw():
        return cm.N + len(out)

    for i in range(cm.N):
        wire_map[i] = i
    for gi, (op, a, b) in enumerate(gates):
        A, B = wire_map[a], wire_map[b]
        if op == 3:                       # NAND
            out.append((3, A, B))
        elif op == 0:                     # AND = NAND(NAND(a,b),same)
            out.append((3, A, B))
            t = nw() - 1 + 0
            t = cm.N + len(out) - 1
            out.append((3, t, t))
        elif op == 1:                     # OR = NAND(NAND(a,a),NAND(b,b))
            out.append((3, A, A))
            na = cm.N + len(out) - 1
            out.append((3, B, B))
            nb = cm.N + len(out) - 1
            out.append((3, na, nb))
        else:                             # XOR via 4 NANDs
            out.append((3, A, B))
            n1 = cm.N + len(out) - 1
            out.append((3, A, n1))
            n2 = cm.N + len(out) - 1
            out.append((3, B, n1))
            n3 = cm.N + len(out) - 1
            out.append((3, n2, n3))
        wire_map[cm.N + gi] = cm.N + len(out) - 1
    return out


def influences_g(gates, wires):
    base = wires[-1]
    infs = []
    for g in range(len(gates)):
        w2 = list(wires[:cm.N + g + 1])
        w2[cm.N + g] = ~wires[cm.N + g]
        for h in range(g + 1, len(gates)):
            op, a, b = gates[h]
            w2.append(cm.gate_eval(op, w2[a], w2[b]))
        infs.append(float(np.count_nonzero(w2[-1] != base)) / cm.DOM)
    return infs


def edit_rows_for(gates, f, g_meta, stream_key, Gn):
    edits = cm.circuit_edit_space(gates)
    rng = cm.rng_for(*stream_key)
    wires = cm.eval_wires(gates)
    infs = influences_g(gates, wires)
    rows = []
    for k in range(K_EDITS):
        e = edits[int(rng.integers(len(edits)))]
        f2 = cm.eval_wires(cm.apply_edit(gates, e))[-1]
        cls = cm.r_vec2(f, f2)
        if cls == "NEUTRAL":
            continue
        rows.append(dict(
            seed=g_meta["seed"],
            y=1 if cls == "SMALL" else 0,
            inf=infs[e[1]], kind=1.0 if e[0] == "op" else 0.0,
            gpos=e[1] / Gn, balance_dev=g_meta["balance_dev"],
            inf_density=g_meta["inf_density"], s_live=g_meta["s_live"]))
    return rows


def auc(scores, labels):
    r = cm.ranks(scores)
    pos = labels == 1
    n1, n0 = int(pos.sum()), int((~pos).sum())
    if n1 == 0 or n0 == 0:
        return 0.5
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def score_global(tr, te):
    Xtr = np.array([[r[f] for f in FE] for r in tr])
    Xte = np.array([[r[f] for f in FE] for r in te])
    ktr = np.array([r["kind"] for r in tr])
    kte = np.array([r["kind"] for r in te])
    ytr = np.array([r["y"] for r in tr], float)
    yte = np.array([r["y"] for r in te])
    score = np.zeros(len(te))
    for kv in (0.0, 1.0):
        m_tr, m_te = ktr == kv, kte == kv
        if not m_te.any():
            continue
        A = np.column_stack([np.ones(m_tr.sum()), Xtr[m_tr]])
        b, *_ = np.linalg.lstsq(A, ytr[m_tr], rcond=None)
        score[m_te] = np.column_stack(
            [np.ones(m_te.sum()), Xte[m_te]]) @ b
    a = auc(score, yte)
    return max(a, 1 - a)


def main():
    geo = cm.per_object_vector_outcomes()
    rows = cm.load_rescored()
    by = defaultdict(list)
    for r in rows:
        by[(r["seed"], r["level"], r["obj"])].append(r)

    # E-ORIG edit rows (regenerated, as 3D/3E)
    orig, nand, relab = [], [], []
    for g in geo:
        gates = [tuple(x) for x in g["_gates"]]
        f = cm.eval_wires(gates)[-1].copy()
        edits = cm.circuit_edit_space(gates)
        rng_e = cm.rng_for(g["seed"], 102, g["level"], g["obj"])
        rs = by[(g["seed"], g["level"], g["obj"])]
        for k in range(K_EDITS):
            e = edits[int(rng_e.integers(len(edits)))]
            r = rs[k]
            if r["new_class"] == "NEUTRAL":
                continue
            orig.append(dict(
                seed=g["seed"], y=1 if r["new_class"] == "SMALL" else 0,
                inf=g["inf_profile"][e[1]],
                kind=1.0 if e[0] == "op" else 0.0,
                gpos=e[1] / 24.0, balance_dev=g["balance_dev"],
                inf_density=g["inf_density"], s_live=g["s_live"]))
        # E-NAND
        ng = nandify(gates)
        fn = cm.eval_wires(ng)[-1]
        assert np.array_equal(fn, f), "NAND same-behavior violation"
        nand.extend(edit_rows_for(
            ng, f, g, (g["seed"], 105, g["level"], g["obj"]), len(ng)))
        # E-RELAB (positive control)
        perm = cm.rng_for(g["seed"], 106, g["level"],
                          g["obj"]).permutation(cm.N)
        rg = [(op,
               int(perm[a]) if a < cm.N else a,
               int(perm[b]) if b < cm.N else b) for op, a, b in gates]
        inv = np.argsort(perm)
        fr = cm.eval_wires(rg, perm=inv)[-1]
        assert np.array_equal(fr, f), "RELAB same-behavior violation"
        # relabeled circuit evaluated in its own frame: behavior f_r
        f_own = cm.eval_wires(rg)[-1]
        g2 = dict(g)
        g2["balance_dev"] = abs(float(f_own.mean()) - 0.5)
        relab.extend(edit_rows_for(
            rg, f_own, g2, (g["seed"], 107, g["level"], g["obj"]), 24))

    report = {"folds": {}}
    for hold in cm.MASTER_SEEDS:
        tr = [r for r in orig if r["seed"] != hold]
        a_orig = score_global(tr, [r for r in orig if r["seed"] == hold])
        a_nand = score_global(tr, [r for r in nand if r["seed"] == hold])
        a_rel = score_global(tr, [r for r in relab if r["seed"] == hold])
        report["folds"][str(hold)] = dict(
            ORIG=round(a_orig, 4), NAND=round(a_nand, 4),
            RELAB=round(a_rel, 4),
            n_nand=len([r for r in nand if r["seed"] == hold]))
        print(f"fold {hold}: {report['folds'][str(hold)]}", flush=True)

    ctrl_ok = all(abs(f["RELAB"] - f["ORIG"]) <= 0.02
                  for f in report["folds"].values())
    nands = [f["NAND"] for f in report["folds"].values()]
    if not ctrl_ok:
        verdict = "HARNESS_SUSPECT"
    elif all(a >= 0.65 for a in nands):
        verdict = "BEHAVIOR_TRACKING"
    elif any(a <= 0.55 for a in nands):
        verdict = "REPRESENTATION_SPECIFIC"
    else:
        verdict = "PARTIAL_INVARIANCE"
    report["G_CONTROL"] = "PASS" if ctrl_ok else "FAIL"
    report["verdict"] = verdict
    json.dump(report, open("results/analysis_3F.json", "w"), indent=1)
    print("G_CONTROL:", report["G_CONTROL"])
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
