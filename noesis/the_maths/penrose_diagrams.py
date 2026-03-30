"""
Penrose Diagrams — Conformal compactification of spacetimes

Connects to: [kerr_geodesics, friedmann_equations, cosmic_topology]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "penrose_diagrams"
OPERATIONS = {}


def conformal_factor_minkowski(t, r):
    """Conformal factor Omega for Minkowski spacetime compactification.
    Using standard compactification: T=arctan(t+r)+arctan(t-r), R=arctan(t+r)-arctan(t-r).
    Omega = cos(T+R)*cos(T-R) = cos(2*arctan(t+r))*cos(2*arctan(t-r))...
    Simplified: Omega^2 = (1+(t+r)^2)^{-1} * (1+(t-r)^2)^{-1}.
    Input: t,r arrays. Output: Omega array."""
    t = np.asarray(t, dtype=float)
    r = np.asarray(r, dtype=float)
    omega_sq = 1.0 / ((1.0 + (t + r)**2) * (1.0 + (t - r)**2))
    return np.sqrt(omega_sq)

OPERATIONS["conformal_factor_minkowski"] = {
    "fn": lambda x: conformal_factor_minkowski(x, x * 0.5),
    "input_type": "array",
    "output_type": "array",
    "description": "Conformal factor Omega for Minkowski compactification"
}


def compactified_coordinates(t, r):
    """Penrose compactified coordinates (T, R) from Minkowski (t, r).
    T = arctan(t+r) + arctan(t-r), R = arctan(t+r) - arctan(t-r).
    Input: t,r arrays. Output: (T,R) tuple of arrays."""
    t = np.asarray(t, dtype=float)
    r = np.asarray(r, dtype=float)
    u = np.arctan(t + r)
    v = np.arctan(t - r)
    T = u + v
    R = u - v
    return np.column_stack([T, R])

OPERATIONS["compactified_coordinates"] = {
    "fn": lambda x: compactified_coordinates(x, np.abs(x) * 0.5),
    "input_type": "array",
    "output_type": "matrix",
    "description": "Penrose compactified coordinates (T,R) from (t,r)"
}


def causal_diamond_volume(T):
    """Volume of causal diamond in 1+1 Minkowski for interval of proper time T.
    V = T^2 / 2. Input: array of T values. Output: volume array."""
    T = np.asarray(T, dtype=float)
    return T**2 / 2.0

OPERATIONS["causal_diamond_volume"] = {
    "fn": causal_diamond_volume,
    "input_type": "array",
    "output_type": "array",
    "description": "Causal diamond volume in 1+1 Minkowski spacetime"
}


def null_geodesic_trace(t0, r0, n_steps=50):
    """Trace null geodesic in compactified Minkowski from (t0,r0).
    Outgoing: t = t0+s, r = r0+s along null ray. Returns compactified path.
    Input: t0,r0 scalars. Output: (n_steps,2) array of (T,R)."""
    t0 = float(np.asarray(t0).flat[0])
    r0 = float(np.abs(np.asarray(r0).flat[0]))
    s = np.linspace(0, 10, n_steps)
    t = t0 + s
    r = r0 + s
    return compactified_coordinates(t, r)

OPERATIONS["null_geodesic_trace"] = {
    "fn": lambda x: null_geodesic_trace(x[0], x[1]),
    "input_type": "array",
    "output_type": "matrix",
    "description": "Trace outgoing null geodesic in Penrose coordinates"
}


def penrose_time_coord(t, r):
    """Penrose time coordinate T = arctan(t+r) + arctan(t-r).
    Input: t,r arrays. Output: T array."""
    t = np.asarray(t, dtype=float)
    r = np.asarray(r, dtype=float)
    return np.arctan(t + r) + np.arctan(t - r)

OPERATIONS["penrose_time_coord"] = {
    "fn": lambda x: penrose_time_coord(x, np.abs(x) * 0.3),
    "input_type": "array",
    "output_type": "array",
    "description": "Penrose time coordinate T"
}


def penrose_space_coord(t, r):
    """Penrose space coordinate R = arctan(t+r) - arctan(t-r).
    Input: t,r arrays. Output: R array."""
    t = np.asarray(t, dtype=float)
    r = np.asarray(r, dtype=float)
    return np.arctan(t + r) - np.arctan(t - r)

OPERATIONS["penrose_space_coord"] = {
    "fn": lambda x: penrose_space_coord(x, np.abs(x) * 0.3),
    "input_type": "array",
    "output_type": "array",
    "description": "Penrose space coordinate R"
}


def future_light_cone_boundary(t0, r0, n_points=50):
    """Future light cone boundary from event (t0,r0) in compactified coords.
    Outgoing: r=r0+(t-t0), Ingoing: r=r0-(t-t0) for t>t0, r>=0.
    Input: t0,r0 scalars (from first elements of array). Output: (n,4) array."""
    t0 = float(np.asarray(t0).flat[0])
    r0 = float(np.abs(np.asarray(r0).flat[0]))
    dt = np.linspace(0, 5, n_points)
    # Outgoing
    t_out = t0 + dt
    r_out = r0 + dt
    out_comp = compactified_coordinates(t_out, r_out)
    # Ingoing (only while r >= 0)
    r_in = r0 - dt
    mask = r_in >= 0
    t_in = (t0 + dt)[mask]
    r_in = r_in[mask]
    in_comp = compactified_coordinates(t_in, r_in)
    return np.vstack([out_comp, in_comp])

OPERATIONS["future_light_cone_boundary"] = {
    "fn": lambda x: future_light_cone_boundary(x[0], x[1]),
    "input_type": "array",
    "output_type": "matrix",
    "description": "Future light cone boundary in Penrose coordinates"
}


def past_light_cone_boundary(t0, r0, n_points=50):
    """Past light cone boundary from event (t0,r0) in compactified coords.
    Input: t0,r0 scalars. Output: (n,4) array of compactified coords."""
    t0 = float(np.asarray(t0).flat[0])
    r0 = float(np.abs(np.asarray(r0).flat[0]))
    dt = np.linspace(0, 5, n_points)
    # Past outgoing (was ingoing)
    t_out = t0 - dt
    r_out = r0 + dt
    out_comp = compactified_coordinates(t_out, r_out)
    # Past ingoing
    r_in = r0 - dt
    mask = r_in >= 0
    t_in = (t0 - dt)[mask]
    r_in = r_in[mask]
    in_comp = compactified_coordinates(t_in, r_in)
    return np.vstack([out_comp, in_comp])

OPERATIONS["past_light_cone_boundary"] = {
    "fn": lambda x: past_light_cone_boundary(x[0], x[1]),
    "input_type": "array",
    "output_type": "matrix",
    "description": "Past light cone boundary in Penrose coordinates"
}


def causal_structure_matrix(events):
    """Compute causal relation matrix for a set of events in 1+1 Minkowski.
    M[i,j] = 1 if event i is in causal past of j (|t_j-t_i| >= |r_j-r_i|, t_j>t_i),
    -1 if in causal future, 0 if spacelike.
    Input: array of length n (interpreted as t coords, r=0). Output: (n,n) matrix."""
    events = np.asarray(events, dtype=float).ravel()
    n = len(events)
    t = events
    r = np.zeros(n)
    M = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            dt = t[j] - t[i]
            dr = abs(r[j] - r[i])
            if abs(dt) >= dr and dt > 1e-15:
                M[i, j] = 1   # i is in causal past of j
            elif abs(dt) >= dr and dt < -1e-15:
                M[i, j] = -1  # i is in causal future of j
    return M

OPERATIONS["causal_structure_matrix"] = {
    "fn": causal_structure_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Causal relation matrix for events in 1+1 Minkowski"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
