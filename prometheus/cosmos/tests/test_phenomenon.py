"""The certificate reads native observations only; cheat and negative controls."""
import inspect

import numpy as np

from prometheus.cosmos import phenomenon
from prometheus.cosmos.phenomenon import MARGIN, certify


def _obs(sel, log, last, E=500, R=1.0):
    return {m: {"reward": np.full(E, R * v[0]), "cost": np.full(E, v[1])} for m, v in
            (("SEL", sel), ("LOG", log), ("LAST", last))}


def test_certificate_signature_cannot_see_the_spec():
    params = set(inspect.signature(certify).parameters)
    assert params == {"obs", "reward_per_success", "n_boot", "boot_seed"}
    src = inspect.getsource(phenomenon)
    for forbidden in ("coords", "space(", "params[", "bitcost", "ehop", "ccell"):
        assert forbidden not in src.split('"""', 2)[2], forbidden


def test_cheat_control_injected_success_is_observed():
    """Fabricate native observations in which SEL wins by 0.3: the channel must report PAYS."""
    r = certify(_obs((0.9, 0.05), (0.9, 0.35), (0.1, 0.0)), 1.0)
    assert r["verdict"] == "PAYS" and abs(r["margin"] - 0.3) < 1e-9


def test_negative_control_no_advantage_is_quiet():
    r = certify(_obs((0.5, 0.0), (0.5, 0.0), (0.5, 0.0)), 1.0)
    assert r["verdict"] == "QUIET" and r["margin"] == 0.0


def test_margin_is_the_wse_margin_and_unit_free():
    assert MARGIN == 0.10
    a = certify(_obs((0.8, 0.1), (0.8, 0.3), (0.2, 0.0)), 1.0)
    b = certify(_obs((0.8, 1.0), (0.8, 3.0), (0.2, 0.0), R=10.0), 10.0)
    assert abs(a["margin"] - b["margin"]) < 1e-12
