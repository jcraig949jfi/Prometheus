"""Archive-arm ladder on the FABLE-5.1 p1_slice reach world (C-013-T010, Argus).

DERIVATIVE WORK. The ladder is Nyx's design, nyx/atlas/experiments/reach_archive/DESIGN_G1_ARCHIVE_ARMS.md and the
reference implementation archive_arms.py, both at commit 3318a2098 (Nyx[gandalf-d1f90ae1], 2026-10-03), read only.
run_ladder() below restates archive_arms.run_lineage / run_chain line for line (archive_arms.py:36-102) and is
differential-tested against that file on Nyx's toy landscapes (tests/test_arms.py). The reach world (genome,
mutation operator, fitness, knock-out) is the FABLE-5.1 prototype's (docs/phase3/design/FABLE-5.1/prototype/p1_slice/
reach.py:73-136, wm_mini.py:246-252), imported read only through _proto.py; the chain arms are differential-tested
against reach.search_lineage on its own hash stream.

What each arm is (one factor between neighbours; the contrast it isolates is in PREREGISTRATION.md s3):

    chain_strict    no archive; accept child iff f(child) >  f(parent)        (reach.py regime 'strict')
    chain_neutral   no archive; accept child iff f(child) >= f(parent)        (reach.py regime 'neutral', Nyx 'chain')
    X1              archive of behaviour cells; parent = elite of a best-scoring cell; admit iff f(child) >= f(parent)
    X2              as X1, parent drawn with weight 1/sqrt(1 + times chosen)
    X3              as X2, and a child landing in an EMPTY cell is admitted whatever its score
    X3G             X3 with the behaviour cells replaced by a genotype hash with B buckets (structure-free control)

In every archive arm an admitted child replaces its cell's elite iff f(child) >= f(elite) or the cell is empty.

NOT Go-Explore. The state of this world IS the program; returning to an archived program is copying a genome. No
arm here restores an environment state or re-traverses a trajectory (Nyx's attack B2). The archive arms measure
retention, rarely-visited selection and new-cell admission of genomes -- population-genetic effects.
"""
from __future__ import annotations

import math
import pathlib

import numpy as np
from numba import njit

from rso.reach._proto import org, ru, wm

ROOT = pathlib.Path(__file__).resolve().parents[2]

# -------------------------------------------------------------------------------------------------- frozen constants
ARMS = ("chain_strict", "chain_neutral", "X1", "X2", "X3", "X3G")
ARM_ID = {a: i for i, a in enumerate(ARMS)}
SEED = 20261011           # fresh search seed (reach.py used 777; 20261010 burned in development, PREREGISTRATION s0)
LINEAGE0 = 5000           # frozen knock-out patterns: lineage j uses reach.knock_out(..., LINEAGE0 + j); TOY lineages are < 0
P_MUT = 7_000_003         # same purpose constant as reach.py, so the 'reach' stream reproduces it exactly
P_SEL = 11_000_003        # parent-selection uniforms
P_GENO = 13_000_003       # genotype hash
REACH_SEARCH_SEED = 777   # reach.py SEARCH_SEED, used only by the differential test
N_TRAIN = 16              # training lives 0..15, as reach.py
TRAIN0 = 0
NPROG = 8
P = ru.Params()
TARGET = org.builder_min()
STORE0 = org.empty_store(P.S)


# -------------------------------------------------------------------------------------------------- numba kernels
@njit(cache=True)
def _mutate_into(parent, child, h, n):
    pos = np.int64((h >> np.uint64(0)) % np.uint64(n))
    for a in range(n):
        for q in range(4):
            child[a, q] = parent[a, q]
    child[pos, 0] = np.int64((h >> np.uint64(8)) % np.uint64(wm.NOPS))
    child[pos, 1] = np.int64((h >> np.uint64(16)) % np.uint64(8))
    child[pos, 2] = np.int64((h >> np.uint64(24)) % np.uint64(64))
    child[pos, 3] = np.int64((h >> np.uint64(32)) % np.uint64(16))


@njit(cache=True)
def _mutate(parent, seed, stream, d, i):
    child = np.empty_like(parent)
    _mutate_into(parent, child, wm.khash(seed, stream, P_MUT + d, i), parent.shape[0])
    return child


@njit(cache=True)
def _uniform(seed, stream, d, i):
    h = wm.khash(seed, stream, P_SEL + d, i)
    return np.float64(h >> np.uint64(11)) / 9007199254740992.0


@njit(cache=True)
def _train_counts(prog, n, store0, seed, life0, nlives, K, R, E, T, F, cap):
    counts = np.zeros((wm.NTYPES, 2), dtype=np.int64)
    for j in range(nlives):
        wm.eval_life(prog, n, store0, seed, life0 + j, K, R, E, T, F, cap, True, True, False, counts)
    return counts


