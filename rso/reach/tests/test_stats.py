"""Preregistered statistics (RED first). Anchors: values quoted by others before this harness existed."""
from fractions import Fraction

import pytest

from rso.reach import stats


def test_fisher_matches_the_values_quoted_in_the_design_record():
    # Nyx DESIGN_G1_ARCHIVE_ARMS.md s4: 0/24 vs 6/24 p = 0.022; 0/24 vs 3/24 p = 0.234 (two-sided Fisher)
    assert stats.fisher_two_sided(0, 24, 6, 24) == pytest.approx(0.022, abs=0.0006)
    assert stats.fisher_two_sided(0, 24, 3, 24) == pytest.approx(0.234, abs=0.0006)
    # Palamedes digest 02 (1/24 baseline): 8/24 p = 0.023, 7/24 p = 0.048, 6/24 p = 0.097
    assert stats.fisher_two_sided(1, 24, 8, 24) == pytest.approx(0.023, abs=0.0006)
    assert stats.fisher_two_sided(1, 24, 7, 24) == pytest.approx(0.048, abs=0.0006)
    assert stats.fisher_two_sided(1, 24, 6, 24) == pytest.approx(0.097, abs=0.0006)


def test_fisher_is_symmetric_and_bounded():
    assert stats.fisher_two_sided(3, 20, 9, 22) == pytest.approx(stats.fisher_two_sided(9, 22, 3, 20))
    assert stats.fisher_two_sided(5, 24, 5, 24) == pytest.approx(1.0)


def test_stratified_exact_test_with_one_stratum_is_fisher():
    for a, b in [(0, 6), (1, 8), (3, 3), (10, 2)]:
        assert stats.stratified_exact([(a, 24, b, 24)]) == pytest.approx(stats.fisher_two_sided(a, 24, b, 24))


def test_stratified_exact_test_is_exact_on_a_small_enumeration():
    """Two strata, brute force: the p-value equals the conditional probability of tables at most as likely."""
    strata = [(0, 4, 3, 4), (1, 5, 2, 3)]
    assert stats.stratified_exact(strata) == pytest.approx(stats._brute_force_stratified(strata), abs=1e-12)


def test_holm():
    adj = stats.holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.005})
    assert adj == pytest.approx({"a": 0.03, "b": 0.06, "c": 0.06, "d": 0.02})


def test_clopper_pearson_zero_upper_bound():
    # 0/24: one-sided 95% upper bound 1 - 0.05^(1/24) = 0.1172
    assert stats.upper_bound_95(0, 24) == pytest.approx(1 - 0.05 ** (1 / 24), abs=1e-6)
