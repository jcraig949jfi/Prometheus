"""Reasoning-oriented serialization of substrate records.

The whole experiment hinges on this file: each heterogeneous substrate
record must become a (prompt, completion) pair that teaches *mathematical
judgement* — "is this claim true, and why / why not" — with the answer
DERIVED, not leaked.

Canonical training/eval format (shared so the model's learned shape
matches what the eval grader expects):

    user:      Claim: <clean claim, no answer leak>
               Is this claim true? Answer True or False, then justify.
    assistant: <True|False>. <one-line justification>

`gold_bool` is computed from the structured payload wherever possible
(so we can also use it as the eval label), falling back to the record's
own `holds`/`verdict` only when the relation is not independently
computable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# Normalized training example
# ---------------------------------------------------------------------------

@dataclass
class Example:
    prompt: str
    completion: str
    source: str
    tier: int
    trust_weight: float
    domain: str
    outcome: str          # rejected | promoted | survived | scrap | forge | unverified | other
    is_failure: bool
    gold_bool: Optional[bool]   # gold true/false label when this is a judgeable claim; else None
    uid: str
    meta: Dict[str, Any] = field(default_factory=dict)
    entities: list = field(default_factory=list)  # underlying objects, for entity-disjoint splits

    def to_row(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "completion": self.completion,
            "source": self.source,
            "tier": self.tier,
            "trust_weight": round(self.trust_weight, 4),
            "domain": self.domain,
            "outcome": self.outcome,
            "is_failure": self.is_failure,
            "gold_bool": self.gold_bool,
            "uid": self.uid,
            "meta": self.meta,
            "entities": self.entities,
        }


JUDGE_INSTRUCTION = "Is this claim true? Answer True or False, then justify in one sentence."


def make_judgement(claim_text: str, gold_bool: bool, justification: str) -> Tuple[str, str]:
    """Return (prompt, completion) in the canonical judgement format."""
    prompt = f"Claim: {claim_text}\n{JUDGE_INSTRUCTION}"
    label = "True" if gold_bool else "False"
    completion = f"{label}. {justification}".strip()
    return prompt, completion


# ---------------------------------------------------------------------------
# Relation library (invariant_equality claims) — computes gold + justification
# ---------------------------------------------------------------------------

def _num(x: Any) -> Optional[float]:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def eval_relation(relation: str, a: Any, b: Any) -> Tuple[Optional[bool], str, str]:
    """Return (holds, english_relation, justification_template).

    holds is None if we cannot independently compute it (caller falls
    back to the record's own holds field). english_relation is a
    natural-language rendering of the relation for the claim text.
    """
    fa, fb = _num(a), _num(b)
    rel = relation or ""
    if fa is None or fb is None:
        return None, rel.replace("_", " "), ""

    ia, ib = int(fa), int(fb)
    if rel == "equal":
        holds = (fa == fb)
        eng = "are equal"
        why = f"the values are {ia} and {ib}"
    elif rel == "abs_diff_le_3":
        holds = (abs(fa - fb) <= 3)
        eng = "differ by at most 3"
        why = f"|{ia} - {ib}| = {abs(ia - ib)}"
    elif rel == "equal_mod_2":
        holds = (ia % 2 == ib % 2)
        eng = "have the same parity"
        why = f"{ia} is {'even' if ia % 2 == 0 else 'odd'} and {ib} is {'even' if ib % 2 == 0 else 'odd'}"
    elif rel == "divides":
        if ia == 0:
            return None, "divides", ""
        holds = (ib % ia == 0)
        eng = "divides"
        why = f"{ib} mod {ia} = {ib % ia}"
    else:
        return None, rel.replace("_", " "), ""

    rel_word = "holds" if holds else "fails"
    just = f"{why}, so the relation {rel_word}."
    return holds, eng, just


_CATALOG_NAME = {
    "knot": "knot",
    "ec": "elliptic curve",
    "mf": "modular form",
    "nf": "number field",
    "g2c": "genus-2 curve",
    "artin": "Artin representation",
    "lfunc": "L-function",
}


def _obj_phrase(catalog: str, invariant: str, obj: str) -> str:
    cat = _CATALOG_NAME.get(catalog, catalog)
    inv = (invariant or "invariant").replace("_", " ")
    return f"the {inv} of {cat} {obj}"


def serialize_invariant_equality(payload: Dict[str, Any],
                                 values_shown: bool = False) -> Optional[Tuple[str, bool, str]]:
    """Render an invariant_equality claim → (clean_claim, gold_bool, justification).

    If values_shown=True the actual invariant values are embedded in the
    claim, so the model is asked to JUDGE THE RELATION given the data
    (a pure reasoning task). If False the values are hidden, so a correct
    answer requires recalling the values (a recall task) — this is the
    framing that the entity-disjoint test exposes as memorization.

    Returns None if it cannot be rendered cleanly (caller falls back).
    """
    rel = payload.get("relation")
    a = payload.get("value_a")
    b = payload.get("value_b")
    holds, eng, just = eval_relation(rel, a, b)

    pa = _obj_phrase(payload.get("catalog_a", ""), payload.get("invariant_a", ""), payload.get("object_a", ""))
    pb = _obj_phrase(payload.get("catalog_b", ""), payload.get("invariant_b", ""), payload.get("object_b", ""))
    vsuffix = f" (the values are {a} and {b})" if values_shown else ""

    if holds is None:
        rec_holds = payload.get("holds")
        if rec_holds is None:
            return None
        eng = (rel or "satisfy the stated relation").replace("_", " ")
        claim = f"{pa} and {pb} {eng}{vsuffix}."
        just = f"the computed values are {a} and {b}."
        return claim, bool(rec_holds), just

    if eng == "divides":
        claim = f"{pa} divides {pb}{vsuffix}."
    else:
        claim = f"{pa} and {pb} {eng}{vsuffix}."
    return claim, holds, just


# ---------------------------------------------------------------------------
# Answer-leak stripping for free-text canonical claims
# ---------------------------------------------------------------------------

_LEAK_RE = re.compile(r"\s*\|\s*[^|]*\bholds\s*=\s*(true|false)\b.*$", re.IGNORECASE)
_VALUES_TAIL_RE = re.compile(r"\s*\|\s*[-\d\. ]+vs[-\d\. ]+\s*$", re.IGNORECASE)


def strip_answer_leak(canonical_text: str) -> str:
    """Remove the '| a vs b | holds=False' answer tail from a canonical
    claim string so it can be used as a prompt without leaking the label."""
    t = canonical_text
    t = _LEAK_RE.sub("", t)
    t = _VALUES_TAIL_RE.sub("", t)
    return t.strip()


def extract_holds(canonical_text: str, payload: Dict[str, Any]) -> Optional[bool]:
    if isinstance(payload, dict) and payload.get("holds") is not None:
        return bool(payload["holds"])
    m = re.search(r"\bholds\s*=\s*(true|false)\b", canonical_text or "", re.IGNORECASE)
    if m:
        return m.group(1).lower() == "true"
    return None
