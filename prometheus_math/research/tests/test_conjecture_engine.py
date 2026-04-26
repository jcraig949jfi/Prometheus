"""Tests for prometheus_math.research.conjecture_engine (project #19 phase 1).

Follows the math-tdd skill's 4-category rubric (Authority / Property /
Edge / Composition). Aim: >= 2 in each category.

Authoritative anchors (verified 2026-04-25 on the local OEIS mirror)
--------------------------------------------------------------------
* LMFDB ``11.a1``  ainvs=[0,-1,1,-7820,-263580]  -> q-expansion = OEIS A006571
  ("Expansion of q*Product_{k>=1} (1-q^k)^2*(1-q^(11*k))^2.").  Same
  sequence is shared by Cremona 11a1 (ainvs=[0,-1,1,-10,-20]); they are
  isogenous, so identical L-series coefficients.
* LMFDB ``37.a1``  ainvs=[0,0,1,-1,0]            -> q-expansion = OEIS A007653
  ('Coefficients of L-series for elliptic curve "37a1": y^2 + y = x^3 - x.').

Both reference rows are EC-themed in OEIS, so their ``surprise_score``
should be LOW (< 0.5).  HIGH-surprise matches (>= 0.5) are the
research-signal target — we test the scoring function symbolically.

Skipping
--------
* LMFDB-bound tests skip cleanly when the Postgres mirror is offline.
* SnapPy is NOT required.
* cypari is required for signature generation (PARI's ellan / ellap);
  tests that need it skip when cypari is unavailable.
"""
from __future__ import annotations

import os
import tempfile

import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math.research import conjecture_engine as ce


# ---------------------------------------------------------------------------
# Liveness probes
# ---------------------------------------------------------------------------

_LMFDB_OK = False
try:
    from prometheus_math.databases import lmfdb as _lmfdb
    _LMFDB_OK = _lmfdb.probe(timeout=3.0)
except Exception:
    _LMFDB_OK = False

_OEIS_OK = False
try:
    from prometheus_math.databases import oeis as _oeis
    _OEIS_OK = _oeis.has_local_mirror()
except Exception:
    _OEIS_OK = False

_PARI_OK = True
try:
    import cypari  # noqa: F401
except Exception:
    _PARI_OK = False


requires_lmfdb = pytest.mark.skipif(
    not _LMFDB_OK, reason="LMFDB Postgres mirror unreachable"
)
requires_oeis_mirror = pytest.mark.skipif(
    not _OEIS_OK, reason="OEIS local mirror not loaded"
)
requires_pari = pytest.mark.skipif(
    not _PARI_OK, reason="cypari not installed"
)


# ---------------------------------------------------------------------------
# Hand-built fixtures (EC ainvs and the q-expansions PARI returns)
# ---------------------------------------------------------------------------

# Cremona 11a1 ainvs (isogenous to LMFDB 11.a1) — shorter coefficients.
AINVS_11A1_CREMONA = [0, -1, 1, -10, -20]
# LMFDB 11.a1 (the canonical isogeny class rep in LMFDB).
AINVS_11A1_LMFDB = [0, -1, 1, -7820, -263580]
# 37.a1 (rank 1 anchor).
AINVS_37A1 = [0, 0, 1, -1, 0]

# Verified prefix of the q-expansion via PARI ellan(_, 30):
# 11.a1: [1, -2, -1, 2, 1, 2, -2, 0, -2, -2, 1, -2, 4, 4, -1, ...]
# 37.a1: [1, -2, -3, 2, -2, 6, -1, 0, 6, 4, -5, -6, -2, 2, 6, ...]
EXPECTED_11A1_AN_FIRST15 = [1, -2, -1, 2, 1, 2, -2, 0, -2, -2, 1, -2, 4, 4, -1]
EXPECTED_37A1_AN_FIRST15 = [1, -2, -3, 2, -2, 6, -1, 0, 6, 4, -5, -6, -2, 2, 6]


# ===========================================================================
# 1. AUTHORITY — anchored against OEIS-curated A-numbers
# ===========================================================================


