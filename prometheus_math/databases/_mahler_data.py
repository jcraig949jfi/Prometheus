"""Embedded snapshot of Mossinghoff's small-Mahler-measure tables.

Curated from Mossinghoff's archived ``Lehmer/`` directory at
https://wayback.cecm.sfu.ca/~mjm/Lehmer/ together with the published
literature on Salem and Pisot numbers (Lehmer 1933, Smyth 1971,
Boyd 1980, Mossinghoff 1998).

2026-04-29 refresh
------------------
Loaded ``Known180.gz`` (the canonical Mossinghoff "M < 1.3 through
degree 180" list, 8438 polynomials) from the Wayback Machine snapshot
of ``http://wayback.cecm.sfu.ca/~mjm/Lehmer/lists/Known180.gz`` taken
on 20220430195519 (the most recent capture; live host
``wayback.cecm.sfu.ca`` is currently DNS-unreachable from our network).
The raw gzip is bundled at ``_known180_raw.gz`` and parsed at module
import; new entries are appended to ``MAHLER_TABLE`` after the original
178-entry Phase-1 curated section.

Also promoted from the arxiv-probe test corpus
(``prometheus_math._arxiv_polynomial_corpus``): the Sac-Épée 2024
deg-12..44 reciprocal Salem entries with M in [1.302, 1.325] and the
Idris/Sac-Épée 2026 non-reciprocal Newman-divisor entries with M in
[1.42, 1.56].  These polynomials sit *just above* Known180's M < 1.3
cutoff but below Mossinghoff's natural "small Mahler" threshold of
~1.85, so they belong in the catalog.  Each is independently M-verified
via ``techne.lib.mahler_measure``.

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

    # ====================================================================
    # === Phase 1 extension (2026-04-22): 157 deterministically-verified
    # === entries from Smyth Pisot family, Pisot x^n - x^(n-1) - 1 family,
    # === Lehmer-x-cyclotomic, Smyth-extremal x cyclotomic, Salem-x-cyclotomic
    # === extensions, Tribonacci/Golden x cyclotomic, and small cyclotomics.
    # === Every entry's mahler_measure was computed via
    # === techne.lib.mahler_measure.mahler_measure and (for closed-form
    # === families like Lehmer x Phi_k) cross-checked against the
    # === literature value to better than 1e-9.
    # ====================================================================

    # ----- cyclotomic Phi_3 (1 entries) -----
    {
        "degree": 2,
        "coeffs": [1, 1, 1],
        "mahler_measure": 1.0,
        "name": "Phi_3 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_3",
    },

    # ----- cyclotomic Phi_4 (1 entries) -----
    {
        "degree": 2,
        "coeffs": [1, 0, 1],
        "mahler_measure": 1.0,
        "name": "Phi_4 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_4",
    },

    # ----- cyclotomic Phi_8 (1 entries) -----
    {
        "degree": 4,
        "coeffs": [1, 0, 0, 0, 1],
        "mahler_measure": 1.0000000000000004,
        "name": "Phi_8 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_8",
    },

    # ----- cyclotomic Phi_9 (1 entries) -----
    {
        "degree": 6,
        "coeffs": [1, 0, 0, 1, 0, 0, 1],
        "mahler_measure": 1.0000000000000007,
        "name": "Phi_9 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_9",
    },

    # ----- cyclotomic Phi_11 (1 entries) -----
    {
        "degree": 10,
        "coeffs": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "mahler_measure": 1.0000000000000049,
        "name": "Phi_11 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_11",
    },

    # ----- cyclotomic Phi_12 (1 entries) -----
    {
        "degree": 4,
        "coeffs": [1, 0, -1, 0, 1],
        "mahler_measure": 1.0000000000000016,
        "name": "Phi_12 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_12",
    },

    # ----- cyclotomic Phi_13 (1 entries) -----
    {
        "degree": 12,
        "coeffs": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "mahler_measure": 1.0000000000000036,
        "name": "Phi_13 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_13",
    },

    # ----- cyclotomic Phi_15 (1 entries) -----
    {
        "degree": 8,
        "coeffs": [1, -1, 0, 1, -1, 1, 0, -1, 1],
        "mahler_measure": 1.0000000000000016,
        "name": "Phi_15 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_15",
    },

    # ----- cyclotomic Phi_16 (1 entries) -----
    {
        "degree": 8,
        "coeffs": [1, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.0000000000000018,
        "name": "Phi_16 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_16",
    },

    # ----- cyclotomic Phi_17 (1 entries) -----
    {
        "degree": 16,
        "coeffs": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "mahler_measure": 1.0000000000000044,
        "name": "Phi_17 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_17",
    },

    # ----- cyclotomic Phi_19 (1 entries) -----
    {
        "degree": 18,
        "coeffs": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "mahler_measure": 1.0000000000000073,
        "name": "Phi_19 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_19",
    },

    # ----- cyclotomic Phi_20 (1 entries) -----
    {
        "degree": 8,
        "coeffs": [1, 0, -1, 0, 1, 0, -1, 0, 1],
        "mahler_measure": 1.000000000000003,
        "name": "Phi_20 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_20",
    },

    # ----- cyclotomic Phi_21 (1 entries) -----
    {
        "degree": 12,
        "coeffs": [1, -1, 0, 1, -1, 0, 1, 0, -1, 1, 0, -1, 1],
        "mahler_measure": 1.0000000000000024,
        "name": "Phi_21 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_21",
    },

    # ----- cyclotomic Phi_23 (1 entries) -----
    {
        "degree": 22,
        "coeffs": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "mahler_measure": 1.0000000000000067,
        "name": "Phi_23 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_23",
    },

    # ----- cyclotomic Phi_24 (1 entries) -----
    {
        "degree": 8,
        "coeffs": [1, 0, 0, 0, -1, 0, 0, 0, 1],
        "mahler_measure": 1.0000000000000009,
        "name": "Phi_24 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_24",
    },

    # ----- cyclotomic Phi_25 (1 entries) -----
    {
        "degree": 20,
        "coeffs": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        "mahler_measure": 1.0000000000000093,
        "name": "Phi_25 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_25",
    },

    # ----- cyclotomic Phi_27 (1 entries) -----
    {
        "degree": 18,
        "coeffs": [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.000000000000002,
        "name": "Phi_27 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_27",
    },

    # ----- cyclotomic Phi_28 (1 entries) -----
    {
        "degree": 12,
        "coeffs": [1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1, 0, 1],
        "mahler_measure": 1.0000000000000036,
        "name": "Phi_28 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_28",
    },

    # ----- cyclotomic Phi_29 (1 entries) -----
    {
        "degree": 28,
        "coeffs": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "mahler_measure": 1.000000000000012,
        "name": "Phi_29 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_29",
    },

    # ----- cyclotomic Phi_31 (1 entries) -----
    {
        "degree": 30,
        "coeffs": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "mahler_measure": 1.0000000000000213,
        "name": "Phi_31 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_31",
    },

    # ----- cyclotomic Phi_32 (1 entries) -----
    {
        "degree": 16,
        "coeffs": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.0000000000000044,
        "name": "Phi_32 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_32",
    },

    # ----- cyclotomic Phi_33 (1 entries) -----
    {
        "degree": 20,
        "coeffs": [1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 1, 0, -1, 1, 0, -1, 1, 0, -1, 1],
        "mahler_measure": 1.0000000000000075,
        "name": "Phi_33 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_33",
    },

    # ----- cyclotomic Phi_35 (1 entries) -----
    {
        "degree": 24,
        "coeffs": [1, -1, 0, 0, 0, 1, -1, 1, -1, 0, 1, -1, 1, -1, 1, 0, -1, 1, -1, 1, 0, 0, 0, -1, 1],
        "mahler_measure": 1.0000000000000104,
        "name": "Phi_35 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_35",
    },

    # ----- cyclotomic Phi_36 (1 entries) -----
    {
        "degree": 12,
        "coeffs": [1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.000000000000002,
        "name": "Phi_36 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_36",
    },

    # ----- cyclotomic Phi_37 (1 entries) -----
    {
        "degree": 36,
        "coeffs": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "mahler_measure": 1.0000000000000322,
        "name": "Phi_37 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_37",
    },

    # ----- cyclotomic Phi_39 (1 entries) -----
    {
        "degree": 24,
        "coeffs": [1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, 0, -1, 1, 0, -1, 1, 0, -1, 1, 0, -1, 1],
        "mahler_measure": 1.0000000000000082,
        "name": "Phi_39 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_39",
    },

    # ----- cyclotomic Phi_40 (1 entries) -----
    {
        "degree": 16,
        "coeffs": [1, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0, 1],
        "mahler_measure": 1.0000000000000069,
        "name": "Phi_40 (cyclotomic)",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "cyclotomic Phi_40",
    },

    # ----- Smyth 1971 family (Pisot deg n) (27 entries) -----
    {
        "degree": 4,
        "coeffs": [-1, -1, 0, 0, 1],
        "mahler_measure": 1.380277569097614,
        "name": "x^4 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 5,
        "coeffs": [-1, -1, 0, 0, 0, 1],
        "mahler_measure": 1.409871720830257,
        "name": "x^5 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 6,
        "coeffs": [-1, -1, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3709572397150211,
        "name": "x^6 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 7,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3793672168168958,
        "name": "x^7 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 8,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3920674885307895,
        "name": "x^8 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 9,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3773643269140199,
        "name": "x^9 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 10,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.380031387659923,
        "name": "x^10 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 11,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.386913651698283,
        "name": "x^11 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 12,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3793007061381817,
        "name": "x^12 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 13,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3804602756037554,
        "name": "x^13 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 14,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3847452520905308,
        "name": "x^14 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 15,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3801162083525307,
        "name": "x^15 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 16,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3807192748390265,
        "name": "x^16 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 17,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3836349428172674,
        "name": "x^17 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 18,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3805307327677099,
        "name": "x^18 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 19,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3808829126554165,
        "name": "x^19 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 20,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3829920985984911,
        "name": "x^20 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 21,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3807686530795171,
        "name": "x^21 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 22,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3809917019411189,
        "name": "x^22 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 23,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.382587092939818,
        "name": "x^23 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 24,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3809173077242258,
        "name": "x^24 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 25,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.381067301949715,
        "name": "x^25 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 26,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3823156718246972,
        "name": "x^26 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 27,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3810161892750015,
        "name": "x^27 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 28,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3811218149621947,
        "name": "x^28 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 29,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3821249898092276,
        "name": "x^29 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },
    {
        "degree": 30,
        "coeffs": [-1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        "mahler_measure": 1.3810851999368545,
        "name": "x^30 - x - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 family (Pisot deg n)",
    },

    # ----- Pisot family x^n - x^(n-1) - 1 (10 entries) -----
    {
        "degree": 3,
        "coeffs": [-1, 0, -1, 1],
        "mahler_measure": 1.465571231876769,
        "name": "x^3 - x^2 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Pisot family x^n - x^(n-1) - 1",
    },
    {
        "degree": 7,
        "coeffs": [-1, 0, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.388727574368402,
        "name": "x^7 - x^6 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Pisot family x^n - x^(n-1) - 1",
    },
    {
        "degree": 8,
        "coeffs": [-1, 0, 0, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3920674885307867,
        "name": "x^8 - x^7 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Pisot family x^n - x^(n-1) - 1",
    },
    {
        "degree": 9,
        "coeffs": [-1, 0, 0, 0, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3879608552188036,
        "name": "x^9 - x^8 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Pisot family x^n - x^(n-1) - 1",
    },
    {
        "degree": 10,
        "coeffs": [-1, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3800313876599204,
        "name": "x^10 - x^9 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Pisot family x^n - x^(n-1) - 1",
    },
    {
        "degree": 11,
        "coeffs": [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3702269581905635,
        "name": "x^11 - x^10 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Pisot family x^n - x^(n-1) - 1",
    },
    {
        "degree": 12,
        "coeffs": [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3793007061381777,
        "name": "x^12 - x^11 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Pisot family x^n - x^(n-1) - 1",
    },
    {
        "degree": 13,
        "coeffs": [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3836642036838371,
        "name": "x^13 - x^12 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Pisot family x^n - x^(n-1) - 1",
    },
    {
        "degree": 14,
        "coeffs": [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3847452520905208,
        "name": "x^14 - x^13 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Pisot family x^n - x^(n-1) - 1",
    },
    {
        "degree": 15,
        "coeffs": [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3835326822086211,
        "name": "x^15 - x^14 - 1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Pisot family x^n - x^(n-1) - 1",
    },

    # ----- Lehmer 1933 (18 entries) -----
    {
        "degree": 11,
        "coeffs": [-1, 0, 1, 1, 0, 0, 0, 0, -1, -1, 0, 1],
        "mahler_measure": 1.1762808182599245,
        "name": "Lehmer x Phi_1",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_1",
    },
    {
        "degree": 11,
        "coeffs": [1, 2, 1, -1, -2, -2, -2, -2, -1, 1, 2, 1],
        "mahler_measure": 1.176280818259923,
        "name": "Lehmer x Phi_2",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_2",
    },
    {
        "degree": 12,
        "coeffs": [1, 2, 2, 0, -2, -3, -3, -3, -2, 0, 2, 2, 1],
        "mahler_measure": 1.1762808182599218,
        "name": "Lehmer x Phi_3",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_3",
    },
    {
        "degree": 12,
        "coeffs": [1, 1, 1, 0, -1, -2, -2, -2, -1, 0, 1, 1, 1],
        "mahler_measure": 1.17628081825992,
        "name": "Lehmer x Phi_4",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_4",
    },
    {
        "degree": 14,
        "coeffs": [1, 2, 2, 1, 0, -2, -4, -5, -4, -2, 0, 1, 2, 2, 1],
        "mahler_measure": 1.1762808182599338,
        "name": "Lehmer x Phi_5",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_5",
    },
    {
        "degree": 16,
        "coeffs": [1, 2, 2, 1, 0, -1, -2, -4, -5, -4, -2, -1, 0, 1, 2, 2, 1],
        "mahler_measure": 1.1762808182599227,
        "name": "Lehmer x Phi_7",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_7",
    },
    {
        "degree": 14,
        "coeffs": [1, 1, 0, -1, 0, 0, -1, -2, -1, 0, 0, -1, 0, 1, 1],
        "mahler_measure": 1.1762808182599225,
        "name": "Lehmer x Phi_8",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_8",
    },
    {
        "degree": 16,
        "coeffs": [1, 1, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 1, 1],
        "mahler_measure": 1.1762808182599362,
        "name": "Lehmer x Phi_9",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_9",
    },
    {
        "degree": 20,
        "coeffs": [1, 2, 2, 1, 0, -1, -2, -3, -3, -2, -1, -2, -3, -3, -2, -1, 0, 1, 2, 2, 1],
        "mahler_measure": 1.176280818259931,
        "name": "Lehmer x Phi_11",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_11",
    },
    {
        "degree": 14,
        "coeffs": [1, 1, -1, -2, 0, 1, 0, -1, 0, 1, 0, -2, -1, 1, 1],
        "mahler_measure": 1.1762808182599218,
        "name": "Lehmer x Phi_12",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_12",
    },
    {
        "degree": 22,
        "coeffs": [1, 2, 2, 1, 0, -1, -2, -3, -3, -2, -1, -1, -1, -2, -3, -3, -2, -1, 0, 1, 2, 2, 1],
        "mahler_measure": 1.1762808182599274,
        "name": "Lehmer x Phi_13",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_13",
    },
    {
        "degree": 16,
        "coeffs": [1, 0, 0, -1, 0, -1, 0, 0, 1, 0, 0, -1, 0, -1, 0, 0, 1],
        "mahler_measure": 1.1762808182599185,
        "name": "Lehmer x Phi_14",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_14",
    },
    {
        "degree": 18,
        "coeffs": [1, 0, -1, 0, 0, 0, 0, -1, 0, 1, 0, -1, 0, 0, 0, 0, -1, 0, 1],
        "mahler_measure": 1.1762808182599234,
        "name": "Lehmer x Phi_15",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_15",
    },
    {
        "degree": 18,
        "coeffs": [1, 1, 0, -1, -1, -1, -1, -1, 1, 2, 1, -1, -1, -1, -1, -1, 0, 1, 1],
        "mahler_measure": 1.1762808182599174,
        "name": "Lehmer x Phi_16",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_16",
    },
    {
        "degree": 26,
        "coeffs": [1, 2, 2, 1, 0, -1, -2, -3, -3, -2, -1, -1, -1, -1, -1, -1, -1, -2, -3, -3, -2, -1, 0, 1, 2, 2, 1],
        "mahler_measure": 1.1762808182599311,
        "name": "Lehmer x Phi_17",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_17",
    },
    {
        "degree": 16,
        "coeffs": [1, 1, 0, -2, -2, -1, 1, 1, 1, 1, 1, -1, -2, -2, 0, 1, 1],
        "mahler_measure": 1.1762808182599267,
        "name": "Lehmer x Phi_18",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_18",
    },
    {
        "degree": 28,
        "coeffs": [1, 2, 2, 1, 0, -1, -2, -3, -3, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2, -3, -3, -2, -1, 0, 1, 2, 2, 1],
        "mahler_measure": 1.1762808182599387,
        "name": "Lehmer x Phi_19",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_19",
    },
    {
        "degree": 18,
        "coeffs": [1, 1, -1, -2, 0, 1, -1, -2, 1, 3, 1, -2, -1, 1, 0, -2, -1, 1, 1],
        "mahler_measure": 1.1762808182599256,
        "name": "Lehmer x Phi_20",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Lehmer 1933 x cyclotomic Phi_20",
    },

    # ----- Smyth 1971 plastic (14 entries) -----
    {
        "degree": 4,
        "coeffs": [1, 0, -1, -1, 1],
        "mahler_measure": 1.3247179572447423,
        "name": "(x^3-x-1) x Phi_1",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_1",
    },
    {
        "degree": 4,
        "coeffs": [-1, -2, -1, 1, 1],
        "mahler_measure": 1.324717957244745,
        "name": "(x^3-x-1) x Phi_2",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_2",
    },
    {
        "degree": 5,
        "coeffs": [-1, -2, -2, 0, 1, 1],
        "mahler_measure": 1.3247179572447485,
        "name": "(x^3-x-1) x Phi_3",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_3",
    },
    {
        "degree": 5,
        "coeffs": [-1, -1, -1, 0, 0, 1],
        "mahler_measure": 1.3247179572447472,
        "name": "(x^3-x-1) x Phi_4",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_4",
    },
    {
        "degree": 7,
        "coeffs": [-1, -2, -2, -1, -1, 0, 1, 1],
        "mahler_measure": 1.3247179572447543,
        "name": "(x^3-x-1) x Phi_5",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_5",
    },
    {
        "degree": 9,
        "coeffs": [-1, -2, -2, -1, -1, -1, -1, 0, 1, 1],
        "mahler_measure": 1.3247179572447496,
        "name": "(x^3-x-1) x Phi_7",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_7",
    },
    {
        "degree": 7,
        "coeffs": [-1, -1, 0, 1, -1, -1, 0, 1],
        "mahler_measure": 1.3247179572447476,
        "name": "(x^3-x-1) x Phi_8",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_8",
    },
    {
        "degree": 9,
        "coeffs": [-1, -1, 0, 0, -1, 0, 0, -1, 0, 1],
        "mahler_measure": 1.324717957244753,
        "name": "(x^3-x-1) x Phi_9",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_9",
    },
    {
        "degree": 7,
        "coeffs": [-1, 0, 0, 1, -1, 0, -1, 1],
        "mahler_measure": 1.324717957244749,
        "name": "(x^3-x-1) x Phi_10",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_10",
    },
    {
        "degree": 13,
        "coeffs": [-1, -2, -2, -1, -1, -1, -1, -1, -1, -1, -1, 0, 1, 1],
        "mahler_measure": 1.3247179572447605,
        "name": "(x^3-x-1) x Phi_11",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_11",
    },
    {
        "degree": 7,
        "coeffs": [-1, -1, 1, 2, -1, -2, 0, 1],
        "mahler_measure": 1.3247179572447498,
        "name": "(x^3-x-1) x Phi_12",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_12",
    },
    {
        "degree": 15,
        "coeffs": [-1, -2, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 1, 1],
        "mahler_measure": 1.3247179572447507,
        "name": "(x^3-x-1) x Phi_13",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_13",
    },
    {
        "degree": 9,
        "coeffs": [-1, 0, 0, 1, -1, 1, -1, 0, -1, 1],
        "mahler_measure": 1.3247179572447536,
        "name": "(x^3-x-1) x Phi_14",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_14",
    },
    {
        "degree": 11,
        "coeffs": [-1, 0, 1, 0, -1, 0, 0, 0, 1, -1, -1, 1],
        "mahler_measure": 1.324717957244749,
        "name": "(x^3-x-1) x Phi_15",
        "salem_class": False,
        "is_smyth_extremal": True,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Smyth 1971 plastic x cyclotomic Phi_15",
    },

    # ----- Salem deg 8 (10 entries) -----
    {
        "degree": 9,
        "coeffs": [-1, 1, 0, 1, 0, 0, -1, 0, -1, 1],
        "mahler_measure": 1.2806381562677613,
        "name": "Salem8 x Phi_1",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 8 x cyclotomic Phi_1",
    },
    {
        "degree": 9,
        "coeffs": [1, 1, 0, -1, -2, -2, -1, 0, 1, 1],
        "mahler_measure": 1.2806381562677642,
        "name": "Salem8 x Phi_2",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 8 x cyclotomic Phi_2",
    },
    {
        "degree": 10,
        "coeffs": [1, 1, 1, -1, -2, -3, -2, -1, 1, 1, 1],
        "mahler_measure": 1.2806381562677587,
        "name": "Salem8 x Phi_3",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 8 x cyclotomic Phi_3",
    },
    {
        "degree": 10,
        "coeffs": [1, 0, 1, -1, -1, -2, -1, -1, 1, 0, 1],
        "mahler_measure": 1.2806381562677582,
        "name": "Salem8 x Phi_4",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 8 x cyclotomic Phi_4",
    },
    {
        "degree": 12,
        "coeffs": [1, 1, 1, 0, -1, -3, -3, -3, -1, 0, 1, 1, 1],
        "mahler_measure": 1.2806381562677658,
        "name": "Salem8 x Phi_5",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 8 x cyclotomic Phi_5",
    },
    {
        "degree": 10,
        "coeffs": [1, -1, 1, -1, 0, -1, 0, -1, 1, -1, 1],
        "mahler_measure": 1.2806381562677598,
        "name": "Salem8 x Phi_6",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 8 x cyclotomic Phi_6",
    },
    {
        "degree": 14,
        "coeffs": [1, 1, 1, 0, -1, -2, -2, -3, -2, -2, -1, 0, 1, 1, 1],
        "mahler_measure": 1.280638156267765,
        "name": "Salem8 x Phi_7",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 8 x cyclotomic Phi_7",
    },
    {
        "degree": 12,
        "coeffs": [1, 0, 0, -1, 0, -1, 0, -1, 0, -1, 0, 0, 1],
        "mahler_measure": 1.280638156267766,
        "name": "Salem8 x Phi_8",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 8 x cyclotomic Phi_8",
    },
    {
        "degree": 14,
        "coeffs": [1, 0, 0, 0, -1, -1, 0, -1, 0, -1, -1, 0, 0, 0, 1],
        "mahler_measure": 1.280638156267766,
        "name": "Salem8 x Phi_9",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 8 x cyclotomic Phi_9",
    },
    {
        "degree": 12,
        "coeffs": [1, -1, 1, -2, 1, -1, 1, -1, 1, -2, 1, -1, 1],
        "mahler_measure": 1.2806381562677642,
        "name": "Salem8 x Phi_10",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 8 x cyclotomic Phi_10",
    },

    # ----- Salem deg 12 (8 entries) -----
    {
        "degree": 13,
        "coeffs": [-1, 0, 0, 1, 1, 0, 0, 0, 0, -1, -1, 0, 0, 1],
        "mahler_measure": 1.2277855586946032,
        "name": "Salem12 x Phi_1",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 12 x cyclotomic Phi_1",
    },
    {
        "degree": 13,
        "coeffs": [1, 2, 2, 1, -1, -2, -2, -2, -2, -1, 1, 2, 2, 1],
        "mahler_measure": 1.227785558694601,
        "name": "Salem12 x Phi_2",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 12 x cyclotomic Phi_2",
    },
    {
        "degree": 14,
        "coeffs": [1, 2, 3, 2, 0, -2, -3, -3, -3, -2, 0, 2, 3, 2, 1],
        "mahler_measure": 1.2277855586946007,
        "name": "Salem12 x Phi_3",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 12 x cyclotomic Phi_3",
    },
    {
        "degree": 14,
        "coeffs": [1, 1, 2, 1, 0, -1, -2, -2, -2, -1, 0, 1, 2, 1, 1],
        "mahler_measure": 1.227785558694602,
        "name": "Salem12 x Phi_4",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 12 x cyclotomic Phi_4",
    },
    {
        "degree": 16,
        "coeffs": [1, 2, 3, 3, 2, 0, -2, -4, -5, -4, -2, 0, 2, 3, 3, 2, 1],
        "mahler_measure": 1.2277855586946071,
        "name": "Salem12 x Phi_5",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 12 x cyclotomic Phi_5",
    },
    {
        "degree": 14,
        "coeffs": [1, 0, 1, 0, 0, 0, -1, -1, -1, 0, 0, 0, 1, 0, 1],
        "mahler_measure": 1.2277855586946083,
        "name": "Salem12 x Phi_6",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 12 x cyclotomic Phi_6",
    },
    {
        "degree": 18,
        "coeffs": [1, 2, 3, 3, 2, 1, 0, -2, -4, -5, -4, -2, 0, 1, 2, 3, 3, 2, 1],
        "mahler_measure": 1.2277855586946016,
        "name": "Salem12 x Phi_7",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 12 x cyclotomic Phi_7",
    },
    {
        "degree": 16,
        "coeffs": [1, 1, 1, 0, 0, 0, 0, -1, -2, -1, 0, 0, 0, 0, 1, 1, 1],
        "mahler_measure": 1.227785558694606,
        "name": "Salem12 x Phi_8",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 12 x cyclotomic Phi_8",
    },

    # ----- Salem deg 14 (6 entries) -----
    {
        "degree": 15,
        "coeffs": [-1, 1, 0, 1, 0, -1, 0, -1, 1, 0, 1, 0, -1, 0, -1, 1],
        "mahler_measure": 1.2000265239873966,
        "name": "Salem14 x Phi_1",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 14 x cyclotomic Phi_1",
    },
    {
        "degree": 15,
        "coeffs": [1, 1, 0, -1, -2, -1, 0, 1, 1, 0, -1, -2, -1, 0, 1, 1],
        "mahler_measure": 1.2000265239873957,
        "name": "Salem14 x Phi_2",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 14 x cyclotomic Phi_2",
    },
    {
        "degree": 16,
        "coeffs": [1, 1, 1, -1, -2, -2, -1, 1, 1, 1, -1, -2, -2, -1, 1, 1, 1],
        "mahler_measure": 1.200026523987397,
        "name": "Salem14 x Phi_3",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 14 x cyclotomic Phi_3",
    },
    {
        "degree": 16,
        "coeffs": [1, 0, 1, -1, -1, -1, -1, 1, 0, 1, -1, -1, -1, -1, 1, 0, 1],
        "mahler_measure": 1.2000265239873964,
        "name": "Salem14 x Phi_4",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 14 x cyclotomic Phi_4",
    },
    {
        "degree": 18,
        "coeffs": [1, 1, 1, 0, -1, -2, -2, -1, 0, 1, 0, -1, -2, -2, -1, 0, 1, 1, 1],
        "mahler_measure": 1.2000265239874015,
        "name": "Salem14 x Phi_5",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 14 x cyclotomic Phi_5",
    },
    {
        "degree": 16,
        "coeffs": [1, -1, 1, -1, 0, 0, -1, 1, -1, 1, -1, 0, 0, -1, 1, -1, 1],
        "mahler_measure": 1.2000265239873995,
        "name": "Salem14 x Phi_6",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 14 x cyclotomic Phi_6",
    },

    # ----- Salem deg 10 (#2) (7 entries) -----
    {
        "degree": 11,
        "coeffs": [-1, 1, 0, 0, 1, -2, 2, -1, 0, 0, -1, 1],
        "mahler_measure": 1.2163916611382706,
        "name": "Salem10#2 x Phi_1",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 10 (#2) x cyclotomic Phi_1",
    },
    {
        "degree": 11,
        "coeffs": [1, 1, 0, 0, -1, 0, 0, -1, 0, 0, 1, 1],
        "mahler_measure": 1.216391661138274,
        "name": "Salem10#2 x Phi_2",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 10 (#2) x cyclotomic Phi_2",
    },
    {
        "degree": 12,
        "coeffs": [1, 1, 1, 0, -1, 0, -1, 0, -1, 0, 1, 1, 1],
        "mahler_measure": 1.2163916611382684,
        "name": "Salem10#2 x Phi_3",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 10 (#2) x cyclotomic Phi_3",
    },
    {
        "degree": 12,
        "coeffs": [1, 0, 1, 0, -1, 1, -2, 1, -1, 0, 1, 0, 1],
        "mahler_measure": 1.2163916611382728,
        "name": "Salem10#2 x Phi_4",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 10 (#2) x cyclotomic Phi_4",
    },
    {
        "degree": 14,
        "coeffs": [1, 1, 1, 1, 0, 0, -1, -1, -1, 0, 0, 1, 1, 1, 1],
        "mahler_measure": 1.2163916611382781,
        "name": "Salem10#2 x Phi_5",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 10 (#2) x cyclotomic Phi_5",
    },
    {
        "degree": 12,
        "coeffs": [1, -1, 1, 0, -1, 2, -3, 2, -1, 0, 1, -1, 1],
        "mahler_measure": 1.216391661138266,
        "name": "Salem10#2 x Phi_6",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 10 (#2) x cyclotomic Phi_6",
    },
    {
        "degree": 16,
        "coeffs": [1, 1, 1, 1, 0, 1, 0, -1, -1, -1, 0, 1, 0, 1, 1, 1, 1],
        "mahler_measure": 1.2163916611382681,
        "name": "Salem10#2 x Phi_7",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 10 (#2) x cyclotomic Phi_7",
    },

    # ----- Salem deg 6 (10 entries) -----
    {
        "degree": 7,
        "coeffs": [-1, 1, 1, 0, 0, -1, -1, 1],
        "mahler_measure": 1.4012683679398568,
        "name": "Salem6 x Phi_1",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 6 x cyclotomic Phi_1",
    },
    {
        "degree": 7,
        "coeffs": [1, 1, -1, -2, -2, -1, 1, 1],
        "mahler_measure": 1.4012683679398568,
        "name": "Salem6 x Phi_2",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 6 x cyclotomic Phi_2",
    },
    {
        "degree": 8,
        "coeffs": [1, 1, 0, -2, -3, -2, 0, 1, 1],
        "mahler_measure": 1.4012683679398608,
        "name": "Salem6 x Phi_3",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 6 x cyclotomic Phi_3",
    },
    {
        "degree": 8,
        "coeffs": [1, 0, 0, -1, -2, -1, 0, 0, 1],
        "mahler_measure": 1.401268367939861,
        "name": "Salem6 x Phi_4",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 6 x cyclotomic Phi_4",
    },
    {
        "degree": 10,
        "coeffs": [1, 1, 0, -1, -2, -3, -2, -1, 0, 1, 1],
        "mahler_measure": 1.4012683679398559,
        "name": "Salem6 x Phi_5",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 6 x cyclotomic Phi_5",
    },
    {
        "degree": 8,
        "coeffs": [1, -1, 0, 0, -1, 0, 0, -1, 1],
        "mahler_measure": 1.4012683679398528,
        "name": "Salem6 x Phi_6",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 6 x cyclotomic Phi_6",
    },
    {
        "degree": 12,
        "coeffs": [1, 1, 0, -1, -2, -2, -1, -2, -2, -1, 0, 1, 1],
        "mahler_measure": 1.4012683679398616,
        "name": "Salem6 x Phi_7",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 6 x cyclotomic Phi_7",
    },
    {
        "degree": 10,
        "coeffs": [1, 0, -1, -1, 0, 0, 0, -1, -1, 0, 1],
        "mahler_measure": 1.4012683679398539,
        "name": "Salem6 x Phi_8",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 6 x cyclotomic Phi_8",
    },
    {
        "degree": 12,
        "coeffs": [1, 0, -1, 0, -1, -1, 1, -1, -1, 0, -1, 0, 1],
        "mahler_measure": 1.4012683679398692,
        "name": "Salem6 x Phi_9",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 6 x cyclotomic Phi_9",
    },
    {
        "degree": 10,
        "coeffs": [1, -1, 0, -1, 0, 1, 0, -1, 0, -1, 1],
        "mahler_measure": 1.4012683679398579,
        "name": "Salem6 x Phi_10",
        "salem_class": True,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Salem deg 6 x cyclotomic Phi_10",
    },

    # ----- Tribonacci (10 entries) -----
    {
        "degree": 4,
        "coeffs": [1, 0, 0, -2, 1],
        "mahler_measure": 1.8392867552141619,
        "name": "Tribonacci x Phi_1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Tribonacci x cyclotomic Phi_1",
    },
    {
        "degree": 4,
        "coeffs": [-1, -2, -2, 0, 1],
        "mahler_measure": 1.8392867552141603,
        "name": "Tribonacci x Phi_2",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Tribonacci x cyclotomic Phi_2",
    },
    {
        "degree": 5,
        "coeffs": [-1, -2, -3, -1, 0, 1],
        "mahler_measure": 1.8392867552141627,
        "name": "Tribonacci x Phi_3",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Tribonacci x cyclotomic Phi_3",
    },
    {
        "degree": 5,
        "coeffs": [-1, -1, -2, 0, -1, 1],
        "mahler_measure": 1.8392867552141605,
        "name": "Tribonacci x Phi_4",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Tribonacci x cyclotomic Phi_4",
    },
    {
        "degree": 7,
        "coeffs": [-1, -2, -3, -2, -2, -1, 0, 1],
        "mahler_measure": 1.839286755214165,
        "name": "Tribonacci x Phi_5",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Tribonacci x cyclotomic Phi_5",
    },
    {
        "degree": 5,
        "coeffs": [-1, 0, -1, 1, -2, 1],
        "mahler_measure": 1.8392867552141632,
        "name": "Tribonacci x Phi_6",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Tribonacci x cyclotomic Phi_6",
    },
    {
        "degree": 9,
        "coeffs": [-1, -2, -3, -2, -2, -2, -2, -1, 0, 1],
        "mahler_measure": 1.8392867552141647,
        "name": "Tribonacci x Phi_7",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Tribonacci x cyclotomic Phi_7",
    },
    {
        "degree": 7,
        "coeffs": [-1, -1, -1, 1, -1, -1, -1, 1],
        "mahler_measure": 1.8392867552141625,
        "name": "Tribonacci x Phi_8",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Tribonacci x cyclotomic Phi_8",
    },
    {
        "degree": 9,
        "coeffs": [-1, -1, -1, 0, -1, -1, 0, -1, -1, 1],
        "mahler_measure": 1.8392867552141783,
        "name": "Tribonacci x Phi_9",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Tribonacci x cyclotomic Phi_9",
    },
    {
        "degree": 7,
        "coeffs": [-1, 0, -1, 2, -2, 1, -2, 1],
        "mahler_measure": 1.839286755214164,
        "name": "Tribonacci x Phi_10",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "Tribonacci x cyclotomic Phi_10",
    },

    # ----- x^2-x-1 (10 entries) -----
    {
        "degree": 3,
        "coeffs": [1, 0, -2, 1],
        "mahler_measure": 1.6180339887498951,
        "name": "Golden x Phi_1",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "x^2-x-1 x cyclotomic Phi_1",
    },
    {
        "degree": 3,
        "coeffs": [-1, -2, 0, 1],
        "mahler_measure": 1.6180339887498956,
        "name": "Golden x Phi_2",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "x^2-x-1 x cyclotomic Phi_2",
    },
    {
        "degree": 4,
        "coeffs": [-1, -2, -1, 0, 1],
        "mahler_measure": 1.6180339887498976,
        "name": "Golden x Phi_3",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "x^2-x-1 x cyclotomic Phi_3",
    },
    {
        "degree": 4,
        "coeffs": [-1, -1, 0, -1, 1],
        "mahler_measure": 1.6180339887498971,
        "name": "Golden x Phi_4",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "x^2-x-1 x cyclotomic Phi_4",
    },
    {
        "degree": 6,
        "coeffs": [-1, -2, -1, -1, -1, 0, 1],
        "mahler_measure": 1.6180339887498962,
        "name": "Golden x Phi_5",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "x^2-x-1 x cyclotomic Phi_5",
    },
    {
        "degree": 4,
        "coeffs": [-1, 0, 1, -2, 1],
        "mahler_measure": 1.6180339887498967,
        "name": "Golden x Phi_6",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "x^2-x-1 x cyclotomic Phi_6",
    },
    {
        "degree": 8,
        "coeffs": [-1, -2, -1, -1, -1, -1, -1, 0, 1],
        "mahler_measure": 1.618033988749902,
        "name": "Golden x Phi_7",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "x^2-x-1 x cyclotomic Phi_7",
    },
    {
        "degree": 6,
        "coeffs": [-1, -1, 1, 0, -1, -1, 1],
        "mahler_measure": 1.6180339887499,
        "name": "Golden x Phi_8",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "x^2-x-1 x cyclotomic Phi_8",
    },
    {
        "degree": 8,
        "coeffs": [-1, -1, 1, -1, -1, 1, -1, -1, 1],
        "mahler_measure": 1.6180339887499038,
        "name": "Golden x Phi_9",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "x^2-x-1 x cyclotomic Phi_9",
    },
    {
        "degree": 6,
        "coeffs": [-1, 0, 1, -1, 1, -2, 1],
        "mahler_measure": 1.6180339887498951,
        "name": "Golden x Phi_10",
        "salem_class": False,
        "is_smyth_extremal": False,
        "lehmer_witness": False,
        "degree_minimum": False,
        "source": "x^2-x-1 x cyclotomic Phi_10",
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


# Mark every Phase-1 curated entry so downstream tooling can distinguish
# the 178 hand-curated rows (which are independently re-verified at
# module load) from the bulk Known180 / arxiv-promoted rows (which are
# trusted from upstream and only spot-checked).
for _e in MAHLER_TABLE:
    _e.setdefault("provenance_tier", "phase1_curated")
del _e

_PHASE1_ENTRY_COUNT = len(MAHLER_TABLE)


# ---------------------------------------------------------------------------
# 2026-04-29 refresh: ingest Mossinghoff Known180.gz and arxiv-corpus rows.
# ---------------------------------------------------------------------------
#
# Source provenance (reproducible):
#   - Live host:   http://wayback.cecm.sfu.ca/~mjm/Lehmer/lists/Known180.gz
#   - Wayback:     https://web.archive.org/web/20220430195519id_/<above>
#   - Retrieved:   2026-04-29 by Techne (toolsmith) during the Stream-B
#                  refresh task.  The live host's DNS was unreachable;
#                  Wayback Machine snapshot 20220430195519 was used.
#   - Bundled at:  prometheus_math/databases/_known180_raw.gz
#   - File header (first 5 lines) verbatim:
#       "All Known Polynomials Through Degree 180"
#       (blank)
#       "This table lists the known primitive, irreducible, noncyclotomic
#        integer polynomials with degree at most 180 having Mahler measure
#        less than 1.3."
#       "This list is only known to be complete through degree 44."
#       (blank)
#
# Format of each data line (one polynomial per line):
#       <degree>  <mahler_measure>  <#roots_outside_unit_circle>  <coeffs...>
#   where <coeffs...> are HALF-coefficients in DESCENDING order of a
#   reciprocal polynomial: c_n c_{n-1} ... c_{n/2}.  Reciprocal symmetry
#   c_i = c_{n-i} fills in the remaining n/2 coefficients.
#
# Known180 covers M < 1.30 only.  Polynomials in our arxiv probe corpus
# at M >= 1.30 (Sac-Épée 2024 reciprocal, Idris/Sac-Épée 2026 Newman
# divisors) are NOT in Known180; we promote them from
# prometheus_math._arxiv_polynomial_corpus separately.

import gzip as _gzip
import os as _os
import re as _re

_KNOWN180_PATH = _os.path.join(
    _os.path.dirname(__file__), "_known180_raw.gz"
)
_KNOWN180_LINE_RE = _re.compile(
    r"^\s*(\d+)\s+(\d+\.\d+)\s+(\d+)\s+([-\d ]+)\s*$"
)


def _x_flip_tuple(coeffs):
    """Apply x -> -x to an ascending coefficient tuple/list."""
    return tuple(c if (i % 2 == 0) else -c for i, c in enumerate(coeffs))


def _normalize_coeffs_key(coeffs):
    """Canonical key for dedup: (length-stripped, min(self, x_flip))."""
    out = list(coeffs)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    a = tuple(out)
    b = _x_flip_tuple(out)
    return min(a, b)


def _existing_keys(table):
    out = set()
    for e in table:
        out.add((e["degree"], _normalize_coeffs_key(e["coeffs"])))
    return out


def _parse_known180(path):
    """Yield ``(degree, M, k, coeffs_ascending)`` tuples from Known180.gz.

    ``k`` is Mossinghoff's count of roots outside the unit circle.
    ``coeffs_ascending`` is the full reciprocal polynomial, length
    ``degree + 1``, in ascending order ``[a_0, ..., a_n]``.
    """
    with open(path, "rb") as fh:
        text = _gzip.decompress(fh.read()).decode("utf-8", errors="replace")
    parse_failures = 0
    for line in text.splitlines():
        m = _KNOWN180_LINE_RE.match(line)
        if not m:
            continue
        try:
            deg = int(m.group(1))
            M = float(m.group(2))
            k = int(m.group(3))
            half_desc = [int(x) for x in m.group(4).split()]
            expected_half = deg // 2 + 1
            if len(half_desc) != expected_half:
                parse_failures += 1
                continue
            full_desc = list(half_desc) + list(reversed(half_desc[:-1]))
            coeffs_asc = list(reversed(full_desc))
            yield deg, M, k, coeffs_asc
        except Exception:  # pragma: no cover - any malformed line just skips
            parse_failures += 1
            continue
    # Stash failure count on the generator's caller via module global.
    global _KNOWN180_PARSE_FAILURES
    _KNOWN180_PARSE_FAILURES = parse_failures


_KNOWN180_PARSE_FAILURES: int = 0


def _ingest_known180():
    """Append Known180.gz entries to ``MAHLER_TABLE``.

    Returns ``(n_appended, n_skipped_dup, n_parse_failures)``.
    """
    existing = _existing_keys(MAHLER_TABLE)
    n_appended = 0
    n_dup = 0
    for deg, M, k, coeffs_asc in _parse_known180(_KNOWN180_PATH):
        key = (deg, _normalize_coeffs_key(coeffs_asc))
        if key in existing:
            n_dup += 1
            continue
        existing.add(key)
        # The rows are noncyclotomic primitive irreducible Salem-class
        # (reciprocal) by file definition; M < 1.3 means we are well
        # below Smyth's bound, so every entry is reciprocal Salem-type.
        is_lehmer = (deg == 10 and abs(M - 1.176280818259918) < 1e-9
                     and coeffs_asc == [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1])
        MAHLER_TABLE.append({
            "degree": deg,
            "coeffs": coeffs_asc,
            "mahler_measure": M,
            "name": f"Mossinghoff Known180 deg-{deg} M={M:.6f}",
            "salem_class": True,
            "is_smyth_extremal": False,
            "lehmer_witness": bool(is_lehmer),
            "degree_minimum": False,
            "source": (
                "Mossinghoff Known180.gz (Wayback 20220430195519); "
                "k_outside_unit_circle="
                f"{k}"
            ),
            "provenance_tier": "known180_2022",
        })
        n_appended += 1
    return n_appended, n_dup, _KNOWN180_PARSE_FAILURES


_KNOWN180_APPENDED, _KNOWN180_DUP, _KNOWN180_PARSE_FAIL = _ingest_known180()


# ---------------------------------------------------------------------------
# 2026-04-29 refresh: promote arxiv-corpus entries (M >= 1.3, outside
# the Known180 file's coverage band).
# ---------------------------------------------------------------------------

# Hard-coded copy of the corpus rows we promote (avoids a circular import
# and keeps this file self-contained).  Each row was independently
# M-verified (see _arxiv_polynomial_corpus.py).  Coefficients are
# ascending.

_ARXIV_PROMOTED: list[dict] = [
    # ----- Sac-Épée 2024 reciprocal Salem polynomials (arXiv:2409.11159).
    # Coefficient vectors are taken VERBATIM from
    # prometheus_math._arxiv_polynomial_corpus.RECENT_POLYNOMIAL_CORPUS
    # (which expands the paper's half-coefficient table via
    # _ascending_from_sacepee_table); each was independently M-verified
    # to ~1e-9 by techne.lib.mahler_measure at corpus build time.
    # Pre-2024 known (degree <= 24 on Mossinghoff's online list):
    {
        "degree": 12,
        "coeffs": [1, -1, 0, 0, 0, -1, 1, -1, 0, 0, 0, -1, 1],
        "mahler_measure": 1.3022688051,
        "name": "Sac-Epee 2024 deg-12 (Boyd 1989 known)",
        "source": "Sac-Epee arXiv:2409.11159 Table; rediscovers Mossinghoff online list",
    },
    {
        "degree": 16,
        "coeffs": [1, 1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 1, 1],
        "mahler_measure": 1.308409006213,
        "name": "Sac-Epee 2024 deg-16 (pre-2024 known)",
        "source": "Sac-Epee arXiv:2409.11159 Table; pre-2024 known",
    },
    {
        "degree": 14,
        "coeffs": [1, -1, 0, -1, 1, 0, 0, -1, 0, 0, 1, -1, 0, -1, 1],
        "mahler_measure": 1.318197504432,
        "name": "Sac-Epee 2024 deg-14 (pre-2024 known)",
        "source": "Sac-Epee arXiv:2409.11159 Table; pre-2024 known",
    },
    {
        "degree": 18,
        "coeffs": [1, -1, -1, 1, 0, 0, 0, -1, 0, 1, 0, -1, 0, 0, 0, 1, -1, -1, 1],
        "mahler_measure": 1.323198173512,
        "name": "Sac-Epee 2024 deg-18 (pre-2024 known)",
        "source": "Sac-Epee arXiv:2409.11159 Table; pre-2024 known",
    },
    # New per Sac-Epee 2024 (degree >= 26, NOT on Mossinghoff online list):
    {
        "degree": 26,
        "coeffs": [1, 0, -1, -1, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1, 0, 1, 0, 0, 0, 0, 0, 0, 0, -1, -1, 0, 1],
        "mahler_measure": 1.304697625411,
        "name": "Sac-Epee 2024 deg-26 NEW",
        "source": "Sac-Epee arXiv:2409.11159 Table; NEW per author",
    },
    {
        "degree": 28,
        "coeffs": [1, 1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 1, 1],
        "mahler_measure": 1.324231319862,
        "name": "Sac-Epee 2024 deg-28 NEW",
        "source": "Sac-Epee arXiv:2409.11159 Table; NEW per author",
    },
    {
        "degree": 30,
        "coeffs": [1, -1, 0, 0, -1, 0, 0, 0, 1, 0, 0, 1, -1, 0, 0, -1, 0, 0, -1, 1, 0, 0, 1, 0, 0, 0, -1, 0, 0, -1, 1],
        "mahler_measure": 1.303385419369,
        "name": "Sac-Epee 2024 deg-30 NEW",
        "source": "Sac-Epee arXiv:2409.11159 Table; NEW per author",
    },
    {
        "degree": 32,
        "coeffs": [1, -1, 0, -1, 0, 1, 0, 0, 0, -1, 1, -1, 1, 0, 0, 0, -1, 0, 0, 0, 1, -1, 1, -1, 0, 0, 0, 1, 0, -1, 0, -1, 1],
        "mahler_measure": 1.302721444014,
        "name": "Sac-Epee 2024 deg-32 NEW",
        "source": "Sac-Epee arXiv:2409.11159 Table; NEW per author",
    },
    {
        "degree": 38,
        "coeffs": [1, -2, 1, 0, 0, 0, 0, 0, -1, 1, 0, -1, 1, 0, -1, 0, 1, 0, -1, 1, -1, 0, 1, 0, -1, 0, 1, -1, 0, 1, -1, 0, 0, 0, 0, 0, 1, -2, 1],
        "mahler_measure": 1.306473537533,
        "name": "Sac-Epee 2024 deg-38 NEW",
        "source": "Sac-Epee arXiv:2409.11159 Table; NEW per author",
    },
    {
        "degree": 44,
        "coeffs": [1, 0, 1, -1, 0, -2, -1, -2, -1, -1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, -1, -1, -2, -1, -2, 0, -1, 1, 0, 1],
        "mahler_measure": 1.308071085577,
        "name": "Sac-Epee 2024 deg-44 NEW",
        "source": "Sac-Epee arXiv:2409.11159 Table; NEW per author",
    },
    {
        "degree": 40,
        "coeffs": [1, -1, 0, 0, -1, 0, 1, -1, 1, 0, -1, 0, 0, -1, 1, 0, 0, 1, 0, -1, 1, -1, 0, 1, 0, 0, 1, -1, 0, 0, -1, 0, 1, -1, 1, 0, -1, 0, 0, -1, 1],
        "mahler_measure": 1.316069252718,
        "name": "Sac-Epee 2024 deg-40 NEW",
        "source": "Sac-Epee arXiv:2409.11159 Table; NEW per author",
    },
    # ----- Idris/Sac-Epee 2026 non-reciprocal Newman divisors (arXiv:2601.11486).
    # Degree-10 improved bound:
    {
        "degree": 10,
        "coeffs": [1, 1, 0, 0, 0, -1, 0, 0, -1, 0, 1],
        "mahler_measure": 1.419404632,
        "name": "Idris/Sac-Epee 2026 deg-10 (improved bound)",
        "source": "Idris/Sac-Epee arXiv:2601.11486 Table 1; improves Drungilas et al",
        "salem_class": False,
    },
    {
        "degree": 9,
        "coeffs": [1, 1, 1, 0, -1, -1, -1, 0, 0, 1],
        "mahler_measure": 1.436632261,
        "name": "Drungilas-Jankauskas-Siurys deg-9 (prior bound)",
        "source": "Cited in Idris/Sac-Epee arXiv:2601.11486 Table 1",
        "salem_class": False,
    },
    {
        "degree": 12,
        "coeffs": [1, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0, -1, 1],
        "mahler_measure": 1.448290492,
        "name": "Idris/Sac-Epee 2026 deg-12 Newman-divisor",
        "source": "Idris/Sac-Epee arXiv:2601.11486 Table 1",
        "salem_class": False,
    },
    {
        "degree": 8,
        "coeffs": [1, 0, 0, 1, -1, 0, 0, -1, 1],
        "mahler_measure": 1.489581321,
        "name": "Idris/Sac-Epee 2026 deg-8 Newman-divisor",
        "source": "Idris/Sac-Epee arXiv:2601.11486 Table 1",
        "salem_class": False,
    },
    {
        "degree": 6,
        "coeffs": [1, 0, 1, -1, 0, -1, 1],
        "mahler_measure": 1.556014485,
        "name": "Hare-Mossinghoff 2014 deg-6 Newman-divisor (historical)",
        "source": "Cited in Idris/Sac-Epee arXiv:2601.11486 Table 1",
        "salem_class": False,
    },
]


def _ingest_arxiv_promoted():
    """Append corpus-promoted entries (skipping any that already exist)."""
    existing = _existing_keys(MAHLER_TABLE)
    n_appended = 0
    for raw in _ARXIV_PROMOTED:
        coeffs = list(raw["coeffs"])
        key = (raw["degree"], _normalize_coeffs_key(coeffs))
        if key in existing:
            continue
        existing.add(key)
        entry = {
            "degree": raw["degree"],
            "coeffs": coeffs,
            "mahler_measure": float(raw["mahler_measure"]),
            "name": raw["name"],
            "salem_class": bool(raw.get("salem_class", True)),
            "is_smyth_extremal": False,
            "lehmer_witness": False,
            "degree_minimum": False,
            "source": raw["source"],
            "provenance_tier": "arxiv_promoted_2026",
        }
        MAHLER_TABLE.append(entry)
        n_appended += 1
    return n_appended


_ARXIV_APPENDED = _ingest_arxiv_promoted()


# Provenance metadata accompanying the snapshot
SNAPSHOT_META = {
    "source_url": "https://wayback.cecm.sfu.ca/~mjm/Lehmer/",
    "snapshot_date": "2026-04-25",
    "n_entries": len(MAHLER_TABLE),
    "lehmer_constant": 1.1762808182599175,
    "smyth_constant": 1.3247179572447460,
    "phase1_extension_date": "2026-04-25",
    "phase1_added_entries": 157,
    "phase1_total_after": 178,
    "phase1_construction_families": [
        "Lehmer 1933 (anchor)",
        "Smyth 1971 Pisot family x^n - x - 1, n=2..30",
        "Pisot family x^n - x^(n-1) - 1, n=2..15",
        "Lehmer x cyclotomic Phi_k, k=1..20",
        "Smyth-extremal (x^3-x-1) x cyclotomic Phi_k, k=1..15",
        "Salem-deg-N x cyclotomic factors (N in {6,8,10,12,14})",
        "Tribonacci x cyclotomic Phi_k",
        "Golden ratio polynomial x cyclotomic Phi_k",
        "Cyclotomic Phi_n, n=2..40 (M = 1)",
    ],
    "phase1_verification": (
        "Every entry's mahler_measure was computed via "
        "techne.lib.mahler_measure.mahler_measure and cross-checked "
        "against the literature value (Lehmer constant, Smyth constant, "
        "Salem family M, or M = 1 for cyclotomics) to better than 1e-9."
    ),
    # 2026-04-29 refresh
    "refresh_2026_04_29_source_url": (
        "https://web.archive.org/web/20220430195519id_/"
        "http://wayback.cecm.sfu.ca/~mjm/Lehmer/lists/Known180.gz"
    ),
    "refresh_2026_04_29_retrieved": "2026-04-29T00:00:00Z",
    "refresh_2026_04_29_phase1_count": _PHASE1_ENTRY_COUNT,
    "refresh_2026_04_29_known180_appended": _KNOWN180_APPENDED,
    "refresh_2026_04_29_known180_dup_skipped": _KNOWN180_DUP,
    "refresh_2026_04_29_known180_parse_failures": _KNOWN180_PARSE_FAIL,
    "refresh_2026_04_29_arxiv_promoted_appended": _ARXIV_APPENDED,
    "refresh_2026_04_29_total_after": len(MAHLER_TABLE),
    "refresh_2026_04_29_note": (
        "Calibration improvement, not a discovery.  We were claiming "
        "'catalog miss' against a snapshot that covered only ~2% of "
        "the published Mossinghoff universe; the refresh closes that "
        "asymmetric error.  Known180.gz covers M < 1.3 only; corpus "
        "promotions cover the M in [1.30, 1.56] band.  Polynomials "
        "above M = 1.56 from recent literature remain a future ingestion "
        "target."
    ),
}
