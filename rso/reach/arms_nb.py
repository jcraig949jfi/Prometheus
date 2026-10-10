"""Numba port of arms.run_ladder on the reach world (C-013-T010, Argus).

Built because the timed measurement required it (NUMBA_DECISION.md: the pure-Python parent draw is O(cells) per
proposal and the X3 archive grows to ~10^4 cells within the 200,000-proposal budget). It must agree with the
reference arms.run_ladder EXACTLY -- every count, the hit time, the final and hit genomes -- on every arm
(tests/test_arms.py::test_numba_port_matches_reference). To make that possible it keeps the reference's
arithmetic order: the X2/X3 weight total is a left-to-right float64 sum over cells in insertion order, then a
left-to-right cumulative scan, exactly as Python's sum() and the reference loop; X1 breaks ties by ascending cell key.
"""
import math

import numpy as np
from numba import njit, types
from numba.typed import Dict

from rso.reach import arms
from rso.reach.arms import (_genome_hash, _mutate_into, _pack, _path_restored, _train_counts, _uniform)
from rso.reach._proto import wm

A_CHAIN_STRICT, A_CHAIN_NEUTRAL, A_X1, A_X2, A_X3, A_X3G = range(6)


@njit(cache=True)
def _eval(prog, n, store0, seed_w, K, R, E, T, F, cap, ntrain, geno_b):
    c = _train_counts(prog, n, store0, seed_w, 0, ntrain, K, R, E, T, F, cap)
    f = c[wm.T_PROBE, 1]
    if geno_b > 0:
        key = np.int64(_genome_hash(prog) % np.uint64(geno_b))
    else:
        key = _pack(c)
    return f, c[wm.T_PROBE, 0], key


@njit(cache=True)
def _lineage(arm, d, start, seed, stream, budget, geno_b, store0, seed_w, K, R, E, T, F, cap, ntrain, arms_target,
             hit_add):
    n = start.shape[0]
    # stats: evals, cells, accepted, new_cells_admitted, distinct, final_fit, seeded_hit,
    #        stones_evaluated, max_stone_restored, stones_retained_end
    st = np.zeros(10, dtype=np.int64)
    target = arms_target
    st[0] = -1
    final_prog = start.copy()
    hit_prog = np.zeros_like(start)
    seen = Dict.empty(key_type=types.uint64, value_type=types.int64)
    f0, nfix, k0 = _eval(start, n, store0, seed_w, K, R, E, T, F, cap, ntrain, geno_b)
    nfix += hit_add
    seen[_genome_hash(start)] = 1
    _stone(start, start, target, d, st)
    st[5] = f0
    child = np.zeros_like(start)
    if f0 >= nfix:
        st[0] = 0
        st[1] = 0 if arm <= A_CHAIN_NEUTRAL else 1
        st[4] = 1
        st[6] = 1
        hit_prog[:, :] = start
        _retained(start, start, target, d, st)
        return st, final_prog, hit_prog

    if arm <= A_CHAIN_NEUTRAL:
        parent = start.copy()
        fp = f0
        for i in range(budget):
            _mutate_into(parent, child, wm.khash(seed, stream, arms.P_MUT + d, i), n)
            _stone(child, start, target, d, st)
            fc, _, _ = _eval(child, n, store0, seed_w, K, R, E, T, F, cap, ntrain, geno_b)
            seen[_genome_hash(child)] = 1
            if fc >= nfix:
                _retained(parent, start, target, d, st)
                st[0] = i + 1
                st[2] += 1
                st[4] = len(seen)
                st[5] = fc
                final_prog[:, :] = child
                hit_prog[:, :] = child
                return st, final_prog, hit_prog
            if (fc > fp) if arm == A_CHAIN_STRICT else (fc >= fp):
                parent[:, :] = child
                fp = fc
                st[2] += 1
        st[4] = len(seen)
        st[5] = fp
        final_prog[:, :] = parent
        _retained(parent, start, target, d, st)
        return st, final_prog, hit_prog

    capn = 1024
    keys = np.zeros(capn, dtype=np.int64)
    fit = np.zeros(capn, dtype=np.int64)
    chosen = np.zeros(capn, dtype=np.int64)
    w = np.zeros(capn, dtype=np.float64)
    elite = np.zeros((capn, n, 4), dtype=np.int64)
    index = Dict.empty(key_type=types.int64, value_type=types.int64)
    keys[0] = k0
    fit[0] = f0
    w[0] = 1.0
    elite[0] = start
    index[k0] = 0
    m = 1
    newcell = arm >= A_X3
    tops = np.zeros(capn, dtype=np.int64)
    for i in range(budget):
        u = _uniform(seed, stream, d, i)
        if arm == A_X1:
            best = fit[0]
            for j in range(1, m):
                if fit[j] > best:
                    best = fit[j]
            nt = 0
            for j in range(m):
                if fit[j] == best:
                    tops[nt] = j
                    nt += 1
            order = np.argsort(keys[tops[:nt]])
            cell = tops[order[int(u * nt)]]
        else:
            tot = 0.0
            for j in range(m):
                tot += w[j]
            r = u * tot
            acc = 0.0
            cell = m - 1
            for j in range(m):
                acc += w[j]
                if r < acc:
                    cell = j
                    break
        chosen[cell] += 1
        w[cell] = 1.0 / math.sqrt(1 + chosen[cell])
        fp = fit[cell]
        _mutate_into(elite[cell], child, wm.khash(seed, stream, arms.P_MUT + d, i), n)
        _stone(child, start, target, d, st)
        fc, _, cc = _eval(child, n, store0, seed_w, K, R, E, T, F, cap, ntrain, geno_b)
        seen[_genome_hash(child)] = 1
        if fc >= nfix:
            for j in range(m):
                _retained(elite[j], start, target, d, st)
            st[0] = i + 1
            st[1] = m
            st[4] = len(seen)
            st[5] = fc
            final_prog[:, :] = child
            hit_prog[:, :] = child
            return st, final_prog, hit_prog
        isnew = cc not in index
        if fc >= fp or (newcell and isnew):
            st[2] += 1
            if isnew:
                st[3] += 1
                if m == capn:
                    capn *= 2
                    keys = _grow1(keys, capn)
                    fit = _grow1(fit, capn)
                    chosen = _grow1(chosen, capn)
                    w = _growf(w, capn)
                    tops = _grow1(tops, capn)
                    e2 = np.zeros((capn, n, 4), dtype=np.int64)
                    e2[:m] = elite[:m]
                    elite = e2
                index[cc] = m
                keys[m] = cc
                fit[m] = fc
                chosen[m] = 0
                w[m] = 1.0
                elite[m] = child
                m += 1
            else:
                j = index[cc]
                if fc >= fit[j]:
                    fit[j] = fc
                    elite[j] = child
    bi = 0
    for j in range(1, m):
        if fit[j] > fit[bi]:
            bi = j
    st[1] = m
    st[4] = len(seen)
    st[5] = fit[bi]
    final_prog[:, :] = elite[bi]
    for j in range(m):
        _retained(elite[j], start, target, d, st)
    return st, final_prog, hit_prog


