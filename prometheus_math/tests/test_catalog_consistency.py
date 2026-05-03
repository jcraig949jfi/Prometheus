"""Tests for prometheus_math.catalog_consistency (§6.3 multi-catalog).

Math-tdd skill rubric: ≥3 tests in each of authority/property/edge/composition.
"""
from __future__ import annotations

import pytest

from prometheus_math.catalog_consistency import (
    CatalogResult,
    CatalogConsistencyCheck,
    DEFAULT_CATALOGS,
    arxiv_title_fuzzy_check,
    lehmer_literature_check,
    lmfdb_check,
    mossinghoff_check,
    oeis_check,
    run_consistency_check,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


# Lehmer's polynomial: M ≈ 1.176, IS in Mossinghoff and IS in literature.
LEHMER_COEFFS = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.17628081826

# Plastic / Smyth's polynomial.
SMYTH_COEFFS = [-1, -1, 0, 1]
SMYTH_M = 1.32471957244

# Nonsense polynomial.  M of x^2 + 100x + 1 ~= 99.99 — far from any
# Lehmer / Salem / Pisot range, so all catalogs should miss.
NONSENSE_COEFFS = [1, 100, 1]
NONSENSE_M = 99.99


# Lightweight offline-only registry for tests that should NOT touch the
# network.  Composing the full default registry would block on LMFDB /
# arXiv / OEIS in CI.
OFFLINE_CATALOGS = {
    "Mossinghoff": mossinghoff_check,
    "lehmer_literature": lehmer_literature_check,
}


# ---------------------------------------------------------------------------
# Authority
# ---------------------------------------------------------------------------


def test_authority_lehmer_hit_in_mossinghoff():
    """Lehmer's polynomial sits at M = 1.17628... in Mossinghoff's table.

    Reference: Lehmer 1933 "Factorization of certain cyclotomic functions",
    Annals of Math. 34(3); cross-checked against Mossinghoff's archived
    Lehmer/ list (the embedded snapshot has lehmer_witness=True).
    """
    r = mossinghoff_check(LEHMER_COEFFS, LEHMER_M)
    assert r.catalog_name == "Mossinghoff"
    assert r.hit is True
    assert r.match_label is not None
    assert r.match_distance is not None
    assert r.match_distance < 1e-5


def test_authority_lehmer_hit_in_literature():
    """Lehmer's polynomial is the M=1.176 entry in the embedded Lehmer
    literature catalog (Lehmer 1933 source).

    Reference: same as the Mossinghoff entry — Lehmer's 1933 paper.
    """
    r = lehmer_literature_check(LEHMER_COEFFS, LEHMER_M)
    assert r.catalog_name == "lehmer_literature"
    assert r.hit is True
    assert r.match_label == "Lehmer-1933"
    assert r.query_kind == "polynomial_match"
    assert r.match_distance == 0.0


def test_authority_smyth_hit_in_literature():
    """Smyth's plastic polynomial sits at M = 1.32472... in the literature
    catalog (Smyth 1971 source).

    Reference: Smyth 1971 "On the product of the conjugates outside the
    unit circle", Bull. London Math. Soc. 3(2); plastic-number proof.
    """
    r = lehmer_literature_check(SMYTH_COEFFS, SMYTH_M)
    assert r.hit is True
    assert "Smyth" in r.match_label
    assert r.query_kind == "polynomial_match"


def test_authority_nonsense_misses_offline_catalogs():
    """A polynomial with M ≈ 100 is nowhere near the small-Mahler band;
    both offline catalogs should miss."""
    r1 = mossinghoff_check(NONSENSE_COEFFS, NONSENSE_M)
    r2 = lehmer_literature_check(NONSENSE_COEFFS, NONSENSE_M)
    assert r1.hit is False
    assert r2.hit is False


def test_authority_run_consistency_check_aggregates_lehmer():
    """For Lehmer's polynomial, the offline-only consistency check sees
    Mossinghoff hit + literature hit = any_hit=True with at least 2 hits."""
    result = run_consistency_check(
        LEHMER_COEFFS, LEHMER_M, catalogs=OFFLINE_CATALOGS
    )
    assert result["any_hit"] is True
    assert result["unanimous_miss"] is False
    assert len(result["hits"]) >= 2
    hit_names = {h.catalog_name for h in result["hits"]}
    assert "Mossinghoff" in hit_names
    assert "lehmer_literature" in hit_names


# ---------------------------------------------------------------------------
# Property
# ---------------------------------------------------------------------------


def test_property_catalog_result_has_expected_fields():
    """Every CatalogResult dataclass instance has the documented fields."""
    r = mossinghoff_check(LEHMER_COEFFS, LEHMER_M)
    # Required field set
    expected_attrs = {
        "catalog_name",
        "query_kind",
        "hit",
        "match_label",
        "match_distance",
        "query_runtime_ms",
        "error",
    }
    for attr in expected_attrs:
        assert hasattr(r, attr), f"missing field {attr}"


def test_property_unanimous_miss_iff_no_hit():
    """For ANY input, unanimous_miss == not any_hit.  Both signs."""
    # Hit case
    r1 = run_consistency_check(LEHMER_COEFFS, LEHMER_M, catalogs=OFFLINE_CATALOGS)
    assert r1["unanimous_miss"] == (not r1["any_hit"])
    # Miss case
    r2 = run_consistency_check(NONSENSE_COEFFS, NONSENSE_M, catalogs=OFFLINE_CATALOGS)
    assert r2["unanimous_miss"] == (not r2["any_hit"])
    # And in fact for nonsense, both should miss → unanimous_miss=True
    assert r2["unanimous_miss"] is True
    assert r2["any_hit"] is False


def test_property_query_runtime_ms_non_negative():
    """Every adapter records a non-negative query_runtime_ms."""
    for adapter in (mossinghoff_check, lehmer_literature_check):
        r = adapter(LEHMER_COEFFS, LEHMER_M)
        assert r.query_runtime_ms >= 0.0


def test_property_errored_adapter_has_hit_false():
    """Catalogs that error out (e.g. LMFDB unreachable) emit hit=False
    with non-None error; the orchestrator never propagates the failure
    as a hit."""
    # Build a fake adapter that always errors via the wrapper.
    def _broken(coeffs, m, tol=1e-5):
        return CatalogResult(
            catalog_name="Broken",
            query_kind="?",
            hit=False,
            error="simulated_failure: test",
        )

    result = run_consistency_check(
        LEHMER_COEFFS, LEHMER_M,
        catalogs={"Broken": _broken, **OFFLINE_CATALOGS},
    )
    # The broken catalog should appear in errors
    assert any(r.catalog_name == "Broken" for r in result["errors"])
    # And NOT in hits
    assert not any(r.catalog_name == "Broken" for r in result["hits"])
    # The two offline catalogs still hit Lehmer
    assert result["any_hit"] is True


def test_property_consistency_check_class_matches_function():
    """The CatalogConsistencyCheck dataclass and run_consistency_check
    function produce equivalent results."""
    cc = CatalogConsistencyCheck(catalogs=OFFLINE_CATALOGS)
    r1 = cc.run(LEHMER_COEFFS, LEHMER_M)
    r2 = run_consistency_check(LEHMER_COEFFS, LEHMER_M, catalogs=OFFLINE_CATALOGS)
    assert r1["any_hit"] == r2["any_hit"]
    assert r1["unanimous_miss"] == r2["unanimous_miss"]
    assert r1["catalogs_checked"] == r2["catalogs_checked"]


# ---------------------------------------------------------------------------
# Edge
# ---------------------------------------------------------------------------


def test_edge_empty_catalogs_returns_unanimous_miss_with_warning():
    """Vacuous case: catalogs={} → unanimous_miss=True with explicit warning."""
    result = run_consistency_check(LEHMER_COEFFS, LEHMER_M, catalogs={})
    assert result["any_hit"] is False
    assert result["unanimous_miss"] is True
    assert result["warning"] is not None
    assert "vacuously" in result["warning"]


def test_edge_empty_coeffs_raises_value_error():
    """coeffs=[] is rejected by every adapter with ValueError."""
    with pytest.raises(ValueError):
        mossinghoff_check([], 1.5)
    with pytest.raises(ValueError):
        lehmer_literature_check([], 1.5)
    with pytest.raises(ValueError):
        run_consistency_check([], 1.5)


def test_edge_negative_m_value_raises():
    """m_value < 0 is rejected."""
    with pytest.raises(ValueError):
        mossinghoff_check([1, 2, 1], -1.0)
    with pytest.raises(ValueError):
        run_consistency_check([1, 2, 1], -1.0)


def test_edge_non_finite_m_value_raises():
    """NaN / inf m_value is rejected."""
    with pytest.raises(ValueError):
        mossinghoff_check([1, 2, 1], float("nan"))
    with pytest.raises(ValueError):
        mossinghoff_check([1, 2, 1], float("inf"))


def test_edge_lmfdb_unreachable_emits_typed_error():
    """LMFDB adapter with a probe that returns False emits hit=False
    with typed error; doesn't crash."""
    # Monkeypatch the lmfdb wrapper's probe to return False.
    from prometheus_math.databases import lmfdb as _lmfdb
    orig_probe = _lmfdb.probe
    _lmfdb.probe = lambda timeout=3.0: False
    try:
        r = lmfdb_check(LEHMER_COEFFS, LEHMER_M)
    finally:
        _lmfdb.probe = orig_probe
    assert r.hit is False
    assert r.error is not None
    assert "unreachable" in r.error


# ---------------------------------------------------------------------------
# Authority — LMFDB cast regression (live-network; skip-clean if unreachable)
# ---------------------------------------------------------------------------


def test_authority_lmfdb_cast_handles_array_binding():
    """Regression for the nf_fields.coeffs ``%s::numeric[]`` cast.

    Bug history: psycopg2's default adaptation of ``list[int]`` produces
    a Postgres ``integer[]``, which does NOT unify with the
    ``nf_fields.coeffs`` column's declared ``numeric[]`` type. Without
    the explicit cast, queries raise
    ``psycopg2.errors.DatatypeMismatch: operator does not exist:
    numeric[] = integer[]``.

    This test exercises the live ``lmfdb_check`` adapter with two known
    polynomials at different degrees:

      * Q(i) = ``[1, 0, 1]`` (degree 2)        → label ``2.0.4.1``
      * Q(zeta_5) = ``[1, -1, 1, -1, 1]`` (degree 4) → label ``4.0.125.1``

    Both must return ``hit=True`` with the expected label. We test two
    degrees specifically because the original bug report only covered
    degree 2; the cast must work uniformly across array sizes.

    Skips cleanly if LMFDB is unreachable (CI without network access).
    See ``prometheus_math/BUGS_FIXED.md`` entry #1.
    """
    from prometheus_math.databases import lmfdb as _lmfdb
    if not _lmfdb.probe(timeout=5.0):
        pytest.skip("LMFDB mirror unreachable; cast regression cannot be exercised")

    # Degree-2 case: the original bug report.
    r2 = lmfdb_check([1, 0, 1], 1.0)
    assert r2.error is None, f"degree-2 cast regressed: {r2.error}"
    assert r2.hit is True, "expected hit for Q(i), got miss"
    assert r2.match_label == "2.0.4.1", (
        f"expected label 2.0.4.1, got {r2.match_label}"
    )

    # Degree-4 case: confirm cast works across coefficient-array sizes.
    # Q(zeta_5), the 5th cyclotomic field.
    r4 = lmfdb_check([1, -1, 1, -1, 1], 1.0)
    assert r4.error is None, f"degree-4 cast regressed: {r4.error}"
    assert r4.hit is True, "expected hit for Q(zeta_5), got miss"
    assert r4.match_label == "4.0.125.1", (
        f"expected label 4.0.125.1, got {r4.match_label}"
    )


def test_edge_oeis_short_sequence_skip():
    """OEIS adapter skips when the coefficient list has < 3 nonzero
    entries (trivial sequence not worth searching)."""
    r = oeis_check([1, 0, 1], 1.0)
    assert r.hit is False
    assert r.error is not None
    assert "trivial" in r.error.lower()


def test_edge_arxiv_unreachable_handled():
    """arXiv adapter with a failing probe emits hit=False with typed error."""
    from prometheus_math.databases import arxiv as _arxiv
    orig_probe = _arxiv.probe
    _arxiv.probe = lambda timeout=3.0: False
    try:
        r = arxiv_title_fuzzy_check(LEHMER_COEFFS, LEHMER_M)
    finally:
        _arxiv.probe = orig_probe
    assert r.hit is False
    assert r.error is not None


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------


def test_composition_pipeline_uses_multiple_catalogs():
    """The DiscoveryPipeline now consults all configured catalogs, not
    just Mossinghoff. process_candidate(Lehmer) records >1 catalog in
    check_results['catalogs_checked']."""
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval import BindEvalExtension
    from prometheus_math.discovery_pipeline import DiscoveryPipeline

    k = SigmaKernel(":memory:")
    ext = BindEvalExtension(k)
    p = DiscoveryPipeline(kernel=k, ext=ext)

    record = p.process_candidate(LEHMER_COEFFS, LEHMER_M)
    catalogs = record.check_results.get("catalogs_checked", [])
    assert len(catalogs) > 1, (
        f"expected >1 catalog consulted, got {catalogs}"
    )
    assert "Mossinghoff" in catalogs
    assert "lehmer_literature" in catalogs


def test_composition_lehmer_routes_to_rejected_unchanged():
    """Lehmer's polynomial through the full pipeline still routes to
    REJECTED with kill_pattern='known_in_catalog:...' — backwards
    compatible with §6.1 behavior."""
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval import BindEvalExtension
    from prometheus_math.discovery_pipeline import DiscoveryPipeline

    k = SigmaKernel(":memory:")
    ext = BindEvalExtension(k)
    p = DiscoveryPipeline(kernel=k, ext=ext)

    record = p.process_candidate(LEHMER_COEFFS, LEHMER_M)
    assert record.terminal_state == "REJECTED"
    assert record.kill_pattern is not None
    assert "known_in_catalog" in record.kill_pattern


def test_composition_literature_only_hit_routes_to_rejected():
    """Synthesize the case where a polynomial is in lehmer_literature but
    NOT in Mossinghoff: monkeypatch Mossinghoff to always miss, run a
    literature-table polynomial through the pipeline; should still route
    to REJECTED with kill_pattern naming the literature hit."""
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval import BindEvalExtension
    from prometheus_math.discovery_pipeline import DiscoveryPipeline
    from prometheus_math import catalog_consistency as cc_mod

    # Pick a literature entry whose M is in band (1.001, 1.18) — Smyth's
    # is at 1.32 (above band) so the band gate would catch it. Use a
    # synthetic case: monkeypatch BOTH the band gate (via caller's M)
    # and the Mossinghoff adapter.
    # Actually, simpler: use Lehmer's polynomial coefficients and
    # monkeypatch mossinghoff_check to always return miss.

    orig_moss = cc_mod.mossinghoff_check

    def _miss_moss(coeffs, m, tol=1e-5):
        return CatalogResult(
            catalog_name="Mossinghoff", query_kind="M_value",
            hit=False,
        )

    cc_mod.mossinghoff_check = _miss_moss
    # Also have to patch DEFAULT_CATALOGS reference.
    orig_default = dict(cc_mod.DEFAULT_CATALOGS)
    cc_mod.DEFAULT_CATALOGS["Mossinghoff"] = _miss_moss

    try:
        k = SigmaKernel(":memory:")
        ext = BindEvalExtension(k)
        p = DiscoveryPipeline(kernel=k, ext=ext)
        record = p.process_candidate(LEHMER_COEFFS, LEHMER_M)
    finally:
        cc_mod.mossinghoff_check = orig_moss
        cc_mod.DEFAULT_CATALOGS.clear()
        cc_mod.DEFAULT_CATALOGS.update(orig_default)

    # Lehmer literature still hits → routed to REJECTED with
    # kill_pattern naming the literature catalog.
    assert record.terminal_state == "REJECTED"
    assert record.kill_pattern is not None
    assert "known_in_catalog" in record.kill_pattern
    assert "lehmer_literature" in record.kill_pattern


def test_composition_default_registry_has_all_five():
    """The DEFAULT_CATALOGS registry exposes all five adapters."""
    expected = {
        "Mossinghoff",
        "lehmer_literature",
        "LMFDB",
        "OEIS",
        "arXiv",
    }
    assert set(DEFAULT_CATALOGS.keys()) == expected


def test_composition_offline_subset_unanimous_miss_synthetic():
    """A polynomial nowhere in the catalogs (the nonsense one) yields
    unanimous_miss=True from the offline catalogs."""
    result = run_consistency_check(
        NONSENSE_COEFFS, NONSENSE_M, catalogs=OFFLINE_CATALOGS
    )
    assert result["any_hit"] is False
    assert result["unanimous_miss"] is True
    assert len(result["catalogs_checked"]) == 2
    # Each individual result should be a clean miss (no error)
    for r in result["by_catalog"].values():
        assert r.hit is False
        assert r.error is None
