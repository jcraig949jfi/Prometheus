"""W2-K regression test: three-valued readings + kill eligibility (patches/inference_reading3_w2k.diff).
FAILS on current code (no reading3 / kill_eligible); PASSES with the patch.
Run: PYTHONPATH=scratch python -m pytest -q -p no:cacheprovider tests/   (from W2-K/), or against the repo."""
import pathlib

import numpy as np
import pytest

from prometheus.ananke import inference

# W2-K's saved C1b pair arrays (force-added; roles/**/*.npz is gitignored)
OUT = pathlib.Path(__file__).resolve().parents[3] / "roles/Ananke/research/harvest/wave2/W2-K/out"
if not (OUT / "pairs_m2spec.npz").exists():
    pytest.skip("W2-K pair arrays not present", allow_module_level=True)


def test_api_exists():
    assert hasattr(inference, "reading3") and hasattr(inference, "kill_eligible")


def test_c1b_m2_B_is_indeterminate_not_false():
    """C1b M2 B (reset_all_nonpacket intact, lo99(diff) >= -.10): recorded False at 0.89 SE -> INDETERMINATE."""
    a = np.load(OUT / "pairs_m2spec.npz")
    r = inference.reading3(a["reset_all_nonpacket"] - a["normal"], -0.10, ">=", "lo")
    assert r["raw"] is False
    assert r["status"] == "INDETERMINATE"
    assert -2.33 < r["d_se"] < 0


def test_far_readings_are_definite():
    a = np.load(OUT / "pairs_m2spec.npz")
    assert inference.reading3(a["flush_inflight"], 0.60, "<=", "hi")["status"] == "TRUE"      # A: kills
    assert inference.reading3(a["census_C"], 0.60, ">", "lo")["status"] == "FALSE"            # C: no
    b = np.load(OUT / "pairs_m3_0a23.npz")
    assert inference.reading3(b["freeze_rule"] - b["normal"], -0.10, "<=", "mean")["status"] == "TRUE"


def test_kill_eligibility_guards_low_normal():
    """f6b6 fresh k0's battery normal (.5566 [.5319, .5781] pct) sits below the kill line; a synthetic array with
    that mean/spread must be kill-INELIGIBLE, while the M3 specimen's normal (.69) is eligible."""
    g = np.random.default_rng(0)
    low = np.clip(0.5566 + 0.04 * g.standard_normal(32), 0, 1)
    assert not inference.kill_eligible(low)
    b = np.load(OUT / "pairs_m3_0a23.npz")
    assert inference.kill_eligible(b["normal"])


def test_zero_variance_and_strictness():
    x = np.full(32, 0.5)
    r = inference.reading3(x, 0.60, "<=", "hi")
    assert r["status"] == "TRUE" and r["d_se"] == float("inf")
    r = inference.reading3(x, 0.50, ">", "lo")
    assert r["raw"] is False and r["status"] == "INDETERMINATE" and r["d_se"] == 0.0
    with pytest.raises(KeyError):
        inference.reading3(x, 0.5, "=>", "lo")
