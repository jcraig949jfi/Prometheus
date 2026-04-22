"""Tests for gen_10 composers package.

Run with:
    PYTHONPATH=. python -m harmonia.composers.test_composers
"""
from __future__ import annotations

import sys

from harmonia.composers.validator import (
    is_valid_composition,
    validate,
)


def test_operator_on_dataset_valid():
    assert is_valid_composition("operator", "dataset") is True


def test_operator_on_operator_valid_default():
    # operator ∘ operator defaults to valid at v1 (with a warning caveat).
    assert is_valid_composition("operator", "operator") is True


def test_dataset_on_dataset_invalid():
    assert is_valid_composition("dataset", "dataset") is False


def test_shape_on_signature_invalid():
    assert is_valid_composition("shape", "signature") is False


def test_constant_is_never_callable():
    for other in ("dataset", "operator", "shape", "signature", "constant"):
        assert is_valid_composition("constant", other) is False


def test_signature_on_anything_invalid():
    for other in ("dataset", "operator", "shape", "signature", "constant"):
        assert is_valid_composition("signature", other) is False


def test_shape_on_dataset_valid():
    # shape ∘ dataset is pattern-matching (e.g., LADDER on data)
    assert is_valid_composition("shape", "dataset") is True


def test_validate_self_composition_rejected_for_non_operators():
    out = validate({"name": "Q_EC_R0_D5", "type": "dataset"},
                   {"name": "Q_EC_R0_D5", "type": "dataset"})
    assert out["valid"] is False
    # Self-composition catches first
    assert "self-composition" in out["reason"] or "dataset ∘ dataset" in out["reason"]


def test_validate_operator_self_composition_allowed_stub():
    # operator self-composition is ALLOWED (operator ∘ operator valid);
    # self-composition check applies only to non-operators.
    out = validate({"name": "NULL_PLAIN", "type": "operator"},
                   {"name": "NULL_PLAIN", "type": "operator"})
    assert out["valid"] is True


def run_all():
    tests = [t for name, t in globals().items() if name.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  ok    {t.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{len(tests) - failed}/{len(tests)} passed.")
    return failed


if __name__ == "__main__":
    sys.exit(run_all())
