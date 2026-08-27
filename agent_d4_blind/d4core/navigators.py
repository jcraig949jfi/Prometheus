"""History-free M0 navigator suite.

All navigators: interface-only, no cross-episode state, fresh seeded RNG per
run, budget binds on metered evaluations, identical hit criterion.
Operator choice always goes through sub.sample_op(rng) — the menu
distribution is physics, not navigator knowledge.

Navigators never receive: operator semantics, substrate identity, oracle
output, graph structure, target identity (only a raw target fingerprint).

Every run records ALL of its viable starts (initial, restarts, fresh
injections) for per-episode oracle attribution, and whether a hit was scored
on an ab-initio draw ('start') or on a mutated/recombined child ('search').
"""
from __future__ import annotations

import numpy as np


class EdgeStore:
    """Observed-transition store for oracle/graph analysis (analysis-only;
    never read by any navigator)."""

    def __init__(self) -> None:
        self.edges: set[tuple] = set()      # single-parent menu transitions only
        self.edges_x: set[tuple] = set()    # crossover (two-parent) transitions:
        #   population-dependent; excluded from the oracle graph, which must
        #   estimate single-trajectory menu-physics topology
        self.fp_by_pkey: dict = {}
        self.nav_start_pkeys: set = set()

    def see(self, sub, fp) -> None:
        k = sub.pkey(fp)
        if k not in self.fp_by_pkey:
            self.fp_by_pkey[k] = fp

    def edge(self, sub, fp_from, op, fp_to) -> None:
        self.see(sub, fp_from)
        self.see(sub, fp_to)
        if op == -1:
            self.edges_x.add((sub.pkey(fp_from), sub.pkey(fp_to)))
        else:
            self.edges.add((sub.pkey(fp_from), sub.pkey(fp_to)))


class RunResult(dict):
    pass


def _sample_viable_start(sub, rng, budget_left, store, starts):
    """Sample a fresh viable start; returns (genome, fp, evals_spent) or None.
    Records the start pkey into `starts` (per-run) and the global store."""
    spent = 0
    while spent < budget_left:
        g = sub.random_genome(rng)
        f = sub.evaluate(g)
        spent += 1
        if store is not None:
            store.see(sub, f)
        if sub.viable(f):
            pk = sub.pkey(f)
            starts.append(pk)
            if store is not None:
                store.nav_start_pkeys.add(pk)
            return g, f, spent
    return None, None, spent


def _mk_result(hit, evals_to_hit, best_d, evals_used, starts, hit_via=None):
    return RunResult(hit=bool(hit), evals_to_hit=evals_to_hit, best_d=float(best_d),
                     evals_used=int(evals_used),
                     start_pkey=starts[0] if starts else None,
                     start_pkeys=list(starts), hit_via=hit_via)


def n1_restart_walk(sub, rng, budget, target_fp=None, eps_hit=0.1, store=None,
                    coverage_out=None, nonviable_restart=25):
    """N1: random-accept viable walk with restarts."""
    used = 0
    best_d = np.inf
    starts: list = []
    g, f, s = _sample_viable_start(sub, rng, budget, store, starts)
    used += s
    if g is None:
        return _mk_result(False, None, best_d, used, starts)
    if coverage_out is not None:
        coverage_out.append((used, sub.pkey(f)))
    if target_fp is not None:
        best_d = sub.d1m(f, target_fp)
        if best_d <= eps_hit:
            return _mk_result(True, used, best_d, used, starts, "start")
    streak = 0
    while used < budget:
        op = sub.sample_op(rng)
        child = sub.mutate(g, op, rng)
        fc = sub.evaluate(child)
        used += 1
        if store is not None:
            store.edge(sub, f, op, fc)
        if sub.viable(fc):
            if coverage_out is not None:
                coverage_out.append((used, sub.pkey(fc)))
            if target_fp is not None:
                d = sub.d1m(fc, target_fp)
                best_d = min(best_d, d)
                if d <= eps_hit:
                    return _mk_result(True, used, best_d, used, starts, "search")
            g, f = child, fc
            streak = 0
        else:
            streak += 1
            if streak >= nonviable_restart:
                g2, f2, s = _sample_viable_start(sub, rng, budget - used, store, starts)
                used += s
                if g2 is None:
                    break
                g, f = g2, f2
                streak = 0
                if coverage_out is not None:
                    coverage_out.append((used, sub.pkey(f)))
                if target_fp is not None:
                    d = sub.d1m(f, target_fp)
                    best_d = min(best_d, d)
                    if d <= eps_hit:
                        return _mk_result(True, used, best_d, used, starts, "start")
    return _mk_result(False, None, best_d, used, starts)


