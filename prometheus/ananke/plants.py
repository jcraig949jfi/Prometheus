"""Hand-written genomes: POSITIVE CONTROLS and CHEATS only.

These exist to prove (a) each family is reachable in PTE-SUB-1 (a
necessity preflight; Ensorain R2) and (b) the detectors fire on real
signal. They are NEVER inserted into a search population: the search
must not be steered toward our designs (mission s17).

A tiny assembler names registers so the plants are readable.
"""
from __future__ import annotations

import numpy as np

from .physics import Physics

OPS = {"NOP": 0, "MOV": 1, "ADD": 2, "SUB": 3, "MULQ": 4, "ADDI": 5, "CONST": 6, "GT": 7,
       "SEL": 8, "MAX": 9, "SHR": 10, "XOR": 11, "MOD": 12, "RAND": 13, "SETRULE": 14, "WIMM": 15}


def regmap(ph: Physics) -> dict:
    D, P, C = ph.state_dim, ph.payload_width, ph.channels
    NW = ph.n_write()
    m = {f"S{i}": i for i in range(D)}
    m.update({f"T{i}": D + i for i in range(4)})
    m.update({"EMIT": D + 4, "CHAN": D + 5, "RPORT": D + 6, "RVAL": D + 7})
    m.update({f"PAY{p}": D + 8 + p for p in range(P)})
    for c in range(C):
        for p in range(P):
            m[f"IN{c}_{p}"] = NW + c * P + p
        m[f"CNT{c}"] = NW + C * P + c
    base = NW + C * P + C
    m.update({"SENSE": base, "ENERGY": base + 1, "ZERO": base + 2})
    return m


def assemble(ph: Physics, lines, L: int | None = None) -> np.ndarray:
    """lines: (op, dst, a, b, imm) with register names or ints. -> [L,5]."""
    rm = regmap(ph)
    L = L or ph.prog_len
    assert len(lines) <= L, (len(lines), L)
    out = np.zeros((L, 5), dtype=np.int64)
    for i, (op, d, a, b, imm) in enumerate(lines):
        r = lambda x: rm[x] if isinstance(x, str) else int(x)
        out[i] = (OPS[op], r(d), r(a), r(b), imm)
    return out


def relay_flood(ph: Physics) -> np.ndarray:
    """A site adopts sign(SENSE + IN0_0)*256 into S0 when non-zero and
    re-emits only when its value changes: one outward wave per change."""
    return assemble(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0),
        ("GT", "T2", "T0", "ZERO", 0),
        ("GT", "T3", "ZERO", "T0", 0),
        ("SUB", "T1", "T2", "T3", 0),        # T1 = sign*256 or 0
        ("MULQ", "T2", "T1", "T1", 0),       # T2 = 256 if T1 != 0
        ("XOR", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T3", 0),       # >0 iff T1 != S0
        ("MULQ", "EMIT", "T2", "T3", 0),
        ("MOV", "PAY0", "T1", 0, 0),
        ("SUB", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T2", 0),
        ("ADD", "S0", "S0", "T3", 0),        # S0 := T1 where T1 != 0
    ])


def hold_latch(ph: Physics) -> np.ndarray:
    """S0 := sign(SENSE)*256 when |SENSE| > 128, else unchanged. Local
    memory only (no packets): solves HOLD without decay."""
    return assemble(ph, [
        ("CONST", "T0", 0, 0, 1),            # T0 = 1 << 7 = 128  (bf=b field=7 below)
        ("GT", "T2", "SENSE", "T0", 0),
        ("SUB", "T1", "ZERO", "T0", 0),      # -128
        ("GT", "T3", "T1", "SENSE", 0),
        ("SUB", "T1", "T2", "T3", 0),        # sign*256 or 0
        ("MULQ", "T2", "T1", "T1", 0),
        ("SUB", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T2", 0),
        ("ADD", "S0", "S0", "T3", 0),
    ])


def fix_const_shift(g: np.ndarray, i: int, shift: int) -> np.ndarray:
    g = g.copy()
    g[i, 3] = shift
    return g


def plant(name: str, ph: Physics) -> np.ndarray:
    """-> genome [1(G) ..., L, 5] broadcast to ph.rules variants."""
    if name == "relay_flood":
        body = relay_flood(ph)
    elif name == "hold_latch":
        body = fix_const_shift(hold_latch(ph), 0, 7)
    elif name == "null":
        body = np.zeros((ph.prog_len, 5), dtype=np.int64)
    elif name == "sense_copy":
        # CHEAT-class local policy: S0 := SENSE (scores only if the target
        # is present at the actuator itself; used with the leak env)
        body = assemble(ph, [("MOV", "S0", "SENSE", 0, 0)])
    else:
        raise KeyError(name)
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()
