"""Tests for prometheus_math.numerics_special_eta.

Covers the four math-tdd categories with ≥2 tests each:

  Authority   — closed-form values from Whittaker & Watson §21,
                Apostol "Modular Functions and Dirichlet Series" Ch.1-3,
                Ramanujan's near-integer identity for the Heegner -163
                discriminant, and cusp-value limits.
  Property    — T- and S-transformations of η, modular invariance of
                Δ and j, non-vanishing of η on the upper half-plane.
  Edge        — Im(τ) ≤ 0, τ = 0, prec < 1, empty η-quotient,
                quasi-modular E_2 correction (NOT modular under S).
  Composition — Δ = (2π)^{12} η^{24}, j = (2π)^{12} E_4^3 / Δ,
                E_2 quasi-modular correction term.

Skipped cleanly if mpmath is missing.
"""
from __future__ import annotations

import math

import pytest

mpmath = pytest.importorskip(
    "mpmath",
    reason="mpmath is required for eta-function tests "
           "(`pip install mpmath`).",
)

from prometheus_math.numerics_special_eta import (  # noqa: E402
    eta,
    eta_quotient,
    delta_function,
    j_invariant,
    eisenstein_e2,
    eisenstein_e4,
    eisenstein_e6,
    eta_modular_t_action,
    eta_modular_s_action,
    q_expansion,
)


# Working tolerance: 53-bit precision => ~1e-15.
TOL = 1e-12


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------

def test_authority_eta_at_i_equals_gamma_one_quarter_form():
    """η(i) = Γ(1/4) / (2 π^{3/4}) ≈ 0.7682254222...

    Reference: Whittaker & Watson, *A Course of Modern Analysis*,
    §21.41 (closed form of η at the lemniscatic τ = i).  Cross-checked
    against the mpmath docstring example.
    """
    val = eta(1j)
    expected_closed = mpmath.gamma(mpmath.mpf("0.25")) / (2 * mpmath.pi ** mpmath.mpf("0.75"))
    expected_numerical = mpmath.mpf("0.7682254223260566590025942")
    assert abs(complex(val) - complex(expected_closed)) < TOL
    assert abs(complex(val).real - float(expected_numerical)) < TOL
    assert abs(complex(val).imag) < TOL


def test_authority_eta_decays_at_cusp():
    """η(i·y) → 0 as y → ∞ (cusp value).

    Reference: leading-order η(τ) ~ q^{1/24} = e^{-πy/12} · e^{iπτ/12}
    times (1 - q + ...) (Apostol, "Modular Functions", §3.1).

    At τ = 100·i:  |η| ≈ e^{-100π/12} ≈ e^{-26.18} ≈ 4.3e-12.
    """
    val = eta(mpmath.mpc(0, 100))
    assert abs(complex(val)) < 1e-10  # very close to 0


def test_authority_j_at_i_equals_1728():
    """j(i) = 1728 (CM at τ = i, j-singular modulus).

    Reference: Cox, *Primes of the Form x²+ny²*, Theorem 11.1; classical
    result (Klein 1879).
    """
    val = j_invariant(1j)
    assert abs(complex(val) - 1728) < 1e-10
    assert abs(complex(val).imag) < 1e-10


def test_authority_j_at_rho_equals_zero():
    """j(ρ) = 0 at the equianharmonic point ρ = e^{2πi/3}.

    Reference: Cox, *Primes of the Form x²+ny²*, Theorem 11.1.
    The j-invariant vanishes precisely at the SL(2,ℤ)-orbit of ρ
    (CM by ℤ[ρ], discriminant -3).
    """
    rho = mpmath.exp(2j * mpmath.pi / 3)
    val = j_invariant(rho)
    assert abs(complex(val)) < 1e-20  # exactly zero up to round-off


