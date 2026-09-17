"""AC-01D-v2 Steps 2-5: transparent coordinates on the canonical (f, t) orbit; how much of C5, CP, C6 and true D they explain;
residual test.  No D-derived quantity is a coordinate.  Fitting: closed-form ridge, additive tables (exact conditional
means), sklearn decision trees of bounded depth, degree-2 polynomial ridge.  All fitted on FIT rows, evaluated on HELD_BOTH.

Coordinates (all functions of the canonical pair only):
  rank_f, rank_t, rank_diff (= minimum number of collapses, since each collapse lowers rank by exactly 1 and the target rank is 2)
  count vector of f (7), block-size multiset of f (7, descending)
  target block sizes (2): sizes of the two target blocks
  joint table J[v, b] = number of positions i with f(i) = v and t(i) = b   (7 x 2 = 14 entries; the canonical pair IS this table)
  from J: for each target block b, the number of distinct f-values present (nv_b), the largest f-class inside block b (maxin_b),
          number of f-values that straddle both blocks (straddle), number of f-values entirely inside block 0 / block 1 (pure_0, pure_1),
          total positions in straddling values (straddle_mass)
  orbit size, stabiliser size
  cyclic-displacement proxies: for the canonical f arrangement, min over rotations r of #positions with f(i) != (i + r) mod 7 (how far
          the image pattern is from a rotation), and whether values 0 and 1 (the swap/collapse values) are present, and their counts
Everything is integer-valued and small.
"""
from __future__ import annotations
import json, os, time
import numpy as np
import torch
from ..corpus import build
from ..families.c2_cp import digit_index
from ..interpret.dissect_c5 import load_c5, hidden, FIT_MEAN
from ..families.c6_dsl import DSLRep, terminals, evaluate as dsl_eval
from .canonical import canonical_pair, pair_index

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WDIR = os.path.join(HERE, "results", "ac01d", "families", "weights")


def coords(fd: np.ndarray, td: np.ndarray) -> tuple[np.ndarray, list[str]]:
    fc, tc, stab, orb = canonical_pair(fd, td)
    n = len(fd); names = []; cols = []
    cnt = np.stack([(fc == v).sum(1) for v in range(7)], 1)                       # count vector of f
    rank_f = (cnt > 0).sum(1); rank_t = np.full(n, 2)
    cols += [rank_f, rank_f - 2]; names += ["rank_f", "rank_diff"]
    for v in range(7): cols.append(cnt[:, v]); names.append(f"cnt_{v}")
    bs = -np.sort(-cnt, 1)
    for k in range(7): cols.append(bs[:, k]); names.append(f"block_{k}")
    tb0 = (tc == 0).sum(1); cols += [tb0, 7 - tb0]; names += ["tblock_0", "tblock_1"]
    J = np.zeros((n, 7, 2), dtype=np.int64)
    for v in range(7):
        for b in range(2): J[:, v, b] = ((fc == v) & (tc == b)).sum(1)
    for v in range(7):
        for b in range(2): cols.append(J[:, v, b]); names.append(f"J_{v}_{b}")
    nv = (J > 0).sum(1)                                                            # distinct f-values in each target block
    cols += [nv[:, 0], nv[:, 1]]; names += ["nvals_in_t0", "nvals_in_t1"]
    cols += [J[:, :, 0].max(1), J[:, :, 1].max(1)]; names += ["max_fclass_in_t0", "max_fclass_in_t1"]
    straddle = ((J[:, :, 0] > 0) & (J[:, :, 1] > 0)); cols.append(straddle.sum(1)); names.append("straddling_values")
    cols.append((straddle * cnt).sum(1)); names.append("straddle_mass")
    cols.append(((J[:, :, 0] > 0) & (J[:, :, 1] == 0)).sum(1)); names.append("pure_in_t0")
    cols.append(((J[:, :, 1] > 0) & (J[:, :, 0] == 0)).sum(1)); names.append("pure_in_t1")
    cols += [orb, stab]; names += ["orbit_size", "stabiliser"]
    rot = np.stack([(fc != ((np.arange(7) + r) % 7)[None, :]).sum(1) for r in range(7)], 1)
    cols.append(rot.min(1)); names.append("min_rotation_mismatch")
    cols += [cnt[:, 0], cnt[:, 1], (cnt[:, 0] > 0).astype(int), (cnt[:, 1] > 0).astype(int)]; names += ["cnt_val0", "cnt_val1", "has_val0", "has_val1"]
    return np.stack(cols, 1).astype(np.float64), names


