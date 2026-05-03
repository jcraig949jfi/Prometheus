"""Phase 2(A): sample-only TT proof skeletons.

HARD CONSTRAINT. Operators may touch only the fixed sample pool S_train.
T_TRUE is constructed once in order to draw samples and to hold out S_val;
it is NEVER referenced inside any op_* function. Enforced by code discipline.

Four gates reported after evolution:
  1. Diversity:          top-5 by val_err -> >=3 distinct op-type signatures
  2. Generalization:     val/train error ratio (target ~1)
  3. Operator contribution: drop-one ablation delta on top-3 elites
  4. Archive orthogonality: Spearman(length, -log10 val_err) should be weak
"""

import json
import os
import random
import time
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).parent
SEED = 43
rng = np.random.default_rng(SEED)
random.seed(SEED)

D = 6
N = 8
RANK_CAP = 10
N_TRAIN = 8192
N_VAL = 4096
SAMPLE_CHOICES = [128, 512, 2048, 8192]


def build_target():
    ks = np.arange(N, dtype=float)
    phi1 = np.sin(2 * np.pi * ks / N)
    phi2 = np.cos(2 * np.pi * ks / N)
    phi3 = (ks / (N - 1)) ** 2 - 0.3
    T = np.zeros((N,) * D)
    for phi in (phi1, phi2, phi3):
        outer = phi
        for _ in range(D - 1):
            outer = np.multiply.outer(outer, phi)
        T = T + outer
    return T


_T_FULL = build_target()


