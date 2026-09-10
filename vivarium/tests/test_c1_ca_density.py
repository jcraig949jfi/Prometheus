"""C1: `ca_density_v0` wraps Herakles's EvCA library, and reproduces its golden.

PARITY IS THE POINT. `golden_c1b.json` is Herakles's regression anchor for
`herakles/evca`. If the six recovered genomes do not come back through the
wrapper with the library's own numbers, the wrapper has changed the science it
was supposed to carry -- and a wrapper that quietly changes a number is worse
than no wrapper.

The wrapper decides nothing about cellular automata. These tests check exactly
that: the encoding, the bit order, the r=3 refusal and the odd-N refusal are
all the library's, and the wrapper surfaces them unaltered.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from viv import executors as _ex
from viv import kinds as _kinds
from viv.ca_density import SUCCESS_CRITERIA, WITNESS_LIMIT, _evca

REPO = Path(__file__).resolve().parent.parent.parent
GOLDEN = REPO / "herakles" / "evca" / "tests" / "golden_c1b.json"

pytestmark = pytest.mark.skipif(
    not GOLDEN.exists(),
    reason="herakles/evca is not on this branch (WP-C1, 3466481b9)")


def golden():
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def spec_for(rule_hex, *, criterion="at_T", n_cells=21, steps=42, n_ic=64,
             densities=None, radius=3, seed=20260908, transform="none"):
    # `transform` joined the contract on 2026-09-10 (Track B) and has NO
    # default in the kind, so every C1 payload names it. "none" is the
    # untransformed run these parity tests have always described, and the
    # golden results below are unchanged by its arrival -- which is itself
    # asserted, in tests/test_ca_transform.py.
    return {"spec_version": 3, "world": {"seed_root": seed},
            "hypothesis": "C1 parity", "prediction": None,
            "work": {"kind": "ca_density_v0",
                     "payload": {"rule_hex": rule_hex, "radius": radius,
                                 "n_cells": n_cells, "steps": steps,
                                 "n_ic": n_ic,
                                 "ic_density_set": densities
                                 if densities is not None else [None],
                                 "success_criterion": criterion,
                                 "transform": transform}},
            "outcome_rule": {"field": "accuracy", "op": ">=", "value": 0.0,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE",
                             "aggregate": "first"},
            "pew": None,
            "repeat": {"count": 1, "order": "sequential",
                       "seed_derivation": "constant", "state": "reset",
                       "budget": {"max_seconds": 300, "max_observations": 1}}}


def run(rule_hex, **kw):
    seed = kw.pop("seed", 20260908)
    return _ex.run(spec_for(rule_hex, seed=seed, **kw), seed=seed,
                   state=None)


# ------------------------------------------------------------- the golden

def test_c1_all_six_genomes_reproduce_the_golden_accuracy():
    g = golden()
    cfg = g["config"]
    assert cfg == {"n_ics": 64, "n_cells": 21, "steps": 42, "seed": 20260908}
    for name, want in g["rules"].items():
        out = run(want["hex"], criterion="at_T", n_cells=cfg["n_cells"],
                  steps=cfg["steps"], n_ic=cfg["n_ics"], seed=cfg["seed"])
        assert out["accuracy_at_T"] == want["accuracy"], name
        assert out["accuracy"] == want["accuracy"], name
        assert out["n_incorrect_at_T"] == want["n_incorrect"], name


def test_c1_the_witness_and_its_digest_match_the_golden():
    g = golden()
    cfg = g["config"]
    for name, want in g["rules"].items():
        out = run(want["hex"], criterion="at_T", n_cells=cfg["n_cells"],
                  steps=cfg["steps"], n_ic=cfg["n_ics"], seed=cfg["seed"])
        assert out["misclassified_ic"] == want["witness"], name
        assert out["mask_digest_at_T"] == want["correct_mask_digest"], name
        assert out["witness_truncated"] == want["witness_truncated"], name


def test_c1_the_fixed_point_facts_match_the_golden():
    g = golden()
    cfg = g["config"]
    for name, want in g["rules"].items():
        out = run(want["hex"], n_cells=cfg["n_cells"], steps=cfg["steps"],
                  n_ic=cfg["n_ics"], seed=cfg["seed"])
        assert out["all_zeros_fixed"] == want["uniform_fixed_points"][
            "all_zeros_fixed"], name
        assert out["all_ones_fixed"] == want["uniform_fixed_points"][
            "all_ones_fixed"], name


def test_c1_the_spacetime_digest_matches_the_goldens_selected_trajectory():
    g = golden()
    sel = g["selected_trajectory"]
    inp = sel["inputs"]
    out = run(inp["rule_hex"], n_cells=inp["n_cells"], steps=inp["steps"],
              n_ic=8, seed=inp["seed"])
    assert out["spacetime_digest"] == sel["digest"]


# --------------------------------------------- both masks (correction 2)

def test_c1_both_accuracies_are_always_reported_whichever_is_scored():
    g = golden()
    out = run(g["rules"]["GKL"]["hex"], criterion="stable")
    for f in ("accuracy_at_T", "accuracy_stable", "n_incorrect_at_T",
              "n_incorrect_stable", "mask_digest_at_T", "mask_digest_stable",
              "criteria_agree"):
        assert f in out, f
    assert out["success_criterion"] == "stable"
    assert out["accuracy"] == out["accuracy_stable"]


def test_c1_accuracy_follows_the_declared_criterion():
    g = golden()
    hexr = g["rules"]["exp"]["hex"]
    at_t = run(hexr, criterion="at_T")
    stable = run(hexr, criterion="stable")
    assert at_t["accuracy"] == at_t["accuracy_at_T"]
    assert stable["accuracy"] == stable["accuracy_stable"]
    # both runs report BOTH numbers identically; only the scoring differs
    assert at_t["accuracy_at_T"] == stable["accuracy_at_T"]
    assert at_t["accuracy_stable"] == stable["accuracy_stable"]


def test_c1_the_criteria_agree_when_both_uniform_states_are_fixed():
    """The library's own reasoning: at_T and 'stays there' can only differ if
    a uniform configuration is not a fixed point. All six golden rules fix
    both, so on this fixture the two masks must coincide -- and the wrapper
    must SAY they coincide rather than leaving a reader to assume it."""
    g = golden()
    for name, want in g["rules"].items():
        out = run(want["hex"], criterion="at_T")
        assert out["all_zeros_fixed"] and out["all_ones_fixed"], name
        assert out["criteria_agree"] is True, name
        assert out["accuracy_at_T"] == out["accuracy_stable"], name


def test_c1_the_two_criteria_are_separable_and_the_wrapper_separates_them():
    """A deterministic construction, so the case the two masks exist for is
    exercised rather than assumed.

    Rule: every entry 1 except 127 -> 0. Then all-ones maps to all-zeros and
    all-zeros maps back to all-ones, so the lattice oscillates with period 2
    and NEITHER uniform configuration is a fixed point. Start from the
    all-ones lattice (density 1.0) with a target of 1: after an EVEN number of
    updates it is back at all-ones, so it is correct AT T -- and one further
    update leaves it, so it is not stable there.
    """
    import numpy as np
    _, core = _evca()
    table = np.ones(128, dtype=np.uint8)
    table[127] = 0
    rule = core.encode_table(table)

    even = run(rule, n_cells=21, steps=42, n_ic=8, densities=[1.0])
    assert even["all_zeros_fixed"] is False
    assert even["all_ones_fixed"] is False
    assert even["accuracy_at_T"] == 1.0
    assert even["accuracy_stable"] == 0.0
    assert even["criteria_agree"] is False
    assert even["mask_digest_at_T"] != even["mask_digest_stable"]
    assert even["n_incorrect_at_T"] == 0
    assert even["n_incorrect_stable"] == 8

    # ...and the scored number really follows the declared criterion.
    assert run(rule, n_cells=21, steps=42, n_ic=8, densities=[1.0],
               criterion="at_T")["accuracy"] == 1.0
    assert run(rule, n_cells=21, steps=42, n_ic=8, densities=[1.0],
               criterion="stable")["accuracy"] == 0.0

    # On an ODD number of updates the lattice is at all-zeros against a target
    # of 1, so it is wrong under both readings and they agree again.
    odd = run(rule, n_cells=21, steps=43, n_ic=8, densities=[1.0])
    assert odd["accuracy_at_T"] == 0.0 and odd["accuracy_stable"] == 0.0
    assert odd["criteria_agree"] is True


def test_c1_stable_is_always_a_subset_of_at_T():
    """The invariant behind the pair: being in the correct state AND holding
    it cannot be commoner than being in it. True for every rule, so it is the
    check that would catch the two masks being crossed or swapped."""
    g = golden()
    for name, want in g["rules"].items():
        out = run(want["hex"])
        assert out["accuracy_stable"] <= out["accuracy_at_T"], name
        assert out["n_incorrect_stable"] >= out["n_incorrect_at_T"], name


def test_c1_the_golden_fixture_cannot_exercise_the_separation():
    """Recorded so nobody reads the golden as evidence the criteria are the
    same thing: all six recovered genomes fix BOTH uniform configurations, so
    on this fixture the two masks provably coincide."""
    g = golden()
    for name, want in g["rules"].items():
        fp = want["uniform_fixed_points"]
        assert fp["all_zeros_fixed"] and fp["all_ones_fixed"], name


# ---------------------------------------- conventions are the library's

def test_c1_the_table_encoding_is_the_librarys():
    """Correction 1: no convention decision here. The wrapper's answer for a
    rule must equal the library's for the table `decode_table` produces."""
    _, core = _evca()
    g = golden()
    hexr = g["rules"]["par"]["hex"]
    ics = core.make_ics(64, 21, 20260908)
    direct = core.classify(core.decode_table(hexr), ics, 42,
                           witness_limit=WITNESS_LIMIT)
    out = run(hexr, criterion="at_T")
    assert out["accuracy_at_T"] == direct["accuracy"]
    assert out["mask_digest_at_T"] == direct["correct_mask_digest"]
    assert out["misclassified_ic"] == direct["witness"]


