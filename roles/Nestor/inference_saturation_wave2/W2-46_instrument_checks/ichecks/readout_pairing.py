"""Class (g): comparisons of unlike readouts.

Incidents:
  * W2-14 / W2-22: F's ATOMIC "validation failure" (0.23 vs 0.67) compared the model's ``depth_f`` (founder tree,
    300 epochs) with the world's depth read at 2000 epochs (whole-field causal depth). On matched readouts
    (``depth_world`` at 300 on both sides) the model is not significantly different (n = 30).
  * W2-28 (k) / W2-25 F4: per-call m (one interaction, realized partners) equated with lifetime m_c (certified births
    over a member's life); "critical" vs "subcritical" were different readouts.
  * W2-28 trace: W2-2's "1 vs 7.7" took the expected count from 320 runs and the observed from the 192-run pool
    (denominator mismatch).

Two checks.

``check_readout_pairing(spec_a, spec_b)``: each spec is a dict over the core fields
``quantity, unit, horizon, estimator, population`` (and optional ``denominator``, ``ruler``, ``partner_stream``).
    UNLIKE_READOUTS   a field declared on both sides differs
    OK                every core field declared on both sides and equal
    NOT_VERIFIED      a core field is missing on either side (cannot certify the pairing)

``check_record_key_pairing(rows_a, key_a, rows_b, key_b)``: a comparison of two record sets by named fields.
    UNLIKE_READOUTS   key_a != key_b (details say whether a MATCHED key exists on both sides, i.e. the like-for-like
                      comparison was available and not used)
    OK                the same key on both sides
    NOT_VERIFIED      a key is absent from its rows, or a side is empty
"""
from __future__ import annotations

import re
from typing import Dict, List, Sequence

from . import CheckResult, NOT_VERIFIED, OK

NAME_SPEC = "readout_pairing"
NAME_KEYS = "record_key_pairing"
CORE = ("quantity", "unit", "horizon", "estimator", "population")
OPTIONAL = ("denominator", "ruler", "partner_stream")


def check_readout_pairing(spec_a: Dict, spec_b: Dict, core: Sequence[str] = CORE) -> CheckResult:
    diffs: List[Dict] = []
    missing = []
    for f in tuple(core) + OPTIONAL:
        a, b = spec_a.get(f), spec_b.get(f)
        if a is None or b is None:
            if f in core:
                missing.append(f)
            continue
        if a != b:
            diffs.append({"field": f, "a": a, "b": b})
    details = {"a": spec_a, "b": spec_b, "missing_core": missing}
    if diffs:
        return CheckResult(NAME_SPEC, "UNLIKE_READOUTS",
                           "readouts differ in %s: compare like with like or model the conversion"
                           % ", ".join(d["field"] for d in diffs), details, diffs)
    if missing:
        return CheckResult(NAME_SPEC, NOT_VERIFIED, "core fields not declared on both sides: %s" % missing, details)
    return CheckResult(NAME_SPEC, OK, "readouts match on every core field", details)


def check_record_key_pairing(rows_a: Sequence[Dict], key_a: str, rows_b: Sequence[Dict], key_b: str) -> CheckResult:
    if not rows_a or not rows_b:
        return CheckResult(NAME_KEYS, NOT_VERIFIED, "a side has no rows")
    has = lambda rows, k: all(k in r for r in rows)  # noqa: E731
    if not has(rows_a, key_a) or not has(rows_b, key_b):
        return CheckResult(NAME_KEYS, NOT_VERIFIED, "key missing from some rows (%s in a: %s; %s in b: %s)"
                           % (key_a, has(rows_a, key_a), key_b, has(rows_b, key_b)))
    if key_a == key_b:
        return CheckResult(NAME_KEYS, OK, "same readout key %r on both sides" % key_a)
    tok = lambda k: {t for t in re.split(r"[_\d]+", k.lower()) if len(t) > 1}  # noqa: E731
    family = tok(key_a) | tok(key_b)
    shared = set(rows_a[0]) & set(rows_b[0])
    common = sorted(k for k in shared if tok(k) & family and has(rows_a, k) and has(rows_b, k))
    details = {"key_a": key_a, "key_b": key_b, "matched_keys_available": common}
    return CheckResult(NAME_KEYS, "UNLIKE_READOUTS",
                       "compares %r with %r%s" % (key_a, key_b, "; the matched key(s) %s exist on BOTH sides" % common
                                                  if common else "; no matched key exists on both sides"),
                       details, [{"matched": k} for k in common])
