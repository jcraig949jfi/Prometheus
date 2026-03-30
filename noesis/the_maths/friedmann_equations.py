"""
Friedmann Equations — Cosmic expansion dynamics

Connects to: [gravitational_lensing, stellar_structure, cosmic_topology]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "friedmann_equations"
OPERATIONS = {}

# Default cosmological parameters (Planck 2018-like)
_H0 = 70.0       # km/s/Mpc
_Omega_m = 0.3    # matter density
_Omega_r = 9e-5   # radiation density
_Omega_L = 0.7    # dark energy density
_c = 299792.458   # km/s
_DH = _c / _H0   # Hubble distance in Mpc


def hubble_parameter(z):
    """Hubble parameter H(z) = H0 * E(z) where E(z) = sqrt(Omega_r(1+z)^4 + Omega_m(1+z)^3 + Omega_L).
    Input: redshift array. Output: H(z) in km/s/Mpc."""
    z = np.asarray(z, dtype=float)
    E_z = np.sqrt(_Omega_r * (1+z)**4 + _Omega_m * (1+z)**3 + _Omega_L)
    return _H0 * E_z

OPERATIONS["hubble_parameter"] = {
    "fn": hubble_parameter,
    "input_type": "array",
    "output_type": "array",
    "description": "Hubble parameter H(z) for flat Lambda-CDM cosmology"
}


def scale_factor_evolve(t_arr):
    """Evolve scale factor a(t) via simple Euler integration of da/dt = a*H(a).
    Input: dimensionless time array (in units of 1/H0). Output: a(t) array."""
    t_arr = np.asarray(t_arr, dtype=float)
    n = len(t_arr)
    a = np.zeros(n)
    a[0] = 0.01  # start from small a
    for i in range(1, n):
        dt = t_arr[i] - t_arr[i-1]
        z_i = 1.0/a[i-1] - 1.0
        H_i = hubble_parameter(max(z_i, 0.0)) / _H0  # dimensionless
        a[i] = a[i-1] + a[i-1] * H_i * dt
        a[i] = min(a[i], 10.0)  # cap
    return a

OPERATIONS["scale_factor_evolve"] = {
    "fn": scale_factor_evolve,
    "input_type": "array",
    "output_type": "array",
    "description": "Evolve scale factor a(t) via Euler integration"
}


def lookback_time(z):
    """Lookback time t_L(z) = integral_0^z dz'/((1+z')*H(z')) via trapezoidal rule.
    Input: redshift array. Output: lookback time in Gyr."""
    z = np.asarray(z, dtype=float)
    results = np.zeros_like(z)
    for i, zi in enumerate(z.flat):
        if zi <= 0:
            results.flat[i] = 0.0
            continue
        zz = np.linspace(0, zi, 500)
        integrand = 1.0 / ((1+zz) * hubble_parameter(zz))
        # Convert: integral in (km/s/Mpc)^{-1} to Gyr
        # 1 Mpc = 3.0857e19 km, 1 Gyr = 3.1557e16 s
        results.flat[i] = np.trapezoid(integrand, zz) * 3.0857e19 / 3.1557e16
    return results

OPERATIONS["lookback_time"] = {
    "fn": lookback_time,
    "input_type": "array",
    "output_type": "array",
    "description": "Lookback time in Gyr for given redshift"
}


def comoving_distance(z):
    """Comoving distance d_C(z) = c * integral_0^z dz'/H(z') in Mpc.
    Input: redshift array. Output: distance in Mpc."""
    z = np.asarray(z, dtype=float)
    results = np.zeros_like(z)
    for i, zi in enumerate(z.flat):
        if zi <= 0:
            results.flat[i] = 0.0
            continue
        zz = np.linspace(0, zi, 500)
        integrand = 1.0 / hubble_parameter(zz)
        results.flat[i] = _c * np.trapezoid(integrand, zz)
    return results

OPERATIONS["comoving_distance"] = {
    "fn": comoving_distance,
    "input_type": "array",
    "output_type": "array",
    "description": "Comoving distance in Mpc"
}


def luminosity_distance(z):
    """Luminosity distance d_L = (1+z) * d_C(z) in Mpc.
    Input: redshift array. Output: distance in Mpc."""
    z = np.asarray(z, dtype=float)
    d_C = comoving_distance(z)
    return (1.0 + z) * d_C

OPERATIONS["luminosity_distance"] = {
    "fn": luminosity_distance,
    "input_type": "array",
    "output_type": "array",
    "description": "Luminosity distance in Mpc"
}


def angular_diameter_distance(z):
    """Angular diameter distance d_A = d_C(z)/(1+z) in Mpc.
    Input: redshift array. Output: distance in Mpc."""
    z = np.asarray(z, dtype=float)
    d_C = comoving_distance(z)
    return d_C / (1.0 + z)

OPERATIONS["angular_diameter_distance"] = {
    "fn": angular_diameter_distance,
    "input_type": "array",
    "output_type": "array",
    "description": "Angular diameter distance in Mpc"
}


def deceleration_parameter(z):
    """Deceleration parameter q(z) = -1 + (1+z)/E(z) * dE/dz.
    For flat LCDM: q = (Omega_m/2*(1+z)^3 + Omega_r*(1+z)^4 - Omega_L) / E(z)^2.
    Input: redshift array. Output: q(z) array."""
    z = np.asarray(z, dtype=float)
    E2 = _Omega_r*(1+z)**4 + _Omega_m*(1+z)**3 + _Omega_L
    q = (0.5*_Omega_m*(1+z)**3 + _Omega_r*(1+z)**4 - _Omega_L) / E2
    return q

OPERATIONS["deceleration_parameter"] = {
    "fn": deceleration_parameter,
    "input_type": "array",
    "output_type": "array",
    "description": "Deceleration parameter q(z)"
}


def age_of_universe(z):
    """Age of universe at redshift z = integral_z^inf dz'/((1+z')*H(z')).
    Input: redshift array. Output: age in Gyr."""
    z = np.asarray(z, dtype=float)
    results = np.zeros_like(z)
    z_max = 1000.0  # use z=1000 as proxy for infinity
    for i, zi in enumerate(z.flat):
        zz = np.linspace(zi, z_max, 1000)
        integrand = 1.0 / ((1+zz) * hubble_parameter(zz))
        results.flat[i] = np.trapezoid(integrand, zz) * 3.0857e19 / 3.1557e16
    return results

OPERATIONS["age_of_universe"] = {
    "fn": age_of_universe,
    "input_type": "array",
    "output_type": "array",
    "description": "Age of universe at redshift z in Gyr"
}


def density_parameter_evolution(z):
    """Omega_m(z) = Omega_m0 * (1+z)^3 / E(z)^2 and Omega_L(z) = Omega_L0 / E(z)^2.
    Input: redshift array. Output: (n,3) array [Omega_m(z), Omega_r(z), Omega_L(z)]."""
    z = np.asarray(z, dtype=float)
    E2 = _Omega_r*(1+z)**4 + _Omega_m*(1+z)**3 + _Omega_L
    Om = _Omega_m * (1+z)**3 / E2
    Or = _Omega_r * (1+z)**4 / E2
    OL = _Omega_L / E2
    return np.column_stack([Om, Or, OL])

OPERATIONS["density_parameter_evolution"] = {
    "fn": density_parameter_evolution,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Evolution of density parameters Omega_m, Omega_r, Omega_Lambda with redshift"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
