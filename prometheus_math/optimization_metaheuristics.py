"""prometheus_math.optimization_metaheuristics — black-box optimizers.

Wrappers around evolutionary, swarm, and annealing methods for global
black-box optimization. All functions follow the convention:

    minimize fn(x) for x in R^n  (or {0,1}^n for binary GA)

When to use what
----------------
- **CMA-ES** (`cma_es_minimize`): de-facto best continuous black-box
  optimizer for medium-dim, ill-conditioned, multi-modal problems
  (Hansen, "The CMA Evolution Strategy: A Tutorial", arXiv:1604.00772).
  Adapts a covariance matrix; very strong when gradient is unavailable
  but the landscape is reasonably smooth at scale.
- **GA** (`genetic_algorithm_minimize`,
  `genetic_algorithm_minimize_binary`): population-based metaheuristic
  via DEAP. Use when the search space is combinatorial (binary), or
  when CMA-ES cannot be applied (mixed types, discrete, structural).
- **Simulated annealing** (`simulated_annealing_minimize`): classical
  thermal relaxation; thin wrapper over `scipy.optimize.dual_annealing`.
  Solid baseline for moderate-dim continuous problems.
- **PSO** (`particle_swarm_minimize`): pure-numpy classical Particle
  Swarm Optimization. Useful baseline; no extra dependencies.
- **Benchmark** (`benchmark_metaheuristics`): apples-to-apples
  comparison across methods on a shared benchmark.

All return a `dict`; canonical keys:
    x              : ndarray (or list of int for binary GA)
    optimal_value  : float
    n_iter         : int
    n_evals        : int
    converged      : bool (where applicable)
    history        : list[float] best-so-far per generation/iter

Backends
--------
- ``cma`` (Hansen reference impl, https://github.com/CMA-ES/pycma)
- ``deap`` (Distributed Evolutionary Algorithms in Python)
- ``scipy.optimize.dual_annealing``
- numpy (PSO native impl)

If a backend is missing, the corresponding entry point raises
``ImportError`` with an actionable install message; tests skip cleanly.
"""
from __future__ import annotations

import importlib.util
import math
import warnings
from typing import Callable, Optional, Sequence, Tuple, Union

import numpy as np

_HAS_CMA = importlib.util.find_spec("cma") is not None
_HAS_DEAP = importlib.util.find_spec("deap") is not None
_HAS_SCIPY = importlib.util.find_spec("scipy") is not None


def _require(pkg: str, hint: str) -> None:
    """Raise informative ImportError when an optional backend is missing."""
    if importlib.util.find_spec(pkg) is None:
        raise ImportError(
            f"{pkg!r} is required for this function. Install via: {hint}")


# ---------------------------------------------------------------------------
# 1. CMA-ES
# ---------------------------------------------------------------------------

BoundsLike = Union[None, Tuple[Sequence[float], Sequence[float]]]


