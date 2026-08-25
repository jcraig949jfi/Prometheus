"""Cycle 062's exported claims. Numbers read from the committed row files, never typed."""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from techne.lib.claim_record import (Adjudication, Adjudicator, Claim,  # noqa: E402
                                     MeasurementContract, Population, render)

ROWS = REPO / "techne" / "loop" / "rung_notes"
G = json.loads((ROWS / "cycle_062_gate_probes.json").read_text(encoding="utf-8"))
H = json.loads((ROWS / "cycle_062_hostile_census.json").read_text(encoding="utf-8"))
A, B = G["experiment_a_boundary_coverage"], G["experiment_b_mutation_assay"]

GATE_CMD = "python techne/loop/measure_062_gate_probes.py"
CENSUS_CMD = "python techne/loop/measure_062_hostile_census.py"

BOUNDARY = Population(
    population_id="promotion-gate-boundary",
    source="techne/lib/claim_record.py::Claim.promotable()",
    row_count=A["n_cases"],
    selection_predicate=("the five boundary cases fixed in the cycle-062 pre-registration: "
                         "valid+independent; not-independent; no adjudication; independent but "
                         "below strength; contract/population mismatch"),
    sampling_method="full-scan (all five, fixed before running)")

MUTATION = Population(
    population_id="promotion-gate-mutations",
    source="techne/lib/claim_record.py::Claim.promotable()",
    row_count=B["n_families"],
    selection_predicate=("the eight epistemic mutation families fixed in the cycle-062 "
                         "pre-registration, each applied to a deep copy of one valid claim"),
    sampling_method="full-scan (all eight, fixed before running)")

CENSUS = Population(
    population_id="arsenal-reds-orthogonal",
    source="techne/loop/rung_notes/cycle_061_red_triage.json",
    row_count=H["of_total"],
    selection_predicate="every red node id, re-expressed under seven orthogonal dimensions",
    sampling_method="full-scan")

EXECUTED = Adjudication(
    kind=Adjudicator.KNOWN_ANSWER_CONTROL,
    detail=("each boundary case has a CORRECT answer fixed before the run -- the valid record "
            "must ACCEPT and the four defective ones must REJECT -- and the real, unmodified "
            "promotable() was executed against all five. The expected answers come from the "
            "promotion rule's own stated semantics, not from its output."),
    passed=True, independent_of_generator=True)

MUTATION_ADJ = Adjudication(
    kind=Adjudicator.METAMORPHIC_INVARIANT,
    detail=("the invariant is: corrupting a field the gate claims to depend on MUST flip the "
            "decision. Each family's should_have_changed value was declared in the script "
            "before the run, so an insensitivity cannot afterwards be re-described as 'that "
            "mutation did not matter'."),
    passed=True, independent_of_generator=True)

REVIEWER = Adjudication(
    kind=Adjudicator.HUMAN_REVIEW,
    detail=("the hostile single question and its predicted outcome were specified by an "
            "EXTERNAL reviewer before I ran it, so the framing is not mine and the result "
            "cannot have been shaped to the answer I preferred"),
    passed=True, independent_of_generator=True)


