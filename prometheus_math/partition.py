"""Partition comparison — refinement, and the information distance between partitions.

Motivated directly by the cycle-022 instrument sweep. Every projection `π` used by the aliasing
machinery induces a partition of the instance set (its fibres), and the questions the sweep asks
are partition questions:

- *Does one evaluator's view factor through another's?* — is one partition a REFINEMENT of the
  other. `verify_factorization` was checking this pairwise and ad hoc; `refines` states it.
- *How far apart are two views?* — a distance between partitions, so that "these two evaluators
  see almost the same thing" is a measurement rather than an impression.

Reference for the distance: M. Meilă, *"Comparing clusterings — an information based distance"*,
Journal of Multivariate Analysis 98 (2007), 873–895. Variation of information

    VI(P, Q) = H(P) + H(Q) − 2·I(P, Q)

is a true metric on the lattice of partitions, which matters here: a non-metric similarity would
let "close" fail to compose across a chain of evaluators.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, FrozenSet, Hashable, List, Sequence, Tuple

__all__ = ["induced_partition", "refines", "entropy", "mutual_information",
           "variation_of_information", "PartitionError"]

Partition = Tuple[FrozenSet[int], ...]


class PartitionError(ValueError):
    """Raised when the inputs are not partitions of a common ground set."""


def _validate(p: Partition, n: int, name: str = "partition") -> None:
    if n <= 0:
        raise PartitionError("the empty ground set has no partition information")
    seen: set = set()
    for block in p:
        if not block:
            raise PartitionError(f"{name} contains an empty block")
        if seen & block:
            raise PartitionError(f"{name} blocks overlap at {sorted(seen & block)}")
        seen |= set(block)
    if seen != set(range(n)):
        raise PartitionError(f"{name} does not cover exactly 0..{n - 1}")


def induced_partition(items: Sequence, key: Callable[[object], Hashable]) -> Partition:
    """The fibres of `key` over `items`, as blocks of INDICES.

    Index-based rather than value-based so that unhashable or duplicate items are handled, and
    so that two different keys over the same item list produce partitions of the same ground
    set — which is what makes them comparable at all.
    """
    buckets: Dict[Hashable, List[int]] = {}
    for i, item in enumerate(items):
        buckets.setdefault(key(item), []).append(i)
    return tuple(frozenset(v) for v in buckets.values())


def refines(fine: Partition, coarse: Partition, n: int) -> bool:
    """Is every block of `fine` contained in some block of `coarse`?

    This is exactly the factorization precondition the aliasing argument needs: an evaluator
    whose view induces `coarse` sees a function of the view that induces `fine`, so a witness
    under `fine` binds it. Note the direction — the FINER partition is the one that sees more.
    """
    _validate(fine, n, "fine")
    _validate(coarse, n, "coarse")
    for fb in fine:
        if not any(fb <= cb for cb in coarse):
            return False
    return True


def entropy(p: Partition, n: int) -> float:
    """H(P) in bits, treating the ground set as uniform."""
    _validate(p, n)
    h = 0.0
    for block in p:
        q = len(block) / n
        h -= q * math.log2(q)
    return h


def mutual_information(p: Partition, q: Partition, n: int) -> float:
    """I(P, Q) in bits."""
    _validate(p, n, "p")
    _validate(q, n, "q")
    mi = 0.0
    for pb in p:
        for qb in q:
            inter = len(pb & qb)
            if inter == 0:
                continue
            joint = inter / n
            mi += joint * math.log2(joint / ((len(pb) / n) * (len(qb) / n)))
    return mi


def variation_of_information(p: Partition, q: Partition, n: int) -> float:
    """VI(P, Q) = H(P) + H(Q) − 2·I(P, Q). A metric on partitions (Meilă 2007).

    Zero exactly when the two partitions are equal, so "these evaluators see the same thing"
    becomes a checkable statement rather than a claim.
    """
    return entropy(p, n) + entropy(q, n) - 2.0 * mutual_information(p, q, n)
