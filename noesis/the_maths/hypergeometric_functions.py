"""
Hypergeometric Functions — 2F1, 3F2, Pochhammer symbols, contiguous relations

Connects to: [orthogonal_polynomials, special_functions, combinatorics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "hypergeometric_functions"
OPERATIONS = {}


def pochhammer_symbol(x):
    """Compute (a)_n = a(a+1)...(a+n-1). x=[a, n]. Input: array. Output: scalar."""
    a = float(x[0])
    n = int(x[1])
    if n < 0:
        return np.nan
    if n == 0:
        return 1.0
    result = 1.0
    for i in range(n):
        result *= (a + i)
    return float(result)


OPERATIONS["pochhammer_symbol"] = {
    "fn": pochhammer_symbol,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Pochhammer symbol (rising factorial) (a)_n"
}


def hypergeometric_2f1(x):
    """Compute 2F1(a,b;c;z) via series. x=[a,b,c,z]. Input: array. Output: scalar."""
    a, b, c, z = float(x[0]), float(x[1]), float(x[2]), float(x[3])
    if abs(z) >= 1:
        return np.nan
    n_terms = 100
    result = 0.0
    term = 1.0
    for n in range(n_terms):
        result += term
        term *= (a + n) * (b + n) / ((c + n) * (n + 1)) * z
        if abs(term) < 1e-15:
            break
    return float(result)


OPERATIONS["hypergeometric_2f1"] = {
    "fn": hypergeometric_2f1,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Gauss hypergeometric 2F1(a,b;c;z) via power series"
}


def hypergeometric_1f1(x):
    """Compute 1F1(a;b;z) (Kummer's confluent). x=[a,b,z]. Input: array. Output: scalar."""
    a, b, z = float(x[0]), float(x[1]), float(x[2])
    n_terms = 150
    result = 0.0
    term = 1.0
    for n in range(n_terms):
        result += term
        term *= (a + n) / ((b + n) * (n + 1)) * z
        if abs(term) < 1e-15:
            break
    return float(result)


OPERATIONS["hypergeometric_1f1"] = {
    "fn": hypergeometric_1f1,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Confluent hypergeometric 1F1(a;b;z) via power series"
}


def hypergeometric_0f1(x):
    """Compute 0F1(;b;z). x=[b,z]. Input: array. Output: scalar."""
    b, z = float(x[0]), float(x[1])
    n_terms = 150
    result = 0.0
    term = 1.0
    for n in range(n_terms):
        result += term
        term *= z / ((b + n) * (n + 1))
        if abs(term) < 1e-15:
            break
    return float(result)


OPERATIONS["hypergeometric_0f1"] = {
    "fn": hypergeometric_0f1,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Hypergeometric 0F1(;b;z) via power series"
}


def hypergeometric_series_truncated(x):
    """Truncated hypergeometric series sum_{k=0}^{N} (a)_k z^k / k!. x=[a, z, N]. Input: array. Output: scalar."""
    a = float(x[0])
    z = float(x[1])
    N = int(x[2])
    result = 0.0
    term = 1.0
    for k in range(N + 1):
        result += term
        term *= (a + k) * z / (k + 1)
    return float(result)


OPERATIONS["hypergeometric_series_truncated"] = {
    "fn": hypergeometric_series_truncated,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Truncated hypergeometric 1F0 series to N terms"
}


def gauss_hypergeometric_special(x):
    """Evaluate 2F1 at special values. x=[case_id]. case 1: 2F1(1,1;2;z)=-ln(1-z)/z. Input: array. Output: array."""
    z_vals = np.asarray(x, dtype=np.float64)
    # 2F1(1,1;2;z) = -ln(1-z)/z
    results = np.where(
        np.abs(z_vals) < 1,
        -np.log(1 - z_vals) / np.where(np.abs(z_vals) > 1e-15, z_vals, 1.0),
        np.nan
    )
    return results


OPERATIONS["gauss_hypergeometric_special"] = {
    "fn": gauss_hypergeometric_special,
    "input_type": "array",
    "output_type": "array",
    "description": "Special case 2F1(1,1;2;z) = -ln(1-z)/z"
}


def contiguous_relation_check(x):
    """Check 2F1 contiguous relation: c*F(a,b;c;z) - c*F(a-1,b;c;z) = bz*F(a,b+1;c+1;z). Input: array. Output: scalar."""
    a, b, c, z = float(x[0]), float(x[1]), float(x[2]), float(x[3]) if len(x) >= 4 else (2.0, 3.0, 4.0, 0.5)
    if abs(z) >= 1:
        return np.nan

    def _2f1(a_, b_, c_, z_):
        result = 0.0
        term = 1.0
        for n in range(80):
            result += term
            term *= (a_ + n) * (b_ + n) / ((c_ + n) * (n + 1)) * z_
            if abs(term) < 1e-15:
                break
        return result

    lhs = c * _2f1(a, b, c, z) - c * _2f1(a - 1, b, c, z)
    rhs = b * z * _2f1(a, b + 1, c + 1, z)
    # Return relative error
    denom = max(abs(lhs), abs(rhs), 1e-15)
    return float(abs(lhs - rhs) / denom)


OPERATIONS["contiguous_relation_check"] = {
    "fn": contiguous_relation_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Relative error of 2F1 contiguous relation (should be ~0)"
}


def pfaff_transformation(x):
    """Verify Pfaff transformation: 2F1(a,b;c;z) = (1-z)^(-a) * 2F1(a,c-b;c;z/(z-1)). Input: array. Output: scalar."""
    a, b, c, z = float(x[0]), float(x[1]), float(x[2]), float(x[3]) if len(x) >= 4 else (1.5, 2.5, 3.5, 0.3)
    if abs(z) >= 1:
        return np.nan
    z2 = z / (z - 1)
    if abs(z2) >= 1:
        return np.nan

    def _2f1(a_, b_, c_, z_):
        result = 0.0
        term = 1.0
        for n in range(80):
            result += term
            term *= (a_ + n) * (b_ + n) / ((c_ + n) * (n + 1)) * z_
            if abs(term) < 1e-15:
                break
        return result

    lhs = _2f1(a, b, c, z)
    rhs = (1 - z) ** (-a) * _2f1(a, c - b, c, z2)
    denom = max(abs(lhs), abs(rhs), 1e-15)
    return float(abs(lhs - rhs) / denom)


OPERATIONS["pfaff_transformation"] = {
    "fn": pfaff_transformation,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Relative error of Pfaff transformation (should be ~0)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
