"""W-P known-answer plants: N produced by a KNOWN joint dependence.

Both extend plants.echo_hold (lines copied; the bit rides out and back in flight and
returns at the HOLD readout tick) with a site latch S1 := cue sign (at the cue).
  max_plant  readout S0 := MAX(arrival sign, S1)             -> JOINT-2(S, Msum), d = +
  mux_plant  gate Kp[J] := cue sign (WIMM at the cue);
             readout S0 := (Kp[J] > 0 ? S1 : arrival sign)   -> GATED(Kp; S, Msum), d = +
Physics: plants.c1b_echo_physics() (+ wimm=1, larger prog_len for mux). Genomes only;
physics untouched.
"""
from __future__ import annotations

import dataclasses

import numpy as np

from prometheus.ananke import plants

ECHO_HEAD = [
    ("CONST", "T0", 0, 7, 1),            # 128
    ("GT", "T1", "SENSE", "T0", 0),
    ("SUB", "T2", "ZERO", "T0", 0),
    ("GT", "T2", "T2", "SENSE", 0),
    ("SUB", "T1", "T1", "T2", 0),        # cue sign*256 or 0
]
LATCH = [
    ("MULQ", "T2", "T1", "T1", 0),       # 256 iff cue
    ("SUB", "T3", "T1", "S1", 0),
    ("MULQ", "T3", "T3", "T2", 0),
    ("ADD", "S1", "S1", "T3", 0),        # S1 := cue sign*256 on cue ticks
]
ECHO_BODY = [
    ("CONST", "T3", 0, 0, 3),
    ("SUB", "T2", "IN0_1", "T3", 0),     # 0 iff marker sum == 3
    ("GT", "T0", "T2", "ZERO", 0),
    ("GT", "T3", "ZERO", "T2", 0),
    ("ADD", "T0", "T0", "T3", 0),        # 256 iff marker != 3
    ("CONST", "T3", 0, 7, 2),            # 256
    ("SUB", "T3", "T3", "T0", 0),        # 256 iff relay
    ("MULQ", "EMIT", "T1", "T1", 0),     # 256 iff cue
    ("MOV", "PAY0", "EMIT", 0, 0),
    ("SEL", "PAY0", "T1", "IN0_0", 0),   # cue ? cue : received payload
    ("MOV", "PAY1", "EMIT", 0, 0),
    ("CONST", "CHAN", 0, 0, 3),
    ("CONST", "RPORT", 0, 0, 1),
    ("SEL", "PAY1", "CHAN", "RPORT", 0),  # cue ? 3 : 1
    ("ADD", "EMIT", "EMIT", "T3", 0),
    ("GT", "T0", "IN0_0", "ZERO", 0),
    ("GT", "T2", "ZERO", "IN0_0", 0),
    ("SUB", "T0", "T0", "T2", 0),        # arrival sign*256 or 0
]


def physics_max():
    return plants.c1b_echo_physics()


def max_plant(ph):
    lines = ECHO_HEAD + LATCH + ECHO_BODY + [("MAX", "S0", "T0", "S1", 0)]
    return plants.assemble(ph, lines)[None]


def physics_mux():
    return dataclasses.replace(plants.c1b_echo_physics(), prog_len=40, wimm=1)


def mux_plant(ph):
    head = ECHO_HEAD + LATCH
    # gate write: WIMM Kp[cue ? J : D0] := T1 (T1 = 0 on non-cue ticks -> harmless)
    gate_w = [
        ("MULQ", "T2", "T1", "T1", 0),       # 256 iff cue
        ("CONST", "T3", 0, 0, None),         # J (filled below)
        ("CONST", "RPORT", 0, 0, None),      # D0
        ("SEL", "T2", "T3", "RPORT", 0),     # cue ? J : D0
        ("WIMM", "CHAN", "T2", "T1", 0),     # Kp[T2 % L] := T1
    ]
    tail = [
        ("MOV", "RVAL", "T0", 0, 0),         # arrival sign
        ("ADDI", "T0", "ZERO", 0, 0),        # line J: T0 := 0 + Kp[J]
        ("SEL", "T0", "S1", "RVAL", 0),      # gate > 0 ? S1 : arrival
        ("MOV", "S0", "T0", 0, 0),
    ]
    lines = head + gate_w + ECHO_BODY + tail
    J = len(head + gate_w + ECHO_BODY) + 1
    D0 = len(lines) - 1                     # the final MOV (does not use the immediate)
    gate_w[1] = ("CONST", "T3", 0, 0, J)
    gate_w[2] = ("CONST", "RPORT", 0, 0, D0)
    lines = head + gate_w + ECHO_BODY + tail
    assert lines[J][0] == "ADDI" and lines[D0][0] == "MOV"
    return plants.assemble(ph, lines)[None]


def latch_fixture():
    ph = dataclasses.replace(plants.c1b_echo_physics(), prog_len=12, payload_width=1)
    return ph, plants.plant("hold_latch", ph)


def echo_fixture():
    ph = plants.c1b_echo_physics()
    return ph, plants.echo_hold(ph)[None]
