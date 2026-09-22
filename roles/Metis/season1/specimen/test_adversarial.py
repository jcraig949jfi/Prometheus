"""Metis Season 1 -- adversarial tests A-F, plus the C-05 regression.

These are written to BREAK a naive version of the mechanism, not to confirm
it. A and B punish counting items instead of reasons. C and F punish
reflexive skepticism, which is the failure mode the season prompt calls out
as number 10. D punishes rewarding accidental correctness. E is the C-05
regression: an incomplete search must never become negative evidence.

Run: python -m pytest roles/Metis/season1/specimen/test_adversarial.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose import (  # noqa: E402
    Bundle, BundleError, Discriminator, Evidence, Instrument, compose,
)

EXPL = {
    "CLAIM": "the effect is real",
    "RIVAL_A": "a first competing explanation",
    "RIVAL_B": "a second competing explanation",
}


def kinds(result) -> list[str]:
    return [v["kind"] for v in result.vetoes]


def n_reasons(result) -> int:
    return len(result.groups)


# --------------------------------------------------------------------------
# A. MANY COPIES -- confidence must not grow because one observation was
#    written down five times.
# --------------------------------------------------------------------------

def test_A_many_copies_collapse_to_one_reason():
    ev = [
        Evidence(id=f"copy{i}", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"THE_ONE_RUN"}),
                 justification="a restatement of the same run")
        for i in range(5)
    ]
    r = compose(Bundle("A", "d", "2026-01-01", "CLAIM", EXPL, ev))
    assert n_reasons(r) == 1, "five copies of one run are one reason"
    assert "AGREEMENT_NOT_ADDITIVE" in kinds(r)
    grp = r.groups[0]
    assert len(grp["members"]) == 5
    assert grp["shared_upstream"] == ["THE_ONE_RUN"]


# --------------------------------------------------------------------------
# B. FALSE INDEPENDENCE -- different names, one hidden shared ancestor.
# --------------------------------------------------------------------------

def test_B_false_independence_is_exposed_by_provenance():
    ev = [
        Evidence(id="channel_alpha", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"ALPHA_LOCAL", "SHARED_PREPROCESSOR"})),
        Evidence(id="channel_beta", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"BETA_LOCAL", "SHARED_PREPROCESSOR"})),
        Evidence(id="channel_gamma", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"GAMMA_LOCAL", "SHARED_PREPROCESSOR"})),
    ]
    r = compose(Bundle("B", "d", "2026-01-01", "CLAIM", EXPL, ev))
    assert n_reasons(r) == 1, "three names, one preprocessor, one reason"
    v = [x for x in r.vetoes if x["kind"] == "AGREEMENT_NOT_ADDITIVE"][0]
    assert v["shared_upstream"] == ["SHARED_PREPROCESSOR"]


# --------------------------------------------------------------------------
# C. TRUE INDEPENDENCE -- the mechanism must NOT veto merely because
#    independent evidence agrees. This is the anti-skepticism test.
# --------------------------------------------------------------------------

def test_C_true_independence_produces_no_veto():
    ev = [
        Evidence(id="indep_1", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"INSTRUMENT_ONE"}),
                 rules_out=frozenset({"RIVAL_A"}),
                 justification="its observed value is incompatible with RIVAL_A"),
        Evidence(id="indep_2", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"INSTRUMENT_TWO"}),
                 rules_out=frozenset({"RIVAL_B"}),
                 justification="its observed value is incompatible with RIVAL_B"),
    ]
    r = compose(Bundle("C", "d", "2026-01-01", "CLAIM", EXPL, ev))
    assert n_reasons(r) == 2, "disjoint ancestry means two reasons"
    assert r.live_explanations == [], "both rivals eliminated"
    assert r.vetoes == [], f"must not veto genuine independent agreement: {kinds(r)}"


# --------------------------------------------------------------------------
# D. INSTRUMENT TRAP -- the conclusion happens to be right; the instrument
#    was not valid. Accidental correctness earns nothing.
# --------------------------------------------------------------------------

def test_D_instrument_trap_not_rewarded_for_being_accidentally_right():
    broken = Instrument(id="blind_counter", degenerate_boundary=True,
                        generator_known_active=True)
    ev = [
        Evidence(id="right_for_wrong_reason", supports="CLAIM",
                 availability="COMMIT", upstream=frozenset({"BLIND_COUNTER_RUN"}),
                 rules_out=frozenset({"RIVAL_A", "RIVAL_B"}),
                 instrument=broken,
                 justification="reads exactly zero everywhere; the eventual "
                               "historical verdict happened to agree with it"),
    ]
    r = compose(Bundle("D", "d", "2026-01-01", "CLAIM", EXPL, ev))
    assert "INSTRUMENT_VETO" in kinds(r), \
        "an observation producible by instrument failure is vetoed even when it is right"


def test_D2_instrument_invalidated_before_cutoff_is_vetoed():
    """The other half of the trap: a defect discovered before this cutoff."""
    fixed_later = Instrument(id="lineage", invalidated_at="2026-05-22")
    ev = [Evidence(id="stale_obs", supports="CLAIM", availability="COMMIT",
                   upstream=frozenset({"X"}), instrument=fixed_later)]
    after = compose(Bundle("D2", "d", "2026-06-27", "CLAIM", EXPL, ev))
    assert "INSTRUMENT_VETO" in kinds(after)
    before = compose(Bundle("D2", "d", "2026-04-06", "CLAIM", EXPL, ev))
    assert "INSTRUMENT_VETO" not in kinds(before), \
        "a defect not yet discovered cannot be used at an earlier cutoff"


# --------------------------------------------------------------------------
# E. UNKNOWN-AS-ABSENT -- the C-05 regression.
# --------------------------------------------------------------------------

def test_E_incomplete_search_yields_unknown_not_absent():
    ev = [
        Evidence(id="nothing_found", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"A_GREP"}),
                 negative_existence=True, enumeration_complete=False,
                 search_domain="git ls-files | grep ... | head -40",
                 rules_out=frozenset({"RIVAL_A", "RIVAL_B"}),
                 justification="C-05: a prefix read produced a false negative "
                               "existence claim on 2026-09-11"),
    ]
    r = compose(Bundle("E", "d", "2026-01-01", "CLAIM", EXPL, ev))
    assert [u["kind"] for u in r.unknowns] == ["ABSENCE_UNPROVEN"]
    assert "nothing_found" not in r.admitted, \
        "an unproven absence must not sit in the supporting set"
    assert set(r.live_explanations) == {"RIVAL_A", "RIVAL_B"}, \
        "an unproven absence must not eliminate rivals"


def test_E2_complete_enumeration_is_admitted():
    """The rule must not make absence unprovable in principle."""
    ev = [
        Evidence(id="exhaustive", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"FULL_ENUM"}),
                 negative_existence=True, enumeration_complete=True,
                 search_domain="every tracked path, no truncation",
                 rules_out=frozenset({"RIVAL_A", "RIVAL_B"})),
    ]
    r = compose(Bundle("E2", "d", "2026-01-01", "CLAIM", EXPL, ev))
    assert r.unknowns == []
    assert "exhaustive" in r.admitted
    assert r.live_explanations == []


# --------------------------------------------------------------------------
# F. VETO FLOOD -- minor dependency present, major conclusion independently
#    supported. The mechanism must not degenerate into permanent skepticism.
# --------------------------------------------------------------------------

def test_F_minor_dependency_does_not_veto_the_major_conclusion():
    ev = [
        # two items that do share a minor ancestor
        Evidence(id="minor_1", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"SHARED_PLOTTING_LIB", "M1"}),
                 rules_out=frozenset({"RIVAL_A"})),
        Evidence(id="minor_2", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"SHARED_PLOTTING_LIB", "M2"})),
        # and one genuinely independent line that closes the remaining rival
        Evidence(id="independent", supports="CLAIM", availability="COMMIT",
                 upstream=frozenset({"SEPARATE_APPARATUS"}),
                 rules_out=frozenset({"RIVAL_B"})),
    ]
    r = compose(Bundle("F", "d", "2026-01-01", "CLAIM", EXPL, ev))
    assert "CONFIDENCE_VETO" not in kinds(r), \
        "no rival survives, so the major conclusion must not be vetoed"
    assert n_reasons(r) == 2, "the dependent pair is one reason, the other is a second"
    assert r.live_explanations == []


# --------------------------------------------------------------------------
# Guards on the mechanism itself.
# --------------------------------------------------------------------------

def test_undeclared_explanation_is_an_error_not_a_silent_noop():
    """Found by running E1: a typo'd rules_out eliminated nothing, silently."""
    ev = [Evidence(id="x", supports="CLAIM", availability="COMMIT",
                   upstream=frozenset({"U"}),
                   rules_out=frozenset({"TYPO_NOT_DECLARED"}))]
    with pytest.raises(BundleError, match="undeclared"):
        compose(Bundle("G", "d", "2026-01-01", "CLAIM", EXPL, ev))


