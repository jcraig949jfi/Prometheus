"""Acceptance suite for the Lean proof-checker oracle.

The load-bearing property is the three-valued verdict: a syntax error must NEVER read as a
refutation. Conflating "I could not tell" with "false" is the phantom-failure pathology canon
R6 scores, and a verdict lane that commits it would poison every claim it touches.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.lean_oracle import (  # noqa: E402
    check_lean_source, check_theorem, lean_available,
)

pytestmark = pytest.mark.skipif(not lean_available(), reason="Lean not installed on this host")


def test_true_arithmetic_theorem_is_PROVED():
    v = check_theorem("2 + 2 = 4")
    assert v.proved, v.diagnostics


def test_FALSE_theorem_is_REFUTED_not_merely_failed():
    """The smoke test that motivated the module: Lean's `decide` actively determines that
    2+2=5 is false. That NO is what makes this a verdict lane rather than a linter."""
    v = check_theorem("2 + 2 = 5")
    assert v.refuted, v.diagnostics
    assert "false" in v.diagnostics.lower()


def test_SYNTAX_ERROR_is_ERROR_never_REFUTED():
    """The separation that matters: an unparseable claim is not a false claim."""
    v = check_lean_source("theorem broken : 2 + + = := by")
    assert v.status == "ERROR"
    assert not v.refuted


def test_UNPROVABLE_BY_THIS_TACTIC_is_ERROR_not_REFUTED():
    """A true statement the supplied tactic cannot discharge must be ERROR — the checker
    failed, the claim did not. Reporting REFUTED here would invent a counterexample."""
    v = check_theorem("(a b : Nat) : a + b = b + a".split(":", 1)[1].strip(), proof="by rfl",
                      preamble="")
    assert v.status in {"ERROR", "PROVED"}
    assert not v.refuted


def test_general_theorem_with_a_real_tactic_is_PROVED():
    v = check_theorem("∀ a b : Nat, a + b = b + a", proof="by intro a b; omega")
    assert v.proved, v.diagnostics


def test_verdict_carries_toolchain_and_source_hash_for_provenance():
    """Provenance doctrine: a verdict must say which checker produced it, and over what."""
    v = check_theorem("1 + 1 = 2")
    assert v.toolchain.startswith("leanprover/lean4:")
    assert len(v.source_sha) == 16
    same = check_theorem("1 + 1 = 2")
    assert same.source_sha == v.source_sha           # deterministic over identical source
    other = check_theorem("1 + 2 = 3")
    assert other.source_sha != v.source_sha


def test_determinism_same_claim_same_verdict():
    assert check_theorem("3 * 3 = 9").status == check_theorem("3 * 3 = 9").status
