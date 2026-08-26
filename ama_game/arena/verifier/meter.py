#!/usr/bin/env python3
"""Metered verifier: the harness owns every chargeable evaluation.

Why this exists. In the v0.1 A0 run the search budget lived in a prompt and
nothing enforced it. Seats enumerated to 579,714 against a 200,000 cap and said
so in their own records. Verifier-call counts were self-reported, and the seats
openly disagreed about what counted — several re-ran an identical script purely
to persist a log and charged themselves for it, several ran a JSON parse check
and did not. A self-reported number is not an instrument.

## Chargeability is defined at the interface

A call is chargeable because it **requests information about the target claim**,
not because it happened to execute code. Parsing JSON is free. Asking whether
the proposition holds at n = 4 is not. This removes the judgement call the v1
seats were forced to make and disagreed on, and it is checkable: see the taint
invariant below.

## The precondition this design depends on, stated plainly

Metering binds only if a seat cannot obtain the same information locally. If the
claim is fully public and cheap to reimplement, a seat can ignore the meter
entirely and the cap is decorative again — the exact failure this module exists
to fix.

So a metered claim must carry a **sealed component**: a function, coefficient
set, or membership predicate the seat can reach only through this API. The
generator has to supply that. A claim without one can still be served here, and
its meter reading will be honest about what it observed, but the budget will not
bind and `binding=False` is recorded on the session so no analysis can quietly
treat it as if it did.

## The taint invariant

Every evaluation of the sealed predicate increments an internal counter that no
caller can reach. Every chargeable operation records what it spent. After any
sequence of operations these two must be equal. If they diverge, some path
touched the claim without paying, which is the one bug class that would silently
invalidate every cost number the arena produces.

`selftest.py` asserts this over randomised operation sequences.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent
sys.path.insert(0, str(ARENA / "generator"))

from exprlang import evaluate as _raw_evaluate  # noqa: E402


class BudgetExhausted(Exception):
    """Raised when a chargeable call would exceed the cap. The call does not run."""


@dataclass
class Ledger:
    entries: list[dict] = field(default_factory=list)

    def record(self, op: str, cost: int, detail: dict) -> None:
        self.entries.append({"seq": len(self.entries), "op": op, "cost": cost,
                             **detail})

    @property
    def spent(self) -> int:
        return sum(e["cost"] for e in self.entries)


class Session:
    """One seat's metered access to one claim.

    Everything a seat can call is a method here. Nothing else reaches the sealed
    predicate. `remaining()` and `refusals()` are free by design: a seat is
    allowed to know how much rope it has left, and hiding that would make
    abstention a guessing game rather than a decision.
    """

    def __init__(self, meter: "Meter", claim_id: str, seat: str, budget: int,
                 binding: bool):
        self._meter = meter
        self.claim_id = claim_id
        self.seat = seat
        self.budget = budget
        self.binding = binding
        self.ledger = Ledger()
        self.refused = 0

    # --- free: no information about the claim crosses this boundary --------

    def remaining(self) -> int:
        return max(0, self.budget - self.ledger.spent)

    def refusals(self) -> int:
        return self.refused

    def statement(self) -> dict:
        """The public statement. Free, and already in the seat's prompt."""
        return self._meter.public(self.claim_id)

    # --- chargeable -------------------------------------------------------

    def _charge(self, op: str, cost: int, detail: dict) -> None:
        if cost <= 0:
            raise ValueError(f"{op} must cost at least 1")
        if self.ledger.spent + cost > self.budget:
            self.refused += 1
            raise BudgetExhausted(
                f"{op} would cost {cost}; {self.remaining()} credits remain. "
                "The call did not run and returned nothing about the claim.")
        self.ledger.record(op, cost, detail)

    def evaluate(self, point: int) -> bool:
        """Does the proposition hold at this point? Cost 1."""
        self._charge("evaluate", 1, {"point": point})
        return self._meter._sealed_eval(self.claim_id, point)

    def evaluate_range(self, lo: int, hi: int) -> dict:
        """Sweep a range. Cost is the FULL requested width, no refund.

        The first version refunded points beyond an early failure, on the
        reasoning that cost should track work done rather than how a question
        was phrased. The selftest showed that reasoning destroys the experiment.

        With a refund, requesting the entire affordable domain costs only up to
        the first failure, so "scan everything" is never worse than any targeted
        strategy and there is no incentive to navigate. The whole point of the
        arena is to measure whether accumulated structure helps a seat choose a
        cheaper probe; a refund makes that choice free.

        So the width you ask for is the width you pay for. Choosing a range is a
        decision with a price, which is what the navigation experiment measures.
        A seat wanting adaptivity should step with `evaluate`, paying one credit
        per probe and stopping when it likes — that route stays available and
        costs exactly the number of probes taken.
        """
        if hi < lo:
            raise ValueError("empty range")
        cost = hi - lo + 1
        # charged before running, and refused whole rather than part-way: a
        # sweep that died mid-flight would let a seat locate the cap by watching
        # where it stopped, leaking budget state on every refused call
        self._charge("evaluate_range", cost, {"lo": lo, "hi": hi})
        first = None
        for n in range(lo, hi + 1):
            if not self._meter._sealed_eval(self.claim_id, n):
                first = n
                break
        return {"first_failure": first, "points_paid": cost}

    def symbolic_check(self, relation: str) -> bool:
        """Ask whether a stated relation holds identically on the domain.

        Cost is flat and small: this is the operation the navigation experiment
        wants seats to discover, so it must be cheap enough to be worth finding
        and expensive enough not to be free.
        """
        self._charge("symbolic_check", self._meter.symbolic_cost,
                     {"relation": relation})
        return self._meter._sealed_symbolic(self.claim_id, relation)

    def report(self) -> dict:
        return {"claim_id": self.claim_id, "seat": self.seat,
                "budget": self.budget, "binding": self.binding,
                "spent": self.ledger.spent, "remaining": self.remaining(),
                "refusals": self.refused, "ledger": self.ledger.entries}


