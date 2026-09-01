"""A2-GENERIC-v1 -- the FROZEN global composition basis for the closure gauntlet.

Addendum 4 (operator, 2026-09-01): "freeze a versioned global composition basis before the third
specimen ... boring substrate-independent machinery -- boolean combinators, equality/order, option
predicates, bounded counting/folding, projection, membership ... every wall gets exactly that
library. Do not tune A2 to the wall."

Frozen 2026-09-01 BEFORE any inspection of the Q045 specimen's desired mechanism. Changing this file
is an experimental intervention: bump BASIS_VERSION and report the effect on every previous
classification (hephaestus/closure_results/*.json record the basis version and hash they ran under).

Types used by specs: int, bool, str, float, pair (2-tuple), list (of anything), list_bool,
opt_list (list | None), dict (key -> collection), edges (list of pairs; treated as list AND pair source).
No op here knows anything about quantifiers, relations, graphs, or any wall.
"""
from __future__ import annotations

import hashlib
import inspect

BASIS_VERSION = "A2-GENERIC-v1"


def _keys(d):
    return list(d.keys())


def _values(d):
    return list(d.values())


def _diag(d):
    """For each key k of a key->collection mapping: is k a member of its own collection?
    Generic reflexivity projection (membership + projection + fold), not a graph op."""
    return [k in v for k, v in d.items()]


A2_GENERIC: dict[str, tuple[tuple[str, ...], str, object]] = {
    # boolean combinators
    "not":        (("bool",), "bool", lambda a: not a),
    "and":        (("bool", "bool"), "bool", lambda a, b: a and b),
    "or":         (("bool", "bool"), "bool", lambda a, b: a or b),
    # equality / order on ints
    "eq":         (("int", "int"), "bool", lambda a, b: a == b),
    "lt":         (("int", "int"), "bool", lambda a, b: a < b),
    "le":         (("int", "int"), "bool", lambda a, b: a <= b),
    # option predicates
    "is_none":    (("opt_list",), "bool", lambda x: x is None),
    "is_some":    (("opt_list",), "bool", lambda x: x is not None),
    # bounded counting / folding
    "len_list":   (("list",), "int", lambda x: len(x)),
    "len_edges":  (("edges",), "int", lambda x: len(x)),
    "len_dict":   (("dict",), "int", lambda x: len(x)),
    "count_true": (("list_bool",), "int", lambda x: sum(1 for b in x if b)),
    "any_true":   (("list_bool",), "bool", lambda x: any(x)),
    "all_true":   (("list_bool",), "bool", lambda x: all(x)),
    # projection
    "first":      (("pair",), "int", lambda p: p[0]),
    "second":     (("pair",), "int", lambda p: p[1]),
    "keys":       (("dict",), "list", _keys),
    "values":     (("dict",), "list", _values),
    # membership (generic, over key->collection mappings)
    "diag":       (("dict",), "list_bool", _diag),
}


def basis_hash() -> str:
    src = "".join(f"{k}:{v[0]}->{v[1]}:{inspect.getsource(v[2]) if not isinstance(v[2], type(lambda: 0)) or v[2].__name__ != '<lambda>' else repr(v[0])+repr(v[1])}"
                  for k, v in sorted(A2_GENERIC.items()))
    return hashlib.sha256((BASIS_VERSION + src).encode()).hexdigest()[:16]


def summary() -> dict:
    return {"version": BASIS_VERSION, "hash": basis_hash(), "ops": {k: f"{v[0]} -> {v[1]}" for k, v in A2_GENERIC.items()}}
