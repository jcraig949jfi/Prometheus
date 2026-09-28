"""Loading of the archived NPE modules (read-only scratch copies) and small shared helpers."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys

SCR = pathlib.Path("/tmp/claude-1000/-home-jcraig-Prometheus/78a7bd7b-da69-4758-859e-8a39e0df5734/scratchpad/p11")
VER = SCR / "d764/roles/Nestor/campaigns/z80atlas-verify-2026-09-22"
SUB = SCR / "d764/roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/substrate"
REASSAY = SCR / "d764/roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/P11_REASSAY.jsonl"
ORIG = SCR / "aa58/roles/Nestor/campaigns/z80atlas-2026-09-19"
OUT = pathlib.Path(__file__).resolve().parent / "results"

if str(VER) not in sys.path:
    sys.path.insert(0, str(VER))     # p11.py does `from constants import C`; world.py imports z8 etc.


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


import p11            # noqa: E402  (verify copy @d7641744d)
import constants      # noqa: E402

Z8SUB = _load("z8_substrate", SUB / "z8.py")      # the VM S1-C actually ran
Z8VER = _load("z8_verify", VER / "z8.py")
Z8ORIG = _load("z8_orig", ORIG / "z8.py")          # aa5833488, no provenance support
C = constants.C

REP_LEN = {"Z8_64": 64, "Z8_32": 32, "Z8_SHARED": 96, "Z8_SEPARATED": 96, "Z8_SLOTTED": 64}
MUT_RATE = {"LOW": 0.002, "MID": 0.01, "HIGH": 0.04}
SLICE = {"S": 220, "M": 300, "L": 360}
FRESH = (None, 0, 0)


def pow2(n):
    k = 1
    while k < n:
        k <<= 1
    return k


def mask_for(cell):
    m = 0
    if cell["reproduction"] in ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE"):
        m |= 0x01
    if cell["reproduction"] == "ENDOGENOUS_PARTIAL":
        m |= 0x10
    if cell["self_location"] == "PRIMITIVE":
        m |= 0x02
    if cell["self_location"] == "PC_RELATIVE":
        m |= 0x04
    m |= 0x08
    if cell["copy_primitive"] == "BLOCK":
        m |= 0x20
    return m


def shabytes(*parts, n):
    out = bytearray()
    c = 0
    key = json.dumps(parts, sort_keys=True, default=str).encode()
    while len(out) < n:
        out += hashlib.sha256(key + c.to_bytes(4, "big")).digest()
        c += 1
    return bytes(out[:n])


def fid(a, b):
    return p11.fidelity(a, b)


def file_hashes():
    fs = [VER / f for f in ("p11.py", "constants.py", "z8.py", "world.py", "grammar.py", "tasks.py", "anticheat.py")]
    fs += [SUB / "z8.py", REASSAY, ORIG / "z8.py", ORIG / "grammar.py"]
    return {str(f.relative_to(SCR)): hashlib.sha256(f.read_bytes()).hexdigest() for f in fs}
