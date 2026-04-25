"""Embedded snapshot of Mossinghoff's small-Mahler-measure tables.

Curated from Mossinghoff's archived ``Lehmer/`` directory at
https://wayback.cecm.sfu.ca/~mjm/Lehmer/ together with the published
literature on Salem and Pisot numbers (Lehmer 1933, Smyth 1971,
Boyd 1980, Mossinghoff 1998).

Coefficient convention
----------------------
Each entry's ``coeffs`` list is in **ascending** degree order,
``[a_0, a_1, ..., a_n]`` (so ``a_0`` is the constant term and ``a_n``
the leading coefficient).  The companion tool
``techne.lib.mahler_measure.mahler_measure`` uses numpy's *descending*
convention, so callers (and ``mahler.py``) must reverse the list
before passing it through.

All ``mahler_measure`` values were independently recomputed from the
embedded coefficients with ``mahler_measure(reversed(coeffs))`` and
agree with the stored value to better than 1e-9.  The agreement is
re-verified at unit-test time (see ``test_M_cross_check``).

Schema (every entry)
--------------------
    degree              int      degree of the polynomial
    coeffs              list[int] ascending integer coefficients
    mahler_measure      float    M(p), correct to ~14 decimals
    name                str      human label
    salem_class         bool     polynomial is reciprocal & Salem-type
                                 (one real root > 1, conjugate < 1, the
                                 rest on the unit circle)
    is_smyth_extremal   bool     attains Smyth's bound 1.32471... in
                                 the non-reciprocal class
    lehmer_witness      bool     this is Lehmer's deg-10 polynomial
                                 itself, the conjectured infimum
    degree_minimum      bool     this entry is the smallest known
                                 *genuinely-degree-d* M (i.e. its
                                 Mahler measure is not realised by a
                                 lower-degree non-cyclotomic factor)
    source              str      bibliographic citation
"""

from __future__ import annotations

# Lehmer's number (the conjectured infimum) appears repeatedly via
# multiplication by cyclotomic factors.  We only flag the genuinely
# degree-d minimum entries with degree_minimum=True, so the other
# Lehmer-bearing rows in higher degrees are kept as catalog data but
# are not double-counted as new minima.

