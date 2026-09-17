"""Family C1: masked low-rank completion of the state x target distance chart (train states x train targets).

Method: hard-impute truncated SVD (iterative): start from the FIT-mean, replace observed cells by their FIT values,
take the rank-r SVD, repeat.  Only FIT entries are observed; held pairs, val/test states and held targets are never
read.  Eligible set: HELD_PAIRS only (no input encoding for unseen states or targets).  Storage = float16 factors
(states x r, targets x r) after lzma.  Structural note recorded in the result: a per-state factor cannot beat the
denominator (823,543 states x r x 2 bytes vs 1,060,696 bytes) unless r = 0, so C1 places a (CR, HC_D) point only.
"""
from __future__ import annotations
import json, lzma, os, time
import numpy as np
from ..corpus import build
from ..evaluate import Context, DENOM_LZMA, write_result

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LowRankRep:
    def __init__(self, name, U_s, V_t, state_index, target_index, mean, nbytes):
        self.name = name; self.Us = U_s; self.Vt = V_t; self.si = state_index; self.ti = target_index; self.mean = mean
        self.serialized_bytes = nbytes; self.eligible_sets = ["HELD_PAIRS"]; self.reach_score = None

    def predict_D(self, states, targets):
        si = self.si[states]; ti = self.ti[targets]; ok = (si >= 0) & (ti >= 0)
        out = np.full(len(states), np.nan)
        if ok.any():
            out[ok] = (self.Us[si[ok]] * self.Vt[ti[ok]]).sum(axis=1) + self.mean
        return out


def fit(ctx: Context, rank: int, iters: int = 20):
    U, M = ctx.U, ctx.M; D = U["D"]
    sr, trole, pr, live, corpus = M["state_role"], M["target_role"], M["pair_role"], M["live"], M["corpus"]
    tr_s = np.nonzero((sr == 0) & corpus)[0]; tr_t = np.nonzero(trole == 0)[0]
    obs = live[np.ix_(tr_s, tr_t)] & (pr[np.ix_(tr_s, tr_t)] == 0)
    X = D[np.ix_(tr_s, tr_t)].astype(np.float32)
    mean = float(X[obs].mean()); Y = np.where(obs, X - mean, 0.0).astype(np.float32)
    Z = Y.copy()
    for _ in range(iters):
        Uf, s, Vh = np.linalg.svd(Z, full_matrices=False)
        L = (Uf[:, :rank] * s[:rank]) @ Vh[:rank]
        Z = np.where(obs, Y, L).astype(np.float32)
    Uf, s, Vh = np.linalg.svd(Z, full_matrices=False)
    Us = (Uf[:, :rank] * np.sqrt(s[:rank])).astype(np.float16); Vt = (Vh[:rank].T * np.sqrt(s[:rank])).astype(np.float16)
    nbytes = len(lzma.compress(Us.tobytes() + Vt.tobytes(), preset=6))
    si = np.full(U["NS"], -1, dtype=np.int64); si[tr_s] = np.arange(len(tr_s))
    ti = np.full(U["NS"], -1, dtype=np.int64); ti[np.array(U["targets"])[tr_t]] = np.arange(len(tr_t))
    fit_rmse = float(np.sqrt((((Us.astype(np.float32) @ Vt.astype(np.float32).T) - Y)[obs] ** 2).mean()))
    return LowRankRep(f"C1-lowrank-r{rank}", Us.astype(np.float32), Vt.astype(np.float32), si, ti, mean, nbytes), {"rank": rank, "fit_rmse": fit_rmse, "observed_cells": int(obs.sum()), "bytes_lzma": nbytes, "CR": DENOM_LZMA / nbytes}


def run(ranks=(1, 2, 4, 8), per_set=300):
    t0 = time.perf_counter(); ctx = Context(per_set=per_set); out = {"family": "C1 masked low-rank completion", "ranks": {}}
    for r in ranks:
        rep, info = fit(ctx, r); ev = ctx.evaluate(rep); ev["fit"] = info; out["ranks"][str(r)] = ev
        print(json.dumps({"rank": r, "CR": round(ev["CR"], 3), "HELD_PAIRS": {k: (v.get("HC_D_transitions"), v.get("mean_excess"), v.get("failures")) for k, v in ev["sets"]["HELD_PAIRS"].items() if k in ("GBFS", "DFS")},
                          "distance": ev["sets"]["HELD_PAIRS"].get("distance")}), flush=True)
    out["structural_note"] = "per-state factors cost >= 823,543 x r x 2 bytes before compression; CR < 1 for every r >= 1 at float16"
    out["seconds"] = round(time.perf_counter() - t0, 1)
    print(write_result(out, "C1_lowrank")); return out


if __name__ == "__main__":
    run()
