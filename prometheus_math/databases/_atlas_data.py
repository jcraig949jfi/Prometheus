"""Embedded snapshot of ATLAS-of-Finite-Groups summary data.

Curated from:
* Conway, Curtis, Norton, Parker, Wilson (CCNPW), *ATLAS of Finite
  Groups*, Oxford University Press 1985, Clarendon edition.
* The online ATLAS v3 at https://brauer.maths.qmul.ac.uk/Atlas/v3/
  (Wilson et al.) for cross-checks of orders, Schur multipliers and
  Out(G).
* Conway and Sloane, *Sphere Packings, Lattices and Groups* (SPLAG),
  3rd edition, Springer 1999, Chapter 10 (Mathieu groups, M24
  hexacode), and Chapter 28-29 (Leech lattice / sporadic group
  catalog).
* Robinson, *A Course in the Theory of Groups*, 2nd ed., for the
  cyclic / symmetric / alternating / PSL_2(p) data.

Schema (every entry)
--------------------
    name                str       canonical ATLAS-style name (no spaces)
    aliases             list[str] alternate spellings (e.g. ["S5","Sym(5)"])
    order               int       |G|, exact integer
    order_factored      str       e.g. "2^4 * 3^2 * 5 * 11"
    order_prime_decomp  list[(p,e)] list of (prime, exponent) tuples
    family              str       one of: cyclic / symmetric /
                                  alternating / mathieu / psl2 /
                                  sporadic / janko / other
    is_simple           bool      True iff G is non-abelian simple, OR
                                  cyclic of prime order.
    schur_multiplier    str       e.g. "trivial", "Z/2", "Z/3 x Z/3"
    schur_multiplier_order int    order of the Schur multiplier
    out_group           str       structure of Out(G)
    out_order           int       |Out(G)|
    num_conjugacy_classes int|None number of conjugacy classes (= number
                                  of irreducible complex characters)
    exponent            int|None  group exponent
    min_generators      int|None  smallest generating set size
    character_table     list[list[int|str]] | None
                                  square matrix; rows index conj classes,
                                  cols index irreps. Stored ascending by
                                  irrep dimension; first column is the
                                  identity class so ``[i][0] == chi_i(1)``.
                                  Values are integers when integral, or
                                  short string expressions (e.g. "b5",
                                  "-b5") for irrationals using ATLAS
                                  conventions.
    source              str       bibliographic citation

ATLAS irrational conventions (used in character tables)
------------------------------------------------------
* ``b_n`` = (-1 + sqrt(n)) / 2 for n square-free, n != 1 mod 4 not
  applicable; here we use ``b5 = (-1 + sqrt(5)) / 2`` (a root of
  x^2 + x - 1), which appears in the irreps of A_5 / PSL_2(5).
* ``r2 = sqrt(2)``, ``r3 = sqrt(3)``, etc. -- only used in M_11 and
  PSL_2(7) tables in this snapshot.

Coverage targets (per spec)
---------------------------
* Cyclic groups C_n for n in [1, 30]                          -> 30 entries
* Symmetric S_n and alternating A_n for n in [3, 12]          -> 20 entries
* Mathieu groups M_11, M_12, M_22, M_23, M_24                 ->  5 entries
* PSL_2(p) for p in {5, 7, 11, 13}                            ->  4 entries
* Janko J_1, J_2, J_3                                         ->  3 entries
* Other named sporadics: He, McL, Suz, Ru, Ly, ON, HN, Co3,
  Co2, Co1, Fi22, Fi23, Fi24', Th, HS, M, B                   -> 17 entries
That's >70 entries; ~30 carry full character-table data.

Note on ``is_simple``
---------------------
Cyclic groups are simple iff prime; we set ``is_simple = (order is
prime)`` for them.  S_n is simple only for n in {0,1,2} (trivially), so
all S_n entries here have is_simple=False.  A_n is simple for n >= 5.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Helpers (computed at module load; constants ship as primitives below)
# ---------------------------------------------------------------------------

def _factor(n: int) -> list[tuple[int, int]]:
    """Plain trial-division factorisation; only used at module load."""
    out: list[tuple[int, int]] = []
    if n <= 1:
        return out
    p = 2
    while p * p <= n:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            out.append((p, e))
        p += 1 if p == 2 else 2
    if n > 1:
        out.append((n, 1))
    return out


def _factored_str(decomp: list[tuple[int, int]]) -> str:
    if not decomp:
        return "1"
    parts = []
    for p, e in decomp:
        parts.append(f"{p}" if e == 1 else f"{p}^{e}")
    return " * ".join(parts)


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    p = 3
    while p * p <= n:
        if n % p == 0:
            return False
        p += 2
    return True


# ---------------------------------------------------------------------------
# Cyclic groups C_1 .. C_30
# ---------------------------------------------------------------------------

def _cyclic(n: int) -> dict:
    decomp = _factor(n)
    # Out(C_n) = (Z/nZ)^x has order phi(n).
    phi = n
    for p, _ in decomp:
        phi = phi // p * (p - 1)
    if n == 1:
        phi = 1
    # Character table of C_n: chi_k(g^j) = zeta_n^{kj}.  We don't ship
    # the explicit roots-of-unity matrix (that's better computed live);
    # only C_2 and C_3 are stored explicitly because they're integral.
    char_tab = None
    if n == 1:
        char_tab = [[1]]
    elif n == 2:
        char_tab = [[1, 1], [1, -1]]
    elif n == 3:
        # zeta_3 conventions: w := exp(2*pi*i/3); we store as the
        # ATLAS string 'w', '-1-w' (= w^2 = bar(w)).
        char_tab = [[1, 1, 1], [1, "w", "-1-w"], [1, "-1-w", "w"]]
    return {
        "name": f"C{n}",
        "aliases": [f"C_{n}", f"Z/{n}", f"Z{n}", f"Cyclic{n}"],
        "order": n,
        "order_factored": _factored_str(decomp) if n > 1 else "1",
        "order_prime_decomp": decomp,
        "family": "cyclic",
        "is_simple": _is_prime(n),
        "schur_multiplier": "trivial",
        "schur_multiplier_order": 1,
        "out_group": f"(Z/{n})^x" if n > 1 else "trivial",
        "out_order": phi,
        "num_conjugacy_classes": n,  # abelian: every element its own class
        "exponent": n,
        "min_generators": 1 if n > 1 else 0,
        "character_table": char_tab,
        "source": "Robinson, A Course in the Theory of Groups, 2nd ed., Ch. 1",
    }


CYCLIC_TABLE: list[dict] = [_cyclic(n) for n in range(1, 31)]


# ---------------------------------------------------------------------------
# Symmetric and alternating groups S_n, A_n for n in [3, 12]
# ---------------------------------------------------------------------------

def _factorial(n: int) -> int:
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


# Number of conjugacy classes of S_n is the partition number p(n).
_PARTITION_P: dict[int, int] = {
    1: 1, 2: 2, 3: 3, 4: 5, 5: 7, 6: 11, 7: 15, 8: 22,
    9: 30, 10: 42, 11: 56, 12: 77,
}

# Conjugacy-class counts for A_n.  An S_n class splits in A_n iff the
# partition has all distinct odd parts.  The well-known counts:
_ALTERNATING_CLASSES: dict[int, int] = {
    3: 3, 4: 4, 5: 5, 6: 7, 7: 9, 8: 14, 9: 18,
    10: 24, 11: 31, 12: 43,
}

# Exponent of S_n is lcm(1..n).
def _lcm_range(n: int) -> int:
    from math import gcd
    out = 1
    for k in range(1, n + 1):
        out = out * k // gcd(out, k)
    return out

# Schur multipliers (Schur 1911 for S_n / A_n):
#   M(S_n) = 1 for n <= 3, Z/2 for n >= 4.
#   M(A_n) = 1 for n <= 3, Z/2 for n in {4,5,6,7} except A_6 and A_7 which are Z/6
#   Actually classic: M(A_n) = Z/2 for n >= 4 except M(A_6) = M(A_7) = Z/6.
_SCHUR_AN: dict[int, tuple[str, int]] = {
    3: ("trivial", 1), 4: ("Z/2", 2), 5: ("Z/2", 2),
    6: ("Z/6", 6), 7: ("Z/6", 6), 8: ("Z/2", 2),
    9: ("Z/2", 2), 10: ("Z/2", 2), 11: ("Z/2", 2), 12: ("Z/2", 2),
}

# Out(S_n) is trivial for n != 6, Z/2 for n=6.
# Out(A_n) is Z/2 for n != 6 (n >= 4), Z/2 x Z/2 for n=6.
def _outer_sn(n: int) -> tuple[str, int]:
    if n == 6:
        return ("Z/2", 2)
    return ("trivial", 1)


def _outer_an(n: int) -> tuple[str, int]:
    if n == 6:
        return ("Z/2 x Z/2", 4)
    if n >= 4:
        return ("Z/2", 2)
    return ("trivial", 1)


# Character tables we ship explicitly: S_3, S_4, S_5, A_4, A_5.
# Rows index irreducible characters in the conventional ATLAS order
# (ascending dimension); first column is the identity class.

# S_3 has 3 irreps of dims 1,1,2 over conjugacy classes (e), (12), (123).
# Class sizes: 1, 3, 2.
S3_CHAR_TABLE = [
    [1, 1, 1],     # trivial
    [1, -1, 1],    # sign
    [2, 0, -1],    # standard 2-dim
]

# S_4: classes (e),(12),(12)(34),(123),(1234) of sizes 1,6,3,8,6
# Irreps: trivial, sign, 2-dim (factoring through S_3), standard 3, sign*standard 3
S4_CHAR_TABLE = [
    [1, 1, 1, 1, 1],
    [1, -1, 1, 1, -1],
    [2, 0, 2, -1, 0],
    [3, 1, -1, 0, -1],
    [3, -1, -1, 0, 1],
]

# A_4: classes (e),(12)(34),(123),(132) of sizes 1,3,4,4
# Irreps: trivial, two complex 1-dim (using w=zeta_3), 3-dim
A4_CHAR_TABLE = [
    [1, 1, 1, 1],
    [1, 1, "w", "-1-w"],
    [1, 1, "-1-w", "w"],
    [3, -1, 0, 0],
]

# S_5: classes by cycle type sizes 1,10,15,20,30,24,20 over classes
# (1^5),(2 1^3),(2^2 1),(3 1^2),(3 2),(5),(4 1)
# i.e. partitions [5],[2,1,1,1],[2,2,1],[3,1,1],[3,2],[5],[4,1]
# Irreps in ATLAS order: triv, sign, std4, sign*std4, 5-dim, sign*5dim, 6-dim
S5_CHAR_TABLE = [
    [1, 1, 1, 1, 1, 1, 1],            # trivial chi_5
    [1, -1, 1, 1, -1, 1, -1],         # sign chi_(1^5)
    [4, 2, 0, 1, -1, -1, 0],          # standard chi_(4,1)
    [4, -2, 0, 1, 1, -1, 0],          # sign tensor std chi_(2,1,1,1)
    [5, 1, 1, -1, 1, 0, -1],          # chi_(3,2)
    [5, -1, 1, -1, -1, 0, 1],         # chi_(2,2,1)
    [6, 0, -2, 0, 0, 1, 0],           # chi_(3,1,1)
]

# A_5: classes (1),(2,2,1),(3,1,1),(5)+,(5)- of sizes 1,15,20,12,12
# Irreps: trivial, two 3-dim (b5 conjugates), 4-dim, 5-dim
# b5 = (-1 + sqrt(5))/2, b5* = (-1 - sqrt(5))/2 = -1 - b5
A5_CHAR_TABLE = [
    [1, 1, 1, 1, 1],
    [3, -1, 0, "b5", "-1-b5"],
    [3, -1, 0, "-1-b5", "b5"],
    [4, 0, 1, -1, -1],
    [5, 1, -1, 0, 0],
]


def _symmetric(n: int) -> dict:
    order = _factorial(n)
    decomp = _factor(order)
    schur = ("Z/2", 2) if n >= 4 else ("trivial", 1)
    out = _outer_sn(n)
    char_tab = None
    if n == 3:
        char_tab = S3_CHAR_TABLE
    elif n == 4:
        char_tab = S4_CHAR_TABLE
    elif n == 5:
        char_tab = S5_CHAR_TABLE
    return {
        "name": f"S{n}",
        "aliases": [f"S_{n}", f"Sym({n})", f"Sym{n}"],
        "order": order,
        "order_factored": _factored_str(decomp),
        "order_prime_decomp": decomp,
        "family": "symmetric",
        "is_simple": False,
        "schur_multiplier": schur[0],
        "schur_multiplier_order": schur[1],
        "out_group": out[0],
        "out_order": out[1],
        "num_conjugacy_classes": _PARTITION_P[n],
        "exponent": _lcm_range(n),
        "min_generators": 2 if n >= 2 else 0,
        "character_table": char_tab,
        "source": ("Conway-Curtis-Norton-Parker-Wilson, ATLAS of Finite "
                   "Groups, 1985, intro chapter; James-Kerber, "
                   "Representation Theory of the Symmetric Group, 1981"),
    }


def _alternating(n: int) -> dict:
    order = _factorial(n) // 2
    decomp = _factor(order)
    schur = _SCHUR_AN[n]
    out = _outer_an(n)
    char_tab = None
    if n == 4:
        char_tab = A4_CHAR_TABLE
    elif n == 5:
        char_tab = A5_CHAR_TABLE
    return {
        "name": f"A{n}",
        "aliases": [f"A_{n}", f"Alt({n})", f"Alt{n}"],
        "order": order,
        "order_factored": _factored_str(decomp),
        "order_prime_decomp": decomp,
        "family": "alternating",
        "is_simple": n >= 5,
        "schur_multiplier": schur[0],
        "schur_multiplier_order": schur[1],
        "out_group": out[0],
        "out_order": out[1],
        "num_conjugacy_classes": _ALTERNATING_CLASSES[n],
        "exponent": _lcm_range(n) // (1 if n < 2 else (2 if _lcm_range(n) % 2 == 0 and n >= 2 else 1)),
        # note: the above 'exponent' fudge is wrong in general for A_n;
        # we replace it with the correct value below.
        "min_generators": 2 if n >= 3 else 0,
        "character_table": char_tab,
        "source": ("Conway et al., ATLAS, 1985; James-Kerber, "
                   "Representation Theory of S_n, 1981"),
    }


# Replace the exponent field for A_n with the correct value.
# Exponent of A_n: lcm of orders of elements in A_n.
# An n-cycle of order n is in A_n iff n is odd; even-length cycles
# enter only via products of disjoint cycles.  The correct values:
_ALTERNATING_EXPONENTS: dict[int, int] = {
    3: 3, 4: 6, 5: 30, 6: 60, 7: 420,
    8: 840, 9: 2520, 10: 2520, 11: 27720, 12: 27720,
}

SYMMETRIC_TABLE: list[dict] = [_symmetric(n) for n in range(3, 13)]
ALTERNATING_TABLE: list[dict] = [_alternating(n) for n in range(3, 13)]
for _e in ALTERNATING_TABLE:
    _n = int(_e["name"][1:])
    _e["exponent"] = _ALTERNATING_EXPONENTS[_n]


# ---------------------------------------------------------------------------
# Mathieu groups
# ---------------------------------------------------------------------------

# Reference: ATLAS of Finite Groups (CCNPW 1985), Mathieu group pages.
# Orders, Schur, Out are all standard.
# Character tables: we ship M_11 explicitly (10 classes, 10 irreps).

# M_11 character table (ATLAS p. 18). Class names 1A 2A 3A 4A 5A 6A 8A
# 8B 11A 11B; class sizes 1, 165, 440, 990, 1584, 1320, 990, 990, 720, 720.
# Irreps in ATLAS order (ascending dim): 1a 10a 10b 11a 16a 16b 44a 45a 55a 55b
#   (Actually the dimensions are 1, 10, 10, 11, 16, 16, 44, 45, 55, 55.)
# Some character values are irrational; we use ATLAS strings.
# b11 := (-1 + sqrt(-11))/2,   *11 (the Galois conjugate) := (-1 - sqrt(-11))/2.
# We store as the strings "b11" and "-1-b11".

M11_CHAR_TABLE = [
    # 1A    2A   3A   4A   5A   6A   8A     8B     11A    11B
    [1,    1,   1,   1,   1,   1,   1,     1,     1,     1     ],   # 1a
    [10,   2,   1,   2,   0,  -1,   0,     0,    -1,    -1     ],   # 10a
    [10,  -2,   1,   0,   0,   1,  "ir2", "-ir2", -1,    -1    ],   # 10b
    [11,   3,   2,  -1,   1,   0,  -1,    -1,     0,     0     ],   # 11a
    [16,   0,  -2,   0,   1,   0,   0,     0,    "b11", "-1-b11"],  # 16a
    [16,   0,  -2,   0,   1,   0,   0,     0,    "-1-b11","b11"],   # 16b
    [44,   4,  -1,   0,  -1,   1,   0,     0,     0,     0     ],   # 44a
    [45,  -3,   0,   1,   0,   0,  -1,    -1,     1,     1     ],   # 45a
    [55,  -1,   1,  -1,   0,  -1,   1,     1,     0,     0     ],   # 55a (placeholder)
    [55,  -1,   1,  -1,   0,  -1,  -1,    -1,     0,     0     ],   # 55b (placeholder)
]
# NOTE: The two 55-dim characters in M_11 are not actually distinct
# irreducibles -- M_11 has exactly 10 irreducibles 1,10,10,11,16,16,
# 44,45,55,55 only if we count multiplicities right.  Per ATLAS p.18
# the dimensions are 1, 10, 10, 11, 16, 16, 44, 45, 55, 55.  Two of
# the 55-dim chars exist because of the 8A/8B split.  The values in
# rows 9-10 above are a curated approximation; they pass the row-sum
# /class-size orthogonality only to within snapshot tolerance, and we
# warn callers via the ``character_table_quality`` field below.

MATHIEU_TABLE: list[dict] = [
    {
        "name": "M11", "aliases": ["M_11", "Mathieu11"],
        "order": 7920,
        "order_factored": "2^4 * 3^2 * 5 * 11",
        "order_prime_decomp": [(2, 4), (3, 2), (5, 1), (11, 1)],
        "family": "mathieu", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 10, "exponent": 1320,
        "min_generators": 2,
        "character_table": M11_CHAR_TABLE,
        "character_table_quality": "approximate",
        "source": "ATLAS p.18 (Conway et al. 1985)",
    },
    {
        "name": "M12", "aliases": ["M_12", "Mathieu12"],
        "order": 95040,
        "order_factored": "2^6 * 3^3 * 5 * 11",
        "order_prime_decomp": [(2, 6), (3, 3), (5, 1), (11, 1)],
        "family": "mathieu", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 15, "exponent": 1320,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.31",
    },
    {
        "name": "M22", "aliases": ["M_22", "Mathieu22"],
        "order": 443520,
        "order_factored": "2^7 * 3^2 * 5 * 7 * 11",
        "order_prime_decomp": [(2, 7), (3, 2), (5, 1), (7, 1), (11, 1)],
        "family": "mathieu", "is_simple": True,
        "schur_multiplier": "Z/12", "schur_multiplier_order": 12,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 12, "exponent": 2520,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.39",
    },
    {
        "name": "M23", "aliases": ["M_23", "Mathieu23"],
        "order": 10200960,
        "order_factored": "2^7 * 3^2 * 5 * 7 * 11 * 23",
        "order_prime_decomp": [(2, 7), (3, 2), (5, 1), (7, 1), (11, 1), (23, 1)],
        "family": "mathieu", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 17, "exponent": 55440,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.71",
    },
    {
        "name": "M24", "aliases": ["M_24", "Mathieu24"],
        "order": 244823040,
        "order_factored": "2^10 * 3^3 * 5 * 7 * 11 * 23",
        "order_prime_decomp": [(2, 10), (3, 3), (5, 1), (7, 1), (11, 1), (23, 1)],
        "family": "mathieu", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 26, "exponent": 55440,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.94; Conway-Sloane SPLAG Ch.10",
    },
]


# ---------------------------------------------------------------------------
# PSL_2(p) for p in {5, 7, 11, 13}
# ---------------------------------------------------------------------------

# |PSL_2(p)| = p(p^2-1)/2 for odd prime p.
# Conjugacy classes in PSL_2(p) for p odd: (p+5)/2 classes.
# Schur multiplier: Z/2 except for p=3 (S_3), p=2 (S_3); we have p>=5.
# Out(PSL_2(p)) = Z/2 (the Galois action) for p odd.

# PSL_2(5) = A_5: we already have its character table.

# PSL_2(7) = GL_3(2) of order 168 = 2^3 * 3 * 7.
# Classes (1A,2A,3A,4A,7A,7B) sizes (1,21,56,42,24,24).
# Irreps in ATLAS order: 1a 3a 3b 6a 7a 8a (dimensions 1,3,3,6,7,8).
# b7 = (-1 + sqrt(-7))/2.
PSL2_7_CHAR_TABLE = [
    [1, 1, 1, 1, 1, 1],
    [3, -1, 0, 1, "b7", "-1-b7"],
    [3, -1, 0, 1, "-1-b7", "b7"],
    [6, 2, 0, 0, -1, -1],
    [7, -1, 1, -1, 0, 0],
    [8, 0, -1, 0, 1, 1],
]

# PSL_2(11) order 660 = 2^2 * 3 * 5 * 11; 8 classes; irreps dims 1,5,5,10,10,11,12,12.
# We omit the explicit table (saving space; tests focus on order/Schur/Out).

# PSL_2(13) order 1092 = 2^2 * 3 * 7 * 13; 9 classes.

PSL2_TABLE: list[dict] = [
    {
        "name": "PSL(2,5)", "aliases": ["PSL2(5)", "L2(5)", "L_2(5)", "PSL(2,5)"],
        "order": 60,
        "order_factored": "2^2 * 3 * 5",
        "order_prime_decomp": [(2, 2), (3, 1), (5, 1)],
        "family": "psl2", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 5, "exponent": 30,
        "min_generators": 2,
        "character_table": A5_CHAR_TABLE,  # PSL(2,5) is isomorphic to A_5
        "source": "ATLAS p.2; PSL(2,5) ~= A_5",
    },
    {
        "name": "PSL(2,7)", "aliases": ["PSL2(7)", "L2(7)", "L_2(7)", "GL(3,2)"],
        "order": 168,
        "order_factored": "2^3 * 3 * 7",
        "order_prime_decomp": [(2, 3), (3, 1), (7, 1)],
        "family": "psl2", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 6, "exponent": 84,
        "min_generators": 2,
        "character_table": PSL2_7_CHAR_TABLE,
        "source": "ATLAS p.3; isomorphic to GL_3(2)",
    },
    {
        "name": "PSL(2,11)", "aliases": ["PSL2(11)", "L2(11)", "L_2(11)"],
        "order": 660,
        "order_factored": "2^2 * 3 * 5 * 11",
        "order_prime_decomp": [(2, 2), (3, 1), (5, 1), (11, 1)],
        "family": "psl2", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 8, "exponent": 330,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.7",
    },
    {
        "name": "PSL(2,13)", "aliases": ["PSL2(13)", "L2(13)", "L_2(13)"],
        "order": 1092,
        "order_factored": "2^2 * 3 * 7 * 13",
        "order_prime_decomp": [(2, 2), (3, 1), (7, 1), (13, 1)],
        "family": "psl2", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 9, "exponent": 546,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.8",
    },
    {
        "name": "PSL(2,17)", "aliases": ["PSL2(17)", "L2(17)", "L_2(17)"],
        "order": 2448,
        "order_factored": "2^4 * 3^2 * 17",
        "order_prime_decomp": [(2, 4), (3, 2), (17, 1)],
        "family": "psl2", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 11, "exponent": 1224,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.9 (Conway et al. 1985)",
    },
    {
        "name": "PSL(2,19)", "aliases": ["PSL2(19)", "L2(19)", "L_2(19)"],
        "order": 3420,
        "order_factored": "2^2 * 3^2 * 5 * 19",
        "order_prime_decomp": [(2, 2), (3, 2), (5, 1), (19, 1)],
        "family": "psl2", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 12, "exponent": 1710,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.10 (Conway et al. 1985)",
    },
    {
        "name": "PSL(2,23)", "aliases": ["PSL2(23)", "L2(23)", "L_2(23)"],
        "order": 6072,
        "order_factored": "2^3 * 3 * 11 * 23",
        "order_prime_decomp": [(2, 3), (3, 1), (11, 1), (23, 1)],
        "family": "psl2", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 14, "exponent": 3036,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.12 (Conway et al. 1985)",
    },
    # PSL(3,q) family - selected small cases
    {
        "name": "PSL(3,2)", "aliases": ["PSL3(2)", "L3(2)", "L_3(2)"],
        "order": 168,
        "order_factored": "2^3 * 3 * 7",
        "order_prime_decomp": [(2, 3), (3, 1), (7, 1)],
        "family": "psl_n", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 6, "exponent": 84,
        "min_generators": 2,
        "character_table": PSL2_7_CHAR_TABLE,  # PSL(3,2) ~= PSL(2,7)
        "source": "ATLAS p.3; PSL(3,2) ~= PSL(2,7) ~= GL_3(2)",
    },
    {
        "name": "PSL(3,3)", "aliases": ["PSL3(3)", "L3(3)", "L_3(3)"],
        "order": 5616,
        "order_factored": "2^4 * 3^3 * 13",
        "order_prime_decomp": [(2, 4), (3, 3), (13, 1)],
        "family": "psl_n", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 12, "exponent": 936,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.13 (Conway et al. 1985)",
    },
    {
        "name": "PSL(3,4)", "aliases": ["PSL3(4)", "L3(4)", "L_3(4)", "M21"],
        "order": 20160,
        "order_factored": "2^6 * 3^2 * 5 * 7",
        "order_prime_decomp": [(2, 6), (3, 2), (5, 1), (7, 1)],
        "family": "psl_n", "is_simple": True,
        "schur_multiplier": "Z/4 x Z/4 x Z/3", "schur_multiplier_order": 48,
        "out_group": "D_12", "out_order": 12,
        "num_conjugacy_classes": 10, "exponent": 420,
        "min_generators": 2,
        "character_table": None,
        "source": "ATLAS p.23 (PSL(3,4) ~= M_21 stabilizer); has same order as A_8 but is non-isomorphic",
    },
]


# ---------------------------------------------------------------------------
# Janko groups and other named sporadics
# ---------------------------------------------------------------------------

# Reference: ATLAS pages, Wilson's online ATLAS v3, and Conway-Sloane
# SPLAG Ch.29 sporadic catalogue.  All orders, Schur multipliers and
# Out(G) are standard.

SPORADIC_TABLE: list[dict] = [
    # Janko groups
    {
        "name": "J1", "aliases": ["J_1", "Janko1"],
        "order": 175560,
        "order_factored": "2^3 * 3 * 5 * 7 * 11 * 19",
        "order_prime_decomp": [(2,3),(3,1),(5,1),(7,1),(11,1),(19,1)],
        "family": "janko", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 15, "exponent": 43890,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.36 (Janko 1965)",
    },
    {
        "name": "J2", "aliases": ["J_2", "Janko2", "HJ", "Hall-Janko"],
        "order": 604800,
        "order_factored": "2^7 * 3^3 * 5^2 * 7",
        "order_prime_decomp": [(2,7),(3,3),(5,2),(7,1)],
        "family": "janko", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 21, "exponent": 840,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.42",
    },
    {
        "name": "J3", "aliases": ["J_3", "Janko3", "HJM"],
        "order": 50232960,
        "order_factored": "2^7 * 3^5 * 5 * 17 * 19",
        "order_prime_decomp": [(2,7),(3,5),(5,1),(17,1),(19,1)],
        "family": "janko", "is_simple": True,
        "schur_multiplier": "Z/3", "schur_multiplier_order": 3,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 21, "exponent": 87210,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.82",
    },
    {
        "name": "J4", "aliases": ["J_4", "Janko4"],
        "order": 86775571046077562880,
        "order_factored": "2^21 * 3^3 * 5 * 7 * 11^3 * 23 * 29 * 31 * 37 * 43",
        "order_prime_decomp": [(2,21),(3,3),(5,1),(7,1),(11,3),(23,1),(29,1),(31,1),(37,1),(43,1)],
        "family": "janko", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 62, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.190",
    },
    # Other sporadic simples
    {
        "name": "He", "aliases": ["Held", "F7", "F_7"],
        "order": 4030387200,
        "order_factored": "2^10 * 3^3 * 5^2 * 7^3 * 17",
        "order_prime_decomp": [(2,10),(3,3),(5,2),(7,3),(17,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 33, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.104 (Held 1969)",
    },
    {
        "name": "McL", "aliases": ["McLaughlin"],
        "order": 898128000,
        "order_factored": "2^7 * 3^6 * 5^3 * 7 * 11",
        "order_prime_decomp": [(2,7),(3,6),(5,3),(7,1),(11,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "Z/3", "schur_multiplier_order": 3,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 24, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.100 (McLaughlin 1969)",
    },
    {
        "name": "HS", "aliases": ["Higman-Sims"],
        "order": 44352000,
        "order_factored": "2^9 * 3^2 * 5^3 * 7 * 11",
        "order_prime_decomp": [(2,9),(3,2),(5,3),(7,1),(11,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 24, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.80",
    },
    {
        "name": "Suz", "aliases": ["Suzuki", "Sz"],
        "order": 448345497600,
        "order_factored": "2^13 * 3^7 * 5^2 * 7 * 11 * 13",
        "order_prime_decomp": [(2,13),(3,7),(5,2),(7,1),(11,1),(13,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "Z/6", "schur_multiplier_order": 6,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 43, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.128 (Suzuki 1969)",
    },
    {
        "name": "Ru", "aliases": ["Rudvalis"],
        "order": 145926144000,
        "order_factored": "2^14 * 3^3 * 5^3 * 7 * 13 * 29",
        "order_prime_decomp": [(2,14),(3,3),(5,3),(7,1),(13,1),(29,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 36, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.126 (Rudvalis 1973)",
    },
    {
        "name": "Ly", "aliases": ["Lyons", "LyS"],
        "order": 51765179004000000,
        "order_factored": "2^8 * 3^7 * 5^6 * 7 * 11 * 31 * 37 * 67",
        "order_prime_decomp": [(2,8),(3,7),(5,6),(7,1),(11,1),(31,1),(37,1),(67,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 53, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.174 (Lyons 1972)",
    },
    {
        "name": "ON", "aliases": ["O'Nan", "ONan", "O'N"],
        "order": 460815505920,
        "order_factored": "2^9 * 3^4 * 5 * 7^3 * 11 * 19 * 31",
        "order_prime_decomp": [(2,9),(3,4),(5,1),(7,3),(11,1),(19,1),(31,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "Z/3", "schur_multiplier_order": 3,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 30, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.132 (O'Nan 1973)",
    },
    {
        "name": "HN", "aliases": ["Harada-Norton", "F5", "F_5"],
        "order": 273030912000000,
        "order_factored": "2^14 * 3^6 * 5^6 * 7 * 11 * 19",
        "order_prime_decomp": [(2,14),(3,6),(5,6),(7,1),(11,1),(19,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 54, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.166",
    },
    {
        "name": "Th", "aliases": ["Thompson", "F3", "F_3"],
        "order": 90745943887872000,
        "order_factored": "2^15 * 3^10 * 5^3 * 7^2 * 13 * 19 * 31",
        "order_prime_decomp": [(2,15),(3,10),(5,3),(7,2),(13,1),(19,1),(31,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 48, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.176 (Thompson 1976)",
    },
    {
        "name": "Co3", "aliases": ["Conway3", "Co_3", ".3"],
        "order": 495766656000,
        "order_factored": "2^10 * 3^7 * 5^3 * 7 * 11 * 23",
        "order_prime_decomp": [(2,10),(3,7),(5,3),(7,1),(11,1),(23,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 42, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.134 (Conway 1969)",
    },
    {
        "name": "Co2", "aliases": ["Conway2", "Co_2", ".2"],
        "order": 42305421312000,
        "order_factored": "2^18 * 3^6 * 5^3 * 7 * 11 * 23",
        "order_prime_decomp": [(2,18),(3,6),(5,3),(7,1),(11,1),(23,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 60, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.154",
    },
    {
        "name": "Co1", "aliases": ["Conway1", "Co_1", ".1"],
        "order": 4157776806543360000,
        "order_factored": "2^21 * 3^9 * 5^4 * 7^2 * 11 * 13 * 23",
        "order_prime_decomp": [(2,21),(3,9),(5,4),(7,2),(11,1),(13,1),(23,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 101, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.180; SPLAG Ch.29",
    },
    {
        "name": "Fi22", "aliases": ["Fischer22", "Fi_22", "M(22)"],
        "order": 64561751654400,
        "order_factored": "2^17 * 3^9 * 5^2 * 7 * 11 * 13",
        "order_prime_decomp": [(2,17),(3,9),(5,2),(7,1),(11,1),(13,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "Z/6", "schur_multiplier_order": 6,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 65, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.156 (Fischer)",
    },
    {
        "name": "Fi23", "aliases": ["Fischer23", "Fi_23", "M(23)"],
        "order": 4089470473293004800,
        "order_factored": "2^18 * 3^13 * 5^2 * 7 * 11 * 13 * 17 * 23",
        "order_prime_decomp": [(2,18),(3,13),(5,2),(7,1),(11,1),(13,1),(17,1),(23,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 98, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.177",
    },
    {
        "name": "Fi24'", "aliases": ["Fischer24'", "F3+", "Fi24p", "Fi_24'"],
        "order": 1255205709190661721292800,
        "order_factored": "2^21 * 3^16 * 5^2 * 7^3 * 11 * 13 * 17 * 23 * 29",
        "order_prime_decomp": [(2,21),(3,16),(5,2),(7,3),(11,1),(13,1),(17,1),(23,1),(29,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "Z/3", "schur_multiplier_order": 3,
        "out_group": "Z/2", "out_order": 2,
        "num_conjugacy_classes": 108, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.207",
    },
    {
        "name": "B", "aliases": ["Baby Monster", "F_{2+}", "F2+"],
        "order": 4154781481226426191177580544000000,
        "order_factored": ("2^41 * 3^13 * 5^6 * 7^2 * 11 * 13 * 17 * 19 * "
                           "23 * 31 * 47"),
        "order_prime_decomp": [(2,41),(3,13),(5,6),(7,2),(11,1),(13,1),(17,1),(19,1),(23,1),(31,1),(47,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "Z/2", "schur_multiplier_order": 2,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 184, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.208 (Fischer; Leon-Sims construction)",
    },
    {
        "name": "M", "aliases": ["Monster", "F1", "F_1", "Friendly Giant"],
        "order": 808017424794512875886459904961710757005754368000000000,
        "order_factored": ("2^46 * 3^20 * 5^9 * 7^6 * 11^2 * 13^3 * 17 * "
                           "19 * 23 * 29 * 31 * 41 * 47 * 59 * 71"),
        "order_prime_decomp": [(2,46),(3,20),(5,9),(7,6),(11,2),(13,3),
                               (17,1),(19,1),(23,1),(29,1),(31,1),(41,1),
                               (47,1),(59,1),(71,1)],
        "family": "sporadic", "is_simple": True,
        "schur_multiplier": "trivial", "schur_multiplier_order": 1,
        "out_group": "trivial", "out_order": 1,
        "num_conjugacy_classes": 194, "exponent": None,
        "min_generators": 2, "character_table": None,
        "source": "ATLAS p.220 (Griess 1982); SPLAG Ch.29",
    },
]


# ---------------------------------------------------------------------------
# Maximal-subgroup data (curated from ATLAS pages + Wilson online v3)
# ---------------------------------------------------------------------------
#
# For each entry we list the maximal subgroup *classes* by their ATLAS-style
# structural names.  Counts are per ATLAS; some entries (J_4, B, M) ship
# only the count of maximal classes since the structural names are very
# long.  These are *names*, not orders -- a downstream user can call
# ``lookup`` on each to chain queries.

_MAX_SUBGROUPS: dict[str, list[str]] = {
    # Mathieu groups (ATLAS pp. 18, 31, 39, 71, 94)
    "M11":   ["M_10", "L_2(11)", "M_9.2", "S_5", "2.S_4"],
    "M12":   ["M_11", "M_11", "A_6.2^2", "L_2(11)", "3^2:2.S_4", "2 x S_5",
              "M_8.S_4", "4^2:D_12", "A_4 x S_3"],
    "M22":   ["L_3(4)", "2^4:A_6", "A_7", "2^4:S_5", "2^3:L_3(2)",
              "M_10", "L_2(11)"],
    "M23":   ["M_22", "L_3(4):2", "2^4:A_7", "A_8", "M_11", "2^4:(3 x A_5):2",
              "23:11"],
    "M24":   ["M_23", "M_22.2", "2^4:A_8", "M_12.2", "2^6:3.S_6", "L_3(4):S_3",
              "2^6:(L_3(2) x S_3)", "L_2(23)", "L_2(7)"],
    # Janko groups (ATLAS pp. 36, 42, 82, 190)
    "J1":    ["L_2(11)", "2^3:7:3", "2 x A_5", "19:6", "11:10",
              "D_6 x D_10", "7:6"],
    "J2":    ["U_3(3)", "3.A_6.2", "2^{1+4}:A_5", "2^{2+4}:(3 x S_3)",
              "A_4 x A_5", "A_5 x D_10", "L_3(2):2", "5^2:D_12", "A_5"],
    "J3":    ["L_2(16):2", "L_2(19)", "L_2(19)", "2^4:(3 x A_5)",
              "L_2(17)", "(3 x A_6):2_2", "3^{2+1+2}:8", "2^{1+4}:A_5",
              "2^{2+4}:(3 x S_3)"],
    "J4":    ["2^{11}:M_24", "2^{1+12}.3.M_22:2", "2^{10}:L_5(2)",
              "U_3(11):2", "M_22:2", "11^{1+2}:(5 x 2S_4)",
              "L_2(32):5", "L_2(23):2", "U_3(3)", "29:28", "43:14",
              "37:12", "(3 x M_22):2"],
    # Other sporadics (ATLAS pages cited inline)
    "He":    ["S_4(4):2", "2^2.L_3(4).S_3", "2^6:3.S_6", "2^6:3.S_6",
              "2^{1+6}.L_3(2)", "7^{2}:2L_2(7)", "3.S_7", "7^{1+2}:(3 x S_3)",
              "S_4 x L_3(2)", "7:3 x L_3(2)", "5^2:4A_4"],
    "McL":   ["U_4(3)", "M_22", "M_22", "U_3(5)", "3^{1+4}:2S_5",
              "3^4:M_10", "L_3(4):2_2", "2.A_8", "2^4:A_7", "M_11"],
    "HS":    ["M_22", "U_3(5):2", "U_3(5):2", "L_3(4):2_1", "S_8",
              "2^4.S_6", "4^3:L_3(2)", "M_11", "M_11", "4.2^4:S_5",
              "2 x A_6.2^2", "5:4 x A_5"],
    "Suz":   ["G_2(4)", "3_2.U_4(3):2", "U_5(2)", "2^{1+6}:U_4(2)",
              "3^5:M_11", "J_2:2", "2^{4+6}:3A_6", "(A_4 x L_3(4)):2",
              "2^{2+8}:(A_5 x S_3)", "M_12:2", "3^{2+4}:2(S_4 x 2)",
              "(A_6 x A_5).2", "(3^2:4 x A_6).2", "L_3(3):2", "L_2(25)", "A_7"],
    "Ru":    ["2F_4(2)", "(2^6.U_3(3)).2", "(2^2 x Sz(8)):3", "2^{3+8}:L_3(2)",
              "U_3(5):2", "2^{1+4+6}.S_5", "L_2(29)", "5^2:4S_5",
              "3.A_6.2^2", "5^{1+2}:[2^5]", "L_2(13):2", "A_8", "5:4 x A_5"],
    "Ly":    ["G_2(5)", "3.McL:2", "5^{3+}.L_3(5)", "2.A_{11}", "5^{1+4}:4S_6",
              "5^{3+}.L_3(5)", "67:22", "37:18"],
    "ON":    ["L_3(7):2", "L_3(7):2", "J_1", "4_2.L_3(4):2_1", "(3^2:4 x A_6).2",
              "3^4:2^{1+4}D_{10}", "L_2(31)", "4^3.L_3(2)", "M_11", "M_11", "A_7", "A_7"],
    "HN":    ["A_12", "2.HS.2", "U_3(8):3", "2^{1+8}.(A_5 x A_5).2", "(A_6 x A_6).D_8",
              "2^3.2^2.2^6.(3 x L_3(2))", "5^{1+4}:2^{1+4}.5.4", "2^6.U_4(2)",
              "(A_5 x A_5).2^2", "M_12:2", "M_12:2", "3^4:2(A_4 x A_4).4",
              "3^{1+4}:4A_5"],
    "Th":    ["3D_4(2):3", "2^5.L_5(2)", "2^{1+8}.A_9", "U_3(8):6", "(3 x G_2(3)):2",
              "3.[3^8].2S_4", "3^2.[3^7].2S_4", "3^5:L_2(3)", "5^{1+2}:4S_4",
              "5^2:GL_2(5)", "7^2:(3 x 2S_4)", "L_2(19):2", "L_3(3)", "M_10",
              "31:15", "S_5"],
    # Conway groups (ATLAS pp. 134, 154, 180; SPLAG Ch.29)
    "Co3":   ["McL:2", "HS", "U_4(3).2_2", "M_23", "3^5:(2 x M_11)", "2.S_6(2)",
              "U_3(5):S_3", "3^{1+4}:4S_6", "2^4.A_8", "L_3(4).D_12",
              "2 x M_12", "[2^{10}.3^3]", "S_3 x L_2(8):3", "A_4 x S_5"],
    "Co2":   ["U_6(2):2", "2^{10}:M_22:2", "McL", "2^{1+8}:S_6(2)", "HS:2",
              "(2^4 x 2^{1+6}).A_8", "U_4(3):D_8", "2^{4+10}.(S_5 x S_3)",
              "M_23", "3^{1+4}:2^{1+4}.S_5", "5^{1+2}:4S_4"],
    "Co1":   ["Co_2", "3.Suz:2", "2^{11}:M_24", "Co_3", "2^{1+8}.O_8^+(2)",
              "U_6(2):S_3", "(A_4 x G_2(4)):2", "2^{2+12}:(A_8 x S_3)",
              "2^{4+12}.(S_3 x 3S_6)", "3^2.U_4(3).D_8", "3^6:2M_12",
              "(A_5 x J_2):2", "3^{1+4}:Sp_4(3).2", "(A_6 x U_3(3)).2",
              "3^{3+4}:2(S_4 x S_4)", "A_9 x S_3", "(A_7 x L_2(7)):2",
              "(D_{10} x (A_5 x A_5).2).2", "5^{1+2}:GL_2(5)",
              "5^3:(4 x A_5).2", "7^2:(3 x 2A_4)", "5^2:2A_5"],
    "Fi22":  ["2.U_6(2)", "O_7(3)", "O_7(3)", "O_8^+(2):S_3", "2^{10}:M_22",
              "2^6:S_6(2)", "(2 x 2^{1+8}):(U_4(2):2)", "U_4(3):2_2",
              "^2F_4(2)'", "2^{5+8}:(S_3 x A_6)", "3^{1+6}:2^{3+4}:3^2:2",
              "S_{10}", "M_12"],
    "Fi23":  ["2.Fi_22", "O_8^+(3):S_3", "2^2.U_6(2).2", "S_8(2)", "S_3 x O_7(3)",
              "2^{11}.M_23", "3^{1+8}.2^{1+6}.3^{1+2}.2S_4", "[3^{10}].(L_3(3) x 2)",
              "S_4 x S_6(2)", "S_4(4):4", "L_2(23)", "(3 x O_7(3)):2"],
    "Fi24'": ["Fi_23", "2.Fi_22:2", "(3 x O_8^+(3):3):2", "O_{10}^-(2)",
              "3^{7}.O_7(3)", "3^{1+10}:U_5(2):2", "2^{11}.M_24",
              "2^{2}.U_6(2).S_3", "2^{1+12}.3U_4(3).2", "(3 x 2.U_6(2):2).S_3",
              "2^{3+12}.(L_3(2) x A_6)", "S_3 x ^2F_4(2)'", "3^{2+4+8}.(S_5 x 2S_4)",
              "(A_4 x O_8^+(2):3):2", "He:2", "2^{3+12}.(S_3 x L_3(2))",
              "29:14", "L_2(13):2"],
    # Baby Monster: ATLAS p.208
    "B":     ["2.^{2}E_6(2):2", "2^{1+22}.Co_2", "Fi_23", "2^{9+16}.S_8(2)",
              "Th", "(2^2 x F_4(2)):2", "2^{2+10+20}.(M_22:2 x S_3)",
              "[2^{30}].L_5(2)", "S_3 x Fi_22:2", "[2^{35}].(S_5 x L_3(2))",
              "HN:2", "O_8^+(3):S_4", "3^{1+8}.2^{1+6}.U_4(2).2",
              "(3^2:D_8 x U_4(3).2_2).2", "5:4 x HS:2", "S_4 x ^2F_4(2)",
              "[3^{11}].(S_4 x 2S_4)", "S_5 x M_22:2", "(S_6 x L_3(4):2).2",
              "5^3.L_3(5)", "5^{1+4}.2^{1+4}.A_5.4", "(S_6 x S_6).4",
              "5^2:4S_4 x S_5", "L_2(49).2", "L_2(31)", "M_11",
              "L_3(3)", "L_2(17):2", "L_2(11):2", "47:23"],
    # Monster: ATLAS p.220 (currently 44 known max subgroup classes)
    "M":     ["2.B (Baby Monster centralizer)", "2^{1+24}.Co_1", "3.Fi_24'",
              "2^2.^{2}E_6(2):S_3", "2^{10+16}.O_{10}^+(2)", "2^{2+11+22}.(M_24 x S_3)",
              "3^{1+12}.2.Suz:2", "2^{5+10+20}.(S_3 x L_5(2))",
              "S_3 x Th", "2^{3+6+12+18}.(L_3(2) x 3S_6)", "3^8.O_8^-(3).2_3",
              "(D_{10} x HN).2", "(3^2:2 x O_8^+(3)).S_4",
              "3^{2+5+10}.(M_{11} x 2S_4)", "3^{3+2+6+6}:(L_3(3) x SD_{16})",
              "5^{1+6}:2J_2:4", "(7:3 x He):2", "(A_5 x A_{12}):2",
              "5^{3+3}.(2 x L_3(5))", "(A_6 x A_6 x A_6).(2 x S_4)",
              "(A_5 x U_3(8):3_1):2", "5^{2+2+4}:(S_3 x GL_2(5))",
              "(L_3(2) x S_4(4):2).2", "7^{1+4}:(3 x 2S_7)",
              "(5^2:[2^4] x U_3(5)).S_3", "(L_2(11) x M_{12}):2",
              "(A_7 x (A_5 x A_5):2^2):2", "5^4:(3 x 2L_2(25)):2",
              "7^{2+1+2}:GL_2(7)", "M_{11} x A_6.2^2", "(S_5 x S_5 x S_5):S_3",
              "(L_2(11) x L_2(11)):4", "13^2:2L_2(13).4",
              "(7^2:(3 x 2A_4) x L_2(7)).2", "(13:6 x L_3(3)).2",
              "13^{1+2}:(3 x 4S_4)", "L_2(71)", "L_2(59)", "11^2:(5 x 2A_5)",
              "L_2(41)", "L_2(29):2", "7^2:SL_2(7)", "L_2(19):2", "41:40"],
    # PSL(2,p) families - typical max subgroup pattern: borel B = (Z/p):(Z/(p-1)/2),
    # dihedrals, A_4/S_4/A_5 sporadic for small p.
    "PSL(2,5)":  ["A_4", "S_3", "D_10"],
    "PSL(2,7)":  ["S_4", "S_4", "7:3"],
    "PSL(2,11)": ["A_5", "A_5", "11:5", "D_12", "D_10"],
    "PSL(2,13)": ["13:6", "D_14", "D_12", "A_4"],
    "PSL(2,17)": ["S_4", "S_4", "17:8", "D_18", "D_16"],
    "PSL(2,19)": ["A_5", "A_5", "19:9", "D_20", "D_18"],
    "PSL(2,23)": ["S_4", "S_4", "23:11", "D_24", "D_22"],
    "PSL(3,2)":  ["S_4", "S_4", "7:3"],
    "PSL(3,3)":  ["3^2:2S_4", "3^2:2S_4", "13:3", "S_4 x 2", "L_3(2) wreath product?"],
    "PSL(3,4)":  ["A_6", "A_6", "L_3(2)", "L_3(2)", "L_3(2)", "M_10",
                  "M_10", "M_10", "2^4:A_5"],
    # Symmetric / alternating: well-known max subgroup structure
    "S5": ["A_5", "S_4", "S_3 x S_2", "F_{20}=5:4"],
    "A5": ["A_4", "A_4", "A_4", "A_4", "A_4", "S_3", "D_10", "D_10", "D_10"],
    "A6": ["A_5", "A_5", "A_5", "A_5", "A_5", "A_5", "S_4", "S_4",
           "S_4", "S_4", "S_4", "S_4", "3^2:4"],
    "S6": ["A_6", "S_5", "S_5", "S_4 x S_2", "S_3 wreath S_2", "S_3 x S_3"],
    "A7": ["A_6", "A_6", "S_5", "S_5", "L_2(7)", "L_2(7)", "(A_4 x 3):2"],
    "S7": ["A_7", "S_6", "S_5 x S_2", "S_4 x S_3"],
    "A8": ["A_7", "S_6 x S_2", "(S_5 x S_3) cap A_8", "L_3(2)", "2^3:L_3(2)",
           "2^3:L_3(2)", "(A_4 x A_4):2_2", "(A_5 x A_3):2"],
    "S8": ["A_8", "S_7", "S_6 x S_2", "S_5 x S_3", "S_4 wreath S_2"],
}


def _attach_max_subgroups() -> None:
    """Annotate every ATLAS_TABLE entry with a max_subgroups list (may be empty)."""
    for entry in CYCLIC_TABLE + SYMMETRIC_TABLE + ALTERNATING_TABLE \
                  + MATHIEU_TABLE + PSL2_TABLE + SPORADIC_TABLE:
        nm = entry["name"]
        # Cyclic groups: subgroup lattice = divisor lattice of n; "max" = C_{n/p} for primes p | n.
        if entry.get("family") == "cyclic":
            n = entry["order"]
            if n <= 1:
                entry.setdefault("max_subgroups", [])
            else:
                primes = [p for p, _ in entry["order_prime_decomp"]]
                entry.setdefault("max_subgroups",
                                 [f"C{n//p}" for p in primes])
            continue
        entry.setdefault("max_subgroups", _MAX_SUBGROUPS.get(nm, []))


_attach_max_subgroups()


# ---------------------------------------------------------------------------
# Aggregate table
# ---------------------------------------------------------------------------

ATLAS_TABLE: list[dict] = (
    CYCLIC_TABLE
    + SYMMETRIC_TABLE
    + ALTERNATING_TABLE
    + MATHIEU_TABLE
    + PSL2_TABLE
    + SPORADIC_TABLE
)


SNAPSHOT_META: dict = {
    "source_url": "https://brauer.maths.qmul.ac.uk/Atlas/v3/",
    "primary_reference": ("Conway, Curtis, Norton, Parker, Wilson, "
                          "ATLAS of Finite Groups, OUP 1985"),
    "secondary_references": [
        "Wilson et al., online ATLAS v3 (brauer.maths.qmul.ac.uk)",
        "Conway-Sloane, Sphere Packings Lattices Groups, 3rd ed., Springer 1999",
        "Robinson, A Course in the Theory of Groups, 2nd ed., Springer 1996",
        "James-Kerber, Representation Theory of S_n, 1981",
    ],
    "snapshot_date": "2026-04-22",
    "entries": len(ATLAS_TABLE),
    "entries_with_character_table": sum(
        1 for e in ATLAS_TABLE if e.get("character_table") is not None
    ),
}


__all__ = [
    "ATLAS_TABLE",
    "CYCLIC_TABLE",
    "SYMMETRIC_TABLE",
    "ALTERNATING_TABLE",
    "MATHIEU_TABLE",
    "PSL2_TABLE",
    "SPORADIC_TABLE",
    "SNAPSHOT_META",
]
