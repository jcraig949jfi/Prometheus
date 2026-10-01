"""Tests for hecate/programs/_lib/evaluator_contract.py (DRAFT v3 contract).

Two parts:
1. Synthetic arms driving every branch of evaluate(): each outcome class,
   each precondition, seed independence, exact comparison and tolerance,
   twin/SIMPLE_ALT judged by the treatment rule, never-crash.
2. The metamorphic harness's own mutation operators (hecate/metamorphic/
   harness.py: mutate, extract, judge) applied in-process to a toy world
   evaluated with the contract; every mutation must be detected. A naive
   evaluator run through the same procedure must be caught (the test can fail).

No files are written; no network; no model calls.
"""
import copy
import importlib.util
import os
import random
import sys
from fractions import Fraction

import pytest

from hecate.programs._lib import evaluator_contract as ec

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEEDS = [0, 1, 2, 3, 4]


def _load_harness():
    path = os.path.join(REPO, "hecate", "metamorphic", "harness.py")
    spec = importlib.util.spec_from_file_location("hecate_metamorphic_harness", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod   # dataclasses look the module up while exec runs
    spec.loader.exec_module(mod)
    return mod


H = _load_harness()


def make_spec(stage="evaluation", **over):
    s = {
        "stage": stage,
        "seeds": list(SEEDS),
        "schema": {"score": "number", "floor": "number"},
        "required_arms": list(ec.MANDATORY_ARMS),
        "optional_arms": ["CONTROL"],
        "success_clauses": [
            {"id": "S1", "field": "score", "agg": "mean", "comparison": ">=",
             "threshold": "3/4", "tolerance": "0"},
            {"id": "S2", "field": "floor", "agg": "min", "comparison": ">=",
             "threshold": "1/2", "tolerance": "0"},
        ],
    }
    s.update(over)
    return s


# per-arm (score, floor) base values; a seed-dependent jitter keeps replicates distinct
SIGNAL_WORLD = {"TREATMENT": (0.86, 0.62), "NULL_TWIN": (0.31, 0.20), "CONTROL": (0.22, 0.10),
                "POSITIVE_CONTROL": (0.95, 0.80), "CHEAT": (0.91, 0.70), "SIMPLE_ALT": (0.81, 0.30)}
NULL_WORLD = dict(SIGNAL_WORLD, TREATMENT=(0.55, 0.40))


def make_rows(world, seeds=SEEDS):
    rows = [{"arm": "_META", "note": "run info"}]
    for arm, (sc, fl) in world.items():
        for s in seeds:
            rows.append({"arm": arm, "seed": s, "score": sc + s / 1000, "floor": fl + s / 2000,
                         "raw_digest": f"{arm}-{s}-{(s * 7919) % 104729}"})
    return rows


def ev(rows, spec=None):
    return ec.evaluate(make_spec() if spec is None else spec, rows)


# =========================================================================== outcome branches
def test_signal():
    out = ev(make_rows(SIGNAL_WORLD))
    assert out["outcome"] == "SIGNAL", out["outcome_reason"]
    assert out["positive_control_detected"] and out["cheat_detected"]
    assert out["null_twin_meets_success"] is False
    assert out["simple_alt_meets_success"] is False
    assert out["clauses"]["SIMPLE_ALT"]["S2"]["holds"] is False
    assert set(out["clauses"]) == set(SIGNAL_WORLD)
    v = out["clauses"]["TREATMENT"]["S1"]
    assert Fraction(v["exact"]) == sum(Fraction(0.86 + s / 1000) for s in SEEDS) / 5


def test_null():
    out = ev(make_rows(NULL_WORLD))
    assert out["outcome"] == "NULL"
    assert out["treatment_meets_success"] is False
    assert "S1" in out["outcome_reason"] and "S2" in out["outcome_reason"]


def test_confounded_by_twin():
    out = ev(make_rows(dict(SIGNAL_WORLD, NULL_TWIN=(0.9, 0.9))))
    assert out["outcome"] == "CONFOUNDED" and out["null_twin_meets_success"] is True


def test_confounded_by_simple_alt_L1():
    out = ev(make_rows(dict(SIGNAL_WORLD, SIMPLE_ALT=(0.9, 0.9))))
    assert out["outcome"] == "CONFOUNDED"
    assert "SIMPLE_ALT" in out["outcome_reason"]


def test_simple_alt_passes_while_treatment_fails_is_null_with_anomaly():
    out = ev(make_rows(dict(NULL_WORLD, SIMPLE_ALT=(0.9, 0.9))))
    assert out["outcome"] == "NULL"
    assert any("SIMPLE_ALT" in a for a in out["anomalies"])


def test_pc_miss_is_instrument_fail_at_evaluation():
    out = ev(make_rows(dict(SIGNAL_WORLD, POSITIVE_CONTROL=(0.95, 0.10))))
    assert out["outcome"] == "INSTRUMENT_FAIL"
    assert out["positive_control_detected"] is False
    assert "S2" in out["outcome_reason"]   # L2: every clause run on the PC


def test_pc_miss_is_spec_unattainable_at_pilot():
    out = ev(make_rows(dict(SIGNAL_WORLD, POSITIVE_CONTROL=(0.60, 0.80))), make_spec(stage="pilot"))
    assert out["outcome"] == "SPEC_UNATTAINABLE"


def test_cheat_miss_is_instrument_fail():
    out = ev(make_rows(dict(SIGNAL_WORLD, CHEAT=(0.4, 0.8))))
    assert out["outcome"] == "INSTRUMENT_FAIL" and out["cheat_detected"] is False


def test_outcome_always_in_vocabulary():
    for w in (SIGNAL_WORLD, NULL_WORLD):
        assert ev(make_rows(w))["outcome"] in ec.OUTCOMES


# =========================================================================== preconditions
@pytest.mark.parametrize("arm", list(ec.MANDATORY_ARMS))
def test_missing_required_arm(arm):
    rows = [r for r in make_rows(SIGNAL_WORLD) if r.get("arm") != arm]
    out = ev(rows)
    assert out["outcome"] == "INSTRUMENT_FAIL"
    assert out["positive_control_detected"] is None and out["cheat_detected"] is None
    assert any(arm in p for p in out["preconditions"]["problems"])


def test_optional_control_may_be_absent():
    rows = [r for r in make_rows(SIGNAL_WORLD) if r.get("arm") != "CONTROL"]
    assert ev(rows)["outcome"] == "SIGNAL"


def test_missing_seed():
    rows = [r for r in make_rows(SIGNAL_WORLD) if not (r.get("arm") == "CHEAT" and r.get("seed") == 3)]
    out = ev(rows)
    assert out["outcome"] == "INSTRUMENT_FAIL" and "missing seeds" in out["outcome_reason"]


def test_extra_seed():
    rows = make_rows(SIGNAL_WORLD) + [{"arm": "TREATMENT", "seed": 99, "score": 0.9, "floor": 0.9}]
    out = ev(rows)
    assert out["outcome"] == "INSTRUMENT_FAIL" and "undeclared seeds" in out["outcome_reason"]


def test_two_rows_for_one_seed():
    rows = make_rows(SIGNAL_WORLD)
    rows.append(dict(next(r for r in rows if r.get("arm") == "TREATMENT"), score=0.99))
    out = ev(rows)
    assert out["outcome"] == "INSTRUMENT_FAIL" and "more than one row" in out["outcome_reason"]


def test_row_without_seed_key():
    rows = make_rows(SIGNAL_WORLD)
    del next(r for r in rows if r.get("arm") == "NULL_TWIN")["seed"]
    assert ev(rows)["outcome"] == "INSTRUMENT_FAIL"


def test_schema_field_absent_is_not_a_keyerror():
    rows = make_rows(SIGNAL_WORLD)
    del next(r for r in rows if r.get("arm") == "CHEAT")["floor"]
    out = ev(rows)
    assert out["outcome"] == "INSTRUMENT_FAIL" and "'floor' absent" in out["outcome_reason"]


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), None, "high", [1]])
def test_non_numeric_or_non_finite_value(bad):
    rows = make_rows(SIGNAL_WORLD)
    next(r for r in rows if r.get("arm") == "TREATMENT")["score"] = bad
    assert ev(rows)["outcome"] == "INSTRUMENT_FAIL"


