"""Five-axis scorer for Tink 2 — Tier B (CAS Layer C + η_trace).

Each candidate is a correlation `corr(E_A, E_B)` where E_A and E_B
are AST expressions over the dataset's atoms. The candidate is
treated as a tuple-valued feature map `σ(x) = (E_A(x), E_B(x))`.

Tier B scoring axes:

  L_expr                — token count × bits-per-token (lower = simpler)
  z_score_abs           — |Fisher-z(corr)| (higher = stronger relationship)
  basis_projection      — CAS Layer C if decided, else Layer B linear R²
  affordance_gain       — linear-probe gain on synthetic target T
  reconstructability    — composite of η_inverse (GBR) + η_trace (AST steps)

Aggregate scalar (lower is better):
  aggregate = α · L_expr − β · z_score_abs

Pareto-front axes (substrate-value triple; non-dominated = retained):
  (1 − basis_projection)        novelty
  affordance_gain               usefulness
  reconstructability            faithfulness

Tier B differences from cheap-path v1:
  - basis_projection now reports CAS verdict alongside Layer B regression
  - reconstructability is composite (0.7 · η_inverse + 0.3 · η_trace)
  - per-candidate trace_eta_A / trace_eta_B exposed for diagnostic
"""

from __future__ import annotations

import numpy as np
import sympy
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor

from ast_utils import (
    atoms_used,
    evaluate,
    evaluate_with_trace,
    to_sympy,
    token_count,
    format_ast,
)
from cas_layer import cas_score_for_candidate
from trace_eta import (
    trace_reversibility,
    composite_reconstructability,
    W_EXTERNAL,
    W_INTERNAL,
)


# ---------- coefficients (provisional defaults from architecture v0.3.1) --

ALPHA = 0.1
BETA = 1.0
BITS_PER_TOKEN = 4.0


# ---------- per-axis scorers ----------------------------------------------

def z_score_corr(E_A: np.ndarray, E_B: np.ndarray) -> tuple[float, float]:
    if E_A.std() < 1e-12 or E_B.std() < 1e-12:
        return 0.0, 0.0
    n = len(E_A)
    r, _ = pearsonr(E_A, E_B)
    if abs(r) >= 0.9999999:
        r = np.sign(r) * 0.9999999
    z = 0.5 * np.log((1 + r) / (1 - r)) * np.sqrt(n - 3)
    return abs(float(z)), float(r)


def basis_projection_layer_b(E_vals: np.ndarray, basis: np.ndarray) -> float:
    """Layer B — linear R² against materialized identity basis."""
    if E_vals.std() < 1e-12:
        return 1.0
    lr = LinearRegression()
    lr.fit(basis, E_vals)
    pred = lr.predict(basis)
    ss_res = float(np.sum((E_vals - pred) ** 2))
    ss_tot = float(np.sum((E_vals - E_vals.mean()) ** 2))
    if ss_tot < 1e-12:
        return 1.0
    return max(0.0, 1.0 - ss_res / ss_tot)


def affordance_gain_score(
    E_A: np.ndarray, E_B: np.ndarray, target: np.ndarray, baseline: np.ndarray
) -> float:
    features = np.column_stack([E_A, E_B])
    lr_c = LinearRegression()
    lr_c.fit(features, target)
    pred_c = lr_c.predict(features)
    ss_tot = float(np.sum((target - target.mean()) ** 2))
    ss_res_c = float(np.sum((target - pred_c) ** 2))
    r2_c = 0.0 if ss_tot < 1e-12 else max(0.0, 1.0 - ss_res_c / ss_tot)

    lr_b = LinearRegression()
    lr_b.fit(baseline, target)
    pred_b = lr_b.predict(baseline)
    ss_res_b = float(np.sum((target - pred_b) ** 2))
    r2_b = 0.0 if ss_tot < 1e-12 else max(0.0, 1.0 - ss_res_b / ss_tot)

    return max(0.0, r2_c - r2_b)


def eta_inverse_score(
    E_A: np.ndarray, E_B: np.ndarray, atoms: dict[str, np.ndarray]
) -> float:
    """External GBR-based inverse model from σ(x) → atoms used."""
    if not atoms:
        return 0.0
    features = np.column_stack([E_A, E_B])
    accuracies = []
    for _, values in atoms.items():
        if values.std() < 1e-12:
            accuracies.append(1.0)
            continue
        gbr = GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=0)
        gbr.fit(features, values)
        pred = gbr.predict(features)
        ss_res = float(np.sum((values - pred) ** 2))
        ss_tot = float(np.sum((values - values.mean()) ** 2))
        r2 = 0.0 if ss_tot < 1e-12 else max(0.0, 1.0 - ss_res / ss_tot)
        accuracies.append(r2)
    return min(accuracies)


