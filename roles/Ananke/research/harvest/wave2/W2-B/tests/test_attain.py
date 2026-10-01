"""Known-answer tests for the W2-B attainability certifier (attain.py, rulers_c1.py, adversaries.py).
Each test has a positive case (the verdict is known by proof, see the W2-B report) and a must-fail input on
which the same assertion would be false. CPU only, 2 threads; a few minutes in total.
  CUDA_VISIBLE_DEVICES=-1 python -m pytest tests/test_attain.py -q -p no:cacheprovider
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import w2b_common as c  # noqa: E402,F401  (CPU guard, 2 threads, repo on sys.path)
from w2b_common import np, envs, assays, Physics, plants  # noqa: E402
import adversaries as adv  # noqa: E402
import attain as A  # noqa: E402
import rulers_c1 as R  # noqa: E402
from prometheus.ananke import swap_rel as sr  # noqa: E402

SEEDS = assays.world_seeds(0x7E5701, 16)
RING = dict(topology="ring", n_sites=24, radius=1, dest_mode="all", lat_base=1, lat_hop=0, lat_jitter=0,
            loss=0.0, payload_width=2, channels=1, update_mode="sync", update_period=1, decay_shift=0,
            state_dim=4, prog_len=28)
PH = Physics(**RING).validate()
PHG = Physics(**{**RING, "topology": "global", "dest_mode": "sample", "fanout": 2}).validate()
X0 = Physics(topology="torus", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1, lat_hop=0,
             lat_jitter=0, decay_shift=0, update_mode="sync", update_period=1, state_dim=4, payload_width=2,
             channels=1, prog_len=18).validate()
ECHO = plants.c1b_echo_physics()
RELAY = envs.EnvSpec(family="RELAY", d=3, delta=8, trials=12)
MAJ = envs.EnvSpec(family="MAJ", d=2, delta=8, trials=12)
XOR = envs.EnvSpec(family="XOR", d=3, delta=8, trials=12)
FLIP = envs.EnvSpec(family="FLIP", d=3, delta=8, block=4, trials=16)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)


def bc(ph, body):
    return np.broadcast_to(body, (ph.rules, ph.prog_len, 5)).copy()


NULL = A.Program("null", "null", lambda ph, env: plants.plant("null", ph))
SILENT = A.Program("sense_copy", "adversary", lambda ph, env: plants.plant("sense_copy", ph), "transport")
FLOOD = A.Program("relay_flood", "plant", lambda ph, env: plants.plant("relay_flood", ph))


def test_zero_comm_forced_in_comm_family_not_in_hold():
    cert = A.certify(R.ZERO_COMM, [A.Cell(PH, RELAY, "relay")], [NULL, SILENT, FLOOD], SEEDS)
    assert cert.verdict == "DEGENERATE" and cert.forced and cert.attainable == (0.5, 0.5)
    # MUST-FAIL input: HOLD (actuator = sensor): a local latch keeps its accuracy under zero_comm
    hold = [NULL, A.Program("hold_latch", "plant", lambda ph, env: plants.plant("hold_latch", ph)),
            A.Program("echo_hold", "plant", lambda ph, env: bc(ph, plants.echo_hold(ph)))]
    cert2 = A.certify(R.ZERO_COMM, [A.Cell(ECHO, HOLD, "hold")], hold, SEEDS)
    assert not cert2.forced and cert2.verdict != "DEGENERATE"


def test_comm_dependent_aliases_signal_when_zero_comm_forced():
    progs = [NULL, SILENT, FLOOD]
    a = A.certify(R.SIGNAL, [A.Cell(PH, RELAY, "relay")], progs, SEEDS)
    b = A.certify(R.COMM_DEPENDENT, [A.Cell(PH, RELAY, "relay")], progs, SEEDS)
    al = A.alias(a, b)
    assert al["identical"] and a.verdict == "SOUND"
    assert any(r["passed"] for r in a.rows)             # MUST-FAIL guard: the alias is not all-False


def test_reach_beyond_hop_legacy_cheatable_nearest_not():
    progs = [NULL, SILENT, FLOOD]
    leg = A.certify(R.REACH_BEYOND_HOP, [A.Cell(PH, MAJ, "maj")], progs, SEEDS)
    # the plant needs a world where one sensor's influence can travel (RELAY); the silent adversary is
    # checked on both worlds
    near = A.certify(R.REACH_BEYOND_HOP_NEAREST, [A.Cell(PH, MAJ, "maj"), A.Cell(PH, RELAY, "relay")], progs, SEEDS)
    assert leg.verdict == "CHEATABLE" and leg.cheapest["program"] == "sense_copy"
    assert near.verdict == "SOUND"


def test_reach_beyond_hop_unreachable_on_global():
    cert = A.certify(R.REACH_BEYOND_HOP, [A.Cell(PHG, RELAY, "global")], [NULL, SILENT, FLOOD], SEEDS)
    assert cert.verdict == "UNREACHABLE" and cert.attainable == (0.0, 0.0)
    ring = A.certify(R.REACH_BEYOND_HOP, [A.Cell(PH, RELAY, "ring")], [NULL, SILENT, FLOOD], SEEDS)
    assert ring.verdict != "UNREACHABLE"                # MUST-FAIL: the same programs reach on a ring


def test_xor_signal_cheatable_pivotality_sound():
    Pd = XOR.period()
    progs = [NULL, A.Program("parity", "plant", lambda ph, env: adv.p_xor(ph, Pd)),
             A.Program("not_P", "adversary", lambda ph, env: adv.xor_oneflag(ph, Pd, "not_P"), "parity")]
    s = A.certify(R.SIGNAL, [A.Cell(X0, XOR, "x0")], progs, SEEDS)
    p = A.certify(R.XOR_PIVOT, [A.Cell(X0, XOR, "x0")], progs, SEEDS)
    assert s.verdict == "CHEATABLE" and s.cheapest["program"] == "not_P"
    assert p.verdict == "SOUND"


def test_flip_signal_cheatable_feedback_control_sound():
    progs = [NULL, A.Program("P_FLIP", "plant", lambda ph, env: adv.p_flip(ph)),
             A.Program("FLIP_CLOCK", "adversary", lambda ph, env: adv.flip_clock(ph, env.period(), env.block),
                       "feedback after trial 0")]
    s = A.certify(R.SIGNAL, [A.Cell(PH, FLIP, "flip")], progs, SEEDS)
    f = A.certify(R.FLIP_FEEDBACK, [A.Cell(PH, FLIP, "flip")], progs, SEEDS)
    assert s.verdict == "CHEATABLE" and s.cheapest["program"] == "FLIP_CLOCK" and s.cheapest["value"] > 0.9
    assert f.verdict == "SOUND"


def test_analytic_gate_eligibility():
    # absolute swap FLIP (hi99 < .40) needs normal well above .60 even with an ideal follow
    n50 = 1 - A.min_true_to_cross(0.40, 32, 12, "hi_lt", 0.5)
    assert 0.62 < n50 < 0.70
    # SIGNAL needs ~.61 at P32 K12 and less with more pairs (monotone)
    a, b = A.min_true_to_cross(0.55, 32, 12), A.min_true_to_cross(0.55, 256, 12)
    assert 0.55 < b < a < 0.65
    # MUST-FAIL: a reader at exactly the .70 ceiling crosses INTEGRATION only ~0.5% of the time
    assert A.ci_gate_power(0.70, 0.70, 32, 12) < 0.01 < A.ci_gate_power(0.784, 0.70, 32, 12)


def test_swap_rel_noop_arm_forces_no_effect():
    rng = np.random.default_rng(3)
    for _ in range(10):
        a = rng.binomial(11, rng.uniform(0.62, 0.95), size=64) / 11
        lab = sr.from_pairs(a, a, 11)
        assert lab["ident"] and lab["label"] == "NO_EFFECT_REL"
    # MUST-FAIL: the same normal with an ideal follow is FLIP_REL, not NO_EFFECT_REL
    assert sr.from_pairs(a, 1 - a, 11)["label"] == "FLIP_REL"


def test_certifier_single_program_never_forced():
    cert = A.certify(R.SIGNAL, [A.Cell(PH, RELAY, "relay")], [FLOOD], SEEDS)
    assert not cert.forced and "single program" in " ".join(cert.notes)