def test_empty_rows_never_pass():
    out = ev([])
    assert out["outcome"] == "INSTRUMENT_FAIL"
    assert out["positive_control_detected"] is None


def test_undeclared_arm_is_noted_not_fatal():
    rows = make_rows(SIGNAL_WORLD) + [{"arm": "EXTRA", "seed": 0, "score": 1}]
    out = ev(rows)
    assert out["outcome"] == "SIGNAL" and any("EXTRA" in n for n in out["notes"])


# =========================================================================== spec validation
@pytest.mark.parametrize("mut, frag", [
    (lambda s: s["success_clauses"][0].pop("tolerance"), "tolerance"),
    (lambda s: s["success_clauses"][0].update(field="ghost"), "shared schema"),
    (lambda s: s["required_arms"].remove("SIMPLE_ALT"), "SIMPLE_ALT"),
    (lambda s: s.update(success_clauses=[]), "success_clauses"),
    (lambda s: s.update(seeds=[]), "seeds"),
    (lambda s: s.update(seeds=[0, 0]), "duplicates"),
    (lambda s: s.update(stage="final"), "stage"),
    (lambda s: s["success_clauses"][0].update(agg="mode"), "agg"),
    (lambda s: s["success_clauses"][0].update(comparison="=="), "comparison"),
    (lambda s: s["success_clauses"][0].update(tolerance="-1/10"), "tolerance"),
    (lambda s: s["success_clauses"][1].update(id="S1"), "duplicate clause"),
    (lambda s: s["schema"].update(seed="number"), "label field"),
])
def test_invalid_spec_is_instrument_fail(mut, frag):
    spec = make_spec()
    mut(spec)
    out = ev(make_rows(SIGNAL_WORLD), spec)
    assert out["outcome"] == "INSTRUMENT_FAIL"
    assert out["outcome_reason"].startswith("spec invalid") and frag in out["outcome_reason"]


