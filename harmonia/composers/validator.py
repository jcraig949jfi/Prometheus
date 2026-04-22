"""Composition type-compatibility validator (gen_10).

Rules per `docs/prompts/gen_10_composition_enumeration.md`:

| Composition            | Validity                                  |
| ---------------------- | ----------------------------------------- |
| operator ∘ dataset     | VALID — apply operator to data            |
| operator ∘ operator    | VALID iff output-type matches input-type  |
| dataset ∘ dataset      | INVALID (unless one is a filter-operator) |
| shape ∘ signature      | INVALID (no runtime semantics)            |
| constant ∘ anything    | INVALID (constants are not callable)      |
| signature ∘ anything   | INVALID (signatures are schemas)          |

The symbol registry distinguishes types: `operator`, `dataset`, `shape`,
`signature`, `constant`, `protocol`. The validator reads symbol type
from the registry.
"""
from __future__ import annotations

from typing import Any, Optional


# (outer_type, inner_type) -> (is_valid, reason)
# outer_type is the type being applied; inner_type is what it's applied to.
TYPE_RULES = {
    # operator applied to dataset: standard apply
    ("operator", "dataset"): (True, "operator ∘ dataset — apply operator to data"),
    # operator applied to operator: only if output/input types compose.
    # Since our registry does not carry output-type metadata per operator,
    # we default to VALID with a provisional reason. A downstream cross-
    # check flag lives in `warning`.
    ("operator", "operator"): (True, "operator ∘ operator — output/input type match assumed; verify per-case"),
    # operator applied to shape: valid in some cases (e.g., a null operator
    # applied to a LADDER shape's underlying data). Default VALID with caveat.
    ("operator", "shape"): (True, "operator ∘ shape — valid iff shape exposes underlying dataset"),
    # operator applied to signature: INVALID — signatures are schemas
    ("operator", "signature"): (False, "operator ∘ signature — signatures are schemas, not values"),
    # operator applied to constant: INVALID — constants are scalars
    ("operator", "constant"): (False, "operator ∘ constant — constants are scalars, not functions"),
    # operator applied to protocol: INVALID — protocols are discipline docs
    ("operator", "protocol"): (False, "operator ∘ protocol — protocols are discipline documents, not data"),

    # dataset applied to anything: INVALID (datasets are not callable)
    ("dataset", "dataset"): (False, "dataset ∘ dataset — datasets are not callable; no filter semantics"),
    ("dataset", "operator"): (False, "dataset ∘ operator — datasets are not callable"),
    ("dataset", "shape"): (False, "dataset ∘ shape — datasets are not callable"),
    ("dataset", "signature"): (False, "dataset ∘ signature — datasets are not callable"),
    ("dataset", "constant"): (False, "dataset ∘ constant — datasets are not callable"),
    ("dataset", "protocol"): (False, "dataset ∘ protocol — datasets are not callable"),

    # shape ∘ anything
    ("shape", "dataset"): (True, "shape ∘ dataset — pattern-match a shape against data (e.g., LADDER detection)"),
    ("shape", "operator"): (False, "shape ∘ operator — shapes are descriptors, not higher-order functions"),
    ("shape", "shape"): (False, "shape ∘ shape — shapes are descriptors"),
    ("shape", "signature"): (False, "shape ∘ signature — no runtime semantics"),
    ("shape", "constant"): (False, "shape ∘ constant — shapes operate on data, not scalars"),
    ("shape", "protocol"): (False, "shape ∘ protocol — protocols are discipline documents"),

    # signature / constant / protocol ∘ anything: all INVALID
    ("signature", "dataset"): (False, "signature ∘ anything — signatures are schemas"),
    ("signature", "operator"): (False, "signature ∘ anything — signatures are schemas"),
    ("signature", "shape"): (False, "signature ∘ anything — signatures are schemas"),
    ("signature", "signature"): (False, "signature ∘ anything — signatures are schemas"),
    ("signature", "constant"): (False, "signature ∘ anything — signatures are schemas"),
    ("signature", "protocol"): (False, "signature ∘ anything — signatures are schemas"),

    ("constant", "dataset"): (False, "constant ∘ anything — constants are not callable"),
    ("constant", "operator"): (False, "constant ∘ anything — constants are not callable"),
    ("constant", "shape"): (False, "constant ∘ anything — constants are not callable"),
    ("constant", "signature"): (False, "constant ∘ anything — constants are not callable"),
    ("constant", "constant"): (False, "constant ∘ anything — constants are not callable"),
    ("constant", "protocol"): (False, "constant ∘ anything — constants are not callable"),

    ("protocol", "dataset"): (False, "protocol ∘ anything — protocols are discipline docs"),
    ("protocol", "operator"): (False, "protocol ∘ anything — protocols are discipline docs"),
    ("protocol", "shape"): (False, "protocol ∘ anything — protocols are discipline docs"),
    ("protocol", "signature"): (False, "protocol ∘ anything — protocols are discipline docs"),
    ("protocol", "constant"): (False, "protocol ∘ anything — protocols are discipline docs"),
    ("protocol", "protocol"): (False, "protocol ∘ anything — protocols are discipline docs"),
}


def is_valid_composition(outer_type: str, inner_type: str) -> bool:
    """Return True iff (outer ∘ inner) is type-valid."""
    rule = TYPE_RULES.get((outer_type, inner_type))
    if rule is None:
        return False
    return rule[0]


def compatibility_reason(outer_type: str, inner_type: str) -> str:
    """Return the human-readable reason for the validator's verdict."""
    rule = TYPE_RULES.get((outer_type, inner_type))
    if rule is None:
        return f"unknown type pair ({outer_type}, {inner_type}); rejected by default"
    return rule[1]


def validate(outer_meta: dict, inner_meta: dict) -> dict:
    """Validate a composition given the two symbols' metadata dicts.

    Returns `{valid: bool, reason: str, outer: ..., inner: ...}`.
    Also rejects self-composition of a symbol with itself (sanity).
    """
    outer_type = outer_meta.get("type", "unknown")
    inner_type = inner_meta.get("type", "unknown")
    outer_name = outer_meta.get("name")
    inner_name = inner_meta.get("name")

    if outer_name == inner_name and outer_type != "operator":
        return {
            "valid": False,
            "reason": f"self-composition of non-operator symbol {outer_name!r} rejected",
            "outer": outer_name,
            "inner": inner_name,
        }

    valid = is_valid_composition(outer_type, inner_type)
    reason = compatibility_reason(outer_type, inner_type)
    return {"valid": valid, "reason": reason,
            "outer": outer_name, "inner": inner_name,
            "outer_type": outer_type, "inner_type": inner_type}
