"""Substrate-generated exact tasks: the D-10 environment.

A task is defined by a REFERENCE PROGRAM in the same substrate the learner
searches. This is deliberate and declared:

- exact solvability is guaranteed by construction (an unreachable target
  would make a null result uninterpretable — instrument failure masquerading
  as hypothesis failure);
- task difficulty has a mechanical dial (reference program length / step
  count), so an operating point with usable variance can be chosen BEFORE
  the experiment rather than hoped for;
- family members share reusable substructure by descent, not by a human
  notion of similarity: a family is a reference program plus its mutational
  neighbours. "Belongs to the same family" is a fact about the substrate's
  own deterministic consequences, never a label any learner, index, or
  organizer can read;
- no human semantic category (arithmetic, string, list, ...) enters the
  environment at all.

Every generated task passes a SHORTCUT SCREEN: it is rejected if any member
of a frozen trivial-program set solves it exactly. The screen's pass rate is
the environment's recorded shortcut ceiling.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from foundry.core.seeds import derive_seed
from foundry.engines.gp.stackvm import vm
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.tasks.base import ExactTask

_ENG = StackVMAdapter()

# -- frozen environment constants ------------------------------------------
ARITY = 2
INPUT_LO, INPUT_HI = 0, 255
PROBE_N = 40                 # inputs used for the non-degeneracy filter
MAX_REF_STEPS = 64           # reference program must halt within this
MIN_DISTINCT_FRAC = 0.60     # distinct outputs / probe inputs
TRIVIAL_MAX_LEN = 2          # exhaustive screen over <=2-instruction programs
TRIVIAL_RANDOM_N = 2000      # plus this many fixed random programs
TRIVIAL_RANDOM_LEN = (8, 48)


def _run(prog: bytes, ins: list[int], max_steps: int = 100_000):
    return vm.run_program(prog, [vm.machine_word(v) for v in ins],
                          max_steps=max_steps, timeout_s=5.0)


def _probe_inputs(seed: int, n: int) -> list[list[int]]:
    rng = random.Random(seed)
    seen, out = set(), []
    while len(out) < n:
        t = tuple(rng.randint(INPUT_LO, INPUT_HI) for _ in range(ARITY))
        if t not in seen:
            seen.add(t)
            out.append(list(t))
    return out


# -- frozen trivial-program set (the shortcut screen) -----------------------

def _trivial_programs() -> list[bytes]:
    progs: list[bytes] = []
    # every 1- and 2-instruction program over the opcode set, operands 0
    ops = list(range(vm.N_OPCODES))
    for a in ops:
        progs.append(bytes([a] + [0] * vm.OPCODES[a][1]))
    if TRIVIAL_MAX_LEN >= 2:
        for a in ops:
            for b in ops:
                progs.append(bytes([a] + [0] * vm.OPCODES[a][1]
                                   + [b] + [0] * vm.OPCODES[b][1]))
    rng = random.Random(derive_seed(0, "d10", "trivial_screen"))
    for _ in range(TRIVIAL_RANDOM_N):
        n = rng.randint(*TRIVIAL_RANDOM_LEN)
        progs.append(bytes(rng.randrange(256) for _ in range(n)))
    return progs


_TRIVIAL: Optional[list[bytes]] = None


def trivial_programs() -> list[bytes]:
    global _TRIVIAL
    if _TRIVIAL is None:
        _TRIVIAL = _trivial_programs()
    return _TRIVIAL


def solved_by_trivial(cases: list[tuple[list[int], int]]) -> bool:
    for p in trivial_programs():
        ok = True
        for ins, want in cases:
            r = _run(p, ins, max_steps=200)
            if r.halt != "end" or r.output != want:
                ok = False
                break
        if ok:
            return True
    return False


# -- reference programs -----------------------------------------------------

def _acceptable_reference(prog: bytes, probe_seed: int) -> Optional[list[int]]:
    """Return the probe outputs if `prog` is an acceptable reference."""
    outs = []
    for ins in _probe_inputs(probe_seed, PROBE_N):
        r = _run(prog, ins, max_steps=MAX_REF_STEPS + 1)
        if r.halt != "end":
            return None
        outs.append(r.output)
    if len(set(outs)) < MIN_DISTINCT_FRAC * PROBE_N:
        return None
    return outs


def sample_root(seed: int, length: int, max_tries: int = 400
                ) -> Optional[bytes]:
    """A family root: a random program that halts, is non-degenerate, and is
    not exactly reproduced by the trivial-program screen."""
    for i in range(max_tries):
        rng = random.Random(derive_seed(seed, "d10", "root", f"#{i}"))
        prog = bytes(rng.randrange(256) for _ in range(length))
        if _acceptable_reference(prog, derive_seed(seed, "d10", "probe")) is None:
            continue
        return prog
    return None


def sample_member(root: bytes, seed: int, n_mut: int,
                  max_tries: int = 200) -> Optional[bytes]:
    """A family member: `n_mut` substrate mutations from the root, still
    an acceptable reference and behaviourally distinct from the root."""
    probe = _probe_inputs(derive_seed(seed, "d10", "probe"), PROBE_N)
    root_outs = [_run(root, ins, MAX_REF_STEPS + 1).output for ins in probe]
    for i in range(max_tries):
        g = root
        for j in range(n_mut):
            g = _ENG.mutate(g, derive_seed(seed, "d10", "member", f"#{i}",
                                           f"m{j}"))
        outs = _acceptable_reference(g, derive_seed(seed, "d10", "probe"))
        if outs is None or outs == root_outs:
            continue
        return g
    return None


@dataclass(frozen=True)
class ProgTask:
    task: ExactTask
    reference: bytes
    family_id: str          # oracle-side ONLY; never reaches a learner
    member_index: int


def task_from_program(prog: bytes, seed: int, n_train: int, n_test: int,
                      family_id: str, member_index: int,
                      screen: bool = True) -> Optional[ProgTask]:
    rng = random.Random(derive_seed(seed, "d10", "cases"))
    seen, pool = set(), []
    while len(pool) < n_train + n_test:
        t = tuple(rng.randint(INPUT_LO, INPUT_HI) for _ in range(ARITY))
        if t in seen:
            continue
        seen.add(t)
        r = _run(prog, list(t), max_steps=MAX_REF_STEPS + 1)
        if r.halt != "end":
            return None
        pool.append((list(t), r.output))
    train, test = pool[:n_train], pool[n_train:]
    if screen and solved_by_trivial(train + test):
        return None
    return ProgTask(
        task=ExactTask(train_cases=train, test_cases=test,
                       admin_metadata={"family_id": family_id},
                       provenance={"source": "d10_progtask",
                                   "family_id": family_id,
                                   "member_index": member_index,
                                   "reference_len": len(prog),
                                   "seed": seed, "n_train": n_train,
                                   "n_test": n_test}),
        reference=prog, family_id=family_id, member_index=member_index)
