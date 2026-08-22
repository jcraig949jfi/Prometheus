"""MIRKIN METRIC — the unnormalised pair-counting distance between partitions.

Reference: Mirkin, B. G. (1996). "Mathematical Classification and Clustering." Kluwer, ch. 5;
originally Mirkin & Chernyi (1970).

    M(X, Y) = sum_i a_i^2 + sum_j b_j^2 - 2 * sum_ij n_ij^2

where `a_i` are the block sizes of X, `b_j` those of Y, and `n_ij` the contingency counts. It
equals twice the number of disagreeing pairs, so `0 <= M <= 2*C(n,2)`.

**Why it belongs next to `rand_index`.** RI is a similarity in [0,1] with no triangle inequality;
M is a true metric. Code that treats `1 - RI` as a distance can violate the triangle inequality
without warning, and having the real metric available means nobody has to. The two are related
exactly by

    M = 2 * C(n,2) * (1 - RI)

which is asserted against `rand_index` rather than assumed.

**Its domain is wider than the normalised family's, and that is the point of the edge test.** At
`n = 1` there are no pairs, so nothing can disagree and `M = 0` — a genuine value. The normalised
indices all refuse there: `normalized_vi` because `log2(1) = 0`, `adjusted_rand` because
`C(1,2) = 0`, `fowlkes_mallows` because neither side has a co-clustered pair. A raw count has no
denominator to vanish. This is the third cycle in which the comparison family has turned out not
to share a domain, so a test pins all four on the same input.
"""
from __future__ import annotations

from prometheus_math.partition import Partition, PartitionError, _validate

__all__ = ["MIRKIN_1996", "mirkin_distance"]

MIRKIN_1996 = ("Mirkin, B. G. (1996). Mathematical Classification and Clustering. Kluwer, "
               "chapter 5; originally Mirkin & Chernyi (1970).")


def mirkin_distance(projection: Partition, truth: Partition, n: int) -> float:
    """`sum a_i^2 + sum b_j^2 - 2 sum n_ij^2` — twice the count of disagreeing pairs.

    A true metric: non-negative, symmetric, zero exactly on identity, and satisfying the triangle
    inequality (all four checked as Hypothesis properties rather than assumed).

    Raises `PartitionError` when `n < 1` or when either argument is not a partition of `n`.
    `n = 1` is DEFINED and returns 0.0 — there are no pairs to disagree.
    """
    if n < 1:
        raise PartitionError(
            f"mirkin_distance needs a non-empty ground set; got n={n}. Returning 0.0 would report "
            "'these two clusterings agree on every pair' over a set with no elements and no pairs")
    _validate(projection, n, "projection")
    _validate(truth, n, "truth")

    sum_a2 = sum(len(bx) ** 2 for bx in projection)
    sum_b2 = sum(len(by) ** 2 for by in truth)
    sum_n2 = sum(len(bx & by) ** 2 for bx in projection for by in truth)
    return float(sum_a2 + sum_b2 - 2 * sum_n2)
