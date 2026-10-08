"""PTE-C4 common: composition and reuse ladder (72h push s7). Plants for the GATE (gated relay) rung, the HOLD rung at
FLIP-cell physics, and module extraction. Hand plants are positive controls ONLY (admission); they never enter the
module library (order s7: the library holds only independently SOLVED one-stage machinery, found by search).
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "c3"))
import c3r_common as R  # noqa: E402
C = R.C
A = C.plants.assemble


def gate_plant(ph):
    """GATED RELAY plant (needs state_dim >= 3): flood-relay the cue sign into latch S1 (P-FLIP's relay front),
    latch the context sign sensed at the actuator into S2 (the context is the only |SENSE| == 128 input; cue arrivals
    are +-256 through IN0), read out S0 = S1 * S2 (MULQ, 256-scale) = sign(cue) * sign(context)."""
    assert ph.state_dim >= 3 and ph.prog_len >= 14
    body = A(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("CONST", "T2", 0, 0, 128), ("SUB", "T3", "ZERO", "T2", 0),
        ("GT", "PAY0", "T0", "T2", 0), ("GT", "T3", "T3", "T0", 0), ("SUB", "PAY0", "PAY0", "T3", 0),   # cue sign
        ("SUB", "T0", "PAY0", "S1", 0), ("MULQ", "EMIT", "T0", "PAY0", 0),                              # emit on change
        ("MULQ", "T1", "PAY0", "PAY0", 0), ("SEL", "T1", "PAY0", "S1", 0), ("MOV", "S1", "T1", 0, 0),   # S1 := cue
        ("MULQ", "T3", "SENSE", "SENSE", 0), ("SEL", "T3", "SENSE", "S2", 0), ("MOV", "S2", "T3", 0, 0),  # S2 := ctx
        ("MULQ", "S0", "S1", "S2", 0)])                                                                  # readout
    return C.canonical(np.broadcast_to(body, (ph.rules, *body.shape)).copy())


def hold_plant(ph):
    return C.canonical(C.plants.plant("hold_latch", ph))


def relay_plant(ph):
    return C.canonical(C.plants.plant("relay_flood", ph))


def live_lines(ph, env, genome, seeds, role, device="cpu"):
    """Module extraction by line ablation: a line is LIVE iff replacing it with NOP changes the per-trial outputs on
    `seeds`. Returns (live line indices, base per-trial)."""
    g = np.asarray(genome, dtype=np.int64)
    L = g.shape[1]
    variants = [g]
    for i in range(L):
        v = g.copy(); v[0, i] = 0
        variants.append(v)
    pt, _ = C.eval_programs(ph, env, seeds, variants, device=device)
    live = [i for i in range(L) if not np.array_equal(pt[i + 1], pt[0])]
    return live, pt[0]


# ------------------------------------------------------------------ library insertion (C4 arm C)
P_LIB = 0.15
B_IS_REGISTER = {2, 3, 4, 7, 8, 9, 11, 12, 15}        # ops whose field 3 is a register operand (CONST/SHR: a shift)


def rename_state(lines, ph, perm):
    """Module INSTANTIATION with register renaming: every reference to a state register S_i (dst field mod NW,
    a field mod NR, and b field mod NR where field 3 is a register operand) is mapped to S_perm[i]; the raw byte keeps
    its high part so only the reduced index changes. Temps, I/O and shift fields are untouched."""
    D, NW, NR = ph.state_dim, ph.n_write(), ph.n_read()
    x = np.array(lines, dtype=np.int64, copy=True)
    for row in x:
        op = int(row[0]) % 16
        for f, mod in ((1, NW), (2, NR)) + (((3, NR),) if op in B_IS_REGISTER else ()):
            v = int(row[f]) % mod
            if v < D:
                row[f] = int(row[f]) - v + int(perm[v])
    return x


def insert_module(g, c, t, d, lib, libtag, ph=None):
    """Copy a uniformly chosen library module (its live lines, in order) into a uniformly chosen fully-free (all-NOP)
    destination run; if none exists, a uniform position (overwrite). If ph is given, the module is instantiated with a
    uniformly random permutation of the state registers (rename_state), so independently evolved modules can occupy
    different state registers. Inserted lines get libtag = module index + 1. Content-blind w.r.t. the target task;
    the library holds only one-stage (RELAY/HOLD) machinery."""
    c = c.copy(); t = t.copy(); d = d.copy(); libtag = libtag.copy()
    R_, L, _ = c.shape
    mi = int(g.integers(len(lib)))
    mod = np.asarray(lib[mi]["lines"], dtype=np.int64)
    perm = None
    if ph is not None:
        perm = g.permutation(ph.state_dim)
        mod = rename_state(mod, ph, perm)
    b = min(len(mod), L)
    r = int(g.integers(R_))
    nop = (c[r, :, 0] % 16) == 0
    free = [p for p in range(0, L - b + 1) if nop[p:p + b].all()]
    pos = free[int(g.integers(len(free)))] if free else int(g.integers(0, L - b + 1))
    c[r, pos:pos + b] = mod[:b]; t[r, pos:pos + b] = False; d[r, pos:pos + b] = False; libtag[r, pos:pos + b] = mi + 1
    return c, t, d, libtag, (mi, pos, bool(free), None if perm is None else perm.tolist())
