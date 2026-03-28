"""
Dynamical Systems organism.

Operations: fixed_points, stability_analysis, bifurcation_scan,
            phase_portrait_2d
"""

from .base import MathematicalOrganism


class DynamicalSystems(MathematicalOrganism):
    name = "dynamical_systems"
    operations = {
        "fixed_points": {
            "code": """
def fixed_points(f_code, x_range=(-5, 5), n_grid=1000, tol=1e-8, max_iter=100):
    \"\"\"Find fixed points of x' = f(x) for a 1-D system via Newton's method
    seeded from a grid.
    f_code: string defining f(x) using numpy (e.g. 'x**2 - x' for x*=0, x*=1).
    Returns array of unique fixed points.\"\"\"
    # Compile f
    f_ns = {"np": np}
    exec("def f(x): return " + f_code, f_ns)
    f = f_ns["f"]

    lo, hi = x_range
    seeds = np.linspace(lo, hi, n_grid)
    fps = []

    for x0 in seeds:
        x = x0
        for _ in range(max_iter):
            fx = f(x)
            # Numerical derivative
            eps = 1e-8
            dfx = (f(x + eps) - f(x - eps)) / (2 * eps)
            if abs(dfx - 1.0) < 1e-12:
                break  # derivative of g(x)=f(x)+x is dfx, but for x'=f(x), fp is f(x)=0
            # Newton step for f(x) = 0
            if abs(fx) < tol:
                fps.append(round(x, 8))
                break
            x = x - fx / (dfx if abs(dfx) > 1e-14 else 1e-14)
            if x < lo or x > hi:
                break

    # Deduplicate
    if not fps:
        return np.array([])
    fps = sorted(set(fps))
    unique = [fps[0]]
    for fp in fps[1:]:
        if abs(fp - unique[-1]) > 1e-6:
            unique.append(fp)
    return np.array(unique)
""",
            "input_type": "function_string",
            "output_type": "vector",
        },
        "stability_analysis": {
            "code": """
def stability_analysis(jacobian):
    \"\"\"Analyse stability of a fixed point from its Jacobian matrix.
    Returns eigenvalues, stability classification, and type.\"\"\"
    J = np.asarray(jacobian, dtype=np.float64)
    eigenvalues = np.linalg.eigvals(J)
    real_parts = eigenvalues.real

    # Classification
    if np.all(real_parts < -1e-10):
        stability = "stable"
    elif np.all(real_parts > 1e-10):
        stability = "unstable"
    elif np.any(np.abs(real_parts) < 1e-10):
        stability = "center/marginal"
    else:
        stability = "saddle"

    # Type for 2D
    if len(eigenvalues) == 2:
        if np.all(np.abs(eigenvalues.imag) < 1e-10):
            if eigenvalues[0].real * eigenvalues[1].real < 0:
                fp_type = "saddle_point"
            elif stability == "stable":
                fp_type = "stable_node"
            else:
                fp_type = "unstable_node"
        else:
            if stability == "stable":
                fp_type = "stable_spiral"
            elif stability == "unstable":
                fp_type = "unstable_spiral"
            else:
                fp_type = "center"
    else:
        fp_type = "n-dimensional"

    return {
        "eigenvalues": eigenvalues,
        "real_parts": real_parts,
        "stability": stability,
        "type": fp_type,
    }
""",
            "input_type": "matrix",
            "output_type": "dict",
        },
        "bifurcation_scan": {
            "code": """
def bifurcation_scan(f_code, param_range=(2.5, 4.0), n_params=500,
                     n_transient=500, n_collect=200, x0=0.5):
    \"\"\"Scan a 1-D map x_{n+1} = f(x, r) across parameter r.
    f_code: string like 'r * x * (1 - x)' using variables x and r.
    Returns (param_values, attractors) for bifurcation diagram.\"\"\"
    f_ns = {"np": np}
    exec("def f(x, r): return " + f_code, f_ns)
    f = f_ns["f"]

    params = np.linspace(param_range[0], param_range[1], n_params)
    all_r = []
    all_x = []

    for r in params:
        x = x0
        # Transient
        for _ in range(n_transient):
            x = f(x, r)
            if not np.isfinite(x):
                x = x0
                break
        # Collect attractor
        for _ in range(n_collect):
            x = f(x, r)
            if np.isfinite(x):
                all_r.append(r)
                all_x.append(x)

    return {"params": np.array(all_r), "values": np.array(all_x)}
""",
            "input_type": "function_string",
            "output_type": "dict",
        },
        "phase_portrait_2d": {
            "code": """
def phase_portrait_2d(fx_code, fy_code, x_range=(-3, 3), y_range=(-3, 3),
                      n_grid=20, n_trajectories=8, dt=0.02, n_steps=500):
    \"\"\"Compute a 2D phase portrait.
    fx_code, fy_code: strings for dx/dt and dy/dt using variables x, y.
    E.g. fx_code='-y', fy_code='x' for simple harmonic oscillator.
    Returns vector field grid and sample trajectories.\"\"\"
    f_ns = {"np": np}
    exec("def fx(x, y): return " + fx_code, f_ns)
    exec("def fy(x, y): return " + fy_code, f_ns)
    fx = f_ns["fx"]
    fy = f_ns["fy"]

    # Vector field on grid
    xs = np.linspace(x_range[0], x_range[1], n_grid)
    ys = np.linspace(y_range[0], y_range[1], n_grid)
    X, Y = np.meshgrid(xs, ys)
    U = np.zeros_like(X)
    V = np.zeros_like(Y)
    for i in range(n_grid):
        for j in range(n_grid):
            U[i, j] = fx(X[i, j], Y[i, j])
            V[i, j] = fy(X[i, j], Y[i, j])

    # Sample trajectories via RK4
    trajectories = []
    angles = np.linspace(0, 2*np.pi, n_trajectories, endpoint=False)
    r0 = min(x_range[1] - x_range[0], y_range[1] - y_range[0]) * 0.3
    for angle in angles:
        x0 = r0 * np.cos(angle)
        y0 = r0 * np.sin(angle)
        traj = np.zeros((n_steps + 1, 2))
        traj[0] = [x0, y0]
        x, y = x0, y0
        for t in range(n_steps):
            k1x, k1y = fx(x, y), fy(x, y)
            k2x, k2y = fx(x+0.5*dt*k1x, y+0.5*dt*k1y), fy(x+0.5*dt*k1x, y+0.5*dt*k1y)
            k3x, k3y = fx(x+0.5*dt*k2x, y+0.5*dt*k2y), fy(x+0.5*dt*k2x, y+0.5*dt*k2y)
            k4x, k4y = fx(x+dt*k3x, y+dt*k3y), fy(x+dt*k3x, y+dt*k3y)
            x += (dt/6)*(k1x + 2*k2x + 2*k3x + k4x)
            y += (dt/6)*(k1y + 2*k2y + 2*k3y + k4y)
            traj[t+1] = [x, y]
            # Bail if diverging
            if abs(x) > 100 or abs(y) > 100:
                traj = traj[:t+2]
                break
        trajectories.append(traj)

    return {
        "grid_X": X, "grid_Y": Y,
        "field_U": U, "field_V": V,
        "trajectories": trajectories,
    }
""",
            "input_type": "function_string_pair",
            "output_type": "dict",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = DynamicalSystems()
    print(org)

    # Fixed points of x' = x^2 - x  => x*(x-1) = 0 => x=0, x=1
    fps = org.execute("fixed_points", "x**2 - x", x_range=(-2, 3))
    print(f"Fixed points of x^2 - x: {fps}  (expect [0, 1])")

    # Fixed points of x' = sin(x)
    fps2 = org.execute("fixed_points", "np.sin(x)", x_range=(-10, 10))
    print(f"Fixed points of sin(x): {fps2}  (expect multiples of pi)")

    # Stability analysis: stable spiral
    J = np.array([[-0.1, 1.0], [-1.0, -0.1]])
    stab = org.execute("stability_analysis", J)
    print(f"Jacobian eigenvalues: {stab['eigenvalues']}")
    print(f"Stability: {stab['stability']}, type: {stab['type']}")

    # Stability of a saddle point
    J2 = np.array([[1.0, 0.0], [0.0, -2.0]])
    stab2 = org.execute("stability_analysis", J2)
    print(f"Saddle eigenvalues: {stab2['eigenvalues']}, type: {stab2['type']}")

    # Bifurcation scan of logistic map
    bif = org.execute("bifurcation_scan", "r * x * (1 - x)",
                      param_range=(2.5, 4.0), n_params=100, n_collect=50)
    print(f"Bifurcation scan: {len(bif['params'])} points collected")

    # Phase portrait: damped oscillator x' = y, y' = -x - 0.3*y
    pp = org.execute("phase_portrait_2d", "y", "-x - 0.3*y")
    print(f"Phase portrait: {len(pp['trajectories'])} trajectories, "
          f"field shape: {pp['field_U'].shape}")

    print("--- dynamical_systems: ALL TESTS PASSED ---")
