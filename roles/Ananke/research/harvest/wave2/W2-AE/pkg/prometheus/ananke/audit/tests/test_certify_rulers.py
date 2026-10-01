"""audit.certify + audit.rulers on the real engine: W2-B's headline known answers (W2-B tests/test_attain.py,
REPORT P1-P6) and W2-J's XOR_SYM. Each positive case has a must-fail twin. 16 worlds, CPU."""
from __future__ import annotations

import numpy as np

from prometheus.ananke import assays, plants
from prometheus.ananke import swap_rel as sr
from prometheus.ananke.audit import certify as C
from prometheus.ananke.audit import rulers as R
from prometheus.explib.outcomes import FAIL, PASS

SEEDS = assays.world_seeds(0x7E5701, 16)
PH, PHG, X0, ECHO = C.ring(), C.global_(), C.x0(), plants.c1b_echo_physics()


def test_zero_comm_forced_in_comm_family_not_in_hold():
    cert = C.certify(R.ZERO_COMM, [C.Cell(PH, C.RELAY, "relay")], C.comm_programs(), SEEDS)
    assert cert.verdict == "DEGENERATE" and cert.forced and cert.attainable == (0.5, 0.5)
    assert {c.name: c.outcome for c in C.family_checks(cert)}["A2_not_forced"] == FAIL
    # MUST-FAIL input: HOLD (actuator = sensor): a local latch keeps its accuracy under zero_comm
    cert2 = C.certify(R.ZERO_COMM, [C.Cell(ECHO, C.HOLD, "hold")], [C.NULL, C.HOLD_LATCH, C.ECHO_HOLD], SEEDS)
    assert not cert2.forced and cert2.verdict != "DEGENERATE"


def test_comm_dependent_aliases_signal_when_zero_comm_forced():
    a = C.certify(R.SIGNAL, [C.Cell(PH, C.RELAY, "relay")], C.comm_programs(), SEEDS)
    b = C.certify(R.COMM_DEPENDENT, [C.Cell(PH, C.RELAY, "relay")], C.comm_programs(), SEEDS)
    assert C.alias(a, b)["identical"] and a.verdict == "SOUND"
    assert any(r["passed"] for r in a.rows)             # MUST-FAIL guard: the alias is not all-False


def test_reach_beyond_hop_legacy_cheatable_nearest_sound_global_unreachable():
    leg = C.certify(R.REACH_BEYOND_HOP, [C.Cell(PH, C.MAJ, "maj")], C.comm_programs(), SEEDS)
    near = C.certify(R.REACH_NEAREST, [C.Cell(PH, C.MAJ, "maj"), C.Cell(PH, C.RELAY, "relay")],
                     C.comm_programs(), SEEDS)
    assert leg.verdict == "CHEATABLE" and leg.cheapest["program"] == "sense_copy"
    assert near.verdict == "SOUND"
    glob = C.certify(R.REACH_BEYOND_HOP, [C.Cell(PHG, C.RELAY, "global")], C.comm_programs(), SEEDS)
    assert glob.verdict == "UNREACHABLE" and glob.attainable == (0.0, 0.0)


def test_xor_nor_cheat_passes_signal_pivot_and_sym_are_sound():
    progs = C.xor_programs(C.XOR.period())
    cell = [C.Cell(X0, C.XOR, "x0")]
    s = C.certify(R.SIGNAL, cell, progs, SEEDS)
    assert s.verdict == "CHEATABLE" and s.cheapest["program"] == "not_P" and 0.70 < s.cheapest["value"]
    assert C.certify(R.XOR_PIVOT, cell, progs, SEEDS).verdict == "SOUND"
    sym = C.certify(R.XOR_SYM, cell, progs, SEEDS)
    assert sym.verdict == "SOUND"
    # the mechanism (value = min/max conditional pivotality): parity is pivotal whatever the other cue is; the
    # NOR readout only when the other cue is - (one conditional pivotality is exactly 0)
    val = {r["program"]: r["value"] for r in sym.rows}
    assert val["parity"] > 0.9 and val["not_P"] == 0.0


def test_flip_clock_passes_signal_feedback_control_sound():
    progs = C.flip_programs()
    cell = [C.Cell(PH, C.FLIP, "flip")]
    s = C.certify(R.SIGNAL, cell, progs, SEEDS)
    f = C.certify(R.FLIP_FEEDBACK, cell, progs, SEEDS)
    assert s.verdict == "CHEATABLE" and s.cheapest["program"] == "FLIP_CLOCK" and s.cheapest["value"] > 0.9
    assert f.verdict == "SOUND"
    ck = {c.name: c.outcome for c in C.family_checks(s)}
    assert ck["G2_adversary"] == FAIL and ck["G1_null"] == PASS and ck["G3_positive"] == PASS


def test_swap_rel_noop_arm_forces_no_effect():
    rng = np.random.default_rng(3)
    for _ in range(10):
        a = rng.binomial(11, rng.uniform(0.62, 0.95), size=64) / 11
        lab = sr.from_pairs(a, a, 11)
        assert lab["ident"] and lab["label"] == "NO_EFFECT_REL"
    assert sr.from_pairs(a, 1 - a, 11)["label"] == "FLIP_REL"       # MUST-FAIL: ideal follow is FLIP_REL
