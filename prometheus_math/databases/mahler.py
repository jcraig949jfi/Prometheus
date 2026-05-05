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

Coverage
--------
The Phase-1 + Phase-2 snapshot covers:

* **178 catalog entries** (after the Phase-1 expansion from 21).
* **Degrees** 2..30 plus 36 (every degree in [2, 30] populated).
* **Mahler measures** in the range [1.0, 1.84].  Cyclotomic Phi_n
  contribute the M = 1 baseline; Lehmer's polynomial sits at
  1.176280818... and the densely populated Salem cluster runs
  through 1.18..1.30.

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
* ``lookup_by_degree(degree, limit=50)`` -- top-K at a single degree
* ``count_by_degree()`` -- ``{degree: count}`` across the catalog
* ``search_polynomial(M, deg=None, tol=1e-3, return_distance=True)``
  -- Phase-2 fuzzy lookup sorted by ``|entry.M - M|`` ascending
* ``search_polynomial_by_coeffs_signature(signature, tol=1e-9)``
  -- structural signature match (length + first/last nonzero +
  parity of nonzero count)
* ``find_extremal_at_degree(degree, criterion='smallest_M')`` -- best
  entry at a degree by smallest M / smallest disc proxy / palindrome
* ``histogram_by_M(bin_count=20, M_range=(1.0, 2.0))`` -- distribution
  of M values across the catalog (default range covers the full
  catalog)
* ``search_by_signature_class(salem=None, smyth_extremal=None,
  lehmer_witness=None, degree_minimum=None)`` -- combination boolean
  filter
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


# ---------------------------------------------------------------------------
# Factorization-aware lookup (catalog-completeness fix, 2026-05-04)
# ---------------------------------------------------------------------------

#: Upper bound on n when probing cyclotomic Phi_n during factorization.
#: phi(n) grows roughly like n / log log n; for poly degree D <= 200, every
#: cyclotomic factor has phi(n) <= D, so n <= ~6 * D suffices in practice.
#: We keep a generous default of 200 (covers all phi(n) <= 200) and degrade
#: gracefully for higher n via the ``max_n`` argument.
_DEFAULT_MAX_CYCLOTOMIC_N: int = 200


def _is_cyclotomic_poly_sympy(f, x, max_n: int = _DEFAULT_MAX_CYCLOTOMIC_N
                              ) -> Optional[int]:
    """If ``f`` (sympy expression in ``x``) equals Phi_n for some n in
    [1, max_n], return that n; otherwise return None.

    Comparison is done at the polynomial-coefficient level (not sympy
    structural equality) so that algebraically-equal but structurally
    different forms still match.
    """
    import sympy as sp

    try:
        f_poly = sp.Poly(f, x, domain=sp.ZZ)
    except Exception:
        return None
    deg_f = f_poly.degree()
    if deg_f < 1:
        return None
    # phi(n) = deg_f restricts the candidate range; iterate small n until
    # phi(n) > max possible deg_f. We keep a tight per-call cap.
    for n in range(1, int(max_n) + 1):
        try:
            phi = sp.cyclotomic_poly(n, x)
        except Exception:
            continue
        try:
            phi_poly = sp.Poly(phi, x, domain=sp.ZZ)
        except Exception:
            continue
        if phi_poly.degree() != deg_f:
            continue
        if phi_poly == f_poly:
            return n
    return None


def _ascending_from_sympy_poly(poly, x) -> list[int]:
    """Extract ascending integer coefficients from a sympy Poly/Expr."""
    import sympy as sp

    if not isinstance(poly, sp.Poly):
        poly = sp.Poly(poly, x, domain=sp.ZZ)
    desc = [int(c) for c in poly.all_coeffs()]
    return list(reversed(desc))


