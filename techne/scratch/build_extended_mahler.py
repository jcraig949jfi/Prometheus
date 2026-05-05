"""Build extended Mahler table by deterministic construction.

Strategy: only use construction families where both the coefficient
sequence AND the resulting M-value are mathematically guaranteed:

1. Cyclotomic polynomials Phi_n for n = 1..40 (M = 1 by construction).
2. Smyth Pisot family x^n - x - 1 for n = 2..30 (M = real root > 1).
3. Pisot family x^n - x^(n-1) - 1 for n = 2..15 (M = real root > 1).
4. Lehmer's polynomial x cyclotomic factor Phi_k for k = 1..15
   (M = LEHMER_CONSTANT exactly, multiplicativity).
5. Smallest Salem polynomial at degree 8 x cyclotomic factors
   (M = 1.28063815627 by multiplicativity).
6. Smyth's extremal x^3-x-1 x cyclotomic factors
   (M = SMYTH_CONSTANT exactly).
7. Existing 21 entries (already in the table; not re-emitted).

We ALSO include a few well-known specific Salem polynomials whose
coefficients are unambiguous in published sources (Boyd 1980 Table 2,
the specific deg-14 small-Mahler entry).
"""
from __future__ import annotations

import sys
import json
sys.path.insert(0, "F:/Prometheus")

import numpy as np
from techne.lib.mahler_measure import mahler_measure


def M_of(asc):
    return float(mahler_measure(list(reversed(asc))))


def asc_mul(a, b):
    arr = np.convolve(np.asarray(a, dtype=np.int64),
                      np.asarray(b, dtype=np.int64))
    return [int(c) for c in arr]


# Cyclotomic polynomial Phi_n by closed-form for small n.
# We compute Phi_n exactly using sympy for safety.
def phi_n_asc(n):
    """Return ascending integer coefficients of Phi_n."""
    from sympy import Poly, symbols, cyclotomic_poly
    x = symbols('x')
    p = cyclotomic_poly(n, x)
    coeffs_desc = Poly(p, x).all_coeffs()  # descending
    return [int(c) for c in reversed(coeffs_desc)]


# Existing 21-entry table to avoid duplicates.
EXISTING_ASC = [
    [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],     # Lehmer
    [1, 1, 1, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, -1, -1, 0, 0, 1, 0, 0, -1, -1, 0, 0, 1],
    [1, 0, 0, 0, -1, 1, -1, 0, 0, 0, 1],
    [1, 1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1, 1],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1],
    [1, 0, -1, 0, 0, 1, 0, 0, -1, 0, 1],
    [1, 0, 0, -1, -1, -1, 0, 0, 1],
    [1, 0, 0, -1, 1, -1, 0, 0, 1],
    [-1, -1, 0, 1],
    [-1, 0, 0, 0, -1, 1],
    [-1, -1, 1],
    [-1, 0, 0, -1, 1],
    [-1, 0, 0, 0, 0, -1, 1],
    [1, 0, -1, -1, -1, 0, 1],
    [1, -1, -1, -1, 1],
    [-1, -1, -1, 1],
    [1, 0, 0, 0, 0, -1, -1, -1, 0, 0, 0, 0, 1],  # Lehmer x Phi_5? — actually deg-12 Lehmer extension
    [1, 0, 0, -1, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 1],
    [1, 1, 1, 1, 1],   # Phi_5
    [1, 1, 1, 1, 1, 1, 1],   # Phi_7
]


def is_dup(asc, existing):
    a = list(asc)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    for e in existing:
        b = list(e)
        while len(b) > 1 and b[-1] == 0:
            b.pop()
        if a == b:
            return True
        if a == [-c for c in b]:  # negation = same poly up to sign
            return True
        # x -> -x flip
        flipped = [c if (i % 2 == 0) else -c for i, c in enumerate(b)]
        if a == flipped:
            return True
    return False


# ---------------------------------------------------------------------------
# Build new entries
# ---------------------------------------------------------------------------
new_entries = []
all_asc_seen = list(EXISTING_ASC)


