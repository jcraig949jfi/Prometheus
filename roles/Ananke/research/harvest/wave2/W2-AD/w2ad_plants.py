"""W2-AD plants. Hand-written; NEVER a search seed. Imports the other workers' plants read-only.

NEW: FLIP_BIT16 -- a 16-line, state_dim-2, decay-robust FLIP plant (answers W2-L Q2 / W2-AB NQ3).
Decay facts used (engine.py step 9, S -= S >> k, applied every tick to S only; T/EMIT/PAY are zeroed each tick):
  (a) 0 and 1 are fixed points for every k >= 1 (1 >> k = 0);
  (b) a positive value never reaches 0 (v - (v >> k) >= 1 for v >= 1); a negative value decays to 0.
So a bit stored as {0,1} is exactly decay-invariant, and "S0 > 0" is a decay-invariant 1-bit classification.
Mechanism:
  - cue latch S1 in {0,1} (1 = last cue/packet was +); every site relays: on an arrival whose sign differs from
    the latch it flips the latch and emits PAY0 = +-256 (one wave per change; the +-128 teacher is excluded by the
    strict > 128 test, so the teacher never echoes; W2-L F3);
  - answer bit A = (S0 > 0); on a latch flip A flips (within a block y_k = -y_{k-1} iff x_k != x_{k-1});
    on a teacher (|SENSE| > 0 at the actuator) A := (SENSE > 0), i.e. y_{k-1};
  - S0 := A ? +128 : -128 re-written at every awake tick (refresh), so a negative answer survives decay between
    wakes (at k = 1, -128 reaches 0 after 8 sleeping ticks).
Readout S0 at ro_k = y_{k-1} * x_{k-1} * x_k = m x_k on every scored trial (k mod block != 0) once both the
previous teacher and the current cue have been processed. It never needs m explicitly, so no MULQ of decayed values.
"""
import numpy as np
from prometheus.ananke import plants
import hp_plants                      # H-PLANT (P-FLIP, P-XOR)
import hp_variants as hv              # W2-L (refresh/thin need 22/28 lines)
import w2m_plants as wm               # W2-M INT_* family
A = plants.assemble


def _bc(ph, body):
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()


def flip_bit16(ph):
    assert ph.prog_len >= 16 and ph.state_dim >= 2
    return _bc(ph, A(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0),
        ("CONST", "T2", 0, 0, 128),
        ("CONST", "T3", 0, 7, -1),          # -128
        ("GT", "T1", "T0", "T2", 0),        # plus arrival (256/0); teacher +128 excluded
        ("GT", "T3", "T3", "T0", 0),        # minus arrival
        ("SUB", "PAY0", "T1", "T3", 0),     # +-256 or 0
        ("MOV", "EMIT", "S1", 0, 0),
        ("SEL", "EMIT", "T3", "T1", 0),     # latch=1 ? minus : plus  -> 256 iff arrival differs from latch
        ("SHR", "T2", "EMIT", 8, 0),        # flip bit 0/1
        ("XOR", "S1", "S1", "T2", 0),       # latch := new sign
        ("GT", "T0", "S0", "ZERO", 0),      # answer bit A (256/0)
        ("XOR", "T0", "T0", "EMIT", 0),     # flip A on a cue change
        ("MULQ", "T1", "SENSE", "SENSE", 0),  # sense present (teacher at actuator)
        ("GT", "T3", "SENSE", "ZERO", 0),
        ("SEL", "T1", "T3", "T0", 0),       # teacher ? (SENSE>0) : A
        ("ADDI", "S0", "T1", 0, -128),      # +128 / -128
    ]))


def relay_bit(ph):
    """RELAY plant with the same {0,1} decay-invariant latch (12 lines): S0 := latch ? +128 : -128."""
    return _bc(ph, A(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0),
        ("CONST", "T2", 0, 0, 128),
        ("CONST", "T3", 0, 7, -1),
        ("GT", "T1", "T0", "T2", 0),
        ("GT", "T3", "T3", "T0", 0),
        ("SUB", "PAY0", "T1", "T3", 0),
        ("MOV", "EMIT", "S1", 0, 0),
        ("SEL", "EMIT", "T3", "T1", 0),
        ("SHR", "T2", "EMIT", 8, 0),
        ("XOR", "S1", "S1", "T2", 0),
        ("GT", "T0", "S1", "ZERO", 0),
        ("ADDI", "S0", "T0", 0, -128),
    ]))


def relay_refresh(ph):
    """P-2 relay_refresh, copied verbatim from P-1/decay_plant.py (that module runs on import)."""
    return _bc(ph, plants.assemble(ph, [
        ("GT", "T2", "S0", "ZERO", 0), ("GT", "T3", "ZERO", "S0", 0), ("SUB", "S0", "T2", "T3", 0),
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("GT", "T2", "T0", "ZERO", 0), ("GT", "T3", "ZERO", "T0", 0),
        ("SUB", "T1", "T2", "T3", 0), ("MULQ", "T2", "T1", "T1", 0), ("XOR", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T3", 0), ("MULQ", "EMIT", "T2", "T3", 0), ("MOV", "PAY0", "T1", 0, 0),
        ("SUB", "T3", "T1", "S0", 0), ("MULQ", "T3", "T3", "T2", 0), ("ADD", "S0", "S0", "T3", 0)]))


def relay_latch(ph):
    import relay_latch_def
    return relay_latch_def.relay_latch(ph)


def nlines(g):
    return int((np.asarray(g)[0, :, 0] % 16 != 0).sum())


DESIGNS = {
    "RELAY": {"relay_flood": lambda ph: plants.plant("relay_flood", ph), "relay_refresh": relay_refresh,
              "relay_bit": relay_bit},
    "FLIP": {"P_FLIP": lambda ph: hp_plants.p_flip(ph), "FLIP_BIT16": flip_bit16},
    "MAJ": {"INT_1": lambda ph: wm.int_1(ph), "INT_2": lambda ph: wm.int_L(ph, 2), "INT_CO": wm.int_co},
}
