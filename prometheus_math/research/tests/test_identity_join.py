"""Tests for prometheus_math.research.identity_join (project #13).

Follows the math-tdd skill's 4-category rubric (Authority / Property /
Edge / Composition). Aim: ≥ 2 in each category.

Authoritative anchors
---------------------
- 5_2 -> LMFDB ``3.1.23.1`` (cubic ``x^3 - x^2 + 1``, disc -23).
  Reference: Aporia session journal 2026-04-22 H101 hand-verification +
  Callahan-Hildebrand-Weeks SnapPea hyperbolic structure data; LMFDB
  number-field 3.1.23.1 (disc_abs=23, disc_sign=-1, coeffs=[1,-1,0,1]).
- 4_1 -> LMFDB ``2.0.3.1`` (Q(sqrt(-3)), ``x^2 - x + 1``, disc -3).
  Reference: Neumann-Reid (1992) "Arithmetic of hyperbolic manifolds";
  LMFDB 2.0.3.1 (disc_abs=3, disc_sign=-1, coeffs=[1,-1,1]).

The LMFDB-bound tests skip cleanly when the Postgres mirror is offline.
SnapPy-bound tests are skipped when SnapPy is unavailable.
"""
from __future__ import annotations

import os
import tempfile

import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math.research import identity_join as ij


# ---------------------------------------------------------------------------
# Liveness probes
# ---------------------------------------------------------------------------

_LMFDB_OK = False
try:
    from prometheus_math.databases import lmfdb as _lmfdb
    _LMFDB_OK = _lmfdb.probe(timeout=3.0)
except Exception:
    _LMFDB_OK = False

_SNAPPY_OK = True
try:
    import snappy  # noqa: F401
except Exception:
    _SNAPPY_OK = False

_PARI_OK = True
try:
    import cypari  # noqa: F401
except Exception:
    _PARI_OK = False


requires_lmfdb = pytest.mark.skipif(
    not _LMFDB_OK, reason="LMFDB Postgres mirror unreachable"
)
requires_snappy = pytest.mark.skipif(
    not _SNAPPY_OK, reason="SnapPy not installed"
)
requires_pari = pytest.mark.skipif(
    not _PARI_OK, reason="cypari not installed"
)


# ---------------------------------------------------------------------------
# Hand-built fixture data (no LMFDB / SnapPy / PARI required)
# ---------------------------------------------------------------------------

# 5_2 trace field — what knot_shape_field('5_2') returns.
KNOT_5_2_SHAPE = {
    "poly": "x^3 - x^2 + 1",
    "degree": 3,
    "disc": -23,
    "bits_prec": 500,
    "is_hyperbolic": True,
}

# LMFDB row for 3.1.23.1 — schema matches lmfdb.number_fields() output.
LMFDB_3_1_23_1 = {
    "label": "3.1.23.1",
    "coeffs": [1, -1, 0, 1],   # 1 - x + 0*x^2 + x^3 = x^3 - x + 1; polredabs => x^3 - x^2 + 1
    "degree": 3,
    "r2": 1,                   # signature (1, 1)
    "disc_abs": 23,
    "disc_sign": -1,
    "class_number": 1,
    "regulator": 0.281,
    "galois_label": "3T2",
    "is_galois": False,
    "gal_is_solvable": True,
    "ramps": [23],
    "rd": 1.0,
}

# 4_1 trace field.
KNOT_4_1_SHAPE = {
    "poly": "x^2 - x + 1",
    "degree": 2,
    "disc": -3,
    "bits_prec": 500,
    "is_hyperbolic": True,
}

LMFDB_2_0_3_1 = {
    "label": "2.0.3.1",
    "coeffs": [1, -1, 1],       # x^2 - x + 1
    "degree": 2,
    "r2": 1,                    # signature (0, 1)
    "disc_abs": 3,
    "disc_sign": -1,
    "class_number": 1,
    "regulator": 1.0,
    "galois_label": "2T1",
    "is_galois": True,
    "gal_is_solvable": True,
    "ramps": [3],
    "rd": 1.0,
}

