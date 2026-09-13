"""Family C2 (tensor), decomposition 1 of 3: CP over digit modes with masked ALS.

Tensor index: 7 state digits (values 0..6) and 7 target digits (values 0..1; digit 0 is always 0) = 14 modes.
Entry value: D(s, t) - FIT mean.  Model: sum_r prod_m A_m[i_m, r].  Fitted by alternating least squares over the
observed FIT entries only (train states x train targets, pair role fit) with ridge lambda; VAL RMSE monitors early
stopping (VAL is the only set allowed to steer hyperparameters).  Eligible for ALL four held sets because every digit
value is seen in training: an unseen state or target is a new combination of seen digit values.
Input policy: raw digits only.  No pairwise features, no kernel, no D lookups at prediction time.
Storage: factors in float16 after lzma.
"""
from __future__ import annotations
import json, lzma, os, time
import numpy as np
from ..corpus import build
from ..evaluate import Context, DENOM_LZMA, write_result

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def digit_index(F, states, targets):
    """(n, 14) int array of mode indices."""
    return np.concatenate([F[states].astype(np.int64), F[targets].astype(np.int64)], axis=1)


class CPRep:
    def __init__(self, name, factors, mean, F, nbytes):
        self.name = name; self.A = factors; self.mean = mean; self.F = F; self.serialized_bytes = nbytes
        self.eligible_sets = ["HELD_PAIRS", "HELD_STATES", "HELD_TARGETS", "HELD_BOTH"]; self.reach_score = None

    def predict_D(self, states, targets):
        idx = digit_index(self.F, np.asarray(states), np.asarray(targets))
        G = np.ones((len(idx), self.A[0].shape[1]), dtype=np.float64)
        for m in range(14):
            G *= self.A[m][idx[:, m]]
        return G.sum(axis=1) + self.mean


def fit_cp(ctx: Context, rank: int, sweeps: int = 25, lam: float = 1e-4, seed: int = 0, max_obs: int = 1_500_000):
    U, M = ctx.U, ctx.M; D = U["D"]; F = U["F"]; tg = np.array(U["targets"])
    sr, trole, pr, live = M["state_role"], M["target_role"], M["pair_role"], M["live"]
    fit = live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 0)
    S, J = np.nonzero(fit)
    rng0 = np.random.default_rng(seed + 1)
    if len(S) > max_obs:  # memory cap on this host: ALS gathers are (observed x rank) float32
        sel = rng0.choice(len(S), max_obs, replace=False); S, J = S[sel], J[sel]
    y_all = D[S, J].astype(np.float32); mean = float(y_all.mean()); y = y_all - mean
    idx = digit_index(F, S, tg[J]).astype(np.int16)
    val = live & (sr == 1)[:, None] & (trole == 0)[None, :]
    Sv, Jv = np.nonzero(val); rng = np.random.default_rng(seed)
    if len(Sv) > 200000: sel = rng.choice(len(Sv), 200000, replace=False); Sv, Jv = Sv[sel], Jv[sel]
    idxv = digit_index(F, Sv, tg[Jv]).astype(np.int16); yv = D[Sv, Jv].astype(np.float32) - mean
    sizes = [7] * 7 + [2] * 7
    # 14-mode products vanish for small factors (0.3**13 ~ 1e-7), which lets the ridge term dominate and collapses the
    # model to the mean (observed in the first run: R^2 = 0 at every rank).  Initialise near 1 so products are O(1).
    A = [(1.0 + 0.2 * rng.standard_normal((sz, rank))).astype(np.float32) for sz in sizes]
    A[0] *= 0.1  # scale lives in one mode
    def predict(idx_):
        G = np.ones((len(idx_), rank), dtype=np.float32)
        for m in range(14): G *= A[m][idx_[:, m]]
        return G.sum(axis=1)
    history = []; best = (1e9, None, 0)
    for sweep in range(sweeps):
        for m in range(14):
            G = np.ones((len(idx), rank), dtype=np.float32)
            for m2 in range(14):
                if m2 != m: G *= A[m2][idx[:, m2]]
            col = idx[:, m]
            for v in range(sizes[m]):
                sel = col == v
                if not sel.any(): continue
                Gv = G[sel]; GtG = Gv.T @ Gv + lam * np.eye(rank, dtype=np.float32); Gty = Gv.T @ y[sel]
                A[m][v] = np.linalg.solve(GtG, Gty)
        rmse_fit = float(np.sqrt(((predict(idx) - y) ** 2).mean())); rmse_val = float(np.sqrt(((predict(idxv) - yv) ** 2).mean()))
        history.append((sweep, rmse_fit, rmse_val))
        if rmse_val < best[0]: best = (rmse_val, [a.copy() for a in A], sweep)
        elif sweep - best[2] >= 4: break
    A = best[1]
    nbytes = len(lzma.compress(b"".join(a.astype(np.float16).tobytes() for a in A), preset=6))
    return CPRep(f"C2-CP-r{rank}", [a.astype(np.float64) for a in A], mean, F, nbytes), {"rank": rank, "observed": int(len(S)), "best_sweep": best[2], "val_rmse": best[0],
                                                                                            "history": history, "bytes_lzma": nbytes, "CR": DENOM_LZMA / nbytes, "std_D_fit": float(y.std())}


def run(ranks=(4, 16, 32), per_set=300):
    t0 = time.perf_counter(); ctx = Context(per_set=per_set); out = {"family": "C2 CP over digit modes (masked ALS)", "ranks": {}}
    for r in ranks:
        rep, info = fit_cp(ctx, r); ev = ctx.evaluate(rep); ev["fit"] = info; out["ranks"][str(r)] = ev
        summary = {k: {kk: (round(vv.get("HC_D_transitions"), 3) if vv.get("HC_D_transitions") is not None else None, vv.get("mean_excess"), vv.get("failures"), vv.get("dominance")) for kk, vv in v.items() if kk in ("GBFS", "DFS")} for k, v in ev["sets"].items()}
        print(json.dumps({"rank": r, "CR": round(ev["CR"], 1), "val_rmse": round(info["val_rmse"], 3), "std_D": round(info["std_D_fit"], 3), "sets": summary,
                          "distance": {k: (round(v["distance"]["R2"], 3), round(v["distance"]["exact"], 3), round(v["distance"]["within_1"], 3)) for k, v in ev["sets"].items() if "distance" in v}}), flush=True)
        write_result(out, "C2_cp")
    out["seconds"] = round(time.perf_counter() - t0, 1); print(write_result(out, "C2_cp")); return out


if __name__ == "__main__":
    run()
