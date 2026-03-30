"""
Quasicrystal Mathematics — aperiodic tilings and Penrose math

Connects to: [aperiodic_order, diffraction_theory, algebraic_number_theory, phason_dynamics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "quasicrystal_mathematics"
OPERATIONS = {}

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio


def penrose_vertex_count(x):
    """Count vertices in a Penrose tiling patch after n inflation steps.
    Vertex count follows Fibonacci-like growth. n = int(sum of input) mod 20.
    Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    n = int(np.abs(np.sum(x))) % 20
    # After n inflations starting from a single rhombus:
    # Vertex count ~ C * phi^(2n). Start: ~4 vertices for a rhombus.
    # Exact: V(n) follows the Fibonacci recurrence scaled
    if n == 0:
        return 4.0
    a, b = 4.0, 10.0  # V(0), V(1) for a kite-dart pair
    for _ in range(n - 1):
        a, b = b, a + b  # Fibonacci-like growth
    return float(b)

OPERATIONS["penrose_vertex_count"] = {
    "fn": penrose_vertex_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Vertex count after n Penrose inflation steps (Fibonacci growth)"
}


def fibonacci_chain(x):
    """Generate a Fibonacci quasicrystal chain (1D quasicrystal).
    Uses the substitution rule: L -> LS, S -> L.
    Length determined by input length. Returns binary array (1=L, 0=S).
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = max(len(x), 3)
    # Generate Fibonacci word by substitution
    word = [1]  # Start with L
    while len(word) < n:
        new_word = []
        for c in word:
            if c == 1:  # L -> LS
                new_word.extend([1, 0])
            else:  # S -> L
                new_word.append(1)
        word = new_word
    return np.array(word[:n], dtype=float)

OPERATIONS["fibonacci_chain"] = {
    "fn": fibonacci_chain,
    "input_type": "array",
    "output_type": "array",
    "description": "Fibonacci quasicrystal chain via L->LS, S->L substitution"
}


def cut_and_project_1d(x):
    """1D cut-and-project method: project a strip of the 2D integer lattice
    onto a line with irrational slope (golden ratio). Produces a 1D quasicrystal.
    Input: array (used for strip width). Output: array (projected points)."""
    x = np.asarray(x, dtype=float)
    width = max(np.mean(np.abs(x)), 0.5)
    n_search = 50  # Search range in 2D lattice

    # Line direction: (1, phi)
    direction = np.array([1.0, PHI])
    direction /= np.linalg.norm(direction)
    perp = np.array([-direction[1], direction[0]])

    points = []
    for i in range(-n_search, n_search + 1):
        for j in range(-n_search, n_search + 1):
            pt = np.array([float(i), float(j)])
            # Distance to the line through origin with direction
            perp_dist = abs(np.dot(pt, perp))
            if perp_dist < width:
                proj = np.dot(pt, direction)
                points.append(proj)

    points = np.sort(np.array(points))
    # Return a reasonable number of points
    if len(points) > 50:
        step = len(points) // 50
        points = points[::step]
    return points[:50] if len(points) > 50 else points

OPERATIONS["cut_and_project_1d"] = {
    "fn": cut_and_project_1d,
    "input_type": "array",
    "output_type": "array",
    "description": "1D quasicrystal via cut-and-project from 2D lattice with golden slope"
}


def phason_strain(x):
    """Compute phason strain: deviation from ideal quasicrystal positions.
    In a Fibonacci chain, ideal spacings are L=phi, S=1. Phason strain
    measures deviation of actual spacings from these ideal values.
    Input: array (spacings). Output: scalar."""
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return 0.0
    spacings = np.abs(np.diff(x))
    if len(spacings) == 0:
        return 0.0
    # Ideal spacings: each should be either phi or 1
    strain = 0.0
    for s in spacings:
        # Distance to nearest ideal spacing
        d_long = abs(s - PHI)
        d_short = abs(s - 1.0)
        strain += min(d_long, d_short) ** 2
    return float(np.sqrt(strain / len(spacings)))

OPERATIONS["phason_strain"] = {
    "fn": phason_strain,
    "input_type": "array",
    "output_type": "scalar",
    "description": "RMS phason strain: deviation of spacings from ideal L=phi, S=1"
}


def diffraction_pattern_1d(x):
    """Compute 1D diffraction pattern (power spectrum) of a point set.
    The diffraction of a quasicrystal has Bragg peaks at positions related
    to the golden ratio. Returns |F(k)|^2 at selected k values.
    Input: array (point positions). Output: array."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n == 0:
        return np.array([0.0])
    # Compute structure factor at selected k values
    k_values = np.linspace(0.1, 10.0, 30)
    intensity = np.zeros(len(k_values))
    for i, k in enumerate(k_values):
        # S(k) = |sum_j exp(i k x_j)|^2 / N
        phases = np.exp(1j * k * x)
        intensity[i] = np.abs(np.sum(phases)) ** 2 / n
    return intensity

