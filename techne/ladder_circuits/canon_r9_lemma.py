"""CANON R9 — lemma invention. (Canon v2.0 §3; numbering per RUNG_LABEL_CORRECTION.md.)

Canon: *"Kill: proof-dependency-graph analysis — is the invented lemma LOAD-BEARING?
Artifact: the lemma + load-bearing flag."* The canon names two traps: a lemma that is true but
unused (**decorative**), and a lemma that merely restates the goal (**circular**).

Unblocked by `prometheus_math.lean_oracle` (cycle 015): every claim here is settled by Lean 4,
not by my own opinion of whether a proof works.

**The finding this cycle turns on:** the canon's stated kill test does NOT catch the second
trap. Deleting a circular lemma breaks the proof exactly as deleting a load-bearing one does —
under proof-dependency-graph analysis the honest inventor and the circular emitter are
observationally IDENTICAL. A second, independent check is required, and its design is where
all the difficulty actually lives.

That second check is a **triviality budget** on the equivalence `lemma <-> goal`: try to prove
it using only a fixed, weak, enumerated list of tactics. If a weak tactic suffices, the lemma
moved no work. The weakness of the list is the load-bearing choice — put `omega` in it and
every true arithmetic lemma is "equivalent to" every other, so the checker rejects legitimate
lemmas. That competitor is built here too, because a circularity checker that kills real
lemmas is the R6 phantom-failure pathology wearing a different hat.

Circuits:
- LemmaInventor       — proposes, verifies in Lean, runs BOTH checks, emits the flagged artifact.
- DeletionOnlyInventor — the canon's kill test as written, and nothing else.
- DecorativeLemmaEmitter (trap 1) — a true lemma the goal proof never touches. Dies on deletion.
- CircularLemmaEmitter   (trap 2) — the goal restated. SURVIVES deletion; dies on triviality.
- SwappedCircularEmitter (trap 2b) — the goal restated with the equation flipped. Survives
  deletion AND survives a syntactic statement-comparison; dies only on the semantic budget.
- OverStrongCircularityChecker (trap 3) — a checker whose budget includes `omega`. Rejects the
  honest lemma. Zero circular lemmas admitted, and zero real ones.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

from prometheus_math.lean_oracle import (
    LeanVerdict, check_lean_source, check_with_lemma, lean_available,
)

# Lean invocations cost seconds each; identical sources are asked once per process.
_CACHE: Dict[str, LeanVerdict] = {}


def _checked(source: str) -> LeanVerdict:
    if source not in _CACHE:
        _CACHE[source] = check_lean_source(source)
    return _CACHE[source]


@dataclass(frozen=True)
class LemmaTask:
    """A goal to be proved, plus a lemma-free proof of it (needed for the deletion test)."""

    name: str
    goal: str                 # e.g. "∀ n : Nat, n + n + 1 = 2 * n + 1"
    direct_proof: str         # a proof that uses no invented lemma


@dataclass(frozen=True)
class LemmaProposal:
    """What a circuit emits before any checking: a lemma and how the goal is meant to use it."""

    lemma_name: str
    lemma_statement: str
    lemma_proof: str
    goal_proof: str           # may reference lemma_name


@dataclass
class LemmaVerdict:
    """THE ARTIFACT: the lemma, plus the load-bearing flag the canon asks for — and the
    circularity flag the canon does not ask for but which its own trap list requires."""

    task: str
    lemma_statement: str
    lemma_true: bool = False
    goal_proved: bool = False
    load_bearing: bool = False        # canon's flag: deletion breaks the proof
    restatement: bool = False         # the second check
    checker_notes: str = ""

    @property
    def accepted(self) -> bool:
        """A lemma is a CONTRIBUTION only if it is true, used, load-bearing and not a
        restatement. Any three of the four is not enough — that is the whole point."""
        return (self.lemma_true and self.goal_proved
                and self.load_bearing and not self.restatement)


#: The WEAK triviality budget. Each entry is a proof term/tactic for `lemma <-> goal`.
#: Deliberately does NOT include a decision procedure. Extending this list makes the checker
#: stricter about circularity and, past a point, wrong about legitimate lemmas.
WEAK_EQUIVALENCE_BUDGET: Tuple[str, ...] = (
    "Iff.rfl",
    "Iff.intro (fun h n => (h n).symm) (fun h n => (h n).symm)",
)

#: The OVER-STRONG budget: a decision procedure. Proves the equivalence of any two true
#: linear-arithmetic statements, so it calls every true lemma a restatement.
STRONG_EQUIVALENCE_BUDGET: Tuple[str, ...] = (
    "Iff.rfl",
    "by constructor <;> intro h n <;> omega",
)


def is_restatement(lemma_statement: str, goal: str,
                   budget: Sequence[str] = WEAK_EQUIVALENCE_BUDGET) -> Tuple[bool, str]:
    """Can `lemma ↔ goal` be closed by a tactic from `budget`? If yes, no work was moved."""
    for proof in budget:
        v = _checked(f"theorem pm_equiv : ({lemma_statement}) ↔ ({goal}) := {proof}\n")
        if v.proved:
            return True, f"equivalence closed by trivial proof: {proof}"
    return False, "equivalence not closed by any trivial proof in budget"


def naive_syntactic_restatement(lemma_statement: str, goal: str) -> bool:
    """The CHEAP circularity check: is the lemma the same STRING as the goal?

    Free, needs no checker, and catches the obvious circular lemma. It is included because it
    is what anyone would reach for first, and because flipping an equation defeats it — the
    measurement that forces the semantic budget above.
    """
    return " ".join(lemma_statement.split()) == " ".join(goal.split())


def deletion_test(task: LemmaTask, prop: LemmaProposal) -> Tuple[bool, str]:
    """THE CANON'S KILL TEST. Re-check the goal proof with the lemma REMOVED. If it still
    checks, the lemma was decorative; if it now fails, the proof depends on it.

    Note what this cannot see: a lemma identical to the goal is depended upon just as hard.
    """
    without = _checked(f"theorem pm_goal : {task.goal} := {prop.goal_proof}\n")
    if without.proved:
        return False, "goal still proves with the lemma deleted (decorative)"
    return True, "goal proof fails without the lemma (dependency confirmed)"


@dataclass
class LemmaInventor:
    """Proposes a lemma, then subjects it to BOTH checks before flagging it."""

    budget: Sequence[str] = WEAK_EQUIVALENCE_BUDGET

    def propose(self, task: LemmaTask) -> LemmaProposal:
        """Hand-authored per task; the content of this cycle is the CHECKING, not the search.
        A generator that invents lemmas without being told belongs at canon R12."""
        return PROPOSALS[(type(self).__name__, task.name)]

    def judge(self, task: LemmaTask, prop: Optional[LemmaProposal] = None) -> LemmaVerdict:
        prop = prop or self.propose(task)
        v = LemmaVerdict(task.name, prop.lemma_statement)

        lemma_only = _checked(
            f"theorem {prop.lemma_name} : {prop.lemma_statement} := {prop.lemma_proof}\n")
        v.lemma_true = lemma_only.proved
        if not v.lemma_true:
            v.checker_notes = "lemma does not check"
            return v

        both = check_with_lemma(prop.lemma_name, prop.lemma_statement, prop.lemma_proof,
                                task.goal, prop.goal_proof)
        v.goal_proved = both.proved
        if not v.goal_proved:
            v.checker_notes = "goal does not check even with the lemma"
            return v

        v.load_bearing, note_lb = deletion_test(task, prop)
        v.restatement, note_rs = is_restatement(prop.lemma_statement, task.goal, self.budget)
        v.checker_notes = f"{note_lb}; {note_rs}"
        return v


@dataclass
class DeletionOnlyInventor(LemmaInventor):
    """The canon's kill test AS WRITTEN — dependency-graph analysis and nothing else."""

    def judge(self, task: LemmaTask, prop: Optional[LemmaProposal] = None) -> LemmaVerdict:
        v = super().judge(task, prop)
        v.restatement = False           # this checker never asks
        v.checker_notes += "; circularity NOT checked"
        return v


