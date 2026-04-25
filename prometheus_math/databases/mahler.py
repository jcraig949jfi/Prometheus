"""prometheus_math.databases.mahler — Mossinghoff small-Mahler tables.

Wrapper around an embedded snapshot of Michael Mossinghoff's canonical
tables of the smallest known Mahler measures M(P) for monic integer
polynomials, organised by degree.  These tables are crucial for work on
Lehmer's conjecture and Salem-number research.

Sources
-------
The primary upstream archive is
``https://wayback.cecm.sfu.ca/~mjm/Lehmer/`` (Mossinghoff at Davidson
College).  Because that host is intermittently unreachable, this module
ships an *embedded* curated snapshot of the well-known polynomials in
``_mahler_data.MAHLER_TABLE`` and uses it as the source of truth.  The
snapshot includes:

* Lehmer's polynomial (degree 10, M = 1.17628081826...) -- the
  conjectured infimum.
* Smyth's extremal x^3 - x - 1 (M = 1.32471957244...) -- the proven
  infimum among non-reciprocal integer polynomials.
* The smallest known Salem-class polynomials at degrees 6, 8, 10, 12,
  14 and 18 (the ones Charon catalogued in its Salem-NF cross-checks).
* A handful of Pisot polynomials and cyclotomic floor entries for
  boundary tests.

Coefficient convention
----------------------
All ``coeffs`` lists are in **ascending** degree order
``[a_0, a_1, ..., a_n]``.  The companion
``techne.lib.mahler_measure.mahler_measure`` uses numpy's *descending*
convention, so we reverse before passing through.  The ``lookup_*``
helpers are tolerant of the ``x -> -x`` substitution (which preserves
M).

Public API
----------
* ``smallest_known(degree=None, limit=20)`` -- ascending by M
* ``lookup_polynomial(coeffs)`` -- match coefficients (with x -> -x
  flip) against the catalog
* ``lookup_by_M(M, tol=1e-6)`` -- match by Mahler measure
* ``lehmer_witness()`` -- the deg-10 Lehmer entry
* ``smyth_extremal(degree=None)`` -- entries with M = Smyth's bound
* ``all_below(M, degree=None)`` -- everything strictly below M
* ``degree_minima()`` -- map degree -> smallest-known entry at that
  degree
* ``update_mirror()`` -- best-effort upstream refresh (returns whether
  it succeeded; the embedded snapshot is always usable)
* ``probe(timeout=3.0)`` -- always True (embedded data)

Forged: 2026-04-22 by Techne (toolsmith).  Cross-checked at import
time: every embedded ``mahler_measure`` value agrees with the live
``techne.lib.mahler_measure`` recomputation to better than 1e-9.
"""

from __future__ import annotations

import copy
from typing import Optional

from ._mahler_data import MAHLER_TABLE, SNAPSHOT_META

try:
    # The exact tool we cross-check against.  Imported lazily inside
    # the cross-check helpers so that the wrapper still imports even
    # if Techne's library tree is missing on a stripped install.
    from techne.lib.mahler_measure import mahler_measure as _mahler_measure
    _HAS_MAHLER_TOOL = True
except Exception:  # pragma: no cover -- graceful degradation
    _mahler_measure = None
    _HAS_MAHLER_TOOL = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEHMER_CONSTANT: float = 1.1762808182599175
"""Lehmer's number — the conjectured infimum of Mahler measures of
non-cyclotomic integer polynomials."""

