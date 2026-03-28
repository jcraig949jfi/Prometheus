"""
Chaos Theory organism.

Operations: logistic_map, lyapunov_exponent, lorenz_system, tent_map
"""

from .base import MathematicalOrganism


class ChaosTheory(MathematicalOrganism):
    name = "chaos_theory"
    operations = {
        "logistic_map": {
            "code": """
def logistic_map(r, x0=0.5, n_steps=200):
    \"\"\"Iterate x_{n+1} = r * x_n * (1 - x_n).
    Returns the full trajectory as a 1-D array.\"\"\"
    x = np.zeros(n_steps + 1)
    x[0] = x0
    for i in range(n_steps):
        x[i + 1] = r * x[i] * (1.0 - x[i])
    return x
""",
            "input_type": "scalar",
            "output_type": "timeseries",
        },
        "lyapunov_exponent": {
            "code": """
def lyapunov_exponent(r, x0=0.5, n_steps=10000, n_transient=1000):
    \"\"\"Compute the Lyapunov exponent of the logistic map at parameter r.
    lambda = (1/N) sum ln|f'(x_n)| where f'(x) = r(1 - 2x).\"\"\"
    x = x0
    # Discard transient
    for _ in range(n_transient):
        x = r * x * (1.0 - x)

    lyap_sum = 0.0
    for _ in range(n_steps):
        deriv = abs(r * (1.0 - 2.0 * x))
        if deriv == 0:
            return float('-inf')
        lyap_sum += np.log(deriv)
        x = r * x * (1.0 - x)

    return lyap_sum / n_steps
""",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "lorenz_system": {
            "code": """
def lorenz_system(state0=None, sigma=10.0, rho=28.0, beta=8.0/3.0,
                  dt=0.01, n_steps=5000):
    \"\"\"Integrate the Lorenz system using RK4.
    dx/dt = sigma*(y - x)
    dy/dt = x*(rho - z) - y
    dz/dt = x*y - beta*z
    Returns (n_steps+1, 3) trajectory.\"\"\"
    if state0 is None:
        state0 = [1.0, 1.0, 1.0]
    state = np.array(state0, dtype=np.float64)
    trajectory = np.zeros((n_steps + 1, 3))
    trajectory[0] = state

    def deriv(s):
        x, y, z = s
        return np.array([
            sigma * (y - x),
            x * (rho - z) - y,
            x * y - beta * z,
        ])

    for i in range(n_steps):
        k1 = deriv(state)
        k2 = deriv(state + 0.5 * dt * k1)
        k3 = deriv(state + 0.5 * dt * k2)
        k4 = deriv(state + dt * k3)
        state = state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        trajectory[i + 1] = state

    return trajectory
""",
            "input_type": "state_vector",
            "output_type": "trajectory",
        },
        "tent_map": {
            "code": """
def tent_map(mu, x0=0.4, n_steps=200):
    \"\"\"Iterate the tent map:
    x_{n+1} = mu * x_n           if x_n < 0.5
              mu * (1 - x_n)     if x_n >= 0.5
    Returns full trajectory.\"\"\"
    x = np.zeros(n_steps + 1)
    x[0] = x0
    for i in range(n_steps):
        if x[i] < 0.5:
            x[i + 1] = mu * x[i]
        else:
            x[i + 1] = mu * (1.0 - x[i])
    return x
""",
            "input_type": "scalar",
            "output_type": "timeseries",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = ChaosTheory()
    print(org)

    # Logistic map in chaotic regime
    traj = org.execute("logistic_map", 3.9)
    print(f"Logistic map r=3.9: last 5 values = {traj[-5:]}")

    # Lyapunov exponent: positive means chaos
    lam = org.execute("lyapunov_exponent", 3.9)
    print(f"Lyapunov(r=3.9) = {lam:.4f}  (expect > 0, chaotic)")

    lam2 = org.execute("lyapunov_exponent", 3.2)
    print(f"Lyapunov(r=3.2) = {lam2:.4f}  (expect < 0, periodic)")

    # Lorenz attractor
    lorenz = org.execute("lorenz_system", n_steps=1000)
    print(f"Lorenz trajectory shape: {lorenz.shape}, final state: {lorenz[-1]}")

    # Tent map
    tent = org.execute("tent_map", 1.9)
    print(f"Tent map mu=1.9: last 5 values = {tent[-5:]}")

    print("--- chaos_theory: ALL TESTS PASSED ---")
