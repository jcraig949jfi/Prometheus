"""Track B: `transform` on ca_density_v0 -- the exact-symmetry null arm.

WHAT AN EXACT SYMMETRY BUYS. Reflection and complementation are symmetries of
the density-classification task itself, not approximations of one. So a
transformed arm must reproduce its untransformed twin's accuracy EXACTLY --
not closely, not on average, bit for bit. That makes it a null with no
tolerance to argue about: any difference is a defect in the instrument, and
there is no reading of a discrepancy that is a scientific result.

The tests below establish the symmetry at the level it is claimed, which is
the dynamics: `step(reverse(s), T_reflect) == reverse(step(s, T))` over random
lattices, and the complement equivalent. Accuracy equality then follows rather
than being hoped for -- and is also checked, because a proof of the step law
does not by itself prove the wrapper applied it to all three of the table, the
sample and the target.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

np = pytest.importorskip("numpy")
core = pytest.importorskip("herakles.evca.core")

from viv import ca_density as _ca                            # noqa: E402
from viv import kinds as _kinds                              # noqa: E402

GKL = "0504058705000f77037755837bffb77f"
GENOMES = pytest.importorskip("herakles.evca.genomes")

BASE = {"rule_hex": GKL, "radius": 3, "n_cells": 21, "steps": 42, "n_ic": 32,
        "ic_density_set": [None], "success_criterion": "at_T",
        "transform": "none"}


def payload(**kw):
    return dict(BASE, **kw)


# ===========================================================================
# 1. THE STEP LAW -- the symmetry, at the level it is claimed
# ===========================================================================

def test_reflection_commutes_with_one_update():
    """step(reverse(s), T') == reverse(step(s, T)) for every lattice tried.

    This is the whole justification for the index permutation, re-earned on
    random data rather than trusted to a paragraph about bit order."""
    table = core.decode_table(GKL)
    tr = _ca._reflect_table(table, np)
    rng = np.random.default_rng(20260910)
    s = rng.integers(0, 2, size=(64, 21), dtype=np.uint8)
    lhs = core.step(s[:, ::-1].copy(), tr)
    rhs = core.step(s, table)[:, ::-1]
    assert np.array_equal(lhs, rhs)


def test_complementation_commutes_with_one_update():
    table = core.decode_table(GKL)
    tc = _ca._complement_table(table, np)
    rng = np.random.default_rng(20260910)
    s = rng.integers(0, 2, size=(64, 21), dtype=np.uint8)
    lhs = core.step((1 - s).astype(np.uint8), tc)
    rhs = 1 - core.step(s, table)
    assert np.array_equal(lhs, rhs)


def test_reflect_complement_commutes_too():
    table = core.decode_table(GKL)
    t2, _ = _ca.apply_transform("reflect_complement", table,
                                np.zeros((1, 21), dtype=np.uint8), np)
    rng = np.random.default_rng(7)
    s = rng.integers(0, 2, size=(32, 21), dtype=np.uint8)
    s2 = (1 - s[:, ::-1]).astype(np.uint8)
    lhs = core.step(s2, t2)
    rhs = (1 - core.step(s, table)[:, ::-1]).astype(np.uint8)
    assert np.array_equal(lhs, rhs)


def test_each_transform_is_an_involution_on_the_table():
    """Applying it twice returns the original rule. A transform that did not
    would not be a symmetry group element and the null would be meaningless."""
    table = core.decode_table(GKL)
    ics = np.zeros((1, 21), dtype=np.uint8)
    for name in ("reflect", "complement", "reflect_complement"):
        once, _ = _ca.apply_transform(name, table, ics, np)
        twice, _ = _ca.apply_transform(name, once, ics, np)
        assert np.array_equal(twice, table), name


# ===========================================================================
# 2. THE NULL -- accuracy is IDENTICAL, for every genome and both criteria
# ===========================================================================

@pytest.mark.parametrize("name", sorted(GENOMES.GENOMES))
@pytest.mark.parametrize("transform",
                         ["reflect", "complement", "reflect_complement"])
def test_accuracy_is_exactly_unchanged_under_every_symmetry(name, transform):
    rule = GENOMES.GENOMES[name]["hex"]
    base = _ca.run(payload(rule_hex=rule), seed=20260908)
    moved = _ca.run(payload(rule_hex=rule, transform=transform), seed=20260908)
    assert moved["accuracy"] == base["accuracy"], (
        "%s under %s: %s != %s -- an EXACT symmetry moved the number, which "
        "is an instrument defect and not a finding"
        % (name, transform, moved["accuracy"], base["accuracy"]))
    assert moved["accuracy_at_T"] == base["accuracy_at_T"]
    assert moved["accuracy_stable"] == base["accuracy_stable"]
    assert moved["n_incorrect_at_T"] == base["n_incorrect_at_T"]
    assert moved["n_incorrect_stable"] == base["n_incorrect_stable"]


def test_the_witness_set_is_the_same_ICs_under_every_symmetry():
    """Not just the same COUNT: the same initial conditions fail, because a
    transformed run is the image of its twin rather than a fresh sample."""
    base = _ca.run(payload(), seed=20260908)
    for transform in ("reflect", "complement", "reflect_complement"):
        moved = _ca.run(payload(transform=transform), seed=20260908)
        assert moved["misclassified_ic"] == base["misclassified_ic"], transform
        assert moved["mask_digest_at_T"] == base["mask_digest_at_T"], transform


def test_the_transform_is_recorded_and_the_rule_that_ran_is_named():
    base = _ca.run(payload(), seed=20260908)
    assert base["transform"] == "none"
    assert base["transformed_rule_hex"] == GKL
    assert base["spacetime_is_image_of_untransformed"] is True

    moved = _ca.run(payload(transform="reflect"), seed=20260908)
    assert moved["transform"] == "reflect"
    assert moved["transformed_rule_hex"] != GKL
    # ... and it is a REAL rule that round-trips through the library.
    assert core.encode_table(core.decode_table(moved["transformed_rule_hex"])) \
        == moved["transformed_rule_hex"]
    assert moved["spacetime_is_image_of_untransformed"] is False


def test_the_fixed_point_facts_move_the_way_the_symmetry_says_they_should():
    """Reflection cannot change whether a uniform state is fixed; complement
    SWAPS the two facts. A transform that left them both alone would not be
    doing anything to the rule."""
    base = _ca.run(payload(), seed=20260908)
    refl = _ca.run(payload(transform="reflect"), seed=20260908)
    comp = _ca.run(payload(transform="complement"), seed=20260908)
    assert refl["all_zeros_fixed"] == base["all_zeros_fixed"]
    assert refl["all_ones_fixed"] == base["all_ones_fixed"]
    assert comp["all_zeros_fixed"] == base["all_ones_fixed"]
    assert comp["all_ones_fixed"] == base["all_zeros_fixed"]


# ===========================================================================
# 3. THE CONTRACT
# ===========================================================================

def test_transform_is_a_required_parameter_with_no_default():
    k = _kinds.get("ca_density_v0")
    assert "transform" in k.params
    missing = {k2: v for k2, v in BASE.items() if k2 != "transform"}
    reasons = k.check(missing)
    assert any("transform" in r for r in reasons), reasons


def test_an_unknown_transform_is_refused():
    with pytest.raises(Exception) as e:
        _ca.run(payload(transform="rotate"), seed=1)
    assert "EXACT symmetries" in str(e.value)


def test_a_transformed_spec_has_its_own_sealed_identity():
    from viv import spec as _spec
    from conftest import ONE_REPEAT

    def s(t):
        return {"spec_version": 3, "world": {"seed_root": 20260908},
                "hypothesis": "h", "prediction": None,
                "work": {"kind": "ca_density_v0", "payload": payload(transform=t)},
                "outcome_rule": {"field": "accuracy", "op": ">=", "value": 0.5,
                                 "if_true": "SURVIVED", "if_false": "FALSIFIED",
                                 "if_indeterminate": "INCONCLUSIVE",
                                 "aggregate": "first"},
                "pew": None, "repeat": dict(ONE_REPEAT)}
    hashes = {t: _spec.spec_hash(s(t)) for t in _ca.TRANSFORMS}
    assert len(set(hashes.values())) == len(_ca.TRANSFORMS), hashes



# ===========================================================================
# F-20: the two flags Herakles's c3_null_check needs and cannot infer
# ===========================================================================

def test_the_flags_are_measured_not_declared_from_the_transform_name():
    """A wrapper that answered these from a lookup keyed on the transform name
    would be asserting it applied the transform correctly -- which is the one
    thing the null check exists to verify independently. Both are read off the
    arrays."""
    base = _ca.run(payload(), seed=20260908)
    assert base["ic_transformed"] is False
    assert base["majority_target_flipped"] is False


@pytest.mark.parametrize("transform,ic,flip", [
    ("reflect", True, False),
    ("complement", True, True),
    ("reflect_complement", True, True),
])
def test_each_symmetry_reports_the_right_pair(transform, ic, flip):
    """Reflection moves the sample and preserves density, so the target does
    NOT flip. Complement moves both. Getting this pair wrong is exactly how a
    null check reports a break that did not happen."""
    out = _ca.run(payload(transform=transform), seed=20260908)
    assert out["ic_transformed"] is ic, transform
    assert out["majority_target_flipped"] is flip, transform


def test_herakles_null_check_returns_IDENTICAL_on_our_own_rows():
    """The end of F-20: his checker, our rows, no fields supplied by hand.

    Recorded as INDETERMINATE 72/72 before the flags existed, because a row
    that does not say whether the INITIAL CONDITION moved has not run the
    symmetry test -- rule-only is not the symmetry.
    """
    nc = pytest.importorskip("herakles.evca.c3_null_check")
    fn = None
    for name in ("check_pair", "compare", "check", "c3_null_check"):
        fn = getattr(nc, name, None)
        if callable(fn):
            break
    if fn is None:                                   # pragma: no cover
        pytest.skip("c3_null_check exposes no comparison entry point")
    base = _ca.run(payload(), seed=20260908)
    for transform in ("reflect", "complement", "reflect_complement"):
        moved = _ca.run(payload(transform=transform), seed=20260908)
        verdict = fn(base, moved)
        got = verdict.get("verdict") if isinstance(verdict, dict) else verdict
        assert got == "IDENTICAL", (transform, verdict)
