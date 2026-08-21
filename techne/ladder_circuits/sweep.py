"""Second-pass instrument sweep — and the DUAL instrument the sweep turned up. (Cycle 022.)

The first pass built R0–R12 and, from cycle 018, three standing instruments: aliasing, evidence
typing, external audit. The instruments arrived at cycle 018, so R0–R5 and R7–R8 were built
before they existed and have never been through them. This module is the sweep harness.

**Sweeping R0 found a limit in the aliasing instrument itself, which is worth more than another
confirmation.** Aliasing detects exactly one of the two ways a projection can be wrong:

- **Under-discrimination (merging).** `π(x₁) = π(x₂)` with `T(x₁) ≠ T(x₂)`. An IMPOSSIBILITY:
  no evaluator factoring through π is correct on both. This is what `find_aliasing_witness`
  finds, and it is what every rung swept so far has yielded.

- **Over-discrimination (splitting).** `π(x₁) ≠ π(x₂)` with `T(x₁) = T(x₂)`. **NOT** an
  impossibility — an evaluator can still be correct on both by treating them separately. What
  it costs is generalisation: evidence about one instance does not transfer to the other, so
  the family needs strictly more training or more cases to reach the same coverage.

R0's actual defect is the second kind — exact-AST retrieval splits renamed variants that share
an answer — and the aliasing instrument is silent on it. `find_splitting_witness` is the dual,
and it is labelled throughout with what it does and does not prove, because the temptation to
report it as if it were an impossibility is exactly the evidence-typing error of claim v12.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any, Callable, Dict, Hashable, List, Optional, Sequence, Tuple

from techne.ladder_circuits.aliasing import (
    AliasingWitness, all_aliasing_witnesses, find_aliasing_witness, verify_factorization,
)

__all__ = ["SplittingWitness", "find_splitting_witness", "all_splitting_witnesses",
           "SweepReport", "sweep_projection", "twins_for_policy"]


@dataclass(frozen=True)
class SplittingWitness:
    """Two instances the evaluator separates although their truths agree.

    **This is not an impossibility result.** An evaluator that distinguishes them can still be
    correct on both — it simply cannot carry evidence from one to the other. Read it as a
    generalisation cost, never as a proof of incapacity.
    """

    left: Any
    right: Any
    left_projection: Hashable
    right_projection: Hashable
    shared_truth: Any
    note: str = ""

    proves_impossibility: bool = False        # stated in the data, not only in the prose


def find_splitting_witness(
    instances: Sequence[Any],
    projection: Callable[[Any], Hashable],
    truth: Callable[[Any], Any],
    note: str = "",
) -> Optional[SplittingWitness]:
    """Dual of `find_aliasing_witness`: equal truths, different projections."""
    for a, b in combinations(instances, 2):
        if projection(a) != projection(b) and truth(a) == truth(b):
            return SplittingWitness(a, b, projection(a), projection(b), truth(a), note)
    return None


def all_splitting_witnesses(
    instances: Sequence[Any],
    projection: Callable[[Any], Hashable],
    truth: Callable[[Any], Any],
) -> List[SplittingWitness]:
    return [SplittingWitness(a, b, projection(a), projection(b), truth(a))
            for a, b in combinations(instances, 2)
            if projection(a) != projection(b) and truth(a) == truth(b)]


@dataclass
class SweepReport:
    """What the sweep found for one rung's projection, in both directions."""

    rung: str
    n_instances: int
    aliasing: Optional[AliasingWitness]
    splitting: Optional[SplittingWitness]
    n_aliased_pairs: int
    n_split_pairs: int

    @property
    def incapacity_proved(self) -> bool:
        """Only under-discrimination proves anything about the whole family."""
        return self.aliasing is not None

    @property
    def verdict(self) -> str:
        if self.aliasing is not None:
            return "ALIASED — no member of the family is correct on both"
        if self.splitting is not None:
            return "SPLIT — family can be correct, but evidence does not transfer"
        return "SUFFICIENT on this instance set (evidence, not proof)"


def sweep_projection(rung: str, instances: Sequence[Any],
                     projection: Callable[[Any], Hashable],
                     truth: Callable[[Any], Any]) -> SweepReport:
    """Run both instruments over one rung's projection and report both directions."""
    return SweepReport(
        rung=rung,
        n_instances=len(instances),
        aliasing=find_aliasing_witness(instances, projection, truth),
        splitting=find_splitting_witness(instances, projection, truth),
        n_aliased_pairs=len(all_aliasing_witnesses(instances, projection, truth)),
        n_split_pairs=len(all_splitting_witnesses(instances, projection, truth)),
    )


# --------------------------------------------------------------------------------------------
# R3 (canon R2, constraint tracking) — resolving the ledger's outstanding unverified claim.

def twins_for_policy(width: int, policy: str = "fifo"):
    """Indistinguishable-state twins built for a SPECIFIC eviction policy.

    Cycle 006's `indistinguishable_twins` floods the window after declaring `xq`, which evicts
    `xq` under FIFO — and RETAINS it under LIFO, because LIFO evicts the most recent arrival.
    So that pair aliases the FIFO pipelines and does not alias the LIFO ones, and the ledger's
    unqualified "R3 capacity width" aliasing claim was too broad.

    The fix is not a cleverer pair. It is that FIFO and LIFO views are INCOMPARABLE — neither
    factors through the other — so incapacity must be proved per observation class, exactly as
    the cycle-019 precondition says. This builds the right pair for each class.
    """
    flood = [("declare_nonzero", f"f{i}") for i in range(1, width + 1)]
    if policy == "fifo":
        # declare first, then flood it out of the window
        h_t = [("declare_nonzero", "xq")] + flood
    else:
        # LIFO keeps the OLDEST facts, so xq must arrive LAST to be the one evicted
        h_t = flood + [("declare_nonzero", "xq")]
    h_f = list(flood)
    return h_t, h_f, ("query_cancel", "xq")