def _draw_disjoint_pools():
    r = np.random.default_rng(777)
    flat = r.choice(N ** D, size=N_TRAIN + N_VAL, replace=False)
    X = np.zeros((N_TRAIN + N_VAL, D), dtype=int)
    for k in range(D):
        X[:, k] = (flat // N ** (D - 1 - k)) % N
    F = _T_FULL[X[:, 0], X[:, 1], X[:, 2], X[:, 3], X[:, 4], X[:, 5]]
    return X[:N_TRAIN], F[:N_TRAIN], X[N_TRAIN:], F[N_TRAIN:]


X_TRAIN, F_TRAIN, X_VAL, F_VAL = _draw_disjoint_pools()
F_TRAIN_NORM = float(np.linalg.norm(F_TRAIN))
F_VAL_NORM = float(np.linalg.norm(F_VAL))

# Delete the full tensor reference to make oracle access impossible by accident
del _T_FULL


def tt_eval(cores, X):
    n = X.shape[0]
    V = np.ones((n, 1))
    for j in range(len(cores)):
        idx = X[:, j]
        sl = np.transpose(cores[j][:, idx, :], (1, 0, 2))
        V = np.einsum("ia,iab->ib", V, sl)
    return V.squeeze(-1)


def sample_err(cores, X, f, f_norm):
    try:
        pred = tt_eval(cores, X)
        return float(np.linalg.norm(pred - f) / f_norm)
    except Exception:
        return float("inf")


def tt_ranks(cores):
    return [cores[0].shape[0]] + [G.shape[-1] for G in cores]


def max_rank(cores):
    rs = tt_ranks(cores)[1:-1]
    return max(rs) if rs else 1


def random_tt(ranks, scale=0.1):
    return [rng.standard_normal((ranks[k], N, ranks[k + 1])) * scale
            for k in range(len(ranks) - 1)]


def tt_orth_rl(cores):
    cores = [G.copy() for G in cores]
    for k in range(len(cores) - 1, 0, -1):
        G = cores[k]
        r_p, nk, r_n = G.shape
        Q, R = np.linalg.qr(G.reshape(r_p, nk * r_n).T)
        r_new = Q.shape[1]
        cores[k] = Q.T.reshape(r_new, nk, r_n)
        cores[k - 1] = np.tensordot(cores[k - 1], R.T, axes=[[-1], [0]])
    return cores


def tt_round(cores, eps=1e-12, max_rank_cap=None):
    cores = tt_orth_rl(cores)
    for k in range(len(cores) - 1):
        G = cores[k]
        r_p, nk, r_n = G.shape
        U, S, Vt = np.linalg.svd(G.reshape(r_p * nk, r_n), full_matrices=False)
        if len(S) == 0:
            r_new = 1
        else:
            cutoff = eps * S[0]
            r_new = max(1, int(np.sum(S > cutoff)))
            if max_rank_cap is not None:
                r_new = min(r_new, max_rank_cap)
        cores[k] = U[:, :r_new].reshape(r_p, nk, r_new)
        cores[k + 1] = np.tensordot(np.diag(S[:r_new]) @ Vt[:r_new, :],
                                    cores[k + 1], axes=[[-1], [0]])
    return cores


def als_sweep_samples(cores, X, f):
    cores = [G.copy() for G in cores]
    d = len(cores)
    n = X.shape[0]
    for k in range(d):
        L = np.ones((n, 1))
        for j in range(k):
            idx = X[:, j]
            sl = np.transpose(cores[j][:, idx, :], (1, 0, 2))
            L = np.einsum("ia,iab->ib", L, sl)
        R = np.ones((n, 1))
        for j in range(d - 1, k, -1):
            idx = X[:, j]
            sl = np.transpose(cores[j][:, idx, :], (1, 0, 2))
            R = np.einsum("iab,ib->ia", sl, R)
        r_p = L.shape[1]
        r_n = R.shape[1]
        outer = np.einsum("ia,ib->iab", L, R)
        xk = X[:, k]
        J = np.zeros((n, r_p, N, r_n))
        J[np.arange(n), :, xk, :] = outer
        J = J.reshape(n, r_p * N * r_n)
        try:
            g_vec, *_ = np.linalg.lstsq(J, f, rcond=None)
            cores[k] = g_vec.reshape(r_p, N, r_n)
        except np.linalg.LinAlgError:
            pass
    return cores


# --------------------------------------------------------------------------
# Operators. NONE of these may access the full target tensor.
# --------------------------------------------------------------------------

def op_fit(state, p):
    """ALS on a random subsample of S_train. The only sample-consuming op."""
    n = min(p["n"], N_TRAIN)
    iters = p["iters"]
    if n < N_TRAIN:
        idx = rng.choice(N_TRAIN, size=n, replace=False)
        X_s = X_TRAIN[idx]
        F_s = F_TRAIN[idx]
    else:
        X_s = X_TRAIN
        F_s = F_TRAIN
    cores = state
    for _ in range(iters):
        cores = als_sweep_samples(cores, X_s, F_s)
    return cores


def op_rerank(state, p):
    target = p["rank"]
    cur = max_rank(state)
    if cur == target:
        return state
    if cur > target:
        return tt_round(state, eps=1e-15, max_rank_cap=target)
    new = [G.copy() for G in state]
    d = len(new)
    for k in range(1, d):
        gL, gR = new[k - 1], new[k]
        r_pL, nL, rk = gL.shape
        rk2, nR, r_n = gR.shape
        if rk < target and rk == rk2:
            amount = target - rk
            padL = rng.standard_normal((r_pL, nL, amount)) * 0.01
            padR = rng.standard_normal((amount, nR, r_n)) * 0.01
            new[k - 1] = np.concatenate([gL, padL], axis=-1)
            new[k] = np.concatenate([gR, padR], axis=0)
    return new


def op_perturb(state, p):
    sigma = p["sigma"]
    return [G + rng.standard_normal(G.shape) * sigma for G in state]


def op_expand(state, p):
    k = p["bond"]
    amount = p["amount"]
    if k < 1 or k >= len(state):
        return state
    new = [G.copy() for G in state]
    gL, gR = new[k - 1], new[k]
    r_pL, nL, rk = gL.shape
    rk2, nR, r_n = gR.shape
    if rk != rk2:
        return state
    padL = rng.standard_normal((r_pL, nL, amount)) * 0.01
    padR = rng.standard_normal((amount, nR, r_n)) * 0.01
    new[k - 1] = np.concatenate([gL, padL], axis=-1)
    new[k] = np.concatenate([gR, padR], axis=0)
    return new


def op_compress(state, p):
    return tt_round(state, eps=1e-15, max_rank_cap=p["target"])


def op_refine(state, p):
    return tt_round(state, eps=p["eps"])


def op_symmetrize(state, p):
    rev = [np.transpose(G, (2, 1, 0)) for G in state[::-1]]
    try:
        return [0.5 * (a + b) for a, b in zip(state, rev)]
    except ValueError:
        return state


def op_reseed(state, p):
    rank = p["rank"]
    return random_tt([1] + [rank] * (D - 1) + [1], scale=0.1)


APPLY = {
    "fit": op_fit,
    "rerank": op_rerank,
    "perturb": op_perturb,
    "expand": op_expand,
    "compress": op_compress,
    "refine": op_refine,
    "symmetrize": op_symmetrize,
    "reseed": op_reseed,
}
OP_NAMES = list(APPLY.keys())


def sample_op():
    name = random.choice(OP_NAMES)
    if name == "fit":
        return (name, {"n": random.choice(SAMPLE_CHOICES),
                       "iters": random.randint(1, 3)})
    if name == "rerank":
        return (name, {"rank": random.randint(1, 8)})
    if name == "perturb":
        return (name, {"sigma": 10 ** random.uniform(-4, -1)})
    if name == "expand":
        return (name, {"bond": random.randint(1, D - 1),
                       "amount": random.randint(1, 3)})
    if name == "compress":
        return (name, {"target": random.randint(1, 8)})
    if name == "refine":
        return (name, {"eps": 10 ** random.uniform(-10, -3)})
    if name == "symmetrize":
        return (name, {})
    if name == "reseed":
        return (name, {"rank": random.randint(1, 6)})
    raise ValueError(name)


def apply_sequence(genome):
    state = random_tt([1] * (D + 1), scale=0.1)
    for name, params in genome:
        try:
            state = APPLY[name](state, params)
        except Exception:
            pass
    return state


def evaluate(genome):
    try:
        state = apply_sequence(genome)
        tr = sample_err(state, X_TRAIN, F_TRAIN, F_TRAIN_NORM)
        va = sample_err(state, X_VAL, F_VAL, F_VAL_NORM)
        r = max_rank(state)
        if not (np.isfinite(tr) and np.isfinite(va)):
            return None
        return r, tr, va, state
    except Exception:
        return None


def max_samples_used(genome):
    nm = 0
    for name, p in genome:
        if name == "fit":
            nm = max(nm, p.get("n", 0))
    return nm


def samples_bin(n):
    if n < 64: return 0
    if n < 256: return 1
    if n < 512: return 2
    if n < 1024: return 3
    return 4


def err_bin(e):
    if e <= 1e-12: return 12
    return int(np.clip(np.floor(-np.log10(e + 1e-15)), 0, 12))


def bin_key(r, err, nmax):
    return (min(r, RANK_CAP), err_bin(err), samples_bin(nmax))


def consider(archive, genome, r, tr, va, nmax):
    key = bin_key(r, tr, nmax)
    if key not in archive or tr < archive[key]["train_err"]:
        archive[key] = {
            "genome": list(genome), "rank": r,
            "train_err": tr, "val_err": va, "n_max": nmax,
        }


def mutate(genome):
    g = list(genome)
    roll = random.random()
    if roll < 0.35:
        if g:
            g[random.randrange(len(g))] = sample_op()
        else:
            g.append(sample_op())
    elif roll < 0.65:
        g.insert(random.randint(0, len(g)), sample_op())
    elif roll < 0.85 and len(g) > 1:
        g.pop(random.randrange(len(g)))
    else:
        if len(g) > 2:
            i, j = sorted(random.sample(range(len(g)), 2))
            block = g[i:j + 1]
            random.shuffle(block)
            g[i:j + 1] = block
    return g


def crossover(a, b):
    if not a: return list(b)
    if not b: return list(a)
    return a[:random.randrange(len(a))] + b[random.randrange(len(b)):]


def random_genome():
    return [sample_op() for _ in range(random.randint(1, 6))]


def run(pop_size=40, gens=60, log_every=5):
    t0 = time.time()
    archive = {}
    pop = [random_genome() for _ in range(pop_size)]
    history = []
    for gen in range(gens):
        for g in pop:
            result = evaluate(g)
            if result is None: continue
            rank, tr, va, _ = result
            consider(archive, g, rank, tr, va, max_samples_used(g))
        if not archive:
            pop = [random_genome() for _ in range(pop_size)]
            continue
        keys = list(archive.keys())
        new_pop = []
        for _ in range(pop_size):
            r = random.random()
            if r < 0.15:
                new_pop.append(random_genome())
            elif r < 0.55 or len(keys) < 2:
                new_pop.append(mutate(archive[random.choice(keys)]["genome"]))
            else:
                k1, k2 = random.sample(keys, 2)
                new_pop.append(mutate(crossover(archive[k1]["genome"],
                                                archive[k2]["genome"])))
        pop = new_pop
        if gen % log_every == 0 or gen == gens - 1:
            best = min(archive.values(), key=lambda v: v["val_err"])
            print(f"gen {gen:3d} | cells={len(archive):3d} | "
                  f"best val={best['val_err']:.3e} tr={best['train_err']:.3e} "
                  f"r={best['rank']} n={best['n_max']} | "
                  f"t={time.time()-t0:.1f}s", flush=True)
            history.append({
                "gen": gen, "archive_size": len(archive),
                "best_val": best["val_err"], "best_train": best["train_err"],
                "best_rank": best["rank"],
            })
    return archive, history


# --------------------------------------------------------------------------
# Gates
# --------------------------------------------------------------------------

def op_histogram(genome):
    ops = [op[0] for op in genome]
    if not ops: return {}
    total = len(ops)
    h = {}
    for o in ops:
        h[o] = h.get(o, 0) + 1.0 / total
    return h


def jsd(h1, h2):
    keys = set(h1) | set(h2)
    if not keys: return 0.0
    p = np.array([h1.get(k, 0) for k in keys])
    q = np.array([h2.get(k, 0) for k in keys])
    m = (p + q) / 2.0
    def kl(a, b):
        mask = (a > 0) & (b > 0)
        return float(np.sum(a[mask] * np.log(a[mask] / b[mask])))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def distinct_clusters(genomes, threshold=0.15):
    sigs = [op_histogram(g) for g in genomes]
    groups = []
    for i, s in enumerate(sigs):
        placed = False
        for grp in groups:
            if jsd(s, sigs[grp[0]]) < threshold:
                grp.append(i)
                placed = True
                break
        if not placed:
            groups.append([i])
    return len(groups), groups


def ablate_one(genome, skip_i):
    return [op for j, op in enumerate(genome) if j != skip_i]


def ablation_scan(genome):
    base = evaluate(genome)
    if base is None: return None
    _, _, va, _ = base
    drops = []
    for i in range(len(genome)):
        r2 = evaluate(ablate_one(genome, i))
        if r2 is None:
            drops.append(None)
        else:
            _, _, va2, _ = r2
            drops.append(va2 - va)
    return va, drops


def gates(archive):
    cells = list(archive.values())
    print(f"\n{'='*60}")
    print(f"GATE CHECKS (archive size: {len(cells)})")
    print(f"{'='*60}")
    if not cells:
        print("ARCHIVE EMPTY - cannot run gates")
        return {k: False for k in ("g1","g2","g3","g4")}

    top5 = sorted(cells, key=lambda v: v["val_err"])[:5]

    print("\n--- Gate 1: strategy diversity (top-5 by val_err) ---")
    for i, t in enumerate(top5):
        ops = [op[0] for op in t["genome"]]
        print(f"  #{i+1} val={t['val_err']:.2e} tr={t['train_err']:.2e} "
              f"r={t['rank']} n={t['n_max']} len={len(ops)} ops={ops}")
    n_distinct, grps = distinct_clusters([t["genome"] for t in top5])
    print(f"  -> distinct clusters (JSD<0.15): {n_distinct} / {len(top5)} "
          f"(gate: >=3)")
    g1 = n_distinct >= 3

    print("\n--- Gate 2: generalization (val / train) ---")
    ratios = [c["val_err"] / max(c["train_err"], 1e-15) for c in cells
              if c["train_err"] > 0 and np.isfinite(c["val_err"])]
    if ratios:
        med = float(np.median(ratios))
        q90 = float(np.percentile(ratios, 90))
        print(f"  val/train ratio: median={med:.2f} q90={q90:.2f} (gate: median<2)")
        top_ratios = [t["val_err"]/max(t["train_err"],1e-15) for t in top5]
        print(f"  top-5 ratios: {[f'{r:.2f}' for r in top_ratios]}")
        g2 = med < 2.0
    else:
        g2 = False

    print("\n--- Gate 3: operator contribution (ablation on top-3) ---")
    all_rel = []
    for idx, t in enumerate(top5[:3]):
        if not t["genome"]: continue
        res = ablation_scan(t["genome"])
        if res is None: continue
        va, drops = res
        ops = [op[0] for op in t["genome"]]
        print(f"  elite #{idx+1}: val={va:.2e} len={len(ops)}")
        for i, (op, d) in enumerate(zip(ops, drops)):
            ds = f"{d:+.2e}" if d is not None else "err"
            rel = (d / max(va, 1e-15)) if (d is not None) else None
            rel_s = f"{rel:+.2f}x" if rel is not None else "n/a"
            print(f"    drop#{i:2d} {op:12s}: dval={ds}  ({rel_s})")
            if rel is not None and np.isfinite(rel):
                all_rel.append(abs(rel))
    if all_rel:
        sig = sum(1 for x in all_rel if x > 0.1)
        frac = sig / len(all_rel)
        print(f"  -> {sig}/{len(all_rel)} drops have |dval|/val > 0.1 "
              f"(frac {frac:.2f}; gate: >0.3)")
        g3 = frac > 0.3
    else:
        g3 = False

    print("\n--- Gate 4: archive orthogonality ---")
    lens = [len(c["genome"]) for c in cells]
    verrs = [-np.log10(c["val_err"] + 1e-15) for c in cells]
    if len(lens) > 3:
        rho, pv = spearmanr(lens, verrs)
        print(f"  Spearman(length, -log10 val_err): rho={rho:.2f} p={pv:.3f}")
        print(f"  (gate: |rho|<0.5; strong rho = axes redundant)")
        g4 = abs(rho) < 0.5
    else:
        g4 = True

    print("\n--- SUMMARY ---")
    print(f"  Gate 1 (diversity):        {'PASS' if g1 else 'FAIL'}")
    print(f"  Gate 2 (generalization):   {'PASS' if g2 else 'FAIL'}")
    print(f"  Gate 3 (op contribution):  {'PASS' if g3 else 'FAIL'}")
    print(f"  Gate 4 (axis orthogonal):  {'PASS' if g4 else 'FAIL'}")
    return {"g1": g1, "g2": g2, "g3": g3, "g4": g4}


def summarize(archive):
    print(f"\nArchive: {len(archive)} cells populated")
    proj = {}
    for key, rec in archive.items():
        r, eb, _ = key
        pkey = (r, eb)
        if pkey not in proj or rec["val_err"] < proj[pkey]["val_err"]:
            proj[pkey] = rec
    ranks = sorted(set(k[0] for k in proj))
    errs = sorted(set(k[1] for k in proj))
    print("\n(projection over samples-bin; showing val_err)")
    print("Rank\\ErrBin", " ".join(f"{e:>7}" for e in errs))
    for r in ranks:
        row = [f"{r:>9}"]
        for e in errs:
            v = proj.get((r, e))
            row.append(f"{v['val_err']:>7.0e}" if v else "    .    ")
        print(" ".join(row))


def save(archive, history, gate_status, path):
    out = {
        "meta": {"D": D, "N": N, "true_rank": 3, "seed": SEED,
                 "n_train": N_TRAIN, "n_val": N_VAL,
                 "rank_cap": RANK_CAP, "sample_choices": SAMPLE_CHOICES},
        "history": history,
        "gates": gate_status,
        "cells": {f"r{k[0]}_e{k[1]}_s{k[2]}": v for k, v in archive.items()},
    }
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)


if __name__ == "__main__":
    pop = int(os.environ.get("POP", 30))
    gens = int(os.environ.get("GENS", 40))
    print(f"Config: POP={pop} GENS={gens} N_TRAIN={N_TRAIN} N_VAL={N_VAL}")
    arc, hist = run(pop_size=pop, gens=gens)
    summarize(arc)
    gs = gates(arc)
    save(arc, hist, gs, HERE / "archive_v2.json")
    print(f"\nSaved: {HERE / 'archive_v2.json'}")
