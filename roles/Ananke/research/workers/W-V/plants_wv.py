"""W-V known-answer plants (PLAN s4): 5-sensor MAJORITY (PMAJ) and 1-of-5 DICTATOR (PDICT) readouts in
the MAJ env of 4781b0a1, built with prometheus.ananke.plants.assemble. Never search seeds."""
from __future__ import annotations

import dataclasses

from prometheus.ananke import plants

_CUE = [
    ("CONST", "T0", 0, 7, 1),            # 128
    ("GT", "T1", "SENSE", "T0", 0),
    ("SUB", "T2", "ZERO", "T0", 0),
    ("GT", "T2", "T2", "SENSE", 0),
    ("SUB", "T1", "T1", "T2", 0),        # T1 = cue sign*256 or 0
    ("MULQ", "T3", "T1", "T1", 0),       # T3 = 256 iff cue
    ("MOV", "PAY0", "T1", 0, 0),
    ("MOV", "EMIT", "T3", 0, 0),         # every sensor emits its vote once (one wake in the cue window)
]
_FRESH = [
    ("GT", "T0", "CNT0", "ZERO", 0),     # 256 iff arrivals this wake
    ("CONST", "T2", 0, 7, 5),            # 640
    ("GT", "T2", "S2", "T2", 0),         # 256 iff >= 3 silent wakes before
    ("MULQ", "T2", "T2", "T0", 0),       # fresh = first arrival wave of a trial
    ("CONST", "T3", 0, 7, 2),            # 256
    ("ADD", "S2", "S2", "T3", 0),
    ("SUB", "T3", "T3", "T0", 0),
    ("MULQ", "S2", "S2", "T3", 0),       # S2 := silent-wake counter (x256), 0 on arrivals
]
_MAJ = [
    ("MULQ", "T1", "S1", "T2", 0),
    ("SUB", "S1", "S1", "T1", 0),        # reset the tally on the first wave
    ("ADD", "S1", "S1", "IN0_0", 0),     # add every arriving vote
    ("MOV", "S0", "S1", 0, 0),           # readout = sign of the vote sum
]
_DICT = [
    ("GT", "T1", "IN0_0", "ZERO", 0),
    ("GT", "T3", "ZERO", "IN0_0", 0),
    ("SUB", "T1", "T1", "T3", 0),        # sign of this wave * 256
    ("SUB", "T1", "T1", "S0", 0),
    ("MULQ", "T1", "T1", "T2", 0),
    ("ADD", "S0", "S0", "T1", 0),        # S0 := sign(first wave) only; later waves ignored
]


def physics(ph_champ):
    return dataclasses.replace(ph_champ, dest_mode="all", loss=0.0, cap=0, lat_base=5, lat_hop=2,
                               lat_jitter=0, state_dim=3, prog_len=24, plastic_route=0, wimm=0,
                               setrule=0, rules=1, mut_site=0.0, dup=0.0, noise=0, decay_shift=0)


def genome(ph, kind):
    body = _CUE + _FRESH + (_MAJ if kind == "PMAJ" else _DICT)
    return plants.assemble(ph, body)[None]
