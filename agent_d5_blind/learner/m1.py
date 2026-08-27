"""M1 — history-conditioned learner. Spec: PREREG-EVIDENCE.md section 2.

Search core = character-identical control flow to the frozen M0c-RX
(navigators/m0.py::_m0_pop, use_crossover=True) with two additions:
  1. extra_pool = the developmental artifact library (the ONE preregistered
     mechanism: 50% of immigrant draws come from the library, mutated);
  2. passive capture of the last scored generation for artifact admission
     (no rng consumption, no meter change, no decision change).
Identity is enforced by the sanity gate: M1 with an empty library must
reproduce M0c-RX rows exactly (same seeds -> same solved/first_solve/evals).

Input boundary: functions here accept ONLY the learner view {'domain',
'table'} plus machine-native genotypes. No oracle-side field is referenced.
Library: genotypes only; cap 64; most-recent-first eviction; genotype-deduped.
Admission after each task: solving genotype (if any) + up to 4
behavior-distinct best-scoring candidates from the last scored generation.
"""
import sys, os, random
HERE = os.path.dirname(__file__)
for d in ('..\\substrate', '..\\mutation', '..\\exact_oracle'):
    sys.path.insert(0, os.path.join(HERE, d))
from physics import mutate, crossover, SEED_REPERTOIRE
from oracle import solves as _authoritative_solves
from rm_fast import FastTask

BIG = 10 ** 9
LIB_CAP = 64
ADMIT_K = 4


class _Ctx:
    def __init__(self, view):
        self.view = view
        self.ft = FastTask(view)

    def d(self, prog):
        v = self.ft.dist(prog)
        if v == 0:
            assert _authoritative_solves(prog, self.view), \
                'fast/reference divergence: freeze-blocker'
        return v


def m1_rx(view, rng, budget, library, psize=32, immigrant=0.10):
    """Identical control flow to frozen _m0_pop(use_crossover=True) with
    extra_pool=library. Returns result + passive admission capture."""
    ctx = _Ctx(view)
    rep = SEED_REPERTOIRE
    extra_pool = library if library else None

    def fresh():
        if extra_pool and rng.random() < 0.5:
            return mutate(extra_pool[rng.randrange(len(extra_pool))], rng)
        return mutate(rep[rng.randrange(len(rep))], rng)

    scored = []                      # passive capture: last scored generation
    pop = [fresh() for _ in range(psize)]
    evals, dists = 0, []
    solver = None
    for g in pop:
        d = ctx.d(g)
        evals += 1
        scored.append((g, d))
        if d == 0:
            return {'solved': True, 'first_solve': evals, 'evals': evals,
                    'solver': g, 'scored': scored}
        dists.append(d)
    while evals < budget:
        children = []
        for _ in range(psize):
            if rng.random() < immigrant:
                children.append(fresh())
                continue
            idxs = [rng.randrange(psize) for _ in range(3)]
            p1 = pop[min(idxs, key=lambda i: dists[i])]
            if rng.random() < 0.5:
                jdxs = [rng.randrange(psize) for _ in range(3)]
                p2 = pop[min(jdxs, key=lambda i: dists[i])]
                children.append(mutate(crossover(p1, p2, rng), rng))
            else:
                children.append(mutate(p1, rng))
        pop, dists = children, []
        scored = []
        for g in pop:
            d = ctx.d(g)
            evals += 1
            scored.append((g, d))
            if d == 0:
                return {'solved': True, 'first_solve': evals, 'evals': evals,
                        'solver': g, 'scored': scored}
            dists.append(d)
            if evals >= budget:
                break
        while len(dists) < len(pop):
            dists.append(BIG)
    return {'solved': False, 'first_solve': None, 'evals': evals,
            'solver': None, 'scored': scored}


def admissions(res, ctx_view):
    """Solver + up to ADMIT_K behavior-distinct best-scoring candidates from
    the last scored generation. Pure bookkeeping (fingerprints allowed)."""
    ft = FastTask(ctx_view)
    out = []
    if res['solver'] is not None:
        out.append(res['solver'])
    seen_behaviors = {tuple(ft.outputs(g)) for g in out}
    ranked = sorted(res['scored'], key=lambda gd: gd[1])
    for g, _d in ranked:
        if len(out) >= (1 if res['solver'] else 0) + ADMIT_K:
            break
        b = tuple(ft.outputs(g))
        if b in seen_behaviors:
            continue
        seen_behaviors.add(b)
        out.append(g)
    return out


def update_library(library, new_genotypes):
    """Most-recent-first, genotype-deduped, cap LIB_CAP."""
    for g in new_genotypes:
        if g in library:
            library.remove(g)
        library.append(g)
    while len(library) > LIB_CAP:
        library.pop(0)
    return library
