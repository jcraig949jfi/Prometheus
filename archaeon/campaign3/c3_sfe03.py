"""C3-SFE-03 -- CORRIDOR LADDER, POWERED (campaign 3, slot 3; parent C2-SFE-06).

    python -m archaeon.campaign3.c3_sfe03 [--seeds 1..12] [--N 200 --E 16 --rung-gens 25 --p 0.1] [--dry-run]

Where in the delay ladder (W0 -> d1 -> d2 -> d4, 25 generations per rung, revisit share p=0.1)
does GENERALIZED delayed competence appear? Twelve seeds with dense transition probes (every
generation within 5 of a rung boundary, every 5 otherwise). Per seed: the first generation
at which the elite scores >= 0.75 on EVERY rung (generality), the rung being trained then,
whether R3 competence rises abruptly (generations from 0.25 to 0.75) or gradually, whether
generality survives later transitions, per-rung appear/collapse/recover events, adaptation
speed per transition, and the genotype/behaviour of the final elite (opcode composition,
persist policy, held-out per rung) to see whether different seeds find the same corridor.

The product is a corridor-table ROUTE row per seed (kind=ladder) and the instrument itself:
if generality appears reliably, the ladder is a standard way to reach W1_d4.
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from archaeon.wse import reachability as R
from archaeon.campaign3.c3base import Experiment3
from archaeon.campaign3.ladder import GENERAL_MIN, LABELS, RUNGS, run_ladder


class Corridor(Experiment3):
    ID = "C3-SFE-03"
    TITLE = "corridor ladder, powered"
    PARENTS = ["C2-SFE-06"]
    METRICS = ("general_gen", "final_r3", "final_r0", "r3_rise_gens", "general_heldout")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=list(range(1, 13)))
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--rung-gens", type=int, default=25)
    ap.add_argument("--p", type=float, default=0.1)
    ap.add_argument("--rung0-max", type=int, default=100, help="hold rung 0 until best >= 0.5 or this many generations (0: fixed schedule, the a02 design)")
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = Corridor(dry_run=a.dry_run, procs=a.procs)
    G_ = a.rung_gens * len(RUNGS)
    hold_max = a.rung0_max if a.rung0_max > 0 else None
    r0_window = hold_max or a.rung_gens
    reach = X.reachability_for([(RUNGS[0], a.N, r0_window, a.E, "E0"), (RUNGS[3], a.N, 60, a.E, "E0")])
    X.seal({
        "question": "On the delay ladder W0 -> d1 -> d2 -> d4 (rung 0 HELD until the elite reaches 0.5 training reward or %s generations, then %d generations per rung, "
                    "revisit share p=%s), at which generation and on which rung does the elite first score >= %.2f on every rung (delay generality), does it appear "
                    "abruptly or gradually, does it survive later transitions, and do different seeds find the same corridor?" % (hold_max, a.rung_gens, a.p, GENERAL_MIN),
        "parent_evidence": "C2-SFE-06 (n=6): delay-1 solutions were delay-invariant on arrival in 2 of 3 retained seeds (generation 30); the ladder reached W1_d4 "
                           "competence 0.96-1.0 in 4/6 seeds by generation 99; p >= 0.1 removed the rung-boundary forgetting cliff. Table: W1_d4 4-bit direct search RARE (1/14 at G60). "
                           "C3-SFE-03 a02 (fixed 25-generation rungs, n=12): POSITIVE_CONTROL_FAILED -- rung 0 climbed within its 25 generations in 5/12 (L3-008); the 7 seeds that "
                           "climbed rung 0 at any time went delay-general in 7/7 (held-out 1.0 on every rung), 5/7 at the same probe as R0 competence itself (r3_rise 0).",
        "why_this_slot": "Direct search rarely reaches W1_d4; if the ladder reaches it reliably and the generality's origin (rung, timing, genotype) is measurable, "
                         "the route becomes an instrument for every later rare-cell question (C3-SFE-04) instead of a rediscovered accident.",
        "assay_capability_requirement": "the population reaches rung-0 competence >= 0.5 within the rung-0 hold (<= %s generations) in >= 6 of %d seeds (else POSITIVE_CONTROL_FAILED: nothing to climb from)" % (hold_max, len(a.seeds)),
        "positive_control": "rung-0 (W0 4-bit) reached within the hold of %s generations (table: W0 pooled 13/21 by G100; a02 measured 5/12 within 25)" % hold_max,
        "reachability_estimate": reach,
        "arms": ["p%s" % a.p],
        "crn_policy": "default; one arm; seeds are the replicates; episode batteries keyed on (generation, seed)",
        "budget": {"N": a.N, "E": a.E, "rung_gens": a.rung_gens, "G_ladder": G_, "rung0_max": hold_max, "hold_min": 0.5, "p": a.p, "seeds": a.seeds, "probe_dense": 5, "probe_sparse": 5, "probe_episodes": 24,
                   "general_min": GENERAL_MIN, "rungs": [r.knobs() for r in RUNGS]},
        "primary_observable": "general_gen (first generation with elite competence >= %.2f on all four rungs) per seed and general_gen_ladder (generations after the hold); "
                              "rung_at_general; r3_rise_gens (abrupt = 0); general_survives; held-out per rung at the end" % GENERAL_MIN,
        "claim_ceiling": "an instrument reading at n=%d: the ladder reaches W1_d4 competence in k/%d seeds with a measured timescale; no mechanism is claimed" % (len(a.seeds), len(a.seeds)),
        "falsification_condition": "general_heldout in < 4 of %d seeds => the ladder is not a reliable corridor at this budget (the C2 4/6 was luck or budget). Pre-stated reading of the a02 hint: "
                                   "if generality arrives at the SAME probe as rung-0 competence in >= half of the general seeds (r3_rise 0 and rung_at_general 0), the ladder is not a corridor "
                                   "but a delay-invariant W0 solver found on rung 0 -- W1_d4 is reached by climbing W0, and the rungs add nothing" % len(a.seeds),
        "kill_condition": "positive control fails (rung 0 unreached in > half the seeds); or the ladder's W1_d4 arrival rate is not above direct search's (1/14)",
        "typed_failure_conditions": ["POSITIVE_CONTROL_FAILED", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["rung x generation matrices with dense transition probes", "appear/collapse/recover events per rung", "adaptation speed per transition",
                                       "revisit cost", "elite genome summaries", "corridor ladder rows"],
        "replacement_condition": "if C3-SFE-01 had shown W1_d4-like cells trivially reachable by direct search the ladder would be moot; it did not (W1_d4 RARE stands)",
        "ancestry": "original (queue slot 3); a03 = a02 with rung 0 held until climbed (machine change ladder.rung0_max, L3-008)",
        "machine_changes_exercised": ["D probe_plan + transition_events (plan re-anchored at the hold release)", "C corridor ladder rows", "G step API with per-step spec/episodes", "I", "ladder.rung0_max hold"],
        "decl": {"positive_control": {"arm": "p%s" % a.p, "metric": "reached_r0_by_rung_end", "min": 1, "min_rows": 6}, "n_min": len(a.seeds),
                 "primary": {"treatment": "p%s" % a.p, "control": "p%s" % a.p, "metric": "general_heldout", "min_effect": 0.0}},
    })
    X.decision("D3-008: generality = elite >= %.2f on all four rungs at a probe (24 eval episodes each), confirmed at the end by 48 held-out episodes per rung; the primary is descriptive (rate and timing), not a comparison" % GENERAL_MIN)
    X.open("cmp3-sfe03")
    wid = X.world("ladder", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    jobs = [{"arm": "p%s" % a.p, "p": a.p, "seed": s, "N": a.N, "E": a.E, "rung_gens": a.rung_gens, "rung0_max": hold_max} for s in a.seeds]
    rows = X.pool_map(run_ladder, jobs, "ladder_s")
    fid = R.default_foundry_id()
    for r in rows:
        res = r.pop("_res")
        X.reach_row(RUNGS[0], res, N=a.N, G=r["gens_run"], E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], kind="treated")
        lvl = "SUMMIT" if r["heldout_by_rung"]["R3"] >= R.SUMMIT_MIN else ("SHELF" if r["heldout_by_rung"]["R3"] >= R.SHELF_MIN else "FLOOR")
        X.corridor_row(arm=r["arm"], source_cell="ladder:W0>W1_d1>W1_d2>W1_d4(p=%s)" % a.p, target_cell="W1_d4", kind="ladder", source_maturity={"route": True},
                       source_foundry=fid, target_foundry=fid, target_budget={"N": a.N, "G": r["gens_run"], "E": a.E, "rung_gens": a.rung_gens, "rung0_max": hold_max},
                       init={"level": lvl, "seed": r["seed"], "first_summit_gen": r["events"]["R3"]["appeared"], "general_gen": r["general_gen"],
                             "heldout_r3": r["heldout_by_rung"]["R3"], "general_survives": r["general_survives"], "hold_gens": r["hold_gens"]},
                       note="dense probes; generality = all rungs >= %.2f" % GENERAL_MIN)
    X.publish(wid, "matrices", "cmp3.rung_matrices.v1", {"%s_s%d" % (r["arm"], r["seed"]): {"matrix": r["matrix"], "events": r["events"]} for r in rows}, {"info_kind": "observation"})
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "N": a.N, "E": a.E, "rung_gens": a.rung_gens, "rung0_max": hold_max, "p": a.p, "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("matrix", "schedule", "elite_summary", "elite_manifest", "gen0_provenance")},
                 "SURVIVED" if r["general_heldout"] else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    summ = {"general_gen": [r["general_gen"] for r in rows], "rung_at_general": [r["rung_at_general"] for r in rows], "r3_rise_gens": [r["r3_rise_gens"] for r in rows],
            "general_survives": sum(1 for r in rows if r["general_survives"]), "general_heldout": sum(r["general_heldout"] for r in rows),
            "final_r3": [r["final_r3"] for r in rows], "final_r0": [r["final_r0"] for r in rows], "fell_r0_at": [r["fell_r0_at"] for r in rows],
            "adapt": [r["adapt_gens"] for r in rows], "hold_gens": [r["hold_gens"] for r in rows], "hold_released_by": [r["hold_released_by"] for r in rows], "general_gen_ladder": [r["general_gen_ladder"] for r in rows], "persist": [r["persist"] for r in rows], "instr": [r["elite_summary"]["instr"] for r in rows],
            "heldout_by_rung": [r["heldout_by_rung"] for r in rows]}
    X.receipt["summary"] = summ
    out = X.close(rows)
    print(json.dumps({"summary": summ, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
