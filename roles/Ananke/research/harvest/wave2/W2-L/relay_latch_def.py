"""RELAY_LATCH definition (shared by t5 and t2_mech)."""
import numpy as np
from prometheus.ananke import plants
A = plants.assemble
def relay_latch(ph):
    body = A(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("CONST", "T2", 0, 0, 128), ("SUB", "T3", "ZERO", "T2", 0),
        ("GT", "PAY0", "T0", "T2", 0), ("GT", "T3", "T3", "T0", 0), ("SUB", "PAY0", "PAY0", "T3", 0),   # v = cue sign*256 (teacher excluded)
        ("SUB", "T0", "PAY0", "S0", 0), ("MULQ", "EMIT", "T0", "PAY0", 0),                              # emit iff v != 0 and v != S0
        ("MULQ", "T1", "PAY0", "PAY0", 0), ("SEL", "T1", "PAY0", "S0", 0), ("MOV", "S0", "T1", 0, 0),   # S0 := v where v != 0
        ("MULQ", "T3", "SENSE", "SENSE", 0), ("SEL", "T3", "SENSE", "S0", 0), ("MOV", "S0", "T3", 0, 0)])  # S0 := SENSE (teacher latch)
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()
