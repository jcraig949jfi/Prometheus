"""Regression tests for R-MECH F2: the SHARED-FAILURE matrix of Certificates A and B on planted systems.

Agreement alone proves nothing (both test the same contrast in passive worlds). What must hold: where the two
certificates' machinery differs, a planted case built on that difference makes them DISAGREE in the predicted
direction; where nothing differs, they agree.
Measured 2026-10-08 (ubu003): HiddenCarrier A PASSIVE on 5/5 seeds / B FUNCTIONAL; Reservoir rows agree.
XorCue(V=2): B-linear .493, B-rf 1.00, but Certificate A is SEED-UNSTABLE there (F/P/I/P/F over 5 seed x size
settings): a linear actor can reach .75 on XOR by sacrificing one pattern, and whether A's trained readout
lands on that solution depends on its training sample. Recorded as an instrument finding (A's label is a
property of world x training procedure x sample where linear usability is knife-edge); the XOR test below
therefore checks only the decoder-class difference, not A.
"""
import pytest

from prometheus.cosmos.c3.certify import certify
from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.c4.cert_b import b_use
from prometheus.cosmos.c4.planted import HiddenCarrier, Reservoir, XorCue


@pytest.mark.slow
def test_state_dict_completeness_is_not_shared():
    tk = Task(4, 4)
    s = HiddenCarrier(tk)
    for sd in (11, 12):
        assert certify(s, tk, seed=sd, E_train=1000, E_test=1500)["class"] == "PASSIVE"
    assert b_use(s, tk, "linear", E_train=1000, E_test=1000, seed=3)["functional"]


@pytest.mark.slow
def test_decoder_class_changes_usability_on_xor():
    tk = Task(2, 4)
    s = XorCue(tk)
    lin = b_use(s, tk, "linear", E_train=1000, E_test=1000, seed=3)
    rf = b_use(s, tk, "rf", E_train=1000, E_test=1000, seed=3)
    assert lin["acc"] <= 0.80          # the linear ceiling on 2-bit XOR is .75
    assert rf["acc"] >= 0.95 and rf["functional"]


def test_b_never_imports_certificate_a():
    import ast
    from pathlib import Path
    import prometheus.cosmos.c4.cert_b as B
    src = Path(B.__file__).read_text()
    names = {n.module for n in ast.walk(ast.parse(src)) if isinstance(n, ast.ImportFrom)}
    assert not any(m and ("certify" in m or "probe" in m or "c3" in m) for m in names), names


@pytest.mark.slow
def test_clean_reservoir_agrees():
    tk = Task(4, 4)
    s = Reservoir(tk, .9, .3)
    assert certify(s, tk, seed=11, E_train=1000, E_test=1500)["class"] == "FUNCTIONAL"
    assert b_use(s, tk, "linear", seed=3)["functional"]
