"""Priority pass: score every candidate perturbation for EXPECTED OPPORTUNITY (never truth),
apply the anti-gravity bonus, enforce diversity, reserve serendipity slots, freeze the top ten.

Scores are explicit integers 0-3 per criterion, recorded on each candidate in
PERTURBATIONS.jsonl by the reconciling session; this script only combines them, so the
ranking is auditable and reproducible from the file.

    python prioritize.py <date-tag>
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import recordsafety as RS      # noqa: E402

CRITERIA = {                      # weight per criterion; each candidate scores 0-3
    "attacks_old_assumption": 2.0,      # a later discovery attacks one of its assumptions
    "failure_surface_perturbable": 2.0,  # a known failure surface is now perturbable
    "unexplained_structure": 1.5,
    "independent_intersection": 1.5,     # independent experiments now intersect it
    "regime_newly_reachable": 1.5,
    "information_gain": 2.0,
    "delta_novelty": 1.5,                # meaningfully different from prior attempts
    "mechanism_discrimination": 1.5,
    "cost_now_lower": 1.0,
    "null_becomes_contrast": 1.0,
    "inconclusive_now_posable": 1.5,
    "underexplored_hard_to_operationalise": 1.0,
}
ANTI_GRAVITY_BONUS = 4.0
SLOTS = 10
SERENDIPITY_SLOTS = 2             # a minority, reserved
MAX_PER_PARENT = 2
MAX_PER_FAMILY = 3
MIN_AWKWARD = 2                   # from stasis / anti-gravity / long-untouched branches


def score(c):
    s = sum(CRITERIA[k] * float(c["scores"].get(k, 0)) for k in CRITERIA)
    if c.get("anti_gravity"):
        s += ANTI_GRAVITY_BONUS
    return round(s, 2)


def main(tag, prefix=None, slots=None):
    """prefix: restrict to candidates whose parent starts with it (a scoped tranche); slots: override SLOTS."""
    global SLOTS
    if slots:
        SLOTS = int(slots)
    raw = [json.loads(l) for l in (HERE / "PERTURBATIONS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    byid = {}
    for d in raw:                                 # amendment lines merge onto the candidate they name
        if d.get("amend"):
            if d["id"] in byid:
                byid[d["id"]].update({k: v for k, v in d.items() if k not in ("amend", "id")})
        else:
            byid[d["id"]] = d
    cands = [c for c in byid.values() if not c.get("superseded_by") and not c.get("executed_in")]
    if prefix:
        cands = [c for c in cands if str(c.get("parent", "")).startswith(prefix)]
        for c in cands:                           # scoped tranche: diversity is over AXES, not the shared family label
            c["family"] = c.get("axis") or c["family"]
    states = {}
    for l in (HERE / "STATE.jsonl").read_text(encoding="utf-8").splitlines():
        if l.strip():
            e = json.loads(l)
            states[e["trajectory_id"]] = e["state"]
    for c in cands:
        c["score"] = score(c)
        c["parent_state"] = states.get(c["parent"], "UNKNOWN")
        c["awkward"] = bool(c.get("anti_gravity") or str(c["parent_state"]).startswith("TEMPORAL_STASIS"))   # scoped labels too (D079)
    # a candidate whose parent is in (scoped) stasis is eligible ONLY if it states how it escapes the boundary
    cands = [c for c in cands if not (str(c["parent_state"]).startswith("TEMPORAL_STASIS") and not c.get("escapes_stasis"))]
    ranked = sorted(cands, key=lambda c: (-c["score"], c["id"]))

    chosen, per_parent, per_family, why = [], {}, {}, {}

    def admit(c, reason):
        chosen.append(c)
        per_parent[c["parent"]] = per_parent.get(c["parent"], 0) + 1
        per_family[c["family"]] = per_family.get(c["family"], 0) + 1
        why[c["id"]] = reason

    executed = {d["id"] for d in raw if d.get("amend") and d.get("executed_in")}

    def fits(c):
        # a candidate that cannot run without another candidate's RESULT (`requires`) is admitted only
        # when every requirement is already chosen or executed (D080 standing rule; cycle 5)
        return (per_parent.get(c["parent"], 0) < MAX_PER_PARENT
                and per_family.get(c["family"], 0) < MAX_PER_FAMILY
                and c["id"] not in why
                and all((r in why) or (r in executed) for r in (c.get("requires") or [])))

    # 0. deformation slots: one per deformation family (A/B/C...) so a material deformation found
    #    in one cycle cannot disappear into global scoring in the next
    for fam in sorted({x["deformation"] for x in ranked if x.get("deformation")}):
        for c in [x for x in ranked if x.get("deformation") == fam]:
            if fits(c):
                admit(c, "deformation slot (%s)" % fam)
                break
    # 1. serendipity slots first (by score among serendipity candidates), so the priority
    #    function cannot crowd them out
    for c in [x for x in ranked if x.get("serendipity")]:
        if len([x for x in chosen if x.get("serendipity")]) >= SERENDIPITY_SLOTS:
            break
        if fits(c):
            admit(c, "serendipity slot")
    # 2. awkward / anti-gravity minimum
    for c in [x for x in ranked if x["awkward"] and not x.get("serendipity")]:
        if len([x for x in chosen if x["awkward"] and not x.get("serendipity")]) >= MIN_AWKWARD:
            break
        if fits(c):
            admit(c, "anti-gravity / stasis protection")
    # 3. fill by score under diversity constraints
    for c in ranked:
        if len(chosen) >= SLOTS:
            break
        if fits(c):
            admit(c, "score under diversity constraints")
    chosen = chosen[:SLOTS]
    frozen_ids = [c["id"] for c in chosen]

    out = {"tag": tag, "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "criteria_weights": CRITERIA,
           "anti_gravity_bonus": ANTI_GRAVITY_BONUS, "slots": SLOTS, "serendipity_slots": SERENDIPITY_SLOTS,
           "max_per_parent": MAX_PER_PARENT, "max_per_family": MAX_PER_FAMILY, "min_awkward": MIN_AWKWARD,
           "n_candidates": len(cands),
           "ranked": [{"id": c["id"], "parent": c["parent"], "family": c["family"], "type": c["type"],
                       "score": c["score"], "anti_gravity": bool(c.get("anti_gravity")),
                       "serendipity": bool(c.get("serendipity")), "parent_state": c["parent_state"],
                       "cost_minutes": c.get("cost_minutes")} for c in ranked],
           "frozen_top_ten": [{"rank": i + 1, "id": c["id"], "parent": c["parent"], "family": c["family"],
                               "type": c["type"], "score": c["score"], "admitted_by": why[c["id"]],
                               "delta": c["delta"], "unchanged": c["unchanged"], "attacks": c["attacks"],
                               "why_now": c.get("why_now") or c.get("nonredundant"), "axis": c.get("axis"),
                               "deformation": c.get("deformation"), "continuation": c.get("continuation"),
                               "cost_minutes": c.get("cost_minutes")}
                              for i, c in enumerate(chosen)],
           "waiting_not_rejected": [c["id"] for c in ranked if c["id"] not in frozen_ids],
           "_rule": "rank is temporary; exclusion is waiting, not rejection; the ordering allocates compute, not truth"}
    p = HERE / ("PRIORITY_%s.json" % tag)
    p.write_text(json.dumps(out, indent=1, ensure_ascii=True), encoding="utf-8")
    RS.require_ascii_safe(p)
    print("candidates %d | frozen top %d -> %s" % (len(cands), len(chosen), p.name))
    for c in out["frozen_top_ten"]:
        print("  %2d %-10s %-7s %5.1f  %-12s %s" % (c["rank"], c["id"], c["parent"], c["score"], c["type"], c["admitted_by"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else time.strftime("%Y-%m-%d"),
                  prefix=(sys.argv[2] if len(sys.argv) > 2 else None),
                  slots=(sys.argv[3] if len(sys.argv) > 3 else None)))
