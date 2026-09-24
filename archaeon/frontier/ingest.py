"""DEEP FRONTIER -- ingest the unresolved observations of Campaigns 4, 5 and 6 as lineages with frontiers
(directive BEGIN 3, s11), and prepare the FIRST FRONTIER without executing it (BEGIN 5).

Every seed lineage below cites the committed artifact its originating observation comes from; every
transformation is a DESCRIPTION of a run (dims varied, from -> to, budget) that the executor can turn
into a segment spec after G6-0. Nothing here evaluates an organism.

    python -m archaeon.frontier.ingest        # idempotent: lineages keyed by originating observation
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from archaeon.frontier.registry import Registry                              # noqa: E402
from archaeon.frontier.queues import Queues                                  # noqa: E402

WG = "archaeon.c6.world_gen/0.1"


def T(tid, dims, frm, to, budget, note=""):
    return {"id": tid, "dims": dims, "from": frm, "to": to, "budget_evaluations": budget, "status": "PENDING", "note": note}


SEEDS = [
    # ---------------------------------------------------------------- Campaign 4 / 5 fossils (REVISIT)
    dict(key="C4-cliff", title="The damage cliff: no single edit falls between neutral and destroyed",
         obs={"source": "C4-01/C4-02", "ref": "archaeon/campaign4/DAMAGE_GEOMETRY_MAP.md", "summary": "1-3% of single edits fall between D5 and D2; D7 = 0 in 5,472 edits; replicated 5,586/5,586 in C5-05"},
         mode="REVISIT", limits=["v0 flat genome: positions not parts (Proteus Axis O scope)"],
         trs=[T("C4-cliff.T1", ["organism_profile"], "v0", "graph_organism.v1", 20000, "the same census under the graph grammar: does the cliff survive connectivity-based edits?"),
              T("C4-cliff.T2", ["world_geometry"], "WorldSpec W0/W2", "composed bins 3,6,9", 30000, "single-edit geometry on feedback worlds"),
              T("C4-cliff.T3", ["organism_profile", "world_geometry"], "v0/W0", "graph/composed", 30000, "both at once")]),
    dict(key="C4-exapt", title="Neutral-network exaptation rises with depth but yield per evaluation falls",
         obs={"source": "C4-05/C5-01", "ref": "archaeon/campaign5/C5-01/READOUT.md", "summary": ".050->.082 at depth 16->64; yield/eval .00127->.00082 below a single edit's .0012; shelf stratum only"},
         mode="REVISIT", limits=["measured on 5 fixed WorldSpec environments"],
         trs=[T("C4-exapt.T1", ["evaluation_horizon", "world_geometry"], "5 envs", "20 composed worlds as exposure set", 40000, "is exaptation an artefact of a 5-world exposure set?"),
              T("C4-exapt.T2", ["organism_profile"], "v0", "graph", 40000, "neutral walks under connectivity edits"),
              T("C4-exapt.T3", ["pressure_timing"], "stable", "labeled schedules with regime changes", 40000, "does a regime change convert neutral depth into gain?")]),
    dict(key="C5-flat", title="The flat elite: 100-180 generations of N=50 move nothing on screened worlds with headroom",
         obs={"source": "C5-02/C5-09", "ref": "archaeon/campaign5/C5-02/READOUT.md", "summary": "0/24 and 0/96 cells improved by a band at equal compute; elite = starting parent"},
         mode="DEPTH", limits=["frozen grammar v0.4 on the flat genome"],
         trs=[T("C5-flat.T1", ["population_size"], "50", "200, 800", 60000, "is it N?"),
              T("C5-flat.T2", ["mutation_operators", "organism_profile"], "v0.4", "graph_grammar.v1", 60000, "is it the grammar?"),
              T("C5-flat.T3", ["evaluation_horizon"], "100 gens", "2,000 gens with archive", 100000, "is it time?"),
              T("C5-flat.T4", ["world_geometry"], "W3_K3/W4_K4", "composed worlds with resources + locality", 60000, "is it the world's cliff?"),
              T("C5-flat.T5", ["lateral_transfer", "population_structure"], "single population", "4 demes with migration schedule", 60000, "structure?")]),
    dict(key="C5-asym", title="Opcode faults recover when skipped, register faults are lost when skipped",
         obs={"source": "C5-06", "ref": "archaeon/campaign5/C5-06/READOUT.md", "summary": "RECOVERY 209 opcode vs 25 register; INSULATION_LOSS 15 vs 142; the two encodings fail in opposite directions"},
         mode="DEPTH", limits=["representation B only; v0 semantics"],
         trs=[T("C5-asym.T1", ["organism_profile"], "repb_fizzle", "graph profile with dormant nodes", 30000, "does the asymmetry exist when structure is connectivity?"),
              T("C5-asym.T2", ["evaluation_horizon", "world_geometry"], "single edits", "100-generation evolution on composed worlds under FIZZLE", 60000, "do recovered holes accumulate as hidden load or get reused?"),
              T("C5-asym.T3", ["mutation_operators"], "grammar B", "grammar B with reconnection of dormant structure", 30000, "is a skipped fault ever reconnected?")]),
    dict(key="C5-load", title="FIZZLE populations carry executed faults in .46-.80 of members with nothing bought",
         obs={"source": "C5-09", "ref": "archaeon/campaign5/C5-09/READOUT.md", "summary": "hidden load under insulation; no discovery gain in 96 cells"},
         mode="REVISIT", limits=["100 generations"],
         trs=[T("C5-load.T1", ["evaluation_horizon"], "100", "5,000 gens", 250000, "does hidden load ever pay (a neutral structure useful much later)?"),
              T("C5-load.T2", ["pressure_intensity"], "none", "structure-cost channel (world charges dormant nodes)", 60000, "load under a cost")]),
    # ---------------------------------------------------------------- Campaign 6 observations
    dict(key="C6-blind", title="Population churn swamps single-organism novelty/discontinuity on the old substrate",
         obs={"source": "C6 calibration rounds 4-6", "ref": "archaeon/campaign6/observatory/CALIBRATION_population_v0.3.json", "summary": "at 1% false-fire, novelty catches 25% and discontinuity 0% of planted events"},
         mode="BLIND_SPOT", limits=["single-organism distance on v0 populations"],
         trs=[T("C6-blind.T1", ["organism_profile"], "v0", "graph_organism.v1", 30000, "does churn shrink when structure is connectivity? (positive control search)"),
              T("C6-blind.T2", ["world_geometry"], "W0", "composed bins 2-8", 40000, "is churn a W0 property?"),
              T("C6-blind.T3", ["measurement_view"], "organism vs pool", "lineage-relative distance (ancestors+siblings only)", 20000, "a different statistic, in a recorded calibration epoch, not a threshold move"),
              T("C6-blind.T4", ["population_size"], "32", "8, 128", 30000, "churn vs N")]),
    dict(key="C6-unable", title="Detectors 4-9 UNABLE or without positive control on the old substrate",
         obs={"source": "C6 ADMISSION_PACKET_v0.1", "ref": "archaeon/campaign6/observatory/ADMISSION_PACKET_v0.1.md", "summary": "environmental_modification, niche_divergence, regime_persistence, unexplained_gain, unexpected_causal_dependence, structural_reuse need C6 geometry"},
         mode="BLIND_SPOT", limits=["needs composed worlds with persistent state, >=2 resources, regime changes; graph profile for components; replay D and ablation sets"],
         trs=[T("C6-unable.T1", ["world_geometry"], "none", "composed worlds with objects+coupling (detector 5 positive controls: a planted writer/reader pair)", 30000),
              T("C6-unable.T2", ["world_geometry", "population_structure"], "one resource", ">=3 resources at distinct nodes; planted specialists (detector 6)", 30000),
              T("C6-unable.T3", ["pressure_timing"], "stable", "step/catastrophe schedules; planted regime-robust organism (detector 7)", 30000),
              T("C6-unable.T4", ["measurement_view"], "in-loop", "replay D and per-node ablation at escalation (detectors 8, 9) on the graph profile", 20000),
              T("C6-unable.T5", ["organism_profile"], "v0 duplicate blocks", "graph SUBGRAPH_COPY executed at >=2 sites (detector 4)", 20000)]),
    dict(key="C6-volume", title="Escalation volume 11-32% of evaluations on composed worlds, dominated by unvalidated rulers",
         obs={"source": "G6-0 rehearsal", "ref": "archaeon/campaign6/G6-0/REHEARSAL_2026-09-18_bin10.json", "summary": "415 events / 1,280 evaluations at bin 10; every firing froze"},
         mode="AUDIT", limits=["freeze policy pending Harmonia"],
         trs=[T("C6-volume.T1", ["measurement_view"], "freeze on any firing", "tiered: EVENT_RECORD / PARTIAL / FULL (s9)", 20000, "cost table per tier per bin"),
              T("C6-volume.T2", ["world_complexity"], "bins 6, 10", "bins 0-10 sweep", 60000, "escalation rate vs complexity bin (return item 13's input)")]),
    dict(key="C6-novel5", title="Five alive, moved children not novel against the library (round 3)",
         obs={"source": "C6 calibration round 3", "ref": "archaeon/campaign6/observatory/CALIBRATION_v0.1.json", "summary": "behavioral_novelty.misses: children that moved from their parent onto another library member's behaviour"},
         mode="AUDIT", limits=[], trs=[T("C6-novel5.T1", ["measurement_view"], "nearest-of-pool", "nearest-of-lineage vs nearest-of-library reported separately", 5000, "are they convergences (real) or distance artefacts?")]),
    # ---------------------------------------------------------------- breadth seeds (procedural, no hypothesis)
    dict(key="B-scatter", title="Breadth scatter: procedural worlds x unlabeled schedules x v0/graph, uniform bins",
         obs={"source": "directive s3", "ref": "archaeon/frontier/DEEP_FRONTIER_CHARTER.md", "summary": "no hypothesis; PROCEDURAL lane; seeds 10000-10399 reserved"},
         mode="BREADTH", limits=[],
         trs=[T("B-scatter.T%03d" % i, ["random_seed", "world_geometry", "pressure_timing"], "-", "world seed %d, schedule unlabeled(%d), bin uniform" % (10000 + i, 10000 + i), 20000) for i in range(40)]),
    dict(key="B-worldgen", title="World-generator mutation lineage (s4): the generator itself as an evolving object",
         obs={"source": "directive s4", "ref": "archaeon/campaign6/worlds/generator.py", "summary": "ten features are the initial ontology, not the permanent one"},
         mode="BREADTH", limits=["every generator mutation must be reproducible from a recorded spec + seed"],
         trs=[T("B-worldgen.T1", ["world_geometry"], "ring locality", "2-D grid + dynamic topology (edges appear/disappear on a schedule)", 40000),
              T("B-worldgen.T2", ["resource_topology"], "R pools", "resource conversion chains (pool A feeds pool B via an object write)", 40000),
              T("B-worldgen.T3", ["interaction_topology"], "shared pools", "artifacts: objects written by one organism read by later generations (niche construction)", 40000),
              T("B-worldgen.T4", ["environmental_nonstationarity"], "regime clock", "seasonality (periodic) + rare catastrophe + recovery ramps", 40000),
              T("B-worldgen.T5", ["evaluation_horizon"], "24 ticks", "structure that pays only after 200+ ticks (long-history opportunities)", 60000)]),
    dict(key="B-pressure", title="Pressures that require machinery (s5): ecological conditions, not required solutions",
         obs={"source": "directive s5", "ref": "archaeon/campaign6/pressure/schedules.py", "summary": "reward persistence, addressable intermediates, reuse, prediction, transfer -- as conditions"},
         mode="BREADTH", limits=["no pressure names a mechanism"],
         trs=[T("B-pressure.T1", ["pressure_intensity"], "single-tick harvest", "harvest value = f(state kept across ticks): intermediate results must persist", 40000),
              T("B-pressure.T2", ["pressure_timing"], "stable", "predictable regime alternation: payoff to anticipating the switch", 40000),
              T("B-pressure.T3", ["interaction_topology"], "independent organisms", "payoff to reading another organism's object writes (exploiting artifacts)", 40000),
              T("B-pressure.T4", ["developmental_schedule"], "fixed lifetime", "lifetime extends with competence (experience-to-competence conversion)", 40000)]),
]


def main() -> int:
    reg = Registry(); q = Queues()
    existing = {r["originating_observation"].get("key"): r["lineage_id"] for r in reg.all()}
    created = []
    for s in SEEDS:
        if s["key"] in existing:
            continue
        obs = dict(s["obs"]); obs["key"] = s["key"]
        lid = reg.create(originating_observation=obs, mode=s["mode"], world_generator_version=WG, transformations=s["trs"], tags=[s["key"].split("-")[0]],
                         representation_limits=s.get("limits", []), title=s["title"])
        pool = {"BREADTH": "EXPLORATION", "DEPTH": "EXPLOITATION", "AUDIT": "AUDIT", "BLIND_SPOT": "AUDIT", "REVISIT": "REVISIT"}[s["mode"]]
        for i, t in enumerate(s["trs"]):
            lane = "PROCEDURAL" if s["key"].startswith("B-scatter") else "LLM_PROPOSED"
            q.push(pool, lineage_id=lid, transformation_id=t["id"], priority=1.0 - 0.01 * i, lane=lane, budget_evaluations=t["budget_evaluations"], note=t.get("note", ""))
        created.append((lid, s["key"], len(s["trs"])))
    print(json.dumps({"created": created, "registry": reg.summary(), "queues": q.status()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