@requires_pari
@requires_oeis_mirror
def test_authority_11a1_ap_sequence_matches_oeis_a006571():
    """Authority: 11.a1's q-expansion is OEIS A006571.

    Reference: OEIS A006571,
    "Expansion of q*Product_{k>=1} (1-q^k)^2*(1-q^(11*k))^2.".
    Cross-checked: Cremona 11a1 has the same a_n sequence as LMFDB 11.a1
    (they are isogenous).  PARI ``ellan(ellinit([0,-1,1,-10,-20]), 15) ==
    [1, -2, -1, 2, 1, 2, -2, 0, -2, -2, 1, -2, 4, 4, -1]`` matches the
    OEIS sequence's data field on first 15 terms.
    """
    sig = ce.generate_ec_signature(AINVS_11A1_CREMONA, kind="ap_sequence",
                                   n_terms=15)
    assert sig == EXPECTED_11A1_AN_FIRST15, (
        f"q-expansion mismatch for 11a1: got {sig}"
    )

    a_id = _oeis.is_known(sig)
    assert a_id == "A006571", (
        f"11.a1 q-expansion should resolve to A006571; got {a_id}"
    )


@requires_pari
@requires_oeis_mirror
def test_authority_37a1_ap_sequence_matches_oeis_a007653():
    """Authority: 37.a1's q-expansion is OEIS A007653.

    Reference: OEIS A007653,
    'Coefficients of L-series for elliptic curve "37a1": y^2 + y = x^3 - x.'.
    Hand-verified: ``ellinit([0,0,1,-1,0])`` is 37.a1; PARI's first 15
    terms are [1, -2, -3, 2, -2, 6, -1, 0, 6, 4, -5, -6, -2, 2, 6].
    """
    sig = ce.generate_ec_signature(AINVS_37A1, kind="ap_sequence", n_terms=15)
    assert sig == EXPECTED_37A1_AN_FIRST15, (
        f"q-expansion mismatch for 37a1: got {sig}"
    )

    a_id = _oeis.is_known(sig)
    assert a_id == "A007653", (
        f"37.a1 q-expansion should resolve to A007653; got {a_id}"
    )


# ===========================================================================
# 2. PROPERTY — invariants that hold across many inputs
# ===========================================================================


def test_property_surprise_score_in_unit_interval():
    """Property: ``surprise_score`` always returns a float in [0, 1]."""
    # Hand-build a few synthetic OEIS records that span the failure modes.
    for name, data in [
        ("Elliptic curve 11a1 modular form coefficients", [1, -2, -1] * 10),
        ("Number of binary trees on n vertices", [1, 1, 2]),
        ("", []),
        ("x" * 500, list(range(50))),
        ("a", []),
    ]:
        score = ce.surprise_score(
            ec_data={"ec_label": "X.a1", "signature": [1, 2, 3]},
            oeis_data={"name": name, "data": data, "number": "A000001"},
        )
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0, f"score out of [0,1] for name={name!r}"


@settings(max_examples=20, deadline=None)
@given(
    st.integers(min_value=0, max_value=200),
    st.lists(st.integers(min_value=-1000, max_value=1000),
             min_size=0, max_size=60),
)
def test_property_surprise_score_unit_interval_random(name_len, data):
    """Hypothesis: any (name length, data list) keeps surprise_score in [0,1]."""
    name = "x" * name_len
    score = ce.surprise_score(
        ec_data={"ec_label": "X.a1", "signature": data},
        oeis_data={"name": name, "data": data, "number": "A000001"},
    )
    assert 0.0 <= score <= 1.0


