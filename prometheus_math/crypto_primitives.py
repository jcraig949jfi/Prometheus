"""prometheus_math.crypto_primitives — classical cryptographic primitives.

EDUCATIONAL / RESEARCH USE ONLY.

This module is a textbook implementation of classical cryptographic
primitives (modular exponentiation, RSA, Diffie-Hellman, ECDH, Miller-
Rabin, Tonelli-Shanks). It is intended for research, teaching, and
exploring the number-theoretic structure underneath cryptography.

DO NOT USE THIS MODULE FOR PRODUCTION CRYPTOGRAPHY.

Reasons (non-exhaustive):
- No constant-time guarantees: every routine is vulnerable to timing
  side-channels.
- No padding (RSA encrypt/decrypt is "textbook RSA", which is
  malleable and meaningfully insecure for real messages).
- No defence against fault injection, power analysis, or chosen-
  ciphertext attacks.
- Key sizes default to research-friendly defaults; for real use, use a
  vetted library (PyCA `cryptography`, `pynacl`, `tink`).

For production use, import from `cryptography` or `pynacl`.

References for the primitives implemented here:
- Knuth, "The Art of Computer Programming, Volume 2: Seminumerical
  Algorithms" (3rd ed., 1997), §4.5 (Euclid), §4.6 (modular
  exponentiation, primality testing).
- Cohen, "A Course in Computational Algebraic Number Theory" (1993),
  §1.4 (Tonelli-Shanks), §1.5 (CRT).
- Menezes, van Oorschot, Vanstone, "Handbook of Applied Cryptography"
  (1996), Ch. 4 (Public-Key Parameters), Ch. 8 (Public-Key Encryption).
- Silverman, "The Arithmetic of Elliptic Curves" (2nd ed., 2009),
  Ch. III (point arithmetic on E/F_p).

Module exports:

  modular_exp(base, exp, modulus) -> int
  miller_rabin(n, k=20) -> bool
  generate_prime(bits, max_tries=1000) -> int
  tonelli_shanks(n, p) -> int | None
  extended_gcd(a, b) -> (g, x, y)
  mod_inverse(a, m) -> int
  rsa_keygen(bits=1024, e=65537, seed=None) -> dict
  rsa_encrypt(message, public_key) -> int
  rsa_decrypt(ciphertext, private_key) -> int
  rsa_sign(message, private_key) -> int
  rsa_verify(message, signature, public_key) -> bool
  dh_keygen(p, g, seed=None) -> dict
  dh_shared_secret(my_private, their_public, p) -> int
  ecdh_keygen(curve='secp256k1', seed=None) -> dict
  ecdh_shared_secret(my_private, their_public, curve='secp256k1') -> bytes
  chinese_remainder_theorem(remainders, moduli) -> int
  quadratic_residues(p) -> set[int]
"""
from __future__ import annotations

import math
import random
import secrets
import warnings
from typing import Optional

# Optional: PyCA cryptography for ECDH. We delay import so the rest
# of the module loads even if cryptography is not available.
try:
    from cryptography.hazmat.primitives.asymmetric import ec as _crypto_ec
    from cryptography.hazmat.primitives import serialization as _crypto_serialization
    _HAS_CRYPTOGRAPHY = True
except Exception:  # pragma: no cover
    _HAS_CRYPTOGRAPHY = False


__all__ = [
    "modular_exp",
    "miller_rabin",
    "generate_prime",
    "tonelli_shanks",
    "extended_gcd",
    "mod_inverse",
    "rsa_keygen",
    "rsa_encrypt",
    "rsa_decrypt",
    "rsa_sign",
    "rsa_verify",
    "dh_keygen",
    "dh_shared_secret",
    "ecdh_keygen",
    "ecdh_shared_secret",
    "chinese_remainder_theorem",
    "quadratic_residues",
]


# ---------------------------------------------------------------------------
# Modular exponentiation
# ---------------------------------------------------------------------------


def modular_exp(base: int, exp: int, modulus: int) -> int:
    """Compute base^exp mod modulus.

    Educational wrapper around Python's built-in three-argument pow
    (which uses left-to-right binary exponentiation, see Knuth TAOCP
    §4.6.3, Algorithm A). Negative exponents are supported when
    gcd(base, modulus) == 1 (we delegate to pow's native modular
    inverse handling on Python >= 3.8).

    Args:
        base: integer base.
        exp: integer exponent. Negative permitted iff base is invertible
            mod ``modulus``.
        modulus: positive integer modulus.

    Returns:
        ``base ** exp mod modulus``, an integer in [0, modulus).

    Raises:
        ValueError: if modulus < 1 or negative exponent with non-unit
            base.
    """
    if modulus < 1:
        raise ValueError(f"modulus must be >= 1, got {modulus}")
    if modulus == 1:
        return 0
    return pow(base, exp, modulus)


