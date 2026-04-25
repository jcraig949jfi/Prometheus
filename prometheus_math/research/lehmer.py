"""Lehmer-degree-profile binner — project #30.

Helper for Charon's Lehmer scans over LMFDB number-field-defining
polynomials.  Charon's scan scripts repeatedly produce lists of
``{degree, mahler_measure, ...}`` records and ad-hoc bin them per
degree to report (count, min/max/median M, Salem count) bins.  This
module codifies that binning so every Lehmer scan reports the same
columns in the same order.

Public API
----------
``degree_profile(scan_output, M_threshold=None, salem_indicator='palindromic')``
    Bin a scan output by ``degree`` and emit one summary row per
    degree.  Returns ``list[dict]`` sorted ascending by degree.
``filter_below_M(scan_output, M_max)``
    Subset of ``scan_output`` with ``mahler_measure < M_max``.
``identify_salem_class(coeffs)``
    Rough Salem-number detector: returns True iff ``coeffs`` is
    palindromic (i.e. ``a_i == a_{n-1-i}`` for all i).  This is the
    structural signature of Salem polynomials and matches the
    ``salem_indicator='palindromic'`` mode of ``degree_profile``.
``identify_smyth_extremal(coeffs, M, tol=1e-6)``
    True iff ``coeffs`` plausibly attains Smyth's bound: ``M`` is
    within ``tol`` of ``SMYTH_CONSTANT = 1.32472...`` and the
    polynomial is non-reciprocal (Smyth's theorem requires
    non-reciprocity).
``to_csv(profile, path)``
    Write the profile to a CSV file.
``to_markdown(profile)``
    Render the profile as a Markdown table.

Authoritative anchor
--------------------
The 178-entry Mossinghoff snapshot exposed by
``prometheus_math.databases.mahler.MAHLER_TABLE`` (via ``smallest_known``)
is the canonical reference.  Lehmer's polynomial (degree 10,
M = 1.17628081826...) sits as the global minimum; Smyth's bound
1.32471957... is the non-reciprocal floor.

Complexity
----------
``degree_profile`` is O(N log N) total — a single scan to bucket by
degree (O(N)) plus per-bin sorting for the median (Σ kᵢ log kᵢ ≤
N log N).  Numpy is used for percentile/median to keep the constant
factor low on large scans.

Forged: 2026-04-25 by Techne (toolsmith) for project #30.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from typing import Iterable, Optional

import numpy as np

from prometheus_math.databases.mahler import (
    LEHMER_CONSTANT,
    SMYTH_CONSTANT,
)

__all__ = [
    "degree_profile",
    "filter_below_M",
    "identify_salem_class",
    "identify_smyth_extremal",
    "to_csv",
    "to_markdown",
    "LEHMER_CONSTANT",
    "SMYTH_CONSTANT",
]


# ---------------------------------------------------------------------------
# Coefficient helpers
# ---------------------------------------------------------------------------

def _strip_trailing_zeros(coeffs: list[int]) -> list[int]:
    out = list(coeffs)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def identify_salem_class(coeffs: Optional[Iterable[int]]) -> bool:
    """Return True iff ``coeffs`` is palindromic.

    Convention: ``coeffs`` is in either ascending or descending degree
    order; palindromicity is order-agnostic (``a == reverse(a)``).
    A polynomial whose coefficients are palindromic is reciprocal,
    which is the structural signature of a Salem polynomial.  This is
    a *necessary* but not strictly sufficient condition (cyclotomics
    are also reciprocal); for a full classification you'd verify the
    root distribution, but for binning Charon's scans this is the
    customary indicator.

    Parameters
    ----------
    coeffs : iterable of int or None
        Coefficient list.  ``None`` or empty returns False.

    Returns
    -------
    bool
    """
    if coeffs is None:
        return False
    cs = _strip_trailing_zeros([int(c) for c in coeffs])
    if not cs:
        return False
    n = len(cs)
    # Length-1 (constant) polynomial: palindromic by convention but not
    # a meaningful Salem candidate.
    if n < 2:
        return False
    for i in range(n // 2):
        if cs[i] != cs[n - 1 - i]:
            return False
    return True


def _is_reciprocal(coeffs: Iterable[int]) -> bool:
    """Reciprocal polynomial test: a == ±reverse(a)."""
    cs = _strip_trailing_zeros([int(c) for c in coeffs])
    if len(cs) < 2:
        return False
    rev = list(reversed(cs))
    return cs == rev or cs == [-c for c in rev]


def identify_smyth_extremal(coeffs: Optional[Iterable[int]],
                            M: float,
                            tol: float = 1e-6) -> bool:
    """Return True iff (coeffs, M) plausibly attains Smyth's bound.

    Smyth (1971) proved that every *non-reciprocal* integer polynomial
    has Mahler measure ≥ SMYTH_CONSTANT = 1.32471957... (the real root
    of x^3 - x - 1, the plastic number).  Equality is achieved only by
    polynomials in the Smyth-extremal class.  This detector returns
    True when:

    1. ``|M - SMYTH_CONSTANT| <= tol``, and
    2. ``coeffs`` is non-reciprocal (i.e. NOT identify_salem_class).

    Parameters
    ----------
    coeffs : iterable of int or None
        Coefficient list.  When ``None``, only the M-equality test is
        applied (rough detection).
    M : float
        Computed Mahler measure.
    tol : float, default 1e-6
        Tolerance for the equality ``M ≈ SMYTH_CONSTANT``.

    Returns
    -------
    bool
    """
    if abs(float(M) - SMYTH_CONSTANT) > float(tol):
        return False
    if coeffs is None:
        return True
    return not _is_reciprocal(coeffs)


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_below_M(scan_output: Iterable[dict],
                   M_max: float) -> list[dict]:
    """Return the subset of ``scan_output`` with ``mahler_measure < M_max``.

    Entries missing ``mahler_measure`` are silently dropped.  The
    returned list preserves the input order; entries are NOT
    deep-copied (cheap shallow filter — Charon's scans regularly run
    on 10^4-entry lists).

    Parameters
    ----------
    scan_output : iterable of dict
        Each dict must contain a numeric ``mahler_measure`` key.
    M_max : float
        Strict upper bound; entries with ``M < M_max`` are kept.

    Returns
    -------
    list[dict]
    """
    threshold = float(M_max)
    out: list[dict] = []
    for e in scan_output:
        m = e.get("mahler_measure")
        if m is None:
            continue
        if float(m) < threshold:
            out.append(e)
    return out


# ---------------------------------------------------------------------------
# Degree-profile binning
# ---------------------------------------------------------------------------

_PROFILE_FIELDS = (
    "degree",
    "count",
    "min_M",
    "max_M",
    "mean_M",
    "median_M",
    "salem_count",
    "lehmer_witness_count",
    "smyth_extremal_count",
    "below_threshold_count",
)


def _row_for_degree(degree: int,
                    entries: list[dict],
                    M_threshold: Optional[float],
                    salem_indicator: str) -> dict:
    """Build the per-degree summary row.  Internal helper."""
    Ms = np.array(
        [float(e["mahler_measure"]) for e in entries], dtype=float
    )
    n = int(Ms.size)
    salem_count = 0
    smyth_count = 0
    lehmer_count = 0
    below = 0
    for e in entries:
        coeffs = e.get("coeffs")
        m = float(e["mahler_measure"])
        # Salem detection
        if salem_indicator == "palindromic":
            if identify_salem_class(coeffs):
                salem_count += 1
        elif salem_indicator == "flag":
            if bool(e.get("salem_class") or e.get("is_salem")):
                salem_count += 1
        else:
            raise ValueError(
                f"unknown salem_indicator {salem_indicator!r}; "
                "expected 'palindromic' or 'flag'"
            )
        # Smyth-extremal detection
        if identify_smyth_extremal(coeffs, m):
            smyth_count += 1
        # Lehmer-witness detection: explicit flag, OR M ≈ Lehmer constant.
        if bool(e.get("lehmer_witness")) or abs(m - LEHMER_CONSTANT) <= 1e-6:
            lehmer_count += 1
        # Below-threshold count
        if M_threshold is not None and m < float(M_threshold):
            below += 1
    return {
        "degree": int(degree),
        "count": n,
        "min_M": float(Ms.min()),
        "max_M": float(Ms.max()),
        "mean_M": float(Ms.mean()),
        "median_M": float(np.median(Ms)),
        "salem_count": salem_count,
        "lehmer_witness_count": lehmer_count,
        "smyth_extremal_count": smyth_count,
        "below_threshold_count": below,
    }


def degree_profile(scan_output: Iterable[dict],
                   M_threshold: Optional[float] = None,
                   salem_indicator: str = "palindromic") -> list[dict]:
    """Bin a Lehmer-scan output by degree and report summary statistics.

    Parameters
    ----------
    scan_output : iterable of dict
        Each dict must have integer ``degree`` and float
        ``mahler_measure``; ``coeffs`` is optional but required for
        Salem / Smyth-extremal detection.  Entries missing either
        of the required keys are silently dropped.
    M_threshold : float, optional
        If supplied, every row's ``below_threshold_count`` reports the
        number of polynomials at that degree with ``M < M_threshold``.
        ``None`` (default) sets all such counts to 0.
    salem_indicator : {'palindromic', 'flag'}, default 'palindromic'
        How to count Salem-class entries:

        * ``'palindromic'`` — call ``identify_salem_class(coeffs)``.
          Requires ``coeffs`` in each scan entry.
        * ``'flag'`` — trust an explicit ``salem_class`` (or
          ``is_salem``) boolean on the entry.  Useful when the scan
          has already done the Salem classification.

    Returns
    -------
    list[dict]
        One row per degree present in ``scan_output``, sorted
        ascending by ``degree``.  Each row has the keys:

        ``degree, count, min_M, max_M, mean_M, median_M, salem_count,
        lehmer_witness_count, smyth_extremal_count, below_threshold_count``.

    Notes
    -----
    Complexity: O(N log N) over the input where N = len(scan_output).
    Numpy is used for the per-degree percentile/median to keep the
    constant factor low.
    """
    if salem_indicator not in ("palindromic", "flag"):
        raise ValueError(
            f"salem_indicator must be 'palindromic' or 'flag'; "
            f"got {salem_indicator!r}"
        )

    # Bucket by degree in a single O(N) pass.
    buckets: dict[int, list[dict]] = defaultdict(list)
    for e in scan_output:
        if "degree" not in e or "mahler_measure" not in e:
            continue
        try:
            d = int(e["degree"])
            float(e["mahler_measure"])  # type-check
        except (TypeError, ValueError):
            continue
        buckets[d].append(e)

    rows = [
        _row_for_degree(d, buckets[d], M_threshold, salem_indicator)
        for d in sorted(buckets)
    ]
    return rows


# ---------------------------------------------------------------------------
# Output formats
# ---------------------------------------------------------------------------

def to_csv(profile: list[dict], path: str) -> None:
    """Write a degree-profile to a CSV file at ``path``.

    Columns are written in the canonical order
    (``degree, count, min_M, max_M, mean_M, median_M, salem_count,
    lehmer_witness_count, smyth_extremal_count, below_threshold_count``).
    An empty profile writes a header row only.
    """
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(_PROFILE_FIELDS))
        writer.writeheader()
        for row in profile:
            writer.writerow({k: row.get(k, "") for k in _PROFILE_FIELDS})


def to_markdown(profile: list[dict]) -> str:
    """Render a degree-profile as a Markdown table.

    Parameters
    ----------
    profile : list[dict]
        Output of :func:`degree_profile`.

    Returns
    -------
    str
        Markdown-formatted table.  Empty profile returns the header
        row only.
    """
    headers = list(_PROFILE_FIELDS)
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in profile:
        cells = []
        for k in headers:
            v = row.get(k, "")
            if isinstance(v, float):
                cells.append(f"{v:.6f}")
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)