def test_unproven_availability_is_dropped():
    ev = [Evidence(id="undated", supports="CLAIM",
                   availability="UNAVAILABLE_UNPROVEN",
                   upstream=frozenset({"U"}),
                   rules_out=frozenset({"RIVAL_A", "RIVAL_B"}))]
    r = compose(Bundle("H", "d", "2026-01-01", "CLAIM", EXPL, ev))
    assert r.dropped_unavailable == ["undated"]
    assert set(r.live_explanations) == {"RIVAL_A", "RIVAL_B"}


def test_discriminator_without_power_is_rejected():
    ev = [Evidence(id="x", supports="CLAIM", availability="COMMIT",
                   upstream=frozenset({"U"}))]
    d = Discriminator(id="useless", available_at_cutoff=True, cost="MINUTES",
                      outcome_branches=(frozenset({"RIVAL_A"}),
                                        frozenset({"RIVAL_A"})))
    r = compose(Bundle("I", "d", "2026-01-01", "CLAIM", EXPL, ev, [d]))
    assert r.discriminator is None
    assert r.rejected_discriminators[0]["reason"] == "NO_DISCRIMINATORY_POWER"


def test_discriminator_not_cheaper_than_baseline_is_rejected():
    ev = [Evidence(id="x", supports="CLAIM", availability="COMMIT",
                   upstream=frozenset({"U"}))]
    d = Discriminator(id="expensive", available_at_cutoff=True, cost="WEEKS",
                      outcome_branches=(frozenset({"RIVAL_A"}), frozenset()))
    r = compose(Bundle("J", "d", "2026-01-01", "CLAIM", EXPL, ev, [d],
                       baseline_experiment_cost="HOURS"))
    assert r.discriminator is None
    assert r.rejected_discriminators[0]["reason"] == "NOT_CHEAPER_THAN_BASELINE"


