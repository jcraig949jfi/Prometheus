"""AC-01D frozen baselines and headroom capture HC_D.  No representation is fitted; the feature model is the
strongest PERMITTED ordinary model (table regressor over pairwise-free features), fitted on FIT pairs only.

Policies (all prune kernel-incompatible successors, i.e. reachability is supplied, as the AC-01D denominator requires):
  KA        kernel-aware, residual-blind: order by rank distance then action order       (denominator, HC_D = 0)
  KA+FM     kernel-aware + permitted feature model: order by predicted successor distance
  KA+LA3    kernel-aware + exact lookahead depth 3 (SAFE proofs), cost charged per call
  ORACLE    exact D descent                                                              (HC_D = 1)
HC_D = 1 - (C_M - C_O) / (C_K - C_O), computed as ratio of sums per evaluation set with a bootstrap interval over problems.
Failures are reported separately and never averaged into cost.
"""
from __future__ import annotations
import collections, json, os, time
import numpy as np
from .corpus import build, save
from ..universe.metrics import Searcher
from ..universe.monoid import ecc_region_by_class
from ..gate2.observation_monoid import MonoidObserver, sample_ball_costs
from ..gate2.navigation2 import guided_dfs, Cost
import heapq


def gbfs(obs, key_fn, s0, j, Dcol, budget=40000):
    """Greedy best-first search: pop the lowest-key open state, expand, push kernel-compatible children (tier-2 pruned).
    Returns the same record shape as guided_dfs; path length is the tree depth of the target when popped."""
    cost = Cost(); t = obs.targets[j]; fi, fx = obs.fi, obs.fx
    if s0 == t: return {"solved": True, "path_len": 0, "excess": 0, "trap_transitions": 0, "exp": 0, "exm": 0, "look_exp": 0.0, "look_exm": 0.0, "calls": 0}
    heap = [((0,), 0, s0, 0)]; seen = {s0}; d0 = int(Dcol[s0]); traps = 0; n = 0
    while heap:
        k, _, s, depth = heapq.heappop(heap)
        succ = fx[fi[s]:fi[s + 1]]; cost.exp += 1; cost.exm += len(succ)
        for i, u in enumerate(succ):
            if u in seen: continue
            kk = key_fn(u, j, i, cost)
            if kk[0] == 2: continue
            seen.add(u); n += 1
            if Dcol[s] >= 0 and Dcol[u] < 0: traps += 1
            if u == t:
                return {"solved": True, "path_len": depth + 1, "excess": depth + 1 - d0, "trap_transitions": traps, "exp": cost.exp, "exm": cost.exm, "look_exp": cost.look_exp, "look_exm": cost.look_exm, "calls": cost.calls}
            heapq.heappush(heap, (kk, n, u, depth + 1))
        if cost.exp > budget: break
    return {"solved": False, "path_len": -1, "excess": -1, "trap_transitions": traps, "exp": cost.exp, "exm": cost.exm, "look_exp": cost.look_exp, "look_exm": cost.look_exm, "calls": cost.calls}
from ..gate2 import analysis2 as A

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def feature_model(U, M):
    """Table regressor D ~ (rank f, rank t, block sizes f, block sizes t, count vector f, count vector t) on FIT pairs."""
    D, C, rank, bs = U["D"], U["C"].astype(np.int64), U["rank"].astype(np.int64), U["bs_id"]
    fit = M["live"] & (M["state_role"] == 0)[:, None] & (M["target_role"] == 0)[None, :] & (M["pair_role"] == 0)
    S, J = np.nonzero(fit); tj = np.array(U["targets"])[J]
    rng = np.random.default_rng(0)
    if len(S) > 1_500_000:
        sel = rng.choice(len(S), 1_500_000, replace=False); S, J, tj = S[sel], J[sel], tj[sel]
    bs_u, bs_inv_all = np.unique(bs, return_inverse=True)
    def key_for(s, t):
        return A._pack([rank[s], rank[t], bs_inv_all[s], bs_inv_all[t]] + [C[s, v] for v in range(U["n"])] + [C[t, v] for v in range(U["n"])])
    key = key_for(S, tj); y = D[S, J].astype(np.float64)
    ku, inv = np.unique(key, return_inverse=True); mean = np.bincount(inv, weights=y) / np.bincount(inv)
    rk = A._pack([rank[S], rank[tj]]); rku, rinv = np.unique(rk, return_inverse=True); rmean = np.bincount(rinv, weights=y) / np.bincount(rinv)
    gmean = float(y.mean())
    def predict(s_arr, t_arr):
        k = key_for(s_arr, t_arr); pos = np.clip(np.searchsorted(ku, k), 0, len(ku) - 1); seen = ku[pos] == k
        r = A._pack([rank[s_arr], rank[t_arr]]); rp = np.clip(np.searchsorted(rku, r), 0, len(rku) - 1); rseen = rku[rp] == r
        return np.where(seen, mean[pos], np.where(rseen, rmean[rp], gmean))
    return predict, {"fit_rows": int(len(S)), "cells": int(len(ku))}


