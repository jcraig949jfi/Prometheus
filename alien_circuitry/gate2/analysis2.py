"""Survivor-gate analyses: exact Q1 lookahead classification, H_obs, R0/R1/D layers, leakage attack, distance attack."""
from __future__ import annotations
import collections
import numpy as np
from ..universe.monoid import kernel_compatible, map_str

HBINS = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 12), (13, 20), (21, 30), (31, 10**9)]


def hbin_hist(values: np.ndarray) -> dict:
    out = {}
    for lo, hi in HBINS:
        out[f"{lo}" if lo == hi else (f"{lo}-{hi}" if hi < 10**9 else f">{lo - 1}")] = int(((values >= lo) & (values <= hi)).sum())
    out["n"] = int(len(values)); return out


def trap_edges(U: dict):
    """All (edge, target) traps: returns dict of arrays."""
    src, dst, D = U["src"], U["dst"], U["D"]
    E, J, = [], []
    for j in range(len(U["targets"])):
        Ds, Dd = D[src, j], D[dst, j]
        idx = np.nonzero((Ds >= 0) & (Dd < 0))[0]
        E.append(idx); J.append(np.full(len(idx), j, dtype=np.int64))
    e = np.concatenate(E); j = np.concatenate(J)
    return {"edge": e, "target_j": j, "src": src[e], "dst": dst[e], "rule": U["rule"][e], "D_src": D[src[e], j], "n": len(e)}


def q1_exact(U: dict, T: dict, ecc: np.ndarray, hmax: int = 5) -> dict:
    src, dst, D = U["src"], U["dst"], U["D"]
    n_live = 0; safe_at = np.zeros(hmax + 1, dtype=np.int64)
    for j in range(len(U["targets"])):
        Ds, Dd = D[src, j], D[dst, j]; live = Ds >= 0; n_live += int(live.sum()); dd = Dd[live]
        for h in range(hmax + 1):
            safe_at[h] += int(((dd >= 0) & (dd <= h)).sum())
    n_trap = T["n"]; n_non = n_live - n_trap; te = ecc[T["dst"]]
    out = {"live_triples": n_live, "traps": n_trap, "prevalence": n_trap / max(1, n_live), "per_depth": {}}
    for h in range(hmax + 1):
        tp = int((te <= h).sum()); fpB = n_non - int(safe_at[h])
        out["per_depth"][str(h)] = {"traps_proven": tp, "recall": tp / max(1, n_trap), "precision": 1.0 if tp else 0.0, "fpr": 0.0, "fnr": 1 - tp / max(1, n_trap),
                                    "balanced_accuracy": 0.5 * (1 + tp / max(1, n_trap)), "nontraps_proven_safe": int(safe_at[h]),
                                    "resolved_fraction": (tp + int(safe_at[h])) / max(1, n_live),
                                    "B_unknown_as_trap": {"precision": n_trap / max(1, n_trap + fpB), "fpr": fpB / max(1, n_non)}}
    out["pr_auc_note"] = "sound three-valued controller: precision is 1 at every attained recall; PR-AUC equals the recall reached (area under a step at precision 1) and is reported as such"
    out["H_obs"] = hbin_hist(te)
    out["min_eccentricity_over_traps"] = int(te.min()) if n_trap else None
    return out


