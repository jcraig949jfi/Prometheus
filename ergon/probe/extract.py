"""Frozen verdict extractor for the Metabolization Probe (prereg §1, format-confound guard).

One deterministic regex ladder, frozen before any arm runs. No parseable verdict counts as
INCORRECT, never as missing data — and the parse-failure rate is a mandatory per-arm diagnostic,
because the 2026-06-07 greedy-LoRA kill decomposed a +0.68 headline into format-following first
and reasoning last. An extractor that silently improves on one arm would reproduce that error.

The flags are as important as the verdict: they are how we detect the failure modes that
*look* like wrong answers but are actually harness or model-config artifacts.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# The frozen prompt template contains verdict words in TWO places — "Is this claim true?" and
# "Answer True or False". Both must be stripped before looking for the model's own verdict, or
# a response that plainly says False parses as True. (Caught by the acceptance suite before any
# real call: stripping only "true or false" still left "is this claim true" in front.)
_PROMPT_FRAGMENTS = re.compile(
    r"\b(?:is\s+this\s+claim\s+true|answer\s+true\s+or\s+false|true\s+or\s+false)\b",
    re.IGNORECASE,
)
_THINKING_BLOCK = re.compile(r"<thinking>.*?</thinking>", re.IGNORECASE | re.DOTALL)
_THINKING_OPEN = re.compile(r"<thinking>", re.IGNORECASE)
_TOOL_CALL_TEXT = re.compile(
    r"(<tool_call>|<function[_ ]call>|\{\s*\"(?:name|function|tool_name|tool)\"\s*:)",
    re.IGNORECASE,
)
_REFUSAL = re.compile(
    r"\b(i (?:can(?:no|')t|cannot|am unable|'m unable)|as an ai\b|i (?:won'?t|will not) )",
    re.IGNORECASE,
)
_EMPHASIS = re.compile(r"[*_`#]+")
_VERDICT_TOKEN = re.compile(r"\b(true|false)\b", re.IGNORECASE)
_TERMINAL_PUNCT = (".", "!", "?", '"', ")", "]")

CONFLICT_WINDOW = 80  # chars: both verdicts inside this window is worth flagging


@dataclass
class Extraction:
    verdict: bool | None
    flags: list[str] = field(default_factory=list)

    @property
    def parsed(self) -> bool:
        return self.verdict is not None


def extract_verdict(raw: str | None) -> Extraction:
    """Deterministic. Same input -> same output, forever. Do not 'improve' mid-experiment."""
    flags: list[str] = []

    if raw is None:
        return Extraction(None, ["null_response"])
    if not raw.strip():
        return Extraction(None, ["empty"])

    text = raw

    # --- model-config artifacts, flagged before parsing -------------------------------
    if _THINKING_BLOCK.search(text):
        flags.append("thinking_leak")
        text = _THINKING_BLOCK.sub(" ", text)
    elif _THINKING_OPEN.search(text):
        # opened and never closed: the response was cut off inside reasoning
        flags.append("thinking_leak")
        flags.append("truncated")
        text = _THINKING_OPEN.sub(" ", text)

    if _TOOL_CALL_TEXT.search(text):
        # The thinking-disabled failure mode: a tool call written as prose. The call never
        # ran, the turn "succeeded", and nothing errored. Treat as unparseable, always.
        flags.append("tool_call_as_text")
        return Extraction(None, flags)

    if _REFUSAL.search(text[:200]):
        flags.append("refusal")

    # --- normalize --------------------------------------------------------------------
    text = _EMPHASIS.sub(" ", text)
    text = _PROMPT_FRAGMENTS.sub(" ", text)

    # --- verdict ----------------------------------------------------------------------
    matches = list(_VERDICT_TOKEN.finditer(text))
    if not matches:
        flags.append("no_verdict")
        return Extraction(None, flags)

    first = matches[0]
    verdict = first.group(1).lower() == "true"

    # Our prompt asks for the verdict first, and models comply; but record when both tokens
    # appear early, so the rate is visible rather than silently absorbed.
    early = [m.group(1).lower() for m in matches if m.start() < CONFLICT_WINDOW]
    if "true" in early and "false" in early:
        flags.append("conflict_early")

    stripped = text.rstrip()
    if stripped and not stripped.endswith(_TERMINAL_PUNCT) and "truncated" not in flags:
        flags.append("possibly_truncated")

    return Extraction(verdict, flags)


def parse_failure_rate(extractions: list[Extraction]) -> float:
    if not extractions:
        return float("nan")
    return sum(1 for e in extractions if not e.parsed) / len(extractions)
