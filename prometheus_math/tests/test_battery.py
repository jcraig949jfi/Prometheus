"""TDD suite for prometheus_math.battery — the four required categories."""
from __future__ import annotations

import math
import pathlib
import sys

import pytest
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.battery import (  # noqa: E402
    BatteryError, battery_strength, member_resolution,
)


# ---- 1. authority --------------------------------------------------------------------------

def test_member_resolution_is_the_entropy_of_the_verdict_column():
    """Hand computation from H = -sum p log2 p. A member splitting four candidates 2/2 carries
    1 bit; 3/1 carries -0.75log2(0.75) - 0.25log2(0.25) = 0.8113; a constant member carries 0."""
    v = {"even": [True, True, False, False],
         "three": [True, True, True, False],
         "always": [True, True, True, True]}
    res = member_resolution(v)
    assert res["even"] == pytest.approx(1.0)
    assert res["three"] == pytest.approx(0.8112781, abs=1e-6)
    assert res["always"] == pytest.approx(0.0)


def test_advertised_versus_discriminating_size():
    """The distinction the module exists for: a battery of three with one silent member is a
    battery of two, measured over these candidates."""
    s = battery_strength({"a": [True, False], "b": [False, True], "c": [True, True]})
    assert s.advertised == 3
    assert s.discriminating == 2
    assert s.silent_members == ["c"]
    assert s.n_candidates == 2


def test_non_boolean_verdicts_are_supported():
    """Verdicts need only be hashable — a three-way router is a battery member too. Reference
    check: three equally-sized classes over six candidates carry log2(3) = 1.585 bits."""
    res = member_resolution({"route": ["A", "A", "B", "B", "C", "C"]})
    assert res["route"] == pytest.approx(math.log2(3), abs=1e-9)


# ---- 2. property (Hypothesis) ----------------------------------------------------------------

@settings(max_examples=200, deadline=None)
@given(st.lists(st.booleans(), min_size=1, max_size=40))
def test_resolution_is_zero_exactly_when_the_member_is_constant(col):
    res = member_resolution({"m": col})["m"]
    assert (res <= 1e-12) == (len(set(col)) == 1)
    assert 0.0 - 1e-12 <= res <= math.log2(len(col)) + 1e-12


@settings(max_examples=150, deadline=None)
@given(st.lists(st.booleans(), min_size=2, max_size=30))
def test_a_binary_member_never_exceeds_one_bit(col):
    """A two-valued verdict cannot carry more than one bit, whatever the split."""
    assert member_resolution({"m": col})["m"] <= 1.0 + 1e-12


@settings(max_examples=120, deadline=None)
@given(st.lists(st.booleans(), min_size=1, max_size=25),
       st.lists(st.booleans(), min_size=1, max_size=25))
def test_discriminating_count_never_exceeds_advertised(a, b):
    n = min(len(a), len(b))
    s = battery_strength({"a": a[:n], "b": b[:n]})
    assert 0 <= s.discriminating <= s.advertised == 2
    assert len(s.silent_members) == s.advertised - s.discriminating


# ---- 3. edge cases ---------------------------------------------------------------------------

def test_battery_edges():
    """Edges covered:
    - no members: BatteryError (a battery with nothing in it has no strength)
    - no candidates: BatteryError — undefined, NOT zero, matching calibration's refusal to
      score an empty forecast set
    - members disagreeing on candidate count: BatteryError
    - single candidate: defined, and every member is necessarily silent
    - every member silent: discriminating 0, advertised preserved
    - a member with entirely distinct verdicts: log2(n) bits, the ceiling
    """
    with pytest.raises(BatteryError):
        member_resolution({})
    with pytest.raises(BatteryError):
        member_resolution({"a": []})
    with pytest.raises(BatteryError):
        member_resolution({"a": [True], "b": [True, False]})

    single = battery_strength({"a": [True], "b": [False]})
    assert single.discriminating == 0 and single.advertised == 2

    allsilent = battery_strength({"a": [1, 1, 1], "b": [2, 2, 2]})
    assert allsilent.discriminating == 0
    assert allsilent.silent_members == ["a", "b"]

    ceiling = member_resolution({"m": list(range(8))})["m"]
    assert ceiling == pytest.approx(3.0)


def test_total_bits_is_documented_as_an_upper_bound_not_the_joint_power():
    """Two members carrying identical verdicts each measure 1 bit and jointly carry 1, not 2.
    `total_bits` sums them, which is why its docstring calls it an upper bound."""
    s = battery_strength({"a": [True, False], "clone": [True, False]})
    assert s.total_bits == pytest.approx(2.0)
    assert s.discriminating == 2          # both fire...
    # ...but jointly they separate exactly one pair, so the sum overstates the battery.


# ---- 4. composition ---------------------------------------------------------------------------

def test_composes_with_partition_entropy_by_an_independent_path():
    """Chain: member_resolution must agree with computing the entropy of the induced partition
    directly — two code paths for one number."""
    from prometheus_math.partition import entropy, induced_partition
    col = [True, True, False, True, False, False, True]
    direct = entropy(induced_partition(list(range(len(col))), lambda i: col[i]), len(col))
    assert member_resolution({"m": col})["m"] == pytest.approx(direct)


def test_composes_with_the_real_discovery_battery_audit():
    """Chain into cycle 028's live measurement: the discovery pipeline's kill path has four
    advertised members and two that discriminate, with F9 and F11 silent."""
    from techne.ladder_circuits.battery_chain import CHECKS, real_candidates

    cands = real_candidates()
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
    assert s.advertised == 4
    assert s.discriminating == 2
    assert s.silent_members == ["F11", "F9"]
