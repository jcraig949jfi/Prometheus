"""DEEP FRONTIER -- the loop runner (directive s1, s12). CONSTRUCTED before G6-0; it runs live only when
`--live` is given AND archaeon/frontier/G6-0_CLOSED.json exists (written by the campaign lead when the
fleet-wide G6-0 receipt is on main). Without --live it executes nothing.

    python -m archaeon.frontier.loop --self-test              # temp registry/queues, one tiny item, W0, 20 generations
    python -m archaeon.frontier.loop --live --epochs 1        # after G6-0: pops items by pool share, runs segments,
                                                              # records runs/observations/events, branches on triggers

One iteration = pop an item from a pool chosen by the current shares (weighted round-robin over
pending budget), build a segment spec from the transformation (concrete builders below; a
transformation whose builder needs a profile or world kind not yet registered is marked BLOCKED
with the reason and left on the frontier), run it in chunks of `chunk` generations with checkpoint
continuity, record every chunk in the registry (run refs = out digests + artifact paths), branch on
the s7 triggers (a new PENDING transformation per trigger kind, pushed to the pool the lineage
belongs to), and charge the pool. Every segment output is written under archaeon/frontier/runs/
<lineage>/<transformation>/<chunk>.json.gz (rows included: the sidecar), never rewritten.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign6 import schemas as S                                  # noqa: E402
from archaeon.campaign6 import segment as SG                                 # noqa: E402
from archaeon.campaign6.worlds import sample_world                           # noqa: E402
from archaeon.campaign6.pressure import schedules as P                       # noqa: E402
from archaeon.frontier.registry import Registry                              # noqa: E402
from archaeon.frontier.queues import Queues                                  # noqa: E402
from archaeon.frontier.allocation import RULES                               # noqa: E402

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
GATE = HERE / "G6-0_CLOSED.json"
BRANCH_TRIGGERS = ("admitted_detector_firing", "persistent_weak_signal", "detector_disagreement", "classifier_failure", "unexplained_phenotype_transition",
                   "unusual_survival", "unexpected_transfer", "large_change_small_distance", "small_change_large_distance", "anomalous_ecological_effect",
                   "unexpected_robustness", "unexpected_fragility", "forensic_nomination", "random_audit_sample")


def frozen_table() -> Tuple[dict, dict]:
    frozen = json.loads((REPO / "archaeon/campaign6/observatory/DETECTORS_FROZEN_candidate.json").read_text(encoding="utf-8"))
    thr = {k: v["threshold"] for k, v in frozen["thresholds"].items() if v.get("threshold") is not None}
    thr.update({"lineage_discontinuity.struct_max": 0.25, "unexplained_gain.struct_max": 0.25, "unexpected_transfer.floor": 3 / 16, "structural_reuse": 2,
                "environmental_modification": 0, "niche_divergence": 0.5, "regime_persistence": 1 / 16})
    return thr, frozen


# ---------------------------------------------------------------- builders: transformation -> (spec kwargs, init population) or BLOCKED
def build(lineage: dict, tr: dict, frozen: dict, thr: dict, *, N: int = 32, E: int = 8, gens: int = 1000) -> Tuple[Optional[dict], Optional[List[dict]], str]:
    key = lineage["originating_observation"].get("key", "")
    tid = tr["id"]; to = str(tr.get("to", "")); dims = tr.get("dims", [])
    parents = C1.parents_from_population()
    init = [p["parent"] for p in parents][:N]
    while len(init) < N:
        init.append(init[len(init) % len(parents)])
    needs_graph = "graph" in to.lower() or "organism_profile" in dims and "graph" in to.lower()
    if needs_graph:
        return None, None, "BLOCKED: graph profile not registered (PROTEUS-47)"
    ov = tr.get("params", {})
    gens = int(gens * ov.get("gens_mult", 1))
    if key.startswith("B-scatter"):
        seed = int(to.split("world seed")[1].split(",")[0]) if "world seed" in to else int(ov.get("seed", 10000))
        seed += int(ov.get("seed_offset", 0))
        w = sample_world(seed); sched = P.unlabeled(seed, gens)
        prov = S.provenance("PROCEDURAL", "frontier.scatter", "0.1", seed, {"world_seed": seed, "bin": w["complexity_bin"]}, thresholds_digest=frozen["digest"])
        return dict(run_id=prov["run_id"], provenance=prov, world={"kind": "c6.composed.v1", "params": w["params"]}, profile="v0", schedule=sched, N=N, E=E,
                    archive={"dense_until": 64, "neighbourhood": 16}, thresholds=thr, spread=frozen["spread"], seed=seed, freeze_policy="tiered"), init, "OK"
    if key == "C6-volume" and tid.endswith("T2"):
        b = int(tr.get("_bin", 5)); seed = 20000 + b
        w = sample_world(seed, bin_target=b); sched = P.stable(gens)
        prov = S.provenance("LLM_PROPOSED", "frontier.volume_sweep", "0.1", seed, {"bin": b}, thresholds_digest=frozen["digest"])
        return dict(run_id=prov["run_id"], provenance=prov, world={"kind": "c6.composed.v1", "params": w["params"]}, profile="v0", schedule=sched, N=N, E=E,
                    archive={"dense_until": 64, "neighbourhood": 16}, thresholds=thr, spread=frozen["spread"], seed=seed, freeze_policy="tiered"), init, "OK"
    if key == "C5-flat" and tid.endswith("T3"):
        prov = S.provenance("LLM_PROPOSED", "frontier.flat_time", "0.1", 3, {"world": "W3_K3"}, thresholds_digest=frozen["digest"])
        from archaeon.campaign5.screen_worlds import CANDIDATES
        return dict(run_id=prov["run_id"], provenance=prov, world={"kind": "wse.WorldSpec", "knobs": CANDIDATES["W3_K3"].knobs()}, profile="v0",
                    schedule=P.stable(gens), N=50, E=16, archive={"dense_until": 64, "neighbourhood": 16}, thresholds=thr, spread=frozen["spread"], seed=3, freeze_policy="tiered"), init[:50], "OK"
    if key == "C5-load" and tid.endswith("T1"):
        prov = S.provenance("LLM_PROPOSED", "frontier.load", "0.1", 5, {"profile": "repb_fizzle"}, thresholds_digest=frozen["digest"])
        return dict(run_id=prov["run_id"], provenance=prov, world={"kind": "wse.WorldSpec", "knobs": C1.ENVS["W2_K2"].knobs()}, profile="repb_fizzle", schedule=P.stable(gens),
                    N=N, E=E, archive={"dense_until": 64, "neighbourhood": 16}, thresholds=thr, spread=frozen["spread"], seed=5, freeze_policy="tiered"), init, "OK"
    return None, None, "BLOCKED: no concrete builder yet for %s (%s)" % (tid, ", ".join(dims))


# ---------------------------------------------------------------- branching on s7 triggers
def branch_from(out: dict, lineage: dict, tr: dict, rng_seed: int) -> List[dict]:
    """Descendants proposed from one chunk's events. Each is one transformation on the lineage's frontier; the trigger is recorded."""
    new = []
    fired_by = {}
    for e in out["events"]:
        for d in e["fired"]:
            fired_by[d] = fired_by.get(d, 0) + 1
    base = tr["id"]
    if any(d not in ("detector_disagreement", "classifier_failure", "structural_reuse") for d in fired_by):
        pv = dict(tr.get("params", {}))
        new.append({"id": base + ".d_seed", "dims": ["random_seed"], "from": "seed", "to": "seed+1 (initialization control)", "budget_evaluations": tr["budget_evaluations"] // 2,
                    "trigger": "admitted_detector_firing", "status": "PENDING", "params": {**pv, "seed_offset": pv.get("seed_offset", 0) + 1}})
        new.append({"id": base + ".d_horizon", "dims": ["evaluation_horizon"], "from": "1 chunk", "to": "4 chunks (persistence)", "budget_evaluations": tr["budget_evaluations"] * 2,
                    "trigger": "admitted_detector_firing", "status": "PENDING", "params": {**pv, "gens_mult": pv.get("gens_mult", 1) * 4}})
    if fired_by.get("detector_disagreement", 0) >= 3:
        new.append({"id": base + ".d_view", "dims": ["measurement_view"], "from": "in-loop", "to": "replay A + D on the disagreeing subjects", "budget_evaluations": 5000, "trigger": "detector_disagreement", "status": "PENDING"})
    if fired_by.get("classifier_failure", 0) >= 3:
        new.append({"id": base + ".d_unknown", "dims": ["world_complexity"], "from": "this bin", "to": "bin-1 and bin+1 (where does the blindness start?)", "budget_evaluations": tr["budget_evaluations"], "trigger": "classifier_failure", "status": "PENDING"})
    if any(f["scope"] == "COMPLETE" for f in out["freezes"]) and rng_seed % 50 == 0:
        new.append({"id": base + ".d_audit", "dims": ["random_seed"], "from": "-", "to": "random audit replay", "budget_evaluations": 2000, "trigger": "random_audit_sample", "status": "PENDING"})
    return new


# ---------------------------------------------------------------- one iteration
def choose_pool(q: Queues, shares: Dict[str, float], spent: Dict[str, int]) -> Optional[str]:
    tot = max(1, sum(spent.values()))
    best, gap = None, -1.0
    for pool in ("EXPLORATION", "EXPLOITATION", "AUDIT", "REVISIT"):
        share = shares.get("AUDIT" if pool == "REVISIT" else pool, 0.0)
        if not q.pending(pool):
            continue
        g = share - spent.get(pool, 0) / tot
        if g > gap:
            best, gap = pool, g
    return best


def iterate(reg: Registry, q: Queues, shares: Dict[str, float], spent: Dict[str, int], *, chunk: int = 1000, gens_cap: int = 1000, runs_dir: Path = RUNS, N: int = 32, E: int = 8) -> dict:
    thr, frozen = frozen_table()
    pool = choose_pool(q, shares, spent)
    if pool is None:
        return {"status": "IDLE", "reason": "no pending items"}
    item = q.pop(pool); lineage = reg.get(item["lineage_id"])
    tr = next(t for t in lineage["transformations"] if t["id"] == item["transformation_id"])
    kw, init, why = build(lineage, tr, frozen, thr, N=N, E=E, gens=gens_cap)
    if kw is None:
        q.set_state(pool, item["item_id"], "PENDING", note=why); reg.event(lineage["lineage_id"], "BLOCKED", {"transformation": tr["id"], "reason": why})
        # demote so the loop moves on; the item stays on the frontier
        it = dict(q.items[pool][item["item_id"]]); it["priority"] = it["priority"] - 1.0; q._append(pool, it)
        return {"status": "BLOCKED", "lineage": lineage["lineage_id"], "transformation": tr["id"], "reason": why}
    gens = min(gens_cap, max(chunk, tr["budget_evaluations"] // max(1, kw["N"])))
    n_chunks = max(1, gens // chunk)
    out_dir = runs_dir / lineage["lineage_id"] / tr["id"]; out_dir.mkdir(parents=True, exist_ok=True)
    spec0 = SG.make_spec(g0=0, g1=min(chunk, gens), **kw); ck = SG.initial_checkpoint(spec0, init)
    total_evals = 0; refs = []; branches = []
    for c in range(n_chunks):
        g0, g1 = c * chunk, min(gens, (c + 1) * chunk)
        spec = SG.make_spec(g0=g0, g1=g1, **kw)
        out = SG.run_segment(spec, ck)
        path = out_dir / ("chunk_%03d.json.gz" % c)
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump({"spec": spec, "checkpoint_in_digest": ck["digest"], "out": out}, f, default=str)
        ref = {"chunk": c, "g0": g0, "g1": g1, "spec_hash": spec["spec_hash"], "out_digest": out["out_digest"], "path": (str(path.relative_to(REPO)) if str(path).startswith(str(REPO)) else str(path)).replace("\\", "/"),
               "evaluations": out["evaluations"], "events": len(out["events"]), "freezes": len(out["freezes"]), "anchors": len(out["anchors"])}
        refs.append(ref); total_evals += out["evaluations"]; ck = out["checkpoint_out"]
        reg.event(lineage["lineage_id"], "CHUNK", ref)
        for fz in out["freezes"]:
            reg.event(lineage["lineage_id"], "FREEZE_REF", {"event_id": fz["event_id"], "scope": fz["scope"], "digest": fz["freeze_digest"], "chunk": c})
        branches += branch_from(out, lineage, tr, kw["seed"] + c)
    reg.record_run(lineage["lineage_id"], tr["id"], {"chunks": refs, "provenance": kw["provenance"]}, status="RUN", evaluations=total_evals)
    reg.observe(lineage["lineage_id"], "transformation %s ran %d chunks, %d evaluations, %d events, %d freezes" % (tr["id"], len(refs), total_evals, sum(r["events"] for r in refs), sum(r["freezes"] for r in refs)),
                ref={"transformation": tr["id"], "chunks": [r["out_digest"] for r in refs]})
    if branches:
        seen = {t["id"] for t in reg.get(lineage["lineage_id"])["transformations"]}
        uniq = {}
        for b in branches:
            if b["id"] not in seen and b["id"] not in uniq:
                uniq[b["id"]] = b
        branches = list(uniq.values())
        if branches:
            reg.add_transformations(lineage["lineage_id"], branches)
            for b in branches:
                q.push(pool, lineage_id=lineage["lineage_id"], transformation_id=b["id"], priority=item["priority"] + 0.5, lane="EVOLUTION_GENERATED" if b.get("trigger") != "random_audit_sample" else "PROCEDURAL",
                       budget_evaluations=b["budget_evaluations"], note="branch on " + b.get("trigger", ""))
    q.set_state(pool, item["item_id"], "DONE")
    spent[pool] = spent.get(pool, 0) + total_evals
    return {"status": "RAN", "pool": pool, "lineage": lineage["lineage_id"], "transformation": tr["id"], "evaluations": total_evals, "chunks": len(refs), "branches": [b["id"] for b in branches]}


def self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="frontier_selftest_"))
    reg = Registry(tmp / "registry"); q = Queues(tmp / "queues")
    lid = reg.create(originating_observation={"key": "B-scatter", "source": "self-test", "summary": "tiny"}, mode="BREADTH", title="self-test",
                     transformations=[{"id": "B-scatter.T000", "dims": ["random_seed"], "from": "-", "to": "world seed 10000, schedule unlabeled(10000)", "budget_evaluations": 640, "status": "PENDING"}])
    q.push("EXPLORATION", lineage_id=lid, transformation_id="B-scatter.T000", priority=1.0, lane="PROCEDURAL", budget_evaluations=640)
    spent = {}
    r1 = iterate(reg, q, RULES["initial"], spent, chunk=10, gens_cap=20, runs_dir=tmp / "runs", N=16, E=4)
    r2 = iterate(reg, q, RULES["initial"], spent, chunk=10, gens_cap=20, runs_dir=tmp / "runs", N=16, E=4)
    rec = reg.get(lid)
    rep = {"first": r1, "second": r2["status"], "lineage_versions": rec["version"], "frontier_after": rec["frontier"], "evaluations_used": rec["budgets"]["evaluations_used"],
           "observations": len(rec["observations"]), "events_logged": sum(1 for _ in open(reg.events_path, encoding="utf-8")), "tmp": str(tmp), "gate_exists": GATE.exists()}
    print(json.dumps(rep, indent=1, default=str))
    ok = r1["status"] == "RAN" and r1["chunks"] == 2 and rec["budgets"]["evaluations_used"] == r1["evaluations"] + (r2.get("evaluations", 0) if r2["status"] == "RAN" else 0)
    ok = ok and len(rec["frontier"]) == len(set(rec["frontier"]))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--iterations", type=int, default=10)
    ap.add_argument("--chunk", type=int, default=1000)
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.live:
        print("constructed; nothing executed (pass --live after G6-0 closes; the gate file is %s)" % GATE); return 0
    if not GATE.exists():
        print("REFUSED: G6-0 is not closed (no %s)" % GATE); return 2
    reg = Registry(); q = Queues(); shares = dict(RULES["initial"]); spent = {}
    for i in range(a.iterations):
        r = iterate(reg, q, shares, spent, chunk=a.chunk)
        print(json.dumps(r, default=str))
        if r["status"] == "IDLE":
            break
    print(json.dumps({"registry": reg.summary(), "queues": q.status(), "spent": spent}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
