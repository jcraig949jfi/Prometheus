"""W2-Z economy-feasible plants (hand-written; never search seeds)."""
import numpy as np
from prometheus.ananke import plants
A = plants.assemble


def relay_att(s=1):
    """Stateless attenuating relay: forward (SENSE+IN)>>s; emit iff |payload|>=16 (MULQ>>8). 3 lines, m=0."""
    return [("ADD", "T0", "SENSE", "IN0_0", 0), ("SHR", "PAY0", "T0", s, 0), ("MULQ", "EMIT", "PAY0", "PAY0", 0)]


DISPATCH = [("SHR", "T1", "SENSE", 7, 0), ("SETRULE", 0, "T1", 0, 0)]  # teacher (+-128)>>7 = +-1 -> odd rule


def sign256(src, dst, t0="T0", t1="T1"):
    return [("GT", t0, src, "ZERO", 0), ("GT", t1, "ZERO", src, 0), ("SUB", dst, t0, t1, 0)]


def flip_actuator():
    """Actuator rule (never emits). S2 = last cue sign (refreshed), S1 = m*256+1 (odd => stays in odd rule),
    S0 = MULQ(S2, S1) = answer. Bootstrap: S1 kept odd while a teacher is present even if x unknown."""
    L = []
    # S2 := sign256(2*sign(IN0_0) + S2)
    L += sign256("IN0_0", "T2")
    L += [("ADD", "T2", "T2", "T2", 0), ("ADD", "T2", "T2", "S2", 0)]
    L += sign256("T2", "S2")
    # Y := sign256(SENSE) -> PAY1 (scratch; this rule never emits)
    L += sign256("SENSE", "RPORT")
    L += [("MULQ", "T2", "RPORT", "S2", 0),          # m_new*256 (teacher) or 0
          ("ADD", "T2", "T2", "T2", 0), ("ADD", "T2", "T2", "S1", 0)]
    L += sign256("T2", "T2")                       # +-256 or 0
    L += [("MULQ", "T3", "T2", "T2", 0),            # 256 iff known m
          ("SHR", "T3", "T3", 2, 0),                # 64 iff known m
          ("MULQ", "T0", "SENSE", "SENSE", 0),      # 64 teacher / 256 cue / 0
          ("MAX", "T3", "T3", "T0", 0),
          ("SHR", "T3", "T3", 6, 0),                # 1 (m known or teacher) / 4 (cue: sensor, leave) / 0
          ("ADD", "S1", "T2", "T3", 0),             # +257 / -255 / 1 / 0
          ("SETRULE", 0, "S1", 0, 0),
          ("MULQ", "S0", "S2", "S1", 0)]
    return L


def two_rule(ph, relay, act, L=None):
    """rules: even index -> relay body, odd -> actuator body."""
    L = L or ph.prog_len
    rb = A(ph, relay, L); ab = A(ph, act, L)
    g = np.stack([rb if (i % 2 == 0) else ab for i in range(ph.rules)])
    return g


def n_nonnop(body):
    return int((np.asarray(body)[..., 0] % 16 != 0).sum())


def flip_actuator_v2(leak=2):
    """v2 actuator rule (never emits): S2 = leaky signed sum of arrivals (x evidence, robust to echoes),
    X = sign256(S2) in CHAN (scratch: this rule never emits), Y = sign256(SENSE) in RPORT (RVAL stays 0),
    S1 = m*256 +/- 1 (odd => stays in an odd rule). Keep-alive if m known, teacher present, or E < 100
    (a site dispatched by the teacher has just paid for the teacher echo; a fresh initial-rule site has E = e_max),
    never on a cue (sensors leave)."""
    L = [("SHR", "T0", "S2", leak, 0), ("SUB", "S2", "S2", "T0", 0), ("ADD", "S2", "S2", "IN0_0", 0)]
    L += sign256("S2", "CHAN")
    L += sign256("SENSE", "RPORT")
    L += [("MULQ", "T2", "RPORT", "CHAN", 0), ("ADD", "T2", "T2", "T2", 0), ("ADD", "T2", "T2", "S1", 0)]
    L += sign256("T2", "T2")
    L += [("MULQ", "T3", "T2", "T2", 0), ("SHR", "T3", "T3", 2, 0),            # 64 iff m known
          ("MULQ", "T0", "SENSE", "SENSE", 0), ("MAX", "T3", "T3", "T0", 0),   # 64 teacher / 256 cue
          ("CONST", "T0", 0, 0, 100), ("GT", "T0", "T0", "ENERGY", 0),         # 256 iff E < 100
          ("SHR", "T0", "T0", 2, 0), ("MAX", "T3", "T3", "T0", 0),
          ("SHR", "T3", "T3", 6, 0),                                            # 1 keep / 4 cue / 0 leave
          ("ADD", "S1", "T2", "T3", 0),
          ("SETRULE", 0, "S1", 0, 0),
          ("MULQ", "S0", "CHAN", "S1", 0)]
    return L


def relay_dedup():
    """relay_flood semantics (re-emit only on a change of the stored sign), 9 lines, m=1 (S1 = last relayed sign)."""
    return [("ADD", "T0", "SENSE", "IN0_0", 0)] + sign256("T0", "PAY0", "T2", "T3") + [
        ("SUB", "T1", "PAY0", "S1", 0), ("MULQ", "EMIT", "PAY0", "T1", 0),
        ("ADD", "T2", "T2", "T3", 0), ("MULQ", "T1", "T1", "T2", 0), ("ADD", "S1", "S1", "T1", 0)]


def flip_actuator_v3():
    """v3 = v1 x-memory (S2 := sign256(2*sign(IN0_0) + S2): no leak, persists across no-wave trials) + v2 keep-alive."""
    L = sign256("IN0_0", "T2") + [("ADD", "T2", "T2", "T2", 0), ("ADD", "T2", "T2", "S2", 0)] + sign256("T2", "S2")
    L += sign256("SENSE", "RPORT")
    L += [("MULQ", "T2", "RPORT", "S2", 0), ("ADD", "T2", "T2", "T2", 0), ("ADD", "T2", "T2", "S1", 0)]
    L += sign256("T2", "T2")
    L += [("MULQ", "T3", "T2", "T2", 0), ("SHR", "T3", "T3", 2, 0),
          ("MULQ", "T0", "SENSE", "SENSE", 0), ("MAX", "T3", "T3", "T0", 0),
          ("CONST", "T0", 0, 0, 100), ("GT", "T0", "T0", "ENERGY", 0),
          ("SHR", "T0", "T0", 2, 0), ("MAX", "T3", "T3", "T0", 0),
          ("SHR", "T3", "T3", 6, 0),
          ("ADD", "S1", "T2", "T3", 0),
          ("SETRULE", 0, "S1", 0, 0),
          ("MULQ", "S0", "S2", "S1", 0)]
    return L
