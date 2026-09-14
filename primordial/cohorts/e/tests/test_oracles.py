import numpy as np

from primordial.cohorts.e import oracles as O
from primordial.qd import e7_run as E7


def _elites(fam="linear", P=4, seed=0):
    g7 = E7.G7(4, fam)
    return g7, g7.init(np.random.default_rng(seed), P)


def test_honest_clean_and_shift_always_caught():
    g7, g = _elites()
    out = O.brain_oracle_cheats(g7, g, E7.HELD8[:2], rows_per_elite=64)
    assert out["honest"]["mismatched_rows"] == 0 and out["honest"]["clear_rows"] > 0
    assert out["shift_action"]["elites_caught"] == out["elites"]


def test_ablate_top_catches_a_brain_that_ignores_odd_features():
    # the int2 failure mode: odd-feature weights are exactly 0, so skip-odd is invariant
    g7, (p, C) = _elites(P=4, seed=1)
    W, b = p
    W[:, 1::2, :] = 0.0
    W[:, 0::2, :] *= 8.0                                           # a brain that USES its even features
    g = ((W, b), C)
    out = O.brain_oracle_cheats(g7, g, E7.HELD8, rows_per_elite=256)
    assert out["skip_odd"]["mismatched_rows"] == 0                  # the blind cheat, reproduced
    live = out["elites"] - out["input_invariant_elites"]
    assert live > 0 and out["ablate_top"]["elites_caught"] == live
    assert all(f % 2 == 0 for f in out["ablate_top_features"] if f >= 0)


def test_input_invariant_brain_is_flagged_not_passed():
    g7, (p, C) = _elites(P=2, seed=2)
    W, b = p
    W[:] = 0.0
    out = O.brain_oracle_cheats(g7, ((W, b), C), E7.HELD8[:2], rows_per_elite=32)
    assert out["input_invariant_elites"] == 2 and out["ablate_top"]["clear_rows"] == 0
