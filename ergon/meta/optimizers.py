"""
Optimizer panel v2a (4 methods; expansion to 8 in v2b).

Each optimizer runs on a landscape with matched budget (max function
evaluations), records the FULL trajectory (subsampled to ~100 steps), and
returns a Trajectory object.

v2a panel:
  lbfgsb            -- scipy L-BFGS-B from random start
  nelder_mead       -- scipy Nelder-Mead from random start
  cmaes             -- evolutionary covariance adaptation (pycma)
  random_restart    -- N random starts x short local search

v2b will add Adam / simulated annealing / trust-region / Sobol.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
from scipy.optimize import minimize, dual_annealing
from scipy.stats import qmc

from ergon.meta.trajectory import Trajectory


# ---------- helpers ----------------------------------------------------------

def _wrap_objective(landscape, counter, box: float = 4.0,
                     overshoot_penalty: float = 10.0):
    """Wrap landscape.evaluate with:
      - eval counter
      - subsampled position/value/grad logging
      - soft box penalty: evaluation outside [-box, box] gets f(clip(x)) plus
        quadratic overshoot penalty. Prevents Nelder-Mead / fallback CMA-ES from
        wandering off and blowing up final_value on flat landscapes.
    """
    state = {"positions": [], "values": [], "grads": []}

    def f(x):
        x = np.asarray(x, dtype=float)
        overshoot = np.maximum(np.abs(x) - box, 0.0)
        if overshoot.sum() > 0:
            x_eval = np.clip(x, -box, box)
            val = float(landscape.evaluate(x_eval)) + overshoot_penalty * float((overshoot ** 2).sum())
        else:
            val = float(landscape.evaluate(x))
        gnorm = float(np.linalg.norm(landscape.grad(np.clip(x, -box, box))))
        counter["n"] += 1
        if counter["n"] % 5 == 0 or counter["n"] == 1:
            state["positions"].append(np.clip(x, -box, box).copy())
            state["values"].append(val)
            state["grads"].append(gnorm)
        return val

    def g(x):
        return landscape.grad(np.clip(np.asarray(x, dtype=float), -box, box))

    return f, g, state


def _pack_trajectory(name: str, state: dict, final_x, final_val,
                     total_iters: int, eps_target: Optional[float],
                     eps: float = 1e-3) -> Trajectory:
    pos = np.array(state["positions"]) if state["positions"] else np.zeros((0, len(final_x)))
    vals = np.array(state["values"])
    grads = np.array(state["grads"])

    iters_to_eps = -1
    if eps_target is not None and len(vals):
        hits = np.where(vals <= eps_target + eps)[0]
        if len(hits):
            iters_to_eps = int(hits[0]) * 5  # account for subsample stride

    return Trajectory(
        optimizer=name,
        positions=pos,
        values=vals,
        grad_norms=grads,
        iters_to_eps=iters_to_eps,
        total_iters=total_iters,
        final_x=np.asarray(final_x, dtype=float),
        final_value=float(final_val),
    )


# ---------- individual optimizers --------------------------------------------

def run_lbfgsb(landscape, x0, budget: int = 500, eps_target=None,
               box: float = 4.0) -> Trajectory:
    counter = {"n": 0}
    f, g, state = _wrap_objective(landscape, counter, box=box)
    bounds = [(-box, box)] * landscape.d
    res = minimize(f, x0, jac=g, method='L-BFGS-B', bounds=bounds,
                   options={'maxiter': budget, 'ftol': 1e-10, 'gtol': 1e-8})
    return _pack_trajectory("lbfgsb", state, res.x, res.fun, counter["n"], eps_target)


def run_nelder_mead(landscape, x0, budget: int = 500, eps_target=None,
                    box: float = 4.0) -> Trajectory:
    counter = {"n": 0}
    f, _, state = _wrap_objective(landscape, counter, box=box)
    res = minimize(f, x0, method='Nelder-Mead',
                   options={'maxiter': budget, 'xatol': 1e-6, 'fatol': 1e-8})
    return _pack_trajectory("nelder_mead", state, res.x, res.fun, counter["n"], eps_target)


def run_cmaes(landscape, x0, budget: int = 500, eps_target=None,
              box: float = 4.0) -> Trajectory:
    try:
        import cma
    except ImportError:
        return _run_cmaes_fallback(landscape, x0, budget, eps_target, box)

    counter = {"n": 0}
    f, _, state = _wrap_objective(landscape, counter, box=box)
    sigma0 = 0.5
    opts = {
        'bounds': [[-box] * landscape.d, [box] * landscape.d],
        'maxfevals': budget,
        'verbose': -9,
        'tolfun': 1e-8,
    }
    es = cma.CMAEvolutionStrategy(list(x0), sigma0, opts)
    while not es.stop() and counter["n"] < budget:
        pop = es.ask()
        fs = [f(p) for p in pop]
        es.tell(pop, fs)
    best = es.result.xbest if es.result.xbest is not None else x0
    best_f = float(es.result.fbest) if es.result.fbest is not None else f(best)
    return _pack_trajectory("cmaes", state, best, best_f, counter["n"], eps_target)


def _run_cmaes_fallback(landscape, x0, budget, eps_target, box):
    """Lightweight (1+1) evolution strategy if pycma unavailable."""
    counter = {"n": 0}
    f, _, state = _wrap_objective(landscape, counter, box=box)
    rng = np.random.default_rng(0)
    x = np.array(x0); fx = f(x); sigma = 0.5
    best_x, best_f = x.copy(), fx
    while counter["n"] < budget:
        cand = x + sigma * rng.standard_normal(len(x))
        cand = np.clip(cand, -box, box)
        fc = f(cand)
        if fc < fx:
            x, fx = cand, fc
            sigma *= 1.1
            if fx < best_f:
                best_x, best_f = x.copy(), fx
        else:
            sigma *= 0.95
        sigma = min(max(sigma, 1e-4), box)
    return _pack_trajectory("cmaes_fallback", state, best_x, best_f,
                            counter["n"], eps_target)


def run_random_restart(landscape, x0, budget: int = 500, eps_target=None,
                       box: float = 4.0, n_restarts: int = 10) -> Trajectory:
    counter = {"n": 0}
    f, g, state = _wrap_objective(landscape, counter, box=box)
    per_budget = max(10, budget // n_restarts)
    bounds = [(-box, box)] * landscape.d
    rng = np.random.default_rng(42)
    best_x, best_f = np.array(x0), float("inf")
    for _ in range(n_restarts):
        if counter["n"] >= budget:
            break
        start = rng.uniform(-box, box, size=landscape.d)
        try:
            res = minimize(f, start, jac=g, method='L-BFGS-B', bounds=bounds,
                           options={'maxiter': per_budget, 'ftol': 1e-10})
            if res.fun < best_f:
                best_x, best_f = res.x, float(res.fun)
        except Exception:
            continue
    return _pack_trajectory("random_restart", state, best_x, best_f,
                            counter["n"], eps_target)


# ---------- v2b additions ----------------------------------------------------

def run_adam(landscape, x0, budget: int = 500, eps_target=None,
             box: float = 4.0, lr: float = 0.05,
             beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8) -> Trajectory:
    """Adam stochastic gradient descent. Adds small noise to gradient each step
    to test Adam's noise-tolerance bias."""
    counter = {"n": 0}
    f, g, state = _wrap_objective(landscape, counter, box=box)
    rng = np.random.default_rng(7)
    x = np.array(x0, dtype=float)
    f(x)  # log start
    m = np.zeros_like(x); v = np.zeros_like(x)
    best_x, best_f = x.copy(), float("inf")
    for t in range(1, budget + 1):
        if counter["n"] >= budget:
            break
        # Add small noise to simulate stochastic gradient
        grad = g(x) + 0.05 * rng.standard_normal(x.shape)
        m = beta1 * m + (1 - beta1) * grad
        v = beta2 * v + (1 - beta2) * (grad * grad)
        m_hat = m / (1 - beta1 ** t)
        v_hat = v / (1 - beta2 ** t)
        x = x - lr * m_hat / (np.sqrt(v_hat) + eps)
        x = np.clip(x, -box, box)
        fv = f(x)
        if fv < best_f:
            best_x, best_f = x.copy(), float(fv)
    return _pack_trajectory("adam", state, best_x, best_f,
                            counter["n"], eps_target)