def cma_es_minimize(
    fn: Callable[[Sequence[float]], float],
    x0: Sequence[float],
    sigma0: float = 1.0,
    max_iter: int = 200,
    tol: float = 1e-8,
    seed: Optional[int] = None,
    verbose: bool = False,
    bounds: BoundsLike = None,
) -> dict:
    """Covariance Matrix Adaptation Evolution Strategy.

    Parameters
    ----------
    fn       : callable f(x: ndarray) -> float (return NaN to reject sample).
    x0       : initial mean of the sampling distribution; len(x0) sets dim.
    sigma0   : initial step-size (must be > 0).
    max_iter : max number of generations (0 returns x0 unchanged).
    tol      : ftarget; stop when best fn value <= tol.
    seed     : RNG seed for reproducibility.
    verbose  : if True, prints CMA-ES progress to stdout.
    bounds   : optional ``(lower, upper)`` arrays of length len(x0).

    Returns
    -------
    dict with keys: x, optimal_value, n_iter, n_evals, converged, history.

    Reference: Hansen (2016), "The CMA Evolution Strategy: A Tutorial",
    arXiv:1604.00772.
    """
    _require("cma", "pip install cma")
    x0 = list(x0)
    n = len(x0)
    if n == 0:
        raise ValueError("cma_es_minimize: x0 has dim 0 (empty)")
    if not (sigma0 > 0):
        raise ValueError(
            f"cma_es_minimize: sigma0 must be > 0 (got {sigma0!r})")
    if max_iter < 0:
        raise ValueError(f"cma_es_minimize: max_iter < 0 (got {max_iter})")

    # Special case: zero budget. Return x0 with its evaluation.
    if max_iter == 0:
        x_arr = np.asarray(x0, dtype=float)
        try:
            f0 = float(fn(x_arr))
        except Exception:
            f0 = float("nan")
        return {
            "x": x_arr,
            "optimal_value": f0,
            "n_iter": 0,
            "n_evals": 1 if math.isfinite(f0) else 0,
            "converged": False,
            "history": [f0],
        }

    import cma  # type: ignore

    opts: dict = {
        "maxiter": max_iter,
        "ftarget": tol,
        "tolfun": tol,
        "verbose": -9 if not verbose else 1,
        "verb_disp": 0 if not verbose else 1,
        "verb_log": 0,
    }
    if seed is not None:
        # cma expects positive int seed; 0 is "random".
        opts["seed"] = int(seed) + 1
    if bounds is not None:
        lo, hi = bounds
        opts["bounds"] = [list(lo), list(hi)]

    history: list = []
    best_so_far = [float("inf")]

    def _wrapped(xv):
        try:
            v = float(fn(xv))
        except Exception:
            return float("nan")
        if not math.isfinite(v):
            return float("nan")
        if v < best_so_far[0]:
            best_so_far[0] = v
        return v

    es = cma.CMAEvolutionStrategy(x0, float(sigma0), opts)
    while not es.stop():
        solutions = es.ask()
        fitnesses = [_wrapped(s) for s in solutions]
        # Replace NaN with a large penalty that does not affect best-so-far
        # but lets CMA-ES keep working (cma natively rejects NaN, but newer
        # versions accept NaN; we shield by penalty in the worst case).
        finite = [f for f in fitnesses if math.isfinite(f)]
        big = max(finite) * 10 if finite else 1e30
        fitnesses = [f if math.isfinite(f) else big for f in fitnesses]
        es.tell(solutions, fitnesses)
        history.append(best_so_far[0])

    result = es.result
    x_best = np.asarray(result.xbest if result.xbest is not None
                        else result.xfavorite, dtype=float)
    f_best = float(result.fbest) if result.fbest is not None \
        else best_so_far[0]
    n_iter = int(result.iterations)
    n_evals = int(result.evaluations)
    # "Converged" means CMA-ES stopped on a meaningful criterion (tolfun,
    # ftarget, tolx) rather than max-iter exhaustion. The stop dict reports
    # which criteria fired; presence of any non-maxiter key is a success.
    stop_reasons = es.stop()
    non_budget = {k: v for k, v in stop_reasons.items()
                  if k not in ("maxiter", "maxfevals")}
    converged = bool(non_budget) or bool(f_best <= tol)
    if not history:
        history = [f_best]
    return {
        "x": x_best,
        "optimal_value": f_best,
        "n_iter": n_iter,
        "n_evals": n_evals,
        "converged": converged,
        "history": history,
    }


# ---------------------------------------------------------------------------
# 2. Genetic Algorithm (continuous, via DEAP)
# ---------------------------------------------------------------------------


def _validate_ga_args(n_dim: int, n_population: int,
                      n_generations: int) -> None:
    if n_dim <= 0:
        raise ValueError(
            f"genetic_algorithm: n_dim must be > 0 (got {n_dim})")
    if n_population <= 0:
        raise ValueError(
            f"genetic_algorithm: n_population must be > 0 "
            f"(got {n_population})")
    if n_generations < 0:
        raise ValueError(
            f"genetic_algorithm: n_generations must be >= 0 "
            f"(got {n_generations})")


