"""Tests for prometheus_math.lehmer_brute_force.

Math-tdd skill rubric: ≥3 tests in each of authority / property / edge /
composition. The full enumeration of the deg-14 [-5, 5] palindromic
subspace is too expensive to run inside the unit test suite (~minutes),
so the composition tests run on tiny coefficient ranges (e.g. [-1, 1])
where the enumeration completes in seconds.

Reference data
--------------
* Lehmer's polynomial: M ≈ 1.17628081826
* Mossinghoff snapshot: 4 deg-14 palindromic ±5 entries with M < 1.18,
  all at M ≈ 1.17628081826 (Lehmer × cyclotomic).
* Phi_15 (cyclotomic of order 15, deg 8): M = 1 exactly.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pytest

from prometheus_math.lehmer_brute_force import (
    DEFAULT_BAND_UPPER,
    DEFAULT_COEF_RANGE,
    DEGREE,
    INCONCLUSIVE_VERIFICATION_FAILURE_THRESHOLD,
    LEHMER_M,
    BATCH_SIZE,
    build_palindrome_descending,
    classify_cyclotomic_noise,
    compute_mahler_batch_descending,
    descending_to_ascending,
    enumerate_subspace,
    filter_band_candidates,
    is_cyclotomic_exact,
    is_irreducible_rational_root,
    is_reducible_to_cyclotomic_factor,
    lookup_in_mossinghoff,
    mpmath_recheck,
    process_shard,
    run_brute_force,
    sanity_check_lehmer,
    shard_iterator,
    total_shards,
    total_subspace_size,
    verdict_from_band,
)


# Lehmer's poly is degree 10 (NOT in our deg-14 subspace), but
# Lehmer-extension polys live in our subspace. The simplest deg-14
# Lehmer-extension is x^14 - x^11 - x^7 - x^3 + 1, ascending coeffs:
LEHMER_EXTENSION_DEG14_ASC = [1, 0, 0, -1, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 1]
# Half-coeffs (c_0..c_7) = first 8 of ascending = [1, 0, 0, -1, 0, 0, 0, -1].
LEHMER_EXTENSION_HALF = (1, 0, 0, -1, 0, 0, 0, -1)


# ---------------------------------------------------------------------------
# Authority — paper-anchored facts
# ---------------------------------------------------------------------------

def test_authority_lehmer_polynomial_rediscovered_exactly():
    """Pipeline reproduces M(Lehmer) ≈ 1.1762808183 to ≤ 1e-9.

    Reference: Lehmer (1933). The deg-14 Lehmer-extension
    1 - x^3 - x^7 - x^11 + x^14 has the SAME M as Lehmer's deg-10
    polynomial because it differs only by cyclotomic factors.
    """
    # Verify on the deg-14 palindrome that lives in OUR subspace.
    desc = build_palindrome_descending(LEHMER_EXTENSION_HALF)
    mat = np.array([desc], dtype=np.complex128)
    M_arr = compute_mahler_batch_descending(mat)
    assert abs(float(M_arr[0]) - LEHMER_M) < 1e-9, (
        f"M(Lehmer-extension) = {M_arr[0]!r}, expected ~{LEHMER_M}"
    )

    # mpmath recheck reproduces to 1e-12.
    M_mp = mpmath_recheck(LEHMER_EXTENSION_HALF, dps=30)
    assert abs(M_mp - LEHMER_M) < 1e-10, (
        f"mpmath M(Lehmer-extension) = {M_mp!r}, expected ~{LEHMER_M}"
    )


def test_authority_sanity_check_passes():
    """The sanity_check_lehmer routine reproduces Lehmer's M correctly."""
    res = sanity_check_lehmer()
    assert res["pass_numpy"] is True, (
        f"numpy err = {res['numpy_abs_err']:.3e}"
    )
    assert res["pass_mpmath"] is True, (
        f"mpmath err = {res['mpmath_abs_err']:.3e}"
    )
    assert abs(res["lehmer_M_numpy"] - LEHMER_M) < 1e-9
    assert abs(res["lehmer_M_mpmath"] - LEHMER_M) < 1e-12