def test_authority_j_at_heegner_minus_163():
    """j((1+i√163)/2) = -640320^3 (Ramanujan's constant).

    Reference: Cohen, *A Course in Computational Algebraic Number
    Theory*, §7.3 — for the Heegner discriminant D = -163, the
    class number is 1 and j evaluates to a perfect cube of a small
    integer.  Equivalently, e^{π√163} ≈ 640320^3 + 743.99999999999...
    (the Ramanujan near-integer).

    Note the SIGN: j is NEGATIVE at this point.
    """
    # Heegner point must be constructed at high precision; otherwise the input
    # τ has only ~15 decimal digits and j(τ) inherits that limited precision.
    with mpmath.workprec(400):
        heegner = (1 + mpmath.sqrt(163) * 1j) / 2
        val = j_invariant(heegner, prec=400)
    expected = mpmath.mpf(-(640320 ** 3))
    err = abs(val.real - expected)
    assert err < mpmath.mpf("1e-50"), (
        f"j(heegner) = {val}, expected {expected}, err={err}"
    )
    assert abs(val.imag) < mpmath.mpf("1e-50")


def test_authority_eisenstein_e4_cusp_value():
    """E_4(i∞) = 1 (cusp value).

    Reference: definition E_4 = 1 + 240 Σ σ_3(n) q^n; at τ = i·(large),
    q ≈ 0 so E_4 → 1.  Tested at τ = 50i where q = e^{-100π} ≈ 1e-137.
    """
    val = eisenstein_e4(mpmath.mpc(0, 50))
    assert abs(complex(val) - 1) < TOL


def test_authority_eisenstein_e6_cusp_value():
    """E_6(i∞) = 1 (cusp value).

    Reference: definition E_6 = 1 - 504 Σ σ_5(n) q^n; at τ = 50i,
    q ≈ 0 so E_6 → 1.
    """
    val = eisenstein_e6(mpmath.mpc(0, 50))
    assert abs(complex(val) - 1) < TOL


def test_authority_delta_at_i_classical_value():
    """Δ(i) = (2π)^{12} · η(i)^{24}.

    Reference: classical formula relating cusp form normalization to
    η.  We cross-check the closed-form value against the explicit
    product for η(i).  Numerical value: Δ(i) ≈ 6.759 × 10^6.
    """
    val = delta_function(1j)
    eta_i = mpmath.gamma(mpmath.mpf("0.25")) / (2 * mpmath.pi ** mpmath.mpf("0.75"))
    expected = (2 * mpmath.pi) ** 12 * eta_i ** 24
    assert abs(complex(val) - complex(expected)) < TOL
    # Numerical sanity: ≈ 6.759e6
    assert abs(complex(val).real - 6759064.906012797) < 1.0


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------

def test_property_eta_T_transformation():
    """η(τ + 1) = e^{πi/12} · η(τ).

    Reference: Apostol §3.1 (Theorem 3.1).  T-action is a 24-th root of
    unity multiplier.  Tested at three diverse τ.
    """
    for tau_val in (1j, mpmath.mpc(0, 2), mpmath.mpc("0.3", "1.5"),
                    mpmath.mpc("-0.7", "0.8")):
        lhs = eta_modular_t_action(tau_val)
        rhs = mpmath.exp(mpmath.pi * 1j / 12) * eta(tau_val)
        assert abs(complex(lhs - rhs)) < 1e-14, (
            f"T-transform failed at τ={tau_val}: lhs-rhs={lhs - rhs}"
        )


def test_property_eta_S_transformation():
    """η(-1/τ) = √(-iτ) · η(τ) (principal branch).

    Reference: Apostol §3.1 (Theorem 3.1).  S-action is a *fractional
    weight* multiplier (weight 1/2).
    """
    for tau_val in (mpmath.mpc(0, 1), mpmath.mpc(0, 2),
                    mpmath.mpc("0.3", "1.5"), mpmath.mpc("-0.7", "0.8"),
                    mpmath.mpc("1.4", "2.0")):
        lhs = eta_modular_s_action(tau_val)
        rhs = mpmath.sqrt(-1j * mpmath.mpc(*[float(getattr(tau_val, x)) for x in ("real", "imag")])) \
              if False else mpmath.sqrt(-1j * tau_val) * eta(tau_val)
        assert abs(complex(lhs - rhs)) < 1e-14, (
            f"S-transform failed at τ={tau_val}: lhs-rhs={lhs - rhs}"
        )


