"""CAS Layer C — symbolic canonicalization against an identity basis.

For Tink 2 / Tier B cheap-path, the basis is a list of atomic symbols
(`log_omega`, `log_prod_cp`, `log_sha`, `log_tor`, `log_L`). The CAS
check verifies that an expression is a linear combination of these
atoms with constant (atom-independent) coefficients.

Cases:
  - Expression is `0` (or simplifies to constant): CAS marker `constant`
    → basis_projection forced to 1.0.
  - Expression's free symbols are subset of basis_atoms AND it is
    polynomial of total degree ≤ 1 in those atoms with non-symbolic
    coefficients: CAS marker `linear_in_basis(coeffs)` → forced to 1.0.
  - Otherwise: CAS marker `not_in_linear_basis` → fall through to
    Layer B empirical regression.

Future v3 extensions (out of scope for cheap-path):
  - Substitution of known identities (e.g., BSD identity) to detect
    expressions that span the basis after rewriting.
  - Polynomial degree > 1 with basis-atom-only support — which is
    not "novel" because polynomial-in-basis is still derivable from
    basis.
  - Transcendental composition (exp/log) substitution.
"""

from __future__ import annotations

from typing import Optional

import sympy


def cas_canonicalize(
    sympy_expr,
    basis_atoms: list,
) -> tuple[str, Optional[dict]]:
    """Determine whether `sympy_expr` lies in the linear span of `basis_atoms`.

    Returns (marker, details):
      - ("constant", {"value": v}) — expression is a constant
      - ("linear_in_basis", {"coeffs": {atom_name: coeff}}) — expression is linear combo
      - ("not_in_linear_basis", None) — fall through to Layer B
    """
    expanded = sympy.expand(sympy_expr)
    free = expanded.free_symbols

    # Constant case
    if not free:
        return ("constant", {"value": float(expanded)})

    # Non-basis free symbols → not in linear basis
    if not free.issubset(set(basis_atoms)):
        return ("not_in_linear_basis", None)

    # Poly check: linear in basis atoms with constant coefficients
    try:
        poly = sympy.Poly(expanded, *basis_atoms)
    except sympy.PolynomialError:
        # Not a polynomial in basis_atoms (e.g., exp/log composition)
        return ("not_in_linear_basis", None)
    except Exception:
        return ("not_in_linear_basis", None)

    if poly.total_degree() <= 1:
        coeffs = {}
        for atom in basis_atoms:
            c = poly.coeff_monomial(atom)
            if c != 0:
                coeffs[str(atom)] = float(c)
        return ("linear_in_basis", {"coeffs": coeffs})

    # Higher-degree polynomial in basis atoms: still "in basis" semantically
    # because all atoms used are basis atoms — but the relation isn't linear.
    # For Tink 2 cheap-path, treat as in-basis (CAS recognizes basis-atom-only
    # composition); v3+ would need richer handling.
    return ("linear_in_basis", {"coeffs": "polynomial_in_basis_atoms"})


def cas_score_for_candidate(
    sympy_E_A,
    sympy_E_B,
    basis_atoms: list,
) -> dict:
    """Run CAS Layer C on both sub-expressions of a correlation candidate.

    Returns dict with per-side markers and the composed verdict.
    """
    marker_A, details_A = cas_canonicalize(sympy_E_A, basis_atoms)
    marker_B, details_B = cas_canonicalize(sympy_E_B, basis_atoms)

    in_basis_A = marker_A in ("constant", "linear_in_basis")
    in_basis_B = marker_B in ("constant", "linear_in_basis")

    # If either side reduces to in-basis, the candidate's basis_projection
    # is forced to 1.0 with explicit reason.
    if in_basis_A or in_basis_B:
        cas_basis_projection = 1.0
        cas_decided = True
        reduce_to = []
        if in_basis_A:
            reduce_to.append(f"E_A:{marker_A}")
        if in_basis_B:
            reduce_to.append(f"E_B:{marker_B}")
        cas_reduced_to = "; ".join(reduce_to)
    else:
        cas_basis_projection = None  # fall through to Layer B
        cas_decided = False
        cas_reduced_to = None

    return {
        "cas_marker_E_A": marker_A,
        "cas_marker_E_B": marker_B,
        "cas_details_E_A": details_A,
        "cas_details_E_B": details_B,
        "cas_basis_projection": cas_basis_projection,
        "cas_decided": cas_decided,
        "cas_reduced_to": cas_reduced_to,
    }
