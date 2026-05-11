"""Curated seed pool of known-survivor candidates for decoy interleaving.

Per Ergon Dim 7 (null/decoy interleaving) — the Tier-0 brute-force
enumerator emits records biased toward kills (in-band rate is 0.026%
per 2026-05-11 smoke test; even the 4 in-band candidates were
REJECTED via reducibility). The Learner needs balanced positive
exemplars. This module curates a small pool of KNOWN survivors
(Mossinghoff catalog entries verified to pass the F-gate battery)
and provides an interleaving generator.

Source: ``prometheus_math.databases._mahler_data.MAHLER_TABLE``
(Mossinghoff 1998 + Phase-1 curation). Filtered to deg-12 in-band
(M ∈ (1.001, 1.18)) for the Lehmer palindromic Tier-1 generator's
target format.

The injected records are TAGGED ``decoy_kind="seeded_survivor"`` in
the LearnerRecord so train/eval splits can keep them separated from
naturally-enumerated kills.
"""
from __future__ import annotations

from itertools import cycle
from typing import Iterator, List, Tuple


# ---------------------------------------------------------------------------
# Curated deg-12 in-band Mossinghoff entries
# ---------------------------------------------------------------------------

# Sourced 2026-05-11 from prometheus_math.databases._mahler_data.MAHLER_TABLE
# entries with degree==12 and 1.001 < mahler_measure < 1.18. All are
# Lehmer-extension polynomials (M = 1.176281 = Lehmer's conjectured
# infimum). Coefficients in ASCENDING degree order [a_0, ..., a_n].
_DEG12_SURVIVORS: List[Tuple[List[int], float, str]] = [
    (
        [1, 0, 0, 0, 0, -1, -1, -1, 0, 0, 0, 0, 1],
        1.176281,
        "Lehmer-extension (deg 12)",
    ),
    (
        [1, 2, 2, 0, -2, -3, -3, -3, -2, 0, 2, 2, 1],
        1.176281,
        "Lehmer x Phi_3",
    ),
    (
        [1, 1, 1, 0, -1, -2, -2, -2, -1, 0, 1, 1, 1],
        1.176281,
        "Lehmer x Phi_4",
    ),
]


def get_deg12_survivors() -> List[Tuple[List[int], float, str]]:
    """Return the curated deg-12 in-band survivor pool. Each entry is
    ``(coeffs_ascending, mahler_measure, label)``."""
    # Return shallow copies so callers can't mutate the curated source
    return [(list(c), m, l) for c, m, l in _DEG12_SURVIVORS]


def iter_seeded_survivors(
    *, degree: int = 12, repeat: bool = True,
) -> Iterator[Tuple[List[int], float, str]]:
    """Iterate the curated survivor pool for the given degree.

    Parameters
    ----------
    degree : int
        Polynomial degree to filter by. Default 12 (Lehmer palindromic).
    repeat : bool
        If True (default), the iterator cycles forever — useful for
        interleaving with an unbounded enumerator. If False, iterates
        once.
    """
    if degree == 12:
        pool = get_deg12_survivors()
    else:
        # Future degrees: extend by adding more curated lists.
        pool = []
    if not pool:
        return
    if repeat:
        for entry in cycle(pool):
            yield entry
    else:
        yield from pool


def interleave_decoys(
    enumerated_iter: Iterator[List[int]],
    *,
    decoy_rate: float = 0.1,
    degree: int = 12,
) -> Iterator[Tuple[List[int], str]]:
    """Interleave seeded survivors into an enumerated candidate stream.

    Yields ``(coeffs, decoy_kind_or_empty)`` tuples; ``decoy_kind`` is
    ``"seeded_survivor"`` for injected positives, ``""`` for
    naturally-enumerated candidates. Decoy injection is deterministic
    (every Nth record is a decoy where N = 1/decoy_rate).

    Parameters
    ----------
    enumerated_iter : Iterator[List[int]]
        Naturally-enumerated candidate stream (e.g. from
        ``enumerate_palindromic_candidates``).
    decoy_rate : float
        Fraction of yielded records that should be seeded survivors.
        Default 0.1 (1 decoy per 10 records). Clamped to [0, 1].
    degree : int
        Polynomial degree (passed to ``iter_seeded_survivors``).
    """
    if not 0.0 <= decoy_rate <= 1.0:
        raise ValueError(
            f"decoy_rate must be in [0, 1]; got {decoy_rate!r}"
        )
    if decoy_rate == 0.0:
        for coeffs in enumerated_iter:
            yield (coeffs, "")
        return
    survivor_iter = iter_seeded_survivors(degree=degree, repeat=True)
    # Inject every Nth where N = round(1/decoy_rate); minimum N=2
    interval = max(2, round(1.0 / decoy_rate))
    i = 0
    for coeffs in enumerated_iter:
        i += 1
        yield (coeffs, "")
        if i % interval == 0:
            try:
                survivor_coeffs, _, _ = next(survivor_iter)
            except StopIteration:
                continue
            yield (survivor_coeffs, "seeded_survivor")


__all__ = [
    "get_deg12_survivors",
    "iter_seeded_survivors",
    "interleave_decoys",
]
