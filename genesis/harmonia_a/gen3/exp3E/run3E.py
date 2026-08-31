#!/usr/bin/env python
"""GEN-3E -- parent-condition dependence, per FREEZE_3E.txt."""

import json
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "..")
import common as cm

STAT_SEED = 20260906
COVS = ("balance_dev", "inf_density", "s_live", "b_live",
        "anf_support", "live_vars", "depth")
BINS = np.linspace(0, 0.5, 6)


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
                idx=k, y=1 if r["new_class"] == "SMALL" else 0,
                inf=g["inf_profile"][e[1]],
                kind=1.0 if e[0] == "op" else 0.0,
                balance_dev=g["balance_dev"],
                inf_density=g["inf_density"], s_live=g["s_live"],
                gpos=e[1] / 24.0))
    return out, geo


def auc(scores, labels):
    r = cm.ranks(scores)
    pos = labels == 1
    n1, n0 = int(pos.sum()), int((~pos).sum())
    if n1 == 0 or n0 == 0:
        return 0.5
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def chart_fit(rows):
    """Per (kind, inf-bin) response curve with fallbacks."""
    prior = float(np.mean([r["y"] for r in rows])) if rows else 0.5
    curve = {}
    for kv in (0.0, 1.0):
        for b in range(len(BINS) - 1):
            sub = [r["y"] for r in rows if r["kind"] == kv
                   and BINS[b] <= min(r["inf"], 0.4999) < BINS[b + 1]]
            curve[(kv, b)] = float(np.mean(sub)) if len(sub) >= 3 \
                else prior
    return curve


def chart_score(curve, r):
    b = int(np.clip(np.digitize(min(r["inf"], 0.4999), BINS) - 1,
                    0, len(BINS) - 2))
    return curve[(r["kind"], b)]


