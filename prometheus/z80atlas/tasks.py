"""Task worlds and the Cycle-8 accessibility manipulations.

A task maps input bytes to an expected output; the SCORING mode and the READ GATE are the accessibility knobs:
  scoring   ATOMIC       exact match or nothing (a known zero-fitness valley around every near-miss)
            INCREMENTAL  partial credit by byte distance (constants are incrementally reachable by INC/DEC steps)
            NEUTRAL      the task exerts no pressure (score always 0; the task is still measured)
  read gate ABR          answer-before-read: outputs emitted before any IN still count (a constant answer scores on
                         the inputs it happens to match -- the moat)
            FORCED       outputs emitted before the first IN are discarded (the organism must read to answer)
Tasks come in matched families so that the mutational distance between them can be MEASURED (geometry.py), never
assumed: CONST (atomic vs incremental constant), ECHO -> INC -> COND_ONE (one conditional edit away from INC) ->
COND_MULTI (several edits), SUM2 (two forced reads).

Environment dynamics (the world's task distribution): FIXED; SHIFT (the task changes at fixed intervals);
DRIFT (the constant target mutates by +-1 with a rate -- environment parameters MUTATE); COEVOLVE (the target moves
AWAY from the population's modal answer -- a minimal world/environment co-evolution); PER_NICHE (each niche has its
own task from the family, a local task distribution); ENV_REPRO (a niche's task parameters are copied into a
neighbouring niche when that niche's population is persistent -- environments REPRODUCE)."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

TASKS = ("CONST", "ECHO", "INC", "COND_ONE", "COND_MULTI", "SUM2")
SCORING = ("ATOMIC", "INCREMENTAL", "NEUTRAL")
READ_GATE = ("ABR", "FORCED")
ENV_DYNAMICS = ("FIXED", "SHIFT", "DRIFT", "COEVOLVE", "PER_NICHE", "ENV_REPRO")


@dataclass
class Task:
    kind: str
    k: int = 42               # the constant target (CONST) / a parameter that can drift
    n_inputs: int = 1

    def expected(self, inputs: List[int]) -> List[int]:
        x = inputs[0] if inputs else 0
        if self.kind == "CONST":
            return [self.k & 0xFF]
        if self.kind == "ECHO":
            return [x]
        if self.kind == "INC":
            return [(x + 1) & 0xFF]
        if self.kind == "COND_ONE":
            return [x if x < 128 else (x + 1) & 0xFF]
        if self.kind == "COND_MULTI":
            return [x if x < 128 else ((x ^ 0x55) + 3) & 0xFF]
        if self.kind == "SUM2":
            y = inputs[1] if len(inputs) > 1 else 0
            return [(x + y) & 0xFF]
        raise ValueError(self.kind)

    def inputs(self, rng: random.Random) -> List[int]:
        n = 2 if self.kind == "SUM2" else 1
        return [rng.randrange(256) for _ in range(n)]

    def needs_read(self) -> bool:
        return self.kind != "CONST"

    def to_dict(self) -> dict:
        return {"kind": self.kind, "k": self.k}


def score(task: Task, outputs: List[int], expected: List[int], scoring: str, read_gate: str, first_out_step, first_in_step) -> float:
    """0..1. Under FORCED, outputs emitted before the first IN are discarded (for tasks that need a read)."""
    if scoring == "NEUTRAL":
        return 0.0
    outs = list(outputs)
    if read_gate == "FORCED" and task.needs_read():
        if first_in_step is None:
            return 0.0
        if first_out_step is not None and first_out_step < first_in_step:
            # drop the outputs that came before the first read: we do not know how many exactly, so require that
            # the organism read before it answered at all (the strict gate)
            return 0.0
    if not outs:
        return 0.0
    got = outs[0]; want = expected[0]
    if scoring == "ATOMIC":
        return 1.0 if got == want else 0.0
    d = abs(got - want); d = min(d, 256 - d)
    return max(0.0, 1.0 - d / 128.0)


class Environment:
    """The world's task distribution over time and niches. Deterministic given its seed."""

    def __init__(self, task_kind: str, dynamics: str, n_niches: int, seed: int, shift_every: int = 60, drift_rate: float = 0.05):
        self.rng = random.Random(seed)
        self.dynamics = dynamics
        self.n_niches = max(1, n_niches)
        self.shift_every = shift_every
        self.drift_rate = drift_rate
        base_k = self.rng.randrange(256)
        if dynamics == "PER_NICHE":
            fam = ["ECHO", "INC", "COND_ONE", "COND_MULTI"] if task_kind in ("COND_ONE", "COND_MULTI") else [task_kind] * 4
            self.tasks = [Task(fam[i % len(fam)], k=(base_k + 17 * i) & 0xFF) for i in range(self.n_niches)]
        else:
            self.tasks = [Task(task_kind, k=base_k) for _ in range(self.n_niches)]
        self.history: List[dict] = [{"tick": 0, "tasks": [t.to_dict() for t in self.tasks], "why": "init"}]
        self.lineage: List[dict] = []          # environment ancestry when environments reproduce

    def task_for(self, niche: int) -> Task:
        return self.tasks[niche % self.n_niches]

    def step(self, tick: int, modal_answers: Optional[List[Optional[int]]] = None, persistent: Optional[List[bool]] = None) -> Optional[dict]:
        """Advance the environment one tick. Returns a change record when something changed (world ancestry)."""
        change = None
        if self.dynamics == "SHIFT" and tick > 0 and tick % self.shift_every == 0:
            order = ["ECHO", "INC", "COND_ONE", "COND_MULTI"]
            for i, t in enumerate(self.tasks):
                if t.kind in order:
                    t.kind = order[(order.index(t.kind) + 1) % len(order)]
                else:
                    t.k = (t.k + 37) & 0xFF
            change = {"tick": tick, "why": "shift", "tasks": [t.to_dict() for t in self.tasks]}
        elif self.dynamics == "DRIFT":
            moved = False
            for t in self.tasks:
                if self.rng.random() < self.drift_rate:
                    t.k = (t.k + self.rng.choice((-1, 1))) & 0xFF; moved = True
            if moved:
                change = {"tick": tick, "why": "drift", "tasks": [t.to_dict() for t in self.tasks]}
        elif self.dynamics == "COEVOLVE" and modal_answers is not None:
            moved = False
            for i, t in enumerate(self.tasks):
                m = modal_answers[i % len(modal_answers)] if modal_answers else None
                if t.kind == "CONST" and m is not None and m == t.k:
                    t.k = (t.k + self.rng.choice((-3, -2, 2, 3))) & 0xFF; moved = True     # the target runs from the answer
            if moved:
                change = {"tick": tick, "why": "coevolve", "tasks": [t.to_dict() for t in self.tasks]}
        elif self.dynamics == "ENV_REPRO" and persistent is not None and tick > 0 and tick % 20 == 0:
            for i in range(self.n_niches):
                j = (i + 1) % self.n_niches
                if persistent[i % len(persistent)] and not persistent[j % len(persistent)] and self.rng.random() < 0.5:
                    src = self.tasks[i]; self.tasks[j] = Task(src.kind, k=(src.k + self.rng.choice((0, 0, 1, -1))) & 0xFF)
                    self.lineage.append({"tick": tick, "parent_niche": i, "child_niche": j, "task": self.tasks[j].to_dict()})
                    change = {"tick": tick, "why": "env_reproduction", "tasks": [t.to_dict() for t in self.tasks]}
        if change:
            self.history.append(change)
        return change


