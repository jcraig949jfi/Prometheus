"""
KnotInfo Ingestion — Parse knot polynomial data into searchable JSON.
=====================================================================
Input: knot_polys.xlsx (12,965 knots with polynomial vectors)
Output: knots.json (structured, searchable)

Vector format: {min_power, max_power, coeff_0, coeff_1, ...}
We extract coefficients as integer arrays for:
  - Alexander polynomial (bridge to OEIS, number theory)
  - Jones polynomial (bridge to OEIS, representation theory)
  - Conway polynomial (bridge to OEIS)

Run: python cartography/knots/scripts/ingest_knotinfo.py
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
XLSX_PATH = DATA_DIR / "knot_polys.xlsx"
OUTPUT_PATH = DATA_DIR / "knots.json"


def parse_vector(vec_str: str) -> dict:
    """Parse KnotInfo vector format: {min_power, max_power, coeff_0, ...}

    Returns {min_power, max_power, coefficients: [int, ...]}
    """
    if not vec_str or not isinstance(vec_str, str):
        return None
    # Strip braces and split
    cleaned = vec_str.strip().strip("{}")
    parts = [p.strip() for p in cleaned.split(",")]
    if len(parts) < 3:
        return None
    try:
        min_power = int(parts[0])
        max_power = int(parts[1])
        coeffs = [int(p) for p in parts[2:]]
        return {
            "min_power": min_power,
            "max_power": max_power,
            "coefficients": coeffs,
        }
    except (ValueError, IndexError):
        return None


def parse_crossing_number(name: str) -> int:
    """Extract crossing number from knot name like '3_1' or '10_152'."""
    m = re.match(r"(\d+)_", name)
    return int(m.group(1)) if m else 0


def ingest():
    import openpyxl
    print(f"Loading {XLSX_PATH}...")
    wb = openpyxl.load_workbook(str(XLSX_PATH), read_only=True)
    ws = wb["Sheet1"]

    knots = []
    skipped = 0

    for i, row in enumerate(ws.iter_rows(min_row=3, values_only=True)):
        name = row[0]
        if not name or not isinstance(name, str) or name == "Name":
            skipped += 1
            continue

        crossing = parse_crossing_number(name)
        alex = parse_vector(row[3])   # alexander_polynomial_vector
        jones = parse_vector(row[5])  # jones_polynomial_vector
        conway = parse_vector(row[7]) # conway_polynomial_vector

        # Build invariant vector: concatenate Alexander + Jones coefficients
        # Pad to fixed length for embedding
        alex_coeffs = alex["coefficients"] if alex else []
        jones_coeffs = jones["coefficients"] if jones else []
        conway_coeffs = conway["coefficients"] if conway else []

        # Determinant = |Alexander(−1)| — alternating sum of coefficients
        determinant = None
        if alex_coeffs:
            det = 0
            for j, c in enumerate(alex_coeffs):
                det += c * ((-1) ** (alex["min_power"] + j)) if alex else 0
            determinant = abs(det)

        knot = {
            "name": name,
            "crossing_number": crossing,
            "determinant": determinant,
            "alexander": alex,
            "jones": jones,
            "conway": conway,
            "alex_coeffs": alex_coeffs,
            "jones_coeffs": jones_coeffs,
            "conway_coeffs": conway_coeffs,
        }
        knots.append(knot)

    wb.close()

    # Sort by crossing number then name
    knots.sort(key=lambda k: (k["crossing_number"], k["name"]))

    # Stats
    n_alex = sum(1 for k in knots if k["alexander"])
    n_jones = sum(1 for k in knots if k["jones"])
    n_conway = sum(1 for k in knots if k["conway"])
    n_det = sum(1 for k in knots if k["determinant"] is not None)

    crossing_dist = {}
    for k in knots:
        c = k["crossing_number"]
        crossing_dist[c] = crossing_dist.get(c, 0) + 1

    # Collect all determinants for bridge analysis
    determinants = sorted(set(k["determinant"] for k in knots if k["determinant"] is not None))

    print(f"Parsed {len(knots)} knots (skipped {skipped})")
    print(f"  Alexander: {n_alex} | Jones: {n_jones} | Conway: {n_conway}")
    print(f"  Determinants: {n_det} computed, {len(determinants)} unique values")
    print(f"  Crossing numbers: {sorted(crossing_dist.keys())[:10]}... max={max(crossing_dist.keys())}")
    print(f"  Top crossings: {sorted(crossing_dist.items(), key=lambda x: -x[1])[:5]}")

    # Save
    output = {
        "n_knots": len(knots),
        "stats": {
            "n_alexander": n_alex,
            "n_jones": n_jones,
            "n_conway": n_conway,
            "n_determinants": n_det,
            "unique_determinants": len(determinants),
            "crossing_distribution": crossing_dist,
        },
        "determinants_list": determinants[:200],  # For OEIS bridge queries
        "knots": knots,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=None), encoding="utf-8")
    size_mb = OUTPUT_PATH.stat().st_size / 1024 / 1024
    print(f"Saved to {OUTPUT_PATH} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    ingest()
