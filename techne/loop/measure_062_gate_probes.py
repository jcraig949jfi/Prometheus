"""Cycle 062, experiments A and B: probe and mutation-test the promotion gate itself.

THE REVIEWER'S RULE, ADOPTED: *no global claim about a gate from a single outcome class.* Cycle
060 inferred that `Claim.promotable()` was toothless from observing only ACCEPTED examples --
eight claims, all promotable, zero negative controls. One negative control would have killed the
claim on the spot. This script is that control, run late.

FREEZE COMPLIANCE. `techne/lib/claim_record.py` is a frozen control. Nothing here modifies it.
Experiment A calls the real `promotable()`. Experiment B mutates COPIES of a valid record and
calls the real `promotable()` on each. Measuring a control is not modifying it.

    python techne/loop/measure_062_gate_probes.py
"""
from __future__ import annotations

import copy
import dataclasses
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from techne.lib.claim_record import (Adjudication, Adjudicator, Claim,  # noqa: E402
                                     MeasurementContract, Population)

DEST = REPO / "techne" / "loop" / "rung_notes" / "cycle_062_gate_probes.json"


def _pop(pid="P1", method="full-scan", rows=100):
    return Population(population_id=pid, source="synthetic", row_count=rows,
                      selection_predicate="every row", sampling_method=method)


def _valid() -> Claim:
    """A claim that SHOULD be promotable: matched contract, command, counterfactual, oracle."""
    return Claim(
        claim_id="PROBE-valid",
        proposition="a synthetic proposition with no positional sampling",
        question="synthetic",
        population=_pop(),
        contract=MeasurementContract(numerator_predicate="n", denominator_predicate="d",
                                     population_id="P1"),
        measurement_command="python -c pass",
        value=1,
        adjudications=[Adjudication(kind=Adjudicator.KNOWN_ANSWER_CONTROL, detail="oracle",
                                    passed=True, independent_of_generator=True)],
        counterfactual="changing X must move this number",
    )


# ---------------------------------------------------------------------------------------
# EXPERIMENT A -- boundary coverage. Five cases fixed in the pre-registration.
# ---------------------------------------------------------------------------------------

def experiment_a() -> dict:
    cases = []

    c = _valid()
    cases.append(("a_valid_independent_known_answer", c, "ACCEPT"))

    c = _valid(); c.claim_id = "PROBE-dependent"
    c.adjudications = [dataclasses.replace(c.adjudications[0], independent_of_generator=False)]
    cases.append(("b_same_claim_but_adjudication_not_independent", c, "REJECT"))

    c = _valid(); c.claim_id = "PROBE-none"; c.adjudications = []
    cases.append(("c_no_adjudication_at_all", c, "REJECT"))

    c = _valid(); c.claim_id = "PROBE-weak"
    c.adjudications = [dataclasses.replace(c.adjudications[0],
                                           kind=Adjudicator.DIFFERENTIAL_TEST)]
    cases.append(("d_independent_but_below_required_strength", c, "REJECT"))

    c = _valid(); c.claim_id = "PROBE-mismatch"
    c.contract = MeasurementContract(numerator_predicate="n", denominator_predicate="d",
                                     population_id="SOMETHING-ELSE")
    cases.append(("e_contract_population_does_not_match_declared", c, "REJECT"))

    rows, correct = [], 0
    for name, claim, expected in cases:
        ok, why = claim.promotable()
        got = "ACCEPT" if ok else "REJECT"
        agree = got == expected
        correct += agree
        rows.append({"case": name, "expected": expected, "got": got,
                     "discriminated_correctly": agree, "reason": why})
    return {
        "n_cases": len(cases),
        "accepted": sum(1 for r in rows if r["got"] == "ACCEPT"),
        "rejected": sum(1 for r in rows if r["got"] == "REJECT"),
        "correct": correct,
        "both_outcome_classes_present": len({r["got"] for r in rows}) == 2,
        "rows": rows,
    }


# ---------------------------------------------------------------------------------------
# EXPERIMENT B -- mutation assay. Does the gate see EPISTEMIC corruption?
# ---------------------------------------------------------------------------------------

