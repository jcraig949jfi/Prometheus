#!/usr/bin/env python
"""GEN-3B -- held-out-parent transport, per FREEZE_3B.txt."""

import json
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "..")
import common as cm

STAT_SEED = 20260903
CANDS = ("s_live", "inf_density", "b_live", "balance_dev", "live_vars",
         "anf_support", "depth", "forced_neutral_floor",
         "forced_local_bound")
NPERM = 100


def rank_linear_fit(Xtr, ytr):
    R = np.column_stack([cm.ranks(Xtr[:, j]) for j in range(Xtr.shape[1])])
    A = np.column_stack([np.ones(len(ytr)), R])
    b, *_ = np.linalg.lstsq(A, cm.ranks(ytr), rcond=None)
    return b


def rank_linear_predict(b, Xtr, Xte):
    # rank test points against train columns
    cols = []
    for j in range(Xte.shape[1]):
        tr = np.sort(Xtr[:, j])
        cols.append(np.searchsorted(tr, Xte[:, j]))
    A = np.column_stack([np.ones(len(Xte)), np.column_stack(cols)])
    return A @ b


def auc(scores, labels):
    r = cm.ranks(scores)
    pos = labels == 1
    n1, n0 = pos.sum(), (~pos).sum()
    if n1 == 0 or n0 == 0:
        return 0.5
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def tier_b1(geo, rng):
    folds = {}
    for hold in cm.MASTER_SEEDS:
        tr = [g for g in geo if g["seed"] != hold
              and g["small_share"] is not None]
        te = [g for g in geo if g["seed"] == hold
              and g["small_share"] is not None]
        Xtr = np.array([[g[c] for c in CANDS] for g in tr])
        Xte = np.array([[g[c] for c in CANDS] for g in te])
        ytr = np.array([g["small_share"] for g in tr])
        yte = np.array([g["small_share"] for g in te])
        res = {}
        # (a) rank-linear
        b = rank_linear_fit(Xtr, ytr)
        rho_a = cm.spearman(rank_linear_predict(b, Xtr, Xte), yte)
        # (b) 1-NN z-scored
        mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-12
        Ztr, Zte = (Xtr - mu) / sd, (Xte - mu) / sd
        nn = np.argmin(((Zte[:, None, :] - Ztr[None, :, :]) ** 2
                        ).sum(-1), axis=1)
        rho_b = cm.spearman(ytr[nn], yte)
        # (c) best single covariate on train
        best_j = max(range(len(CANDS)),
                     key=lambda j: abs(cm.spearman(Xtr[:, j], ytr)))
        sgn = np.sign(cm.spearman(Xtr[:, best_j], ytr)) or 1.0
        rho_c = cm.spearman(sgn * Xte[:, best_j], yte)
        # nulls (within-train label permutation)
        nulls = {"a": [], "b": [], "c": []}
        for _ in range(NPERM):
            yp = rng.permutation(ytr)
            bp = rank_linear_fit(Xtr, yp)
            nulls["a"].append(cm.spearman(
                rank_linear_predict(bp, Xtr, Xte), yte))
            nulls["b"].append(cm.spearman(yp[nn], yte))
            bj = max(range(len(CANDS)),
                     key=lambda j: abs(cm.spearman(Xtr[:, j], yp)))
            sg = np.sign(cm.spearman(Xtr[:, bj], yp)) or 1.0
            nulls["c"].append(cm.spearman(sg * Xte[:, bj], yte))
        folds[hold] = dict(
            n_test=len(te),
            rho=dict(a=round(rho_a, 4), b=round(rho_b, 4),
                     c=round(rho_c, 4)),
            null99=dict({k: round(float(np.percentile(v, 99)), 4)
                         for k, v in nulls.items()}),
            best_single=CANDS[best_j])
    return folds


