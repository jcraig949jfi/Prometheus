"""Regression tests for R-MECH F1 (SYSID restatement) and the G7 locality guard.

The F1 cheat (probe decodability after h steps, indexed at h = q by the law) must be IMPOSSIBLE to build
through the coordinate interface, not merely blacklisted.
"""
import ast
from pathlib import Path

import numpy as np
import pytest

from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.c4 import sysid_local as L
from prometheus.cosmos.c4.planted import Reservoir, RotReservoir

TASK = Task(4, 2)


def _probe(sys_, seed=1):
    return L.LocalProbe(sys_, TASK.n_symbols, seed=seed)


def rel_at_h_cheat(probe, h, V=4, n=256):
    """Bellerophon's F1 coordinate rebuilt against the probe: inject a probe symbol, drive h steps, decode."""
    s = probe.stationary(n)
    p = probe.symbols(n) % V
    s = probe.step1(s, p, probe.noise(n))
    for _ in range(h):
        s = probe.step1(s, probe.symbols(n), probe.noise(n))
    return s


def test_f1_rel_cheat_cannot_be_built_through_the_probe():
    with pytest.raises(L.HorizonError):
        rel_at_h_cheat(_probe(Reservoir(TASK, .8, .3)), h=3)


def test_kick_after_step_refused():
    pr = _probe(Reservoir(TASK, .8, .3))
    s = pr.step1(pr.stationary(8), np.zeros(8, int), pr.noise(8))
    with pytest.raises(L.HorizonError):
        pr.kick(s, .01)


def test_g1_imports_numpy_only():
    tree = ast.parse(Path(L.__file__).read_text())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mods.add((node.module or "").split(".")[0])
    assert mods <= {"numpy", "typing", "__future__"}, mods


def test_coordinates_recover_planted_leak():
    for a in (.3, .6, .9):
        c = L.coordinates(_probe(Reservoir(TASK, a, .3)))
        assert c["rho"] == pytest.approx(a, abs=1e-6)


def test_g3_coordinates_identical_across_k():
    cs = [L.coordinates(_probe(Reservoir(Task(4, k), .8, .3))) for k in (2, 4, 8)]
    assert cs[0] == cs[1] == cs[2]


class _Rebased(Reservoir):
    """Same physics, views re-encoded by an invertible linear map plus duplicated components (G5)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        D = self.d + TASK.n_symbols
        r = np.random.default_rng(7)
        self.A = r.standard_normal((D, D)) + 3 * np.eye(D)

    def full_state(self, st):
        F = super().full_state(st) @ self.A.T
        return np.hstack([F, F[:, :2]])

    def readout_features(self, st):
        return self.full_state(st)


def test_g5_reencoding_invariance():
    a = L.coordinates(_probe(Reservoir(TASK, .8, .3)))
    b = L.coordinates(_probe(_Rebased(TASK, .8, .3)))
    for k in ("rho", "eta", "gamma"):
        assert b[k] == pytest.approx(a[k], rel=0.05), k


def test_rotation_equivalent_physics_same_coordinates():
    a = L.coordinates(_probe(Reservoir(TASK, .8, .3)))
    b = L.coordinates(_probe(RotReservoir(TASK, .8, .3)))
    assert b["rho"] == pytest.approx(a["rho"], rel=0.02)
