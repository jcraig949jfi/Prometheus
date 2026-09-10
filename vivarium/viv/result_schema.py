"""WP-0f -- what an executor RETURNS, declared and checked.

`Kind` declared parameter *names* only, so nothing said what came back. Two
consequences, both real:

* an `outcome_rule.field` naming something no executor produces was only
  discovered at run time, as an `if_indeterminate` branch, one experiment at a
  time -- and an indeterminate outcome caused by a typo is indistinguishable
  in the record from one caused by the science;
* Archaeon's template builder had to keep a LOCAL copy of the result fields
  for the three live kinds, which is a second source of truth that drifts.
  Their WP-0e note says it defers to this the moment it exists.

So a kind now declares its result, `cli kinds` prints it, validation checks
the executor's OUTPUT against it, and Archaeon can check a template's
`outcome_rule.field` before admission instead of after execution.

WHAT A FIELD DECLARES
    type        number | integer | boolean | string | vector
    required    absent output is a violation, not an empty measurement
    finite      numbers only: NaN and +/-Inf are refused. A non-finite score
                compares silently as False against every threshold, so an
                outcome rule keyed on it reads as FALSIFIED rather than as
                broken -- exactly the WP-0a failure in a different costume.
    bounds      vectors only: (min_len, max_len). A witness list with no
                declared ceiling is an unbounded write into the record.
    reductions  vectors only: which E16 reductions are meaningful on it.
                `any`/`all` over a list of misclassified inputs is a question;
                `max` over a list of strings is not.

WHAT IT DOES NOT DO. It does not say whether a number is good, does not
range-check a score, and does not touch the outcome. It answers one question:
is this the SHAPE the kind promised?
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

TYPES = ("number", "integer", "boolean", "string", "vector")

#: What a vector's ELEMENTS may be. `record` is a JSON object whose INNER
#: shape this module does NOT validate -- it checks that each element is an
#: object and nothing further. It exists because an ordered list of
#: counterexamples is genuinely a list of structured records, and flattening
#: them to strings to satisfy a type system would make the record less legible
#: while proving no more about it. `describe()` and the validation result both
#: say "inner shape not validated" so that `validated: true` is never read as
#: covering something it did not check.
ELEMENTS = ("number", "integer", "boolean", "string", "record")

#: E16 reductions. Declared per vector field because a reduction that is
#: meaningless on a field should be refused at admission, not attempted.
REDUCTIONS = ("any", "all", "max", "min", "first", "count")


@dataclass(frozen=True)
class Field:
    type: str
    required: bool = True
    #: numbers/integers: reject NaN and infinities.
    finite: bool = True
    #: vectors: (min_len, max_len). max_len None means declared unbounded,
    #: which a kind must state deliberately rather than reach by omission.
    bounds: Optional[Tuple[int, Optional[int]]] = None
    #: vectors: element type, and the reductions that mean something.
    element: Optional[str] = None
    reductions: Tuple[str, ...] = ()
    note: str = ""

    def __post_init__(self):
        if self.type not in TYPES:
            raise ValueError("unknown result type %r" % self.type)
        if self.type == "vector":
            if self.bounds is None:
                raise ValueError(
                    "a vector field must declare bounds; an unbounded witness "
                    "list is an unbounded write into the record")
            if self.element not in ELEMENTS:
                raise ValueError(
                    "a vector must declare its element type, one of %s"
                    % (list(ELEMENTS),))
        for r in self.reductions:
            if r not in REDUCTIONS:
                raise ValueError("unknown reduction %r" % r)


class ResultSchemaError(ValueError):
    """The executor returned something the kind did not promise."""

    def __init__(self, kind: str, reasons: list):
        self.kind = kind
        self.reasons = list(reasons)
        super().__init__("%s: %s" % (kind, "; ".join(self.reasons)))


#: Fields every executor adds and no kind has to redeclare.
COMMON = {
    "executor": Field("string", note="which executor produced this"),
    "reproducibility": Field(
        "string", note="BIT_DETERMINISTIC | SEMANTIC | PARTIAL | "
                       "NONDETERMINISTIC, measured per result, never declared "
                       "per tool"),
}


def _check_scalar(name: str, f: Field, v, reasons: list) -> None:
    if f.type == "boolean":
        if not isinstance(v, bool):
            reasons.append("%s must be a boolean, got %s"
                           % (name, type(v).__name__))
        return
    if f.type == "string":
        if not isinstance(v, str):
            reasons.append("%s must be a string, got %s"
                           % (name, type(v).__name__))
        return
    if f.type == "integer":
        if not isinstance(v, int) or isinstance(v, bool):
            reasons.append("%s must be an integer, got %s"
                           % (name, type(v).__name__))
        return
    # number
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        reasons.append("%s must be a number, got %s" % (name, type(v).__name__))
        return
    if f.finite and not math.isfinite(v):
        reasons.append(
            "%s is %r, which is not finite. A non-finite value compares False "
            "against every threshold, so an outcome rule keyed on it would "
            "read as FALSIFIED rather than as broken" % (name, v))


def validate_result(kind_name: str, schema: Dict[str, Field], result,
                    *, truncation: Optional[dict] = None) -> dict:
    """Check `result` against `schema`. Returns metadata; raises on violation.

    `truncation` is the executor's own declaration that it cut a vector short.
    A truncated vector is legal ONLY when the executor says so -- otherwise a
    witness list at exactly its ceiling is indistinguishable from one that
    silently lost its tail.
    """
    reasons: list = []
    if not isinstance(result, dict):
        raise ResultSchemaError(kind_name,
                                ["result must be an object, got %s"
                                 % type(result).__name__])
    full = {**COMMON, **schema}
    truncation = truncation or {}

    missing = sorted(n for n, f in full.items()
                     if f.required and n not in result)
    if missing:
        reasons.append("missing required output(s) %s; an absent measurement "
                       "is not an empty one" % missing)
    unknown = sorted(set(result) - set(full))
    if unknown:
        reasons.append("unknown output field(s) %s; the result contract is "
                       "exact, and an undeclared field cannot be validated, "
                       "reduced, or read by a template" % unknown)

    vectors = {}
    for name, f in full.items():
        if name not in result:
            continue
        v = result[name]
        if f.type != "vector":
            _check_scalar(name, f, v, reasons)
            continue
        if not isinstance(v, list):
            reasons.append("%s must be a vector (list), got %s"
                           % (name, type(v).__name__))
            continue
        lo, hi = f.bounds
        if len(v) < lo:
            reasons.append("%s has %d element(s), below the declared minimum "
                           "%d" % (name, len(v), lo))
        if hi is not None and len(v) > hi:
            reasons.append("%s has %d element(s), above the declared maximum "
                           "%d" % (name, len(v), hi))
        if hi is not None and len(v) == hi and name not in truncation:
            reasons.append(
                "%s is exactly at its declared maximum %d and the executor "
                "declared no truncation; a full vector and a silently cut one "
                "must not look the same" % (name, hi))
        if f.element == "record":
            # Shape only, deliberately: see the note on ELEMENTS. The result
            # below records inner_shape_validated=False so `validated: true`
            # is never read as covering what this did not check.
            for i, item in enumerate(v):
                if not isinstance(item, dict):
                    reasons.append("%s[%d] must be an object, got %s"
                                   % (name, i, type(item).__name__))
        else:
            elem = Field(f.element)
            for i, item in enumerate(v):
                _check_scalar("%s[%d]" % (name, i), elem, item, reasons)
        vectors[name] = {"length": len(v), "bounds": list(f.bounds),
                         "truncated": bool(truncation.get(name)),
                         "element": f.element,
                         "inner_shape_validated": f.element != "record",
                         "reductions": list(f.reductions)}

    for name in truncation:
        if name not in full:
            reasons.append("truncation declared for unknown field %r" % name)
        elif full[name].type != "vector":
            reasons.append("truncation declared for non-vector field %r" % name)

    if reasons:
        raise ResultSchemaError(kind_name, reasons)
    return {"validated": True, "fields": sorted(full), "vectors": vectors,
            "truncation": dict(truncation)}


def reduction_supported(schema: Dict[str, Field], field_name: str,
                        reduction: str) -> Tuple[bool, str]:
    """May E16 reduce `field_name` with `reduction`?

    Archaeon calls this before admitting a template, so an unsupported
    reduction is refused with a reason instead of producing an experiment whose
    outcome could never mean anything."""
    full = {**COMMON, **schema}
    f = full.get(field_name)
    if f is None:
        return False, ("no output field %r; the kind declares %s"
                       % (field_name, sorted(full)))
    if f.type == "vector":
        if reduction in f.reductions:
            return True, ""
        return False, ("%r is a vector supporting %s, not %r"
                       % (field_name, list(f.reductions) or "no reductions",
                          reduction))
    if f.type in ("number", "integer"):
        return True, ""
    if reduction in ("any", "all", "first"):
        return True, ""
    return False, ("%r is a %s; %r is not meaningful on it"
                   % (field_name, f.type, reduction))


def describe(schema: Dict[str, Field]) -> list:
    """One printable line per field, for `cli kinds`."""
    out = []
    for name, f in sorted({**COMMON, **schema}.items()):
        bits = [f.type]
        if not f.required:
            bits.append("optional")
        if f.type == "vector":
            lo, hi = f.bounds
            bits.append("of %s" % f.element)
            bits.append("len %d..%s" % (lo, "unbounded" if hi is None else hi))
            if f.reductions:
                bits.append("reductions=%s" % ",".join(f.reductions))
        elif f.type in ("number", "integer") and f.finite:
            bits.append("finite")
        out.append("%-18s %s" % (name, " ".join(bits)))
    return out
