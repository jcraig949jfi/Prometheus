"""P-FLIP and two pre-declared variants (W2-L PLAN). base = H-PLANT hp_plants.p_flip unchanged."""
import numpy as np
import hp_plants
from prometheus.ananke import plants
A = plants.assemble
NEED_L = {"base": 16, "refresh": 22, "thin": 28}
REFRESH = [("GT", "T0", "S0", "ZERO", 0), ("GT", "T1", "ZERO", "S0", 0), ("SUB", "S0", "T0", "T1", 0),
           ("GT", "T0", "S1", "ZERO", 0), ("GT", "T1", "ZERO", "S1", 0), ("SUB", "S1", "T0", "T1", 0)]


def _base_lines():
    return [
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("CONST", "T2", 0, 0, 128), ("SUB", "T3", "ZERO", "T2", 0),
        ("GT", "PAY0", "T0", "T2", 0), ("GT", "T3", "T3", "T0", 0), ("SUB", "PAY0", "PAY0", "T3", 0),
        ("SUB", "T0", "PAY0", "S1", 0), ("MULQ", "EMIT", "T0", "PAY0", 0), ("MULQ", "T1", "S0", "S1", 0),
        ("MULQ", "T2", "PAY0", "PAY0", 0), ("SEL", "T2", "PAY0", "S1", 0), ("MOV", "S1", "T2", 0, 0),
        ("MULQ", "S0", "T1", "S1", 0), ("MULQ", "T3", "SENSE", "SENSE", 0), ("SEL", "T3", "SENSE", "S0", 0),
        ("MOV", "S0", "T3", 0, 0)]


def plant(variant, ph):
    if variant == "base":
        return hp_plants.p_flip(ph)
    lines = _base_lines()
    if variant == "thin":
        # after line 7 (EMIT on change): EMIT := EMIT if RAND(+-128) > 0 else 0 (p ~ 1/2 per awake re-emission)
        # RAND m = |A|: T1 = RAND in [-128,128] using A = T2 (=128 const at that point)
        thin = [("RAND", "T1", "T2", 0, 0), ("GT", "T1", "T1", "ZERO", 0),
                ("MULQ", "T3", "SENSE", "SENSE", 0), ("GT", "T3", "T3", "T2", 0),   # 256 iff |SENSE|=256 (a cue)
                ("MAX", "T1", "T1", "T3", 0), ("MULQ", "EMIT", "EMIT", "T1", 0)]    # sensors always emit
        lines = lines[:8] + thin + lines[8:]
    lines = REFRESH + lines      # normalise S0,S1 to sign*256 at the START of every awake tick (before m = S0*S1)
    body = A(ph, lines)
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()
