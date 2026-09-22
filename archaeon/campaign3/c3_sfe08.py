"""C3-SFE-08 (REPLACEMENT, D3-013) -- DOES PARTIAL CREDIT BUILD THE SHELF? (campaign 3, slot 8).

    python -m archaeon.campaign3.c3_sfe08 [--seeds 1..12] [--G 300] [--dry-run]

The original slot 8 (wall-clock producer-consumer with a FULL-solve criterion) required a
meaningful full-solve regime. C3-SFE-01 found none: 0 confirmed summits and 0 candidates in 24
runs of 300 generations on W2_K2, summit OBSERVED_UNREACHABLE at every ladder point. The
directive's replacement rule and preferred direction A (shelf / summit) give this question.

C3-SFE-02 showed the W2_K2 shelf is a ONE-VALUE memory paying ~0.5 because HALF the asks are
about the remembered stream, and that every second-stream gain in its neighbourhood costs the
first (58/58). That half credit is a property of the READOUT, not of the task: per-ask credit
pays an organism that solves nothing. Arms:

  per_ask   selection on per-ask credit (every campaign so far)
  episode   selection on ALL-OR-NOTHING episode credit (a correct episode requires EVERY ask
            correct; the one-value memory earns 0)

Both arms are read out identically at the end (held-out per-ask AND episode competence), so
levels stay comparable. If the shelf is a reward-shaping trap, the episode arm should leave the
floor less often but reach higher when it does; if the summit is out of reach for structural
reasons, neither arm reaches it and the shelf is not a trap but a ceiling.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List

from archaeon.wse import reachability as R
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2
from archaeon.campaign3.c3base import CAMPAIGN_SEED, Experiment3, level_fields

TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
ARMS = ["per_ask", "episode"]
LADDER = [60, 100, 150, 200, 300]
HELDOUT_N = 48


def run_arm(job: dict) -> dict:
    arm, seed, N, E, G_ = job["arm"], job["seed"], job["N"], job["E"], job["G"]
    t0 = time.time()
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c3-sfe08-" + arm, foundry=FOUNDRY_C2, reward_mode=arm)
    ho = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, HELDOUT_N)
    per_ask_tb: List[float] = []                       # the COMMON yardstick: per-ask credit of the arm's elite
    ep_tb: List[float] = []
    first_summit = None; candidates = 0
    for g in range(G_):
        row = ev.evaluate_generation(last=(g == G_ - 1))
        top = ev.scored[0][2]
        per_ask_tb.append(round(top["reward_per_ask"], 6)); ep_tb.append(round(top["reward_episode"], 6))
        if per_ask_tb[-1] >= R.SUMMIT_MIN:
            candidates += 1
            if first_summit is None and evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward_per_ask"] >= R.SUMMIT_MIN:
                first_summit = g
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    e = evaluate(res["elite"]["manifest"], ho, rng_seed=7)
    lv = level_fields(res, e["reward_per_ask"])
    # levels are always read on the per-ask yardstick so the two arms are comparable
    first_shelf = R.first_at(per_ask_tb, R.SHELF_MIN)
    lv["first_shelf_gen"] = first_shelf
    lv["best_train_max"] = round(max(per_ask_tb), 6)
    lv["level"] = R.level_of(max(per_ask_tb), e["reward_per_ask"])
    lv["first_summit_gen"] = first_summit
    return {"arm": arm, "seed": seed, "G": G_, "competence_heldout": round(e["reward_per_ask"], 4), "heldout_episode": round(e["reward_episode"], 4),
            "heldout_per_ask": [round(x, 4) for x in e.get("per_ask_reward", [])], **lv,
            "shelf_reached": int(first_shelf is not None), "summit": int(first_summit is not None), "summit_candidates": candidates,
            "best_per_ask_max": round(max(per_ask_tb), 4), "best_episode_max": round(max(ep_tb), 4), "final_per_ask": per_ask_tb[-1], "final_episode": ep_tb[-1],
            "gens_at_floor": sum(1 for x in per_ask_tb if x < R.SHELF_MIN), "gens_on_shelf": sum(1 for x in per_ask_tb if R.SHELF_MIN <= x < R.SUMMIT_MIN),
            "shelf_residence": None if first_shelf is None else ((first_summit if first_summit is not None else G_) - first_shelf),
            "ladder": {str(g): {"shelf": int(first_shelf is not None and first_shelf < g), "summit": int(first_summit is not None and first_summit < g),
                                "best_per_ask": round(max(per_ask_tb[:g]) if per_ask_tb[:g] else 0.0, 4), "best_episode": round(max(ep_tb[:g]) if ep_tb[:g] else 0.0, 4)}
                       for g in LADDER if g <= G_},
            "elite_summary": res["elite_summary"], "trace_per_ask": per_ask_tb, "trace_episode": ep_tb,
            "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"], "wall_s": round(time.time() - t0, 1), "_res": res}


class PartialCredit(Experiment3):
    ID = "C3-SFE-08"
    TITLE = "does partial credit build the shelf?"
    PARENTS = ["C3-SFE-01", "C3-SFE-02"]
    METRICS = ("competence_heldout", "best_per_ask_max", "best_episode_max", "first_shelf_gen", "first_summit_gen")


def med(xs):
    xs = sorted(x for x in xs if x is not None)
    return None if not xs else xs[len(xs) // 2]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=list(range(1, 13)))
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--G", type=int, default=300)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = PartialCredit(dry_run=a.dry_run, procs=a.procs)
    reach = X.reachability_for([(TARGET, a.N, g, a.E, "E0") for g in LADDER if g < a.G] + [(TARGET, a.N, a.G, a.E, "E0")])
    X.seal({
        "question": "On W2_K2 4-bit (N=%d, E=%d, G=%d), does selection on ALL-OR-NOTHING episode credit (an episode counts only if every ask is correct) change where "
                    "the search ends up, compared with the per-ask partial credit every campaign has used: fewer runs on the half-credit shelf, and any run reaching "
                    "the summit?" % (a.N, a.E, a.G),
        "parent_evidence": "C3-SFE-01 (n=24, G300): 0 confirmed summits, 0 candidates; fresh runs reach the shelf in 11/12 (median ~90 generations) and stay, residence "
                           "censored at 300 everywhere; end-of-run held-out per ask ~0.5/0.5. C3-SFE-02 (n=12 shelf elites, 400 grammar children each): the shelf is a "
                           "one-value memory (first-put 6/12, last-put 4/12), 1 improving child in 4,800, every second-stream gain (58/58) costs the first, 0/480 greedy "
                           "paths to 0.90. The shelf pays ~0.5 under per-ask credit while solving neither stream: that half credit is a readout property.",
        "why_this_slot": "the original slot 8 is dead (it required a full-solve regime C3-SFE-01 showed does not exist). Direction A asks what makes the shelf. If the "
                         "shelf is an artefact of partial credit, the reward readout is a design variable for every K>=2 cell in campaign 4; if the summit is unreached "
                         "under both readouts, the ceiling is structural and no reward shaping will move it -- and campaign 4 must change the organism or the search, "
                         "not the payoff.",
        "assay_capability_requirement": "the per_ask arm reproduces C3-SFE-01's shelf rate (>= 8 of %d seeds reach the shelf) -- else the assay is not the one that "
                                        "produced the parent evidence" % len(a.seeds),
        "positive_control": "per_ask arm on W2_K2 4-bit (table: shelf in 11/12 at G300, C3-SFE-01)",
        "reachability_estimate": reach,
        "arms": ARMS,
        "crn_policy": "default; both arms share generation 0 per seed and the same per-generation batteries (episodes are keyed on (generation, cell seed)); only the "
                      "fitness readout differs; both arms are SCORED at the end on the same held-out battery with both readouts",
        "budget": {"N": a.N, "E": a.E, "G": a.G, "seeds": a.seeds, "arms": ARMS, "heldout_n": HELDOUT_N, "target": TARGET.knobs(), "runs": len(ARMS) * len(a.seeds)},
        "primary_observable": "summit arrival (held-out per-ask >= 0.90) per seed, and, since both arms are expected to be summit-free, the preregistered secondary "
                              "ladder: shelf arrival rate, generations on the shelf, best per-ask and best episode credit reached",
        "claim_ceiling": "one cell, one organism family, n=%d per arm at G=%d: whether the half-credit shelf survives the removal of partial credit; no claim about "
                         "which readout is 'right', and none about cells other than W2_K2" % (len(a.seeds), a.G),
        "falsification_condition": "the episode arm reaches the shelf as often as the per_ask arm AND neither reaches a summit => partial credit does not build the "
                                   "shelf; the half-credit plateau is what this organism/search can do on this cell",
        "kill_condition": "the per_ask arm does not reproduce the parent shelf rate (< 8/12): the assay drifted and no comparison is licensed",
        "typed_failure_conditions": ["POSITIVE_CONTROL_FAILED", "TARGET_UNREACHABLE", "READOUT_CANNOT_EXPRESS", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["both readouts per generation for the elite of every arm", "levels on the common per-ask yardstick", "generations at floor / on "
                                       "shelf", "ladder points", "reachability rows (per_ask baseline, episode treated)"],
        "replacement_condition": "this IS the replacement (D3-013). It would itself be replaced only if C3-SFE-02 had found a gradient off the shelf, which it did not "
                                 "(0 of 4,800 children kept the first stream while gaining the second)",
        "ancestry": "replacement (queue slot 8; original: wall-clock producer-consumer with a FULL-solve criterion, killed by C3-SFE-01's 0/24 summits)",
        "machine_changes_exercised": ["evaluate(reward_mode) + Evolution(reward_mode) all-or-nothing episode credit", "A levels on a common yardstick", "B ladder lookups"],
        "decl": {"positive_control": {"arm": "per_ask", "metric": "shelf_reached", "min": 1, "min_rows": 8}, "n_min": len(a.seeds),
                 "primary": {"treatment": "episode", "control": "per_ask", "metric": "summit", "min_effect": 0.25},
                 "battery": [{"name": "episode_arm_shelf_rate_below_per_ask", "passed": None},
                             {"name": "episode_arm_reaches_higher_episode_credit", "passed": None},
                             {"name": "per_ask_arm_reproduces_parent_shelf_rate", "passed": None}]},
    })
    X.decision("D3-019: both arms are read out on the SAME held-out battery with both readouts; levels (FLOOR/SHELF/SUMMIT) are always computed on per-ask credit so the arms are comparable")
    X.open("C3-SFE-08 (replacement) partial-credit removal on W2_K2")
    wid = X.world("credit", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    jobs = [{"arm": arm, "seed": s, "N": a.N, "E": a.E, "G": a.G} for arm in ARMS for s in a.seeds]
    rows = X.pool_map(run_arm, jobs, "scan_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(TARGET, res, N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"],
                    kind=None if r["arm"] == "per_ask" else "treated", heldout_per_ask=r["heldout_per_ask"] or None)
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E, "target": TARGET.knobs(), "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("trace_per_ask", "trace_episode", "elite_summary", "gen0_provenance")},
                 "SURVIVED" if r["summit"] else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    def rs_of(arm):
        return sorted([r for r in rows if r["arm"] == arm], key=lambda r: r["seed"])
    shelf = {arm: sum(r["shelf_reached"] for r in rs_of(arm)) for arm in ARMS}
    ep_best = {arm: med([r["best_episode_max"] for r in rs_of(arm)]) for arm in ARMS}
    battery = [{"name": "episode_arm_shelf_rate_below_per_ask", "passed": bool(shelf["episode"] < shelf["per_ask"]), "value": shelf},
               {"name": "episode_arm_reaches_higher_episode_credit", "passed": bool(ep_best["episode"] is not None and ep_best["per_ask"] is not None and ep_best["episode"] > ep_best["per_ask"]), "value": ep_best},
               {"name": "per_ask_arm_reproduces_parent_shelf_rate", "passed": bool(shelf["per_ask"] >= 8), "value": {"shelf": shelf["per_ask"], "parent": 11}}]
    summ = {arm: {"n": len(rs_of(arm)), "shelf": shelf[arm], "summit": sum(r["summit"] for r in rs_of(arm)), "candidates": sum(r["summit_candidates"] for r in rs_of(arm)),
                  "first_shelf": [r["first_shelf_gen"] for r in rs_of(arm)], "gens_at_floor_med": med([r["gens_at_floor"] for r in rs_of(arm)]),
                  "gens_on_shelf_med": med([r["gens_on_shelf"] for r in rs_of(arm)]), "best_per_ask": [r["best_per_ask_max"] for r in rs_of(arm)],
                  "best_episode": [r["best_episode_max"] for r in rs_of(arm)], "heldout_med": med([r["competence_heldout"] for r in rs_of(arm)]),
                  "heldout_episode_med": med([r["heldout_episode"] for r in rs_of(arm)]),
                  "ladder": {str(g): {"shelf": sum(r["ladder"][str(g)]["shelf"] for r in rs_of(arm)), "summit": sum(r["ladder"][str(g)]["summit"] for r in rs_of(arm))}
                             for g in LADDER if g <= a.G}} for arm in ARMS}
    X.receipt["summary"] = summ; X.receipt["battery"] = battery
    out = X.close(rows, meas_extra={"battery": battery})
    print(json.dumps({"summary": summ, "battery": battery, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
