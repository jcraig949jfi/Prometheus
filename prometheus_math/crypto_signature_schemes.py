"""prometheus_math.crypto_signature_schemes — classical signature schemes.

EDUCATIONAL / RESEARCH USE ONLY.

This module is a teaching wrapper around three classical signature
schemes:

- ECDSA (NIST FIPS 186-4) on secp256k1, P-256 (secp256r1), P-384
  (secp384r1).
- Schnorr signatures, BIP-340 variant on secp256k1 (Bitcoin Taproot).
  Implemented from the spec in pure Python so the algebra is
  inspectable; not constant-time.
- Ed25519 (RFC 8032), via PyCA cryptography. Deterministic EdDSA.

Plus a HMAC-SHA256 helper for cross-checks against signed digests.

DO NOT USE THIS MODULE FOR PRODUCTION SIGNATURE GENERATION OR
VERIFICATION. The Schnorr implementation in particular is a textbook
reference port — vulnerable to timing side-channels, no fault-injection
defence, and uses Python ints for scalar arithmetic. For real
applications use a vetted library (`pyca/cryptography`,
`pynacl`, `coincurve`).

Phase 1 only — Falcon (post-quantum) is deferred to phase 2.

References:
- FIPS 186-4 "Digital Signature Standard (DSS)" (NIST 2013) §6 (ECDSA).
- RFC 6979 "Deterministic Usage of DSA and ECDSA" (Pornin 2013) §A.2.5
  for the P-256 / SHA-256 sample vector.
- RFC 8032 "Edwards-Curve Digital Signature Algorithm (EdDSA)"
  (Josefsson-Liusvaara 2017) §5.1, §7.1 (test vectors).
- BIP-340 "Schnorr Signatures for secp256k1" (Wuille-Nick-Towns 2020).
- RFC 4231 "Identifiers and Test Vectors for HMAC-SHA-...-512"
  (Nystrom 2005).

Module exports:

  ecdsa_keygen(curve='secp256k1', seed=None) -> dict
  ecdsa_sign(message, private_key, curve='secp256k1', hash_alg='sha256') -> bytes
  ecdsa_verify(message, signature, public_key, curve='secp256k1', hash_alg='sha256') -> bool
  schnorr_keygen(curve='secp256k1', seed=None) -> dict
  schnorr_sign(message, private_key, curve='secp256k1', aux_rand=None) -> bytes
  schnorr_verify(message, signature, public_key, curve='secp256k1') -> bool
  ed25519_keygen(seed=None) -> dict
  ed25519_sign(message, private_key) -> bytes
  ed25519_verify(message, signature, public_key) -> bool
  hmac_sign(message, key, hash_alg='sha256') -> bytes
  signature_compare_schemes(message, schemes=None) -> dict
  is_valid_signature_format(signature, scheme) -> bool
"""
from __future__ import annotations

import hashlib
import hmac as _hmac
import os
import secrets
import time
from typing import Optional, Union

# Optional PyCA cryptography backend. We keep import optional so the
# rest of prometheus_math loads even if cryptography is missing; users
# of this module receive a clear ImportError on first call.
try:
    from cryptography.hazmat.primitives.asymmetric import (
        ec as _crypto_ec,
        ed25519 as _crypto_ed25519,
        utils as _crypto_utils,
    )
    from cryptography.hazmat.primitives import (
        hashes as _crypto_hashes,
        serialization as _crypto_serialization,
    )
    from cryptography.exceptions import InvalidSignature as _InvalidSignature
    _HAS_CRYPTOGRAPHY = True
except Exception:  # pragma: no cover
    _HAS_CRYPTOGRAPHY = False


__all__ = [
    "ecdsa_keygen",
    "ecdsa_sign",
    "ecdsa_verify",
    "schnorr_keygen",
    "schnorr_sign",
    "schnorr_verify",
    "ed25519_keygen",
    "ed25519_sign",
    "ed25519_verify",
    "hmac_sign",
    "signature_compare_schemes",
    "is_valid_signature_format",
]


# ---------------------------------------------------------------------------
# Backend gates and shared helpers
# ---------------------------------------------------------------------------


def _require_cryptography() -> None:
    if not _HAS_CRYPTOGRAPHY:
        raise ImportError(
            "crypto_signature_schemes requires the `cryptography` package. "
            "Install with `pip install cryptography`."
        )