def test_never_crashes_on_garbage():
    assert ec.evaluate(None, [])["outcome"] == "INSTRUMENT_FAIL"
    assert ec.evaluate(make_spec(), None)["outcome"] == "INSTRUMENT_FAIL"
    assert ec.evaluate(make_spec(), [1, "x", None])["outcome"] == "INSTRUMENT_FAIL"


def test_load_rows_missing_file_returns_error():
    rows, err = ec.load_rows(os.path.join(REPO, "hecate", "tests", "__no_such_rows__.jsonl"))
    assert rows is None and "cannot read rows" in err
    assert ec.evaluate_file(make_spec(), "__no_such_rows__.jsonl")["outcome"] == "INSTRUMENT_FAIL"


# =========================================================================== seed independence
def test_identical_rows_across_seeds_fail():
    rows = make_rows(SIGNAL_WORLD)
    t0 = next(r for r in rows if r.get("arm") == "TREATMENT" and r["seed"] == 0)
    t1 = next(r for r in rows if r.get("arm") == "TREATMENT" and r["seed"] == 1)
    t1.update({k: v for k, v in t0.items() if k != "seed"})
    out = ev(rows)
    assert out["outcome"] == "INSTRUMENT_FAIL"
    assert any("pseudo-replication" in a for a in out["anomalies"])


def test_single_seed_spec_skips_independence():
    spec = make_spec(seeds=[0])
    assert ev(make_rows(SIGNAL_WORLD, seeds=[0]), spec)["outcome"] == "SIGNAL"


# =========================================================================== exactness
def test_exact_fraction_comparison_and_tolerance():
    v = Fraction(0.1) + Fraction(0.2)          # exact binary value, > 3/10
    assert ec.compare(v, ">=", Fraction(3, 10), Fraction(0))
    assert not ec.compare(v, "<=", Fraction(3, 10), Fraction(0))
    assert ec.compare(v, "<=", Fraction(3, 10), Fraction(1, 10**9))
    # tolerance narrows strict comparisons
    assert not ec.compare(Fraction(1, 2), ">", Fraction(1, 2), Fraction(0))
    assert ec.compare(Fraction(6, 10), ">", Fraction(1, 2), Fraction(1, 20))
    assert not ec.compare(Fraction(52, 100), ">", Fraction(1, 2), Fraction(1, 20))
    assert ec.compare(Fraction(45, 100), "<", Fraction(1, 2), Fraction(1, 50))
    assert not ec.compare(Fraction(49, 100), "<", Fraction(1, 2), Fraction(1, 50))


def test_boundary_value_is_exact_in_evaluate():
    # mean score exactly 3/4 via rational strings: holds for >=, fails for >
    world_rows = make_rows(SIGNAL_WORLD)
    for r in world_rows:
        if r.get("arm") == "TREATMENT":
            r["score"] = "3/4"
    assert ev(world_rows)["clauses"]["TREATMENT"]["S1"]["holds"] is True
    spec = make_spec()
    spec["success_clauses"][0]["comparison"] = ">"
    assert ev(world_rows, spec)["clauses"]["TREATMENT"]["S1"]["holds"] is False


def test_median_and_aggregates():
    xs = [Fraction(v) for v in (3, 1, 2, 10)]
    assert ec.aggregate(xs, "median") == Fraction(5, 2)
    assert ec.aggregate(xs, "mean") == 4
    assert ec.aggregate(xs, "min") == 1 and ec.aggregate(xs, "max") == 10
    with pytest.raises(ec.ContractError):
        ec.aggregate([], "mean")


# =========================================================================== same rule for every arm
@pytest.mark.parametrize("arm", ["NULL_TWIN", "SIMPLE_ALT", "POSITIVE_CONTROL", "CHEAT"])
def test_each_arm_judged_by_treatment_rule(arm):
    """Put an arm's data into the TREATMENT slot: treatment success must equal
    that arm's success flag (no asymmetric twin/cheat rule)."""
    for world in (SIGNAL_WORLD, NULL_WORLD, dict(SIGNAL_WORLD, NULL_TWIN=(0.9, 0.9))):
        base = ev(make_rows(world))
        swapped = ev(make_rows(dict(world, TREATMENT=world[arm])))
        arm_success = all(c["holds"] for c in base["clauses"][arm].values())
        assert swapped["treatment_meets_success"] == arm_success
        assert swapped["clauses"]["TREATMENT"] == base["clauses"][arm]


