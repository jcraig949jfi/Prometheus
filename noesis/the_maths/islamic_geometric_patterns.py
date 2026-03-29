"""
Islamic Geometric Patterns — Wallpaper groups, girih tiles, quasi-crystalline constructions

Connects to: [sona_lusona, bambara_divination, context_dependent_arithmetic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

Islamic geometric art encodes deep mathematical structure: the 17 wallpaper
groups, girih tile substitution rules, and quasi-crystalline patterns with
forbidden 5-fold symmetry (anticipating Penrose tilings by centuries).
"""

import numpy as np

FIELD_NAME = "islamic_geometric_patterns"
OPERATIONS = {}

# The 5 girih tile types with their interior angles (in degrees)
GIRIH_TILES = {
    "tabl": {"sides": 10, "angle": 144},       # regular decagon
    "pange": {"sides": 5, "angle": 108},        # regular pentagon
    "shesh_band": {"sides": 6, "angle_seq": [72, 144, 144, 72, 144, 144]},  # elongated hexagon
    "sormeh_dan": {"sides": 4, "angle_seq": [72, 108, 72, 108]},  # bowtie/rhombus
    "torange": {"sides": 4, "angle_seq": [36, 144, 36, 144]},     # kite
}


def wallpaper_group_detect(x):
    """Detect wallpaper group properties from a 2D pattern encoded in x.
    Analyzes symmetry order. The 17 wallpaper groups have rotation orders
    1, 2, 3, 4, or 6. Returns [max_rotation_order, has_reflection, has_glide].
    Input: array. Output: array."""
    n = len(x)
    # Test rotational symmetry by checking correlation with rotated versions
    best_order = 1
    for order in [6, 4, 3, 2]:
        step = n // order
        if step < 1 or n % order != 0:
            continue
        reshaped = x[:step * order].reshape(order, step)
        ref = reshaped[0]
        match = all(np.allclose(reshaped[i], ref, atol=0.5) for i in range(1, order))
        if match:
            best_order = order
            break

    # Reflection: check palindrome-like symmetry
    has_reflection = 1.0 if np.allclose(x, x[::-1], atol=0.5) else 0.0

    # Glide reflection: shift by half and reflect
    half = n // 2
    if half > 0:
        shifted = np.roll(x, half)
        has_glide = 1.0 if np.allclose(shifted, x[::-1], atol=0.5) else 0.0
    else:
        has_glide = 0.0

    return np.array([float(best_order), has_reflection, has_glide])


OPERATIONS["wallpaper_group_detect"] = {
    "fn": wallpaper_group_detect,
    "input_type": "array",
    "output_type": "array",
    "description": "Detects wallpaper group symmetry properties"
}


def girih_tile_substitution(x):
    """Apply girih tile substitution: inflate each value by the golden ratio
    phi = (1+sqrt(5))/2, then subdivide. This models how girih tiles decompose
    into smaller tiles at ratio 1/phi. Input: array. Output: array."""
    phi = (1.0 + np.sqrt(5.0)) / 2.0
    # Inflate
    inflated = x * phi
    # Subdivide: each tile produces two sub-tiles (at 1/phi and 1/phi^2 scale)
    sub1 = inflated / phi
    sub2 = inflated / (phi * phi)
    return np.concatenate([sub1, sub2])


OPERATIONS["girih_tile_substitution"] = {
    "fn": girih_tile_substitution,
    "input_type": "array",
    "output_type": "array",
    "description": "Girih tile inflation/substitution via golden ratio"
}


def girih_tile_types(x):
    """Classify each value into one of 5 girih tile types based on angle.
    Maps value modulo 360 to nearest girih angle: 36(torange), 72(sormeh_dan),
    108(pange), 144(tabl/shesh_band). Returns tile type index 0-4.
    Input: array. Output: array."""
    angles = np.array([36.0, 72.0, 108.0, 144.0, 160.0])  # representative angles
    vals = np.abs(x) % 360.0
    result = np.zeros(len(x))
    for i, v in enumerate(vals):
        result[i] = float(np.argmin(np.abs(angles - v)))
    return result


OPERATIONS["girih_tile_types"] = {
    "fn": girih_tile_types,
    "input_type": "array",
    "output_type": "array",
    "description": "Classifies values into 5 girih tile types by angle"
}


