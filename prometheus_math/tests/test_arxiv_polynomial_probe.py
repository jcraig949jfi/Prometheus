"""Tests for prometheus_math.arxiv_polynomial_probe (rediscovery benchmark).

Math-tdd skill rubric: ≥3 tests in each of authority/property/edge/composition.

The probe runs against the embedded ``RECENT_POLYNOMIAL_CORPUS`` and
the catalog-consistency cross-check.  Live LMFDB / OEIS / arXiv calls
are deliberately AVOIDED here to keep CI green offline; the
property/composition tests use an offline-only catalog registry
(``Mossinghoff + lehmer_literature``) and the integration tests that
hit live services are gated behind explicit reachability skips.
"""
from __future__ import annotations

import time

import pytest

from prometheus_math._arxiv_polynomial_corpus import (
    RECENT_POLYNOMIAL_CORPUS,
    RecentPolynomialEntry,
    corpus_size,
    likely_outside_snapshot_entries,
    post_2018_entries,
)
from prometheus_math.arxiv_polynomial_probe import (
    ProbeResult,
    format_per_entry_table,
    format_summary,
    probe_recent_polynomials,
    summarize_probe,
)
from prometheus_math.catalog_consistency import (
    DEFAULT_CATALOGS,
    lehmer_literature_check,
    mossinghoff_check,
)
from techne.lib.mahler_measure import mahler_measure


# Offline-only registry — no LMFDB / OEIS / arXiv live calls.
OFFLINE_CATALOGS = {
    "Mossinghoff": mossinghoff_check,
    "lehmer_literature": lehmer_literature_check,
}


# ---------------------------------------------------------------------------
# Authority — paper-anchored facts about the corpus
# ---------------------------------------------------------------------------


def test_authority_corpus_has_at_least_5_arxiv_entries():
    """The corpus contains at least 5 entries with paper-arxiv-id metadata.

    Reference: this is the lower bound declared in the task spec; the
    probe is meant to be a small but real-N benchmark.  At time of
    table-build (2026-04-29) we have 17 entries.
    """
    assert corpus_size() >= 5
    for entry in RECENT_POLYNOMIAL_CORPUS:
        assert isinstance(entry.paper_arxiv_id, str)
        # arXiv IDs are formatted YYMM.NNNNN (or older yyyymm) — always
        # at least 8 chars after stripping version suffix.
        assert len(entry.paper_arxiv_id) >= 8


def test_authority_lehmer_polynomial_anchor_hits_both_offline_catalogs():
    """Lehmer's polynomial is the load-bearing anchor of the entire
    Mahler-measure literature.  Recent arXiv papers (e.g. 2601.11486)
    quote it explicitly.  Our embedded Mossinghoff snapshot AND our
    embedded Lehmer-literature snapshot must BOTH hit it; otherwise
    something is broken.

    Reference: Lehmer 1933, "Factorization of certain cyclotomic
    functions", Annals of Math. 34(3); reproduced in proof of Prop 2.1
    of Idris/Sac-Épée 2026 (arXiv:2601.11486).
    """
    # Find the Lehmer entry.
    lehmer = next(
        (e for e in RECENT_POLYNOMIAL_CORPUS
         if abs(e.mahler_measure - 1.1762808182599175) < 1e-6),
        None,
    )
    assert lehmer is not None, "Lehmer's polynomial missing from corpus"
    results = probe_recent_polynomials(
        corpus=[lehmer], catalogs=OFFLINE_CATALOGS
    )
    assert len(results) == 1
    assert results[0].actual_hits["Mossinghoff"] is True
    assert results[0].actual_hits["lehmer_literature"] is True