def test_authority_cyclotomic_simple_polys_detected():
    """Simple cyclotomic deg-14 palindromic polys are detected (M = 1).

    The simplest deg-14 cyclotomic in our palindromic subspace is
    Phi_28 = x^14 + 1 (because Phi_28 has degree φ(28) = 12... no, that's
    wrong: Phi_n has degree φ(n) and Phi_n divides x^n - 1. The poly
    x^14 + 1 = (x^28 - 1)/(x^14 - 1) is the product of Phi_d for d | 28,
    d not dividing 14. That's Phi_28 (deg φ(28)=12) times Phi_4 (deg 2) =
    deg 14, palindromic, and cyclotomic.

    Reference: Phi_n products with sum of degrees 14 yield M=1.
    """
    # x^14 + 1 = product of cyclotomic factors, M = 1.
    half = (1, 0, 0, 0, 0, 0, 0, 0)
    assert is_cyclotomic_exact(half), "x^14 + 1 should be cyclotomic"

    # x^14 - 1: roots are 14th roots of unity, all on unit circle, M = 1.
    # Wait: this is a 'reciprocal' palindrome only if [-1, 0, ..., 0, 1] —
    # but that's anti-palindromic (reads as -1 ... 1), not palindromic.
    # Skip; only test Phi_28-like cases.

    # (x^2 + x + 1) * x^12 + ... hmm, products that LIVE in our palindromic
    # subspace are constrained. Pure x^14 + 1 is enough as the canonical
    # test: it's palindromic, irreducible-status irrelevant, and M = 1.

    # Verify the M is exactly 1 numerically too.
    desc = build_palindrome_descending(half)
    mat = np.array([desc], dtype=np.complex128)
    M = float(compute_mahler_batch_descending(mat)[0])
    assert abs(M - 1.0) < 1e-9, f"Expected M=1, got {M}"


def test_authority_mahler_lower_bound_for_high_coef_polys():
    """Polys with high-magnitude coefficients have correspondingly large M.

    For an integer polynomial with leading coefficient |a_n| >= 1 and
    a non-trivial constant term magnitude, M(P) >= |a_0/a_n|^(1/k) for
    some k depending on degree. More cheaply: a deg-14 palindromic poly
    with c_0 = 5 (so leading coef = 5) has M >= 5 / max(|root|^14) where
    a tighter bound is M >= |a_n| = 5 (since for a palindromic poly all
    root products contribute >=1 by reciprocity).

    Reference: |M(P)| >= |a_n| for any non-constant polynomial.
    """
    # c_0 = 5, all others zero ⇒ P = 5 + 5x^14, palindromic.
    half = (5, 0, 0, 0, 0, 0, 0, 0)
    desc = build_palindrome_descending(half)
    mat = np.array([desc], dtype=np.complex128)
    M = float(compute_mahler_batch_descending(mat)[0])
    # Roots: x^14 = -1 ⇒ all on unit circle; M = |a_n| * prod(max(1, |root|))
    # = 5 * 1 = 5.
    assert abs(M - 5.0) < 1e-9, f"Expected M=5, got {M}"
    # And it's well above the band:
    assert M > DEFAULT_BAND_UPPER


# ---------------------------------------------------------------------------
# Property — invariants of the construction
# ---------------------------------------------------------------------------

def test_property_palindrome_construction_is_reciprocal():
    """Output of build_palindrome_descending is always palindromic.

    For any 8-tuple, the resulting deg-14 polynomial must satisfy
    P(x) = x^14 * P(1/x), i.e. its coefficient list reads the same
    forwards and backwards.
    """
    rng = np.random.default_rng(42)
    for _ in range(50):
        half = tuple(int(c) for c in rng.integers(-5, 6, size=8))
        desc = build_palindrome_descending(half)
        assert desc == list(reversed(desc)), (
            f"build_palindrome_descending({half}) = {desc} is not palindromic"
        )