def test_property_rank_by_surprise_sorted_descending():
    """Property: ``rank_by_surprise`` output is sorted by surprise_score desc."""
    matches = [
        {"ec_label": "A", "surprise_score": 0.3},
        {"ec_label": "B", "surprise_score": 0.9},
        {"ec_label": "C", "surprise_score": 0.7},
        {"ec_label": "D", "surprise_score": 0.1},
        {"ec_label": "E", "surprise_score": 0.5},
    ]
    ranked = ce.rank_by_surprise(matches, top_n=5)
    scores = [r["surprise_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True), (
        f"expected descending; got {scores}"
    )
    assert ranked[0]["ec_label"] == "B"
    assert ranked[-1]["ec_label"] == "D"


def test_property_ec_signature_length_matches_n_terms():
    """Property: every signature kind respects ``n_terms`` length."""
    if not _PARI_OK:
        pytest.skip("cypari not installed")
    for kind in ["ap_sequence", "ap_only", "torsion_growth", "ap_mod_2",
                 "ap_mod_3"]:
        sig = ce.generate_ec_signature(
            AINVS_11A1_CREMONA, kind=kind, n_terms=10,
        )
        assert len(sig) == 10, (
            f"kind={kind} returned len={len(sig)}, expected 10"
        )


@requires_pari
def test_property_torsion_growth_matches_p_plus_1_minus_ap():
    """Property: torsion_growth[i] == primes[i] + 1 - ap_only[i] for each i.

    This is the definition of #E(F_p) for an EC of good reduction at p,
    which holds for almost all primes.  We only assert on the first 10
    primes for speed.
    """
    primes = ce._first_n_primes(10)
    tg = ce.generate_ec_signature(AINVS_11A1_CREMONA, kind="torsion_growth",
                                  n_terms=10)
    ap = ce.generate_ec_signature(AINVS_11A1_CREMONA, kind="ap_only",
                                  n_terms=10)
    for p, t, a in zip(primes, tg, ap):
        # Bad primes (here p=11) still satisfy the formula because PARI's
        # ellap returns the right "a_p" for both good and bad reduction.
        assert t == p + 1 - a, f"#E(F_{p}) != p+1-a_p: {t} vs {p+1-a}"


# ===========================================================================
# 3. EDGE — documented edge cases handled correctly
# ===========================================================================


def test_edge_too_few_primes_returns_empty():
    """Edge: ``n_terms <= 0`` -> empty signature, no PARI call.

    Covers the "EC with too few primes" requirement: callers who pass 0
    or negative term counts should get an empty list back, never an
    exception.
    """
    assert ce.generate_ec_signature([0, 0, 0, 1, 1], n_terms=0) == []
    assert ce.generate_ec_signature([0, 0, 0, 1, 1], n_terms=-5) == []
    # NF signature: same contract.
    assert ce.generate_nf_signature([1, 0, 1], n_terms=0) == []


def test_edge_invalid_ainvs_raises():
    """Edge: malformed ainvs -> ValueError with informative message."""
    with pytest.raises(ValueError, match="ainvs must have 5 entries"):
        ce.generate_ec_signature([1, 2, 3], n_terms=5)
    with pytest.raises(ValueError, match="ainvs must have 5 entries"):
        ce.generate_ec_signature([], n_terms=5)
    with pytest.raises(ValueError, match="ainvs must have 5 entries"):
        ce.generate_ec_signature([0, 0, 0, 0, 0, 0, 0], n_terms=5)


def test_edge_unknown_signature_kind_raises():
    """Edge: bad ``kind`` string -> ValueError listing the valid options."""
    with pytest.raises(ValueError, match="unknown signature kind"):
        ce.generate_ec_signature([0, 0, 0, 1, 1], kind="bogus", n_terms=5)
    with pytest.raises(ValueError, match="unknown signature kind"):
        ce.generate_nf_signature([1, 0, 1], kind="not_a_kind", n_terms=5)


def test_edge_ap_mod_modulus_lt_2_raises():
    """Edge: ``ap_mod_<n>`` with modulus < 2 is meaningless -> ValueError."""
    with pytest.raises(ValueError, match="must be >= 2"):
        ce.generate_ec_signature([0, 0, 0, 1, 1], kind="ap_mod_1", n_terms=5)


def test_edge_cross_join_zero_ecs_returns_empty():
    """Edge: cross_join over an empty label iterable returns []."""
    out = ce.cross_join_ec_oeis([], kinds=["ap_sequence"])
    assert out == []


def test_edge_rank_by_surprise_empty_input():
    """Edge: rank_by_surprise([]) -> []; top_n <= 0 -> []."""
    assert ce.rank_by_surprise([]) == []
    assert ce.rank_by_surprise(
        [{"ec_label": "X", "surprise_score": 0.5}], top_n=0,
    ) == []
    assert ce.rank_by_surprise(
        [{"ec_label": "X", "surprise_score": 0.5}], top_n=-5,
    ) == []


def test_edge_first_n_primes_bounds():
    """Edge: prime sieve handles n=0, n=1, n=large transitions."""
    assert ce._first_n_primes(0) == []
    assert ce._first_n_primes(1) == [2]
    assert ce._first_n_primes(5) == [2, 3, 5, 7, 11]
    # Boundary near the Rosser-bound switch (n=6).
    p100 = ce._first_n_primes(100)
    assert len(p100) == 100
    assert p100[-1] == 541  # 100th prime


def test_edge_surprise_score_handles_missing_fields():
    """Edge: oeis_data dict missing optional keys -> well-defined score.

    Specifically: ``name`` missing, ``data`` missing, both missing.
    Should never raise; should return a value in [0, 1].
    """
    s1 = ce.surprise_score({"ec_label": "X"}, {})
    s2 = ce.surprise_score({"ec_label": "X"}, {"number": "A001"})
    s3 = ce.surprise_score({"ec_label": "X"}, "not even a dict")  # type: ignore[arg-type]
    for s in [s1, s2, s3]:
        assert 0.0 <= s <= 1.0


# ===========================================================================
# 4. COMPOSITION — chain of operations producing a known invariant
# ===========================================================================


@requires_pari
@requires_oeis_mirror
def test_composition_cross_join_rank_report_chain():
    """Composition: cross_join -> rank_by_surprise -> generate_report.

    Build the cross-join hits *manually* (so the test doesn't require
    LMFDB) by simulating what ``cross_join_ec_oeis`` would emit on the
    two anchors.  Both 11a1 and 37a1 hit OEIS rows whose names contain
    EC vocabulary, so both should rank LOW (surprise < 0.5).  Add a
    synthetic high-surprise hit and check that it bubbles to position 1.
    """
    # Anchor 1: 11.a1 -> A006571 (EC-themed, low surprise)
    sig_11 = ce.generate_ec_signature(AINVS_11A1_CREMONA, n_terms=15)
    a_id_11 = _oeis.is_known(sig_11)
    rec_11 = _oeis.lookup(a_id_11)
    s_11 = ce.surprise_score({"ec_label": "11.a1", "signature": sig_11},
                              rec_11)

    # Anchor 2: 37.a1 -> A007653 (also EC-themed)
    sig_37 = ce.generate_ec_signature(AINVS_37A1, n_terms=15)
    a_id_37 = _oeis.is_known(sig_37)
    rec_37 = _oeis.lookup(a_id_37)
    s_37 = ce.surprise_score({"ec_label": "37.a1", "signature": sig_37},
                              rec_37)

    # Synthetic non-EC OEIS hit (e.g., a combinatorial sequence).
    s_combo = ce.surprise_score(
        {"ec_label": "X.a1", "signature": [1, 2, 3, 4]},
        {"number": "A999999",
         "name": "Number of permutations of n elements",
         "data": [1, 1, 2]},  # short data => high rarity
    )

    matches = [
        {"ec_label": "11.a1", "ainvs": AINVS_11A1_CREMONA,
         "conductor": 11, "rank": 0, "signature_kind": "ap_sequence",
         "signature": sig_11, "oeis_match": a_id_11,
         "oeis_name": rec_11.get("name", ""), "surprise_score": s_11},
        {"ec_label": "37.a1", "ainvs": AINVS_37A1,
         "conductor": 37, "rank": 1, "signature_kind": "ap_sequence",
         "signature": sig_37, "oeis_match": a_id_37,
         "oeis_name": rec_37.get("name", ""), "surprise_score": s_37},
        {"ec_label": "X.a1", "ainvs": [0, 0, 0, 1, 1],
         "conductor": 999, "rank": 0, "signature_kind": "ap_sequence",
         "signature": [1, 2, 3, 4], "oeis_match": "A999999",
         "oeis_name": "Number of permutations of n elements",
         "surprise_score": s_combo},
    ]

    # Both EC-themed hits should be LOW surprise.
    assert s_11 < 0.5, f"A006571 should be low surprise; got {s_11}"
    assert s_37 < 0.5, f"A007653 should be low surprise; got {s_37}"
    # Synthetic combinatorial hit should be HIGH surprise.
    assert s_combo > 0.5, f"non-EC hit should be high surprise; got {s_combo}"

    # Compose: rank descending, take top 3, render report.
    ranked = ce.rank_by_surprise(matches, top_n=3)
    assert ranked[0]["ec_label"] == "X.a1", (
        "high-surprise hit should rank first"
    )

    md = ce.generate_report(ranked)
    assert "X.a1" in md
    assert "A999999" in md
    assert "permutations" in md.lower()
    # Report shape: header + separator + 3 data rows = 6 lines minimum.
    assert md.count("\n|") >= 4


def test_composition_signature_kinds_consistent_for_same_ec():
    """Composition: ap_sequence, ap_only, torsion_growth on the same EC
    are mutually consistent.

    For a curve E and its first n primes p_1,...,p_n:
      ap_only[i]        == ap_sequence[p_i - 1]
      torsion_growth[i] == p_i + 1 - ap_only[i]
    Chains 3 signature generators in one assertion.
    """
    if not _PARI_OK:
        pytest.skip("cypari not installed")
    n = 8
    primes = ce._first_n_primes(n)
    # Need an ap_sequence that goes at least to the largest prime.
    longest = primes[-1]
    full = ce.generate_ec_signature(AINVS_11A1_CREMONA, kind="ap_sequence",
                                    n_terms=longest)
    only = ce.generate_ec_signature(AINVS_11A1_CREMONA, kind="ap_only",
                                    n_terms=n)
    tg = ce.generate_ec_signature(AINVS_11A1_CREMONA, kind="torsion_growth",
                                  n_terms=n)
    for i, p in enumerate(primes):
        assert full[p - 1] == only[i], (
            f"ap_sequence[{p}-1]={full[p-1]} vs ap_only[{i}]={only[i]}"
        )
        assert tg[i] == p + 1 - only[i], (
            f"torsion_growth[{i}]={tg[i]} vs p+1-ap={p+1-only[i]}"
        )


def test_composition_generate_report_writes_to_disk():
    """Composition: generate_report -> file -> readback chain."""
    matches = [
        {"ec_label": "11.a1", "conductor": 11, "rank": 0,
         "signature_kind": "ap_sequence", "signature": [1, -2, -1],
         "oeis_match": "A006571", "oeis_name": "Expansion of ...",
         "surprise_score": 0.2},
    ]
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "report.md")
        md = ce.generate_report(matches, out_path=out)
        assert os.path.isfile(out)
        with open(out, "r", encoding="utf-8") as f:
            disk = f.read()
        assert disk == md
        assert "A006571" in disk


# ===========================================================================
# Live integration tests — exercise the full LMFDB+OEIS pipeline
# ===========================================================================


@requires_lmfdb
@requires_oeis_mirror
@requires_pari
def test_live_cross_join_two_anchors():
    """Live: ``cross_join_ec_oeis(['11.a1', '37.a1'])`` finds both anchors.

    This is the highest-confidence end-to-end path: LMFDB -> ainvs ->
    PARI ellan -> OEIS local mirror -> ranked match record.
    """
    out = ce.cross_join_ec_oeis(
        ["11.a1", "37.a1"],
        kinds=["ap_sequence"],
        n_terms=15,
        min_match_terms=8,
    )
    assert len(out) == 2, f"expected 2 hits; got {out}"
    by_label = {r["ec_label"]: r for r in out}
    assert by_label["11.a1"]["oeis_match"] == "A006571"
    assert by_label["37.a1"]["oeis_match"] == "A007653"
    # Each record carries the full signature length we asked for.
    assert len(by_label["11.a1"]["signature"]) == 15
    # Both surprise scores should be LOW (EC vocab in OEIS name).
    for r in out:
        assert 0.0 <= r["surprise_score"] < 0.5
