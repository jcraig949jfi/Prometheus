"""ADJUSTED RAND INDEX — pair-counting agreement, corrected for chance.

Reference: Hubert, L. & Arabie, P. (1985). "Comparing partitions." Journal of Classification
2(1):193-218 — the chance-corrected form of Rand (1971).

    ARI = (index - expected) / (max - expected)

where `index = sum_ij C(n_ij, 2)` over the contingency table, `expected = sum_a * sum_b / C(n,2)`,
and `max = (sum_a + sum_b) / 2`.

This completes a trio built over three cycles, and the point of having all three is that they
disagree in useful ways:

    normalized_vi   (cycle 041)  a true METRIC, log n normalisation, distance in [0, 1]
    normalized_mi   (cycle 042)  information-theoretic SIMILARITY, sqrt(H H) normalisation
    adjusted_rand   (cycle 043)  PAIR-COUNTING similarity, chance-corrected, CAN GO NEGATIVE

**The negative range is the feature, not an artefact.** A pairing that agrees less often than
chance scores below zero, and clamping that to zero would erase the difference between "no better
than chance" and "actively anti-correlated". A test constructs a below-chance pairing explicitly
so the case cannot quietly stop being exercised.

**Where it refuses.** When both partitions are trivial in the same way — both a single block, or
both all singletons — `index == expected == max` and the ratio is `0/0`. This family of indices is
notorious for it. Returning `1.0` is the seductive wrong answer here, because the two partitions
genuinely ARE identical; it is still wrong, since the number would come from dividing by zero
rather than from measuring agreement. The refusal names the situation so a caller can choose a
different index — `variation_of_information` stays defined on exactly these inputs.
"""
from __future__ import annotations

from math import comb

from prometheus_math.partition import Partition, PartitionError, _validate

__all__ = ["HUBERT_ARABIE_1985", "adjusted_rand"]

HUBERT_ARABIE_1985 = ("Hubert, L. & Arabie, P. (1985). Comparing partitions. "
                      "Journal of Classification, 2(1), 193-218.")


def adjusted_rand(projection: Partition, truth: Partition, n: int) -> float:
    """Chance-corrected pair-counting agreement. 1.0 on identity, ~0 at chance, negative below it.

    Raises `PartitionError` when `n < 2` (no pairs exist), when either argument is not a partition
    of `n`, or when the correction denominator vanishes.
    """
    if n < 2:
        raise PartitionError(
            f"adjusted_rand needs at least two elements to have any pairs to count; got n={n}, "
            f"and C({n},2) = 0. Returning 0.0 would report 'agreement no better than chance' "
            "when no pair was examined")
    _validate(projection, n, "projection")
    _validate(truth, n, "truth")

    total_pairs = comb(n, 2)
    index = sum(comb(len(bx & by), 2) for bx in projection for by in truth)
    sum_a = sum(comb(len(bx), 2) for bx in projection)
    sum_b = sum(comb(len(by), 2) for by in truth)
    expected = sum_a * sum_b / total_pairs
    maximum = (sum_a + sum_b) / 2

    denominator = maximum - expected
    if abs(denominator) < 1e-15:
        raise PartitionError(
            "adjusted_rand is degenerate here: max == expected, so the value would be 0/0. This "
            "happens when both partitions are trivial in the same way — both a single block, or "
            "both all singletons — and every pair therefore agrees by construction. Returning "
            "1.0 is tempting because the partitions ARE identical, but the number would come "
            "from dividing by zero rather than from measuring agreement. Use "
            "variation_of_information, which stays defined on these inputs.")

    return (index - expected) / denominator