def test_check_output_name_L10():
    ec.check_output_name("OUTCOME.json", ["rows.jsonl", "spec.json"])
    with pytest.raises(ec.ContractError):
        ec.check_output_name("Rows.JSONL", ["rows.jsonl"])


# =========================================================================== metamorphic harness
GOOD = {"OK", "DETECTED"}
BAD = {"INSENSITIVE", "SILENT", "WRONG", "ASYM", "BLIND", "SHIFTED", "UNDET",
       "CRASH", "CRASH_SCHEMA", "UNTESTABLE", "NA", "TIMEOUT"}
ROLES = {"TREATMENT": "TREATMENT", "NULL_TWIN": "NULL_TWIN", "CONTROL": "CONTROL",
         "POSITIVE_CONTROL": "POSITIVE_CONTROL", "CHEAT": "CHEAT"}


def _as_harness_result(out):
    rec = H.extract(out, "main")
    rec.update(status="OK", wall_s=0.0)
    return rec


def run_mutations(evaluator, rows):
    B = _as_harness_result(evaluator(rows))
    mutated, results = {}, {}
    for m in H.ORDER:
        info = {}
        mutated[m] = H.mutate(m, copy.deepcopy(rows), ROLES, "main",
                              random.Random(f"20260930:toy:{m}"), info=info)
        results[m] = None if mutated[m] is None else _as_harness_result(evaluator(mutated[m]))
    m1 = results.get("M1") or {}
    aux = {"t_success": m1.get("nt"), "row_keys": set().union(*[set(r) for r in rows])}
    labels = {m: H.judge(m, "main", B, results[m], aux) for m in H.ORDER}
    return B, labels, results


def test_harness_order_covers_required_mutations():
    for m in ("M1", "M2", "M3a", "M3b", "M4", "M4c", "M5", "M6"):
        assert m in H.ORDER


def test_metamorphic_signal_world_every_mutation_detected():
    B, labels, results = run_mutations(lambda r: ec.evaluate(make_spec(), r), make_rows(SIGNAL_WORLD))
    assert B["verdict"] == "SIGNAL"
    bad = {m: lab for m, lab in labels.items() if lab[0] not in GOOD}
    assert not bad, bad
    assert results["M6"]["verdict"] == "INSTRUMENT_FAIL"
    assert results["M1"]["verdict"] == "CONFOUNDED" and results["M2"]["verdict"] == "CONFOUNDED"


def test_metamorphic_null_world_no_silent_pass():
    B, labels, results = run_mutations(lambda r: ec.evaluate(make_spec(), r), make_rows(NULL_WORLD))
    assert B["verdict"] == "NULL"
    for m, (lab, note) in labels.items():
        assert lab not in BAD, (m, lab, note)
        # M7 on a NULL world may legitimately stay NULL (harness: UNINF)
        assert lab in GOOD or (m == "M7" and lab == "UNINF"), (m, lab, note)
    for m in ("M4", "M4c", "M6"):
        assert results[m]["cls"] == "INSTR", m


def _naive_evaluator(rows):
    """Negative control: the round-1 pattern (all() over possibly-empty arms,
    no seed-independence check, twin judged on one clause only)."""
    def arm(a):
        return [r for r in rows if r.get("arm") == a]

    def succ(rs):
        return bool(rs) and sum(r["score"] for r in rs) / len(rs) >= 0.75 and min(r["floor"] for r in rs) >= 0.5

    pc = all(r["score"] >= 0.75 and r["floor"] >= 0.5 for r in arm("POSITIVE_CONTROL"))
    ch = all(r["score"] >= 0.75 and r["floor"] >= 0.5 for r in arm("CHEAT"))
    tw = arm("NULL_TWIN")
    nt = bool(tw) and sum(r["score"] for r in tw) / len(tw) >= 0.75
    outcome = ("INSTRUMENT_FAIL" if not (pc and ch) else "CONFOUNDED" if nt
               else "SIGNAL" if succ(arm("TREATMENT")) else "NULL")
    return {"outcome": outcome, "positive_control_detected": pc, "cheat_detected": ch,
            "null_twin_meets_success": nt, "anomalies": []}


def test_metamorphic_procedure_catches_a_naive_evaluator():
    _, labels, _ = run_mutations(_naive_evaluator, make_rows(SIGNAL_WORLD))
    assert labels["M4"][0] == "INSENSITIVE"
    assert labels["M4c"][0] == "INSENSITIVE"
    assert labels["M6"][0] in ("BLIND", "SHIFTED")
