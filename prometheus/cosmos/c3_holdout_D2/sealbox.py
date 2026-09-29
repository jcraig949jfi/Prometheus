"""Crypto + commitment primitives for holdout D2. No secret lives in this file; no family import.

Cipher: AES-256-GCM from the `cryptography` package (authenticated; a flipped ciphertext bit or a wrong
key raises InvalidTag). 96-bit random IV (public, in the manifest). AAD = AAD_PREFIX + family source
sha256 (binds the ciphertext to the exact family code it was drawn for).

Commitment (salted, to the plaintext): sha256(salt_bytes || plaintext_bytes), salt = 32 random bytes,
kept secret until reveal. Separate public hash of the ciphertext: sha256(ciphertext_bytes).
The plaintext bytes are the canonical JSON of the hidden set (sort_keys, separators (",", ":"), UTF-8).
"""
from __future__ import annotations

import hashlib
import json
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CIPHER_NAME = "AES-256-GCM (cryptography.hazmat.primitives.ciphers.aead.AESGCM), 96-bit IV, 128-bit tag"
AAD_PREFIX = b"prometheus/cosmos/c3_holdout_D2|v1|family_src_sha256="
KEY_BYTES = 32
SALT_BYTES = 32
IV_BYTES = 12


def canon_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def src_sha_lf(path) -> str:
    """sha256 of a source file with CRLF normalised to LF (holdout D convention)."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def new_key() -> bytes:
    return secrets.token_bytes(KEY_BYTES)


def new_salt() -> bytes:
    return secrets.token_bytes(SALT_BYTES)


def new_iv() -> bytes:
    return secrets.token_bytes(IV_BYTES)


def aad(family_src_sha256: str) -> bytes:
    return AAD_PREFIX + family_src_sha256.encode("ascii")


def commitment(salt: bytes, plaintext: bytes) -> str:
    if len(salt) != SALT_BYTES:
        raise ValueError("salt must be %d bytes" % SALT_BYTES)
    return sha256_hex(salt + plaintext)


def encrypt(key: bytes, iv: bytes, plaintext: bytes, family_src_sha256: str) -> bytes:
    if len(key) != KEY_BYTES or len(iv) != IV_BYTES:
        raise ValueError("bad key/iv length")
    return AESGCM(key).encrypt(iv, plaintext, aad(family_src_sha256))


def decrypt(key: bytes, iv: bytes, ciphertext: bytes, family_src_sha256: str) -> bytes:
    """Raises cryptography.exceptions.InvalidTag on any tampering / wrong key / wrong AAD."""
    if len(key) != KEY_BYTES or len(iv) != IV_BYTES:
        raise ValueError("bad key/iv length")
    return AESGCM(key).decrypt(iv, ciphertext, aad(family_src_sha256))


def read_hex_file(path, n_bytes: int) -> bytes:
    with open(path, "r", encoding="ascii") as f:
        b = bytes.fromhex(f.read().strip())
    if len(b) != n_bytes:
        raise ValueError("expected %d bytes in hex file" % n_bytes)
    return b


def manifest_spec_id(manifest: dict) -> str:
    """spec_id = sha256 of the canonical manifest WITHOUT the spec_id field (public data only)."""
    return sha256_hex(canon_bytes({k: v for k, v in manifest.items() if k != "spec_id"}))
