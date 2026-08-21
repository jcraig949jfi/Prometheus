"""Lean assumption tracer — the three layers, and the audit lane that catches `sorry`.

Built cycle 018 against external review of the canon R10 work, which argued that `#print axioms`
is too coarse to serve as an assumption tracer. That is checked here rather than taken on trust,
and it is TRUE on this toolchain: a theorem whose proof runs through a custom typeclass reports
`[propext, Quot.sound]` and nothing else.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.lean_oracle import (  # noqa: E402
    check_frozen_term, check_lean_source, check_theorem, dependency_closure, lean_available,
    traced_classes,
)

pytestmark = pytest.mark.skipif(not lean_available(), reason="Lean toolchain not reachable")

SRC = """class MyChar (R : Type) where
  ch : Nat
instance instCharNat : MyChar Nat := ⟨0⟩
def usesChar (R : Type) [MyChar R] : Nat := MyChar.ch R
theorem tgt : usesChar Nat = 0 := rfl
theorem plain : 2 + 2 = 4 := rfl"""


# ---- layer 1 + 2: the closure, and why #print axioms is not enough ----------------------------

def test_tracer_sees_the_typeclass_chain_that_print_axioms_misses():
    """The headline. `tgt`'s proof goes through the `MyChar Nat` instance, and that dependency
    is exactly the kind of thing an R10 assumption set must contain. The axiom lane reports
    only the two kernel axioms — measured, not assumed."""
    d = dependency_closure(SRC, "tgt")
    assert "MyChar" in d.classes
    assert ("instCharNat", "MyChar") in d.instances
    assert set(d.axioms) <= {"propext", "Quot.sound", "Classical.choice"}
    assert "MyChar" not in " ".join(d.axioms)


def test_tracer_does_not_report_a_class_the_proof_does_not_use():
    """No-false-positive check: without discrimination the tracer would be another
    always-breaks trap, which canon R10 already has enough of."""
    assert "MyChar" not in traced_classes(SRC, "plain")
    assert "MyChar" in traced_classes(SRC, "tgt")


def test_constructors_are_not_reported_as_instances():
    """`MyChar.mk` has the class as its type head but is a constructor, not an instance. Left
    unfiltered it inflates the assumption set with artifacts of the encoding."""
    d = dependency_closure(SRC, "tgt")
    assert all(name != "MyChar.mk" for name, _cls in d.instances)


# ---- the audit lane, and a genuine gap in the checker ------------------------------------------

def test_AUDIT_LANE_sorry_is_invisible_to_the_verdict_and_caught_by_the_axioms():
    """A REAL GAP, found while building this. `sorry` produces a Lean WARNING, not an error, so
    `check_lean_source` classifies a sorry-contaminated proof as PROVED. The axiom lane catches
    it: `sorryAx` appears in the dependency report. This is why `#print axioms` is retained as
    an independent lane even though it is useless as an assumption tracer.
    """
    contaminated = "theorem bad : 2 + 2 = 5 := by sorry"
    assert check_lean_source(contaminated).status == "PROVED"      # the gap, measured
    assert "sorryAx" in dependency_closure(contaminated, "bad").axioms


def test_clean_proofs_carry_no_sorryAx():
    assert "sorryAx" not in dependency_closure(SRC, "tgt").axioms


# ---- layer 3: necessity against a FROZEN term ---------------------------------------------------

def test_frozen_term_fails_when_its_assumption_is_ablated():
    """Necessity: delete the instance and the SAME proof term no longer elaborates."""
    ablated = """class MyChar (R : Type) where
  ch : Nat
def usesChar (R : Type) [MyChar R] : Nat := MyChar.ch R"""
    v = check_frozen_term(ablated, "usesChar Nat = 0", "rfl")
    assert v.status == "ERROR"


def test_WHY_THE_TERM_MUST_BE_FROZEN_re_searching_reports_the_assumption_unused():
    """The reviewer's warning, demonstrated. `pm_double` is load-bearing for the proof
    `by rw [pm_double]` — ablate it and that proof dies. But ask Lean to prove the goal AGAIN
    with a decision procedure and it succeeds, which a naive necessity test reads as
    'the assumption was never needed'. Same goal, opposite conclusions.

    This is canon R9's non-unique-proof problem wearing R10 clothes, and freezing the artifact
    is the fix.
    """
    goal = "∀ n : Nat, n + n + 1 = 2 * n + 1"
    with_lemma = "theorem pm_double : ∀ n : Nat, n + n = 2 * n := by intro n; omega"

    assert check_frozen_term(with_lemma, goal, "by intro n; rw [pm_double]").proved
    assert check_frozen_term("", goal, "by intro n; rw [pm_double]").status == "ERROR"  # frozen
    assert check_theorem(goal, "by intro n; omega").proved                              # re-search
