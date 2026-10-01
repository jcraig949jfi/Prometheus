"""W2-B cheap adversaries and reference plants (hand-written genomes; never search seeds).

p_xor / p_flip are copied verbatim from harvest/H-PLANT/hp_plants.py (frozen plan 01234c0ad) so the
references cannot drift; the adversaries are new:

  xor_oneflag(ph, Pd, rule)   XOR flood of the two sign flags P (+ cue seen) and Q (- cue seen), but the
                              readout is a NON-PARITY function of (P, Q). Every such rule agrees with
                              x1*x2 on 3/4 or 1/4 of input combos (proof in REPORT), so the best scores .75.
  flip_clock(ph, Pd, block)   FLIP solved WITHOUT tracking feedback: the actuator accepts the teacher ONCE
                              (trial 0: learns m0), then flips its stored mapping on a block clock. Because
                              envs.build makes m_k = m0 * (-1)^(k // block) deterministic, this scores 1.0
                              on every scored trial while ignoring every later teacher.
"""
from __future__ import annotations

import numpy as np

from prometheus.ananke import plants
from prometheus.ananke.physics import Physics

A = plants.assemble


def _bc(ph, body):
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()


def p_xor(ph: Physics, Pd: int, variant: str = "normal") -> np.ndarray:
    """H-PLANT P-XOR (verbatim body; variant 'normal' only here)."""
    assert ph.state_dim >= 4 and ph.payload_width >= 2 and ph.prog_len >= 16
    return _bc(ph, A(ph, _xor_front(Pd) + [
        ("XOR", "T3", "S1", "S2", 0),
        ("ADDI", "S0", "T3", 0, -128),
    ]))


def _xor_front(Pd: int) -> list:
    return [
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
    ]


XOR_RULES = {
    # name: readout lines after the flood front; S1 = 256*[P], S2 = 256*[Q]
    "not_P": [("SUB", "S0", "ZERO", "S1", 0), ("ADDI", "S0", "S0", 0, 128)],       # + iff no + cue  (NOR-type)
    "not_Q": [("SUB", "S0", "S2", "ZERO", 0), ("ADDI", "S0", "S0", 0, -128)],      # + iff a - cue  (OR-type; scores .25, its negation .75)
    "P": [("ADDI", "S0", "S1", 0, -128)],                                           # + iff a + cue (scores .25)
    "P_and_notQ_neg": [("SUB", "T3", "S1", "S2", 0), ("GT", "T3", "T3", "ZERO", 0),  # - iff (P and not Q)  (scores .25)
                       ("SUB", "S0", "ZERO", "T3", 0), ("ADDI", "S0", "S0", 0, 128)],
}


def xor_oneflag(ph: Physics, Pd: int, rule: str = "not_P") -> np.ndarray:
    assert ph.state_dim >= 4 and ph.payload_width >= 2 and ph.prog_len >= 18
    return _bc(ph, A(ph, _xor_front(Pd) + XOR_RULES[rule]))


def p_flip(ph: Physics, variant: str = "normal") -> np.ndarray:
    """H-PLANT P-FLIP (verbatim)."""
    assert ph.state_dim >= 2 and ph.prog_len >= 16
    teach = "ZERO" if variant == "mf_teacher" else "SENSE"
    last = ("MOV", "S0", "S1", 0, 0) if variant == "mf_readout_no_m" else ("MOV", "S0", "T3", 0, 0)
    return _bc(ph, A(ph, _flip_front() + [
        ("MULQ", "T3", teach, teach, 0),
        ("SEL", "T3", "SENSE", "S0", 0),
        last,
    ]))