def make_policies(U, M, obs, predict, ball):
    kmask = U["kmask"]; targets = U["targets"]; rank = obs.rank; D = U["D"]
    def dead(s, t): return s != t and (rank[s] < rank[t] or (kmask[s] & ~kmask[t]) != 0)
    def ka(s, j, idx, cost):
        t = targets[j]
        if s == t: return (0, 0, idx)
        if dead(s, t): return (2, 0, idx)
        return (1, int(rank[s]) - int(rank[t]), idx)
    cache = {}
    def kafm(s, j, idx, cost):
        t = targets[j]
        if s == t: return (0, 0, idx)
        if dead(s, t): return (2, 0, idx)
        k = (s, j)
        if k not in cache: cache[k] = float(predict(np.array([s]), np.array([t]))[0])
        return (1, cache[k], idx)
    bc = ball["3"]
    def kala3(s, j, idx, cost):
        t = targets[j]
        if s == t: return (0, 0, idx)
        if dead(s, t): return (2, 0, idx)
        v = obs.verdict(s, j, 3); cost.calls += 1; cost.look_exp += bc["mean_states_expanded"]; cost.look_exm += bc["mean_transitions_examined"]
        if v == "SAFE": return (0, int(D[s, j]), idx)
        return (1, int(rank[s]) - int(rank[t]), idx)
    return {"KA": ("dfs", ka), "KA+FM": ("dfs", kafm), "KA+LA3": ("dfs", kala3), "KA-GBFS": ("gbfs", ka), "KA+FM-GBFS": ("gbfs", kafm)}


def sample_eval_problems(U, M, per_set, seed, min_d=5):
    D = U["D"]; live = M["live"]; sr, trole, pr = M["state_role"], M["target_role"], M["pair_role"]
    sets = {"HELD_PAIRS": live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 1),
            "HELD_STATES": live & (sr == 2)[:, None] & (trole == 0)[None, :],
            "HELD_TARGETS": live & (sr == 0)[:, None] & (trole == 1)[None, :],
            "HELD_BOTH": live & (sr == 2)[:, None] & (trole == 1)[None, :]}
    rng = np.random.default_rng(seed); out = {}
    for name, m in sets.items():
        m = m & (D >= min_d); S, J = np.nonzero(m)
        pick = rng.choice(len(S), min(per_set, len(S)), replace=False)
        out[name] = [(int(S[i]), int(J[i]), int(D[S[i], J[i]])) for i in pick]
    return out


def hc(cm, co, ck):
    return float(1 - (cm.sum() - co.sum()) / max(1e-9, (ck.sum() - co.sum())))


