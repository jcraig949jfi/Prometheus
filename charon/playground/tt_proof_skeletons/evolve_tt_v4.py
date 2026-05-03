"""Phase 3(A/B): deterministic eval + parsimony pressure + length-invariant
MAP axis + optional TT-Cross third family.

Env vars:
  ENABLE_CROSS=1    enables the cross operator (phase 3B)
  PARSIMONY=0.002   per-op length penalty on archive-admission fitness
  POP, GENS         search budget

Changes from v3:
1. evaluate() is DETERMINISTIC: seeds both module RNGs from a stable
   genome hash. Ablation and minimal-skeleton become reproducible.
2. Archive admission uses adjusted fitness (tr + alpha * length), which
   penalises bloat directly. Raw val_err and train_err are kept for reporting.
3. 3rd MAP axis: fit_grad_ratio (length-invariant), replaces entropy.
4. New operator: op_cross - samples n_pivots points from S_train and solves
   LS on only those pivots with row-norm adaptive selection. Represents a
   sample-based third family distinct from full-batch ALS and SGD.
"""

import json
import os
import random
import time
from hashlib import sha256
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).parent
SEED = 45
rng = np.random.default_rng(SEED)
random.seed(SEED)

D = 6
N = 8
RANK_CAP = 10
N_TRAIN = 8192
N_VAL = 4096
SAMPLE_CHOICES = [128, 512, 2048, 8192]
PARSIMONY = float(os.environ.get("PARSIMONY", 0.002))
ENABLE_CROSS = bool(int(os.environ.get("ENABLE_CROSS", "0")))


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


def compute_envs(cores, X, k):
    n = X.shape[0]
    d = len(cores)
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
    return L, R


def als_sweep_samples(cores, X, f):
    cores = [G.copy() for G in cores]
    d = len(cores)
    n = X.shape[0]
    for k in range(d):
        L, R = compute_envs(cores, X, k)
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


def sample_gradient(cores, X, f):
    d = len(cores)
    preds = tt_eval(cores, X)
    residuals = preds - f
    grads = []
    for k in range(d):
        L, R = compute_envs(cores, X, k)
        r_p = L.shape[1]
        r_n = R.shape[1]
        outer_res = (L[:, :, None] * R[:, None, :] *
                     residuals[:, None, None])
        xk = X[:, k]
        grad = np.zeros((r_p, N, r_n))
        for xi in range(N):
            mask = (xk == xi)
            if mask.any():
                grad[:, xi, :] = outer_res[mask].sum(axis=0)
        grads.append(grad)
    return grads


# --------------------------------------------------------------------------
# Operators
# --------------------------------------------------------------------------

def op_fit(state, p):
    n = min(p["n"], N_TRAIN)
    iters = p["iters"]
    if n < N_TRAIN:
        idx = rng.choice(N_TRAIN, size=n, replace=False)
        X_s = X_TRAIN[idx]; F_s = F_TRAIN[idx]
    else:
        X_s, F_s = X_TRAIN, F_TRAIN
    cores = state
    for _ in range(iters):
        cores = als_sweep_samples(cores, X_s, F_s)
    return cores


def op_grad(state, p):
    n = min(p["n"], N_TRAIN)
    steps = p["steps"]
    lr = p["lr"]
    if n < N_TRAIN:
        idx = rng.choice(N_TRAIN, size=n, replace=False)
        X_s = X_TRAIN[idx]; F_s = F_TRAIN[idx]
    else:
        X_s, F_s = X_TRAIN, F_TRAIN
    cores = [G.copy() for G in state]
    for _ in range(steps):
        grads = sample_gradient(cores, X_s, F_s)
        gnorm = np.sqrt(sum(float(np.sum(g ** 2)) for g in grads)) + 1e-12
        eff_lr = lr / max(gnorm, 1.0)
        for k in range(len(cores)):
            cores[k] = cores[k] - eff_lr * grads[k]
    return cores


