#!/usr/bin/env sage
"""
Hecke Characteristic Polynomial Computation — SageMath
=======================================================
Computes T_p characteristic polynomials for cusp forms across weights and levels.
Required for Gouvea-Mazur ladder verification and Maeda's conjecture testing.

This must be run inside SageMath (not plain Python):
    sage compute_hecke_charpolys.sage
    sage compute_hecke_charpolys.sage --max-weight 100 --level 1 --primes 2,3,5

Output: cartography/convergence/data/hecke_charpolys.json

The output includes:
  - Characteristic polynomials of T_p for each (level, weight, prime) triple
  - Dimension of the cusp form space
  - Whether the polynomial is irreducible (relevant to Maeda's conjecture)
  - p-adic valuation data (relevant to Gouvea-Mazur slopes)
"""

import json
import os
import sys
from datetime import datetime

# Parse command-line arguments (sage passes them after --)
import argparse
parser = argparse.ArgumentParser(description="Compute Hecke characteristic polynomials")
parser.add_argument("--max-weight", type=int, default=50, help="Maximum even weight (default: 50)")
parser.add_argument("--level", type=int, default=1, help="Level (default: 1)")
parser.add_argument("--primes", type=str, default="2,3,5,7", help="Comma-separated primes (default: 2,3,5,7)")
parser.add_argument("--output", type=str, default=None, help="Output file path")
args = parser.parse_args()

# Resolve output path relative to repo structure
if args.output:
    output_path = args.output
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    output_path = os.path.join(repo_root, "cartography", "convergence", "data", "hecke_charpolys.json")

primes = [int(p) for p in args.primes.split(",")]
max_weight = args.max_weight
level = args.level

print(f"=== Hecke Characteristic Polynomial Computation ===")
print(f"Level: {level}")
print(f"Primes: {primes}")
print(f"Weight range: 2 to {max_weight} (even)")
print(f"Output: {output_path}")
print()

results = {
    "source": "SageMath computation",
    "table": "hecke_characteristic_polynomials",
    "computed": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "parameters": {
        "level": level,
        "max_weight": max_weight,
        "primes": primes,
    },
    "records": [],
}

total_computed = 0
total_irreducible = 0

for k in range(2, max_weight + 2, 2):
    try:
        S = CuspForms(level, k)
        dim = S.dimension()

        if dim == 0:
            continue

        weight_data = {
            "weight": k,
            "dimension": dim,
            "hecke_polys": {},
        }

        for p in primes:
            try:
                T = S.hecke_operator(p)
                poly = T.charpoly()

                # Check irreducibility (Maeda's conjecture: should be irreducible for level 1)
                is_irred = poly.is_irreducible()

                # Extract coefficients as list of integers
                coeffs = [int(c) for c in poly.list()]

                # For Gouvea-Mazur: compute p-adic slopes of roots
                # (Newton polygon slopes)
                newton_slopes = []
                if p in ZZ and dim > 0:
                    try:
                        Rp = Qp(p, prec=20)
                        poly_p = poly.change_ring(Rp)
                        np = poly_p.newton_polygon()
                        newton_slopes = [(int(s[0]), int(s[1])) for s in np.vertices()]
                    except Exception:
                        newton_slopes = []  # p-adic computation may fail for large polys

                weight_data["hecke_polys"][str(p)] = {
                    "charpoly_coeffs": coeffs,
                    "degree": len(coeffs) - 1,
                    "is_irreducible": is_irred,
                    "newton_slopes": newton_slopes,
                }

                total_computed += 1
                if is_irred:
                    total_irreducible += 1

                status = "IRRED" if is_irred else "REDUCIBLE"
                print(f"  Weight {k:3d}, T_{p}: deg={len(coeffs)-1} [{status}]")

            except Exception as e:
                print(f"  Weight {k:3d}, T_{p}: FAILED — {e}")
                weight_data["hecke_polys"][str(p)] = {"error": str(e)}

        results["records"].append(weight_data)

    except Exception as e:
        print(f"  Weight {k:3d}: SPACE FAILED — {e}")

print()
print(f"=== Summary ===")
print(f"Total polynomials computed: {total_computed}")
print(f"Irreducible: {total_irreducible} / {total_computed}")
if total_computed > 0:
    irred_pct = 100.0 * total_irreducible / total_computed
    print(f"Irreducibility rate: {irred_pct:.1f}%")
    if level == 1 and irred_pct == 100.0:
        print("Maeda's conjecture consistent: all level-1 charpolys irreducible")

results["summary"] = {
    "total_weights": len(results["records"]),
    "total_polynomials": total_computed,
    "total_irreducible": total_irreducible,
}

# Ensure output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults → {output_path}")
