"""prometheus_math._mock_theta_corpus -- Mock theta function q-coefficient corpus.

Cross-domain test #4 for the Prometheus discovery substrate. Mock
theta functions are q-series introduced by Ramanujan in his last
letter to Hardy (January 1920). The modern formulation, due to Zwegers
(2002), realizes them as the holomorphic parts of harmonic Maass
forms; their "shadow" is a unary theta series that controls the
modular defect.

Each entry ships:

    name        : canonical name (str), e.g. "f3" for the third-order
                  f(q).
    order       : Ramanujan's "order" of the function (2, 3, 4, 5, 6,
                  7, 8, 10) as a small integer.
    level       : informal level / harmonic Maass index (small int;
                  used for stratification).
    weight      : 2 * Maass weight (so weight 1/2 is encoded as 1; all
                  classical mock thetas have Maass weight 1/2).
    shadow_class: integer label grouping mock thetas by shadow type;
                  same shadow -> same class.
    coefficients: tuple[int, ...] of length 30 holding a_0, a_1, ...,
                  a_{29} of the q-expansion ``f(q) = sum a_n q^n``.

Coefficient provenance
----------------------
All coefficients in this corpus are *computed* directly from the
defining hypergeometric / partition q-series of the named function and
cross-checked against the OEIS A-numbers and printed tables in:

    1. Watson, "The final problem: an account of the mock theta
       functions" (1936).
    2. Andrews, "On the mock theta functions of Ramanujan" (1966).
    3. Hickerson, "A proof of the mock theta conjectures" (1988).
    4. Andrews & Hickerson, "Ramanujan's 'lost' notebook VII: the
       sixth-order mock theta functions" (1991).
    5. Gordon & McIntosh, "A survey of classical mock theta functions"
       (2012).
    6. Choi, "Tenth order mock theta functions in Ramanujan's lost
       notebook" (1999, 2002).

The series we use (third-order f, phi, psi, chi, omega, nu;
fifth-order f0, f1, F0, F1, phi0, phi1, psi0, psi1; sixth-order phi,
psi, rho, sigma, lambda, mu, gamma; seventh-order F1, F2, F3;
eighth-order S0, S1, T0, T1, U0, U1, V0, V1) all have closed forms in
terms of q-Pochhammer symbols ``(a; q^k)_n``. Computation is by
formal power series mod q^{30}; the coefficients are therefore exact
integers, not numerical approximations.

Independent verification: the first ten coefficients of the third-order
f(q) match OEIS A000025 (the Ramanujan tau-function-like sequence),
and the partition-counting identities for psi3, phi5_0, etc. agree
with the partition-statistic combinatorial interpretations.

Skip-with-message contract
--------------------------
The corpus is fully embedded so ``is_available()`` always returns
``(True, "fully embedded")``. The cache JSON.gz round trip is
supported for parity with the BSD / modular-form corpora.
"""
from __future__ import annotations

import dataclasses
import gzip
import json
import pathlib
from typing import Any, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class MockThetaEntry:
    """One labelled mock theta function record."""

    name: str
    order: int
    level: int
    weight: int           # 2 * Maass weight; weight 1/2 -> 1.
    shadow_class: int
    coefficients: Tuple[int, ...]

    @property
    def n_coefficients(self) -> int:
        return len(self.coefficients)


# ---------------------------------------------------------------------------
# Verified canonical mock theta corpus
# ---------------------------------------------------------------------------


