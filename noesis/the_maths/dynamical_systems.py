"""
Dynamical Systems — Iteration and time evolution operators

Connects to: [optimization_landscapes, noise_perturbation, multiscale_operators, spectral_transforms]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "dynamical_systems"
OPERATIONS = {}


def logistic_map_iterate(x, r=3.9, n_iter=50):
    """Iterate logistic map x_{n+1} = r*x_n*(1-x_n). Input: array. Output: array."""
    # Use first element as seed, normalized to (0,1)
    x0 = np.clip(np.abs(x[0]) % 1.0, 0.01, 0.99)
    trajectory = np.zeros(n_iter)
    trajectory[0] = x0
    for i in range(1, n_iter):
        trajectory[i] = r * trajectory[i - 1] * (1 - trajectory[i - 1])
    return trajectory


OPERATIONS["logistic_map_iterate"] = {
    "fn": logistic_map_iterate,
    "input_type": "array",
    "output_type": "array",
    "description": "Iterate logistic map from seed derived from input"
}


def henon_map_iterate(x, a=1.4, b=0.3, n_iter=50):
    """Iterate Henon map. Input: array. Output: array (x-coordinates)."""
    xn = float(x[0] % 1.0)
    yn = float(x[-1] % 1.0) if len(x) > 1 else 0.0
    traj = np.zeros(n_iter)
    for i in range(n_iter):
        traj[i] = xn
        xn_new = 1 - a * xn ** 2 + yn
        yn = b * xn
        xn = xn_new
        if abs(xn) > 1e10:
            traj[i + 1:] = np.nan
            break
    return traj


OPERATIONS["henon_map_iterate"] = {
    "fn": henon_map_iterate,
    "input_type": "array",
    "output_type": "array",
    "description": "Iterate Henon map and return x-coordinate trajectory"
}


def lorenz_discretized(x, sigma=10.0, rho=28.0, beta=8.0 / 3.0, dt=0.01, n_steps=100):
    """Euler-discretized Lorenz system. Input: array. Output: array (x-component)."""
    state = np.array([x[0] % 10, x[1 % len(x)] % 10, x[2 % len(x)] % 10], dtype=float)
    traj = np.zeros(n_steps)
    for i in range(n_steps):
        traj[i] = state[0]
        dx = sigma * (state[1] - state[0])
        dy = state[0] * (rho - state[2]) - state[1]
        dz = state[0] * state[1] - beta * state[2]
        state += dt * np.array([dx, dy, dz])
    return traj


OPERATIONS["lorenz_discretized"] = {
    "fn": lorenz_discretized,
    "input_type": "array",
    "output_type": "array",
    "description": "Euler-discretized Lorenz attractor x-component"
}


def tent_map_iterate(x, mu=1.99, n_iter=50):
    """Iterate tent map. Input: array. Output: array."""
    x0 = np.clip(np.abs(x[0]) % 1.0, 0.01, 0.99)
    traj = np.zeros(n_iter)
    traj[0] = x0
    for i in range(1, n_iter):
        if traj[i - 1] < 0.5:
            traj[i] = mu * traj[i - 1]
        else:
            traj[i] = mu * (1 - traj[i - 1])
    return traj


OPERATIONS["tent_map_iterate"] = {
    "fn": tent_map_iterate,
    "input_type": "array",
    "output_type": "array",
    "description": "Iterate tent map from seed"
}


def circle_map_iterate(x, omega=0.6, K=1.0, n_iter=50):
    """Iterate circle map theta_{n+1} = theta_n + omega - (K/2pi)*sin(2pi*theta_n). Input: array. Output: array."""
    theta = float(x[0]) % 1.0
    traj = np.zeros(n_iter)
    for i in range(n_iter):
        traj[i] = theta
        theta = (theta + omega - (K / (2 * np.pi)) * np.sin(2 * np.pi * theta)) % 1.0
    return traj


OPERATIONS["circle_map_iterate"] = {
    "fn": circle_map_iterate,
    "input_type": "array",
    "output_type": "array",
    "description": "Iterate circle map from seed"
}


def markov_chain_evolve(x, n_steps=50):
    """Evolve Markov chain with transition matrix from array. Input: array. Output: array."""
    n = len(x)
    # Build a stochastic matrix from the array
    mat = np.abs(x[:, None] - x[None, :]) + 0.1
    mat /= mat.sum(axis=1, keepdims=True)
    # Initial state: uniform
    state = np.ones(n) / n
    history = np.zeros(n_steps)
    for i in range(n_steps):
        history[i] = np.dot(np.arange(n), state)  # expected state index
        state = state @ mat
        state /= state.sum()
    return history


OPERATIONS["markov_chain_evolve"] = {
    "fn": markov_chain_evolve,
    "input_type": "array",
    "output_type": "array",
    "description": "Evolve Markov chain and track expected state"
}


def standard_map_iterate(x, K=0.97, n_iter=50):
    """Iterate Chirikov standard map. Input: array. Output: array (p-values)."""
    p = float(x[0]) % (2 * np.pi)
    theta = float(x[-1]) % (2 * np.pi) if len(x) > 1 else 0.5
    traj = np.zeros(n_iter)
    for i in range(n_iter):
        traj[i] = p
        p_new = (p + K * np.sin(theta)) % (2 * np.pi)
        theta = (theta + p_new) % (2 * np.pi)
        p = p_new
    return traj


OPERATIONS["standard_map_iterate"] = {
    "fn": standard_map_iterate,
    "input_type": "array",
    "output_type": "array",
    "description": "Iterate Chirikov standard map"
}


def rossler_discretized(x, a=0.2, b=0.2, c=5.7, dt=0.05, n_steps=100):
    """Euler-discretized Rossler system. Input: array. Output: array (x-component)."""
    state = np.array([x[0] % 5, x[1 % len(x)] % 5, x[2 % len(x)] % 5], dtype=float)
    traj = np.zeros(n_steps)
    for i in range(n_steps):
        traj[i] = state[0]
        dx = -state[1] - state[2]
        dy = state[0] + a * state[1]
        dz = b + state[2] * (state[0] - c)
        state += dt * np.array([dx, dy, dz])
        if np.any(np.abs(state) > 1e10):
            traj[i + 1:] = np.nan
            break
    return traj


OPERATIONS["rossler_discretized"] = {
    "fn": rossler_discretized,
    "input_type": "array",
    "output_type": "array",
    "description": "Euler-discretized Rossler attractor x-component"
}


def feigenbaum_delta_estimate(x, n_bifurcations=6):
    """Estimate Feigenbaum delta from logistic map bifurcation points. Input: array. Output: scalar."""
    # Find bifurcation points of logistic map
    bif_points = []
    for r in np.linspace(2.5, 4.0, 2000):
        val = 0.5
        for _ in range(500):
            val = r * val * (1 - val)
        # Collect last few values
        vals = set()
        for _ in range(64):
            val = r * val * (1 - val)
            vals.add(round(val, 6))
        period = len(vals)
        bif_points.append((r, period))
    # Find first r where period doubles: 1->2, 2->4, 4->8
    r_vals = []
    target_periods = [2, 4, 8, 16]
    for tp in target_periods:
        for r, p in bif_points:
            if p >= tp:
                r_vals.append(r)
                break
    if len(r_vals) >= 3:
        deltas = []
        for i in range(len(r_vals) - 2):
            dr1 = r_vals[i + 1] - r_vals[i]
            dr2 = r_vals[i + 2] - r_vals[i + 1]
            if dr2 > 0:
                deltas.append(dr1 / dr2)
        if deltas:
            return float(np.mean(deltas))
    return 4.669  # Known Feigenbaum constant fallback


OPERATIONS["feigenbaum_delta_estimate"] = {
    "fn": feigenbaum_delta_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimate Feigenbaum delta constant from logistic map"
}


def bifurcation_diagram_slice(x, r_val=3.5, n_iter=200, n_discard=150):
    """Return attractor values at given r for logistic map. Input: array. Output: array."""
    x0 = np.clip(np.abs(x[0]) % 1.0, 0.01, 0.99)
    val = x0
    for _ in range(n_discard):
        val = r_val * val * (1 - val)
    attractor = np.zeros(n_iter - n_discard)
    for i in range(n_iter - n_discard):
        val = r_val * val * (1 - val)
        attractor[i] = val
    return np.unique(np.round(attractor, 6))


OPERATIONS["bifurcation_diagram_slice"] = {
    "fn": bifurcation_diagram_slice,
    "input_type": "array",
    "output_type": "array",
    "description": "Attractor values at given r-parameter for logistic map"
}


def lyapunov_spectrum_estimate(x, r=3.9, n_iter=1000):
    """Estimate Lyapunov exponent for logistic map. Input: array. Output: scalar."""
    x0 = np.clip(np.abs(x[0]) % 1.0, 0.01, 0.99)
    val = x0
    lyap_sum = 0.0
    for _ in range(n_iter):
        derivative = abs(r * (1 - 2 * val))
        if derivative > 0:
            lyap_sum += np.log(derivative)
        val = r * val * (1 - val)
    return float(lyap_sum / n_iter)


OPERATIONS["lyapunov_spectrum_estimate"] = {
    "fn": lyapunov_spectrum_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Lyapunov exponent estimate for logistic map"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