def n2_hillclimb(sub, rng, budget, target_fp=None, eps_hit=0.1, store=None,
                 coverage_out=None, stall_restart=60, nonviable_restart=25):
    """N2: greedy d1-to-target descent, plateau-tolerant, random restarts."""
    assert target_fp is not None
    used = 0
    best_d = np.inf
    starts: list = []

    def fresh():
        nonlocal used
        g, f, s = _sample_viable_start(sub, rng, budget - used, store, starts)
        used += s
        return g, f

    g, f = fresh()
    if g is None:
        return _mk_result(False, None, best_d, used, starts)
    d_cur = sub.d1m(f, target_fp)
    best_d = d_cur
    if d_cur <= eps_hit:
        return _mk_result(True, used, best_d, used, starts, "start")
    stall = 0
    nonviable = 0
    while used < budget:
        op = sub.sample_op(rng)
        child = sub.mutate(g, op, rng)
        fc = sub.evaluate(child)
        used += 1
        if store is not None:
            store.edge(sub, f, op, fc)
        if sub.viable(fc):
            nonviable = 0
            d = sub.d1m(fc, target_fp)
            best_d = min(best_d, d)
            if d <= eps_hit:
                return _mk_result(True, used, best_d, used, starts, "search")
            if d < d_cur or (d == d_cur and rng.random() < 0.5):
                if d < d_cur:
                    stall = 0
                else:
                    stall += 1
                g, f, d_cur = child, fc, d
            else:
                stall += 1
        else:
            nonviable += 1
            stall += 1
        if stall >= stall_restart or nonviable >= nonviable_restart:
            g2, f2 = fresh()
            if g2 is None:
                break
            g, f = g2, f2
            d_cur = sub.d1m(f, target_fp)
            best_d = min(best_d, d_cur)
            if d_cur <= eps_hit:
                return _mk_result(True, used, best_d, used, starts, "start")
            stall = 0
            nonviable = 0
    return _mk_result(False, None, best_d, used, starts)


def n3_novelty(sub, rng, budget, target_fp=None, eps_hit=0.1, store=None,
               coverage_out=None, k_near=5, add_thresh=0.05, archive_cap=400,
               nonviable_restart=25):
    """N3: archive-based novelty walk (targetless mapper; archive is within-run
    search state, discarded across runs). Incidental target hits recorded."""
    used = 0
    best_d = np.inf
    starts: list = []
    archive: list = []

    def novelty(f):
        if not archive:
            return 1.0
        ds = []
        for a in archive:
            ds.append(sub.d1m(f, a))
        ds.sort()
        return float(np.mean(ds[:k_near]))

    g, f, s = _sample_viable_start(sub, rng, budget, store, starts)
    used += s
    if g is None:
        return _mk_result(False, None, best_d, used, starts)
    archive.append(f)
    if coverage_out is not None:
        coverage_out.append((used, sub.pkey(f)))
    if target_fp is not None:
        best_d = sub.d1m(f, target_fp)
        if best_d <= eps_hit:
            return _mk_result(True, used, best_d, used, starts, "start")
    nov_cur = 0.0
    streak = 0
    while used < budget:
        op = sub.sample_op(rng)
        child = sub.mutate(g, op, rng)
        fc = sub.evaluate(child)
        used += 1
        if store is not None:
            store.edge(sub, f, op, fc)
        if not sub.viable(fc):
            streak += 1
            if streak >= nonviable_restart:
                g2, f2, s = _sample_viable_start(sub, rng, budget - used, store, starts)
                used += s
                if g2 is None:
                    break
                g, f = g2, f2
                streak = 0
                if target_fp is not None:
                    d = sub.d1m(f, target_fp)
                    best_d = min(best_d, d)
                    if d <= eps_hit:
                        return _mk_result(True, used, best_d, used, starts, "start")
            continue
        streak = 0
        if coverage_out is not None:
            coverage_out.append((used, sub.pkey(fc)))
        if target_fp is not None:
            d = sub.d1m(fc, target_fp)
            best_d = min(best_d, d)
            if d <= eps_hit:
                return _mk_result(True, used, best_d, used, starts, "search")
        nov_child = novelty(fc)
        if nov_child >= nov_cur:
            g, f, nov_cur = child, fc, nov_child
        nd = min((sub.d1m(fc, a) for a in archive), default=1.0)
        if nd > add_thresh:
            archive.append(fc)
            if len(archive) > archive_cap:
                archive.pop(0)
    return _mk_result(False, None, best_d, used, starts)