def test_authority_corpus_m_values_independently_recompute():
    """Every entry's stored M-value agrees with a fresh recomputation
    of ``mahler_measure(reversed(coeffs))`` to better than 1e-5.

    Reference: this is the verification protocol enforced at table-
    build time (2026-04-29), re-asserted here so future edits to the
    corpus don't silently drift.
    """
    for entry in RECENT_POLYNOMIAL_CORPUS:
        # mahler_measure expects descending coefficients (numpy convention).
        m_recomputed = mahler_measure(list(reversed(entry.coeffs)))
        assert abs(m_recomputed - entry.mahler_measure) < 1e-5, (
            f"M-value drift: {entry.paper_arxiv_id} stored="
            f"{entry.mahler_measure}, recomputed={m_recomputed}"
        )


def test_authority_corpus_m_values_in_lehmer_band():
    """Every M-value sits in the Lehmer/Salem band ``[1.001, 5.0]``.

    Reference: Lehmer's conjecture asserts a gap at M=1; the smallest
    known is 1.176 (Lehmer's polynomial).  All small-Mahler arXiv
    papers report M between ~1.176 (Lehmer) and ~2.0 (Salem extension
    range).  An M outside [1.001, 5.0] would indicate a corpus bug.
    """
    for entry in RECENT_POLYNOMIAL_CORPUS:
        assert 1.001 <= entry.mahler_measure <= 5.0, (
            f"{entry.paper_arxiv_id} M={entry.mahler_measure} out of band"
        )


# ---------------------------------------------------------------------------
# Property — invariants over arbitrary corpus entries
# ---------------------------------------------------------------------------


def test_property_actual_and_expected_keys_match():
    """For every entry, after the probe runs, the keys of
    ``actual_hits`` and the keys of ``expected_hits`` agree (modulo
    catalog registration).

    Specifically: every catalog name we predicted should also appear
    in the actual probe results.  This catches the classic test bug
    where a typo in the corpus breaks the dict-keys contract.
    """
    results = probe_recent_polynomials(catalogs=OFFLINE_CATALOGS)
    for res in results:
        actual_keys = set(res.actual_hits.keys())
        expected_keys = set(res.expected_hits.keys())
        # Every offline-catalog key must be present in actual.
        for k in OFFLINE_CATALOGS:
            assert k in actual_keys
        # Every expected key that we DO consult should be in actual.
        # (We may predict for catalogs we don't run in this offline call,
        # so the converse direction is allowed.)
        for k in expected_keys:
            if k in OFFLINE_CATALOGS:
                assert k in actual_keys


def test_property_predicted_mossinghoff_hit_implies_actual_mossinghoff_hit():
    """Sanity check on entry curation: if we predicted
    ``Mossinghoff = True`` for an entry, the live offline probe must
    confirm it.  Otherwise the entry was mis-curated.

    Mossinghoff is a deterministic offline catalog (no network), so
    this is a STRONG assertion — there's no ``"Maybe"`` excuse.
    """
    results = probe_recent_polynomials(catalogs=OFFLINE_CATALOGS)
    for res in results:
        if res.expected_hits.get("Mossinghoff", "Maybe") is True:
            assert res.actual_hits["Mossinghoff"] is True, (
                f"Entry {res.entry.paper_arxiv_id} predicted Mossinghoff hit, "
                f"but probe missed.  Either Mossinghoff snapshot drifted, "
                f"or the entry's expected_catalog_hits['Mossinghoff'] is wrong."
            )


def test_property_probe_runtime_bounded_offline():
    """Offline probe (no network) runs in well under 5s/entry, well
    under 30s for the full ~17-entry corpus.

    The two offline catalogs do O(178) and O(24) Python-loop scans;
    each is microseconds.  Generous bound: <2s for the full corpus.
    """
    t0 = time.monotonic()
    results = probe_recent_polynomials(catalogs=OFFLINE_CATALOGS)
    elapsed = time.monotonic() - t0
    assert len(results) == corpus_size()
    assert elapsed < 2.0, f"offline probe too slow: {elapsed:.2f}s"