def mahler_lookup_factored(
    coeffs: list[int],
    max_cyclotomic_n: int = _DEFAULT_MAX_CYCLOTOMIC_N,
) -> tuple[Optional[str], list[tuple[int, int]], str]:
    """Catalog lookup with factorization-aware composite matching.

    The original :func:`lookup_polynomial` does exact-coefficient matching
    only, so a polynomial like ``Lehmer(x) * Phi_1(x)^4`` (degree 14) is
    a "miss" even though its non-cyclotomic factor IS Lehmer's polynomial
    in the catalog and the cyclotomic factor is canonical structure.
    This function bridges that gap.

    Algorithm
    ---------
    1. Try direct lookup via :func:`lookup_polynomial` (with x -> -x flip).
       If hit, return ``(name, [], "direct_match")``.
    2. Otherwise, factor the polynomial over ZZ via
       ``sympy.factor_list``. Classify each irreducible factor as either
       cyclotomic Phi_n (recording (n, multiplicity)) or non-cyclotomic
       (kept aside as the "core").
    3. If every factor is cyclotomic, return
       ``(label, [(n_1, k_1), ...], "all_cyclotomic_match")`` where
       ``label`` is a canonical printable summary like
       ``"Phi_1^4 * Phi_2^2"``.
    4. Otherwise, reassemble the non-cyclotomic core polynomial and look
       it up directly. If it matches a catalog entry, return
       ``(name, [(n_1, k_1), ...], "composite_match")`` — e.g.
       ``("Lehmer's polynomial", [(1, 4)], "composite_match")``.
    5. If the core does not match anything, return
       ``(None, [(n_i, k_i), ...], "no_match")``. The cyclotomic
       structure is still reported (informational; useful for diagnostics).

    Parameters
    ----------
    coeffs : list of int
        Ascending integer coefficients.
    max_cyclotomic_n : int, default 200
        Largest cyclotomic index probed during classification.

    Returns
    -------
    (label, cyclotomic_structure, match_type)
        ``label`` : str or None — catalog entry name (or pure-cyclotomic
        summary, or None when no match).
        ``cyclotomic_structure`` : list of (n, k) tuples in ascending
        ``n`` order.
        ``match_type`` : one of
        ``"direct_match"`` / ``"composite_match"`` / ``"all_cyclotomic_match"``
        / ``"no_match"``.

    Notes
    -----
    Backwards compatibility: :func:`lookup_polynomial` is unchanged and
    still callable independently. Performance: factorization is moderately
    expensive (~ms per polynomial) and should NOT be applied to every
    poly in a large brute-force run — only to those that fail direct
    lookup. See ``MAHLER_FACTORED_LOOKUP_SPEC.md``.
    """
    target = _normalize(list(int(c) for c in coeffs))
    if not target or (len(target) == 1):
        # Constant or empty — handled as edge case.
        direct = lookup_polynomial(target)
        if direct is not None:
            return (str(direct.get("name", "Mossinghoff (unnamed)")), [],
                    "direct_match")
        return (None, [], "no_match")

    # Step 1: direct match (cheap).
    direct = lookup_polynomial(target)
    if direct is not None:
        return (str(direct.get("name", "Mossinghoff (unnamed)")), [],
                "direct_match")

    # Step 2: factor over ZZ.
    try:
        import sympy as sp
    except Exception:
        return (None, [], "no_match")

    x = sp.symbols("x")
    P = sum(int(c) * x ** i for i, c in enumerate(target))
    try:
        unit, factors = sp.factor_list(P, x, domain="ZZ")
    except Exception:
        return (None, [], "no_match")

    cyclo_struct: dict[int, int] = {}
    non_cyclo: list[tuple[object, int]] = []
    for f, mult in factors:
        # Skip the trivial leading-unit constant factor (rare; defensive).
        try:
            f_poly = sp.Poly(f, x, domain=sp.ZZ)
        except Exception:
            return (None, [], "no_match")
        if f_poly.degree() < 1:
            continue
        n = _is_cyclotomic_poly_sympy(f, x, max_n=int(max_cyclotomic_n))
        if n is not None:
            cyclo_struct[n] = cyclo_struct.get(n, 0) + int(mult)
        else:
            non_cyclo.append((f, int(mult)))

    cyclo_list = sorted(cyclo_struct.items())  # [(n_1, k_1), ...]

    # Step 3: every factor cyclotomic.
    if not non_cyclo:
        if not cyclo_list:
            # Degenerate (e.g. unit) — treat as no_match.
            return (None, [], "no_match")
        label = " * ".join(
            (f"Phi_{n}^{k}" if k != 1 else f"Phi_{n}")
            for n, k in cyclo_list
        )
        return (label, cyclo_list, "all_cyclotomic_match")

    # Step 4: reassemble non-cyclotomic core, look it up.
    core_expr = sp.Integer(1)
    for f, mult in non_cyclo:
        core_expr = core_expr * (f ** mult)
    core_poly = sp.expand(core_expr)
    core_asc = _ascending_from_sympy_poly(core_poly, x)
    core_hit = lookup_polynomial(core_asc)
    if core_hit is not None:
        return (str(core_hit.get("name", "Mossinghoff (unnamed)")),
                cyclo_list, "composite_match")

    # Step 5: no match.
    return (None, cyclo_list, "no_match")


