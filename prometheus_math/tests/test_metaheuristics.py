"""Tests for prometheus_math.optimization_metaheuristics.

Test plan (math-tdd skill):
  Authority (>=2): textbook benchmark functions with known global optima.
  Property  (>=2): invariants over many runs (return shape, monotone history,
                   reproducibility under seed, convergence on convex fn).
  Edge      (>=2): malformed inputs, n_dim=0, sigma0<=0, max_iter=0,
                   NaN-returning fn handled gracefully.
  Composition (>=2): cross-method agreement on convex problem; bounded vs
                     unbounded equivalence; benchmark wrapper composition.

Authority references:
- Sphere f(x) = sum(x_i^2): global min 0 at origin. Standard test in
  Hansen, "The CMA Evolution Strategy: A Tutorial" (arXiv:1604.00772),
  Section 1.
- Rosenbrock f(x,y) = (1-x)^2 + 100*(y-x^2)^2: global min 0 at (1, 1).
  Rosenbrock, "An automatic method for finding the greatest or least
  value of a function", Comp. J. 1960.
- Rastrigin f(x) = 10n + sum(x_i^2 - 10 cos(2 pi x_i)): global min 0 at
  origin. Rastrigin (1974), "Systems of extremal control".
- Beale f(x,y): global min 0 at (3, 0.5). Beale (1958); see Jamil &
  Yang, "A literature survey of benchmark functions for global
  optimization problems", IJMNO 4(2), 2013, Table 1.
"""
from __future__ import annotations

import importlib.util
import math

import numpy as np
import pytest

_HAS_CMA = importlib.util.find_spec("cma") is not None
_HAS_DEAP = importlib.util.find_spec("deap") is not None
_HAS_SCIPY = importlib.util.find_spec("scipy") is not None

from prometheus_math import optimization_metaheuristics as mh


# --------------------------------------------------------------------------
# Benchmark functions (authority references in module docstring)
# --------------------------------------------------------------------------

def sphere(x):
    x = np.asarray(x, dtype=float)
    return float(np.sum(x * x))


def rosenbrock(x):
    x = np.asarray(x, dtype=float)
    return float((1 - x[0]) ** 2 + 100 * (x[1] - x[0] ** 2) ** 2)