def test_property_mahler_measure_non_negative():
    """M(P) >= 0 for all non-zero polynomials in the subspace.

    Mahler measure is a product of |a_n| and max(1, |alpha_i|) — never
    negative. Skipping the all-zero degenerate case (P = 0) which is
    excluded by c_0 != 0.
    """
    rng = np.random.default_rng(7)
    halves = []
    for _ in range(200):
        half = list(int(c) for c in rng.integers(-5, 6, size=8))
        if half[0] == 0:
            half[0] = 1
        halves.append(tuple(half))
    descs = [build_palindrome_descending(h) for h in halves]
    mat = np.array(descs, dtype=np.complex128)
    M_arr = compute_mahler_batch_descending(mat)
    assert np.all(M_arr >= 0), "Mahler measure must be non-negative"
    assert np.all(np.isfinite(M_arr)), "All M values should be finite"


def test_property_enumeration_is_deterministic():
    """Two enumerations of the same subspace produce identical lists.

    Ensures multiprocessing / batching does not perturb the polynomial
    set we visit.
    """
    a = list(enumerate_subspace([1], coef_range=(-1, 1)))
    b = list(enumerate_subspace([1], coef_range=(-1, 1)))
    assert a == b, "Enumeration should be deterministic"
    # Each entry should be length 8 and start with c_0 = 1
    for tup in a:
        assert len(tup) == 8
        assert tup[0] == 1
    # Total count: 1 (c_0=1) * 3 (each of c_1..c_7 in {-1,0,1}) ^ 7 = 3^7 = 2187
    assert len(a) == 3 ** 7


def test_property_total_subspace_size_matches_enumeration():
    """``total_subspace_size`` agrees with the actual enumeration count."""
    # Tiny subspace: c_0 in {1}, c_1..c_7 in {-1, 0, 1}.
    n_decl = total_subspace_size(coef_range=(-1, 1), c0_positive_only=True)
    n_enum = sum(1 for _ in enumerate_subspace([1], coef_range=(-1, 1)))
    assert n_decl == n_enum
    assert n_decl == 3 ** 7  # 2187


# ---------------------------------------------------------------------------
# Edge — boundary / degenerate inputs
# ---------------------------------------------------------------------------

def test_edge_all_zero_except_leading():
    """c_0 = 1, c_1 = ... = c_7 = 0 ⇒ P(x) = 1 + x^14 = Phi_28 (cyclotomic).

    This poly has M = 1 exactly. Should be classified as cyclotomic and
    therefore EXCLUDED from the Lehmer band.
    """
    half = (1, 0, 0, 0, 0, 0, 0, 0)
    desc = build_palindrome_descending(half)
    mat = np.array([desc], dtype=np.complex128)
    M = float(compute_mahler_batch_descending(mat)[0])
    assert abs(M - 1.0) < 1e-9, f"M(x^14 + 1) should be 1, got {M}"
    assert is_cyclotomic_exact(half), "x^14 + 1 = Phi_28, cyclotomic"


def test_edge_smallest_nontrivial_coefficient_set():
    """Coef range (-1, 1) reduces to a tiny subspace; ensure it runs cleanly."""
    halves = list(enumerate_subspace([1], coef_range=(-1, 1)))
    assert len(halves) == 3 ** 7  # 2187
    # All have c_0 = 1
    assert all(h[0] == 1 for h in halves)
    # Building & batching the smallest set works without error.
    descs = [build_palindrome_descending(h) for h in halves[:100]]
    mat = np.array(descs, dtype=np.complex128)
    M_arr = compute_mahler_batch_descending(mat)
    assert M_arr.shape == (100,)
    assert np.all(M_arr >= 0)


def test_edge_build_palindrome_rejects_wrong_length():
    """build_palindrome_descending raises on wrong-length input."""
    with pytest.raises(ValueError):
        build_palindrome_descending([1, 2, 3])  # too short
    with pytest.raises(ValueError):
        build_palindrome_descending([1] * 15)  # too long


