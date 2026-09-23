"""D-R6-3: decision rule on synthetic arrays (the per-seed census is the job's, after the predicate)."""
import numpy as np

from primordial.cohorts.d import r6_3_skip_odd_held64_coverage as D

SEEDS = list(range(100, 116))
HELD8 = SEEDS[:8]


def arrays():
    cd = np.zeros((3, 16), bool)
    af = np.zeros((3, 16), np.int64)
    return cd, af


def test_coverage_when_blind_elites_differ_only_outside_held8_with_flips():
    cd, af = arrays()
    cd[0, 10] = cd[1, 12] = cd[2, 3] = True
    af[0, 10] = af[1, 12] = af[2, 3] = 2
    assert D.decide(True, True, cd, af, SEEDS, HELD8)[0] == "COVERAGE"


def test_path_disagree_when_charge_differs_without_any_flip():
    cd, af = arrays()
    cd[0, 10] = cd[1, 12] = True
    af[0, 10] = 1
    got, detail = D.decide(True, True, cd, af, SEEDS, HELD8)
    assert got == "PATH_DISAGREE" and detail["path_disagree"] == [(1, 112)]


def test_not_coverage_when_a_blind_elite_differs_on_held8_or_never():
    cd, af = arrays()
    cd[0, 2] = cd[1, 12] = True
    af[0, 2] = af[1, 12] = 1
    assert D.decide(True, True, cd, af, SEEDS, HELD8)[0] == "NOT_COVERAGE"
    cd, af = arrays()
    cd[0, 10] = True
    af[0, 10] = 1
    assert D.decide(True, True, cd, af, SEEDS, HELD8)[0] == "NOT_COVERAGE"


def test_indeterminate_on_failed_i1_or_control():
    cd, af = arrays()
    assert D.decide(False, True, cd, af, SEEDS, HELD8)[0] == "INDETERMINATE"
    assert D.decide(True, False, cd, af, SEEDS, HELD8)[0] == "INDETERMINATE"
