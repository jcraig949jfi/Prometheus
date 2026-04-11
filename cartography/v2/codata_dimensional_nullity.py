"""
NF4: Dimensional Basis Nullity
==============================
Build the M×N dimensional matrix for CODATA physical constants.
Rows = constants with SI-decomposable units.
Columns = base SI dimensions: [kg, m, s, A, K, mol, cd].
Entries = exponent of that base unit in the constant's dimension.

Compute rank and nullity (= number of independent dimensionless
combinations via Buckingham Pi theorem). Identify a minimal basis
set of constants that spans the column space.
"""

import json
import re
import numpy as np
from pathlib import Path

# ── Base SI dimensions (column order) ──
BASE_DIMS = ["kg", "m", "s", "A", "K", "mol", "cd"]

# ── Derived-to-base decomposition ──
# Each maps to a dict of {base_unit: exponent}
DERIVED = {
    "J":    {"kg": 1, "m": 2, "s": -2},              # joule
    "N":    {"kg": 1, "m": 1, "s": -2},              # newton
    "Pa":   {"kg": 1, "m": -1, "s": -2},             # pascal
    "W":    {"kg": 1, "m": 2, "s": -3},              # watt
    "C":    {"A": 1, "s": 1},                         # coulomb
    "V":    {"kg": 1, "m": 2, "s": -3, "A": -1},     # volt
    "F":    {"kg": -1, "m": -2, "s": 4, "A": 2},     # farad
    "ohm":  {"kg": 1, "m": 2, "s": -3, "A": -2},     # ohm
    "T":    {"kg": 1, "s": -2, "A": -1},              # tesla
    "Hz":   {"s": -1},                                 # hertz
    "lm":   {"cd": 1},                                # lumen (cd·sr, sr dimensionless)
    "eV":   {"kg": 1, "m": 2, "s": -2},              # electron-volt (same dims as J)
}

# Units we skip (non-SI or ambiguous)
SKIP_UNITS = {"u", "E_h", "GeV", "GeV^-2", "(GeV/c^2)^-2", "MeV", "MeV/c", "MHz T^-1"}


def parse_unit_string(unit_str: str) -> dict | None:
    """
    Parse a CODATA unit string like 'kg m^2 s^-3 A^-1' into
    a dict of {base_unit: exponent}. Returns None if unparseable
    or contains non-SI units.
    """
    if unit_str in SKIP_UNITS:
        return None

    dims = {d: 0 for d in BASE_DIMS}

    # Tokenize: split on spaces, each token is "unit" or "unit^exp"
    tokens = unit_str.strip().split()
    for token in tokens:
        # Parse token into (unit_name, exponent)
        m = re.match(r'^([A-Za-z]+)(\^(-?\d+))?$', token)
        if not m:
            return None
        name = m.group(1)
        exp = int(m.group(3)) if m.group(3) else 1

        if name in BASE_DIMS:
            dims[name] += exp
        elif name in DERIVED:
            for base, base_exp in DERIVED[name].items():
                dims[base] += base_exp * exp
        else:
            return None  # unknown unit

    return dims


