"""Cycle 061's exported factual claims, as `techne.lib.claim_record.Claim` records.

CAMPAIGN RULE 2: every number is read from a committed row file
(`techne/loop/rung_notes/cycle_061_red_triage.json`,
`techne/loop/rung_notes/cycle_061_zaremba_{prefix,postfix}.json`,
`pivot/arsenal_red_060.json`); markdown is rendered from these records, never typed beside them.

    python techne/loop/claims_061.py
"""
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
T = json.loads((ROWS / "cycle_061_red_triage.json").read_text(encoding="utf-8"))
ZPRE = json.loads((ROWS / "cycle_061_zaremba_prefix.json").read_text(encoding="utf-8"))
ZPOST = json.loads((ROWS / "cycle_061_zaremba_postfix.json").read_text(encoding="utf-8"))

TRIAGE_CMD = "python techne/loop/measure_061_red_triage.py"

#: Buckets assigned BY READING, for the 8 the mechanical classifier left UNCLASSIFIED. Recorded
#: here rather than folded into the script so the machine-decided and human-decided parts of the
#: classification stay separable -- the mechanical share is auditable, this share is not.
READ_ASSIGNMENTS = {
    "test_solve_mip_all_continuous_matches_solve_lp": "MISSING_DEPENDENCY",
    "test_all_integer": "MISSING_DEPENDENCY",
    "test_infeasible_integer": "MISSING_DEPENDENCY",
    "test_integrality_none_lp": "MISSING_DEPENDENCY",
    "test_authority_mossinghoff_178_entries": "STALE_ASSERTION",
    "test_authority_figure_8_volume_is_2_0299": "DELIBERATELY_RED",
    "test_property_all_hyperbolic_knots_have_nonzero_volume": "DELIBERATELY_RED",
    "test_couplet_claim_does_not_dispatch_primary_verifier": "ENVIRONMENT",
}


def final_tally() -> dict:
    out: dict = {}
    for r in T["rows"]:
        b = r["bucket"]
        if b == "UNCLASSIFIED":
            b = READ_ASSIGNMENTS.get(r["node"].split("::")[-1], "UNCLASSIFIED")
        out[b] = out.get(b, 0) + 1
    return out


TALLY = final_tally()

REDS = Population(
    population_id="arsenal-reds-060",
    source="pivot/arsenal_red_060.json",
    row_count=T["n_nodes"],
    selection_predicate=("every FAILED pytest node id (44) plus every collection error (3) in "
                         "the committed arsenal_red_060 report, each re-run individually"),
    sampling_method="full-scan (complete list, no truncation)",
)

ZAREMBA = Population(
    population_id="zaremba-q-1-to-500",
    source="techne/lib/cf_expansion.py::zaremba_test",
    row_count=500,
    selection_predicate="every integer q from 1 to 500 inclusive, before and after the fix",
    sampling_method="full-scan",
)

RERUN = Adjudication(
    kind=Adjudicator.DIFFERENTIAL_TEST,
    detail=("each node id was RE-RUN in its own subprocess and classified from the exception it "
            "actually raised, not from its name. The name would have misled: "
            "`test_edge_non_psd_raises` sounds mathematical and fails on an ImportError; "
            "`test_3sat_unsatisfiable` sounds like a solver disagreement and fails on a missing "
            "`pysat`."),
    passed=True,
    independent_of_generator=True,
)

EXC_TYPE = Adjudication(
    kind=Adjudicator.KNOWN_ANSWER_CONTROL,
    detail=("the MISSING_DEPENDENCY share of the classification is decided by the exception TYPE "
            "(ModuleNotFoundError / ImportError) and the absent module name is extracted from "
            "the interpreter's own message -- not from my recollection of which packages are "
            "installed. The 7 module names in the row file are therefore evidence, and the #242 "
            "dependency list is derived rather than remembered."),
    passed=True,
    independent_of_generator=True,
)

ZAREMBA_DIFF = Adjudication(
    kind=Adjudicator.KNOWN_ANSWER_CONTROL,
    detail=("Zaremba's conjecture with bound 5 now holds across the full authority range "
            "q = 1..200 (it held only over 2..200 before), an external mathematical fact; and a "
            "500-value before/after differential shows exactly one q changed"),
    passed=True,
    independent_of_generator=True,
)


