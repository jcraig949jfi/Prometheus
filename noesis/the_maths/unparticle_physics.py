"""
Unparticle Physics — Continuous mass dimension, fractional-dimensional phase space

Connects to: [fractional_qm, rg_flow_qft, spin_foam]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from scipy.special import gamma as gammafn

FIELD_NAME = "unparticle_physics"
OPERATIONS = {}


def unparticle_propagator(x):
    """Unparticle propagator: Delta(p^2) ~ A_d * (-p^2 - i*eps)^{d_U - 2}.
    Input: array of p^2 values. x[0] = scaling dimension d_U (default ~1.5).
    Output: array of propagator magnitudes."""
    d_U = x[0] if len(x) > 0 else 1.5
    if d_U < 1.0:
        d_U = 1.5
    p2_vals = x[1:] if len(x) > 1 else np.array([1.0, 2.0, 3.0])
    if len(p2_vals) == 0:
        p2_vals = np.array([1.0])
    # Normalization factor
    A_d = (16.0 * np.pi ** 2.5) / ((2.0 * np.pi) ** (2 * d_U)) * \
          gammafn(d_U + 0.5) / (gammafn(d_U - 1.0) * gammafn(2.0 * d_U))
    # Propagator magnitude
    prop = np.abs(A_d) * np.abs(p2_vals) ** (d_U - 2.0)
    return prop


OPERATIONS["unparticle_propagator"] = {
    "fn": unparticle_propagator,
    "input_type": "array",
    "output_type": "array",
    "description": "Unparticle propagator magnitude for given p^2 and scaling dimension"
}


def fractional_phase_space(x):
    """Phase space volume for d_U-dimensional unparticle.
    Input: array where x[0]=d_U, x[1]=energy E. Output: scalar.
    dPS ~ E^{2*d_U - 2} * A_d."""
    d_U = x[0] if len(x) > 0 else 1.5
    E = abs(x[1]) if len(x) > 1 else 1.0
    if d_U < 1.0:
        d_U = 1.5
    A_d = (16.0 * np.pi ** 2.5) / ((2.0 * np.pi) ** (2 * d_U)) * \
          gammafn(d_U + 0.5) / (gammafn(d_U - 1.0) * gammafn(2.0 * d_U))
    ps = abs(A_d) * E ** (2.0 * d_U - 2.0)
    return np.float64(ps)


OPERATIONS["fractional_phase_space"] = {
    "fn": fractional_phase_space,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Phase space volume for fractional-dimensional unparticle"
}


def unparticle_spectral_function(x):
    """Spectral function rho(M^2) for unparticle: rho ~ theta(M^2) * (M^2)^{d_U - 2}.
    Input: array where x[0]=d_U, rest=M^2 values. Output: array of spectral weights."""
    d_U = x[0] if len(x) > 0 else 1.5
    if d_U < 1.0:
        d_U = 1.5
    M2 = x[1:] if len(x) > 1 else np.array([1.0, 2.0])
    if len(M2) == 0:
        M2 = np.array([1.0])
    # theta(M^2) * (M^2)^{d_U - 2} / Gamma(d_U)
    rho = np.where(M2 > 0, M2 ** (d_U - 2.0) / gammafn(d_U), 0.0)
    return rho


OPERATIONS["unparticle_spectral_function"] = {
    "fn": unparticle_spectral_function,
    "input_type": "array",
    "output_type": "array",
    "description": "Unparticle spectral function rho(M^2)"
}


def scaling_dimension_effect(x):
    """Show how observable cross-section scales with energy for different d_U.
    Input: array where x[0]=d_U, x[1]=energy ratio E/Lambda. Output: scalar scaling factor.
    sigma ~ (E/Lambda)^{2*d_U - 2}."""
    d_U = x[0] if len(x) > 0 else 1.5
    ratio = abs(x[1]) if len(x) > 1 else 1.0
    if d_U < 1.0:
        d_U = 1.5
    if ratio < 1e-15:
        return np.float64(0.0)
    scaling = ratio ** (2.0 * d_U - 2.0)
    return np.float64(scaling)


OPERATIONS["scaling_dimension_effect"] = {
    "fn": scaling_dimension_effect,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Energy scaling factor (E/Lambda)^{2*d_U - 2}"
}


def interference_amplitude(x):
    """Interference between unparticle and SM amplitude.
    Input: array where x[0]=d_U, x[1]=SM amplitude, x[2]=unparticle coupling.
    Output: scalar |A_SM + A_U|^2."""
    d_U = x[0] if len(x) > 0 else 1.5
    A_SM = x[1] if len(x) > 1 else 1.0
    g_U = x[2] if len(x) > 2 else 0.1
    if d_U < 1.0:
        d_U = 1.5
    # Unparticle amplitude has a phase from fractional power
    phase = np.pi * (d_U - 1.0)  # from (-1)^{d_U - 2}
    A_U = g_U * np.exp(1j * phase)
    total = A_SM + A_U
    return np.float64(np.abs(total) ** 2)


OPERATIONS["interference_amplitude"] = {
    "fn": interference_amplitude,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Interference |A_SM + A_unparticle|^2 with fractional phase"
}


def fractional_dimensional_integral(x):
    """Integrate r^{d-1} * f(r) in d fractional dimensions using Gamma function.
    Input: array where x[0]=d (fractional dimension), rest=function samples on [0,1].
    Output: scalar (integral * S_d / S_1) where S_d = 2*pi^{d/2}/Gamma(d/2)."""
    d = x[0] if len(x) > 0 else 2.5
    if d < 0.1:
        d = 2.5
    f_vals = x[1:] if len(x) > 1 else np.ones(5)
    if len(f_vals) == 0:
        f_vals = np.ones(5)
    n = len(f_vals)
    r = np.linspace(1e-10, 1.0, n)
    dr = r[1] - r[0]
    # d-dimensional radial integral: int r^{d-1} f(r) dr
    integrand = r ** (d - 1.0) * f_vals
    result = np.sum((integrand[:-1] + integrand[1:]) / 2.0 * np.diff(r))
    # Multiply by solid angle S_d
    S_d = 2.0 * np.pi ** (d / 2.0) / gammafn(d / 2.0)
    return np.float64(result * S_d)


OPERATIONS["fractional_dimensional_integral"] = {
    "fn": fractional_dimensional_integral,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Radial integral in fractional d dimensions with solid angle factor"
}


def unparticle_cross_section(x):
    """Unparticle contribution to cross-section: sigma_U ~ (s/Lambda^2)^{d_U - 1} / s.
    Input: array where x[0]=d_U, x[1]=sqrt(s) [GeV], x[2]=Lambda [GeV].
    Output: scalar cross-section in arbitrary units."""
    d_U = x[0] if len(x) > 0 else 1.5
    sqrts = abs(x[1]) if len(x) > 1 else 100.0
    Lambda = abs(x[2]) if len(x) > 2 else 1000.0
    if d_U < 1.0:
        d_U = 1.5
    if Lambda < 1e-10:
        Lambda = 1000.0
    s = sqrts ** 2
    sigma = (s / Lambda ** 2) ** (d_U - 1.0) / s
    return np.float64(sigma)


OPERATIONS["unparticle_cross_section"] = {
    "fn": unparticle_cross_section,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Unparticle cross-section ~ (s/Lambda^2)^{d_U-1}/s"
}


def continuous_mass_spectrum(x):
    """Generate continuous mass spectrum for unparticle.
    Input: array where x[0]=d_U, rest=mass values. Output: array of spectral weights.
    Spectrum is continuous above threshold: w(m) ~ m^{2*d_U - 3} for m > 0."""
    d_U = x[0] if len(x) > 0 else 1.5
    if d_U < 1.0:
        d_U = 1.5
    masses = x[1:] if len(x) > 1 else np.linspace(0.1, 5, 5)
    if len(masses) == 0:
        masses = np.linspace(0.1, 5, 5)
    # Continuous mass spectrum weight
    weights = np.where(masses > 0, masses ** (2.0 * d_U - 3.0), 0.0)
    # Normalize
    total = np.sum(weights)
    if total > 1e-15:
        weights = weights / total
    return weights


OPERATIONS["continuous_mass_spectrum"] = {
    "fn": continuous_mass_spectrum,
    "input_type": "array",
    "output_type": "array",
    "description": "Normalized continuous mass spectrum for unparticle"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
