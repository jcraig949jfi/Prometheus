"""The step key: ONE derivation, shared by the producer and the executor.

    step_key = "idem:" + sha256(design_digest | step_kind | parts_json)[:32]

Where it came from. archaeon/campaign2/runner.py Attempt.key() derives
sha(experiment, prereg_digest, name, *parts) since Campaign 2 fixed L2-021:
a resumed attempt with a CHANGED design replayed the previous design's
engine steps because the key did not contain the design. Here the design
digest is the first component and the database trigger in migration 006
(VIV20) recomputes the same expression and refuses a key that differs, so a
key without the design cannot enter the step table by any writer.

Why the SQL and this module must agree byte for byte. The trigger computes
    'idem:' || left(encode(sha256(convert_to(dd || '|' || kind || '|' || parts::text, 'UTF8')), 'hex'), 32)
and jsonb::text renders an ARRAY OF SCALARS exactly as json.dumps does with
its default separators (", " between elements): [1, "a", true, null]. For
that to hold, `parts` is RESTRICTED to a flat list of str / int / bool /
None. Nested objects (whose key order jsonb normalises differently) are
refused here so the two derivations can never diverge silently; the golden
fixtures in tests/test_stepkey.py pin both.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

PREFIX = "idem:"
HEX_LEN = 32


class StepKeyError(ValueError):
    pass


def canonical_parts(parts: Iterable[Any]) -> str:
    """The exact text the database trigger sees for `parts`."""
    lst = list(parts)
    for p in lst:
        if p is not None and not isinstance(p, (str, int, bool)) or isinstance(p, float):
            raise StepKeyError(
                "step parts must be a flat list of str/int/bool/null (jsonb::text "
                "parity with migration 006); got %r" % (p,))
        if isinstance(p, str) and not p.isprintable():
            raise StepKeyError("step part %r is not printable" % (p,))
    return json.dumps(lst, ensure_ascii=False)


def step_key(design_digest: str, step_kind: str, parts: Iterable[Any] = ()) -> str:
    if not isinstance(design_digest, str) or not design_digest.startswith("sha256:"):
        raise StepKeyError("design_digest must be 'sha256:<hex>', got %r" % (design_digest,))
    if not isinstance(step_kind, str) or not step_kind or "|" in step_kind:
        raise StepKeyError("step_kind must be a non-empty string without '|', got %r" % (step_kind,))
    basis = "%s|%s|%s" % (design_digest, step_kind, canonical_parts(parts))
    return PREFIX + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:HEX_LEN]


def is_step_key(value: Any) -> bool:
    return (isinstance(value, str) and value.startswith(PREFIX)
            and len(value) == len(PREFIX) + HEX_LEN
            and all(c in "0123456789abcdef" for c in value[len(PREFIX):]))
