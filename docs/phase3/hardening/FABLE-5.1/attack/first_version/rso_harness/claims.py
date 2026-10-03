"""G11 and G12. Custody of confirmation data, and claims as functions of evidence facets.

A claim is a record. Its level is computed from the verdicts of its facets and can go down as well
as up. A claim cannot be rendered without its conditions, so a verdict cannot be quoted without the
setting it depends on.
"""
from .verdict import BLOCKED, FAIL, INDETERMINATE, PASS, UNQUALIFIED, Result, combine

KINDS = ("EFFECT", "TRANSFER", "MECHANISM", "LAW")

# Facets required at each display level. L1 qualified, L2 robust, L3 reproduced, L4 predicted.
L1 = ("registration", "power", "detection", "demand", "independence", "exposure")
L2 = ("exact_null", "attack_round", "custody", "second_implementation")
L3 = ("reproduced",)
L4 = ("predicted",)
MECHANISM = ("intervention",)


def check_custody(record):
    """G11. Discovery and confirmation must be different data under different custody."""
    gate = "G11.custody"
    need = ("discovery", "confirmation", "selection_data", "claim", "tuning_evaluations", "tuning_budget")
    missing = [k for k in need if record.get(k) is None]
    if missing:
        return Result(gate, BLOCKED, "custody record lacks: %s" % ", ".join(missing))
    d, c = record["discovery"], record["confirmation"]
    if set(d["seeds"]) & set(c["seeds"]):
        return Result(gate, FAIL, "confirmation seeds were used in discovery")
    if d["panel_sha256"] == c["panel_sha256"]:
        return Result(gate, FAIL, "confirmation panel is the discovery panel")
    if record["selection_data"] != "discovery":
        return Result(gate, FAIL, "the reported candidate was selected on confirmation data")
    if record["claim"] == "NEW_FAMILY" and d["generator"] == c["generator"]:
        return Result(gate, FAIL, "new seeds of the same generator are presented as a new family")
    if record["tuning_evaluations"] > record["tuning_budget"]:
        return Result(gate, FAIL, "tuning used %d evaluations against a registered budget of %d"
                      % (record["tuning_evaluations"], record["tuning_budget"]))
    return Result(gate, PASS)


def required(claim, level):
    """Facet names a claim needs in order to stand at a level (1 to 4)."""
    if claim.get("kind") not in KINDS:
        raise ValueError("claim kind must be one of %s" % (KINDS,))
    need = list(L1) + (list(MECHANISM) if claim["kind"] == "MECHANISM" else [])
    for extra in (L2, L3, L4)[:max(0, level - 1)]:
        need += list(extra)
    return need


def promote(claim, level):
    """G12. May this claim stand at this level? Absent facets block; non-PASS facets carry their own verdict."""
    gate = "G12.promote[L%d]" % level
    facets = claim.get("facets", {})
    need = required(claim, level)
    absent = [f for f in need if f not in facets]
    if absent:
        return Result(gate, BLOCKED, "facets absent: %s" % ", ".join(absent))
    results = [Result(f, facets[f]) for f in need]
    out = combine(gate, results)
    return Result(gate, out.verdict, out.reason)


def level(claim):
    """Highest level at which the claim stands now. L0 means a logged run and nothing more."""
    best = 0
    for lv in (1, 2, 3, 4):
        if promote(claim, lv).verdict == PASS:
            best = lv
        else:
            break
    return best


def render(claim):
    """The only way to quote a claim: kind, level, cell and every condition travel with it."""
    conditions = claim.get("conditions")
    if not conditions or not claim.get("cell"):
        return Result("G12.render", BLOCKED, "a claim without its cell and conditions may not be quoted")
    text = "%s, L%d, cell %s; conditions: %s" % (
        claim["kind"], level(claim), claim["cell"], "; ".join("%s = %s" % kv for kv in sorted(conditions.items())))
    return Result("G12.render", PASS, text)


__all__ = ["check_custody", "promote", "level", "render", "required", "BLOCKED", "FAIL", "INDETERMINATE", "PASS",
           "UNQUALIFIED"]