def bootstrap_hc(cm, co, ck, n=1000, seed=0):
    rng = np.random.default_rng(seed); vals = []
    for _ in range(n):
        i = rng.integers(0, len(cm), len(cm)); vals.append(hc(cm[i], co[i], ck[i]))
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def run(per_set=100, budget=40000, seed=20260912):
    t0 = time.perf_counter()
    U, M, manifest = build(); save(U, M, manifest)
    ecc, region, _ = ecc_region_by_class(U); obs = MonoidObserver(U, ecc, region)
    ball = sample_ball_costs(obs, U, 2000, seed)
    predict, fm_info = feature_model(U, M)
    # feature-model prediction quality on held-out sets (distance channel), for the record
    D = U["D"]; live = M["live"]; sr, trole, pr = M["state_role"], M["target_role"], M["pair_role"]; tg = np.array(U["targets"])
    fmq = {}
    for name, m in {"HELD_PAIRS": live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 1), "HELD_STATES": live & (sr == 2)[:, None] & (trole == 0)[None, :],
                    "HELD_TARGETS": live & (sr == 0)[:, None] & (trole == 1)[None, :], "HELD_BOTH": live & (sr == 2)[:, None] & (trole == 1)[None, :]}.items():
        S, J = np.nonzero(m); rng = np.random.default_rng(1)
        if len(S) > 300000: sel = rng.choice(len(S), 300000, replace=False); S, J = S[sel], J[sel]
        p = predict(S, tg[J]); y = D[S, J].astype(float)
        fmq[name] = {"rows": int(len(S)), "R2": float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()), "exact": float((np.round(p) == y).mean()), "within_1": float((np.abs(np.round(p) - y) <= 1).mean()), "MAE": float(np.abs(p - y).mean())}
    S_ = Searcher(U); pols = make_policies(U, M, obs, predict, ball)
    probs = sample_eval_problems(U, M, per_set, seed)
    res = {"feature_model": fm_info, "feature_model_quality": fmq, "ball_costs": ball, "per_set": {}, "budget": budget, "per_set_problems": per_set}
    for name, plist in probs.items():
        O = np.array([[S_.oracle(s, j)["states_expanded"], S_.oracle(s, j)["transitions_examined"]] for s, j, d in plist], float)
        rows = {"oracle": {"mean_states": float(O[:, 0].mean()), "mean_transitions": float(O[:, 1].mean()), "mean_D": float(np.mean([d for _, _, d in plist]))}}
        costs = {}
        for pn, (kind, pol) in pols.items():
            R = [(guided_dfs if kind == "dfs" else gbfs)(obs, pol, s, j, D[:, j], budget) for s, j, d in plist]
            st = np.array([r["exp"] + r["look_exp"] for r in R], float); tr = np.array([r["exm"] + r["look_exm"] for r in R], float)
            solved = np.array([r["solved"] for r in R]); ex = np.array([r["excess"] for r in R if r["solved"]], float)
            costs[pn] = (st, tr)
            rows[pn] = {"solve_rate": float(solved.mean()), "failures": int((~solved).sum()), "mean_states": float(st.mean()), "mean_transitions": float(tr.mean()),
                        "mean_excess": float(ex.mean()) if len(ex) else None, "mean_path": float(np.mean([r["path_len"] for r in R if r["solved"]])) if solved.any() else None,
                        "traps_taken": float(np.mean([r["trap_transitions"] for r in R]))}
        ck_s, ck_t = costs["KA"]
        for pn in pols:
            cs, ct = costs[pn]
            rows[pn]["HC_D_transitions"] = hc(ct, O[:, 1], ck_t); rows[pn]["HC_D_transitions_CI95"] = bootstrap_hc(ct, O[:, 1], ck_t)
            rows[pn]["HC_D_states"] = hc(cs, O[:, 0], ck_s); rows[pn]["HC_D_states_CI95"] = bootstrap_hc(cs, O[:, 0], ck_s)
        res["per_set"][name] = rows
    res["seconds"] = round(time.perf_counter() - t0, 1)
    out = os.path.join(HERE, "results", "ac01d"); os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "baselines.json"), "w") as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == "__main__":
    r = run()
    print(json.dumps({"fm": r["feature_model"], "fmq": r["feature_model_quality"],
                      "sets": {k: {p: {kk: v[p][kk] for kk in v[p] if kk in ("solve_rate", "failures", "mean_transitions", "mean_excess", "HC_D_transitions", "HC_D_transitions_CI95", "HC_D_states")} for p in v} for k, v in r["per_set"].items()},
                      "seconds": r["seconds"]}, indent=1))