_HASH_TABLE: dict = {}
if _HAS_CRYPTOGRAPHY:
    _HASH_TABLE = {
        "sha256": _crypto_hashes.SHA256,
        "sha384": _crypto_hashes.SHA384,
        "sha512": _crypto_hashes.SHA512,
    }


def _resolve_hash(hash_alg: str):
    if hash_alg not in _HASH_TABLE:
        raise ValueError(
            f"unknown hash_alg {hash_alg!r}; supported: "
            f"{sorted(_HASH_TABLE)}"
        )
    return _HASH_TABLE[hash_alg]()


_ECDSA_CURVES: dict = {}
if _HAS_CRYPTOGRAPHY:
    _ECDSA_CURVES = {
        "secp256k1": _crypto_ec.SECP256K1,
        "secp256r1": _crypto_ec.SECP256R1,
        "secp384r1": _crypto_ec.SECP384R1,
    }


def _resolve_curve(curve: str):
    if curve not in _ECDSA_CURVES:
        raise ValueError(
            f"unknown curve {curve!r}; supported: "
            f"{sorted(_ECDSA_CURVES)}"
        )
    return _ECDSA_CURVES[curve]()


def _coerce_message(message) -> bytes:
    """Coerce message-like inputs to bytes; raise on incompatible types.

    Educational convenience: strings are auto-encoded as UTF-8.
    """
    if isinstance(message, (bytes, bytearray, memoryview)):
        return bytes(message)
    if isinstance(message, str):
        return message.encode("utf-8")
    raise TypeError(
        f"message must be bytes or str, got {type(message).__name__}"
    )


def _check_nonempty_key(key: bytes, name: str = "private_key") -> bytes:
    if not isinstance(key, (bytes, bytearray)):
        raise TypeError(
            f"{name} must be bytes, got {type(key).__name__}"
        )
    key = bytes(key)
    if len(key) == 0:
        raise ValueError(f"{name} must be non-empty")
    return key


# ---------------------------------------------------------------------------
# ECDSA
# ---------------------------------------------------------------------------


def ecdsa_keygen(
    curve: str = "secp256k1",
    seed: Optional[Union[int, bytes]] = None,
) -> dict:
    """Generate an ECDSA keypair on a named curve. EDUCATIONAL ONLY.

    Args:
        curve: one of {'secp256k1', 'secp256r1', 'secp384r1'}.
        seed: optional integer / bytes scalar to derive a deterministic
            private key. If given, must be in [1, n-1] where n is the
            curve order. EDUCATIONAL — never seed real keys.

    Returns:
        Dict with keys:
            'private_key': bytes (raw scalar, big-endian)
            'public_key':  bytes (X9.62 uncompressed point)
            'curve':       str (curve name)

    Raises:
        ValueError: if curve unknown.
        ImportError: if `cryptography` is not installed.
    """
    _require_cryptography()
    curve_cls = _resolve_curve(curve)
    if seed is not None:
        if isinstance(seed, bytes):
            scalar = int.from_bytes(seed, "big")
        else:
            scalar = int(seed)
        priv = _crypto_ec.derive_private_key(scalar, curve_cls)
    else:
        priv = _crypto_ec.generate_private_key(curve_cls)
    pub = priv.public_key()
    priv_bytes = priv.private_numbers().private_value.to_bytes(
        (curve_cls.key_size + 7) // 8, "big"
    )
    pub_bytes = pub.public_bytes(
        encoding=_crypto_serialization.Encoding.X962,
        format=_crypto_serialization.PublicFormat.UncompressedPoint,
    )
    return {
        "private_key": priv_bytes,
        "public_key": pub_bytes,
        "curve": curve,
    }


def ecdsa_sign(
    message,
    private_key: bytes,
    curve: str = "secp256k1",
    hash_alg: str = "sha256",
) -> bytes:
    """Sign ``message`` with raw-scalar ``private_key`` under ECDSA.

    Returns the DER-encoded signature (RFC 5912 SEQUENCE OF INTEGER, INTEGER).

    Args:
        message: bytes (or str, auto-encoded UTF-8).
        private_key: raw big-endian scalar in [1, n-1].
        curve: see ecdsa_keygen.
        hash_alg: 'sha256' | 'sha384' | 'sha512'.
    """
    _require_cryptography()
    curve_cls = _resolve_curve(curve)
    hash_obj = _resolve_hash(hash_alg)
    msg = _coerce_message(message)
    sk = _check_nonempty_key(private_key, "private_key")
    scalar = int.from_bytes(sk, "big")
    if scalar == 0:
        raise ValueError("private_key scalar is 0; must be in [1, n-1]")
    priv = _crypto_ec.derive_private_key(scalar, curve_cls)
    return priv.sign(msg, _crypto_ec.ECDSA(hash_obj))