def run_simulated_annealing(landscape, x0, budget: int = 500, eps_target=None,
                             box: float = 4.0) -> Trajectory:
    """scipy.optimize.dual_annealing wrapper. Uses Tsallis-Stariolo + LBFGS local
    refinement; good for landscapes with many basins."""
    counter = {"n": 0}
    f, _, state = _wrap_objective(landscape, counter, box=box)
    bounds = [(-box, box)] * landscape.d
    try:
        res = dual_annealing(
            f, bounds, x0=np.asarray(x0, dtype=float),
            maxiter=budget, maxfun=budget, seed=11,
            no_local_search=False,
        )
        best_x, best_f = res.x, float(res.fun)
    except Exception:
        best_x, best_f = np.asarray(x0, dtype=float), float(f(x0))
    return _pack_trajectory("simulated_annealing", state, best_x, best_f,
                            counter["n"], eps_target)


def run_trust_region(landscape, x0, budget: int = 500, eps_target=None,
                      box: float = 4.0) -> Trajectory:
    """scipy 'trust-constr' method: quasi-Newton trust-region.

    Different curvature handling than L-BFGS — may converge differently on
    near-singular landscapes.
    """
    counter = {"n": 0}
    f, g, state = _wrap_objective(landscape, counter, box=box)
    bounds = [(-box, box)] * landscape.d
    try:
        res = minimize(f, x0, jac=g, method='trust-constr',
                       bounds=[(-box, box)] * landscape.d,
                       options={'maxiter': budget, 'gtol': 1e-7})
        best_x, best_f = res.x, float(res.fun)
    except Exception:
        best_x, best_f = np.asarray(x0, dtype=float), float(f(x0))
    return _pack_trajectory("trust_region", state, best_x, best_f,
                            counter["n"], eps_target)


