"""CANON R10 acceptance suite — and the promotion of the strength-dial pattern.

Every number here was measured before it was written down. Two results carry the cycle:

1. A technique's assumption can FAIL in the target world while its conclusion SURVIVES. Found
   by computation, not by design: `frobenius_additive` assumes char 5, and in F_3 that
   assumption is false, yet (a+b)^5 = a^5 + b^5 still holds there because a^5 = a for every
   a in F_3. An assumption-tracer alone phantom-breaks it.
2. The feature-sensitivity dial does not merely trade catch against phantoms — on this battery
   it CANNOT reach the honest operating point at any setting, for a structural reason that
   generalises beyond the battery.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.canon_r10_analogy import (  # noqa: E402
    ASSUMPTION_PROBES, BATTERY, TECHNIQUES, W_F3, W_F5, W_Z,
    AssumptionMismatchFlagger, AssumptionTracingTransfer, FeatureSensitiveTransfer,
    MemorizedVerdicts, PessimisticTransferrer, SurfaceMapper, ground_truth, role_map, run,
    score, verdict_only_score,
)

BY_NAME = {t.name: t for t in TECHNIQUES}


# ---- capability: the artifact canon R10 asks for ----------------------------------------------

def test_role_mapping_table_is_instantiated_at_the_actual_q():
    """Half the artifact is the role-mapping TABLE. It must carry the real parameter, not the
    generic letter — the unit row at q = 5 says order 4, and that is what makes the near-analogy
    decidable rather than decorative."""
    rows = {r.role: r for r in role_map(W_Z, W_F5)}
    assert rows["ring"].source == "ℤ" and rows["ring"].target == "F_5[t]"
    assert rows["units"].target == "F_5^* (order 4)"
    assert rows["constant field"].target == "F_5 (char 5)"
    assert rows["prime"].target == "monic irreducible polynomial"


def test_honest_circuit_names_the_broken_assumption_for_every_real_break():
    """The other half of the artifact: the assumption, NAMED, and verified to be one the
    technique actually uses AND to genuinely fail in the target."""
    circuit = AssumptionTracingTransfer()
    for tech, world in BATTERY:
        if ground_truth(tech, world):
            continue
        v = circuit.transfer(tech, world)
        assert v.verdict == "BREAKS"
        assert v.broken_assumption in tech.assumptions
        assert not ASSUMPTION_PROBES[v.broken_assumption](world)
        assert v.witness is not None


def test_honest_circuit_scores_clean_on_both_scorings():
    s_naive, s_strict = verdict_only_score(run(AssumptionTracingTransfer())), \
        score(run(AssumptionTracingTransfer()))
    assert s_naive == {"catch_rate": 1.0, "phantom_break_rate": 0.0}
    assert s_strict["catch_rate"] == 1.0 and s_strict["phantom_break_rate"] == 0.0
    assert s_strict["misnamed"] == 0.0 and s_strict["unsupported"] == 0.0


# ---- the canon's kill test: a near-analogy where exactly ONE assumption fails ------------------

def test_KILL_near_analogy_the_same_technique_breaks_at_q5_and_transfers_at_q3():
    """The canon's kill test, made parameter-dependent. `exactly_two_units` rests on one
    assumption: |units| = 2. ℤ has {±1}; F_5[t] has F_5^* of order 4 (break); F_3[t] has F_3^*
    of order 2 (transfer). A circuit that reasons about DOMAIN KIND rather than the actual
    parameter gets this wrong, and the two cases differ in nothing else."""
    tech = BY_NAME["exactly_two_units"]
    circuit = AssumptionTracingTransfer()
    at5, at3 = circuit.transfer(tech, W_F5), circuit.transfer(tech, W_F3)
    assert at5.verdict == "BREAKS" and at5.broken_assumption == "unit group has order 2"
    assert "4 units" in at5.witness
    assert at3.verdict == "TRANSFERS"


def test_a_size_statement_that_looks_archimedean_transfers_anyway():
    """The control the traps cannot supply. 'Finitely many elements of bounded size' sounds like
    it needs an archimedean absolute value; it holds in both worlds (q^(d+1) polynomials of
    degree <= d). Surface resemblance is not the signal, and neither is surface difference."""
    v = AssumptionTracingTransfer().transfer(BY_NAME["bounded_size_is_finite"], W_F5)
    assert v.verdict == "TRANSFERS"


def test_transfer_is_directional():
    """`frobenius_additive` lives in F_5[t] and breaks going the other way. Analogies have a
    direction, and the role-mapping table must be inverted, not reused."""
    v = AssumptionTracingTransfer().transfer(BY_NAME["frobenius_additive"], W_Z)
    assert v.verdict == "BREAKS" and v.broken_assumption == "characteristic is 5"
    assert "32" in v.witness
    rows = {r.role: r for r in v.mapping}
    assert rows["ring"].source == "F_5[t]" and rows["ring"].target == "ℤ"


# ---- the finding: one instrument is not enough ------------------------------------------------

def test_AN_ASSUMPTION_CAN_FAIL_HARMLESSLY():
    """MEASURED, and not by design. `frobenius_additive` assumes characteristic 5. In F_3 that
    assumption is FALSE — and the conclusion still holds, because a^5 = a^3·a^2 = a·a^2 = a^3 = a
    for every a in F_3, so both sides collapse to a + b.

    A circuit that names a broken assumption whenever one fails would call this a break. The
    honest circuit runs the conclusion and reports TRANSFERS. This is why the R10 artifact needs
    two instruments: the trace supplies the NAME, the probe supplies the VERDICT, and neither
    substitutes for the other.
    """
    tech = BY_NAME["frobenius_additive"]
    assert not ASSUMPTION_PROBES["characteristic is 5"](W_F3)   # the assumption fails
    assert ground_truth(tech, W_F3) is True                     # the conclusion survives
    assert AssumptionTracingTransfer().transfer(tech, W_F3).verdict == "TRANSFERS"


# ---- traps ------------------------------------------------------------------------------------

def test_KILL_surface_mapper_finds_a_mapping_and_calls_it_a_transfer():
    """Trap 1: a role mapping always exists. Zero catch rate, and a perfect phantom rate —
    the reason 'the analogy holds' is not a finding."""
    s = verdict_only_score(run(SurfaceMapper()))
    assert s["catch_rate"] == 0.0 and s["phantom_break_rate"] == 0.0


def test_KILL_assumption_mismatch_flagger_breaks_everything_and_names_the_wrong_thing():
    """Trap 2, the over-suspicious end. Under verdict-only scoring it looks like a perfect
    detector (catch 1.0) and is exposed only by its 100% phantom rate. Under artifact-required
    scoring its catch rate collapses to zero: it names a world FEATURE, which is not the
    assumption the technique's proof used."""
    r = run(AssumptionMismatchFlagger())
    naive, strict = verdict_only_score(r), score(r)
    assert naive["catch_rate"] == 1.0 and naive["phantom_break_rate"] == 1.0
    assert strict["catch_rate"] == 0.0 and strict["misnamed"] == 5.0


