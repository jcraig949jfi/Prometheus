#!/usr/bin/env python
"""GEN-3D -- mathematical-type tournament, per FREEZE_3D.txt."""

import json
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "..")
import common as cm

STAT_SEED = 20260905
K_NN = 15
FEATS = ("inf_target", "kind", "balance_dev", "inf_density", "s_live",
         "gpos")


def build_edit_rows():
    geo = cm.per_object_vector_outcomes()
    rows = cm.load_rescored()
    by = defaultdict(list)
    for r in rows:
        by[(r["seed"], r["level"], r["obj"])].append(r)
    out = []
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
            out.append(dict(
                pid=(g["seed"], g["level"], g["obj"]), seed=g["seed"],
                y=1 if r["new_class"] == "SMALL" else 0,
                inf_target=g["inf_profile"][e[1]],
                kind=1.0 if e[0] == "op" else 0.0,
                gpos=e[1] / 24.0, balance_dev=g["balance_dev"],
                inf_density=g["inf_density"], s_live=g["s_live"]))
    return out, geo


def auc(scores, labels):
    r = cm.ranks(scores)
    pos = labels == 1
    n1, n0 = int(pos.sum()), int((~pos).sum())
    if n1 == 0 or n0 == 0:
        return 0.5
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def fold_eval(tr, te, geo_by_pid):
    Xtr = np.array([[r[f] for f in FEATS] for r in tr])
    Xte = np.array([[r[f] for f in FEATS] for r in te])
    ytr = np.array([r["y"] for r in tr])
    yte = np.array([r["y"] for r in te])
    res = {}

    # F1 scalar
    s = np.sign(cm.spearman(Xtr[:, 0], ytr)) or 1.0
    res["F1_scalar"] = auc(s * Xte[:, 0], yte)

    # F2 stratified by balance_dev terciles (train cuts)
    bd_tr, bd_te = Xtr[:, 2], Xte[:, 2]
    cuts = np.quantile(bd_tr, [1 / 3, 2 / 3])
    stra_tr = np.digitize(bd_tr, cuts)
    stra_te = np.digitize(bd_te, cuts)
    score = np.zeros(len(te))
    for st in range(3):
        m_tr, m_te = stra_tr == st, stra_te == st
        if not m_te.any():
            continue
        if m_tr.sum() < 20:
            score[m_te] = float(ytr.mean())
            continue
        A = np.column_stack([np.ones(m_tr.sum()), Xtr[m_tr][:, :1]])
        b, *_ = np.linalg.lstsq(A, ytr[m_tr].astype(float), rcond=None)
        score[m_te] = np.column_stack(
            [np.ones(m_te.sum()), Xte[m_te][:, :1]]) @ b
    res["F2_stratified"] = auc(score, yte)

    # F3 kNN
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-12
    Ztr, Zte = (Xtr - mu) / sd, (Xte - mu) / sd
    score = np.zeros(len(te))
    B = 500
    for s0 in range(0, len(te), B):
        blk = Zte[s0:s0 + B]
        d2 = ((blk[:, None, :] - Ztr[None, :, :]) ** 2).sum(-1)
        nn = np.argpartition(d2, K_NN, axis=1)[:, :K_NN]
        score[s0:s0 + B] = ytr[nn].mean(1)
    res["F3_knn"] = auc(score, yte)

    # F4 partial order (dominance cone on inf_target, balance_dev)
    s1 = np.sign(cm.spearman(Xtr[:, 0], ytr)) or 1.0
    s2 = np.sign(cm.spearman(Xtr[:, 2], ytr)) or 1.0
    a_tr, b_tr = s1 * Xtr[:, 0], s2 * Xtr[:, 2]
    a_te, b_te = s1 * Xte[:, 0], s2 * Xte[:, 2]
    prior = float(ytr.mean())
    score = np.zeros(len(te))
    for s0 in range(0, len(te), B):
        dom = ((a_tr[None, :] <= a_te[s0:s0 + B, None])
               & (b_tr[None, :] <= b_te[s0:s0 + B, None]))
        cnt = dom.sum(1)
        hit = (dom * ytr[None, :]).sum(1)
        blkscore = np.where(cnt >= 10, hit / np.maximum(cnt, 1), prior)
        score[s0:s0 + B] = blkscore
    res["F4_partial_order"] = auc(score, yte)

    # F5 operator family (per kind rank-linear on remaining feats)
    score = np.zeros(len(te))
    for kv in (0.0, 1.0):
        m_tr = Xtr[:, 1] == kv
        m_te = Xte[:, 1] == kv
        if not m_te.any():
            continue
        cols = [0, 2, 3, 4, 5]
        A = np.column_stack([np.ones(m_tr.sum()), Xtr[m_tr][:, cols]])
        b, *_ = np.linalg.lstsq(A, ytr[m_tr].astype(float), rcond=None)
        score[m_te] = np.column_stack(
            [np.ones(m_te.sum()), Xte[m_te][:, cols]]) @ b
    res["F5_operator_family"] = auc(score, yte)

    # F6 parent-conditioned charts, transported by nearest parent
    COVS = ("balance_dev", "inf_density", "s_live", "b_live",
            "anf_support", "live_vars", "depth")
    pids_tr = sorted({r["pid"] for r in tr})
    bins = np.linspace(0, 0.5, 6)   # inf bins (influence rarely > 0.5)
    charts = {}
    pcov = {}
    by_pid = defaultdict(list)
    for r in tr:
        by_pid[r["pid"]].append(r)
    for p in pids_tr:
        rs = by_pid[p]
        xv = np.array([r["inf_target"] for r in rs])
        yv = np.array([r["y"] for r in rs], float)
        idx = np.clip(np.digitize(xv, bins) - 1, 0, len(bins) - 2)
        curve = np.full(len(bins) - 1, float(yv.mean()))
        for bidx in range(len(bins) - 1):
            m = idx == bidx
            if m.sum() >= 3:
                curve[bidx] = float(yv[m].mean())
        charts[p] = curve
        g = geo_by_pid[p]
        pcov[p] = np.array([g[c] for c in COVS])
    P = np.array([pcov[p] for p in pids_tr])
    mu, sd = P.mean(0), P.std(0) + 1e-12
    Pz = (P - mu) / sd
    score = np.zeros(len(te))
    te_pids = sorted({r["pid"] for r in te})
    nearest = {}
    for p in te_pids:
        g = geo_by_pid[p]
        z = (np.array([g[c] for c in COVS]) - mu) / sd
        nearest[p] = pids_tr[int(np.argmin(((Pz - z) ** 2).sum(1)))]
    for w, r in enumerate(te):
        curve = charts[nearest[r["pid"]]]
        bidx = int(np.clip(np.digitize(r["inf_target"], bins) - 1,
                           0, len(bins) - 2))
        score[w] = curve[bidx]
    res["F6_parent_charts"] = auc(score, yte)

    res["F7_null"] = 0.5
    return {k: round(max(v, 1 - v), 4) for k, v in res.items()}