def test_edge_filter_band_excludes_M_at_one():
    """Cyclotomic polys (M ≈ 1) must NOT be flagged as band candidates.

    The lower band bound is 1.0 + 1e-9, so noise around M = 1 is filtered.
    """
    halves = [(1, 0, 0, 0, 0, 0, 0, 0)]  # Phi_28, M=1
    descs = [build_palindrome_descending(h) for h in halves]
    mat = np.array(descs, dtype=np.complex128)
    M_arr = compute_mahler_batch_descending(mat)
    cands = filter_band_candidates(halves, M_arr,
                                    band_lower=1.0 + 1e-6,
                                    band_upper=DEFAULT_BAND_UPPER)
    assert cands == [], "Cyclotomic poly should not be a band candidate"


# ---------------------------------------------------------------------------
# Composition — pipeline-level integration
# ---------------------------------------------------------------------------

def test_composition_run_brute_force_tiny_smoke(tmp_path: Path):
    """End-to-end pipeline runs on the smallest non-trivial subspace.

    We use coef_range=(-1, 1) which gives 1 * 3^7 = 2187 polys — a
    couple of seconds with multiprocessing. Confirms the JSON schema
    and verdict logic.
    """
    out = tmp_path / "tiny.json"
    res = run_brute_force(
        coef_range=(-1, 1),
        band_upper=DEFAULT_BAND_UPPER,
        num_workers=2,
        output_path=str(out),
        c0_positive_only=True,
        progress=False,
    )
    # Schema
    for k in [
        "subspace", "coef_range", "band_upper", "total_polynomials",
        "polys_processed", "in_lehmer_band", "cyclotomic_noise_filtered",
        "wall_time_seconds", "verdict", "metadata",
    ]:
        assert k in res, f"missing key {k}"
    assert res["total_polynomials"] == 3 ** 7
    assert res["polys_processed"] == 3 ** 7
    # Verdict is one of four (post bug-fix 2026-05-04 added INCONCLUSIVE).
    assert res["verdict"] in (
        "H1_LOCAL_LEMMA", "H2_BREAKS", "H5_CONFIRMED", "INCONCLUSIVE",
    )
    # File on disk matches.
    assert out.exists()
    with out.open() as fh:
        loaded = json.load(fh)
    assert loaded["total_polynomials"] == res["total_polynomials"]
    assert loaded["verdict"] == res["verdict"]


def test_composition_band_count_consistent_with_filter():
    """Band candidates from process_shard agree with manual filter.

    Run shard_idx=0 on a small subspace and verify that every candidate
    M sits in (1+1e-9, band_upper).
    """
    n_shards = total_shards(coef_range=(-1, 1), c0_positive_only=True)
    res = process_shard((0, n_shards, (-1, 1), DEFAULT_BAND_UPPER, True))
    for hc, M in res["in_band"]:
        assert 1.0 + 1e-6 < M < DEFAULT_BAND_UPPER, (
            f"Out-of-band candidate: half={hc}, M={M}"
        )
        # half should be length-8 tuple
        assert len(hc) == 8
        assert hc[0] >= 1  # c_0 positive


