"""(1) Reachability certification: applied is not reached. Core only (no PTE import)."""
from __future__ import annotations

import numpy as np

from prometheus.explib.reach import (ABSORBED, INCONSISTENT, NOT_CERTIFIED, NOT_REACHED, REACHED, UNAPPLIED, applied_ticks,
                          certify, null_admissibility, reach_certificate)
from prometheus.explib.toys import ToyRing
from prometheus.explib.trace import DiffRecord

T, RO_T, RO = 12, 10, 3


def cert(iv, **kw):
    e = ToyRing(mode="relay", ro=RO, T=T, **kw)
    U = e.n_units
    return certify(e, T, iv, [RO_T] * U, [RO] * U)


def test_four_verdicts_with_paths():
    r = {"flush_mid": cert({3: "flush"}), "flip_readout": cert({9: ("flip_s", RO)}),
         "aux_readout": cert({9: ("add_aux", RO)}), "elsewhere": cert({9: ("flip_s_except", RO)}),
         "noop": cert({5: "noop"})}
    assert r["flush_mid"]["verdict"] == REACHED and set(r["flush_mid"]["path"]) == {"TRANSPORTED"}
    assert r["flip_readout"]["verdict"] == REACHED and set(r["flip_readout"]["path"]) == {"LOCAL"}
    assert r["aux_readout"]["verdict"] == ABSORBED and r["aux_readout"]["admissible_null"]
    assert r["elsewhere"]["verdict"] == NOT_REACHED and r["elsewhere"]["applied"] == 1.0
    assert r["noop"]["verdict"] == UNAPPLIED                                           # NEGATIVE
    assert len({v["verdict"] for v in r.values()}) == 4                                 # MUST-FAIL: they differ
    assert all(v["closure"] == "PASS" for v in r.values())


def test_applied_is_not_reached_lens_verify_reach_reading():
    """HISTORICAL (H-INST s4, lens.verify_reach): a whole-run digest count calls an edit 'applied' on every
    tick after it, although the edit never reaches the readout. Same here: applied_ticks > 0 while the
    certificate is NOT_REACHED, and the null is a NON-TEST, not an admissible null."""
    r = cert({9: ("flip_s_except", RO)})
    assert r["applied_ticks_digest_reading"] > 0 and r["verdict"] == NOT_REACHED
    assert null_admissibility(r["verdict"]).startswith("NON_TEST")
    # window miss: the same edit after the readout tick is applied and cannot reach it (W-D 1a, C1 D-A)
    late = cert({RO_T: ("flip_s_except", RO)})
    assert late["verdict"] == NOT_REACHED
    # MUST-FAIL input: an edit that does reach is not NOT_REACHED under the same counting
    assert cert({9: ("flip_s", RO)})["verdict"] == REACHED


def test_negative_verdicts_need_a_closed_tracer():
    """Burden symmetry: when locality is broken (leak), a negative reading is NOT_CERTIFIED, never a null."""
    r = cert({9: ("flip_s_except", RO)}, leak=True)
    assert r["closure"] == "FAIL" and r["verdict"] == NOT_CERTIFIED and r["reading"] in (NOT_REACHED, ABSORBED)
    assert not r["admissible_null"]
    # a positive observation stays certified even with an open tracer
    assert cert({9: ("flip_s", RO)}, leak=True)["verdict"] == REACHED


def test_output_change_without_touch_is_inconsistent():
    """Fail-closed: if the readout changed but the record shows no path, the tracer missed a channel."""
    Tn, U, N = 6, 2, 3
    held = np.zeros((Tn, U, N), bool)
    hook = np.zeros((Tn, U, N), bool)
    hook[1, :, 0] = True
    held[1:, :, 0] = True
    post = held.copy()
    post[1] = False                                   # the difference at t=1 is the hook's write
    rec = DiffRecord(held=held, inp=np.zeros_like(held), arr=np.zeros_like(held),
                     edges=np.zeros((0, 5), int), hook_node=hook, post=post)
    assert rec.closure()["outcome"] == "PASS"
    r = reach_certificate(rec, [4, 4], [2, 2], np.array([1, 1]), np.array([1, -1]))
    assert r["verdict"] == INCONSISTENT and r["counts"]["INCONSISTENT"] == 1
    ok = reach_certificate(rec, [4, 4], [2, 2], np.array([1, 1]), np.array([1, 1]))
    assert ok["verdict"] == NOT_REACHED                                                 # MUST-FAIL twin
    assert applied_ticks(rec) == Tn - 1
