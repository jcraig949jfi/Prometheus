"""C5-10 -- HELD-OUT TRIAL (campaign 5, Phase B). Rule: C5-10/RULE.md (committed before C5-05 ran).

    python -m archaeon.campaign5.c5_10 [--attempt a01] [--procs 12] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5                                     # noqa: E402
from archaeon.campaign5 import c5_09 as R9                                   # noqa: E402
from archaeon.campaign5.screen_worlds import CANDIDATES                      # noqa: E402

ID = "C5-10"
HELD_OUT_WORLDS = ("W3_K3d1", "W2_K2d4")
HELD_OUT_SEEDS = (11, 12, 13, 14, 15, 16)


def select(reach: dict) -> dict:
    """RULE.md: selectable iff net >= +4 and OLD_B net < +4; larger net wins; ties -> B_FAIL."""
    nets = {arm: reach["cells"][arm]["net"] for arm in ("OLD_B", "B_FAIL", "B_FIZZLE")}
    sel = [arm for arm in ("B_FAIL", "B_FIZZLE") if nets[arm] >= 4 and nets["OLD_B"] < 4]
    if not sel:
        return {"nets": nets, "selected": None, "reason": "no condition reached net >= +4 with OLD_B < +4"}
    best = max(nets[a] for a in sel)
    chosen = "B_FAIL" if ("B_FAIL" in sel and nets["B_FAIL"] == best) else [a for a in sel if nets[a] == best][0]
    return {"nets": nets, "selected": chosen, "reason": "net %d" % best}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempt", default=None)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5-10")
    from archaeon.campaign5.c5base import harness                            # noqa: PLC0415
    att = a.attempt or sorted(d.name for d in (C5 / "C5-09" / "attempts").iterdir() if (d / "REACH.json").exists())[-1]
    reach = json.loads((C5 / "C5-09" / "attempts" / att / "REACH.json").read_text(encoding="utf-8"))
    rule = (C5 / "C5-10" / "RULE.md").read_text(encoding="utf-8")
    sel = select(reach)
    # held-out worlds never used: check the C5-02 / C5-09 preregs' world lists
    used = set()
    for slot in ("C5-02", "C5-09"):
        for d in (C5 / slot / "attempts").iterdir():
            pr = d / "PREREG.json"
            if pr.exists():
                used.update(json.loads(pr.read_text(encoding="utf-8")).get("budget", {}).get("worlds", []))
    never_used = not (set(HELD_OUT_WORLDS) & used)

    class Trial(harness()):
        ID = "C5-10"
        TITLE = "held-out trial under the committed rule"
        PARENTS = ["C5-09"]
        ARM_FIELD = "arm"
        METRICS = ("heldout_final",)

    X = Trial(dry_run=a.dry_run, procs=a.procs)
    X.seal({
        "question": "Does the condition C5-09 selected (if any) replicate on two held-out worlds with held-out seeds, against OLD_v04 at equal total compute?",
        "parent_evidence": "C5-09 attempt %s: nets %s" % (att, json.dumps(sel["nets"])),
        "why_this_slot": "The directive's held-out trial; NO_CONDITION_SELECTED is a success of the rule.",
        "assay_capability_requirement": "held-out worlds unused by every earlier slot (%s); rule digest sealed" % never_used,
        "positive_control": "controls arm: pass >= 1.0",
        "reachability_estimate": {"note": "screened held-out worlds (receipt): W3_K3d1 .375, W2_K2d4 .552"},
        "arms": ["controls", "OLD_v04", sel["selected"] or "NONE"],
        "crn_policy": "held-out seeds 11-16; starting subsample keyed by seed; same evolver streams in both arms",
        "budget": {"worlds": list(HELD_OUT_WORLDS), "seeds": list(HELD_OUT_SEEDS), "N": 50, "G": 100, "E": 16, "selected": sel["selected"],
                   "rule_sha256": hashlib.sha256(rule.replace("\r\n", "\n").encode("utf-8")).hexdigest(), "c5_09_attempt": att},
        "primary_observable": "RULE.md: net cells >= 2 of 12 and no cell lost by >= 2/16 -> REPLICATED",
        "claim_ceiling": "one selected condition on two held-out worlds",
        "falsification_condition": "FAILED_TO_REPLICATE",
        "kill_condition": "held-out world previously used -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["NO_CONDITION_SELECTED", "FAILED_TO_REPLICATE", "INSTRUMENT_INVALID"],
        "expected_machine_telemetry": ["per-cell held-out finals"],
        "machine_changes_exercised": ["rule reader"],
        "replacement_condition": "none",
        "ancestry": "original (Phase B, slot 8)",
        "design_digest": "sha256:" + hashlib.sha256((C5 / "C5-10" / "DESIGN.md").read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 1, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": sel["selected"] or "NONE", "control": "OLD_v04", "metric": "heldout_final", "min_effect": 0.0625}},
    })
    X.open("cmp5-c5-10")
    wid = X.world("held-out-trial", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    if sel["selected"] is None:
        res = {"selection": sel, "disposition": "NO_CONDITION_SELECTED", "held_out_never_used": never_used, "wall_s": 0.0}
        grouped = [{"arm": "controls", "pass": float(never_used), "n": 1}]
        X.record(wid, {"arm": "selection"}, {"arm": "selection"}, res, "SURVIVED", key_parts=("selection",))
        X.att.write("TRIAL.json", res)
        X.publish(wid, "trial", "cmp5.c510_trial.v1", res, {"info_kind": "artifact", "label": "C5-10 NO_CONDITION_SELECTED"})
        out = X.close(grouped, addendum={"disposition": res["disposition"], "nets": json.dumps(sel["nets"])})
        print(json.dumps({"disposition": res["disposition"], "selection": sel, "close": out["disposition"]}, indent=1, default=str))
        return 0
    # the trial
    R9.WORLDS = HELD_OUT_WORLDS; R9.SPECS = {w: CANDIDATES[w] for w in HELD_OUT_WORLDS}
    parents = C1.parents_from_population()
    jobs = [{"arm": arm, "seed": s, "N": 50, "G": 100, "E": 16, "parents": parents} for arm in ("OLD_v04", sel["selected"]) for s in HELD_OUT_SEEDS]
    runs = X.pool_map(R9.run_arm, jobs, "trial_s")
    by = {(r["arm"], r["seed"]): r for r in runs}
    cells = {}; won = lost = 0; big_loss = 0
    for s in HELD_OUT_SEEDS:
        for w in HELD_OUT_WORLDS:
            d = by[(sel["selected"], s)]["worlds"][w]["heldout_final"] - by[("OLD_v04", s)]["worlds"][w]["heldout_final"]
            cells["%s/s%d" % (w, s)] = round(d, 4); won += d >= C1.BAND; lost += d <= -C1.BAND; big_loss += d <= -2 * C1.BAND
    replicated = (won - lost) >= 2 and big_loss == 0
    again = R9.run_arm(jobs[0]); det = json.dumps(again, sort_keys=True) == json.dumps(runs[0], sort_keys=True)
    screen = json.loads((C5 / "WORLD_SCREEN_2026-09-18.json").read_text(encoding="utf-8"))
    start_ok = all(by[("OLD_v04", HELD_OUT_SEEDS[0])]["worlds"][w]["start_best_heldout"] <= screen["worlds"][w]["best"] + 1e-9 for w in HELD_OUT_WORLDS)
    ctrl = {"never_used": never_used, "deterministic": det, "start_below_screen": start_ok, "pass": never_used and det and start_ok}
    res = {"selection": sel, "cells": cells, "won": won, "lost": lost, "big_loss": big_loss, "net": won - lost, "controls": ctrl,
           "disposition": "REPLICATED" if replicated else "FAILED_TO_REPLICATE", "wall_s": round(time.time() - t0, 1)}
    grouped = [{"arm": "controls", "pass": float(ctrl["pass"]), "n": 1}]
    for r in runs:
        for w in HELD_OUT_WORLDS:
            grouped.append({"arm": r["arm"], "seed": r["seed"], "world": w, "heldout_final": r["worlds"][w]["heldout_final"]})
        X.record(wid, r, {"arm": r["arm"], "seed": r["seed"]}, {k: v for k, v in r.items() if k != "worlds"} | {"worlds": {w: {k: v for k, v in r["worlds"][w].items() if not k.startswith("trace")} for w in HELD_OUT_WORLDS}},
                 "SURVIVED", key_parts=(r["arm"], r["seed"]))
    X.att.write("TRIAL.json", res); X.att.write("runs.json", runs)
    X.publish(wid, "trial", "cmp5.c510_trial.v1", res, {"info_kind": "artifact", "label": "C5-10 held-out trial"})
    out = X.close(grouped, addendum={"disposition": res["disposition"], "net": str(res["net"])})
    print(json.dumps({k: v for k, v in res.items() if k != "cells"} | {"close": out["disposition"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