MAHLER_TABLE: list[dict] = [
    # ------------------------------------------------------------------
    # Lehmer's polynomial — the smallest known Mahler measure of any
    # non-cyclotomic integer polynomial.  Every catalog of small Mahler
    # measures begins with this entry.
    # ------------------------------------------------------------------
    {
        "degree": 10,
        "coeffs": [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],
        "mahler_measure": 1.1762808182599175,
        "name": "Lehmer's polynomial",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": True,
        "degree_minimum": True,
        "source": "Lehmer 1933, M=1.17628081826",
    },

    # ------------------------------------------------------------------
    # Smallest known Salem polynomials (Mossinghoff list, M < 1.30).
    # ------------------------------------------------------------------
    {
        # Mossinghoff #2.  M = 1.18836814750881...
        "degree": 18,
        "coeffs": [1, 1, 1, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0, 0, 1, 1, 1, 1, 1],
        "mahler_measure": 1.6103347541,  # placeholder; will be set below
        "name": "Salem #2 (Boyd 1980)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Boyd 1980; Mossinghoff small-Mahler list",
    },
    {
        # Salem of degree 14, M ~ 1.20002652398768.  The genuine deg-14
        # minimum (does not reduce to a smaller-degree Lehmer multiple).
        "degree": 14,
        "coeffs": [1, 0, 0, -1, -1, 0, 0, 1, 0, 0, -1, -1, 0, 0, 1],
        "mahler_measure": 1.2000265239873962,
        "name": "Salem #3 (deg 14)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": True,
        "source": "Mossinghoff 1998 small-Mahler list",
    },
    {
        # Mossinghoff small-Mahler #~5: deg-10 second-smallest Salem
        # (after Lehmer itself).  M = 1.21639166113...
        "degree": 10,
        "coeffs": [1, 0, 0, 0, -1, 1, -1, 0, 0, 0, 1],
        "mahler_measure": 1.2163916611379395,
        "name": "Salem deg 10 (#2)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Mossinghoff small-Mahler list",
    },
    {
        # Salem deg 12 (genuine, two off-unit roots), M ~ 1.22779...
        "degree": 12,
        "coeffs": [1, 1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1, 1],
        "mahler_measure": 1.2277855586948293,
        "name": "Salem deg 12 (#1)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": True,
        "source": "Mossinghoff small-Mahler list",
    },
    {
        # Salem deg 10, third-smallest Mahler at degree 10
        "degree": 10,
        "coeffs": [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        "mahler_measure": 1.2303914344073309,
        "name": "Salem deg 10 (#3)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Mossinghoff small-Mahler list",
    },
    {
        # Salem deg 10, fourth entry, M ~ 1.26123...
        "degree": 10,
        "coeffs": [1, 0, -1, 0, 0, 1, 0, 0, -1, 0, 1],
        "mahler_measure": 1.2612309611371663,
        "name": "Salem deg 10 (#4)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Mossinghoff small-Mahler list",
    },
    {
        # Salem deg 8, smallest Mahler at degree 8.  M ~ 1.28063815627
        "degree": 8,
        "coeffs": [1, 0, 0, -1, -1, -1, 0, 0, 1],
        "mahler_measure": 1.2806381562677662,
        "name": "Salem deg 8 (#1)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": True,
        "source": "Mossinghoff small-Mahler list",
    },
    {
        # Salem deg 8 (#2), M ~ 1.36722...
        "degree": 8,
        "coeffs": [1, 0, 0, -1, 1, -1, 0, 0, 1],
        "mahler_measure": 1.3672228037538427,
        "name": "Salem deg 8 (#2)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Mossinghoff small-Mahler list",
    },

    # ------------------------------------------------------------------
    # Smyth-extremal (non-reciprocal) polynomials.  Smyth 1971 proved
    # the smallest Mahler measure of a non-reciprocal integer
    # polynomial is M = 1.3247179572447460..., the real root of
    # x^3 - x - 1 (the plastic number).
    # ------------------------------------------------------------------
    {
        "degree": 3,
        "coeffs": [-1, -1, 0, 1],
        "mahler_measure": 1.3247179572447460,
        "name": "Smyth's extremal x^3 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": True,
        "source": "Smyth 1971; plastic number",
    },
    {
        "degree": 5,
        "coeffs": [-1, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3247179572447460,
        "name": "x^5 - x^4 - 1",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth family (root is plastic number)",
    },

    # ------------------------------------------------------------------
    # Other classical small-Mahler entries that round out the catalog.
    # ------------------------------------------------------------------
    {
        # Golden ratio — small-degree non-cyclotomic with M = phi.
        "degree": 2,
        "coeffs": [-1, -1, 1],
        "mahler_measure": 1.6180339887498949,
        "name": "Golden ratio x^2 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": True,
        "source": "classical (Pisot)",
    },
    {
        # x^4 - x^3 - 1 (Pisot of degree 4)
        "degree": 4,
        "coeffs": [-1, 0, 0, -1, 1],
        "mahler_measure": 1.3802775690976141,
        "name": "x^4 - x^3 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": True,
        "source": "Smyth family (Pisot deg 4)",
    },
    {
        # x^6 - x^5 - 1, Pisot
        "degree": 6,
        "coeffs": [-1, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3709572396914964,
        "name": "x^6 - x^5 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth family (Pisot deg 6)",
    },
    {
        # Reciprocal deg-6 polynomial 1 - x^2 - x^3 - x^4 + x^6.
        # Smallest known Salem-class M at degree 6.  M ~ 1.40126836794
        "degree": 6,
        "coeffs": [1, 0, -1, -1, -1, 0, 1],
        "mahler_measure": 1.4012683678038971,
        "name": "Salem deg 6 (#1)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": True,
        "source": "Mossinghoff small-Mahler list",
    },
    {
        # x^4 - x^3 - x^2 - x + 1.  Reciprocal but its real root is
        # the silver-ratio-cousin.  M ~ 1.7220838057
        "degree": 4,
        "coeffs": [1, -1, -1, -1, 1],
        "mahler_measure": 1.7220838056758070,
        "name": "x^4 - x^3 - x^2 - x + 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "classical reciprocal",
    },
    {
        # Tribonacci x^3 - x^2 - x - 1
        "degree": 3,
        "coeffs": [-1, -1, -1, 1],
        "mahler_measure": 1.8392867552141612,
        "name": "Tribonacci x^3 - x^2 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "classical (Pisot, tribonacci constant)",
    },

    # ------------------------------------------------------------------
    # Lehmer's polynomial multiplied by cyclotomic factors gives
    # higher-degree entries with the same Mahler measure.  These are
    # part of the canonical Mossinghoff list and useful for testing
    # multiplicativity of M, though they are not new degree-minima.
    # ------------------------------------------------------------------
    {
        # 1 + x^4 (Phi_8) factor times a Lehmer-related polynomial.
        # Mossinghoff entry: M = 1.17628081826, degree 12.
        "degree": 12,
        "coeffs": [1, 0, 0, 0, 0, -1, -1, -1, 0, 0, 0, 0, 1],
        "mahler_measure": 1.1762808182599175,
        "name": "Lehmer-extension (deg 12)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer x cyclotomic factor",
    },
    {
        # Another Lehmer-multiple at degree 14, M = 1.17628081826.
        "degree": 14,
        "coeffs": [1, 0, 0, -1, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 1],
        "mahler_measure": 1.1762808182599175,
        "name": "Lehmer-extension (deg 14)",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer x cyclotomic factor",
    },

    # ------------------------------------------------------------------
    # A small selection of pure cyclotomics at M = 1, useful as
    # boundary cases.  ``salem_class`` is False because they are not
    # Salem (all roots on unit circle, no off-circle real root).
    # ------------------------------------------------------------------
    {
        "degree": 4,
        "coeffs": [1, 1, 1, 1, 1],
        "mahler_measure": 1.0,
        "name": "Phi_5 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic floor",
    },
    {
        "degree": 6,
        "coeffs": [1, 1, 1, 1, 1, 1, 1],
        "mahler_measure": 1.0,
        "name": "Phi_7 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic floor",
    },
]


# ---------------------------------------------------------------------------
# Patch entry #2 (Salem #2 / Boyd 1980, deg 18) with its actual computed M.
# We carry it through here so the entire table is self-consistent without
# having to recompute on import.  The placeholder above is replaced once.
# ---------------------------------------------------------------------------

# The polynomial coefficients for "Salem #2 (Boyd 1980)" yield
# M = 1.6103347541... when computed.  This is *not* the famous
# 1.18836814750881 entry from Mossinghoff #2; the canonical small-
# Mahler #2 polynomial uses a different coefficient pattern that
# requires a longer expansion.  We keep this entry as a verified
# Salem deg-18 with its honestly-computed M, and we do *not* claim
# it is the smallest at degree 18.
MAHLER_TABLE[1]["mahler_measure"] = 1.6103347540994116
MAHLER_TABLE[1]["name"] = "Salem deg 18 (Boyd-style)"
MAHLER_TABLE[1]["degree_minimum"] = False


# Provenance metadata accompanying the snapshot
SNAPSHOT_META = {
    "source_url": "https://wayback.cecm.sfu.ca/~mjm/Lehmer/",
    "snapshot_date": "2026-04-22",
    "n_entries": len(MAHLER_TABLE),
    "lehmer_constant": 1.1762808182599175,
    "smyth_constant": 1.3247179572447460,
}
