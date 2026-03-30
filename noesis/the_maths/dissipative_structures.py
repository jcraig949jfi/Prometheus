"""
Dissipative Structures — Prigogine's non-equilibrium thermodynamics mathematics

Connects to: [thermodynamics, reaction-diffusion, bifurcation theory, pattern formation, chemical kinetics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "dissipative_structures"
OPERATIONS = {}


def entropy_production_rate(x):
    """Compute the entropy production rate sigma = sum_k J_k * X_k where J_k are
    thermodynamic fluxes and X_k are thermodynamic forces.
    Input: array (alternating fluxes and forces). Output: scalar."""
    n = len(x)
    pairs = n // 2
    if pairs == 0:
        return float(np.abs(x[0]))
    fluxes = x[0:2 * pairs:2]
    forces = x[1:2 * pairs:2]
    # Entropy production rate (must be >= 0 by second law)
    sigma = np.sum(fluxes * forces)
    return float(sigma)


OPERATIONS["entropy_production_rate"] = {
    "fn": entropy_production_rate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes entropy production rate sigma = sum(J_k * X_k)"
}


def brusselator_steady_state(x):
    """Compute the Brusselator steady state and its stability.
    Brusselator: dx/dt = A - (B+1)x + x^2*y, dy/dt = Bx - x^2*y.
    Steady state: x_s = A, y_s = B/A.
    Input: array [A, B, ...]. Output: array [x_s, y_s, stable(1/0), eigenvalue_real_max]."""
    A = np.abs(x[0]) + 0.1 if len(x) > 0 else 1.0
    B = np.abs(x[1]) + 0.1 if len(x) > 1 else 3.0

    x_s = A
    y_s = B / A

    # Jacobian at steady state:
    # J = [[B-1, A^2], [-B, -A^2]]
    J = np.array([[B - 1, A ** 2], [-B, -A ** 2]])
    eigenvalues = np.linalg.eigvals(J)
    max_real = float(np.max(eigenvalues.real))
    stable = 1.0 if max_real < 0 else 0.0

    result = np.zeros(max(len(x), 4))
    result[0] = x_s
    result[1] = y_s
    result[2] = stable
    result[3] = max_real
    return result[:len(x)]


OPERATIONS["brusselator_steady_state"] = {
    "fn": brusselator_steady_state,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Brusselator steady state (x_s=A, y_s=B/A) and stability"
}


def turing_pattern_eigenvalue(x):
    """Compute eigenvalues determining Turing pattern instability.
    A Turing instability occurs when diffusion destabilizes a homogeneous steady state.
    Condition: the diffusion-modified Jacobian has a positive eigenvalue for some wavenumber k.
    Input: array [a11, a12, a21, a22, D1, D2, ...wavenumbers]. Output: array (max eigenvalues per k)."""
    if len(x) < 6:
        # Pad with defaults
        params = np.zeros(7)
        params[:len(x)] = x
        params[4] = max(params[4], 0.01)
        params[5] = max(params[5], 0.1)
        params[6] = 1.0
    else:
        params = x

    a11, a12, a21, a22 = params[0], params[1], params[2], params[3]
    D1, D2 = max(np.abs(params[4]), 0.01), max(np.abs(params[5]), 0.01)
    wavenumbers = np.abs(params[6:]) if len(params) > 6 else np.array([1.0])

    if len(wavenumbers) == 0:
        wavenumbers = np.array([1.0])

    results = np.zeros(len(wavenumbers))
    for i, k in enumerate(wavenumbers):
        k2 = k ** 2
        # Modified Jacobian: J_k = J - D*k^2
        Jk = np.array([[a11 - D1 * k2, a12],
                        [a21, a22 - D2 * k2]])
        eigs = np.linalg.eigvals(Jk)
        results[i] = float(np.max(eigs.real))

    # Pad to match input length
    out = np.zeros(len(x))
    out[:len(results)] = results
    return out


OPERATIONS["turing_pattern_eigenvalue"] = {
    "fn": turing_pattern_eigenvalue,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Turing instability eigenvalues for diffusion-coupled system"
}


def dissipation_function(x):
    """Compute the Rayleigh dissipation function Phi = (1/2) * sum_ij L_ij * X_i * X_j
    where L is the Onsager matrix and X are thermodynamic forces.
    Input: array (thermodynamic forces). Output: scalar."""
    n = len(x)
    # Construct symmetric positive-definite Onsager matrix
    # Use diagonal dominance for physical validity
    L = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            coupling = 0.1 / (1 + abs(i - j))
            L[i, j] = coupling
            L[j, i] = coupling  # Onsager reciprocal relations
    # Dissipation function (always >= 0)
    phi = 0.5 * x @ L @ x
    return float(phi)


OPERATIONS["dissipation_function"] = {
    "fn": dissipation_function,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes Rayleigh dissipation function with Onsager reciprocal relations"
}


def chemical_potential_gradient(x):
    """Compute chemical potential gradients driving non-equilibrium transport.
    mu = mu_0 + RT * ln(c), grad(mu) = RT * (1/c) * grad(c).
    Input: array (concentrations). Output: array (chemical potential gradients)."""
    RT = 2.479  # kJ/mol at 298K
    c = np.maximum(np.abs(x), 1e-10)  # Avoid division by zero
    # Finite difference gradient of chemical potential
    mu = RT * np.log(c)
    grad_mu = np.zeros_like(mu)
    if len(mu) > 1:
        grad_mu[0] = mu[1] - mu[0]
        grad_mu[-1] = mu[-1] - mu[-2]
        for i in range(1, len(mu) - 1):
            grad_mu[i] = (mu[i + 1] - mu[i - 1]) / 2.0
    return grad_mu


OPERATIONS["chemical_potential_gradient"] = {
    "fn": chemical_potential_gradient,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes chemical potential gradients mu = RT*ln(c) driving transport"
}


def rayleigh_benard_critical(x):
    """Compute the critical Rayleigh number for the onset of Rayleigh-Benard convection.
    Ra_c = (pi^2 + k^2)^3 / k^2 where k is the horizontal wavenumber.
    The minimum Ra_c = 27*pi^4/4 ~ 657.51 occurs at k = pi/sqrt(2).
    Input: array (wavenumber values). Output: array (critical Rayleigh numbers)."""
    k = np.abs(x) + 0.01  # Avoid k=0
    Ra = (np.pi ** 2 + k ** 2) ** 3 / k ** 2
    return Ra


OPERATIONS["rayleigh_benard_critical"] = {
    "fn": rayleigh_benard_critical,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes critical Rayleigh number Ra_c = (pi^2+k^2)^3/k^2 for convection onset"
}


def belousov_zhabotinsky_period(x):
    """Estimate the oscillation period of the Belousov-Zhabotinsky reaction
    using the Oregonator model. The Oregonator is:
    dx/dt = s*(y - x*y + x - q*x^2), dy/dt = (-y - x*y + f*z)/s, dz/dt = w*(x - z).
    We compute the period via simple Euler integration.
    Input: array [s, q, f, w, ...]. Output: scalar (estimated period)."""
    s = np.abs(x[0]) + 0.1 if len(x) > 0 else 77.27
    q = np.abs(x[1]) * 1e-4 + 1e-5 if len(x) > 1 else 8.375e-6
    f = np.abs(x[2]) + 0.1 if len(x) > 2 else 1.0
    w = np.abs(x[3]) + 0.01 if len(x) > 3 else 0.161

    # Euler integration of Oregonator
    dt = 0.01
    max_time = 100.0
    steps = int(max_time / dt)

    xv, yv, zv = 1.0, 0.5, 0.5
    crossings = []

    for step in range(steps):
        dx = s * (yv - xv * yv + xv - q * xv ** 2)
        dy = (-yv - xv * yv + f * zv) / s
        dz = w * (xv - zv)
        xv_new = max(xv + dt * dx, 1e-10)
        yv_new = max(yv + dt * dy, 1e-10)
        zv_new = max(zv + dt * dz, 1e-10)

        # Detect zero-crossing of dx/dt (local maxima of x)
        dx_new = s * (yv_new - xv_new * yv_new + xv_new - q * xv_new ** 2)
        if dx > 0 and dx_new <= 0:
            crossings.append(step * dt)

        xv, yv, zv = xv_new, yv_new, zv_new

    if len(crossings) >= 2:
        periods = np.diff(crossings)
        return float(np.mean(periods[-min(5, len(periods)):]))
    return 0.0


OPERATIONS["belousov_zhabotinsky_period"] = {
    "fn": belousov_zhabotinsky_period,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates BZ reaction oscillation period via Oregonator model integration"
}


def minimum_entropy_production(x):
    """Compute the state satisfying Prigogine's minimum entropy production principle.
    Near equilibrium, the steady state minimizes sigma = sum L_ij * X_i * X_j
    subject to constraints. Input: array (initial thermodynamic forces).
    Output: array (forces at minimum entropy production)."""
    n = len(x)
    # Onsager matrix (symmetric, positive definite)
    L = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            coupling = 0.1 / (1 + abs(i - j))
            L[i, j] = coupling
            L[j, i] = coupling
    # Minimum entropy production with constraint: fix first force
    # The free forces adjust to minimize sigma
    # At minimum: L @ X = 0 for unconstrained components
    # With first component fixed, solve L[1:,1:] @ X[1:] = -L[1:,0] * x[0]
    if n <= 1:
        return x.copy()
    L_sub = L[1:, 1:]
    rhs = -L[1:, 0] * x[0]
    x_free = np.linalg.solve(L_sub, rhs)
    result = np.zeros(n)
    result[0] = x[0]
    result[1:] = x_free
    return result


OPERATIONS["minimum_entropy_production"] = {
    "fn": minimum_entropy_production,
    "input_type": "array",
    "output_type": "array",
    "description": "Finds forces minimizing entropy production (Prigogine's principle)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
