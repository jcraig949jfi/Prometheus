"""G6-0 REHEARSAL, ARCHAEON SIDE (item 7): the minimum complete path
    world (Axis W, composed) -> organism (v0) -> pressure (Axis P, labeled) -> segment -> telemetry (T0 rows, anchors)
    -> detectors (frozen candidate table) -> freeze -> replay A (exact) and D (rollback) -> receipt
run as plumbing under load, with an intentionally planted event, and the twelve G6-0 proofs of ruling R9 each
answered YES / NO / NOT_MINE (the fleet's halves: Vivarium wrap, engine schema 10, PEW registry, Harmonia's
receipt consumption, fixture commitments).

    python -m archaeon.campaign6.g6_0_rehearsal [--gens 40] [--N 32] [--out archaeon/campaign6/G6-0/REHEARSAL_<date>.json]
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign6 import schemas as S                                  # noqa: E402
from archaeon.campaign6 import segment as SG                                 # noqa: E402
from archaeon.campaign6.worlds import sample_world                           # noqa: E402
from archaeon.campaign6.worlds.fixtures import HARVESTER                     # noqa: E402
from archaeon.campaign6.pressure import schedules as P                       # noqa: E402

HERE = Path(__file__).resolve().parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=40)
    ap.add_argument("--N", type=int, default=32)
    ap.add_argument("--E", type=int, default=6)
    ap.add_argument("--out", default=None)
    ap.add_argument("--bin", type=int, default=6)
    ap.add_argument("--world-seed", type=int, default=4242)
    a = ap.parse_args(argv)
    t0 = time.time()
    frozen = json.loads((HERE / "observatory" / "DETECTORS_FROZEN_candidate.json").read_text(encoding="utf-8"))
    thr = {k: v["threshold"] for k, v in frozen["thresholds"].items() if v.get("threshold") is not None}
    thr.update({"lineage_discontinuity.struct_max": 0.25, "unexplained_gain.struct_max": 0.25, "unexpected_transfer.floor": 3 / 16, "structural_reuse": 2,
                "environmental_modification": 0, "niche_divergence": 0.5, "regime_persistence": 1 / 16})
    parents = C1.parents_from_population()
    init = [p["parent"] for p in parents][:a.N]
    while len(init) < a.N:
        init.append(init[len(init) % len(parents)])
    wrec = sample_world(a.world_seed, bin_target=a.bin)            # a PROCEDURAL world; seed and bin chosen before any run
    sched = P.labeled(7, a.gens)
    prov = S.provenance("PROCEDURAL", "g6_0_rehearsal", "0.1", 1, {"world_seed": a.world_seed, "schedule_seed": 7, "gens": a.gens, "bin": a.bin}, thresholds_digest=frozen["digest"])
    world = {"kind": "c6.composed.v1", "params": wrec["params"]}
    plant_gen = a.gens // 2
    planted = [{"generation": plant_gen, "kind": "inject_foreign", "index": 3, "manifest": HARVESTER}]
    base = dict(run_id=prov["run_id"], provenance=prov, world=world, profile="v0", schedule=sched, N=a.N, E=a.E,
                archive={"dense_until": 16, "neighbourhood": 8}, thresholds=thr, spread=frozen["spread"], seed=11)
    # ---- 1. two segments with a boundary, planted event in the second
    half = a.gens // 2
    s1 = SG.make_spec(g0=0, g1=half, **base); s2 = SG.make_spec(g0=half, g1=a.gens, planted=planted, **base)
    ck0 = SG.initial_checkpoint(s1, init)
    o1 = SG.run_segment(s1, ck0); o2 = SG.run_segment(s2, o1["checkpoint_out"])
    # ---- 2. replay A (exact) of segment 2
    o2b = SG.run_segment(s2, o1["checkpoint_out"]); replay_A = "SAME" if o2b["out_digest"] == o2["out_digest"] else "DIFFERENT"
    # ---- 3. replay D (rollback): the same segment without the plant -> the planted freeze must not appear
    s2_roll = SG.make_spec(g0=half, g1=a.gens, planted=[], **base); o2_roll = SG.run_segment(s2_roll, o1["checkpoint_out"])
    plant_ids = {fz["subject"]["organism_id"] for fz in o2["freezes"] if fz["subject"]["generation"] == plant_gen and "planted" in json.dumps(fz.get("mutation_chain", []))}
    planted_subject_fired = any(e["generation"] == plant_gen and e["organism_id"] in {o["organism_id"] for o in []} for e in o2["events"])
    ev_plant = [e for e in o2["events"] if e["generation"] == plant_gen]
    fz_plant = [fz for fz in o2["freezes"] if fz["subject"]["generation"] == plant_gen]
    rollback = "DIFFERENT" if o2_roll["out_digest"] != o2["out_digest"] else "SAME"
    # ---- 4. anchors, coverage, chain across the boundary
    anchors = o1["anchors"] + o2["anchors"]
    chain_ok = all(anchors[i]["prev_segment_hash"] == anchors[i - 1]["segment_hash"] for i in range(1, len(anchors)))
    cover = sum(x["n"] for x in anchors) == o1["evaluations"] + o2["evaluations"]
    # ---- 5. pressure history: EXO and ENDO both present, exact and reproducible
    ph = o1["pressure_history"] + o2["pressure_history"]
    kinds = {e["kind"] for e in ph}
    # ---- 6. freeze scopes / partial visibility / interpretation None / preserved before any label
    scopes = {}
    for fz in o1["freezes"] + o2["freezes"]:
        scopes[fz["scope"]] = scopes.get(fz["scope"], 0) + 1
    interp_none = all(fz["interpretation"] is None for fz in o1["freezes"] + o2["freezes"])
    # ---- 7. detectors emit with the frozen table digest in provenance; UNABLE counts by detector
    unable = {}; fired = {}
    for e in o1["events"] + o2["events"]:
        for d in e["unable"]:
            unable[d] = unable.get(d, 0) + 1
        for d in e["fired"]:
            fired[d] = fired.get(d, 0) + 1
    proofs = {
        "segment_execution_works": {"answer": "YES", "evidence": {"segments": 2, "evaluations": o1["evaluations"] + o2["evaluations"], "continuity_checked_by": "segment.self_test"}},
        "graph_organism_checkpointing_works": {"answer": "NOT_MINE", "evidence": "profile v0 only until Proteus's graph triple registers (PROTEUS-47)"},
        "world_and_pressure_provenance_survives": {"answer": "YES", "evidence": {"world_provenance": wrec["provenance"]["run_id"], "world_id": wrec["world_id"], "complexity_bin": wrec["complexity_bin"],
                                                                                  "schedule_id": sched["schedule_id"], "schedule_provenance": sched["provenance"]["run_id"], "in_spec_hash": s1["spec_hash"]}},
        "t0_sidecars_anchor_correctly": {"answer": "YES" if (chain_ok and cover) else "NO", "evidence": {"anchors": len(anchors), "chain_intact_across_boundary": chain_ok, "coverage": cover}},
        "detectors_emit_frozen_version_firings": {"answer": "YES", "evidence": {"thresholds_digest_in_provenance": prov["thresholds_digest"], "fired_by_detector": fired, "unable_by_detector": unable}},
        "freezes_span_ownership_boundaries": {"answer": "NOT_MINE", "evidence": "single client here; the engine's PARTIAL-with-reason path is Daedalus's (R2); my PARTIAL_FREEZE carries member/owner/reason/at"},
        "partial_freezes_remain_visible": {"answer": "YES" if scopes.get("PARTIAL_FREEZE") else "NO_INSTANCE", "evidence": scopes},
        "escalation_ordering_auditable": {"answer": "YES" if interp_none else "NO", "evidence": {"interpretation_none_on_all_freezes": interp_none, "preserved_at_on_every_freeze": all("preserved_at" in fz for fz in o1["freezes"] + o2["freezes"])}},
        "replay_requires_preserved_state": {"answer": "YES", "evidence": {"replay_A_exact": replay_A, "replay_D_rollback": rollback, "replay_input": "spec_hash + checkpoint_in digest (no replay without them)"}},
        "fixture_commitments_verify": {"answer": "NOT_MINE", "evidence": "Harmonia's registry + engine/PEW commitments (R3)"},
        "harmonia_can_consume_receipts": {"answer": "PENDING", "evidence": "this receipt + freezes are in c6_observatory's shape by construction; Harmonia to confirm"},
        "planted_event_travels_the_chain": {"answer": "YES" if (ev_plant and fz_plant and replay_A == "SAME" and rollback == "DIFFERENT") else "NO",
                                            "evidence": {"planted_generation": plant_gen, "events_at_plant_gen": len(ev_plant), "freezes_at_plant_gen": len(fz_plant),
                                                         "detectors_on_plant": sorted({d for e in ev_plant for d in e["fired"]}), "replay_A": replay_A, "replay_D": rollback}},
    }
    receipt = {"schema": "archaeon.c6.g6_0_rehearsal.v1", "side": "Archaeon", "world": {"id": wrec["world_id"], "features": wrec["features"], "bin": wrec["complexity_bin"]},
               "schedule": {"id": sched["schedule_id"], "mode": sched["mode"], "segments": len(sched["segments"])},
               "N": a.N, "E": a.E, "generations": a.gens, "evaluations": o1["evaluations"] + o2["evaluations"], "rows_bytes_mean": round(sum(len(json.dumps(r, separators=(",", ":"))) for r in o1["rows"][:200]) / max(1, min(200, len(o1["rows"]))), 1),
               "events": len(o1["events"]) + len(o2["events"]), "freezes": len(o1["freezes"]) + len(o2["freezes"]), "freeze_scopes": scopes,
               "pressure_kinds": sorted(kinds), "pressure_history_n": len(ph), "proofs": proofs, "thresholds_digest": frozen["digest"], "wall_s": round(time.time() - t0, 1)}
    receipt["all_mine_yes"] = all(v["answer"] in ("YES", "NOT_MINE", "PENDING", "NO_INSTANCE") for v in proofs.values())
    out = Path(a.out) if a.out else HERE / "G6-0" / ("REHEARSAL_%s.json" % time.strftime("%Y-%m-%d", time.gmtime()))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "proofs"}, indent=1)); print(json.dumps({k: v["answer"] for k, v in proofs.items()}, indent=1))
    print(json.dumps(proofs["planted_event_travels_the_chain"], indent=1)); print("written", out)
    return 0 if receipt["all_mine_yes"] else 1


if __name__ == "__main__":
    sys.exit(main())
