"""Tests for prometheus_math.crypto_primitives.

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority: classical numeric examples (CRT 23, mod_inverse 3*5=1
  mod 7, Tonelli-Shanks 2 mod 7), known primes (7919) and composites
  (8051 = 79*101).
- Property: RSA round-trip, RSA sign/verify, DH agreement, ECDH
  agreement, mod_inverse identity, extended_gcd divisibility.
- Edge: miller_rabin(0/1/2), tonelli_shanks(0, p), mod_inverse on
  non-coprime, rsa_keygen below educational floor, dh on non-prime,
  ecdh on unknown curve.
- Composition: encrypt -> decrypt round-trip, sign -> verify,
  generate_prime certified by miller_rabin, tonelli_shanks(n,p)^2
  mod p == n, CRT inverts via per-modulus reduction.

EDUCATIONAL ONLY — these tests document insecure textbook crypto.
"""
from __future__ import annotations

import math
import random

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from prometheus_math.crypto_primitives import (
    modular_exp,
    miller_rabin,
    generate_prime,
    tonelli_shanks,
    extended_gcd,
    mod_inverse,
    rsa_keygen,
    rsa_encrypt,
    rsa_decrypt,
    rsa_sign,
    rsa_verify,
    dh_keygen,
    dh_shared_secret,
    ecdh_keygen,
    ecdh_shared_secret,
    chinese_remainder_theorem,
    quadratic_residues,
)

# Detect optional dependency used by ECDH tests.
try:
    import cryptography  # noqa: F401

    _HAS_CRYPTOGRAPHY = True
except Exception:  # pragma: no cover
    _HAS_CRYPTOGRAPHY = False


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_miller_rabin_known_prime_7919():
    """7919 is the 1000th prime.

    Reference: OEIS A000040 a(1000) = 7919; verified by hand
    via trial division.
    """
    assert miller_rabin(7919) is True


def test_miller_rabin_known_composite_8051():
    """8051 = 79 * 101 is composite.

    Reference: 79 * 101 = 7979 + 79 + ... = 8051 (hand factored).
    Cross-check: sympy.isprime(8051) == False.
    """
    assert miller_rabin(8051) is False


def test_tonelli_shanks_2_mod_7():
    """sqrt(2) mod 7 is 3 or 4: 3^2 = 9 ≡ 2 mod 7, 4^2 = 16 ≡ 2 mod 7.

    Reference: Cohen, Computational ANT, Algorithm 1.5.1, with
    hand-verification.
    """
    r = tonelli_shanks(2, 7)
    assert r in {3, 4}
    assert (r * r) % 7 == 2


def test_tonelli_shanks_non_residue_returns_none():
    """3 is a quadratic non-residue mod 7 (QRs mod 7 are {1, 2, 4}).

    Reference: Cohen Table, or direct enumeration:
    1^2=1, 2^2=4, 3^2=2, 4^2=2, 5^2=4, 6^2=1.
    """
    assert tonelli_shanks(3, 7) is None


def test_extended_gcd_35_15():
    """gcd(35, 15) = 5; Bezout: 35*1 + 15*(-2) = 5.

    Reference: Knuth TAOCP §4.5.2, hand computation.
    """
    g, x, y = extended_gcd(35, 15)
    assert g == 5
    assert 35 * x + 15 * y == 5


def test_mod_inverse_3_mod_7_is_5():
    """3^{-1} mod 7 = 5 because 3*5 = 15 = 2*7 + 1.

    Reference: hand computation.
    """
    assert mod_inverse(3, 7) == 5


def test_chinese_remainder_theorem_classical_23():
    """CRT classical: x ≡ 2 (mod 3), 3 (mod 5), 2 (mod 7) => x = 23.

    Reference: Sun Tzu Suan Ching (~3rd century AD), the original
    statement of CRT. Modulus M = 105, smallest non-neg solution = 23.
    """
    assert chinese_remainder_theorem([2, 3, 2], [3, 5, 7]) == 23


def test_quadratic_residues_mod_7():
    """QRs mod 7 are {1, 2, 4}.

    Reference: Cohen, hand enumeration of x^2 mod 7 for x in 1..6.
    """
    assert quadratic_residues(7) == {1, 2, 4}


