"""NORMALIZED MUTUAL INFORMATION — agreement between two clusterings, on a fixed scale.

Reference: Strehl, A. & Ghosh, J. (2002). "Cluster Ensembles — A Knowledge Reuse Framework for
Combining Multiple Partitions." Journal of Machine Learning Research 3:583-617.

    NMI(X, Y) = I(X; Y) / sqrt(H(X) H(Y))

A SIMILARITY in [0, 1], maximal exactly on identity. Cycle 041 built normalized variation of
information, which is a DISTANCE and a true metric. The two are easy to confuse and are NOT
complements: VI normalises by `log n`, NMI by `sqrt(H(X)H(Y))`, so `NMI = 1 - normalized_vi` is
false in general and true only at the identity endpoint. A test asserts that specifically, to stop
a future caller substituting one for the other.

**Where it refuses, decided at design time rather than after an instrument caught it.** When
either partition is a single block its entropy is exactly zero, so the denominator vanishes — and
so does `I(X;Y)`, making the quantity `0/0`. Every available answer is a lie about the data:
`0.0` reads as "these clusterings share nothing", `1.0` reads as "they agree perfectly", and `nan`
propagates silently into whatever consumes it. NMI is undefined when either side is constant, and
the refusal names WHICH side so the caller can fix the right thing.

That last detail is not decoration. Cycle 042 spent its main track on a live pipeline that
reported a loader schema mismatch as the substrate fact "no residue exists at this distance" — the
same conflation, at pipeline scale, in production. An error that says only "undefined" would have
been nearly as unhelpful.
"""
from __future__ import annotations

import math

from prometheus_math.partition import (
    Partition, PartitionError, _validate, entropy, mutual_information,
)

__all__ = ["STREHL_GHOSH_2002", "normalized_mi"]

STREHL_GHOSH_2002 = (
    "Strehl, A. & Ghosh, J. (2002). Cluster Ensembles — A Knowledge Reuse Framework for "
    "Combining Multiple Partitions. Journal of Machine Learning Research, 3, 583-617.")


def normalized_mi(projection: Partition, truth: Partition, n: int) -> float:
    """`I(projection; truth) / sqrt(H(projection) H(truth))` — agreement in [0, 1].

    Raises `PartitionError` when `n < 1`, when either argument is not a partition of `n`, or when
    either has zero entropy (a single block), which makes the ratio 0/0.
    """
    if n < 1:
        raise PartitionError(
            f"normalized_mi needs a non-empty ground set; got n={n}. Returning 0.0 would report "
            "'these clusterings share no information' when there was nothing to share it over")
    _validate(projection, n, "projection")
    _validate(truth, n, "truth")

    h_proj = entropy(projection, n)
    h_truth = entropy(truth, n)
    degenerate = [name for name, h in (("projection", h_proj), ("truth", h_truth)) if h <= 0.0]
    if degenerate:
        raise PartitionError(
            f"normalized_mi is undefined: {' and '.join(degenerate)} has zero entropy (it is a "
            "single block, i.e. constant), so the denominator sqrt(H*H) is exactly 0 and the "
            "mutual information is 0 too — the value would be 0/0. Returning 0.0 would read as "
            "'no agreement' and 1.0 as 'perfect agreement'; both are claims about the "
            "clusterings and neither is true. Use mutual_information for the unnormalised "
            "quantity, or variation_of_information, which stays defined here.")

    return mutual_information(projection, truth, n) / math.sqrt(h_proj * h_truth)