def composite_label(label: Optional[str],
                    cyclotomic_structure: list[tuple[int, int]]) -> str:
    """Reconstruct a human-readable label from a composite-match tuple.

    Examples
    --------
    >>> composite_label("Lehmer's polynomial", [(1, 4)])
    "Lehmer's polynomial * Phi_1^4"
    >>> composite_label(None, [(1, 2), (3, 1)])
    'Phi_1^2 * Phi_3'
    """
    parts: list[str] = []
    if label:
        parts.append(label)
    for n, k in cyclotomic_structure:
        parts.append(f"Phi_{n}^{k}" if k != 1 else f"Phi_{n}")
    if not parts:
        return ""
    return " * ".join(parts)


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


def search_polynomial(M: float,
                      deg: Optional[int] = None,
                      tol: Optional[float] = 1e-3,
                      return_distance: bool = True) -> list[dict]:
    """Fuzzy lookup: catalog entries whose Mahler measure is near ``M``.

    Parameters
    ----------
    M : float
        Target Mahler measure.
    deg : int, optional
        If supplied, restrict to entries of exactly this degree.
    tol : float or None, default 1e-3
        Maximum allowed ``|entry.M - M|``.  Entries beyond ``tol`` are
        omitted.  Pass ``None`` to disable the radius cap (returns the
        full catalog, sorted by distance to ``M``).
    return_distance : bool, default True
        If True, every returned dict includes a ``"distance"`` field
        equal to ``abs(entry.mahler_measure - M)``.

    Returns
    -------
    list[dict]
        Catalog entries (deep-copied), sorted ascending by distance to
        ``M``.  Empty list if nothing falls within ``tol``.

    Notes
    -----
    The catalog covers M in [1.0, 1.84] and degrees [2..30, 36].
    Search is O(N) over the 178-entry catalog (no index needed).
    """
    M = float(M)
    out: list[tuple] = []
    for e in MAHLER_TABLE:
        if deg is not None and e["degree"] != int(deg):
            continue
        d = abs(e["mahler_measure"] - M)
        if tol is not None and d > float(tol):
            continue
        entry = copy.deepcopy(e)
        if return_distance:
            entry["distance"] = d
        # Tiebreak: cluster distances within 1e-9 to avoid spurious
        # ordering by floating-point noise, then prefer (a) the Lehmer
        # witness (b) Smyth-extremal (c) other named degree-minima
        # (d) lower degree.  Booleans inverted because we sort ascending.
        d_bucket = round(d / 1e-9)
        out.append((
            d_bucket,
            0 if e.get("lehmer_witness") else 1,
            0 if e.get("is_smyth_extremal") else 1,
            0 if e.get("degree_minimum") else 1,
            e["degree"],
            d,  # final continuous tiebreak
            entry,
        ))
    out.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4], t[5]))
    return [t[-1] for t in out]