def add_entry(asc, name, source, salem, smyth, lehmer, deg_min, expected=None):
    """Compute M, check expected (if given), reject if mismatch > 1e-9."""
    if is_dup(asc, all_asc_seen):
        return None
    m = M_of(asc)
    if expected is not None and abs(m - expected) > 1e-9:
        return ("REJECT", name, m, expected)
    entry = {
        "degree": len(asc) - 1,
        "coeffs": list(asc),
        "mahler_measure": m,
        "name": name,
        "salem_class": salem,
        "is_smyth_extremal": smyth,
        "lehmer_witness": False,
        "degree_minimum": deg_min,
        "source": source,
    }
    new_entries.append(entry)
    all_asc_seen.append(list(asc))
    return entry


rejected = []


def try_add(*args, **kwargs):
    res = add_entry(*args, **kwargs)
    if isinstance(res, tuple) and res[0] == "REJECT":
        rejected.append(res)


# --- 1. Cyclotomic polynomials Phi_n -------------------------------------
# All have M = 1 exactly.
for n in range(1, 41):
    asc = phi_n_asc(n)
    if len(asc) <= 1:
        continue  # Phi_1 = x - 1 has degree 1 — we'll include only deg >= 2.
    if len(asc) - 1 < 2:
        continue
    try_add(
        asc, f"Phi_{n} (cyclotomic)",
        f"cyclotomic Phi_{n}", False, False, False, False,
        expected=1.0,
    )

# --- 2. Smyth Pisot family x^n - x - 1 -----------------------------------
# Pisot, non-reciprocal, M = real root > 1.
# Special: n=3 and n=5 attain Smyth's bound (plastic number).
for n in range(2, 31):
    asc = [-1, -1] + [0] * (n - 2) + [1]
    is_smyth = (n == 3 or n == 5)
    is_min = (n == 3)  # plastic IS Smyth's deg-3 minimum
    try_add(
        asc, f"x^{n} - x - 1",
        "Smyth 1971 family (Pisot deg n)",
        False, is_smyth, False, is_min,
    )

# --- 3. Pisot family x^n - x^(n-1) - 1 -----------------------------------
for n in range(2, 16):
    asc = [-1] + [0] * (n - 2) + [-1, 1]
    try_add(
        asc, f"x^{n} - x^{n-1} - 1",
        "Pisot family x^n - x^(n-1) - 1",
        False, False, False, False,
    )

# --- 4. Lehmer's polynomial x Phi_k, M = LEHMER_CONSTANT ------------------
LEHMER_ASC = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_CONST = 1.1762808182599175
for k in range(1, 21):
    phi_k = phi_n_asc(k)
    prod = asc_mul(LEHMER_ASC, phi_k)
    if len(prod) - 1 > 60:
        continue
    try_add(
        prod, f"Lehmer x Phi_{k}",
        f"Lehmer 1933 x cyclotomic Phi_{k}",
        True, False, False, False,
        expected=LEHMER_CONST,
    )

# --- 5. Smyth-extremal x^3-x-1 x Phi_k, M = SMYTH_CONSTANT ---------------
SMYTH_PLASTIC_ASC = [-1, -1, 0, 1]
SMYTH_CONST = 1.3247179572447460
for k in range(1, 16):
    phi_k = phi_n_asc(k)
    prod = asc_mul(SMYTH_PLASTIC_ASC, phi_k)
    if len(prod) - 1 > 30:
        continue
    try_add(
        prod, f"(x^3-x-1) x Phi_{k}",
        f"Smyth 1971 plastic x cyclotomic Phi_{k}",
        False, True, False, False,
        expected=SMYTH_CONST,
    )

# --- 6. Smallest Salem deg-8 polynomial x cyclotomic factors -------------
# x^8 - x^5 - x^4 - x^3 + 1, M = 1.2806381562677662
SALEM8_ASC = [1, 0, 0, -1, -1, -1, 0, 0, 1]
SALEM8_M = 1.2806381562677662
for k in range(1, 11):
    phi_k = phi_n_asc(k)
    prod = asc_mul(SALEM8_ASC, phi_k)
    if len(prod) - 1 > 30:
        continue
    try_add(
        prod, f"Salem8 x Phi_{k}",
        f"Salem deg 8 x cyclotomic Phi_{k}",
        True, False, False, False,
        expected=SALEM8_M,
    )

