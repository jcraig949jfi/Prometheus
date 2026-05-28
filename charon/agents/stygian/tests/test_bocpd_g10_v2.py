"""Tests for BOCPD primitive + G10 v2 loader.

Per Erebos v3 Phase 1A ITER-32. Validates Adams-MacKay 2007 BOCPD
on synthetic step / drift / noise sequences + the G10 retrofit on
live Mossinghoff data.
"""
from __future__ import annotations

import pytest

from charon.agents.stygian.loaders._bocpd import (
    BOCPDResult,
    detect_changepoints,
)


# ---------------------------------------------------------------------
# BOCPD primitive
# ---------------------------------------------------------------------

def test_bocpd_too_few_observations_safe():
    """N < 2 returns empty result without crashing."""
    result = detect_changepoints([])
    assert isinstance(result, BOCPDResult)
    assert result.most_likely_changepoint_t is None

    result = detect_changepoints([1.0])
    assert result.most_likely_changepoint_t is None


def test_bocpd_constant_sequence_no_changepoint():
    """Constant sequence has no real changepoints; max posterior low."""
    obs = [0.5] * 30
    result = detect_changepoints(obs, hazard_rate=0.05)
    # No spike in posterior
    interior = result.changepoint_probabilities[1:]
    assert max(interior) < 0.5  # well below substrate-grade threshold


def test_bocpd_detects_clear_step():
    """Step function: 15 samples at 0, then 15 samples at 10 with
    low noise. BOCPD should detect changepoint near t=15."""
    obs = [0.05 * (i % 3) for i in range(15)] + [
        10.0 + 0.05 * (i % 3) for i in range(15)
    ]
    result = detect_changepoints(obs, hazard_rate=0.1)
    assert result.most_likely_changepoint_t is not None
    # Allow some slack — changepoint should be detected near t=15
    assert 12 <= result.most_likely_changepoint_t <= 18
    assert result.max_posterior > 0.3


def test_bocpd_returns_per_observation_posteriors():
    """changepoint_probabilities has one entry per observation."""
    obs = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = detect_changepoints(obs)
    assert len(result.changepoint_probabilities) == len(obs)


def test_bocpd_hazard_rate_propagates():
    obs = [0.0] * 10 + [5.0] * 10
    r1 = detect_changepoints(obs, hazard_rate=0.05)
    r2 = detect_changepoints(obs, hazard_rate=0.3)
    assert r1.hazard_rate == 0.05
    assert r2.hazard_rate == 0.3


def test_bocpd_uses_data_driven_default_prior():
    """If prior_mean is None, BOCPD derives it from the data; should
    not crash."""
    obs = [10.0, 11.0, 9.0, 10.5, 9.5]
    result = detect_changepoints(obs)
    assert isinstance(result, BOCPDResult)
    assert result.n_observations == 5


# ---------------------------------------------------------------------
# G10 v2 loader
# ---------------------------------------------------------------------

def test_g10_v2_applicable_routes_on_bocpd_marker():
    from charon.agents.stygian.loaders.composition_g10_lehmer_bocpd_sweep import (
        G10LehmerBOCPDSweepLoader,
    )
    loader = G10LehmerBOCPDSweepLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g10_boundary",
        "erebos_composed_id": "EREBOS-G10-bocpd_lehmer_test",
    }) is True


def test_g10_v2_does_not_steal_v1_emissions():
    """v1 (smoothness-ratio) G10 emissions continue routing to the
    original loader."""
    from charon.agents.stygian.loaders.composition_g10_lehmer_bocpd_sweep import (
        G10LehmerBOCPDSweepLoader,
    )
    loader = G10LehmerBOCPDSweepLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g10_boundary",
        "erebos_composed_id": "EREBOS-G10-boundary_BL-C-001-lehmer",
    }) is False


def test_g10_v2_rejects_non_g10_plugin():
    from charon.agents.stygian.loaders.composition_g10_lehmer_bocpd_sweep import (
        G10LehmerBOCPDSweepLoader,
    )
    loader = G10LehmerBOCPDSweepLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g02_contrast",
        "erebos_composed_id": "EREBOS-G02-bocpd_test",
    }) is False


# ---------------------------------------------------------------------
# Live Mossinghoff smoke
# ---------------------------------------------------------------------

def test_g10_v2_live_returns_substantive_posterior_at_salem_cliff():
    """The ITER-10 G10 v1 finding documented the Salem cliff at
    threshold M=1.30 (drop from 0.97 survival to 0.01). BOCPD should
    detect this with substrate-grade interior posterior spike at
    that threshold. (The cold-start window's raw argmax is artifactual;
    the substrate's signal is interior_spike_threshold.)"""
    from charon.agents.stygian.loaders.composition_g10_lehmer_bocpd_sweep import (
        run_g10_lehmer_bocpd_sweep,
    )
    result = run_g10_lehmer_bocpd_sweep()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"Live Mossinghoff catalog not available: "
                    f"{result.get('notes')}")
    # Decision rule must REJECT (sharp boundary at the Salem cliff)
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "sharp_boundary_detected_bocpd"
    # The interior spike (cold-start excluded) should land at M=1.30
    assert result["interior_spike_threshold"] is not None
    assert 1.20 <= result["interior_spike_threshold"] <= 1.40
    assert result["interior_spike_value"] > 0.3  # substantive signal
