"""
RG Flow QFT — Beta functions and renormalization group flow in QFT coupling space

Connects to: [unparticle_physics, fractional_qm, spin_foam, noncommutative_geometry_connes]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "rg_flow_qft"
OPERATIONS = {}


def one_loop_beta_function(x):
    """Generic one-loop beta function: beta(g) = -b0 * g^3 / (16*pi^2).
    Input: array where x[0]=coupling g, x[1]=b0 coefficient.
    Output: scalar beta(g)."""
    g = x[0] if len(x) > 0 else 0.1
    b0 = x[1] if len(x) > 1 else 1.0
    beta = -b0 * g ** 3 / (16.0 * np.pi ** 2)
    return np.float64(beta)


OPERATIONS["one_loop_beta_function"] = {
    "fn": one_loop_beta_function,
    "input_type": "array",
    "output_type": "scalar",
    "description": "One-loop beta function beta(g) = -b0 * g^3 / (16*pi^2)"
}


def beta_function_qed(x):
    """QED beta function at one loop: beta(e) = e^3 / (12*pi^2) * N_f.
    Input: array where x[0]=coupling e, x[1]=N_f (number of fermion flavors).
    Output: scalar beta(e). QED is NOT asymptotically free (beta > 0)."""
    e = x[0] if len(x) > 0 else 0.3
    Nf = x[1] if len(x) > 1 else 1.0
    beta = e ** 3 * Nf / (12.0 * np.pi ** 2)
    return np.float64(beta)


OPERATIONS["beta_function_qed"] = {
    "fn": beta_function_qed,
    "input_type": "array",
    "output_type": "scalar",
    "description": "QED one-loop beta function: e^3 * N_f / (12*pi^2)"
}


def beta_function_qcd(x):
    """QCD beta function at one loop: beta(g) = -g^3/(16*pi^2) * (11*N_c/3 - 2*N_f/3).
    Input: array where x[0]=coupling g, x[1]=N_c (colors), x[2]=N_f (flavors).
    Output: scalar beta(g). Asymptotically free when 11*N_c > 2*N_f."""
    g = x[0] if len(x) > 0 else 0.3
    Nc = x[1] if len(x) > 1 else 3.0
    Nf = x[2] if len(x) > 2 else 6.0
    b0 = 11.0 * Nc / 3.0 - 2.0 * Nf / 3.0
    beta = -g ** 3 * b0 / (16.0 * np.pi ** 2)
    return np.float64(beta)


OPERATIONS["beta_function_qcd"] = {
    "fn": beta_function_qcd,
    "input_type": "array",
    "output_type": "scalar",
    "description": "QCD one-loop beta function with N_c colors and N_f flavors"
}


def fixed_point_find(x):
    """Find fixed points of a polynomial beta function beta(g) = sum a_i g^i.
    Input: array of polynomial coefficients [a0, a1, a2, ...].
    Output: array of real fixed-point coupling values (roots of beta(g)=0)."""
    coeffs = x
    if len(coeffs) < 2:
        return np.array([0.0])
    # Find roots of the polynomial
    roots = np.roots(coeffs[::-1])  # np.roots takes highest power first
    # Keep only real roots
    real_roots = roots[np.abs(roots.imag) < 1e-8].real
    if len(real_roots) == 0:
        return np.array([0.0])
    return np.sort(real_roots)


OPERATIONS["fixed_point_find"] = {
    "fn": fixed_point_find,
    "input_type": "array",
    "output_type": "array",
    "description": "Find fixed points (zeros) of polynomial beta function"
}


def anomalous_dimension(x):
    """One-loop anomalous dimension gamma(g) = c * g^2 / (16*pi^2).
    Input: array where x[0]=coupling g, x[1]=coefficient c.
    Output: scalar gamma."""
    g = x[0] if len(x) > 0 else 0.1
    c = x[1] if len(x) > 1 else 1.0
    gamma = c * g ** 2 / (16.0 * np.pi ** 2)
    return np.float64(gamma)


OPERATIONS["anomalous_dimension"] = {
    "fn": anomalous_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "One-loop anomalous dimension c * g^2 / (16*pi^2)"
}


def callan_symanzik_integrate(x):
    """Integrate the Callan-Symanzik equation: mu * dg/dmu = beta(g).
    Input: array where x[0]=g_0 (initial coupling), x[1]=b0, x[2]=log(mu/mu_0) range.
    Output: array of coupling values g(mu) along the flow.
    For one-loop: g(mu) = g_0 / sqrt(1 + b0*g_0^2*ln(mu/mu0)/(8*pi^2))."""
    g0 = x[0] if len(x) > 0 else 0.3
    b0 = x[1] if len(x) > 1 else 7.0  # QCD-like
    log_range = x[2] if len(x) > 2 else 5.0
    n_steps = min(int(abs(x[3])) if len(x) > 3 else 20, 100)
    t = np.linspace(0, log_range, n_steps)
    # Analytic one-loop running: g(t) = g0 / sqrt(1 + b0*g0^2*t/(8*pi^2))
    denom = 1.0 + b0 * g0 ** 2 * t / (8.0 * np.pi ** 2)
    # Handle possible Landau pole
    denom = np.maximum(denom, 1e-10)
    g_t = g0 / np.sqrt(denom)
    return g_t


OPERATIONS["callan_symanzik_integrate"] = {
    "fn": callan_symanzik_integrate,
    "input_type": "array",
    "output_type": "array",
    "description": "Integrate one-loop RG flow: coupling g(mu) vs scale"
}


def asymptotic_freedom_check(x):
    """Check if a gauge theory is asymptotically free.
    Input: array where x[0]=N_c, x[1]=N_f (for SU(N_c) with N_f fundamental fermions).
    Output: scalar (1 if asymptotically free, 0 if not).
    Condition: 11*N_c/3 > 2*N_f/3 => N_f < 11*N_c/2."""
    Nc = x[0] if len(x) > 0 else 3.0
    Nf = x[1] if len(x) > 1 else 6.0
    b0 = 11.0 * Nc / 3.0 - 2.0 * Nf / 3.0
    return np.float64(1.0 if b0 > 0 else 0.0)


OPERATIONS["asymptotic_freedom_check"] = {
    "fn": asymptotic_freedom_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check asymptotic freedom: 1 if b0 > 0, 0 otherwise"
}


def coupling_at_scale(x):
    """Running coupling at given scale using one-loop RG.
    Input: array where x[0]=g_0 at mu_0, x[1]=b0, x[2]=ln(mu/mu_0).
    Output: scalar g(mu)."""
    g0 = x[0] if len(x) > 0 else 0.3
    b0 = x[1] if len(x) > 1 else 7.0
    log_mu = x[2] if len(x) > 2 else 1.0
    denom = 1.0 + b0 * g0 ** 2 * log_mu / (8.0 * np.pi ** 2)
    if denom <= 0:
        return np.float64(np.inf)  # Landau pole
    g = g0 / np.sqrt(denom)
    return np.float64(g)


OPERATIONS["coupling_at_scale"] = {
    "fn": coupling_at_scale,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Running coupling g(mu) at scale mu using one-loop RG"
}


def dimensional_transmutation(x):
    """Compute dynamically generated scale Lambda from coupling.
    Input: array where x[0]=g at scale mu, x[1]=b0, x[2]=mu.
    Output: scalar Lambda_QCD = mu * exp(-8*pi^2 / (b0 * g^2))."""
    g = x[0] if len(x) > 0 else 0.3
    b0 = x[1] if len(x) > 1 else 7.0
    mu = x[2] if len(x) > 2 else 91.2  # Z boson mass
    if abs(b0 * g ** 2) < 1e-15:
        return np.float64(0.0)
    Lambda = mu * np.exp(-8.0 * np.pi ** 2 / (b0 * g ** 2))
    return np.float64(Lambda)


OPERATIONS["dimensional_transmutation"] = {
    "fn": dimensional_transmutation,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Dynamically generated scale Lambda = mu * exp(-8*pi^2/(b0*g^2))"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
