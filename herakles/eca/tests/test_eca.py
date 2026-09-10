"""H5 alpha tests for eca_rule_eval_v1.

The convention is re-earned rather than trusted: each of the six named rules
is DERIVED from its behavioural definition and the derived number is compared
with the published one. A test that only asserted "rule 90 does what rule 90
does" would prove nothing about the index convention.
"""
from __future__ import annotations

import os
import subprocess
import sys

import numpy as np
import pytest

from herakles import eca

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "..", "..", ".."))


# ---------------------------------------------------------------------------
# The six hand-derived rules. This IS the convention check.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,expected,derive", eca.HAND_DERIVED)
def test_hand_derived_rules_match_their_numbers(name, expected, derive):
    assert derive() == expected, name


def test_the_wrong_index_convention_does_not_also_fit():
    """If it did, the test above would be consistent rather than identifying.

    Under index = left + 2*centre + 4*right the shift rules swap, so deriving
    'output = left neighbour' would give 170 instead of 240.
    """
    t = np.zeros(eca.TABLE_BITS, dtype=np.uint8)
    for idx in range(eca.TABLE_BITS):
        left, centre, right = idx & 1, (idx >> 1) & 1, (idx >> 2) & 1
        t[idx] = left
    assert eca.table_to_rule(t) == 170            # NOT 240
    assert eca.derive_shift_right() == 240        # the pinned convention


def test_rule_table_round_trip_over_all_256():
    for r in range(eca.N_RULES):
        assert eca.table_to_rule(eca.rule_table(r)) == r


def test_all_256_rules_obey_the_output_formula():
    """The alpha exit condition: every rule, every neighbourhood."""
    for r in range(eca.N_RULES):
        t = eca.rule_table(r)
        for left in (0, 1):
            for centre in (0, 1):
                for right in (0, 1):
                    idx = 4 * left + 2 * centre + right
                    assert t[idx] == ((r >> idx) & 1), (r, idx)


# ---------------------------------------------------------------------------
# Hand-computed dynamics
# ---------------------------------------------------------------------------

def test_hand_computed_single_step_rule_90():
    """Rule 90 is left XOR right, so a lone 1 becomes two 1s either side."""
    s = np.array([[0, 0, 0, 1, 0, 0, 0]], dtype=np.uint8)
    got = eca.step(s, 90)[0].tolist()
    assert got == [0, 0, 1, 0, 1, 0, 0]


def test_hand_computed_shifts_move_the_declared_way():
    s = np.array([[0, 0, 0, 1, 0, 0, 0]], dtype=np.uint8)
    # 170: output = right neighbour, so the 1 moves toward lower index
    assert eca.step(s, 170)[0].tolist() == [0, 0, 1, 0, 0, 0, 0]
    # 240: output = left neighbour, so the 1 moves toward higher index
    assert eca.step(s, 240)[0].tolist() == [0, 0, 0, 0, 1, 0, 0]


def test_hand_computed_constants_and_identity():
    s = np.array([[1, 0, 1, 1, 0, 0, 1]], dtype=np.uint8)
    assert eca.step(s, 0)[0].tolist() == [0] * 7
    assert eca.step(s, 255)[0].tolist() == [1] * 7
    assert eca.step(s, 204)[0].tolist() == s[0].tolist()


def test_ring_wraps_at_both_ends():
    """A 1 at index 0 must reach index n-1 under the right-shift rule."""
    n = 7
    s = np.zeros((1, n), dtype=np.uint8)
    s[0, 0] = 1
    assert eca.step(s, 240)[0].tolist()[1] == 1
    s2 = np.zeros((1, n), dtype=np.uint8)
    s2[0, 0] = 1
    assert eca.step(s2, 170)[0].tolist()[n - 1] == 1


def test_index_convention_on_a_hand_worked_lattice():
    s = np.array([[1, 0, 0]], dtype=np.uint8)     # n = 3, minimum ring
    idx = eca.neighbourhood_index(s)[0].tolist()
    # cell 0: left = cell 2 = 0, centre = 1, right = cell 1 = 0 -> 2
    # cell 1: left = 1, centre = 0, right = 0 -> 4
    # cell 2: left = 0, centre = 0, right = cell 0 = 1 -> 1
    assert idx == [2, 4, 1]


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def test_rule_numbers_outside_the_range_are_refused():
    for bad in (-1, 256, 1000, 1.5, "90", True, None):
        with pytest.raises(eca.EcaError):
            eca.require_rule(bad)


def test_small_lattices_and_bad_steps_refused():
    for bad in (0, 1, 2):
        with pytest.raises(eca.EcaError):
            eca.require_lattice(bad)
    eca.require_lattice(3)                     # the minimum ring is legal
    with pytest.raises(eca.EcaError):
        eca.require_steps(-1)
    with pytest.raises(eca.EcaError):
        eca.require_steps(2.5)


def test_even_lattices_are_allowed_here_unlike_the_radius_3_kind():
    """No majority is computed, so no tie can arise and no rule is needed."""
    assert eca.require_lattice(8) == 8
    s = np.zeros((1, 8), dtype=np.uint8)
    assert eca.step(s, 204).shape == (1, 8)


def test_enumeration_is_bounded():
    with pytest.raises(eca.EcaError):
        eca.all_configurations(21)


# ---------------------------------------------------------------------------
# The assay
# ---------------------------------------------------------------------------

def test_all_configurations_is_complete_and_ordered():
    c = eca.all_configurations(7)
    assert c.shape == (128, 7)
    assert c[0].tolist() == [0] * 7
    assert c[-1].tolist() == [1] * 7
    # ascending integer order
    vals = [int("".join(map(str, row)), 2) for row in c]
    assert vals == list(range(128))


