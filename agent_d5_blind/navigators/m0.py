"""History-free M0 navigators over TASKS (Phase 2 machinery).

Same search physics as the preflight navigators, but the objective is the
task table and the meter is exact-oracle verifier evaluations (1 evaluation =
one candidate checked against the full task table; capped mismatch counting is
ordering-preserving and used for selection only). Solved == mismatches 0 ==
exact oracle pass, because distance is counted over the ENTIRE task domain.

Every navigator records first-solve evaluation index (acquisition cost) and
per-rung solve flags for the frozen budget ladder.
"""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'substrate'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mutation'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'exact_oracle'))
from physics import mutate, crossover, SEED_REPERTOIRE
from oracle import bit_mismatch_capped as nav_dist

BIG = 10 ** 9


def _full_d(prog, task):
    return nav_dist(prog, task, 16 * len(task['table']))


def m0_hc(task, rng, budget, repertoire=None, lam=8, stall=50, extra_pool=None):
    rep = repertoire or SEED_REPERTOIRE
    cur = rep[rng.randrange(len(rep))]
    bd = _full_d(cur, task)
    evals = 1
    if bd == 0:
        return {'solved': True, 'first_solve': 1, 'evals': 1}
    no_imp = 0
    while evals < budget:
        best_c, best_d = None, bd
        for _ in range(lam):
            c = mutate(cur, rng)
            evals += 1
            d = nav_dist(c, task, best_d)
            if d <= best_d:
                best_c, best_d = c, d
            if best_d == 0 or evals >= budget:
                break
        if best_c is not None:
            improved = best_d < bd
            cur, bd = best_c, best_d
            no_imp = 0 if improved else no_imp + 1
        else:
            no_imp += 1
        if bd == 0:
            return {'solved': True, 'first_solve': evals, 'evals': evals}
        if no_imp >= stall:
            cur = rep[rng.randrange(len(rep))]
            bd = _full_d(cur, task)
            evals += 1
            no_imp = 0
            if bd == 0:
                return {'solved': True, 'first_solve': evals, 'evals': evals}
    return {'solved': False, 'first_solve': None, 'evals': evals}


def _m0_pop(task, rng, budget, use_crossover, repertoire=None, extra_pool=None,
            psize=32, immigrant=0.10):
    """extra_pool: additional artifact source for immigrants/parents — used
    ONLY by M1 wrappers later; M0 evidence arms always pass None."""
    rep = repertoire or SEED_REPERTOIRE
    def fresh():
        if extra_pool and rng.random() < 0.5:
            return mutate(extra_pool[rng.randrange(len(extra_pool))], rng)
        return mutate(rep[rng.randrange(len(rep))], rng)
    pop = [fresh() for _ in range(psize)]
    evals, dists = 0, []
    for g in pop:
        d = _full_d(g, task)
        evals += 1
        if d == 0:
            return {'solved': True, 'first_solve': evals, 'evals': evals}
        dists.append(d)
    while evals < budget:
        children = []
        for _ in range(psize):
            if rng.random() < immigrant:
                children.append(fresh())
                continue
            idxs = [rng.randrange(psize) for _ in range(3)]
            p1 = pop[min(idxs, key=lambda i: dists[i])]
            if use_crossover and rng.random() < 0.5:
                jdxs = [rng.randrange(psize) for _ in range(3)]
                p2 = pop[min(jdxs, key=lambda i: dists[i])]
                children.append(mutate(crossover(p1, p2, rng), rng))
            else:
                children.append(mutate(p1, rng))
        pop, dists = children, []
        for g in pop:
            d = _full_d(g, task)
            evals += 1
            if d == 0:
                return {'solved': True, 'first_solve': evals, 'evals': evals}
            dists.append(d)
            if evals >= budget:
                break
        while len(dists) < len(pop):
            dists.append(BIG)
    return {'solved': False, 'first_solve': None, 'evals': evals}


def m0_pop(task, rng, budget, repertoire=None, extra_pool=None):
    return _m0_pop(task, rng, budget, False, repertoire, extra_pool)


def m0_rx(task, rng, budget, repertoire=None, extra_pool=None):
    return _m0_pop(task, rng, budget, True, repertoire, extra_pool)


M0_SUITE = {'M0a-HC': m0_hc, 'M0b-POP': m0_pop, 'M0c-RX': m0_rx}


def run_ladder(nav_name, task, seed, ladder):
    """Run once at max(ladder); derive per-rung solved flags from first_solve.
    (Same trajectory prefix property: a single run at the top budget contains
    the run at every smaller budget, since budget only truncates.)"""
    fn = M0_SUITE[nav_name]
    res = fn(task, random.Random(seed), max(ladder))
    fs = res['first_solve']
    res['ladder'] = {str(b): (fs is not None and fs <= b) for b in ladder}
    return res
