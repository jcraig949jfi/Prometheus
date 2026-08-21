"""COMPOSITION acceptance suite — the first seam probe. (Cycle 024.)

R1 downstream of R2, solving `f(x) = 0` for a rational `f`. Four chains: one sound, three that
pass their stages individually and fail composed — or worse, pass composed without using them.

Three results, in order of how much they cost me:

1. Composition can only LOSE, and the two sweep quantities move in opposite directions along a
   chain (data-processing inequality). The first stage where deficit rises is the seam, so
   seam-location becomes a measurement.
2. **The profile is blind to two of the three traps.** Shortcut and laundering chains produce
   profiles byte-identical to the sound chain. The instrument I built this cycle is aliased
   against exactly the failures it was built to find.
3. **My first laundering detector was wrong**, and the module keeps the wrong version renamed
   rather than deleting it: "discards nothing" also describes every lossless stage.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from prometheus_math.partition import induced_partition, is_refinement_chain  # noqa: E402
from techne.ladder_circuits.aliasing import find_aliasing_witness  # noqa: E402
from techne.ladder_circuits.composition import (  # noqa: E402
    LAUNDERING_CHAIN, LOCALLY_SOUND_CHAIN, PROBLEMS, SHORTCUT_CHAIN, SOUND_CHAIN, ablate,
    analyse_chain, is_injective_on, reads_beyond_declared_output, stage_is_load_bearing,
    true_root,
)

ALL_CHAINS = [SOUND_CHAIN, LOCALLY_SOUND_CHAIN, SHORTCUT_CHAIN, LAUNDERING_CHAIN]


# ---- capability: the sound chain -----------------------------------------------------------------

def test_the_sound_chain_solves_every_problem():
    """R2's `together` and `numer` feed R1's root rule. Composed, they are correct."""
    for p in PROBLEMS:
        assert SOUND_CHAIN.answer(p) == true_root(p)


def test_every_stage_of_the_sound_chain_is_load_bearing():
    """Canon R9's deletion test, lifted from lemmas to pipeline stages."""
    assert [stage_is_load_bearing(SOUND_CHAIN, i)
            for i in range(len(SOUND_CHAIN.stages))] == [True, True, True]


# ---- finding 1: composition can only lose, in two opposite directions ------------------------------

def test_a_pipeline_induces_a_refinement_chain():
    """The premise of everything else: if stage k+1 sees only stage k's output, its fibres are
    unions of stage k's. Checked rather than assumed, on all four chains."""
    for chain in ALL_CHAINS:
        assert analyse_chain(chain).is_chain


def test_DEFICIT_ONLY_RISES_AND_EXCESS_ONLY_FALLS():
    """The data-processing inequality, in the sweep's own vocabulary (Cover & Thomas, *Elements
    of Information Theory* 2nd ed., Thm 2.8.1).

        deficit = H(T | P_k)  non-decreasing — truth information can only be lost
        excess  = H(P_k | T)  non-increasing — surplus can only be discarded

    So a chain cannot repair an upstream loss, and the only question a composition poses is
    whether what it discarded was excess or deficit.
    """
    for chain in ALL_CHAINS:
        r = analyse_chain(chain)
        assert r.deficit_monotone, (chain.name, r.profile)
        assert r.excess_monotone, (chain.name, r.profile)


def test_the_sound_chain_spends_its_whole_excess_budget_and_no_deficit():
    """Excess 0.667 bits at the input, 0.000 at the answer, deficit 0.000 throughout. The chain
    consumed exactly the surplus and none of the signal."""
    r = analyse_chain(SOUND_CHAIN)
    assert r.profile[0][1] == pytest.approx(0.6666667, abs=1e-6)
    assert r.profile[-1][1] == pytest.approx(0.0)
    assert all(d == pytest.approx(0.0) for d, _e in r.profile)
    assert r.excess_spent == pytest.approx(0.6666667, abs=1e-6)
    assert r.sound and r.seam is None


def test_SEAM_LOCATION_is_a_measurement_not_a_hunt():
    """The locally-sound chain: every stage is sound for its own local target, and `degree_only`
    — sound for "is this linear?" — destroys the end target. Deficit jumps from 0.000 to 1.918
    at exactly that stage and never recovers, and the report names it.

    A stage-wise green suite says nothing about this. That is the whole point of the cycle.
    """
    r = analyse_chain(LOCALLY_SOUND_CHAIN)
    assert r.seam == "degree_only"
    assert not r.sound
    assert r.profile[2][0] == pytest.approx(0.0)              # after numer: still clean
    assert r.profile[3][0] == pytest.approx(1.9182958, abs=1e-6)   # after degree_only: broken
    assert r.profile[4][0] == pytest.approx(1.9182958, abs=1e-6)   # and never recovers
    assert all(LOCALLY_SOUND_CHAIN.answer(p) != true_root(p) for p in PROBLEMS)


