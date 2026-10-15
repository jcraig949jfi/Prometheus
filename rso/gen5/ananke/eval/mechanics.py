"""Rung-4 causal-attribution mechanics on PTE genomes (directive 2026-10-15 s4; C-019-T040 item 3).

A MODULE is a set of line indices of a genome (rule 0 broadcast; the C4 genomes have rules = 1). Interventions:

  lines_nop(g, lines)              ABLATE: the module's lines become NOP (all fields 0), as the owner's live_lines /
                                   LIB_NOP do (c4_common.py:52-56, assay_c4.py:5 @ f58362c5e).
  substitute(g, lines, rows)       SUBSTITUTE: the module's lines replaced, in program order, by a size-matched module.
  lesion_input(rows, ph, reg)      a size-matched INCOMPATIBLE module built from the module itself: every register
                                   read of `reg` becomes a read of ZERO (same ops, wrong input).
  transplant(rows, ph, start, background=None)
                                   TRANSPLANT: the module's rows into a fresh genome (NOP, or a given background) at
                                   `start`; optionally after rename_state (the owner's instantiation, c4_common.py:64-77).
  use_disabled(g, lines, ph)       DISABLE USE WITHOUT DELETING THE BYTES. Defined for PTE (no call instruction exists;
                                   every line of the running rule executes, so "invocation" is the module's effect on
                                   the rest of the program through the registers it writes). Every module line keeps
                                   its op, a, b and imm bytes and its position, keeps executing (it is still non-NOP,
                                   still reads its inputs, still draws its RAND stream), but its destination is renamed
                                   to the CHANNEL register O.chan, which is DEAD when channels == 1 (O.chan mod C = 0
                                   for every value; DESIGN.md s6 step 7). The rename keeps the raw byte's high part
                                   exactly as rename_state does, so by the owner's own identity convention (register
                                   renaming preserves a module: library-tagged lines are renamed at instantiation) the
                                   module is still present. Refused (UnsupportedIntervention) when channels != 1 or when
                                   any line outside the module reads O.chan (then the sink is not dead).
  reg_zero(i)                      REGISTER-ZERO: after_tick hook forcing S_i := 0 after every tick, after the readout
                                   is recorded (engine lens.run hook timing; assay_c4.py:42-45).
  zero_comm (evaluate kwarg)       ZERO-COMMUNICATION: no packet copy is ever delivered.
  context_off_after_block0, context_off_all, teacher_off   sense-schedule edits (assay_candidates.py:68-74).
"""
from __future__ import annotations

import numpy as np

from .evaluate import register_layout

B_IS_REGISTER = {2, 3, 4, 7, 8, 9, 11, 12, 15}          # ops whose b field is a register (c4_common.py:61)
A_IS_REGISTER = set(range(1, 16)) - {6}                  # every op except NOP and CONST reads its a field
SEL = 8                                                   # reads reg[dst] as its condition


class UnsupportedIntervention(ValueError):
    pass


def _g(g) -> np.ndarray:
    g = np.array(g, dtype=np.int64, copy=True)
    return g[None] if g.ndim == 2 else g


def lines_nop(g, lines) -> np.ndarray:
    x = _g(g)
    x[:, list(lines)] = 0
    return x


def substitute(g, lines, rows) -> np.ndarray:
    rows = np.asarray(rows, dtype=np.int64).reshape(-1, 5)
    if len(rows) != len(lines):
        raise ValueError(f"substitute must be size-matched: {len(rows)} rows for {len(lines)} lines")
    x = _g(g)
    x[:, sorted(lines)] = rows
    return x


def rename_state(rows, ph: dict, perm) -> np.ndarray:
    """Owner's instantiation (c4_common.rename_state): S_i -> S_perm[i] in dst (mod NW), a (mod NR) and b (mod NR,
    register operands only); the raw byte keeps its high part."""
    L = register_layout(ph)
    x = np.array(rows, dtype=np.int64, copy=True).reshape(-1, 5)
    for row in x:
        op = int(row[0]) % 16
        for f, mod in ((1, L["NW"]), (2, L["NR"])) + (((3, L["NR"]),) if op in B_IS_REGISTER else ()):
            v = int(row[f]) % mod
            if v < L["D"]:
                row[f] = int(row[f]) - v + int(perm[v])
    return x


def lesion_input(rows, ph: dict, reg: int) -> np.ndarray:
    L = register_layout(ph)
    x = np.array(rows, dtype=np.int64, copy=True).reshape(-1, 5)
    for row in x:
        op = int(row[0]) % 16
        if op in A_IS_REGISTER and int(row[2]) % L["NR"] == reg:
            row[2] = int(row[2]) - reg + L["ZERO"]
        if op in B_IS_REGISTER and int(row[3]) % L["NR"] == reg:
            row[3] = int(row[3]) - reg + L["ZERO"]
    return x


def transplant(rows, ph: dict, start: int = 0, background=None) -> np.ndarray:
    rows = np.asarray(rows, dtype=np.int64).reshape(-1, 5)
    Lp = int(ph["prog_len"])
    if start < 0 or start + len(rows) > Lp:
        raise ValueError(f"module of {len(rows)} lines does not fit at {start} in {Lp}")
    g = np.zeros((int(ph["rules"]), Lp, 5), dtype=np.int64) if background is None else _g(background)
    g[:, start:start + len(rows)] = rows
    return g


def _reads(row, L) -> set:
    op = int(row[0]) % 16
    r = set()
    if op in A_IS_REGISTER:
        r.add(int(row[2]) % L["NR"])
    if op in B_IS_REGISTER:
        r.add(int(row[3]) % L["NR"])
    if op == SEL:
        r.add(int(row[1]) % L["NW"])
    return r


def use_disabled(g, lines, ph: dict):
    L = register_layout(ph)
    if int(ph["channels"]) != 1:
        raise UnsupportedIntervention("O.chan is a dead sink only when channels == 1")
    x = _g(g)
    lines = sorted(set(lines))
    outside = [i for i in range(x.shape[1]) if i not in lines]
    for r in range(x.shape[0]):
        for i in outside:
            if int(x[r, i, 0]) % 16 and L["CHAN"] in _reads(x[r, i], L):
                raise UnsupportedIntervention(f"line {i} outside the module reads O.chan: the sink is not dead")
    changed = 0
    for r in range(x.shape[0]):
        for i in lines:
            v = int(x[r, i, 1]) % L["NW"]
            if v != L["CHAN"]:
                changed += 1
            x[r, i, 1] = int(x[r, i, 1]) - v + L["CHAN"]
    nonnop = int(sum(int(x[0, i, 0]) % 16 != 0 for i in lines))
    return x, {"bytes_changed": changed // x.shape[0], "lines": lines, "lines_executed_nonnop": nonnop,
               "sink": "O.chan", "sink_index": L["CHAN"]}


def reg_zero(i: int):
    def hook(t, b, S_b):
        for site in S_b:
            site[i] = 0
    return hook


def context_off_after_block0(env):
    Pd = env.period()

    def edit(sv, ep):
        sv[env.block * Pd:, :, 1] = 0
    return edit


def context_off_all(sv, ep):
    sv[:, :, 1] = 0


def teacher_off(env):
    Pd = env.delta + 1 + env.cue_len + env.iti

    def edit(sv, ep):
        sv[Pd:, :, 1] = 0
    return edit
