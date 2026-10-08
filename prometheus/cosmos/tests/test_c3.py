"""C3 instrument tests: certificate classes on planted systems, decoder-free coordinates, substitution."""
import numpy as np
import pytest

from prometheus.cosmos.c3.calib import DelayLine, NoMemory, Register
from prometheus.cosmos.c3.certify import certify
from prometheus.cosmos.c3.geometry import coordinates
from prometheus.cosmos.c3.substrates import Graph, Hybrid, RNN, Stig
from prometheus.cosmos.c3.system import rollout
from prometheus.cosmos.c3.task import Task, paired_batch

T = Task(4, 4)


@pytest.mark.parametrize("sysm,expected", [
    (NoMemory(T), "NONE"),
    (Register(T, read_register=False, name="PV"), "PASSIVE"),
    (Register(T, read_register=True, name="FX"), "FUNCTIONAL"),
])
def test_certificate_classes_on_planted_systems(sysm, expected):
    r = certify(sysm, T, seed=3, E_train=600, E_test=900)
    assert r["class"] == expected, (r["P1"], r["P2"])


def test_passive_readout_probe_sees_nothing_generic_probe_sees_everything():
    r = certify(Register(T, read_register=False, name="PV"), T, seed=4, E_train=600, E_test=900)
    assert r["P1"]["D_generic"] > 1.5 and abs(r["P1"]["D_readout"]) < 0.05 and r["P2"]["effect"] == 0


def test_interchange_swaps_the_full_state_between_pair_partners():
    fd = DelayLine(T)
    cues, obs = paired_batch(T, 50, np.random.default_rng(0))
    a = rollout(fd, obs, np.random.default_rng(1), paired=True)
    b = rollout(fd, obs, np.random.default_rng(1), paired=True, swap_at=T.k)
    last_a = a["final"]["chain"][:, -1]
    last_b = b["final"]["chain"][:, -1]
    assert (last_b[0::2] == last_a[1::2]).all() and (last_b[1::2] == last_a[0::2]).all()


def test_coordinates_show_the_passive_signature_in_the_world():
    stay = coordinates(Stig(T, 0.05, 0.0, 0, 0.0), T, n_pairs=100)
    leave = coordinates(Stig(T, 0.05, 0.0, 1, 0.0), T, n_pairs=100)
    assert stay["sR"] > 0.5 and stay["sF"] > 0.5
    assert leave["sR"] < 1e-9 and leave["sF"] > 0.5          # history in the world, none in the agent's view


def test_memoryless_substrates_have_zero_signal():
    c = coordinates(RNN(T, 0.0, 1.0, 0.05), T, n_pairs=100)
    assert c["sF"] < 1e-9 and c["sR"] < 1e-9


def test_substitution_hybrid_keeps_signal_through_either_channel():
    for internal, external, expect in ((True, False, True), (False, True, True), (False, False, False)):
        c = coordinates(Hybrid(T, internal, external), T, n_pairs=100)
        assert (c["sR"] > 0.03) == expect, (internal, external, c["sR"])


def test_coordinates_are_unit_free_under_state_rescaling():
    """Standardisation per component: scaling a view by a constant must not move sR / sF."""
    class Scaled(RNN):
        def full_state(self, st):
            return 1000.0 * st["x"]

        def readout_features(self, st):
            return 1000.0 * st["x"]
    a = coordinates(RNN(T, 0.9, 0.5, 0.05), T, n_pairs=100, seed=5)
    b = coordinates(Scaled(T, 0.9, 0.5, 0.05), T, n_pairs=100, seed=5)
    assert abs(a["sR"] - b["sR"]) < 1e-9 and abs(a["sF"] - b["sF"]) < 1e-9