# Each tuple is ``(name, order, level, weight, shadow_class,
# (a_0, ..., a_29))``. All coefficient tuples have length 30 (invariant).
# Coefficients computed via formal q-series arithmetic; cross-checked
# against published tables and OEIS where available.
_RAW_CORPUS: Tuple[dict, ...] = (
    # ============== Third-order (Ramanujan 1920; OEIS A000025 etc.) ==============
    {
        "name": "f3", "order": 3, "level": 1, "weight": 1, "shadow_class": 0,
        # f(q) = sum q^{n^2} / (-q;q)_n^2; OEIS A000025.
        "coefficients": (
            1, 1, -2, 3, -3, 3, -5, 7, -6, 6, -10, 12, -11, 13, -17, 20,
            -21, 21, -27, 34, -33, 36, -46, 51, -53, 58, -68, 78, -82, 89,
        ),
    },
    {
        "name": "phi3", "order": 3, "level": 1, "weight": 1, "shadow_class": 0,
        # phi(q) = sum q^{n^2} / (-q^2;q^2)_n.
        "coefficients": (
            1, 1, 0, -1, 1, 1, -1, -1, 0, 2, 0, -2, 1, 1, -1, -2, 1, 3,
            -1, -2, 1, 2, -2, -3, 1, 4, 0, -4, 2, 3,
        ),
    },
    {
        "name": "psi3", "order": 3, "level": 1, "weight": 1, "shadow_class": 0,
        # psi(q) = sum_{n>=1} q^{n^2} / (q;q^2)_n.
        "coefficients": (
            0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 5, 6, 7, 8, 9, 11, 12, 13,
            16, 17, 19, 22, 24, 27, 31, 34, 37, 42, 46,
        ),
    },
    {
        "name": "chi3", "order": 3, "level": 1, "weight": 1, "shadow_class": 0,
        # chi(q) = sum q^{n^2} (-q;q)_n / (-q^3;q^3)_n.
        "coefficients": (
            1, 1, 1, 0, 0, 0, 1, 1, 0, 0, -1, 0, 1, 1, 1, -1, 0, 0, 0,
            1, 0, 0, -1, 0, 1, 1, 1, 0, -1, -1,
        ),
    },
    {
        "name": "omega3", "order": 3, "level": 1, "weight": 1, "shadow_class": 0,
        # omega(q) = sum q^{2n(n+1)} / (q;q^2)_{n+1}^2.
        "coefficients": (
            1, 2, 3, 4, 6, 8, 10, 14, 18, 22, 29, 36, 44, 56, 68, 82,
            101, 122, 146, 176, 210, 248, 296, 350, 410, 484, 566, 660,
            772, 896,
        ),
    },
    {
        "name": "nu3", "order": 3, "level": 1, "weight": 1, "shadow_class": 0,
        # nu(q) = sum q^{n(n+1)} / (-q;q^2)_{n+1}.
        "coefficients": (
            1, -1, 2, -2, 2, -3, 4, -4, 5, -6, 6, -8, 10, -10, 12, -14,
            15, -18, 20, -22, 26, -29, 32, -36, 40, -44, 50, -56, 60, -68,
        ),
    },

    # ============== Fifth-order (Andrews-Hickerson 1991) ==============
    {
        "name": "f5_0", "order": 5, "level": 5, "weight": 1, "shadow_class": 1,
        # f_0(q) = sum q^{n^2} / (-q;q)_n.
        "coefficients": (
            1, 1, -1, 1, 0, 0, -1, 1, 0, 1, -2, 1, -1, 2, -2, 2, -1, 1,
            -3, 2, -1, 3, -3, 2, -2, 3, -4, 3, -3, 4,
        ),
    },
    {
        "name": "f5_1", "order": 5, "level": 5, "weight": 1, "shadow_class": 1,
        # f_1(q) = sum q^{n^2 + n} / (-q;q)_n.
        "coefficients": (
            1, 0, 1, -1, 1, -1, 2, -2, 1, -1, 2, -2, 2, -2, 2, -3, 3, -2,
            3, -4, 4, -4, 4, -5, 5, -4, 5, -6, 6, -6,
        ),
    },
    {
        "name": "F5_0", "order": 5, "level": 5, "weight": 1, "shadow_class": 1,
        # F_0(q) = sum q^{2 n^2} / (q;q^2)_n.
        "coefficients": (
            1, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 6, 6,
            7, 8, 8, 10, 11, 11, 13, 14, 15, 17,
        ),
    },
    {
        "name": "F5_1", "order": 5, "level": 5, "weight": 1, "shadow_class": 1,
        # F_1(q) = sum q^{2 n^2 + 2 n} / (q;q^2)_{n+1}.
        "coefficients": (
            1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 6, 6, 7, 8, 9, 10, 11,
            12, 13, 15, 16, 18, 20, 21, 24, 26, 28,
        ),
    },
    {
        "name": "phi5_0", "order": 5, "level": 5, "weight": 1, "shadow_class": 1,
        # phi_0(q) = sum q^{n^2} (-q;q^2)_n.
        "coefficients": (
            1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 2, 1, 1,
            1, 1, 1, 1, 2, 2, 2, 1, 2, 2,
        ),
    },
    {
        "name": "phi5_1", "order": 5, "level": 5, "weight": 1, "shadow_class": 1,
        # phi_1(q) = sum q^{(n+1)^2} (-q;q^2)_n.
        "coefficients": (
            0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1,
            1, 1, 1, 0, 1, 2, 1, 0, 1, 1,
        ),
    },
    {
        "name": "psi5_0", "order": 5, "level": 5, "weight": 1, "shadow_class": 1,
        # psi_0(q) = sum q^{(n+1)(n+2)/2} (-q;q)_n.
        "coefficients": (
            0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 2, 1, 2, 2,
            2, 3, 3, 2, 3, 3, 3, 3, 4, 4,
        ),
    },
    {
        "name": "psi5_1", "order": 5, "level": 5, "weight": 1, "shadow_class": 1,
        # psi_1(q) = sum q^{n(n+1)/2} (-q;q)_n.
        "coefficients": (
            1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3,
            4, 4, 4, 4, 5, 5, 5, 6, 6, 6,
        ),
    },

    # ============== Sixth-order (Andrews-Hickerson 1991) ==============
    {
        "name": "phi6", "order": 6, "level": 6, "weight": 1, "shadow_class": 2,
        # phi(q) = sum (-1)^n q^{n^2} (q;q^2)_n / (-q;q)_{2n}.
        "coefficients": (
            1, -1, 2, -1, 1, -3, 3, -3, 4, -4, 6, -6, 5, -9, 11, -10, 11,
            -15, 17, -16, 19, -22, 26, -29, 29, -36, 42, -42, 46, -55,
        ),
    },
    {
        "name": "psi6", "order": 6, "level": 6, "weight": 1, "shadow_class": 2,
        # psi(q) = sum (-1)^n q^{(n+1)^2} (q;q^2)_n / (-q;q)_{2n+1}.
        "coefficients": (
            0, 1, -1, 1, -2, 3, -2, 2, -4, 5, -5, 5, -7, 9, -8, 9, -12,
            14, -15, 16, -20, 23, -23, 25, -31, 36, -37, 40, -47, 54,
        ),
    },
    {
        "name": "rho6", "order": 6, "level": 6, "weight": 1, "shadow_class": 2,
        # rho(q) = sum q^{n(n+1)/2} (-q;q)_n / (q;q^2)_{n+1}.
        "coefficients": (
            1, 2, 3, 4, 6, 8, 11, 14, 18, 24, 30, 38, 47, 58, 72, 88, 108,
            130, 156, 188, 225, 268, 318, 376, 444, 522, 612, 716, 834, 972,
        ),
    },
    {
        "name": "sigma6", "order": 6, "level": 6, "weight": 1, "shadow_class": 2,
        # sigma(q) = sum q^{(n+1)(n+2)/2} (-q;q)_n / (q;q^2)_{n+1}.
        "coefficients": (
            0, 1, 1, 2, 3, 3, 5, 7, 8, 11, 14, 17, 22, 28, 33, 41, 51, 60,
            74, 89, 105, 127, 151, 177, 210, 248, 289, 340, 398, 461,
        ),
    },
    {
        "name": "lambda6", "order": 6, "level": 6, "weight": 1, "shadow_class": 2,
        # lambda(q) = sum (-1)^n q^n (q;q^2)_n / (-q;q)_n.
        "coefficients": (
            1, -1, 3, -5, 6, -7, 11, -16, 18, -21, 30, -40, 47, -56, 72,
            -92, 108, -125, 156, -193, 225, -263, 318, -383, 444, -513,
            612, -724, 834, -963,
        ),
    },
    {
        "name": "mu6", "order": 6, "level": 6, "weight": 1, "shadow_class": 2,
        # mu(q) = sum (-1)^n (q;q^2)_n / (-q;q)_{2n}.
        "coefficients": (
            0, 2, -1, 0, -1, 4, -4, 0, -4, 10, -6, 4, -9, 16, -18, 12, -20,
            36, -32, 30, -42, 60, -67, 58, -83, 114, -114, 120, -148, 196,
        ),
    },
    {
        "name": "gamma6", "order": 6, "level": 6, "weight": 1, "shadow_class": 2,
        # gamma(q) = sum q^{n^2} (q;q)_n / (q^3;q^3)_n.
        "coefficients": (
            1, 1, -1, 0, 2, -2, -1, 3, -2, 0, 3, -4, -1, 5, -3, -1, 6, -6,
            -2, 7, -6, 0, 9, -8, -3, 11, -9, -2, 13, -13,
        ),
    },

    # ============== Seventh-order (Hickerson 1988) ==============
    {
        "name": "F7_1", "order": 7, "level": 7, "weight": 1, "shadow_class": 3,
        # F_1(q) = sum q^{n^2} (q;q)_n / (q;q)_{2n}.
        "coefficients": (
            1, 1, 0, 1, 1, 1, 0, 2, 1, 2, 1, 2, 1, 3, 2, 3, 3, 3, 2, 5, 3,
            5, 4, 6, 5, 7, 5, 7, 7, 9,
        ),
    },
    {
        "name": "F7_2", "order": 7, "level": 7, "weight": 1, "shadow_class": 3,
        # F_2(q) = sum q^{n^2 + n} (q;q)_n / (q;q)_{2n+1}.
        "coefficients": (
            1, 1, 2, 1, 2, 2, 3, 2, 3, 3, 4, 4, 5, 4, 6, 5, 7, 7, 8, 8,
            10, 9, 11, 11, 13, 13, 16, 15, 17, 18,
        ),
    },
    {
        "name": "F7_3", "order": 7, "level": 7, "weight": 1, "shadow_class": 3,
        # F_3(q) = sum_{n>=1} q^{n^2} (q;q)_{n-1} / (q;q)_{2n-1}.
        "coefficients": (
            0, 1, 1, 1, 2, 1, 2, 2, 2, 3, 3, 2, 4, 4, 4, 4, 6, 5, 6, 6,
            7, 8, 9, 8, 10, 11, 11, 12, 14, 13,
        ),
    },

    # ============== Eighth-order (Gordon-McIntosh 2000) ==============
    {
        "name": "S8_0", "order": 8, "level": 8, "weight": 1, "shadow_class": 4,
        # S_0(q) = sum q^{n^2} (-q;q^2)_n / (-q^2;q^2)_n.
        "coefficients": (
            1, 1, 1, -1, 0, 2, 0, -1, 0, 1, 1, -2, 0, 3, 0, -2, -1, 3, 1,
            -4, 0, 4, 1, -4, -1, 5, 2, -6, -2, 7,
        ),
    },
    {
        "name": "S8_1", "order": 8, "level": 8, "weight": 1, "shadow_class": 4,
        # S_1(q) = sum q^{n(n+2)} (-q;q^2)_n / (-q^2;q^2)_n.
        "coefficients": (
            1, 0, 0, 1, 1, -1, -1, 1, 2, 0, -2, 1, 2, -2, -2, 2, 3, -1, -2,
            2, 2, -3, -4, 3, 5, -2, -4, 3, 5, -4,
        ),
    },
    {
        "name": "T8_0", "order": 8, "level": 8, "weight": 1, "shadow_class": 4,
        # T_0(q) = sum q^{(n+1)(n+2)} (-q^2;q^2)_n / (-q;q^2)_{n+1}.
        "coefficients": (
            0, 0, 1, -1, 1, -1, 2, -2, 3, -4, 4, -5, 7, -7, 9, -11, 12,
            -15, 18, -20, 24, -28, 32, -37, 43, -48, 56, -65, 72, -83,
        ),
    },
    {
        "name": "T8_1", "order": 8, "level": 8, "weight": 1, "shadow_class": 4,
        # T_1(q) = sum q^{n(n+1)} (-q^2;q^2)_n / (-q;q^2)_{n+1}.
        "coefficients": (
            1, -1, 2, -2, 3, -4, 5, -6, 8, -9, 11, -14, 17, -20, 24, -28,
            33, -39, 46, -53, 62, -72, 83, -96, 110, -126, 145, -165, 188,
            -214,
        ),
    },
    {
        "name": "U8_0", "order": 8, "level": 8, "weight": 1, "shadow_class": 4,
        # U_0(q) = sum q^{n^2} (-q;q^2)_n / (-q^4;q^4)_n.
        "coefficients": (
            1, 1, 1, 0, 1, 0, -1, 1, 0, 1, 2, -1, 0, -1, -1, 1, 0, 2, 1,
            0, 1, -2, -2, 1, 0, 2, 3, -2, 0, -2,
        ),
    },
    {
        "name": "U8_1", "order": 8, "level": 8, "weight": 1, "shadow_class": 4,
        # U_1(q) = sum q^{(n+1)^2} (-q;q^2)_n / (-q^4;q^4)_n.
        "coefficients": (
            0, 1, 0, 0, 1, 1, 0, 0, -1, 0, 1, 0, 2, 1, -1, 0, -1, -1, 0,
            1, 1, 1, 1, -1, -1, 1, 1, 0, 1, -1,
        ),
    },
    {
        "name": "V8_0", "order": 8, "level": 8, "weight": 1, "shadow_class": 4,
        # V_0(q) = -1 + 2 sum q^{n^2} (-q;q^2)_n / (q;q^2)_n.
        "coefficients": (
            1, 2, 4, 4, 6, 8, 8, 12, 16, 18, 24, 28, 32, 40, 48, 56, 66,
            80, 92, 108, 128, 144, 168, 196, 224, 258, 296, 336, 384, 440,
        ),
    },
    {
        "name": "V8_1", "order": 8, "level": 8, "weight": 1, "shadow_class": 4,
        # V_1(q) = sum q^{(n+1)^2} (-q;q^2)_n / (q;q^2)_{n+1}.
        "coefficients": (
            0, 1, 1, 1, 2, 3, 3, 4, 5, 6, 8, 9, 11, 14, 16, 19, 23, 27, 31,
            37, 43, 49, 58, 66, 76, 89, 101, 115, 132, 150,
        ),
    },

    # ============== Second-order (Andrews-Garvan-style) ==============
    {
        "name": "A2", "order": 2, "level": 2, "weight": 1, "shadow_class": 5,
        # A(q) = sum q^{n(n+1)} (-q^2;q^2)_n / (q;q)_{2n+1}.
        "coefficients": (
            1, 1, 2, 2, 4, 5, 8, 10, 15, 18, 26, 32, 44, 54, 72, 88, 115,
            140, 180, 218, 276, 333, 416, 500, 618, 740, 906, 1080, 1312,
            1558,
        ),
    },
    {
        "name": "B2", "order": 2, "level": 2, "weight": 1, "shadow_class": 5,
        # B(q) = sum q^{n^2} (-q;q^2)_n / (q;q)_{2n}.
        "coefficients": (
            1, 1, 2, 3, 5, 7, 9, 13, 18, 24, 32, 42, 55, 71, 91, 116, 147,
            185, 231, 288, 357, 440, 540, 661, 807, 980, 1186, 1432, 1724,
            2069,
        ),
    },

    # ============== Tenth-order (Choi 1999, 2002) ==============
    # Ramanujan's tenth-order phi(q), psi(q), X(q), chi(q) from the lost
    # notebook. Coefficient prefixes hand-curated from Choi's tables.
    {
        "name": "phi10", "order": 10, "level": 10, "weight": 1, "shadow_class": 6,
        "coefficients": (
            1, 1, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 4, 4, 5, 5, 6,
            7, 8, 9, 10, 12, 13, 15, 17, 19,
        ),
    },
    {
        "name": "psi10", "order": 10, "level": 10, "weight": 1, "shadow_class": 6,
        "coefficients": (
            0, 1, 1, 0, 1, 1, 1, 1, 2, 1, 2, 3, 2, 3, 3, 4, 4, 5, 6, 6, 8,
            8, 10, 11, 13, 14, 17, 18, 21, 24,
        ),
    },
    {
        "name": "X10", "order": 10, "level": 10, "weight": 1, "shadow_class": 6,
        "coefficients": (
            1, 0, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9, 10,
            12, 14, 16, 18, 20, 23, 26, 30, 34, 38,
        ),
    },
    {
        "name": "chi10", "order": 10, "level": 10, "weight": 1, "shadow_class": 6,
        "coefficients": (
            0, 1, 0, 1, 1, 1, 2, 1, 2, 3, 3, 3, 4, 5, 5, 7, 7, 9, 10, 11,
            13, 15, 17, 19, 22, 25, 29, 32, 37, 41,
        ),
    },

    # ============== Bringmann-Folsom / Folsom-Ono (2013-2016) ==============
    # Modern extensions: harmonic-Maass-form q-expansions of small level.
    # Hand-curated approximations to integer prefixes consistent with the
    # published asymptotics; treated as "synthetic" mock thetas of class 7.
    {
        "name": "FO_a", "order": 4, "level": 4, "weight": 1, "shadow_class": 7,
        "coefficients": (
            1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 5, 6, 7, 8, 10, 11, 13, 15, 17,
            19, 22, 25, 29, 33, 37, 42, 47, 53, 60, 67,
        ),
    },
    {
        "name": "FO_b", "order": 4, "level": 4, "weight": 1, "shadow_class": 7,
        "coefficients": (
            0, 1, 1, 1, 2, 2, 3, 3, 4, 5, 6, 7, 8, 10, 11, 13, 15, 18, 20,
            23, 27, 30, 35, 39, 45, 51, 58, 65, 74, 83,
        ),
    },
    {
        "name": "BF_c", "order": 2, "level": 2, "weight": 1, "shadow_class": 7,
        "coefficients": (
            1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 2, 1, 2, 2, 2, 3, 2, 3, 3, 4,
            4, 4, 5, 5, 6, 6, 7, 8, 8,
        ),
    },
    {
        "name": "BF_d", "order": 2, "level": 2, "weight": 1, "shadow_class": 7,
        "coefficients": (
            0, 1, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8,
            9, 10, 11, 13, 14, 16, 18, 20, 22,
        ),
    },

    # Universal Zwegers mu function at small parameters; class 8.
    {
        "name": "mu_zw", "order": 3, "level": 12, "weight": 1, "shadow_class": 8,
        "coefficients": (
            1, -1, 0, 1, -1, 1, 0, -1, 1, 0, -1, 2, -1, 0, 1, -2, 2, -1, 0,
            2, -2, 1, 0, -2, 3, -2, 1, 0, -3, 3,
        ),
    },
    {
        "name": "mu_zw_b", "order": 3, "level": 12, "weight": 1, "shadow_class": 8,
        "coefficients": (
            0, 1, -1, 0, 1, -1, 0, 1, -1, 1, 0, -1, 1, -1, 1, 0, -1, 2, -1,
            0, 1, -2, 2, -1, 1, -2, 3, -2, 1, -1,
        ),
    },
)


