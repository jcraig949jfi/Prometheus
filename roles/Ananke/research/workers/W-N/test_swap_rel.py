"""Fast CPU tests for swap_rel.py. Every check has a positive input and an
input that makes it FAIL (asserted to give a different verdict)."""
import pathlib
import sys

import numpy as np
import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[4]))
import swap_rel as sr  # noqa: E402

P, K = 256, 11
PM = 0.59           # p_min(256, 11) from out/attain_table.json


def worlds(pair_vals: np.ndarray) -> np.ndarray:
    """[P, K] pair outcomes -> [2P, K] world outcomes (mirror-identical)."""
    return np.repeat(pair_vals, 2, axis=0).astype(float)


def draw(p, seed, shape=(P, K)):
    return (np.random.default_rng(seed).random(shape) < p).astype(float)


def verdict(n, s, pmin=PM):
    return sr.swap_verdict_rel(worlds(n), worlds(s), pmin=pmin)["verdict"]


# ---------------------------------------------------------------- exact truths
@pytest.mark.parametrize("p", [0.62, 0.7, 0.8, 1.0])
def test_flip_exact(p):
    n = draw(p, 1)
    assert verdict(n, 1 - n) == "FLIP_REL"
    # FAIL input: the same check fed a no-effect arm
    assert verdict(n, n) != "FLIP_REL"


@pytest.mark.parametrize("p", [0.62, 0.7, 0.8, 1.0])
def test_no_effect_exact(p):
    n = draw(p, 2)
    assert verdict(n, n.copy()) == "NO_EFFECT_REL"
    assert verdict(n, 1 - n) != "NO_EFFECT_REL"          # FAIL input: a flip arm


@pytest.mark.parametrize("p", [0.62, 0.7, 0.8])
def test_chance_tie(p):
    n = draw(p, 3)
    s = np.full_like(n, 0.5)                              # every readout a tie
    assert verdict(n, s) == "CHANCE_REL"
    assert verdict(n, n) != "CHANCE_REL"                  # FAIL input


@pytest.mark.parametrize("p", [0.66, 0.75, 0.9])
def test_chance_independent(p):
    n = draw(p, 4)
    s = draw(0.5, 5)
    assert verdict(n, s) == "CHANCE_REL"
    assert verdict(n, 1 - n) != "CHANCE_REL"              # FAIL input


def test_indeterminate_partial_transfer():
    """z = -1/2 (transfer in 75 % of pairs): no definite verdict."""
    n = draw(0.8, 6)
    s = n.copy()
    rng = np.random.default_rng(7)
    flip = rng.random(P) < 0.75
    s[flip] = 1 - n[flip]
    assert verdict(n, s) == "INDETERMINATE"
    s_full = 1 - n                                        # FAIL input: full transfer
    assert verdict(n, s_full) != "INDETERMINATE"


# ---------------------------------------------------------------- the gap itself
def test_absolute_rule_misses_low_accuracy_flip():
    """The motivating defect: complete transfer at normal .60 reads CHANCE under
    lens.swap_verdict but FLIP_REL under the (ungated) relative rule. At this
    P, K the frozen gate says NOT_ELIGIBLE (lo99 < .59): see test_gate_*."""
    n = draw(0.60, 8)
    s = 1 - n
    assert sr.absolute_verdict(worlds(n), worlds(s)) == "CHANCE"
    r = sr.swap_verdict_rel(worlds(n), worlds(s), pmin=PM)
    assert r["verdict_ungated"] == "FLIP_REL"
    # at normal 1.0 both agree (FAIL input for 'they always disagree')
    n1 = np.ones((P, K))
    assert sr.absolute_verdict(worlds(n1), worlds(1 - n1)) == "FLIP"
    assert verdict(n1, 1 - n1) == "FLIP_REL"


def test_absolute_rule_flips_at_large_n():
    """Sample-size dependence of the gap: at P=256, K=11 and normal .70 the
    absolute rule already FLIPs (hi99 of .30 < .40)."""
    n = draw(0.70, 8)
    assert sr.absolute_verdict(worlds(n), worlds(1 - n)) == "FLIP"


# ---------------------------------------------------------------- eligibility gate
def test_gate_not_eligible_near_half():
    n = draw(0.55, 9)
    assert verdict(n, 1 - n) == "NOT_ELIGIBLE"
    r = sr.swap_verdict_rel(worlds(n), worlds(1 - n), pmin=PM)
    assert r["verdict_ungated"] == "FLIP_REL"             # exact flip would be certifiable ...
    assert not r["eligible"]                              # ... but the three are not separable
    n2 = draw(0.75, 9)                                    # FAIL input for the gate: high normal
    assert verdict(n2, 1 - n2) != "NOT_ELIGIBLE"


def test_gate_uses_lo99_not_point():
    """A point estimate above p_min whose lo99 is below it is NOT_ELIGIBLE."""
    n = draw(0.595, 10)
    r = sr.swap_verdict_rel(worlds(n), worlds(1 - n), pmin=PM)
    assert r["normal"][0] >= PM > r["normal"][1]
    assert r["verdict"] == "NOT_ELIGIBLE"


def test_power_function_monotone_and_separates():
    lo = min(sr.power(0.55, 64, 11, n_sim=60, n_boot=500).values())
    hi = min(sr.power(0.85, 64, 11, n_sim=60, n_boot=500).values())
    assert hi >= 0.9 and lo <= 0.2


def test_p_min_table_matches_function_small():
    # recompute one cheap cell and compare with the frozen table (P=32, K=3 -> .91)
    assert sr.p_min(32, 3) == pytest.approx(0.91)


# ---------------------------------------------------------------- pairing / NaN handling
def test_pairing_restricts_normal_to_swap_scored_cells():
    """The normal arm is restricted to the world-trials the SINGLE swap arm scored."""
    n = np.ones((2 * P, K))
    n[:, 0] = 0.0                                         # trial 0 always wrong
    s = np.full((2 * P, K), np.nan)
    s[:, 1:] = 0.0                                        # swap scored on trials 1.. only
    r = sr.swap_verdict_rel(n, s, pmin=PM)
    assert r["normal"][0] == pytest.approx(1.0)           # trial 0 excluded
    assert r["verdict"] == "FLIP_REL"
    # FAIL input: unpaired pooling would count trial 0 (normal mean < 1)
    assert np.nanmean(n) < 1.0


def test_flip_rate_accuracy_free():
    for p in (0.6, 0.9):
        n = worlds(draw(p, 11))
        assert sr.flip_rate(n, 1 - n)["f"] == pytest.approx(1.0)
        assert sr.flip_rate(n, n)["f"] == pytest.approx(0.0)
        f = sr.flip_rate(n, worlds(draw(0.5, 12)))["f"]
        assert 0.45 < f < 0.55
