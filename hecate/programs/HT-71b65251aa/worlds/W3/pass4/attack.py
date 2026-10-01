"""HT-71b65251aa / W3 Pass 4 attacks: R, ORIG, ALT. See NOTES.md.

Writes rows.jsonl: one row per (attack, arm, seed), flushed per row.
Prints no treatment statistic.
"""
import json
import os
import time

import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

N_CONTEXTS = 2000
SEEDS = list(range(100, 110))
THETAS = [0.6, 0.7, 0.8, 0.9]
MAX_DEPTH = 3
SIZES = [3, 4]
UTTS = ["SOME_A", "ALL_A", "SOME_B", "ALL_B"]
TYPES = [(a, b) for a in range(3) for b in range(3) if (a, b) != (0, 0)]
FEAT = np.array([[a >= 1, a == 2, b >= 1, b == 2] for a, b in TYPES], dtype=float)

ORIGINAL = dict(name="ORIGINAL", alpha=1.0, cost=[0.0, 0.0, 0.0, 0.0])
ALT_V1 = dict(name="ALT_V1", alpha=4.0, cost=[0.0, 0.0, 0.0, 0.0])
ALT_V2 = dict(name="ALT_V2", alpha=4.0, cost=[0.0, 1.0, 0.0, 1.0])
ELIG_GAP = 0.02  # PREREG: fixed-L2 acc - fixed-L1 acc >= 0.02


def listeners(sem, alpha, cost):
    L, S = [], [None]
    colsum = sem.sum(0, keepdims=True)
    L.append(np.where(colsum > 0, sem / np.where(colsum > 0, colsum, 1), 0.0).T)  # utt x obj
    c = np.exp(-alpha * np.asarray(cost))[None, :]  # 1 x utt; all ones when cost 0
    for k in range(1, MAX_DEPTH + 1):
        prev = L[k - 1].T  # obj x utt
        w = np.where(prev > 0, prev ** alpha, 0.0) * c
        rs = w.sum(1, keepdims=True)
        Sk = np.where(rs > 0, w / np.where(rs > 0, rs, 1), 0.0)
        S.append(Sk)
        cs = Sk.sum(0, keepdims=True)
        L.append(np.where(cs > 0, Sk / np.where(cs > 0, cs, 1), 0.0).T)
    return L, S


def score(post, target):
    m = post.max()
    arg = np.flatnonzero(np.isclose(post, m, atol=1e-12))
    return (1.0 / len(arg)) if target in arg else 0.0, arg


