"""H-PLANT hand-written plants (PLAN s2). No search."""
import numpy as np

from prometheus.ananke import plants
from prometheus.ananke.physics import Physics

A = plants.assemble


def p_xor(ph: Physics, Pd: int, variant: str = "normal") -> np.ndarray:
    assert ph.state_dim >= 4 and ph.payload_width >= 2 and ph.prog_len >= 16
    q_in_readout = "ZERO" if variant == "mf_q_readout" else "S2"
    body = A(ph, [
        ("CONST", "T3", 0, 0, Pd - 1),
        ("MOD", "T2", "S3", "T3", 0),
        ("ADDI", "S3", "S3", 0, 1),
        ("GT", "T2", "T2", "ZERO", 0),
        ("MULQ", "S1", "S1", "T2", 0),
        ("MULQ", "S2", "S2", "T2", 0),
        ("MAX", "T0", "SENSE", "IN0_0", 0),
        ("GT", "T0", "T0", "ZERO", 0),
        ("GT", "T1", "IN0_1", "SENSE", 0),
        ("GT", "PAY0", "T0", "S1", 0),
        ("GT", "PAY1", "T1", "S2", 0),
        ("ADD", "EMIT", "PAY0", "PAY1", 0),
        ("MAX", "S1", "S1", "T0", 0),
        ("MAX", "S2", "S2", "T1", 0),
        ("XOR", "T3", "S1", q_in_readout, 0),
        ("ADDI", "S0", "T3", 0, -128),
    ])
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()


def p_flip(ph: Physics, variant: str = "normal") -> np.ndarray:
    assert ph.state_dim >= 2 and ph.prog_len >= 16
    teach = "ZERO" if variant == "mf_teacher" else "SENSE"
    last = ("MOV", "S0", "S1", 0, 0) if variant == "mf_readout_no_m" else ("MOV", "S0", "T3", 0, 0)
    body = A(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0),
        ("CONST", "T2", 0, 0, 128),
        ("SUB", "T3", "ZERO", "T2", 0),
        ("GT", "PAY0", "T0", "T2", 0),
        ("GT", "T3", "T3", "T0", 0),
        ("SUB", "PAY0", "PAY0", "T3", 0),
        ("SUB", "T0", "PAY0", "S1", 0),
        ("MULQ", "EMIT", "T0", "PAY0", 0),
        ("MULQ", "T1", "S0", "S1", 0),
        ("MULQ", "T2", "PAY0", "PAY0", 0),
        ("SEL", "T2", "PAY0", "S1", 0),
        ("MOV", "S1", "T2", 0, 0),
        ("MULQ", "S0", "T1", "S1", 0),
        ("MULQ", "T3", teach, teach, 0),
        ("SEL", "T3", "SENSE", "S0", 0),
        last,
    ])
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()


def p_multihop(ph: Physics, variant: str = "normal") -> np.ndarray:
    body = plants.relay_flood(ph)
    if variant == "mf_no_relay":
        n = 12
        extra = A(ph, [("MULQ", "T0", "SENSE", "SENSE", 0), ("GT", "T0", "T0", "ZERO", 0),
                       ("MULQ", "EMIT", "EMIT", "T0", 0)])
        body = body.copy()
        body[n:n + 3] = extra[:3]
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()
