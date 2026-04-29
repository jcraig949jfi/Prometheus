"""Tests for prometheus_math.crypto_signature_schemes (project #84 phase 1).

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority: NIST FIPS 186-4 / RFC 6979 ECDSA P-256 known triple,
  BIP-340 Schnorr test-vector 1, RFC 8032 Ed25519 vector "test 1"
  (empty message, sk=9d61...), HMAC-SHA256 RFC 4231 vectors.
- Property: sign+verify round-trip for ECDSA / Schnorr / Ed25519,
  tampered-message rejection, tampered-signature rejection,
  Schnorr/Ed25519 determinism, distinct keys yield distinct pubkeys.
- Edge: empty message handled, empty key ValueError, invalid curve
  ValueError, wrong-length key bytes ValueError, non-bytes message
  encoded or rejected, hash_alg='unknown' ValueError.
- Composition: keygen -> sign -> verify cycle for all three schemes,
  HMAC + ECDSA composition, cross-curve compatibility.

EDUCATIONAL ONLY — these tests document a research/teaching wrapper
around PyCA cryptography + a pure-Python BIP-340 implementation.
"""
from __future__ import annotations

import hashlib
import hmac as _hmac_stdlib
import pytest

# Detect cryptography availability up front; skip the file if missing.
cryptography = pytest.importorskip("cryptography")

from hypothesis import given, settings, strategies as st

from prometheus_math.crypto_signature_schemes import (
    ecdsa_keygen,
    ecdsa_sign,
    ecdsa_verify,
    schnorr_keygen,
    schnorr_sign,
    schnorr_verify,
    ed25519_keygen,
    ed25519_sign,
    ed25519_verify,
    hmac_sign,
    signature_compare_schemes,
    is_valid_signature_format,
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_ecdsa_p256_rfc6979_sample_vector_verifies():
    """RFC 6979 §A.2.5 ECDSA P-256/SHA-256 known triple verifies.

    Reference: RFC 6979 §A.2.5 (Pornin 2013). Inputs:
      private key x = C9AF...6721
      public key Ux/Uy as listed
      message = b"sample"
      (deterministic) (r, s) = (EFD4..3716, F7CB..ACDA8)

    We construct (sig, pubkey) from the published values and ask the
    verify routine to accept. This pins the verify path against an
    RFC-mandated value.
    """
    from cryptography.hazmat.primitives.asymmetric import ec, utils as _crypto_utils
    priv_int = int(
        "C9AFA9D845BA75166B5C215767B1D6934E50C3DB36E89B127B8A622B120F6721", 16
    )
    r_int = int(
        "EFD48B2AACB6A8FD1140DD9CD45E81D69D2C877B56AAF991C34D0EA84EAF3716", 16
    )
    s_int = int(
        "F7CB1C942D657C41D436C7A1B6E29F65F3E900DBB9AFF4064DC4AB2F843ACDA8", 16
    )
    # Reconstruct public key in our representation.
    priv = ec.derive_private_key(priv_int, ec.SECP256R1())
    pub = priv.public_key()
    from cryptography.hazmat.primitives import serialization
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )
    sig = _crypto_utils.encode_dss_signature(r_int, s_int)
    assert ecdsa_verify(b"sample", sig, pub_bytes, curve="secp256r1") is True