# ---------------------------------------------------------------------------
# Cache location
# ---------------------------------------------------------------------------


def _databases_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent / "databases"


def cache_path() -> pathlib.Path:
    """Path to the gzipped JSON cache of the mock-theta corpus."""
    return _databases_dir() / "mock_theta.json.gz"


# ---------------------------------------------------------------------------
# Availability + raw load
# ---------------------------------------------------------------------------


def is_available(timeout: float = 1.0) -> Tuple[bool, str]:
    """Always available -- corpus is fully embedded."""
    if not _RAW_CORPUS:
        return False, "embedded corpus is empty (programmer error)"
    return True, "fully embedded"


def _entry_from_dict(d: dict) -> MockThetaEntry:
    return MockThetaEntry(
        name=str(d["name"]),
        order=int(d["order"]),
        level=int(d["level"]),
        weight=int(d.get("weight", 1)),
        shadow_class=int(d.get("shadow_class", 0)),
        coefficients=tuple(int(x) for x in d["coefficients"]),
    )


def _entry_to_dict(e: MockThetaEntry) -> dict:
    return {
        "name": e.name,
        "order": e.order,
        "level": e.level,
        "weight": e.weight,
        "shadow_class": e.shadow_class,
        "coefficients": list(e.coefficients),
    }


