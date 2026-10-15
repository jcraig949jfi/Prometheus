"""Verdict logic and the runner core (C-019-T011). Engine-agnostic.

Per attack a target reports exactly one of:
    REJECTED        the component refused the counterfeit (the refusal is quoted; a raised exception counts, with its type)
    LIMITATION <id> the component accepted it AND the variant names a recorded limitation (rso.adversary.limitations)
    SURVIVED        the component accepted it and no recorded limitation covers it: a counterfeit got a verdict
    VACUOUS         the attack did not change its input (the test proves nothing)
    NOT_APPLICABLE  the target has no such surface (a reason is required)
    ERROR           the harness itself raised outside the component call: a kit bug can never read as a rejection
Exit code: 0 all REJECTED / LIMITATION / NOT_APPLICABLE; 1 any SURVIVED; 2 any VACUOUS or ERROR (outranks 1).
"""
import collections

from rso.adversary import attacks as X, limitations as L

REJECTED, LIMITATION, SURVIVED, VACUOUS, NOT_APPLICABLE = "REJECTED", "LIMITATION", "SURVIVED", "VACUOUS", "NOT_APPLICABLE"
ERROR = "ERROR"                 # the KIT failed (not the component): never a rejection

Result = collections.namedtuple("Result", "verdict detail limitation fired")


class ComponentRaised(Exception):
    """The component under test raised: it produced no verdict (a refusal by exception). Wrap ONLY the component call in call()."""


def call(fn, *args, **kw):
    try:
        return fn(*args, **kw)
    except Exception as e:
        raise ComponentRaised(e) from e


def judge(accepted, refusal, fired, limitation=None):
    """`accepted`: the component printed / licensed a verdict on the counterfeit. `refusal`: its refusal text (or, if accepted,
    a note). `fired`: the attack changed its input. `limitation`: the recorded id this variant is expected to reach."""
    if not fired:
        return Result(VACUOUS, "the attack did not change its input: " + (refusal or "accepted"), None, False)
    if not accepted:
        return Result(REJECTED, refusal, None, True)
    if limitation is None:
        return Result(SURVIVED, refusal or "accepted", None, True)
    why = L.problems(limitation)
    if why:
        return Result(SURVIVED, "%s (%s)" % (refusal or "accepted", "; ".join(why)), None, True)
    return Result(LIMITATION, refusal or "accepted", limitation, True)


def run_variants(target, variants, not_applicable=None):
    """variants: [(attack, variant_id, fn() -> Result)]. not_applicable: {attack: reason} for every attack with no variant.
    Returns rows (dicts) in attack order. A target that leaves an attack neither run nor excused is refused."""
    not_applicable = not_applicable or {}
    uncovered = [a for a in X.ATTACKS if not any(v[0] == a for v in variants) and a not in not_applicable]
    if uncovered:
        raise ValueError("target %s neither runs nor excuses: %s" % (target, uncovered))
    rows = []
    for attack in X.ATTACKS:
        if attack in not_applicable and not any(v[0] == attack for v in variants):
            rows.append(dict(target=target, attack=attack, variant="-", verdict=NOT_APPLICABLE, detail=not_applicable[attack],
                             limitation=None, fired=False))
        for a, vid, fn in variants:
            if a != attack:
                continue
            try:
                r = fn()
            except ComponentRaised as e:              # the component raised: no verdict was produced
                inner = e.args[0]
                r = Result(REJECTED, "raised %s: %s" % (type(inner).__name__, str(inner)[:120]), None, True)
            except Exception as e:                    # anything else is the kit's own fault
                r = Result(ERROR, "KIT ERROR %s: %s" % (type(e).__name__, str(e)[:160]), None, False)
            rows.append(dict(target=target, attack=attack, variant=vid, verdict=r.verdict, detail=r.detail,
                             limitation=r.limitation, fired=r.fired))
    return rows


def run_target(name):
    from rso.adversary import targets
    t = targets.TARGETS[name]               # KeyError for an unknown target
    return run_variants(name, t["variants"], t["not_applicable"])


def exit_code(rows):
    vs = {r["verdict"] for r in rows}
    return 2 if vs & {VACUOUS, ERROR} else 1 if SURVIVED in vs else 0
