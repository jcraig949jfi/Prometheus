"""
Gravitational Lensing — Thin-lens gravitational optics

Connects to: [kerr_geodesics, friedmann_equations, penrose_diagrams]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "gravitational_lensing"
OPERATIONS = {}


def lens_equation_solve(beta, theta_E):
    """Solve the thin-lens equation: beta = theta - theta_E^2/theta.
    For a point lens, returns the two image positions.
    Input: beta array (source positions), theta_E scalar (Einstein radius).
    Output: (n,2) array of image positions."""
    beta = np.asarray(beta, dtype=float)
    theta_E = float(np.mean(theta_E)) if hasattr(theta_E, '__len__') else float(theta_E)
    # Two solutions: theta_+/- = (beta +/- sqrt(beta^2 + 4*theta_E^2)) / 2
    disc = np.sqrt(beta**2 + 4.0 * theta_E**2)
    theta_p = (beta + disc) / 2.0
    theta_m = (beta - disc) / 2.0
    return np.column_stack([theta_p, theta_m])

OPERATIONS["lens_equation_solve"] = {
    "fn": lambda x: lens_equation_solve(x, 1.0),
    "input_type": "array",
    "output_type": "matrix",
    "description": "Solve point-mass lens equation for image positions"
}


def einstein_radius(M, D_L, D_S):
    """Einstein radius theta_E = sqrt(4GM/(c^2) * D_LS/(D_L*D_S)).
    In geometric units (G=c=1): theta_E = sqrt(4M * (D_S-D_L)/(D_L*D_S)).
    Input: M array, D_L, D_S scalars. Output: theta_E array."""
    M = np.asarray(M, dtype=float)
    D_LS = D_S - D_L
    theta_E = np.sqrt(4.0 * M * D_LS / (D_L * D_S))
    return theta_E

OPERATIONS["einstein_radius"] = {
    "fn": lambda x: einstein_radius(x, 1.0, 2.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Einstein radius for point lens"
}


def magnification_factor(beta, theta_E):
    """Total magnification for a point lens: mu = u^2+2 / (u*sqrt(u^2+4)) where u=beta/theta_E.
    Input: beta array, theta_E scalar. Output: magnification array."""
    beta = np.asarray(beta, dtype=float)
    u = np.abs(beta) / theta_E
    u = np.clip(u, 1e-10, None)
    mu = (u**2 + 2.0) / (u * np.sqrt(u**2 + 4.0))
    return mu

OPERATIONS["magnification_factor"] = {
    "fn": lambda x: magnification_factor(x, 1.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Total magnification factor for point gravitational lens"
}


def critical_curve_radius(M, D_L, D_S):
    """Critical curve radius equals the Einstein radius for a point lens.
    For an SIS lens: theta_cr = 4*pi*sigma_v^2 * D_LS/D_S.
    Here we use point mass. Input: M array. Output: radius array."""
    return einstein_radius(M, D_L, D_S)

OPERATIONS["critical_curve_radius"] = {
    "fn": lambda x: critical_curve_radius(x, 1.0, 2.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Critical curve radius (= Einstein radius for point lens)"
}


def caustic_structure(kappa, gamma):
    """Caustic eigenvalues for a convergence kappa and shear gamma lens.
    The Jacobian eigenvalues are (1-kappa-gamma) and (1-kappa+gamma).
    Caustics occur where an eigenvalue = 0.
    Input: kappa array, gamma scalar. Output: (n,2) eigenvalue array."""
    kappa = np.asarray(kappa, dtype=float)
    lam1 = 1.0 - kappa - gamma
    lam2 = 1.0 - kappa + gamma
    return np.column_stack([lam1, lam2])

OPERATIONS["caustic_structure"] = {
    "fn": lambda x: caustic_structure(x, 0.3),
    "input_type": "array",
    "output_type": "matrix",
    "description": "Jacobian eigenvalues for convergence-shear lens mapping"
}


def time_delay(theta, beta, theta_E, D_dt):
    """Gravitational time delay: Delta_t = D_dt/2 * [(theta-beta)^2 - psi(theta)]
    where psi = theta_E^2 * ln|theta| for point lens.
    Input: theta array, beta/theta_E/D_dt scalars. Output: delay array."""
    theta = np.asarray(theta, dtype=float)
    geometric = 0.5 * (theta - beta)**2
    potential = theta_E**2 * np.log(np.clip(np.abs(theta), 1e-15, None))
    delay = D_dt * (geometric - potential)
    return delay

OPERATIONS["time_delay"] = {
    "fn": lambda x: time_delay(x, 0.5, 1.0, 1.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Gravitational time delay for point lens"
}


def deflection_angle(M, b):
    """Deflection angle alpha = 4GM/(c^2 * b) for a point mass.
    Geometric units: alpha = 4M/b.
    Input: b (impact parameter) array. Output: alpha array."""
    b = np.asarray(b, dtype=float)
    M_val = float(np.mean(M)) if hasattr(M, '__len__') else float(M)
    alpha = 4.0 * M_val / np.clip(np.abs(b), 1e-15, None)
    return alpha

OPERATIONS["deflection_angle"] = {
    "fn": lambda x: deflection_angle(1.0, x),
    "input_type": "array",
    "output_type": "array",
    "description": "Gravitational deflection angle for point mass"
}


def shear_from_convergence(kappa_2d):
    """Compute shear gamma from convergence kappa via Kaiser-Squires relation.
    In Fourier space: gamma_hat = D_hat * kappa_hat where D = (k1^2-k2^2+2ik1k2)/|k|^2.
    For 1D input, approximate as finite differences of convergence.
    Input: kappa array (1D profile). Output: shear array."""
    kappa = np.asarray(kappa_2d, dtype=float)
    # Simple finite-difference approximation of the shear for a 1D convergence profile
    # gamma ~ d^2 psi / dx^2 - kappa where psi'' = 2*kappa for the 1D case
    # So gamma = kappa for a 1D sheet (tangential shear)
    # More realistically, use a running second derivative
    gamma = np.gradient(np.gradient(kappa))
    return gamma

OPERATIONS["shear_from_convergence"] = {
    "fn": shear_from_convergence,
    "input_type": "array",
    "output_type": "array",
    "description": "Approximate shear from convergence profile"
}


def multiple_image_count(beta, theta_E):
    """Number of images for a point lens: always 2 (for beta != 0), or Einstein ring (beta=0).
    For SIS lens: 2 if beta < theta_E, 1 otherwise.
    Here: SIS model. Input: beta array, theta_E scalar. Output: count array."""
    beta = np.asarray(beta, dtype=float)
    counts = np.where(np.abs(beta) < theta_E, 2, 1)
    return counts.astype(float)

OPERATIONS["multiple_image_count"] = {
    "fn": lambda x: multiple_image_count(x, 3.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Number of images for SIS lens"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
