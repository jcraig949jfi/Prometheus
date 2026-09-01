"""D-10 acquisition harness: the ONE downstream procedure every arm shares.

Frozen properties (identical across all arms; the ONLY thing an arm may
change is WHICH k genotypes are handed in as `seed_genotypes`):

- population size P, exactly k seeded members + (P-k) fresh random members;
- elitist tournament GA;
- a hard evaluation meter AND a first-class VM-step meter;
- deterministic in (seed, task, seed_genotypes, config);
- train-exact success is the SEARCH signal; test-exact success (checked
  oracle-side, never visible to the search) is the ENDPOINT.

PHASE 2 REPAIRS
  D2  Fitness ties are broken by a SEEDED PER-INDIVIDUAL HASH, not by
      genotype bytes and not by list position. Before this repair the
      cold-start regime (where essentially every individual is tied at
      fitness 0) made the GA a lexicographic sort on genotype bytes, which
      gave injected material a large content-free advantage or handicap
      purely from its leading byte. Measured in the real loop before
      repair: injected genotypes occupied 6.137% of parent slots at
      leading byte 0x00 versus 0.217% at 0xFF -- a 28.3x swing carrying no
      admissible scientific content. The tie-break is now deterministic in
      (trial seed, genotype) and pseudorandom with respect to every
      admissible property.
  D4  Genotype length is hard-bounded at MAX_GENOTYPE_BYTES (donor
      variation semantics are untouched: the operator runs unchanged and
      its output is truncated, which is total because every byte string is
      a legal StackVM program). VM steps are metered and returned as a
      first-class cost alongside the evaluation count.
"""
from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from typing import Optional, Sequence

from foundry.core.seeds import SeedStream
from foundry.engines.base import EngineLimits

# Frozen acquisition configuration.
POP_SIZE = 24
N_ELITES = 2
TOURNAMENT_K = 3
P_CROSSOVER = 0.5
# D4: experiment-local hard bound on program size. The Foundry's own
# EngineLimits.max_genotype_bytes default is 1_000_000 and only PENALISES
# oversize genotypes after evaluation; nothing bounded growth. Measured
# before repair: 3139 bytes at B=6400.
MAX_GENOTYPE_BYTES = 1024


@dataclass(frozen=True)
class AcqResult:
    solved_train: bool
    solved_test: bool
    evaluations: int
    vm_steps: int                 # D4: first-class compute meter
    first_solve_eval: Optional[int]
    best_train_fitness: float
    solver_genotype: Optional[bytes]
    final_population: tuple = ()
    n_truncated: int = 0          # D4: how often the length bound bound


def _tiebreak(salt: int, genotype: bytes) -> bytes:
    """D2: deterministic, content-pseudorandom tie-break token."""
    h = hashlib.sha256()
    h.update(int(salt).to_bytes(8, "big"))
    h.update(b"\x00")
    h.update(genotype)
    return h.digest()


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
    salt = ss.child("tiebreak").at(0)
    can_recombine = "recombine" in engine.info().capabilities

    used = 0
    steps = 0
    truncated = 0
    best = -math.inf
    first_solve = None
    solver = None

    def bound(g: bytes) -> bytes:
        nonlocal truncated
        if len(g) > MAX_GENOTYPE_BYTES:
            truncated += 1
            return g[:MAX_GENOTYPE_BYTES]
        return g

    def ev(g: bytes):
        nonlocal used, steps, best, first_solve, solver
        if used >= budget:
            raise _Done
        r = engine.evaluate(g, tv, eval_s.next(), limits)
        used += 1
        steps += int(getattr(r.resources, "steps", 0) or 0)
        f = r.fitness if (r.fitness is not None
                          and math.isfinite(r.fitness)) else -math.inf
        if f > best:
            best = f
        if r.exact_success and first_solve is None:
            first_solve = used
            solver = g
            raise _Done
        return f

    # population members are (genotype, fitness, tiebreak_token)
    pop: list[tuple[bytes, float, bytes]] = []
    try:
        for g in list(seed_genotypes)[:pop_size]:
            g = bound(bytes(g))
            pop.append((g, ev(g), _tiebreak(salt, g)))
        while len(pop) < pop_size:
            g = bound(engine.create_random(create_s.next()))
            pop.append((g, ev(g), _tiebreak(salt, g)))
        while True:
            # D2: ties resolved by the seeded token, never by genotype bytes
            pop.sort(key=lambda m: (-m[1], m[2]))
            nxt = pop[:N_ELITES]
            while len(nxt) < pop_size:
                if can_recombine and len(pop) >= 2 and rng.random() < P_CROSSOVER:
                    pa = _tournament(rng, pop, TOURNAMENT_K)
                    pb = _tournament(rng, pop, TOURNAMENT_K)
                    child = bound(engine.recombine(pa[0], pb[0],
                                                   recombine_s.next()))
                else:
                    pa = _tournament(rng, pop, TOURNAMENT_K)
                    child = bound(engine.mutate(pa[0], mutate_s.next()))
                nxt.append((child, ev(child), _tiebreak(salt, child)))
            pop = nxt
    except _Done:
        pass

    solved_train = solver is not None
    solved_test = False
    if solved_train:
        solved_test = _test_exact(engine, task, solver, limits)
    return AcqResult(solved_train=solved_train, solved_test=solved_test,
                     evaluations=used, vm_steps=steps,
                     first_solve_eval=first_solve,
                     best_train_fitness=(best if math.isfinite(best) else 0.0),
                     solver_genotype=solver,
                     final_population=tuple(g for g, _, _ in pop),
                     n_truncated=truncated)


class _Done(Exception):
    pass


def _tournament(rng, items, k):
    """D2: among equal fitness the winner is decided by the seeded token,
    not by list position (which previously inherited the byte ordering)."""
    idxs = [rng.randrange(len(items)) for _ in range(max(1, min(k, len(items))))]
    return items[min(idxs, key=lambda i: (-items[i][1], items[i][2]))]


def _test_exact(engine, task, genotype: bytes, limits: EngineLimits) -> bool:
    """Oracle-side generalization check on the held-out test split. Never
    visible to the search; charged separately as endpoint-measurement
    compute."""
    from foundry.engines.gp.stackvm import vm
    for ins, want in task.test_cases:
        r = vm.run_program(bytes(genotype),
                           [vm.machine_word(v) for v in ins],
                           max_steps=limits.max_steps,
                           timeout_s=limits.timeout_s)
        if r.halt != "end" or r.output != want:
            return False
    return True