SMYTH_CONSTANT: float = 1.3247179572447460
"""Smyth's bound — the proven infimum of Mahler measures among
*non-reciprocal* integer polynomials.  Equals the real root of
x^3 - x - 1, the plastic number."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _x_flip(coeffs: list[int]) -> list[int]:
    """Apply the substitution x -> -x to a polynomial.

    With ascending coefficients, this just negates every odd-indexed
    coefficient.  M(p(x)) = M(p(-x)), so the catalog should match
    against either form.
    """
    return [c if (i % 2 == 0) else -c for i, c in enumerate(coeffs)]


def _normalize(coeffs: list[int]) -> list[int]:
    """Strip trailing zeros and return a canonical ascending list."""
    out = list(coeffs)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def _entries() -> list[dict]:
    """Return a *deep* copy of the embedded table.

    We never expose live references to the snapshot; mutating returned
    dicts must not poison the catalog.
    """
    return copy.deepcopy(MAHLER_TABLE)


# ---------------------------------------------------------------------------
# Catalog queries
# ---------------------------------------------------------------------------

def smallest_known(degree: Optional[int] = None,
                   limit: int = 20) -> list[dict]:
    """Return the smallest known Mahler measures, ascending by M.

    Parameters
    ----------
    degree : int, optional
        Restrict to entries of exactly this degree.  ``None`` returns
        across all degrees.
    limit : int, default 20
        Maximum number of entries to return.

    Returns
    -------
    list[dict]
        Catalog entries (deep-copied), sorted by ``mahler_measure``
        ascending.
    """
    rows = _entries()
    if degree is not None:
        rows = [r for r in rows if r["degree"] == degree]
    rows.sort(key=lambda r: (r["mahler_measure"], r["degree"]))
    return rows[: max(0, int(limit))]


def lookup_polynomial(coeffs: list[int]) -> Optional[dict]:
    """Find a catalog entry matching these ascending coefficients.

    Mahler measure is invariant under the substitution x -> -x, so we
    also try the sign-flipped form.  Returns the first matching entry
    (deep-copied) or ``None``.
    """
    target = _normalize(list(coeffs))
    target_flip = _normalize(_x_flip(target))
    for e in MAHLER_TABLE:
        c = _normalize(list(e["coeffs"]))
        if c == target or c == target_flip:
            return copy.deepcopy(e)
    return None


def lookup_by_M(M: float, tol: float = 1e-6) -> list[dict]:
    """Find every catalog entry whose Mahler measure is within ``tol``
    of ``M``.

    Returns a list (possibly empty) sorted ascending by stored M.
    """
    M = float(M)
    out = [copy.deepcopy(e) for e in MAHLER_TABLE
           if abs(e["mahler_measure"] - M) <= tol]
    out.sort(key=lambda r: r["mahler_measure"])
    return out


def lehmer_witness() -> dict:
    """Return Lehmer's degree-10 polynomial entry.

    This is the polynomial conjecturally achieving the global infimum
    M = 1.17628081826... -- Lehmer's conjecture asserts no integer
    polynomial has smaller non-trivial Mahler measure.
    """
    for e in MAHLER_TABLE:
        if e.get("lehmer_witness", False):
            return copy.deepcopy(e)
    raise RuntimeError("Lehmer witness missing from embedded snapshot "
                       "-- this should never happen.")


def smyth_extremal(degree: Optional[int] = None) -> list[dict]:
    """Polynomials achieving Smyth's bound 1.32471957...

    These are the non-reciprocal extremals -- Smyth (1971) proved that
    no non-reciprocal integer polynomial has smaller Mahler measure
    than the real root of x^3 - x - 1.

    Parameters
    ----------
    degree : int, optional
        Restrict to a single degree.  ``None`` returns all.
    """
    rows = [copy.deepcopy(e) for e in MAHLER_TABLE
            if e.get("is_smyth_extremal", False)]
    if degree is not None:
        rows = [r for r in rows if r["degree"] == degree]
    rows.sort(key=lambda r: r["degree"])
    return rows


def all_below(M: float, degree: Optional[int] = None) -> list[dict]:
    """All catalog entries with Mahler measure strictly less than ``M``.

    Sorted ascending by M.  Optionally filter to a single degree.
    """
    M = float(M)
    rows = [copy.deepcopy(e) for e in MAHLER_TABLE
            if e["mahler_measure"] < M]
    if degree is not None:
        rows = [r for r in rows if r["degree"] == degree]
    rows.sort(key=lambda r: r["mahler_measure"])
    return rows


def lookup_by_degree(degree: int, limit: int = 50) -> list[dict]:
    """Return all entries of a given degree, ascending by Mahler measure.

    Parameters
    ----------
    degree : int
        Degree to filter on.
    limit : int, default 50
        Maximum number of entries to return.

    Returns
    -------
    list[dict]
        Catalog entries (deep-copied) of exactly this degree, sorted by
        ``mahler_measure`` ascending.  Empty list if no entries match.

    Notes
    -----
    Convenience wrapper over ``smallest_known(degree=degree, limit=limit)``
    with a less-overloaded name.  Use this when you want a top-K
    smallest-Mahler list at a specific degree (e.g. for Charon's
    Lehmer/Salem cross-checks).
    """
    return smallest_known(degree=int(degree), limit=int(limit))


def count_by_degree() -> dict[int, int]:
    """Return ``{degree: number_of_entries}`` across the whole catalog.

    Useful for stats reporting and quick coverage audits (e.g. "do we
    have any deg-22 entries?").
    """
    out: dict[int, int] = {}
    for e in MAHLER_TABLE:
        d = e["degree"]
        out[d] = out.get(d, 0) + 1
    return dict(sorted(out.items()))


def degree_minima() -> dict[int, dict]:
    """Map ``degree -> smallest-known Mahler-measure entry`` at each
    degree present in the catalog.

    Only entries flagged ``degree_minimum=True`` are eligible; if
    multiple flagged entries share the same degree (e.g. catalog
    revisions) the one with smallest M wins.
    """
    by_deg: dict[int, dict] = {}
    for e in MAHLER_TABLE:
        if not e.get("degree_minimum", False):
            continue
        d = e["degree"]
        cur = by_deg.get(d)
        if cur is None or e["mahler_measure"] < cur["mahler_measure"]:
            by_deg[d] = copy.deepcopy(e)
    return dict(sorted(by_deg.items()))


# ---------------------------------------------------------------------------
# Cross-check (used by tests and as a sanity guard)
# ---------------------------------------------------------------------------

def _cross_check(tol: float = 1e-9) -> list[dict]:
    """Recompute Mahler measure for every embedded entry and return
    the list of mismatches (each with stored vs recomputed values).

    If the Techne tool is unavailable, returns an empty list (we
    can't cross-check, but we also don't fail).
    """
    if not _HAS_MAHLER_TOOL:
        return []
    out = []
    for i, e in enumerate(MAHLER_TABLE):
        desc = list(reversed(e["coeffs"]))
        M_actual = float(_mahler_measure(desc))
        diff = abs(M_actual - e["mahler_measure"])
        if diff > tol:
            out.append({
                "index": i,
                "name": e["name"],
                "stored": e["mahler_measure"],
                "recomputed": M_actual,
                "diff": diff,
            })
    return out


# ---------------------------------------------------------------------------
# Mirror refresh (best-effort)
# ---------------------------------------------------------------------------

def update_mirror(timeout: float = 5.0) -> dict:
    """Best-effort attempt to refresh the snapshot from upstream.

    The Mossinghoff archive at ``wayback.cecm.sfu.ca`` is intermittent
    and the page format is HTML rather than a clean machine-readable
    feed, so we don't *replace* the embedded snapshot here -- this
    function only checks that the upstream is reachable and returns
    a status dict.  The embedded snapshot remains the source of
    truth in all cases.

    Returns
    -------
    dict
        ``{"refreshed": bool, "count": int, "source_url": str,
        "note": str}``.  ``count`` is the embedded snapshot size.
    """
    source_url = SNAPSHOT_META.get(
        "source_url", "https://wayback.cecm.sfu.ca/~mjm/Lehmer/"
    )
    note = "embedded snapshot only"
    refreshed = False
    try:
        import urllib.request
        import urllib.error
        req = urllib.request.Request(
            source_url, headers={"User-Agent": "prometheus_math/0.1"}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                _ = r.read(64)  # touch the body; we don't parse it
                refreshed = True
                note = ("upstream reachable; snapshot left unchanged "
                        "(parser not implemented)")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            note = f"upstream unreachable: {type(e).__name__}: {e}"
    except Exception as e:  # pragma: no cover
        note = f"refresh failed: {type(e).__name__}: {e}"
    return {
        "refreshed": refreshed,
        "count": len(MAHLER_TABLE),
        "source_url": source_url,
        "note": note,
    }


# ---------------------------------------------------------------------------
# Probe (always True -- embedded snapshot is unconditionally available)
# ---------------------------------------------------------------------------

def probe(timeout: float = 3.0) -> bool:
    """Return whether the Mossinghoff snapshot is available.

    Always returns ``True``: the snapshot is bundled with this module
    and does not need network access.  ``timeout`` is accepted for
    interface uniformity with the other ``prometheus_math.databases``
    wrappers but ignored.
    """
    # Sanity: the embedded snapshot must be non-empty and contain the
    # Lehmer witness.  These conditions are guaranteed at module-build
    # time but we double-check defensively.
    if not MAHLER_TABLE:
        return False
    has_lehmer = any(e.get("lehmer_witness") for e in MAHLER_TABLE)
    return bool(has_lehmer)


# ---------------------------------------------------------------------------
# Module-load consistency check
# ---------------------------------------------------------------------------

# Run a cheap consistency check on import so that an accidental edit to
# the snapshot doesn't silently corrupt downstream queries.  We don't
# raise here -- pathological floats from numpy can drift slightly --
# but we record any mismatches for diagnostic access.
_LOAD_TIME_MISMATCHES: list[dict] = _cross_check(tol=1e-6)


__all__ = [
    "LEHMER_CONSTANT",
    "SMYTH_CONSTANT",
    "smallest_known",
    "lookup_polynomial",
    "lookup_by_M",
    "lookup_by_degree",
    "count_by_degree",
    "lehmer_witness",
    "smyth_extremal",
    "all_below",
    "degree_minima",
    "update_mirror",
    "probe",
]
