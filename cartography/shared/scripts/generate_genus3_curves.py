#!/usr/bin/env python3
"""
Generate random genus-3 plane quartics for SageMath Frobenius computation.
=========================================================================
Produces smooth plane quartics C: f(x,y,z) = 0 of degree 4 in P^2.
A smooth plane quartic has genus g = (d-1)(d-2)/2 = 3.

Output: cartography/shared/scripts/v2/genus3_sage_input.json
        (appends to existing curves, deduplicates by polynomial)

Smoothness check: the discriminant of a ternary quartic is expensive,
so we use a heuristic — check the curve has no singular points mod several
small primes. SageMath does the real verification.

Usage: python generate_genus3_curves.py [--count 900] [--max-coeff 5]
"""

import argparse
import json
import random
import itertools
from pathlib import Path

OUT_FILE = Path(__file__).resolve().parent / "v2" / "genus3_sage_input.json"


def monomial_basis_deg4():
    """All monomials of degree 4 in x, y, z (15 total)."""
    basis = []
    for i in range(5):
        for j in range(5 - i):
            k = 4 - i - j
            basis.append((i, j, k))
    return basis


def poly_to_str(coeffs, basis):
    """Convert coefficient vector to polynomial string (SageMath-compatible)."""
    terms = []
    for c, (i, j, k) in zip(coeffs, basis):
        if c == 0:
            continue
        parts = []
        if i > 0:
            parts.append(f"x^{i}" if i > 1 else "x")
        if j > 0:
            parts.append(f"y^{j}" if j > 1 else "y")
        if k > 0:
            parts.append(f"z^{k}" if k > 1 else "z")
        monomial = "*".join(parts) if parts else "1"
        if c == 1:
            terms.append(monomial)
        elif c == -1:
            terms.append(f"-{monomial}")
        else:
            terms.append(f"{c}*{monomial}")
    if not terms:
        return "0"
    result = terms[0]
    for t in terms[1:]:
        if t.startswith("-"):
            result += f" - {t[1:]}"
        else:
            result += f" + {t}"
    return result


def eval_poly_mod_p(coeffs, basis, x, y, z, p):
    """Evaluate polynomial mod p."""
    val = 0
    for c, (i, j, k) in zip(coeffs, basis):
        val = (val + c * pow(x, i, p) * pow(y, j, p) * pow(z, k, p)) % p
    return val


def partial_deriv(coeffs, basis, var_idx):
    """Compute partial derivative (returns new coeffs, new basis)."""
    new_coeffs = []
    new_basis = []
    for c, mono in zip(coeffs, basis):
        if mono[var_idx] > 0:
            new_c = c * mono[var_idx]
            new_mono = list(mono)
            new_mono[var_idx] -= 1
            new_coeffs.append(new_c)
            new_basis.append(tuple(new_mono))
    return new_coeffs, new_basis


def is_likely_smooth(coeffs, basis, primes=(5, 7, 11, 13)):
    """Heuristic smoothness: check no singular points mod several primes."""
    # Compute partials
    dx_c, dx_b = partial_deriv(coeffs, basis, 0)
    dy_c, dy_b = partial_deriv(coeffs, basis, 1)
    dz_c, dz_b = partial_deriv(coeffs, basis, 2)

    for p in primes:
        # Check all projective points mod p
        found_singular = False
        for x in range(p):
            for y in range(p):
                for z in range(p):
                    if x == 0 and y == 0 and z == 0:
                        continue
                    f_val = eval_poly_mod_p(coeffs, basis, x, y, z, p)
                    if f_val % p != 0:
                        continue
                    fx = eval_poly_mod_p(dx_c, dx_b, x, y, z, p)
                    fy = eval_poly_mod_p(dy_c, dy_b, x, y, z, p)
                    fz = eval_poly_mod_p(dz_c, dz_b, x, y, z, p)
                    if fx % p == 0 and fy % p == 0 and fz % p == 0:
                        found_singular = True
                        break
                if found_singular:
                    break
            if found_singular:
                break
        if found_singular:
            return False
    return True


def generate_random_quartic(max_coeff, basis):
    """Generate a random degree-4 ternary form with small coefficients."""
    # Sparse: zero out ~40% of terms
    coeffs = []
    for _ in basis:
        if random.random() < 0.4:
            coeffs.append(0)
        else:
            coeffs.append(random.randint(-max_coeff, max_coeff))
    # Ensure not all zero
    if all(c == 0 for c in coeffs):
        coeffs[random.randint(0, len(coeffs)-1)] = 1
    return coeffs


def make_id_from_coeffs(coeffs):
    """Deterministic ID from coefficients (for dedup)."""
    # Use hash of coefficient tuple
    h = hash(tuple(coeffs))
    return str(abs(h) % 10**7)


def main():
    parser = argparse.ArgumentParser(description="Generate genus-3 plane quartics")
    parser.add_argument("--count", type=int, default=900, help="Number of new curves to generate")
    parser.add_argument("--max-coeff", type=int, default=5, help="Max absolute value of coefficients")
    args = parser.parse_args()

    basis = monomial_basis_deg4()
    print(f"Monomial basis: {len(basis)} terms of degree 4")
    print(f"Generating {args.count} smooth plane quartics (max_coeff={args.max_coeff})...")

    # Load existing curves
    existing = {"curves": []}
    if OUT_FILE.exists():
        with open(OUT_FILE) as f:
            existing = json.load(f)
    existing_polys = {c["poly"] for c in existing["curves"]}
    print(f"Existing: {len(existing['curves'])} curves")

    new_curves = []
    attempts = 0
    max_attempts = args.count * 20  # expect ~50% smoothness rate

    while len(new_curves) < args.count and attempts < max_attempts:
        attempts += 1
        coeffs = generate_random_quartic(args.max_coeff, basis)
        poly_str = poly_to_str(coeffs, basis)

        if poly_str in existing_polys:
            continue

        if is_likely_smooth(coeffs, basis):
            curve_id = make_id_from_coeffs(coeffs)
            new_curves.append({
                "id": curve_id,
                "poly": poly_str
            })
            existing_polys.add(poly_str)

            if len(new_curves) % 100 == 0:
                print(f"  {len(new_curves)}/{args.count} ({attempts} attempts, "
                      f"{len(new_curves)/attempts*100:.0f}% smooth rate)")

    print(f"\nGenerated {len(new_curves)} new curves ({attempts} attempts, "
          f"{len(new_curves)/attempts*100:.1f}% smooth rate)")

    # Merge and save
    all_curves = existing["curves"] + new_curves
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"curves": all_curves}, f, indent=2, ensure_ascii=False)

    print(f"Total: {len(all_curves)} curves saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