OPERATIONS["diffraction_pattern_1d"] = {
    "fn": diffraction_pattern_1d,
    "input_type": "array",
    "output_type": "array",
    "description": "1D diffraction pattern (structure factor) of point set"
}


def ammann_beenker_density(x):
    """Compute vertex density of Ammann-Beenker tiling (octagonal quasicrystal).
    Density = (1 + sqrt(2)) per unit cell area. Returns density after n steps.
    Input: array (length = steps). Output: scalar."""
    x = np.asarray(x, dtype=float)
    n = min(len(x), 15)
    # Ammann-Beenker: inflation factor = 1 + sqrt(2) (silver ratio)
    silver = 1 + np.sqrt(2)
    # Vertex count grows as silver^(2n), area grows as silver^(2n)
    # Density converges to a constant
    # Starting from a single octagon: 8 vertices, area = 2(1+sqrt(2))
    if n == 0:
        return 8.0 / (2 * silver)
    vertices = 8.0
    area = 2.0 * silver
    for _ in range(n):
        vertices = vertices * silver ** 2
        area = area * silver ** 2
    density = vertices / area
    return float(density)

OPERATIONS["ammann_beenker_density"] = {
    "fn": ammann_beenker_density,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Vertex density of Ammann-Beenker octagonal quasicrystal tiling"
}


def debruijn_penrose_dual(x):
    """De Bruijn's dual method: construct Penrose tiling vertices from
    families of parallel lines. Uses 5 families at 72-degree angles.
    Returns vertex coordinates (flattened x,y pairs).
    Input: array (used as offsets for the 5 line families). Output: array."""
    x = np.asarray(x, dtype=float)
    # 5 families of lines at angles 0, 72, 144, 216, 288 degrees
    n_families = 5
    offsets = np.zeros(n_families)
    offsets[:min(len(x), n_families)] = x[:min(len(x), n_families)]

    angles = np.array([k * 2 * np.pi / 5 for k in range(n_families)])
    normals = np.column_stack([np.cos(angles), np.sin(angles)])

    # For each pair of families, find intersection points
    vertices = []
    grid_range = range(-3, 4)
    for f1 in range(n_families):
        for f2 in range(f1 + 1, n_families):
            n1 = normals[f1]
            n2 = normals[f2]
            det = n1[0] * n2[1] - n1[1] * n2[0]
            if abs(det) < 1e-10:
                continue
            for k1 in grid_range:
                for k2 in grid_range:
                    d1 = k1 + offsets[f1 % len(offsets)]
                    d2 = k2 + offsets[f2 % len(offsets)]
                    # Solve n1.v = d1, n2.v = d2
                    vx = (d1 * n2[1] - d2 * n1[1]) / det
                    vy = (n1[0] * d2 - n2[0] * d1) / det
                    vertices.append([vx, vy])

    if len(vertices) == 0:
        return np.array([0.0, 0.0])
    vertices = np.array(vertices)
    # Return flattened, limited size
    flat = vertices[:50].flatten()
    return flat

OPERATIONS["debruijn_penrose_dual"] = {
    "fn": debruijn_penrose_dual,
    "input_type": "array",
    "output_type": "array",
    "description": "De Bruijn dual method: Penrose vertices from 5 families of parallel lines"
}


def quasicrystal_inflation_factor(x):
    """Compute inflation factors for various quasicrystal types.
    Penrose: phi, Ammann-Beenker: 1+sqrt(2), Danzer: phi^2, etc.
    Returns array of common inflation factors raised to powers from input.
    Input: array (exponents). Output: array."""
    x = np.asarray(x, dtype=float)
    # Common quasicrystal inflation factors
    factors = np.array([
        PHI,                    # Penrose (5-fold)
        1 + np.sqrt(2),        # Ammann-Beenker (8-fold)
        2 + np.sqrt(3),        # 12-fold
        PHI ** 2,              # Danzer tiling
        2 * np.cos(np.pi/7),   # 7-fold
    ])
    # Apply exponents from input
    n = min(len(x), len(factors))
    result = factors[:n] ** np.abs(x[:n])
    return result

OPERATIONS["quasicrystal_inflation_factor"] = {
    "fn": quasicrystal_inflation_factor,
    "input_type": "array",
    "output_type": "array",
    "description": "Quasicrystal inflation factors raised to input exponents"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
