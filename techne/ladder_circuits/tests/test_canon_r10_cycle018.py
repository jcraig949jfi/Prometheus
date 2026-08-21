"""CANON R10, cycle-018 extensions — the two-field verdict and the residue-class near-analogy.

Both come from external review (round 6) and both are sharper than what cycle 017 built:

- The verdict splits into (assumption status, conclusion status), because a broken assumption
  does not entail a false conclusion. (BROKEN, UNKNOWN) is a legitimate state, and reading it
  as a refutation is a new trap.
- The near-analogy hides the break in a residue-class property. At FIXED q, varying only the
  technique's parameter flips the verdict, so even an evaluator with PERFECT world knowledge is
  aliased — strictly stronger than cycle 017's witness, which needed two different techniques.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.aliasing import find_aliasing_witness  # noqa: E402
from techne.ladder_circuits.canon_r10_analogy import (  # noqa: E402
    ASSUMPTION_PROBES, BATTERY, OPEN_BATTERY, QR_BATTERY, W_F3, W_F7, W_Z,
    AssumptionTracingTransfer, UnknownCollapser, _is_nonsquare, derive_verdict, ground_truth,
    nonsquare_technique, run,
)

HONEST = AssumptionTracingTransfer()


# ---- the residue-class near-analogy ------------------------------------------------------------

def test_verdict_flips_with_the_parameter_at_fixed_q():
    """At q = 7: 3² = 2, so x² − 2 factors and the technique breaks; 3 and 5 are nonsquares
    mod 7, so those transfer. Same world, same technique family, same everything visible."""
    verdicts = {t.name: HONEST.transfer(t, W_F7).verdict for t, _w in QR_BATTERY}
    assert verdicts == {"nonsquare_2": "BREAKS", "nonsquare_3": "TRANSFERS",
                        "nonsquare_5": "TRANSFERS"}
    assert "3^2 = 2 mod 7" in HONEST.transfer(nonsquare_technique(2), W_F7).witness


def test_STRONGEST_ALIASING_WITNESS_perfect_world_knowledge_is_still_insufficient():
    """Cycle 017's witness needed two different techniques to alias a world pair. This one is
    stronger: the projection here is the ENTIRE (source, target) pair — everything there is to
    know about both worlds, not a feature subset — and it still fails, because the verdict is
    determined by a residue-class property carried inside the technique.

    This is what forces the composition the rung is actually about:
    technique → its own assumption → a target-world test.
    """
    projection = lambda tw: (tw[0].home.name, tw[1].name)      # complete world knowledge
    w = find_aliasing_witness(list(QR_BATTERY), projection, lambda tw: ground_truth(*tw))
    assert w is not None
    assert w.projection_value == ("Z", "F_7[t]")
    assert {w.left_truth, w.right_truth} == {True, False}


def test_the_two_instruments_are_independent_code_paths_that_agree():
    """The assumption is checked by a residue computation; the conclusion by sympy
    factorisation. They agree by mathematics, not by construction — which is what makes their
    agreement evidence rather than tautology."""
    for a in (2, 3, 5, 6, 10):
        for world in (W_F7, W_F3, W_Z):
            assumption_holds = ASSUMPTION_PROBES[
                f"{a} is a nonsquare in the constant field"](world)
            conclusion_holds = ground_truth(nonsquare_technique(a), world)
            assert assumption_holds == conclusion_holds


def test_world_features_are_byte_identical_across_the_QR_battery():
    """The premise of the aliasing claim, checked rather than asserted."""
    assert len({(t.home.char, t.home.q, w.char, w.q) for t, w in QR_BATTERY}) == 1


# ---- the two-field verdict and the UNKNOWN state -----------------------------------------------

def test_open_conclusion_yields_BROKEN_UNKNOWN_and_derives_to_UNVERIFIED():
    """Artin's primitive-root conjecture and the twin-prime conjecture are OPEN over ℤ — that
    half is not in doubt and is all this verdict rests on. Their function-field proofs lean on
    the constant field being FINITE, which ℤ does not supply, so the assumption is genuinely
    BROKEN with a witness available. The honest circuit still refuses to call it a refutation.
    """
    for tech, world in OPEN_BATTERY:
        v = HONEST.transfer(tech, world)
        assert (v.assumption_status, v.conclusion_status) == ("BROKEN", "UNKNOWN")
        assert v.verdict == "UNVERIFIED"
        assert ground_truth(tech, world) is None


def test_KILL_collapsing_UNKNOWN_into_a_refutation():
    """TRAP 5. The dishonest circuit differs from the honest one in one place: it reads a
    witnessed assumption violation as evidence against the conclusion. It is the most natural
    error available here, and it manufactures a refutation of the twin-prime conjecture.

    Note the shape of its 'witness': a restatement of the assumption violation, not a
    counterexample to the conclusion. No counterexample can exist, since the conclusion is open.
    """
    collapser = UnknownCollapser()
    for tech, world in OPEN_BATTERY:
        v = collapser.transfer(tech, world)
        assert v.verdict == "BREAKS"
        assert v.is_supported                      # it PASSES the cycle-017 artifact check
        assert "violated" in v.witness             # ...on a witness that witnesses nothing
        assert ground_truth(tech, world) is None   # there is nothing for it to have found


def test_the_two_fields_are_genuinely_orthogonal():
    """All four reachable combinations occur in the built batteries — the empirical case that
    the fields must not be collapsed into one label."""
    seen = set()
    for tech, world in list(BATTERY) + list(QR_BATTERY) + list(OPEN_BATTERY):
        v = HONEST.transfer(tech, world)
        seen.add((v.assumption_status, v.conclusion_status))
    assert ("PRESERVED", "SURVIVES") in seen      # ordinary transfer
    assert ("BROKEN", "REFUTED") in seen          # ordinary break
    assert ("BROKEN", "SURVIVES") in seen         # the harmless failure (Frobenius in F_3)
    assert ("BROKEN", "UNKNOWN") in seen          # not enough reality-bits


def test_derive_verdict_never_turns_UNKNOWN_into_a_refutation():
    """The rule, stated once and tested exhaustively over the status space."""
    for a in ("PRESERVED", "BROKEN"):
        assert derive_verdict(a, "UNKNOWN") == "UNVERIFIED"
        assert derive_verdict(a, "REFUTED") == "BREAKS"
        assert derive_verdict(a, "SURVIVES") == "TRANSFERS"


def test_cycle_017_scoring_is_unaffected_by_the_new_state():
    """Regression: the decidable battery scores exactly as it did before UNKNOWN existed, and
    the scorers ignore open entries rather than counting them as breaks."""
    from techne.ladder_circuits.canon_r10_analogy import score, verdict_only_score
    r = run(HONEST)
    assert verdict_only_score(r) == {"catch_rate": 1.0, "phantom_break_rate": 0.0}
    open_r = run(HONEST, list(OPEN_BATTERY))
    assert verdict_only_score(open_r) == {"catch_rate": 0.0, "phantom_break_rate": 0.0}
    assert score(open_r)["misnamed"] == 0.0


def test_REPAIR_the_strict_artifact_check_stops_the_collapser():
    """The cycle-017 artifact check asked only whether a witness FIELD was populated, and the
    collapser satisfies it by filling that field with a restatement of the assumption violation.
    The repair: a BREAKS claim requires the CONCLUSION to have been refuted.

    Both circuits are re-checked so the repair is shown not to cost the honest one anything.
    """
    from techne.ladder_circuits.canon_r10_analogy import score
    collapsed = [UnknownCollapser().transfer(t, w) for t, w in OPEN_BATTERY]
    assert all(v.is_supported for v in collapsed)              # the old check: passes
    assert not any(v.is_supported_strict for v in collapsed)   # the repair: fails, every one

    honest = run(HONEST)
    assert score(honest)["unsupported"] == 0.0
    assert score(honest)["unsupported_strict"] == 0.0
