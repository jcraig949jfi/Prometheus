"""RAND INDEX — the uncorrected proportion of agreeing pairs.

Reference: Rand, W. M. (1971). "Objective Criteria for the Evaluation of Clustering Methods."
Journal of the American Statistical Association 66(336):846-850.

    RI = (a + d) / C(n, 2)

`a` = pairs together in both partitions, `d` = pairs separated in both.

Kept alongside cycle 043's `adjusted_rand` because the pair is what makes chance correction
legible. Hubert & Arabie's motivation was that RI is INFLATED — dominated by the `d` term once
there are several blocks, so it does not approach 0 for unrelated clusterings. A test demonstrates
that directly: on a below-chance pairing RI stays above 0.5 while ARI goes negative. A caller
reading RI as "fraction correct" will call an anti-correlated projection a good one.

**A domain difference worth knowing.** On two all-singleton partitions every pair is apart in both,
so `a = 0`, `d = C(n,2)`, and RI = 1 exactly — well-defined and correct. `adjusted_rand` and
`fowlkes_mallows` are both 0/0 on that same input and refuse. The family does not share a domain,
and a test pins all three together so nobody assumes it does.
"""
from __future__ import annotations

from math import comb

from prometheus_math.partition import Partition, PartitionError, _validate

__all__ = ["RAND_1971", "rand_index"]

RAND_1971 = ("Rand, W. M. (1971). Objective Criteria for the Evaluation of Clustering Methods. "
             "Journal of the American Statistical Association, 66(336), 846-850.")


def rand_index(projection: Partition, truth: Partition, n: int) -> float:
    """`(a + d) / C(n, 2)` — agreeing pairs over all pairs. 1.0 on identity.

    Raises `PartitionError` when `n < 2` (no pairs exist, so the denominator is 0) or when either
    argument is not a partition of `n`.
    """
    if n < 2:
        raise PartitionError(
            f"rand_index needs at least two elements to have any pairs; got n={n}, so C({n},2)=0 "
            "and the value would be 0/0. Returning 1.0 would report perfect agreement over a "
            "comparison that never happened")
    _validate(projection, n, "projection")
    _validate(truth, n, "truth")

    total = comb(n, 2)
    a = sum(comb(len(bx & by), 2) for bx in projection for by in truth)
    together_x = sum(comb(len(bx), 2) for bx in projection)
    together_y = sum(comb(len(by), 2) for by in truth)
    d = total - together_x - together_y + a
    return (a + d) / total