def sp(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 2 or np.all(x == x[0]) or np.all(y == y[0]):
        return None
    return float(spearmanr(x, y).correlation)


def entropy(p):
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def run_seed(seed, var):
    rng = np.random.default_rng(seed)
    items = []
    for _ in range(N_CONTEXTS):
        n = int(rng.choice(SIZES))
        idx = rng.choice(len(TYPES), size=n, replace=False)
        sem = FEAT[idx]
        tgt = int(rng.integers(n))
        L, S = listeners(sem, var["alpha"], var["cost"])
        u = int(rng.choice(4, p=S[2][tgt]))
        amb = int(sem[:, u].sum())
        acc_k, arg_k, maxp_k = [], [], []
        for k in range(MAX_DEPTH + 1):
            a, arg = score(L[k][u], tgt)
            acc_k.append(a); arg_k.append(frozenset(arg.tolist())); maxp_k.append(float(L[k][u].max()))
        items.append(dict(size=n, amb=amb, acc=acc_k, arg=arg_k, maxp=maxp_k,
                          H0=entropy(L[0][u]), unc1=1.0 - float(L[1][u].max())))
    return items


def adaptive_depth(it, theta):
    for k in range(MAX_DEPTH + 1):
        if it["maxp"][k] >= theta - 1e-12:
            return k
    return MAX_DEPTH


def stats(d, a, amb, H0, unc1):
    return dict(accuracy=float(np.mean(a)), mean_depth=float(np.mean(d)),
                spearman_depth_ambiguity=sp(d, amb), spearman_depth_uncertainty=sp(d, H0),
                spearman_depth_unc1=sp(d, unc1), n_items=len(a))


def world_rows(attack, var, seed, emit):
    """Emit CONTROL, TREATMENT, NULL_TWIN, POSITIVE_CONTROL, CHEAT rows; return fixed accs."""
    items = run_seed(seed, var)
    amb = np.array([it["amb"] for it in items]); size = np.array([it["size"] for it in items])
    H0 = np.array([it["H0"] for it in items]); unc1 = np.array([it["unc1"] for it in items])
    acc = np.array([it["acc"] for it in items])
    twin_rng = np.random.default_rng(10_000 + seed)
    ctrl = {f"L{k}": stats(np.full(len(items), k), acc[:, k], amb, H0, unc1) for k in range(MAX_DEPTH + 1)}
    diag = {f"frac_L{k}_argmax_differs_from_L2": float(np.mean([it["arg"][k] != it["arg"][2] for it in items]))
            for k in (0, 1, 3)}
    diag["frac_ambiguity_1"] = float(np.mean(amb == 1))
    base = dict(attack=attack, variant=var["name"], seed=seed)
    emit(dict(base, arm="CONTROL", fixed=ctrl, diagnostics=diag))
    treat, twin, pos = {}, {}, {}
    for th in THETAS:
        d = np.array([adaptive_depth(it, th) for it in items])
        a = acc[np.arange(len(items)), d]
        s = stats(d, a, amb, H0, unc1)
        s["depth_hist"] = [int((d == k).sum()) for k in range(MAX_DEPTH + 1)]
        s["spearman_within_size3"] = sp(d[size == 3], amb[size == 3])
        s["spearman_within_size4"] = sp(d[size == 4], amb[size == 4])
        treat[str(th)] = s
        dt = twin_rng.permutation(d)
        twin[str(th)] = stats(dt, acc[np.arange(len(items)), dt], amb, H0, unc1)
        u = amb == 1
        pos[str(th)] = dict(n_unique=int(u.sum()), all_depth0=bool(np.all(d[u] == 0)),
                            all_correct=bool(np.all(a[u] == 1.0)))
    emit(dict(base, arm="TREATMENT", by_theta=treat))
    emit(dict(base, arm="NULL_TWIN", by_theta=twin))
    emit(dict(base, arm="POSITIVE_CONTROL", by_theta=pos))
    dc = np.where(amb == 1, 0, 1)
    emit(dict(base, arm="CHEAT", injected=stats(dc, np.ones(len(items)), amb, H0, unc1)))
    return ctrl, treat


def main():
    t0 = time.process_time()
    fh = open(ROWS, "w", encoding="utf-8")

    def emit(row, var):
        row.update(params=dict(n_contexts=N_CONTEXTS, thetas=THETAS, max_depth=MAX_DEPTH, sizes=SIZES,
                               utterances=UTTS, speaker="S2_sampled", prior="uniform",
                               alpha=var["alpha"], cost=var["cost"], seeds=SEEDS))
        fh.write(json.dumps(row) + "\n"); fh.flush()

    # R and ORIG: original world, seeds 100..109
    for seed in SEEDS:
        ctrl, treat = world_rows("R", ORIGINAL, seed, lambda r: emit(r, ORIGINAL))
        emit(dict(attack="ORIG", variant="ORIGINAL", seed=seed, arm="FIXED_L1",
                  accuracy=ctrl["L1"]["accuracy"], mean_depth=ctrl["L1"]["mean_depth"]), ORIGINAL)
        emit(dict(attack="ORIG", variant="ORIGINAL", seed=seed, arm="ADAPTIVE",
                  by_theta={th: dict(accuracy=v["accuracy"], mean_depth=v["mean_depth"])
                            for th, v in treat.items()}), ORIGINAL)

    # ALT: V1, then V2 only if V1 is not eligible (pre-declared rule)
    tried = []
    for var in (ALT_V1, ALT_V2):
        gaps = []
        for seed in SEEDS:
            ctrl, _ = world_rows("ALT", var, seed, lambda r, v=var: emit(r, v))
            gaps.append((ctrl["L2"]["accuracy"], ctrl["L1"]["accuracy"]))
        eligible = float(np.mean([g[0] for g in gaps]) - np.mean([g[1] for g in gaps])) >= ELIG_GAP
        tried.append(dict(variant=var["name"], eligible=eligible))
        if eligible:
            break

    fh.close()
    cpu = time.process_time() - t0
    with open(os.path.join(HERE, "attack_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"cpu_seconds": cpu, "alt_variants_tried": [t["variant"] for t in tried]}, f)
    print(f"done, cpu {cpu:.2f}s, ALT variants run: {[t['variant'] for t in tried]}")


if __name__ == "__main__":
    main()