def genetic_algorithm_minimize(
    fn: Callable[[Sequence[float]], float],
    n_dim: int,
    n_population: int = 50,
    n_generations: int = 100,
    bounds: Tuple[float, float] = (-1.0, 1.0),
    cx_prob: float = 0.7,
    mut_prob: float = 0.2,
    seed: Optional[int] = None,
    verbose: bool = False,
) -> dict:
    """Continuous-variable Genetic Algorithm via DEAP.

    Floating-point individuals; uniform initialization in ``bounds``;
    blend crossover (BLX-alpha-style, alpha=0.5); Gaussian mutation;
    tournament selection (size 3).

    Parameters
    ----------
    fn           : callable f(x: list[float]) -> float.
    n_dim        : dimension of search space (must be > 0).
    n_population : population size per generation (must be > 0).
    n_generations: number of generations (must be >= 0).
    bounds       : (lo, hi) box bounds applied componentwise.
    cx_prob      : crossover probability per pairing.
    mut_prob     : mutation probability per individual.
    seed         : RNG seed for reproducibility (sets random + numpy).
    verbose      : if True, prints generation log.

    Returns
    -------
    dict with keys: x, optimal_value, n_evals, history.

    Reference: Holland (1975), "Adaptation in Natural and Artificial
    Systems"; DEAP framework, Fortin et al. (2012), JMLR 13.
    """
    _require("deap", "pip install deap")
    _validate_ga_args(n_dim, n_population, n_generations)

    import random
    from deap import base, creator, tools  # type: ignore

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    lo, hi = float(bounds[0]), float(bounds[1])
    if hi <= lo:
        raise ValueError(
            f"genetic_algorithm: bounds[1] must exceed bounds[0] "
            f"(got {bounds!r})")

    # DEAP requires a global creator type; use a module-unique name to
    # avoid the noisy "class already exists" warning between repeated calls
    # within the same Python process.
    fitness_name = "_PMFitnessMin"
    indiv_name = "_PMIndividual"
    if not hasattr(creator, fitness_name):
        creator.create(fitness_name, base.Fitness, weights=(-1.0,))
    if not hasattr(creator, indiv_name):
        creator.create(indiv_name, list,
                       fitness=getattr(creator, fitness_name))

    Indiv = getattr(creator, indiv_name)
    toolbox = base.Toolbox()
    toolbox.register("attr_float", random.uniform, lo, hi)
    toolbox.register("individual", tools.initRepeat, Indiv,
                     toolbox.attr_float, n=n_dim)
    toolbox.register("population", tools.initRepeat, list,
                     toolbox.individual)

    def _evaluate(ind):
        try:
            v = float(fn(list(ind)))
        except Exception:
            v = float("inf")
        if not math.isfinite(v):
            v = float("inf")
        return (v,)

    toolbox.register("evaluate", _evaluate)
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutGaussian, mu=0.0,
                     sigma=(hi - lo) * 0.1, indpb=0.5)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=n_population)
    history: list = []
    n_evals = 0

    # Evaluate initial population
    fits = [toolbox.evaluate(ind) for ind in pop]
    for ind, f in zip(pop, fits):
        ind.fitness.values = f
    n_evals += len(pop)
    best_so_far = min(f[0] for f in fits)
    history.append(best_so_far)

    for gen in range(n_generations):
        offspring = toolbox.select(pop, len(pop))
        offspring = [toolbox.clone(o) for o in offspring]

        # Crossover
        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cx_prob:
                toolbox.mate(c1, c2)
                del c1.fitness.values
                del c2.fitness.values

        # Mutate + clip to bounds
        for m in offspring:
            if random.random() < mut_prob:
                toolbox.mutate(m)
                del m.fitness.values
            for i in range(len(m)):
                if m[i] < lo:
                    m[i] = lo
                elif m[i] > hi:
                    m[i] = hi

        invalid = [i for i in offspring if not i.fitness.valid]
        for ind in invalid:
            ind.fitness.values = toolbox.evaluate(ind)
        n_evals += len(invalid)

        pop[:] = offspring
        gen_best = min(ind.fitness.values[0] for ind in pop)
        if gen_best < best_so_far:
            best_so_far = gen_best
        history.append(best_so_far)

        if verbose:
            print(f"gen {gen}: best={best_so_far:.6g}")

    best_ind = min(pop, key=lambda i: i.fitness.values[0])
    return {
        "x": np.asarray(list(best_ind), dtype=float),
        "optimal_value": float(best_ind.fitness.values[0]),
        "n_evals": n_evals,
        "n_iter": n_generations,
        "converged": False,
        "history": history,
    }


