"""Mutation score: expectation (metamorphic relation per operator x stage x fixture) and classification.

EXPECTATION (declared before any mutant runs; written to out/mr_spec.json with its sha256):
  change      a correct pipeline's VERDICT must change or it must ALARM (the corruption alters the answer)
  alarm_only  the verdict may legitimately stay, but the corruption violates a recorded design/provenance
              invariant, so a correct pipeline must ALARM
  invariant   the corruption cannot alter the answer for this fixture (semantically equivalent mutant)
  unknown     the fixture's ground truth for this corruption is not known (C1 champions, some operators)

CLASSIFICATION (per operator x stage x fixture, mutant vs baseline):
  KILLED(A)    new alarm states (anomaly flag, NOT_APPLICABLE, UNDEFINED/IDENTITY-BROKEN, NOT_ELIGIBLE,
               conformance failure, exception) not present in the baseline: SELF-detection, needs no clean run
  KILLED(D)    verdict differs from the baseline, no new alarm: detection only by DIFFERENTIAL comparison
               (a clean replication); a production run has no baseline, so this is weaker than KILLED(A)
  EQUIVALENT   verdict unchanged, no alarm, and either the worlds AND reported numbers are bit-identical
               (inert) or the declared
               expectation is 'invariant' (semantically equivalent for this fixture)
  SURVIVED     verdict unchanged and no alarm where the expectation is 'change' or 'alarm_only'
               (a pipeline blind spot or an inadequate fixture; analysed one by one)
  UNRESOLVED   verdict unchanged, no alarm, worlds differ, expectation 'unknown'
  FRAGILE      verdict changed or alarmed where the expectation is 'invariant'
"""
from __future__ import annotations

import hashlib
import json


def expect(op: str, stage: str, fx) -> str:
    p = fx.props
    comm, local = p.get("comm"), p.get("local")
    sel = bool(p.get("selection"))
    timing, directed = p.get("timing"), p.get("directed")
    if stage == "oracle":
        return "change"
    if stage == "plant":
        # the plant stage runs ITS OWN plant (relay_flood, or hold_latch for HOLD) at the fixture physics
        pcomm = fx.env.family != "HOLD"
        comm, local = pcomm, not pcomm
        timing, directed = False, fx.ph.topology == "random"
        if fx.env.family not in ("RELAY", "HOLD"):
            return "unknown"          # relay_flood on XOR/MAJ/FLIP is not a known-answer positive control
    if op == "swap_labels":
        if stage == "lens_swap":
            return "change"
        if stage == "controls":
            return "change" if comm else "invariant"
        return "change" if comm else "invariant"
    if op == "duplicate_condition":
        if stage in ("controls", "lens_swap"):
            return "change"
        if stage == "plant":
            return "invariant"        # the plant verdict reads the normal arm only
        return "change" if comm else "invariant"
    if op == "control_ignored":
        if stage == "controls":
            return "change"
        if stage == "plant":
            return "invariant"
        return "change" if comm else "invariant"
    if op in ("disable_channel", "randomize_source"):
        return "change" if comm else "invariant"
    if op == "freeze_state":
        return "change"
    if op == "reverse_edges":
        if fx.ph.topology in ("ring", "torus", "global"):
            return "invariant"
        return "change" if (directed and comm) else ("invariant" if local else "unknown")
    if op == "alter_timing":
        if local:
            return "alarm_only"
        if timing is None:
            return "unknown"
        return "change" if timing else "alarm_only"
    if op == "sever_search_ruler":
        return "change"
    if op == "reuse_selection_seeds":
        return "change" if sel else "alarm_only"
    if op == "drop_mirror":
        if stage == "lens_swap":
            return "change"
        return "alarm_only"
    if op == "permute_seeds":
        if stage == "lens_swap":
            return "unknown"
        if comm and stage in ("held", "plant"):
            return "invariant"        # the control is world-independent (forced .5), pairing cannot matter
        return "unknown" if comm else "invariant"
    if op in ("silent_sensors", "invert_sign"):
        return "change"
    raise KeyError(op)


def classify(base, mut, expectation: str) -> dict:
    new_alarms = sorted(set(mut.alarms) - set(base.alarms))
    changed = mut.verdict != base.verdict
    inert = bool(base.fingerprints) and base.fingerprints == mut.fingerprints
    num = {}
    for k, v in base.numeric.items():
        w = mut.numeric.get(k)
        if isinstance(v, (int, float)) and isinstance(w, (int, float)) and not isinstance(v, bool):
            num[k] = round(w - v, 4)
    # inert worlds prove equivalence only if the reported numbers are also unchanged: a scoring/label
    # corruption leaves every World bit-identical while changing what is reported
    inert = inert and not any(num.values())
    if expectation == "invariant" and (changed or new_alarms):
        cat = "FRAGILE"
    elif new_alarms:
        cat = "KILLED(A)"
    elif changed:
        cat = "KILLED(D)"
    elif inert or expectation == "invariant":
        cat = "EQUIVALENT"
    elif expectation == "unknown":
        cat = "UNRESOLVED"
    else:
        cat = "SURVIVED"
    return {"category": cat, "expectation": expectation, "verdict_changed": changed, "new_alarms": new_alarms,
            "inert_worlds": inert, "numeric_delta": num, "base_verdict": base.verdict, "mut_verdict": mut.verdict}


def spec_table(ops, stages_by_fixture, fixtures) -> dict:
    tab = {}
    for op in ops.values():
        for st in op.stages:
            if st == "report":
                continue
            if st == "oracle":
                if op.layer == "engine":
                    tab[f"{op.name}|oracle|conformance"] = "change"
                continue
            for fname, fstages in stages_by_fixture.items():
                if st in fstages and (op.name != "reuse_selection_seeds" or st == "held"):
                    tab[f"{op.name}|{st}|{fname}"] = expect(op.name, st, fixtures[fname])
    blob = json.dumps(tab, sort_keys=True).encode()
    return {"table": tab, "sha256": hashlib.sha256(blob).hexdigest(),
            "mr": {o.name: o.mr for o in ops.values()}}