def test_property_eta_nonvanishing():
    """η(τ) ≠ 0 in the interior of the upper half-plane.

    Reference: η(τ) = q^{1/24} ∏(1 - q^n); each factor (1 - q^n) is
    non-zero for |q| < 1, and q^{1/24} is non-zero for any finite τ
    with Im(τ) > 0.  Tested at a range of τ.
    """
    for tau_val in (mpmath.mpc(0, 0.1), 1j, mpmath.mpc(0, 5),
                    mpmath.mpc("0.5", "0.5"), mpmath.mpc("-0.4", "0.2"),
                    mpmath.mpc("3.7", "0.001")):
        val = eta(tau_val)
        assert abs(complex(val)) > 1e-100, (
            f"η vanished at τ={tau_val}: |η|={abs(complex(val))}"
        )


def test_property_delta_T_modular():
    """Δ(τ + 1) = Δ(τ) (Δ is invariant under T).

    Reference: Apostol §1.4 — Δ is the unique normalized cusp form of
    weight 12, hence T-invariant.
    """
    for tau_val in (1j, mpmath.mpc("0.3", "1.5"), mpmath.mpc("-0.7", "0.8")):
        lhs = delta_function(tau_val + 1)
        rhs = delta_function(tau_val)
        # Δ values are large; use relative tolerance.
        rel_err = abs(complex(lhs - rhs)) / max(abs(complex(rhs)), 1e-30)
        assert rel_err < 1e-12, (
            f"Δ T-modular failed at τ={tau_val}: rel_err={rel_err}"
        )


def test_property_j_T_modular():
    """j(τ + 1) = j(τ) (j is SL(2,ℤ)-invariant).

    Reference: Cox §11; j is a Hauptmodul for the modular group.
    """
    for tau_val in (mpmath.mpc("0.3", "1.5"), mpmath.mpc("-0.7", "0.8"),
                    mpmath.mpc("1.4", "0.5")):
        lhs = j_invariant(tau_val + 1)
        rhs = j_invariant(tau_val)
        rel_err = abs(complex(lhs - rhs)) / max(abs(complex(rhs)), 1.0)
        assert rel_err < 1e-12, (
            f"j T-modular failed at τ={tau_val}: rel_err={rel_err}"
        )


def test_property_j_S_modular():
    """j(-1/τ) = j(τ) (S-invariance).

    Reference: Cox §11.  Composition test: invokes both j_invariant
    and the S-action on τ via -1/τ.
    """
    for tau_val in (mpmath.mpc("0.3", "1.5"), mpmath.mpc("0.0", "2.0")):
        lhs = j_invariant(-1 / tau_val)
        rhs = j_invariant(tau_val)
        rel_err = abs(complex(lhs - rhs)) / max(abs(complex(rhs)), 1.0)
        assert rel_err < 1e-12


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def test_edge_im_tau_nonpositive():
    """Im(τ) ≤ 0 raises ValueError for every public function."""
    bad_taus = [mpmath.mpc(0, 0),       # τ = 0
                mpmath.mpc(1, 0),       # real τ
                mpmath.mpc(0, -0.5),    # below real axis
                mpmath.mpc(2, -3)]
    for bad in bad_taus:
        with pytest.raises(ValueError, match="upper half-plane"):
            eta(bad)
        with pytest.raises(ValueError, match="upper half-plane"):
            delta_function(bad)
        with pytest.raises(ValueError, match="upper half-plane"):
            j_invariant(bad)
        with pytest.raises(ValueError, match="upper half-plane"):
            eisenstein_e4(bad)


def test_edge_tau_zero():
    """τ = 0 specifically raises (Im = 0)."""
    with pytest.raises(ValueError, match="upper half-plane"):
        eta(0)
    with pytest.raises(ValueError, match="upper half-plane"):
        eta_quotient({1: 24}, 0)
    with pytest.raises(ValueError, match="upper half-plane"):
        eta_modular_t_action(0)
    with pytest.raises(ValueError, match="upper half-plane"):
        eta_modular_s_action(0)


