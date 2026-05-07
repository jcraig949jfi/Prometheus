"""Single-fact-decomposition prompt protocol (E007, fire 1 post-restart).

Charon-as-Learner-Tester 6-fire arc isolated multi-part question
scaffolding as a causal degeneration trigger. Paired test P-028 (single-
part "chromatic of Petersen?" → correct) vs P-029 (multi-part "(a)
chromatic, (b) girth" → degenerate) confirmed the hypothesis.

This module decomposes any multi-fact / multi-part question into a
sequence of single-fact subqueries before model invocation, then
reassembles the answers. Pure inference-time wrapper — no model weights
touched, no contract change to existing Learner public API.

Per HARD-2 (anti-gravitational-well doctrine): the conventional response
to "model degenerates on multi-part questions" is "train it on more
multi-part data." That's a training-time fix that takes weeks. The
substrate-grade response is to recognize that the bottleneck is the
prompt protocol — and fix it at the protocol layer instead. Free win.

API
---
- ``is_multi_part(question)`` — heuristic detector
- ``decompose_question(question)`` — returns ordered list of subqueries
- ``assemble_answers(subqueries, answers)`` — reassembles into a single
  response string
- ``answer_with_decomposition(question, answer_fn, *, decomposition_on=True)``
  — wrapper around any single-question answer function. Supports
  ``decomposition_on=False`` for ablation A/B testing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional


# Heuristic: enumeration markers that indicate sub-question scaffolding.
# Order matters — match longer markers before shorter ones.
_ENUM_PATTERNS = [
    r"\(\s*[a-zA-Z]\s*\)",      # (a), (b), ( c )
    r"\(\s*[ivxlcdmIVXLCDM]+\s*\)",  # (i), (ii), (IV)
    r"\(\s*\d+\s*\)",            # (1), (2)
    r"^\s*[a-zA-Z]\.\s+",        # a. b. (line-start)
    r"^\s*\d+\.\s+",             # 1. 2.
]
_ENUM_RE = re.compile("|".join(_ENUM_PATTERNS), flags=re.MULTILINE)

# "First X. Second Y. Third Z." ordinal-prefix pattern
_ORDINAL_RE = re.compile(
    r"\b(first|second|third|fourth|fifth)\b",
    flags=re.IGNORECASE,
)

# Conjoined factual-ask pattern (heuristic): "X and Y", where each side is
# a question word. Stricter than naive "and" split.
_CONJ_PROMPT_RE = re.compile(
    r"\b(what|when|who|where|how|which)\b.*?\band\b.*?\b(what|when|who|where|how|which|state|give|provide|compute|calculate)\b",
    flags=re.IGNORECASE | re.DOTALL,
)


def is_multi_part(question: str) -> bool:
    """Detect multi-part questions via enumeration markers + ordinal prefixes
    + conjoined factual asks.

    Conservative: false-positives (treating a single-fact question as
    multi-part) cost an extra model call but produce the same answer.
    False-negatives (missing a real multi-part) leave the bug. So we
    bias toward declaring multi-part.
    """
    if not question or not question.strip():
        return False

    enum_hits = _ENUM_RE.findall(question)
    if len(enum_hits) >= 2:
        return True

    if _CONJ_PROMPT_RE.search(question):
        return True

    # Two distinct ordinal prefixes ("first ... second ...")
    ordinals = _ORDINAL_RE.findall(question)
    if len({o.lower() for o in ordinals}) >= 2:
        return True

    return False


@dataclass(frozen=True)
class _Subquery:
    """One decomposed subquery with its enumeration label (if any)."""
    label: Optional[str]   # "(a)", "(i)", "1.", "first", or None
    text: str              # the substantive subquery text


def _split_by_enumeration(question: str) -> List[_Subquery]:
    """Split a question on enumeration markers, preserving label + text.

    Bug fix (E007 fire 1, observed in ablation): when a question contains
    a trailing "labeled (a) and (b)" instruction, the regex finds the
    trailing labels as additional enumeration markers, producing spurious
    short-body subqueries. Filter: drop subqueries whose body has fewer
    than 4 characters (these are the "and" / connective fragments
    between the trailing labels). Also dedupe by exact-label-text so
    repeated `(a)` doesn't generate two subqueries.
    """
    matches = list(_ENUM_RE.finditer(question))
    if len(matches) < 2:
        return []

    # Preamble is everything before the first enumeration marker.
    preamble = question[: matches[0].start()].strip()
    subs: List[_Subquery] = []
    seen_labels: set = set()
    for i, m in enumerate(matches):
        label = m.group(0).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(question)
        body = question[body_start:body_end].strip().rstrip(",;.").strip()
        if not body or len(body) < 4:
            # Trailing "labeled (a) and (b)" produces empty / very-short
            # bodies between the labels. Skip them.
            continue
        # Drop trailing "and" / connective-only bodies that survived length filter
        if body.lower() in ("and", "or", "and?", "or?"):
            continue
        # Dedupe: if we've already emitted a subquery for this label,
        # skip the trailing duplicate (the trailing one is in the
        # "labeled X and Y" reference, not a real subquery).
        norm_label = re.sub(r"\s+", "", label).lower()
        if norm_label in seen_labels:
            continue
        seen_labels.add(norm_label)

        # Compose the subquery: preamble (context) + body (specific ask)
        if preamble:
            full_q = f"{preamble} {body}".strip()
        else:
            full_q = body
        # Ensure subquery ends with a question mark or period
        if not full_q.endswith(("?", ".")):
            full_q = full_q + "?"
        subs.append(_Subquery(label=label, text=full_q))
    return subs


def _split_by_conjunction(question: str) -> List[_Subquery]:
    """Last-resort split on conjoined factual asks (single ' and ' between
    two question words)."""
    if not _CONJ_PROMPT_RE.search(question):
        return []
    # Split on the first " and " that lies between two question words.
    # Conservative: only split if both halves contain a question word.
    qword_re = re.compile(r"\b(what|when|who|where|how|which|state|give|provide|compute|calculate)\b", re.IGNORECASE)
    halves = re.split(r"\s+and\s+", question, maxsplit=1)
    if len(halves) != 2:
        return []
    left, right = halves
    if not (qword_re.search(left) and qword_re.search(right)):
        return []
    left_t = left.strip().rstrip(",;.").strip()
    right_t = right.strip().rstrip(",;.").strip()
    if not left_t.endswith(("?", ".")):
        left_t += "?"
    if not right_t.endswith(("?", ".")):
        right_t += "?"
    return [
        _Subquery(label=None, text=left_t),
        _Subquery(label=None, text=right_t),
    ]


def decompose_question(question: str) -> List[str]:
    """Return ordered list of single-fact subqueries.

    Single-part question → returns [question] unchanged. Multi-part →
    returns 2+ subqueries each rephrased to ask one fact.

    Decomposition strategies, in order:
    1. Enumeration markers ("(a)", "(b)", "1.", "2.", etc.) — preferred
    2. Conjoined factual asks ("what is X and what is Y") — fallback
    3. Default: single-element list with the original question
    """
    if not question or not question.strip():
        return [question]
    enum_subs = _split_by_enumeration(question)
    if enum_subs:
        return [s.text for s in enum_subs]
    conj_subs = _split_by_conjunction(question)
    if conj_subs:
        return [s.text for s in conj_subs]
    return [question]


def assemble_answers(subqueries: List[str], answers: List[str]) -> str:
    """Reassemble per-subquery answers into a single response string.

    Uses ``(a)``-style labels in the assembled output regardless of the
    original enumeration style — keeps the assembly format stable for
    eval / parsing.
    """
    if len(subqueries) != len(answers):
        raise ValueError(
            f"subqueries ({len(subqueries)}) and answers ({len(answers)}) "
            f"have different lengths"
        )
    if len(subqueries) == 1:
        return answers[0].strip()
    parts = []
    for i, ans in enumerate(answers):
        label = chr(ord("a") + i) if i < 26 else str(i + 1)
        parts.append(f"({label}) {ans.strip()}")
    return " ".join(parts)


@dataclass
class DecompositionResult:
    """Telemetry for one answer_with_decomposition call.

    Pre-registered fields so the A/B ablation can compare ON vs OFF runs
    on the same probe set. Backwards-compat: callers wanting just the
    answer text use ``.answer``; callers wanting telemetry get the full
    dataclass.
    """
    answer: str
    decomposition_on: bool
    is_multi_part: bool
    subqueries: List[str]
    per_subquery_answers: List[str]
    n_model_calls: int
    metadata: dict = field(default_factory=dict)


def answer_with_decomposition(
    question: str,
    answer_fn: Callable[[str], str],
    *,
    decomposition_on: bool = True,
) -> DecompositionResult:
    """Wrap any single-question ``answer_fn(question_str) -> answer_str``
    so multi-part questions route through decomposition.

    Args:
        question: full natural-language question, possibly multi-part.
        answer_fn: callable that takes a single question string and
            returns the model's answer string. Inference-time only.
        decomposition_on: if True, decompose multi-part questions and
            call answer_fn once per subquery, then reassemble. If False,
            pass the full question through to answer_fn unchanged
            (control / ablation A/B comparison).

    Returns:
        DecompositionResult with answer text + telemetry.
    """
    multi = is_multi_part(question)
    if not decomposition_on or not multi:
        ans = answer_fn(question)
        return DecompositionResult(
            answer=ans,
            decomposition_on=decomposition_on,
            is_multi_part=multi,
            subqueries=[question],
            per_subquery_answers=[ans],
            n_model_calls=1,
            metadata={"path": "passthrough" if not decomposition_on else "single_part"},
        )

    subqueries = decompose_question(question)
    per_answers = [answer_fn(sq) for sq in subqueries]
    assembled = assemble_answers(subqueries, per_answers)
    return DecompositionResult(
        answer=assembled,
        decomposition_on=True,
        is_multi_part=True,
        subqueries=subqueries,
        per_subquery_answers=per_answers,
        n_model_calls=len(subqueries),
        metadata={"path": "decomposed"},
    )


__all__ = [
    "is_multi_part",
    "decompose_question",
    "assemble_answers",
    "answer_with_decomposition",
    "DecompositionResult",
]
