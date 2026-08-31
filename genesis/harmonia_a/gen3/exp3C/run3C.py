#!/usr/bin/env python
"""GEN-3C -- kill-pair search, per FREEZE_3C.txt."""

import json
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "..")
import common as cm

STAT_SEED = 20260904
NPAIRS = 200_000


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
                small=1 if r["new_class"] == "SMALL" else 0,
                inf=g["inf_profile"][e[1]],
                kind=1.0 if e[0] == "op" else 0.0,
                gpos=e[1] / 24.0, balance_dev=g["balance_dev"],
                s_live=g["s_live"], inf_density=g["inf_density"]))
    return out, geo


def auc(scores, labels):
    r = cm.ranks(scores)
    pos = labels == 1
    n1, n0 = int(pos.sum()), int((~pos).sum())
    if n1 == 0 or n0 == 0:
        return 0.5
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def main():
    rng = np.random.default_rng(STAT_SEED)
    edits, geo = build_edit_rows()
    n = len(edits)
    inf = np.array([e["inf"] for e in edits])
    small = np.array([e["small"] for e in edits])
    pid = [e["pid"] for e in edits]

    i = rng.integers(n, size=NPAIRS)
    j = rng.integers(n, size=NPAIRS)
    cross = np.array([pid[a] != pid[b] for a, b in zip(i, j)])
    i, j = i[cross], j[cross]
    dinf = np.abs(inf[i] - inf[j])
    differ = small[i] != small[j]

    base = float(differ.mean())
    m1 = dinf <= 0.02
    disc = float(differ[m1].mean())
    kp1_idx = np.flatnonzero(m1 & differ)
    kp1_parents = {pid[i[a]] for a in kp1_idx} | \
                  {pid[j[a]] for a in kp1_idx}
    kp1_seeds = {p[0] for p in kp1_parents}
    kp1_force = (len(kp1_idx) >= 100 and len(kp1_parents) >= 20
                 and len(kp1_seeds) >= 3)

    m2 = dinf >= 0.30
    kp2_concord = float((~differ[m2]).mean()) if m2.any() else None

    # residual test on KP1 pairs: which member is SMALL?
    feats = ("balance_dev", "s_live", "inf_density", "kind", "gpos")
    rowsP = []
    for a in kp1_idx:
        ea, eb = edits[i[a]], edits[j[a]]
        # orient randomly-but-deterministically; label = first is SMALL
        if (a % 2) == 0:
            ea, eb = eb, ea
        rowsP.append(dict(
            y=ea["small"],
            seeds=(ea["seed"], eb["seed"]),
            x=[ea[f] - eb[f] for f in feats]))
    folds = {}
    for hold in cm.MASTER_SEEDS:
        tr = [p for p in rowsP if hold not in p["seeds"]]
        te = [p for p in rowsP if hold in p["seeds"]]
        if len(tr) < 50 or len(te) < 30:
            folds[hold] = dict(n_test=len(te), auc=None)
            continue
        Xtr = np.array([p["x"] for p in tr])
        Xte = np.array([p["x"] for p in te])
        ytr = np.array([p["y"] for p in tr], float)
        yte = np.array([p["y"] for p in te])
        A = np.column_stack([np.ones(len(Xtr)), Xtr])
        b, *_ = np.linalg.lstsq(A, ytr, rcond=None)
        s = np.column_stack([np.ones(len(Xte)), Xte]) @ b
        a_ = auc(s, yte)
        folds[hold] = dict(n_test=len(te), auc=round(max(a_, 1 - a_), 4))
    aucs = [f["auc"] for f in folds.values() if f["auc"] is not None]
    residual_pass = (len(aucs) == 5 and all(a >= 0.65 for a in aucs))

    # KP3: parent-level composite (rank-linear yhat, LOSO as 3B)
    CANDS = ("s_live", "inf_density", "b_live", "balance_dev",
             "live_vars", "anf_support", "depth",
             "forced_neutral_floor", "forced_local_bound")
    kp3 = 0
    kp3_pairs = 0
    sub = [g for g in geo if g["small_share"] is not None]
    yhat = np.zeros(len(sub))
    for hold in cm.MASTER_SEEDS:
        tr = [g for g in sub if g["seed"] != hold]
        Xtr = np.array([[g[c] for c in CANDS] for g in tr])
        ytr = np.array([g["small_share"] for g in tr])
        A = np.column_stack([np.ones(len(Xtr)), Xtr])
        b, *_ = np.linalg.lstsq(A, ytr, rcond=None)
        for idx, g in enumerate(sub):
            if g["seed"] == hold:
                yhat[idx] = np.array(
                    [1.0] + [g[c] for c in CANDS]) @ b
    ss = np.array([g["small_share"] for g in sub])
    for a in range(len(sub)):
        for b2 in range(a + 1, len(sub)):
            if abs(yhat[a] - yhat[b2]) <= 0.05:
                kp3_pairs += 1
                if abs(ss[a] - ss[b2]) >= 0.30:
                    kp3 += 1

    if not kp1_force and disc <= 0.05:
        verdict = "COORDINATE_SUFFICIENT"
    elif kp1_force and residual_pass:
        verdict = "COORDINATE_INSUFFICIENT_RICHER_STRUCTURE"
    elif kp1_force:
        verdict = "COORDINATE_PLUS_IRREDUCIBLE_NOISE"
    else:
        verdict = "INDETERMINATE"

    report = dict(
        n_edits=n, n_cross_pairs=int(len(i)),
        BASE_discordance=round(base, 4),
        KP1=dict(n=len(kp1_idx), disc_at_matched=round(disc, 4),
                 parents=len(kp1_parents), seeds=len(kp1_seeds),
                 in_force=bool(kp1_force)),
        KP2=dict(concordance_far_coord=round(kp2_concord, 4)),
        residual_folds=folds, residual_pass=bool(residual_pass),
        KP3=dict(matched_yhat_pairs=kp3_pairs,
                 discordant=kp3,
                 rate=round(kp3 / max(kp3_pairs, 1), 4)),
        verdict=verdict)
    json.dump(report, open("results/analysis_3C.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in report.items()
                      if k != "residual_folds"}, indent=1))
    print("residual folds:", {s: f for s, f in folds.items()})
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
