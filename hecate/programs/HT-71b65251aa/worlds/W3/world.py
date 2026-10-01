"""HT-71b65251aa / W3: metacognitively gated RSA recursion depth.

See IMPLEMENTATION_NOTES.md. Writes rows.jsonl (one row per (arm, seed)).
"""
import json
import os
import time

import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

N_CONTEXTS = 2000
SEEDS = list(range(10))
THETAS = [0.6, 0.7, 0.8, 0.9]
MAX_DEPTH = 3
ALPHA = 1.0
SIZES = [3, 4]
UTTS = ["SOME_A", "ALL_A", "SOME_B", "ALL_B"]
PARAMS = dict(n_contexts=N_CONTEXTS, thetas=THETAS, max_depth=MAX_DEPTH,
              alpha=ALPHA, sizes=SIZES, utterances=UTTS, speaker="S2_sampled",
              prior="uniform", cost=0.0)

# object types: (level_A, level_B), levels 0 none, 1 some-not-all, 2 all
TYPES = [(a, b) for a in range(3) for b in range(3) if (a, b) != (0, 0)]


def features(t):
    a, b = t
    return np.array([a >= 1, a == 2, b >= 1, b == 2], dtype=float)


FEAT = np.array([features(t) for t in TYPES])  # 8 x 4


def listeners(sem):
    """sem: objects x utterances literal truth. Returns L[k] (utt x obj), S[k] (obj x utt)."""
    L, S = [], [None]
    colsum = sem.sum(0, keepdims=True)
    L0 = np.where(colsum > 0, sem / np.where(colsum > 0, colsum, 1), 0.0).T  # utt x obj
    L.append(L0)
    for k in range(1, MAX_DEPTH + 1):
        prev = L[k - 1].T  # obj x utt
        w = np.where(prev > 0, prev ** ALPHA, 0.0)
        rs = w.sum(1, keepdims=True)
        Sk = np.where(rs > 0, w / np.where(rs > 0, rs, 1), 0.0)  # obj x utt
        S.append(Sk)
        cs = Sk.sum(0, keepdims=True)
        Lk = np.where(cs > 0, Sk / np.where(cs > 0, cs, 1), 0.0).T  # utt x obj
        L.append(Lk)
    return L, S


def score(post, target):
    m = post.max()
    arg = np.flatnonzero(np.isclose(post, m, atol=1e-12))
    return (1.0 / len(arg)) if target in arg else 0.0, arg


def sp(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if np.all(x == x[0]) or np.all(y == y[0]):
        return float("nan")
    return float(spearmanr(x, y).correlation)


def nanfix(v):
    return None if (isinstance(v, float) and np.isnan(v)) else v


def run_seed(seed):
    rng = np.random.default_rng(seed)
    items = []
    for _ in range(N_CONTEXTS):
        n = int(rng.choice(SIZES))
        idx = rng.choice(len(TYPES), size=n, replace=False)
        sem = FEAT[idx]  # n x 4
        tgt = int(rng.integers(n))
        L, S = listeners(sem)
        u = int(rng.choice(4, p=S[2][tgt]))
        amb = int(sem[:, u].sum())
        acc_k, arg_k, maxp_k = [], [], []
        for k in range(MAX_DEPTH + 1):
            post = L[k][u]
            a, arg = score(post, tgt)
            acc_k.append(a); arg_k.append(frozenset(arg.tolist())); maxp_k.append(float(post.max()))
        items.append(dict(size=n, amb=amb, acc=acc_k, arg=arg_k, maxp=maxp_k))
    return items


def adaptive_depth(it, theta):
    for k in range(MAX_DEPTH + 1):
        if it["maxp"][k] >= theta - 1e-12:
            return k
    return MAX_DEPTH


def stats(depths, accs, ambs):
    return dict(accuracy=float(np.mean(accs)), mean_depth=float(np.mean(depths)),
                spearman_depth_ambiguity=nanfix(sp(depths, ambs)), n_items=len(accs))


def main():
    t0 = time.process_time()
    fh = open(ROWS, "w", encoding="utf-8")

    def emit(row):
        row.update(params=PARAMS)
        fh.write(json.dumps(row) + "\n"); fh.flush()

    for seed in SEEDS:
        items = run_seed(seed)
        amb = np.array([it["amb"] for it in items]); size = np.array([it["size"] for it in items])
        acc = np.array([it["acc"] for it in items])  # items x 4
        twin_rng = np.random.default_rng(10_000 + seed)

        # CONTROL: fixed depths (L2, L3 per spec; L0, L1 as diagnostics)
        ctrl = {f"L{k}": stats(np.full(len(items), k), acc[:, k], amb) for k in range(MAX_DEPTH + 1)}
        diff = {f"frac_L{k}_argmax_differs_from_L2": float(np.mean([it["arg"][k] != it["arg"][2] for it in items]))
                for k in (0, 1, 3)}
        impl = [len(it["arg"][2]) < it["amb"] for it in items]
        impl_succ = [acc[i, 2] for i, f in enumerate(impl) if f]
        emit(dict(arm="CONTROL", seed=seed, fixed=ctrl, diagnostics=dict(
            **diff, frac_ambiguity_1=float(np.mean(amb == 1)),
            implicature_rate_L2=float(np.mean(impl)),
            implicature_success_L2=float(np.mean(impl_succ)) if impl_succ else None,
            spearman_size_ambiguity=nanfix(sp(size, amb)))))

        treat, twin, pos = {}, {}, {}
        for th in THETAS:
            d = np.array([adaptive_depth(it, th) for it in items])
            a = acc[np.arange(len(items)), d]
            s = stats(d, a, amb)
            s["depth_hist"] = [int((d == k).sum()) for k in range(MAX_DEPTH + 1)]
            s["spearman_within_size3"] = nanfix(sp(d[size == 3], amb[size == 3]))
            s["spearman_within_size4"] = nanfix(sp(d[size == 4], amb[size == 4]))
            s["spearman_depth_size"] = nanfix(sp(d, size))
            treat[str(th)] = s
            dt = twin_rng.permutation(d)
            at = acc[np.arange(len(items)), dt]
            twin[str(th)] = stats(dt, at, amb)
            u = amb == 1
            pos[str(th)] = dict(n_unique=int(u.sum()), all_depth0=bool(np.all(d[u] == 0)),
                                all_correct=bool(np.all(a[u] == 1.0)),
                                accuracy=float(a[u].mean()) if u.any() else None,
                                mean_depth=float(d[u].mean()) if u.any() else None)
        emit(dict(arm="TREATMENT", seed=seed, by_theta=treat))
        emit(dict(arm="NULL_TWIN", seed=seed, by_theta=twin))
        emit(dict(arm="POSITIVE_CONTROL", seed=seed, by_theta=pos))

        # CHEAT: observable written directly, mechanism bypassed
        dc = np.where(amb == 1, 0, 1)
        emit(dict(arm="CHEAT", seed=seed, injected=stats(dc, np.ones(len(items)), amb)))

    fh.close()
    cpu = time.process_time() - t0
    with open(os.path.join(HERE, "world_cpu_seconds.json"), "w", encoding="utf-8") as f:
        json.dump({"cpu_seconds": cpu}, f)
    print(f"done, cpu {cpu:.2f}s")


if __name__ == "__main__":
    main()
