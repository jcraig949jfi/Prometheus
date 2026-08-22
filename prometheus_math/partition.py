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
           "variation_of_information", "conditional_entropy", "is_refinement_chain",
           "information_profile", "normalized_deficit", "chain_direction",
           "refinement_multiplicity", "within_class_loss", "PartitionError"]

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


def conditional_entropy(p: Partition, q: Partition, n: int) -> float:
    """H(P | Q) in bits — what P still distinguishes once Q is known.

    Zero exactly when Q refines P, which is the identity that makes the sweep's two directions
    one measurement (cycle 023):

        H(T | P) > 0  <=>  P does not refine T  <=>  an ALIASING witness exists
        H(P | T) > 0  <=>  T does not refine P  <=>  a SPLITTING witness exists
        VI(P, T) = H(T | P) + H(P | T)

    So a projection is exactly sufficient AND exactly necessary iff VI = 0, and the two failure
    directions are the two halves of that single number.
    """
    return entropy(p, n) - mutual_information(p, q, n)


def is_refinement_chain(chain: Sequence[Partition], n: int) -> bool:
    """Is each partition coarsened by its successor — `chain[k]` refines `chain[k+1]`?

    Any pipeline induces one automatically: if stage k+1 sees only stage k's output, its fibres
    are unions of stage k's fibres. A chain that FAILS this test is not a pipeline — some stage
    is reading something its predecessor did not hand it.
    """
    return all(refines(chain[k], chain[k + 1], n) for k in range(len(chain) - 1))


def information_profile(chain: Sequence[Partition], truth: Partition,
                        n: int) -> List[Tuple[float, float]]:
    """Per-stage `(deficit, excess)` = `(H(T | P_k), H(P_k | T))` along a pipeline.

    On a refinement chain the data-processing inequality (Cover & Thomas, *Elements of
    Information Theory* 2nd ed., Thm 2.8.1) forces the two columns in OPPOSITE directions:

        deficit is non-DECREASING   — information about the truth can only be lost
        excess  is non-INCREASING   — surplus distinctions can only be discarded

    So a pipeline can only lose. The question a chain poses is never "did it lose something" but
    "was what it lost excess (free) or deficit (fatal)", and the first stage where deficit rises
    above zero is the seam where the chain broke.
    """
    return [(conditional_entropy(truth, p, n), conditional_entropy(p, truth, n))
            for p in chain]


def normalized_deficit(truth: Partition, projection: Partition, n: int) -> float:
    """`H(T | P) / H(T)` — the FRACTION of the target's information the projection has lost.

    Bits are not comparable across batteries with different target entropies: 4.585 bits of
    deficit is total loss over 24 equiprobable tasks and a rounding error over a million. This
    normalises to [0, 1], where 0 is sufficient and 1 is "the projection says nothing at all
    about the target".

    Undefined when the target is constant (H(T) = 0): there is nothing to lose, and reporting 0
    would claim a sufficiency the battery never tested. Raises instead.
    """
    h_t = entropy(truth, n)
    if h_t <= 0.0:
        raise PartitionError(
            "the target is constant on this battery, so normalized deficit is undefined; "
            "a battery with no target variation cannot test sufficiency")
    return conditional_entropy(truth, projection, n) / h_t


def chain_direction(chain: Sequence[Partition], n: int) -> str:
    """Which way does a pipeline's information flow — "DESTROYING", "ACCUMULATING", "NEITHER"?

    Cycle 024 built `information_profile` for TRANSFORM pipelines, where stage k+1 sees only
    stage k's output; those coarsen forward, deficit rises and excess falls. Cycle 027 measured a
    falsification battery, where each stage ADDS a verdict bit and discards nothing; those refine
    forward and every monotonicity runs backwards.

    Reading a profile without checking the direction first is how a healthy accumulating chain
    gets flagged as broken, so this exists to be called before the profile is interpreted.
    "NEITHER" means consecutive stages are incomparable and no chain argument is available at all.
    """
    if is_refinement_chain(chain, n):
        return "DESTROYING"
    if is_refinement_chain(list(reversed(chain)), n):
        return "ACCUMULATING"
    return "NEITHER"


def refinement_multiplicity(projection: Partition, truth: Partition, n: int) -> int:
    """WORST-CASE fragmentation: the largest number of projection cells inside one truth cell.

    External review, round 8, on why `H(P | T)` alone is not enough: **the excess bits are
    distribution-dependent, so a massive refinement in a rare corner looks cheap.** A projection
    that shatters one rare truth class into a hundred pieces and leaves the common classes intact
    barely moves the average, and this number reports it immediately.

    Bits tell you average fragmentation; multiplicity tells you worst-case. Keep both.

    Note where this sits in the cycle-031 2x2: it is a MAX OF COUNTS, so it is monotone up under
    domain growth — an EXISTENTIAL-kind claim — whereas `H(P | T)` is normalised and therefore
    AGGREGATE. The reviewer's "keep both" is exactly "keep one monotone measure and one
    normalised one", which is a pleasing convergence between two independent lines.
    """
    _validate(projection, n, "projection")
    _validate(truth, n, "truth")
    if not refines(projection, truth, n):
        raise PartitionError(
            "refinement_multiplicity presupposes that the projection REFINES the truth; this "
            "projection merges truth distinctions instead, so there is no fragmentation to "
            "measure. Returning 0 here would read as 'perfectly efficient' when the projection "
            "is in fact losing information — use conditional_entropy(truth, projection) for "
            "that direction. (Fourth instance of the answering-outside-your-domain bug class: "
            "structural_constancy c029, find_aliasing_witness and fiber_search c037, this c038.)")
    worst = 0
    for cell in truth:
        inside = sum(1 for d in projection if d <= cell)
        worst = max(worst, inside)
    return worst


def within_class_loss(projection: Partition, target: Partition, n: int) -> float:
    """`H(target | projection)` — but named for the use round 8 identified.

    Merge/split exhaust CLASSIFICATION ERROR against a fixed target. They do not exhaust
    REPRESENTATION ADEQUACY, because a projection can induce exactly the truth partition —
    no merge, no split, VI zero — and still have destroyed everything a LATER task needs.

    Measured on the integers 2..41: the primality projection is perfect for "is it prime"
    (VI = 0.0000) and loses 1.9567 bits against "what is the smallest factor". Same projection,
    same inputs, a different question.

    So the merge/split theorem is scoped to a FIXED target, and adequacy is quantified over
    future targets — a different quantifier, which is why no amount of care about the first
    target detects it.
    """
    return conditional_entropy(target, projection, n)