def tier_b2(geo, rng):
    # regenerate per-edit rows: class + target-gate influence + kind
    rows = cm.load_rescored()
    by = defaultdict(list)
    for r in rows:
        by[(r["seed"], r["level"], r["obj"])].append(r)
    edit_rows = []
    for g in geo:
        gates = [tuple(x) for x in g["_gates"]]
        edits = cm.circuit_edit_space(gates)
        rng_e = cm.rng_for(g["seed"], 102, g["level"], g["obj"])
        rs = by[(g["seed"], g["level"], g["obj"])]
        for k in range(128):
            e = edits[int(rng_e.integers(len(edits)))]
            r = rs[k]
            if r["new_class"] == "NEUTRAL":
                continue                      # exclusion declared forced
            edit_rows.append(dict(
                seed=g["seed"],
                y=1 if r["new_class"] == "SMALL" else 0,
                inf_target=g["inf_profile"][e[1]],
                kind=1.0 if e[0] == "op" else 0.0,
                balance_dev=g["balance_dev"],
                inf_density=g["inf_density"], s_live=g["s_live"]))
    feats = ("inf_target", "kind", "balance_dev", "inf_density", "s_live")
    folds = {}
    for hold in cm.MASTER_SEEDS:
        tr = [r for r in edit_rows if r["seed"] != hold]
        te = [r for r in edit_rows if r["seed"] == hold]
        Xtr = np.array([[r[f] for f in feats] for r in tr])
        Xte = np.array([[r[f] for f in feats] for r in te])
        ytr = np.array([r["y"] for r in tr])
        yte = np.array([r["y"] for r in te])
        b = rank_linear_fit(Xtr, ytr.astype(float))
        auc_a = auc(rank_linear_predict(b, Xtr, Xte), yte)
        if auc_a < 0.5:
            auc_a = 1.0 - auc_a
        auc_b = auc(Xte[:, 0], yte)
        if auc_b < 0.5:
            auc_b = 1.0 - auc_b
        nulls = []
        for _ in range(NPERM):
            yp = rng.permutation(ytr).astype(float)
            bp = rank_linear_fit(Xtr, yp)
            a = auc(rank_linear_predict(bp, Xtr, Xte), yte)
            nulls.append(max(a, 1 - a))
        folds[hold] = dict(n_test=len(te), pos_rate=round(float(
            yte.mean()), 3), auc_linear=round(auc_a, 4),
            auc_inf_only=round(auc_b, 4),
            null99=round(float(np.percentile(nulls, 99)), 4))
    return folds


def gate_b1(folds):
    for m in ("a", "b", "c"):
        rhos = [f["rho"][m] for f in folds.values()]
        beats = all(f["rho"][m] > f["null99"][m] for f in folds.values())
        if all(r >= 0.5 for r in rhos) and beats:
            return "TRANSPORT", m
    for m in ("a", "b", "c"):
        rhos = [f["rho"][m] for f in folds.values()]
        beats = all(f["rho"][m] > f["null99"][m] for f in folds.values())
        if all(r >= 0.3 for r in rhos) and beats:
            return "WEAK", m
    return "NONE", None


def gate_b2(folds):
    for key in ("auc_linear", "auc_inf_only"):
        aucs = [f[key] for f in folds.values()]
        beats = all(f[key] > f["null99"] for f in folds.values())
        if all(a >= 0.70 for a in aucs) and beats:
            return "TRANSPORT", key
    for key in ("auc_linear", "auc_inf_only"):
        aucs = [f[key] for f in folds.values()]
        beats = all(f[key] > f["null99"] for f in folds.values())
        if all(a >= 0.60 for a in aucs) and beats:
            return "WEAK", key
    return "NONE", None


def main():
    rng = np.random.default_rng(STAT_SEED)
    geo = cm.per_object_vector_outcomes()
    b1 = tier_b1(geo, rng)
    b2 = tier_b2(geo, rng)
    g1, m1 = gate_b1(b1)
    g2, m2 = gate_b2(b2)
    support_ok = (all(f["n_test"] >= 30 for f in b1.values())
                  and all(f["n_test"] >= 500 for f in b2.values()))
    if not support_ok:
        verdict = "INDETERMINATE"
    elif "TRANSPORT" in (g1, g2):
        verdict = "TRANSPORT_CONFIRMED"
    elif "WEAK" in (g1, g2):
        verdict = "TRANSPORT_WEAK"
    else:
        verdict = "NO_TRANSPORT"
    report = dict(tier_b1=b1, tier_b2=b2,
                  gates=dict(b1=[g1, m1], b2=[g2, m2]),
                  verdict=verdict)
    json.dump(report, open("results/analysis_3B.json", "w"), indent=1)
    print("B1 folds:")
    for s, f in b1.items():
        print(f"  seed {s}: rho={f['rho']} null99={f['null99']} "
              f"best_single={f['best_single']}")
    print("B2 folds:")
    for s, f in b2.items():
        print(f"  seed {s}: n={f['n_test']} auc_lin={f['auc_linear']} "
              f"auc_inf={f['auc_inf_only']} null99={f['null99']}")
    print("gates:", report["gates"])
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