def layers(U: dict, T: dict) -> dict:
    """R0 = kernel-incompatible; R1 = kernel-compatible but unreachable; DL = reachable.  Corpus = states of rank >= 3."""
    D = U["D"]; NS = U["NS"]; targets = U["targets"]; corpus = U["rank"] >= 3
    states = np.nonzero(corpus)[0]
    R0 = R1 = DL = 0; per_t = []; r1_per_state = np.zeros(NS, dtype=np.int64); r1_state_t = []
    for j, t in enumerate(targets):
        comp = kernel_compatible(U, states, t); reach = D[states, j] >= 0
        assert not (reach & ~comp).any(), "reachable but kernel-incompatible: theorem violated"
        r0 = int((~comp).sum()); r1 = int((comp & ~reach).sum()); dl = int(reach.sum())
        R0 += r0; R1 += r1; DL += dl; per_t.append({"target": map_str(U["F"][t]), "R0": r0, "R1": r1, "reachable": dl, "R1_fraction_of_compatible": r1 / max(1, r1 + dl)})
        r1_per_state[states[comp & ~reach]] += 1
    # trap contribution: successor kernel-incompatible (explained by the invariant) vs kernel-compatible (R1 trap)
    tj = T["target_j"]; tdst = T["dst"]
    comp_succ = np.zeros(T["n"], dtype=bool)
    for j in range(len(targets)):
        m = tj == j
        if m.any():
            comp_succ[m] = kernel_compatible(U, tdst[m], targets[j])
    r1_traps = int(comp_succ.sum())
    hist = collections.Counter(r1_per_state[states].tolist())
    return {"corpus_states_rank_ge_3": int(corpus.sum()), "pairs": int(len(states) * len(targets)), "R0": R0, "R1": R1, "reachable": DL,
            "R1_fraction_of_kernel_compatible": R1 / max(1, R1 + DL), "R1_traps": r1_traps, "R1_trap_fraction_of_traps": r1_traps / max(1, T["n"]),
            "R0_traps": int(T["n"] - r1_traps), "per_target": per_t,
            "R1_per_state_histogram": {str(k): int(v) for k, v in sorted(hist.items())}, "R1_flags": comp_succ}


# ----------------------------------------------------------------------------- feature tables (pairwise-free)
def _pack(cols: list[np.ndarray]) -> np.ndarray:
    key = np.zeros(len(cols[0]), dtype=np.int64)
    for c in cols:
        c = c.astype(np.int64); key = key * (int(c.max()) + 2) + c
    return key


def _split(states: np.ndarray, frac: float = 0.6) -> np.ndarray:
    h = (states.astype(np.uint64) * np.uint64(11400714819323198485)) >> np.uint64(40)
    return (h % np.uint64(1000)).astype(np.int64) < int(frac * 1000)


def _pr_auc(score: np.ndarray, y: np.ndarray) -> float:
    order = np.argsort(-score, kind="stable"); ys = y[order]
    tp = np.cumsum(ys); k = np.arange(1, len(ys) + 1)
    prec = tp / k; rec = tp / max(1, ys.sum())
    # step-wise area (average precision)
    return float((prec * ys).sum() / max(1, ys.sum()))


def _binary_metrics(p: np.ndarray, y: np.ndarray, thr: float) -> dict:
    pred = p >= thr; tp = int((pred & y).sum()); fp = int((pred & ~y).sum()); fn = int((~pred & y).sum()); tn = int((~pred & ~y).sum())
    tpr = tp / max(1, tp + fn); tnr = tn / max(1, tn + fp)
    return {"threshold": thr, "precision": tp / max(1, tp + fp), "recall": tpr, "fpr": 1 - tnr, "balanced_accuracy": 0.5 * (tpr + tnr)}


def _entropy(p):
    p = p[(p > 0) & (p < 1)]; return float(-(p * np.log2(p) + (1 - p) * np.log2(1 - p)).sum())


