"""boundary.py — the admissible observation boundary.

Solver code may touch a task ONLY through a Boundary instance. It exposes:

    start                the initial state (an ordered tuple of comparable symbols)
    is_goal(state)       exact oracle equality against the (hidden) target
    apply(pid, state)    execute one primitive; None on runtime failure; counts execs
    read(state)          the state as an ordered tuple of symbols (== and < comparable)
    prim_ids             the primitive ID alphabet

It deliberately does NOT expose: the world object, world identity, generator metadata,
witnesses, strata, moduli, inverse primitives, or any distance information. The oracle is
equality-only. tests/test_boundary.py enforces the import boundary statically.
"""
from __future__ import annotations

from primitives import PRIM_IDS


class Boundary:
    def __init__(self, world, task):
        self.prim_ids = PRIM_IDS
        self._idx = {pid: i for i, pid in enumerate(PRIM_IDS)}
        step = world.step                       # closure only; world is not retained
        self._step = step
        self._start = world.decode(task["start"])
        self._target = world.decode(task["target"])
        self.execs = 0

    @property
    def start(self):
        return self._start

    def is_goal(self, state):
        return state == self._target

    def apply(self, pid, state):
        self.execs += 1
        return self._step(self._idx[pid], state)

    def read(self, state):
        return tuple(state)

    def run_word(self, word, state):
        """Execute a sequence of primitive IDs. (state_or_None, fail_index_or_None)."""
        for i, pid in enumerate(word):
            state = self.apply(pid, state)
            if state is None:
                return None, i
        return state, None
