"""G0. Five verdicts and one rule for combining them.

PASS           a qualified gate ran on complete inputs and its registered pass condition held.
FAIL           a qualified gate ran on complete inputs and its registered fail condition held: a
               defect is shown.
INDETERMINATE  a qualified gate ran on complete inputs and neither registered condition held: the
               evidence is insufficient. A registered third outcome, not an error.
BLOCKED        the gate could not run: a required input or precondition is missing. It says nothing
               about the object.
UNQUALIFIED    the gate has no authority on this object: it lacks a known positive or a known
               negative for this physics or claim, or it has never been shown able to fail. Whatever
               it printed is recorded and carries no verdict.

Only PASS lets a claim move up. The other four are different reasons for not moving, and a report
must keep them apart: UNQUALIFIED and BLOCKED are not evidence of absence, and FAIL is.
"""

PASS = "PASS"
FAIL = "FAIL"
INDETERMINATE = "INDETERMINATE"
BLOCKED = "BLOCKED"
UNQUALIFIED = "UNQUALIFIED"
ALL = (PASS, FAIL, INDETERMINATE, BLOCKED, UNQUALIFIED)

# When several gates feed one decision the combined verdict is the most informative reason for not
# passing: a shown defect first, then a gate that could not run, then one without authority, then
# one that ran and could not decide.
_RANK = {FAIL: 4, BLOCKED: 3, UNQUALIFIED: 2, INDETERMINATE: 1, PASS: 0}


class Result:
    """What a gate returns: its name, one of the five verdicts, a reason, and optional detail."""

    __slots__ = ("gate", "verdict", "reason", "detail")

    def __init__(self, gate, verdict, reason="", detail=None):
        if verdict not in ALL:
            raise ValueError("unknown verdict %r" % (verdict,))
        self.gate, self.verdict, self.reason, self.detail = gate, verdict, reason, detail

    def as_dict(self):
        out = {"gate": self.gate, "verdict": self.verdict, "reason": self.reason}
        if self.detail is not None:
            out["detail"] = self.detail
        return out

    def __repr__(self):
        return "Result(%s, %s, %r)" % (self.gate, self.verdict, self.reason)


def combine(gate, results):
    """One verdict for several results. An empty list is BLOCKED: nothing was checked."""
    results = list(results)
    if not results:
        return Result(gate, BLOCKED, "no results to combine")
    worst = max(results, key=lambda r: _RANK[r.verdict])
    reasons = ["%s: %s%s" % (r.gate, r.verdict, (" (" + r.reason + ")") if r.reason else "")
               for r in results if r.verdict != PASS]
    return Result(gate, worst.verdict, "; ".join(reasons), [r.as_dict() for r in results])
