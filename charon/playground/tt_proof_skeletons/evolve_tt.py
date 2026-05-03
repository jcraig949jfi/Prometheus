"""
TT proof-skeleton evolution.

Phase 1: evolve sequences of TT transformation operators that approximate a
known-rank target tensor. MAP-Elites archive keyed on (achieved max rank,
approximation error). Each cell preserves a distinct "proof strategy" that
reached that tradeoff.

Target: f(x_1,...,x_6) = sum over 3 mode-separable terms (sin, cos, poly).
True TT rank = 3. A working evolutionary search should find rank-3 genomes
that push error to 1e-10+, and populate adjacent cells with diverse strategies.
"""

import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
SEED = 42
rng = np.random.default_rng(SEED)
random.seed(SEED)

D = 6
N = 8


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


T_TRUE = build_target()
T_NORM = float(np.linalg.norm(T_TRUE))


def tt_to_full(cores):
    r = cores[0]
    for G in cores[1:]:
        r = np.tensordot(r, G, axes=[[-1], [0]])
    return r.squeeze()


def tt_error(cores):
    return float(np.linalg.norm(tt_to_full(cores) - T_TRUE) / T_NORM)


def tt_ranks(cores):
    return [cores[0].shape[0]] + [G.shape[-1] for G in cores]


def max_rank(cores):
    rs = tt_ranks(cores)[1:-1]
    return max(rs) if rs else 1


def random_tt(ranks, scale=0.1):
    cores = []
    for k in range(len(ranks) - 1):
        cores.append(rng.standard_normal((ranks[k], N, ranks[k + 1])) * scale)
    return cores


def tt_svd(T, max_rank_cap):
    d = T.ndim
    cores = []
    C = T.copy()
    r_prev = 1
    for k in range(d - 1):
        mat = C.reshape(r_prev * N, -1)
        U, S, Vt = np.linalg.svd(mat, full_matrices=False)
        r_next = min(max_rank_cap, len(S))
        cores.append(U[:, :r_next].reshape(r_prev, N, r_next))
        C = (np.diag(S[:r_next]) @ Vt[:r_next, :]).reshape(r_next, *([N] * (d - k - 1)))
        r_prev = r_next
    cores.append(C.reshape(r_prev, N, 1))
    return cores


def tt_orth_rl(cores):
    cores = [G.copy() for G in cores]
    d = len(cores)
    for k in range(d - 1, 0, -1):
        G = cores[k]
        r_prev, nk, r_next = G.shape
        Q, R = np.linalg.qr(G.reshape(r_prev, nk * r_next).T)
        r_new = Q.shape[1]
        cores[k] = Q.T.reshape(r_new, nk, r_next)
        cores[k - 1] = np.tensordot(cores[k - 1], R.T, axes=[[-1], [0]])
    return cores


def tt_round(cores, eps=1e-12, max_rank_cap=None):
    cores = tt_orth_rl(cores)
    d = len(cores)
    for k in range(d - 1):
        G = cores[k]
        r_prev, nk, r_next = G.shape
        U, S, Vt = np.linalg.svd(G.reshape(r_prev * nk, r_next), full_matrices=False)
        if len(S) == 0:
            r_new = 1
        else:
            cutoff = eps * S[0]
            r_new = max(1, int(np.sum(S > cutoff)))
            if max_rank_cap is not None:
                r_new = min(r_new, max_rank_cap)
        cores[k] = U[:, :r_new].reshape(r_prev, nk, r_new)
        cores[k + 1] = np.tensordot(
            np.diag(S[:r_new]) @ Vt[:r_new, :], cores[k + 1], axes=[[-1], [0]]
        )
    return cores


# --------------------------------------------------------------------------
# Operators. Each maps a TT (list of cores) to a new TT.
# Semantic labels chosen to foreshadow the "proof-step" interpretation.
# --------------------------------------------------------------------------

def op_ansatz(state, p):
    """Posit an approximation of a given rank via TT-SVD of the target."""
    return tt_svd(T_TRUE, p["rank"])


def op_refine(state, p):
    """Tighten representation: SVD-round to precision eps."""
    return tt_round(state, eps=p["eps"])


def op_perturb(state, p):
    s = p["sigma"]
    return [G + rng.standard_normal(G.shape) * s for G in state]


def op_expand(state, p):
    """Introduce a new bond degree of freedom at position `bond`."""
    k = p["bond"]
    amount = p["amount"]
    if k < 1 or k >= len(state):
        return state
    new = [G.copy() for G in state]
    gL, gR = new[k - 1], new[k]
    r_prev_L, nL, rk = gL.shape
    rk2, nR, r_next = gR.shape
    if rk != rk2:
        return state
    padL = rng.standard_normal((r_prev_L, nL, amount)) * 0.01
    padR = rng.standard_normal((amount, nR, r_next)) * 0.01
    new[k - 1] = np.concatenate([gL, padL], axis=-1)
    new[k] = np.concatenate([gR, padR], axis=0)
    return new


def op_compress(state, p):
    """Force truncation to a rank budget."""
    return tt_round(state, eps=1e-15, max_rank_cap=p["target"])


def op_symmetrize(state, p):
    """Invoke mode-reversal symmetry by averaging with mode-reversed copy."""
    rev = [np.transpose(G, (2, 1, 0)) for G in state[::-1]]
    try:
        avg = [0.5 * (a + b) for a, b in zip(state, rev)]
        return avg
    except ValueError:
        return state


def op_reseed(state, p):
    """Replace state with fresh random TT at given rank."""
    rank = p["rank"]
    ranks = [1] + [rank] * (D - 1) + [1]
    return random_tt(ranks, scale=p.get("scale", 0.1))