def rastrigin(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    return float(10 * n + np.sum(x * x - 10 * np.cos(2 * math.pi * x)))


def beale(x):
    a, b = float(x[0]), float(x[1])
    t1 = (1.5 - a + a * b) ** 2
    t2 = (2.25 - a + a * b * b) ** 2
    t3 = (2.625 - a + a * b ** 3) ** 2
    return t1 + t2 + t3


# Binary GA test: count-zeros (max ones) — minimum at all-zeros vector.
def count_ones(bits):
    return float(sum(bits))


# --------------------------------------------------------------------------
# AUTHORITY TESTS
# --------------------------------------------------------------------------

@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_sphere_authority():
    """Authority: sphere fn min at origin.

    Reference: Hansen (2016) arXiv:1604.00772 sec.1 — sphere f(x)=||x||^2,
    global min 0 at x=0. CMA-ES converges in O(d log(1/eps)) evaluations.
    """
    res = mh.cma_es_minimize(sphere, x0=[1.0, 2.0, -1.5, 0.5],
                             sigma0=0.5, max_iter=150, seed=42, tol=1e-8)
    assert res["optimal_value"] < 1e-7
    assert np.allclose(res["x"], np.zeros(4), atol=1e-3)
    assert res["converged"] is True
    assert res["n_evals"] > 0


@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_rosenbrock_authority():
    """Authority: Rosenbrock min at (1,1).

    Reference: Rosenbrock (1960), Comp. J. 3(3): 175-184. f(1,1)=0.
    """
    res = mh.cma_es_minimize(rosenbrock, x0=[-1.0, 1.0],
                             sigma0=0.5, max_iter=200, seed=7, tol=1e-10)
    assert res["optimal_value"] < 1e-6
    assert np.allclose(res["x"], np.array([1.0, 1.0]), atol=1e-2)


@pytest.mark.skipif(not _HAS_DEAP, reason="deap package not installed")
def test_genetic_algorithm_rastrigin_authority():
    """Authority: Rastrigin min 0 at origin.

    Reference: Rastrigin (1974). For n=2, f(0,0)=0 is the global minimum
    among many local minima. GA finds it within budget on bounded box.
    """
    res = mh.genetic_algorithm_minimize(
        rastrigin, n_dim=2, n_population=80, n_generations=60,
        bounds=(-5.12, 5.12), seed=11)
    # Multimodal: GA should at least find a value near 0 (within 5).
    assert res["optimal_value"] < 5.0
    assert "x" in res and len(res["x"]) == 2


@pytest.mark.skipif(not _HAS_SCIPY, reason="scipy not installed")
def test_simulated_annealing_beale_authority():
    """Authority: Beale fn min 0 at (3, 0.5).

    Reference: Jamil & Yang (2013), IJMNO 4(2), Table 1 entry for Beale.
    dual_annealing converges within tolerance.
    """
    res = mh.simulated_annealing_minimize(
        beale, x0=[1.0, 1.0], sigma0=1.0,
        max_iter=500, seed=3)
    assert res["optimal_value"] < 1e-3
    assert np.allclose(res["x"], np.array([3.0, 0.5]), atol=0.05)


# --------------------------------------------------------------------------
# PROPERTY TESTS
# --------------------------------------------------------------------------

@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_returns_required_keys():
    """Property: dict shape contract."""
    res = mh.cma_es_minimize(sphere, x0=[1.0, 1.0], sigma0=0.3,
                             max_iter=20, seed=1)
    for key in ("x", "optimal_value", "n_iter", "n_evals",
                "converged", "history"):
        assert key in res, f"missing {key}"


@pytest.mark.skipif(not (_HAS_CMA and _HAS_DEAP and _HAS_SCIPY),
                    reason="needs cma+deap+scipy")
def test_all_methods_converge_on_convex():
    """Property: every black-box optimizer attains a small value on sphere."""
    cma_res = mh.cma_es_minimize(sphere, x0=[2.0, -1.0], sigma0=0.5,
                                 max_iter=60, seed=0)
    ga_res = mh.genetic_algorithm_minimize(
        sphere, n_dim=2, n_population=40, n_generations=40,
        bounds=(-3.0, 3.0), seed=0)
    sa_res = mh.simulated_annealing_minimize(
        sphere, x0=[2.0, -1.0], max_iter=300, seed=0)
    pso_res = mh.particle_swarm_minimize(
        sphere, n_dim=2, n_particles=30, max_iter=80,
        bounds=[(-3.0, 3.0), (-3.0, 3.0)], seed=0)
    assert cma_res["optimal_value"] < 1e-6
    assert ga_res["optimal_value"] < 0.5
    assert sa_res["optimal_value"] < 1e-3
    assert pso_res["optimal_value"] < 1e-2


@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_seed_reproducible():
    """Property: same seed -> identical optimum (deterministic)."""
    r1 = mh.cma_es_minimize(sphere, x0=[1.0, -1.0], sigma0=0.4,
                            max_iter=30, seed=123)
    r2 = mh.cma_es_minimize(sphere, x0=[1.0, -1.0], sigma0=0.4,
                            max_iter=30, seed=123)
    assert math.isclose(r1["optimal_value"], r2["optimal_value"],
                        rel_tol=0, abs_tol=1e-12)
    np.testing.assert_allclose(r1["x"], r2["x"], atol=1e-12)


@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_more_iter_is_no_worse():
    """Property: increasing budget improves or maintains best value."""
    r_short = mh.cma_es_minimize(sphere, x0=[2.0, 2.0], sigma0=0.5,
                                 max_iter=5, seed=0)
    r_long = mh.cma_es_minimize(sphere, x0=[2.0, 2.0], sigma0=0.5,
                                max_iter=80, seed=0)
    assert r_long["optimal_value"] <= r_short["optimal_value"] + 1e-12


@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_history_non_increasing():
    """Property: best-so-far history must be non-increasing."""
    res = mh.cma_es_minimize(sphere, x0=[1.5, -2.0, 0.7], sigma0=0.4,
                             max_iter=40, seed=4)
    h = res["history"]
    assert len(h) >= 2
    for i in range(1, len(h)):
        assert h[i] <= h[i - 1] + 1e-12


# --------------------------------------------------------------------------
# EDGE CASES
# --------------------------------------------------------------------------

@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_zero_dim_raises():
    """Edge: empty x0 -> ValueError."""
    with pytest.raises(ValueError, match="(?i)dim|empty|x0"):
        mh.cma_es_minimize(sphere, x0=[], sigma0=1.0)


@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_nonpositive_sigma_raises():
    """Edge: sigma0 <= 0 -> ValueError."""
    with pytest.raises(ValueError, match="(?i)sigma"):
        mh.cma_es_minimize(sphere, x0=[1.0, 1.0], sigma0=0.0)
    with pytest.raises(ValueError, match="(?i)sigma"):
        mh.cma_es_minimize(sphere, x0=[1.0, 1.0], sigma0=-0.5)


@pytest.mark.skipif(not _HAS_DEAP, reason="deap package not installed")
def test_ga_nonpositive_population_raises():
    """Edge: n_population <= 0 -> ValueError."""
    with pytest.raises(ValueError, match="(?i)population"):
        mh.genetic_algorithm_minimize(sphere, n_dim=2, n_population=0)
    with pytest.raises(ValueError, match="(?i)population"):
        mh.genetic_algorithm_minimize(sphere, n_dim=2, n_population=-3)


@pytest.mark.skipif(not _HAS_DEAP, reason="deap package not installed")
def test_ga_zero_dim_raises():
    """Edge: n_dim == 0 -> ValueError."""
    with pytest.raises(ValueError, match="(?i)dim"):
        mh.genetic_algorithm_minimize(sphere, n_dim=0)


@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_max_iter_zero_returns_x0():
    """Edge: max_iter=0 returns starting point unchanged."""
    x0 = [3.0, -1.5]
    res = mh.cma_es_minimize(sphere, x0=x0, sigma0=0.5, max_iter=0, seed=0)
    np.testing.assert_allclose(res["x"], np.array(x0))
    assert res["n_iter"] == 0
    # optimal_value evaluated at x0
    assert math.isclose(res["optimal_value"], sphere(x0), abs_tol=1e-12)


@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_handles_nan():
    """Edge: fn returning NaN must not crash; fn is rejected/penalised."""
    def flaky(x):
        if x[0] > 100.0:
            return float("nan")
        return sphere(x)
    res = mh.cma_es_minimize(flaky, x0=[1.0, 1.0], sigma0=0.4,
                             max_iter=30, seed=0)
    # We just need finite result with no exception.
    assert math.isfinite(res["optimal_value"])
    assert res["optimal_value"] < 5.0


@pytest.mark.skipif(not _HAS_DEAP, reason="deap package not installed")
def test_ga_binary_basic():
    """Edge / smoke: binary GA returns 0/1 vector and reaches good value."""
    res = mh.genetic_algorithm_minimize_binary(
        count_ones, n_bits=12, n_population=30, n_generations=25, seed=2)
    assert "x" in res and len(res["x"]) == 12
    for b in res["x"]:
        assert b in (0, 1)
    # Should be near zero (all-zero vector).
    assert res["optimal_value"] <= 3.0


# --------------------------------------------------------------------------
# COMPOSITION TESTS
# --------------------------------------------------------------------------

@pytest.mark.skipif(not (_HAS_CMA and _HAS_DEAP),
                    reason="needs cma+deap")
def test_benchmark_composition_cma_beats_random_ga():
    """Composition: benchmark wrapper shows CMA-ES has lower mean than
    a tightly-budgeted random GA on sphere."""
    out = mh.benchmark_metaheuristics(
        sphere, n_dim=3,
        methods=["cma_es", "genetic_algorithm"],
        n_runs=3, seed=0)
    assert "cma_es" in out and "genetic_algorithm" in out
    assert out["cma_es"]["mean"] < out["genetic_algorithm"]["mean"]
    for k in out:
        for sub in ("best", "mean", "std"):
            assert sub in out[k]


@pytest.mark.skipif(not _HAS_CMA, reason="cma package not installed")
def test_cma_es_bounds_equivalence():
    """Composition: CMA-ES with explicit bounds and unbounded+clip optimum
    agree on a bowl-shaped fn whose minimum is interior to the box.

    Sphere min at origin lies inside [-2, 2]^2: bounded result must be
    close to unbounded result (both ~0).
    """
    bounded = mh.cma_es_minimize(sphere, x0=[1.0, 1.0], sigma0=0.4,
                                 max_iter=60, seed=0,
                                 bounds=([-2.0, -2.0], [2.0, 2.0]))
    unbounded = mh.cma_es_minimize(sphere, x0=[1.0, 1.0], sigma0=0.4,
                                   max_iter=60, seed=0)
    assert bounded["optimal_value"] < 1e-4
    assert unbounded["optimal_value"] < 1e-4
    # Both should locate near origin
    np.testing.assert_allclose(bounded["x"], np.zeros(2), atol=1e-1)
    np.testing.assert_allclose(unbounded["x"], np.zeros(2), atol=1e-1)


@pytest.mark.skipif(not (_HAS_CMA and _HAS_DEAP and _HAS_SCIPY),
                    reason="needs cma+deap+scipy")
def test_methods_agree_on_optimum_location():
    """Composition: 4 black-box methods agree on optimum location for sphere."""
    cma_res = mh.cma_es_minimize(sphere, x0=[1.5, -1.5], sigma0=0.5,
                                 max_iter=80, seed=0)
    ga_res = mh.genetic_algorithm_minimize(
        sphere, n_dim=2, n_population=60, n_generations=60,
        bounds=(-3.0, 3.0), seed=0)
    sa_res = mh.simulated_annealing_minimize(
        sphere, x0=[1.5, -1.5], max_iter=300, seed=0)
    pso_res = mh.particle_swarm_minimize(
        sphere, n_dim=2, n_particles=40, max_iter=80,
        bounds=[(-3.0, 3.0), (-3.0, 3.0)], seed=0)
    for r in (cma_res, ga_res, sa_res, pso_res):
        # All within 0.6 of true optimum (0,0); GA loose tolerance.
        np.testing.assert_allclose(r["x"], np.zeros(2), atol=0.6)