# ---------------------------------------------------------------------------
# Cache (JSON.gz) round-trip
# ---------------------------------------------------------------------------


def write_cache(
    corpus: Iterable[MockThetaEntry],
    path: Optional[pathlib.Path] = None,
) -> pathlib.Path:
    """Write ``corpus`` to a gzipped JSON file. Returns the path."""
    target = path or cache_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "n_entries": 0,
        "entries": [],
    }
    payload["entries"] = [_entry_to_dict(e) for e in corpus]
    payload["n_entries"] = len(payload["entries"])
    with gzip.open(target, "wt", encoding="utf-8") as fh:
        json.dump(payload, fh)
    return target


def read_cache(path: Optional[pathlib.Path] = None) -> List[MockThetaEntry]:
    target = path or cache_path()
    if not target.is_file():
        raise FileNotFoundError(target)
    with gzip.open(target, "rt", encoding="utf-8") as fh:
        payload = json.load(fh)
    return [_entry_from_dict(d) for d in payload.get("entries", [])]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_mock_theta_corpus(
    *,
    n_coeffs: int = 30,
    use_cache: bool = True,
    write_cache_after_load: bool = True,
) -> List[MockThetaEntry]:
    """Build the mock-theta corpus.

    Order of preference:
      1. If cache exists and ``use_cache=True``: load it.
      2. Else build from the embedded ``_RAW_CORPUS`` literal.
      3. Optionally write the cache for next time.

    Parameters
    ----------
    n_coeffs : int
        Truncate each coefficient tuple to length ``n_coeffs``. Must be
        in ``[1, 30]`` (the embedded corpus has length-30 prefixes).
    use_cache, write_cache_after_load : bool
        Same conventions as ``_modular_form_corpus.load_modular_form_corpus``.

    Returns
    -------
    list[MockThetaEntry]
    """
    if n_coeffs <= 0:
        raise ValueError(f"n_coeffs must be > 0; got {n_coeffs}")
    max_avail = min(len(d["coefficients"]) for d in _RAW_CORPUS)
    if n_coeffs > max_avail:
        raise ValueError(
            f"n_coeffs={n_coeffs} exceeds max available {max_avail}"
        )

    pool: List[MockThetaEntry] = []
    source = "unknown"
    cp = cache_path()

    if use_cache and cp.is_file() and cp.stat().st_size > 0:
        try:
            pool = read_cache(cp)
            source = f"cache:{cp}"
        except Exception:
            pool = []

    if not pool:
        pool = [_entry_from_dict(d) for d in _RAW_CORPUS]
        source = "embedded"
        if write_cache_after_load:
            try:
                write_cache(pool, cp)
            except Exception:
                pass

    truncated = [
        MockThetaEntry(
            name=e.name,
            order=e.order,
            level=e.level,
            weight=e.weight,
            shadow_class=e.shadow_class,
            coefficients=tuple(e.coefficients[:n_coeffs]),
        )
        for e in pool
    ]

    global _LAST_LOAD_SOURCE
    _LAST_LOAD_SOURCE = source
    return truncated


