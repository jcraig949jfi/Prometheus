"""D-R8-2: the sweep decision, binding, derived response variables and I1 (the runs are the job's)."""
import json

from primordial.cohorts.d import r8_2_ap02_beta_sweep as D
from primordial.fabric import envelope as EV

KEYS = [(f, rs) for f in D.FAMILIES for rs in range(8)]


def row(held, fbytes, nk=2_000_000.0, sha="a", fit=1):
    return {"held_per_landscape_top1": float(held), "top1_program": {"functional_bytes": fbytes, "code_len": 8, "d": 1},
            "train_nk_per_landscape_top1": nk, "top1_sha256": sha, "train_fit_top1": fit}


def point(held, fbytes):
    return {k: row(held(i) if callable(held) else held, fbytes(i) if callable(fbytes) else fbytes)
            for i, k in enumerate(KEYS)}


def sweep(held_by_m, fb_by_m, ctrl_held=100.0):
    pts = {"control": point(lambda i: ctrl_held + (i % 4), 5)}
    for m in D.MULTS:
        pts[D.key(m)] = point(held_by_m.get(m, ctrl_held + 1), fb_by_m.get(m, 5))
    return pts


def test_order_and_size():
    assert D.todo()[0] == ("control", 4200, 0) and len(D.todo()) == 192
    assert [D.key(p) for p in D.ORDER] == ["control", "m1", "m0", "m4", "m16", "m64"]


def test_derived_response_variables():
    d = D.derived(row(1, 6, nk=1_000_000.0), 169144)
    assert d["avoidable_paid"] == 1.0 and d["fb_over_max"] == 1.0 and d["charge_paid"] == 6 * 169144
    assert abs(d["charge_share"] - 169144 * 6 / 8_000_000) < 1e-12
    assert D.derived(row(1, 3), 0)["avoidable_paid"] == 0.0 and D.derived(row(1, 3), 0)["charge_share"] == 0.0


def test_parity_survives_binding():
    got, st = D.decide(True, True, sweep({}, {0: 5, 1: 5, 4: 4, 16: 3, 64: 3}))
    assert got == "PARITY_SURVIVES_BINDING" and st["bound"]["m64"] and not st["non_monotone"]


def test_parity_breaks_at_first_failing_bound_point():
    got, st = D.decide(True, True, sweep({16: 50.0, 64: 40.0}, {0: 5, 4: 4, 16: 3, 64: 3}))
    assert got == "PARITY_BREAKS" and st["m_break"] == 16 and st["beta_break"] == 16 * 169144
    assert st["beta_last_pass_below"] == 4 * 169144


def test_break_where_charge_does_not_bind_is_mixed():
    got, _ = D.decide(True, True, sweep({4: 50.0}, {0: 5, 4: 5, 16: 3, 64: 3}))
    assert got == "MIXED"


def test_charge_never_binds():
    assert D.decide(True, True, sweep({}, {0: 3, 1: 3, 4: 3, 16: 3, 64: 3}))[0] == "CHARGE_NEVER_BINDS"
    few = lambda i: 3 if i < 20 else 5                      # 20 smaller pairs < 24
    assert D.decide(True, True, sweep({}, {0: 5, 64: few}))[0] == "CHARGE_NEVER_BINDS"


def test_null_arm_failure_and_instrument_failures_are_indeterminate():
    got, st = D.decide(True, True, sweep({0: 50.0}, {0: 5, 64: 3}))
    assert got == "INDETERMINATE" and st["null_arm"] == "FAILED"
    ok = sweep({}, {0: 5, 64: 3})
    assert D.decide(False, True, ok)[0] == "INDETERMINATE" and D.decide(True, False, ok)[0] == "INDETERMINATE"
    ok.pop("m16")
    assert D.decide(True, True, ok)[0] == "INDETERMINATE"


def test_non_monotone_is_reported_not_relabelled():
    got, st = D.decide(True, True, sweep({4: 50.0}, {0: 5, 4: 3, 16: 3, 64: 3}))
    assert got == "PARITY_BREAKS" and st["m_break"] == 4 and st["non_monotone"]


def test_i1_requires_exact_reproduction_of_c():
    pts = {"control": {k: row(1.5, 5, sha=f"c{k}") for k in KEYS}, "m1": {k: row(2.5, 4, sha=f"x{k}") for k in KEYS}}
    ref = {("control", f, rs): row(1.5, 5, sha=f"c{(f, rs)}") for f, rs in KEYS}
    ref.update({("cell", f, rs): row(2.5, 4, sha=f"x{(f, rs)}") for f, rs in KEYS})
    assert D.i1_check(pts, ref, 169144)["ok"]
    assert not D.i1_check(pts, ref, 169145)["ok"]
    ref[("cell", 4200, 3)] = row(2.5000001, 4, sha=f"x{(4200, 3)}")
    out = D.i1_check(pts, ref, 169144)
    assert not out["ok"] and out["mismatched"] == [["cell", 4200, 3]]


def test_c_reference_reads_only_completed_glen8_runs():
    text = "\n".join(json.dumps(x) for x in (
        {"kind": "reference", "status": "control"},
        {"kind": "run", "arm": "cell", "family": 4200, "run_seed": 0, "genome_bytes": 6, "held_per_landscape_top1": 0},
        {"kind": "run", "arm": "cell", "family": 4200, "run_seed": 0, "genome_bytes": 8, "held_per_landscape_top1": 9}))
    ref = D.c_reference(text)
    assert list(ref) == [("cell", 4200, 0)] and ref[("cell", 4200, 0)]["held_per_landscape_top1"] == 9


def test_verdict_of_is_withheld_when_unclean():
    st = {"parity": {"m4": False, "m1": True}}
    assert D.verdict_of(st, "m4", True) == "FAIL" and D.verdict_of(st, "m1", True) == "PASS"
    assert D.verdict_of(st, "m4", False) is None and D.verdict_of(st, "control", True) is None


def test_emitted_statuses_are_in_the_row_vocabulary():
    import inspect
    assert inspect.signature(D.job).parameters["status"].default in EV.ROW_STATUSES
    assert "control" in EV.ROW_STATUSES
