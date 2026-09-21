"""Slice 2B invariants: lineage independence, tribunal isolation, bounded
structural search. Written BEFORE the implementation (AMENDMENT_3).

The two properties that must be ENFORCED rather than promised:
  - development entropy and tribunal entropy come from disjoint domains,
    and no lineage identifier reaches the tribunal;
  - the tribunal cannot be constructed before a generation-8 artifact is
    frozen, and is never handed to an evolving lineage.
"""
import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine as E  # noqa: E402

LINEAGES = ("L-001", "L-002", "L-003")


# ------------------------------------------------- frozen derivation rule
def test_dev_entropy_matches_the_frozen_derivation_rule():
    for lid in LINEAGES:
        for gen in (0, 3, 8):
            want = int(hashlib.sha256(
                ("APHRODITE/ENGINE/DEV/v1/%s/%d" % (lid, gen)).encode()
            ).hexdigest()[:16], 16)
            assert E.dev_entropy(lid, gen) == want


def test_independent_lineages_get_different_development_entropy():
    seen = {E.dev_entropy(lid, 0) for lid in LINEAGES}
    assert len(seen) == len(LINEAGES)


def test_search_entropy_is_a_separate_domain_from_development():
    for lid in LINEAGES:
        assert E.search_entropy(lid) != E.dev_entropy(lid, 0)


# ------------------------------------------------------ tribunal isolation
def test_tribunal_entropy_contains_no_lineage_identifier():
    """Disjoint domain: the tribunal's entropy is a function of the class and
    index ONLY, so no lineage can influence or predict it."""
    for cls in E.HEADROOM_FAMILIES:
        want = int(hashlib.sha256(
            ("APHRODITE/ENGINE/TRIBUNAL/v1/%s/0" % cls).encode()
        ).hexdigest()[:16], 16)
        assert E.tribunal_entropy(cls, 0) == want
        for lid in LINEAGES:
            assert lid not in "APHRODITE/ENGINE/TRIBUNAL/v1/%s/0" % cls


def test_tribunal_refuses_to_exist_before_the_freeze():
    with pytest.raises(E.BoundaryViolation):
        E.Tribunal.after_freeze(None)
    lin = E.Lineage(seed=1, base=E.base_image(), lineage_id="L-001")
    lin.evolve(generations=2, escrow=E.Escrow(5000))
    with pytest.raises(ValueError):
        E.Tribunal.after_freeze(lin.extract(2))     # not the frozen generation


def test_an_evolving_lineage_is_never_given_a_tribunal():
    lin = E.Lineage(seed=1, base=E.base_image(), lineage_id="L-001")
    assert not any("tribunal" in k.lower() for k in vars(lin))


# --------------------------------------------- the tribunal is actually hostile
def test_the_numtheory_tribunal_breaks_the_coprime_shortcut():
    """RULING 4: counterexamples must cover regions where a*b+1 fails."""
    art = E.Artifact.from_modules(dict(E.base_image()))
    art = E.Artifact.from_modules(
        dict(art.modules(), search=art.modules()["search"] + E.shortcut_solver_source()),
        generation=E.FROZEN_GENERATION)
    trib = E.Tribunal.after_freeze(art)
    assert trib.score(art, "numtheory")["counterexample_accuracy"] <= 0.10


def test_metamorphic_checks_reject_the_shortcut_without_an_oracle():
    art = E.Artifact.from_modules(dict(E.base_image()))
    art = E.Artifact.from_modules(
        dict(art.modules(), search=art.modules()["search"] + E.shortcut_solver_source()),
        generation=E.FROZEN_GENERATION)
    trib = E.Tribunal.after_freeze(art)
    assert trib.score(art, "numtheory")["metamorphic_pass"] is False


def test_the_tribunal_accepts_a_correct_solver():
    pos = E.Artifact.from_modules(dict(E.positive_control_artifact().modules()),
                                  generation=E.FROZEN_GENERATION)
    trib = E.Tribunal.after_freeze(pos)
    for cls in E.HEADROOM_FAMILIES:
        r = trib.score(pos, cls)
        assert r["held_out_accuracy"] == 1.0
        assert r["counterexample_accuracy"] == 1.0
        assert r["metamorphic_pass"] is True


# ------------------------------------------------ the structural gate (C6)
def test_structural_detector_rejects_single_expression_dispatch():
    art = E.Artifact.from_modules(
        dict(E.base_image(), search=E.base_image()["search"] + E.shortcut_solver_source()))
    assert E.structural_change(art) is False


def test_the_grammar_can_express_a_bounded_helper_with_control_flow():
    """If Euclid is not EXPRESSIBLE, C6 is unreachable by construction and the
    slice would be testing nothing."""
    src = E.helper_solver_source("numtheory", e1="y", e2="(x % y)",
                                 answer="(h(nums[0], nums[1]) + ((nums[0] * nums[1]) "
                                        "// h(nums[0], nums[1])))")
    art = E.Artifact.from_modules(dict(E.base_image(), search=E.base_image()["search"] + src),
                                  generation=E.FROZEN_GENERATION)
    assert E.structural_change(art) is True
    trib = E.Tribunal.after_freeze(art)
    r = trib.score(art, "numtheory")
    assert r["held_out_accuracy"] == 1.0 and r["counterexample_accuracy"] == 1.0
    assert r["metamorphic_pass"] is True
