"""C5-09 -- REACH / DISCOVERY TEST (campaign 5, Phase B). Preregistration: C5-09/DESIGN.md.

    python -m archaeon.campaign5.c5_09 [--seeds 1..6] [--N 50] [--G 100] [--E 16] [--procs 12] [--dry-run] [--self-test]

Four arms (OLD_v04, OLD_B, B_FAIL, B_FIZZLE) on the four screened Phase-A worlds, identical
starting populations, identical total compute. Readings per C5-09/DESIGN.md; C5-10/RULE.md reads
the same numbers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import generate as G                                   # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from archaeon.wse.economics import REGIMES                                   # noqa: E402
from archaeon.wse.worlds import episodes_for                                 # noqa: E402
from archaeon.campaign2.c2base import FOUNDRY_C2                             # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign5.c5_02 import WORLDS, SPECS, HELDOUT                   # noqa: E402
from archaeon.campaign5.repb import gen_b                                    # noqa: E402
from archaeon.campaign5.repb.evolve_b import EvolutionB, make_evaluator      # noqa: E402

ID = "C5-09"
ARMS = {"OLD_v04": ("OLD", "v04"), "OLD_B": ("OLD", "B"), "B_FAIL": ("B_FAIL", "B"), "B_FIZZLE": ("B_FIZZLE", "B")}
PROBE_EVERY = 10
BASELINE = "OLD_v04"


def starting(parents: list, seed: int, N: int) -> list:
    rng = SplitMix64(seed_from("c5.09.start", CAMPAIGN_SEED, seed))
    return [gen_b.canonicalize(parents[rng.randbelow(len(parents))]["parent"]) for _ in range(N)]


def run_arm(job: dict) -> dict:
    arm, seed, N, Gn, E, parents = job["arm"], job["seed"], job["N"], job["G"], job["E"], job["parents"]
    interp, grammar = ARMS[arm]
    ev_fn = make_evaluator(interp)
    start = starting(parents, seed, N)
    out_w: Dict[str, dict] = {}
    t0 = time.time()
    for w in WORLDS:
        init = []
        for m in start:
            org = G.organism_record(dict(m), None, 0); org["origins"] = ["start"]; init.append(org)
        prov = {"fill": "57 canonical parents subsampled to N by the seed's rng (shared by every arm)", "n": N, "verified_common": True}
        ev = EvolutionB(SPECS[w], REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c5-09-%s-%s" % (arm, w), foundry=FOUNDRY_C2,
                        init_pop=init, gen0_provenance=prov, rng_label="c5-09-%s" % w, interp=interp, grammar=grammar)
        ho = episodes_for(SPECS[w], CAMPAIGN_SEED, "heldout", seed, HELDOUT)
        probes = []
        start_best = max(ev_fn(m, ho, 7, "per_ask")["reward_per_ask"] for m in start)
        for g in range(Gn):
            ev.evaluate_generation(last=(g == Gn - 1))
            if g % PROBE_EVERY == 0 or g == Gn - 1:
                elite = ev.scored[0][1]
                r = ev_fn(elite["manifest"], ho, 7, "per_ask")
                probes.append({"gen": g, "heldout": round(r["reward_per_ask"], 4), "train": round(ev.scored[0][2]["reward_per_ask"], 4),
                               "elite_len": len(elite["manifest"]["genome"]) // 4, "elite_faults": r.get("faults", 0), "elite_fault_sites": r.get("fault_sites", 0),
                               "crossing_share": ev.trace[-1]["crossing_share"], "trapped_share": ev.trace[-1]["trapped_share"], "faulted_share": ev.trace[-1]["faulted_share"]})
            if g < Gn - 1:
                ev.reproduce()
        res = ev.result()
        levels = sorted({p["heldout"] for p in probes})
        first_gain = next((p["gen"] for p in probes if p["heldout"] >= start_best + C1.BAND), None)
        out_w[w] = {"start_best_heldout": round(start_best, 4), "heldout_final": probes[-1]["heldout"], "heldout_best_probe": max(p["heldout"] for p in probes),
                    "first_gain_gen": first_gain, "levels_passed": len(levels) - 1, "probes": probes,
                    "trace_best": [t["best_reward"] for t in res["trace"]], "trace_crossing": [t["crossing_share"] for t in res["trace"]],
                    "elite_len": probes[-1]["elite_len"], "elite_ancestry_depth": len(res["ancestry"]), "evaluations": N * Gn}
    return {"arm": arm, "seed": seed, "N": N, "G": Gn, "E": E, "worlds": out_w, "total_evals": len(WORLDS) * N * Gn, "wall_s": round(time.time() - t0, 1),
            "start_digest": hashlib.sha256(json.dumps(start, sort_keys=True).encode()).hexdigest()}


def readings(runs: list, seeds: list) -> dict:
    by = {(r["arm"], r["seed"]): r for r in runs}
    cells = {}
    for arm in ARMS:
        if arm == BASELINE:
            continue
        won = lost = tied = 0; detail = {}
        for s in seeds:
            for w in WORLDS:
                d = by[(arm, s)]["worlds"][w]["heldout_final"] - by[(BASELINE, s)]["worlds"][w]["heldout_final"]
                k = "WON" if d >= C1.BAND else "LOST" if d <= -C1.BAND else "TIED"
                won += k == "WON"; lost += k == "LOST"; tied += k == "TIED"
                detail["%s/s%d" % (w, s)] = {"delta": round(d, 4), "k": k, "arm": by[(arm, s)]["worlds"][w]["heldout_final"], "baseline": by[(BASELINE, s)]["worlds"][w]["heldout_final"]}
        cells[arm] = {"won": won, "lost": lost, "tied": tied, "net": won - lost, "cells": detail}
    grammar_gain = cells["OLD_B"]["net"] >= 4
    out = {"cells": cells, "GRAMMAR_GAIN": grammar_gain,
           "DISCOVERY_GAIN": {arm: (cells[arm]["net"] >= 4 and not grammar_gain) for arm in ("B_FAIL", "B_FIZZLE")}}
    out["reading"] = ("GRAMMAR_GAIN" if grammar_gain else "DISCOVERY_GAIN" if any(out["DISCOVERY_GAIN"].values()) else "NO_GAIN")
    per_world = {}
    for w in WORLDS:
        per_world[w] = {arm: {"final_mean": round(sum(by[(arm, s)]["worlds"][w]["heldout_final"] for s in seeds) / len(seeds), 4),
                              "first_gain_gens": [by[(arm, s)]["worlds"][w]["first_gain_gen"] for s in seeds],
                              "levels_passed_mean": round(sum(by[(arm, s)]["worlds"][w]["levels_passed"] for s in seeds) / len(seeds), 2),
                              "elite_len_mean": round(sum(by[(arm, s)]["worlds"][w]["elite_len"] for s in seeds) / len(seeds), 1),
                              "crossing_final_mean": round(sum(by[(arm, s)]["worlds"][w]["probes"][-1]["crossing_share"] for s in seeds) / len(seeds), 4),
                              "faulted_final_mean": round(sum(by[(arm, s)]["worlds"][w]["probes"][-1]["faulted_share"] for s in seeds) / len(seeds), 4)} for arm in ARMS}
    out["per_world"] = per_world
    out["start_identical"] = all(len({by[(arm, s)]["start_digest"] for arm in ARMS}) == 1 for s in seeds)
    return out


def self_test() -> int:
    ps = C1.parents_from_population()
    a = run_arm({"arm": "OLD_v04", "seed": 1, "N": 8, "G": 3, "E": 8, "parents": ps})
    b = run_arm({"arm": "OLD_v04", "seed": 1, "N": 8, "G": 3, "E": 8, "parents": ps})
    c = run_arm({"arm": "B_FIZZLE", "seed": 1, "N": 8, "G": 3, "E": 8, "parents": ps})
    d = run_arm({"arm": "B_FAIL", "seed": 1, "N": 8, "G": 3, "E": 8, "parents": ps})
    e = run_arm({"arm": "OLD_B", "seed": 1, "N": 8, "G": 3, "E": 8, "parents": ps})
    det = json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    rd = readings([a, c, d, e], [1])
    print(json.dumps({"deterministic": det, "start_identical": rd["start_identical"], "reading": rd["reading"], "nets": {k: v["net"] for k, v in rd["cells"].items()},
                      "fizzle_W3": c["worlds"]["W3_K3"]["probes"][-1], "fail_W3": d["worlds"]["W3_K3"]["probes"][-1]}, indent=1))
    return 0 if (det and rd["start_identical"]) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--N", type=int, default=50)
    ap.add_argument("--G", type=int, default=100)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5-09")
    if a.self_test:
        return self_test()
    from archaeon.campaign5.c5base import harness                            # noqa: PLC0415

    class Reach(harness()):
        ID = "C5-09"
        TITLE = "reach / discovery at equal total compute: OLD_v04, OLD_B, B_FAIL, B_FIZZLE"
        PARENTS = ["C5-02", "C5-05"]
        ARM_FIELD = "arm"
        METRICS = ("heldout_final", "first_gain_gen", "levels_passed", "crossing_final")

    X = Reach(dry_run=a.dry_run, procs=a.procs)
    design = (C5 / "C5-09" / "DESIGN.md").read_text(encoding="utf-8")
    parents = C1.parents_from_population()
    X.seal({
        "question": "At equal total compute on screened worlds with headroom, does evolution under representation B discover more than under the old representation, "
                    "and is any gain the representation's or the grammar's?",
        "parent_evidence": "C5-02 (elite flat at the starting parent, 0/24 cells); C5-05 geometry under B; C5-03 F8 crossing 9.3%.",
        "why_this_slot": "The directive's reach/discovery test; feeds C5-10's committed rule.",
        "assay_capability_requirement": "determinism of OLD_v04 seed 1; identical gen-0 programs across arms (digest); starting best <= screen receipt",
        "positive_control": "controls arm: pass >= 1.0",
        "reachability_estimate": {"note": "screened worlds (WORLD_SCREEN_2026-09-18.json)"},
        "arms": list(ARMS) + ["controls"],
        "crn_policy": "same seeds, same starting subsample, same evolver rng streams per world in every arm; only (evaluator, grammar) differ",
        "budget": {"worlds": list(WORLDS), "N": a.N, "G": a.G, "E": a.E, "seeds": a.seeds, "evals_per_arm_seed": len(WORLDS) * a.N * a.G},
        "primary_observable": "per-cell WON/LOST/TIED vs OLD_v04 on final held-out (band 1/16); net per arm; DISCOVERY_GAIN / GRAMMAR_GAIN / NO_GAIN",
        "claim_ceiling": "24 cells per arm; a count; C5-10 replicates any selection on held-out worlds",
        "falsification_condition": "prediction NO_GAIN is lost if any B arm reaches net >= +4 with OLD_B < +4",
        "kill_condition": "control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID"],
        "expected_machine_telemetry": ["probes per 10 generations with crossing/trapped/faulted shares", "elite length and fault sites"],
        "machine_changes_exercised": ["EvolutionB (pluggable evaluator and grammar)"],
        "replacement_condition": "none",
        "ancestry": "original (Phase B, slot 7)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": len(a.seeds), "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "B_FIZZLE", "control": "OLD_v04", "metric": "heldout_final", "min_effect": 0.0625}},
    })
    X.open("cmp5-c5-09")
    wid = X.world("reach-discovery-b", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    jobs = [{"arm": arm, "seed": s, "N": a.N, "G": a.G, "E": a.E, "parents": parents} for arm in ARMS for s in a.seeds]
    runs = X.pool_map(run_arm, jobs, "arms_s")
    rd = readings(runs, a.seeds)
    # controls
    again = run_arm({"arm": BASELINE, "seed": a.seeds[0], "N": a.N, "G": a.G, "E": a.E, "parents": parents}) if not a.dry_run else None
    first = next(r for r in runs if r["arm"] == BASELINE and r["seed"] == a.seeds[0])
    det = again is not None and json.dumps(again, sort_keys=True) == json.dumps(first, sort_keys=True)
    screen = json.loads((C5 / "WORLD_SCREEN_2026-09-18.json").read_text(encoding="utf-8"))
    start_ok = all(first["worlds"][w]["start_best_heldout"] <= screen["worlds"][w]["best"] + 1e-9 for w in WORLDS)
    ctrl = {"deterministic": det, "start_identical": rd["start_identical"], "start_below_screen": start_ok, "pass": det and rd["start_identical"] and start_ok}
    grouped = [{"arm": "controls", "pass": float(ctrl["pass"]), "n": 1}]
    for r in runs:
        for w in WORLDS:
            row = {"arm": r["arm"], "seed": r["seed"], "world": w, "heldout_final": r["worlds"][w]["heldout_final"], "first_gain_gen": r["worlds"][w]["first_gain_gen"],
                   "levels_passed": r["worlds"][w]["levels_passed"], "crossing_final": r["worlds"][w]["probes"][-1]["crossing_share"]}
            grouped.append(row)
        content = {k: v for k, v in r.items() if k != "worlds"} | {"worlds": {w: {k: v for k, v in r["worlds"][w].items() if k not in ("trace_best", "trace_crossing")} for w in WORLDS}}
        X.record(wid, r, {"arm": r["arm"], "seed": r["seed"]}, content, "SURVIVED", key_parts=(r["arm"], r["seed"]))
    summary = {"reading": rd["reading"], "DISCOVERY_GAIN": rd["DISCOVERY_GAIN"], "GRAMMAR_GAIN": rd["GRAMMAR_GAIN"], "cells": rd["cells"], "per_world": rd["per_world"],
               "controls": ctrl, "wall_s": round(time.time() - t0, 1)}
    X.att.write("REACH.json", summary)
    X.att.write("runs.json", runs)
    X.publish(wid, "reach", "cmp5.c509_reach.v1", {k: v for k, v in summary.items() if k != "cells"} | {"nets": {k: {kk: vv for kk, vv in v.items() if kk != "cells"} for k, v in rd["cells"].items()}},
              {"info_kind": "artifact", "label": "C5-09 reach/discovery readings"})
    out = X.close(grouped, addendum={"reading": rd["reading"], "nets": json.dumps({k: v["net"] for k, v in rd["cells"].items()})})
    print(json.dumps({"reading": rd["reading"], "nets": {k: {kk: vv for kk, vv in v.items() if kk != "cells"} for k, v in rd["cells"].items()}, "per_world": rd["per_world"],
                      "controls": ctrl, "close": out["disposition"], "wall_s": summary["wall_s"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
