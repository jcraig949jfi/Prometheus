"""Calibration round 5 (population stage; DETECTORS_v0.1 named "C5-09 OLD_v04 populations" as the
negative class): novelty / discontinuity scores are taken INSIDE the segment loop, exactly as
production scores them (pool = library + population + ancestors + siblings).

  run A  population = the 12 canonical W0 solvers (N=32 with repeats), W0, 60 generations, 3 seeds.
         natural children = NEGATIVES (both detectors).
         plants at generations 12/24/36/48: a single-edit CHILD of a population member taken from
         the C5-05 census (replacement / operand_perturbation, displacement >= .5, struct <= .25,
         parent a W0 solver) -> POSITIVES for lineage_discontinuity (small edit, big jump).
  run B  population = the gen0_random parents (degenerate on W0), W0, 60 generations, 3 seeds.
         natural children = NEGATIVES; plants: canonical W0 solvers -> POSITIVES for
         behavioral_novelty (a behaviour this population has never shown).
  Round 4 (foreign shelf/delay solvers into a W0 population) is preserved: they are SILENT on W0
  and therefore, correctly, not novel there -- a mis-specified positive, not a detector failure.

    python -m archaeon.campaign6.observatory.calibrate_population

Threshold rule unchanged: 99th percentile of negatives (<= 1% fire); every positive must fire.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5                                     # noqa: E402
from archaeon.campaign6 import schemas as S                                  # noqa: E402
from archaeon.campaign6 import segment as SG                                 # noqa: E402
from archaeon.campaign6.observatory.calibrate import percentile, canonical_parents, regen_child, latest_c505   # noqa: E402

HERE = Path(__file__).resolve().parent
GENS = 60
PLANT_GENS = (12, 24, 36, 48)
SEEDS = (1, 2, 3)


def _pop(manifests, N):
    out = list(manifests)
    while len(out) < N:
        out.append(manifests[len(out) % len(manifests)])
    return out[:N]


def main() -> int:
    frozen = json.loads((HERE / "DETECTORS_FROZEN_candidate.json").read_text(encoding="utf-8"))
    thr = {k: v["threshold"] for k, v in frozen["thresholds"].items() if v.get("threshold") is not None}
    thr.update({"lineage_discontinuity.struct_max": 0.25, "unexplained_gain.struct_max": 0.25, "unexpected_transfer.floor": 3 / 16, "structural_reuse": 2})
    cps = canonical_parents()
    w0 = [p for p in cps.values() if p["stratum"] == "w0_solver"]
    g0r = [p for p in cps.values() if p["stratum"] == "gen0_random"]
    world = {"kind": "wse.WorldSpec", "knobs": C1.ENVS["W0"].knobs()}
    sched = [{"from_gen": 0, "kind": "EXOGENOUS_PRESSURE", "label": "stable", "params": {}}]
    # edited children of W0 solvers from the census: small edit, big displacement
    with gzip.open(latest_c505() / "children.json.gz", "rt", encoding="utf-8") as f:
        rows = json.load(f)
    w0_ids = {p["organism_id"] for p in w0}
    cands = [r for r in rows if r["grammar"] == "B" and r["parent_id"] in w0_ids and r["operator"] in ("replacement", "operand_perturbation", "reference_redirection")
             and r["applied"] and r["by"]["OLD"].get("displacement", 0) >= 0.5 and r["by"]["OLD"].get("answered_share", 0) > 0]
    cands.sort(key=lambda r: (r["parent_id"], r["operator"], r["draw"]))
    out = {"schema": "archaeon.c6.calibration_population.v1", "stage": "BASELINE_ADMITTED_CANDIDATE (population round 5)", "world": "W0", "N": 32, "E": 16, "generations": GENS,
           "seeds": list(SEEDS), "edited_child_candidates": len(cands), "runs": []}
    neg = {"behavioral_novelty": [], "lineage_discontinuity": []}; pos = {"behavioral_novelty": [], "lineage_discontinuity": []}
    popA = _pop([p["parent"] for p in w0], 32); popB = _pop([p["parent"] for p in g0r], 32)
    idxA = {p["organism_id"]: i for i, p in enumerate(w0)}
    for seed in SEEDS:
        # run A: discontinuity positives
        plantsA = []
        for i, g in enumerate(PLANT_GENS):
            r = cands[(seed * 5 + i) % len(cands)]
            pm = cps[r["parent_id"]]["parent"]; child = regen_child(r, pm)
            from proteus.foundry import generate as G
            pid_ = G.organism_record(dict(pm), None, 0)["organism_id"]
            plantsA.append({"generation": g - 1, "kind": "inject_foreign", "index": 20 + i, "manifest": pm})            # the parent, one generation earlier (enters history)
            plantsA.append({"generation": g, "kind": "inject_child_of", "index": 21 + i, "parent_id": pid_, "manifest": child, "operator": r["operator"]})
        provA = S.provenance("PROCEDURAL", "calibrate_population.A", "0.2", seed, {"world": "W0", "plants": list(PLANT_GENS)})
        specA = SG.make_spec(run_id=provA["run_id"], provenance=provA, world=world, profile="v0", schedule=sched, g0=0, g1=GENS, N=32, E=16,
                             archive={"dense_until": 64, "neighbourhood": 16}, thresholds=thr, spread=frozen["spread"], seed=seed, planted=plantsA, log_scores=True)
        oA = SG.run_segment(specA, SG.initial_checkpoint(specA, popA))
        # run B: novelty positives
        plantsB = [{"generation": g, "kind": "inject_foreign", "index": 20 + i, "manifest": w0[(seed * 3 + i) % len(w0)]["parent"]} for i, g in enumerate(PLANT_GENS)]
        provB = S.provenance("PROCEDURAL", "calibrate_population.B", "0.2", seed, {"world": "W0", "plants": list(PLANT_GENS)})
        specB = SG.make_spec(run_id=provB["run_id"], provenance=provB, world=world, profile="v0", schedule=sched, g0=0, g1=GENS, N=32, E=16,
                             archive={"dense_until": 64, "neighbourhood": 16}, thresholds=thr, spread=frozen["spread"], seed=seed, planted=plantsB, log_scores=True)
        oB = SG.run_segment(specB, SG.initial_checkpoint(specB, popB))
        for tag, o in (("A", oA), ("B", oB)):
            for rec in o["score_log"]:
                planted_here = rec["generation"] in PLANT_GENS and rec.get("planted_now") and (rec["origins"] in (["planted_child"], ["planted_foreign"]))
                for d in ("behavioral_novelty", "lineage_discontinuity"):
                    oc, sc = rec.get(d, ("UNABLE", None))
                    if sc is None:
                        continue
                    if planted_here:
                        if (tag == "A" and d == "lineage_discontinuity") or (tag == "B" and d == "behavioral_novelty"):
                            pos[d].append(sc)
                    else:
                        neg[d].append(sc)
            out["runs"].append({"run": tag, "seed": seed, "evaluations": o["evaluations"], "events_at_single_edit_thresholds": len(o["events"]), "wall_s": o["wall_s"],
                                "planted_scores": [{"gen": r["generation"], **{d: r.get(d) for d in ("behavioral_novelty", "lineage_discontinuity")}} for r in o["score_log"] if r.get("planted_now") and r["generation"] in PLANT_GENS]})
    cal = {}
    for d in ("behavioral_novelty", "lineage_discontinuity"):
        n, p = neg[d], pos[d]
        t = percentile(n, 0.99) if n else None
        neg_fire = sum(1 for x in n if x > t) / max(1, len(n)); pos_fire = sum(1 for x in p if x > t) / max(1, len(p))
        cal[d] = {"threshold": t, "neg_n": len(n), "neg_fire": round(neg_fire, 4), "pos_n": len(p), "pos_fire": round(pos_fire, 4), "pos_min": min(p) if p else None,
                  "pos_scores": sorted(p), "admittable": bool(p) and pos_fire == 1.0, "single_edit_threshold": frozen["thresholds"][d].get("single_edit_stage_threshold", frozen["thresholds"][d]["threshold"]),
                  "reason": "" if (p and pos_fire == 1.0) else "a planted positive did not fire at the population 1% threshold"}
    out["calibration"] = cal
    ev = sum(r["events_at_single_edit_thresholds"] for r in out["runs"]); n_ev = sum(r["evaluations"] for r in out["runs"])
    out["escalation_rate_at_single_edit_thresholds"] = round(ev / n_ev, 4)
    (HERE / "CALIBRATION_population_v0.3.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    for d in ("behavioral_novelty", "lineage_discontinuity"):
        frozen["thresholds"][d].update({"threshold": cal[d]["threshold"], "single_edit_stage_threshold": cal[d]["single_edit_threshold"],
                                        "admittable_on_v0": cal[d]["admittable"], "stage": "BASELINE_ADMITTED_CANDIDATE" if cal[d]["admittable"] else "NOT_ADMITTED_ON_V0",
                                        "reason": cal[d]["reason"], "calibrated_on": "population round 6 (CALIBRATION_population_v0.3.json)"})
    frozen["calibration_rounds"] = [r for r in frozen["calibration_rounds"] if "population" not in r] + ["CALIBRATION_population_v0.1.json (round 4, preserved, mis-specified positives)",
                                                                                                          "CALIBRATION_population_v0.2.json (round 5, preserved, plant bookkeeping defects)", "CALIBRATION_population_v0.3.json (round 6)"]
    frozen.pop("digest", None)
    body = json.dumps(frozen, indent=1, sort_keys=True, default=str)
    frozen["digest"] = "sha256:" + hashlib.sha256(body.encode()).hexdigest()
    (HERE / "DETECTORS_FROZEN_candidate.json").write_text(json.dumps(frozen, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "pos_scores"} for k, v in cal.items()}, indent=1))
    print("escalation rate at single-edit thresholds", out["escalation_rate_at_single_edit_thresholds"], "candidates", len(cands), "frozen", frozen["digest"][:20])
    return 0


if __name__ == "__main__":
    sys.exit(main())
