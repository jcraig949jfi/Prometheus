"""REAL SUBSTRATE III — the discovery pipeline's kill-path battery. Cycle 027, READ-ONLY.

Target chosen first, stage type verified before measuring, per the cycle-025 guard:

    1. Target: F1 / F6 / F9 / F11 over polynomial candidates.
    2. Stage type: each check is a FILTER, which partitions the candidate set — inter-record,
       so cycle 026's scope statement says the instruments should apply.
    3. Direction check: they accumulate rather than destroy, and that inverts the instrument.

The candidates are real reciprocal integer polynomials with Mahler measures computed at high
precision, Lehmer's polynomial among them. Nothing here is a fixture.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from prometheus_math.partition import chain_direction, induced_partition  # noqa: E402
from techne.ladder_circuits.battery_chain import (  # noqa: E402
    CHECKS, analyse_battery_chain, check_resolution, real_candidates, verdict_chain,
)


@pytest.fixture(scope="module")
def report():
    return analyse_battery_chain()


# ---- the candidates are real -----------------------------------------------------------------

def test_the_candidates_are_real_polynomials_with_computed_measures():
    """Lehmer's polynomial is in the set and its measure is the known 1.17628…, which is the
    smallest Mahler measure greater than 1 known for any integer polynomial."""
    cands = real_candidates()
    assert len(cands) > 25
    lehmer = [m for c, m in cands if c == (1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1)]
    assert lehmer and lehmer[0] == pytest.approx(1.17628, abs=1e-4)
    assert all(m >= 1.0 - 1e-9 for _c, m in cands)      # Kronecker: M >= 1 for integer polys


# ---- FINDING 1: the chain runs the other way ---------------------------------------------------

def test_FINDING_a_falsification_battery_ACCUMULATES_rather_than_destroys(report):
    """**The cycle's result.** Cycle 024 built the profile for a transform pipeline, where stage
    k+1 sees only stage k's output; those coarsen forward. A battery ADDS a verdict bit per check
    and discards nothing, so the state refines forward.

    Measured: `is_refinement_chain` is False forward and True reversed.
    """
    assert not report.forward_is_refinement_chain
    assert report.reversed_is_refinement_chain
    assert report.direction.startswith("ACCUMULATING")


def test_FINDING_cycle024s_monotonicity_flags_a_HEALTHY_battery_as_broken(report):
    """Deficit against the terminal verdict DECREASES to zero — 1.8295 → 0.8698 → 0.0000 — which
    is exactly what a working battery should do and exactly what cycle 024 asserts cannot happen.

    So the instruments are not blind here as they were on rewrite stages (cycle 025). They are
    INVERTED, which is worse: an empty reading is obviously useless, a confident wrong one is not.
    """
    assert report.deficit_decreases
    assert not report.matches_cycle024_assumption
    assert report.deficits[0] == pytest.approx(report.terminal_entropy, abs=1e-9)
    assert report.deficits[-1] == pytest.approx(0.0, abs=1e-9)


def test_the_direction_primitive_is_the_precondition_and_it_catches_this():
    """The repair, and it is a precondition rather than a new measure: check the direction before
    reading a profile. `chain_direction` names this chain ACCUMULATING from the partitions
    alone, with no knowledge of what the stages do."""
    cands = real_candidates()
    n = len(cands)
    chains = [verdict_chain(c, m) for c, m in cands]
    stages = [induced_partition(list(range(n)), lambda i, k=k: chains[i][k])
              for k in range(len(chains[0]))]
    assert chain_direction(stages, n) == "ACCUMULATING"


def test_three_stage_type_categories_are_now_measured_not_assumed(report):
    """The taxonomy this and the previous two cycles produced, each entry measured on live code:

        transform / rewrite   instruments BLIND      (cycle 025, ergon render/redact)
        select / reorder      instruments WORK       (cycle 026, ergon _order vs BC-2)
        filter / accumulate   instruments INVERTED   (cycle 027, discovery battery)
    """
    assert report.direction.startswith("ACCUMULATING")
    assert report.n_candidates > 25


# ---- FINDING 2: two checks carry no bits on this evidence ---------------------------------------

def test_FINDING_F9_and_F11_have_ZERO_resolution_on_this_candidate_set():
    """F1 contributes 0.960 bits and F6 0.908; F9 and F11 return the same verdict for every
    candidate and contribute 0.000.

    That is canon R11's hedging forecaster inside a real falsification battery: a member that
    never fires is observationally identical to a member that is not there, and both are
    perfectly "sound". Reported, not judged — a check that has not fired on the candidates it has
    seen may still be the one that catches the next thing. What is worth knowing is that the
    battery's discriminating power on this evidence is entirely F1 and F6.
    """
    res = check_resolution()
    assert res["F1"] > 0.9 and res["F6"] > 0.9
    assert res["F9"] == pytest.approx(0.0)
    assert res["F11"] == pytest.approx(0.0)


def test_the_terminal_verdict_is_fully_determined_after_F6(report):
    """The same fact from the chain side: deficit reaches zero at F6 and the last two stages move
    nothing. Whatever F9 and F11 are for, on this evidence they are not deciding outcomes."""
    assert report.deficits[2] == pytest.approx(0.0, abs=1e-9)      # after F6
    assert report.deficits[3] == pytest.approx(0.0, abs=1e-9)      # after F9
    assert report.deficits[4] == pytest.approx(0.0, abs=1e-9)      # after F11
    assert report.stage_names == ("F1", "F6", "F9", "F11")


def test_the_pipeline_is_untouched():
    """Contract guard: this audit imports and measures, and modifies nothing."""
    import prometheus_math.discovery_pipeline as dp
    assert callable(dp.DiscoveryPipeline.process_candidate)
    assert len(CHECKS) == 4


# ---- CYCLE 028: removing the sample-size objection to my own cycle-027 finding ------------------

def test_CYCLE028_the_wider_sample_does_not_move_F9_or_F11():
    """Cycle 027 measured F9 and F11 at zero over 34 reciprocal candidates in a narrow band and
    recorded the caveat that this was a small sample. Widened to n = 81 — degrees 2-8,
    coefficients to ±5, 37 reciprocal and 44 NON-reciprocal, M spanning 1.0 to 9.6 rather than
    one band — and both stay at exactly 0.0000 bits.
    """
    from prometheus_math.battery import battery_strength
    from techne.ladder_circuits.battery_chain import wide_candidates

    cands = wide_candidates()
    assert len(cands) > 70
    assert max(m for _c, m in cands) > 5.0                       # genuinely wider than one band
    assert sum(1 for c, _m in cands if list(c) != list(c)[::-1]) > 30   # non-reciprocal present

    verdicts = {}
    for name, fn in CHECKS:
        col = []
        for coeffs, m in cands:
            try:
                col.append(bool(fn(list(coeffs), m)[0]))
            except Exception:
                col.append(None)
        verdicts[name] = col

    s = battery_strength(verdicts)
    assert s.advertised == 4 and s.discriminating == 2
    assert s.silent_members == ["F11", "F9"]
    assert s.resolution["F9"] == pytest.approx(0.0)
    assert s.resolution["F11"] == pytest.approx(0.0)


def test_CYCLE028_F9s_ZERO_IS_STRUCTURAL_not_a_sampling_artefact():
    """**Reading the source settled this harder than any amount of sampling could.**

    `_f9_simpler_explanation` is `return True, "..."` with no computation on `coeffs` at all.
    It returns True for the empty list. No candidate set, at any size, can make it fire — so its
    zero is a property of the function, not of my battery.

    Its own docstring is honest about this: the band gate upstream already excludes cyclotomic,
    and the check exists "for post-rejection record-keeping". It is not pretending to be a
    filter. It is simply counted as one.
    """
    from techne.ladder_circuits.battery_chain import f9_is_structurally_constant
    assert f9_is_structurally_constant()
    from prometheus_math.discovery_pipeline import _f9_simpler_explanation
    assert _f9_simpler_explanation([])[0] is True                # even on no polynomial at all


def test_CYCLE028_F11s_CROSS_VALIDATION_PATH_IS_VACUOUS_BY_A_THEOREM():
    """**The sharper half.** F11's docstring says it re-computes M "via two independent paths".
    The second path is `M(reversed(coeffs))` — and reversal maps every root α to 1/α while
    swapping the leading and trailing coefficient, leaving `|a|·∏max(1,|α|)` unchanged. So
    `M(p) = M(reverse(p))` for EVERY polynomial and the two paths compute the same number.

    Verified on 40 random NON-reciprocal integer polynomials, where the reversal really is a
    different polynomial: zero disagreements.
    """
    from techne.ladder_circuits.battery_chain import f11_reciprocal_path_is_vacuous
    assert f11_reciprocal_path_is_vacuous(n_probes=40)


def test_CYCLE028_F11s_SURVIVING_BRANCH_TESTS_THE_CALLER_NOT_THE_CANDIDATE():
    """F11 is not inert — its third comparison, against the caller's reported M, fires correctly.
    But no property of a polynomial can trigger it; only an inconsistent `m_value` handed in from
    outside. As a discriminator over CANDIDATES it contributes zero by construction, while
    remaining a real assertion about bookkeeping.
    """
    from techne.ladder_circuits.battery_chain import f11_drift_branch_fires
    assert f11_drift_branch_fires()


def test_CYCLE028_the_two_zeros_have_DIFFERENT_causes():
    """The distinction worth carrying: F9 cannot fire on anything, ever. F11 can fire, but only
    on caller error, never on a candidate. Both read 0.000 bits over candidates and they are not
    the same finding — which is exactly why 'measure more samples' was the wrong instinct and
    reading the source was the right one."""
    from techne.ladder_circuits.battery_chain import (
        f11_drift_branch_fires, f9_is_structurally_constant,
    )
    assert f9_is_structurally_constant()          # F9: no input can make it fire
    assert f11_drift_branch_fires()               # F11: some input CAN, just not a candidate