def genetic_algorithm_minimize_binary(
    fn: Callable[[Sequence[int]], float],
    n_bits: int,
    n_population: int = 50,
    n_generations: int = 100,
    cx_prob: float = 0.7,
    mut_prob: float = 0.2,
    seed: Optional[int] = None,
) -> dict:
    """Binary-string Genetic Algorithm via DEAP.

    Two-point crossover; bit-flip mutation (per-bit p=1/n_bits);
    tournament selection.

    Parameters
    ----------
    fn      : callable f(bits: list[int]) -> float.
    n_bits  : length of binary individual (must be > 0).
    others  : as in genetic_algorithm_minimize.

    Returns
    -------
    dict with keys: x (list[int]), optimal_value, n_evals, history.
    """
    _require("deap", "pip install deap")
    _validate_ga_args(n_bits, n_population, n_generations)

    import random
    from deap import base, creator, tools  # type: ignore

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    fitness_name = "_PMFitnessMinBin"
    indiv_name = "_PMIndividualBin"
    if not hasattr(creator, fitness_name):
        creator.create(fitness_name, base.Fitness, weights=(-1.0,))
    if not hasattr(creator, indiv_name):
        creator.create(indiv_name, list,
                       fitness=getattr(creator, fitness_name))
    Indiv = getattr(creator, indiv_name)

    toolbox = base.Toolbox()
    toolbox.register("attr_bool", random.randint, 0, 1)
    toolbox.register("individual", tools.initRepeat, Indiv,
                     toolbox.attr_bool, n=n_bits)
    toolbox.register("population", tools.initRepeat, list,
                     toolbox.individual)

    def _evaluate(ind):
        try:
            v = float(fn(list(ind)))
        except Exception:
            v = float("inf")
        if not math.isfinite(v):
            v = float("inf")
        return (v,)

    toolbox.register("evaluate", _evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=1.0 / max(n_bits, 1))
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=n_population)
    history: list = []
    n_evals = 0

    fits = [toolbox.evaluate(ind) for ind in pop]
    for ind, f in zip(pop, fits):
        ind.fitness.values = f
    n_evals += len(pop)
    best_so_far = min(f[0] for f in fits)
    history.append(best_so_far)

    for _ in range(n_generations):
        offspring = toolbox.select(pop, len(pop))
        offspring = [toolbox.clone(o) for o in offspring]

        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cx_prob:
                toolbox.mate(c1, c2)
                del c1.fitness.values
                del c2.fitness.values
        for m in offspring:
            if random.random() < mut_prob:
                toolbox.mutate(m)
                del m.fitness.values

        invalid = [i for i in offspring if not i.fitness.valid]
        for ind in invalid:
            ind.fitness.values = toolbox.evaluate(ind)
        n_evals += len(invalid)
        pop[:] = offspring
        gen_best = min(ind.fitness.values[0] for ind in pop)
        if gen_best < best_so_far:
            best_so_far = gen_best
        history.append(best_so_far)

    best_ind = min(pop, key=lambda i: i.fitness.values[0])
    return {
        "x": [int(b) for b in best_ind],
        "optimal_value": float(best_ind.fitness.values[0]),
        "n_evals": n_evals,
        "n_iter": n_generations,
        "converged": False,
        "history": history,
    }


# ---------------------------------------------------------------------------
# 3. Simulated Annealing (scipy.optimize.dual_annealing)
# ---------------------------------------------------------------------------