def n4_recombiner(sub, rng, budget, target_fp=None, eps_hit=0.1, store=None,
                  coverage_out=None, pop_size=16, p_mutate=0.5, p_fresh=0.05,
                  tourn_k=3):
    """N4: population recombination with selection on d1-to-target.
    p_fresh kept low (0.05): at 0.15 N4 was substantially a restart sampler."""
    assert target_fp is not None
    used = 0
    best_d = np.inf
    starts: list = []
    pop: list = []  # (genome, fp, d)
    while len(pop) < pop_size and used < budget // 3:
        g = sub.random_genome(rng)
        f = sub.evaluate(g)
        used += 1
        if store is not None:
            store.see(sub, f)
        if sub.viable(f):
            pk = sub.pkey(f)
            starts.append(pk)
            if store is not None:
                store.nav_start_pkeys.add(pk)
            d = sub.d1m(f, target_fp)
            best_d = min(best_d, d)
            if d <= eps_hit:
                return _mk_result(True, used, best_d, used, starts, "start")
            pop.append((g, f, d))
    if len(pop) < 2:
        return _mk_result(False, None, best_d, used, starts)

    def tournament():
        idx = rng.integers(0, len(pop), size=tourn_k)
        return min(idx, key=lambda i: pop[i][2])

    while used < budget:
        if rng.random() < p_fresh:
            child = sub.random_genome(rng)
            fc = sub.evaluate(child)
            used += 1
            via = "start"
            if store is not None:
                store.see(sub, fc)
            if sub.viable(fc):
                pk = sub.pkey(fc)
                starts.append(pk)
                if store is not None:
                    store.nav_start_pkeys.add(pk)
        else:
            i, j = tournament(), tournament()
            child = sub.crossover(pop[i][0], pop[j][0], rng)
            if rng.random() < p_mutate:
                op = sub.sample_op(rng)
                child = sub.mutate(child, op, rng)
            fc = sub.evaluate(child)
            used += 1
            via = "search"
            if store is not None:
                store.edge(sub, pop[i][1], -1, fc)
        if sub.viable(fc):
            d = sub.d1m(fc, target_fp)
            best_d = min(best_d, d)
            if d <= eps_hit:
                return _mk_result(True, used, best_d, used, starts, via)
            worst = max(range(len(pop)), key=lambda t: pop[t][2])
            if d < pop[worst][2]:
                pop[worst] = (child, fc, d)
    return _mk_result(False, None, best_d, used, starts)


NAVIGATORS = {
    "N1_RESTART_WALK": n1_restart_walk,
    "N2_HILLCLIMB": n2_hillclimb,
    "N3_NOVELTY": n3_novelty,
    "N4_RECOMBINER": n4_recombiner,
}
COMPETITIVE_PAIR = ("N2_HILLCLIMB", "N4_RECOMBINER")
TARGETED = ("N1_RESTART_WALK", "N2_HILLCLIMB", "N3_NOVELTY", "N4_RECOMBINER")
COVERAGE = ("N1_RESTART_WALK", "N3_NOVELTY")
