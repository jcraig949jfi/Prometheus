"""NORMALIZED VARIATION OF INFORMATION — a scale-free distance between clusterings.

Reference: Marina Meila, "Comparing clusterings — an information based distance", Journal of
Multivariate Analysis 98 (2007) 873-895.

Variation of information, `VI(P, T) = H(P|T) + H(T|P)`, is a true metric on the space of
partitions of a fixed ground set: non-negative, symmetric, zero exactly on identity, and
satisfying the triangle inequality (Meila 2007, Properties 1-3). Cycle 023 already built the
unnormalised quantity for the sweep directions. What was missing is the normalisation, and the
reason it is worth a module rather than a division is a standing instruction I keep re-learning:

    **test mean-spacing / scale normalisation FIRST on any comparison of gaps.**

Raw VI between the two extremes of the refinement lattice is `log n`. So a raw comparison of two
projections measured on ground sets of different sizes reports the SIZE DIFFERENCE, not the
disagreement — the larger ground set looks more disagreeing no matter what the projections do.
Dividing by the attained maximum `log2(n)` puts every comparison on [0, 1], and
`test_composition_normalisation_is_the_scale_free_comparison_it_claims_to_be` checks that the
raw numbers differ across n while the normalised ones do not.

**Where this refuses, and why the refusal is the interesting part.** At `n = 1` the normaliser is
`log2(1) = 0`. The two tempting implementations both commit this loop's recurring bug: returning
`0.0` says "these clusterings are identical", and returning `nan` propagates a silent poison
value. Neither is true — the normalised distance has no value on a one-element ground set, and
that is a statement about the input. It is said out loud instead, which is the eleventh time this
distinction has come up in the ladder work and the first time it was designed in from the start
rather than retrofitted after an instrument caught it.
"""
from __future__ import annotations

import math

from prometheus_math.partition import (
    Partition, PartitionError, variation_of_information, _validate,
)

__all__ = ["MEILA_2007", "normalized_vi", "vi_upper_bound"]

MEILA_2007 = ("Meila, M. (2007). Comparing clusterings — an information based distance. "
              "Journal of Multivariate Analysis, 98(5), 873-895.")


def vi_upper_bound(n: int) -> float:
    """The maximum VI attainable between two clusterings of `n` points: `log2(n)` bits.

    Meila (2007), Section 4. Attained by the pair (all singletons, one block): the first has
    entropy `log2(n)`, the second has entropy 0, and they share no information.
    """
    if n < 1:
        raise PartitionError(
            f"an upper bound on VI needs a non-empty ground set; got n={n}. Returning 0.0 would "
            "report 'no two clusterings of this set can differ', which is a claim about "
            "clusterings rather than about the empty input")
    return math.log2(n)


def normalized_vi(projection: Partition, truth: Partition, n: int) -> float:
    """`VI(projection, truth) / log2(n)` — a metric on clusterings, rescaled to [0, 1].

    Inherits every metric property from the unnormalised form, since dividing by a positive
    constant that does not depend on the arguments preserves symmetry, identity and the triangle
    inequality (all three are checked as Hypothesis properties rather than assumed).

    Raises `PartitionError` when `n < 2`: the normaliser `log2(1)` is zero and `log2(0)` is
    undefined, so there is nothing to divide by. The UNNORMALISED `variation_of_information`
    remains well-defined at `n = 1` and stays available for callers who want it.
    """
    if n < 2:
        raise PartitionError(
            f"normalized_vi is undefined on a ground set of {n}: the normaliser is log2({n}) "
            f"{'which is undefined' if n < 1 else '= 0'}, so there is no scale to divide by. "
            "Returning 0.0 would read as 'these clusterings are identical' and nan would "
            "propagate silently; neither is a fact about the clusterings. Use "
            "variation_of_information for the unnormalised quantity, which is well-defined at "
            "one element.")
    _validate(projection, n, "projection")
    _validate(truth, n, "truth")
    return variation_of_information(projection, truth, n) / math.log2(n)
