"""
Stellar Structure — Lane-Emden equation and stellar models

Connects to: [friedmann_equations, kerr_geodesics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "stellar_structure"
OPERATIONS = {}


def lane_emden_integrate(n_poly, xi_max=20.0, n_steps=2000):
    """Integrate the Lane-Emden equation: d^2 theta/d xi^2 + (2/xi)*d theta/d xi + theta^n = 0.
    BC: theta(0)=1, theta'(0)=0.
    Input: n_poly array (use first element as polytropic index). Output: (n_steps,2) [xi, theta]."""
    n_poly = float(np.asarray(n_poly).flat[0])
    xi = np.linspace(1e-6, xi_max, n_steps)
    dxi = xi[1] - xi[0]
    theta = np.ones(n_steps)
    dtheta = np.zeros(n_steps)
    # Initial conditions near origin: theta ~ 1 - xi^2/6
    theta[0] = 1.0 - xi[0]**2 / 6.0
    dtheta[0] = -xi[0] / 3.0
    for i in range(n_steps - 1):
        if theta[i] <= 0:
            theta[i:] = 0.0
            break
        d2theta = -2.0 / xi[i] * dtheta[i] - np.abs(theta[i])**n_poly
        dtheta[i+1] = dtheta[i] + d2theta * dxi
        theta[i+1] = theta[i] + dtheta[i+1] * dxi
    return np.column_stack([xi, theta])

OPERATIONS["lane_emden_integrate"] = {
    "fn": lane_emden_integrate,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Integrate Lane-Emden equation for polytropic index n"
}


def chandrasekhar_mass_limit(mu_e):
    """Chandrasekhar mass limit M_Ch = 5.83 / mu_e^2 solar masses.
    mu_e = mean molecular weight per electron (~2 for He/C/O white dwarfs).
    Input: mu_e array. Output: M_Ch array in solar masses."""
    mu_e = np.asarray(mu_e, dtype=float)
    return 5.83 / mu_e**2

OPERATIONS["chandrasekhar_mass_limit"] = {
    "fn": chandrasekhar_mass_limit,
    "input_type": "array",
    "output_type": "array",
    "description": "Chandrasekhar mass limit in solar masses"
}


def polytropic_density_profile(xi, n_poly=1.5):
    """Density profile rho(xi) = rho_c * theta(xi)^n for polytrope.
    Uses Lane-Emden solution. Input: xi array (dimensionless radius). Output: rho/rho_c array."""
    xi = np.asarray(xi, dtype=float)
    # Solve Lane-Emden for the given n
    sol = lane_emden_integrate(np.array([n_poly]), xi_max=max(float(xi.max())+1, 10.0))
    xi_sol = sol[:, 0]
    theta_sol = sol[:, 1]
    theta_interp = np.interp(xi, xi_sol, theta_sol)
    theta_interp = np.clip(theta_interp, 0, None)
    return theta_interp ** n_poly

OPERATIONS["polytropic_density_profile"] = {
    "fn": polytropic_density_profile,
    "input_type": "array",
    "output_type": "array",
    "description": "Polytropic density profile rho/rho_c vs dimensionless radius"
}


def central_pressure(M, R):
    """Estimate central pressure for a star via P_c ~ G*M^2/(8*pi*R^4).
    Using solar units: P_c in dyn/cm^2 with M in Msun, R in Rsun.
    G=6.674e-8 cgs, Msun=1.989e33 g, Rsun=6.96e10 cm.
    Input: M array (solar masses), R scalar (solar radii). Output: P_c array."""
    M = np.asarray(M, dtype=float)
    G = 6.674e-8
    Msun = 1.989e33
    Rsun = 6.96e10
    R_cgs = R * Rsun
    M_cgs = M * Msun
    P_c = G * M_cgs**2 / (8.0 * np.pi * R_cgs**4)
    return P_c

OPERATIONS["central_pressure"] = {
    "fn": lambda x: central_pressure(x, 1.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Estimate central pressure of a star in dyn/cm^2"
}


def tov_equation_step(r, m, p, rho):
    """One step of the Tolman-Oppenheimer-Volkoff equation.
    dp/dr = -G(rho + p/c^2)(m + 4*pi*r^3*p/c^2) / (r^2*(1 - 2Gm/(rc^2)))
    In geometric units (G=c=1): dp/dr = -(rho+p)(m+4*pi*r^3*p) / (r*(r-2m)).
    Input: array [r, m, p, rho] (first 4 elements). Output: dp/dr scalar."""
    x = np.asarray([r, m, p, rho], dtype=float).ravel()
    r, m, p, rho = float(x[0]), float(x[1]), float(x[2]), float(x[3])
    if r < 1e-10:
        return np.float64(0.0)
    denom = r * (r - 2.0 * m)
    if denom <= 0:
        return np.float64(-1e30)  # inside horizon
    dpdr = -(rho + p) * (m + 4.0 * np.pi * r**3 * p) / denom
    return np.float64(dpdr)

OPERATIONS["tov_equation_step"] = {
    "fn": lambda x: tov_equation_step(x[0], x[1], x[2], x[3] if len(x)>3 else 1.0),
    "input_type": "array",
    "output_type": "scalar",
    "description": "One RHS evaluation of the TOV equation"
}


def mass_radius_relation(rho_c_arr, n_poly=1.5):
    """Mass-radius relation for polytropes: M ~ rho_c^{(3-n)/(2n)} * R^{(3-n)/(1-n)}.
    Simplified: compute dimensionless M and R from Lane-Emden solution.
    Input: central density array (dimensionless). Output: (n,2) [M, R] array."""
    rho_c = np.asarray(rho_c_arr, dtype=float)
    # From Lane-Emden: R = alpha*xi_1, M = -4*pi*alpha^3*rho_c*xi_1^2*theta'(xi_1)
    # alpha^2 = (n+1)*K*rho_c^{(1-n)/n} / (4*pi*G)
    # For dimensionless output scaled to rho_c:
    sol = lane_emden_integrate(np.array([n_poly]))
    xi_sol = sol[:, 0]
    theta_sol = sol[:, 1]
    # Find xi_1 where theta first goes to 0
    idx = np.where(theta_sol <= 0)[0]
    xi_1 = xi_sol[idx[0]] if len(idx) > 0 else xi_sol[-1]
    dtheta_1 = np.gradient(theta_sol, xi_sol)[idx[0]-1] if len(idx) > 0 else -0.1
    R_dim = rho_c**((1.0-n_poly)/(2.0*n_poly)) * xi_1
    M_dim = rho_c**((3.0-n_poly)/(2.0*n_poly)) * (-xi_1**2 * dtheta_1)
    return np.column_stack([M_dim, R_dim])

OPERATIONS["mass_radius_relation"] = {
    "fn": mass_radius_relation,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Mass-radius relation for polytropic stars"
}


def eddington_luminosity(M):
    """Eddington luminosity L_Edd = 4*pi*G*M*m_p*c / sigma_T.
    L_Edd ~ 1.26e38 * (M/Msun) erg/s.
    Input: M array in solar masses. Output: L_Edd array in erg/s."""
    M = np.asarray(M, dtype=float)
    return 1.26e38 * M

OPERATIONS["eddington_luminosity"] = {
    "fn": eddington_luminosity,
    "input_type": "array",
    "output_type": "array",
    "description": "Eddington luminosity in erg/s"
}


def stellar_lifetime_estimate(M):
    """Main-sequence lifetime estimate: t ~ 10^10 * (M/Msun)^{-2.5} years.
    Input: M array in solar masses. Output: lifetime array in years."""
    M = np.asarray(M, dtype=float)
    return 1e10 * M**(-2.5)

OPERATIONS["stellar_lifetime_estimate"] = {
    "fn": stellar_lifetime_estimate,
    "input_type": "array",
    "output_type": "array",
    "description": "Main-sequence lifetime estimate in years"
}


def lane_emden_exact_n0(xi):
    """Exact solution of Lane-Emden for n=0: theta = 1 - xi^2/6.
    First zero at xi_1 = sqrt(6).
    Input: xi array. Output: theta array."""
    xi = np.asarray(xi, dtype=float)
    theta = 1.0 - xi**2 / 6.0
    return np.clip(theta, 0, None)

OPERATIONS["lane_emden_exact_n0"] = {
    "fn": lane_emden_exact_n0,
    "input_type": "array",
    "output_type": "array",
    "description": "Exact Lane-Emden solution for n=0"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
