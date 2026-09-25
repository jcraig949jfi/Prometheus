"""A guard is not evidence. A guard OBSERVED REFUSING a bad state is evidence.

WHY THIS EXISTS

cw01-e05 promoted learnability.require_controlled to a standing gate after CW01-D038a
(an intervention applied to a mixture but not to its own baselines, so the comparison
spanned two worlds while producing a clean-looking number). The EXECUTE driver then
called it like this:

    LN.require_controlled(dict(kw), dict(kw), "nsa/%s" % law)

The same dict, twice. The guard is present in the source, named in the frozen verdict
contract, and passes on every run. It is logically incapable of failing on any input.
It reads as a deliberate, contract-named safeguard, which is what makes it worse than
having no guard at all: it buys unearned confidence.

This is the same family as the campaign's recurring failure - conditions satisfiable
in the ABSENCE of the phenomenon:

  CW01-D022  a gain detector with no noise floor fired on pure noise
  CW01-D034  a matched-arms check passed with info=0.0 on both arms
  CW01-D035  an intervention verdict tested direction but never magnitude
  CW01-D038a a guard whose two sides were built from one expression

THE RULE

"Guard exists" is not evidence. "Guard has been observed refusing the bad state" is
evidence. Before a guard may be relied upon, it must be shown to:

  1. REFUSE a deliberately malformed case,
  2. ADMIT a well-formed case, and
  3. have those two cases be DISTINGUISHABLE from each other.

Condition 3 is the one this module exists for. Without it the fixture reproduces the
very defect it is meant to catch: a test whose bad case equals its good case passes
forever and proves nothing. prove_refuses() therefore fails closed on an
indistinguishable pair rather than reporting a comfortable PASS.

NOTE ON SCOPE: this is infrastructure for cw01-e06 onward. cw01-e05's driver is frozen
and committed under contract c80b5bfd and is NOT modified; e05's guards are proven here
retroactively, as a demonstration against real production code.
"""
from __future__ import annotations

import json


class GuardNotProven(AssertionError):
    """Raised when a guard is relied upon without an observed refusal on record."""


class VacuousFixture(AssertionError):
    """Raised when a guard fixture's bad case is indistinguishable from its good case."""


def _sig(obj):
    """A comparable signature for arbitrary call arguments."""
    try:
        return json.dumps(obj, sort_keys=True, default=repr)
    except Exception:                                   # noqa: BLE001
        return repr(obj)


def prove_refuses(guard, bad_args=(), good_args=(), expect=Exception, label="",
                  bad_kwargs=None, good_kwargs=None):
    """Observe a guard refusing a bad state and admitting a good one.

    guard       the production callable itself, never a copy or a stand-in
    bad_args    arguments that MUST be refused
    good_args   arguments that MUST be admitted
    expect      the exception type the refusal is expected to take

    Returns a verdict dict. `proven` is true only if all three conditions hold. A
    fixture whose bad and good cases are indistinguishable is reported as VACUOUS and
    is never proven, because such a fixture is the CW01-D038a defect wearing a test's
    clothing.
    """
    bad_kwargs = dict(bad_kwargs or {})
    good_kwargs = dict(good_kwargs or {})

    distinguishable = (_sig(list(bad_args)), _sig(bad_kwargs)) != \
                      (_sig(list(good_args)), _sig(good_kwargs))

    refused_bad, raised = False, None
    try:
        guard(*bad_args, **bad_kwargs)
    except expect as e:                                 # noqa: PERF203
        refused_bad, raised = True, "%s: %s" % (type(e).__name__, str(e)[:160])
    except Exception as e:                              # noqa: BLE001
        raised = "WRONG EXCEPTION %s: %s" % (type(e).__name__, str(e)[:160])

    admitted_good, good_err = False, None
    try:
        guard(*good_args, **good_kwargs)
        admitted_good = True
    except Exception as e:                              # noqa: BLE001
        good_err = "%s: %s" % (type(e).__name__, str(e)[:160])

    proven = bool(distinguishable and refused_bad and admitted_good)
    if not distinguishable:
        verdict = ("VACUOUS FIXTURE - the bad case is indistinguishable from the good case; "
                   "this fixture cannot fail and proves nothing (CW01-D038a)")
    elif not refused_bad:
        verdict = "GUARD DID NOT REFUSE the malformed case - it cannot detect anything"
    elif not admitted_good:
        verdict = "GUARD REFUSED the well-formed case too - it refuses unconditionally"
    else:
        verdict = "PROVEN - observed refusing the bad state and admitting the good one"

    return {"label": label, "guard": getattr(guard, "__qualname__", repr(guard)),
            "proven": proven, "distinguishable": distinguishable,
            "refused_bad": refused_bad, "admitted_good": admitted_good,
            "refusal": raised, "good_error": good_err, "verdict": verdict}


def require_proven(verdict):
    """Fail closed rather than relying on an unproven guard."""
    if not verdict.get("proven"):
        if not verdict.get("distinguishable"):
            raise VacuousFixture("%s %s" % (verdict.get("label", ""), verdict["verdict"]))
        raise GuardNotProven("%s %s" % (verdict.get("label", ""), verdict["verdict"]))
    return verdict


class GuardLedger:
    """Record of which guards have been OBSERVED refusing, so a driver can demand proof."""

    def __init__(self):
        self._v = {}

    def prove(self, name, guard, bad_args=(), good_args=(), expect=Exception,
              bad_kwargs=None, good_kwargs=None):
        v = prove_refuses(guard, bad_args, good_args, expect, name,
                          bad_kwargs=bad_kwargs, good_kwargs=good_kwargs)
        self._v[name] = v
        return v

    def proven(self):
        return {k for k, v in self._v.items() if v["proven"]}

    def require(self, *names):
        """Refuse to proceed while relying on a guard with no observed refusal."""
        missing = [n for n in names if n not in self.proven()]
        if missing:
            detail = "; ".join("%s: %s" % (n, self._v[n]["verdict"]) if n in self._v
                               else "%s: no fixture at all" % n for n in missing)
            raise GuardNotProven("relying on unproven guards -> %s" % detail)
        return self

    def as_dict(self):
        return {"guards": self._v,
                "n_proven": len(self.proven()), "n_total": len(self._v),
                "all_proven": len(self.proven()) == len(self._v),
                "_rule": "a guard is evidence only once it has been observed refusing a bad state"}