# ---- verified solving (added 2026-09-23, forensics C2/C3/C4) ---------------------------------------------------------
# A 'solver' in the v1 telemetry is score_ema >= 0.85 under the run's scoring: under INCREMENTAL that accepts answers
# ~19 off, under ATOMIC a half-right program reaches it by luck. The verified test below is the one ruler every arm
# shares: the tape, ALONE (empty neighbour window), answers EVERY input of a fixed panel exactly, under the run's read
# gate, for the CONFIGURED task (never an easier niche task).
_PANEL_1 = (0, 1, 2, 42, 64, 100, 126, 127, 128, 129, 130, 170, 200, 213, 254, 255)


def panel(task: Task) -> List[List[int]]:
    if task.kind == "SUM2":
        return [[a, b] for a, b in zip(_PANEL_1, reversed(_PANEL_1))]
    return [[x] for x in _PANEL_1]


def verify_tape(tape: bytes, L: int, task: Task, read_gate: str, budget: int = 256, layout: str = "SHARED", allow_copyall: bool = False) -> dict:
    from prometheus.z80atlas import vm
    tape = bytes(tape[:L]) + bytes(max(0, L - len(tape)))
    right = 0; P = panel(task)
    for inputs in P:
        mem = bytearray(256); mem[:L] = tape
        for k, v in enumerate(inputs):
            mem[vm.IN_BASE + k] = v
        if layout == "SEPARATED":
            t1 = vm.execute(mem, L, 0, budget // 2, inputs, region=(0, L // 2), allow_copyall=allow_copyall)
            t2 = vm.execute(mem, L, L // 2, budget // 2, inputs, region=(L // 2, L), allow_copyall=allow_copyall)
            outs = t1.outputs + t2.outputs
            fi = t1.first_in_step if t1.first_in_step is not None else (None if t2.first_in_step is None else t2.first_in_step + t1.steps)
            fo = t1.first_out_step if t1.first_out_step is not None else (None if t2.first_out_step is None else t2.first_out_step + t1.steps)
        else:
            t1 = vm.execute(mem, L, 0, budget, inputs, allow_copyall=allow_copyall)
            outs, fi, fo = t1.outputs, t1.first_in_step, t1.first_out_step
        right += score(task, outs, task.expected(inputs), "ATOMIC", read_gate, fo, fi) >= 0.999
    return {"exact": right == len(P), "accuracy": right / len(P), "n": len(P)}