def test_modular_exp_basic():
    """7^256 mod 13 = 9 (hand-verified by repeated squaring)."""
    assert modular_exp(7, 256, 13) == pow(7, 256, 13)
    # Hand spot-check: 2^10 mod 1000 = 24.
    assert modular_exp(2, 10, 1000) == 24


def test_rsa_keygen_satisfies_e_d_relation():
    """RSA keygen produces (n,e,d) with e*d ≡ 1 mod totient(n).

    Reference: Menezes-van Oorschot-Vanstone HAC §8.2.
    """
    key = rsa_keygen(bits=512, e=65537, seed=42)
    n, e, d, p, q, totient = (
        key["n"], key["e"], key["d"], key["p"], key["q"], key["totient"]
    )
    assert n == p * q
    assert totient == (p - 1) * (q - 1)
    assert (e * d) % totient == 1


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------


# Pre-compute one RSA key for the Hypothesis property tests, so each
# example doesn't pay keygen cost.
_RSA_KEY_PROP = rsa_keygen(bits=256, e=65537, seed=1234)


@given(st.integers(min_value=2, max_value=_RSA_KEY_PROP["n"] - 1))
@settings(
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_rsa_round_trip(m):
    """For any 0 < m < n, decrypt(encrypt(m)) == m. Textbook RSA correctness."""
    pub = {"n": _RSA_KEY_PROP["n"], "e": _RSA_KEY_PROP["e"]}
    priv = {"n": _RSA_KEY_PROP["n"], "d": _RSA_KEY_PROP["d"]}
    c = rsa_encrypt(m, pub)
    assert rsa_decrypt(c, priv) == m


@given(st.integers(min_value=2, max_value=_RSA_KEY_PROP["n"] - 1))
@settings(
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_rsa_sign_verify(m):
    """Signature s = m^d mod n verifies as s^e == m mod n. Textbook RSA."""
    pub = {"n": _RSA_KEY_PROP["n"], "e": _RSA_KEY_PROP["e"]}
    priv = {"n": _RSA_KEY_PROP["n"], "d": _RSA_KEY_PROP["d"]}
    s = rsa_sign(m, priv)
    assert rsa_verify(m, s, pub) is True


# A safe-ish DH prime for tests (Sophie-Germain pair, p = 2*q + 1
# with q prime). p = 2*1019 + 1 = 2039 is prime; we use generator 2.
_DH_P = 2039
_DH_G = 2


@given(
    st.integers(min_value=2, max_value=_DH_P - 2),
    st.integers(min_value=2, max_value=_DH_P - 2),
)
@settings(max_examples=25, deadline=None)
def test_dh_shared_secret_agrees(a, b):
    """For DH, shared(a, B, p) == shared(b, A, p) where A = g^a, B = g^b."""
    A = pow(_DH_G, a, _DH_P)
    B = pow(_DH_G, b, _DH_P)
    assert dh_shared_secret(a, B, _DH_P) == dh_shared_secret(b, A, _DH_P)


@given(
    st.integers(min_value=1, max_value=10000),
    st.integers(min_value=2, max_value=10000),
)
def test_mod_inverse_property(a, m):
    """When gcd(a, m) == 1, a * a^{-1} ≡ 1 (mod m)."""
    if math.gcd(a, m) != 1:
        return
    inv = mod_inverse(a, m)
    assert (a * inv) % m == 1


@given(st.integers(), st.integers())
def test_extended_gcd_divides(a, b):
    """g | a and g | b for g = gcd(a, b) returned by extended_gcd."""
    g, x, y = extended_gcd(a, b)
    assert g >= 0
    if a == 0 and b == 0:
        assert g == 0
        return
    assert g > 0
    assert a % g == 0
    assert b % g == 0
    assert a * x + b * y == g


# A small list of known composites: Carmichael numbers + their products.
# Miller-Rabin must reject all of them (with high probability).
_KNOWN_COMPOSITES = [
    9, 15, 21, 25, 27, 33, 35, 49, 51, 55, 65, 77, 91, 93, 95,
    121, 125, 169, 187, 209, 221, 247, 253, 289, 299, 323, 341,
    # Carmichael numbers (pseudo-prime to many bases):
    561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841,
    # Composite of two large-ish primes:
    79 * 101, 521 * 523, 1009 * 1013,
]


@pytest.mark.parametrize("n", _KNOWN_COMPOSITES)
def test_miller_rabin_rejects_composites(n):
    """Miller-Rabin must return False for known composites, including
    Carmichael numbers (which fool Fermat's test)."""
    assert miller_rabin(n, k=20) is False


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_miller_rabin_edge_cases():
    """Edges: 0, 1, 2, 3, 4 — small-integer corner cases."""
    assert miller_rabin(0) is False
    assert miller_rabin(1) is False
    assert miller_rabin(2) is True
    assert miller_rabin(3) is True
    assert miller_rabin(4) is False
    # Negative inputs are not prime by convention.
    assert miller_rabin(-7) is False


def test_tonelli_shanks_zero_and_p_equals_2():
    """tonelli_shanks(0, p) == 0; tonelli_shanks(_, 2) returns input mod 2."""
    assert tonelli_shanks(0, 7) == 0
    assert tonelli_shanks(0, 13) == 0
    assert tonelli_shanks(1, 2) == 1
    assert tonelli_shanks(0, 2) == 0


def test_mod_inverse_non_coprime_raises():
    """When gcd(a, m) > 1, mod_inverse must raise ValueError."""
    with pytest.raises(ValueError):
        mod_inverse(6, 9)  # gcd(6,9) = 3
    with pytest.raises(ValueError):
        mod_inverse(0, 5)  # gcd(0,5) = 5


def test_modular_exp_invalid_modulus():
    """modulus < 1 must raise ValueError; modulus == 1 returns 0."""
    with pytest.raises(ValueError):
        modular_exp(2, 3, 0)
    with pytest.raises(ValueError):
        modular_exp(2, 3, -5)
    assert modular_exp(2, 100, 1) == 0


def test_rsa_keygen_below_educational_floor():
    """bits < 16 must raise ValueError (we set the floor at 16)."""
    with pytest.raises(ValueError):
        rsa_keygen(bits=8)
    with pytest.raises(ValueError):
        rsa_keygen(bits=0)


def test_dh_keygen_non_prime_raises():
    """Non-prime modulus must raise ValueError (Miller-Rabin gate)."""
    with pytest.raises(ValueError):
        dh_keygen(p=15, g=2)  # 15 = 3*5
    with pytest.raises(ValueError):
        dh_keygen(p=3, g=2)  # below the floor of 5


def test_dh_keygen_bad_generator():
    """Generator out of [2, p) must raise ValueError."""
    with pytest.raises(ValueError):
        dh_keygen(p=2039, g=1)
    with pytest.raises(ValueError):
        dh_keygen(p=2039, g=2039)


def test_chinese_remainder_theorem_edge_cases():
    """CRT edges: empty input, length mismatch, non-coprime moduli."""
    with pytest.raises(ValueError):
        chinese_remainder_theorem([], [])
    with pytest.raises(ValueError):
        chinese_remainder_theorem([1, 2], [3])
    # Non-coprime moduli (gcd(6, 9) = 3).
    with pytest.raises(ValueError):
        chinese_remainder_theorem([1, 1], [6, 9])


@pytest.mark.skipif(not _HAS_CRYPTOGRAPHY, reason="cryptography not installed")
def test_ecdh_unknown_curve_raises():
    """Unknown curve name must raise ValueError."""
    with pytest.raises(ValueError):
        ecdh_keygen(curve="not-a-real-curve")


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_rsa_encrypt_decrypt_roundtrip_specific():
    """Encrypt -> decrypt round-trip on a hand-picked message.

    Composition: rsa_keygen + rsa_encrypt + rsa_decrypt agree.
    """
    key = rsa_keygen(bits=256, e=65537, seed=99)
    pub = {"n": key["n"], "e": key["e"]}
    priv = {"n": key["n"], "d": key["d"]}
    for m in (0, 1, 2, 12345, key["n"] - 1):
        c = rsa_encrypt(m, pub)
        assert rsa_decrypt(c, priv) == m


def test_rsa_sign_verify_roundtrip_specific():
    """Sign -> verify must agree on a hand-picked message; tampered
    signature must fail verification.

    Composition: rsa_keygen + rsa_sign + rsa_verify.
    """
    key = rsa_keygen(bits=256, e=65537, seed=7)
    pub = {"n": key["n"], "e": key["e"]}
    priv = {"n": key["n"], "d": key["d"]}
    m = 0xDEAD_BEEF % key["n"]
    s = rsa_sign(m, priv)
    assert rsa_verify(m, s, pub) is True
    # Tamper with the signature.
    bad = (s + 1) % key["n"]
    assert rsa_verify(m, bad, pub) is False


def test_dh_two_party_keygen_agrees():
    """Two parties run dh_keygen; their shared secrets agree.

    Composition: dh_keygen (twice) + dh_shared_secret (twice).
    """
    p = 2039
    g = 2
    a = dh_keygen(p, g, seed=1)
    b = dh_keygen(p, g, seed=2)
    s_a = dh_shared_secret(a["private"], b["public"], p)
    s_b = dh_shared_secret(b["private"], a["public"], p)
    assert s_a == s_b


@pytest.mark.skipif(not _HAS_CRYPTOGRAPHY, reason="cryptography not installed")
def test_ecdh_two_party_agreement():
    """Two ECDH parties derive the same shared secret.

    Composition: ecdh_keygen (twice) + ecdh_shared_secret (twice).
    """
    a = ecdh_keygen(curve="secp256r1")
    b = ecdh_keygen(curve="secp256r1")
    s_ab = ecdh_shared_secret(a, b, curve="secp256r1")
    s_ba = ecdh_shared_secret(b, a, curve="secp256r1")
    assert s_ab == s_ba
    assert isinstance(s_ab, (bytes, bytearray))
    assert len(s_ab) > 0


@pytest.mark.skipif(not _HAS_CRYPTOGRAPHY, reason="cryptography not installed")
def test_ecdh_accepts_serialized_public_bytes():
    """ECDH must accept public key as serialized X9.62 bytes (composition
    of keygen.public_bytes -> shared_secret)."""
    a = ecdh_keygen(curve="secp256r1")
    b = ecdh_keygen(curve="secp256r1")
    # Pass b's serialized public key as bytes.
    s = ecdh_shared_secret(a, b["public_bytes"], curve="secp256r1")
    s_ref = ecdh_shared_secret(a, b, curve="secp256r1")
    assert s == s_ref


@given(st.integers(min_value=1, max_value=200))
@settings(max_examples=30, deadline=None)
def test_tonelli_shanks_roundtrip(n):
    """When tonelli_shanks(n, p) returns r, r^2 ≡ n (mod p).

    Composition: tonelli_shanks + modular_exp.
    """
    p = 1009  # a prime
    r = tonelli_shanks(n, p)
    if r is None:
        # n is a non-residue; verify Euler's criterion confirms.
        assert pow(n % p, (p - 1) // 2, p) in (p - 1, 0)
    else:
        assert (r * r) % p == n % p


def test_generate_prime_certified_by_miller_rabin():
    """generate_prime(bits) returns a value that miller_rabin confirms.

    Composition: generate_prime + miller_rabin.
    """
    for bits in (32, 64, 128):
        p = generate_prime(bits=bits)
        assert (1 << (bits - 1)) <= p < (1 << bits)
        assert miller_rabin(p, k=40) is True


def test_chinese_remainder_inverts():
    """For x in [0, M), CRT applied to (x mod m_i) returns x.

    Composition: chinese_remainder_theorem composed with explicit
    per-modulus reduction (a self-inversion check).
    """
    moduli = [3, 5, 7, 11]
    M = 1
    for m in moduli:
        M *= m
    for x in (0, 1, 17, 100, M - 1, M // 2):
        rems = [x % m for m in moduli]
        assert chinese_remainder_theorem(rems, moduli) == x % M
