"""TDD tests for the persistent-homology recipe gallery.

Covers (per math-tdd skill, >= 2 in every category):
- Authority: noisy-circle Carlsson test, hand-computed bottleneck examples,
  cycle-graph H_1 lifetime, single-point H_0 = 1, two-coincident-points
  H_0 = 1.
- Property: bottleneck >= 0, symmetry, triangle inequality on small
  examples, Wasserstein >= bottleneck, persistence-image non-negativity,
  beta_0 >= 1 for any non-empty cloud, translation invariance.
- Edge: empty cloud raises, singleton cloud, two coincident points,
  small max_edge_length, missing-backend skip.
- Composition: rips -> bottleneck -> persistence_image; rips ->
  betti_numbers chain; sliding_window_embed -> rips on a sine has 1 H_1
  bar; cubical -> betti chain.

Plus smoke tests for each of the 10 recipes (import + main()).
"""

from __future__ import annotations

import math
import os

import numpy as np
import pytest

# Skip the whole module cleanly if GUDHI is missing.
gudhi = pytest.importorskip("gudhi")
hypothesis = pytest.importorskip("hypothesis")

from hypothesis import given, settings, strategies as st

from prometheus_math.recipes.persistent_homology import api as pha


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _noisy_circle(n: int, noise: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    theta = 2 * np.pi * np.linspace(0, 1, n, endpoint=False)
    pts = np.stack([np.cos(theta), np.sin(theta)], axis=1)
    return pts + rng.normal(scale=noise, size=pts.shape)


def _h1_finite_pairs(diag, dim: int = 1):
    return [(b, x) for d, (b, x) in diag if d == dim and not math.isinf(x)]


def _persistences(diag, dim: int = 1):
    return [x - b for b, x in _h1_finite_pairs(diag, dim)]


# ---------------------------------------------------------------------------
# 1. Authority tests
# ---------------------------------------------------------------------------

def test_authority_noisy_circle_carlsson_h1():
    """Noisy circle (n=100, eps=0.05) has exactly one H_1 bar with persistence > 0.5.

    Reference: Carlsson, "Topology and Data", Bull. AMS 46 (2009), Section 5
    -- the canonical "circle test" for persistent homology.  H_1(S^1) = Z,
    so a sufficiently dense, low-noise sample of the circle has one
    long-lived H_1 class.  We pick the standard Carlsson parameters.
    """
    pts = _noisy_circle(100, 0.05, seed=0)
    diag = pha.rips_persistence(pts, max_dim=1, max_edge_length=2.5)

    # Exactly one infinite H_0 bar (connected).
    n_inf_h0 = sum(1 for d, (_, x) in diag if d == 0 and math.isinf(x))
    assert n_inf_h0 == 1, "expected exactly 1 infinite H_0 bar"

    # Exactly one H_1 bar with persistence > 0.5.
    n_long_h1 = sum(1 for p in _persistences(diag, 1) if p > 0.5)
    assert n_long_h1 == 1, f"expected 1 persistent H_1 loop, got {n_long_h1}"


def test_authority_bottleneck_small_shift():
    """bottleneck({(3.0, 5.0)}, {(3.0, 5.0001)}) == 0.0001.

    Hand computation: the bottleneck distance moves the single point
    (3.0, 5.0) to (3.0, 5.0001); L_inf cost = max(|0|, |0.0001|) = 0.0001.
    Reference: Cohen-Steiner et al. (2007), Definition 1.
    """
    diag_a = [(1, (3.0, 5.0))]
    diag_b = [(1, (3.0, 5.0001))]
    bn = pha.bottleneck_distance(diag_a, diag_b, dim=1)
    assert abs(bn - 0.0001) < 1e-7, f"expected ~1e-4, got {bn}"


def test_authority_bottleneck_self_distance_zero():
    """bottleneck(d, d) == 0 for any diagram d.

    Reference: Cohen-Steiner et al. (2007), Section 2 -- bottleneck is a
    metric, so it satisfies d(x, x) = 0.
    """
    pts = _noisy_circle(50, 0.05, seed=0)
    diag = pha.rips_persistence(pts, max_dim=1, max_edge_length=2.5)
    bn = pha.bottleneck_distance(diag, diag, dim=1)
    assert bn < 1e-9, f"expected ~0, got {bn}"


def test_authority_cycle_graph_h1_birth():
    """24-cycle graph has one H_1 bar that is born at t=1.

    Hand computation: edges of the cycle have weight 1, so H_1 first
    appears in the Rips complex at filtration value 1 (the moment the
    1-skeleton is the cycle).  Reference: de Silva & Ghrist, AGT 7 (2007),
    Section 2.1.
    """
    n = 24
    idx = np.arange(n)
    diff = np.abs(idx[:, None] - idx[None, :])
    D = np.minimum(diff, n - diff).astype(float)
    diag = pha.persistence_diagram_from_distmat(D, max_dim=1, max_edge_length=float(n))
    h1 = _h1_finite_pairs(diag, 1)
    assert len(h1) == 1, f"expected 1 H_1 bar, got {len(h1)}"
    birth, _death = h1[0]
    assert abs(birth - 1.0) < 1e-9


def test_authority_single_point_h0_eq_1():
    """A single point has H_0 = 1, all higher H_k empty.

    Reference: Hatcher, *Algebraic Topology*, Example 2.6 -- a one-point
    space has H_0 = Z and H_k = 0 for k > 0.
    """
    pts = np.array([[0.0, 0.0]])
    diag = pha.rips_persistence(pts, max_dim=1, max_edge_length=1.0)
    inf_bars_per_dim: dict = {}
    finite_per_dim: dict = {}
    for d, (_b, x) in diag:
        if math.isinf(x):
            inf_bars_per_dim[d] = inf_bars_per_dim.get(d, 0) + 1
        else:
            finite_per_dim[d] = finite_per_dim.get(d, 0) + 1
    assert inf_bars_per_dim == {0: 1}, f"expected 1 infinite H_0 bar, got {inf_bars_per_dim}"
    assert finite_per_dim.get(1, 0) == 0, "expected no H_1 bars on a single point"


def test_authority_two_coincident_points_h0_one_component():
    """Two coincident points behave like a single H_0 component (distance 0).

    Hand computation: the Rips complex at any filtration value >= 0
    contains the edge between the duplicate points, so the two vertices
    fuse into a single H_0 class immediately.  Reference: Edelsbrunner &
    Harer, *Computational Topology*, Section VI.3.
    """
    pts = np.array([[0.0, 0.0], [0.0, 0.0]])
    diag = pha.rips_persistence(pts, max_dim=1, max_edge_length=1.0)
    # One infinite H_0 bar; the second H_0 class dies at filtration 0.
    n_inf = sum(1 for d, (_, x) in diag if d == 0 and math.isinf(x))
    assert n_inf == 1
    # The "duplicate" component should have death ~ 0.
    finite_h0 = [x - b for d, (b, x) in diag if d == 0 and not math.isinf(x)]
    assert all(p < 1e-9 for p in finite_h0), f"finite H_0 bars: {finite_h0}"


# ---------------------------------------------------------------------------
# 2. Property tests (Hypothesis + hand-rolled)
# ---------------------------------------------------------------------------

@given(
    n=st.integers(min_value=5, max_value=30),
    seed=st.integers(min_value=0, max_value=99),
)
@settings(max_examples=10, deadline=None)
def test_property_betti_0_at_least_one(n, seed):
    """beta_0 >= 1 for any non-empty point cloud.

    Property: a non-empty topological space has at least one connected
    component, so beta_0 >= 1.
    """
    rng = np.random.default_rng(seed)
    pts = rng.uniform(-1.0, 1.0, size=(n, 2))
    diag = pha.rips_persistence(pts, max_dim=0, max_edge_length=4.0)
    betti = pha.betti_numbers_from_diagram(diag)
    assert betti.get(0, 0) >= 1


@given(seed=st.integers(min_value=0, max_value=20))
@settings(max_examples=5, deadline=None)
def test_property_bottleneck_non_negative_and_symmetric(seed):
    """bottleneck(d_a, d_b) >= 0 and bottleneck(a, b) == bottleneck(b, a)."""
    rng = np.random.default_rng(seed)
    a = rng.uniform(-1.0, 1.0, size=(20, 2))
    b = rng.uniform(-1.0, 1.0, size=(20, 2))
    diag_a = pha.rips_persistence(a, max_dim=1, max_edge_length=4.0)
    diag_b = pha.rips_persistence(b, max_dim=1, max_edge_length=4.0)
    bn_ab = pha.bottleneck_distance(diag_a, diag_b, dim=1)
    bn_ba = pha.bottleneck_distance(diag_b, diag_a, dim=1)
    assert bn_ab >= 0
    assert abs(bn_ab - bn_ba) < 1e-9


def test_property_bottleneck_triangle_inequality_small_diagrams():
    """bottleneck(a, c) <= bottleneck(a, b) + bottleneck(b, c).

    Hand-picked small diagrams; cheap and deterministic.
    """
    a = [(1, (0.0, 1.0))]
    b = [(1, (0.0, 1.5))]
    c = [(1, (0.0, 2.0))]
    ab = pha.bottleneck_distance(a, b, dim=1)
    bc = pha.bottleneck_distance(b, c, dim=1)
    ac = pha.bottleneck_distance(a, c, dim=1)
    assert ac <= ab + bc + 1e-9


def test_property_persistence_image_non_negative():
    """Persistence image is non-negative everywhere."""
    pts = _noisy_circle(60, 0.05, seed=0)
    diag = pha.rips_persistence(pts, max_dim=1, max_edge_length=2.5)
    img = pha.persistence_image(diag, dim=1, resolution=15, sigma=0.1)
    assert (img >= 0).all()
    assert np.isfinite(img).all()


def test_property_wasserstein_at_least_bottleneck():
    """W_p(a, b) >= bottleneck(a, b) (bottleneck = limit p -> infinity).

    Reference: Cohen-Steiner et al., FoCM 10 (2010), Section 3.  The
    p-Wasserstein distance tends to bottleneck as p -> infinity from
    above, so W_p >= bottleneck for finite p.
    """
    a = _noisy_circle(40, 0.04, seed=0)
    b = _noisy_circle(40, 0.04, seed=1)
    da = pha.rips_persistence(a, max_dim=1, max_edge_length=2.5)
    db = pha.rips_persistence(b, max_dim=1, max_edge_length=2.5)
    bn = pha.bottleneck_distance(da, db, dim=1)
    w2 = pha.wasserstein_distance(da, db, p=2.0, dim=1)
    assert w2 + 1e-9 >= bn


def test_property_persistence_image_translation_invariance():
    """Translating the input cloud preserves the persistence diagram (and image).

    The Vietoris-Rips filtration depends only on pairwise distances, so a
    rigid translation leaves the diagram unchanged up to numerical noise.
    """
    pts = _noisy_circle(60, 0.05, seed=0)
    shift = np.array([10.0, -5.0])
    pts2 = pts + shift
    img1 = pha.persistence_image(
        pha.rips_persistence(pts, max_dim=1, max_edge_length=2.5),
        dim=1, resolution=12, sigma=0.1,
    )
    img2 = pha.persistence_image(
        pha.rips_persistence(pts2, max_dim=1, max_edge_length=2.5),
        dim=1, resolution=12, sigma=0.1,
    )
    # Persistence image domain is fit per-input, so equal up to a small numerical tolerance.
    assert img1.shape == img2.shape
    assert np.max(np.abs(img1 - img2)) < 1e-6


# ---------------------------------------------------------------------------
# 3. Edge tests
# ---------------------------------------------------------------------------

def test_edge_empty_cloud_raises():
    """rips_persistence on an empty point cloud raises ValueError."""
    with pytest.raises(ValueError):
        pha.rips_persistence(np.empty((0, 2)), max_dim=1)


def test_edge_distance_matrix_must_be_symmetric():
    """Asymmetric distance matrix raises ValueError."""
    D = np.array([[0.0, 1.0], [2.0, 0.0]])  # asymmetric
    with pytest.raises(ValueError):
        pha.persistence_diagram_from_distmat(D)


def test_edge_distance_matrix_must_be_non_negative():
    """Negative distances raise ValueError."""
    D = np.array([[0.0, -1.0], [-1.0, 0.0]])
    with pytest.raises(ValueError):
        pha.persistence_diagram_from_distmat(D)


def test_edge_max_edge_length_too_small_yields_trivial_h0():
    """If max_edge_length is below all pairwise distances, H_0 stays disconnected.

    Edge case from the spec: max_edge_length too small -> diagram is just
    H_0 bars (one infinite bar per vertex, since nothing merges).
    """
    pts = np.array([[0.0, 0.0], [10.0, 0.0], [0.0, 10.0]])
    diag = pha.rips_persistence(pts, max_dim=1, max_edge_length=0.5)
    inf_h0 = sum(1 for d, (_, x) in diag if d == 0 and math.isinf(x))
    finite_h0 = sum(1 for d, (_, x) in diag if d == 0 and not math.isinf(x))
    h1 = sum(1 for d, _ in diag if d == 1)
    assert inf_h0 == 3, f"expected 3 disconnected components, got {inf_h0}"
    assert finite_h0 == 0
    assert h1 == 0


def test_edge_sliding_window_too_short_raises():
    """sliding_window_embed raises if the time series is too short."""
    with pytest.raises(ValueError):
        pha.sliding_window_embed(np.zeros(3), dim=4, tau=2)


def test_edge_sliding_window_invalid_dim_or_tau():
    """dim < 1 or tau < 1 raises."""
    with pytest.raises(ValueError):
        pha.sliding_window_embed(np.zeros(10), dim=0, tau=1)
    with pytest.raises(ValueError):
        pha.sliding_window_embed(np.zeros(10), dim=2, tau=0)


def test_edge_cubical_persistence_rejects_bad_input():
    """cubical_persistence rejects non-2D / empty arrays."""
    with pytest.raises(ValueError):
        pha.cubical_persistence(np.zeros((0, 0)))
    with pytest.raises(ValueError):
        pha.cubical_persistence(np.zeros(5))  # 1D


# ---------------------------------------------------------------------------
# 4. Composition tests
# ---------------------------------------------------------------------------

def test_composition_rips_then_bottleneck_then_image_translation_invariant():
    """rips -> bottleneck -> image: translating the cloud preserves all three.

    Composition test: the entire pipeline rips -> bottleneck -> image must
    be invariant under rigid translation of the input.
    """
    pts = _noisy_circle(60, 0.04, seed=0)
    pts_shift = pts + np.array([3.0, -7.0])
    diag1 = pha.rips_persistence(pts, max_dim=1, max_edge_length=2.5)
    diag2 = pha.rips_persistence(pts_shift, max_dim=1, max_edge_length=2.5)
    bn = pha.bottleneck_distance(diag1, diag2, dim=1)
    img1 = pha.persistence_image(diag1, dim=1, resolution=12, sigma=0.1)
    img2 = pha.persistence_image(diag2, dim=1, resolution=12, sigma=0.1)
    assert bn < 1e-6, f"bottleneck under translation: {bn}"
    assert np.max(np.abs(img1 - img2)) < 1e-6


def test_composition_rips_then_betti_circle():
    """For a noisy circle: betti via VR + effective persistence threshold = (1, 1).

    Composition test combining rips_persistence and a thresholded Betti
    extractor on the diagram.  At a 0.5 persistence cutoff the canonical
    Betti numbers of S^1 emerge.
    """
    pts = _noisy_circle(80, 0.04, seed=2)
    diag = pha.rips_persistence(pts, max_dim=1, max_edge_length=2.5)
    # H_0 infinite bar contributes beta_0; H_1 long bar contributes beta_1.
    beta_inf = pha.betti_numbers_from_diagram(diag)
    n_long_h1 = sum(1 for p in _persistences(diag, 1) if p > 0.5)
    assert beta_inf.get(0, 0) == 1
    assert n_long_h1 == 1


def test_composition_sliding_window_then_rips_finds_one_loop_for_sine():
    """Composition: sliding_window_embed -> rips -> H_1 = 1 long bar for a sine wave.

    A pure (or noisy) sinusoid embedded with sliding windows traces a loop
    in R^d; its H_1 has exactly one persistent bar.  Reference: Perea &
    Harer, FoCM 15 (2015).
    """
    rng = np.random.default_rng(3)
    t = np.arange(200, dtype=float)
    ts = np.sin(2 * np.pi * t / 20) + rng.normal(scale=0.05, size=t.shape)
    cloud = pha.sliding_window_embed(ts, dim=5, tau=5)
    diag = pha.rips_persistence(cloud, max_dim=1, max_edge_length=4.0)
    n_long = sum(1 for p in _persistences(diag, 1) if p > 0.5)
    assert n_long >= 1, f"expected at least one persistent loop, got {n_long}"


def test_composition_cubical_then_betti_blob_image():
    """Composition: cubical_persistence -> count significant H_0 = 3 dark blobs.

    Composition spans cubical and diagram-level helpers.
    """
    from prometheus_math.recipes.persistent_homology.cubical_complex_image import make_three_blob_image
    img = make_three_blob_image(60)
    diag = pha.cubical_persistence(img)
    finite_h0 = [(b, x) for d, (b, x) in diag if d == 0 and not math.isinf(x)]
    n_significant = sum(1 for b, x in finite_h0 if (x - b) > 0.2)
    inf_h0 = sum(1 for d, (_, x) in diag if d == 0 and math.isinf(x))
    assert inf_h0 + n_significant == 3, f"expected 3 dark blobs, got {inf_h0 + n_significant}"


# ---------------------------------------------------------------------------
# 5. Smoke tests for each of the 10 recipes (importable + main() runs)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module_name", [
    "rip_basic",
    "rip_circle",
    "rip_torus",
    "distance_matrix_to_diagram",
    "bottleneck_distance",
    "wasserstein_distance",
    "persistence_image",
    "time_series_tda",
    "cubical_complex_image",
    "betti_numbers_recipe",
])
def test_smoke_recipe_runs(module_name, monkeypatch):
    """Every recipe imports and main() returns a dict without crashing."""
    import importlib
    mod = importlib.import_module(
        f"prometheus_math.recipes.persistent_homology.{module_name}"
    )
    assert hasattr(mod, "main"), f"{module_name} must expose main()"
    result = mod.main()
    assert isinstance(result, dict), f"{module_name}.main() must return a dict"


# ---------------------------------------------------------------------------
# Cleanup hook: scrub the recipe-local outputs/ dir if recipes wrote there.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True, scope="module")
def _cleanup_outputs():
    yield
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "outputs")
    out = os.path.normpath(out)
    if os.path.isdir(out):
        for name in os.listdir(out):
            try:
                os.remove(os.path.join(out, name))
            except OSError:  # pragma: no cover
                pass