def run_sobol_local(landscape, x0, budget: int = 500, eps_target=None,
                     box: float = 4.0, n_seeds: int = 16) -> Trajectory:
    """Sobol low-discrepancy seeds + short L-BFGS-B refine on each. Tests
    structured-coverage exploration vs random_restart."""
    counter = {"n": 0}
    f, g, state = _wrap_objective(landscape, counter, box=box)
    bounds = [(-box, box)] * landscape.d
    sampler = qmc.Sobol(d=landscape.d, scramble=True, seed=23)
    raw = sampler.random_base2(m=int(np.log2(n_seeds)))
    seeds = -box + 2 * box * raw
    per_budget = max(10, budget // n_seeds)
    best_x, best_f = np.asarray(x0, dtype=float), float("inf")
    for s in seeds:
        if counter["n"] >= budget:
            break
        try:
            res = minimize(f, s, jac=g, method='L-BFGS-B', bounds=bounds,
                           options={'maxiter': per_budget, 'ftol': 1e-10})
            if res.fun < best_f:
                best_x, best_f = res.x, float(res.fun)
        except Exception:
            continue
    return _pack_trajectory("sobol_local", state, best_x, best_f,
                            counter["n"], eps_target)


# ---------- panel runner -----------------------------------------------------

def run_panel(landscape, x0=None, budget: int = 500, eps_target=None,
              box: float = 4.0, expanded: bool = True) -> list:
    """Run the optimizer panel and return list of Trajectories.

    expanded=True (v2b default): 8 optimizers — adds Adam, simulated_annealing,
    trust_region, sobol_local to the v2a 4-method panel.
    """
    if x0 is None:
        x0 = np.zeros(landscape.d) + 0.1
    trajs = []
    trajs.append(run_lbfgsb(landscape, x0, budget=budget, eps_target=eps_target, box=box))
    trajs.append(run_nelder_mead(landscape, x0, budget=budget, eps_target=eps_target, box=box))
    trajs.append(run_cmaes(landscape, x0, budget=budget, eps_target=eps_target, box=box))
    trajs.append(run_random_restart(landscape, x0, budget=budget, eps_target=eps_target, box=box))
    if expanded:
        trajs.append(run_adam(landscape, x0, budget=budget, eps_target=eps_target, box=box))
        trajs.append(run_simulated_annealing(landscape, x0, budget=budget, eps_target=eps_target, box=box))
        trajs.append(run_trust_region(landscape, x0, budget=budget, eps_target=eps_target, box=box))
        trajs.append(run_sobol_local(landscape, x0, budget=budget, eps_target=eps_target, box=box))
    return trajs
