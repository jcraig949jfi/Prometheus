"""The probe battery is exercised ONLY on synthetic fixtures (operator directive 2026-09-19b s2):
frozen before any replication data is seen, so it cannot be tuned to the results it will judge.
Nothing here touches ASAL, Lenia or any replication artifact.

Each test asserts a probe ORDERS two synthetic behaviours the way its definition claims. That is the
only thing a probe has to do: separate. Absolute values are not asserted (they are not meaningful).
"""
import numpy as np
import pytest

from nyx.atlas import probes as P

T, H, W = 8, 32, 32


def _blob(cy, cx, r=4.0, amp=1.0):
    yy, xx = np.mgrid[0:H, 0:W]
    return amp * np.exp(-(((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * r * r)))


def translating():          # moves, keeps its shape
    return np.stack([_blob(16, 6 + 2.5 * t) for t in range(T)])


def breathing():            # stays put, changes shape
    return np.stack([_blob(16, 16, r=3.0 + 1.8 * abs(np.sin(t))) for t in range(T)])


def static():
    return np.stack([_blob(16, 16)] * T)


def noise():
    rng = np.random.default_rng(20260919)
    return rng.random((T, H, W))


def two_cycle():
    a, b = _blob(16, 12), _blob(16, 20)
    return np.stack([a if t % 2 == 0 else b for t in range(T)])


def collapsing():
    return np.stack([_blob(16, 16, r=6.0, amp=1.0 if t < 4 else 0.02) for t in range(T)])


def texture():              # scene-scale, not a compact object
    rng = np.random.default_rng(7)
    base = rng.random((H, W))
    return np.stack([np.roll(base, t, axis=1) for t in range(T)])


# ----------------------------------------------------------------- contract
def test_declared_battery_is_complete_and_finite():
    out = P.declared(translating())
    assert len(out) == 14 and set(out) == set(P.DECLARED)
    assert all(np.isfinite(v) for v in out.values())


def test_probes_are_deterministic():
    f = breathing()
    assert P.declared(f) == P.declared(f)


def test_degenerate_input_does_not_crash_or_nan():
    for f in (np.zeros((T, H, W)), np.ones((1, H, W))):
        out = P.declared(f)
        assert all(np.isfinite(v) for v in out.values())
    with pytest.raises(ValueError):
        P.declared(np.zeros((0, H, W)))
    with pytest.raises(ValueError):
        P.declared(np.zeros((H, W)))


# ----------------------------------------------------------------- separation (the point)
def test_locomotion_separates_moving_from_deforming():
    assert P.p02_locomotion_vs_deformation(translating()) > P.p02_locomotion_vs_deformation(breathing())
    assert P.p07_frame_displacement(translating()) > P.p07_frame_displacement(breathing())


def test_coherence_separates_smooth_dynamics_from_turbulence():
    assert P.p01_coherence(translating()) > P.p01_coherence(noise())


def test_temporal_novelty_is_high_for_noise_and_low_for_static():
    """Same functional form as the ASAL score but in pixel space -- no learned representation."""
    assert P.p06_temporal_novelty_pixelspace(noise()) < P.p06_temporal_novelty_pixelspace(static())
    # static frames are maximally self-similar, so max-cosine-to-earlier is ~1
    assert P.p06_temporal_novelty_pixelspace(static()) > 0.99


def test_periodicity_detects_a_two_cycle():
    assert P.p09_periodicity(two_cycle()) > P.p09_periodicity(noise())


def test_persistence_and_catastrophe_detect_collapse():
    assert P.p08_persistence(collapsing()) < P.p08_persistence(static())
    assert P.p13_catastrophic_change(collapsing()) > P.p13_catastrophic_change(static())


def test_separability_and_scale_distinguish_object_from_texture():
    assert P.p11_object_background_separability(static()) > P.p11_object_background_separability(texture())
    assert P.p14_scene_scale_texture(texture()) > P.p14_scene_scale_texture(static())


def test_spatial_frequency_higher_for_noise():
    assert P.p04_spatial_frequency(noise()) > P.p04_spatial_frequency(static())


def test_morphology_preserving_motion_higher_for_translation():
    assert P.p12_morphology_preserving_motion(translating()) > P.p12_morphology_preserving_motion(noise())


def test_identity_halflife_longer_for_static_than_noise():
    assert P.p03_identity_halflife(static()) > P.p03_identity_halflife(noise())


def test_spectral_change_higher_for_breathing_than_static():
    assert P.p10_spectral_change(breathing()) > P.p10_spectral_change(static())


def test_edge_density_higher_for_noise():
    assert P.p05_occupancy_edge_density(noise()) > P.p05_occupancy_edge_density(static())


# ----------------------------------------------------------------- open channel + freeze
def test_open_descriptor_is_fixed_length_finite_and_deterministic():
    d1, d2 = P.open_descriptor(translating()), P.open_descriptor(translating())
    assert d1.shape == d2.shape and np.allclose(d1, d2)
    assert np.isfinite(d1).all()
    assert P.open_descriptor(noise()).shape == d1.shape       # same length across inputs -> clusterable


def test_open_descriptor_distinguishes_unrelated_behaviours():
    a, b = P.open_descriptor(translating()), P.open_descriptor(noise())
    assert np.linalg.norm(a - b) > 1e-3


def test_probe_module_is_frozen_and_intact():
    """The battery must be frozen BEFORE the replication results exist; re-freezing needs a recorded reason."""
    assert P.frozen_hash(), "probes.FREEZE missing -- the battery must be frozen before results are seen"
    assert P.is_frozen_intact(), (
        "probes.py changed after its freeze: re-freeze deliberately with a recorded reason, "
        f"source={P.source_hash()[:16]} frozen={P.frozen_hash()[:16]}")