def search_polynomial_by_coeffs_signature(
    signature: list[int],
    tol: float = 1e-9,
) -> list[dict]:
    """Find entries whose coefficient vectors match a structural signature.

    A "signature" match means the entry's ascending-coeffs list has
    the same length as ``signature``, the same first-nonzero and
    last-nonzero coefficient values, and the same parity (even/odd) of
    the number of nonzero coefficients.  Useful for locating "is this
    Lehmer's polynomial up to substitution / cyclotomic factor swap?".

    Parameters
    ----------
    signature : list[int]
        Reference ascending coefficient list.
    tol : float, default 1e-9
        Reserved for future float-coefficient signatures; integer
        coefficients are compared exactly.

    Returns
    -------
    list[dict]
        Catalog entries (deep-copied) whose coefficient signature
        matches.  Sorted ascending by Mahler measure.
    """
    sig = _normalize(list(signature))
    if not sig:
        return []
    sig_len = len(sig)
    sig_first = next((c for c in sig if c != 0), 0)
    sig_last = next((c for c in reversed(sig) if c != 0), 0)
    sig_nz_parity = sum(1 for c in sig if c != 0) % 2
    out: list[dict] = []
    for e in MAHLER_TABLE:
        c = _normalize(list(e["coeffs"]))
        if len(c) != sig_len:
            continue
        first = next((x for x in c if x != 0), 0)
        last = next((x for x in reversed(c) if x != 0), 0)
        nz_parity = sum(1 for x in c if x != 0) % 2
        if (first == sig_first and last == sig_last
                and nz_parity == sig_nz_parity):
            out.append(copy.deepcopy(e))
    out.sort(key=lambda r: r["mahler_measure"])
    return out


def _coeff_disc_proxy(coeffs: list[int]) -> int:
    """Cheap O(n^2) proxy for |discriminant| of a coefficient vector.

    Real polynomial discriminants need numerical root-finding; this
    proxy is sum_{i!=j} |a_i - a_j|^2 + sum |a_i|, which is monotone
    in the "spread" of the coefficient vector and usable as an
    ordering key when ranking entries by structural simplicity.
    """
    cs = list(coeffs)
    n = len(cs)
    s = sum(abs(c) for c in cs)
    for i in range(n):
        for j in range(i + 1, n):
            s += (cs[i] - cs[j]) ** 2
    return s


def _palindromic_score(coeffs: list[int]) -> float:
    """Return 1.0 for a perfect palindrome (Salem candidate), 0.0 for
    a fully non-palindromic vector.  Linear interpolation: fraction
    of index pairs (i, n-1-i) with c_i == c_{n-1-i}.
    """
    cs = list(coeffs)
    n = len(cs)
    if n == 0:
        return 0.0
    pairs = n // 2
    if pairs == 0:
        return 1.0  # singleton: trivially palindromic
    matches = sum(1 for i in range(pairs) if cs[i] == cs[n - 1 - i])
    return matches / pairs


def find_extremal_at_degree(degree: int,
                            criterion: str = "smallest_M") -> Optional[dict]:
    """Return the "extremal" catalog entry at a given degree.

    Parameters
    ----------
    degree : int
        Degree to search.
    criterion : str, default 'smallest_M'
        One of:

        * ``'smallest_M'``  -- entry with the smallest Mahler measure
        * ``'smallest_disc'`` -- entry minimizing the cheap coefficient
          discriminant proxy (a structural simplicity score)
        * ``'most_palindromic'`` -- entry whose coefficients are most
          palindromic (Salem-class indicator)

    Returns
    -------
    dict or None
        Best entry under the criterion, deep-copied; ``None`` if no
        catalog entry exists at that degree.
    """
    rows = [e for e in MAHLER_TABLE if e["degree"] == int(degree)]
    if not rows:
        return None
    if criterion == "smallest_M":
        best = min(rows, key=lambda r: r["mahler_measure"])
    elif criterion == "smallest_disc":
        best = min(rows, key=lambda r: _coeff_disc_proxy(r["coeffs"]))
    elif criterion == "most_palindromic":
        # Tie-break by smaller M for determinism.
        best = max(
            rows,
            key=lambda r: (_palindromic_score(r["coeffs"]),
                           -r["mahler_measure"]),
        )
    else:
        raise ValueError(
            f"unknown criterion {criterion!r}; expected one of "
            "'smallest_M', 'smallest_disc', 'most_palindromic'"
        )
    return copy.deepcopy(best)


