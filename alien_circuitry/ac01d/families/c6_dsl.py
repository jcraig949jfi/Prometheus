"""Family C6: evolved symbolic representation (small typed DSL, genetic programming), the exploratory arm.

Terminals: state digits s0..s6 (0..6), target digits t0..t6 (0..1), integer constants 0..7.
Operators (all vectorised): add, sub, mul, max, min, abs, eq (a == b -> 1/0), lt, ite (cond ? a : b),
  cnt_s(k) = number of state positions with digit k, cnt_t(k) likewise, and rank_s = number of distinct state digits.
A program is a random expression tree of bounded depth; the representation is a small ensemble (ridge-combined)
of evolved trees, serialised as its expression strings plus weights.  Fitness = RMSE on a FIT subsample; selection by
VAL RMSE (the only set allowed to steer).  The DSL may construct pairwise equalities of state digits internally
(discovery from raw digits is allowed); nothing hands it the kernel or D.
Eligible for all four held sets.  Budget: generations x population bounded by wall-clock.
"""
from __future__ import annotations
import json, lzma, os, random, time
import numpy as np
from ..evaluate import Context, DENOM_LZMA, write_result
from .c2_cp import digit_index

TERMS = [f"s{i}" for i in range(7)] + [f"t{i}" for i in range(7)] + [f"c{k}" for k in range(8)] + [f"ns{k}" for k in range(7)] + [f"nt{k}" for k in range(2)] + ["rank"]
BIN = ["add", "sub", "mul", "max", "min", "eq", "lt"]; UN = ["abs"]; TER = ["ite"]


def evaluate(node, X):
    """X: dict of terminal arrays (float32). node: nested tuples."""
    if isinstance(node, str): return X[node]
    op = node[0]
    if op == "abs": return np.abs(evaluate(node[1], X))
    if op == "ite":
        c = evaluate(node[1], X); return np.where(c > 0, evaluate(node[2], X), evaluate(node[3], X))
    a, b = evaluate(node[1], X), evaluate(node[2], X)
    if op == "add": return a + b
    if op == "sub": return a - b
    if op == "mul": return np.clip(a * b, -1e4, 1e4)
    if op == "max": return np.maximum(a, b)
    if op == "min": return np.minimum(a, b)
    if op == "eq": return (a == b).astype(np.float32)
    if op == "lt": return (a < b).astype(np.float32)
    raise ValueError(op)


def rand_tree(rng, depth):
    if depth <= 0 or rng.random() < 0.25: return rng.choice(TERMS)
    r = rng.random()
    if r < 0.8: return (rng.choice(BIN), rand_tree(rng, depth - 1), rand_tree(rng, depth - 1))
    if r < 0.9: return ("abs", rand_tree(rng, depth - 1))
    return ("ite", rand_tree(rng, depth - 1), rand_tree(rng, depth - 1), rand_tree(rng, depth - 1))


def mutate(rng, node, depth=3):
    if rng.random() < 0.15 or isinstance(node, str): return rand_tree(rng, depth)
    node = list(node); i = rng.randrange(1, len(node)); node[i] = mutate(rng, node[i], depth - 1); return tuple(node)


def crossover(rng, a, b):
    if isinstance(a, str) or rng.random() < 0.3: return b
    a = list(a); i = rng.randrange(1, len(a)); a[i] = crossover(rng, a[i], b); return tuple(a)


def to_str(node):
    return node if isinstance(node, str) else "(" + " ".join([node[0]] + [to_str(n) for n in node[1:]]) + ")"


def terminals(F, states, targets):
    idx = digit_index(F, states, targets).astype(np.float32); X = {}
    for i in range(7): X[f"s{i}"] = idx[:, i]; X[f"t{i}"] = idx[:, 7 + i]
    for k in range(8): X[f"c{k}"] = np.full(len(idx), float(k), dtype=np.float32)
    for k in range(7): X[f"ns{k}"] = (idx[:, :7] == k).sum(axis=1).astype(np.float32)
    for k in range(2): X[f"nt{k}"] = (idx[:, 7:] == k).sum(axis=1).astype(np.float32)
    X["rank"] = np.array([len(set(r)) for r in idx[:, :7].astype(int).tolist()], dtype=np.float32)
    return X


class DSLRep:
    def __init__(self, name, trees, weights, mean, F, nbytes):
        self.name = name; self.trees = trees; self.w = weights; self.mean = mean; self.F = F; self.serialized_bytes = nbytes
        self.eligible_sets = ["HELD_PAIRS", "HELD_STATES", "HELD_TARGETS", "HELD_BOTH"]; self.reach_score = None
        self._cache = {}

    def features(self, states, targets):
        X = terminals(self.F, np.asarray(states), np.asarray(targets))
        return np.stack([evaluate(t, X) for t in self.trees] + [np.ones(len(states), dtype=np.float32)], axis=1)

    def predict_D(self, states, targets):
        return self.features(states, targets) @ self.w + self.mean


def ridge(Phi, y, lam=1.0):
    A = Phi.T @ Phi + lam * np.eye(Phi.shape[1]); return np.linalg.solve(A, Phi.T @ y)