def simulated_annealing_minimize(
    fn: Callable[[Sequence[float]], float],
    x0: Sequence[float],
    sigma0: float = 1.0,
    max_iter: int = 10000,
    T_init: float = 1.0,
    T_final: float = 1e-3,
    bounds: BoundsLike = None,
    seed: Optional[int] = None,
) -> dict:
    """Simulated annealing via ``scipy.optimize.dual_annealing``.

    ``dual_annealing`` is a generalized simulated-annealing scheme
    (Tsallis & Stariolo, 1996; Xiang et al., 1997). When ``bounds`` is
    None, a symmetric box of half-width ``5*sigma0`` around ``x0`` is
    used.

    Parameters
    ----------
    fn       : callable f(x) -> float.
    x0       : initial point (also used to derive default bounds).
    sigma0   : scale used to derive default symmetric bounds.
    max_iter : max iterations (passed to dual_annealing's ``maxiter``).
    T_init   : initial visiting temperature (mapped to ``initial_temp``).
    T_final  : restart-threshold temperature (mapped to ``restart_temp_ratio``).
    bounds   : optional list of (lo, hi); default = symmetric box.
    seed     : RNG seed.

    Returns
    -------
    dict with keys: x, optimal_value, n_iter, n_evals, converged, history.

    Reference: scipy.optimize.dual_annealing, based on Xiang et al.,
    "Generalized Simulated Annealing for global optimization: the GenSA
    package for R", The R Journal (2013).
    """
    _require("scipy", "pip install scipy")
    from scipy.optimize import dual_annealing  # type: ignore

    x0 = np.asarray(x0, dtype=float)
    n = len(x0)
    if n == 0:
        raise ValueError("simulated_annealing_minimize: x0 has dim 0")
    if not (sigma0 > 0):
        raise ValueError(
            f"simulated_annealing_minimize: sigma0 must be > 0 "
            f"(got {sigma0!r})")
    if max_iter <= 0:
        raise ValueError(
            f"simulated_annealing_minimize: max_iter must be > 0 "
            f"(got {max_iter})")

    if bounds is None:
        radius = 5.0 * sigma0
        b = [(float(x0[i] - radius), float(x0[i] + radius))
             for i in range(n)]
    else:
        # Accept either ([lo...], [hi...]) or [(lo,hi),...] forms.
        if (isinstance(bounds, tuple) and len(bounds) == 2
                and hasattr(bounds[0], "__len__")):
            lo, hi = bounds
            b = list(zip([float(v) for v in lo], [float(v) for v in hi]))
        else:
            b = [(float(p[0]), float(p[1])) for p in bounds]

    history: list = []
    best_so_far = [float("inf")]

    def _wrapped(xv):
        try:
            v = float(fn(xv))
        except Exception:
            v = float("inf")
        if not math.isfinite(v):
            v = float("inf")
        if v < best_so_far[0]:
            best_so_far[0] = v
            history.append(v)
        return v

    initial_temp = max(T_init, 0.01) * 5230.0  # scipy default range
    restart_temp_ratio = max(T_final / max(T_init, 1e-12), 1e-9)
    res = dual_annealing(
        _wrapped, bounds=b, x0=x0, maxiter=max_iter,
        initial_temp=min(max(initial_temp, 0.01), 5e4),
        restart_temp_ratio=min(max(restart_temp_ratio, 1e-9), 0.5),
        seed=seed,
    )
    if not history:
        history.append(float(res.fun))
    return {
        "x": np.asarray(res.x, dtype=float),
        "optimal_value": float(res.fun),
        "n_iter": int(getattr(res, "nit", max_iter)),
        "n_evals": int(getattr(res, "nfev", 0)),
        "converged": bool(res.success),
        "history": history,
    }


# ---------------------------------------------------------------------------
# 4. Particle Swarm Optimization (numpy-only)
# ---------------------------------------------------------------------------


def particle_swarm_minimize(
    fn: Callable[[Sequence[float]], float],
    n_dim: int,
    n_particles: int = 30,
    max_iter: int = 100,
    bounds: Optional[Sequence[Tuple[float, float]]] = None,
    w: float = 0.7,
    c1: float = 1.4,
    c2: float = 1.4,
    seed: Optional[int] = None,
) -> dict:
    """Classical Particle Swarm Optimization (Kennedy & Eberhart, 1995).

    Parameters
    ----------
    fn          : callable f(x) -> float.
    n_dim       : dimension of search space (must be > 0).
    n_particles : swarm size (must be > 0).
    max_iter    : iterations (must be >= 0; 0 returns initial best).
    bounds      : list of (lo, hi); default [(-1, 1)] * n_dim.
    w, c1, c2   : inertia, cognitive, social coefficients.
    seed        : RNG seed.

    Returns
    -------
    dict with keys: x, optimal_value, n_iter, n_evals, converged, history.
    """
    if n_dim <= 0:
        raise ValueError(f"particle_swarm: n_dim must be > 0 (got {n_dim})")
    if n_particles <= 0:
        raise ValueError(
            f"particle_swarm: n_particles must be > 0 (got {n_particles})")
    if max_iter < 0:
        raise ValueError(
            f"particle_swarm: max_iter must be >= 0 (got {max_iter})")

    rng = np.random.default_rng(seed)
    if bounds is None:
        bounds = [(-1.0, 1.0)] * n_dim
    if len(bounds) != n_dim:
        raise ValueError(
            f"particle_swarm: len(bounds)={len(bounds)} != n_dim={n_dim}")
    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([b[1] for b in bounds], dtype=float)
    if np.any(hi <= lo):
        raise ValueError(
            "particle_swarm: each bounds[i][1] must exceed bounds[i][0]")

    pos = lo + rng.random((n_particles, n_dim)) * (hi - lo)
    vel_range = (hi - lo)
    vel = (rng.random((n_particles, n_dim)) - 0.5) * vel_range

    def _eval(x):
        try:
            v = float(fn(x))
        except Exception:
            return float("inf")
        return v if math.isfinite(v) else float("inf")

    fitness = np.array([_eval(pos[i]) for i in range(n_particles)])
    n_evals = n_particles
    p_best = pos.copy()
    p_best_val = fitness.copy()
    g_idx = int(np.argmin(p_best_val))
    g_best = p_best[g_idx].copy()
    g_best_val = float(p_best_val[g_idx])
    history = [g_best_val]

    for _ in range(max_iter):
        r1 = rng.random((n_particles, n_dim))
        r2 = rng.random((n_particles, n_dim))
        vel = (w * vel
               + c1 * r1 * (p_best - pos)
               + c2 * r2 * (g_best - pos))
        # Velocity clamp
        vel = np.clip(vel, -vel_range, vel_range)
        pos = pos + vel
        # Position clamp
        pos = np.clip(pos, lo, hi)

        for i in range(n_particles):
            f = _eval(pos[i])
            n_evals += 1
            if f < p_best_val[i]:
                p_best_val[i] = f
                p_best[i] = pos[i]
                if f < g_best_val:
                    g_best_val = f
                    g_best = pos[i].copy()
        history.append(g_best_val)

    return {
        "x": g_best,
        "optimal_value": g_best_val,
        "n_iter": max_iter,
        "n_evals": n_evals,
        "converged": False,
        "history": history,
    }


