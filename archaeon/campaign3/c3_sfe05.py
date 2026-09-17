"""C3-SFE-05 -- RETENTION ECONOMICS BREAK-EVEN (campaign 3, slot 5; parent C2-SFE-06).

    python -m archaeon.campaign3.c3_sfe05 [--seeds 1..12] [--N 200 --E 16 --rung-gens 25] [--dry-run]

What is the minimum ecological price (revisit share p of earlier rungs in the training
battery) that prevents the rung-boundary forgetting cliff while adaptation continues? Arms:
p in {0, 0.05, 0.10, 0.20} and p0.10_then_0 (revisits removed the moment the elite is general
on every rung: does revisit pressure keep old competence, or does it only help the population
find a general solution after which the pressure is no longer needed?). n=12, dense probes.
Measures per run: competence per rung per probe, adaptation speed per transition (generations
from the transition to >= 0.75 on the new rung), retained rung-0 competence (final / peak),
total revisit cost (episodes), final generality, generality appearance generation.
Nothing rewards memory: the ecology charges old-rung episodes and the population does what
pays.
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from archaeon.wse import reachability as R
from archaeon.campaign3.c3base import Experiment3
from archaeon.campaign3.ladder import GENERAL_MIN, LABELS, RUNGS, run_ladder

SHARES = [0.0, 0.05, 0.10, 0.20]


class Retention(Experiment3):
    ID = "C3-SFE-05"
    TITLE = "retention economics break-even"
    PARENTS = ["C2-SFE-06", "SFE-05"]
    METRICS = ("final_r0", "final_r3", "general_gen", "revisit_cost_episodes", "general_heldout")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=list(range(1, 13)))
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--rung-gens", type=int, default=25)
    ap.add_argument("--rung0-max", type=int, default=100, help="hold rung 0 until best >= 0.5 or this many generations (0: fixed schedule)")
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = Retention(dry_run=a.dry_run, procs=a.procs)
    G_ = a.rung_gens * len(RUNGS)
    hold_max = a.rung0_max if a.rung0_max > 0 else None
    reach = X.reachability_for([(RUNGS[0], a.N, hold_max or a.rung_gens, a.E, "E0")])
    arms = ["p%s" % p for p in SHARES] + ["p0.1_then_0"]
    X.seal({
        "question": "Between p=0 and p=0.10 revisit share, where is the break-even at which rung-0 competence is retained to the end of the ladder without cost to "
                    "rung-3 adaptation; and does removing the revisit pressure once the elite is general (p0.1_then_0) keep or lose that retention?",
        "parent_evidence": "C2-SFE-06 (n=6, 3 retained seeds): p=0 lost rung 0 within 5 generations of the pressure moving; p>=0.1 retained it and RAISED final delay-4 "
                           "competence (0.36 -> 0.61-0.69); the first delay-1 solutions were delay-invariant on arrival.",
        "why_this_slot": "The campaign-2 result located the effect but not the price: the economic boundary (and whether revisits are needed after generality) is the "
                         "critical uncertainty of the retention line; n=6 with three informative seeds could not place it.",
        "assay_capability_requirement": "the p0 arm reaches rung-0 competence >= 0.5 within the rung-0 HOLD (<= %s generations; C3-SFE-03 a02 showed a fixed first rung releases the ladder before W0 is climbed in 7/12) in >= 6 of %d seeds (else POSITIVE_CONTROL_FAILED)" % (hold_max, len(a.seeds)),
        "positive_control": "rung-0 arrival under p0 within the hold of %s generations (C3-SFE-03 a05: 12/12 seeds climbed rung 0 within the hold, 12-97 generations)" % hold_max,
        "reachability_estimate": reach,
        "arms": arms,
        "crn_policy": "default; identical generation 0 and selection stream per seed across arms; batteries keyed on (generation, seed); p0.1_then_0 differs from "
                      "p0.1 only after the generality probe fires",
        "budget": {"N": a.N, "E": a.E, "rung_gens": a.rung_gens, "G_ladder": G_, "rung0_max": hold_max, "shares": SHARES, "seeds": a.seeds, "probe_dense": 5, "probe_sparse": 5, "general_min": GENERAL_MIN},
        "primary_observable": "final_r0 per arm x seed (retained rung-0 competence at the end); cost: final_r3 and adaptation speed; revisit_cost_episodes; general_gen",
        "claim_ceiling": "weak at n=%d: a break-even REGION (the smallest p with final_r0 not below p0.1's by 0.15) and a yes/no on post-generality removal" % len(a.seeds),
        "falsification_condition": "final_r0(p0.05) - final_r0(p0) < 0.15 => 5%% revisits do not retain (break-even is above 0.05); "
                                   "final_r0(p0.1_then_0) - final_r0(p0.1) < -0.15 => the pressure must continue after generality",
        "kill_condition": "positive control fails; or p0 retains rung 0 in >= 8/%d seeds (no cliff to price)" % len(a.seeds),
        "typed_failure_conditions": ["POSITIVE_CONTROL_FAILED", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["rung x generation matrices (dense)", "events per rung", "adapt_gens per transition", "revisit_cost_episodes",
                                       "general_gen and rung_at_general", "p_switched_at for the then_0 arm", "held-out per rung at the end"],
        "replacement_condition": "if C3-SFE-03 finds no generality in any seed the then_0 arm is vacuous and is dropped (4 arms remain)",
        "ancestry": "original (queue slot 5)",
        "machine_changes_exercised": ["D dense probes", "G per-step episodes with a mid-run policy change", "I"],
        "decl": {"positive_control": {"arm": "p0.0", "metric": "reached_r0_by_rung_end", "min": 1, "min_rows": 6}, "n_min": len(a.seeds),
                 "primary": {"treatment": "p0.05", "control": "p0.0", "metric": "final_r0", "min_effect": 0.15}},
    })
    X.decision("D3-009: the then_0 arm switches p to 0 at the first probe where the elite is general (all rungs >= %.2f); revisit cost is charged in episodes, not rewarded" % GENERAL_MIN)
    X.open("cmp3-sfe05")
    wid = X.world("retention", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    jobs = [{"arm": "p%s" % p, "p": p, "seed": s, "N": a.N, "E": a.E, "rung_gens": a.rung_gens, "rung0_max": hold_max} for p in SHARES for s in a.seeds] + \
           [{"arm": "p0.1_then_0", "p": 0.10, "p_after_general": 0.0, "seed": s, "N": a.N, "E": a.E, "rung_gens": a.rung_gens, "rung0_max": hold_max} for s in a.seeds]
    rows = X.pool_map(run_ladder, jobs, "ladder_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(RUNGS[0], res, N=a.N, G=r["gens_run"], E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], kind="treated")
    X.publish(wid, "matrices", "cmp3.rung_matrices.v1", {"%s_s%d" % (r["arm"], r["seed"]): {"matrix": r["matrix"], "events": r["events"]} for r in rows}, {"info_kind": "observation"})
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "arm": r["arm"], "p": r["p"], "seed": r["seed"], "N": a.N, "E": a.E, "rung_gens": a.rung_gens, "rung0_max": hold_max, "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("matrix", "schedule", "elite_summary", "elite_manifest", "gen0_provenance")},
                 "SURVIVED" if r["final_r0"] >= GENERAL_MIN else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    summ = {}
    for arm in arms:
        rs = sorted([r for r in rows if r["arm"] == arm], key=lambda r: r["seed"])
        summ[arm] = {"final_r0": [round(r["final_r0"], 2) for r in rs], "final_r3": [round(r["final_r3"], 2) for r in rs], "mean_final_r0": round(sum(r["final_r0"] for r in rs) / len(rs), 3),
                     "mean_final_r3": round(sum(r["final_r3"] for r in rs) / len(rs), 3), "fell_r0": [r["fell_r0_at"] for r in rs], "general_gen": [r["general_gen"] for r in rs],
                     "general_heldout": sum(r["general_heldout"] for r in rs), "revisit_cost": [r["revisit_cost_episodes"] for r in rs], "switched_at": [r.get("p_switched_at") for r in rs],
                     "adapt_R3": [r["adapt_gens"].get("R3") for r in rs]}
    X.receipt["summary"] = summ
    out = X.close(rows)
    print(json.dumps({"summary": summ, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
