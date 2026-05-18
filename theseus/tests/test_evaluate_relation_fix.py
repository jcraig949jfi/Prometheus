"""Regression tests for the abs_diff_le_K evaluator fix (Fire #3 bug).

Previously _evaluate_relation only matched the literal "abs_diff_le_3";
mutated thresholds (from C2/C4/D2) silently evaluated to False, producing
spurious kills (C4 at 98% kill rate when it should be ~0%).
"""
from __future__ import annotations

import pytest

from theseus.generators.a1_catalog_cross_product import _evaluate_relation


def test_abs_diff_le_0_correct():
    assert _evaluate_relation(0, 0, "abs_diff_le_0") is True
    assert _evaluate_relation(0, 1, "abs_diff_le_0") is False


def test_abs_diff_le_3_correct():
    assert _evaluate_relation(0, 3, "abs_diff_le_3") is True
    assert _evaluate_relation(0, 4, "abs_diff_le_3") is False


def test_abs_diff_le_5_correct():
    # The bug case: any K other than 3 was returning False unconditionally
    assert _evaluate_relation(0, 5, "abs_diff_le_5") is True
    assert _evaluate_relation(0, 6, "abs_diff_le_5") is False


def test_abs_diff_le_100_correct():
    assert _evaluate_relation(0, 99, "abs_diff_le_100") is True
    assert _evaluate_relation(0, 101, "abs_diff_le_100") is False


def test_invalid_abs_diff_le_returns_false():
    assert _evaluate_relation(0, 5, "abs_diff_le_notanumber") is False


def test_unknown_relation_returns_false():
    assert _evaluate_relation(0, 5, "totally_made_up") is False


def test_other_relations_unaffected():
    assert _evaluate_relation(5, 5, "equal") is True
    assert _evaluate_relation(5, 7, "equal") is False
    assert _evaluate_relation(4, 6, "equal_mod_2") is True
    assert _evaluate_relation(3, 8, "equal_mod_2") is False
    assert _evaluate_relation(2, 8, "divides") is True
    assert _evaluate_relation(3, 8, "divides") is False


def test_divides_with_zero_fire22():
    """Fire #22 fix: divides(a, 0) is True for nonzero a (since 0 = 0*a)."""
    # Every nonzero a divides 0
    assert _evaluate_relation(2, 0, "divides") is True
    assert _evaluate_relation(1, 0, "divides") is True
    assert _evaluate_relation(-3, 0, "divides") is True
    assert _evaluate_relation(7, 0, "divides") is True
    # 0 doesn't divide any nonzero number
    assert _evaluate_relation(0, 5, "divides") is False
    assert _evaluate_relation(0, -3, "divides") is False
    # Convention: 0 divides 0
    assert _evaluate_relation(0, 0, "divides") is True