def ecdsa_verify(
    message,
    signature: bytes,
    public_key: bytes,
    curve: str = "secp256k1",
    hash_alg: str = "sha256",
) -> bool:
    """Verify an ECDSA signature.

    ``public_key`` is X9.62-uncompressed point bytes (as returned by
    ecdsa_keygen). Returns True on success, False on any failure
    (signature parse error, wrong curve, tampered message/signature).

    Raises:
        ValueError: on unknown curve / unknown hash_alg / empty inputs.
    """
    _require_cryptography()
    curve_cls = _resolve_curve(curve)
    hash_obj = _resolve_hash(hash_alg)
    msg = _coerce_message(message)
    if not isinstance(signature, (bytes, bytearray)):
        raise TypeError(
            f"signature must be bytes, got {type(signature).__name__}"
        )
    if not isinstance(public_key, (bytes, bytearray)) or len(public_key) == 0:
        raise ValueError("public_key must be non-empty bytes")
    try:
        pub = _crypto_ec.EllipticCurvePublicKey.from_encoded_point(
            curve_cls, bytes(public_key)
        )
    except Exception:
        return False
    try:
        pub.verify(bytes(signature), msg, _crypto_ec.ECDSA(hash_obj))
        return True
    except _InvalidSignature:
        return False
    except Exception:
        # Cross-curve / malformed sig / etc. — treat as verification failure.
        return False


# ---------------------------------------------------------------------------
# BIP-340 Schnorr on secp256k1 (pure Python reference port)
# ---------------------------------------------------------------------------

# secp256k1 parameters (BIP-340 §spec).
_BIP340_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_BIP340_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_BIP340_GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_BIP340_GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
_BIP340_G = (_BIP340_GX, _BIP340_GY)


def _bip340_point_add(P1, P2):
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    if P1[0] == P2[0] and P1[1] != P2[1]:
        return None
    if P1 == P2:
        lam = (
            3 * P1[0] * P1[0] * pow(2 * P1[1], _BIP340_P - 2, _BIP340_P)
        ) % _BIP340_P
    else:
        lam = (
            (P2[1] - P1[1]) * pow(P2[0] - P1[0], _BIP340_P - 2, _BIP340_P)
        ) % _BIP340_P
    x3 = (lam * lam - P1[0] - P2[0]) % _BIP340_P
    y3 = (lam * (P1[0] - x3) - P1[1]) % _BIP340_P
    return (x3, y3)


def _bip340_point_mul(P, n):
    R = None
    while n:
        if n & 1:
            R = _bip340_point_add(R, P)
        P = _bip340_point_add(P, P)
        n >>= 1
    return R


