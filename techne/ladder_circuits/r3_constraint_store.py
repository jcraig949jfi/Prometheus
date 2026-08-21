"""R3 separation experiment: persistent queryable state vs bounded sequential state.

Folds in the 2026-08-21 ChatGPT critique (via James): "R3 = R2 + blackboard" collapses if
R2's threaded witness may grow without bound — history-threading IS a blackboard. The killable
boundary needs a RESOURCE RESTRICTION:

    R2: bounded sufficient state passed locally (fixed width k).
    R3: unbounded persistent facts with content-addressable consultation.

Their minimal separating family, implemented here: declare constraints x_1!=0 ... x_n!=0,
run arbitrarily many irrelevant transformations, then ask whether x_k/x_k may cancel for an
ADVERSARIALLY chosen k. Correct = cancel iff x_k != 0 was declared. Pigeonhole: any circuit
holding at most k < n independently-queryable facts must have lost some declared fact; the
adversary queries a lost one. The constraint store answers all queries at any n.

Honesty rule for the bounded circuit: when it does not KNOW a fact, it abstains (returns
False for "may cancel") — it is conservative, never unsound. The failure mode the separation
exhibits is INCOMPLETENESS under capacity pressure, which is exactly the R2/R3 boundary
behavior, not a bug.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import List, Literal, Set, Tuple

Event = Tuple[str, str]  # ("declare_nonzero", var) | ("noise", payload) | ("query_cancel", var)


@dataclass
class ConstraintStoreCircuit:
    """R3: unbounded, content-addressable fact store. Facts persist; queries are global."""

    facts: Set[str] = field(default_factory=set)

    def run(self, events: List[Event]) -> List[bool]:
        answers: List[bool] = []
        for kind, payload in events:
            if kind == "declare_nonzero":
                self.facts.add(payload)
            elif kind == "query_cancel":
                answers.append(payload in self.facts)
            # noise events deliberately touch nothing
        return answers


@dataclass
class FixedWidthPipeline:
    """R2-with-a-bound: threads at most `width` facts of sequential state. Eviction policy is
    a parameter so the separation is shown against the canonical policies, not one straw
    choice (the pigeonhole argument is policy-independent; tests exhibit it concretely)."""

    width: int
    policy: Literal["fifo", "lifo"] = "fifo"
    _state: "OrderedDict[str, None]" = field(default_factory=OrderedDict)

    def run(self, events: List[Event]) -> List[bool]:
        answers: List[bool] = []
        for kind, payload in events:
            if kind == "declare_nonzero":
                self._state[payload] = None
                self._state.move_to_end(payload)
                while len(self._state) > self.width:
                    if self.policy == "fifo":
                        self._state.popitem(last=False)   # evict oldest
                    else:
                        # LIFO keeps the oldest facts, evicts the most recent arrival
                        self._state.popitem(last=True)
            elif kind == "query_cancel":
                # Conservative: cancel only on a RETAINED fact. Unsound guessing is a
                # different (worse) circuit; incompleteness is the honest failure.
                answers.append(payload in self._state)
        return answers


def disequality_family(n: int, noise_every: int = 3) -> List[Event]:
    """The separating probe family: n declarations, interleaved noise, no queries yet."""
    events: List[Event] = []
    for i in range(1, n + 1):
        events.append(("declare_nonzero", f"x{i}"))
        if i % noise_every == 0:
            events.append(("noise", f"transform_{i}"))
    return events


def adversarial_query(circuit_width: int, n: int, policy: str) -> Event:
    """The adversary knows the policy (kill tests are white-box): query a fact the bounded
    circuit provably evicted. FIFO evicts early facts -> query x1; LIFO evicts late -> x_n."""
    assert n > circuit_width
    return ("query_cancel", "x1" if policy == "fifo" else f"x{n}")


# --------------------------------------------------------------------------- cycle 006 fold-in

def lexicographic_score(answers, gold, abstain=None):
    """ChatGPT round-2 scoring contract: (soundness_violations, -coverage), minimized
    LEXICOGRAPHICALLY. No penalty constants: one fabricated fact disqualifies a liar from
    competing on coverage at all — (0, -0.20) < (1, -0.99), always.

    `answers[i]` is True/False/abstain; gold[i] is True/False. A soundness violation is a
    non-abstaining WRONG answer; coverage is the fraction answered (rightly or not is the
    soundness axis's business)."""
    violations = sum(1 for a, g in zip(answers, gold) if a is not abstain and a != g)
    coverage = sum(1 for a in answers if a is not abstain) / max(len(answers), 1)
    return (violations, -coverage)


def indistinguishable_twins(width: int, policy: str = "fifo"):
    """The round-2 kill battery: two histories that leave IDENTICAL bounded state S, but the
    queried proposition differs. H_T declares xq!=0 early (then floods the window); H_F never
    declares it (same flood). Any deterministic circuit answering from S alone is wrong on
    one twin; abstention is sound on both.

    Returns (events_T, events_F, query) with n = width+1 declarations in H_T so xq is
    provably evicted under FIFO."""
    flood = [("declare_nonzero", f"f{i}") for i in range(1, width + 1)]
    h_t = [("declare_nonzero", "xq")] + flood
    h_f = list(flood)
    return h_t, h_f, ("query_cancel", "xq")