@pytest.mark.parametrize("radius", [1, 2, 4, 0])
def test_c1_an_unsupported_radius_is_refused_by_the_library(radius):
    _, core = _evca()
    g = golden()
    with pytest.raises(core.EvcaError) as exc:
        run(g["rules"]["maj"]["hex"], radius=radius)
    assert "not supported" in str(exc.value)


def test_c1_an_even_lattice_is_refused_by_the_library():
    _, core = _evca()
    g = golden()
    with pytest.raises(core.EvcaError):
        run(g["rules"]["maj"]["hex"], n_cells=20)


def test_c1_a_malformed_rule_is_refused_by_the_library():
    _, core = _evca()
    for bad in ("abc", "z" * 32, 12345):
        with pytest.raises(core.EvcaError):
            run(bad)


# ------------------------------------------------- initial conditions

def test_c1_n_ic_is_per_density_and_blocks_concatenate_in_order():
    g = golden()
    hexr = g["rules"]["GKL"]["hex"]
    one = run(hexr, n_ic=16, densities=[None])
    three = run(hexr, n_ic=16, densities=[None, 0.25, 0.75])
    assert one["n_ic_total"] == 16
    assert three["n_ic_total"] == 48


def test_c1_a_single_density_set_reproduces_the_library_called_directly():
    """Block 0 is seeded with the run's seed unchanged, which is what makes
    the golden reproduce at all."""
    _, core = _evca()
    g = golden()
    hexr = g["rules"]["particle1"]["hex"]
    ics = core.make_ics(64, 21, 20260908)
    direct = core.classify(core.decode_table(hexr), ics, 42,
                           witness_limit=WITNESS_LIMIT)
    out = run(hexr, criterion="at_T")
    assert out["accuracy_at_T"] == direct["accuracy"]


