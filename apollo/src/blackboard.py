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


# ── 2026-05-27 Phase 0 — wrapper protocol corrections ────────────────
# Per the 2026-05-25 null-slot ablation signature analysis, four
# corrections are baked into the protocol so the LLM mutation operator
# (Phase 1) can't easily produce decorative organisms:
#   - declared-reads-must-be-actual-reads (catches recompute-bypass)
#   - one-write-per-op preferred (catches side-output)
#   - no-redundant-encoding (catches redundant-encoding)
#   - mid-step corruption test (catches atomic-with-output)


import ast
import inspect


def verify_declared_reads_are_actual_reads(op: BlackboardOp) -> list[dict]:
    """Static AST check: does the op's source actually reference state.X
    for each declared read X? Returns a list of signature warnings.

    Signature emitted: "recompute-bypass" if a declared read is never
    referenced as state.X in the source. The op may be recomputing the
    value from upstream slots, defeating the typed-state discipline.
    """
    warnings = []
    try:
        src = inspect.getsource(op.fn)
        tree = ast.parse(src.strip())
    except (OSError, TypeError, IndentationError):
        return warnings  # built-ins / dynamic; can't verify
    referenced = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id in ("state", "s"):
            referenced.add(node.attr)
    for r in op.reads:
        if r not in referenced:
            warnings.append({
                "op": op.name,
                "signature": "recompute-bypass",
                "slot": r,
                "lesson": f"op declares it reads '{r}' but source never references state.{r}; "
                          f"the value may be recomputed from upstream slots, defeating typed-state discipline",
            })
    return warnings


def verify_single_output_preferred(op: BlackboardOp, hard_limit: int = 4) -> list[dict]:
    """Side-output check: ops that write many slots should be split.

    Soft warn at >=2 writes; hard fail at >=hard_limit. Atomic
    output ops (e.g. terminal scorers writing candidate_scores +
    selected_answer) are exempt by convention if the op name starts
    with 'score_' or 'select_'.
    """
    warnings = []
    is_terminal = op.name.startswith(("score_", "select_"))
    n = len(op.writes)
    if n >= 2 and not is_terminal:
        warnings.append({
            "op": op.name,
            "signature": "side-output",
            "n_writes": n,
            "writes": list(op.writes),
            "lesson": f"op writes {n} slots in one step; consider splitting into "
                      f"atomic single-output ops so data flow is visible at the genome level",
        })
    if n >= hard_limit:
        warnings[-1]["severity"] = "hard"
    return warnings


def verify_no_redundant_encoding(pipeline: list[BlackboardOp]) -> list[dict]:
    """Detect parser/producer ops that write multiple slots which are
    likely redundant views of the same source data.

    Heuristic: an op that writes ≥2 slots from the same "encoding group"
    is flagged. Encoding groups are hand-declared below.
    """
    REDUNDANT_GROUPS = [
        # (slot_a, slot_b, lesson) — if an op writes both, the second is
        # likely recoverable from the first
        {"names", "relations"},  # names is recoverable from relations entries
    ]
    warnings = []
    for op in pipeline:
        ws = set(op.writes)
        for group in REDUNDANT_GROUPS:
            overlap = ws & group
            if len(overlap) >= 2:
                warnings.append({
                    "op": op.name,
                    "signature": "redundant-encoding",
                    "slots": list(overlap),
                    "lesson": f"op writes {sorted(overlap)} but one is recoverable from the other; "
                              f"prefer the canonical representation",
                })
    return warnings


def mid_step_corruption_test(op: BlackboardOp, state: BlackboardState,
                             corrupt_slot: str,
                             corrupted_value=None) -> dict:
    """Run the op once normally, once with `corrupt_slot` corrupted DURING
    execution (i.e. corrupted on input before the op reads it). Returns
    a signature dict.

    This is the complementary instrument for atomic-with-output cases
    where the standard null-slot ablation can't separate the slot from
    the output (because they're written in the same step). By corrupting
    the input rather than the output, we expose whether the op actually
    READS the slot.
    """
    import copy as _copy
    # Baseline run
    s1 = _copy.deepcopy(state)
    s1 = op(s1)
    baseline_outputs = {w: getattr(s1, w, None) for w in op.writes}
    # Corrupted run
    s2 = _copy.deepcopy(state)
    if hasattr(s2, corrupt_slot):
        setattr(s2, corrupt_slot, corrupted_value if corrupted_value is not None else
                type(getattr(s2, corrupt_slot, None))() if getattr(s2, corrupt_slot, None) is not None
                else None)
    s2 = op(s2)
    corrupted_outputs = {w: getattr(s2, w, None) for w in op.writes}
    # Diff
    differs = {w: (baseline_outputs[w] != corrupted_outputs[w]) for w in op.writes}
    return {
        "op": op.name,
        "corrupted_slot": corrupt_slot,
        "any_output_differs": any(differs.values()),
        "outputs_diff": differs,
        "signature": "load-bearing-input" if any(differs.values()) else "decorative-input",
        "lesson": ("op reads the corrupted slot meaningfully" if any(differs.values())
                   else "op does not actually read the corrupted slot; declared read may be decorative"),
    }


def audit_pipeline(pipeline: list[BlackboardOp]) -> dict:
    """Full Phase-0 pipeline audit. Returns a dict of signatures + lessons,
    NOT a pass/fail verdict. Per Doctrine #2."""
    signatures = {
        "recompute_bypass": [],
        "side_output": [],
        "redundant_encoding": [],
        "compile_check_errors": [],
    }
    ok, errors = compile_check(pipeline)
    signatures["compile_check_errors"] = errors
    for op in pipeline:
        signatures["recompute_bypass"].extend(verify_declared_reads_are_actual_reads(op))
        signatures["side_output"].extend(verify_single_output_preferred(op))
    signatures["redundant_encoding"].extend(verify_no_redundant_encoding(pipeline))
    return signatures
