"""blackboard.py — typed shared state + @blackboard_op decorator.

The Branch C representation. Each organism is a pipeline of state-aware
operators reading/writing typed slots on a shared BlackboardState. This
replaces the gen-3551 output-wiring DAG representation that the
2026-05-22 baseline-matrix experiment falsified.

Design doc: pivot/apollo_branch_c_blackboard_design_2026-05-24.md
"""
from __future__ import annotations
import functools
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


# ── Typed state ───────────────────────────────────────────────────────


@dataclass
class BlackboardState:
    """Typed shared state. Each slot has an explicit semantic type.

    Adding a slot is intentional, not emergent. The semantic-type label
    is the contract; Python types are coincidence.
    """
    # ── Inputs (set at organism start) ────────────────────────────
    problem_text: str = ""
    candidates: list[str] = field(default_factory=list)

    # ── Parsed entities ───────────────────────────────────────────
    numbers: list[float] = field(default_factory=list)          # parsed numeric values
    names: list[str] = field(default_factory=list)              # proper-name tokens
    relations: list[tuple[str, str]] = field(default_factory=list)  # ordered pairs (a > b)
    quantities: dict[str, int] = field(default_factory=dict)    # named counts
    question_target: str = ""                                   # what the question asks for

    # ── Derived ───────────────────────────────────────────────────
    transitive_closure: dict[str, set[str]] = field(default_factory=dict)
    ordered: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    evidence: list[dict] = field(default_factory=list)
    hypotheses: list[str] = field(default_factory=list)
    probabilities: dict[str, float] = field(default_factory=dict)
    confidence: Optional[float] = None
    max_entity: str = ""
    max_value: Optional[float] = None

    # ── Output ────────────────────────────────────────────────────
    candidate_scores: list[float] = field(default_factory=list)
    selected_answer: str = ""

    # ── Provenance ────────────────────────────────────────────────
    write_log: list[tuple[str, str]] = field(default_factory=list)
    op_log: list[str] = field(default_factory=list)
    skipped_ops: list[str] = field(default_factory=list)


# Semantic types declared by slot name. Coarse but sufficient for
# now — refine when type-violation patterns warrant it.
SLOT_TYPES: dict[str, str] = {
    "problem_text": "str",
    "candidates": "list_str",
    "numbers": "list_num",
    "names": "list_str",
    "relations": "list_pair_str",
    "quantities": "dict_str_int",
    "question_target": "str",
    "transitive_closure": "dict_str_set_str",
    "ordered": "list_str",
    "counts": "dict_str_int",
    "evidence": "list_dict",
    "hypotheses": "list_str",
    "probabilities": "dict_str_probability",
    "confidence": "probability",
    "max_entity": "str",
    "max_value": "float",
    "candidate_scores": "list_num",
    "selected_answer": "str",
}


def slot_type(name: str) -> Optional[str]:
    """Lookup the semantic type of a slot. Returns None if unknown."""
    return SLOT_TYPES.get(name)


# ── @blackboard_op decorator ──────────────────────────────────────────


class BlackboardOp:
    """A state-aware operator. Declares reads/writes/precondition.

    Wraps a function that takes a BlackboardState and returns a
    modified BlackboardState. The wrapper enforces the precondition
    (with configurable on_fail behavior) and records provenance.
    """
    def __init__(
        self,
        fn: Callable[[BlackboardState], BlackboardState],
        *,
        reads: list[str],
        writes: list[str],
        precondition: Optional[Callable[[BlackboardState], bool]] = None,
        on_fail: str = "skip",  # "skip", "error", "default"
        name: Optional[str] = None,
    ):
        self.fn = fn
        self.reads = list(reads)
        self.writes = list(writes)
        self.precondition = precondition or (lambda s: True)
        self.on_fail = on_fail
        self.name = name or fn.__name__
        functools.update_wrapper(self, fn)

    def __call__(self, state: BlackboardState) -> BlackboardState:
        if not self.precondition(state):
            state.skipped_ops.append(self.name)
            if self.on_fail == "skip":
                return state
            if self.on_fail == "error":
                raise RuntimeError(f"Precondition failed for {self.name}")
            # "default": fall through and run anyway

        try:
            state = self.fn(state)
        except Exception as e:
            state.skipped_ops.append(f"{self.name}:exception:{type(e).__name__}")
            if self.on_fail == "error":
                raise
            return state

        state.op_log.append(self.name)
        for w in self.writes:
            state.write_log.append((self.name, w))
        return state

    def __repr__(self):
        return f"<BlackboardOp {self.name} reads={self.reads} writes={self.writes}>"


def blackboard_op(
    reads: list[str],
    writes: list[str],
    precondition: Optional[Callable[[BlackboardState], bool]] = None,
    on_fail: str = "skip",
    name: Optional[str] = None,
):
    """Decorator factory. Use as:

        @blackboard_op(reads=["numbers"], writes=["max_value"],
                       precondition=lambda s: len(s.numbers) > 0)
        def numeric_argmax(state):
            state.max_value = max(state.numbers)
            return state
    """
    def deco(fn):
        return BlackboardOp(fn, reads=reads, writes=writes,
                            precondition=precondition, on_fail=on_fail, name=name)
    return deco


# ── Pipeline runner ───────────────────────────────────────────────────


def run_pipeline(pipeline: list[BlackboardOp], state: BlackboardState) -> BlackboardState:
    """Execute a pipeline of ops over a state. Returns the final state."""
    for op in pipeline:
        state = op(state)
    return state


def compile_check(pipeline: list[BlackboardOp]) -> tuple[bool, list[str]]:
    """Static check: do all reads have an upstream writer?

    Returns (ok, errors). Slot defaults from the initial state count
    as 'written' (problem_text, candidates always set; others empty
    but readable as empty list/dict).
    """
    written: set[str] = {"problem_text", "candidates"}  # always set by run_pipeline caller
    # Also treat default-initialized slots as writable for empty reads;
    # the runtime will return empty containers for unset slots, so we
    # only emit a hard error if a read is for a slot no operator writes
    # AND that slot has no sensible default.
    NO_DEFAULT = {"max_entity", "max_value", "confidence", "question_target", "selected_answer"}

    errors = []
    for op in pipeline:
        for r in op.reads:
            if r in NO_DEFAULT and r not in written:
                errors.append(f"{op.name} reads {r} but no upstream op writes it")
        for w in op.writes:
            written.add(w)
    return (len(errors) == 0, errors)
