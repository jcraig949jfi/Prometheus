"""R5 straw men: counterfactual control — "what changes if premise X flips?"

Rung notes: techne/loop/rung_notes/R5_counterfactual.md. The cycle-006 ChatGPT block asked
whether R5 is distinct from "run twice sequentially and diff". This module is our own answer,
in the resource discipline the ladder now runs on (claims v4/v5):

    Under SINGLE-PASS input (each event seen once) with bounded memory, run-twice needs a
    replay buffer whose size grows with the stream — a blackboard smuggled in as "just
    re-run". Genuine counterfactual control holds MULTIPLE LIVE STATES in O(#branches)
    memory. Same capacity-separation shape as R3, one level up: the resource is now live
    PARALLEL state, not retained facts.

Circuits:
- TwoBranchCircuit: at the fork, clones the register; every later event updates BOTH
  branches; any query (actual/counterfactual/diff) answerable at any time. Memory: 2 cells.
- ReplayCircuit(cap): the run-twice strategy made honest — buffers events (up to cap) and
  re-runs with the flip on demand. Works below cap; ABSTAINS beyond it (a silent truncation
  would be the liar variant).
- DeltaOnlyCircuit: the gaming trap. Tracks only the DIFFERENCE between branches. Passes
  every battery whose post-fork updates are additive (delta is invariant); breaks the moment
  a multiplicative event scales the gap. Batteries with only linear post-fork updates cannot
  tell delta-tracking from branch-holding — that is the trap to publish, not the circuit.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

Event = Tuple[str, float]  # ("add", v) | ("mul", v)
Fork = Tuple[int, float]   # (event index to flip, alternative value for that event)


def apply_event(state: float, ev: Event) -> float:
    kind, v = ev
    if kind == "add":
        return state + v
    if kind == "mul":
        return state * v
    raise ValueError(f"unknown event kind {kind!r}")


@dataclass
class TwoBranchCircuit:
    """Holds actual and counterfactual as FIRST-CLASS parallel state. Single pass, O(1) mem."""

    actual: float = 0.0
    counterfactual: Optional[float] = None
    _index: int = 0
    fork: Optional[Fork] = None

    def feed(self, ev: Event) -> None:
        if self.fork is not None and self._index == self.fork[0]:
            # the fork point: counterfactual branch takes the alternative event
            self.counterfactual = apply_event(self.actual, (ev[0], self.fork[1]))
            self.actual = apply_event(self.actual, ev)
        else:
            self.actual = apply_event(self.actual, ev)
            if self.counterfactual is not None:
                self.counterfactual = apply_event(self.counterfactual, ev)
        self._index += 1

    def query(self, which: str) -> Optional[float]:
        if which == "actual":
            return self.actual
        if self.counterfactual is None:
            return None
        if which == "counterfactual":
            return self.counterfactual
        if which == "diff":
            return self.counterfactual - self.actual
        raise ValueError(which)

    def memory_cells(self) -> int:
        return 2 if self.counterfactual is not None else 1


@dataclass
class ReplayCircuit:
    """Run-twice-and-diff, honestly bounded: buffers up to `cap` events for replay."""

    cap: int
    fork: Optional[Fork] = None
    actual: float = 0.0
    _buffer: List[Event] = field(default_factory=list)
    _dropped: bool = False

    def feed(self, ev: Event) -> None:
        self.actual = apply_event(self.actual, ev)
        if len(self._buffer) < self.cap:
            self._buffer.append(ev)
        else:
            self._dropped = True  # single-pass world: an unbuffered event is gone forever

    def query(self, which: str) -> Optional[float]:
        if which == "actual":
            return self.actual
        if self.fork is None:
            return None
        if self._dropped:
            return None  # cannot replay what it could not keep — abstain, never fabricate
        k, alt = self.fork
        state = 0.0
        for i, ev in enumerate(self._buffer):
            state = apply_event(state, (ev[0], alt) if i == k else ev)
        if which == "counterfactual":
            return state
        if which == "diff":
            return state - self.actual
        raise ValueError(which)

    def memory_cells(self) -> int:
        return 1 + len(self._buffer)


@dataclass
class DeltaOnlyCircuit:
    """The trap: tracks actual + (counterfactual - actual) only. Exact while post-fork
    events are additive; silently WRONG after any multiplicative event (it applies the
    update to actual but cannot scale the gap it never decomposed)."""

    actual: float = 0.0
    delta: Optional[float] = None
    _index: int = 0
    fork: Optional[Fork] = None

    def feed(self, ev: Event) -> None:
        if self.fork is not None and self._index == self.fork[0]:
            self.delta = self.fork[1] - ev[1] if ev[0] == "add" else None
            if ev[0] == "mul":
                self.delta = self.actual * self.fork[1] - self.actual * ev[1]
        self.actual = apply_event(self.actual, ev)
        self._index += 1
        # the bug that defines the circuit: post-fork events never touch self.delta

    def query(self, which: str) -> Optional[float]:
        if which == "actual":
            return self.actual
        if self.delta is None:
            return None
        if which == "diff":
            return self.delta
        if which == "counterfactual":
            return self.actual + self.delta
        raise ValueError(which)