def claims() -> list:
    und = B["undetected_families"]
    sym = H["symptoms_vs_capabilities"]
    return [
        Claim(
            claim_id="C062-1",
            question=("Does the promotion gate discriminate at all? Cycle 060 said no, cycle 061 "
                      "said yes on two accidental examples. Neither ran a negative control."),
            proposition=(
                f"It discriminates perfectly on the boundary. Of {A['n_cases']} synthetic records "
                f"spanning the promotion boundary, {A['correct']} were decided correctly: the one "
                f"valid record was ACCEPTED and all {A['rejected']} defective ones were REJECTED. "
                f"Both outcome classes are present, which is what cycle 060 lacked when it "
                f"declared the gate toothless from eight accepted examples."),
            population=BOUNDARY,
            contract=MeasurementContract(
                numerator_predicate="boundary cases decided as pre-specified",
                denominator_predicate="all 5 boundary cases",
                population_id=BOUNDARY.population_id),
            measurement_command=GATE_CMD,
            value={"correct": A["correct"], "of": A["n_cases"],
                   "accepted": A["accepted"], "rejected": A["rejected"],
                   "both_outcome_classes_present": A["both_outcome_classes_present"]},
            adjudications=[EXECUTED],
            counterfactual=("removing the strength check from MIN_PROMOTABLE must flip case (d) "
                            "from REJECT to ACCEPT"),
            source_artifacts=["techne/loop/rung_notes/cycle_062_gate_probes.json"],
        ),
        Claim(
            claim_id="C062-2",
            question="What KIND of gate is it, then?",
            proposition=(
                f"A PROVENANCE gate, not a truth gate. Under eight epistemic mutations of one "
                f"valid claim it caught {B['detected']} and "
                f"{B['survived_undetected']} survived undetected: {', '.join(und)}. A claim whose "
                f"measured VALUE is corrupted by six orders of magnitude, and one whose declared "
                f"ROW COUNT is off by a factor of a hundred, are both still PROMOTABLE. The rule "
                f"validates how a claim was arrived at and is blind by construction to what it "
                f"says. Sensitivity to epistemic corruption: "
                f"{B['epistemic_mutation_sensitivity']}."),
            population=MUTATION,
            contract=MeasurementContract(
                numerator_predicate="mutation families that flip the promotion decision",
                denominator_predicate="all 8 pre-registered mutation families",
                population_id=MUTATION.population_id),
            measurement_command=GATE_CMD,
            value={"detected": B["detected"], "of": B["n_families"],
                   "sensitivity": B["epistemic_mutation_sensitivity"],
                   "undetected": und},
            adjudications=[MUTATION_ADJ, EXECUTED],
            counterfactual=("adding a value-provenance check -- the number must be re-derivable "
                            "from the recorded command -- must move measured_value_corrupted "
                            "from undetected to detected"),
            caveats=["this supersedes BOTH prior characterisations: cycle 060's 'cannot block "
                     "anything' and cycle 061's 'enforces the bar on honest labels'. The gate "
                     "blocks reliably on epistemic shape and never on content."],
            source_artifacts=["techne/loop/rung_notes/cycle_062_gate_probes.json"],
        ),
        Claim(
            claim_id="C062-3",
            question=("Under a hostile framing I did not author, does 'zero real defects' "
                      "survive?"),
            proposition=(
                f"No. Asked the reviewer's single question -- is something presently false, "
                f"unavailable, non-reproducible or knowingly corrupted in the tested system? -- "
                f"{H['hostile_YES']} of {H['of_total']} red node ids answer YES and "
                f"{H['hostile_NO']} answer NO. The reviewer predicted the zero would explode and "
                f"it explodes completely. The defensible residue of cycle 061's headline is only "
                f"this: zero NEWLY DISCOVERED mathematical-code defects caused these reds."),
            population=CENSUS,
            contract=MeasurementContract(
                numerator_predicate="node ids where something is presently false, unavailable, "
                                    "non-reproducible or knowingly corrupted",
                denominator_predicate="all 47 red node ids",
                population_id=CENSUS.population_id),
            measurement_command=CENSUS_CMD,
            value={"hostile_YES": H["hostile_YES"], "hostile_NO": H["hostile_NO"],
                   "of": H["of_total"], "dimension_totals": H["dimension_totals"]},
            adjudications=[REVIEWER],
            counterfactual=("installing the absent packages must move at least 39 rows from "
                            "defect_present=True to False; nothing about how I describe them can"),
            caveats=["the bucket-to-dimension mapping is my judgement, declared once and applied "
                     "uniformly to all 47 rather than decided per node, so it can be rejected "
                     "wholesale but not tuned row by row"],
            source_artifacts=["techne/loop/rung_notes/cycle_062_hostile_census.json"],
        ),
        Claim(
            claim_id="C062-4",
            question="Is 39 a count of defects or a count of symptoms?",
            proposition=(
                f"Symptoms. The {sym['missing_dependency_symptoms']} missing-dependency reds "
                f"trace to {sym['distinct_absent_packages']} distinct absent packages across "
                f"{sym['distinct_test_files_affected']} test files. This is my one AMENDMENT to "
                f"the review rather than an adoption: reading 39 as 39 deployment defects "
                f"inflates in the opposite direction from my own headline. The honest pair is "
                f"{sym['distinct_absent_packages']}-or-so unavailable capabilities producing "
                f"{sym['missing_dependency_symptoms']} red symptoms."),
            population=CENSUS,
            contract=MeasurementContract(
                numerator_predicate="distinct absent packages named by the interpreter",
                denominator_predicate="all 47 red node ids",
                population_id=CENSUS.population_id),
            measurement_command=CENSUS_CMD,
            value=sym,
            adjudications=[
                Adjudication(
                    kind=Adjudicator.KNOWN_ANSWER_CONTROL,
                    detail=("the package names come from the interpreter's own ImportError text, "
                            "captured per node id, not from my recollection of the environment"),
                    passed=True, independent_of_generator=True)],
            counterfactual=("installing exactly one of the named packages must clear all and only "
                            "the rows naming it"),
            caveats=["the extracted list contains one mis-parsed entry -- the shapely requirement "
                     "surfaces as a prometheus_math symbol because the regex captured the wrong "
                     "group -- and the MIP backend is absent from the list entirely because it "
                     "raises ValueError rather than ImportError. Counting both, the true figure "
                     "is 8 capability families, not 7."],
            source_artifacts=["techne/loop/rung_notes/cycle_062_hostile_census.json"],
        ),
        Claim(
            claim_id="C062-5",
            question=("How much of the arsenal's defect load is being carried by the fact that I "
                      "already know about it?"),
            proposition=(
                f"Almost all of it. Under the reviewer's D_open metric -- new defects plus "
                f"known-but-unrepaired defects, where discovery state may never reduce the second "
                f"term -- D_open is {H['D_open']['D_open_total']}: "
                f"{H['D_open']['D_new_this_cycle']} new this cycle and "
                f"{H['D_open']['D_known_unrepaired']} known and unrepaired. Every prior cycle's "
                f"framing let the second term disappear into the word 'known'. Only repair may "
                f"reduce it, and this cycle repaired none of them."),
            population=CENSUS,
            contract=MeasurementContract(
                numerator_predicate="defects present and unrepaired at cycle end",
                denominator_predicate="all 47 red node ids",
                population_id=CENSUS.population_id),
            measurement_command=CENSUS_CMD,
            value=H["D_open"],
            adjudications=[REVIEWER],
            counterfactual=("a ruling on #242 followed by an install must reduce "
                            "D_known_unrepaired by the missing-dependency count; writing a better "
                            "classification of them must not move it at all"),
            source_artifacts=["techne/loop/rung_notes/cycle_062_hostile_census.json"],
        ),
        Claim(
            claim_id="C062-6",
            question="Was prediction 2 falsified by the data, or by its own design?",
            proposition=(
                f"By its own design, and that is a new error shape. I pre-registered that at "
                f"least 4 of 8 mutation families would leave the decision unchanged. Only "
                f"{B['survived_undetected']} did. But the eight families were fixed in the SAME "
                f"document, and only two of them touch fields the gate reads nothing from -- so "
                f"the prediction was arithmetically unsatisfiable given the instrument declared "
                f"beside it. The stated mechanism was correct and the count attached to it was "
                f"impossible."),
            population=MUTATION,
            contract=MeasurementContract(
                numerator_predicate="families targeting fields promotable() does not read",
                denominator_predicate="all 8 pre-registered mutation families",
                population_id=MUTATION.population_id),
            measurement_command=GATE_CMD,
            value={"predicted_at_least": 4, "observed": B["survived_undetected"],
                   "families_targeting_unread_fields": und},
            adjudications=[
                Adjudication(
                    kind=Adjudicator.SAME_MODEL_AUDIT,
                    detail="I read my own pre-registration against my own family list",
                    passed=True, independent_of_generator=False)],
            counterfactual=("adding mutation families for `question`, `caveats` and "
                            "`source_artifacts` -- all unread by the gate -- would have made the "
                            "prediction satisfiable without changing the gate at all"),
            source_artifacts=["techne/loop/cycle_062.md"],
        ),
    ]


def main() -> int:
    cs = claims()
    promo = 0
    for c in cs:
        ok, _ = c.promotable()
        promo += bool(ok)
        print(render(c))
        print()
    print(f"<!-- {promo}/{len(cs)} claims promotable; rendered by techne/loop/claims_062.py -->")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
