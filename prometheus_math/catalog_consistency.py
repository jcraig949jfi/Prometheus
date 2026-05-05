"""prometheus_math.catalog_consistency — multi-catalog cross-check (§6.3).

Implements §6.3 of `harmonia/memory/architecture/discovery_via_rediscovery.md`:

    "Multi-catalog cross-check (Techne's lane). Currently
    discovery_env.py checks Mossinghoff only. Production discovery work
    requires LMFDB + OEIS + arXiv-title fuzzy match + Lehmer-literature
    catalog (Boyd, Smyth, Mossinghoff, Borwein-Mossinghoff). Techne forges
    the tool; each external catalog becomes a typed
    catalog_consistency_check@v1 that EVAL through the substrate."

Architectural shape
-------------------
Five typed catalog adapters, all sharing the
``(coeffs, mahler_measure, tol) -> CatalogResult`` signature:

  * ``mossinghoff_check``  — embedded Mossinghoff snapshot (always live)
  * ``lmfdb_check``        — Postgres mirror at devmirror.lmfdb.xyz
                             (skip-cleanly if unreachable)
  * ``oeis_check``         — OEIS coefficient-sequence match
                             (skip-cleanly if unreachable)
  * ``arxiv_title_fuzzy_check`` — recent arXiv "Mahler measure" /
                             "Salem polynomial" titles, M-fuzzy match
                             (skip-cleanly if unreachable; heuristic)
  * ``lehmer_literature_check`` — embedded snapshot from Boyd, Smyth,
                             Borwein-Mossinghoff (always live)

The orchestrator ``run_consistency_check(coeffs, m_value)`` runs all
five and returns ``{by_catalog, any_hit, hits, unanimous_miss, errors}``.

Honest framing
--------------
``unanimous_miss = True`` is a STRONGER novelty signal than
"missing in Mossinghoff alone", but is **not** a positive verification of
novelty.  A polynomial absent from N consulted catalogs is more likely
genuinely new than one absent from one catalog, but the negative-evidence
shape doesn't change: catalog-miss in N sources is bounded above by the
union of their coverage.  Lehmer's conjecture is still open precisely
because we cannot verify what's NOT in any catalog.

This is captured explicitly in CATALOG_CONSISTENCY_NOTES.md.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CatalogResult:
    """Typed result from one catalog adapter.

    Fields
    ------
    catalog_name : str
        Identifier of the catalog (e.g. "Mossinghoff", "LMFDB",
        "OEIS", "arXiv", "lehmer_literature").
    query_kind : str
        How the catalog was queried ("M_value", "coeff_sequence",
        "title_fuzzy", "polynomial_match").
    hit : bool
        True iff the polynomial / its M-value / a related signature
        matches a catalog entry within the catalog's tolerance.
    match_label : Optional[str]
        Short identifier of the matching catalog entry (e.g. an LMFDB
        label, an OEIS A-number, the literature label).  None on miss.
    match_distance : Optional[float]
        Distance metric of the match.  For M-value matches, ``|stored
        - observed|``.  For sequence matches, ``0.0`` on exact match,
        else ``None``.
    query_runtime_ms : float
        Wall-clock time the adapter spent.  Always >= 0.
    error : Optional[str]
        Typed error string if the catalog could not be reached.  An
        adapter that errors out emits ``hit=False`` and a non-None
        ``error`` field; the orchestrator treats this as "skip with
        warning", NOT as a miss.
    """

    catalog_name: str
    query_kind: str
    hit: bool
    match_label: Optional[str] = None
    match_distance: Optional[float] = None
    query_runtime_ms: float = 0.0
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Common validation
# ---------------------------------------------------------------------------


def _validate_inputs(coeffs: List[int], m_value: float) -> None:
    """Shared input validation for all adapters."""
    if not coeffs:
        raise ValueError("coeffs must be a non-empty list of integers")
    if not isinstance(m_value, (int, float)):
        raise ValueError(f"m_value must be a number, got {type(m_value).__name__}")
    if m_value < 0:
        raise ValueError(f"m_value must be >= 0, got {m_value}")
    if not math.isfinite(m_value):
        raise ValueError(f"m_value must be finite, got {m_value}")


# ---------------------------------------------------------------------------
# Adapter: Mossinghoff (always live; embedded snapshot)
# ---------------------------------------------------------------------------


def mossinghoff_check(
    coeffs: List[int],
    m_value: float,
    tol: float = 1e-5,
) -> CatalogResult:
    """Check a polynomial against the embedded Mossinghoff snapshot.

    Refactor of the original ``_check_catalog_miss`` from
    ``discovery_pipeline.py``: same matching semantics (exact M within
    ``tol``), now returning a typed ``CatalogResult``.

    The Mossinghoff snapshot is bundled at
    ``prometheus_math.databases._mahler_data.MAHLER_TABLE`` and is
    ALWAYS available; this adapter cannot raise a connection error.
    """
    _validate_inputs(coeffs, m_value)
    t0 = time.monotonic()
    try:
        from prometheus_math.databases import mahler as _mahler_db
    except Exception as e:  # pragma: no cover -- defensive
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="Mossinghoff",
            query_kind="M_value",
            hit=False,
            error=f"import_failed: {type(e).__name__}: {e}",
            query_runtime_ms=rt,
        )

    snapshot = getattr(_mahler_db, "MAHLER_TABLE", None) or []
    best: Optional[dict] = None
    best_dist = float("inf")
    for entry in snapshot:
        try:
            entry_m = float(entry.get("mahler_measure", float("inf")))
        except (TypeError, ValueError):
            continue
        d = abs(entry_m - m_value)
        if d < tol and d < best_dist:
            best = entry
            best_dist = d

    rt = (time.monotonic() - t0) * 1000.0
    if best is not None:
        label = best.get("name") or best.get("label") or "?"
        return CatalogResult(
            catalog_name="Mossinghoff",
            query_kind="M_value",
            hit=True,
            match_label=str(label),
            match_distance=best_dist,
            query_runtime_ms=rt,
        )
    return CatalogResult(
        catalog_name="Mossinghoff",
        query_kind="M_value",
        hit=False,
        query_runtime_ms=rt,
    )


# ---------------------------------------------------------------------------
# Adapter: LMFDB (skip-cleanly if unreachable)
# ---------------------------------------------------------------------------


def lmfdb_check(
    coeffs: List[int],
    m_value: float,
    tol: float = 1e-5,
    timeout: int = 5,
) -> CatalogResult:
    """Check whether the polynomial appears as a defining polynomial of
    a number field in LMFDB's ``nf_fields`` table.

    Query strategy: probe by ``coeffs`` exact match.  LMFDB stores
    polredabs-canonicalized coefficient vectors, so the match is exact
    iff our polynomial is already in polredabs form.  We do NOT polredabs
    ourselves here (that's a heavyweight cypari operation); the false-
    negative rate is acceptable for a multi-catalog gate (the other
    catalogs cover the polredabs-flip cases).

    On any connection error, returns ``CatalogResult(hit=False,
    error=...)``.  The orchestrator treats this as skip-with-warning.
    """
    _validate_inputs(coeffs, m_value)
    t0 = time.monotonic()
    try:
        from prometheus_math.databases import lmfdb as _lmfdb
    except Exception as e:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="LMFDB",
            query_kind="polynomial_match",
            hit=False,
            error=f"import_failed: {type(e).__name__}: {e}",
            query_runtime_ms=rt,
        )

    # Cheap reachability check.  If the mirror is down we don't even
    # try the query.
    try:
        reachable = bool(_lmfdb.probe(timeout=float(timeout)))
    except Exception as e:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="LMFDB",
            query_kind="polynomial_match",
            hit=False,
            error=f"probe_failed: {type(e).__name__}: {e}",
            query_runtime_ms=rt,
        )
    if not reachable:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="LMFDB",
            query_kind="polynomial_match",
            hit=False,
            error="lmfdb_unreachable",
            query_runtime_ms=rt,
        )

    # nf_fields stores ascending coefficient lists in the "coeffs"
    # column as numeric[].  We search by exact match.  Use a small
    # parameterized query rather than the curated number_fields()
    # accessor so we don't pull a 1000-row scan.  Cast %s::numeric[]
    # because LMFDB's "coeffs" column is numeric[] and psycopg2's
    # default int-list mapping doesn't unify implicitly.
    try:
        rows = _lmfdb.query_dicts(
            'SELECT "label", "coeffs", "degree", "disc_abs" FROM "nf_fields" '
            'WHERE "coeffs" = %s::numeric[] LIMIT 5',
            params=(list(coeffs),),
            timeout=timeout,
        )
    except Exception as e:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="LMFDB",
            query_kind="polynomial_match",
            hit=False,
            error=f"query_failed: {type(e).__name__}: {e}",
            query_runtime_ms=rt,
        )

    rt = (time.monotonic() - t0) * 1000.0
    if rows:
        first = rows[0]
        return CatalogResult(
            catalog_name="LMFDB",
            query_kind="polynomial_match",
            hit=True,
            match_label=str(first.get("label", "?")),
            match_distance=0.0,
            query_runtime_ms=rt,
        )
    return CatalogResult(
        catalog_name="LMFDB",
        query_kind="polynomial_match",
        hit=False,
        query_runtime_ms=rt,
    )


# ---------------------------------------------------------------------------
# Adapter: OEIS (skip-cleanly if unreachable)
# ---------------------------------------------------------------------------


def oeis_check(
    coeffs: List[int],
    m_value: float,
    tol: float = 1e-5,
    timeout: int = 10,
) -> CatalogResult:
    """Check whether the coefficient sequence appears in OEIS.

    OEIS doesn't index Mahler measures directly, but it DOES index
    polynomial coefficient sequences (e.g. "coefficients of polynomial
    P(x)" sequences are frequent).  If our coefficient list (interpreted
    as an integer sequence) matches an OEIS sequence, that's strong
    evidence the polynomial is "known".

    This adapter uses ``oeis.is_known(values)``: returns the matching
    A-number on hit, None on miss.  Any network or parsing error yields
    ``CatalogResult(hit=False, error=...)``.
    """
    _validate_inputs(coeffs, m_value)
    t0 = time.monotonic()
    try:
        from prometheus_math.databases import oeis as _oeis
    except Exception as e:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="OEIS",
            query_kind="coeff_sequence",
            hit=False,
            error=f"import_failed: {type(e).__name__}: {e}",
            query_runtime_ms=rt,
        )

    # OEIS won't match against trivial sequences (all zero / all one);
    # short-circuit those to avoid wasting an API hit.
    nz = [c for c in coeffs if c != 0]
    if len(nz) < 3:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="OEIS",
            query_kind="coeff_sequence",
            hit=False,
            error="trivial_sequence:not_searchable",
            query_runtime_ms=rt,
        )

    try:
        # is_known returns A-number on hit, None on miss.
        a_number = _oeis.is_known(coeffs)
    except Exception as e:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="OEIS",
            query_kind="coeff_sequence",
            hit=False,
            error=f"oeis_unreachable: {type(e).__name__}: {e}",
            query_runtime_ms=rt,
        )

    rt = (time.monotonic() - t0) * 1000.0
    if a_number:
        return CatalogResult(
            catalog_name="OEIS",
            query_kind="coeff_sequence",
            hit=True,
            match_label=str(a_number),
            match_distance=0.0,
            query_runtime_ms=rt,
        )
    return CatalogResult(
        catalog_name="OEIS",
        query_kind="coeff_sequence",
        hit=False,
        query_runtime_ms=rt,
    )


# ---------------------------------------------------------------------------
# Adapter: arXiv title fuzzy (skip-cleanly if unreachable)
# ---------------------------------------------------------------------------


def arxiv_title_fuzzy_check(
    coeffs: List[int],
    m_value: float,
    m_tol: float = 1e-3,
    max_results: int = 30,
) -> CatalogResult:
    """Heuristic: search recent arXiv titles for "Mahler measure" or
    "Salem polynomial", then check whether any abstract/comment mentions
    a numerical M-value within ``m_tol`` of ours.

    HEURISTIC, not a real catalog query.  Documented limitations:

    * arXiv abstracts rarely quote M-values to high precision; the
      hit rate is consequently low.
    * The third-party ``arxiv`` Python client adds ~3s latency per call
      by design (rate-limit compliance), so this is an EXPENSIVE check.
    * If the network is unreachable or the client returns an empty
      result list, we emit ``error="arxiv_unreachable"`` and skip with
      warning.

    The MVP is skip-with-warning the vast majority of the time; we keep
    the structure in place for §6.3-2 (full-text indexing) follow-up.
    """
    _validate_inputs(coeffs, m_value)
    t0 = time.monotonic()
    try:
        from prometheus_math.databases import arxiv as _arxiv
    except Exception as e:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="arXiv",
            query_kind="title_fuzzy",
            hit=False,
            error=f"import_failed: {type(e).__name__}: {e}",
            query_runtime_ms=rt,
        )

    # Cheap reachability check.  arxiv.probe is itself a network hit.
    try:
        reachable = bool(_arxiv.probe(timeout=3.0))
    except Exception as e:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="arXiv",
            query_kind="title_fuzzy",
            hit=False,
            error=f"probe_failed: {type(e).__name__}: {e}",
            query_runtime_ms=rt,
        )
    if not reachable:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="arXiv",
            query_kind="title_fuzzy",
            hit=False,
            error="arxiv_unreachable",
            query_runtime_ms=rt,
        )

    # Search recent papers with relevant titles.
    query = "ti:\"Mahler measure\" OR ti:\"Salem polynomial\""
    try:
        results = _arxiv.search(query, max_results=max_results,
                                sort_by="submittedDate")
    except Exception as e:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="arXiv",
            query_kind="title_fuzzy",
            hit=False,
            error=f"search_failed: {type(e).__name__}: {e}",
            query_runtime_ms=rt,
        )

    if not results:
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="arXiv",
            query_kind="title_fuzzy",
            hit=False,
            error="arxiv_empty_results",
            query_runtime_ms=rt,
        )

    # Heuristic abstract scan: look for a numerical token within m_tol
    # of m_value.  This is intentionally simple — the MVP catches "M = 1.176..."
    # style mentions, nothing fancier.
    import re
    num_re = re.compile(r"\b(\d+\.\d{3,})\b")
    target = float(m_value)
    for paper in results:
        text = " ".join([
            str(paper.get("title", "")),
            str(paper.get("abstract", "")),
            str(paper.get("comment", "")),
        ])
        for match in num_re.finditer(text):
            try:
                v = float(match.group(1))
            except ValueError:
                continue
            if abs(v - target) < m_tol:
                rt = (time.monotonic() - t0) * 1000.0
                return CatalogResult(
                    catalog_name="arXiv",
                    query_kind="title_fuzzy",
                    hit=True,
                    match_label=str(paper.get("id", "?")),
                    match_distance=abs(v - target),
                    query_runtime_ms=rt,
                )

    rt = (time.monotonic() - t0) * 1000.0
    return CatalogResult(
        catalog_name="arXiv",
        query_kind="title_fuzzy",
        hit=False,
        query_runtime_ms=rt,
    )


# ---------------------------------------------------------------------------
# Adapter: Lehmer literature (always live; embedded snapshot)
# ---------------------------------------------------------------------------


def lehmer_literature_check(
    coeffs: List[int],
    m_value: float,
    tol: float = 1e-5,
) -> CatalogResult:
    """Check a polynomial against the embedded Lehmer-literature snapshot.

    The snapshot at
    ``prometheus_math._lehmer_literature_data.LEHMER_LITERATURE_TABLE``
    aggregates 24 hand-curated entries from Boyd 1980 / 1981 / 1989,
    Smyth 1971, Lehmer 1933, Mossinghoff 1998, and Borwein-Mossinghoff
    2007.  Each entry's M was independently verified at table-build
    time.

    Match policy:
    * Try exact coefficient match (with the x -> -x flip, which preserves M).
    * Else match by M-value within ``tol``.
    * Prefer coefficient-match over M-match when both apply; the
      former is structurally stronger.

    The literature snapshot is bundled with this module and is ALWAYS
    available; this adapter cannot raise a connection error.
    """
    _validate_inputs(coeffs, m_value)
    t0 = time.monotonic()
    try:
        from prometheus_math._lehmer_literature_data import (
            LEHMER_LITERATURE_TABLE,
        )
    except Exception as e:  # pragma: no cover -- defensive
        rt = (time.monotonic() - t0) * 1000.0
        return CatalogResult(
            catalog_name="lehmer_literature",
            query_kind="polynomial_match",
            hit=False,
            error=f"import_failed: {type(e).__name__}: {e}",
            query_runtime_ms=rt,
        )

    target = list(coeffs)
    target_flip = [c if (i % 2 == 0) else -c for i, c in enumerate(target)]

    # Phase 1: coefficient-match (strongest).
    for entry in LEHMER_LITERATURE_TABLE:
        ec = list(entry["polynomial_coeffs"])
        if ec == target or ec == target_flip:
            rt = (time.monotonic() - t0) * 1000.0
            return CatalogResult(
                catalog_name="lehmer_literature",
                query_kind="polynomial_match",
                hit=True,
                match_label=str(entry["label"]),
                match_distance=0.0,
                query_runtime_ms=rt,
            )

    # Phase 2: M-value match within tol.
    best: Optional[dict] = None
    best_dist = float("inf")
    for entry in LEHMER_LITERATURE_TABLE:
        try:
            em = float(entry["m_value"])
        except (TypeError, ValueError):
            continue
        d = abs(em - m_value)
        if d < tol and d < best_dist:
            best = entry
            best_dist = d

    rt = (time.monotonic() - t0) * 1000.0
    if best is not None:
        return CatalogResult(
            catalog_name="lehmer_literature",
            query_kind="M_value",
            hit=True,
            match_label=str(best["label"]),
            match_distance=best_dist,
            query_runtime_ms=rt,
        )
    return CatalogResult(
        catalog_name="lehmer_literature",
        query_kind="M_value",
        hit=False,
        query_runtime_ms=rt,
    )


# ---------------------------------------------------------------------------
# Default catalog registry
# ---------------------------------------------------------------------------


# Adapter signature: (coeffs, m_value, tol) -> CatalogResult.
# arXiv fuzzy uses m_tol (not tol); we wrap below to share the signature.

CatalogAdapter = Callable[[List[int], float, float], CatalogResult]


def _arxiv_wrapper(
    coeffs: List[int], m_value: float, tol: float = 1e-3
) -> CatalogResult:
    """Adapter signature wrapper around arxiv_title_fuzzy_check."""
    return arxiv_title_fuzzy_check(coeffs, m_value, m_tol=tol)


DEFAULT_CATALOGS: Dict[str, CatalogAdapter] = {
    "Mossinghoff": mossinghoff_check,
    "lehmer_literature": lehmer_literature_check,
    "LMFDB": lmfdb_check,
    "OEIS": oeis_check,
    "arXiv": _arxiv_wrapper,
}


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


@dataclass
class CatalogConsistencyCheck:
    """Run a polynomial through a configured set of catalog adapters.

    The default registry consults all five adapters above.  Pass
    ``catalogs=`` to restrict to a subset (e.g. ``["Mossinghoff",
    "lehmer_literature"]`` for fast offline checks).
    """

    catalogs: Dict[str, CatalogAdapter] = field(
        default_factory=lambda: dict(DEFAULT_CATALOGS)
    )
    tol: float = 1e-5

    def run(self, coeffs: List[int], m_value: float) -> Dict[str, Any]:
        """Run the check; return the aggregated result."""
        return run_consistency_check(
            coeffs, m_value, catalogs=self.catalogs, tol=self.tol
        )


def run_consistency_check(
    coeffs: List[int],
    m_value: float,
    catalogs: Optional[Dict[str, CatalogAdapter]] = None,
    tol: float = 1e-5,
) -> Dict[str, Any]:
    """Run a polynomial through all configured catalogs and aggregate.

    Parameters
    ----------
    coeffs : list[int]
        Ascending integer coefficients.
    m_value : float
        Mahler measure (>= 0, finite).
    catalogs : dict[str, CatalogAdapter], optional
        Adapter registry.  Defaults to ``DEFAULT_CATALOGS`` (all five).
        Pass ``{}`` to vacuously skip every catalog (returns
        ``unanimous_miss=True`` with explicit warning).
    tol : float, default 1e-5
        Tolerance passed to each adapter.

    Returns
    -------
    dict with keys:
      * ``by_catalog``: ``dict[name, CatalogResult]``
      * ``any_hit``: ``bool`` — did ANY catalog flag a hit?
      * ``hits``: ``list[CatalogResult]`` — the hits, ordered by
        catalog-registry order
      * ``unanimous_miss``: ``bool`` — did EVERY catalog miss (errors
        and skip-with-warning DO count as miss for this aggregate, but
        are also surfaced in ``errors``)
      * ``errors``: ``list[CatalogResult]`` — adapter results with
        non-None ``error`` field
      * ``catalogs_checked``: ``list[str]`` — catalog names actually
        consulted
      * ``warning``: ``Optional[str]`` — set when ``catalogs={}``
    """
    _validate_inputs(coeffs, m_value)

    registry = DEFAULT_CATALOGS if catalogs is None else dict(catalogs)

    by_catalog: Dict[str, CatalogResult] = {}
    hits: List[CatalogResult] = []
    errors: List[CatalogResult] = []
    catalogs_checked: List[str] = []
    warning: Optional[str] = None

    if not registry:
        warning = (
            "no catalogs consulted (empty registry); unanimous_miss is "
            "vacuously True — interpret as zero evidence rather than "
            "novelty"
        )

    for name, adapter in registry.items():
        catalogs_checked.append(name)
        try:
            result = adapter(coeffs, m_value, tol)
        except Exception as e:
            # Adapter contract is "skip-with-warning, never raise"; if
            # an adapter raises we wrap it ourselves so the orchestrator
            # never propagates.
            result = CatalogResult(
                catalog_name=name,
                query_kind="?",
                hit=False,
                error=f"adapter_raised: {type(e).__name__}: {e}",
                query_runtime_ms=0.0,
            )
        by_catalog[name] = result
        if result.error is not None:
            errors.append(result)
        if result.hit:
            hits.append(result)

    any_hit = bool(hits)
    unanimous_miss = not any_hit

    return {
        "by_catalog": by_catalog,
        "any_hit": any_hit,
        "hits": hits,
        "unanimous_miss": unanimous_miss,
        "errors": errors,
        "catalogs_checked": catalogs_checked,
        "warning": warning,
    }


__all__ = [
    "CatalogResult",
    "CatalogConsistencyCheck",
    "mossinghoff_check",
    "lmfdb_check",
    "oeis_check",
    "arxiv_title_fuzzy_check",
    "lehmer_literature_check",
    "run_consistency_check",
    "DEFAULT_CATALOGS",
]
