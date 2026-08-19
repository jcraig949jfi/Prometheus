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


# ---------------------------------------------------------------------------------------
# Numeric answers (task family v2). Frozen at first use, same contract as the verdict ladder:
# deterministic, and never "improved" mid-experiment.
#
# The binary extractor above has a companion defect the v2 family removes: on a True/False task
# the reasoning trace IS the answer, so no redaction can keep the residue and drop the label
# (measured: prose alone recovers gold at 72.2%). A numeric answer is a different object from
# its derivation, which is what makes break-location residue possible at all.

_ANSWER_LINE = re.compile(r"ANSWER\s*[:=]\s*(-?\d[\d,_ ]*)", re.IGNORECASE)
_TRAILING_INT = re.compile(r"(-?\d[\d,_]*)\s*\.?\s*$")
_ANY_INT = re.compile(r"-?\d[\d,_]*")


@dataclass
class NumericExtraction:
    value: int | None
    flags: list[str] = field(default_factory=list)

    @property
    def parsed(self) -> bool:
        return self.value is not None


def _to_int(s: str) -> int | None:
    try:
        return int(s.replace(",", "").replace("_", "").replace(" ", ""))
    except ValueError:
        return None


def extract_numeric(raw: str | None) -> NumericExtraction:
    """Frozen ladder: explicit ANSWER: tag -> trailing integer -> last integer anywhere."""
    flags: list[str] = []
    if raw is None:
        return NumericExtraction(None, ["null_response"])
    if not raw.strip():
        return NumericExtraction(None, ["empty"])

    text = raw
    if _THINKING_BLOCK.search(text):
        flags.append("thinking_leak")
        text = _THINKING_BLOCK.sub(" ", text)
    if _TOOL_CALL_TEXT.search(text):
        flags.append("tool_call_as_text")
        return NumericExtraction(None, flags)
    if _REFUSAL.search(text[:200]):
        flags.append("refusal")

    m = _ANSWER_LINE.search(text)
    if m:
        v = _to_int(m.group(1))
        if v is not None:
            return NumericExtraction(v, flags)
        flags.append("answer_tag_unparseable")

    stripped = _EMPHASIS.sub(" ", text).rstrip()
    m = _TRAILING_INT.search(stripped)
    if m:
        v = _to_int(m.group(1))
        if v is not None:
            flags.append("no_answer_tag")
            return NumericExtraction(v, flags)

    ints = _ANY_INT.findall(stripped)
    if ints:
        v = _to_int(ints[-1])
        if v is not None:
            flags.append("no_answer_tag")
            flags.append("last_int_fallback")
            return NumericExtraction(v, flags)

    flags.append("no_number")
    return NumericExtraction(None, flags)


# ---------------------------------------------------------------------------------------
# Numeric-answer redaction (task family v3, count answers). Same contract as the verdict
# redactor: scorer/redactor parity — anything extract_numeric() would read as an answer is
# exactly what gets removed from a rendered D0/D1 packet.
#
# The leak channels on a count task, in order of directness:
#   1. ANSWER: <n> lines            — the scorer's primary channel
#   2. standalone small integers    — the count restated in prose ("so 3 are prime")
#   3. spelled-out count words      — "three of them are prime", "all five", "none"
# Element values themselves are 4-17 digit integers and are NOT redacted — they are the
# residue. Single-digit tokens are almost surely counts or step indices; losing step indices
# is accepted over-stripping (that error direction can only shrink D0/D1 delta).

# Tag-scoped, not line-scoped: nuking the whole line eats co-located reasoning ("...gcd is 1.
# Final answer: True."), and the scorer only ever reads the token AFTER the tag — parity says
# remove exactly that.
_ANSWER_LINE_ANY = re.compile(r"(?:final\s+)?ANSWER\s*[:=]\s*\S*", re.IGNORECASE)
# Guard decimals (3.14) without protecting sentence-final counts ("count is 4."): a digit is
# redacted unless it adjoins another digit, or sits inside a decimal on either side.
_SMALL_INT = re.compile(r"(?<!\d)(?<!\d\.)[0-9](?!\d)(?!\.\d)")
_COUNT_WORDS = re.compile(
    r"\b(zero|one|two|three|four|five|none|all\s+(?:of\s+)?(?:them|five))\b", re.IGNORECASE)