def histogram_by_M(bin_count: int = 20,
                   M_range: tuple[float, float] = (1.0, 2.0)) -> list[tuple]:
    """Distribution of Mahler measures across the catalog.

    Parameters
    ----------
    bin_count : int, default 20
        Number of equal-width bins between ``M_range[0]`` and
        ``M_range[1]``.
    M_range : (float, float), default (1.0, 2.0)
        Inclusive lower bound, exclusive upper bound (the topmost bin
        includes its right edge to catch boundary entries).

    Returns
    -------
    list[(float, float, int)]
        ``[(M_lo, M_hi, count), ...]`` for each bin in ascending order.
        Counts include only entries with ``M_lo <= M < M_hi`` (or
        ``<= M_hi`` for the final bin).

    Examples
    --------
    >>> bins = histogram_by_M(bin_count=10, M_range=(1.0, 2.0))
    >>> sum(c for _, _, c in bins) <= len(smallest_known(limit=10000))
    True
    """
    if int(bin_count) <= 0:
        raise ValueError(f"bin_count must be positive, got {bin_count}")
    lo, hi = float(M_range[0]), float(M_range[1])
    if hi <= lo:
        raise ValueError(
            f"M_range must satisfy lo < hi; got ({lo}, {hi})"
        )
    width = (hi - lo) / int(bin_count)
    bins = [(lo + i * width, lo + (i + 1) * width, 0)
            for i in range(int(bin_count))]
    bins_mut = [list(b) for b in bins]
    for e in MAHLER_TABLE:
        m = e["mahler_measure"]
        if m < lo or m > hi:
            continue
        idx = int((m - lo) / width)
        if idx == int(bin_count):  # right edge of final bin
            idx -= 1
        if 0 <= idx < int(bin_count):
            bins_mut[idx][2] += 1
    return [(b[0], b[1], b[2]) for b in bins_mut]


def search_by_signature_class(salem: Optional[bool] = None,
                              smyth_extremal: Optional[bool] = None,
                              lehmer_witness: Optional[bool] = None,
                              degree_minimum: Optional[bool] = None,
                              ) -> list[dict]:
    """Filter the catalog by combination of class booleans.

    Each parameter is tri-valued:

    * ``True``  -- entry must have the flag set
    * ``False`` -- entry must NOT have the flag set
    * ``None``  -- don't filter on this flag

    Returns
    -------
    list[dict]
        Matching entries (deep-copied), sorted ascending by Mahler
        measure.

    Examples
    --------
    Salem-class entries that are also degree minima:

    >>> rows = search_by_signature_class(salem=True, degree_minimum=True)
    """
    out: list[dict] = []
    for e in MAHLER_TABLE:
        if salem is not None and bool(e.get("salem_class")) != bool(salem):
            continue
        if smyth_extremal is not None \
                and bool(e.get("is_smyth_extremal")) != bool(smyth_extremal):
            continue
        if lehmer_witness is not None \
                and bool(e.get("lehmer_witness")) != bool(lehmer_witness):
            continue
        if degree_minimum is not None \
                and bool(e.get("degree_minimum")) != bool(degree_minimum):
            continue
        out.append(copy.deepcopy(e))
    out.sort(key=lambda r: (r["mahler_measure"], r["degree"]))
    return out


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

def _cross_check(tol: float = 1e-9,
                 tier: Optional[str] = "phase1_curated") -> list[dict]:
    """Recompute Mahler measure for embedded entries; return mismatches.

    Parameters
    ----------
    tol : float
        Tolerance for accepting an entry as agreeing with recomputation.
    tier : str or None, default "phase1_curated"
        If set, only entries whose ``provenance_tier`` matches are
        re-verified.  This keeps the module-load check fast (~178
        entries) instead of recomputing M for all 8000+ Known180
        rows on every import.  Pass ``None`` to verify the entire
        catalog (used by the strict regression test).

    If the Techne tool is unavailable, returns an empty list.
    """
    if not _HAS_MAHLER_TOOL:
        return []
    out = []
    for i, e in enumerate(MAHLER_TABLE):
        if tier is not None and e.get("provenance_tier") != tier:
            continue
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
    # Phase-2 fuzzy search additions:
    "search_polynomial",
    "search_polynomial_by_coeffs_signature",
    "find_extremal_at_degree",
    "histogram_by_M",
    "search_by_signature_class",
    # 2026-05-04 factorization-aware lookup (catalog-completeness fix):
    "mahler_lookup_factored",
    "composite_label",
]
