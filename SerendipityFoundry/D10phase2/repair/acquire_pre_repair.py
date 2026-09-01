"""D-10 acquisition harness: the ONE downstream procedure every arm shares.

Frozen properties (identical across all arms; the ONLY thing an arm may
change is WHICH k genotypes are handed in as `seed_genotypes`):

- population size P, exactly k seeded members + (P-k) fresh random members;
- elitist tournament GA identical in structure to the Foundry's
  ObjectiveSearchDriver (elites carried un-re-evaluated, one variation op
  per offspring, tournament selection, mutation/crossover mix);
- a hard evaluation meter: every engine.evaluate call costs exactly 1;
- deterministic in (seed, task, seed_genotypes, config);
- train-exact success is the SEARCH signal; test-exact success (checked
  oracle-side, never visible to the search) is the ENDPOINT.

`evented=False` runs the identical procedure without per-candidate ledger
writes. Evaluations are still counted exactly; only durability of each
individual candidate event is traded away. Used for inner/organizer
compute where the cost, not the per-candidate provenance, is what the
experiment must account for.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional, Sequence

from foundry.core.seeds import SeedStream
from foundry.engines.base import EngineLimits

# Frozen acquisition configuration. Changing any of these changes the
# harness identity and must be recorded in the preregistration.
POP_SIZE = 24
N_ELITES = 2
TOURNAMENT_K = 3
P_CROSSOVER = 0.5


@dataclass(frozen=True)
class AcqResult:
    solved_train: bool
    solved_test: bool
    evaluations: int
    first_solve_eval: Optional[int]
    best_train_fitness: float
    solver_genotype: Optional[bytes]
    final_population: tuple = ()


def acquire(engine, task, seed: int, budget: int,
            seed_genotypes: Sequence[bytes], limits: EngineLimits,
            pop_size: int = POP_SIZE) -> AcqResult:
    """Run one acquisition trial. `task` is an oracle-side ExactTask; only
    task.machine_view() ever reaches the engine."""
    tv = task.machine_view()
    ss = SeedStream(seed, "d10", "acquire")
    create_s = ss.child("create")
    mutate_s = ss.child("mutate")
    recombine_s = ss.child("recombine")
    eval_s = ss.child("eval")
    rng = random.Random(ss.child("rng").at(0))
    can_recombine = "recombine" in engine.info().capabilities

    used = 0
    best = -math.inf
    first_solve = None
    solver = None

    def ev(g: bytes):
        nonlocal used, best, first_solve, solver
        if used >= budget:
            raise _Done
        r = engine.evaluate(g, tv, eval_s.next(), limits)
        used += 1
        f = r.fitness if (r.fitness is not None
                          and math.isfinite(r.fitness)) else -math.inf
        if f > best:
            best = f
        if r.exact_success and first_solve is None:
            first_solve = used
            solver = g
            raise _Done
        return f

    pop: list[tuple[bytes, float]] = []
    try:
        for g in list(seed_genotypes)[:pop_size]:
            pop.append((bytes(g), ev(bytes(g))))
        while len(pop) < pop_size:
            g = engine.create_random(create_s.next())
            pop.append((g, ev(g)))
        while True:
            pop.sort(key=lambda m: (-m[1], m[0]))
            nxt = pop[:N_ELITES]
            while len(nxt) < pop_size:
                if can_recombine and len(pop) >= 2 and rng.random() < P_CROSSOVER:
                    pa = _tournament(rng, pop, TOURNAMENT_K)
                    pb = _tournament(rng, pop, TOURNAMENT_K)
                    child = engine.recombine(pa[0], pb[0], recombine_s.next())
                else:
                    pa = _tournament(rng, pop, TOURNAMENT_K)
                    child = engine.mutate(pa[0], mutate_s.next())
                nxt.append((child, ev(child)))
            pop = nxt
    except _Done:
        pass

    solved_train = solver is not None
    solved_test = False
    if solved_train:
        solved_test = _test_exact(engine, task, solver, limits)
    return AcqResult(solved_train=solved_train, solved_test=solved_test,
                     evaluations=used, first_solve_eval=first_solve,
                     best_train_fitness=(best if math.isfinite(best) else 0.0),
                     solver_genotype=solver,
                     final_population=tuple(g for g, _ in pop))


class _Done(Exception):
    pass


def _tournament(rng, items, k):
    idxs = [rng.randrange(len(items)) for _ in range(max(1, min(k, len(items))))]
    return items[min(idxs, key=lambda i: (-items[i][1], i))]


def _test_exact(engine, task, genotype: bytes, limits: EngineLimits) -> bool:
    """Oracle-side generalization check on the held-out test split. Never
    visible to the search; costs no acquisition budget (it is charged
    separately as endpoint-measurement compute)."""
    from foundry.engines.gp.stackvm import vm
    for ins, want in task.test_cases:
        r = vm.run_program(bytes(genotype),
                           [vm.machine_word(v) for v in ins],
                           max_steps=limits.max_steps,
                           timeout_s=limits.timeout_s)
        if r.halt != "end" or r.output != want:
            return False
    return True
