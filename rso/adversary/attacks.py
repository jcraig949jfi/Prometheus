"""The five recurring Observatory attacks (directive Generation 5 s7; C-019-T011) as plain functions over evidence or inputs.

    DROP             remove a required shard, row or condition                          (C-017 integration dropped 1 of 6 shards)
    DUPLICATE        duplicate a row, overwriting another so the apparent count holds   (C-018 B5: a copied unit under another seed)
    REWRITE_DERIVED  rewrite derived evidence, then restore the simple invariants       (C-018-T042 R1c: a clamp array rewritten)
    CONSTANT         replace a detector with a constant classifier                      (C-017-T040: 'always INSERTED' passed Q2)
    SCRUB_ANSWER     remove or corrupt an answer- or recipe-bearing field               (C-017-T041 A2: the recipe lookup table)

Nothing here knows an engine. Every function returns a NEW object and never touches its input. An attack that would change
nothing raises ValueError: a test that cannot change its input is vacuous (rso/qualify/FALSIFIABILITY.md item 4), so the kit
refuses to run it rather than report it as passed. `fingerprint` is how the runner shows that an attack fired.
"""
import copy
import hashlib

import numpy as np

ATTACKS = ("DROP", "DUPLICATE", "REWRITE_DERIVED", "CONSTANT", "SCRUB_ANSWER")


def fingerprint(obj):
    """sha256 over a canonical walk of dicts (key-sorted), lists (ordered), numpy arrays (dtype, shape, bytes), scalars."""
    h = hashlib.sha256()

    def walk(o):
        if isinstance(o, dict):
            h.update(b"{")
            for k in sorted(o, key=repr):
                h.update(repr(k).encode() + b":")
                walk(o[k])
            h.update(b"}")
        elif isinstance(o, (list, tuple)):
            h.update(b"[")
            for v in o:
                walk(v)
            h.update(b"]")
        elif isinstance(o, np.ndarray):
            h.update(("%s|%s|" % (o.dtype.str, o.shape)).encode() + np.ascontiguousarray(o).tobytes())
        elif isinstance(o, (bytes, bytearray)):
            h.update(b"b" + bytes(o))
        else:
            h.update(repr(o).encode())
        h.update(b",")
    walk(obj)
    return h.hexdigest()


def drop(items, index=0):
    """DROP: `items` without items[index] (a shard, a row, a condition's rows). Refuses to drop from nothing."""
    if not items or not -len(items) <= index < len(items):
        raise ValueError("nothing to drop at index %r of %d items" % (index, len(items)))
    out = list(items)
    del out[index]
    return out


def duplicate(rows, src=0, dst=-1):
    """DUPLICATE: rows[dst] is replaced by a copy of rows[src], so len(rows) is unchanged. Refuses a no-op (same slot, or
    two rows already identical)."""
    n = len(rows)
    if n < 2 or not (-n <= src < n and -n <= dst < n) or src % n == dst % n:
        raise ValueError("duplicate needs two distinct slots (src=%r dst=%r of %d)" % (src, dst, n))
    if fingerprint(rows[src]) == fingerprint(rows[dst]):
        raise ValueError("rows %r and %r are already identical: the duplication changes nothing" % (src, dst))
    out = copy.deepcopy(list(rows))
    out[dst] = copy.deepcopy(rows[src])
    return out


def rewrite_derived(obj, rewrite, rebind=None):
    """REWRITE_DERIVED: apply `rewrite(copy)` in place on a deep copy, then `rebind(copy)` to restore the simple invariants a
    checker would test (counts, hashes, sums). Without `rebind` the inconsistency stays visible. Refuses a no-op."""
    out = copy.deepcopy(obj)
    rewrite(out)
    if rebind is not None:
        rebind(out)
    if fingerprint(out) == fingerprint(obj):
        raise ValueError("rewrite changed nothing")
    return out


def constant_detector(value):
    """CONSTANT: a classifier that ignores its input and always answers `value`."""
    return lambda _x: value


def _corrupt(v):
    if isinstance(v, bool):
        return not v
    if isinstance(v, int):
        return v + 1
    if isinstance(v, float):
        return v + 1.0
    if isinstance(v, str):
        return v + "~scrubbed"
    if isinstance(v, (list, tuple)):
        return [_corrupt(v[0])] + list(v[1:]) if v else ["~scrubbed"]
    if isinstance(v, dict):
        return dict(v, **{"~scrubbed": True})
    return "~scrubbed"


def scrub_answer(x, fields, mode="remove"):
    """SCRUB_ANSWER: remove (mode 'remove') or corrupt (mode 'corrupt') the named answer-bearing fields of a dict. Refuses
    a field that is not there."""
    missing = [f for f in fields if f not in x]
    if missing:
        raise ValueError("no such field(s) to scrub: %s" % missing)
    if mode not in ("remove", "corrupt"):
        raise ValueError("mode must be 'remove' or 'corrupt'")
    out = copy.deepcopy(x)
    for f in fields:
        if mode == "remove":
            del out[f]
        else:
            out[f] = _corrupt(out[f])
    return out
