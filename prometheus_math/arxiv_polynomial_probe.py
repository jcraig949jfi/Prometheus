"""prometheus_math.arxiv_polynomial_probe — rediscovery benchmark.

Runs the multi-catalog cross-check (``catalog_consistency.py``) against
``RECENT_POLYNOMIAL_CORPUS`` and reports per-entry hit patterns plus
aggregate hit-rate statistics.

The benchmark is qualitative-direction: the corpus is small (~17
entries), so per-catalog hit rates have wide error bars.  The
substantive output is **the structure**:

  * Which catalogs catch which entries.
  * Which entries no catalog catches (the genuinely-uncaught real-
    world signals).
  * Which entries multiple catalogs catch (calibration anchors).
  * Where the agent's predicted hit pattern disagrees with the actual
    pattern (surprises).

CLI
---
    python -m prometheus_math.arxiv_polynomial_probe

Prints the per-entry table and the aggregate summary.  Live LMFDB /
OEIS / arXiv calls are made; if any are unreachable, the relevant
catalog is reported as "skip" rather than as a miss.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from prometheus_math._arxiv_polynomial_corpus import (
    RECENT_POLYNOMIAL_CORPUS,
    RecentPolynomialEntry,
)
from prometheus_math.catalog_consistency import (
    CatalogResult,
    DEFAULT_CATALOGS,
    run_consistency_check,
)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class ProbeResult:
    """Result of running the catalog cross-check on one corpus entry.

    Fields
    ------
    entry : RecentPolynomialEntry
        The original corpus entry.
    actual_hits : dict[str, bool]
        For each catalog name, whether the live cross-check returned
        ``hit=True``.  Catalogs with errors (e.g. LMFDB unreachable)
        are recorded as ``False`` here AND tagged in ``errors`` below.
    actual_results : dict[str, CatalogResult]
        The full per-catalog ``CatalogResult`` (including ``error`` and
        ``match_label`` fields), for downstream auditability.
    expected_hits : dict[str, object]
        The agent's prediction (from ``entry.expected_catalog_hits``).
        Values are ``True``, ``False``, or the string ``"Maybe"``.
    agreement : dict[str, str]
        For each catalog name, one of:
          * ``"agree"``   — predicted matches actual (or predicted "Maybe"
                            and actual is well-defined)
          * ``"surprise:false_negative"`` — predicted hit, actual miss
          * ``"surprise:false_positive"`` — predicted miss, actual hit
    surprises : list[str]
        Catalog names where ``agreement[name]`` starts with ``"surprise"``.
    errors : list[str]
        Catalog names whose ``actual_results[name].error`` is non-None.
    """

    entry: RecentPolynomialEntry
    actual_hits: Dict[str, bool]
    actual_results: Dict[str, CatalogResult]
    expected_hits: Dict[str, object]
    agreement: Dict[str, str]
    surprises: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core probe
# ---------------------------------------------------------------------------


def _agreement_label(predicted: object, actual: bool) -> str:
    """Three-state agreement classifier.

    ``predicted`` is True / False / "Maybe".  ``actual`` is the
    cross-check's hit verdict (True / False).  Returns one of
    ``"agree"``, ``"surprise:false_negative"`` (predicted True but
    actual False), ``"surprise:false_positive"`` (predicted False but
    actual True), or ``"agree-maybe"`` (predicted "Maybe", any actual).
    """
    if predicted == "Maybe":
        return "agree-maybe"
    if predicted is True and actual is False:
        return "surprise:false_negative"
    if predicted is False and actual is True:
        return "surprise:false_positive"
    return "agree"


def probe_recent_polynomials(
    corpus: Optional[List[RecentPolynomialEntry]] = None,
    catalogs: Optional[Dict[str, Any]] = None,
    tol: float = 1e-5,
) -> List[ProbeResult]:
    """Run the multi-catalog cross-check on each corpus entry.

    Parameters
    ----------
    corpus : list[RecentPolynomialEntry], optional
        Defaults to ``RECENT_POLYNOMIAL_CORPUS``.
    catalogs : dict, optional
        Catalog adapter registry.  Defaults to ``DEFAULT_CATALOGS`` (all
        five).  Pass a subset to do an offline-only probe in tests.
    tol : float, default 1e-5
        Tolerance forwarded to each adapter.

    Returns
    -------
    list[ProbeResult]
        One per corpus entry, in input order.
    """
    if corpus is None:
        corpus = RECENT_POLYNOMIAL_CORPUS
    if catalogs is None:
        catalogs = dict(DEFAULT_CATALOGS)

    out: List[ProbeResult] = []
    for entry in corpus:
        cc = run_consistency_check(
            entry.coeffs, entry.mahler_measure, catalogs=catalogs, tol=tol
        )
        actual_results: Dict[str, CatalogResult] = cc["by_catalog"]
        actual_hits: Dict[str, bool] = {
            name: bool(r.hit) for name, r in actual_results.items()
        }

        expected = dict(entry.expected_catalog_hits)
        agreement: Dict[str, str] = {}
        surprises: List[str] = []
        errors: List[str] = []
        for name in actual_results:
            pred = expected.get(name, "Maybe")
            label = _agreement_label(pred, actual_hits.get(name, False))
            agreement[name] = label
            if label.startswith("surprise"):
                surprises.append(name)
            if actual_results[name].error is not None:
                errors.append(name)

        out.append(
            ProbeResult(
                entry=entry,
                actual_hits=actual_hits,
                actual_results=actual_results,
                expected_hits=expected,
                agreement=agreement,
                surprises=surprises,
                errors=errors,
            )
        )
    return out


def summarize_probe(results: List[ProbeResult]) -> Dict[str, Any]:
    """Aggregate-statistics summary of a list of ``ProbeResult``.

    Returns a dict with:
      * ``n_entries``: total corpus size probed.
      * ``per_catalog_hit_count``: dict[name, int] — how many entries
        each catalog flagged with hit=True.
      * ``per_catalog_hit_rate``: dict[name, float] — same /n_entries.
      * ``per_catalog_error_count``: dict[name, int] — how many entries
        had a non-None error in this catalog (skipped).
      * ``entries_with_zero_hits``: list[arxiv_id] — entries no catalog
        caught.
      * ``entries_with_multi_hits``: list[(arxiv_id, n_hits)] — entries
        flagged by 2+ catalogs.
      * ``surprise_count``: int — total (entry, catalog) pairs flagged
        as surprises (excluding "Maybe" predictions).
      * ``surprises_by_catalog``: dict[name, int].
    """
    n = len(results)
    if n == 0:
        return {
            "n_entries": 0,
            "per_catalog_hit_count": {},
            "per_catalog_hit_rate": {},
            "per_catalog_error_count": {},
            "entries_with_zero_hits": [],
            "entries_with_multi_hits": [],
            "surprise_count": 0,
            "surprises_by_catalog": {},
        }

    catalog_names: List[str] = list(results[0].actual_hits.keys())
    hit_counts = {c: 0 for c in catalog_names}
    err_counts = {c: 0 for c in catalog_names}
    surprise_counts = {c: 0 for c in catalog_names}
    zero_hit_entries: List[str] = []
    multi_hit_entries: List[tuple] = []
    surprise_total = 0

    for res in results:
        n_hits_this = sum(1 for v in res.actual_hits.values() if v)
        if n_hits_this == 0:
            zero_hit_entries.append(res.entry.paper_arxiv_id)
        elif n_hits_this >= 2:
            multi_hit_entries.append((res.entry.paper_arxiv_id, n_hits_this))
        for c in catalog_names:
            if res.actual_hits.get(c, False):
                hit_counts[c] += 1
            if c in res.errors:
                err_counts[c] += 1
            if c in res.surprises:
                surprise_counts[c] += 1
                surprise_total += 1

    hit_rates = {c: hit_counts[c] / n for c in catalog_names}

    return {
        "n_entries": n,
        "per_catalog_hit_count": hit_counts,
        "per_catalog_hit_rate": hit_rates,
        "per_catalog_error_count": err_counts,
        "entries_with_zero_hits": zero_hit_entries,
        "entries_with_multi_hits": multi_hit_entries,
        "surprise_count": surprise_total,
        "surprises_by_catalog": surprise_counts,
    }


# ---------------------------------------------------------------------------
# Pretty-print helpers (CLI)
# ---------------------------------------------------------------------------


def _format_per_entry_row(res: ProbeResult, catalog_names: List[str]) -> str:
    deg = len(res.entry.coeffs) - 1
    short_id = res.entry.paper_arxiv_id
    cells = []
    for c in catalog_names:
        actual = res.actual_hits.get(c, False)
        err = c in res.errors
        if err:
            cells.append("skip")
        elif actual:
            label = res.actual_results[c].match_label or "?"
            # Cap label length so the row doesn't blow out terminal width.
            label = label if len(label) <= 18 else label[:15] + "..."
            cells.append(f"HIT[{label}]")
        else:
            cells.append("miss")
    n_hits = sum(1 for v in res.actual_hits.values() if v)
    return (
        f"deg={deg:>3}  M={res.entry.mahler_measure:.6f}  "
        f"{short_id:<10}  hits={n_hits}  | "
        + " | ".join(f"{c:>17}: {v:<24}" for c, v in zip(catalog_names, cells))
    )


def format_per_entry_table(results: List[ProbeResult]) -> str:
    if not results:
        return "(empty)"
    catalog_names = list(results[0].actual_hits.keys())
    lines = [
        "Per-entry catalog cross-check results",
        "-" * 72,
    ]
    for res in results:
        lines.append(_format_per_entry_row(res, catalog_names))
        # Show surprises in a sub-line for readability.
        if res.surprises:
            sur = ", ".join(
                f"{c}({res.agreement[c]})" for c in res.surprises
            )
            lines.append(f"      surprises: {sur}")
    return "\n".join(lines)


def format_summary(summary: Dict[str, Any]) -> str:
    n = summary["n_entries"]
    if n == 0:
        return "Empty probe."
    lines = ["", "Aggregate summary", "-" * 72,
             f"  Entries probed: {n}", "  Per-catalog hit rates:"]
    for c, rate in summary["per_catalog_hit_rate"].items():
        cnt = summary["per_catalog_hit_count"][c]
        err = summary["per_catalog_error_count"][c]
        lines.append(f"    {c:>17}: {cnt:>3}/{n} = {rate*100:5.1f}%   "
                     f"(errors: {err})")
    lines.append(
        f"  Entries with ZERO catalog hits: {len(summary['entries_with_zero_hits'])} "
        f"({summary['entries_with_zero_hits']})"
    )
    lines.append(
        f"  Entries with MULTIPLE catalog hits: "
        f"{len(summary['entries_with_multi_hits'])} "
        f"({summary['entries_with_multi_hits']})"
    )
    lines.append(
        f"  Total surprises (excluding 'Maybe'): {summary['surprise_count']}  "
        f"by catalog: {summary['surprises_by_catalog']}"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the catalog cross-check on the recent-arXiv polynomial "
            "corpus and report results."
        )
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help=(
            "Use only the offline catalogs (Mossinghoff + lehmer_literature). "
            "Skips LMFDB / OEIS / arXiv live calls."
        ),
    )
    parser.add_argument(
        "--tol", type=float, default=1e-5, help="Catalog M-value tolerance."
    )
    args = parser.parse_args(argv)

    catalogs: Dict[str, Any]
    if args.offline:
        catalogs = {
            "Mossinghoff": DEFAULT_CATALOGS["Mossinghoff"],
            "lehmer_literature": DEFAULT_CATALOGS["lehmer_literature"],
        }
    else:
        catalogs = dict(DEFAULT_CATALOGS)

    results = probe_recent_polynomials(catalogs=catalogs, tol=args.tol)
    print(format_per_entry_table(results))
    summary = summarize_probe(results)
    print(format_summary(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "ProbeResult",
    "probe_recent_polynomials",
    "summarize_probe",
    "format_per_entry_table",
    "format_summary",
    "main",
]
