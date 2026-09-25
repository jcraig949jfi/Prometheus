"""D-R6-10: decision rule, exact CI and world construction (evolution and branch points are the job's, after the predicate)."""
import numpy as np

from primordial.cohorts.d import r6_10_fakefit_null_exceedance as D


def test_decide():
    assert D.decide(True, 0) == "NULL_HOLDS"
    assert D.decide(True, 1) == "RARE" and D.decide(True, 2) == "RARE"
    assert D.decide(True, 3) == "CHEAT_LEAKS" and D.decide(True, 10) == "CHEAT_LEAKS"
    assert D.decide(False, 0) == "INDETERMINATE"


def test_clopper_pearson_known_values():
    lo, hi = D.clopper_pearson(0, 10)
    assert lo == 0.0 and abs(hi - 0.3084971) < 1e-4
    lo, hi = D.clopper_pearson(1, 10)
    assert abs(lo - 0.0025285) < 1e-4 and abs(hi - 0.4450161) < 1e-4
    lo, hi = D.clopper_pearson(10, 10)
    assert hi == 1.0 and abs(lo - 0.6915029) < 1e-4


def test_worlds_include_e2b_nulls_and_are_deterministic():
    a, b = D.worlds(), D.worlds()
    assert len(a) == 101 and "held25" in a and "null99" in a
    assert all(np.array_equal(a[k].table, b[k].table) for k in ("held25", "null0", "null19", "null99"))