def r2(y, p): return float(1 - ((y - p) ** 2).sum() / max(1e-9, ((y - y.mean()) ** 2).sum()))


def ridge(Xtr, ytr, Xte, lam=1.0):
    mu = Xtr.mean(0); sd = Xtr.std(0) + 1e-9; A = (Xtr - mu) / sd; B = (Xte - mu) / sd
    A = np.concatenate([A, np.ones((len(A), 1))], 1); B = np.concatenate([B, np.ones((len(B), 1))], 1)
    W = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ ytr); return B @ W


def table(keys_tr, ytr, keys_te, fallback):
    u, inv = np.unique(keys_tr, return_inverse=True); m = np.bincount(inv, weights=ytr) / np.bincount(inv)
    pos = np.clip(np.searchsorted(u, keys_te), 0, len(u) - 1); seen = u[pos] == keys_te
    return np.where(seen, m[pos], fallback), float(seen.mean()), int(len(u))


def run(n_fit=400000, n_te=150000, seed=0):
    t0 = time.perf_counter(); U, M, _ = build(); D = U["D"]; F = U["F"]; tg = np.array(U["targets"]); live = M["live"]
    sr, trole, pr = M["state_role"], M["target_role"], M["pair_role"]; rng = np.random.default_rng(seed)
    fit = live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 0); S, J = np.nonzero(fit); sel = rng.choice(len(S), n_fit, replace=False); S, J = S[sel], J[sel]
    hb = live & (sr == 2)[:, None] & (trole == 1)[None, :]; Se, Je = np.nonzero(hb); sel = rng.choice(len(Se), n_te, replace=False); Se, Je = Se[sel], Je[sel]
    Xtr, names = coords(F[S].astype(np.int64), F[tg[J]].astype(np.int64)); Xte, _ = coords(F[Se].astype(np.int64), F[tg[Je]].astype(np.int64))
    ytr = D[S, J].astype(np.float64); yte = D[Se, Je].astype(np.float64)
    # frozen model predictions on HELD_BOTH (diagnostic targets)
    net, _ = load_c5("medium"); _, _, _, o = hidden(net, digit_index(F, Se, tg[Je])); p_c5 = o + FIT_MEAN
    cp = np.load(os.path.join(WDIR, "C2-CP-r16.npz")); A_ = [cp[f"arr_{m}"].astype(np.float64) for m in range(14)]; idx = digit_index(F, Se, tg[Je])
    G = np.ones((n_te, A_[0].shape[1]))
    for m in range(14): G *= A_[m][idx[:, m]]
    p_cp = G.sum(1) + float(cp["mean"])
    c6 = json.load(open(os.path.join(HERE, "results", "ac01d", "families", "C6_dsl.json")))["result"]["fit"]
    from ..families.c6_dsl import to_str
    import ast as _ast
    def parse(s):
        # trees were serialised as s-expressions; re-parse
        toks = s.replace("(", " ( ").replace(")", " ) ").split(); pos = [0]
        def rd():
            t = toks[pos[0]]; pos[0] += 1
            if t == "(":
                op = toks[pos[0]]; pos[0] += 1; args = []
                while toks[pos[0]] != ")": args.append(rd())
                pos[0] += 1; return tuple([op] + args)
            return t
        return rd()
    trees = [parse(s) for s in c6["trees"]]; w6 = np.array(json.load(open(os.path.join(HERE, "results", "ac01d", "families", "C6_dsl.json")))["result"]["fit"].get("w", [])) if False else None
    # C6 weights are inside the serialized payload only; reconstruct by ridge on FIT with its own trees (identical procedure, same rows count)
    X6tr = terminals(F, S, tg[J]); X6te = terminals(F, Se, tg[Je])
    Phi_tr = np.stack([dsl_eval(t, X6tr) for t in trees] + [np.ones(n_fit, np.float32)], 1); Phi_te = np.stack([dsl_eval(t, X6te) for t in trees] + [np.ones(n_te, np.float32)], 1)
    W6 = np.linalg.solve(Phi_tr.T @ Phi_tr + 1.0 * np.eye(Phi_tr.shape[1]), Phi_tr.T @ (ytr - ytr.mean())); p_c6 = Phi_te @ W6 + ytr.mean()
    targets = {"true_D": yte, "C5_pred": p_c5, "CP_pred": p_cp, "C6_pred": p_c6, "C5_minus_CP": p_c5 - p_cp, "C5_minus_C6": p_c5 - p_c6}
    out = {"n_fit": n_fit, "n_test": n_te, "coordinates": names, "reference_R2_on_true_D": {"C5": r2(yte, p_c5), "CP_r16": r2(yte, p_cp), "C6": r2(yte, p_c6)}, "models": {}}
    # 1. linear ridge on all coordinates
    preds = {}
    preds["linear_all"] = {k: ridge(Xtr, (ytr if k == "true_D" else None) if False else ytr, Xte) for k in ["true_D"]}  # placeholder replaced below
    def fit_all(fn):
        res = {}
        for k, yt in targets.items():
            if k in ("true_D",): ytrain = ytr
            else:
                # diagnostic targets are defined on HELD rows only (frozen model outputs); fit on half of HELD_BOTH, test on the other half
                ytrain = None
            res[k] = fn(k, ytrain, yt)
        return res
    half = n_te // 2
    def eval_model(name, fitter):
        res = {}
        for k, yt in targets.items():
            if k == "true_D":
                p = fitter(Xtr, ytr, Xte); res[k] = {"R2": r2(yte, p), "exact": float((np.round(p) == yte).mean()), "within_1": float((np.abs(np.round(p) - yte) <= 1).mean())}
                if name == "additive_table_joint": res[k]["pred"] = p
            else:
                p = fitter(Xte[:half], yt[:half], Xte[half:]); res[k] = {"R2": r2(yt[half:], p)}
        out["models"][name] = res
    eval_model("linear_ridge", lambda A, y, B: ridge(A, y, B))
    # 2. degree-2 polynomial ridge on the 12 most basic coordinates (rank, counts, joint table summaries)
    basic = [names.index(x) for x in ["rank_f", "tblock_0", "nvals_in_t0", "nvals_in_t1", "max_fclass_in_t0", "max_fclass_in_t1", "straddling_values", "straddle_mass", "pure_in_t0", "pure_in_t1", "min_rotation_mismatch", "cnt_val0", "cnt_val1"]]
    def poly2(A, y, B):
        def ex(X):
            Xb = X[:, basic]; cross = np.stack([Xb[:, i] * Xb[:, j] for i in range(Xb.shape[1]) for j in range(i, Xb.shape[1])], 1); return np.concatenate([Xb, cross], 1)
        return ridge(ex(A), y, ex(B), lam=10.0)
    eval_model("poly2_ridge_basic13", poly2)
    # 3. additive tables: exact conditional mean over the canonical JOINT TABLE (14 integers) -- this is the full orbit id
    key_tr = pair_index(*canonical_pair(F[S].astype(np.int64), F[tg[J]].astype(np.int64))[:2]); key_te = pair_index(*canonical_pair(F[Se].astype(np.int64), F[tg[Je]].astype(np.int64))[:2])
    def tab_joint(A, y, B):
        ktr = key_tr if len(A) == n_fit else key_te[:half]; kte = key_te if len(B) == n_te else key_te[half:]
        p, cov, ncell = table(ktr, y, kte, y.mean()); tab_joint.cov = cov; tab_joint.cells = ncell; return p
    eval_model("additive_table_joint", tab_joint); out["models"]["additive_table_joint"]["coverage_on_test"] = tab_joint.cov; out["models"]["additive_table_joint"]["cells"] = tab_joint.cells
    # 4. table on coarser coordinates: (rank_f, tblock_0, nvals, maxin, straddle, pure) -- "orbit summary"
    coarse = [names.index(x) for x in ["rank_f", "tblock_0", "nvals_in_t0", "nvals_in_t1", "max_fclass_in_t0", "max_fclass_in_t1", "straddling_values", "straddle_mass", "pure_in_t0", "pure_in_t1"]]
    def keyc(X):
        k = np.zeros(len(X), np.int64)
        for c in coarse: k = k * 16 + X[:, c].astype(np.int64)
        return k
    def tab_coarse(A, y, B):
        p, cov, ncell = table(keyc(A), y, keyc(B), y.mean()); tab_coarse.cov = cov; tab_coarse.cells = ncell; return p
    eval_model("additive_table_orbit_summary10", tab_coarse); out["models"]["additive_table_orbit_summary10"]["coverage_on_test"] = tab_coarse.cov; out["models"]["additive_table_orbit_summary10"]["cells"] = tab_coarse.cells
    # 5. decision trees
    from sklearn.tree import DecisionTreeRegressor
    for depth in (6, 10, 16):
        def tree(A, y, B, depth=depth):
            m = DecisionTreeRegressor(max_depth=depth, min_samples_leaf=20, random_state=0).fit(A, y); return m.predict(B)
        eval_model(f"tree_depth{depth}", tree)
    # 5b. tree leaf count / bytes for the true-D tree at depth 16
    m16 = DecisionTreeRegressor(max_depth=16, min_samples_leaf=20, random_state=0).fit(Xtr, ytr); out["tree16_leaves"] = int(m16.get_n_leaves())
    # Step 5 residual test: residual of the best transparent model on true D
    best = max(("linear_ridge", "poly2_ridge_basic13", "additive_table_joint", "additive_table_orbit_summary10", "tree_depth16"), key=lambda k: out["models"][k]["true_D"]["R2"])
    out["best_transparent_model_on_true_D"] = best
    fitters = {"linear_ridge": lambda A, y, B: ridge(A, y, B), "poly2_ridge_basic13": poly2, "additive_table_joint": tab_joint, "additive_table_orbit_summary10": tab_coarse,
               "tree_depth16": lambda A, y, B: DecisionTreeRegressor(max_depth=16, min_samples_leaf=20, random_state=0).fit(A, y).predict(B)}
    p_best = fitters[best](Xtr, ytr, Xte); R = yte - p_best
    out["residual"] = {"var_ratio_residual_over_D": float(R.var() / yte.var()), "R2_of_C5_on_residual": r2(R, p_c5 - p_best), "R2_of_CP_on_residual": r2(R, p_cp - p_best),
                       "R2_of_C6_on_residual": r2(R, p_c6 - p_best), "residual_abs_mean": float(np.abs(R).mean()),
                       "residual_by_rank_f": {str(k): float(np.abs(R[Xte[:, 0] == k]).mean()) for k in np.unique(Xte[:, 0])},
                       "residual_by_orbit_size": {str(int(k)): float(np.abs(R[Xte[:, names.index('orbit_size')] == k]).mean()) for k in np.unique(Xte[:, names.index("orbit_size")])}}
    # representation complexity of the exact orbit table (all 289,247 orbits) -- Step 1 deliverable
    import lzma
    allS, allJ = np.nonzero(live); keys_all = np.zeros(len(allS), np.int64); dall = D[live].astype(np.int64)
    for a in range(0, len(allS), 500000):
        b = min(len(allS), a + 500000); fc, tc, _, _ = canonical_pair(F[allS[a:b]].astype(np.int64), F[tg[allJ[a:b]]].astype(np.int64)); keys_all[a:b] = pair_index(fc, tc)
    u, first = np.unique(keys_all, return_index=True); orbit_D = dall[first]
    blob = u.astype(np.int64).tobytes() + orbit_D.astype(np.uint8).tobytes()
    out["orbit_table"] = {"orbits": int(len(u)), "raw_bytes": len(blob), "lzma_bytes": len(lzma.compress(blob, preset=6)), "CR_vs_denominator": 1060696 / len(lzma.compress(blob, preset=6)), "exact": True}
    out["seconds"] = round(time.perf_counter() - t0, 1)
    od = os.path.join(HERE, "results", "ac01d", "v2"); os.makedirs(od, exist_ok=True)
    for mname in out["models"]:
        out["models"][mname]["true_D"].pop("pred", None)
    json.dump(out, open(os.path.join(od, "coordinates.json"), "w"), indent=1, default=float); return out


if __name__ == "__main__":
    r = run()
    print(json.dumps({k: v for k, v in r.items() if k not in ("coordinates",)}, indent=1, default=float))