NUMERIC_REDACTION_PLACEHOLDER = "[COUNT-REDACTED]"

# Per-element CONCLUSIONS are the answer, distributed: on a count task, "X is prime ... Y is
# composite" lets a reader recover the count by counting phrases, with no digit anywhere.
# Measured on real M30 packets 2026-08-19: 45% gold recovery vs 25% chance (p~0) with every
# explicit answer form already stripped. The METHOD is the residue; the per-element verdict is
# the answer. Both polarities are stripped symmetrically so the marker count stays constant
# (five elements, five conclusions) and carries no information.
_ELEMENT_CONCLUSION = re.compile(
    r"(?:is|are|was|were|appears?(?:\s+to\s+be)?|seems?(?:\s+to\s+be)?|must\s+be|"
    r"cannot\s+be|can't\s+be|therefore|thus|hence|so\s+it'?s?)\s+"
    r"(?:(?:a|an|not\s+a?n?|definitely|likely|clearly|indeed)\s+)*"
    r"(?:prime|composite|pseudoprime)(?:\s+numbers?)?",
    re.IGNORECASE)
_CONCLUSION_SHORT = re.compile(
    r"(?:prime|composite)\s*[.!:]|->\s*(?:prime|composite)|"
    r"\((?:prime|composite)\)|:\s*(?:prime|composite)",
    re.IGNORECASE)
CONCLUSION_PLACEHOLDER = "[CONCLUSION-REDACTED]"


def redact_numeric_answers(text: str) -> str:
    """Strip every form the numeric scorer (or a solver) could read the count from."""
    text = _ANSWER_LINE_ANY.sub(NUMERIC_REDACTION_PLACEHOLDER, text)
    text = _COUNT_WORDS.sub(NUMERIC_REDACTION_PLACEHOLDER, text)
    text = _SMALL_INT.sub(NUMERIC_REDACTION_PLACEHOLDER, text)
    text = _ELEMENT_CONCLUSION.sub(CONCLUSION_PLACEHOLDER, text)
    text = _CONCLUSION_SHORT.sub(CONCLUSION_PLACEHOLDER, text)
    return text


def leaks_numeric_answer(text: str) -> bool:
    """True if any channel the redactor targets survives."""
    return bool(_ANSWER_LINE_ANY.search(text) or _COUNT_WORDS.search(text)
                or _SMALL_INT.search(text))


# ---------------------------------------------------------------------------------------
# METHOD PROJECTION (2026-08-19). Measured on real M30 D0 packets: even with every explicit
# answer form and every per-element conclusion stripped, a blinded classifier recovers the
# count at 45% vs 25% chance — the leak is DIFFUSE PROSE STYLE ("only", "exactly", "quickly"),
# because the work a trace performs depends on the answer. No finite phrase list removes that.
# So the D0/D1 rendering for count-family residue is a deterministic PROJECTION onto the one
# thing the residue-plausibility argument ever claimed carries: WHICH METHODS the prior
# attempt applied. Fixed vocabulary, unordered, no counts, no per-element structure — the
# style channel is removed by construction, not by pattern-matching. This is a rendering
# reduction (R6-legal), not enrichment; its thinness is the measurement.

METHOD_VOCAB = {
    "trial-division": ("trial division", "divide by", "dividing by", "small prime", "small factor"),
    "fermat-test": ("fermat", "2^(n-1)", "pow(2,"),
    "miller-rabin": ("miller",),
    "sqrt-bound": ("sqrt", "square root", "up to the root"),
    "parity-or-last-digit": ("even", "ends in", "last digit", "parity"),
    "digit-sum-rule": ("digit sum", "sum of digits", "divisible by 3", "divisible by 9"),
    "modular-arithmetic": ("mod ", "modulo", "modular"),
    "factorization-attempt": ("factor", "factoriz", "factoris"),
}


def method_projection(attempt_text: str) -> str:
    """Deterministic, answer-free rendering of a count-family attempt: methods only."""
    low = (attempt_text or "").lower()
    seen = sorted(k for k, needles in METHOD_VOCAB.items()
                  if any(n in low for n in needles))
    if not seen:
        return "(prior attempt recorded no recognizable method vocabulary)"
    return ("prior attempt applied (method projection; prose withheld — measured diffuse "
            "answer leakage): " + ", ".join(seen))