# A non-matching LMFDB candidate (different poly, different disc) for
# tests of "low confidence" scoring.
LMFDB_OTHER_CUBIC = {
    "label": "3.1.31.1",
    "coeffs": [1, 1, -1, 1],   # x^3 - x^2 + x + 1
    "degree": 3,
    "r2": 1,
    "disc_abs": 31,
    "disc_sign": -1,
    "class_number": 1,
    "regulator": 0.31,
    "galois_label": "3T2",
    "is_galois": False,
    "gal_is_solvable": True,
    "ramps": [31],
    "rd": 1.0,
}


# ===========================================================================
# 1. AUTHORITY — anchored against published / LMFDB-curated values
# ===========================================================================


@requires_pari
def test_authority_5_2_score_match_against_lmfdb_3_1_23_1():
    """Authority: 5_2 shape field <-> LMFDB ``3.1.23.1`` matches.

    Reference: Aporia H101 session journal 2026-04-22; LMFDB
    https://www.lmfdb.org/NumberField/3.1.23.1 (cubic, disc -23, the
    Callahan-Hildebrand-Weeks invariant trace field of 5_2).

    Hand-verification: ``polredabs(x^3 - x + 1)`` on PARI gives
    ``x^3 - x^2 + 1``; ``poldisc`` of the latter is ``-23``; LMFDB stores
    ``coeffs=[1, -1, 0, 1]`` (constant -> leading), ``disc_abs=23``,
    ``disc_sign=-1``. All four match -> score == 1.0.
    """
    score = ij.score_match(KNOT_5_2_SHAPE, LMFDB_3_1_23_1)
    # All four flags fire: poly+disc+degree+signature = 0.6+0.2+0.1+0.1 = 1.0
    assert score == pytest.approx(1.0, abs=1e-9), (
        f"5_2 <-> 3.1.23.1 should be a perfect match; got score={score}"
    )


@requires_pari
def test_authority_4_1_score_match_against_lmfdb_2_0_3_1():
    """Authority: 4_1 shape field (Q(sqrt(-3))) <-> LMFDB ``2.0.3.1``.

    Reference: Neumann-Reid (1992) "Arithmetic of hyperbolic manifolds";
    LMFDB https://www.lmfdb.org/NumberField/2.0.3.1 (disc -3, the
    invariant trace field of the figure-eight knot complement).
    Hand-verified: x^2 - x + 1 has discriminant 1 - 4 = -3.
    """
    score = ij.score_match(KNOT_4_1_SHAPE, LMFDB_2_0_3_1)
    assert score == pytest.approx(1.0, abs=1e-9), (
        f"4_1 <-> 2.0.3.1 should be a perfect match; got score={score}"
    )


@requires_pari
def test_authority_5_2_does_not_match_unrelated_cubic():
    """Authority: 5_2 should NOT match LMFDB 3.1.31.1.

    3.1.31.1 has the same degree (3) but different disc and poly. Score
    should be much less than 1.0 (degree-only contribution is 0.1).
    """
    score = ij.score_match(KNOT_5_2_SHAPE, LMFDB_OTHER_CUBIC)
    assert score < 0.5, (
        f"5_2 vs 3.1.31.1 should score low (only deg+sig matches); got {score}"
    )
    # Degree match (+0.1) and signature match (cubic, disc<0 -> (1,1) for
    # both, +0.1) fire; |disc| differs (23 vs 31) and poly differs.
    assert score == pytest.approx(0.2, abs=1e-9)


@requires_lmfdb
@requires_snappy
@requires_pari
def test_authority_5_2_full_pipeline_against_live_lmfdb():
    """Authority: full knot_to_nf('5_2') pipeline returns 3.1.23.1.

    Reference: live LMFDB devmirror.lmfdb.xyz query; Aporia H101 hand-check.
    This is the integration anchor — it exercises shape_field +
    LMFDB query + scoring end-to-end on the canonical knot anchor.
    """
    results = ij.knot_to_nf(["5_2"], max_deg=8, bits_prec=500)
    assert len(results) == 1
    rec = results[0]
    assert rec["status"] == "matched", f"unexpected status: {rec}"
    assert rec["best_match"] is not None
    assert rec["best_match"]["lmfdb_label"] == "3.1.23.1"
    assert rec["best_match"]["confidence"] >= 0.8


