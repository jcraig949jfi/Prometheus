"""W2-H regression tests for the proposed prometheus/ananke/inference.py.
FAILS on current code (module absent; and test_pair_ci_percentile_undercovers documents the defect the module
addresses), PASSES with patches/inference_w2h.diff applied. CPU, numpy, < 30 s.
Run on a scratch copy:  PYTHONPATH=<W2-H>/scratch python -m pytest -q tests/test_inference_w2h.py"""
import math

import numpy as np
import pytest


def _sim(P, Kw, p, conc, n, rng):
    """heterogeneous mirror pairs, mirror-identical trials (rho = 1): pair mean ~ Binomial(Kw, Beta) / Kw."""
    pi = rng.beta(p * conc, (1 - p) * conc, (n, P))
    return rng.binomial(Kw, pi) / Kw


def _lo_miss(fn, P, p, conc, n=2000, seed=1):
    rng = np.random.default_rng(seed)
    x = _sim(P, 12, p, conc, n, rng)
    _, lo, _ = fn(x)
    return float(np.mean(lo > p))


def test_pair_ci_percentile_undercovers():
    """Characterizes the CURRENT held CI (assays.pair_ci) at the C1 design: one-sided miss of lo99 well above
    the nominal 0.5% for a heterogeneous high-accuracy champion. (A guard that this defect is real.)"""
    from prometheus.ananke import assays
    assert _lo_miss(assays.pair_ci, 32, 0.9, 4.0) > 0.02


def test_student_pair_ci_holds_nominal():
    from prometheus.ananke import inference as I
    for p in (0.55, 0.9):
        assert _lo_miss(I.pair_ci_student, 32, p, 4.0) <= 0.012
    m, lo, hi = I.pair_ci_t(np.array([0.5, 0.6, 0.7, 0.8]))
    assert lo < m < hi


def test_t_interval_matches_formula():
    from prometheus.ananke import inference as I
    x = np.array([0.4, 0.5, 0.75, 0.9, 1.0])
    m, lo, hi = I.pair_ci_t(x, 0.95)
    from scipy import stats
    se = x.std(ddof=1) / math.sqrt(5)
    assert abs(lo - (x.mean() - stats.t.ppf(0.975, 4) * se)) < 1e-12


def test_signal_pvalue_and_degenerate_bound():
    from prometheus.ananke import inference as I
    assert I.signal_pvalue(np.full(32, 1.0)) == pytest.approx(0.55 ** 32)
    assert I.signal_pvalue(np.full(32, 0.5)) == 1.0
    assert I.signal_pvalue(np.r_[np.full(16, 0.6), np.full(16, 0.7)]) < 1e-6


def test_bh_holm_known_answers():
    from prometheus.ananke import inference as I
    p = np.array([0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205, 0.212, 0.216])
    assert I.bh(p, 0.05).sum() == 2          # classic BH example: 0.001, 0.008 rejected
    assert I.holm(p, 0.05).sum() == 1        # 0.001 <= .005, 0.008 > .05/9
    assert I.bh(np.array([]), 0.05).size == 0


def test_keep_prob_and_gate():
    from prometheus.ananke import inference as I
    assert float(I.keep_prob(0.0)) == pytest.approx(0.5)
    assert float(I.keep_prob(1.0)) == pytest.approx(0.7602499, abs=1e-6)
    assert I.margin_for_keep(0.95) == pytest.approx(2.3262, abs=1e-3)
    g = I.replication_gate(0.57, 0.01, 0.55)                 # 2 SE above the cut -> keep .92 -> FRAGILE
    assert g["status"] == "FRAGILE" and g["keep"] == pytest.approx(0.9214, abs=1e-3)
    assert I.replication_gate(0.60, 0.01, 0.55)["status"] == "REPLICABLE"
    assert I.replication_gate(0.30, 0.02, 0.40, side="below")["status"] == "REPLICABLE"


def test_mirror_structure_detects_identical_and_complementary_partners():
    from prometheus.ananke import inference as I
    rng = np.random.default_rng(0)
    A = (rng.random((64, 12)) < 0.7).astype(float)
    same = np.empty((128, 12)); same[0::2] = A; same[1::2] = A          # odd-symmetric program: rho = 1
    comp = np.empty((128, 12)); comp[0::2] = A; comp[1::2] = 1 - A      # input-blind program: rho = -1
    assert I.mirror_structure(same)["mirror_rho"] == pytest.approx(1.0)
    s = I.mirror_structure(comp)
    assert s["mirror_rho"] == pytest.approx(-1.0) and s["K_eff_per_pair"] == float("inf")