def test_property_probe_result_has_expected_fields():
    """Every ``ProbeResult`` instance has the documented attributes."""
    results = probe_recent_polynomials(catalogs=OFFLINE_CATALOGS)
    expected_attrs = {
        "entry",
        "actual_hits",
        "actual_results",
        "expected_hits",
        "agreement",
        "surprises",
        "errors",
    }
    for res in results:
        for attr in expected_attrs:
            assert hasattr(res, attr), f"{attr} missing from ProbeResult"


def test_property_summary_hit_rate_in_unit_interval():
    """For every catalog, the aggregate hit rate is in [0, 1]."""
    results = probe_recent_polynomials(catalogs=OFFLINE_CATALOGS)
    summary = summarize_probe(results)
    for c, rate in summary["per_catalog_hit_rate"].items():
        assert 0.0 <= rate <= 1.0


# ---------------------------------------------------------------------------
# Edge — boundary and degenerate inputs
# ---------------------------------------------------------------------------


def test_edge_empty_corpus_returns_empty_results():
    """An empty corpus yields zero probe results."""
    results = probe_recent_polynomials(corpus=[], catalogs=OFFLINE_CATALOGS)
    assert results == []
    summary = summarize_probe(results)
    assert summary["n_entries"] == 0
    assert summary["per_catalog_hit_count"] == {}
    assert summary["entries_with_zero_hits"] == []
    assert summary["entries_with_multi_hits"] == []


def test_edge_entry_with_m_below_one_raises_value_error():
    """The catalog-consistency check rejects M < 0; the probe must
    propagate that ValueError without swallowing it.

    Reference: ``catalog_consistency._validate_inputs`` requires
    ``m_value >= 0``; we test the strictest case (negative).
    """
    bad_entry = RecentPolynomialEntry(
        coeffs=[1, 1, 1],
        mahler_measure=-0.5,
        paper_arxiv_id="0000.00000",
        paper_title="bogus negative M",
        paper_year=2026,
        source_quote="(synthetic test entry)",
        expected_catalog_hits={"Mossinghoff": False, "lehmer_literature": False},
    )
    with pytest.raises(ValueError):
        probe_recent_polynomials(
            corpus=[bad_entry], catalogs=OFFLINE_CATALOGS
        )


def test_edge_malformed_arxiv_id_still_works():
    """The arxiv_id is METADATA — it's never actually queried by the
    probe (only the (coeffs, M) pair is), so a malformed ID must not
    block the probe.

    This is a safety property: the probe shouldn't fail just because
    a curator mistypes a paper ID.
    """
    # Use Lehmer's polynomial with a malformed (non-arxiv-format) ID.
    weird_entry = RecentPolynomialEntry(
        coeffs=[1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],
        mahler_measure=1.1762808182599175,
        paper_arxiv_id="not-an-arxiv-id!",  # malformed
        paper_title="malformed-id test",
        paper_year=2026,
        source_quote="(synthetic test entry)",
        expected_catalog_hits={"Mossinghoff": True, "lehmer_literature": True},
    )
    results = probe_recent_polynomials(
        corpus=[weird_entry], catalogs=OFFLINE_CATALOGS
    )
    assert len(results) == 1
    # And Lehmer's polynomial still hits both offline catalogs.
    assert results[0].actual_hits["Mossinghoff"] is True
    assert results[0].actual_hits["lehmer_literature"] is True


