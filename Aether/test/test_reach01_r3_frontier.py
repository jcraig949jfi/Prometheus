"""REACH01 R3 known answers: descriptor / rung logic and the evaluator on hand-built patches (CPU, small lattice)."""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "V2B", "REACH01", "R3"))
import r3_frontier as F  # noqa: E402


def test_rung_logic():
    const = np.full(16, 7, np.uint8)
    assert F.descriptor(const)[1] == 0
    only_a = np.array([10 * (c // 4) for c in range(16)], np.uint8)
    assert F.descriptor(only_a)[1] == 1
    both = np.array([(c // 4) ^ (4 * (c % 4)) for c in range(16)], np.uint8)
    assert F.descriptor(both)[1] == 2


def test_depmap_known_answer():
    fin = np.zeros((16, 16, 16), np.uint32)
    for c in range(16):
        fin[c, 0, 0] = c // 4          # depends on a only
        fin[c, 0, 5] = c % 4           # b only
        fin[c, 3, 9] = c               # both
    da, db = F.depmap(fin)
    assert da[0, 0] and not db[0, 0] and db[0, 5] and not da[0, 5] and da[3, 9] and db[3, 9]
    assert da.sum() == 2 and db.sum() == 2


def empty():
    p = np.zeros((5, 16, 16), np.uint8)
    p[0] = 9
    return p


def test_empty_patch_has_no_reach():
    ev = F.Evaluator("XOR", side=2, backend="cpu")
    o = ev.run_batch(np.stack([empty()]))
    d = F.frontier_descriptor(o[0], ev.last_fin[0])
    assert d == (1, 1, 0, 0, 0)       # each input deposits into patch column 0 (reach 1) and goes no further


def test_relay_row_extends_reach_of_a_only():
    p = empty()
    p[:, 4, :] = np.array([1, F.X.E, 3, 0, 7], np.uint8)[:, None]     # row 6 of the tile (patch row 4)
    ev = F.Evaluator("XOR", side=2, backend="cpu")
    o = ev.run_batch(np.stack([p]))
    d = F.frontier_descriptor(o[0], ev.last_fin[0])
    assert d[0] >= 5 and d[1] == 1                                   # a reaches further (per-column, v2); b only its deposit


def test_isolation_between_tiles():
    rng = np.random.default_rng(3)
    ev = F.Evaluator("XOR", side=2, backend="cpu")
    P = F.random_patches(rng, 4)
    full = ev.run_batch(P)
    finfull = ev.last_fin.copy()
    for i in range(4):
        Q = np.stack([empty() for _ in range(4)])
        Q[i] = P[i]
        o = ev.run_batch(Q)
        assert (o[i] == full[i]).all() and (ev.last_fin[i] == finfull[i]).all()
