"""G11 and G12. Custody of confirmation data, and claims as functions of evidence facets.

A claim is a record. Its level is computed from the verdicts of its facets and can go down as well
as up. Every facet names where its verdict came from. A claim cannot be rendered without its cell,
its registered setting and the class it excludes, so a verdict cannot be quoted without what it
depends on.

What these gates cannot see: whether a facet's source was really run; whether two generators with
different code are one family; whether two custodian names are one person; whether a claim that is
about structure was entered under another kind; and whether the setting and its hash were replaced
together. All are declarations. meta.known_escapes pins a case of each gate.
"""
import hashlib
import json

from .stats import is_count
from .verdict import ALL, BLOCKED, FAIL, PASS, Result, combine

# Facets every claim needs at L1, and what each further level adds.
L1 = ("registration", "power", "detection", "demand", "independence", "exposure", "resources")
L2 = ("exact_null", "attack_round", "custody", "second_implementation")
L3 = ("reproduced",)
L4 = ("predicted",)
# What a claim of each kind needs besides, at every level. NESTED cannot rest on a retention
# certificate alone: the certificate says bits crossed a boundary, and nothing about how.
KIND = {
    "EFFECT": (),
    "TRANSFER": ("new_family",),
    "MECHANISM": ("intervention",),
    "ORIGIN": ("cold_start", "class_bound"),
    "ECONOMY": ("lifecycle_cost", "frozen_comparators"),
    "NESTED": ("retention_at_boundary", "mediation", "cargo_control", "flattened_twin"),
    "LAW": ("prediction_registered",),
}
KINDS = tuple(KIND)
CUSTODY_FIELDS = ("discovery", "confirmation", "selection_data", "claim", "tuning_evaluations", "tuning_budget",
                  "rule_fixed_at", "confirmation_opened_at", "discovery_custodian", "confirmation_custodian")
CUSTODY_CLAIMS = ("NEW_FAMILY", "NEW_SEEDS")
SELECTED_ON = ("discovery", "confirmation")


def check_custody(record):
    """G11. Discovery and confirmation must be different data under different custody.

    Every problem is reported; the verdict is the worst. Generators are compared by the hash of
    their code, not by name. NEW_SEEDS claims new seeds of the same generator and may share it.
    """
    gate = "G11.custody"
    missing = [k for k in CUSTODY_FIELDS if record.get(k) in (None, "")]
    if missing:
        return Result(gate, BLOCKED, "custody record lacks: %s" % ", ".join(missing))
    d, c = record["discovery"], record["confirmation"]
    part = ("seeds", "panel_sha256", "generator_sha256")
    if any(not side.get(k) for side in (d, c) for k in part):
        return Result(gate, BLOCKED, "discovery and confirmation each need seeds, a panel hash and a generator hash")
    if not (is_count(record["tuning_evaluations"]) and is_count(record["tuning_budget"])
            and is_count(record["rule_fixed_at"]) and is_count(record["confirmation_opened_at"])):
        return Result(gate, BLOCKED, "tuning counts and the two clock readings must be non-negative integers")
    if record["claim"] not in CUSTODY_CLAIMS or record["selection_data"] not in SELECTED_ON:
        return Result(gate, BLOCKED, "claim must be one of %s and selection_data one of %s"
                      % (CUSTODY_CLAIMS, SELECTED_ON))
    found = []
    if set(d["seeds"]) & set(c["seeds"]):
        found.append(Result("seeds", FAIL, "confirmation seeds were used in discovery"))
    if d["panel_sha256"] == c["panel_sha256"]:
        found.append(Result("panel", FAIL, "the confirmation panel is the discovery panel"))
    if record["selection_data"] != "discovery":
        found.append(Result("selection", FAIL, "the reported candidate was selected on confirmation data"))
    if record["claim"] == "NEW_FAMILY" and d["generator_sha256"] == c["generator_sha256"]:
        found.append(Result("family", FAIL, "new seeds of one generator are presented as a new family"))
    if record["tuning_evaluations"] > record["tuning_budget"]:
        found.append(Result("tuning", FAIL, "tuning used %d evaluations against a registered budget of %d"
                            % (record["tuning_evaluations"], record["tuning_budget"])))
    if record["rule_fixed_at"] >= record["confirmation_opened_at"]:
        found.append(Result("rule", FAIL, "the acceptance rule was not fixed before the confirmation data was opened"))
    if record["discovery_custodian"] == record["confirmation_custodian"]:
        found.append(Result("custodian", FAIL, "one custodian holds both the discovery and the confirmation data"))
    out = combine(gate, found or [Result("all", PASS)])
    return Result(gate, out.verdict, out.reason)


def required(claim, level):
    """Facet names a claim needs in order to stand at a level (1 to 4). None for a kind that is not registered."""
    if claim.get("kind") not in KIND:
        return None
    need = list(L1) + list(KIND[claim["kind"]])
    for extra in (L2, L3, L4)[:max(0, level - 1)]:
        need += list(extra)
    return need


def facet(claim, name):
    """One facet as a result. Absent, without a source, or with an unknown verdict: BLOCKED."""
    f = claim.get("facets", {}).get(name)
    if f is None:
        return Result(name, BLOCKED, "absent")
    if not isinstance(f, dict) or f.get("verdict") not in ALL:
        return Result(name, BLOCKED, "no verdict")
    if not isinstance(f.get("source"), str) or not f["source"].strip():
        return Result(name, BLOCKED, "no source")
    return Result(name, f["verdict"])


def promote(claim, level):
    """G12. May this claim stand at this level? The verdict is the worst over the facets it needs."""
    gate = "G12.promote[L%d]" % level
    need = required(claim, level)
    if need is None:
        return Result(gate, BLOCKED, "the kind of claim is not registered: %r" % (claim.get("kind"),))
    out = combine(gate, [facet(claim, f) for f in need])
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


def setting_hash(setting):
    return hashlib.sha256(json.dumps(setting, sort_keys=True).encode("ascii")).hexdigest()


def render(claim):
    """The only way to quote a claim: kind, level, why it stands no higher, its cell, the class it excludes and
    its registered setting."""
    gate = "G12.render"
    setting, cell, excluded = claim.get("setting"), claim.get("cell"), claim.get("excluded_class")
    if not setting or not cell or not excluded or not claim.get("setting_sha256"):
        return Result(gate, BLOCKED, "a claim without its cell, the class it excludes and its registered setting may "
                      "not be quoted")
    if required(claim, 1) is None:
        return Result(gate, BLOCKED, "the kind of claim is not registered: %r" % (claim.get("kind"),))
    if setting_hash(setting) != claim["setting_sha256"]:
        return Result(gate, FAIL, "the setting quoted is not the setting that was registered")
    lv = level(claim)
    held = promote(claim, lv + 1) if lv < 4 else None
    why = "" if held is None else " (L%d withheld: %s)" % (lv + 1, held.reason)
    text = "%s, L%d%s, cell %s; excludes: %s; setting: %s" % (
        claim["kind"], lv, why, cell, excluded, "; ".join("%s = %s" % kv for kv in sorted(setting.items())))
    return Result(gate, PASS, text)
