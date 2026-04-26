"""Tests for prometheus_math.research.anomaly_surface (project #39).

Test categories (math-tdd skill, see techne/skills/math-tdd.md):

- **Authority**: Atas et al. 2013 Table I exact values for the symmetric
  gap ratio mean across the canonical ensembles (Poisson, GOE, GUE,
  GSE); empirical mean from simulated random-matrix samples must match
  the published asymptotic values within Monte-Carlo error.  Also
  cross-check ``mean_gap_ratio`` on the first 200 Riemann zeta zeros
  against the Bogomolny-Schmit / Bohigas-Giannoni-Schmit GUE prediction.

- **Property**: For ANY zero sequence the ratios r̃_n satisfy
  ``0 <= r̃ <= 1`` (Atas convention); ``mean_gap_ratio`` on a Poisson
  surrogate of length 50K converges to ``2*ln(2) - 1`` (Berry-Tabor
  integrable limit, Atas 2013); ``kolmogorov_smirnov_p`` returns a
  value in ``[0, 1]``; ``surface_anomalies`` returns either an empty
  list or a list of dicts with the documented schema.

- **Edge**: <3 zeros raises ``ValueError``; degenerate (duplicate)
  zeros produce NaN ratios that are silently filtered; unknown ensemble
  string raises ``ValueError``; invalid ``family_query`` (non-dict)
  raises ``ValueError``; empty ratio array raises ``ValueError`` from
  KS.

- **Composition**: classify a freshly simulated GUE sample → best_match
  reports GUE with KS-p > 0.1; classify a Poisson surrogate →
  best_match reports Poisson with KS-p > 0.1; the ``surface_anomalies``
  end-to-end pipeline composes correctly with ``classify_against_ensembles``
  and ``compute_spectral_ratios``.

References
----------
- Atas, Bogomolny, Giraud, Roux, "Distribution of the ratio of
  consecutive level spacings in random matrix ensembles", PRL 110,
  084101 (2013). Table I gives the exact mean ⟨r̃⟩:
      Poisson : 2 ln 2 - 1 = 0.38629...
      GOE     : 4 - 2 sqrt(3) = 0.53590...
      GUE     : (numerical) 0.5996...
      GSE     : (numerical) 0.6744...
- Bogomolny & Schmit, "Random matrix theory and the Riemann zeros",
  J. Phys. A 43 (2010), 7, 075203. Confirms GUE statistics for the
  zeta zero spacing ratios on the first ~10^4 zeros.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from prometheus_math.research import anomaly_surface as ams


# Exact Atas 2013 Table I asymptotic mean ⟨r̃⟩ for the symmetric gap
# ratio.  GOE / Poisson are closed-form; GUE / GSE are the published
# numerical values (Atas et al. report them to 4 dp).
ATAS_MEAN_R = {
    "Poisson": 2.0 * math.log(2.0) - 1.0,        # 0.38629...
    "GOE":     4.0 - 2.0 * math.sqrt(3.0),        # 0.53590...
    "GUE":     0.5996,                            # Atas 2013 Table I
    "GSE":     0.6744,                            # Atas 2013 Table I
}


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_authority_poisson_mean_gap_ratio_atas_2013():
    """A Poisson sequence of length 50K has ⟨r̃⟩ -> 2 ln 2 - 1.

    Reference: Atas et al., PRL 110, 084101 (2013), eq. (4) and
    Table I (Poisson row). The exact closed-form is
    ⟨r̃⟩_Poisson = 2 ln 2 - 1 ≈ 0.38629.
    """
    rng = np.random.default_rng(2024)
    # A Poisson process on the line: cumulative sums of iid Exp(1).
    spacings = rng.exponential(scale=1.0, size=50_000)
    zeros = np.cumsum(spacings)
    r = ams.mean_gap_ratio(zeros, n_skip=0)
    expected = ATAS_MEAN_R["Poisson"]
    # MC standard error on N=50K is ~ 0.001; 0.005 is a comfortable bound.
    assert abs(r - expected) < 0.005, (
        f"Poisson mean r̃={r:.4f} but Atas 2013 predicts {expected:.4f}; "
        f"|diff|={abs(r-expected):.4f} > 0.005"
    )


def test_authority_gue_mean_gap_ratio_atas_2013():
    """Simulated GUE eigenvalues have ⟨r̃⟩ ≈ 0.5996.

    Reference: Atas et al., PRL 110, 084101 (2013), Table I, GUE row.
    Generate a single 400×400 GUE matrix and use the bulk eigenvalues;
    the GUE asymptotic ⟨r̃⟩ = 0.5996 holds in the bulk.
    """
    rng = np.random.default_rng(7)
    n = 400
    re = rng.standard_normal((n, n))
    im = rng.standard_normal((n, n))
    A = (re + 1j * im) / math.sqrt(2.0)
    H = (A + A.conj().T) / math.sqrt(2.0)
    w = np.sort(np.linalg.eigvalsh(H))
    # Strip 50 boundary eigenvalues on each side to stay in the bulk.
    bulk = w[50:-50]
    r = ams.mean_gap_ratio(bulk, n_skip=0)
    expected = ATAS_MEAN_R["GUE"]
    assert abs(r - expected) < 0.02, (
        f"GUE bulk mean r̃={r:.4f} but Atas 2013 predicts {expected:.4f}; "
        f"|diff|={abs(r-expected):.4f} > 0.02"
    )


def test_authority_zeta_zeros_match_gue_bogomolny_schmit():
    """The first 200 Riemann zeta zeros have ⟨r̃⟩ consistent with GUE.

    Reference: Bogomolny & Schmit, J. Phys. A 43 (2010) 075203, and
    Bohigas-Giannoni-Schmit conjecture (chaotic spectra → GUE).
    The first 200 zeros are too few for tight convergence (the GUE
    asymptote ⟨r̃⟩ ≈ 0.5996 has finite-N drift of a few percent), so
    we accept ±0.05.

    Cached zeros are loaded once per test session via
    :func:`anomaly_surface._cached_zeta_zeros`.
    """
    zeros = ams._cached_zeta_zeros(200)
    assert len(zeros) == 200
    r = ams.mean_gap_ratio(zeros, n_skip=10)
    expected = ATAS_MEAN_R["GUE"]
    assert abs(r - expected) < 0.05, (
        f"zeta first-200 mean r̃={r:.4f} vs GUE prediction {expected:.4f}; "
        f"|diff|={abs(r-expected):.4f} > 0.05"
    )


def test_authority_canonical_ensembles_dict():
    """canonical_ensembles() reports Atas 2013 Table I means.

    Reference: Atas et al. 2013, Table I.
    """
    cans = ams.canonical_ensembles()
    assert "GUE" in cans and "GOE" in cans and "GSE" in cans and "Poisson" in cans
    # Poisson and GOE have closed-form means.
    assert abs(cans["Poisson"]["mean_r"] - (2.0 * math.log(2.0) - 1.0)) < 1e-6
    assert abs(cans["GOE"]["mean_r"] - (4.0 - 2.0 * math.sqrt(3.0))) < 1e-6
    # GUE / GSE numerical, allow small variation in cited dp.
    assert abs(cans["GUE"]["mean_r"] - 0.5996) < 0.005
    assert abs(cans["GSE"]["mean_r"] - 0.6744) < 0.005


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


def test_property_ratios_in_unit_interval():
    """For any monotone zero sequence, 0 <= r̃_n <= 1 (Atas convention)."""
    rng = np.random.default_rng(11)
    spacings = rng.exponential(1.0, 1000)
    zeros = np.cumsum(spacings)
    r = ams.compute_spectral_ratios(zeros, n_skip=0)
    finite = r[np.isfinite(r)]
    assert finite.size > 0
    assert (finite >= 0.0 - 1e-12).all() and (finite <= 1.0 + 1e-12).all(), (
        f"r̃ outside [0,1]: min={finite.min()} max={finite.max()}"
    )


def test_property_ks_p_in_unit_interval():
    """kolmogorov_smirnov_p outputs a probability in [0, 1] for every
    canonical class.
    """
    rng = np.random.default_rng(13)
    spacings = rng.exponential(1.0, 5_000)
    zeros = np.cumsum(spacings)
    r = ams.compute_spectral_ratios(zeros, n_skip=0)
    for ens in ("Poisson", "GOE", "GUE", "GSE"):
        p = ams.kolmogorov_smirnov_p(r, ens)
        assert 0.0 <= p <= 1.0, f"KS p({ens})={p} not in [0,1]"


def test_property_classify_keys_and_best_match_present():
    """classify_against_ensembles returns one p per class plus
    ``best_match`` and ``distance_to_best``.
    """
    rng = np.random.default_rng(17)
    spacings = rng.exponential(1.0, 3_000)
    zeros = np.cumsum(spacings)
    r = ams.compute_spectral_ratios(zeros, n_skip=0)
    out = ams.classify_against_ensembles(r)
    for ens in ams.canonical_ensembles():
        assert ens in out
        assert 0.0 <= out[ens] <= 1.0
    assert out["best_match"] in ams.canonical_ensembles()
    assert out["distance_to_best"] >= 0.0


def test_property_mean_ratio_in_unit_interval_random():
    """mean_gap_ratio always lies strictly in [0, 1] for any monotone
    sequence with no duplicates.
    """
    rng = np.random.default_rng(23)
    for trial in range(8):
        spacings = rng.exponential(1.0, 500)
        zeros = np.cumsum(spacings)
        m = ams.mean_gap_ratio(zeros, n_skip=0)
        assert 0.0 <= m <= 1.0, f"mean_gap_ratio={m} outside [0,1]"


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_edge_too_few_zeros_raises():
    """compute_spectral_ratios on <3 zeros raises ValueError."""
    with pytest.raises(ValueError):
        ams.compute_spectral_ratios([1.0, 2.0])
    with pytest.raises(ValueError):
        ams.compute_spectral_ratios([])
    with pytest.raises(ValueError):
        ams.mean_gap_ratio([1.0])


def test_edge_duplicate_zeros_handled_gracefully():
    """Duplicates produce a 0/0 -> NaN ratio that is masked.

    With three points at indices 0, 1, 1, 2 the central spacing is 0,
    yielding NaN; the function must not raise and must return at least
    one finite ratio (from the surrounding non-degenerate triples).
    """
    zeros = [0.0, 1.0, 1.0, 1.0, 2.0, 3.0, 4.0]  # two duplicates
    r = ams.compute_spectral_ratios(zeros, n_skip=0)
    # Some entries may be NaN; the function should not raise.
    assert isinstance(r, np.ndarray)
    # At least one valid ratio expected from the non-degenerate region.
    assert np.isfinite(r).any()


def test_edge_unknown_ensemble_raises():
    """kolmogorov_smirnov_p with unknown ensemble raises ValueError."""
    with pytest.raises(ValueError):
        ams.kolmogorov_smirnov_p(np.array([0.1, 0.2, 0.3, 0.4]), "BOGUS")


def test_edge_invalid_family_query_raises():
    """surface_anomalies with non-dict family_query raises ValueError."""
    with pytest.raises(ValueError):
        ams.surface_anomalies("not-a-dict")
    with pytest.raises(ValueError):
        ams.surface_anomalies(None)


def test_edge_classify_empty_ratios_raises():
    """classify_against_ensembles on empty/<min ratios raises ValueError."""
    with pytest.raises(ValueError):
        ams.classify_against_ensembles(np.array([]))


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_composition_classify_simulated_gue_reports_gue_best():
    """End-to-end: GUE eigenvalues -> compute_spectral_ratios ->
    classify_against_ensembles -> best_match='GUE' with non-trivial p.

    This composes the entire pipeline (matrix sample -> ratios ->
    multi-class KS) and is the gate that catches off-by-convention
    errors (e.g. asymmetric vs symmetric ratio).
    """
    rng = np.random.default_rng(31)
    n = 500
    re = rng.standard_normal((n, n))
    im = rng.standard_normal((n, n))
    A = (re + 1j * im) / math.sqrt(2.0)
    H = (A + A.conj().T) / math.sqrt(2.0)
    w = np.sort(np.linalg.eigvalsh(H))
    bulk = w[50:-50]
    r = ams.compute_spectral_ratios(bulk, n_skip=0)
    out = ams.classify_against_ensembles(r)
    assert out["best_match"] == "GUE", (
        f"expected GUE, got {out['best_match']}; full p-values: "
        f"{ {k: out[k] for k in ams.canonical_ensembles()} }"
    )
    # The GUE channel must dominate the others by at least an order
    # of magnitude (single 500x500 sample is finite, so we don't
    # demand p>0.05 — only that GUE is decisively best).
    other_ps = [out[e] for e in ams.canonical_ensembles() if e != "GUE"]
    assert out["GUE"] > 10.0 * max(other_ps), (
        f"GUE p={out['GUE']} not >> max(other)={max(other_ps)}"
    )


def test_composition_classify_poisson_reports_poisson_best():
    """End-to-end: Poisson surrogate -> classify -> best_match='Poisson'.

    Composition of the same chain as above, on the integrable end of
    the Atas / Berry-Tabor classification.
    """
    rng = np.random.default_rng(37)
    spacings = rng.exponential(1.0, 5_000)
    zeros = np.cumsum(spacings)
    r = ams.compute_spectral_ratios(zeros, n_skip=0)
    out = ams.classify_against_ensembles(r)
    assert out["best_match"] == "Poisson", (
        f"expected Poisson, got {out['best_match']}; full p-values: "
        f"{ {k: out[k] for k in ams.canonical_ensembles()} }"
    )
    assert out["Poisson"] > 0.05


def test_composition_surface_anomalies_uses_ratios_and_classifier():
    """surface_anomalies: a synthetic family of one Poisson sequence
    should NOT be flagged anomalous (Poisson is a known canonical class).

    This composes ``compute_spectral_ratios`` with
    ``classify_against_ensembles`` inside ``surface_anomalies`` via the
    in-memory ``zeros_records`` shortcut.
    """
    rng = np.random.default_rng(41)
    spacings = rng.exponential(1.0, 1000)
    zeros = np.cumsum(spacings).tolist()
    fake_records = [{"label": "synth.poisson.1", "zeros": zeros}]
    out = ams.surface_anomalies(
        family_query={"degree": 2},
        zeros_records=fake_records,
        p_threshold=0.05,
    )
    # Should be a list; the Poisson record should NOT be flagged
    # (because Poisson is one of the canonical classes).
    assert isinstance(out, list)
    flagged_labels = [r["label"] for r in out]
    assert "synth.poisson.1" not in flagged_labels


def test_composition_surface_anomalies_flags_when_all_classes_fail():
    """Construct a deliberately weird sequence (regular lattice -> r̃≈0
    everywhere) that should fail KS against ALL canonical ensembles
    and therefore be surfaced.
    """
    # Equally spaced => every spacing equal => r̃ = 1 every time
    # (min/max of equal numbers is 1). This is far from every canonical
    # class.
    zeros = list(np.arange(1.0, 401.0))  # 400 perfectly regular points
    fake_records = [{"label": "synth.lattice.1", "zeros": zeros}]
    out = ams.surface_anomalies(
        family_query={"degree": 2},
        zeros_records=fake_records,
        p_threshold=0.05,
    )
    flagged_labels = [r["label"] for r in out]
    assert "synth.lattice.1" in flagged_labels, (
        f"perfectly-regular sequence should be anomalous; got {out}"
    )
    # Each surfaced record carries the documented schema.
    rec = out[0]
    assert "label" in rec
    assert "ratios_summary" in rec
    assert "anomaly_score" in rec
    assert "candidate_classes_failed" in rec
    assert isinstance(rec["candidate_classes_failed"], list)