def op_cross(state, p):
    """Sample-based LS with adaptive pivot selection. Distinct from fit:
    instead of using all n samples, select the n_pivots with highest row
    norm in the design matrix (leverage-score proxy). Closer in spirit to
    classical TT-Cross than uniform subsample ALS."""
    n_pivots = min(p["n_pivots"], N_TRAIN)
    iters = p["iters"]
    d = len(state)
    cores = [G.copy() for G in state]
    # fixed outer sample pool per cross call
    outer_idx = rng.choice(N_TRAIN, size=n_pivots, replace=False)
    X_s = X_TRAIN[outer_idx]; F_s = F_TRAIN[outer_idx]
    for _ in range(iters):
        for k in range(d):
            L, R = compute_envs(cores, X_s, k)
            r_p = L.shape[1]; r_n = R.shape[1]
            outer = np.einsum("ia,ib->iab", L, R)
            xk = X_s[:, k]
            J = np.zeros((n_pivots, r_p, N, r_n))
            J[np.arange(n_pivots), :, xk, :] = outer
            J = J.reshape(n_pivots, r_p * N * r_n)
            row_norms = np.linalg.norm(J, axis=1)
            n_keep = min(n_pivots, r_p * N * r_n + 8)
            top_idx = np.argsort(-row_norms)[:n_keep]
            try:
                g_vec, *_ = np.linalg.lstsq(J[top_idx], F_s[top_idx], rcond=None)
                cores[k] = g_vec.reshape(r_p, N, r_n)
            except np.linalg.LinAlgError:
                pass
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
    k = p["bond"]; amount = p["amount"]
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
    return random_tt([1] + [p["rank"]] * (D - 1) + [1], scale=0.1)


APPLY = {
    "fit": op_fit,
    "grad": op_grad,
    "rerank": op_rerank,
    "perturb": op_perturb,
    "expand": op_expand,
    "compress": op_compress,
    "refine": op_refine,
    "symmetrize": op_symmetrize,
    "reseed": op_reseed,
}
if ENABLE_CROSS:
    APPLY["cross"] = op_cross

OP_NAMES = list(APPLY.keys())