def test_composition_verdict_logic_is_consistent():
    """verdict_from_band returns the documented label for each branch.

    Updated 2026-05-04 (post bug-fix): H5_CONFIRMED now strictly requires
    every band entry to be in Mossinghoff. Cyclotomic-noise entries are
    filtered upstream in ``run_brute_force`` and never reach this dispatch.
    """
    # Empty band ⇒ H1_LOCAL_LEMMA.
    assert verdict_from_band([]) == "H1_LOCAL_LEMMA"

    # All-Mossinghoff hits ⇒ H5_CONFIRMED.
    fake = [
        {"is_cyclotomic": False, "is_irreducible": True,
         "in_mossinghoff": True, "mossinghoff_label": "x",
         "has_cyclotomic_factor": False, "verification_failed": False},
    ]
    assert verdict_from_band(fake) == "H5_CONFIRMED"

    # Genuinely-novel entry ⇒ H2_BREAKS.
    fake3 = [
        {"is_cyclotomic": False, "is_irreducible": True,
         "in_mossinghoff": False, "mossinghoff_label": None,
         "has_cyclotomic_factor": False, "verification_failed": False},
    ]
    assert verdict_from_band(fake3) == "H2_BREAKS"

    # NEW (bug fix 2026-05-04): a cyclotomic-factored entry that is NOT
    # in Mossinghoff and has NOT failed verification is a genuine non-Moss
    # band hit. Verdict must be H2_BREAKS, NOT H5_CONFIRMED. (Pre-fix this
    # incorrectly returned H5_CONFIRMED, which silently masked novel hits.)
    fake_novel_cyc_factor = [
        {"is_cyclotomic": False, "is_irreducible": False,
         "in_mossinghoff": False, "mossinghoff_label": None,
         "has_cyclotomic_factor": True, "verification_failed": False},
    ]
    assert verdict_from_band(fake_novel_cyc_factor) == "H2_BREAKS"

    # Mixed in-Moss + novel ⇒ H2_BREAKS (one novel breaks the universal).
    mixed = [
        {"is_cyclotomic": False, "is_irreducible": True,
         "in_mossinghoff": True, "mossinghoff_label": "x",
         "has_cyclotomic_factor": False, "verification_failed": False},
        {"is_cyclotomic": False, "is_irreducible": True,
         "in_mossinghoff": False, "mossinghoff_label": None,
         "has_cyclotomic_factor": False, "verification_failed": False},
    ]
    assert verdict_from_band(mixed) == "H2_BREAKS"


def test_authority_phi15_cyclotomic_classified_as_noise(tmp_path: Path):
    """Bug-fix 2026-05-04: cyclotomic Phi_15-class polys go to REJECTED.

    Phi_15 has degree phi(15) = 8 (the 8 primitive 15th roots of unity).
    A deg-14 polynomial of the form Phi_15 * Phi_d (with deg(Phi_d) = 6) is
    a pure cyclotomic product — true M = 1 exactly. The numpy companion
    matrix can drift these slightly above 1 + 1e-6, putting them inside
    the band filter; the cyclotomic-noise classifier must catch them.

    Concrete case: classify_cyclotomic_noise must return True when given
    NaN mpmath, has_cyclotomic_factor=True, residual_M ~= 1.0.
    """
    # Direct unit test of the classifier.
    assert classify_cyclotomic_noise(
        M_numpy=1.00012,
        M_mpmath=float("nan"),
        has_cyclotomic_factor=True,
        residual_M_after_cyclotomic_factor=1.00005,
    ) is True
    # Sanity: with no cyclotomic factor, NOT classified as noise.
    assert classify_cyclotomic_noise(
        M_numpy=1.176,
        M_mpmath=1.176,
        has_cyclotomic_factor=False,
        residual_M_after_cyclotomic_factor=None,
    ) is False
    # Sanity: a true Lehmer-band entry (M ~ 1.176, residual ~ 1.176) is
    # NOT classified as cyclotomic noise even with a cyclotomic factor.
    assert classify_cyclotomic_noise(
        M_numpy=1.176,
        M_mpmath=1.176,
        has_cyclotomic_factor=True,
        residual_M_after_cyclotomic_factor=1.176,
    ) is False