def test_behaviour_is_deterministic_and_replayable():
    a = eca.behaviour_digest(110, 7, 8)
    b = eca.behaviour_digest(110, 7, 8)
    assert a == b
    assert eca.behaviour_digest(110, 7, 9) != a       # horizon is part of it
    assert eca.behaviour_digest(110, 9, 8) != a       # so is lattice size


def test_constant_rules_collapse_to_one_behaviour_each():
    z = eca.behaviour(0, 7, 8)
    assert (z == 0).all()
    o = eca.behaviour(255, 7, 8)
    assert (o == 1).all()


def test_equivalence_classes_partition_all_256_rules():
    """Deduplication by observable behaviour, with classes retained."""
    classes = eca.equivalence_classes(7, 8)
    members = sorted(r for group in classes.values() for r in group)
    assert members == list(range(eca.N_RULES))
    assert sum(len(g) for g in classes.values()) == eca.N_RULES
    # every rule appears exactly once
    assert len(set(members)) == eca.N_RULES


def test_identity_and_a_period_8_shift_are_indistinguishable_at_this_scope():
    """A real, checkable degeneracy of the declared scope.

    On a 7-cell ring after 8 steps, shifting by one each step returns the
    lattice to a rotation by 8 mod 7 = 1, so shift is NOT identity here. This
    test records what the scope can and cannot separate rather than assuming.
    """
    same = eca.behaviour_digest(204, 7, 8) == eca.behaviour_digest(240, 7, 8)
    assert same is False
    # but at a horizon of 7 the right-shift returns every configuration
    assert eca.behaviour_digest(240, 7, 7) == eca.behaviour_digest(204, 7, 7)


def test_no_dependency_on_the_radius_3_library():
    """The kinds must not share a decoder.

    An earlier version of this test grepped the source text and failed on the
    module docstring, which names the radius-3 library deliberately in order
    to say it is NOT used. Text is the wrong evidence. The real property is
    that importing this package does not import that one, so it is checked
    in a clean interpreter.
    """
    code = chr(10).join([
        "import sys",
        "import herakles.eca",
        "bad = [m for m in sys.modules if %r in m]" % "evca",
        "assert not bad, bad",
        "print(%r)" % "OK",
    ])
    out = subprocess.run([sys.executable, "-c", code], cwd=REPO,
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip().endswith("OK")


def test_no_radius_3_decoder_symbol_is_reachable():
    """A rule here is a NUMBER; there is no hex table decoder to reuse."""
    assert not hasattr(eca, "decode_table")
    assert not hasattr(eca, "encode_table")

# ---------------------------------------------------------------------------
# The published class-map fixture. Bound to a fresh derivation so it cannot
# go stale silently: the point of publishing it is that nobody re-derives it,
# which only works if a change here fails loudly.
# ---------------------------------------------------------------------------

def test_class_map_fixture_matches_a_fresh_derivation():
    import json
    path = os.path.join(os.path.dirname(__file__), "..",
                        "class_map_fixture.json")
    with open(os.path.abspath(path), encoding="utf-8") as fh:
        fx = json.load(fh)
    assert fx["scope"]["n_cells"] == 7 and fx["scope"]["steps"] == 8
    classes = eca.equivalence_classes(7, 8)
    fresh = {}
    for members in classes.values():
        cid = min(members)
        for r in members:
            fresh[r] = cid
    assert len(fresh) == 256
    assert fx["n_classes"] == len({v for v in fresh.values()}) == 224
    for rule_str, cid in fx["rule_to_class"].items():
        assert fresh[int(rule_str)] == cid, rule_str


def test_the_two_shift_rules_are_NOT_uniquely_identified_at_this_scope():
    """A degeneracy that matters for task construction, recorded as a test.

    Terminal behaviour at 8 steps on a 7-ring does not separate the shift
    rules from three others each. A task set built from rule numbers rather
    than class ids would count synonyms as independent teachers.
    """
    classes = eca.equivalence_classes(7, 8)
    by_rule = {}
    for members in classes.values():
        for r in members:
            by_rule[r] = sorted(members)
    assert by_rule[240] == [15, 180, 210, 240]
    assert by_rule[170] == [85, 154, 166, 170]
    # identity is not in either, so the earlier separation test still holds
    assert by_rule[204] != by_rule[240]


def test_T9_class_map_fixture_matches_a_fresh_derivation():
    """Same staleness binding as the T=8 map. A new scope, a new fixture."""
    import json
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
                                        "class_map_fixture_T9.json"))
    with open(path, encoding="utf-8") as fh:
        fx = json.load(fh)
    assert fx["scope"]["n_cells"] == 7 and fx["scope"]["steps"] == 9
    classes = eca.equivalence_classes(7, 9)
    fresh = {}
    for members in classes.values():
        cid = min(members)
        for r in members:
            fresh[r] = cid
    assert len(fresh) == 256
    assert fx["n_classes"] == len(set(fresh.values()))
    for rule_str, cid in fx["rule_to_class"].items():
        assert fresh[int(rule_str)] == cid, rule_str


def test_T9_is_the_rings_ceiling_and_T8_is_below_it():
    """The claim the T=9 fixture is justified by, asserted not asserted-in-prose."""
    counts = {T: len(eca.equivalence_classes(7, T)) for T in (7, 8, 9, 11)}
    assert counts[7] < counts[8] < counts[9]
    assert counts[9] == counts[11], "T=9 should already be the ceiling"


def test_the_published_T8_map_is_untouched_by_the_T9_fixture():
    import json
    p8 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
                                      "class_map_fixture.json"))
    with open(p8, encoding="utf-8") as fh:
        fx8 = json.load(fh)
    assert fx8["scope"]["steps"] == 8 and fx8["n_classes"] == 224