def test_edge_invalid_prec():
    """prec < 1 raises ValueError."""
    with pytest.raises(ValueError, match="prec"):
        eta(1j, prec=0)
    with pytest.raises(ValueError, match="prec"):
        delta_function(1j, prec=-5)
    with pytest.raises(ValueError, match="prec"):
        j_invariant(1j, prec=-1)


def test_edge_eta_quotient_empty():
    """Empty η-quotient returns 1 (empty product)."""
    val = eta_quotient({}, 1j)
    assert abs(complex(val) - 1) < TOL


def test_edge_eta_quotient_invalid_keys():
    """Non-positive integer key raises."""
    with pytest.raises(ValueError, match="positive ints"):
        eta_quotient({0: 24}, 1j)
    with pytest.raises(ValueError, match="positive ints"):
        eta_quotient({-1: 24}, 1j)
    with pytest.raises(ValueError, match="ints"):
        eta_quotient({1: 1.5}, 1j)  # type: ignore[dict-item]


def test_edge_q_expansion_invalid_n_terms():
    """n_terms < 1 raises."""
    with pytest.raises(ValueError, match="n_terms"):
        q_expansion(1j, n_terms=0)
    with pytest.raises(ValueError, match="n_terms"):
        q_expansion(1j, n_terms=-3)


def test_edge_eisenstein_e2_quasi_modular_NOT_modular_under_S():
    """E_2 is quasi-modular under S, NOT modular: it requires a
    correction term.

    Reference: Apostol §3.2, Theorem 3.4.  E_2(-1/τ) - τ^2·E_2(τ)
    equals 6τ/(πi) (non-zero), proving E_2 is *not* a modular form.
    The correction term is exactly the documented edge case the user
    must respect.
    """
    tau = mpmath.mpc(0, 1.5)
    e2_S = eisenstein_e2(-1 / tau)
    e2_T = eisenstein_e2(tau)
    # The naive modular law would give e2_S == tau^2 * e2_T.  Show it doesn't.
    naive = tau ** 2 * e2_T
    diff = e2_S - naive
    # It should differ by approximately 6 tau / (pi i):
    correction = 6 * tau / (mpmath.pi * 1j)
    assert abs(complex(diff - correction)) < 1e-14, (
        f"E_2 quasi-modular law violated: diff={diff}, expected={correction}"
    )
    # And the difference is non-trivial:
    assert abs(complex(diff)) > 0.1


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------

def test_composition_delta_equals_2pi_to_12_times_eta_24():
    """Δ(τ) = (2π)^{12} · η(τ)^{24}.

    Composition: chains delta_function with eta.  Reference: Apostol §1.4.
    """
    for tau_val in (1j, mpmath.mpc(0, 2), mpmath.mpc("0.3", "1.5")):
        lhs = delta_function(tau_val)
        rhs = (2 * mpmath.pi) ** 12 * eta(tau_val) ** 24
        rel_err = abs(complex(lhs - rhs)) / max(abs(complex(rhs)), 1e-30)
        assert rel_err < 1e-13, (
            f"Δ vs (2π)^{{12}} η^{{24}} mismatch at τ={tau_val}: rel_err={rel_err}"
        )


def test_composition_j_equals_2pi12_e4_cubed_over_delta():
    """j(τ) = (2π)^{12} · E_4(τ)^3 / Δ(τ).

    Composition: chains j_invariant, eisenstein_e4, delta_function.
    Reference: Apostol §1.5 — the *closed* form for j in terms of
    Eisenstein series and the cusp form.

    NOTE on conventions: with our Δ = (2π)^{12} η^{24}, the prefactor
    is (2π)^{12}, NOT 1728.  The 1728-version uses the *normalized*
    Δ_norm = η^{24} (q-leading coefficient 1).
    """
    for tau_val in (1j, mpmath.mpc(0, 2), mpmath.mpc("0.3", "1.5")):
        j_direct = j_invariant(tau_val)
        e4 = eisenstein_e4(tau_val)
        delta = delta_function(tau_val)
        j_chain = (2 * mpmath.pi) ** 12 * e4 ** 3 / delta
        rel_err = abs(complex(j_direct - j_chain)) / max(abs(complex(j_direct)), 1.0)
        assert rel_err < 1e-12, (
            f"j vs (2π)^{{12}} E_4^3 / Δ mismatch at τ={tau_val}: rel_err={rel_err}"
        )