# ---------------------------------------------------------------------------
# 5. Benchmark dispatcher
# ---------------------------------------------------------------------------


_DEFAULT_METHODS = ("cma_es", "genetic_algorithm",
                    "simulated_annealing", "particle_swarm")


def benchmark_metaheuristics(
    fn: Callable[[Sequence[float]], float],
    n_dim: int,
    methods: Optional[Sequence[str]] = None,
    n_runs: int = 5,
    seed: Optional[int] = None,
    bounds: Tuple[float, float] = (-3.0, 3.0),
    max_iter: int = 60,
    n_population: int = 40,
) -> dict:
    """Run each method ``n_runs`` times on ``fn`` and report best/mean/std.

    Parameters
    ----------
    fn          : objective.
    n_dim       : problem dimension.
    methods     : subset of {'cma_es','genetic_algorithm',
                  'simulated_annealing','particle_swarm'}; default all.
    n_runs      : runs per method; seeds are seed, seed+1, ..., seed+n_runs-1.
    seed        : base seed.

    Returns
    -------
    {method: {'best': float, 'mean': float, 'std': float, 'values': [..]}}
    """
    if methods is None:
        methods = list(_DEFAULT_METHODS)
    if n_dim <= 0:
        raise ValueError(f"benchmark: n_dim must be > 0 (got {n_dim})")
    if n_runs <= 0:
        raise ValueError(f"benchmark: n_runs must be > 0 (got {n_runs})")

    base_seed = 0 if seed is None else int(seed)
    out: dict = {}
    lo, hi = bounds

    for method in methods:
        vals = []
        for k in range(n_runs):
            s = base_seed + k
            x0 = np.linspace(lo + 0.5, hi - 0.5, n_dim).tolist()
            try:
                if method == "cma_es":
                    r = cma_es_minimize(
                        fn, x0=x0, sigma0=(hi - lo) / 4.0,
                        max_iter=max_iter, seed=s)
                elif method == "genetic_algorithm":
                    r = genetic_algorithm_minimize(
                        fn, n_dim=n_dim, n_population=n_population,
                        n_generations=max_iter, bounds=(lo, hi), seed=s)
                elif method == "simulated_annealing":
                    r = simulated_annealing_minimize(
                        fn, x0=x0, sigma0=(hi - lo) / 4.0,
                        max_iter=max(max_iter, 200), seed=s)
                elif method == "particle_swarm":
                    r = particle_swarm_minimize(
                        fn, n_dim=n_dim, n_particles=n_population,
                        max_iter=max_iter,
                        bounds=[(lo, hi)] * n_dim, seed=s)
                else:
                    raise ValueError(f"benchmark: unknown method {method!r}")
            except ImportError as exc:
                warnings.warn(f"skipping {method}: {exc}")
                vals = []
                break
            vals.append(float(r["optimal_value"]))
        if not vals:
            continue
        arr = np.asarray(vals)
        out[method] = {
            "best": float(arr.min()),
            "mean": float(arr.mean()),
            "std": float(arr.std()),
            "values": vals,
        }
    return out


__all__ = [
    "cma_es_minimize",
    "genetic_algorithm_minimize",
    "genetic_algorithm_minimize_binary",
    "simulated_annealing_minimize",
    "particle_swarm_minimize",
    "benchmark_metaheuristics",
]