def test_KILL_pessimist_has_perfect_verdicts_and_a_worthless_artifact():
    """Trap 3. Every claim unsupported: no witness on any of the 14 battery entries."""
    r = run(PessimisticTransferrer())
    assert verdict_only_score(r)["catch_rate"] == 1.0
    assert score(r)["catch_rate"] == 0.0
    assert score(r)["unsupported"] == float(len(BATTERY))


def test_KILL_memorizer_dies_on_name_randomization():
    """Trap 4, the gaming route. A lookup table keyed on the technique name reproduces the
    battery's verdicts without doing any mapping work. Randomising the names — which changes
    nothing mathematical — takes its catch rate from 1.0 to 0.0, while the honest circuit is
    unmoved. This is the R0 fresh-seed defence, reused."""
    scrambled = [(dataclasses.replace(t, name=f"tech_{i}"), w)
                 for i, (t, w) in enumerate(BATTERY)]
    assert verdict_only_score(run(MemorizedVerdicts()))["catch_rate"] == 1.0
    assert verdict_only_score(run(MemorizedVerdicts(), scrambled))["catch_rate"] == 0.0
    honest = AssumptionTracingTransfer()
    assert verdict_only_score(run(honest)) == verdict_only_score(run(honest, scrambled))


def test_memorizer_also_dies_on_the_parameter_shift_alone():
    """A second, independent kill: the memoriser says `exactly_two_units` BREAKS, which is right
    at q = 5 and wrong at q = 3. Name randomisation is not the only defence available."""
    assert verdict_only_score(run(MemorizedVerdicts()))["phantom_break_rate"] > 0.0


# ---- the dial, and why its optimum is not on it ------------------------------------------------

def test_FOURTH_SIGHTING_the_dial_cannot_reach_the_honest_operating_point():
    """**Fourth sighting of the battery strength-dial pattern** (after R3's lexicographic
    (soundness, −coverage), R6's search horizon, R9's tactic budget) — and the sighting that
    explains the other three.

    Sweeping k = number of world features treated as disqualifying gives a CLIFF, not a curve:

        k=0  catch 0.000  phantom 0.000
        k=1  catch 1.000  phantom 1.000
        k=2  catch 1.000  phantom 1.000
        k=3  catch 1.000  phantom 1.000

    versus the honest circuit at catch 1.000, phantom 0.000. No setting attains it.
    """
    points = [verdict_only_score(run(FeatureSensitiveTransfer(k))) for k in range(4)]
    assert points[0] == {"catch_rate": 0.0, "phantom_break_rate": 0.0}
    for p in points[1:]:
        assert p == {"catch_rate": 1.0, "phantom_break_rate": 1.0}
    honest = verdict_only_score(run(AssumptionTracingTransfer()))
    assert honest == {"catch_rate": 1.0, "phantom_break_rate": 0.0}
    assert honest not in points


def test_the_reason_is_structural_the_dial_reads_the_wrong_arguments():
    """Why no setting can work, in a form that generalises past this battery: a feature-
    sensitive circuit is a function of (source world, target world) ALONE, so it must return the
    same verdict for every technique on a given pair. On the pair ℤ → F_5[t] the ground truth
    is not constant across techniques. Therefore any such circuit is wrong on at least one.

    Generalised: **a battery parameter that does not read the instance cannot separate instances
    that differ.** R6's horizon, R9's tactic budget and R3's capacity are instance-blind in
    exactly this way, which is why each is defeated by an instance placed past its setting.
    """
    same_pair = [(t, W_F5) for t in TECHNIQUES if t.home is W_Z]
    truths = {ground_truth(t, W_F5) for t in TECHNIQUES if t.home is W_Z}
    assert truths == {True, False}          # ground truth varies WITHIN the world pair
    for k in range(4):
        verdicts = {run(FeatureSensitiveTransfer(k), same_pair)[i][2].verdict
                    for i in range(len(same_pair))}
        assert len(verdicts) == 1           # every setting is constant on the pair


@pytest.mark.parametrize("k", [0, 1, 2, 3])
def test_no_dial_setting_produces_a_supported_artifact_for_every_break(k):
    """The artifact requirement kills the dial a second time, independently of the scoring."""
    r = run(FeatureSensitiveTransfer(k))
    assert score(r)["catch_rate"] < 1.0