class Meter:
    """Holds the sealed claims and serves metered sessions against them."""

    def __init__(self, sealed_dir: Path, budget: int, symbolic_cost: int = 3):
        self.sealed_dir = Path(sealed_dir)
        self.budget = budget
        self.symbolic_cost = symbolic_cost
        self._claims: dict[str, dict] = {}
        # Taint counters. No public method exposes them; the selftest reaches in
        # deliberately. Point evaluations and symbolic sampling are counted
        # SEPARATELY: symbolic_check charges a flat fee while sampling several
        # points under the hood, and folding both into one counter would make
        # the invariant inexact -- which is precisely where a metering bug would
        # hide. Two exact invariants beat one approximate one.
        self._oracle_evaluations = 0        # point evaluations, charged 1:1
        self._symbolic_evaluations = 0      # sampling inside symbolic_check
        self._symbolic_calls = 0

    def load(self, claim_id: str) -> dict:
        if claim_id not in self._claims:
            p = self.sealed_dir / f"{claim_id}.json"
            self._claims[claim_id] = json.loads(p.read_text(encoding="utf-8"))
        return self._claims[claim_id]

    def public(self, claim_id: str) -> dict:
        c = self.load(claim_id)
        return {"claim_id": claim_id, "domain_lo": c["domain_lo"],
                "domain_hi": c["domain_hi"], "var": c["witness_var"],
                # public metadata the generator chose to disclose. Free: it is
                # already in the seat's prompt, and charging for re-reading the
                # statement would make cost depend on note-taking.
                "shape": c.get("shape")}

    def open(self, claim_id: str, seat: str) -> Session:
        c = self.load(claim_id)
        binding = bool(c.get("sealed_component", False))
        return Session(self, claim_id, seat, self.budget, binding)

    # --- the only paths that touch the claim ------------------------------

    def _sealed_eval(self, claim_id: str, point: int) -> bool:
        c = self.load(claim_id)
        self._oracle_evaluations += 1
        lo, hi = c["domain_lo"], c["domain_hi"]
        if not (lo <= point <= hi):
            return True          # outside the quantified domain: vacuous
        return bool(_raw_evaluate(c["claim_predicate"], {c["witness_var"]: point}))

    def _sealed_symbolic(self, claim_id: str, relation: str) -> bool:
        """A symbolic question, answered by sampling under the hood.

        Charged flat, so the seat pays for the QUESTION rather than for however
        many points the harness needed. Its sampling is counted on a separate
        taint counter so the point-evaluation invariant stays exact.
        """
        c = self.load(claim_id)
        lo, hi = c["domain_lo"], c["domain_hi"]
        self._symbolic_calls += 1
        pts = sorted({lo, lo + 1, (lo + hi) // 2, hi - 1, hi})
        for n in pts:
            if not (lo <= n <= hi):
                continue
            self._symbolic_evaluations += 1
            try:
                if not bool(_raw_evaluate(relation, {c["witness_var"]: n})):
                    return False
            except Exception:
                return False
        return True
