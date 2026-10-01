"""(3) State and write-authority tracing; difference is not use. Core only (no PTE import)."""
from __future__ import annotations

from prometheus.explib.authority import (DIFFERENT_UNUSED, NOT_DIFFERENT, UNTESTED, USED, WriteEvent, WriteLedger,
                              carrier_claims, check_authority, component_difference, difference_vs_use)
from prometheus.explib.lockstep import run_lockstep
from prometheus.explib.outcomes import FAIL, PASS
from prometheus.explib.reach import certify
from prometheus.explib.toys import ToyRing

T = 12


def test_dynamic_write_authority_and_declared_map():
    latch = run_lockstep(ToyRing(T=T, mode="latch", cue_twin=True), T).rec.component_causes()
    relay = run_lockstep(ToyRing(T=T, mode="relay", ro=3, cue_twin=True), T).rec.component_causes()
    assert latch["outcome"] == PASS and latch["causes"] == {"s": {"SENSED": 8}, "aux": {"SENSED": 8}}
    assert relay["causes"]["s"].get("TRANSPORTED", 0) > 0 and "UNEXPLAINED" not in relay["causes"]["s"]
    decl = {"s": {"SENSED", "TRANSPORTED"}, "aux": {"SENSED"}}
    assert check_authority(relay["causes"], decl).outcome == PASS
    # MUST-FAIL: the code-only assumption "s is written only by the sensor" is refuted on relay
    bad = check_authority(relay["causes"], {"s": {"SENSED"}, "aux": {"SENSED"}})
    assert bad.outcome == FAIL and bad.detail["violations"][0]["class"] == "TRANSPORTED"
    # NEGATIVE: a component never declared must never start to differ
    assert check_authority(latch["causes"], {"s": {"SENSED"}}).outcome == FAIL


def test_difference_is_not_use_W_Y_Kp0():
    """HISTORICAL (W-Y vs W-V): "readout Kp differs 78-98%" was Kp[0], which never enters the readout. Here
    aux at the readout differs in 100% of twin units and is never read: the paired intervention is ABSORBED,
    so aux is DIFFERENT_UNUSED; s is USED. Only s may be named as a carrier."""
    e = ToyRing(T=T, mode="latch", cue_twin=True)
    rec = run_lockstep(e, T).rec
    U = e.n_units
    frac = {c: float(component_difference(rec, c, [10] * U, [0] * U).mean()) for c in ("s", "aux")}
    assert frac == {"s": 1.0, "aux": 1.0}
    e2 = ToyRing(T=T, mode="latch")
    tests = {"s": certify(e2, T, {6: ("flip_s", 0)}, [10] * U, [0] * U),
             "aux": certify(e2, T, {6: ("add_aux", 0)}, [10] * U, [0] * U)}
    dvu = difference_vs_use(frac, tests)
    assert dvu["s"]["use"] == USED and dvu["aux"]["use"] == DIFFERENT_UNUSED
    assert carrier_claims(dvu) == ["s"]
    # NEGATIVE / MUST-FAIL: without the intervention, a difference is UNTESTED and never a carrier
    untested = difference_vs_use(frac, {"s": tests["s"]})
    assert untested["aux"]["use"] == UNTESTED and carrier_claims(untested) == ["s"]
    assert difference_vs_use({"x": 0.0}, {})["x"]["use"] == NOT_DIFFERENT


def test_write_ledger_who_wrote_and_hijack():
    L = WriteLedger([WriteEvent(1, 0, "site3", 3, "Kp", "TRANSPORTED", owner="site3"),
                     WriteEvent(4, 0, "site2", 3, "Kp", "COMPUTED", owner="site3"),
                     WriteEvent(5, 0, "site3", 3, "S", "SENSED", owner="site3")])
    assert L.who_wrote(0, 3, "Kp", 3).writer == "site3"
    assert L.who_wrote(0, 3, "Kp", 9).writer == "site2"
    assert L.who_wrote(0, 3, "Kp", 0) is None                                # NEGATIVE
    assert [e.t for e in L.foreign_writes()] == [4]                          # executing context != owner
    assert L.authority_map() == {"Kp": {"TRANSPORTED": 1, "COMPUTED": 1}, "S": {"SENSED": 1}}
    try:
        L.add(WriteEvent(2, 0, "site1", 1, "S", "SENSED"))
        raise AssertionError("ledger accepted an out-of-order event")       # MUST-FAIL guard
    except ValueError:
        pass