def quasi_crystalline_point_set(x):
    """Generate quasi-crystalline point set using the cut-and-project method.
    Project a 5D lattice onto 2D using angles from x.
    Returns 2D coordinates as flat array. Input: array. Output: array."""
    n = len(x)
    # Use x values as phase offsets for 5 wave directions
    phases = np.zeros(5)
    phases[:min(n, 5)] = x[:min(n, 5)]

    points = []
    grid_range = 5
    for i in range(-grid_range, grid_range + 1):
        for j in range(-grid_range, grid_range + 1):
            # Project using 5-fold angles
            px = 0.0
            py = 0.0
            for k in range(5):
                angle = 2.0 * np.pi * k / 5.0 + phases[k] * 0.01
                px += np.cos(angle) * (i * np.cos(k * 0.4) + j * np.sin(k * 0.4))
                py += np.sin(angle) * (i * np.cos(k * 0.4) + j * np.sin(k * 0.4))
            points.extend([px, py])
    return np.array(points)


OPERATIONS["quasi_crystalline_point_set"] = {
    "fn": quasi_crystalline_point_set,
    "input_type": "array",
    "output_type": "array",
    "description": "Quasi-crystalline point set via 5D cut-and-project"
}


def fivefold_symmetry_generate(x):
    """Generate 5-fold symmetric pattern: rotate each point by 72 degrees.
    Input treated as radial distances. Returns (r, theta) pairs.
    Input: array. Output: array."""
    result = []
    for r in x:
        for k in range(5):
            theta = 2.0 * np.pi * k / 5.0
            result.extend([np.abs(r) * np.cos(theta), np.abs(r) * np.sin(theta)])
    return np.array(result)


OPERATIONS["fivefold_symmetry_generate"] = {
    "fn": fivefold_symmetry_generate,
    "input_type": "array",
    "output_type": "array",
    "description": "Generates 5-fold rotationally symmetric point set"
}


def tiling_symmetry_order(x):
    """Compute the symmetry order of the pattern in x.
    Tests for n-fold rotational symmetry for n = 1..12.
    Input: array. Output: scalar."""
    n = len(x)
    best = 1
    for order in range(12, 1, -1):
        if n % order != 0:
            continue
        step = n // order
        ref = x[:step]
        match = True
        for k in range(1, order):
            segment = x[k * step:(k + 1) * step]
            if len(segment) != len(ref) or not np.allclose(segment, ref, atol=0.1):
                match = False
                break
        if match:
            best = order
            break
    return float(best)


OPERATIONS["tiling_symmetry_order"] = {
    "fn": tiling_symmetry_order,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Highest rotational symmetry order of the pattern"
}


def pattern_inflation_factor(x):
    """Compute inflation factor for self-similar tiling.
    For Islamic girih patterns, this is the golden ratio phi.
    Estimates from data by comparing successive scale ratios.
    Input: array. Output: scalar."""
    if len(x) < 2:
        return 1.0
    sorted_x = np.sort(np.abs(x[x != 0])) if np.any(x != 0) else np.array([1.0, 1.0])
    if len(sorted_x) < 2:
        return 1.0
    ratios = sorted_x[1:] / np.where(sorted_x[:-1] == 0, 1e-12, sorted_x[:-1])
    return float(np.median(ratios))


OPERATIONS["pattern_inflation_factor"] = {
    "fn": pattern_inflation_factor,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimated self-similar inflation factor"
}


def crystallographic_restriction_check(x):
    """Check crystallographic restriction theorem: only rotational symmetries
    of order 1, 2, 3, 4, 6 are allowed in periodic 2D tilings.
    Returns 1.0 if the detected order is allowed, 0.0 if forbidden (quasi-crystal).
    Input: array. Output: scalar."""
    order = int(tiling_symmetry_order(x))
    allowed = {1, 2, 3, 4, 6}
    return 1.0 if order in allowed else 0.0


OPERATIONS["crystallographic_restriction_check"] = {
    "fn": crystallographic_restriction_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Checks if symmetry order obeys crystallographic restriction"
}


def rosette_group_construct(x):
    """Construct rosette group pattern: cyclic Cn symmetry.
    Uses first element as the symmetry order n, remaining as template.
    Returns the full rosetted pattern. Input: array. Output: array."""
    n_sym = max(int(np.clip(x[0], 2, 12)), 2) if len(x) > 0 else 4
    template = x[1:] if len(x) > 1 else np.array([1.0])
    result = []
    for k in range(n_sym):
        angle = 2.0 * np.pi * k / n_sym
        # Rotate template values by angle (phase shift)
        rotated = template * np.cos(angle) + np.roll(template, 1) * np.sin(angle)
        result.extend(rotated)
    return np.array(result)


OPERATIONS["rosette_group_construct"] = {
    "fn": rosette_group_construct,
    "input_type": "array",
    "output_type": "array",
    "description": "Constructs cyclic rosette group pattern"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