def test_schnorr_bip340_vector_1():
    """BIP-340 test vector 1 (with auxiliary randomness 0x00..01).

    Reference: https://github.com/bitcoin/bips/blob/master/bip-0340/
    test-vectors.csv index 1.

      sk = B7E1...CFEF
      pubkey = DFF1...A659  (x-only, 32 bytes)
      msg = 243F...6C89
      aux_rand = 00..01
      sig = 6896...4B0A

    The signing routine accepts an explicit aux_rand for KAT testing
    (this is allowed by BIP-340 §SIG: aux_rand is recommended random
    but may be set to a fixed value).
    """
    sk = bytes.fromhex(
        "B7E151628AED2A6ABF7158809CF4F3C762E7160F38B4DA56A784D9045190CFEF"
    )
    msg = bytes.fromhex(
        "243F6A8885A308D313198A2E03707344A4093822299F31D0082EFA98EC4E6C89"
    )
    aux = bytes.fromhex(
        "0000000000000000000000000000000000000000000000000000000000000001"
    )
    expected_pub = bytes.fromhex(
        "DFF1D77F2A671C5F36183726DB2341BE58FEAE1DA2DECED843240F7B502BA659"
    )
    expected_sig = bytes.fromhex(
        "6896BD60EEAE296DB48A229FF71DFE071BDE413E6D43F917DC8DCF8C78DE33418906D11AC976ABCCB20B091292BFF4EA897EFCB639EA871CFA95F6DE339E4B0A"
    )
    sig = schnorr_sign(msg, sk, aux_rand=aux)
    assert sig == expected_sig
    assert schnorr_verify(msg, sig, expected_pub) is True


def test_ed25519_rfc8032_test_1_empty_message():
    """RFC 8032 §7.1 ed25519 "Test 1" KAT.

    sk      = 9d61b19deffd5a60ba844af492ec2cc4
              4449c5697b326919703bac031cae7f60
    pk      = d75a980182b10ab7d54bfed3c964073a
              0ee172f3daa62325af021a68f707511a
    msg     = (empty)
    sig     = e5564300c360ac729086e2cc806e828a
              84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701c
              f9b46bd25bf5f0595bbe24655141438e7a100b

    Reference: RFC 8032 §7.1 (Josefsson-Liusvaara 2017).
    """
    sk = bytes.fromhex(
        "9d61b19deffd5a60ba844af492ec2cc4"
        "4449c5697b326919703bac031cae7f60"
    )
    expected_pk = bytes.fromhex(
        "d75a980182b10ab7d54bfed3c964073a"
        "0ee172f3daa62325af021a68f707511a"
    )
    expected_sig = bytes.fromhex(
        "e5564300c360ac729086e2cc806e828a"
        "84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701c"
        "f9b46bd25bf5f0595bbe24655141438e7a100b"
    )
    key = ed25519_keygen(seed=sk)
    assert key["public_key"] == expected_pk
    assert key["private_key"] == sk
    sig = ed25519_sign(b"", sk)
    assert sig == expected_sig
    assert ed25519_verify(b"", sig, expected_pk) is True


def test_hmac_sha256_rfc4231_test_1():
    """RFC 4231 §4.2 HMAC-SHA256 test case 1.

    key  = 0x0b * 20
    data = b"Hi There"
    HMAC-SHA-256 = b0344c61d8db38535ca8afceaf0bf12b
                   881dc200c9833da726e9376c2e32cff7

    Reference: RFC 4231 §4.2 (Nystrom 2005).
    """
    key = b"\x0b" * 20
    data = b"Hi There"
    expected = bytes.fromhex(
        "b0344c61d8db38535ca8afceaf0bf12b"
        "881dc200c9833da726e9376c2e32cff7"
    )
    assert hmac_sign(data, key, hash_alg="sha256") == expected


def test_hmac_sha256_rfc4231_test_2():
    """RFC 4231 §4.3 HMAC-SHA256 test case 2.

    key  = b"Jefe"
    data = b"what do ya want for nothing?"
    HMAC-SHA-256 = 5bdcc146bf60754e6a042426089575c7
                   5a003f089d2739839dec58b964ec3843
    """
    key = b"Jefe"
    data = b"what do ya want for nothing?"
    expected = bytes.fromhex(
        "5bdcc146bf60754e6a042426089575c7"
        "5a003f089d2739839dec58b964ec3843"
    )
    assert hmac_sign(data, key, hash_alg="sha256") == expected