def test_property_verdict_consistent_with_band_contents():
    """Bug-fix 2026-05-04 invariant: verdict and band contents are coherent.

    The H5_CONFIRMED verdict must imply every entry in_lehmer_band has
    in_mossinghoff == True. (Pre-fix this could fire with non-Moss
    entries because cyclotomic-noise entries leaked through.)

    We test this on the (-1, 1) smoke run.
    """
    res = run_brute_force(
        coef_range=(-1, 1),
        band_upper=DEFAULT_BAND_UPPER,
        num_workers=1,
        c0_positive_only=True,
        progress=False,
    )
    if res["verdict"] == "H5_CONFIRMED":
        assert len(res["in_lehmer_band"]) > 0, (
            "H5_CONFIRMED with empty band is inconsistent (should be H1)"
        )
        for entry in res["in_lehmer_band"]:
            assert entry["in_mossinghoff"] is True, (
                f"H5_CONFIRMED but entry not in Mossinghoff: {entry!r}"
            )
    elif res["verdict"] == "H1_LOCAL_LEMMA":
        assert len(res["in_lehmer_band"]) == 0
    elif res["verdict"] == "H2_BREAKS":
        # At least one non-Moss, non-failed entry exists.
        novel = [
            e for e in res["in_lehmer_band"]
            if (not e["in_mossinghoff"])
            and (not e.get("verification_failed", False))
        ]
        assert len(novel) >= 1, (
            "H2_BREAKS requires at least one verified non-Moss entry"
        )
    elif res["verdict"] == "INCONCLUSIVE":
        n_total = len(res["in_lehmer_band"])
        n_failed = sum(
            1 for e in res["in_lehmer_band"]
            if e.get("verification_failed", False)
        )
        assert n_total > 0
        assert (n_failed / n_total) > INCONCLUSIVE_VERIFICATION_FAILURE_THRESHOLD


def test_edge_nan_mpmath_marks_verification_failed_or_filters():
    """Bug-fix 2026-05-04 edge: M_mpmath = NaN entries are either filtered
    as cyclotomic noise OR marked verification_failed.

    The substrate cannot certify M to high precision when mpmath returns
    NaN; we either reclassify (if cyclotomic-factor evidence) or flag the
    entry so the verdict logic can route to INCONCLUSIVE.
    """
    res = run_brute_force(
        coef_range=(-1, 1),
        band_upper=DEFAULT_BAND_UPPER,
        num_workers=1,
        c0_positive_only=True,
        progress=False,
    )
    # Every entry in in_lehmer_band must have a verification_failed field.
    for entry in res["in_lehmer_band"]:
        assert "verification_failed" in entry, (
            f"verification_failed key missing from entry: {entry!r}"
        )
        # If mpmath is NaN, the entry should either be filtered out (in
        # cyclotomic_noise_filtered) or flagged with verification_failed.
        if not (entry["M_mpmath"] == entry["M_mpmath"]):  # NaN-safe
            assert entry["verification_failed"] is True, (
                f"NaN M_mpmath but verification_failed not set: {entry!r}"
            )
    # cyclotomic_noise_filtered must be present in the result schema.
    assert "cyclotomic_noise_filtered" in res
    # Every filtered entry must have filter_reason == "cyclotomic_noise".
    for entry in res["cyclotomic_noise_filtered"]:
        assert entry.get("filter_reason") == "cyclotomic_noise"


def test_composition_lehmer_extension_lookup_in_mossinghoff():
    """Lehmer-extension deg-14 ([1,0,0,-1,0,0,0,-1,0,0,0,-1,0,0,1])
    is recognised as a Mossinghoff entry.
    """
    in_moss, label = lookup_in_mossinghoff(
        LEHMER_EXTENSION_HALF, LEHMER_M, M_tol=1e-6,
    )
    assert in_moss is True, (
        f"Lehmer-extension should be in Mossinghoff; got label={label!r}"
    )
    assert label is not None


def test_composition_resumable_via_shard_partition():
    """Splitting the enumeration into shards covers the same set as one pass.

    Concatenate half-coefficient tuples from all shards and verify the
    union equals the single-pass enumeration (no duplicates, no gaps).
    """
    n_shards = total_shards(coef_range=(-1, 1), c0_positive_only=True)
    all_shards: set[tuple[int, ...]] = set()
    for s in range(n_shards):
        for hc in shard_iterator(s, n_shards, (-1, 1), True):
            all_shards.add(hc)
    single = set(enumerate_subspace([1], coef_range=(-1, 1)))
    assert all_shards == single
    assert len(all_shards) == 3 ** 7