APPLY = {
    "ansatz": op_ansatz,
    "refine": op_refine,
    "perturb": op_perturb,
    "expand": op_expand,
    "compress": op_compress,
    "symmetrize": op_symmetrize,
    "reseed": op_reseed,
}

OP_NAMES = list(APPLY.keys())


def sample_op():
    name = random.choice(OP_NAMES)
    if name == "ansatz":
        return (name, {"rank": random.randint(1, 8)})
    if name == "refine":
        return (name, {"eps": 10 ** random.uniform(-12, -3)})
    if name == "perturb":
        return (name, {"sigma": 10 ** random.uniform(-5, -1)})
    if name == "expand":
        return (name, {"bond": random.randint(1, D - 1), "amount": random.randint(1, 3)})
    if name == "compress":
        return (name, {"target": random.randint(1, 8)})
    if name == "symmetrize":
        return (name, {})
    if name == "reseed":
        return (name, {"rank": random.randint(1, 6)})
    raise ValueError(name)


def apply_sequence(genome, start_rank=1):
    state = random_tt([1] + [start_rank] * (D - 1) + [1])
    for name, params in genome:
        try:
            state = APPLY[name](state, params)
        except Exception:
            pass
    return state


def evaluate(genome):
    try:
        state = apply_sequence(genome)
        err = tt_error(state)
        r = max_rank(state)
        if not np.isfinite(err):
            return None
        return r, err, state
    except Exception:
        return None


# MAP-Elites grid
def err_bin(err):
    if err <= 1e-14:
        return 14
    return int(np.clip(np.floor(-np.log10(err)), 0, 14))


RANK_CAP = 10


def bin_key(r, err):
    return (min(r, RANK_CAP), err_bin(err))


def consider(archive, genome, r, err):
    key = bin_key(r, err)
    if key not in archive or err < archive[key]["error"]:
        archive[key] = {"genome": list(genome), "error": err, "rank": r}


# GA variation
def mutate(genome):
    g = list(genome)
    roll = random.random()
    if roll < 0.35:
        if g:
            i = random.randrange(len(g))
            g[i] = sample_op()
        else:
            g.append(sample_op())
    elif roll < 0.65:
        i = random.randint(0, len(g))
        g.insert(i, sample_op())
    elif roll < 0.85 and len(g) > 1:
        g.pop(random.randrange(len(g)))
    else:
        # shuffle contiguous block
        if len(g) > 2:
            i, j = sorted(random.sample(range(len(g)), 2))
            block = g[i:j + 1]
            random.shuffle(block)
            g[i:j + 1] = block
    return g


def crossover(a, b):
    if not a:
        return list(b)
    if not b:
        return list(a)
    ia = random.randrange(len(a))
    ib = random.randrange(len(b))
    return a[:ia] + b[ib:]


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
            if result is None:
                continue
            r, err, _ = result
            consider(archive, g, r, err)
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
                k = random.choice(keys)
                new_pop.append(mutate(archive[k]["genome"]))
            else:
                k1, k2 = random.sample(keys, 2)
                new_pop.append(mutate(crossover(archive[k1]["genome"], archive[k2]["genome"])))
        pop = new_pop
        if gen % log_every == 0 or gen == gens - 1:
            best = min(archive.values(), key=lambda v: v["error"])
            print(
                f"gen {gen:3d} | archive={len(archive):3d} cells | "
                f"best_err={best['error']:.3e} @ rank={best['rank']} | "
                f"elapsed={time.time()-t0:.1f}s",
                flush=True,
            )
            history.append({
                "gen": gen,
                "archive_size": len(archive),
                "best_error": best["error"],
                "best_rank": best["rank"],
            })
    return archive, history


def summarize(archive):
    print(f"\nArchive: {len(archive)} cells populated")
    # Print grid (rank × error)
    ranks = sorted(set(k[0] for k in archive))
    errs = sorted(set(k[1] for k in archive))
    print("\nRank\\ErrBin", " ".join(f"{e:>6}" for e in errs))
    for r in ranks:
        row = [f"{r:>9}"]
        for e in errs:
            v = archive.get((r, e))
            row.append(f"{v['error']:>6.0e}" if v else "   .   ")
        print(" ".join(row))
    print()
    # Highlights: best per rank
    print("Frontier (best error per rank):")
    per_rank_best = {}
    for key, rec in archive.items():
        r = key[0]
        if r not in per_rank_best or rec["error"] < per_rank_best[r]["error"]:
            per_rank_best[r] = rec
    for r in sorted(per_rank_best):
        rec = per_rank_best[r]
        ops = [op[0] for op in rec["genome"]]
        print(f"  rank={r}: err={rec['error']:.3e}  len={len(rec['genome'])}  ops={ops}")


def save_archive(archive, history, path):
    out = {
        "meta": {
            "D": D, "N": N, "true_rank": 3, "seed": SEED,
            "target_norm": T_NORM, "rank_cap": RANK_CAP,
        },
        "history": history,
        "cells": {
            f"r{key[0]}_e{key[1]}": {
                "rank": rec["rank"],
                "error": rec["error"],
                "genome": rec["genome"],
            }
            for key, rec in archive.items()
        },
    }
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Saved archive to {path}")


if __name__ == "__main__":
    pop_size = int(os.environ.get("POP", 40))
    gens = int(os.environ.get("GENS", 60))
    archive, history = run(pop_size=pop_size, gens=gens)
    summarize(archive)
    save_archive(archive, history, HERE / "archive.json")