@requires_lmfdb
@requires_snappy
@requires_pari
def test_authority_4_1_full_pipeline_against_live_lmfdb():
    """Authority: full knot_to_nf('4_1') returns 2.0.3.1.

    Reference: LMFDB 2.0.3.1; Neumann-Reid iTrF table.
    """
    results = ij.knot_to_nf(["4_1"], max_deg=4, bits_prec=300)
    assert len(results) == 1
    rec = results[0]
    assert rec["status"] == "matched"
    assert rec["best_match"]["lmfdb_label"] == "2.0.3.1"
    assert rec["best_match"]["confidence"] >= 0.8


# ===========================================================================
# 2. PROPERTY — Hypothesis-driven invariants
# ===========================================================================


@given(
    poly=st.sampled_from([
        "x^2 - x + 1", "x^2 + 1", "x^3 - x^2 + 1", "x^3 - 2",
        "x^4 - x - 1", "x^2 + 5",
    ]),
    deg=st.integers(min_value=2, max_value=8),
    disc=st.integers(min_value=-10000, max_value=10000).filter(lambda d: d != 0),
    coeffs=st.lists(st.integers(min_value=-20, max_value=20),
                    min_size=2, max_size=8),
    disc_abs=st.integers(min_value=1, max_value=10000),
    disc_sign=st.sampled_from([-1, 1]),
    r2=st.integers(min_value=0, max_value=4),
)
@settings(max_examples=80, deadline=None)
def test_property_score_match_in_unit_interval(
    poly, deg, disc, coeffs, disc_abs, disc_sign, r2
):
    """Property: score_match always returns a float in [0, 1].

    No matter what shape-field dict and LMFDB row are passed, the
    returned confidence must be a probability-like value in [0, 1].
    """
    knot_shape = {"poly": poly, "degree": deg, "disc": disc}
    lmfdb_nf = {
        "coeffs": coeffs, "degree": deg, "disc_abs": disc_abs,
        "disc_sign": disc_sign, "r2": r2,
    }
    score = ij.score_match(knot_shape, lmfdb_nf)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


@requires_pari
def test_property_identical_input_scores_one():
    """Property: scoring a shape field against its own LMFDB-shaped
    representation (same poly, same |disc|, same signature) gives 1.0.

    This is the "identity at the diagonal" sanity invariant.
    """
    # Build LMFDB-shaped row from KNOT_5_2_SHAPE and assert score_match=1.
    row = {
        "label": "self.5_2", "degree": 3, "r2": 1,
        "disc_abs": 23, "disc_sign": -1, "coeffs": [1, -1, 0, 1],
    }
    assert ij.score_match(KNOT_5_2_SHAPE, row) == pytest.approx(1.0, abs=1e-9)
    # And for 4_1 too.
    row2 = {
        "label": "self.4_1", "degree": 2, "r2": 1,
        "disc_abs": 3, "disc_sign": -1, "coeffs": [1, -1, 1],
    }
    assert ij.score_match(KNOT_4_1_SHAPE, row2) == pytest.approx(1.0, abs=1e-9)


def test_property_score_components_are_additive_and_bounded():
    """Property: per-component score weights sum to 1.0; partial matches
    yield strictly partial scores (degree-only = 0.1, +disc = 0.3, etc).

    This pins down the documented weight scheme and protects against
    silent re-weighting in future refactors.
    """
    # Degree-only match (poly differs, disc differs, signature differs)
    only_deg = {
        "label": "x.x.x", "degree": 3, "r2": 0,  # signature (3,0) — degree but r2 differs
        "disc_abs": 9999, "disc_sign": 1, "coeffs": [9, 9, 9, 9],
    }
    assert ij.score_match(KNOT_5_2_SHAPE, only_deg) == pytest.approx(0.1, abs=1e-9)
    # Degree + |disc| match (poly differs, signature differs)
    deg_disc = {
        "label": "x.x.x", "degree": 3, "r2": 0,
        "disc_abs": 23, "disc_sign": 1, "coeffs": [9, 9, 9, 9],
    }
    assert ij.score_match(KNOT_5_2_SHAPE, deg_disc) == pytest.approx(0.3, abs=1e-9)