@njit(cache=True)
def _pack(counts):
    """C-BEH: per-type (novel, repeat, probe, other) correct counts, 11 bits each (each <= 16 lives * 48 trials)."""
    return (counts[0, 1] | (counts[1, 1] << 11) | (counts[2, 1] << 22) | (counts[3, 1] << 33))


@njit(cache=True)
def _genome_hash(prog):
    h = np.uint64(P_GENO)
    n = prog.shape[0]
    for a in range(n):
        for q in range(4):
            h = wm.khash(P_GENO, a * 4 + q, prog[a, q], h)
    return h


@njit(cache=True)
def _path_restored(g, start, target):
    """-1 if g is NOT on a shortest edit path from start to target under the row-replacement operator; else the
    number of knocked rows already restored. On a path: every row the start shares with the target is unchanged,
    every knocked row is still the start row (NOP) or already the target row. Exact row equality, so a synonym of
    a path genome (unused fields differ) is not counted: the stepping-stone counts are LOWER bounds."""
    r = 0
    for i in range(g.shape[0]):
        same_st = True
        same_tg = True
        knocked = False
        for q in range(4):
            if start[i, q] != target[i, q]:
                knocked = True
            if g[i, q] != start[i, q]:
                same_st = False
            if g[i, q] != target[i, q]:
                same_tg = False
        if not knocked:
            if not same_tg:
                return -1
        elif same_tg:
            r += 1
        elif not same_st:
            return -1
    return r


# -------------------------------------------------------------------------------------------------- python wrappers
def mutate(parent, seed, stream, d, i):
    return _mutate(np.ascontiguousarray(parent, dtype=np.int64), seed, stream, d, i)


def train_counts(prog):
    prog = np.ascontiguousarray(prog, dtype=np.int64)
    return _train_counts(prog, prog.shape[0], STORE0, P.seed, TRAIN0, N_TRAIN, P.K, P.R, P.E, P.T, P.F, P.cap)


def train_eval(prog):
    """(probe fitness, probe count, C-BEH key) on the training block -- the ONLY signal search ever sees."""
    c = train_counts(prog)
    return int(c[wm.T_PROBE, 1]), int(c[wm.T_PROBE, 0]), int(_pack(c))


def unpack_beh(key):
    return tuple((key >> (11 * k)) & 0x7FF for k in range(4))


def genome_hash(prog):
    return int(_genome_hash(np.ascontiguousarray(prog, dtype=np.int64)))


def knock_out(d, lineage_index):
    import reach   # prototype module (read only); imported lazily: it pulls the whole reach grid's kernels
    return reach.knock_out(TARGET, NPROG, d, P.seed, lineage_index)


# -------------------------------------------------------------------------------------------------- the ladder
def run_ladder(arm, start, evaluate, propose, budget, target_fit, rng_u, sort_key=repr, ident=None):
    """One lineage of one arm. Restates Nyx's archive_arms.run_lineage (X1-X3) and run_chain (chain_neutral) at
    3318a2098 with the same interfaces, adds chain_strict (reach.py regime 'strict'), and returns diagnostics.

    evaluate(prog) -> (fitness, cell_key); propose(parent, i) -> child; rng_u(i) -> uniform in [0, 1).
    Returns dict: evals (proposals until a child with fitness >= target_fit was EVALUATED, 0 if the start already
    does, -1 if never), cells, accepted, new_cells_admitted, distinct_genomes, final_prog, final_fit, hit_prog,
    seeded_hit (the START met the target: a seeded control, never a discovery).
    """
    ident = ident or (lambda p: p)
    seen = set()
    f0, c0 = evaluate(start)
    seen.add(ident(start))
    out = dict(evals=-1, cells=0, accepted=0, new_cells_admitted=0, final_prog=start, final_fit=f0, hit_prog=None,
               seeded_hit=False)
    if f0 >= target_fit:
        out.update(evals=0, seeded_hit=True, hit_prog=start, cells=0 if arm.startswith("chain") else 1,
                   distinct_genomes=1, archive=[start])
        return out
    if arm.startswith("chain"):
        strict = arm == "chain_strict"
        parent, fp = start, f0
        for i in range(budget):
            child = propose(parent, i)
            fc, _ = evaluate(child)
            seen.add(ident(child))
            if fc >= target_fit:
                out.update(evals=i + 1, final_prog=child, final_fit=fc, hit_prog=child, accepted=out["accepted"] + 1,
                           distinct_genomes=len(seen), archive=[parent])
                return out
            if (fc > fp) if strict else (fc >= fp):
                parent, fp = child, fc
                out["accepted"] += 1
        out.update(final_prog=parent, final_fit=fp, distinct_genomes=len(seen), archive=[parent])
        return out

    elite, fit, chosen = {c0: start}, {c0: f0}, {c0: 0}      # dicts keep insertion order (Nyx's Archive)
    for i in range(budget):
        cells = list(elite)
        if arm == "X1":
            best = max(fit[c] for c in cells)
            top = sorted([c for c in cells if fit[c] == best], key=sort_key)
            cell = top[int(rng_u(i) * len(top))]
        else:
            w = [1.0 / math.sqrt(1 + chosen[c]) for c in cells]
            r, acc, cell = rng_u(i) * sum(w), 0.0, cells[-1]
            for c, wc in zip(cells, w):
                acc += wc
                if r < acc:
                    cell = c
                    break
        chosen[cell] += 1
        parent, fp = elite[cell], fit[cell]
        child = propose(parent, i)
        fc, cc = evaluate(child)
        seen.add(ident(child))
        if fc >= target_fit:
            out.update(evals=i + 1, cells=len(elite), hit_prog=child, final_prog=child, final_fit=fc,
                       distinct_genomes=len(seen), archive=list(elite.values()))
            return out
        admit = fc >= fp or (arm in ("X3", "X3G") and cc not in elite)
        if admit:
            out["accepted"] += 1
            new = cc not in elite
            out["new_cells_admitted"] += int(new)
            if new or fc >= fit[cc]:
                elite[cc], fit[cc] = child, fc
                if new:
                    chosen[cc] = 0
    best = None
    for c in elite:                                         # first cell, in insertion order, of the highest score
        if best is None or fit[c] > fit[best]:
            best = c
    out.update(cells=len(elite), final_prog=elite[best], final_fit=fit[best], distinct_genomes=len(seen),
               archive=list(elite.values()))
    return out