def test_distinct_keys_distinct_pubkeys():
    """Two unrelated keygens must produce distinct public keys for all
    schemes (with overwhelming probability, hand-checked here)."""
    a = ecdsa_keygen(curve="secp256k1")
    b = ecdsa_keygen(curve="secp256k1")
    assert a["public_key"] != b["public_key"]

    a2 = schnorr_keygen()
    b2 = schnorr_keygen()
    assert a2["public_key"] != b2["public_key"]

    a3 = ed25519_keygen()
    b3 = ed25519_keygen()
    assert a3["public_key"] != b3["public_key"]


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------


@given(st.binary(min_size=0, max_size=128))
@settings(max_examples=15, deadline=None)
def test_ecdsa_round_trip(message):
    """ECDSA on secp256k1 sign+verify round-trip for arbitrary bytes."""
    key = ecdsa_keygen(curve="secp256k1")
    sig = ecdsa_sign(message, key["private_key"], curve="secp256k1")
    assert ecdsa_verify(
        message, sig, key["public_key"], curve="secp256k1"
    ) is True


@given(st.binary(min_size=0, max_size=128))
@settings(max_examples=15, deadline=None)
def test_schnorr_round_trip(message):
    """BIP-340 Schnorr sign+verify round-trip on secp256k1."""
    key = schnorr_keygen()
    sig = schnorr_sign(message, key["private_key"])
    assert schnorr_verify(message, sig, key["public_key"]) is True


@given(st.binary(min_size=0, max_size=128))
@settings(max_examples=15, deadline=None)
def test_ed25519_round_trip(message):
    """Ed25519 sign+verify round-trip."""
    key = ed25519_keygen()
    sig = ed25519_sign(message, key["private_key"])
    assert ed25519_verify(message, sig, key["public_key"]) is True


def test_tampered_message_fails_verification():
    """For all three schemes, flipping a bit in the message must cause
    verify to return False."""
    msg = b"the quick brown fox jumps over the lazy dog"
    bad_msg = b"the quick brown fox jumps over the lazy CAT"

    e_key = ecdsa_keygen(curve="secp256k1")
    e_sig = ecdsa_sign(msg, e_key["private_key"], curve="secp256k1")
    assert ecdsa_verify(
        bad_msg, e_sig, e_key["public_key"], curve="secp256k1"
    ) is False

    s_key = schnorr_keygen()
    s_sig = schnorr_sign(msg, s_key["private_key"])
    assert schnorr_verify(bad_msg, s_sig, s_key["public_key"]) is False

    d_key = ed25519_keygen()
    d_sig = ed25519_sign(msg, d_key["private_key"])
    assert ed25519_verify(bad_msg, d_sig, d_key["public_key"]) is False


def test_tampered_signature_fails_verification():
    """Flipping a bit in the signature must cause verify to return False
    for all three schemes."""
    msg = b"signed message"

    def flip_first_byte(b: bytes) -> bytes:
        return bytes([b[0] ^ 0x01]) + b[1:]

    e_key = ecdsa_keygen(curve="secp256k1")
    e_sig = ecdsa_sign(msg, e_key["private_key"], curve="secp256k1")
    assert ecdsa_verify(
        msg, flip_first_byte(e_sig), e_key["public_key"], curve="secp256k1"
    ) is False

    s_key = schnorr_keygen()
    s_sig = schnorr_sign(msg, s_key["private_key"])
    assert schnorr_verify(
        msg, flip_first_byte(s_sig), s_key["public_key"]
    ) is False

    d_key = ed25519_keygen()
    d_sig = ed25519_sign(msg, d_key["private_key"])
    assert ed25519_verify(
        msg, flip_first_byte(d_sig), d_key["public_key"]
    ) is False


def test_schnorr_is_deterministic_when_aux_fixed():
    """BIP-340 Schnorr is deterministic when aux_rand is fixed.

    Same (msg, sk, aux_rand) -> same signature. (Note: BIP-340 omits
    aux_rand by accepting random, but with explicit aux fixed the
    output is fully deterministic — all randomness lives in aux_rand.)
    """
    key = schnorr_keygen()
    msg = b"deterministic check"
    aux = b"\x00" * 32
    sig1 = schnorr_sign(msg, key["private_key"], aux_rand=aux)
    sig2 = schnorr_sign(msg, key["private_key"], aux_rand=aux)
    assert sig1 == sig2


