"""AC-01R leakage re-report under the post-014aa4f ruling.

Scored population: live collapse actions of T_7 (state rank >= 3, target reachable), label = trap.  Permitted features
only (tuple A of the survivor gate: action, rank f, rank f', block sizes f', c0(f), c1(f), rank t, block sizes t).
Reports prevalence of the scored population, PR-AUC with a bootstrap 95% interval, normalised improvement over
prevalence (PR-AUC - p) / (1 - p), balanced accuracy at the train-chosen threshold, and normalised mutual information.
Rank-conditional prevalence is an ALLOWED baseline signal by ruling; leakage means substantial reconstruction of the
withheld kernel relation.  This script fits nothing beyond a frequency table.
"""
from __future__ import annotations
import json, os
import numpy as np
from ..universe.monoid import build_monoid
from ..universe.uc1_seed import pch_generators
from ..gate2 import analysis2 as A

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(max_rows=3_000_000, boot=200, seed=0):
    U = build_monoid("PCH", 7, pch_generators(7), 2)
    src, dst, rid, D, C, rank, bs = U["src"], U["dst"], U["rule"], U["D"], U["C"].astype(np.int64), U["rank"].astype(np.int64), U["bs_id"]
    fam = np.array([r.family for r in U["rules"]]); E = np.nonzero((fam[rid] == "rankdrop") & (src != dst) & (U["rank"][src] >= 3))[0]
    rng = np.random.default_rng(seed); per = max_rows // len(U["targets"]); es, js, ys = [], [], []; total = 0
    for j in range(len(U["targets"])):
        live = D[src[E], j] >= 0; e = E[live]; total += int(len(e))
        if len(e) > per: e = e[rng.choice(len(e), per, replace=False)]
        es.append(e.astype(np.int32)); js.append(np.full(len(e), j, dtype=np.int32)); ys.append(D[dst[e], j] < 0)
    e = np.concatenate(es); j = np.concatenate(js); y = np.concatenate(ys); tj = np.array(U["targets"])[j]
    tr = A._split(src[e]); prior = float(y[tr].mean())
    key = A._pack([rid[e], rank[src[e]], rank[dst[e]], np.unique(bs[dst[e]], return_inverse=True)[1], C[src[e], 0], C[src[e], 1], rank[tj], np.unique(bs[tj], return_inverse=True)[1]])
    r = A.table_classifier(key[tr], y[tr], key[~tr], y[~tr], prior)
    # bootstrap PR-AUC over held-out rows
    ku, inv = np.unique(key[tr], return_inverse=True); ptab = np.bincount(inv, weights=y[tr].astype(float)) / np.bincount(inv)
    pos = np.clip(np.searchsorted(ku, key[~tr]), 0, len(ku) - 1); p = np.where(ku[pos] == key[~tr], ptab[pos], prior); yt = y[~tr].astype(float)
    vals = []
    for _ in range(boot):
        i = rng.integers(0, len(p), len(p)); vals.append(A._pr_auc(p[i], yt[i]))
    prev = float(yt.mean()); auc = r["pr_auc"]
    out = {"scored_population": "live collapse actions from states of rank >= 3", "total_rows": total, "sampled_rows": int(len(e)),
           "prevalence_test": prev, "pr_auc": auc, "pr_auc_CI95_bootstrap": [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))],
           "normalised_improvement_over_prevalence": (auc - prev) / (1 - prev),
           "balanced_accuracy": r["best_train_threshold_metrics_on_test"]["balanced_accuracy"], "normalised_MI": r["normalised_MI"],
           "trap_entropy_remaining_fraction": 1 - r["normalised_MI"], "cells": r["cells"],
           "ruling": "rank-conditional prevalence is an allowed baseline signal; leakage = substantial reconstruction of the withheld kernel relation"}
    os.makedirs(os.path.join(HERE, "results", "ac01d"), exist_ok=True)
    with open(os.path.join(HERE, "results", "ac01d", "ac01r_leakage_report.json"), "w") as f:
        json.dump(out, f, indent=1)
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