def main():
    edits, geo = build_edit_rows()
    geo_by_pid = {(g["seed"], g["level"], g["obj"]): g for g in geo}
    folds = {}
    for hold in cm.MASTER_SEEDS:
        tr = [r for r in edits if r["seed"] != hold]
        te = [r for r in edits if r["seed"] == hold]
        folds[hold] = fold_eval(tr, te, geo_by_pid)
        print(f"fold {hold}: {folds[hold]}", flush=True)
    fams = sorted(folds[11].keys())
    means = {f: round(float(np.mean([folds[s][f]
                                     for s in cm.MASTER_SEEDS])), 4)
             for f in fams}
    ranked = sorted((f for f in fams if f != "F7_null"),
                    key=lambda f: -means[f])
    top, runner = ranked[0], ranked[1]
    beat_folds = sum(1 for s in cm.MASTER_SEEDS
                     if folds[s][top] >= folds[s][runner])
    if means[top] - means[runner] >= 0.02 and beat_folds >= 4:
        verdict = f"WINNER_{top}"
    else:
        tie = [f for f in ranked if means[ranked[0]] - means[f] <= 0.02]
        verdict = "TIE_SET_" + "+".join(tie)
    support_ok = all(len([r for r in edits if r["seed"] == s]) >= 500
                     for s in cm.MASTER_SEEDS)
    if not support_ok:
        verdict = "INDETERMINATE"
    report = dict(folds={str(k): v for k, v in folds.items()},
                  means=means, verdict=verdict)
    json.dump(report, open("results/analysis_3D.json", "w"), indent=1)
    print("means:", means)
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