def run(pop=120, generations=30, n_trees=24, fit_rows=150_000, per_set=300, wall_limit_s=1500, seed=0):
    t0 = time.perf_counter(); ctx = Context(per_set=per_set); U, M = ctx.U, ctx.M; D = U["D"]; F = U["F"]; tg = np.array(U["targets"])
    sr, trole, pr, live = M["state_role"], M["target_role"], M["pair_role"], M["live"]; rng = random.Random(seed); nrng = np.random.default_rng(seed)
    fit = live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 0); S, J = np.nonzero(fit); sel = nrng.choice(len(S), fit_rows, replace=False); S, J = S[sel], J[sel]
    val = live & (sr == 1)[:, None] & (trole == 0)[None, :]; Sv, Jv = np.nonzero(val); sel = nrng.choice(len(Sv), 60000, replace=False); Sv, Jv = Sv[sel], Jv[sel]
    mean = float(D[S, J].mean()); y = D[S, J].astype(np.float32) - mean; yv = D[Sv, Jv].astype(np.float32) - mean
    X = terminals(F, S, tg[J]); Xv = terminals(F, Sv, tg[Jv])
    # evolve single trees by correlation with the residual of a growing ridge ensemble (forward stagewise GP)
    trees, hist = [], []
    def ensemble_pred(ts, Xd):
        if not ts: return np.zeros(len(next(iter(Xd.values()))), dtype=np.float32), None
        Phi = np.stack([evaluate(t, Xd) for t in ts] + [np.ones(len(next(iter(Xd.values()))), dtype=np.float32)], axis=1)
        return Phi, None
    w = None
    for stage in range(n_trees):
        if time.perf_counter() - t0 > wall_limit_s: break
        Phi_cur = np.stack([evaluate(t, X) for t in trees] + [np.ones(len(y), dtype=np.float32)], axis=1)
        w = ridge(Phi_cur, y); resid = y - Phi_cur @ w
        population = [rand_tree(rng, 4) for _ in range(pop)]
        def fitness(t):
            v = evaluate(t, X); v = v - v.mean(); n = np.linalg.norm(v)
            return float(abs(v @ resid) / n) if n > 1e-6 and np.isfinite(n) else 0.0
        scores = [fitness(t) for t in population]
        for g in range(generations):
            order = np.argsort(scores)[::-1]; elite = [population[i] for i in order[:pop // 4]]
            children = []
            while len(children) < pop - len(elite):
                a, b = rng.choice(elite), rng.choice(elite)
                child = crossover(rng, a, b) if rng.random() < 0.6 else mutate(rng, a)
                children.append(child)
            population = elite + children; scores = [fitness(t) for t in population]
        best = population[int(np.argmax(scores))]; trees.append(best)
        Phi_cur = np.stack([evaluate(t, X) for t in trees] + [np.ones(len(y), dtype=np.float32)], axis=1); w = ridge(Phi_cur, y)
        Phi_v = np.stack([evaluate(t, Xv) for t in trees] + [np.ones(len(yv), dtype=np.float32)], axis=1)
        rmse_fit = float(np.sqrt(((Phi_cur @ w - y) ** 2).mean())); rmse_val = float(np.sqrt(((Phi_v @ w - yv) ** 2).mean()))
        hist.append({"stage": stage, "tree": to_str(best), "rmse_fit": rmse_fit, "rmse_val": rmse_val, "t": round(time.perf_counter() - t0)})
        print(json.dumps(hist[-1]), flush=True)
    # select the ensemble size by VAL
    best_k = min(range(1, len(trees) + 1), key=lambda k: hist[k - 1]["rmse_val"]); trees = trees[:best_k]
    Phi_cur = np.stack([evaluate(t, X) for t in trees] + [np.ones(len(y), dtype=np.float32)], axis=1); w = ridge(Phi_cur, y)
    payload = json.dumps({"trees": [to_str(t) for t in trees], "w": w.astype(np.float32).tolist(), "mean": mean}).encode()
    nbytes = len(lzma.compress(payload, preset=6))
    rep = DSLRep(f"C6-DSL-{best_k}trees", trees, w.astype(np.float32), mean, F, nbytes)
    ev = ctx.evaluate(rep); ev["fit"] = {"trees": [to_str(t) for t in trees], "history": hist, "bytes_lzma": nbytes, "fit_rows": fit_rows, "pop": pop, "generations": generations}
    out = {"family": "C6 evolved DSL (forward-stagewise genetic programming, ridge ensemble)", "result": ev, "seconds": round(time.perf_counter() - t0, 1)}
    summary = {k: {kk: (round(vv.get("HC_D_transitions"), 3) if vv.get("HC_D_transitions") is not None else None, vv.get("mean_excess"), vv.get("failures"), vv.get("dominance")) for kk, vv in v.items() if kk in ("GBFS", "DFS")} for k, v in ev["sets"].items()}
    print(json.dumps({"CR": round(ev["CR"], 1), "trees": best_k, "sets": summary, "distance": {k: (round(v["distance"]["R2"], 3), round(v["distance"]["exact"], 3), round(v["distance"]["within_1"], 3)) for k, v in ev["sets"].items() if "distance" in v}}, indent=1))
    print(write_result(out, "C6_dsl")); return out


if __name__ == "__main__":
    run()