# ---------- composite scoring (Tier B) -------------------------------------

def score_candidate(
    candidate: dict,
    data: dict[str, np.ndarray],
    basis: np.ndarray,
    basis_atom_names: list[str],
    atom_symbols: dict,
    baseline_features: np.ndarray,
) -> dict:
    E_A_ast = candidate["E_A"]
    E_B_ast = candidate["E_B"]

    # Evaluate (with trace for η_trace)
    E_A_val, trace_A = evaluate_with_trace(E_A_ast, data)
    E_B_val, trace_B = evaluate_with_trace(E_B_ast, data)

    # Token count + atoms used
    n_tokens = token_count(E_A_ast) + token_count(E_B_ast) + 1  # +1 for `corr`
    atoms_used_set = atoms_used(E_A_ast) | atoms_used(E_B_ast)
    atoms_used_dict = {name: data[name] for name in atoms_used_set}

    # Axis 1: simplicity
    l_expr = n_tokens * BITS_PER_TOKEN

    # Axis 2: relationship strength
    z_abs, r = z_score_corr(E_A_val, E_B_val)

    # Axis 3: basis projection (CAS Layer C → fall through to Layer B)
    sympy_E_A = to_sympy(E_A_ast, atom_symbols)
    sympy_E_B = to_sympy(E_B_ast, atom_symbols)
    sympy_basis_atoms = [atom_symbols[name] for name in basis_atom_names]
    cas_result = cas_score_for_candidate(sympy_E_A, sympy_E_B, sympy_basis_atoms)

    if cas_result["cas_decided"]:
        bp_score = cas_result["cas_basis_projection"]
        bp_source = "CAS_Layer_C"
        bp_A = 1.0 if cas_result["cas_marker_E_A"] in ("constant", "linear_in_basis") else None
        bp_B = 1.0 if cas_result["cas_marker_E_B"] in ("constant", "linear_in_basis") else None
        # If only one side is in basis via CAS, the other still gets Layer B
        if bp_A is None:
            bp_A = basis_projection_layer_b(E_A_val, basis)
        if bp_B is None:
            bp_B = basis_projection_layer_b(E_B_val, basis)
    else:
        bp_A = basis_projection_layer_b(E_A_val, basis)
        bp_B = basis_projection_layer_b(E_B_val, basis)
        bp_score = max(bp_A, bp_B)
        bp_source = "Layer_B_linear"

    # Axis 4: affordance gain
    aff_gain = affordance_gain_score(E_A_val, E_B_val, data["T"], baseline_features)

    # Axis 5: reconstructability composite (η_inverse + η_trace)
    eta_inv = eta_inverse_score(E_A_val, E_B_val, atoms_used_dict)
    eta_trace_A = trace_reversibility(trace_A)
    eta_trace_B = trace_reversibility(trace_B)
    eta_composite = composite_reconstructability(eta_inv, eta_trace_A, eta_trace_B)

    return {
        "name": candidate["name"],
        "description": candidate["description"],
        "class": candidate["class"],
        "E_A_str": format_ast(E_A_ast),
        "E_B_str": format_ast(E_B_ast),
        "n_tokens": n_tokens,
        "atoms_used": sorted(atoms_used_set),
        "L_expr": l_expr,
        "z_abs": z_abs,
        "r": r,
        "basis_projection": bp_score,
        "basis_projection_source": bp_source,
        "basis_projection_E_A": bp_A,
        "basis_projection_E_B": bp_B,
        "cas_marker_E_A": cas_result["cas_marker_E_A"],
        "cas_marker_E_B": cas_result["cas_marker_E_B"],
        "cas_reduced_to": cas_result["cas_reduced_to"],
        "affordance_gain": aff_gain,
        "eta_inverse": eta_inv,
        "eta_trace_A": eta_trace_A,
        "eta_trace_B": eta_trace_B,
        "reconstructability": eta_composite,
        # aggregate: lower is better
        "aggregate_score": ALPHA * l_expr - BETA * z_abs,
        # Pareto axes
        "pareto_novelty": 1.0 - bp_score,
        "pareto_usefulness": aff_gain,
        "pareto_faithfulness": eta_composite,
    }


def pareto_dominated(a: dict, b: dict) -> bool:
    a_vec = (a["pareto_novelty"], a["pareto_usefulness"], a["pareto_faithfulness"])
    b_vec = (b["pareto_novelty"], b["pareto_usefulness"], b["pareto_faithfulness"])
    if all(b_i >= a_i for a_i, b_i in zip(a_vec, b_vec)):
        if any(b_i > a_i + 1e-9 for a_i, b_i in zip(a_vec, b_vec)):
            return True
    return False


def pareto_front(scored: list[dict]) -> list[dict]:
    return [a for a in scored if not any(pareto_dominated(a, b) for b in scored if b is not a)]