# --- 7. Smallest Salem deg-12 polynomial x cyclotomic factors ------------
# x^12 + x^11 + x^10 - x^8 - x^7 - x^6 - x^5 - x^4 + x^2 + x + 1
# (asc = [1,1,1,0,-1,-1,-1,-1,-1,0,1,1,1])
SALEM12_ASC = [1, 1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1, 1]
SALEM12_M = 1.2277855586948293
for k in range(1, 9):
    phi_k = phi_n_asc(k)
    prod = asc_mul(SALEM12_ASC, phi_k)
    if len(prod) - 1 > 36:
        continue
    try_add(
        prod, f"Salem12 x Phi_{k}",
        f"Salem deg 12 x cyclotomic Phi_{k}",
        True, False, False, False,
        expected=SALEM12_M,
    )

# --- 8. Smallest Salem deg-14 polynomial x cyclotomic factors ------------
SALEM14_ASC = [1, 0, 0, -1, -1, 0, 0, 1, 0, 0, -1, -1, 0, 0, 1]
SALEM14_M = 1.2000265239873962
for k in range(1, 7):
    phi_k = phi_n_asc(k)
    prod = asc_mul(SALEM14_ASC, phi_k)
    if len(prod) - 1 > 36:
        continue
    try_add(
        prod, f"Salem14 x Phi_{k}",
        f"Salem deg 14 x cyclotomic Phi_{k}",
        True, False, False, False,
        expected=SALEM14_M,
    )

# --- 9. Salem deg-10 #2 (Mossinghoff list) x cyclotomic factors ----------
SALEM10_2 = [1, 0, 0, 0, -1, 1, -1, 0, 0, 0, 1]
SALEM10_2_M = 1.2163916611379395
for k in range(1, 8):
    phi_k = phi_n_asc(k)
    prod = asc_mul(SALEM10_2, phi_k)
    if len(prod) - 1 > 36:
        continue
    try_add(
        prod, f"Salem10#2 x Phi_{k}",
        f"Salem deg 10 (#2) x cyclotomic Phi_{k}",
        True, False, False, False,
        expected=SALEM10_2_M,
    )

# --- 10. Salem deg-6 polynomial x cyclotomic factors ---------------------
SALEM6 = [1, 0, -1, -1, -1, 0, 1]
SALEM6_M = 1.4012683678038971
for k in range(1, 11):
    phi_k = phi_n_asc(k)
    prod = asc_mul(SALEM6, phi_k)
    if len(prod) - 1 > 30:
        continue
    try_add(
        prod, f"Salem6 x Phi_{k}",
        f"Salem deg 6 x cyclotomic Phi_{k}",
        True, False, False, False,
        expected=SALEM6_M,
    )

# --- 11. Tribonacci x Phi_k ---------------------------------------------
# x^3 - x^2 - x - 1, M = 1.8392867552141612
TRIB = [-1, -1, -1, 1]
TRIB_M = 1.8392867552141612
for k in range(1, 11):
    phi_k = phi_n_asc(k)
    prod = asc_mul(TRIB, phi_k)
    if len(prod) - 1 > 30:
        continue
    try_add(
        prod, f"Tribonacci x Phi_{k}",
        f"Tribonacci x cyclotomic Phi_{k}",
        False, False, False, False,
        expected=TRIB_M,
    )

# --- 12. Golden ratio polynomial x Phi_k ---------------------------------
GOLD = [-1, -1, 1]
PHI = 1.6180339887498949
for k in range(1, 11):
    phi_k = phi_n_asc(k)
    prod = asc_mul(GOLD, phi_k)
    if len(prod) - 1 > 30:
        continue
    try_add(
        prod, f"Golden x Phi_{k}",
        f"x^2-x-1 x cyclotomic Phi_{k}",
        False, False, False, False,
        expected=PHI,
    )


print(f"New entries: {len(new_entries)}")
print(f"Rejected: {len(rejected)}")
for r in rejected[:20]:
    print(f"  REJECTED: {r[1]} M_computed={r[2]:.10f} expected={r[3]:.10f}")

# Save for inspection
with open("F:/Prometheus/techne/scratch/extended_entries.json", "w") as f:
    json.dump(new_entries, f, indent=2)
print(f"\nSaved {len(new_entries)} new entries to extended_entries.json")

# Distribution
from collections import Counter
deg_count = Counter(e["degree"] for e in new_entries)
print("\nDegree distribution of NEW entries:")
for d in sorted(deg_count):
    print(f"  deg {d}: {deg_count[d]}")
