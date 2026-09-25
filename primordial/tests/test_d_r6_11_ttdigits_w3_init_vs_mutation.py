"""D-R6-11: decision rule on synthetic 4 x 4 grids (the grid runs are the job's, after the predicate)."""
import numpy as np

from primordial.cohorts.d import r6_11_ttdigits_w3_init_vs_mutation as D


def test_no_swing():
    H = 80.0 + np.arange(16).reshape(4, 4) * 0.5
    assert D.decide(True, H)[0] == "NO_SWING"


def test_init_dominates():
    H = np.array([[20.0] * 4, [40.0] * 4, [60.0] * 4, [80.0] * 4]) + np.array([0, 1, 0, 1])[None, :]
    got, st = D.decide(True, H)
    assert got == "INIT_DOMINATES" and st["var_init_means"] > 2 * st["var_mut_means"]


def test_mutation_dominates():
    H = np.array([[20.0, 40.0, 60.0, 80.0]] * 4) + np.array([0, 1, 0, 1])[:, None]
    assert D.decide(True, H)[0] == "MUTATION_DOMINATES"


def test_both_and_indeterminate():
    H = np.array([[20.0, 40.0, 60.0, 80.0]] * 4) + np.array([0, 20, 40, 60])[:, None]
    assert D.decide(True, H)[0] == "BOTH"
    assert D.decide(False, H)[0] == "INDETERMINATE"
    assert D.decide(True, H[:3])[0] == "INDETERMINATE"