# -------------------------------------------------------------------------------------------------- reach adapters
def _reach_streams(arm, d, lineage, stream):
    if stream == "reach":      # reach.py's own stream (differential test only)
        reg = {"chain_neutral": 1, "chain_strict": 2}[arm]
        return REACH_SEARCH_SEED, lineage * 4 + reg, lineage
    return SEED, (LINEAGE0 + lineage) * 16 + ARM_ID[arm], LINEAGE0 + lineage


def run_reach_lineage(arm, d, lineage, budget, impl="py", stream="fresh", geno_buckets=None, confirmatory=False,
                      blind=False):
    """One lineage of `arm` at knock-out distance d on the reach world. impl 'py' = run_ladder (the reference);
    'nb' = the numba port (arms_nb.py), which must agree with 'py' exactly (tests/test_arms.py).
    Lineages >= 0 on the fresh stream are the FROZEN set: only the confirmatory runner (confirmatory=True) may run
    them. Development and tests use lineage < 0.
    blind=True sets the hit threshold one above the maximum score, so the lineage ALWAYS runs its whole budget and no
    hit can be observed (the outcome-blind cell-count calibration, calibrate.py)."""
    assert arm in ARMS
    if stream == "fresh" and lineage >= 0 and not confirmatory:
        raise ValueError("lineage %d is in the frozen set; development uses lineage < 0" % lineage)
    if arm == "X3G":
        assert geno_buckets and geno_buckets >= 1
    seed, s, kidx = _reach_streams(arm, d, lineage, stream)
    start = knock_out(d, kidx)
    if impl == "nb":
        from rso.reach import arms_nb
        return arms_nb.run_reach_lineage_nb(arm, d, start, seed, s, budget, geno_buckets or 0, int(blind))
    nfix = train_eval(TARGET)[1] + int(blind)
    stones = dict(evaluated=0, max_restored=0)

    def count_stone(p):
        r = int(_path_restored(np.asarray(p), start, TARGET))
        if 1 <= r <= d - 1:
            stones["evaluated"] += 1
            stones["max_restored"] = max(stones["max_restored"], r)

    if arm == "X3G":
        def evaluate(p):
            count_stone(p)
            f, _, _ = train_eval(p)
            return f, genome_hash(p) % geno_buckets
    else:
        def evaluate(p):
            count_stone(p)
            f, _, k = train_eval(p)
            return f, k

    def propose(p, i):
        return mutate(p, seed, s, d, i)

    def rng_u(i):
        return float(_uniform(seed, s, d, i))

    r = run_ladder("X3" if arm == "X3G" else arm, start, evaluate, propose, budget, nfix, rng_u,
                   sort_key=lambda c: c, ident=genome_hash)
    r["start"] = start
    r["stones_evaluated"] = stones["evaluated"]
    r["max_stone_restored"] = stones["max_restored"]
    r["stones_retained_end"] = sum(1 for g in r.pop("archive")
                                   if 1 <= int(_path_restored(np.asarray(g), start, TARGET)) <= d - 1)
    r["final_prog"] = np.asarray(r["final_prog"])
    r["hit_prog"] = None if r["hit_prog"] is None else np.asarray(r["hit_prog"])
    return r


HAVE_NB_PORT = (pathlib.Path(__file__).parent / "arms_nb.py").exists()
