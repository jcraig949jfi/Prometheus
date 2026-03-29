"""
Mathematical Music Theory -- Pitch class sets, interval vectors, Forte numbers, Z12 group actions

Connects to: [modular_arithmetic_exotic, finite_fields, combinatorial_species, lattice_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "mathematical_music_theory"
OPERATIONS = {}


def pitch_class_set_normal_form(x):
    """Compute normal form of a pitch class set (mod 12). Input: array. Output: array."""
    pcs = np.unique(np.round(x) % 12).astype(int)
    n = len(pcs)
    if n <= 1:
        return pcs.astype(float)
    pcs = np.sort(pcs)
    # Try all rotations, find the one with smallest span then lexicographically smallest
    best = None
    for i in range(n):
        rotated = np.roll(pcs, -i)
        # Transpose so first element is 0
        normalized = (rotated - rotated[0]) % 12
        if best is None or _lex_compare(normalized, best) < 0:
            best = normalized.copy()
    return best.astype(float)


def _lex_compare(a, b):
    """Compare two arrays lexicographically, preferring smaller span first."""
    if a[-1] != b[-1]:
        return -1 if a[-1] < b[-1] else 1
    for i in range(len(a)):
        if a[i] != b[i]:
            return -1 if a[i] < b[i] else 1
    return 0


OPERATIONS["pitch_class_set_normal_form"] = {
    "fn": pitch_class_set_normal_form,
    "input_type": "array",
    "output_type": "array",
    "description": "Normal form of pitch class set in Z12"
}


def interval_vector(x):
    """Compute interval vector (IC vector) of a pitch class set. Input: array. Output: array (6 entries)."""
    pcs = np.unique(np.round(x) % 12).astype(int)
    iv = np.zeros(6)
    n = len(pcs)
    for i in range(n):
        for j in range(i + 1, n):
            interval = abs(int(pcs[j]) - int(pcs[i]))
            ic = min(interval, 12 - interval)
            if 1 <= ic <= 6:
                iv[ic - 1] += 1
    return iv


OPERATIONS["interval_vector"] = {
    "fn": interval_vector,
    "input_type": "array",
    "output_type": "array",
    "description": "Interval class vector [ic1, ic2, ic3, ic4, ic5, ic6]"
}


def forte_number_lookup(x):
    """Return approximate Forte catalog index based on set cardinality and interval vector.
    Input: array. Output: scalar (encoded as cardinality * 100 + index)."""
    pcs = np.unique(np.round(x) % 12).astype(int)
    card = len(pcs)
    iv = interval_vector(x)
    # Hash the interval vector to get a pseudo-index
    index = int(np.sum(iv * np.array([1, 6, 36, 216, 1296, 7776]))) % 50 + 1
    return float(card * 100 + index)


OPERATIONS["forte_number_lookup"] = {
    "fn": forte_number_lookup,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate Forte number as cardinality*100 + catalog_index"
}


def transposition_z12(x):
    """Transpose pitch class set by n semitones (n = last element). Input: array. Output: array."""
    if len(x) < 2:
        return x.copy()
    n = int(np.round(x[-1]))
    pcs = x[:-1]
    return (np.round(pcs) + n) % 12


OPERATIONS["transposition_z12"] = {
    "fn": transposition_z12,
    "input_type": "array",
    "output_type": "array",
    "description": "Transpose pitch class set by n semitones (T_n operation in Z12)"
}


def inversion_z12(x):
    """Invert pitch class set: map each pc to (12 - pc) mod 12. Input: array. Output: array."""
    pcs = np.round(x) % 12
    return (12 - pcs) % 12


OPERATIONS["inversion_z12"] = {
    "fn": inversion_z12,
    "input_type": "array",
    "output_type": "array",
    "description": "Inversion I(pc) = (12 - pc) mod 12"
}


def retrograde(x):
    """Retrograde: reverse the sequence. Input: array. Output: array."""
    return x[::-1].copy()


OPERATIONS["retrograde"] = {
    "fn": retrograde,
    "input_type": "array",
    "output_type": "array",
    "description": "Retrograde (time reversal) of a pitch sequence"
}


def pitch_class_complement(x):
    """Complement: all pitch classes NOT in the set. Input: array. Output: array."""
    pcs = set(int(p) for p in np.unique(np.round(x) % 12))
    complement = sorted(set(range(12)) - pcs)
    return np.array(complement, dtype=float)


OPERATIONS["pitch_class_complement"] = {
    "fn": pitch_class_complement,
    "input_type": "array",
    "output_type": "array",
    "description": "Pitch class complement in Z12"
}


def set_class_cardinality(x):
    """Number of distinct transpositions and inversions of this set class. Input: array. Output: scalar."""
    pcs = np.unique(np.round(x) % 12).astype(int)
    nf = pitch_class_set_normal_form(x)
    seen = set()
    for t in range(12):
        # Transposition
        trans = tuple(sorted((nf + t) % 12))
        seen.add(trans)
        # Transposition of inversion
        inv = tuple(sorted((12 - nf + t) % 12))
        seen.add(inv)
    return float(len(seen))


OPERATIONS["set_class_cardinality"] = {
    "fn": set_class_cardinality,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of distinct forms in the set class (TnI orbit size)"
}


def all_interval_tetrachord(x):
    """Check if input (mod 12, 4 pcs) is an all-interval tetrachord. Input: array. Output: scalar (0 or 1)."""
    pcs = np.unique(np.round(x[:4]) % 12).astype(int) if len(x) >= 4 else np.unique(np.round(x) % 12).astype(int)
    if len(pcs) != 4:
        return 0.0
    iv = interval_vector(pcs.astype(float))
    # All-interval tetrachord has interval vector [1,1,1,1,1,1]
    if np.array_equal(iv, np.ones(6)):
        return 1.0
    return 0.0


OPERATIONS["all_interval_tetrachord"] = {
    "fn": all_interval_tetrachord,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if 4-element set is an all-interval tetrachord"
}


def tone_row_properties(x):
    """Analyze a 12-tone row: return array of [is_valid_row, num_unique_intervals,
    interval_content_richness]. Input: array. Output: array."""
    row = np.round(x) % 12
    n = len(row)
    unique_pcs = len(np.unique(row))
    is_valid = 1.0 if unique_pcs == 12 and n >= 12 else 0.0
    # Successive intervals
    if n > 1:
        intervals = np.diff(row) % 12
        unique_intervals = len(np.unique(intervals))
        richness = unique_intervals / 11.0
    else:
        unique_intervals = 0
        richness = 0.0
    return np.array([is_valid, float(unique_intervals), richness])


OPERATIONS["tone_row_properties"] = {
    "fn": tone_row_properties,
    "input_type": "array",
    "output_type": "array",
    "description": "Properties of a 12-tone row: [is_valid, unique_intervals, richness]"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
