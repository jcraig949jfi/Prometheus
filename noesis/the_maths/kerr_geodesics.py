"""
Kerr Geodesics — Orbits around rotating black holes (Kerr metric)

Connects to: [gravitational_lensing, penrose_diagrams, friedmann_equations]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "kerr_geodesics"
OPERATIONS = {}


def isco_radius(a):
    """Innermost stable circular orbit radius vs spin parameter a (in units of M=1).
    Input: array of spin parameters |a|<=1. Output: array of r_isco/M."""
    a = np.asarray(a, dtype=float)
    # Bardeen, Press, Teukolsky (1972) formula for prograde ISCO
    z1 = 1.0 + (1.0 - a**2)**(1.0/3.0) * ((1.0 + a)**(1.0/3.0) + (1.0 - a)**(1.0/3.0))
    z2 = np.sqrt(3.0 * a**2 + z1**2)
    r_isco = 3.0 + z2 - np.sign(a) * np.sqrt((3.0 - z1) * (3.0 + z1 + 2.0 * z2))
    return r_isco

OPERATIONS["isco_radius"] = {
    "fn": isco_radius,
    "input_type": "array",
    "output_type": "array",
    "description": "ISCO radius for Kerr BH as function of spin parameter a (M=1)"
}


def photon_sphere_radius(a):
    """Photon sphere radius for prograde orbits in Kerr spacetime (M=1).
    Input: array of spin params. Output: array of r_ph/M."""
    a = np.asarray(a, dtype=float)
    # r_ph = 2M(1 + cos(2/3 * arccos(-|a|))) for prograde, simplified
    r_ph = 2.0 * (1.0 + np.cos(2.0/3.0 * np.arccos(-np.clip(a, -1, 1))))
    return r_ph

OPERATIONS["photon_sphere_radius"] = {
    "fn": photon_sphere_radius,
    "input_type": "array",
    "output_type": "array",
    "description": "Photon sphere radius for prograde orbits in Kerr metric"
}


def frame_dragging_omega(r, a):
    """Frame-dragging angular velocity omega = 2Mar / Sigma*Delta + ... (Boyer-Lindquist).
    For equatorial plane theta=pi/2. Input: r array, a scalar. Output: omega array."""
    r = np.asarray(r, dtype=float)
    # omega = 2*a*r / (r^2 + a^2)^2 - a^2*Delta  but simplified on equatorial:
    # omega = 2*a / (r^3 + a^2*r + 2*a^2)  [equatorial, M=1]
    sigma = r**2 + a**2  # theta=pi/2 so cos(theta)=0
    A = (r**2 + a**2)**2 - a**2 * (r**2 - 2.0*r + a**2)
    omega = 2.0 * a * r / A
    return omega

OPERATIONS["frame_dragging_omega"] = {
    "fn": lambda x: frame_dragging_omega(x, 0.5),
    "input_type": "array",
    "output_type": "array",
    "description": "Frame-dragging angular velocity at equator for a=0.5"
}


def carter_constant(r, a, E, L):
    """Carter constant Q for equatorial circular orbits. Q=0 for equatorial.
    For slightly inclined orbits: Q ~ (L - aE)^2 * correction.
    Input: arrays r, scalar a,E,L. Output: array."""
    r = np.asarray(r, dtype=float)
    # For equatorial orbits Q=0; compute the effective potential term
    # Q = -(L - a*E)^2 for confined equatorial motion is 0
    # For general motion: Q = p_theta^2 + cos^2(theta)(a^2(1-E^2)+L^2/sin^2(theta))
    # We return the quantity (L - a*E)^2 as the "Carter-like" constant
    Q = (L - a * E)**2 * np.ones_like(r)
    return Q

OPERATIONS["carter_constant"] = {
    "fn": lambda x: carter_constant(x, 0.5, 0.9, 3.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Carter constant for given orbital parameters"
}


def ergosphere_radius(theta, a):
    """Ergosphere outer boundary r_ergo = M + sqrt(M^2 - a^2 cos^2 theta), M=1.
    Input: theta array, a scalar. Output: r array."""
    theta = np.asarray(theta, dtype=float)
    r_ergo = 1.0 + np.sqrt(1.0 - a**2 * np.cos(theta)**2)
    return r_ergo

OPERATIONS["ergosphere_radius"] = {
    "fn": lambda x: ergosphere_radius(x, 0.5),
    "input_type": "array",
    "output_type": "array",
    "description": "Ergosphere radius as function of polar angle theta"
}


def schwarzschild_radius(M):
    """Schwarzschild radius r_s = 2GM/c^2. In geometric units (G=c=1): r_s=2M.
    Input: mass array. Output: radius array."""
    M = np.asarray(M, dtype=float)
    return 2.0 * M

OPERATIONS["schwarzschild_radius"] = {
    "fn": schwarzschild_radius,
    "input_type": "array",
    "output_type": "array",
    "description": "Schwarzschild radius r_s = 2M (geometric units)"
}


def gravitational_redshift(r, a):
    """Gravitational redshift factor sqrt(-g_tt) for static observer on equator.
    z = 1/sqrt(1 - 2M/r) for Schwarzschild; Kerr: sqrt(1 - 2r/(r^2+a^2 cos^2 theta)).
    Equatorial: sqrt(1 - 2/r). Input: r array, a scalar. Output: array."""
    r = np.asarray(r, dtype=float)
    # g_tt for Kerr equatorial: -(1 - 2/r), so redshift factor = 1/sqrt(1 - 2/r) - 1
    # Return 1+z = 1/sqrt(1 - 2/r)
    val = 1.0 / np.sqrt(np.clip(1.0 - 2.0 / r, 1e-15, None))
    return val

OPERATIONS["gravitational_redshift"] = {
    "fn": lambda x: gravitational_redshift(x, 0.5),
    "input_type": "array",
    "output_type": "array",
    "description": "Gravitational redshift factor 1+z at equator"
}


def kerr_angular_momentum(r, a):
    """Specific angular momentum L for circular equatorial prograde orbit in Kerr.
    L = M^{1/2}(r^2 - 2a*M^{1/2}*r^{1/2} + a^2) / (r^{3/4}*sqrt(r^{3/2}-3M*r^{1/2}+2a*M^{1/2}))
    M=1. Input: r array, a scalar. Output: array."""
    r = np.asarray(r, dtype=float)
    sr = np.sqrt(r)
    num = r**2 - 2.0 * a * sr + a**2
    den = sr * np.sqrt(np.clip(r**1.5 - 3.0 * sr + 2.0 * a, 1e-15, None))
    L = num / den
    return L

OPERATIONS["kerr_angular_momentum"] = {
    "fn": lambda x: kerr_angular_momentum(x, 0.5),
    "input_type": "array",
    "output_type": "array",
    "description": "Specific angular momentum for circular equatorial Kerr orbit"
}


def orbital_energy_circular(r, a):
    """Specific energy E for circular equatorial prograde orbit in Kerr.
    E = (r^{3/2} - 2r^{1/2} + a) / (r^{3/4} sqrt(r^{3/2} - 3r^{1/2} + 2a))
    M=1. Input: r array, a scalar. Output: array."""
    r = np.asarray(r, dtype=float)
    sr = np.sqrt(r)
    num = r**1.5 - 2.0 * sr + a
    den = r**0.75 * np.sqrt(np.clip(r**1.5 - 3.0 * sr + 2.0 * a, 1e-15, None))
    E = num / den
    return E

OPERATIONS["orbital_energy_circular"] = {
    "fn": lambda x: orbital_energy_circular(x, 0.5),
    "input_type": "array",
    "output_type": "array",
    "description": "Specific energy for circular equatorial Kerr orbit"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