def test_ed25519_is_deterministic():
    """Ed25519 is deterministic by RFC 8032 — same (msg, sk) yields the
    same signature on every call."""
    key = ed25519_keygen()
    msg = b"deterministic check"
    sig1 = ed25519_sign(msg, key["private_key"])
    sig2 = ed25519_sign(msg, key["private_key"])
    assert sig1 == sig2


def test_keygen_distinct_pubkeys_unseeded():
    """Without a fixed seed, two keygen calls produce different pubkeys."""
    a = ed25519_keygen()
    b = ed25519_keygen()
    assert a["public_key"] != b["public_key"]


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_empty_message_signs_and_verifies():
    """Empty bytes b'' must produce a valid signature for all schemes
    (RFC 8032 explicitly tests empty message)."""
    e_key = ecdsa_keygen(curve="secp256r1")
    e_sig = ecdsa_sign(b"", e_key["private_key"], curve="secp256r1")
    assert ecdsa_verify(
        b"", e_sig, e_key["public_key"], curve="secp256r1"
    ) is True

    s_key = schnorr_keygen()
    s_sig = schnorr_sign(b"", s_key["private_key"])
    assert schnorr_verify(b"", s_sig, s_key["public_key"]) is True

    d_key = ed25519_keygen()
    d_sig = ed25519_sign(b"", d_key["private_key"])
    assert ed25519_verify(b"", d_sig, d_key["public_key"]) is True


def test_empty_key_raises():
    """Empty private-key bytes must raise ValueError for each scheme."""
    with pytest.raises(ValueError):
        ecdsa_sign(b"msg", b"", curve="secp256k1")
    with pytest.raises(ValueError):
        schnorr_sign(b"msg", b"")
    with pytest.raises(ValueError):
        ed25519_sign(b"msg", b"")


def test_invalid_curve_raises():
    """Unknown curve names must raise ValueError."""
    with pytest.raises(ValueError):
        ecdsa_keygen(curve="not-a-curve")
    with pytest.raises(ValueError):
        ecdsa_sign(b"m", b"\x01" * 32, curve="not-a-curve")
    # Schnorr (BIP-340) is locked to secp256k1; other curves rejected.
    with pytest.raises(ValueError):
        schnorr_keygen(curve="secp256r1")


def test_wrong_length_key_raises():
    """Wrong-length private key bytes must raise ValueError."""
    # Schnorr (secp256k1) requires 32-byte sk.
    with pytest.raises(ValueError):
        schnorr_sign(b"msg", b"\x01" * 16)
    # Ed25519 requires 32-byte seed.
    with pytest.raises(ValueError):
        ed25519_sign(b"msg", b"\x01" * 16)
    # Ed25519 verify requires 32-byte public key.
    valid = ed25519_keygen()
    sig = ed25519_sign(b"msg", valid["private_key"])
    with pytest.raises(ValueError):
        ed25519_verify(b"msg", sig, b"\x01" * 16)


def test_non_bytes_message_is_encoded_or_rejected():
    """Strings should be auto-encoded as UTF-8 (educational convenience).

    Non-bytes/non-str types must raise TypeError or ValueError.
    """
    key = ed25519_keygen()
    # str: auto-encoded.
    sig = ed25519_sign("hello", key["private_key"])
    assert ed25519_verify("hello", sig, key["public_key"]) is True
    # int: not coercible.
    with pytest.raises((TypeError, ValueError)):
        ed25519_sign(12345, key["private_key"])


def test_unknown_hash_alg_raises():
    """ECDSA hash_alg='unknown' must raise ValueError."""
    key = ecdsa_keygen(curve="secp256k1")
    with pytest.raises(ValueError):
        ecdsa_sign(b"msg", key["private_key"], hash_alg="not-a-hash")
    with pytest.raises(ValueError):
        hmac_sign(b"msg", b"key", hash_alg="not-a-hash")