@dataclass
class OverStrongCircularityChecker(LemmaInventor):
    """TRAP 3: a decision procedure in the equivalence budget. Admits no circular lemma and
    no real one either — the phantom-failure pathology of canon R6, relocated."""

    budget: Sequence[str] = STRONG_EQUIVALENCE_BUDGET


@dataclass
class DecorativeLemmaEmitter(LemmaInventor):
    """TRAP 1: emits a true, irrelevant lemma; the goal is proved directly."""


@dataclass
class CircularLemmaEmitter(LemmaInventor):
    """TRAP 2: emits the goal itself as the lemma, then invokes it."""


@dataclass
class SwappedCircularEmitter(LemmaInventor):
    """TRAP 2b: emits the goal with the equation flipped — a different STRING, the same claim."""


# --------------------------------------------------------------------------------------------
# Tasks, and the hand-authored proposal each circuit makes for each task.

GOAL_A = LemmaTask(
    name="double_succ",
    goal="∀ n : Nat, n + n + 1 = 2 * n + 1",
    direct_proof="by intro n; omega",
)

_HONEST_A = LemmaProposal(
    "pm_double", "∀ n : Nat, n + n = 2 * n", "by intro n; omega",
    "by intro n; rw [pm_double]")

PROPOSALS: Dict[Tuple[str, str], LemmaProposal] = {
    ("LemmaInventor", "double_succ"): _HONEST_A,
    ("DeletionOnlyInventor", "double_succ"): _HONEST_A,
    ("OverStrongCircularityChecker", "double_succ"): _HONEST_A,
    ("DecorativeLemmaEmitter", "double_succ"): LemmaProposal(
        "pm_mulzero", "∀ n : Nat, n * 0 = 0", "by intro n; simp",
        "by intro n; omega"),
    ("CircularLemmaEmitter", "double_succ"): LemmaProposal(
        "pm_restate", "∀ n : Nat, n + n + 1 = 2 * n + 1", "by intro n; omega",
        "by intro n; exact pm_restate n"),
    ("SwappedCircularEmitter", "double_succ"): LemmaProposal(
        "pm_flip", "∀ n : Nat, 2 * n + 1 = n + n + 1", "by intro n; omega",
        "by intro n; exact (pm_flip n).symm"),
}
