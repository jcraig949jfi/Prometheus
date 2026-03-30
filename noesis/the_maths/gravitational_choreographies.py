"""
Gravitational Choreographies — Special periodic N-body solutions (figure-eight etc.)

Connects to: [pseudo_riemannian, causal_set_theory, spin_foam]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "gravitational_choreographies"
OPERATIONS = {}


def figure_eight_orbit_points(x):
    """Generate points on the Chenciner-Montgomery figure-eight three-body orbit.
    Input: array where x[0]=number of points (clamped to [10,500]).
    Output: array of flattened [x, y] coordinates on the figure-eight.
    Uses the known Fourier approximation of the figure-eight solution."""
    n_pts = int(np.clip(x[0] if len(x) > 0 else 50, 10, 500))
    t = np.linspace(0, 2 * np.pi, n_pts, endpoint=False)
    # Fourier coefficients for figure-eight (Moore 1993, refined by Chenciner-Montgomery)
    # x(t) approx: sum of odd harmonics
    x_coords = (0.97000436 * np.cos(t) - 0.24308753 * np.cos(3 * t) +
                0.03100236 * np.cos(5 * t))
    y_coords = (0.24308753 * np.sin(t) + 0.97000436 * np.sin(3 * t) -
                0.03100236 * np.sin(5 * t))
    # Normalize to unit scale
    scale = max(np.max(np.abs(x_coords)), np.max(np.abs(y_coords)))
    if scale > 0:
        x_coords /= scale
        y_coords /= scale
    return np.concatenate([x_coords, y_coords])


OPERATIONS["figure_eight_orbit_points"] = {
    "fn": figure_eight_orbit_points,
    "input_type": "array",
    "output_type": "array",
    "description": "Points on the figure-eight three-body choreography"
}


def choreography_integrate_step(x):
    """One Verlet integration step for N-body gravitational choreography.
    Input: array [x1,y1,x2,y2,x3,y3, vx1,vy1,vx2,vy2,vx3,vy3] (3 bodies in 2D).
    Output: array of updated positions and velocities after dt=0.001.
    G*m = 1 for all bodies."""
    # Parse 3 bodies in 2D: 6 positions + 6 velocities = 12 values
    vals = np.zeros(12)
    vals[:min(len(x), 12)] = x[:min(len(x), 12)]
    pos = vals[:6].reshape(3, 2)
    vel = vals[6:12].reshape(3, 2)
    dt = 0.001
    Gm = 1.0

    def compute_accel(pos):
        acc = np.zeros_like(pos)
        for i in range(3):
            for j in range(3):
                if i != j:
                    r = pos[j] - pos[i]
                    dist = np.sqrt(np.sum(r ** 2) + 1e-10)  # softening
                    acc[i] += Gm * r / dist ** 3
        return acc

    # Velocity Verlet
    acc = compute_accel(pos)
    pos_new = pos + vel * dt + 0.5 * acc * dt ** 2
    acc_new = compute_accel(pos_new)
    vel_new = vel + 0.5 * (acc + acc_new) * dt

    return np.concatenate([pos_new.flatten(), vel_new.flatten()])


OPERATIONS["choreography_integrate_step"] = {
    "fn": choreography_integrate_step,
    "input_type": "array",
    "output_type": "array",
    "description": "One Verlet step of 3-body gravitational integration"
}


def floquet_multiplier(x):
    """Compute Floquet multipliers for stability of periodic orbit.
    Input: array of deviations from periodic orbit at successive periods.
    Output: array of estimated Floquet multipliers (eigenvalues of monodromy matrix).
    Uses ratio of successive deviations as approximation."""
    n = len(x)
    if n < 2:
        return np.array([1.0])
    # Build approximate monodromy from deviation ratios
    ratios = x[1:] / np.where(np.abs(x[:-1]) > 1e-15, x[:-1], 1e-15)
    # Floquet multipliers are eigenvalues of the monodromy matrix
    # Approximate: geometric mean of ratios gives dominant multiplier
    if n >= 4:
        dim = min(n // 2, 4)
        M = np.zeros((dim, dim))
        for i in range(dim):
            for j in range(dim):
                idx = i * dim + j
                if idx < len(ratios):
                    M[i, j] = ratios[idx]
        eigvals = np.linalg.eigvals(M)
        return np.abs(eigvals)
    else:
        return np.abs(ratios)


OPERATIONS["floquet_multiplier"] = {
    "fn": floquet_multiplier,
    "input_type": "array",
    "output_type": "array",
    "description": "Floquet multipliers for periodic orbit stability"
}


def phase_offset_verify(x):
    """Verify that bodies in a choreography have correct phase offsets (T/N apart).
    Input: array of N phase angles [phi_1, phi_2, ..., phi_N].
    Output: scalar (max deviation from ideal T/N spacing, 0=perfect)."""
    phases = np.sort(x % (2 * np.pi))
    n = len(phases)
    ideal_spacing = 2 * np.pi / n
    spacings = np.diff(phases)
    if len(spacings) > 0:
        spacings = np.append(spacings, 2 * np.pi - phases[-1] + phases[0])
    else:
        return np.float64(0.0)
    deviation = np.max(np.abs(spacings - ideal_spacing))
    return np.float64(deviation)


OPERATIONS["phase_offset_verify"] = {
    "fn": phase_offset_verify,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Max deviation from ideal T/N phase spacing in choreography"
}


def lagrange_equilateral_solution(x):
    """Lagrange equilateral triangle solution for 3 equal masses.
    Input: array where x[0]=orbital radius R, x[1]=angular velocity omega.
    Output: array of [x1,y1,x2,y2,x3,y3] positions.
    Bodies at vertices of equilateral triangle, rotating uniformly."""
    R = abs(x[0]) if len(x) > 0 else 1.0
    omega = x[1] if len(x) > 1 else 1.0
    t = x[2] if len(x) > 2 else 0.0
    positions = np.zeros(6)
    for i in range(3):
        angle = omega * t + 2 * np.pi * i / 3.0
        positions[2 * i] = R * np.cos(angle)
        positions[2 * i + 1] = R * np.sin(angle)
    return positions


OPERATIONS["lagrange_equilateral_solution"] = {
    "fn": lagrange_equilateral_solution,
    "input_type": "array",
    "output_type": "array",
    "description": "Lagrange equilateral triangle positions for 3 equal masses"
}


def euler_collinear_solution(x):
    """Euler collinear solution: 3 bodies on a rotating line.
    Input: array where x[0]=separation d, x[1]=angular velocity, x[2]=time.
    Output: array [x1,y1,x2,y2,x3,y3]."""
    d = abs(x[0]) if len(x) > 0 else 1.0
    omega = x[1] if len(x) > 1 else 1.0
    t = x[2] if len(x) > 2 else 0.0
    angle = omega * t
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    # Bodies at -d, 0, +d on rotating line
    positions = np.zeros(6)
    for i, r in enumerate([-d, 0.0, d]):
        positions[2 * i] = r * cos_a
        positions[2 * i + 1] = r * sin_a
    return positions


OPERATIONS["euler_collinear_solution"] = {
    "fn": euler_collinear_solution,
    "input_type": "array",
    "output_type": "array",
    "description": "Euler collinear solution for 3 bodies on a rotating line"
}


def choreography_period(x):
    """Estimate period of a choreography from position time series.
    Input: array of x-coordinates sampled uniformly in time.
    Output: scalar estimated period (in sample units) via autocorrelation."""
    n = len(x)
    if n < 4:
        return np.float64(float(n))
    # Autocorrelation
    x_centered = x - np.mean(x)
    corr = np.correlate(x_centered, x_centered, mode='full')
    corr = corr[n - 1:]  # positive lags only
    corr /= corr[0] if corr[0] > 1e-15 else 1.0
    # Find first peak after initial decay
    for i in range(1, len(corr) - 1):
        if corr[i] > corr[i - 1] and corr[i] > corr[i + 1] and corr[i] > 0.5:
            return np.float64(float(i))
    return np.float64(float(n))


OPERATIONS["choreography_period"] = {
    "fn": choreography_period,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimate choreography period from autocorrelation of position data"
}


def choreography_energy(x):
    """Compute total energy (kinetic + potential) for 3-body system.
    Input: array [x1,y1,x2,y2,x3,y3, vx1,vy1,vx2,vy2,vx3,vy3].
    Output: scalar total energy. G*m=1."""
    vals = np.zeros(12)
    vals[:min(len(x), 12)] = x[:min(len(x), 12)]
    pos = vals[:6].reshape(3, 2)
    vel = vals[6:12].reshape(3, 2)
    # Kinetic energy (m=1)
    KE = 0.5 * np.sum(vel ** 2)
    # Potential energy
    PE = 0.0
    for i in range(3):
        for j in range(i + 1, 3):
            r = np.sqrt(np.sum((pos[i] - pos[j]) ** 2) + 1e-10)
            PE -= 1.0 / r
    return np.float64(KE + PE)


OPERATIONS["choreography_energy"] = {
    "fn": choreography_energy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Total energy of 3-body system (KE + PE)"
}


def stability_classify(x):
    """Classify stability from Floquet multipliers: stable, unstable, marginal.
    Input: array of Floquet multiplier magnitudes. Output: scalar code.
    0=stable (all |mu|<=1), 1=marginal (|mu|~1), 2=unstable (some |mu|>1)."""
    mags = np.abs(x)
    max_mag = np.max(mags)
    if max_mag > 1.01:
        return np.float64(2.0)  # unstable
    elif max_mag > 0.99:
        return np.float64(1.0)  # marginal
    else:
        return np.float64(0.0)  # stable


OPERATIONS["stability_classify"] = {
    "fn": stability_classify,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Classify orbit stability: 0=stable, 1=marginal, 2=unstable"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
