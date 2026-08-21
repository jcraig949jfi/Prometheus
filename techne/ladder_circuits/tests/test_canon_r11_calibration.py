"""CANON R11 acceptance suite — and the first genuine counterexample to claim v11'.

The aliasing analysis was run BEFORE the circuits were designed, per the cycle-019 carry-in, and
it produced two results that pull in opposite directions:

- At the forecaster level, aliasing is unavoidable and is the REASON the rung exists. You cannot
  out-instrument a misleading streak from inside it; you can only be honest about the odds.
- At the scorer level, empirical calibration is definitionally a function of the record, so no
  aliasing witness can exist — the first genuine counterexample to v11' this loop has found.
  The aliasing returns the instant the target becomes calibration on the NEXT battery.

Both are measured on one constructed pair, so the boundary is exhibited rather than argued.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.aliasing import (  # noqa: E402
    fiber_search, find_aliasing_witness, verify_factorization, verify_family_incapacity,
)
from techne.ladder_circuits.canon_r11_calibration import (  # noqa: E402
    BATTERY, CALIBRATION_BATTERY, DEFAULT_BUDGET, SHIFTED_BATTERY, Assessment,
    BatteryTunedForecaster, HedgingForecaster, MimicForecaster, OverconfidentAsserter,
    ReferenceClassForecaster, SelectiveReporter, always_true, audit_report, base_rate,
    late_failure, reference_class_prior, score, verify_refutations,
)

HONEST = ReferenceClassForecaster()


def scored(forecaster, battery=BATTERY):
    return score(forecaster.assess_all(battery), len(battery))


# ---- the aliasing analysis, run first ----------------------------------------------------------

def test_ALIASING_IS_THE_ENVIRONMENT_NOT_A_DEFECT():
    """**The design-shaping result.** A claim that fails at n = 14 and a claim that never fails
    are byte-identical to anyone who has checked n ≤ 10. The witness exists, every forecaster in
    the family is wrong on one of the pair, and — unlike R6, R9 and R10 — there is no better
    projection available from inside the situation.

    Every earlier rung treated an aliasing witness as something to design away. Here you cannot,
    and calibration is what you do instead. The rung is the response to the witness.
    """
    instances = [late_failure(14, "_probe"), always_true(99, "_probe")]
    projection = lambda c: tuple(c.holds_at(n) for n in range(DEFAULT_BUDGET + 1))
    w = find_aliasing_witness(instances, projection, lambda c: c.truth,
                              note=f"everything checkable within budget {DEFAULT_BUDGET}")
    assert w is not None
    assert w.projection_value == (True,) * (DEFAULT_BUDGET + 1)

    family = [HONEST, OverconfidentAsserter(), HedgingForecaster()]
    result = verify_family_incapacity(
        family=[type(f).__name__ for f in family],
        evaluate=lambda name, c: next(
            f for f in family if type(f).__name__ == name).assess(c).confidence >= 0.5,
        witness=w,
    )
    assert result["all_members_err"] and result["all_members_aliased"]


def test_the_honest_response_to_an_unbreakable_alias_is_the_survivor_base_rate():
    """Being wrong on the individual claim is unavoidable. Being wrong about HOW OFTEN one is
    wrong is not. The honest circuit reports 0.75 because 0.75 of budget-10 survivors in its
    declared reference class are true — a fact it measured, not a feeling."""
    assert reference_class_prior(CALIBRATION_BATTERY) == pytest.approx(0.75)
    a = HONEST.assess(late_failure(14, "_probe"))
    assert a.confidence == pytest.approx(0.75) and a.state == "probable"
    assert scored(HONEST)["reliability"] == pytest.approx(0.0)


def test_COUNTEREXAMPLE_TO_V11_empirical_calibration_cannot_be_aliased():
    """**The first genuine counterexample to claim v11' in this loop.**

    Two forecasters, constructed to have byte-identical records on BATTERY — the mimic replays
    the honest circuit's answers. Under the projection "the record on BATTERY", they are aliased
    by construction. And with the target being EMPIRICAL calibration on that same battery, no
    witness exists: the target is a function of the projection, so equal projections force equal
    truths. The scorer sees everything the property depends on.
    """
    mimic = MimicForecaster.of(HONEST, BATTERY)
    pair = [HONEST, mimic]
    record = lambda f: tuple((a.claim, a.confidence, a.outcome) for a in f.assess_all(BATTERY))
    assert record(HONEST) == record(mimic)                       # aliased by construction

    empirical = lambda f: round(scored(f)["ece"], 12)
    assert find_aliasing_witness(pair, record, empirical) is None


def test_and_the_aliasing_returns_for_the_target_anyone_actually_wants():
    """The boundary, on the same pair. Make the target calibration on the NEXT battery and a
    witness appears immediately — because that target is no longer a function of the record."""
    mimic = MimicForecaster.of(HONEST, BATTERY)
    pair = [HONEST, mimic]
    record = lambda f: tuple((a.claim, a.confidence, a.outcome) for a in f.assess_all(BATTERY))
    predictive = lambda f: round(scored(f, SHIFTED_BATTERY)["ece"], 12)

    w = find_aliasing_witness(pair, record, predictive,
                              note="identical on BATTERY, divergent on SHIFTED_BATTERY")
    assert w is not None
    assert w.left_truth != w.right_truth
    assert scored(HONEST, SHIFTED_BATTERY)["ece"] == pytest.approx(0.5)
    assert scored(mimic, SHIFTED_BATTERY)["ece"] == pytest.approx(0.25)


def test_the_projection_precondition_is_checked_not_assumed():
    """Per cycle 019: never assert a finest-projection argument without checking factorization.
    A budget-5 view is a coarsening of the budget-10 view, so a witness under the finer one
    binds the coarser member; the reverse does not hold."""
    claims = [late_failure(k, "_f") for k in (3, 7, 12)] + [always_true(1, "_f")]
    fine = lambda c: tuple(c.holds_at(n) for n in range(11))
    coarse = lambda c: tuple(c.holds_at(n) for n in range(6))
    assert verify_factorization(claims, coarse, fine)
    assert not verify_factorization(claims, fine, coarse)


def test_fiber_search_synthesises_the_misleading_streak():
    """Synthesis rather than hand-picking: hold the observable prefix fixed and walk the failure
    point until the truth flips. Seeded on a true claim, it finds a claim that survives the whole
    budget and is false."""
    seed = always_true(0, "_fiber")
    mutate = lambda _c: (late_failure(k, "_fiber") for k in range(1, 40))
    projection = lambda c: tuple(c.holds_at(n) for n in range(DEFAULT_BUDGET + 1))
    w = fiber_search(seed, mutate, projection, lambda c: c.truth)
    assert w is not None
    assert w.right.first_failure > DEFAULT_BUDGET      # only streaks past the budget survive
    assert (w.left_truth, w.right_truth) == (True, False)


# ---- the canon's kill test and the traps -------------------------------------------------------

def test_KILL_overconfidence_on_the_misleading_streak():
    """The canon's kill. 0.99 on everything unrefuted turns each surviving false claim into a
    confident error, and the reliability term is where it shows."""
    over = scored(OverconfidentAsserter())
    assert over["reliability"] > scored(HONEST)["reliability"]
    assert over["ece"] == pytest.approx(0.16)
    assert over["brier"] > scored(HONEST)["brier"]


def test_KILL_hedging_ties_the_honest_circuit_on_BOTH_calibration_metrics():
    """TRAP 2, and the R11 analogue of R6's recall/phantom pair. The hedger reports the base
    rate on every claim: reliability 0.0 and ECE 0.0, exactly matching the honest circuit. It is
    separated only by resolution — it carries no information — which is why canon R11 says
    Brier-scored rather than calibration-scored."""
    hedge, honest = scored(HedgingForecaster()), scored(HONEST)
    assert hedge["reliability"] == pytest.approx(honest["reliability"])
    assert hedge["ece"] == pytest.approx(honest["ece"])          # indistinguishable so far
    assert hedge["resolution"] == pytest.approx(0.0)
    assert honest["resolution"] > 0.0                            # the separator
    assert hedge["skill"] == pytest.approx(0.0) and honest["skill"] > 0.0


def test_KILL_battery_tuned_forecaster_has_perfect_numbers_and_no_evidence():
    """TRAP 3. Brier 0, ECE 0, reliability 0, skill 1 — every number a scoreboard can produce,
    and no forecasting behind any of them.

    The kill does not need name randomisation. It issues refutations of claims whose
    counterexamples lie at n = 14 and n = 19, past its own search budget of 10, and cannot say
    where they fail. Evidence typing catches what the scoreboard cannot.
    """
    tuned = BatteryTunedForecaster()
    s = scored(tuned)
    assert s["brier"] == pytest.approx(0.0) and s["skill"] == pytest.approx(1.0)
    assert s["ece"] == pytest.approx(0.0) and s["reliability"] == pytest.approx(0.0)

    bad = verify_refutations(tuned.assess_all(BATTERY), BATTERY)
    assert len(bad) == 6                                        # every refutation, unwitnessed
    assert "fails_at_14_test" in bad and "fails_at_19_test" in bad
    assert verify_refutations(HONEST.assess_all(BATTERY), BATTERY) == ()


def test_battery_tuned_also_dies_on_name_randomisation():
    """The second, independent kill. Renaming the claims voids the lookup table and the
    forecaster falls back to an honest budget search — so its skill does not collapse to zero,
    it collapses from a perfect 1.000 to 0.333, BELOW the honest circuit's 0.500. What remains
    is the value of the genuine refutations it can still find, which is the correct reading:
    strip the memorised answers and what is left is a weak forecaster, not a broken one.

    The honest circuit does not notice the renaming at all, because it never read the names."""
    renamed = [dataclasses.replace(c, name=f"anon_{i}") for i, c in enumerate(BATTERY)]
    tuned_before = scored(BatteryTunedForecaster())["skill"]
    tuned_after = scored(BatteryTunedForecaster(), renamed)["skill"]
    assert tuned_before == pytest.approx(1.0)
    assert tuned_after == pytest.approx(1 / 3)
    assert tuned_after < scored(HONEST)["skill"]
    assert scored(HONEST, renamed)["skill"] == scored(HONEST)["skill"]


def test_KILL_selective_reporting_is_rewarded_by_the_proper_scoring_rule():
    """TRAP 4, and the one that motivates a constitution rather than a metric.

    MEASURED: dropping the claims it got wrong improves the selective reporter's Brier from
    0.125 to 0.0375 and its skill from 0.500 to 0.844. The evidence it publishes is not
    falsified — it is incomplete, and no function of the published record can see what is absent
    from it. Only an external count against a PRE-DECLARED claim ledger catches it.
    """
    sel = SelectiveReporter()
    published = sel.assess_all(BATTERY)
    s = score(published, len(BATTERY))
    honest = scored(HONEST)
    assert s["brier"] < honest["brier"] and s["skill"] > honest["skill"]     # rewarded
    assert verify_refutations(published, BATTERY) == ()                      # nothing falsified
    assert s["completeness"] < 1.0

    audit = audit_report(published, BATTERY)
    assert not audit["complete"]
    assert set(audit["missing"]) == {"fails_at_14_test", "fails_at_19_test"}


def test_the_reliability_degradation_of_the_selective_reporter_is_not_a_defence():
    """Honesty about a measurement that looks like a defence and is not. Reliability does get
    worse (0.0 -> 0.0375), because dropping only confident-and-wrong claims leaves the survivors
    systematically under-forecast. That is a property of THIS drop rule; a reporter dropping in
    a balanced way would not pay it, while completeness would still catch it."""
    s = score(SelectiveReporter().assess_all(BATTERY), len(BATTERY))
    assert s["reliability"] > scored(HONEST)["reliability"]
    assert s["completeness"] == pytest.approx(10 / 12)


# ---- the artifact, and the audit -----------------------------------------------------------------

def test_the_artifact_is_calibration_state_against_ground_truth():
    """Canon's artifact. Every assessment carries the three-way state the canon names, plus the
    outcome, so the record can be checked claim by claim rather than in aggregate."""
    assessments = HONEST.assess_all(BATTERY)
    states = {a.state for a in assessments}
    assert states == {"refuted", "probable"}
    assert all(a.is_supported for a in assessments)
    refuted = [a for a in assessments if a.state == "refuted"]
    assert all(a.outcome == 0 and "fails at n =" in a.witness for a in refuted)


def test_completeness_is_the_one_number_a_record_cannot_supply_for_itself():
    """The structural point, isolated: `score` needs `expected` passed in from outside. Given
    only the published record, the selective reporter's completeness is unknowable — it reads
    1.0 against its own length and 0.83 against the real ledger."""
    published = SelectiveReporter().assess_all(BATTERY)
    assert score(published, len(published))["completeness"] == pytest.approx(1.0)
    assert score(published, len(BATTERY))["completeness"] == pytest.approx(10 / 12)


def test_honest_circuit_survives_every_check_in_this_suite():
    """A battery that killed the honest circuit too would be the R6 phantom pathology again."""
    assessments = HONEST.assess_all(BATTERY)
    s = score(assessments, len(BATTERY))
    assert s["completeness"] == 1.0 and s["unsupported"] == 0.0
    assert s["reliability"] == pytest.approx(0.0) and s["resolution"] > 0.0
    assert verify_refutations(assessments, BATTERY) == ()
    assert audit_report(assessments, BATTERY)["complete"]
