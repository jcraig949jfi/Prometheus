"""Fast tests for W-X REL5 (DEGEN model + ZW control). Run:
python -m pytest -q -p no:cacheprovider roles/Ananke/research/workers/W-X/test_degen.py"""
import pathlib
import sys

import numpy as np
import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import degen as dg  # noqa: E402


@pytest.mark.parametrize("z,stat", [(-0.5, "DF"), (0.5, "DN")])
@pytest.mark.parametrize("d", [0.5, 0.95])
def test_truth_at_boundary(z, stat, d):
    a, s = dg.simulate_degen(0.95, z, d, 64, 11, 20000, np.random.default_rng(1))
    X = (s - .5) + (a - .5) / 2 if stat == "DF" else (s - .5) - (a - .5) / 2
    assert abs(X.mean()) < 3e-3


def test_deterministic_pairs_are_constant_arms():
    a, s = dg.simulate_degen(0.9, -0.5, 1.0, 32, 11, 500, np.random.default_rng(2))
    assert np.all(a == 1.0) and set(np.unique(s)) <= {0.0, 1.0}
    assert abs((s == 0).mean() - 0.75) < 0.01


def test_seed_reproducible():
    r1 = dg.rng_for(1, 32, 3, .8, .95, -.5)
    r2 = dg.rng_for(1, 32, 3, .8, .95, -.5)
    assert np.array_equal(dg.simulate_degen(.95, -.5, .8, 32, 3, 50, r1)[1],
                          dg.simulate_degen(.95, -.5, .8, 32, 3, 50, r2)[1])


def _near_degenerate(P=32, j=30):
    """j pairs DF=-.25, P-j pairs DF=+.75 (boundary-type data, many all-equal resamples)."""
    X = np.full((1, P), -0.25)
    X[0, j:] = 0.75
    return X


def test_nesting_and_zw_narrower_on_degenerate_data():
    X = _near_degenerate()
    C = dg.s2.boot_counts(32)
    out, share = dg.intervals(X, C, 3)
    assert share[0] > 0.05
    (l0, h0), (l2, h2), (lz, hz) = out["H0"], out["H2"], out["ZW"]
    assert l0[0] <= l2[0] <= h2[0] <= h0[0]
    assert l0[0] <= lz[0] <= hz[0] <= h0[0]
    assert (hz[0] - lz[0]) < (h0[0] - l0[0])


def test_zw_equals_h0_without_degenerate_resamples():
    rng = np.random.default_rng(3)
    X = rng.normal(0, 0.3, (20, 64))
    C = dg.s2.boot_counts(64)
    out, share = dg.intervals(X, C, 11)
    assert np.all(share == 0)
    for c in ("H2", "ZW"):
        assert np.array_equal(out[c][0], out["H0"][0]) and np.array_equal(out[c][1], out["H0"][1])


def test_wilson_known_value():
    lo, hi = dg.wilson(100, 10000)
    assert lo == pytest.approx(0.00774, abs=1e-5) and hi == pytest.approx(0.01291, abs=1e-5)  # hand-computed Wilson, z=2.5758