# ===========================================================================
# 3. EDGE — non-hyperbolic, no LMFDB match, malformed input
# ===========================================================================


@requires_snappy
def test_edge_non_hyperbolic_knot_returns_shape_field_failed():
    """Edge: 3_1 (trefoil) is a torus knot, not hyperbolic.

    knot_shape_field raises ValueError on non-hyperbolic knots; bulk_scan
    should catch this and return ``status='shape_field_failed'`` rather
    than propagating the exception.

    Reference: techne/tests/test_knot_shape_field.py::test_torus_knot_raises.
    """
    results = ij.knot_to_nf(["3_1"], max_deg=4, bits_prec=200)
    assert len(results) == 1
    rec = results[0]
    assert rec["status"] == "shape_field_failed"
    assert rec["best_match"] is None
    assert rec["candidates"] == []
    assert "error" in rec
    # The error string should mention non-hyperbolic.
    assert "hyperbolic" in rec["error"].lower() or "could not" in rec["error"].lower()


def test_edge_no_lmfdb_candidate_returns_no_candidate(monkeypatch):
    """Edge: a valid shape field with no LMFDB row at (deg, |disc|).

    If LMFDB returns zero rows, the result must have status='no_candidate',
    empty candidates, and best_match=None.
    """
    # Mock both layers so the test works offline.
    def _fake_shape(name, bits_prec, max_deg):
        return {
            "poly": "x^7 - 999999*x + 1",
            "degree": 7,
            "disc": -999999999,
            "bits_prec": bits_prec,
            "is_hyperbolic": True,
        }, None
    monkeypatch.setattr(ij, "_shape_field_for_knot", _fake_shape)
    monkeypatch.setattr(ij, "_query_lmfdb_candidates",
                        lambda **kw: [])

    results = ij.knot_to_nf(["fake_knot"], max_deg=8, bits_prec=300)
    assert len(results) == 1
    rec = results[0]
    assert rec["status"] == "no_candidate"
    assert rec["best_match"] is None
    assert rec["candidates"] == []
    assert rec["shape_field"]["degree"] == 7


def test_edge_score_match_handles_missing_keys():
    """Edge: score_match on dicts missing keys returns 0.0 cleanly.

    Empty dicts, None inputs, partial dicts — none should crash.
    """
    assert ij.score_match({}, {}) == 0.0
    assert ij.score_match(None, LMFDB_3_1_23_1) == 0.0
    assert ij.score_match(KNOT_5_2_SHAPE, None) == 0.0
    # Partial: only degree present
    partial_knot = {"degree": 3}
    partial_nf = {"degree": 3}
    s = ij.score_match(partial_knot, partial_nf)
    assert 0.0 <= s <= 1.0
    # Only degree match contributes -> 0.1
    assert s == pytest.approx(0.1, abs=1e-9)


def test_edge_empty_knot_iter_returns_empty_list():
    """Edge: knot_to_nf([]) returns an empty list, not an error."""
    results = ij.knot_to_nf([])
    assert results == []
    # Same for bulk_scan
    assert list(ij.bulk_scan([])) == []


def test_edge_generate_match_report_handles_all_statuses():
    """Edge: report generation must handle matched / no_candidate /
    shape_field_failed records uniformly without crashing.
    """
    fake_results = [
        {
            "knot_name": "5_2",
            "shape_field": KNOT_5_2_SHAPE,
            "candidates": [{"lmfdb_label": "3.1.23.1", "confidence": 1.0,
                            "polredabs_match": True, "disc_match": True,
                            "signature_match": True}],
            "best_match": {"lmfdb_label": "3.1.23.1", "confidence": 1.0,
                           "polredabs_match": True, "disc_match": True,
                           "signature_match": True},
            "status": "matched",
        },
        {
            "knot_name": "fake",
            "shape_field": {"poly": "x^9", "degree": 9, "disc": -7777},
            "candidates": [],
            "best_match": None,
            "status": "no_candidate",
        },
        {
            "knot_name": "3_1",
            "shape_field": None,
            "candidates": [],
            "best_match": None,
            "status": "shape_field_failed",
            "error": "not hyperbolic",
        },
    ]
    md = ij.generate_match_report(fake_results)
    assert isinstance(md, str)
    assert "5_2" in md
    assert "3.1.23.1" in md
    assert "no_candidate" in md
    assert "shape_field_failed" in md
    # Markdown table header present
    assert "| Knot |" in md


