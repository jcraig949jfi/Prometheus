"""(4) Control competence: identity audit. Core only (no PTE import).

POSITIVE example (the audit must flag): zero_comm on a mirror-pair RELAY-like task whose actuator is not the
sensor. Exactly the PTE structure: partners share every exogenous draw, so with no delivery the actuator's
output is identical in both partners while the targets are negated -> every pair mean is exactly 1/2.
NEGATIVE example (the audit must pass): zero_comm on a HOLD-like task whose actuator IS the sensor, where a
local latch solves without communication, so the control can come out either way.
"""
from __future__ import annotations

import numpy as np

from prometheus.explib.controls import (COMPETENT, FORCED, NO_OP, data_identity, identity_audit, mirror_identity,
                             relation_audit)
from prometheus.explib.outcomes import FAIL, PASS
from prometheus.explib.toys import ToyRing, pair_means, unit_scores

T_READ = 20


def run(e: ToyRing, iv=None, t_read=T_READ):
    w = e.make("A")
    for t in range(t_read + 1):
        e.step(w, t)
        if iv and t in iv:
            e.intervene(w, iv[t], t)
    return w.s[:, e.ro].copy()


def panel(ro, specs, zero_comm):
    out = {}
    for name, kw in specs.items():
        e = ToyRing(T=40, ro=ro, zero_comm=zero_comm, N=6, **kw)
        r = run(e)
        out[name] = (r, e.y, float(pair_means(unit_scores(r, e.y)).mean()))
    return out


RELAY_SPECS = {"relay_d2": {"mode": "relay", "delay": 2}, "relay_d1": {"mode": "relay", "delay": 1},
               "relay_slow": {"mode": "relay", "delay": 8}, "null": {"mode": "null"},
               "null_const": {"mode": "null", "init_const": True}}
HOLD_SPECS = {"latch": {"mode": "latch"}, "loop": {"mode": "loop", "delay": 1},
              "null": {"mode": "null"}}


def audit(ro, specs, witness):
    treat = panel(ro, specs, zero_comm=False)
    ctrl = panel(ro, specs, zero_comm=True)
    raw = {k: (ctrl[k][0], treat[k][0], ctrl[k][1]) for k in specs}
    rule = lambda acc: acc <= 0.55                                   # C1: zero_comm acc <= .55 supports COMM
    wit = {w: panel(ro, {w: kw}, zero_comm=True)[w][2] for w, kw in witness.items()}
    return identity_audit(control_stats={k: v[2] for k, v in ctrl.items()},
                          treatment_stats={k: v[2] for k, v in treat.items()},
                          raw=raw, rule=rule, witness_stats=wit), treat, ctrl


def test_positive_zero_comm_is_forced_on_mirror_relay():
    """HISTORICAL (C1 COMM_DEPENDENT / CAUSAL_SUPPORT): zero_comm was counted as evidence although it is
    exactly .500 in every comm-family row. The audit flags it FORCED: constant across a panel whose
    treatment accuracy spans .5 .. 1, mirror identity in every specimen, and no witness can make it fail
    (a local latch read at the actuator is still exactly .5)."""
    r, treat, ctrl = audit(3, RELAY_SPECS, witness={"latch_at_sensor": {"mode": "latch"}})
    assert {k: v[2] for k, v in ctrl.items()} == {k: 0.5 for k in RELAY_SPECS}
    assert max(v[2] for v in treat.values()) == 1.0
    by = {c["name"]: c["outcome"] for c in r["checks"]}
    assert by["A2_not_constant"] == FAIL and by["A3_no_design_identity"] == FAIL and by["A4_can_fail"] == FAIL
    assert r["verdict"] == FORCED and not r["evidence_admissible"]


def test_negative_zero_comm_is_competent_on_hold_with_local_witness():
    r, treat, ctrl = audit(0, {"loop": HOLD_SPECS["loop"], "null": HOLD_SPECS["null"],
                               "latch": HOLD_SPECS["latch"]}, witness={"latch": {"mode": "latch"}})
    assert ctrl["latch"][2] == 1.0 and ctrl["loop"][2] == 0.5
    assert r["verdict"] == COMPETENT and r["evidence_admissible"], r["checks"]


def test_mirror_identity_and_no_op_directly():
    y = np.array([1, -1, -1, 1])
    assert mirror_identity(np.array([3, 3, -2, -2]), y).outcome == FAIL          # forced 1/2
    assert mirror_identity(np.array([3, -3, -2, 2]), y).outcome == PASS          # cue-following: not forced
    same = np.array([1, 1, 1, 1])
    r = identity_audit(control_stats={"a": 0.9, "b": 0.6}, treatment_stats={"a": 0.9, "b": 0.6},
                       raw={"a": (same, same, np.array([1, 1, -1, -1]))})
    assert r["verdict"] == NO_OP                                                 # control == treatment


def site_chan(e: ToyRing, t_sw=9):
    s_site = pair_means(unit_scores(run(e, {t_sw: "swap_site"}), e.y))
    s_chan = pair_means(unit_scores(run(e, {t_sw: "swap_chan"}), e.y))
    return {"site": s_site, "chan": s_chan}


def test_relation_audit_site_plus_channel_is_forced_W_M():
    """HISTORICAL (W-M): site_acc + chan_acc = 1 is forced by the mirror design, not a finding. Swapping all
    node arrays of b gives (site_p, chan_b); swapping all channels of p gives the same state, so the two
    readouts coincide while targets are negated. The audit calls it FORCED (it holds on specimens with no
    mechanism at all); "site swap FLIPs" is INFORMATIVE (it fails on both null sets)."""
    instrument = lambda kw: site_chan(ToyRing(T=40, N=6, ro=kw.get("ro", 3), **{k: v for k, v in kw.items() if k != "ro"}))
    nulls = {"no_write": [{"mode": "null"}], "constant": [{"mode": "null", "init_const": True}],
             "late": [{"mode": "relay", "delay": 8}]}
    observed = [{"mode": "relay"}, {"mode": "latch", "ro": 0}, {"mode": "loop", "ro": 0, "delay": 1}]
    forced = relation_audit(lambda o: bool(np.allclose(o["site"] + o["chan"], 1.0)), instrument, nulls, observed)
    flip = relation_audit(lambda o: bool((o["site"] <= 0.4).all()), instrument, nulls, observed)
    assert forced["verdict"] == FORCED and forced["observed_rate"] == 1.0
    assert flip["verdict"] == "INFORMATIVE"
    # observation-level screen on the same outputs
    arrays = {str(k): (o["site"], o["chan"]) for k, o in ((str(x), instrument(x)) for x in observed)}
    assert data_identity(arrays, lambda a, b: np.isclose(a + b, 1.0))["flag"] == "IDENTITY_SUSPECTED"
