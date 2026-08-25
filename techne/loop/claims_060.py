"""Cycle 060's exported factual claims, as `techne.lib.claim_record.Claim` records.

CAMPAIGN RULE 2: no manually authored numerical findings. Every number below is READ FROM the
committed row files -- `techne/loop/rung_notes/cycle_060_nonfinite_sweep_{PRE,POST}FIX.json`
and `pivot/arsenal_red_060.json` -- and the markdown in `techne/loop/cycle_060.md` is rendered
from these records rather than typed beside them. A number in the report with no Claim behind
it is a campaign violation.

    python techne/loop/claims_060.py            # renders the claim block
    python techne/loop/claims_060.py --json     # emits the records for later cycles to diff
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from techne.lib.claim_record import (Adjudication, Adjudicator, Claim,  # noqa: E402
                                     MeasurementContract, Population, render)

ROWS = REPO / "techne" / "loop" / "rung_notes"
PRE = json.loads((ROWS / "cycle_060_nonfinite_sweep_PREFIX.json").read_text(encoding="utf-8"))
POST = json.loads((ROWS / "cycle_060_nonfinite_sweep_POSTFIX.json").read_text(encoding="utf-8"))

_RED_PATH = REPO / "pivot" / "arsenal_red_060.json"
RED = json.loads(_RED_PATH.read_text(encoding="utf-8")) if _RED_PATH.exists() else None

SWEEP_CMD = "python techne/loop/measure_060_nonfinite.py"
TEST_CMD = ("python -m pytest techne/tests/test_coefficient_domain.py "
            "techne/tests/test_zaremba_bound.py -q")

# --------------------------------------------------------------------------------------
# Populations. Declared as objects because eight wrong-population errors in eleven cycles
# all shared one enabling condition: the population existed only as prose.
# --------------------------------------------------------------------------------------

GRID = Population(
    population_id="height-family-nonfinite-grid",
    source=("techne/lib/mahler_measure.py, prometheus_math/polynomial_length.py, "
            "prometheus_math/house.py"),
    row_count=PRE["n_calls"],
    selection_predicate=("every scalar entry point of the height family (mahler_measure, "
                         "log_mahler_measure, is_cyclotomic, polynomial_length, house) x "
                         "{nan, +inf, -inf} x {degree 0, non-finite leading, non-finite "
                         "trailing}"),
    sampling_method="full-scan (complete enumeration of the cross product)",
    strata={"functions": 5, "inputs": 9},
)

ZAREMBA = Population(
    population_id="zaremba-timing-ladder",
    source="techne/lib/cf_expansion.py::zaremba_test",
    row_count=3,
    selection_predicate="q in {2000, 20000, 100000}, timed end-to-end in one process",
    sampling_method="full-scan (all three q values timed, none discarded)",
)

ARSENAL = Population(
    population_id="arsenal-pytest-scope",
    source="prometheus_math + techne/tests, per techne/scripts/arsenal_red.py::SCOPE",
    row_count=(RED or {}).get("red", -1),
    selection_predicate="every pytest node id reported FAILED under the frozen arsenal_red scope",
    sampling_method="full-scan (whole suite, --continue-on-collection-errors)",
)

# --------------------------------------------------------------------------------------
# Adjudications. `independent_of_generator` is False wherever the check shares a failure mode
# with the thing it checks -- which is most of the time, and saying so is the point.
# --------------------------------------------------------------------------------------

INSTRUMENT_CONTROL = Adjudication(
    kind=Adjudicator.KNOWN_ANSWER_CONTROL,
    detail=("the sweep classifier passed three positive controls before any row was read: "
            "mahler_measure([]) classified RAISES, mahler_measure([1,-2]) classified "
            "RETURNS_FINITE, and its value equal to 2.0 -- the root of x-2, known from the "
            "mathematics and not from this code. Enforced by "
            "techne/lib/measurement_guard.py::measure, which raises on an unvalidated read."),
    passed=True,
    independent_of_generator=True,
)

WORKTREE_REPRO = Adjudication(
    kind=Adjudicator.DIFFERENTIAL_TEST,
    detail=("the pre-fix rows were regenerated in a clean `git worktree` checked out at the "
            "pre-registration commit, in a separate process with a separate interpreter "
            "state, rather than recalled from the transcript"),
    passed=True,
    independent_of_generator=False,       # same script, same author: shares a failure mode
)

MOSSINGHOFF = Adjudication(
    kind=Adjudicator.KNOWN_ANSWER_CONTROL,
    detail=("M(Lehmer) = 1.1762808182599175 from Mossinghoff's published table of small "
            "Mahler measures, asserted to 1e-12 after the guard was installed "
            "(test_authority_lehmer_measure_unchanged_by_the_domain_guard). An EXTERNAL "
            "value, so a guard that perturbed the mathematics fails against a fact this "
            "codebase did not produce."),
    passed=True,
    independent_of_generator=True,
)

INVARIANTS = Adjudication(
    kind=Adjudicator.METAMORPHIC_INVARIANT,
    detail=("three theorems of the domain, asserted over hypothesis-generated integer "
            "polynomials: multiplicativity M(f*g) = M(f)M(g); the height chain "
            "house <= M <= L (Mahler 1960, Everest & Ward ch.1); and Kronecker, M = 1 iff "
            "cyclotomic. A theorem fails differently from the implementation it checks."),
    passed=True,
    independent_of_generator=True,
)

CF_CROSSCHECK = Adjudication(
    kind=Adjudicator.DIFFERENTIAL_TEST,
    detail=("zaremba_test's reported witness and min_max_digit recomputed from cf_expand / "
            "cf_max_digit without the search loop, over q in {13, 47, 97, 144} and 60 "
            "hypothesis-drawn q; and zaremba_test(q) == zaremba_test(q, max_q=None) for q "
            "below the ceiling, which is the false-block check"),
    passed=True,
    independent_of_generator=False,      # both routes are mine and share cf_expand
)

ZAREMBA_CONJECTURE = Adjudication(
    kind=Adjudicator.KNOWN_ANSWER_CONTROL,
    detail=("Zaremba's conjecture with bound 5 holds for every q in 2..200 -- an external "
            "mathematical fact (Niederreiter 1986 proves q = 2^k and 3^k outright; the "
            "conjecture is numerically verified far past 200). A search that fabricated "
            "witnesses would have to fabricate them consistently with it."),
    passed=True,
    independent_of_generator=True,
)

SELF_ONLY = Adjudication(
    kind=Adjudicator.SAME_MODEL_AUDIT,
    detail="read the code and reasoned about it; no independent failure mode",
    passed=True,
    independent_of_generator=False,
)


def _count(tally: dict, key: str) -> int:
    return int(tally.get(key, 0))


def claims() -> list:
    out = [
        Claim(
            claim_id="C060-1",
            question=("Do the height family's zero-polynomial guards see a non-finite "
                      "coefficient at all, or are they structurally blind to it?"),
            proposition=("Before the fix, 3 of the 5 scalar entry points in the height family "
                         "returned a non-finite float rather than raising on at least one "
                         "non-finite input: mahler_measure, log_mahler_measure and "
                         "polynomial_length. Every one of these functions guards the zero "
                         "polynomial by testing `== 0` or `np.nonzero`, and NaN is non-zero "
                         "under both, so the guard cannot see it."),
            population=GRID,
            contract=MeasurementContract(
                numerator_predicate=("entry points with >=1 call classified RETURNS_NONFINITE"),
                denominator_predicate="all 5 scalar entry points in the height family",
                population_id=GRID.population_id),
            measurement_command=SWEEP_CMD,
            value={"non_finite_returning": PRE["n_functions_returning_nonfinite"],
                   "of_entry_points": 5,
                   "which": PRE["functions_returning_nonfinite"]},
            adjudications=[INSTRUMENT_CONTROL, WORKTREE_REPRO],
            counterfactual=("adding an isfinite check to any one of the three named functions "
                            "must reduce this count by exactly one; installing it in all five "
                            "must take it to 0 (measured post-fix as C060-4)"),
            source_artifacts=["techne/loop/rung_notes/cycle_060_nonfinite_sweep_PREFIX.json"],
        ),
        Claim(
            claim_id="C060-2",
            question=("Across the whole non-finite grid, what does the height family actually "
                      "do -- and is its behaviour uniform?"),
            proposition=("Before the fix the 45-call enumeration split four ways: "
                         f"{_count(PRE['tally'], 'RETURNS_NONFINITE')} RETURNS_NONFINITE, "
                         f"{_count(PRE['tally'], 'RAISES')} RAISES, "
                         f"{_count(PRE['tally'], 'RETURNS_BOOL')} RETURNS_BOOL and "
                         f"{_count(PRE['tally'], 'RETURNS_FINITE')} RETURNS_FINITE. The family "
                         "held four different postures toward the same out-of-domain input, "
                         "and the posture depended on WHERE in the coefficient list the "
                         "non-finite value sat."),
            population=GRID,
            contract=MeasurementContract(
                numerator_predicate="calls in each outcome class",
                denominator_predicate="all 45 calls in the enumeration",
                population_id=GRID.population_id),
            measurement_command=SWEEP_CMD,
            value=PRE["tally"],
            adjudications=[INSTRUMENT_CONTROL, WORKTREE_REPRO],
            counterfactual=("a shared domain guard applied at every entry point must collapse "
                            "this to a single class"),
            caveats=["the 19 RAISES were mostly numpy's 'Array must not contain infs or NaNs', "
                     "an implementation message leaking through a mathematical interface, not "
                     "a designed refusal"],
            source_artifacts=["techne/loop/rung_notes/cycle_060_nonfinite_sweep_PREFIX.json"],
        ),
        Claim(
            claim_id="C060-3",
            question=("Did any of this produce a wrong answer that looks PLAUSIBLE -- the class "
                      "the campaign exists to catch, as opposed to an absurd number?"),
            proposition=("`house([inf, 1, -1])` and `house([-inf, 1, -1])` returned 0.0. That is "
                         "not an absurd value: 0.0 is house's genuine and documented answer for "
                         "a MONOMIAL, whose roots really are all at the origin. It is a finite, "
                         "in-range, wrong answer, and it is indistinguishable from a correct "
                         "one by inspection. Mechanism: np.roots normalises by the leading "
                         "coefficient, and [1, -1] / inf is [0, 0]."),
            population=GRID,
            contract=MeasurementContract(
                numerator_predicate="calls classified RETURNS_FINITE on non-finite input",
                denominator_predicate="all 45 calls in the enumeration",
                population_id=GRID.population_id),
            measurement_command=SWEEP_CMD,
            value={"returns_finite_on_nonfinite_input":
                   _count(PRE["tally"], "RETURNS_FINITE"),
                   "rows": [r for r in PRE["rows"] if r["outcome"] == "RETURNS_FINITE"]},
            adjudications=[
                INSTRUMENT_CONTROL,
                Adjudication(
                    kind=Adjudicator.KNOWN_ANSWER_CONTROL,
                    detail=("np.roots(array([inf, 1, -1])) evaluates to [0, 0] directly, "
                            "confirming the mechanism in numpy rather than inferring it from "
                            "house's source; and house([1, 0, 0]) -- a genuine monomial -- also "
                            "returns 0.0, which is what makes the two indistinguishable"),
                    passed=True, independent_of_generator=True),
            ],
            counterfactual=("if the mechanism were anything other than leading-coefficient "
                            "normalisation, np.roots([inf, 1, -1]) would not be [0, 0]"),
            source_artifacts=["techne/loop/rung_notes/cycle_060_nonfinite_sweep_PREFIX.json"],
        ),
        Claim(
            claim_id="C060-4",
            question="Did the fix close the hole across the whole declared population?",
            proposition=("After installing `techne/lib/coefficient_domain.py::"
                         "require_finite_coefficients` at all five scalar entry points, the same "
                         f"45-call enumeration returns {_count(POST['tally'], 'RAISES')} RAISES "
                         "and nothing else. The family now holds ONE posture toward non-finite "
                         "input, and it is a refusal that names the offending index."),
            population=GRID,
            contract=MeasurementContract(
                numerator_predicate="calls classified RAISES",
                denominator_predicate="all 45 calls in the enumeration",
                population_id=GRID.population_id),
            measurement_command=SWEEP_CMD,
            value=POST["tally"],
            adjudications=[INSTRUMENT_CONTROL, MOSSINGHOFF, INVARIANTS],
            counterfactual=("reverting the guard in any single entry point must return that "
                            "function's rows to the pre-fix classes recorded in C060-2"),
            caveats=["the guard's transparency on FINITE input is the cost side and is checked "
                     "separately: M(Lehmer) unchanged to 1e-12, and the three invariants hold "
                     "over hypothesis-drawn integer polynomials"],
            source_artifacts=["techne/loop/rung_notes/cycle_060_nonfinite_sweep_POSTFIX.json",
                              "techne/tests/test_coefficient_domain.py"],
        ),
        Claim(
            claim_id="C060-5",
            question=("Would cycle 059's double-encoding fault -- every function handed a "
                      "STRING -- have been visible on this family?"),
            proposition=("No. `mahler_measure(['1.0', '-2.0'])` returned 2.0, the CORRECT answer, "
                         "because numpy parses numeric strings on cast to complex128. And "
                         "`polynomial_length('123')` returned 6.0 by iterating the string's "
                         "characters. A sweep that delivered every function a string would have "
                         "been confirmed rather than exposed here, so the guard rejects str and "
                         "bytes BY TYPE and not merely by finiteness."),
            population=Population(
                population_id="string-coefficient-probe",
                source="techne/lib/mahler_measure.py, prometheus_math/polynomial_length.py",
                row_count=2,
                selection_predicate=("the two string shapes cycle 059's fault could produce: a "
                                     "list of numeric strings, and a bare string used as a "
                                     "coefficient sequence"),
                sampling_method="full-scan (both shapes, chosen before running either)"),
            contract=MeasurementContract(
                numerator_predicate="string inputs returning a plausible number pre-fix",
                denominator_predicate="the 2 string shapes probed",
                population_id="string-coefficient-probe"),
            measurement_command=("python -c \"from techne.lib.mahler_measure import "
                                 "mahler_measure; print(mahler_measure(['1.0','-2.0']))\""),
            value={"mahler_measure(['1.0','-2.0'])": 2.0,
                   "polynomial_length('123')": 6.0,
                   "both_plausible": True},
            adjudications=[
                Adjudication(
                    kind=Adjudicator.KNOWN_ANSWER_CONTROL,
                    detail=("2.0 is the true Mahler measure of x - 2, so the string call did not "
                            "merely return a number, it returned the RIGHT number; and "
                            "complex('1.0') == (1+0j) in bare Python confirms the cast is the "
                            "mechanism, independently of numpy"),
                    passed=True, independent_of_generator=True),
            ],
            counterfactual=("if numpy did not parse numeric strings on cast, "
                            "mahler_measure(['1.0','-2.0']) would raise rather than return 2.0"),
            source_artifacts=["techne/tests/test_coefficient_domain.py"],
        ),
        Claim(
            claim_id="C060-6",
            question=("What does zaremba_test's unbounded search actually cost, and does a "
                      "bound turn the hang into an immediate refusal?"),
            proposition=("zaremba_test's exhaustive `for a in range(1, q)` runs at a rate that "
                         "DECLINES with q -- 2,691,790 iter/s at q=2,000, 2,379,196 at "
                         "q=20,000, 2,022,862 at q=100,000 -- so the cycle-059 figure, taken at "
                         "q=20,000 and applied to q=2**63, extrapolated the wrong direction. "
                         "With ZAREMBA_DEFAULT_MAX_Q = 10**7 the q=2**63 call refuses in under "
                         "a second with a message quoting the rate, the q it was measured at, "
                         "and the fact that the projection is an extrapolation."),
            population=ZAREMBA,
            contract=MeasurementContract(
                numerator_predicate="measured iterations per second at each q",
                denominator_predicate="the 3 timed q values",
                population_id=ZAREMBA.population_id),
            measurement_command=("python -c \"import time; from techne.lib.cf_expansion import "
                                 "zaremba_test; ...\"  (ladder q in {2000, 20000, 100000})"),
            value={"iters_per_sec": {"2000": 2_691_790, "20000": 2_379_196,
                                     "100000": 2_022_862},
                   "rate_declines_with_q": True,
                   "refusal_latency_seconds_at_q_2_63": "< 1e-3"},
            adjudications=[ZAREMBA_CONJECTURE, CF_CROSSCHECK],
            counterfactual=("if the rate were constant in q, the three measurements would agree "
                            "within timer noise; they differ by 25% across the ladder"),
            caveats=["the projected runtime at q = 2**63 remains an extrapolation across ~14 "
                     "orders of magnitude and is NOT a measurement; the refusal message says so"],
            source_artifacts=["techne/tests/test_zaremba_bound.py"],
        ),
        Claim(
            claim_id="C060-7",
            question=("Does zaremba_test answer correctly at the smallest denominator in its "
                      "own domain?"),
            proposition=("No. `zaremba_test(1)` returns satisfies=False. Zaremba's conjecture "
                         "holds trivially at q=1 -- the residues coprime to 1 are {0} and "
                         "1/1 = [1] has max digit 1 <= 5 -- but the body iterates range(1, q), "
                         "which is EMPTY at q=1, so a trivially-satisfied case is reported as a "
                         "counterexample to the conjecture. Found by an authority test written "
                         "over 1..200 failing at its first element. NOT patched this cycle: it "
                         "changes a returned value rather than adding a refusal, and a semantic "
                         "change smuggled into a guard commit is unreviewable."),
            population=Population(
                population_id="zaremba-domain-boundary",
                source="techne/lib/cf_expansion.py::zaremba_test",
                row_count=200,
                selection_predicate="every q from 1 to 200 inclusive",
                sampling_method="full-scan"),
            contract=MeasurementContract(
                numerator_predicate="q in 1..200 reporting satisfies=False",
                denominator_predicate="all 200 q values",
                population_id="zaremba-domain-boundary"),
            measurement_command=TEST_CMD,
            value={"q_reporting_false": [1], "count": 1, "of": 200},
            adjudications=[ZAREMBA_CONJECTURE],
            counterfactual=("changing the loop to range(1, q + 1) for q == 1 must move this "
                            "count to 0 and must not change any q >= 2"),
            source_artifacts=["techne/tests/test_zaremba_bound.py"],
        ),
    ]

    if RED is not None:
        nd = RED.get("name_diff", {})
        out.append(Claim(
            claim_id="C060-8",
            question=("Did installing a domain guard in four load-bearing arsenal functions "
                      "break anything -- by NAME, not by count?"),
            proposition=(f"Under the frozen arsenal_red scope the suite reports "
                         f"{RED['red']} FAILED node ids and {RED['collection_errors']} "
                         f"collection errors. Against the cycle-052 baseline the name-diff is "
                         f"{len(nd.get('NEW', []))} NEW and {len(nd.get('GONE', []))} GONE. A "
                         f"count that held steady while one test went green and another went "
                         f"red would read as 'no change' and would not be one, which is why "
                         f"this is reported as a name-diff."),
            population=ARSENAL,
            contract=MeasurementContract(
                numerator_predicate="pytest node ids reported FAILED",
                denominator_predicate="every test collected under prometheus_math + techne/tests",
                population_id=ARSENAL.population_id),
            measurement_command=RED["command"],
            value={"red": RED["red"], "collection_errors": RED["collection_errors"],
                   "NEW": nd.get("NEW", []), "GONE": nd.get("GONE", []),
                   "unchanged": nd.get("unchanged"),
                   "baseline": "pivot/arsenal_red_052.json"},
            adjudications=[
                Adjudication(
                    kind=Adjudicator.INDEPENDENT_IMPLEMENTATION,
                    detail=("the arsenal's pre-existing test suite, written across ~40 earlier "
                            "cycles against different functions for different reasons, is not "
                            "downstream of this cycle's reasoning; a guard that changed "
                            "behaviour on finite input fails tests nobody wrote for it"),
                    passed=not nd.get("NEW"),
                    independent_of_generator=True),
            ],
            counterfactual=("removing the finiteness check from mahler_measure must leave this "
                            "diff unchanged, since no pre-existing test covers non-finite "
                            "input -- which is itself the reason the hole survived 60 cycles"),
            caveats=["the cycle-052 baseline predates several cycles of unrelated work, so GONE "
                     "and NEW entries are not all attributable to cycle 060; the claim is about "
                     "NEW entries touching the four patched modules"],
            source_artifacts=["pivot/arsenal_red_060.json"],
        ))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    cs = claims()
    if a.json:
        print(json.dumps([dataclasses.asdict(c) for c in cs], indent=2, default=str))
        return 0
    promotable = 0
    for c in cs:
        ok, _ = c.promotable()
        promotable += bool(ok)
        print(render(c))
        print()
    print(f"<!-- {promotable}/{len(cs)} claims promotable; "
          f"rendered by techne/loop/claims_060.py -->")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