def test_composition_j_equals_1728_e4_cubed_over_e4_cubed_minus_e6_squared():
    """j(τ) = 1728 · E_4(τ)^3 / (E_4(τ)^3 - E_6(τ)^2).

    Alternate composition test: chains j_invariant, eisenstein_e4,
    eisenstein_e6.  Reference: Apostol §1.5.
    """
    for tau_val in (1j, mpmath.mpc(0, 2), mpmath.mpc("0.3", "1.5")):
        j_direct = j_invariant(tau_val)
        e4 = eisenstein_e4(tau_val)
        e6 = eisenstein_e6(tau_val)
        denom = e4 ** 3 - e6 ** 2
        # Avoid division by zero at τ=i (where E_6 = 0 and 1728 E_4^3 / E_4^3 = 1728)
        # Actually E_6 = 0 at τ=i but E_4^3 - 0 ≠ 0.
        if abs(complex(denom)) < 1e-100:
            continue
        j_chain = 1728 * e4 ** 3 / denom
        rel_err = abs(complex(j_direct - j_chain)) / max(abs(complex(j_direct)), 1.0)
        assert rel_err < 1e-10, (
            f"j vs 1728 E_4^3/(E_4^3 - E_6^2) mismatch at τ={tau_val}: rel_err={rel_err}"
        )


def test_composition_eta_quotient_recovers_delta():
    """Δ(τ) = (2π)^{12} · eta_quotient({1: 24}, τ).

    Composition: chains eta_quotient and delta_function.  Verifies the
    η-quotient API can reproduce the discriminant cusp form.
    """
    for tau_val in (1j, mpmath.mpc("0.3", "1.5")):
        delta = delta_function(tau_val)
        quotient = eta_quotient({1: 24}, tau_val)
        recovered = (2 * mpmath.pi) ** 12 * quotient
        rel_err = abs(complex(delta - recovered)) / max(abs(complex(delta)), 1e-30)
        assert rel_err < 1e-13


def test_composition_q_expansion_matches_eta_div_q_one_24th():
    """The integer η coefficients (factor q^{1/24} out) match the
    truncated Euler-pentagonal series 1 - q - q^2 + q^5 + q^7 - q^12 - ...

    Composition: chains q_expansion with eta directly via the explicit
    product / sum.  Reference: Apostol §3.4 (Euler's pentagonal-number
    theorem applied to η).
    """
    pairs = q_expansion(1j, n_terms=16)
    # Expected leading 16 coefficients of ∏(1 - q^k) (Euler pentagonal):
    # exponents 0, 1, 2, 5, 7, 12, 15 carry ±1; rest are 0.
    # Generalized pentagonal numbers: 1, 2, 5, 7, 12, 15, 22, 26, ...
    # Signs: alternate starting with -1 at k=±1.
    expected = [1, -1, -1, 0, 0, 1, 0, 1, 0, 0, 0, 0, -1, 0, 0, -1]
    for (n, c), exp_c in zip(pairs, expected):
        assert int(complex(c).real) == exp_c, (
            f"q_expansion[{n}]: got {c}, expected {exp_c}"
        )
        assert abs(complex(c).imag) < TOL


def test_composition_eta_S_matches_sqrt_minus_i_tau_eta():
    """η(-1/τ) / √(-iτ) = η(τ) for τ in the upper half-plane.

    Composition: chains eta_modular_s_action, eta, and complex sqrt.
    Stronger than the property test: explicitly inverts the S-action
    to recover the original eta value.
    """
    for tau_val in (mpmath.mpc("1.4", "2.0"), mpmath.mpc("-0.3", "0.7")):
        eta_S = eta_modular_s_action(tau_val)
        recovered = eta_S / mpmath.sqrt(-1j * tau_val)
        direct = eta(tau_val)
        assert abs(complex(recovered - direct)) < 1e-14