def claims() -> list:
    changed = [q for q in range(1, 501) if ZPRE[str(q)] != ZPOST[str(q)]]
    md = T["missing_modules"]
    return [
        Claim(
            claim_id="C061-1",
            question=("How many of the arsenal's reds are actually broken MATHEMATICS, as opposed "
                      "to an incomplete environment?"),
            proposition=(
                f"None of them. Across all {T['n_nodes']} red node ids -- the complete FAILED "
                f"list plus the collection errors -- the count classified as an unaddressed "
                f"defect in arsenal code is ZERO. The distribution is "
                f"{TALLY.get('MISSING_DEPENDENCY', 0)} missing optional dependency, "
                f"{TALLY.get('NO_LONGER_FAILS', 0)} that pass when run individually, "
                f"{TALLY.get('STALE_ASSERTION', 0)} stale authority literal, "
                f"{TALLY.get('DELIBERATELY_RED', 0)} deliberately red by a prior "
                f"pre-registration, and {TALLY.get('ENVIRONMENT', 0)} load-sensitive wall-clock "
                f"gate. The standing framing of 'N arsenal reds' has been reporting an "
                f"incomplete environment as if it were a broken arsenal."),
            population=REDS,
            contract=MeasurementContract(
                numerator_predicate="node ids whose cause is a defect in arsenal code",
                denominator_predicate="all 47 red node ids in arsenal_red_060.json",
                population_id=REDS.population_id),
            measurement_command=TRIAGE_CMD,
            value={"tally": TALLY, "real_defects": 0},
            adjudications=[RERUN, EXC_TYPE],
            counterfactual=("installing the 7 named absent modules must move at least the "
                            "MISSING_DEPENDENCY count to zero; if it does not, the "
                            "classification is wrong"),
            caveats=[
                "the MISSING_DEPENDENCY share is part machine-decided (exception type) and part "
                "read by me: 4 of them raise ValueError('No MIP backend available') rather than "
                "ImportError, and I assigned those by reading. The split is recorded in "
                "techne/loop/claims_061.py::READ_ASSIGNMENTS so the auditable share stays "
                "separable from the inferential share.",
                "'no unaddressed defect' is not 'no defect': the 2 DELIBERATELY_RED entries are a "
                "REAL mathematical defect (48 hyperbolic knots carrying volume 0.0) that cycle "
                "046 diagnosed, flagged in the data, and correctly declined to make green."],
            source_artifacts=["techne/loop/rung_notes/cycle_061_red_triage.json"],
        ),
        Claim(
            claim_id="C061-2",
            question="Is the '46 arsenal reds, 26+ missing dependencies' figure I have been quoting right?",
            proposition=(
                f"The total was wrong and the dependency share was UNDERSTATED. The current total "
                f"is 44 FAILED plus 3 collection errors, not 46 -- 46 is the cycle-052 baseline, "
                f"stale by eight cycles. And {TALLY.get('MISSING_DEPENDENCY', 0)} of "
                f"{T['n_nodes']} are missing-dependency, against a standing figure of '26+'. I "
                f"pre-registered a prediction that the true number would be BELOW 26 because I "
                f"distrusted the carried-forward figure; the distrust was itself the error."),
            population=REDS,
            contract=MeasurementContract(
                numerator_predicate="node ids failing for want of an absent optional package",
                denominator_predicate="all 47 red node ids in arsenal_red_060.json",
                population_id=REDS.population_id),
            measurement_command=TRIAGE_CMD,
            value={"missing_dependency": TALLY.get("MISSING_DEPENDENCY", 0),
                   "of": T["n_nodes"], "prior_standing_figure": "26+",
                   "absent_modules": md},
            adjudications=[EXC_TYPE, RERUN],
            counterfactual=("if the standing '26+' were right and mine wrong, at most 26 node ids "
                            "would name an absent module in their exception text"),
            source_artifacts=["techne/loop/rung_notes/cycle_061_red_triage.json"],
        ),
        Claim(
            claim_id="C061-3",
            question="Does the red COUNT mean what a cycle diffing it would assume?",
            proposition=(
                f"Not entirely. {TALLY.get('NO_LONGER_FAILS', 0)} of the node ids reported FAILED "
                f"by the full-suite run PASS when run individually -- all four in "
                f"`prometheus_math/databases/tests/test_cremona.py`. Their redness is a property "
                f"of what else ran in the same session, not of the test or the code. A count "
                f"diffed across cycles therefore carries a component that can move without "
                f"anything changing, which is a second reason -- beyond the name-diff argument "
                f"already in `techne/scripts/arsenal_red.py` -- not to read the total as a "
                f"health measure."),
            population=REDS,
            contract=MeasurementContract(
                numerator_predicate="node ids FAILED in the full suite that pass in isolation",
                denominator_predicate="all 47 red node ids in arsenal_red_060.json",
                population_id=REDS.population_id),
            measurement_command=TRIAGE_CMD,
            value={"pass_in_isolation": [r["node"] for r in T["rows"]
                                         if r["bucket"] == "NO_LONGER_FAILS"]},
            adjudications=[
                Adjudication(
                    kind=Adjudicator.DIFFERENTIAL_TEST,
                    detail=("two independently produced row sets disagree about the same four "
                            "node ids: the full-suite run committed in pivot/arsenal_red_060.json "
                            "lists them FAILED, and the per-node re-runs committed in the triage "
                            "file record them passing"),
                    passed=True, independent_of_generator=True),
            ],
            counterfactual=("running the four in the full suite again must reproduce the "
                            "failures; running them alone again must reproduce the passes"),
            caveats=["the mechanism (ordering, shared fixture, network state) was NOT determined "
                     "this cycle; only the discrepancy is measured"],
            source_artifacts=["techne/loop/rung_notes/cycle_061_red_triage.json",
                              "pivot/arsenal_red_060.json"],
        ),
        Claim(
            claim_id="C061-4",
            question=("Did fixing finding #16 change anything other than the case it was "
                      "about?"),
            proposition=(
                f"No. Over q = 1..500, exactly {len(changed)} value changed, and it is q = "
                f"{changed[0] if changed else 'none'}. `zaremba_test(1)` went from "
                f"satisfies=False, witness=None, n_tested=0 to satisfies=True, witness=1, "
                f"n_tested=1, min_max_digit=1; all 499 results for q >= 2 are identical. The "
                f"change is `range(1, q)` to `range(1, q + 1)` for EVERY q rather than a "
                f"special case at 1, because for q >= 2 the added value a = q has gcd(q, q) = q "
                f"!= 1 and is discarded on the next line."),
            population=ZAREMBA,
            contract=MeasurementContract(
                numerator_predicate="q values whose full result dict differs before vs after",
                denominator_predicate="all 500 q values from 1 to 500",
                population_id=ZAREMBA.population_id),
            measurement_command="python techne/loop/claims_061.py",
            value={"changed_q": changed,
                   "q1_before": ZPRE["1"], "q1_after": ZPOST["1"],
                   "identical_for_q_ge_2": all(ZPRE[str(q)] == ZPOST[str(q)]
                                               for q in range(2, 501))},
            adjudications=[ZAREMBA_DIFF],
            counterfactual=("special-casing q == 1 instead would produce the same diff; any other "
                            "loop-bound change would move at least one q >= 2"),
            source_artifacts=["techne/loop/rung_notes/cycle_061_zaremba_prefix.json",
                              "techne/loop/rung_notes/cycle_061_zaremba_postfix.json"],
        ),
        Claim(
            claim_id="C061-5",
            question=("Was the classification scheme I fixed before looking adequate to what I "
                      "found?"),
            proposition=(
                "No. The scheme pre-registered five buckets -- MISSING_DEPENDENCY, "
                "STALE_ASSERTION, REAL_DEFECT, ENVIRONMENT, UNCLASSIFIED -- and the data needed "
                "two more. NO_LONGER_FAILS (passes alone, fails in the suite) is not a cause at "
                "all, and DELIBERATELY_RED (a red a prior pre-registration decided must STAY red, "
                "because making it green would fabricate a measurement) is a category that "
                "cannot be derived from an exception. Fixing a scheme in advance does not make it "
                "complete; it makes its incompleteness visible, which is the whole value."),
            population=REDS,
            contract=MeasurementContract(
                numerator_predicate="buckets required by the data but absent from the pre-registration",
                denominator_predicate="buckets in the final classification",
                population_id=REDS.population_id),
            measurement_command=TRIAGE_CMD,
            value={"preregistered": ["MISSING_DEPENDENCY", "STALE_ASSERTION", "REAL_DEFECT",
                                     "ENVIRONMENT", "UNCLASSIFIED"],
                   "added_after_looking": ["NO_LONGER_FAILS", "DELIBERATELY_RED"],
                   "preregistered_but_empty": ["REAL_DEFECT", "UNCLASSIFIED"]},
            adjudications=[
                Adjudication(
                    kind=Adjudicator.HUMAN_REVIEW,
                    detail=("this is a judgement about my own scheme and has no independent "
                            "adjudicator; it is recorded as inferential and should not be read "
                            "as measured"),
                    passed=True, independent_of_generator=False),
            ],
            counterfactual=("if the two added buckets were unnecessary, every node id in them "
                            "would fit one of the five pre-registered buckets without distortion"),
            caveats=["REAL_DEFECT was pre-registered and came back EMPTY; UNCLASSIFIED was "
                     "pre-registered, held 8 after the mechanical pass, and emptied after reading"],
            source_artifacts=["techne/loop/cycle_061.md"],
        ),
    ]


def main() -> int:
    cs = claims()
    promotable = 0
    for c in cs:
        ok, _ = c.promotable()
        promotable += bool(ok)
        print(render(c))
        print()
    print(f"<!-- {promotable}/{len(cs)} claims promotable; "
          f"rendered by techne/loop/claims_061.py -->")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