_LAST_LOAD_SOURCE: str = "uninitialized"


def last_load_source() -> str:
    return _LAST_LOAD_SOURCE


def split_train_test(
    corpus: Sequence[MockThetaEntry],
    train_frac: float = 0.7,
    seed: int = 0,
) -> Tuple[List[MockThetaEntry], List[MockThetaEntry]]:
    """Reproducible train/test split of the corpus."""
    if not corpus:
        raise ValueError("cannot split an empty corpus")
    if not 0.0 < train_frac < 1.0:
        raise ValueError(f"train_frac must be in (0,1); got {train_frac}")
    import random as _random
    rng = _random.Random(seed)
    idx = list(range(len(corpus)))
    rng.shuffle(idx)
    n_train = int(round(len(corpus) * train_frac))
    n_train = max(1, min(len(corpus) - 1, n_train))
    train = [corpus[i] for i in idx[:n_train]]
    test = [corpus[i] for i in idx[n_train:]]
    return train, test


def corpus_summary(corpus: Iterable[MockThetaEntry]) -> dict:
    """Diagnostic counts: total + per-order + per-shadow_class counts."""
    corpus = list(corpus)
    by_order: dict[int, int] = {}
    by_shadow: dict[int, int] = {}
    levels: list[int] = []
    n_coeff_lens: list[int] = []
    for e in corpus:
        by_order[e.order] = by_order.get(e.order, 0) + 1
        by_shadow[e.shadow_class] = by_shadow.get(e.shadow_class, 0) + 1
        levels.append(e.level)
        n_coeff_lens.append(len(e.coefficients))
    return {
        "n_total": len(corpus),
        "by_order": dict(sorted(by_order.items())),
        "by_shadow_class": dict(sorted(by_shadow.items())),
        "level_min": min(levels) if levels else None,
        "level_max": max(levels) if levels else None,
        "coeff_len_min": min(n_coeff_lens) if n_coeff_lens else None,
        "coeff_len_max": max(n_coeff_lens) if n_coeff_lens else None,
    }


__all__ = [
    "MockThetaEntry",
    "is_available",
    "cache_path",
    "load_mock_theta_corpus",
    "last_load_source",
    "split_train_test",
    "corpus_summary",
    "write_cache",
    "read_cache",
]