def table_classifier(key_train, y_train, key_test, y_test, prior: float) -> dict:
    ku, inv = np.unique(key_train, return_inverse=True)
    cnt = np.bincount(inv, minlength=len(ku)).astype(float); pos = np.bincount(inv, weights=y_train.astype(float), minlength=len(ku))
    ptab = pos / cnt
    pos_t = np.searchsorted(ku, key_test); pos_t = np.clip(pos_t, 0, len(ku) - 1); seen = ku[pos_t] == key_test
    p = np.where(seen, ptab[pos_t], prior)
    y = y_test.astype(bool)
    # threshold chosen on TRAIN (best balanced accuracy over the table probabilities)
    p_train = ptab[inv]; ytr = y_train.astype(bool); best = (0.5, 0.5)
    for thr in np.unique(np.round(np.quantile(p_train, np.linspace(0.5, 0.999, 60)), 4)):
        m = _binary_metrics(p_train, ytr, thr)
        if m["balanced_accuracy"] > best[0]: best = (m["balanced_accuracy"], thr)
    m = _binary_metrics(p, y, best[1])
    # recall at precision >= 0.5
    order = np.argsort(-p, kind="stable"); ys = y[order]; tp = np.cumsum(ys); prec = tp / np.arange(1, len(ys) + 1); rec = tp / max(1, ys.sum())
    ok = prec >= 0.5; rec_at_p50 = float(rec[ok].max()) if ok.any() else 0.0
    # calibration
    bins = np.linspace(0, 1, 11); bi = np.clip(np.digitize(p, bins) - 1, 0, 9)
    calib = [{"bin": f"{bins[b]:.1f}-{bins[b+1]:.1f}", "n": int((bi == b).sum()), "mean_pred": float(p[bi == b].mean()) if (bi == b).any() else None,
              "observed": float(y[bi == b].mean()) if (bi == b).any() else None} for b in range(10)]
    # plug-in mutual information on test with train-estimated conditionals
    H = _entropy(np.array([prior])) if 0 < prior < 1 else 0.0
    pc = np.clip(p, 1e-12, 1 - 1e-12); Hc = float(np.mean(-(pc * np.log2(pc) + (1 - pc) * np.log2(1 - pc)))) if len(p) else 0.0
    return {"train_rows": int(len(key_train)), "test_rows": int(len(key_test)), "cells": int(len(ku)), "unseen_test_fraction": float(1 - seen.mean()),
            "pr_auc": _pr_auc(p, y.astype(float)), "base_rate_test": float(y.mean()), "best_train_threshold_metrics_on_test": m,
            "recall_at_precision_0.5": rec_at_p50, "calibration": calib, "H_trap_bits": H, "H_trap_given_features_bits": Hc,
            "normalised_MI": (H - Hc) / H if H > 0 else None}


