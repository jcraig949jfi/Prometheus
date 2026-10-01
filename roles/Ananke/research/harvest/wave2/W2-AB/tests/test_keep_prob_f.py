"""W2-AB regression test: the C2 replication gate keep = Phi(d / (sqrt2 * f)) with f = 1.12 (W2-N) must be
expressible in prometheus.ananke.inference. FAILS on current code (no f argument); PASSES on the patched copy.
Neutrality: with the default f = 1 every value equals the original function.
Module under test: env W2AB_INF (path to an inference.py); default = the repo module."""
import importlib.util, math, os, pathlib
import numpy as np
import pytest
from scipy import stats as st

ROOT = pathlib.Path(__file__).resolve().parents[7]
TARGET = os.environ.get("W2AB_INF", str(ROOT / "prometheus" / "ananke" / "inference.py"))


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


inf = _load(TARGET, "inf_under_test")
orig = _load(str(ROOT / "prometheus" / "ananke" / "inference.py"), "inf_repo")


def test_keep_prob_accepts_f_and_matches_closed_form():
    d = np.array([0.0, 1.0, 2.33, 2.605, 3.0])
    for f in (1.0, 1.12):
        got = inf.keep_prob(d, f=f)
        want = st.norm.cdf(d / (math.sqrt(2) * f))
        assert np.allclose(got, want, atol=1e-12)


def test_margin_for_keep_f112_is_2p605():
    assert abs(inf.margin_for_keep(0.95, f=1.12) - 2.6052) < 1e-3
    assert abs(inf.margin_for_keep(0.95) - 2.3262) < 1e-3


def test_replication_gate_f_changes_status_in_the_2p33_to_2p6_band():
    # stat 2.45 SE beyond the cut: REPLICABLE at f = 1, FRAGILE at f = 1.12 (must-fail direction exercised)
    g1 = inf.replication_gate(0.55 + 2.45 * 0.01, 0.01, 0.55, f=1.0)
    g2 = inf.replication_gate(0.55 + 2.45 * 0.01, 0.01, 0.55, f=1.12)
    assert g1["status"] == "REPLICABLE" and g2["status"] == "FRAGILE"


def test_default_f_reproduces_repo_values():
    d = np.linspace(-4, 4, 33)
    for mode in ("predictive", "plugin"):
        assert np.allclose(inf.keep_prob(d, mode=mode), orig.keep_prob(d, mode=mode), atol=0)
    assert inf.margin_for_keep(0.99) == orig.margin_for_keep(0.99)
    a = inf.replication_gate(0.6, 0.02, 0.55); b = orig.replication_gate(0.6, 0.02, 0.55)
    assert a["keep"] == b["keep"] and a["status"] == b["status"]


def test_f_must_be_positive():
    with pytest.raises((ValueError, TypeError)):
        inf.keep_prob(1.0, f=0.0)