@njit(cache=True)
def _stone(g, start, target, d, st):
    r = _path_restored(g, start, target)
    if r >= 1 and r <= d - 1:
        st[7] += 1
        if r > st[8]:
            st[8] = r


@njit(cache=True)
def _retained(g, start, target, d, st):
    r = _path_restored(g, start, target)
    if r >= 1 and r <= d - 1:
        st[9] += 1


@njit(cache=True)
def _grow1(a, capn):
    b = np.zeros(capn, dtype=a.dtype)
    b[:a.shape[0]] = a
    return b


@njit(cache=True)
def _growf(a, capn):
    b = np.zeros(capn, dtype=np.float64)
    b[:a.shape[0]] = a
    return b


def run_reach_lineage_nb(arm, d, start, seed, stream, budget, geno_buckets, hit_add=0):
    P = arms.P
    a = arms.ARM_ID[arm]
    st, final_prog, hit_prog = _lineage(a, d, np.ascontiguousarray(start, dtype=np.int64), seed, stream, budget,
                                        geno_buckets if arm == "X3G" else 0, arms.STORE0, P.seed,
                                        P.K, P.R, P.E, P.T, P.F, P.cap, arms.N_TRAIN, arms.TARGET, hit_add)
    return dict(evals=int(st[0]), cells=int(st[1]), accepted=int(st[2]), new_cells_admitted=int(st[3]),
                distinct_genomes=int(st[4]), final_fit=int(st[5]), seeded_hit=bool(st[6]),
                stones_evaluated=int(st[7]), max_stone_restored=int(st[8]), stones_retained_end=int(st[9]),
                final_prog=final_prog, hit_prog=hit_prog if st[0] >= 0 else None, start=start)
