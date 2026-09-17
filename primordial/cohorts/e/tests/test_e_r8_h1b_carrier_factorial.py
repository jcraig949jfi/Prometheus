"""E-R8-H1b: the factorial cells take each component from the declared source, and the preregistered carrier rule
reads planted main effects as designed."""
import numpy as np
import pytest

from primordial.cohorts.e import r8_h1b_carrier_factorial as F
from primordial.fabric import envelope as EV
from primordial.qd import e7_run as E7
from primordial.score import evidence_n as EN


@pytest.fixture(scope="module")
def g7r():
    return E7.G7(13, "linear")


@pytest.mark.parametrize("seed", range(4))
def test_cells_integrity(g7r, seed):
    dA = g7r.pack(g7r.init(np.random.default_rng(seed), 16))
    sc = g7r.pack(g7r.init(np.random.default_rng(100 + seed), 16))
    cells = F.make_cells(g7r, dA, sc)
    integ = F.cell_integrity(g7r, dA, sc, cells)
    assert len(cells) == 8 and all(v["ok"] for v in integ.values()), integ
    assert np.array_equal(cells["W1b1C1"], dA) and np.array_equal(cells["W0b0C0"], sc)
    assert len({c.tobytes() for c in cells.values()}) == 8


def test_integrity_catches_a_wrong_source(g7r):
    dA = g7r.pack(g7r.init(np.random.default_rng(1), 16))
    sc = g7r.pack(g7r.init(np.random.default_rng(2), 16))
    cells = F.make_cells(g7r, dA, sc)
    cells["W0b1C0"] = cells["W0b0C0"].copy()
    assert not F.cell_integrity(g7r, dA, sc, cells)["W0b1C0"]["ok"]


def _rows(eff, n=32, noise=0.3, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for f, rs in F.H.run_order(F.FAMILIES, F.RUN_SEEDS)[:n]:
        base = 150 + rng.normal(0, 2)
        for cell in F.CELLS:
            bits = F.bits_of(cell)
            v = base + sum(e * bit for e, bit in zip(eff, bits)) + rng.normal(0, noise)
            out.append({"exp_id": F.EXP, "condition": cell, "status": F.STATUS[cell], "run_id": f"{f}|{rs}",
                        "held_auc": float(v), "held64": 1.0, "zero_shot_held64": 1.0, "train_auc": 1.0,
                        "cell_integrity": {"ok": True}, "donor_fused_eq_numpy": True})
    return out


@pytest.mark.parametrize("eff,want", [((0, 0, 0), "CARRIERS_NONE"), ((0, 2, 0), "CARRIERS_b"),
                                      ((0, 1.5, 1.5), "CARRIERS_b+C"), ((2, 0, 0), "CARRIERS_W")])
def test_carrier_rule(eff, want):
    got = F.analyze(_rows(eff))
    assert got["n_complete_runs"] == 32 and got["outcome"] == want


def test_partial_is_indeterminate():
    assert F.analyze(_rows((0, 2, 0), n=24))["outcome"] == "INDETERMINATE"


def test_envelope():
    env = dict(F.ENVELOPE)
    assert EV.validate(env) == [] and EN.admission_reasons(env) == []
    assert env["evidence_class"] == "OBSERVATION" and env["runs_total"] == 32
    assert not set(F.RUN_SEEDS) & set(F.H.RUN_SEEDS)
    assert EV.check_rows([{"status": F.STATUS[c]} for c in F.CELLS]) == []
