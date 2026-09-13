"""S5 phase 0: the selection bound is a property of the WORK, deterministic
and interruptible; an expensive selector is cut off, a cheap one is not,
the outcome is explicit, the provenance says what was attempted, and the
mechanism sees no target."""
import inspect
import random

import pytest

from archaeon.producer import acquisition as AQ, fossil_inference as FI, s4_producers as P, work_budget as WB


def _score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def _fossils(t, xs):
    return [FI.Fossil(x, _score(x, t)) for x in xs]


def test_charge_is_a_noop_without_a_budget_and_raises_with_provenance_inside_one():
    WB.charge(10, "x")                                   # no active budget: nothing happens
    with pytest.raises(WB.BudgetExhausted) as e:
        with WB.WorkBudget(5):
            WB.charge(3, "a"); WB.charge(3, "b")
    prov = e.value.provenance
    assert prov["outcome"] == "BUDGET_EXHAUSTED" and prov["units_used"] == 6 and prov["max_units"] == 5 and prov["counters"] == {"a": 3, "b": 3} and prov["phase"] == "b"
    assert WB.active() is None                           # the context is restored after the exception


def test_an_intentionally_expensive_selector_is_cut_off_and_a_cheap_one_is_not():
    rnd = random.Random(1); L = 16; t = "".join(rnd.choice("01") for _ in range(L))
    fs = _fossils(t, ["".join(rnd.choice("01") for _ in range(L)) for _ in range(3)])
    cheap = P.produce_G(fs, {"lane": "t", "world": 1, "step": 1})
    assert cheap.probe is not None and cheap.extra.get("outcome") != "BUDGET_EXHAUSTED"
    tight = P.produce_G(fs, {"lane": "t", "world": 1, "step": 1}, max_units=50)
    assert tight.probe is None and tight.extra["outcome"] == "BUDGET_EXHAUSTED"
    w = tight.extra["work"]
    assert w["units_used"] > w["max_units"] == 50 and w["phase"] in ("infer_dfs_node", "partition_solution_blocks", "probe_scored") and "counters" in w
    # the bound is deterministic: the same call stops at the same unit count in the same phase
    again = P.produce_G(fs, {"lane": "t", "world": 1, "step": 1}, max_units=50)
    assert again.extra["work"]["units_used"] == w["units_used"] and again.extra["work"]["phase"] == w["phase"]
    # W and M honour the same contract
    for fn in (P.produce_W, P.produce_M):
        r = fn(fs, {"lane": "t", "world": 1, "step": 1}, max_units=50)
        assert r.probe is None and r.extra["outcome"] == "BUDGET_EXHAUSTED"


def test_the_budget_bounds_work_not_time_and_reports_wall_separately():
    rnd = random.Random(2); L = 12; t = "".join(rnd.choice("01") for _ in range(L)); fs = _fossils(t, ["".join(rnd.choice("01") for _ in range(L))])
    st = AQ.feasible(fs); pool = [format(n, "012b") for n in range(4096)]        # 4096 probes: expensive by units, fast by clock
    with pytest.raises(WB.BudgetExhausted) as e:
        with WB.WorkBudget(max_units=500):
            AQ.select(st, pool)
    assert e.value.provenance["outcome"] == "BUDGET_EXHAUSTED" and e.value.provenance["elapsed_seconds"] < 30
    with WB.WorkBudget(max_units=10 ** 9) as b:                              # generous: completes, and the units are recorded
        AQ.select(st, pool)
    assert b.units > 4096 and b.counters["probe_scored"] == 4096


def test_no_target_leakage_through_the_budget():
    for fn in (WB.WorkBudget.__init__, WB.charge, P.exhausted, P.produce_G, P.produce_W, P.produce_M):
        assert not any(k in ("target", "hidden_target", "t") for k in inspect.signature(fn).parameters), fn
    rnd = random.Random(3); L = 10; t = "".join(rnd.choice("01") for _ in range(L)); fs = _fossils(t, ["".join(rnd.choice("01") for _ in range(L))])
    r = P.produce_W(fs, {"lane": "t", "world": 2, "step": 1}, max_units=30)
    assert t not in repr(r.extra["work"]) and t not in repr(r.ancestry)


def test_M_has_no_wall_clock_fallback_any_more():
    assert "time_bound_s" not in inspect.signature(P.produce_M).parameters
    rnd = random.Random(4); L = 8; t = "".join(rnd.choice("01") for _ in range(L)); fs = _fossils(t, ["".join(rnd.choice("01") for _ in range(L))])
    ok = P.produce_M(fs, {"lane": "t", "world": 0, "step": 1})
    assert ok.probe is not None and ok.objective_value is not None and "intractable" not in ok.extra
