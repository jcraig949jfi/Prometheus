"""
Lattice Gauge Theory — Discrete quantum field theory on a lattice

Connects to: [feynman_diagram_algebra, tqft, tropical_qft]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "lattice_gauge_theory"
OPERATIONS = {}


def wilson_loop_value(area, beta, string_tension=None):
    """Wilson loop expectation value for a rectangular loop of given area.
    In strong coupling (confinement): <W> ~ exp(-sigma * Area) (area law).
    In weak coupling: <W> ~ exp(-c * Perimeter) (perimeter law).
    We use area law: <W> = exp(-sigma * A) where sigma ~ -ln(beta/(2*N_c^2)) for U(1).
    Simplified: sigma = 1/beta for strong coupling.
    Input: area array, beta scalar. Output: W array."""
    A = np.asarray(area, dtype=float)
    beta_val = float(beta) if not hasattr(beta, '__len__') else float(np.mean(beta))
    if string_tension is None:
        sigma = 1.0 / max(beta_val, 0.01)
    else:
        sigma = string_tension
    return np.exp(-sigma * A)

OPERATIONS["wilson_loop_value"] = {
    "fn": lambda x: wilson_loop_value(x, 2.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Wilson loop expectation value (area law)"
}


def plaquette_action(theta):
    """Plaquette action for U(1) lattice gauge theory.
    S_p = beta * (1 - cos(theta_p)) where theta_p is the plaquette angle.
    theta_p = theta_12 + theta_23 - theta_34 - theta_41.
    Input: theta array (link angles). For 4 links: use first 4. Output: action scalar."""
    theta = np.asarray(theta, dtype=float)
    if len(theta) >= 4:
        theta_p = theta[0] + theta[1] - theta[2] - theta[3]
    else:
        theta_p = np.sum(theta)
    # Return plaquette values = cos(theta_p) for each possible grouping
    # For array input: treat as individual plaquette angles
    return 1.0 - np.cos(theta)

OPERATIONS["plaquette_action"] = {
    "fn": plaquette_action,
    "input_type": "array",
    "output_type": "array",
    "description": "Plaquette action 1-cos(theta) for U(1) gauge theory"
}


def polyakov_loop(link_phases, N_t=None):
    """Polyakov loop: trace of product of temporal link variables along time direction.
    P = (1/N_c) * Tr(prod_t U_0(x,t)). For U(1): P = exp(i * sum of phases).
    Input: link_phases array (temporal link phases). Output: complex P value (as [Re, Im])."""
    phases = np.asarray(link_phases, dtype=float)
    total_phase = np.sum(phases)
    P = np.exp(1j * total_phase)
    return np.array([P.real, P.imag])

OPERATIONS["polyakov_loop"] = {
    "fn": polyakov_loop,
    "input_type": "array",
    "output_type": "array",
    "description": "Polyakov loop for U(1) temporal links"
}


def link_variable_update(theta_old, delta_S, beta_val):
    """Propose a new link variable via Metropolis update.
    Propose theta_new = theta_old + uniform(-delta, delta).
    Accept if Delta S < 0 or with prob exp(-beta * Delta S).
    Input: theta_old array, delta_S scalar, beta scalar. Output: updated theta array."""
    theta = np.asarray(theta_old, dtype=float)
    # Propose random change
    rng = np.random.RandomState(42)
    delta = rng.uniform(-0.5, 0.5, size=theta.shape)
    theta_new = theta + delta
    # Compute action change for each link (simplified: local action ~ beta*cos(theta))
    dS = -beta_val * (np.cos(theta_new) - np.cos(theta))
    # Accept/reject
    r = rng.uniform(0, 1, size=theta.shape)
    accept = (dS < 0) | (r < np.exp(-dS))
    result = np.where(accept, theta_new, theta)
    return result

OPERATIONS["link_variable_update"] = {
    "fn": lambda x: link_variable_update(x, 0.1, 2.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Metropolis update of link variables"
}


def wilson_action_total(plaquette_angles, beta_val):
    """Total Wilson action: S = beta * sum_p (1 - cos(theta_p)).
    Input: plaquette_angles array. Output: total action scalar."""
    theta = np.asarray(plaquette_angles, dtype=float)
    S = beta_val * np.sum(1.0 - np.cos(theta))
    return np.float64(S)

OPERATIONS["wilson_action_total"] = {
    "fn": lambda x: wilson_action_total(x, 2.0),
    "input_type": "array",
    "output_type": "scalar",
    "description": "Total Wilson action for U(1) lattice gauge theory"
}


def lattice_spacing_renormalize(beta_val, Lambda_lat=1.0):
    """Lattice spacing from beta via asymptotic scaling (SU(3)):
    a * Lambda = exp(-beta/(2*b0)) where b0 = 11/(16*pi^2) for SU(3).
    For U(1): a ~ 1/sqrt(beta).
    Input: beta array. Output: lattice spacing array."""
    beta = np.asarray(beta_val, dtype=float)
    # U(1) in 4D: rough relation a ~ 1/sqrt(beta)
    a = Lambda_lat / np.sqrt(np.clip(beta, 0.01, None))
    return a

OPERATIONS["lattice_spacing_renormalize"] = {
    "fn": lattice_spacing_renormalize,
    "input_type": "array",
    "output_type": "array",
    "description": "Lattice spacing from coupling beta"
}


def confinement_order_parameter(polyakov_values):
    """Confinement order parameter: <|P|> where P is the Polyakov loop.
    <|P|> = 0 in confined phase, > 0 in deconfined phase.
    Input: array of Polyakov loop magnitudes. Output: mean value scalar."""
    P = np.asarray(polyakov_values, dtype=float)
    return np.float64(np.mean(np.abs(P)))

OPERATIONS["confinement_order_parameter"] = {
    "fn": confinement_order_parameter,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Confinement order parameter from Polyakov loop"
}


def gauge_field_energy_density(plaquette_angles, beta_val, volume):
    """Energy density: epsilon = (beta / V) * sum_p (1 - cos(theta_p)).
    Input: plaquette_angles array. Output: energy density scalar."""
    theta = np.asarray(plaquette_angles, dtype=float)
    vol = float(volume) if not hasattr(volume, '__len__') else float(np.prod(volume))
    epsilon = beta_val * np.sum(1.0 - np.cos(theta)) / max(vol, 1.0)
    return np.float64(epsilon)

OPERATIONS["gauge_field_energy_density"] = {
    "fn": lambda x: gauge_field_energy_density(x, 2.0, len(x)),
    "input_type": "array",
    "output_type": "scalar",
    "description": "Gauge field energy density from plaquette values"
}


def metropolis_accept_probability(delta_S, beta_val):
    """Metropolis acceptance probability: min(1, exp(-beta * delta_S)).
    Input: delta_S array. Output: acceptance probability array."""
    dS = np.asarray(delta_S, dtype=float)
    return np.minimum(1.0, np.exp(-beta_val * dS))

OPERATIONS["metropolis_accept_probability"] = {
    "fn": lambda x: metropolis_accept_probability(x, 2.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Metropolis acceptance probability"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