# ---------------------------------------------------------------------------
# Extended Euclidean algorithm and modular inverse
# ---------------------------------------------------------------------------


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclidean algorithm. Educational.

    Returns (g, x, y) such that a*x + b*y = g = gcd(a, b).

    Reference: Knuth TAOCP Vol. 2, §4.5.2, Algorithm X.

    Args:
        a, b: integers (any sign; zeros allowed but g >= 0).

    Returns:
        Tuple (g, x, y) with g >= 0.
    """
    if a == 0 and b == 0:
        return (0, 0, 0)
    # Iterative form to avoid recursion limits for large inputs.
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    g, x, y = old_r, old_s, old_t
    if g < 0:
        g, x, y = -g, -x, -y
    return (g, x, y)


def mod_inverse(a: int, m: int) -> int:
    """Modular inverse a^{-1} mod m. Educational.

    Returns the unique integer in [0, m) congruent to a^{-1} mod m,
    when gcd(a, m) == 1.

    Reference: Knuth TAOCP §4.5.2.

    Raises:
        ValueError: if gcd(a, m) > 1 (no inverse exists) or m < 2.
    """
    if m < 2:
        raise ValueError(f"modulus must be >= 2, got {m}")
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(
            f"mod_inverse undefined: gcd({a}, {m}) = {g} != 1"
        )
    return x % m


# ---------------------------------------------------------------------------
# Miller-Rabin probabilistic primality testing
# ---------------------------------------------------------------------------

# Deterministic small-prime trial divisors, useful as a fast filter
# before invoking Miller-Rabin.
_SMALL_PRIMES = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
    61, 67, 71, 73, 79, 83, 89, 97,
)


def miller_rabin(n: int, k: int = 20, _rng: Optional[random.Random] = None) -> bool:
    """Miller-Rabin probabilistic primality test. Educational.

    Returns True iff n is prime (with probability of false-positive at
    most ``4^-k``). Composite n is rejected with certainty up to the
    selection of the witness; for k=20 the probability of a false
    "prime" verdict is < 1e-12 for random n.

    Reference: Menezes-van Oorschot-Vanstone, HAC, Algorithm 4.24.

    Args:
        n: integer to test.
        k: number of witness rounds (each contributes a factor of 4
            against false positives).

    Returns:
        True if n is probably prime, False if definitely composite.
    """
    if n < 2:
        return False
    # Trivial small-prime checks.
    for p in _SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    # Write n - 1 = 2^s * d with d odd.
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    rng = _rng if _rng is not None else random.SystemRandom()
    for _ in range(k):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True


def generate_prime(bits: int, max_tries: int = 1000) -> int:
    """Generate a uniformly random prime of a given bit length. Educational.

    Returns a probable prime ``p`` with ``2**(bits-1) <= p < 2**bits``,
    verified by Miller-Rabin (k=25). For research use only; production
    keys should use a vetted library.

    Args:
        bits: target bit length, must be >= 2.
        max_tries: candidate samples before raising RuntimeError.

    Raises:
        ValueError: if bits < 2.
        RuntimeError: if no prime is found in max_tries attempts.
    """
    if bits < 2:
        raise ValueError(f"bits must be >= 2, got {bits}")
    for _ in range(max_tries):
        # Force the high bit so the result has exactly `bits` bits;
        # force the low bit so it is odd.
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if miller_rabin(candidate, k=25):
            return candidate
    raise RuntimeError(
        f"generate_prime: no prime found in {max_tries} attempts at "
        f"{bits} bits"
    )


# ---------------------------------------------------------------------------
# Tonelli-Shanks (square root mod prime)
# ---------------------------------------------------------------------------


def tonelli_shanks(n: int, p: int) -> Optional[int]:
    """Square root of n modulo prime p. Educational.

    Returns an integer r in [0, p) with r*r ≡ n mod p, or None if no
    such r exists (i.e. n is a non-residue mod p). The companion root
    is p - r.

    Reference: Cohen, "A Course in Computational Algebraic Number
    Theory", Algorithm 1.5.1 (Tonelli-Shanks).

    Args:
        n: integer (will be reduced mod p).
        p: odd prime > 2, or p == 2.

    Raises:
        ValueError: if p < 2.
    """
    if p < 2:
        raise ValueError(f"p must be a prime >= 2, got {p}")
    n = n % p
    if n == 0:
        return 0
    if p == 2:
        return n  # n is 0 or 1 mod 2, both square roots of themselves
    # Euler's criterion: n is a QR iff n^{(p-1)/2} == 1 (mod p).
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    # Special case p ≡ 3 (mod 4): r = n^{(p+1)/4} mod p.
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    # General Tonelli-Shanks.
    # Write p - 1 = q * 2^s with q odd.
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    # Find a quadratic non-residue z.
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)
    while True:
        if t == 1:
            return r
        # Find least i, 0 < i < m, such that t^{2^i} == 1 (mod p).
        i = 0
        temp = t
        while temp != 1:
            temp = (temp * temp) % p
            i += 1
            if i == m:  # pragma: no cover (only if n is non-residue)
                return None
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p


# ---------------------------------------------------------------------------
# Quadratic residues
# ---------------------------------------------------------------------------


def quadratic_residues(p: int) -> set[int]:
    """Set of all quadratic residues modulo prime p. Educational.

    Returns {x^2 mod p : x in [1, p)}. By Lagrange / Euler this set has
    exactly (p-1)/2 elements when p is an odd prime, plus 0 is
    sometimes included separately (we follow the convention that 0 is
    NOT a "non-trivial" QR and we exclude it from the returned set).

    Args:
        p: odd prime.

    Raises:
        ValueError: if p < 2.
    """
    if p < 2:
        raise ValueError(f"p must be >= 2, got {p}")
    return {(x * x) % p for x in range(1, p)}


# ---------------------------------------------------------------------------
# Chinese remainder theorem
# ---------------------------------------------------------------------------


def chinese_remainder_theorem(remainders, moduli) -> int:
    """CRT: find x with x ≡ r_i (mod m_i) for each i. Educational.

    Returns the unique x in [0, M) where M = prod m_i, when the moduli
    are pairwise coprime.

    Reference: Knuth TAOCP Vol. 2, §4.3.2, equation (24).

    Args:
        remainders: sequence of residues r_i.
        moduli: sequence of pairwise-coprime moduli m_i (all >= 1).

    Raises:
        ValueError: on length mismatch, empty input, non-coprime moduli,
            or any modulus <= 0.
    """
    if len(remainders) != len(moduli):
        raise ValueError(
            f"remainders and moduli length mismatch: "
            f"{len(remainders)} vs {len(moduli)}"
        )
    if len(moduli) == 0:
        raise ValueError("CRT requires at least one congruence")
    for m in moduli:
        if m <= 0:
            raise ValueError(f"all moduli must be positive, got {m}")
    M = 1
    for m in moduli:
        M *= m
    x = 0
    for r, m in zip(remainders, moduli):
        Mi = M // m
        g, yi, _ = extended_gcd(Mi, m)
        if g != 1:
            raise ValueError(
                f"CRT moduli must be pairwise coprime; gcd hit {g}"
            )
        x = (x + r * Mi * yi) % M
    return x % M


# ---------------------------------------------------------------------------
# RSA — textbook
# ---------------------------------------------------------------------------


def rsa_keygen(bits: int = 1024, e: int = 65537, seed: Optional[int] = None) -> dict:
    """Textbook RSA key generation. EDUCATIONAL ONLY.

    Generates two distinct primes p, q of about ``bits/2`` bits each,
    sets n = p*q, totient = (p-1)*(q-1), d = e^{-1} mod totient.

    Args:
        bits: target modulus bit length, must be >= 16. (Sub-1024 is
            cryptographically broken; we permit small sizes for
            teaching.)
        e: public exponent, default 65537.
        seed: optional integer seed for the internal RNG (used to make
            the test suite deterministic). When provided we deviate
            from secrets-based generation.

    Returns:
        Dict with keys ``n, e, d, p, q, totient``.

    Raises:
        ValueError: if bits < 16, or if e shares a factor with totient
            (extremely rare for e=65537).
    """
    if bits < 16:
        raise ValueError(
            f"bits must be >= 16 (educational floor), got {bits}"
        )
    half = bits // 2
    if seed is not None:
        rng = random.Random(seed)

        def _gen() -> int:
            for _ in range(10000):
                cand = rng.getrandbits(half) | (1 << (half - 1)) | 1
                if miller_rabin(cand, k=25, _rng=rng):
                    return cand
            raise RuntimeError("seeded prime gen exhausted")

        p = _gen()
        q = _gen()
        while q == p:
            q = _gen()
    else:
        p = generate_prime(half)
        q = generate_prime(half)
        while q == p:
            q = generate_prime(half)
    n = p * q
    totient = (p - 1) * (q - 1)
    g, d, _ = extended_gcd(e, totient)
    if g != 1:
        raise ValueError(
            f"e={e} not coprime with totient; pick a different e"
        )
    d = d % totient
    return {"n": n, "e": e, "d": d, "p": p, "q": q, "totient": totient}


def rsa_encrypt(message: int, public_key: dict) -> int:
    """Textbook RSA encryption: c = m^e mod n. EDUCATIONAL ONLY.

    No padding (insecure against chosen-ciphertext attacks). Use OAEP
    for real applications.
    """
    n = public_key["n"]
    e = public_key["e"]
    if not (0 <= message < n):
        raise ValueError(f"message must be in [0, n); got {message}")
    return pow(message, e, n)


def rsa_decrypt(ciphertext: int, private_key: dict) -> int:
    """Textbook RSA decryption: m = c^d mod n. EDUCATIONAL ONLY."""
    n = private_key["n"]
    d = private_key["d"]
    if not (0 <= ciphertext < n):
        raise ValueError(
            f"ciphertext must be in [0, n); got {ciphertext}"
        )
    return pow(ciphertext, d, n)


def rsa_sign(message: int, private_key: dict) -> int:
    """Textbook RSA signature: s = m^d mod n. EDUCATIONAL ONLY.

    No hashing, no padding (insecure: existential forgery via
    multiplicativity). Use RSASSA-PSS or RSASSA-PKCS1-v1_5 with a
    cryptographic hash for real applications.
    """
    n = private_key["n"]
    d = private_key["d"]
    if not (0 <= message < n):
        raise ValueError(f"message must be in [0, n); got {message}")
    return pow(message, d, n)


def rsa_verify(message: int, signature: int, public_key: dict) -> bool:
    """Textbook RSA verification: check m == s^e mod n. EDUCATIONAL ONLY."""
    n = public_key["n"]
    e = public_key["e"]
    if not (0 <= signature < n):
        return False
    return pow(signature, e, n) == (message % n)


# ---------------------------------------------------------------------------
# Diffie-Hellman
# ---------------------------------------------------------------------------


def dh_keygen(p: int, g: int, seed: Optional[int] = None) -> dict:
    """Diffie-Hellman keypair. EDUCATIONAL ONLY.

    Returns {private, public} with public = g^private mod p.
    The private key is in [2, p-2].

    Args:
        p: large prime modulus. We Miller-Rabin verify it.
        g: generator (we do NOT verify it generates a large subgroup).
        seed: optional seed for deterministic tests.

    Raises:
        ValueError: if p is not prime or g is out of range.
    """
    if p < 5:
        raise ValueError(f"p must be a prime >= 5, got {p}")
    if not miller_rabin(p, k=20):
        raise ValueError(f"p={p} fails Miller-Rabin; not prime")
    if not (2 <= g < p):
        raise ValueError(f"generator g must be in [2, p), got {g}")
    if seed is not None:
        rng = random.Random(seed)
        priv = rng.randrange(2, p - 1)
    else:
        priv = secrets.randbelow(p - 3) + 2
    pub = pow(g, priv, p)
    return {"private": priv, "public": pub}


def dh_shared_secret(my_private: int, their_public: int, p: int) -> int:
    """DH shared secret: their_public ** my_private mod p. EDUCATIONAL.

    Args:
        my_private: my private exponent.
        their_public: peer's public g^b mod p.
        p: shared prime modulus.
    """
    if p < 2:
        raise ValueError(f"p must be >= 2, got {p}")
    return pow(their_public, my_private, p)


# ---------------------------------------------------------------------------
# ECDH (delegated to PyCA cryptography for the curve arithmetic)
# ---------------------------------------------------------------------------

# Mapping from human-readable curve name -> cryptography ec curve class.
# We use cryptography to avoid reinventing constant-time field arithmetic.
# All ECDH ops here are still educational wrappers; for production use
# go through `cryptography.hazmat.primitives.asymmetric.ec` directly.
_ECDH_CURVES = {}
if _HAS_CRYPTOGRAPHY:
    _ECDH_CURVES = {
        "secp256k1": _crypto_ec.SECP256K1,
        "secp256r1": _crypto_ec.SECP256R1,
        "secp384r1": _crypto_ec.SECP384R1,
        "secp521r1": _crypto_ec.SECP521R1,
    }


def _require_cryptography() -> None:
    if not _HAS_CRYPTOGRAPHY:
        raise ImportError(
            "ECDH primitives require the `cryptography` package. "
            "Install with `pip install cryptography`."
        )


def ecdh_keygen(curve: str = "secp256k1", seed: Optional[int] = None) -> dict:
    """ECDH keypair on a named curve. EDUCATIONAL ONLY.

    Returns a dict with:
      - 'private': cryptography private key object (for use with
        ``ecdh_shared_secret``)
      - 'public': cryptography public key object
      - 'private_int': integer scalar (for inspection)
      - 'public_bytes': uncompressed serialised public point
      - 'curve': the curve name

    Args:
        curve: one of {'secp256k1', 'secp256r1', 'secp384r1', 'secp521r1'}.
        seed: when not None, attempts to derive a deterministic key by
            seeded random rejection sampling. Educational only.

    Raises:
        ImportError: if `cryptography` is not installed.
        ValueError: if curve is unknown.
    """
    _require_cryptography()
    if curve not in _ECDH_CURVES:
        raise ValueError(
            f"unknown curve {curve!r}; supported: "
            f"{sorted(_ECDH_CURVES)}"
        )
    curve_cls = _ECDH_CURVES[curve]()
    if seed is not None:
        # Seeded-deterministic path: sample a scalar from a seeded PRNG
        # and load it as a private key. Educational; never do this in
        # real code.
        warnings.warn(
            "ecdh_keygen with seed is for tests only and is insecure",
            stacklevel=2,
        )
        # Each curve has a known order; the cryptography lib exposes
        # private_key_from_int which validates the scalar is in range.
        rng = random.Random(seed)
        # Pick scalar by bit-length, retry until in [1, n-1]; here we
        # just pick within the curve's bit length and let cryptography
        # raise if invalid.
        bits = curve_cls.key_size
        for _ in range(64):
            scalar = rng.getrandbits(bits)
            if scalar < 1:
                continue
            try:
                priv = _crypto_ec.derive_private_key(scalar, curve_cls)
                break
            except Exception:
                continue
        else:  # pragma: no cover
            raise RuntimeError("seeded ECDH keygen failed")
    else:
        priv = _crypto_ec.generate_private_key(curve_cls)
    pub = priv.public_key()
    pub_bytes = pub.public_bytes(
        encoding=_crypto_serialization.Encoding.X962,
        format=_crypto_serialization.PublicFormat.UncompressedPoint,
    )
    return {
        "private": priv,
        "public": pub,
        "private_int": priv.private_numbers().private_value,
        "public_bytes": pub_bytes,
        "curve": curve,
    }


def ecdh_shared_secret(my_private, their_public, curve: str = "secp256k1") -> bytes:
    """ECDH shared secret as raw bytes. EDUCATIONAL ONLY.

    ``my_private`` is the dict returned by ``ecdh_keygen`` (or a raw
    cryptography private key object). ``their_public`` is the same
    party's dict, raw public key, or serialized X9.62 uncompressed
    bytes.

    Returns:
        The raw ECDH shared secret bytes (no KDF applied).

    Raises:
        ImportError: if `cryptography` is not installed.
        ValueError: if curve is unknown or types mismatch.
    """
    _require_cryptography()
    if curve not in _ECDH_CURVES:
        raise ValueError(
            f"unknown curve {curve!r}; supported: "
            f"{sorted(_ECDH_CURVES)}"
        )
    curve_cls = _ECDH_CURVES[curve]()
    # Resolve my_private to a private-key object.
    priv_obj = my_private
    if isinstance(my_private, dict):
        priv_obj = my_private["private"]
    # Resolve their_public to a public-key object.
    pub_obj = their_public
    if isinstance(their_public, dict):
        pub_obj = their_public["public"]
    elif isinstance(their_public, (bytes, bytearray)):
        pub_obj = _crypto_ec.EllipticCurvePublicKey.from_encoded_point(
            curve_cls, bytes(their_public)
        )
    return priv_obj.exchange(_crypto_ec.ECDH(), pub_obj)