def leakage_attack(U: dict, T: dict, R1_flags: np.ndarray | None = None, max_rows: int = 3_000_000, seed: int = 0) -> dict:
    """Trap prediction on rank-dropping actions from permitted features only.  Tuple A: action, rank f, rank f',
    block sizes f', counts of values 0/1 in f, rank t, block sizes t.  Tuple B: A + full count vectors of f' and t."""
    src, dst, rid, D, C, rank, bs = U["src"], U["dst"], U["rule"], U["D"], U["C"].astype(np.int64), U["rank"].astype(np.int64), U["bs_id"]
    fam = np.array([r.family for r in U["rules"]]); drop = fam[rid] == "rankdrop"
    E = np.nonzero(drop & (src != dst))[0]
    rows_e, rows_j, ys = [], [], []; total_rows = 0
    rng = np.random.default_rng(seed); per_target = max(1, max_rows // len(U["targets"]))
    for j in range(len(U["targets"])):
        live = D[src[E], j] >= 0; e = E[live]; total_rows += int(len(e))
        if len(e) > per_target:  # memory cap: seeded uniform subsample per target BEFORE concatenation
            e = e[rng.choice(len(e), per_target, replace=False)]
        rows_e.append(e.astype(np.int32)); rows_j.append(np.full(len(e), j, dtype=np.int32)); ys.append((D[dst[e], j] < 0))
    e = np.concatenate(rows_e); j = np.concatenate(rows_j); y = np.concatenate(ys)
    tj = np.array(U["targets"])[j]
    tr = _split(src[e])
    prior = float(y[tr].mean())
    ct = C[tj]
    A = _pack([rid[e], rank[src[e]], rank[dst[e]], np.unique(bs[dst[e]], return_inverse=True)[1], C[src[e], 0], C[src[e], 1], rank[tj], np.unique(bs[tj], return_inverse=True)[1]])
    Bcols = [A] + [C[dst[e], v] for v in range(U["n"])] + [ct[:, v] for v in range(U["n"])]
    B = _pack(Bcols)
    out = {"rows": int(len(e)), "total_live_rankdrop_triples": total_rows, "base_rate": float(y.mean()),
           "tuple_A": table_classifier(A[tr], y[tr], A[~tr], y[~tr], prior), "tuple_B": table_classifier(B[tr], y[tr], B[~tr], y[~tr], prior)}
    return out


def distance_attack(U: dict, max_rows: int = 250_000, seed: int = 0) -> dict:
    """Predict D on reachable (f, t) pairs from permitted features.  Table regressor on (rank f, rank t, block sizes f,
    block sizes t, count vector f, count vector t); linear regressor on numeric features."""
    from scipy.stats import spearmanr
    D, C, rank, bs = U["D"], U["C"].astype(np.int64), U["rank"].astype(np.int64), U["bs_id"]
    corpus = np.nonzero(U["rank"] >= 3)[0]
    rng = np.random.default_rng(seed); per_target = max(1, max_rows // D.shape[1]); Ss, Js = [], []
    for j in range(D.shape[1]):  # per-target subsample before concatenation (memory cap)
        s_ = corpus[D[corpus, j] >= 0]
        if len(s_) > per_target: s_ = s_[rng.choice(len(s_), per_target, replace=False)]
        Ss.append(s_.astype(np.int32)); Js.append(np.full(len(s_), j, dtype=np.int32))
    S = np.concatenate(Ss); J = np.concatenate(Js)
    tj = np.array(U["targets"])[J]; y = D[S, J].astype(np.float32); C = C.astype(np.int16)
    tr = _split(S)
    key = _pack([rank[S], rank[tj], np.unique(bs[S], return_inverse=True)[1], np.unique(bs[tj], return_inverse=True)[1]] + [C[S, v] for v in range(U["n"])] + [C[tj, v] for v in range(U["n"])])
    ku, inv = np.unique(key[tr], return_inverse=True); cnt = np.bincount(inv).astype(float); mean = np.bincount(inv, weights=y[tr]) / cnt
    pos = np.clip(np.searchsorted(ku, key[~tr]), 0, len(ku) - 1); seen = ku[pos] == key[~tr]
    pred = np.where(seen, mean[pos], y[tr].mean()); yt = y[~tr]
    ss = ((yt - yt.mean()) ** 2).sum()
    def metrics(pred):
        return {"R2": float(1 - ((yt - pred) ** 2).sum() / ss), "exact_match": float((np.round(pred) == yt).mean()), "within_1": float((np.abs(np.round(pred) - yt) <= 1).mean()),
                "MAE": float(np.abs(pred - yt).mean()), "spearman": float(spearmanr(pred, yt).correlation)}
    CS = C[S].astype(np.int32); CT = C[tj].astype(np.int32)
    X = np.stack([rank[S], rank[tj], rank[S] - rank[tj], np.abs(CS - CT).sum(axis=1), (CS * CT).sum(axis=1), np.ones(len(S))], axis=1).astype(np.float32)
    del CS, CT
    beta, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None); lin = X[~tr] @ beta
    return {"rows": int(len(S)), "train_rows": int(tr.sum()), "test_rows": int((~tr).sum()), "cells": int(len(ku)), "unseen_test_fraction": float(1 - seen.mean()),
            "std_D_test": float(yt.std()), "table_regressor": metrics(pred), "linear_regressor": metrics(lin),
            "rank_only_baseline": metrics(np.where(seen, mean[pos], yt.mean()) * 0 + np.array([y[tr][(rank[S][tr] == r)].mean() if (rank[S][tr] == r).any() else y[tr].mean() for r in rank[S][~tr]])),
            "linear_coefficients": {"rank_f": beta[0], "rank_t": beta[1], "rank_diff": beta[2], "L1_count_distance": beta[3], "count_dot": beta[4], "intercept": beta[5]}}