def main():
    edits, geo = build_edit_rows()
    geo_by_pid = {(g["seed"], g["level"], g["obj"]): g for g in geo}
    folds = {}
    for hold in cm.MASTER_SEEDS:
        tr = [r for r in edits if r["seed"] != hold]
        te = [r for r in edits if r["seed"] == hold]
        yte = np.array([r["y"] for r in te])

        # GLOBAL (3D F5 verbatim: per-kind rank-linear)
        FE = ("inf", "balance_dev", "inf_density", "s_live", "gpos")
        Xtr = np.array([[r[f] for f in FE] for r in tr])
        Xte = np.array([[r[f] for f in FE] for r in te])
        ktr = np.array([r["kind"] for r in tr])
        kte = np.array([r["kind"] for r in te])
        ytr = np.array([r["y"] for r in tr], float)
        score = np.zeros(len(te))
        for kv in (0.0, 1.0):
            m_tr, m_te = ktr == kv, kte == kv
            A = np.column_stack([np.ones(m_tr.sum()), Xtr[m_tr]])
            b, *_ = np.linalg.lstsq(A, ytr[m_tr], rcond=None)
            score[m_te] = np.column_stack(
                [np.ones(m_te.sum()), Xte[m_te]]) @ b
        auc_global = auc(score, yte)

        # ATLAS: nearest-train-parent chart (kind x inf-bin)
        by_pid = defaultdict(list)
        for r in tr:
            by_pid[r["pid"]].append(r)
        pids_tr = sorted(by_pid)
        charts = {p: chart_fit(by_pid[p]) for p in pids_tr}
        P = np.array([[geo_by_pid[p][c] for c in COVS]
                      for p in pids_tr])
        mu, sd = P.mean(0), P.std(0) + 1e-12
        Pz = (P - mu) / sd
        nearest = {}
        for p in sorted({r["pid"] for r in te}):
            z = (np.array([geo_by_pid[p][c] for c in COVS]) - mu) / sd
            nearest[p] = pids_tr[int(np.argmin(((Pz - z) ** 2).sum(1)))]
        score_a = np.array([chart_score(charts[nearest[r["pid"]]], r)
                            for r in te])
        auc_atlas = auc(score_a, yte)

        # CEILING: within-test-parent even->odd chart (reference only)
        by_te = defaultdict(list)
        for r in te:
            by_te[r["pid"]].append(r)
        sc, yy = [], []
        for p, rs in by_te.items():
            ev = [r for r in rs if r["idx"] % 2 == 0]
            od = [r for r in rs if r["idx"] % 2 == 1]
            if len(ev) < 10 or len(od) < 10:
                continue
            curve = chart_fit(ev)
            sc.extend(chart_score(curve, r) for r in od)
            yy.extend(r["y"] for r in od)
        auc_ceiling = auc(np.array(sc), np.array(yy))

        folds[hold] = dict(GLOBAL=round(auc_global, 4),
                           ATLAS=round(auc_atlas, 4),
                           CEILING=round(auc_ceiling, 4))
        print(f"fold {hold}: {folds[hold]}", flush=True)

    mg = float(np.mean([f["GLOBAL"] for f in folds.values()]))
    ma = float(np.mean([f["ATLAS"] for f in folds.values()]))
    mc = float(np.mean([f["CEILING"] for f in folds.values()]))
    atlas_wins = sum(1 for f in folds.values()
                     if f["ATLAS"] >= f["GLOBAL"])
    if ma - mg >= 0.02 and atlas_wins >= 4:
        verdict = "ATLAS_SUPERIOR"
    elif mg >= ma - 0.01:
        verdict = "GLOBAL_SUFFICIENT"
    else:
        verdict = "INDETERMINATE_MARGIN"

    # CHARTS_MAPPABLE flag
    params = []
    for g in geo:
        pid = (g["seed"], g["level"], g["obj"])
        rs = [r for r in edits if r["pid"] == pid]
        lo = [r["y"] for r in rs if r["inf"] <= 0.1]
        hi = [r["y"] for r in rs if r["inf"] > 0.25]
        if len(lo) >= 5 and len(hi) >= 5:
            params.append(dict(seed=g["seed"],
                               p_low=float(np.mean(lo)),
                               p_high=float(np.mean(hi)),
                               cov=[g[c] for c in COVS]))
    map_folds = {}
    for hold in cm.MASTER_SEEDS:
        tr = [p for p in params if p["seed"] != hold]
        te = [p for p in params if p["seed"] == hold]
        Xtr = np.array([p["cov"] for p in tr])
        Xte = np.array([p["cov"] for p in te])
        rhos = {}
        for key in ("p_low", "p_high"):
            ytr = np.array([p[key] for p in tr])
            yte2 = np.array([p[key] for p in te])
            A = np.column_stack([np.ones(len(Xtr)), Xtr])
            b, *_ = np.linalg.lstsq(A, ytr, rcond=None)
            pred = np.column_stack([np.ones(len(Xte)), Xte]) @ b
            rhos[key] = round(cm.spearman(pred, yte2), 4)
        map_folds[hold] = dict(n=len(te), **rhos)
    mappable = all(f["p_low"] >= 0.5 and f["p_high"] >= 0.5
                   for f in map_folds.values())

    report = dict(folds={str(k): v for k, v in folds.items()},
                  means=dict(GLOBAL=round(mg, 4), ATLAS=round(ma, 4),
                             CEILING=round(mc, 4)),
                  flags=dict(
                      OBJECT_HEADROOM_LARGE=bool(
                          mc - max(mg, ma) >= 0.10),
                      CHARTS_MAPPABLE=bool(mappable)),
                  chart_map_folds={str(k): v
                                   for k, v in map_folds.items()},
                  n_chart_parents=len(params),
                  verdict=verdict)
    json.dump(report, open("results/analysis_3E.json", "w"), indent=1)
    print("means:", report["means"])
    print("flags:", report["flags"])
    print("chart map folds:", map_folds)
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