# --------------------------------------------------------------------------
# The preregistered veto-rate bound (SEASON1_PREREGISTRATION s6): at most
# 4 of the 6 lettered tests may emit any veto. Named before the mechanism
# existed; enforced here so it cannot be quietly moved.
# --------------------------------------------------------------------------

def _bundle_for(letter: str) -> Bundle:
    builders = {
        "A": lambda: Bundle("A", "d", "2026-01-01", "CLAIM", EXPL, [
            Evidence(id=f"c{i}", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"THE_ONE_RUN"})) for i in range(5)]),
        "B": lambda: Bundle("B", "d", "2026-01-01", "CLAIM", EXPL, [
            Evidence(id="a", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"AL", "SHARED"})),
            Evidence(id="b", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"BL", "SHARED"}))]),
        "C": lambda: Bundle("C", "d", "2026-01-01", "CLAIM", EXPL, [
            Evidence(id="i1", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"I1"}), rules_out=frozenset({"RIVAL_A"})),
            Evidence(id="i2", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"I2"}), rules_out=frozenset({"RIVAL_B"}))]),
        "D": lambda: Bundle("D", "d", "2026-01-01", "CLAIM", EXPL, [
            Evidence(id="r", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"B"}),
                     rules_out=frozenset({"RIVAL_A", "RIVAL_B"}),
                     instrument=Instrument(id="blind", degenerate_boundary=True,
                                           generator_known_active=True))]),
        "E": lambda: Bundle("E", "d", "2026-01-01", "CLAIM", EXPL, [
            Evidence(id="n", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"G"}), negative_existence=True,
                     enumeration_complete=False, search_domain="prefix"),
            Evidence(id="ok", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"OK"}),
                     rules_out=frozenset({"RIVAL_A", "RIVAL_B"}))]),
        "F": lambda: Bundle("F", "d", "2026-01-01", "CLAIM", EXPL, [
            Evidence(id="m1", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"LIB", "M1"}),
                     rules_out=frozenset({"RIVAL_A"})),
            Evidence(id="m2", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"LIB", "M2"})),
            Evidence(id="ind", supports="CLAIM", availability="COMMIT",
                     upstream=frozenset({"SEP"}), rules_out=frozenset({"RIVAL_B"}))]),
    }
    return builders[letter]()


def test_preregistered_veto_rate_bound_not_exceeded():
    fired = {L: bool(compose(_bundle_for(L)).vetoes) for L in "ABCDEF"}
    n = sum(fired.values())
    assert n <= 4, (
        f"PREREG s6 bound: at most 4 of 6 adversarial tests may emit a veto; "
        f"got {n}. Fired on: {sorted(k for k, v in fired.items() if v)}")
    # The two anti-skepticism tests must be among the silent ones.
    assert not fired["C"], "C (true independence) must produce no veto"
    assert not fired["E"], "E (unknown-not-absent) must produce no veto here"
