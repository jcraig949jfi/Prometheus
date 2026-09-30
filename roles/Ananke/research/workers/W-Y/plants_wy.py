"""W-Y known-answer plants (PLAN s4 + PLAN_ADDENDUM A3). Built on W-V's plant physics (MAJ env of
4781b0a1) with wimm=1 and prog_len=28 (addendum A3/A5). Never a search seed.
Plant A: readout S0 := IN0_0 + Kp[7]; Kp[7] is the running vote sum written by WIMM (cue in Kp[7] AND
         the not-yet-arrived votes in flight). Kp[22] := 1 every wake (live, cue-free) for MF-X.
Plant B: S0 := S1 + Kp[7]; the vote sum lives in S1 and Kp[7] := 1 (constant, cue-free)."""
from __future__ import annotations

import dataclasses
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W-V"))
from prometheus.ananke import plants  # noqa: E402
import plants_wv  # noqa: E402

J = 7        # the Kp[7] analogue
JX = 22      # cue-free live slot (MF-X)
PROG_LEN = 28


def physics(ph_champ):
    return dataclasses.replace(plants_wv.physics(ph_champ), wimm=1, prog_len=PROG_LEN)


def body(kind):
    cue, fresh = plants_wv._CUE, plants_wv._FRESH
    head = cue[:7] + [("ADDI", "RVAL", "ZERO", 0, 0)] + cue[7:] + fresh      # idx 7: RVAL = Kp[7]
    assert len(head) == 17 and head[J][0] == "ADDI"
    if kind == "A":
        tail = [
            ("MULQ", "T1", "RVAL", "T2", 0),     # Kp[7] if fresh wave
            ("SUB", "RVAL", "RVAL", "T1", 0),    # reset the carried sum on the first wave
            ("ADD", "S0", "IN0_0", "RVAL", 0),   # S0 = IN + Kp[7]
            ("CONST", "RPORT", 0, 0, J),
            ("WIMM", "T3", "RPORT", "S0", 0),    # Kp[7] := S0
            ("ADDI", "PAY1", "ZERO", 0, 0),      # idx 22: reads Kp[22] (cue-free)
            ("CONST", "RPORT", 0, 0, JX),
            ("CONST", "T1", 0, 0, 1),
            ("WIMM", "T3", "RPORT", "T1", 0),    # Kp[22] := 1
        ]
        assert len(head) + 5 == JX
    elif kind == "B":
        tail = [
            ("MULQ", "T1", "S1", "T2", 0),
            ("SUB", "S1", "S1", "T1", 0),        # reset tally on the first wave
            ("ADD", "S1", "S1", "IN0_0", 0),     # vote sum in S1
            ("ADD", "S0", "S1", "RVAL", 0),      # S0 = S1 + Kp[7]
            ("CONST", "RPORT", 0, 0, J),
            ("CONST", "T1", 0, 0, 1),
            ("WIMM", "T3", "RPORT", "T1", 0),    # Kp[7] := 1 (constant)
        ]
    else:
        raise KeyError(kind)
    return head + tail


def genome(ph, kind):
    return plants.assemble(ph, body(kind))[None]