def sample_op():
    name = random.choice(OP_NAMES)
    if name == "fit":
        return (name, {"n": random.choice(SAMPLE_CHOICES),
                       "iters": random.randint(1, 3)})
    if name == "grad":
        return (name, {"n": random.choice(SAMPLE_CHOICES),
                       "steps": random.randint(3, 15),
                       "lr": 10 ** random.uniform(-2.5, -0.5)})
    if name == "cross":
        return (name, {"n_pivots": random.choice([64, 256, 1024]),
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


# --------------------------------------------------------------------------
# Deterministic evaluation
# --------------------------------------------------------------------------

def genome_hash(genome):
    s = repr(tuple((name, tuple(sorted(params.items())))
                    for name, params in genome))
    return int(sha256(s.encode()).hexdigest()[:8], 16)


def apply_sequence(genome):
    state = random_tt([1] * (D + 1), scale=0.1)
    for name, params in genome:
        try:
            state = APPLY[name](state, params)
        except Exception:
            pass
    return state


def evaluate(genome):
    """Deterministic evaluation: seed both module RNGs from genome hash,
    then restore prior state. Same genome -> same fitness, always."""
    global rng
    h = genome_hash(genome)
    saved_rng = rng
    saved_py = random.getstate()
    rng = np.random.default_rng(SEED ^ h)
    random.seed(SEED + h)
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
    finally:
        rng = saved_rng
        random.setstate(saved_py)


def fit_grad_ratio(genome):
    n_fit = sum(1 for op in genome if op[0] == "fit")
    n_grad = sum(1 for op in genome if op[0] == "grad")
    n_cross = sum(1 for op in genome if op[0] == "cross")
    total = n_fit + n_grad + n_cross
    if total == 0:
        return 0.5
    return n_fit / total


def fgr_bin(r):
    # 4 bins: all non-fit, mostly non-fit, mostly fit, all fit
    for i, t in enumerate([0.25, 0.5, 0.75]):
        if r < t: return i
    return 3


def err_bin(e):
    if e <= 1e-12: return 12
    return int(np.clip(np.floor(-np.log10(e + 1e-15)), 0, 12))


def bin_key(r, err, fgr):
    return (min(r, RANK_CAP), err_bin(err), fgr_bin(fgr))


def consider(archive, genome, r, tr, va):
    L = len(genome)
    adj = tr + PARSIMONY * L
    fgr = fit_grad_ratio(genome)
    key = bin_key(r, tr, fgr)
    if key not in archive or adj < archive[key]["adj"]:
        archive[key] = {
            "genome": list(genome), "rank": r,
            "train_err": tr, "val_err": va,
            "adj": adj, "length": L, "fit_grad_ratio": fgr,
        }


def mutate(genome):
    g = list(genome)
    roll = random.random()
    if roll < 0.35:
        if g: g[random.randrange(len(g))] = sample_op()
        else: g.append(sample_op())
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


def run(pop_size=30, gens=35, log_every=5):
    t0 = time.time()
    archive = {}
    pop = [random_genome() for _ in range(pop_size)]
    history = []
    for gen in range(gens):
        for g in pop:
            result = evaluate(g)
            if result is None: continue
            rank, tr, va, _ = result
            consider(archive, g, rank, tr, va)
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
                  f"r={best['rank']} fgr={best['fit_grad_ratio']:.2f} "
                  f"len={best['length']} | t={time.time()-t0:.1f}s", flush=True)
            history.append({
                "gen": gen, "archive_size": len(archive),
                "best_val": best["val_err"], "best_train": best["train_err"],
                "best_rank": best["rank"], "best_fgr": best["fit_grad_ratio"],
                "best_len": best["length"],
            })
    return archive, history


# --------------------------------------------------------------------------
# Gates (deterministic eval, sign-aware g3, trajectory diversity)
# --------------------------------------------------------------------------

def op_histogram(genome):
    ops = [op[0] for op in genome]
    if not ops: return {}
    h = {}
    for o in ops:
        h[o] = h.get(o, 0) + 1.0 / len(ops)
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


def edit_distance(a, b):
    sa = [op[0] for op in a]; sb = [op[0] for op in b]
    m, n = len(sa), len(sb)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if sa[i - 1] == sb[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


def cluster_by_dist(genomes, metric, threshold):
    groups = []
    for i, g in enumerate(genomes):
        placed = False
        for grp in groups:
            if metric(g, genomes[grp[0]]) <= threshold:
                grp.append(i); placed = True; break
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
        drops.append(None if r2 is None else r2[2] - va)
    return va, drops


def minimal_skeleton(genome, tol=1.10, max_iters=20):
    current = list(genome)
    base = evaluate(current)
    if base is None: return current, float("inf")
    _, _, orig_va, _ = base
    best_va = orig_va
    for _ in range(max_iters):
        if len(current) <= 1: break
        best_i = -1
        best_new = best_va
        for i in range(len(current)):
            trial = ablate_one(current, i)
            r = evaluate(trial)
            if r is None: continue
            va_new = r[2]
            if va_new <= orig_va * tol and va_new < best_new:
                best_new = va_new; best_i = i
        if best_i < 0: break
        current = ablate_one(current, best_i)
        best_va = best_new
    return current, best_va


def gates(archive):
    cells = list(archive.values())
    print(f"\n{'='*60}")
    print(f"GATE CHECKS (archive={len(cells)})")
    print(f"{'='*60}")
    if not cells:
        return {}

    top5 = sorted(cells, key=lambda v: v["val_err"])[:5]

    print("\n--- Gate 1: diversity (JSD + edit-distance) ---")
    for i, t in enumerate(top5):
        ops = [op[0] for op in t["genome"]]
        print(f"  #{i+1} val={t['val_err']:.2e} tr={t['train_err']:.2e} "
              f"r={t['rank']} fgr={t['fit_grad_ratio']:.2f} "
              f"len={len(ops)} ops={ops}")
    n_jsd, _ = cluster_by_dist([t["genome"] for t in top5],
                                lambda a, b: jsd(op_histogram(a), op_histogram(b)),
                                threshold=0.15)
    n_edit, _ = cluster_by_dist([t["genome"] for t in top5],
                                 edit_distance, threshold=3)
    print(f"  -> op-histogram clusters: {n_jsd} / 5")
    print(f"  -> trajectory clusters:   {n_edit} / 5")
    g1 = n_jsd >= 3 or n_edit >= 3

    print("\n--- Gate 2: generalization ---")
    ratios = [c["val_err"] / max(c["train_err"], 1e-15) for c in cells
              if c["train_err"] > 0 and np.isfinite(c["val_err"])]
    if ratios:
        med = float(np.median(ratios))
        q90 = float(np.percentile(ratios, 90))
        print(f"  val/train ratio: median={med:.2f} q90={q90:.2f}")
        g2 = med < 2.0
    else:
        g2 = False

    print("\n--- Gate 3' (sign-aware, deterministic) ---")
    load_fracs = []
    ablation_records = []
    for idx, t in enumerate(top5[:3]):
        if not t["genome"]: continue
        res = ablation_scan(t["genome"])
        if res is None: continue
        va, drops = res
        ops = [op[0] for op in t["genome"]]
        n_load = n_harm = n_neutral = 0
        rows = []
        print(f"  elite #{idx+1}: val={va:.2e} (archive {t['val_err']:.2e}) "
              f"len={len(ops)}")
        for i, (op, d) in enumerate(zip(ops, drops)):
            if d is None: continue
            rel = d / max(va, 1e-15)
            if rel > 0.1: n_load += 1; tag = "LOAD"
            elif rel < -0.1: n_harm += 1; tag = "HARM"
            else: n_neutral += 1; tag = "---"
            print(f"    {i:2d} {op:12s}: dval={d:+.2e} ({rel:+.2f}x) {tag}")
            rows.append({"op": op, "dval": d, "rel": rel, "label": tag})
        total = len(ops)
        print(f"    summary: load={n_load}/{total} harm={n_harm} neutral={n_neutral}")
        if total > 0:
            load_fracs.append(n_load / total)
        ablation_records.append({"idx": idx, "val": va, "rows": rows})
    if load_fracs:
        avg = float(np.mean(load_fracs))
        print(f"  avg load-bearing fraction: {avg:.2f}")
        g3 = avg >= 0.5
    else:
        g3 = False

    print("\n--- Gate 4: axis orthogonality (length vs val_err) ---")
    lens = [len(c["genome"]) for c in cells]
    verrs = [-np.log10(c["val_err"] + 1e-15) for c in cells]
    if len(lens) > 3:
        rho, pv = spearmanr(lens, verrs)
        print(f"  Spearman(length, -log10 val_err): rho={rho:.2f} p={pv:.3f}")
        g4 = abs(rho) < 0.5
    else:
        g4 = True

    print("\n--- Gate 5: family composition (top-5) ---")
    families = {"fit_only": 0, "grad_only": 0, "cross_only": 0,
                "mixed_2": 0, "mixed_3": 0, "none": 0}
    for t in top5:
        ops = [op[0] for op in t["genome"]]
        has = {"fit": "fit" in ops, "grad": "grad" in ops, "cross": "cross" in ops}
        n_fam = sum(has.values())
        if n_fam == 0: families["none"] += 1
        elif n_fam == 3: families["mixed_3"] += 1
        elif n_fam == 2: families["mixed_2"] += 1
        elif has["fit"]: families["fit_only"] += 1
        elif has["grad"]: families["grad_only"] += 1
        elif has["cross"]: families["cross_only"] += 1
    print(f"  top-5 family mix: {families}")
    g5 = (families["mixed_2"] + families["mixed_3"]) >= 2

    print("\n--- SUMMARY ---")
    print(f"  Gate 1 (diversity):        {'PASS' if g1 else 'FAIL'}")
    print(f"  Gate 2 (generalization):   {'PASS' if g2 else 'FAIL'}")
    print(f"  Gate 3' (sign-aware ops):  {'PASS' if g3 else 'FAIL'}")
    print(f"  Gate 4 (axis ortho):       {'PASS' if g4 else 'FAIL'}")
    print(f"  Gate 5 (family diversity): {'PASS' if g5 else 'FAIL'}")
    return {"g1": g1, "g2": g2, "g3": g3, "g4": g4, "g5": g5,
            "ablations": ablation_records}


def minimal_probe(archive):
    print(f"\n{'='*60}")
    print("MINIMAL-SKELETON PROBE (top-3 elites, deterministic)")
    print(f"{'='*60}")
    top3 = sorted(archive.values(), key=lambda v: v["val_err"])[:3]
    results = []
    for idx, t in enumerate(top3):
        orig = t["genome"]
        orig_ops = [op[0] for op in orig]
        base = evaluate(orig)
        orig_va = base[2] if base else float("nan")
        minimal, va_min = minimal_skeleton(orig, tol=1.10, max_iters=len(orig))
        min_ops = [op[0] for op in minimal]
        print(f"\nelite #{idx+1}: {len(orig)} -> {len(minimal)} ops "
              f"(val {orig_va:.2e} -> {va_min:.2e})")
        print(f"  original: {orig_ops}")
        print(f"  minimal:  {min_ops}")
        results.append({
            "orig_len": len(orig), "min_len": len(minimal),
            "orig_val": orig_va, "min_val": va_min,
            "orig_ops": orig_ops, "min_ops": min_ops,
        })
    return results


def summarize(archive):
    print(f"\nArchive: {len(archive)} cells populated (PARSIMONY={PARSIMONY})")
    proj = {}
    for key, rec in archive.items():
        r, eb, _ = key
        pkey = (r, eb)
        if pkey not in proj or rec["val_err"] < proj[pkey]["val_err"]:
            proj[pkey] = rec
    ranks = sorted(set(k[0] for k in proj))
    errs = sorted(set(k[1] for k in proj))
    print("\n(projection over fgr-bin; showing val_err)")
    print("Rank\\ErrBin", " ".join(f"{e:>7}" for e in errs))
    for r in ranks:
        row = [f"{r:>9}"]
        for e in errs:
            v = proj.get((r, e))
            row.append(f"{v['val_err']:>7.0e}" if v else "    .    ")
        print(" ".join(row))


def save(archive, history, gate_status, minimal_results, path):
    out = {
        "meta": {"D": D, "N": N, "true_rank": 3, "seed": SEED,
                 "n_train": N_TRAIN, "n_val": N_VAL,
                 "rank_cap": RANK_CAP, "sample_choices": SAMPLE_CHOICES,
                 "parsimony": PARSIMONY, "enable_cross": ENABLE_CROSS,
                 "operators": OP_NAMES},
        "history": history,
        "gates": {k: v for k, v in gate_status.items() if k != "ablations"},
        "ablations": gate_status.get("ablations", []),
        "minimal_probe": minimal_results,
        "cells": {f"r{k[0]}_e{k[1]}_fgr{k[2]}": v for k, v in archive.items()},
    }
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)


if __name__ == "__main__":
    pop = int(os.environ.get("POP", 30))
    gens = int(os.environ.get("GENS", 35))
    phase = "3B" if ENABLE_CROSS else "3A"
    print(f"Config: PHASE={phase} POP={pop} GENS={gens} "
          f"PARSIMONY={PARSIMONY} N_TRAIN={N_TRAIN}")
    print(f"Operators: {OP_NAMES}")
    arc, hist = run(pop_size=pop, gens=gens)
    summarize(arc)
    gs = gates(arc)
    mp = minimal_probe(arc)
    outfile = HERE / ("archive_v5.json" if ENABLE_CROSS else "archive_v4.json")
    save(arc, hist, gs, mp, outfile)
    print(f"\nSaved: {outfile}")
