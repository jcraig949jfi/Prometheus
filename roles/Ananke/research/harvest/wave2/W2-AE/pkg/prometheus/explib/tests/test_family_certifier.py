"""(6b) The role-based family certifier (promoted from W2-B attain.py) on engine-free toy rulers, and the analytic
CI-gate eligibility threshold (W2-B known answers). Each verdict has a must-fail twin."""
from __future__ import annotations

import numpy as np
import pytest

from prometheus.explib.attainable import (Cell, Program, Ruler, alias, certify_family, ci_gate_power,
                                          family_checks, min_true_to_cross)
from prometheus.explib.outcomes import FAIL, NOT_VERIFIED, PASS

# A "world" is a dict of per-program true accuracies; a "genome" is the program's name. The measure returns
# exactly that accuracy (pairs: a constant vector), so every verdict is known by construction.
P = 8


def acc_ruler(threshold=0.55, constant=None):
    def measure(ph, env, g, seeds, sched_fn=None):
        v = ph[g] if constant is None else constant
        return {"value": v, "passed": v > threshold, "pairs": np.full(P, v)}
    return Ruler("acc", "competence", measure)


def prog(name, role, lacks=""):
    return Program(name, role, lambda ph, env, n=name: n, lacks)


WORLD = Cell({"null": 0.5, "plant": 0.9, "cheat": 0.76, "probe": 0.6}, None, "w")
NULL, PLANT, CHEAT, PROBE = prog("null", "null"), prog("plant", "plant"), prog("cheat", "adversary", "x"), \
    prog("probe", "probe")


def test_verdicts_known_by_construction():
    assert certify_family(acc_ruler(), [WORLD], [NULL, PLANT], None).verdict == "SOUND"
    ch = certify_family(acc_ruler(), [WORLD], [NULL, PLANT, CHEAT], None)
    assert ch.verdict == "CHEATABLE" and ch.cheapest["program"] == "cheat"
    # the same family with a stricter gate: the cheat no longer crosses -> SOUND (must-fail twin)
    assert certify_family(acc_ruler(0.8), [WORLD], [NULL, PLANT, CHEAT], None).verdict == "SOUND"
    assert certify_family(acc_ruler(0.95), [WORLD], [NULL, PLANT, CHEAT], None).verdict == "UNREACHABLE"
    assert certify_family(acc_ruler(0.95), [WORLD], [NULL, CHEAT], None).verdict == "NO_PLANT"
    assert certify_family(acc_ruler(0.55), [WORLD], [NULL, PROBE], None).verdict == "NO_PLANT"


def test_forced_value_is_degenerate_or_unreachable():
    forced = certify_family(acc_ruler(0.55, constant=0.5), [WORLD], [NULL, PLANT, CHEAT], None)
    assert forced.forced and forced.verdict == "UNREACHABLE" and forced.attainable == (0.5, 0.5)
    always = certify_family(acc_ruler(0.4, constant=0.5), [WORLD], [NULL, PLANT], None)
    assert always.verdict == "DEGENERATE"
    # a single program can never be called forced
    one = certify_family(acc_ruler(), [WORLD], [PLANT], None)
    assert not one.forced and "single program" in " ".join(one.notes)


def test_alias_and_family_checks():
    a = certify_family(acc_ruler(0.55), [WORLD], [NULL, PLANT, CHEAT], None)
    b = certify_family(acc_ruler(0.60), [WORLD], [NULL, PLANT, CHEAT], None)
    c = certify_family(acc_ruler(0.80), [WORLD], [NULL, PLANT, CHEAT], None)
    assert alias(a, b)["identical"] and not alias(a, c)["identical"]
    ck = {x.name: x.outcome for x in family_checks(a)}
    assert ck == {"G1_null": PASS, "G2_adversary": FAIL, "G3_positive": PASS, "A2_not_forced": PASS}
    ck2 = {x.name: x.outcome for x in family_checks(certify_family(acc_ruler(), [WORLD], [PLANT, PROBE], None))}
    assert ck2["G1_null"] == NOT_VERIFIED and ck2["G2_adversary"] == NOT_VERIFIED   # fail-closed


def test_bad_role_and_empty_family_refused():
    with pytest.raises(ValueError):
        Program("x", "champion", lambda ph, env: "x")
    with pytest.raises(ValueError):
        certify_family(acc_ruler(), [WORLD], [Program("na", "plant", lambda ph, env: None)], None)


def test_analytic_gate_eligibility_W2B_known_answers():
    # absolute swap FLIP (hi99 < .40) needs normal well above .60 even with an ideal follow
    n50 = 1 - min_true_to_cross(0.40, 32, 12, "hi_lt", 0.5)
    assert 0.62 < n50 < 0.70
    # SIGNAL needs ~.61 at P32 K12 and less with more pairs (monotone)
    a, b = min_true_to_cross(0.55, 32, 12), min_true_to_cross(0.55, 256, 12)
    assert 0.55 < b < a < 0.65
    # MUST-FAIL: a reader at exactly the .70 ceiling crosses INTEGRATION only ~0.5% of the time
    assert ci_gate_power(0.70, 0.70, 32, 12) < 0.01 < ci_gate_power(0.784, 0.70, 32, 12)
    with pytest.raises(ValueError):
        ci_gate_power(0.7, 0.7, 32, 12, side="lo_ge")
