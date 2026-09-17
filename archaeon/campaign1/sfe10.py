"""SFE-10 -- PRODUCER-CONSUMER SPECIALIZATION through the live engine (campaign 1).

    python -m archaeon.campaign1.sfe10 [--seeds 1 2 3] [--N 200 --G 60 --E 16] [--dry-run]

Matched TOTAL resource envelope: B = N x G generations of E episodes on the target W2_K2.
  mono        one search spends all of B on the target
  pc_p        PRODUCERS spend a share p of B on source cells (W0 and W1_d1, half each) and
              PUBLISH their final elites as artifacts on the engine (a producer world each,
              FULLY_SHARED); the CONSUMER imports and fetches them, pays explicit
              COMMUNICATION and STORAGE costs in generations, and spends the remainder on the
              target seeded from the fetched artifacts
  pc_p_noex   the same producer spend with NO exchange (the consumer gets random generation 0):
              isolates the artifact effect from the budget lost to producers
Costs (declared): communication = ceil(bytes_transferred / 4096) generations; storage =
0.5 generation per artifact held; both subtracted from the consumer's generations.
Primary: held-out competence on the target per arm x seed at equal total generations;
footholds; first-solved generation. Common random numbers.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import multiprocessing as mp
import sys
import time
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import generate as G                      # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH              # noqa: E402

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.wse.economics import REGIMES                     # noqa: E402
from archaeon.wse.evolve import evaluate, run_cell             # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for        # noqa: E402
from archaeon.campaign1.sfe01 import FOUNDRY_C1, CAMPAIGN_SEED, engine_client, sha   # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SFE-10"
TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
SOURCES = [WorldSpec("W0", value_bits=4), WorldSpec("W1_d1", delay=1, value_bits=4)]
SHARES = [0.2, 0.4]
COMM_BYTES_PER_GEN = 4096
STORAGE_GEN_PER_ARTIFACT = 0.5


def run_producer(job: dict) -> dict:
    spec, seed, N, G_, E = job["spec"], job["seed"], job["N"], job["G"], job["E"]
    res = run_cell(spec, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=G_, E=E, branch="cmp1-sfe10-prod", foundry=FOUNDRY_C1)
    return {"source": spec.name, "seed": seed, "G": G_, "elite_reward": res["elite_eval"]["reward"],
            "manifests": [e["manifest"] for e in res["final_elites"]]}


def run_consumer(job: dict) -> dict:
    arm, seed, N, G_, E = job["arm"], job["seed"], job["N"], job["G"], job["E"]
    init = None
    if job.get("seed_manifests"):
        init = [G.organism_record(m, None, 0) for m in job["seed_manifests"]]
        fm = dict(FOUNDRY_C1); fm["seed"] = 1010 + seed; fm["n"] = max(0, N - len(init))
        if fm["n"]:
            init = init + G.generate(fm)
    t0 = time.time()
    res = run_cell(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=max(1, G_), E=E, init_pop=init, branch="cmp1-sfe10-common", foundry=FOUNDRY_C1)
    ho = evaluate(res["elite"]["manifest"], episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48), rng_seed=7)
    return {"arm": arm, "seed": seed, "consumer_G": G_, "competence_heldout": ho["reward"], "train_last": res["elite_eval"]["reward"],
            "first_solved_gen": next((t["gen"] for t in res["trace"] if t["best_reward"] >= 0.5), None), "persist": ho["persist"],
            "trace_best": [t["best_reward"] for t in res["trace"]], "wall_s": round(time.time() - t0, 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run SFE-10")
    OUT.mkdir(parents=True, exist_ok=True)
    T = time.time()
    receipt: Dict = {"experiment": "SFE-10", "campaign_seed": CAMPAIGN_SEED, "workspace": ws, "runtime_hash": RUNTIME_HASH,
                     "engine_path": not a.dry_run, "timings": {}, "worlds": {}, "artifacts": {}, "imports": {}, "errors": [],
                     "envelope": {"N": a.N, "G_total": a.G, "E": a.E, "shares": SHARES, "comm_bytes_per_gen": COMM_BYTES_PER_GEN,
                                  "storage_gen_per_artifact": STORAGE_GEN_PER_ARTIFACT}, "costs": {}}
    c = None
    if not a.dry_run:
        t0 = time.time(); c, _ = engine_client()
        sid = c.create_session("cmp1-sfe10"); gid = c.create_topology_group("cmp1-sfe10 producer-consumer")
        for s in SOURCES:
            w = c.create_world(sid, "cmp1-sfe10-producer-%s" % s.name, sharing_policy="FULLY_SHARED", topology_group=gid, seed_root=CAMPAIGN_SEED)
            c.start(w["world_id"]); receipt["worlds"]["producer_" + s.name] = w["world_id"]
        w = c.create_world(sid, "cmp1-sfe10-consumer", sharing_policy="EXPLICIT_IMPORT_ONLY", topology_group=gid, seed_root=CAMPAIGN_SEED)
        c.start(w["world_id"]); receipt["worlds"]["consumer"] = w["world_id"]; cw = w["world_id"]
        receipt["session_id"] = sid; receipt["topology_group"] = gid
        receipt["hypothesis"] = c.hypothesis(cw, "Under a matched total generation budget with explicit communication and storage costs, producers on source "
                                                 "cells plus a consumer seeded from their artifacts reach higher held-out competence on W2_K2 than a monolithic "
                                                 "search of the same total budget; the no-exchange control separates the artifact effect from the producer spend.")
        receipt["timings"]["startup_s"] = round(time.time() - t0, 2)
    # producers (one run per source x share x seed)
    pjobs = []
    for p in SHARES:
        gp = max(1, int(round(a.G * p / len(SOURCES))))
        for s in a.seeds:
            for spec in SOURCES:
                pjobs.append({"share": p, "spec": spec, "seed": s, "N": a.N, "G": gp, "E": a.E})
    t0 = time.time()
    with mp.Pool(processes=min(a.procs, len(pjobs))) as pool:
        prods = pool.map(run_producer, pjobs)
    receipt["timings"]["producers_s"] = round(time.time() - t0, 1)
    pres = {}
    for j, r in zip(pjobs, prods):
        pres[(j["share"], j["seed"], j["spec"].name)] = r
    # publish + import + fetch (the consumer runs with the bytes it fetched; costs from the bytes)
    seeds_for: Dict[tuple, List[dict]] = {}
    for p in SHARES:
        for s in a.seeds:
            mans, nbytes, narts = [], 0, 0
            for spec in SOURCES:
                r = pres[(p, s, spec.name)]
                if c is not None:
                    try:
                        b = json.dumps({"source": spec.name, "share": p, "seed": s, "manifests": r["manifests"], "elite_reward": r["elite_reward"]}, sort_keys=True).encode()
                        art = c.artifact(receipt["worlds"]["producer_" + spec.name], "cmp1.pc.producer_elites.v0", b, {"info_kind": "success", "seed": s, "share": p},
                                         expected_blob_hash=sha(b))
                        imp = c.import_artifact(cw, receipt["worlds"]["producer_" + spec.name], art["artifact_id"])
                        content = c.artifact_content(cw, imp["artifact_id"]); raw = base64.b64decode(content["content_b64"])
                        mans.extend(json.loads(raw)["manifests"]); nbytes += len(raw); narts += 1
                        receipt["artifacts"]["p%s_s%d_%s" % (p, s, spec.name)] = art["artifact_id"]
                        receipt["imports"]["p%s_s%d_%s" % (p, s, spec.name)] = {"artifact_id": imp["artifact_id"], "bytes": len(raw),
                                                                                  "hash_ok": sha(raw) == str(art.get("blob_hash", "")).replace("sha256:", "")}
                    except Exception as e:                           # noqa: BLE001
                        receipt["errors"].append({"step": "exchange", "share": p, "seed": s, "source": spec.name, "error": repr(e)})
                else:
                    b = json.dumps({"manifests": r["manifests"]}).encode(); mans.extend(r["manifests"]); nbytes += len(b); narts += 1
            comm = math.ceil(nbytes / COMM_BYTES_PER_GEN); store = STORAGE_GEN_PER_ARTIFACT * narts
            gp = max(1, int(round(a.G * p / len(SOURCES)))) * len(SOURCES)
            receipt["costs"]["p%s_s%d" % (p, s)] = {"producer_generations": gp, "bytes": nbytes, "artifacts": narts, "comm_generations": comm,
                                                  "storage_generations": store, "consumer_generations": a.G - gp - comm - store}
            seeds_for[(p, s)] = mans
    cjobs = []
    for s in a.seeds:
        cjobs.append({"arm": "mono", "seed": s, "N": a.N, "G": a.G, "E": a.E})
        for p in SHARES:
            cost = receipt["costs"]["p%s_s%d" % (p, s)]
            gcons = int(math.floor(cost["consumer_generations"]))
            cjobs.append({"arm": "pc_%g" % p, "seed": s, "N": a.N, "G": gcons, "E": a.E, "seed_manifests": seeds_for[(p, s)]})
            cjobs.append({"arm": "pc_%g_noex" % p, "seed": s, "N": a.N, "G": a.G - cost["producer_generations"], "E": a.E})
    t0 = time.time()
    with mp.Pool(processes=min(a.procs, len(cjobs))) as pool:
        rows = pool.map(run_consumer, cjobs)
    receipt["timings"]["consumers_s"] = round(time.time() - t0, 1)
    if c is not None:
        t0 = time.time()
        for r in rows:
            try:
                exp = c.experiment(cw, {"experiment": "SFE-10", "arm": r["arm"], "seed": r["seed"], "consumer_G": r["consumer_G"], "envelope": receipt["envelope"]})
                obs = c.observation(cw, exp["exp_id"], {"competence_heldout": r["competence_heldout"], "first_solved_gen": r["first_solved_gen"], "consumer_G": r["consumer_G"]},
                                    "SURVIVED" if r["competence_heldout"] >= 0.5 else "FALSIFIED")
                r["engine"] = {"exp_id": exp["exp_id"], "obs_id": obs}
            except Exception as e:                                   # noqa: BLE001
                receipt["errors"].append({"step": "record", "arm": r["arm"], "seed": r["seed"], "error": repr(e)})
        receipt["timings"]["records_s"] = round(time.time() - t0, 2)
        t0 = time.time(); td = {}
        for name, wid in receipt["worlds"].items():
            try:
                c.terminate(wid); td[name] = c.get_world(wid).get("state")
            except Exception as e:                                   # noqa: BLE001
                td[name] = "ERROR " + repr(e)
        receipt["teardown"] = td; receipt["timings"]["teardown_s"] = round(time.time() - t0, 2)
    arms = sorted({r["arm"] for r in rows}, key=lambda z: (z != "mono", z))
    summ = {arm: {"heldout": [round(r["competence_heldout"], 3) for r in rows if r["arm"] == arm], "consumer_G": [r["consumer_G"] for r in rows if r["arm"] == arm],
                  "footholds": sum(1 for r in rows if r["arm"] == arm and r["competence_heldout"] >= 0.5),
                  "first_solved_gen": [r["first_solved_gen"] for r in rows if r["arm"] == arm]} for arm in arms}
    receipt["producers"] = {"%s_s%d_%s" % k: {"G": v["G"], "elite_reward": v["elite_reward"]} for k, v in pres.items()}
    receipt["summary"] = summ
    receipt["timings"]["total_s"] = round(time.time() - T, 1)
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    (OUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"summary": summ, "costs": receipt["costs"], "producers": receipt["producers"], "timings": receipt["timings"], "errors": receipt["errors"],
                      "teardown": receipt.get("teardown")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
