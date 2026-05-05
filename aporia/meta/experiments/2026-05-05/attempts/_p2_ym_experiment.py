"""
P2 / Yang-Mills mass gap: 2D U(1) lattice gauge as calibration anchor.

In 2D U(1), the Wilson plaquette action gives an exactly solvable theory.
The plaquette expectation value is

    <cos theta_plaq> = I_1(beta) / I_0(beta)

where I_n is the modified Bessel function.  Wilson loops follow exact
area law

    <W(R, T)> = ( I_1(beta) / I_0(beta) )^(R*T)

(for 2D U(1) on a periodic lattice, in the planar Wilson-loop regime).

This script runs a Metropolis simulation and verifies these to ~3
significant digits.  The mass gap question is *not* solved here -- the
purpose is to anchor the simulation toolchain in the regime where
rigorous existence + exact analytic answers both hold, contrasting with
4D non-Abelian where neither does.
"""
import numpy as np
from scipy.special import iv

rng = np.random.default_rng(20260505)

L = 16        # 2D lattice size L x L
beta = 2.0    # gauge coupling
n_therm = 2000
n_meas = 4000
n_skip = 5

# theta[mu, x, y] in [0, 2pi), for mu in {0, 1}
theta = rng.uniform(0, 2 * np.pi, size=(2, L, L))

def plaquette_angle(theta, x, y):
    """U_mu(x) U_nu(x+mu_hat) U_mu(x+nu_hat)^* U_nu(x)^* with mu=0, nu=1."""
    return (theta[0, x, y]
            + theta[1, (x + 1) % L, y]
            - theta[0, x, (y + 1) % L]
            - theta[1, x, y])

def avg_plaquette(theta):
    s = 0.0
    for x in range(L):
        for y in range(L):
            s += np.cos(plaquette_angle(theta, x, y))
    return s / (L * L)

def wilson_loop(theta, R, T, x0=0, y0=0):
    """Rectangular Wilson loop sides R (x-dir) and T (y-dir) at corner (x0,y0)."""
    s = 0.0
    for r in range(R):
        s += theta[0, (x0 + r) % L, y0]
    for t in range(T):
        s += theta[1, (x0 + R) % L, (y0 + t) % L]
    for r in range(R):
        s -= theta[0, (x0 + R - 1 - r) % L, (y0 + T) % L]
    for t in range(T):
        s -= theta[1, x0, (y0 + T - 1 - t) % L]
    return np.cos(s)

def metropolis_sweep(theta, beta):
    """Single sweep through every link with random proposal."""
    accepted = 0
    for mu in (0, 1):
        for x in range(L):
            for y in range(L):
                old = theta[mu, x, y]
                proposal = old + rng.uniform(-1.0, 1.0)
                # change in action: link mu at x,y enters 2 plaquettes
                # for mu=0: plaq at (x,y) and at (x, y-1)
                # for mu=1: plaq at (x,y) and at (x-1, y)
                if mu == 0:
                    s_old = (np.cos(plaquette_angle(theta, x, y))
                             + np.cos(plaquette_angle(theta, x, (y - 1) % L)))
                else:
                    s_old = (np.cos(plaquette_angle(theta, x, y))
                             + np.cos(plaquette_angle(theta, (x - 1) % L, y)))
                theta[mu, x, y] = proposal
                if mu == 0:
                    s_new = (np.cos(plaquette_angle(theta, x, y))
                             + np.cos(plaquette_angle(theta, x, (y - 1) % L)))
                else:
                    s_new = (np.cos(plaquette_angle(theta, x, y))
                             + np.cos(plaquette_angle(theta, (x - 1) % L, y)))
                dS = -beta * (s_new - s_old)
                if dS <= 0 or rng.random() < np.exp(-dS):
                    accepted += 1
                else:
                    theta[mu, x, y] = old
    return accepted / (2 * L * L)

# Thermalize
for sweep in range(n_therm):
    metropolis_sweep(theta, beta)

# Measure
plaq_vals = []
w11_vals = []
w22_vals = []
w13_vals = []

for sweep in range(n_meas):
    metropolis_sweep(theta, beta)
    if sweep % n_skip == 0:
        plaq_vals.append(avg_plaquette(theta))
        # average Wilson loops over a few origin choices to reduce variance
        w11 = np.mean([wilson_loop(theta, 1, 1, x, y) for x in range(0, L, 4) for y in range(0, L, 4)])
        w22 = np.mean([wilson_loop(theta, 2, 2, x, y) for x in range(0, L, 4) for y in range(0, L, 4)])
        w13 = np.mean([wilson_loop(theta, 1, 3, x, y) for x in range(0, L, 4) for y in range(0, L, 4)])
        w11_vals.append(w11)
        w22_vals.append(w22)
        w13_vals.append(w13)

plaq_mean = np.mean(plaq_vals)
plaq_err = np.std(plaq_vals) / np.sqrt(len(plaq_vals))
w11_mean = np.mean(w11_vals)
w11_err = np.std(w11_vals) / np.sqrt(len(w11_vals))
w22_mean = np.mean(w22_vals)
w22_err = np.std(w22_vals) / np.sqrt(len(w22_vals))
w13_mean = np.mean(w13_vals)
w13_err = np.std(w13_vals) / np.sqrt(len(w13_vals))

# Exact analytic predictions
exact_plaq = iv(1, beta) / iv(0, beta)
exact_w11 = exact_plaq ** 1
exact_w22 = exact_plaq ** 4
exact_w13 = exact_plaq ** 3

print(f"L = {L}, beta = {beta}")
print(f"thermalize sweeps : {n_therm}")
print(f"measurement sweeps: {n_meas}")
print(f"effective samples : {len(plaq_vals)}")
print()
print(f"plaquette  : sim {plaq_mean:.5f} +/- {plaq_err:.5f}   exact {exact_plaq:.5f}")
print(f"W(1,1)     : sim {w11_mean:.5f} +/- {w11_err:.5f}   exact {exact_w11:.5f}")
print(f"W(2,2)     : sim {w22_mean:.5f} +/- {w22_err:.5f}   exact {exact_w22:.5f}")
print(f"W(1,3)     : sim {w13_mean:.5f} +/- {w13_err:.5f}   exact {exact_w13:.5f}")

string_tension_sim = -np.log(max(w22_mean, 1e-10)) / 4
string_tension_exact = -np.log(exact_plaq)
print()
print(f"string tension (from W(2,2) area law)  : sim {string_tension_sim:.5f}   exact -log(I1/I0) = {string_tension_exact:.5f}")
