"""Graph profile through the whole Archaeon path (after Proteus's handover): gen-0 from the graph foundry,
evaluate_any on a WorldSpec world and on a composed world, rows (Proteus's graph fingerprint + ext),
a 12-generation segment with the frozen candidate table, checkpoint continuity, determinism, and the
substrate firewall (a v0 mate is refused).

    python -m archaeon.campaign6.test_graph_profile
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign6 import schemas as S, segment as SG, substrate as SUB  # noqa: E402
from archaeon.campaign6.worlds import sample_world, world_from_record, evaluate_world   # noqa: E402
from archaeon.campaign6.pressure import schedules as P                       # noqa: E402


def main() -> int:
    rep = {}
    pop = SUB.gen0_any("graph", 16, 1)
    rep["gen0_graph"] = len(pop); rep["schema"] = pop[0]["schema_version"]
    eps = C1.episodes("W0", 8)
    ev = SUB.evaluate_any(pop[0], eps, rng_seed=0); ev2 = SUB.evaluate_any(pop[0], eps, rng_seed=0)
    rep["evaluate_any_ok"] = 0.0 <= ev["reward"] <= 1.0 and ev["substrate"] == "graph"
    rep["evaluate_deterministic"] = json.dumps(ev, sort_keys=True, default=str) == json.dumps(ev2, sort_keys=True, default=str)
    t0, ext = SUB.rows_any(pop[0], "g0", None, 0, 0, ev, ev["_answers"], ["W0"], ev["_asks_per_episode"])
    rep["row_graph"] = t0["behaviour"]["substrate"] == "graph" and "nodes_executed" in t0["behaviour"] and len(json.dumps(t0)) <= 1024
    w = world_from_record(sample_world(77, bin_target=5))
    wv = evaluate_world(pop[1], w, seed=1, E=3)
    rep["composed_world_graph"] = 0.0 <= wv["reward"] <= 1.0 and wv["meter"].get("nodes_executed") is not None
    # firewall
    try:
        SUB.descend_for(SUB.organism_record_for(pop[0], None, 0), 1, mate=SUB.organism_record_for(C1.parents_from_population()[0]["parent"], None, 0))
        rep["cross_substrate_mate_refused"] = False
    except ValueError:
        rep["cross_substrate_mate_refused"] = True
    # a segment
    frozen = json.load(open(REPO / "archaeon/campaign6/observatory/DETECTORS_FROZEN_candidate.json", encoding="utf-8"))
    thr = {k: v["threshold"] for k, v in frozen["thresholds"].items() if v.get("threshold") is not None}
    thr.update({"lineage_discontinuity.struct_max": 0.25, "unexplained_gain.struct_max": 0.25, "unexpected_transfer.floor": 3 / 16, "structural_reuse": 2})
    prov = S.provenance("PROCEDURAL", "graph_profile_test", "0.1", 1, {})
    base = dict(run_id=prov["run_id"], provenance=prov, world={"kind": "wse.WorldSpec", "knobs": C1.ENVS["W0"].knobs()}, profile="graph", schedule=P.stable(12), N=16, E=6,
                archive={"dense_until": 8, "neighbourhood": 4}, thresholds=thr, spread=frozen["spread"], seed=1, freeze_policy="tiered")
    s12 = SG.make_spec(g0=0, g1=12, **base); ck = SG.initial_checkpoint(s12, pop)
    a = SG.run_segment(s12, ck); b = SG.run_segment(s12, ck)
    s1 = SG.make_spec(g0=0, g1=6, **base); s2 = SG.make_spec(g0=6, g1=12, **base)
    o1 = SG.run_segment(s1, SG.initial_checkpoint(s1, pop)); o2 = SG.run_segment(s2, o1["checkpoint_out"])
    rep["segment_deterministic"] = a["out_digest"] == b["out_digest"]
    rep["segment_continuity"] = sorted(o["organism_id"] for o in o2["checkpoint_out"]["population"]) == sorted(o["organism_id"] for o in a["checkpoint_out"]["population"])
    rep["segment"] = {"evaluations": a["evaluations"], "events": len(a["events"]), "freezes": len(a["freezes"]), "anchors": len(a["anchors"]), "lineage_records": len(a["lineage_delta"])}
    rep["runtime_hash_graph"] = SUB.PROFILES["graph"]["runtime_hash"][:16]
    unable = {}
    for e in a["events"]:
        for d in e["unable"]:
            unable[d] = unable.get(d, 0) + 1
    rep["unable_by_detector"] = unable
    print(json.dumps(rep, indent=1))
    ok = all(rep[k] for k in ("evaluate_any_ok", "evaluate_deterministic", "row_graph", "composed_world_graph", "cross_substrate_mate_refused", "segment_deterministic", "segment_continuity"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