def test_edge_summary_handles_all_misses():
    """A corpus where NO entry hits any catalog produces a sensible
    summary (every entry in zero_hit_entries, no multi_hit_entries).
    """
    # Use bizarre M values that nothing in the snapshot has.
    miss_entry = RecentPolynomialEntry(
        coeffs=[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # x^10 + 1, cyclotomic-like
        mahler_measure=1.999999,  # nothing in snapshots near here
        paper_arxiv_id="9999.99999",
        paper_title="synthetic miss",
        paper_year=2026,
        source_quote="(synthetic; M intentionally chosen to miss every catalog)",
        expected_catalog_hits={"Mossinghoff": False, "lehmer_literature": False},
    )
    results = probe_recent_polynomials(
        corpus=[miss_entry, miss_entry], catalogs=OFFLINE_CATALOGS
    )
    summary = summarize_probe(results)
    assert summary["n_entries"] == 2
    assert len(summary["entries_with_zero_hits"]) == 2
    assert len(summary["entries_with_multi_hits"]) == 0


# ---------------------------------------------------------------------------
# Composition — end-to-end pipeline assertions
# ---------------------------------------------------------------------------


def test_composition_format_helpers_run_without_error():
    """``format_per_entry_table`` and ``format_summary`` produce non-empty
    strings for the live offline probe.  Smoke test of the CLI surface.
    """
    results = probe_recent_polynomials(catalogs=OFFLINE_CATALOGS)
    table = format_per_entry_table(results)
    summary = format_summary(summarize_probe(results))
    assert isinstance(table, str) and len(table) > 50
    assert isinstance(summary, str) and len(summary) > 50
    # Spot-check that key headers are present.
    assert "catalog cross-check" in table
    assert "Aggregate summary" in summary


def test_composition_lehmer_anchor_drives_multi_hit_count():
    """The full corpus probed offline must have AT LEAST ONE entry with
    multi_hits >= 2 — the Lehmer anchor.  This proves the cross-check
    can detect multi-catalog agreement (calibration-anchor signal).

    If this fails, either the Lehmer entry was removed from the corpus
    or one of the offline catalogs no longer indexes Lehmer's
    polynomial — both are regressions worth flagging.
    """
    results = probe_recent_polynomials(catalogs=OFFLINE_CATALOGS)
    summary = summarize_probe(results)
    assert len(summary["entries_with_multi_hits"]) >= 1


def test_composition_likely_outside_snapshot_partition_is_meaningful():
    """At least 5 entries in the corpus are predicted to be OUTSIDE the
    Mossinghoff snapshot — these are the genuine rediscovery test
    cases.  The probe must agree (Mossinghoff actually misses them).
    """
    candidates = likely_outside_snapshot_entries()
    assert len(candidates) >= 5
    results = probe_recent_polynomials(
        corpus=candidates, catalogs=OFFLINE_CATALOGS
    )
    n_actually_missed = sum(
        1 for res in results if not res.actual_hits["Mossinghoff"]
    )
    # We don't require ALL to miss — there could be coincidental
    # M-value matches within tolerance — but the BULK should miss.
    assert n_actually_missed >= len(candidates) - 2, (
        f"Predicted {len(candidates)} outside snapshot, but only "
        f"{n_actually_missed} actually missed Mossinghoff.  Either the "
        f"snapshot grew, or the prediction labeling was off."
    )


def test_composition_post_2018_subset_partition():
    """Every corpus entry has paper_year >= 2019 (post-2018 by
    construction) — this is what makes it a 'recent arXiv' benchmark.
    """
    assert len(post_2018_entries()) == corpus_size()
    for entry in RECENT_POLYNOMIAL_CORPUS:
        assert entry.paper_year >= 2019


def test_composition_offline_catalogs_catch_at_least_one_hit():
    """Sanity composition test: probing the FULL corpus offline,
    AT LEAST one entry must register a hit.  If the offline catalogs
    catch zero entries, our embedded snapshots have decoupled from
    the literature anchor (Lehmer's polynomial), which would be a
    regression.
    """
    results = probe_recent_polynomials(catalogs=OFFLINE_CATALOGS)
    summary = summarize_probe(results)
    total_hits = sum(summary["per_catalog_hit_count"].values())
    assert total_hits >= 1, (
        "Offline catalogs caught zero entries; expected at least the "
        "Lehmer anchor to hit Mossinghoff and lehmer_literature."
    )
