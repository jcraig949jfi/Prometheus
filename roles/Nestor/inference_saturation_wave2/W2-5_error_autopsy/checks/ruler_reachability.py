"""Ruler-reachability check: can the gate be crossed by a planted positive, and can it refuse?

Incidents: memory guard_that_cannot_fire (require_controlled(dict(kw), dict(kw), ...));
launch_gate_needs_real_negative_controls ("HOLD" in s and "RELEASE" in s fired on #605/#631);
REDTEAM B4 (E1's implant-identity O_F decays to 0 under takeover, so "T4 dead" fires
vacuously); Bellerophon REPL-01 K3 (FM founder ruler had no route to SURVIVES); X-PAIR-NORECOMB
CLEAN_NULL with no positive arm (P-11 events 0/0); X-P2-ATTRIB negative control with 0 members;
CW01 D091 (flag read a key the statistic never writes).

    ruler(x) -> truthy when the gate FIRES (e.g. "positive / survives / detected")

Verdicts
    UNREACHABLE      fires on fewer than `min_pos_rate` of planted positives
    CANNOT_REFUSE    fires on more than `max_neg_rate` of negatives (incl. real near-miss texts)
    DEGENERATE       same output on every input (both of the above at once)
    OK               reachable and refusing
    NOT_VERIFIED     no positives or no negatives supplied, or the ruler raised on any input

Also :func:`check_guard_sides_distinct` -- a two-sided guard whose sides are the same object or
equal by value cannot fire.
"""
from typing import Any, Callable, Sequence

from . import CheckResult, OK, NOT_VERIFIED

NAME = "ruler_reachability"


def check_ruler_reachability(ruler: Callable[[Any], Any], planted_positives: Sequence,
                             negatives: Sequence, min_pos_rate: float = 0.8,
                             max_neg_rate: float = 0.0) -> CheckResult:
    if not planted_positives or not negatives:
        return CheckResult(NAME, NOT_VERIFIED,
                           "a ruler is unvalidated without BOTH a planted positive and a negative set "
                           "(n_pos=%d, n_neg=%d)" % (len(planted_positives), len(negatives)))
    try:
        pos = [bool(ruler(x)) for x in planted_positives]
        neg = [bool(ruler(x)) for x in negatives]
    except Exception as e:  # noqa: BLE001
        return CheckResult(NAME, NOT_VERIFIED, "ruler raised %s: %s" % (type(e).__name__, e))
    pr, nr = sum(pos) / len(pos), sum(neg) / len(neg)
    details = {"pos_fire_rate": pr, "neg_fire_rate": nr, "n_pos": len(pos), "n_neg": len(neg)}
    findings = [{"negative_index": i} for i, f in enumerate(neg) if f]
    unreachable, cannot_refuse = pr < min_pos_rate, nr > max_neg_rate
    if unreachable and cannot_refuse:
        return CheckResult(NAME, "DEGENERATE", "ruler does not discriminate positives from negatives",
                           details, findings)
    if unreachable:
        return CheckResult(NAME, "UNREACHABLE",
                           "planted positives cross the gate at %.2f < %.2f: a null/kill from this ruler "
                           "is vacuous" % (pr, min_pos_rate), details)
    if cannot_refuse:
        return CheckResult(NAME, "CANNOT_REFUSE",
                           "ruler fires on %.2f of negatives" % nr, details, findings)
    return CheckResult(NAME, OK, "ruler reachable by planted positives and refuses negatives", details)


def check_guard_sides_distinct(left: Any, right: Any, name: str = "guard") -> CheckResult:
    """A comparison guard must be handed two independently built objects that CAN differ."""
    if left is right:
        return CheckResult(NAME, "SELF_COMPARISON", "%s compares an object with itself" % name)
    try:
        equal = left == right
    except Exception as e:  # noqa: BLE001
        return CheckResult(NAME, NOT_VERIFIED, "cannot compare sides: %s" % e)
    if equal:
        return CheckResult(NAME, "SIDES_EQUAL",
                           "%s sides are equal by value at call time: it cannot fire on this input; feed "
                           "the genuinely differing pair or measure the property directly" % name)
    return CheckResult(NAME, OK, "%s sides differ" % name)
