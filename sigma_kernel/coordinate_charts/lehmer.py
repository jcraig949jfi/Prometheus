"""sigma_kernel.coordinate_charts.lehmer — Lehmer chart registration.

Joint-sprint sync point T5 (see
``pivot/techne_ergon_joint_sprint_2026-05-05.md`` §6.1). Aporia
priority — Ergon W3.2 fixture materialization unblocks when this lands.

The chart
---------
Region: degree-14 reciprocal palindromic polynomials with integer
coefficients in the band ``[-5, +5]``. This is the brute-force
enumeration slice closed on Day-5 of the 2026-05-01 → 05 sprint
(97.4M polynomials, INCONCLUSIVE → H5_CONFIRMED-local-lemma).

Coordinate system
-----------------
A degree-14 reciprocal palindromic polynomial has coefficients
``(c0, c1, c2, c3, c4, c5, c6, c7, c6, c5, c4, c3, c2, c1, c0)``.
The independent coordinates are the first 8 (``c0`` … ``c7``); the
remaining 7 are determined by palindromicity. We use the half-vector
``(c0, c1, ..., c7)`` as the chart's coordinate system.

Equivalence relation
--------------------
``x → -x`` reflection: replacing ``x`` with ``-x`` flips the sign of
every odd-index coefficient. Since the Mahler measure (and thus
Lehmer-band membership) is invariant under this reflection, two
polynomials related by ``x → -x`` represent the same physical object.
The canonicalization picks the lex-min of ``{coeffs, reflected}``.

Metric
------
L2 distance over the (canonicalized) 8-dimensional coefficient
half-vector. There were several reasonable choices here; see the
docstring on :func:`_lehmer_distance` for the rationale.

Admissibility
-------------
A coordinate vector is admissible iff:
1. It has length exactly 8 (the half of a degree-14 palindrome).
2. All entries are integers in ``[-5, +5]``.
3. The corresponding full polynomial is palindromic (trivially true
   for any half-vector — but the predicate is exposed so callers
   passing a full 15-coefficient vector also work).
4. The corresponding full polynomial has degree exactly 14 (i.e.
   ``c0 != 0``; otherwise the leading coefficient is zero and the
   polynomial collapses to a lower degree).
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence, Tuple, Union

from sigma_kernel.coordinate_chart import (
    CanonicalizationProtocol,
    CoordinateChart,
    register_chart,
)


# ---------------------------------------------------------------------------
# Tunables (the chart's region constants)
# ---------------------------------------------------------------------------


_DEGREE = 14
"""Polynomial degree this chart represents."""

_HALF_LEN = _DEGREE // 2 + 1  # 8 — independent coords (c0..c7) of a deg-14 palindrome
"""Number of independent coordinates after applying palindromicity."""

_COEFF_BOUND = 5
"""Coefficient absolute-value bound for this region."""


# ---------------------------------------------------------------------------
# Coordinate normalization helpers
# ---------------------------------------------------------------------------


CoeffVec = Union[Sequence[int], Tuple[int, ...]]


def _to_half_tuple(coeffs: CoeffVec) -> Tuple[int, ...]:
    """Normalize input to an 8-tuple of ints (the half-vector form).

    Accepts:
    * an 8-element half-vector (returned as a tuple of ints)
    * a 15-element full palindrome (truncated to its first 8 entries)
    """
    if coeffs is None:
        raise TypeError("coeffs must be a sequence of ints; got None")
    seq = tuple(int(c) for c in coeffs)
    if len(seq) == _HALF_LEN:
        return seq
    if len(seq) == _DEGREE + 1:
        return seq[:_HALF_LEN]
    raise ValueError(
        f"expected coefficient vector of length {_HALF_LEN} (half) or "
        f"{_DEGREE + 1} (full); got length {len(seq)}"
    )


def _reflect_half(half: Tuple[int, ...]) -> Tuple[int, ...]:
    """Apply x → -x to a half-vector.

    The full polynomial coefficient at index ``i`` (counting from the
    constant term) gets multiplied by ``(-1)^i`` under x → -x. Since
    the half-vector indices correspond directly to the first 8 full
    indices (``c0`` is the degree-0 coefficient, ``c1`` is degree-1,
    etc. — by the palindrome convention used here), we simply flip the
    sign of every odd-index entry.
    """
    return tuple(-c if (i % 2 == 1) else c for i, c in enumerate(half))


# ---------------------------------------------------------------------------
# Canonicalization, metric, admissibility
# ---------------------------------------------------------------------------


def _lehmer_canonicalize(coeffs: CoeffVec) -> Tuple[int, ...]:
    """Canonical form under the ``x → -x`` reflection.

    Returns the lex-min of ``{half, reflected_half}`` so that any two
    representations of the same physical polynomial collapse to the
    same canonical tuple.
    """
    half = _to_half_tuple(coeffs)
    reflected = _reflect_half(half)
    return min(half, reflected)


def _lehmer_distance(a: CoeffVec, b: CoeffVec) -> float:
    """L2 distance over canonicalized half-vectors.

    Why L2: callers (Ergon W3.2 fixture materialization, future
    ExclusionCertificate.exclusion_distance queries) want a smooth
    metric over the discrete coefficient lattice. L2 is symmetric,
    satisfies the triangle inequality, has a well-known
    interpretation, and is the natural ambient metric for the L2
    norm-ball-style perturbations we use as the
    ``coefficient_perturbation`` valid_operation.

    Both inputs are normalized to half-vectors and zero-padded to the
    longer length before subtraction (so a half-vector and a
    full-vector compare cleanly even though we currently only accept
    matching lengths via ``_to_half_tuple``).

    Note: this function expects inputs in *raw* form (it
    re-canonicalizes them); :meth:`CoordinateChart.distance` handles
    canonicalization automatically, but downstream callers using
    ``chart.metric`` directly get the same answer because the metric
    is invariant under canonicalization (canonicalize is idempotent
    and respects the equivalence relation).
    """
    ca = _lehmer_canonicalize(a)
    cb = _lehmer_canonicalize(b)
    n = max(len(ca), len(cb))
    pa = ca + (0,) * (n - len(ca))
    pb = cb + (0,) * (n - len(cb))
    return math.sqrt(sum((x - y) * (x - y) for x, y in zip(pa, pb)))


def _is_palindromic_full(full: Sequence[int]) -> bool:
    """True iff a 15-coefficient vector is palindromic
    (``c[i] == c[14-i]`` for all i)."""
    n = len(full)
    return all(full[i] == full[n - 1 - i] for i in range(n // 2))


def _lehmer_admissible(coeffs: CoeffVec) -> bool:
    """Reciprocal palindromic + degree-exactly-14 + coefficient-bound.

    Accepts either an 8-element half or a 15-element full vector.
    Returns False for any input that fails any of the three checks
    (without raising — the predicate is total).
    """
    if coeffs is None:
        return False
    try:
        seq = tuple(int(c) for c in coeffs)
    except (TypeError, ValueError):
        return False

    if len(seq) == _DEGREE + 1:
        # Full vector: must be palindromic, degree exactly 14, and bounded.
        if not _is_palindromic_full(seq):
            return False
        if seq[0] == 0 or seq[-1] == 0:
            # Leading/trailing zero collapses to a lower-degree polynomial.
            return False
        if any(abs(c) > _COEFF_BOUND for c in seq):
            return False
        return True

    if len(seq) == _HALF_LEN:
        # Half-vector: degree-14 means c0 != 0; bounded; palindromicity is
        # implicit in the half-vector representation.
        if seq[0] == 0:
            return False
        if any(abs(c) > _COEFF_BOUND for c in seq):
            return False
        return True

    return False


# ---------------------------------------------------------------------------
# The chart instance
# ---------------------------------------------------------------------------


LEHMER_DEG14_PM5_PALINDROMIC = CoordinateChart(
    domain="lehmer",
    region_key="deg14:pm5:palindromic",
    coordinate_system=("c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7"),
    canonicalization=CanonicalizationProtocol(
        impl="reflection_quotient",
        decidability_status="decidable",
        choice_dependencies=("lex_minimization",),
        version="1.0.0",
        canonicalize=_lehmer_canonicalize,
    ),
    metric=_lehmer_distance,
    metric_id="L2",
    equivalence_relations=("x→-x",),
    admissible_region=_lehmer_admissible,
    valid_operations=("coefficient_perturbation", "reflection"),
)
"""The Lehmer ``deg14:pm5:palindromic`` chart. Registered at module
import time."""


# Register at import time -----------------------------------------------------
register_chart(LEHMER_DEG14_PM5_PALINDROMIC)


__all__ = [
    "LEHMER_DEG14_PM5_PALINDROMIC",
    # exposed for tests / debug; not part of the substrate's public surface
    "_lehmer_canonicalize",
    "_lehmer_distance",
    "_lehmer_admissible",
]