def test_edge_generate_match_report_writes_file_when_path_given(tmp_path):
    """Edge: generate_match_report writes the markdown to disk when a
    path is provided, and returns the same string."""
    out = tmp_path / "report.md"
    md = ij.generate_match_report(
        [{"knot_name": "x", "shape_field": None, "candidates": [],
          "best_match": None, "status": "shape_field_failed", "error": "x"}],
        out_path=str(out),
    )
    assert out.exists()
    written = out.read_text(encoding="utf-8")
    assert written == md
    assert "Identity Join Report" in md


# ===========================================================================
# 4. COMPOSITION — chain across modules
# ===========================================================================


def test_composition_knot_to_nf_chains_shape_field_and_lmfdb_query(monkeypatch):
    """Composition: knot_to_nf composes knot_shape_field +
    lmfdb.number_fields correctly.

    Mock both upstream tools and verify that knot_to_nf threads the
    shape-field output into the LMFDB query parameters and into the
    score_match composition.
    """
    captured_query = {}

    def _fake_shape(name, bits_prec, max_deg):
        # Emit a known shape field.
        return dict(KNOT_5_2_SHAPE), None

    def _fake_query(**kwargs):
        captured_query.update(kwargs)
        # Emit one matching row.
        return [dict(LMFDB_3_1_23_1)]

    monkeypatch.setattr(ij, "_shape_field_for_knot", _fake_shape)
    monkeypatch.setattr(ij, "_query_lmfdb_candidates", _fake_query)

    results = ij.knot_to_nf(["5_2"], max_deg=12, bits_prec=500)
    rec = results[0]

    # Composition checks:
    # 1. The LMFDB query was issued with the SHAPE-FIELD's (deg, |disc|).
    assert captured_query["degree"] == 3
    assert captured_query["disc_abs"] == 23
    # 2. The shape-field made it into the per-knot record.
    assert rec["shape_field"]["poly"] == "x^3 - x^2 + 1"
    # 3. The score_match composition produced confidence 1.0 (perfect).
    assert rec["best_match"]["confidence"] == pytest.approx(1.0, abs=1e-9)
    # 4. Status flows through correctly.
    assert rec["status"] == "matched"


def test_composition_score_match_composes_polredabs_and_signature(monkeypatch):
    """Composition: score_match composes polredabs canonicalization
    with the signature derivation tool.

    A non-canonical PARI poly string for KNOT_5_2_SHAPE should
    canonicalize to the same canonical form LMFDB stores, AND the
    signature derived from (degree, disc) for the cubic case must
    match the LMFDB r2 signature.
    """
    # 5_2's iTrF poly written in a non-canonical-but-equivalent form.
    # x^3 - x + 1 has the SAME splitting field as x^3 - x^2 + 1
    # (polredabs maps both to x^3 - x^2 + 1).
    knot_alt = {"poly": "x^3 - x + 1", "degree": 3, "disc": -23}
    score = ij.score_match(knot_alt, LMFDB_3_1_23_1)
    # polredabs canonicalizes both -> equal -> full score 1.0
    assert score == pytest.approx(1.0, abs=1e-9), (
        f"polredabs composition failed: alt poly should canonicalize to "
        f"the same form as LMFDB; got score={score}"
    )


@requires_lmfdb
@requires_snappy
@requires_pari
def test_composition_reverse_join_finds_5_2_for_3_1_23_1():
    """Composition: knots_matching_nf('3.1.23.1') finds the 5_2 knot.

    This is the round-trip of the forward identity join: starting
    from the LMFDB label, recover at least one knot whose iTrF
    realizes that field. Composes lmfdb.number_fields(label=...)
    with knot_shape_field on a small corpus.
    """
    # Restrict the corpus to a handful of low-crossing knots so the test
    # is fast (~10s) instead of scanning all 12,966.
    corpus = ["4_1", "5_2", "6_1", "7_4"]
    matches = ij.knots_matching_nf(
        "3.1.23.1", knot_corpus=corpus,
        max_deg=8, bits_prec=300, min_confidence=0.5,
    )
    names = [m["knot_name"] for m in matches]
    assert "5_2" in names, f"expected 5_2 in matches, got {names}"
    # And the best_match label should round-trip.
    rec = next(m for m in matches if m["knot_name"] == "5_2")
    assert rec["best_match"]["lmfdb_label"] == "3.1.23.1"


