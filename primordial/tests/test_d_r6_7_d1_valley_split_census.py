"""D-R6-7: decision rule and census sanity on hand codes (the trapped-code census is the job's, after the predicate)."""
import numpy as np

from primordial.cohorts.d import r6_7_d1_valley_split_census as D
from primordial.lingua import signal as S


def test_decide():
    assert D.decide(True, True, 0.9, 0.0) == "SAMPLING_MISS"
    assert D.decide(True, True, 0.1, 0.9) == "MASS_BARRIER"
    assert D.decide(True, True, 0.0, 0.1) == "DEEPER_VALLEY"
    assert D.decide(True, True, 0.5, 0.5) == "MIXED"
    assert D.decide(False, True, 0.1, 0.9) == "INDETERMINATE"
    assert D.decide(True, False, 0.1, 0.9) == "INDETERMINATE"


def test_subsets_skip_empty_and_whole_group():
    enc = np.zeros(S.N_R, np.int64)
    subs = D.subsets(enc)
    assert all(0 < m.sum() < S.N_R for _, _, m in subs)
    assert sum(f == "one_bit" for f, _, _ in subs) == 16 and sum(f == "three_bit" for f, _, _ in subs) == 56 * 8


def test_census_finds_bucket_symbol_on_a_code_one_symbol_short_at_alpha0():
    k, enc, dec = S.hand_code(1)                       # silence everywhere; at alpha 0, beta 0 a new bucket symbol pays
    got = D.census(k, enc, dec, 0.0, 0.0)
    assert got["three_bit"]["improving"] >= 1 and got["three_bit"]["best_delta"] < 0


def test_census_on_analytic_optimum_has_no_improving_move():
    for a, b in D.CELLS:
        m, c_opt = S.analytic_optimum(a, b, D.DELTA)
        k, enc, dec = S.hand_code(m)
        got = D.census(k, enc, dec, a, b)
        assert abs(got["cost"] - c_opt) < 1e-12
        assert got["one_bit"]["improving"] == 0 and got["three_bit"]["improving"] == 0