def main():
    data_path = Path(__file__).parent.parent / "physics" / "data" / "codata" / "constants.json"
    with open(data_path) as f:
        constants = json.load(f)

    # ── Build dimensional matrix ──
    rows = []        # list of exponent vectors
    names = []       # constant names
    unit_strs = []   # original unit strings
    skipped = []     # constants we couldn't parse

    for c in constants:
        unit = c.get("unit")
        if unit is None:
            # Dimensionless — include as zero vector
            rows.append([0] * len(BASE_DIMS))
            names.append(c["name"])
            unit_strs.append("(dimensionless)")
            continue

        dims = parse_unit_string(unit)
        if dims is None:
            skipped.append({"name": c["name"], "unit": unit, "reason": "non-SI or unparseable"})
            continue

        row = [dims[d] for d in BASE_DIMS]
        rows.append(row)
        names.append(c["name"])
        unit_strs.append(unit)

    M = len(rows)
    N = len(BASE_DIMS)
    mat = np.array(rows, dtype=float)

    print(f"Dimensional matrix: {M} constants × {N} base dimensions")
    print(f"Skipped: {len(skipped)} constants (non-SI units)")

    # ── Rank and nullity ──
    rank = int(np.linalg.matrix_rank(mat))
    nullity = M - rank
    dimensionless_count = sum(1 for r in rows if all(x == 0 for x in r))

    print(f"\nRank of dimensional matrix: {rank}")
    print(f"Nullity (M - rank): {nullity}")
    print(f"  = {dimensionless_count} trivially dimensionless + {nullity - dimensionless_count} non-trivial dimensionless combinations")
    print(f"Number of base SI dimensions: {N}")
    print(f"Dimensions actually spanned: {rank}")

    # ── Find unique dimension vectors and which constants share them ──
    unique_dims = {}
    for i, row in enumerate(rows):
        key = tuple(row)
        if key not in unique_dims:
            unique_dims[key] = []
        unique_dims[key].append(names[i])

    print(f"\nUnique dimension signatures: {len(unique_dims)}")

    # ── Minimal basis: greedy selection of constants that span column space ──
    # Use row echelon form approach: pick first constant that adds rank
    basis_indices = []
    current_rank = 0
    sub = np.zeros((0, N), dtype=float)

    for i in range(M):
        candidate = np.vstack([sub, mat[i:i+1, :]])
        r = int(np.linalg.matrix_rank(candidate))
        if r > current_rank:
            basis_indices.append(i)
            sub = candidate
            current_rank = r
            if current_rank == rank:
                break

    basis_constants = []
    print(f"\nMinimal basis ({len(basis_indices)} constants spanning all {rank} occupied dimensions):")
    for idx in basis_indices:
        dims_dict = {BASE_DIMS[j]: int(rows[idx][j]) for j in range(N) if rows[idx][j] != 0}
        print(f"  {names[idx]:50s} {unit_strs[idx]:25s} -> {dims_dict}")
        basis_constants.append({
            "name": names[idx],
            "unit": unit_strs[idx],
            "dimensions": {BASE_DIMS[j]: int(rows[idx][j]) for j in range(N)},
        })

    # ── Which base dimensions are NOT covered? ──
    covered = set()
    for idx in basis_indices:
        for j in range(N):
            if rows[idx][j] != 0:
                covered.add(BASE_DIMS[j])
    uncovered = [d for d in BASE_DIMS if d not in covered]
    if uncovered:
        print(f"\nBase dimensions NOT spanned by any constant: {uncovered}")

    # ── Null space: find dimensionless combinations ──
    # For the unique non-zero rows, compute null space
    non_zero_rows = [(i, rows[i]) for i in range(M) if any(x != 0 for x in rows[i])]
    non_trivial_nullity = len(non_zero_rows) - rank

    print(f"\nNon-trivial dimensionless combinations (from {len(non_zero_rows)} dimensioned constants): {non_trivial_nullity}")

    # ── Save results ──
    results = {
        "description": "NF4: Dimensional Basis Nullity — CODATA physical constants",
        "matrix_shape": {"M_rows_constants": M, "N_cols_dimensions": N},
        "base_dimensions": BASE_DIMS,
        "rank": rank,
        "nullity": nullity,
        "dimensionless_constants_count": dimensionless_count,
        "non_trivial_dimensionless_combinations": non_trivial_nullity,
        "unique_dimension_signatures": len(unique_dims),
        "skipped_count": len(skipped),
        "skipped": skipped,
        "minimal_basis": basis_constants,
        "uncovered_dimensions": uncovered,
        "interpretation": {
            "buckingham_pi": f"Any formula involving these {M} constants can be rewritten using {nullity} dimensionless groups",
            "basis_meaning": f"Only {rank} constants are needed to represent all dimensional signatures; the rest are dimensionally redundant",
            "rank_vs_7": f"Rank {rank} out of 7 possible SI dimensions means {7 - rank} base dimensions are absent from CODATA constants" if rank < 7 else f"All 7 SI base dimensions are represented",
        },
        "dimension_signature_census": [
            {
                "dimensions": {BASE_DIMS[j]: int(k[j]) for j in range(N) if k[j] != 0},
                "count": len(v),
                "examples": v[:3],
            }
            for k, v in sorted(unique_dims.items(), key=lambda x: -len(x[1]))
        ],
    }

    out_path = Path(__file__).parent / "codata_dimensional_nullity_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