def test_composition_bulk_scan_is_streaming(monkeypatch):
    """Composition: bulk_scan yields results lazily and never loads the
    full input into memory.

    We compose bulk_scan with a generator that raises after N pulls;
    if bulk_scan greedily consumed the iterator, we'd see the raise
    immediately. Instead we should be able to pull the first K results
    cleanly.
    """
    counter = {"n": 0}

    def _fake_shape(name, bits_prec, max_deg):
        return dict(KNOT_5_2_SHAPE), None

    def _fake_query(**kwargs):
        return [dict(LMFDB_3_1_23_1)]

    monkeypatch.setattr(ij, "_shape_field_for_knot", _fake_shape)
    monkeypatch.setattr(ij, "_query_lmfdb_candidates", _fake_query)

    def _knot_generator():
        for i in range(100_000):
            counter["n"] = i
            yield f"knot_{i}"
            if i >= 10:
                raise RuntimeError("should not get here in streaming mode "
                                   "if we only pull 5")

    gen = ij.bulk_scan(_knot_generator())
    # Pull only 5 -- the generator raise happens at i=10, so as long as
    # we don't drain past 10 we should never see the RuntimeError.
    out = []
    for _ in range(5):
        out.append(next(gen))
    assert len(out) == 5
    # Each result should be a "matched" record because of our mocks.
    for r in out:
        assert r["status"] == "matched"
        assert r["best_match"]["lmfdb_label"] == "3.1.23.1"
    # Generator never consumed past index 5
    assert counter["n"] < 10


def test_composition_candidate_ordering_by_confidence(monkeypatch):
    """Composition: when LMFDB returns multiple rows of the same
    (deg, |disc|), candidates must be ordered by descending confidence.

    Composes _query_lmfdb_candidates output -> score_match -> sort.
    Ensures best_match is always the highest-confidence row.
    """
    def _fake_shape(name, bits_prec, max_deg):
        return dict(KNOT_5_2_SHAPE), None

    def _fake_query(**kwargs):
        # Order intentionally garbled: bad row first, perfect row last.
        return [
            {  # poly differs
                "label": "3.1.23.99", "degree": 3, "r2": 1,
                "disc_abs": 23, "disc_sign": -1, "coeffs": [9, 9, 9, 9],
            },
            dict(LMFDB_3_1_23_1),
        ]

    monkeypatch.setattr(ij, "_shape_field_for_knot", _fake_shape)
    monkeypatch.setattr(ij, "_query_lmfdb_candidates", _fake_query)

    results = ij.knot_to_nf(["5_2"])
    rec = results[0]
    assert rec["status"] == "matched"
    # best_match must be the perfect-confidence one
    assert rec["best_match"]["lmfdb_label"] == "3.1.23.1"
    # candidates sorted desc by confidence
    confidences = [c["confidence"] for c in rec["candidates"]]
    assert confidences == sorted(confidences, reverse=True)


# ===========================================================================
# Smoke test: module is importable and exposes the documented API
# ===========================================================================


def test_module_exports_documented_api():
    """Smoke: the module advertises the five public functions in __all__."""
    expected = {"knot_to_nf", "score_match", "knots_matching_nf",
                "generate_match_report", "bulk_scan"}
    assert expected.issubset(set(ij.__all__))
    for name in expected:
        assert callable(getattr(ij, name))


def test_module_exposed_via_research_namespace():
    """Smoke: prometheus_math.research.identity_join is reachable."""
    from prometheus_math import research
    # Defensive __init__ silently drops broken submodules; if our import
    # is broken, identity_join won't be in __all__.
    assert "identity_join" in research.__all__