def _flip_front() -> list:
    return [
        ("ADD", "T0", "SENSE", "IN0_0", 0),
        ("CONST", "T2", 0, 0, 128),
        ("SUB", "T3", "ZERO", "T2", 0),
        ("GT", "PAY0", "T0", "T2", 0),
        ("GT", "T3", "T3", "T0", 0),
        ("SUB", "PAY0", "PAY0", "T3", 0),        # v = cue sign * 256 (teacher +-128 excluded)
        ("SUB", "T0", "PAY0", "S1", 0),
        ("MULQ", "EMIT", "T0", "PAY0", 0),       # re-emit only on change
        ("MULQ", "T1", "S0", "S1", 0),           # m = S0 * last cue
        ("MULQ", "T2", "PAY0", "PAY0", 0),
        ("SEL", "T2", "PAY0", "S1", 0),
        ("MOV", "S1", "T2", 0, 0),               # S1 = last cue sign
        ("MULQ", "S0", "T1", "S1", 0),           # S0 = m * c
    ]


def flip_clock(ph: Physics, Pd: int, block: int) -> np.ndarray:
    """P-FLIP's transport and m*c bookkeeping, but (i) SENSE overwrites S0 only while flag S2 == 0 (so the
    actuator uses the FIRST teacher only), and (ii) at every block boundary tick (S3 mod block*Pd == 0)
    S0 is negated, so the carried mapping flips on the clock. Needs sync update_period 1 (tick clock),
    state_dim >= 4, channels 1, plastic_route 0 (RVAL is scratch), prog_len >= 28."""
    assert ph.state_dim >= 4 and ph.prog_len >= 28 and ph.update_mode == "sync" and ph.update_period == 1
    assert not ph.plastic_route and block * Pd - 1 <= 32767
    return _bc(ph, A(ph, _flip_front() + [
        ("MULQ", "T3", "SENSE", "SENSE", 0),     # nonzero iff SENSE != 0
        ("GT", "T2", "S2", "ZERO", 0),           # 256 iff a SENSE event was already seen
        ("CONST", "T0", 0, 7, 2),                # 256
        ("SUB", "T0", "T0", "T2", 0),            # 256 iff first event
        ("MAX", "S2", "S2", "T3", 0),            # latch the flag
        ("MULQ", "T3", "T3", "T0", 0),           # nonzero iff SENSE and first event
        ("SEL", "T3", "SENSE", "S0", 0),
        ("MOV", "S0", "T3", 0, 0),               # the teacher writes S0 only once
        ("CONST", "RVAL", 0, 0, block * Pd - 1),
        ("MOD", "T2", "S3", "RVAL", 0),          # phase = tick mod (block*Pd)
        ("ADDI", "S3", "S3", 0, 1),
        ("GT", "T2", "T2", "ZERO", 0),           # 256 unless block boundary
        ("ADD", "T2", "T2", "T2", 0),
        ("ADDI", "T2", "T2", 0, -256),           # +256, or -256 at a boundary
        ("MULQ", "S0", "S0", "T2", 0),           # flip the carried mapping on the clock
    ]))


def maj_sum(ph: Physics) -> np.ndarray:
    """MAJ positive control for one-hop physics (all sensors inside the actuator's radius, dest all, fixed
    latency): each sensor emits its cue sign; every site latches sign(sum of the payloads that arrive in one
    tick). Simultaneous arrival makes the latch a 5-sensor majority (.837); with one live sensor it is .70."""
    return _bc(ph, A(ph, [
        ("CONST", "T0", 0, 7, 1),                # 128
        ("GT", "T1", "SENSE", "T0", 0),
        ("SUB", "T2", "ZERO", "T0", 0),
        ("GT", "T2", "T2", "SENSE", 0),
        ("SUB", "T1", "T1", "T2", 0),            # cue sign*256 or 0
        ("MULQ", "EMIT", "T1", "T1", 0),         # emit on cue
        ("MOV", "PAY0", "T1", 0, 0),
        ("GT", "T2", "IN0_0", "ZERO", 0),
        ("GT", "T3", "ZERO", "IN0_0", 0),
        ("SUB", "T2", "T2", "T3", 0),            # sign of the arriving sum *256, or 0
        ("MULQ", "T3", "T2", "T2", 0),
        ("SUB", "T0", "T2", "S0", 0),
        ("MULQ", "T0", "T0", "T3", 0),
        ("ADD", "S0", "S0", "T0", 0),            # S0 := arrival-sum sign where nonzero
    ]))
