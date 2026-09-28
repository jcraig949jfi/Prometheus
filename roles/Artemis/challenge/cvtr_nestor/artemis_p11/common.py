"""Shim for certs.py (Artemis P-11 challenge @2af325f7b): supplies only the two helpers certs.py imports.
shabytes is copied verbatim from roles/Artemis/challenge/p11/common.py; fid is p11.fidelity (same as there)."""
from __future__ import annotations

import hashlib
import json


def shabytes(*parts, n):
    out = bytearray()
    c = 0
    key = json.dumps(parts, sort_keys=True, default=str).encode()
    while len(out) < n:
        out += hashlib.sha256(key + c.to_bytes(4, "big")).digest()
        c += 1
    return bytes(out[:n])


def fid(a, b):
    import p11
    return p11.fidelity(a, b)