def test_c1_a_biased_density_is_a_different_ensemble():
    """The library says so; the wrapper must not blur it."""
    g = golden()
    hexr = g["rules"]["par"]["hex"]
    unbiased = run(hexr, densities=[None])
    biased = run(hexr, densities=[0.2])
    assert unbiased["mask_digest_at_T"] != biased["mask_digest_at_T"]


@pytest.mark.parametrize("bad", [[], "0.5", [True], ["x"], [2.0], [-0.1]])
def test_c1_a_malformed_density_set_is_refused(bad):
    _, core = _evca()
    g = golden()
    with pytest.raises(core.EvcaError):
        run(g["rules"]["maj"]["hex"], densities=bad)


# ---------------------------------------------------- the kind contract

def test_c1_the_result_satisfies_the_declared_schema():
    g = golden()
    out = run(g["rules"]["GKL"]["hex"])
    _kinds.get("ca_density_v0").check_result(
        dict(out), truncation=out.get("_truncated"))


def test_c1_the_kind_is_stateless_so_persist_is_refused():
    from viv import spec as _spec
    k = _kinds.get("ca_density_v0")
    assert k.stateful is False
    s = spec_for(golden()["rules"]["maj"]["hex"])
    s["repeat"]["state"] = "persist"
    s["repeat"]["count"] = 2
    s["repeat"]["budget"]["max_observations"] = 2
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(s)
    assert any("stateless" in r for r in exc.value.reasons)


@pytest.mark.parametrize("bad", ["reached", "AT_T", "", None])
def test_c1_an_undeclared_success_criterion_is_refused(bad):
    _, core = _evca()
    g = golden()
    with pytest.raises(core.EvcaError) as exc:
        run(g["rules"]["maj"]["hex"], criterion=bad)
    assert "success_criterion" in str(exc.value)


def test_c1_re_execution_is_bit_identical():
    g = golden()
    hexr = g["rules"]["exp"]["hex"]
    a, b = run(hexr), run(hexr)
    assert a == b


def test_c1_the_witness_is_bounded_and_declares_its_truncation():
    """256 unbiased ICs on `maj`, which misclassifies most of them, exceeds
    the 64-element bound."""
    g = golden()
    out = run(g["rules"]["maj"]["hex"], n_ic=256)
    assert len(out["misclassified_ic"]) == WITNESS_LIMIT
    assert out["witness_truncated"] is True
    assert out["n_incorrect_at_T"] > WITNESS_LIMIT
    # `_truncated` is the validation channel, not a result field: executors.run
    # consumes it when checking the schema, so it must NOT survive into the
    # observation. `witness_truncated` is the declared, durable fact.
    assert "_truncated" not in out


def test_c1_the_criteria_vocabulary_is_closed():
    assert SUCCESS_CRITERIA == ("at_T", "stable")
