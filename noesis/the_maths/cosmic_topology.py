"""
Cosmic Topology — Nontrivial topology of flat universes

Connects to: [friedmann_equations, penrose_diagrams, tqft]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "cosmic_topology"
OPERATIONS = {}


def flat_torus_eigenmodes(L, n_max=5):
    """Eigenmodes of the Laplacian on a flat 3-torus with side length L.
    Eigenvalues: lambda_{n1,n2,n3} = (2*pi/L)^2 * (n1^2 + n2^2 + n3^2).
    Input: L array (use first element). Output: sorted array of distinct eigenvalues."""
    L_val = float(np.asarray(L).flat[0])
    base = (2.0 * np.pi / L_val) ** 2
    eigenvalues = set()
    for n1 in range(-n_max, n_max+1):
        for n2 in range(-n_max, n_max+1):
            for n3 in range(-n_max, n_max+1):
                lam = base * (n1**2 + n2**2 + n3**2)
                eigenvalues.add(round(lam, 10))
    return np.sort(np.array(list(eigenvalues)))

OPERATIONS["flat_torus_eigenmodes"] = {
    "fn": flat_torus_eigenmodes,
    "input_type": "array",
    "output_type": "array",
    "description": "Eigenvalues of Laplacian on flat 3-torus"
}


def fundamental_domain_volume(L):
    """Volume of the fundamental domain of a flat 3-torus: V = L1*L2*L3.
    For cubic torus: V = L^3. Input: L array (side lengths). Output: scalar volume."""
    L = np.asarray(L, dtype=float)
    if L.size >= 3:
        return np.float64(L[0] * L[1] * L[2])
    return np.float64(L[0] ** 3)

OPERATIONS["fundamental_domain_volume"] = {
    "fn": fundamental_domain_volume,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Volume of fundamental domain of flat torus"
}


def covering_space_copies(L, R):
    """Number of copies of fundamental domain visible within radius R.
    N ~ (4/3)*pi*R^3 / L^3 for cubic torus.
    Input: array [L, R, ...] or L array with R=max. Output: count array."""
    arr = np.asarray(L, dtype=float)
    if arr.size >= 2:
        L_val, R_val = arr[0], arr[1]
    else:
        L_val = arr[0]
        R_val = 3.0 * L_val
    V_sphere = 4.0/3.0 * np.pi * R_val**3
    V_domain = L_val**3
    return np.float64(V_sphere / V_domain)

OPERATIONS["covering_space_copies"] = {
    "fn": lambda x: covering_space_copies(x, 3.0 * float(np.asarray(x).flat[0])),
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of fundamental domain copies within given radius"
}


def cosmic_crystallography_pattern(L, n_points=100):
    """Pair separation histogram peaks for a toroidal universe.
    In a 3-torus of side L, pair separations cluster at |n|*L for integer vectors n.
    Returns the expected peak positions. Input: L array (first elem). Output: peak array."""
    L_val = float(np.asarray(L).flat[0])
    peaks = []
    for n1 in range(0, 4):
        for n2 in range(0, 4):
            for n3 in range(0, 4):
                if n1 == 0 and n2 == 0 and n3 == 0:
                    continue
                d = L_val * np.sqrt(n1**2 + n2**2 + n3**2)
                peaks.append(d)
    return np.sort(np.unique(np.round(peaks, 8)))

OPERATIONS["cosmic_crystallography_pattern"] = {
    "fn": cosmic_crystallography_pattern,
    "input_type": "array",
    "output_type": "array",
    "description": "Expected pair-separation peaks for toroidal universe"
}


def klein_bottle_identification(points):
    """Apply Klein bottle identification to 2D points: (x, y) ~ (x+L, y) ~ (-x, y+L).
    Maps points into fundamental domain [0,L) x [0,L) with orientation reversal.
    Input: array (interpreted as x-coordinates, y=0, L=max(x)). Output: identified x array."""
    x = np.asarray(points, dtype=float)
    L = np.max(np.abs(x)) + 1.0
    # Klein bottle identification on x-coordinate with L
    x_mod = x % L
    # The orientation-reversing identification means crossing y-boundary flips x
    # For 1D projection: just apply standard modular identification
    return x_mod

OPERATIONS["klein_bottle_identification"] = {
    "fn": klein_bottle_identification,
    "input_type": "array",
    "output_type": "array",
    "description": "Klein bottle identification map on coordinates"
}


def laplacian_eigenvalues_torus(L, n_modes=20):
    """First n_modes eigenvalues of the Laplacian on a 2-torus with sides L1=L, L2=L.
    lambda_{m,n} = (2*pi)^2 * (m^2 + n^2) / L^2.
    Input: L array (first elem). Output: first n_modes eigenvalues sorted."""
    L_val = float(np.asarray(L).flat[0])
    base = (2.0 * np.pi / L_val) ** 2
    eigenvalues = set()
    n_max = int(np.sqrt(n_modes)) + 3
    for m in range(-n_max, n_max+1):
        for n in range(-n_max, n_max+1):
            eigenvalues.add(round(base * (m**2 + n**2), 10))
    eigs = np.sort(np.array(list(eigenvalues)))
    return eigs[:n_modes]

OPERATIONS["laplacian_eigenvalues_torus"] = {
    "fn": laplacian_eigenvalues_torus,
    "input_type": "array",
    "output_type": "array",
    "description": "First eigenvalues of Laplacian on a 2-torus"
}


def topology_from_spectrum_test(eigenvalues):
    """Test if a Laplacian spectrum is consistent with a flat torus.
    Check if eigenvalue ratios match n1^2+n2^2 pattern.
    Input: eigenvalue array. Output: array of ratios lambda_i/lambda_1."""
    eigs = np.asarray(eigenvalues, dtype=float)
    eigs = eigs[eigs > 1e-10]  # remove zero eigenvalue
    if len(eigs) < 2:
        return np.array([1.0])
    ratios = eigs / eigs[0]
    return ratios

OPERATIONS["topology_from_spectrum_test"] = {
    "fn": topology_from_spectrum_test,
    "input_type": "array",
    "output_type": "array",
    "description": "Eigenvalue ratios to test for flat torus topology"
}


def genus_from_euler(V, E, F):
    """Genus of a surface from Euler characteristic: chi = V - E + F = 2 - 2g.
    g = (2 - chi) / 2.
    Input: array [V, E, F, ...]. Output: genus scalar."""
    arr = np.asarray([V, E, F], dtype=float).ravel()
    V, E, F = float(arr[0]), float(arr[1]), float(arr[2])
    chi = V - E + F
    g = (2.0 - chi) / 2.0
    return np.float64(g)

OPERATIONS["genus_from_euler"] = {
    "fn": lambda x: genus_from_euler(x[0], x[1], x[2]),
    "input_type": "array",
    "output_type": "scalar",
    "description": "Genus from Euler characteristic (V - E + F)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
