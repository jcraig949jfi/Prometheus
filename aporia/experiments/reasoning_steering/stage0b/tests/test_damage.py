"""TDD tests for the Stage 0b Axis-2 damage scorer (RATIFIED metric).

damage(state) = -(EvidenceField Axis 2 battery-survival depth n_passed), i.e.
-(number of falsifiers the polynomial passed before any kill). Chain (confirmed):
  DiscoveryPipeline.process_candidate(coeffs, M).kill_vector
    -> build_evidence_field(kill_vector=...).battery_survival_depth.n_passed
    -> damage = -n_passed

More survival (more falsifiers passed) => MORE NEGATIVE damage => closer to a well.
This is the only scalar the Hodge decomposer will read (as edge Delta-damage).
"""
import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math.discovery_pipeline import DiscoveryPipeline
from prometheus_math.evidence_field import build_evidence_field
from sigma_kernel.bind_eval import BindEvalExtension
from sigma_kernel.sigma_kernel import SigmaKernel

from aporia.experiments.reasoning_steering.stage0b.damage import Axis2DamageScorer

# Lehmer's polynomial: smallest known Mahler measure (~1.17628), reciprocal,
# irreducible, in-band (1.001, 1.18). Reference: Lehmer (1933); the canonical
# small-Mahler example.
LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.1762808182599175


# --------------------------------------------------------------------------
# 1. AUTHORITY
# --------------------------------------------------------------------------
def test_authority_lehmer_polynomial_survival():
    """Lehmer's polynomial passes the structural falsifiers it should.

    It is in-band, reciprocal, and irreducible, so out_of_band / reciprocity /
    irreducibility must be among the passed falsifiers. Damage = -n_passed is
    strictly negative (it survives many falsifiers). Reference: Lehmer 1933.
    """
    s = Axis2DamageScorer()
    r = s.score(LEHMER, LEHMER_M)
    assert "out_of_band" in r.passed
    assert "reciprocity" in r.passed
    assert "irreducibility" in r.passed
    assert r.n_passed >= 6
    assert r.damage == -r.n_passed
    assert r.damage < 0


def test_authority_out_of_band_has_zero_survival():
    """An out-of-band candidate is killed at phase 0: zero falsifiers passed,
    damage = 0 (the maximum-damage / no-survival baseline)."""
    s = Axis2DamageScorer()
    r = s.score([1, 2, 3], 5.0)          # M=5.0 is far outside (1.001, 1.18)
    assert r.n_passed == 0
    assert r.damage == 0


# --------------------------------------------------------------------------
# 2. PROPERTY
# --------------------------------------------------------------------------
def test_property_invariants_over_fixed_polynomials():
    """damage = -n_passed is a non-positive integer with 0 <= n_passed <= n_total,
    and is deterministic. Checked over a small fixed set (pipeline is ~1s/call)."""
    s = Axis2DamageScorer()
    polys = [(LEHMER, LEHMER_M), ([1, -1, 1], 1.05), ([1, 0, 0, 1], 1.10), ([1, 2, 3], 5.0)]
    for coeffs, m in polys:
        r = s.score(coeffs, m)
        assert isinstance(r.damage, int)
        assert r.damage <= 0
        assert 0 <= r.n_passed <= r.n_total
        assert r.damage == -r.n_passed
        # determinism
        assert s.score(coeffs, m).damage == r.damage


@settings(max_examples=8, deadline=None)
@given(m=st.floats(min_value=1.20, max_value=10.0))
def test_property_out_of_band_always_zero_survival(m):
    """Any above-band M is a phase-0 kill => n_passed 0, damage 0."""
    s = Axis2DamageScorer()
    r = s.score([1, 1, 1], m)
    assert r.damage == 0


# --------------------------------------------------------------------------
# 3. EDGE CASES
# --------------------------------------------------------------------------
def test_edge_cases():
    """Edges:
    - empty coeffs: ValueError
    - non-finite Mahler measure: ValueError
    """
    s = Axis2DamageScorer()
    with pytest.raises(ValueError):
        s.score([], 1.1)
    with pytest.raises(ValueError):
        s.score([1, 1, 1], float("nan"))


# --------------------------------------------------------------------------
# 4. COMPOSITION — scorer faithfully wraps the documented chain.
# --------------------------------------------------------------------------
def test_composition_scorer_matches_raw_chain():
    """Axis2DamageScorer.score(...).n_passed equals the raw
    DiscoveryPipeline -> build_evidence_field chain (no drift)."""
    kernel = SigmaKernel(":memory:")
    pipe = DiscoveryPipeline(kernel=kernel, ext=BindEvalExtension(kernel))
    rec = pipe.process_candidate(LEHMER, LEHMER_M)
    raw_n_passed = build_evidence_field(kill_vector=rec.kill_vector).battery_survival_depth.n_passed

    s = Axis2DamageScorer()
    assert s.score(LEHMER, LEHMER_M).n_passed == raw_n_passed
