"""One-time, idempotent migration (operator directive s1): every registry transformation gets an executable
`spec` (archaeon.frontier.experiment_spec.v1) derived by code from its dims/target, plus the breadth scatter
becomes a parameterized FAMILY sweep. Transformations already carrying a valid spec are left alone.

    python -m archaeon.frontier.migrate_specs
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.frontier import specs as SP                                    # noqa: E402
from archaeon.frontier.registry import Registry                              # noqa: E402
from archaeon.frontier.queues import Queues                                  # noqa: E402


def spec_for(rec: dict, t: dict) -> dict:
    key = rec["originating_observation"].get("key", ""); tid = t["id"]; to = str(t.get("to", "")); dims = t.get("dims", [])
    nums = [int(x) for x in re.findall(r"\b(\d{1,6})\b", to)]
    seed = 40000 + (sum(ord(c) for c in tid) % 9973)
    N, E, gens, profile, lane = 32, 8, 250, "v0", "LLM_PROPOSED"
    world = None; sched = {"kind": "stable", "seed": seed}; pop = {"source": "c4_parents", "seed": seed, "N": N}
    budget = int(t.get("budget_evaluations", 20000))
    if "graph" in to.lower():
        profile = "graph"; pop = {"source": "foundry", "seed": seed, "N": N}
    if "repb" in to.lower() or "fizzle" in to.lower() or key in ("C5-asym", "C5-load"):
        profile = "repb_fizzle"
    if "population_size" in dims and nums:
        N = max(8, min(800, nums[0])); pop["N"] = N
    if "evaluation_horizon" in dims and nums:
        gens = max(gens, min(5000, max(nums)))
    if any(d in dims for d in ("pressure_timing", "pressure_intensity", "environmental_nonstationarity")):
        sched = {"kind": "labeled", "seed": seed}
    if key.startswith("B-scatter"):
        ws = nums[0] if nums else 10000
        world = {"kind": "c6.composed.sample", "seed": ws, "bin": None}; sched = {"kind": "unlabeled", "seed": ws}; lane = "PROCEDURAL"; seed = ws
    elif any(d in dims for d in ("world_geometry", "world_complexity", "resource_topology", "interaction_topology")) or key.startswith(("C6-unable", "B-worldgen", "B-pressure")):
        b = nums[0] if (nums and nums[0] <= 10) else (7 if key.startswith("C6-unable") else 8 if key.startswith("B-") else 5)
        world = {"kind": "c6.composed.sample", "seed": seed, "bin": b}
        if key.startswith("B-pressure"):
            sched = {"kind": "labeled", "seed": seed}; lane = "MIXED"
        if key.startswith("B-worldgen"):
            sched = {"kind": "unlabeled", "seed": seed}; lane = "MIXED"
    if world is None:
        if key.startswith("C5-flat"):
            from archaeon.campaign5.screen_worlds import CANDIDATES
            world = {"kind": "wse.WorldSpec", "knobs": CANDIDATES["W3_K3"].knobs()}; pop["N"] = max(pop["N"], 50); E = 16
        elif key in ("C5-asym", "C5-load", "C4-exapt"):
            world = {"kind": "wse.WorldSpec", "knobs": C1.ENVS["W2_K2"].knobs()}
        else:
            world = {"kind": "wse.WorldSpec", "knobs": C1.ENVS["W0"].knobs()}
    gens = max(gens, min(5000, budget // max(1, pop["N"])))
    return SP.make_spec(family_id=key, experiment_id=tid, world=world, profile=profile, population=pop, E=E, generations=gens, chunk=250, schedule=sched, seed=seed,
                        budget_evaluations=budget, lane=lane, generator="frontier.migrate", note=to[:120])


def main() -> int:
    reg = Registry(); q = Queues(); added = 0; kept = 0; failed = []
    for rec in reg.all():
        trs = [dict(t) for t in rec["transformations"]]; changed = False
        for t in trs:
            if t.get("spec"):
                try:
                    SP.validate_spec(t["spec"]); kept += 1; continue
                except SP.SpecError:
                    pass
            try:
                t["spec"] = spec_for(rec, t); added += 1; changed = True
            except SP.SpecError as e:
                failed.append((t["id"], str(e)))
        if changed:
            reg.update(rec["lineage_id"], transformations=trs)
            reg.event(rec["lineage_id"], "SPECS_ATTACHED", {"n": sum(1 for t in trs if t.get("spec"))})
    # the breadth scatter as a FAMILY sweep: 40 world seeds x 2 profiles x 2 population sizes = 160 specs, one lineage
    existing = {r["originating_observation"].get("key") for r in reg.all()}
    if "B-scatter.family" not in existing:
        tmpl = SP.make_spec(family_id="B-scatter.family", world={"kind": "c6.composed.sample", "seed": 10000, "bin": None}, profile="v0", population={"source": "c4_parents", "seed": 1, "N": 32},
                            E=8, generations=250, chunk=250, schedule={"kind": "unlabeled", "seed": 10000}, seed=10000, budget_evaluations=8000, lane="PROCEDURAL", generator="frontier.scatter.family")
        fam = []
        for ws in range(10040, 10080):
            for prof, src in (("v0", "c4_parents"), ("graph", "foundry")):
                for N in (16, 64):
                    s = json.loads(json.dumps(tmpl)); s["world"]["seed"] = ws; s["schedule"]["seed"] = ws; s["seed"] = ws
                    s["organism"] = {"profile": prof, "population": {"source": src, "seed": ws, "N": N}}; s["budget"]["evaluations"] = N * 250
                    s.pop("spec_digest", None); s["required_capabilities"] = SP.capabilities_for(s); s["sweep_point"] = {"world_seed": ws, "profile": prof, "N": N}
                    s["experiment_id"] = "B-scatter.family/%d_%s_N%d" % (ws, prof, N); fam.append(SP.validate_spec(s))
        trs = [{"id": s["experiment_id"], "dims": ["random_seed", "organism_profile", "population_size"], "from": "-", "to": json.dumps(s["sweep_point"]), "budget_evaluations": s["budget"]["evaluations"], "status": "PENDING", "spec": s} for s in fam]
        lid = reg.create(originating_observation={"key": "B-scatter.family", "source": "directive s9", "summary": "parameterized breadth family: 40 world seeds x {v0, graph} x N in {16, 64}"},
                         mode="BREADTH", title="Breadth scatter family (procedural worlds x unlabeled schedules x two substrates x two N)", transformations=trs, tags=["B", "family"])
        for i, t in enumerate(trs):
            q.push("EXPLORATION", lineage_id=lid, transformation_id=t["id"], priority=0.5 - 0.001 * i, lane="PROCEDURAL", budget_evaluations=t["budget_evaluations"])
    print(json.dumps({"specs_added": added, "kept": kept, "failed": failed, "registry": reg.summary(), "queues": {k: v["pending"] for k, v in q.status().items()}}, indent=1))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