def _mutations():
    """(family, mutator, whether a correct epistemic gate SHOULD change its verdict).

    `should_change` is my judgement, declared here rather than inferred from the result, so
    'the gate is insensitive' cannot later be softened into 'that mutation did not matter'.
    """
    def m_independence(c):
        c.adjudications = [dataclasses.replace(c.adjudications[0],
                                               independent_of_generator=False)]

    def m_strength(c):
        c.adjudications = [dataclasses.replace(c.adjudications[0],
                                               kind=Adjudicator.SAME_MODEL_AUDIT)]

    def m_population_id(c):
        c.contract = MeasurementContract(numerator_predicate="n", denominator_predicate="d",
                                         population_id="WRONG")

    def m_row_count(c):
        c.population = _pop(rows=1)                       # 100 rows claimed, 1 measured

    def m_sampling(c):
        c.population = _pop(method="first-40-ordered")     # undisclosed positional sample

    def m_command(c):
        c.measurement_command = ""

    def m_value(c):
        c.value = 999999                                   # the NUMBER is now wrong

    def m_counterfactual(c):
        c.counterfactual = None

    return [
        ("adjudicator_independence_flag", m_independence, True),
        ("adjudicator_strength_class", m_strength, True),
        ("population_id_vs_contract", m_population_id, True),
        ("declared_row_count", m_row_count, True),
        ("sampling_method_to_undisclosed_positional", m_sampling, True),
        ("measurement_command_emptied", m_command, True),
        ("measured_value_corrupted", m_value, True),
        ("counterfactual_removed", m_counterfactual, True),
    ]


def experiment_b() -> dict:
    base = _valid()
    base_ok, _ = base.promotable()
    rows = []
    for family, mutate, should_change in _mutations():
        c = copy.deepcopy(base)
        mutate(c)
        ok, why = c.promotable()
        changed = ok != base_ok
        rows.append({
            "family": family,
            "baseline_decision": "ACCEPT" if base_ok else "REJECT",
            "mutated_decision": "ACCEPT" if ok else "REJECT",
            "decision_changed": changed,
            "should_have_changed": should_change,
            "SURVIVED_UNDETECTED": bool(should_change and not changed),
            "reason": why,
        })
    undetected = [r["family"] for r in rows if r["SURVIVED_UNDETECTED"]]
    return {
        "baseline_promotable": base_ok,
        "n_families": len(rows),
        "detected": sum(1 for r in rows if r["decision_changed"]),
        "survived_undetected": len(undetected),
        "undetected_families": undetected,
        "epistemic_mutation_sensitivity": round(
            sum(1 for r in rows if r["decision_changed"]) / len(rows), 4),
        "rows": rows,
    }


def main() -> int:
    a, b = experiment_a(), experiment_b()
    out = {
        "population": ("EXPERIMENT A: the 5 boundary cases fixed in the cycle-062 "
                       "pre-registration, complete. EXPERIMENT B: the 8 mutation families fixed "
                       "in the same pre-registration, complete. No sampling in either."),
        "command": "python techne/loop/measure_062_gate_probes.py",
        "freeze_note": ("techne/lib/claim_record.py is UNMODIFIED; experiment B mutates deep "
                        "copies of a synthetic record and calls the real promotable()"),
        "experiment_a_boundary_coverage": a,
        "experiment_b_mutation_assay": b,
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({
        "A_correct": f"{a['correct']}/{a['n_cases']}",
        "A_accepted": a["accepted"], "A_rejected": a["rejected"],
        "A_both_classes": a["both_outcome_classes_present"],
        "B_sensitivity": b["epistemic_mutation_sensitivity"],
        "B_survived_undetected": b["undetected_families"],
    }, indent=2))
    for r in a["rows"]:
        print(f"  A {'OK ' if r['discriminated_correctly'] else 'BAD'} {r['case']:52s} -> {r['got']}")
    for r in b["rows"]:
        flag = "UNDETECTED" if r["SURVIVED_UNDETECTED"] else "caught    "
        print(f"  B {flag} {r['family']:44s} -> {r['mutated_decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
