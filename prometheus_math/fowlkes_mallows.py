"""FOWLKES-MALLOWS INDEX — pair precision and recall, geometric mean, NOT chance-corrected.

Reference: Fowlkes, E. B. & Mallows, C. L. (1983). "A Method for Comparing Two Hierarchical
Clusterings." Journal of the American Statistical Association 78(383):553-569.

    FM = TP / sqrt((TP + FP)(TP + FN))

over co-clustered PAIRS: `TP` is pairs together in both partitions, `TP + FP` pairs together in
the projection, `TP + FN` pairs together in the truth. Equivalently `sqrt(precision * recall)`.

Fourth member of the comparison family, and deliberately the one that is **not** chance-corrected:

    normalized_vi   (041)  metric, log n                      distance   [0, 1]
    normalized_mi   (042)  information-theoretic              similarity [0, 1]
    adjusted_rand   (043)  pair-counting, chance-corrected    similarity (-, 1]
    fowlkes_mallows (044)  pair-counting, NOT corrected       similarity [0, 1]

Having ARI and FM side by side is what isolates what chance correction buys: on a below-chance
pairing ARI goes negative while FM stays positive. Code that treats them as interchangeable
silently loses the "worse than chance" signal, and a test constructs that case explicitly.

**Where it refuses.** When either partition is all singletons it contributes zero co-clustered
pairs, so a factor of the denominator is exactly zero and FM is `0/0`. Returning `0.0` there would
be indistinguishable from a genuine "these two clusterings share no pair" — which is a real,
different, and perfectly well-defined situation. Both cases are tested, and only the first raises.
"""
from __future__ import annotations

import math

from prometheus_math.partition import Partition, PartitionError, _validate

__all__ = ["FOWLKES_MALLOWS_1983", "fowlkes_mallows"]

FOWLKES_MALLOWS_1983 = (
    "Fowlkes, E. B. & Mallows, C. L. (1983). A Method for Comparing Two Hierarchical "
    "Clusterings. Journal of the American Statistical Association, 78(383), 553-569.")


def fowlkes_mallows(projection: Partition, truth: Partition, n: int) -> float:
    """`TP / sqrt((TP+FP)(TP+FN))` over co-clustered pairs. 1.0 on identity, 0.0 on no shared pair.

    Raises `PartitionError` when `n < 2`, when either argument is not a partition of `n`, or when
    either side has no co-clustered pairs at all (all singletons), which makes the value 0/0.
    """
    from math import comb

    if n < 2:
        raise PartitionError(
            f"fowlkes_mallows needs at least two elements to have any pairs; got n={n}. "
            "Returning 0.0 would report 'these clusterings share no pair' when no pair exists "
            "to be shared")
    _validate(projection, n, "projection")
    _validate(truth, n, "truth")

    tp = sum(comb(len(bx & by), 2) for bx in projection for by in truth)
    tp_fp = sum(comb(len(bx), 2) for bx in projection)
    tp_fn = sum(comb(len(by), 2) for by in truth)

    degenerate = [name for name, v in (("projection", tp_fp), ("truth", tp_fn)) if v == 0]
    if degenerate:
        raise PartitionError(
            f"fowlkes_mallows is undefined: {' and '.join(degenerate)} has no co-clustered pairs "
            "(it is all singletons), so a factor of the denominator is exactly 0 and the value "
            "would be 0/0. Returning 0.0 would be indistinguishable from the genuine case where "
            "both sides have pairs and share none — which is well-defined and does not raise. "
            "Use adjusted_rand or variation_of_information if you need a number here.")

    return tp / math.sqrt(tp_fp * tp_fn)
