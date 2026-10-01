"""PTE families for the explib family certifier: standard program roles, the reference cells, and certify().

    from prometheus.ananke.audit import certify as C, rulers as R
    cert = C.certify(R.SIGNAL, [C.Cell(C.X0, C.XOR, "x0")], C.xor_programs(C.XOR.period()), seeds)
    cert.verdict   # CHEATABLE: the NOR one-flag readout crosses (cert.cheapest names it)

certify() is prometheus.explib.attainable.certify_family; Cell / Program / Ruler / alias are re-exported. The
reference physics (RING, GLOBAL, X0) and environments are W2-B's known-answer worlds (W2-B tests/test_attain.py,
REPORT P1-P6). A verdict is relative to the declared family: SOUND is never a proof; CHEATABLE / DEGENERATE
rows are constructive counterexamples.
"""
from __future__ import annotations

import numpy as np

from prometheus.ananke import envs, plants
from prometheus.ananke.physics import Physics
from prometheus.explib.attainable import Cell, Program, Ruler, alias, certify_family, family_checks  # noqa: F401

from . import programs as PG

certify = certify_family

RING_KW = dict(topology="ring", n_sites=24, radius=1, dest_mode="all", lat_base=1, lat_hop=0, lat_jitter=0,
               loss=0.0, payload_width=2, channels=1, update_mode="sync", update_period=1, decay_shift=0,
               state_dim=4, prog_len=28)


def ring() -> Physics:
    return Physics(**RING_KW).validate()


def global_() -> Physics:
    return Physics(**{**RING_KW, "topology": "global", "dest_mode": "sample", "fanout": 2}).validate()


def x0() -> Physics:
    """H-PLANT X0 with prog_len 18 (room for two readout lines)."""
    return Physics(topology="torus", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1, lat_hop=0,
                   lat_jitter=0, decay_shift=0, update_mode="sync", update_period=1, state_dim=4,
                   payload_width=2, channels=1, prog_len=18).validate()


RELAY = envs.EnvSpec(family="RELAY", d=3, delta=8, trials=12)
MAJ = envs.EnvSpec(family="MAJ", d=2, delta=8, trials=12)
XOR = envs.EnvSpec(family="XOR", d=3, delta=8, trials=12)
FLIP = envs.EnvSpec(family="FLIP", d=3, delta=8, block=4, trials=16)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)


def _bc(ph, body):
    return np.broadcast_to(body, (ph.rules, ph.prog_len, 5)).copy()


NULL = Program("null", "null", lambda ph, env: plants.plant("null", ph))
SENSE_COPY = Program("sense_copy", "adversary", lambda ph, env: plants.plant("sense_copy", ph), "transport")
RELAY_FLOOD = Program("relay_flood", "plant", lambda ph, env: plants.plant("relay_flood", ph))
HOLD_LATCH = Program("hold_latch", "plant", lambda ph, env: plants.plant("hold_latch", ph))
ECHO_HOLD = Program("echo_hold", "plant", lambda ph, env: _bc(ph, plants.echo_hold(ph)))


def comm_programs() -> list:
    """null, a silent local adversary (sense_copy lacks transport) and the relay_flood plant."""
    return [NULL, SENSE_COPY, RELAY_FLOOD]


def xor_programs(Pd: int, cheat: str = "not_P") -> list:
    return [NULL, Program("parity", "plant", lambda ph, env: PG.p_xor(ph, Pd)),
            Program(cheat, "adversary", lambda ph, env: PG.xor_oneflag(ph, Pd, cheat), "parity")]


def flip_programs() -> list:
    return [NULL, Program("P_FLIP", "plant", lambda ph, env: PG.p_flip(ph)),
            Program("FLIP_CLOCK", "adversary", lambda ph, env: PG.flip_clock(ph, env.period(), env.block),
                    "feedback after trial 0")]


def flip_b_programs() -> list:
    """P-FLIP (infers m) vs RELAY_LATCH (copy class: relays the cue, latches the teacher)."""
    return [Program("P_FLIP", "plant", lambda ph, env: PG.p_flip(ph)),
            Program("RELAY_LATCH", "adversary", lambda ph, env: PG.relay_latch(ph), "mapping inference")]