def _bip340_lift_x(x: int):
    if x >= _BIP340_P:
        return None
    y_sq = (pow(x, 3, _BIP340_P) + 7) % _BIP340_P
    y = pow(y_sq, (_BIP340_P + 1) // 4, _BIP340_P)
    if pow(y, 2, _BIP340_P) != y_sq:
        return None
    return (x, y if y % 2 == 0 else _BIP340_P - y)


def _bip340_has_even_y(P) -> bool:
    return P[1] % 2 == 0


def _bip340_int_from_bytes(b: bytes) -> int:
    return int.from_bytes(b, "big")


def _bip340_bytes_from_int(x: int) -> bytes:
    return x.to_bytes(32, "big")


def _bip340_tagged_hash(tag: str, msg: bytes) -> bytes:
    tag_h = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(tag_h + tag_h + msg).digest()


def schnorr_keygen(
    curve: str = "secp256k1",
    seed: Optional[Union[int, bytes]] = None,
) -> dict:
    """Generate a BIP-340 Schnorr keypair on secp256k1. EDUCATIONAL ONLY.

    Returns a dict with raw 32-byte ``private_key`` and 32-byte x-only
    ``public_key`` (per BIP-340 §SIG: pubkeys are x-only).

    Args:
        curve: must be 'secp256k1'; BIP-340 is locked to this curve.
        seed: optional integer / bytes scalar. If given, must yield a
            scalar in [1, n-1].
    """
    if curve != "secp256k1":
        raise ValueError(
            f"BIP-340 Schnorr only supports secp256k1, got {curve!r}"
        )
    if seed is not None:
        if isinstance(seed, bytes):
            d0 = _bip340_int_from_bytes(seed) % _BIP340_N
        else:
            d0 = int(seed) % _BIP340_N
        if d0 == 0:
            raise ValueError("seed reduces to 0 mod n; pick a different seed")
    else:
        d0 = secrets.randbelow(_BIP340_N - 1) + 1
    P = _bip340_point_mul(_BIP340_G, d0)
    pub_x = _bip340_bytes_from_int(P[0])
    sk_bytes = _bip340_bytes_from_int(d0)
    return {
        "private_key": sk_bytes,
        "public_key": pub_x,
        "curve": curve,
    }


def schnorr_sign(
    message,
    private_key: bytes,
    curve: str = "secp256k1",
    aux_rand: Optional[bytes] = None,
) -> bytes:
    """BIP-340 Schnorr signature on secp256k1.

    Args:
        message: bytes (or str, auto-encoded). Any length permitted.
        private_key: raw 32-byte scalar in [1, n-1] (big-endian).
        curve: must be 'secp256k1'.
        aux_rand: optional 32-byte auxiliary randomness. If None, a
            fresh 32 bytes from secrets is used. For known-answer
            tests, pass the spec's aux value explicitly.

    Returns:
        64-byte BIP-340 signature (R.x || s).
    """
    if curve != "secp256k1":
        raise ValueError(
            f"BIP-340 Schnorr only supports secp256k1, got {curve!r}"
        )
    msg = _coerce_message(message)
    sk = _check_nonempty_key(private_key, "private_key")
    if len(sk) != 32:
        raise ValueError(
            f"BIP-340 private_key must be 32 bytes, got {len(sk)}"
        )
    d0 = _bip340_int_from_bytes(sk)
    if not (1 <= d0 <= _BIP340_N - 1):
        raise ValueError("private_key scalar out of range [1, n-1]")
    if aux_rand is None:
        aux_rand = secrets.token_bytes(32)
    if not isinstance(aux_rand, (bytes, bytearray)) or len(aux_rand) != 32:
        raise ValueError("aux_rand must be 32 bytes")
    aux_rand = bytes(aux_rand)
    P = _bip340_point_mul(_BIP340_G, d0)
    d = d0 if _bip340_has_even_y(P) else _BIP340_N - d0
    t = (d ^ _bip340_int_from_bytes(
        _bip340_tagged_hash("BIP0340/aux", aux_rand)
    )).to_bytes(32, "big")
    rand = _bip340_tagged_hash(
        "BIP0340/nonce", t + _bip340_bytes_from_int(P[0]) + msg
    )
    k0 = _bip340_int_from_bytes(rand) % _BIP340_N
    if k0 == 0:  # pragma: no cover (vanishingly rare)
        raise RuntimeError("BIP-340 nonce reduced to 0")
    R = _bip340_point_mul(_BIP340_G, k0)
    k = k0 if _bip340_has_even_y(R) else _BIP340_N - k0
    e = _bip340_int_from_bytes(
        _bip340_tagged_hash(
            "BIP0340/challenge",
            _bip340_bytes_from_int(R[0])
            + _bip340_bytes_from_int(P[0])
            + msg,
        )
    ) % _BIP340_N
    s = (k + e * d) % _BIP340_N
    return _bip340_bytes_from_int(R[0]) + _bip340_bytes_from_int(s)


def schnorr_verify(
    message,
    signature: bytes,
    public_key: bytes,
    curve: str = "secp256k1",
) -> bool:
    """Verify a BIP-340 Schnorr signature on secp256k1.

    Returns True on success, False on any failure (parse error,
    point not on curve, tampered values).
    """
    if curve != "secp256k1":
        raise ValueError(
            f"BIP-340 Schnorr only supports secp256k1, got {curve!r}"
        )
    msg = _coerce_message(message)
    if not isinstance(signature, (bytes, bytearray)) or len(signature) != 64:
        return False
    if not isinstance(public_key, (bytes, bytearray)) or len(public_key) != 32:
        return False
    signature = bytes(signature)
    public_key = bytes(public_key)
    Px = _bip340_int_from_bytes(public_key)
    P = _bip340_lift_x(Px)
    if P is None:
        return False
    r = _bip340_int_from_bytes(signature[:32])
    s = _bip340_int_from_bytes(signature[32:])
    if r >= _BIP340_P or s >= _BIP340_N:
        return False
    e = _bip340_int_from_bytes(
        _bip340_tagged_hash(
            "BIP0340/challenge",
            signature[:32] + public_key + msg,
        )
    ) % _BIP340_N
    # R = s*G - e*P  (BIP-340 verification)
    sG = _bip340_point_mul(_BIP340_G, s)
    eP = _bip340_point_mul(P, _BIP340_N - e)  # negate by N-e
    R = _bip340_point_add(sG, eP)
    if R is None:
        return False
    if not _bip340_has_even_y(R):
        return False
    return R[0] == r


# ---------------------------------------------------------------------------
# Ed25519 (RFC 8032)
# ---------------------------------------------------------------------------


def ed25519_keygen(seed: Optional[bytes] = None) -> dict:
    """Generate an Ed25519 keypair (RFC 8032). EDUCATIONAL ONLY.

    Args:
        seed: optional 32-byte seed (= the RFC 8032 "private key").
            When None, a fresh 32 random bytes is used.

    Returns:
        Dict with 'private_key' (32 bytes), 'public_key' (32 bytes,
        the encoded Edwards point), and 'curve' = 'ed25519'.
    """
    _require_cryptography()
    if seed is None:
        sk = _crypto_ed25519.Ed25519PrivateKey.generate()
        seed_bytes = sk.private_bytes(
            encoding=_crypto_serialization.Encoding.Raw,
            format=_crypto_serialization.PrivateFormat.Raw,
            encryption_algorithm=_crypto_serialization.NoEncryption(),
        )
    else:
        if not isinstance(seed, (bytes, bytearray)):
            raise TypeError(
                f"seed must be bytes, got {type(seed).__name__}"
            )
        seed_bytes = bytes(seed)
        if len(seed_bytes) != 32:
            raise ValueError(
                f"Ed25519 seed must be 32 bytes, got {len(seed_bytes)}"
            )
        sk = _crypto_ed25519.Ed25519PrivateKey.from_private_bytes(seed_bytes)
    pk = sk.public_key()
    pk_bytes = pk.public_bytes(
        encoding=_crypto_serialization.Encoding.Raw,
        format=_crypto_serialization.PublicFormat.Raw,
    )
    return {
        "private_key": seed_bytes,
        "public_key": pk_bytes,
        "curve": "ed25519",
    }


def ed25519_sign(message, private_key: bytes) -> bytes:
    """RFC 8032 Ed25519 signature.

    Args:
        message: bytes (or str, auto-encoded UTF-8).
        private_key: 32-byte seed.

    Returns:
        64-byte detached signature.
    """
    _require_cryptography()
    msg = _coerce_message(message)
    sk = _check_nonempty_key(private_key, "private_key")
    if len(sk) != 32:
        raise ValueError(
            f"Ed25519 private_key must be 32 bytes, got {len(sk)}"
        )
    obj = _crypto_ed25519.Ed25519PrivateKey.from_private_bytes(sk)
    return obj.sign(msg)


def ed25519_verify(
    message, signature: bytes, public_key: bytes
) -> bool:
    """RFC 8032 Ed25519 signature verification.

    Returns True on success, False on parse / verification failure.

    Raises:
        ValueError: if public_key is not exactly 32 bytes.
    """
    _require_cryptography()
    msg = _coerce_message(message)
    if not isinstance(public_key, (bytes, bytearray)):
        raise TypeError(
            f"public_key must be bytes, got {type(public_key).__name__}"
        )
    if len(public_key) != 32:
        raise ValueError(
            f"Ed25519 public_key must be 32 bytes, got {len(public_key)}"
        )
    if not isinstance(signature, (bytes, bytearray)):
        raise TypeError(
            f"signature must be bytes, got {type(signature).__name__}"
        )
    try:
        obj = _crypto_ed25519.Ed25519PublicKey.from_public_bytes(
            bytes(public_key)
        )
    except Exception:
        return False
    try:
        obj.verify(bytes(signature), msg)
        return True
    except _InvalidSignature:
        return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# HMAC (symmetric MAC for cross-checks)
# ---------------------------------------------------------------------------

_HMAC_HASH_TABLE = {
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    "sha1": hashlib.sha1,
}


def hmac_sign(
    message,
    key: bytes,
    hash_alg: str = "sha256",
) -> bytes:
    """RFC 2104 / 4231 HMAC.

    Args:
        message: bytes / str.
        key: bytes (any length; per RFC 2104 keys longer than the
            block size are pre-hashed).
        hash_alg: 'sha256' (default), 'sha384', 'sha512', 'sha1'.

    Returns:
        Raw HMAC tag (length = digest size of the hash).
    """
    if hash_alg not in _HMAC_HASH_TABLE:
        raise ValueError(
            f"unknown hash_alg {hash_alg!r}; supported: "
            f"{sorted(_HMAC_HASH_TABLE)}"
        )
    msg = _coerce_message(message)
    if not isinstance(key, (bytes, bytearray)):
        raise TypeError(
            f"key must be bytes, got {type(key).__name__}"
        )
    return _hmac.new(bytes(key), msg, _HMAC_HASH_TABLE[hash_alg]).digest()


# ---------------------------------------------------------------------------
# Cross-scheme benchmark and format-validation helpers
# ---------------------------------------------------------------------------


def signature_compare_schemes(
    message,
    schemes: Optional[list] = None,
) -> dict:
    """Benchmark sign + verify time across schemes. EDUCATIONAL.

    For each scheme in ``schemes`` (default: all three), the routine
    (a) generates a keypair, (b) signs ``message``, (c) verifies the
    signature, and reports per-step wall-clock time plus a boolean
    'verified'.

    The output is a dict keyed by scheme name with sub-dicts
    ``{'sign_seconds', 'verify_seconds', 'verified', 'sig_bytes'}``.
    """
    msg = _coerce_message(message)
    if schemes is None:
        schemes = ["ecdsa", "schnorr", "ed25519"]
    out: dict = {}
    for scheme in schemes:
        if scheme == "ecdsa":
            key = ecdsa_keygen(curve="secp256k1")
            t0 = time.perf_counter()
            sig = ecdsa_sign(msg, key["private_key"], curve="secp256k1")
            t1 = time.perf_counter()
            ok = ecdsa_verify(
                msg, sig, key["public_key"], curve="secp256k1"
            )
            t2 = time.perf_counter()
        elif scheme == "schnorr":
            key = schnorr_keygen()
            t0 = time.perf_counter()
            sig = schnorr_sign(msg, key["private_key"])
            t1 = time.perf_counter()
            ok = schnorr_verify(msg, sig, key["public_key"])
            t2 = time.perf_counter()
        elif scheme == "ed25519":
            key = ed25519_keygen()
            t0 = time.perf_counter()
            sig = ed25519_sign(msg, key["private_key"])
            t1 = time.perf_counter()
            ok = ed25519_verify(msg, sig, key["public_key"])
            t2 = time.perf_counter()
        else:
            raise ValueError(f"unknown scheme {scheme!r}")
        out[scheme] = {
            "sign_seconds": t1 - t0,
            "verify_seconds": t2 - t1,
            "verified": bool(ok),
            "sig_bytes": len(sig),
        }
    return out


def is_valid_signature_format(signature: bytes, scheme: str) -> bool:
    """Quick syntactic format check (length only) per scheme.

    - schnorr  : 64-byte (R.x || s)
    - ed25519  : 64-byte (R || S)
    - ecdsa    : DER-encoded ASN.1 SEQUENCE (we check decode-ability)

    Raises ValueError on unknown scheme.
    """
    if scheme not in ("ecdsa", "schnorr", "ed25519"):
        raise ValueError(
            f"unknown scheme {scheme!r}; supported: "
            f"['ecdsa', 'schnorr', 'ed25519']"
        )
    if not isinstance(signature, (bytes, bytearray)):
        return False
    if scheme in ("schnorr", "ed25519"):
        return len(signature) == 64
    # ecdsa: try to decode DER; valid DER => True, anything else => False.
    if not _HAS_CRYPTOGRAPHY:
        # Fall back to a length sanity check (DER-encoded ECDSA sig is
        # roughly 70-72 bytes for P-256, up to 144 for P-521).
        return 8 <= len(signature) <= 256
    try:
        _crypto_utils.decode_dss_signature(bytes(signature))
        return True
    except Exception:
        return False