def test_is_valid_signature_format_basic():
    """Signature-format helper accepts well-formed sigs and rejects
    obviously malformed ones."""
    key = schnorr_keygen()
    sig = schnorr_sign(b"x", key["private_key"])
    assert is_valid_signature_format(sig, "schnorr") is True
    # Wrong length.
    assert is_valid_signature_format(b"too short", "schnorr") is False
    # Ed25519 sigs are 64 bytes.
    ed_key = ed25519_keygen()
    ed_sig = ed25519_sign(b"x", ed_key["private_key"])
    assert is_valid_signature_format(ed_sig, "ed25519") is True
    assert is_valid_signature_format(b"\x00" * 32, "ed25519") is False
    # Unknown scheme.
    with pytest.raises(ValueError):
        is_valid_signature_format(ed_sig, "not-a-scheme")


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_full_keygen_sign_verify_cycle_all_schemes():
    """End-to-end keygen → sign → verify works for ECDSA, Schnorr,
    and Ed25519. Composition test."""
    msg = b"end to end"
    # ECDSA
    ek = ecdsa_keygen(curve="secp256k1")
    es = ecdsa_sign(msg, ek["private_key"], curve="secp256k1")
    assert ecdsa_verify(msg, es, ek["public_key"], curve="secp256k1")
    # Schnorr
    sk = schnorr_keygen()
    ss = schnorr_sign(msg, sk["private_key"])
    assert schnorr_verify(msg, ss, sk["public_key"])
    # Ed25519
    dk = ed25519_keygen()
    ds = ed25519_sign(msg, dk["private_key"])
    assert ed25519_verify(msg, ds, dk["public_key"])


def test_hmac_then_ecdsa_composition():
    """Long-message protocol: HMAC the long message to a digest, then
    sign the digest with ECDSA. Composition of hmac_sign + ecdsa_sign
    + ecdsa_verify."""
    long_msg = b"x" * 4096
    mac_key = b"\xaa" * 32
    digest = hmac_sign(long_msg, mac_key, hash_alg="sha256")
    assert len(digest) == 32
    ek = ecdsa_keygen(curve="secp256r1")
    sig = ecdsa_sign(digest, ek["private_key"], curve="secp256r1")
    assert ecdsa_verify(
        digest, sig, ek["public_key"], curve="secp256r1"
    ) is True
    # Recipient recomputes HMAC and re-verifies.
    digest2 = hmac_sign(long_msg, mac_key, hash_alg="sha256")
    assert digest2 == digest
    assert ecdsa_verify(
        digest2, sig, ek["public_key"], curve="secp256r1"
    ) is True


def test_cross_curve_compatibility():
    """A signature produced on secp256k1 cannot be verified on
    secp256r1 with the same public-key bytes (curves differ)."""
    msg = b"cross-curve"
    ek = ecdsa_keygen(curve="secp256k1")
    sig = ecdsa_sign(msg, ek["private_key"], curve="secp256k1")
    # Same curve passes.
    assert ecdsa_verify(msg, sig, ek["public_key"], curve="secp256k1")
    # Different curve must fail (the public-key bytes parse as a
    # different point or fail to load entirely).
    assert ecdsa_verify(
        msg, sig, ek["public_key"], curve="secp256r1"
    ) is False


def test_signature_compare_schemes_runs_all_three():
    """signature_compare_schemes returns timing dict for all three
    schemes (composition of all keygen+sign+verify wrappers)."""
    result = signature_compare_schemes(b"benchmark")
    assert isinstance(result, dict)
    for scheme in ("ecdsa", "schnorr", "ed25519"):
        assert scheme in result
        assert "sign_seconds" in result[scheme]
        assert "verify_seconds" in result[scheme]
        # Sanity: timings are non-negative floats.
        assert result[scheme]["sign_seconds"] >= 0.0
        assert result[scheme]["verify_seconds"] >= 0.0
        # Sanity: verify result agrees on the freshly produced sig.
        assert result[scheme]["verified"] is True