# ---- finding 2: the profile is aliased against its own traps --------------------------------------

def test_FINDING_the_profile_cannot_see_the_shortcut_or_the_laundering():
    """**The instrument built this cycle is blind to two of the three failures it was built for.**

    The shortcut chain ignores its stages and answers from the raw input; the laundering chain
    smuggles the input past a stage that claims to reduce. Both produce profiles byte-identical
    to the sound chain — deficit 0.000 throughout, excess 0.667 spent to 0.000, seam None.
    """
    profiles = {c.name: tuple((round(d, 9), round(e, 9)) for d, e in analyse_chain(c).profile)
                for c in (SOUND_CHAIN, SHORTCUT_CHAIN, LAUNDERING_CHAIN)}
    assert profiles["sound"] == profiles["shortcut"] == profiles["laundering"]
    for name in profiles:
        assert analyse_chain({c.name: c for c in ALL_CHAINS}[name]).sound


def test_the_blindness_is_an_ALIASING_WITNESS_on_the_instrument_itself():
    """Stated in the instrument's own vocabulary: under the projection "the chain's profile",
    the sound and shortcut chains are aliased, and their truths differ on whether the stages are
    used at all. So no threshold on the profile separates them — the usual impossibility, this
    time against a tool I built four hours ago."""
    prof = lambda c: tuple((round(d, 9), round(e, 9)) for d, e in analyse_chain(c).profile[-3:])
    uses = lambda c: all(stage_is_load_bearing(c, i) for i in range(len(c.stages)))
    w = find_aliasing_witness(ALL_CHAINS, prof, uses)
    assert w is not None
    assert {w.left.name, w.right.name} == {"sound", "shortcut"}
    assert (w.left_truth, w.right_truth) == (True, False)


def test_ABLATION_catches_the_shortcut_that_the_profile_cannot():
    """Canon R9's deletion test at chain level. Every stage of the shortcut chain is
    decorative — remove any of them and the answers are unchanged — while every stage of the
    sound chain is load-bearing. Note `ablate` preserves the chain's TYPE, so the shortcut
    cannot escape by having its class swapped out from under it."""
    assert [stage_is_load_bearing(SHORTCUT_CHAIN, i)
            for i in range(len(SHORTCUT_CHAIN.stages))] == [False, False, False]
    assert all(SHORTCUT_CHAIN.answer(p) == true_root(p) for p in PROBLEMS)  # right answers!
    assert ablate(SHORTCUT_CHAIN, 0).name.startswith("shortcut-minus")


# ---- finding 3: my first laundering detector was wrong ---------------------------------------------

def test_FINDING_injectivity_is_not_the_laundering_signature():
    """**A detector I built this cycle and had to withdraw, kept renamed rather than deleted.**

    I reasoned that a stage claiming to reduce while discarding nothing must be smuggling.
    Measured: the SOUND chain's `together` reports exactly the same thing, because it is
    injective on these problems. A lossless transform discards nothing either, so injectivity
    and laundering are indistinguishable to any information measure.
    """
    assert is_injective_on(SOUND_CHAIN, 0) is True          # legitimate, lossless
    assert is_injective_on(LAUNDERING_CHAIN, 1) is True     # dishonest
    # identical readings, opposite verdicts: the measure cannot be the detector


def test_REPAIR_laundering_is_a_CONTRACT_violation_and_needs_an_intervention():
    """The working detector corrupts everything the stage emitted except its declared output and
    re-runs the chain. If the answers move, a downstream stage read past the interface.

    It must be an intervention because laundering is not an information-flow property at all —
    the bits are present in both chains, and what differs is entitlement. Third instance in this
    loop of that shape, after claim v13 (completeness) and R11's declared reference class.
    """
    assert reads_beyond_declared_output(LAUNDERING_CHAIN, 1) is True
    assert reads_beyond_declared_output(SOUND_CHAIN, 0) is False
    assert reads_beyond_declared_output(SOUND_CHAIN, 1) is False


def test_the_three_detectors_are_independent_and_all_three_are_needed():
    """Each trap is caught by exactly one instrument, and the sound chain passes all three."""
    def verdicts(chain):
        return (analyse_chain(chain).sound,
                all(stage_is_load_bearing(chain, i) for i in range(len(chain.stages))),
                not any(reads_beyond_declared_output(chain, i)
                        for i in range(len(chain.stages) - 1)))

    assert verdicts(SOUND_CHAIN) == (True, True, True)
    assert verdicts(LOCALLY_SOUND_CHAIN)[0] is False        # profile catches it
    assert verdicts(SHORTCUT_CHAIN)[1] is False             # ablation catches it
    assert verdicts(LAUNDERING_CHAIN)[2] is False           # intervention catches it
    assert verdicts(SHORTCUT_CHAIN)[0] is True              # and the other two are fooled
    assert verdicts(LAUNDERING_CHAIN)[0] is True
