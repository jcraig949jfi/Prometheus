"""SFE-03 -- H1 RELEVANT FAILURE TRANSPORT through the live engine (campaign 1).

    python -m archaeon.campaign1.sfe03 [--seeds 1 2 3] [--N 200 --G 60 --E 16] [--k 8] [--dry-run]

Three arms on the TARGET cell W1_d4 (K=1, D=1, delay 4):
  fresh      the target's own training episodes only (bounded search, no transported information)
  relevant   + k transported FAILURE EPISODES from a RELEVANT source (W1_d1: same K, D, ask kind,
             shorter delay) -- episodes on which the source's own final population FAILED, with
             the source world's expected answers (never the target's)
  random     + k transported failure episodes from a RANDOM-COMPATIBLE source (W7_K2: same grammar
             and syntax, different structure: two streams, ASK2 combine)
Relevance is RECOMPUTED here as a declared structural rule (knob equality on K, D, ask_kind),
never as a post-hoc label; the transported episodes are published as failure artifacts on the
engine by the source worlds and IMPORTED by the target world; the target's held-out family is
untouched by any transport. Primary: held-out competence per arm x seed at matched budget
(the transported episodes REPLACE k of the E training episodes each generation, so total
evaluations per generation are equal across arms).
"""
from __future__ import annotations

import argparse
import base64
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry.identity import RUNTIME_HASH              # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from         # noqa: E402

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.wse.economics import REGIMES                     # noqa: E402
from archaeon.wse import evolve as EV                          # noqa: E402
from archaeon.wse.evolve import evaluate, run_cell             # noqa: E402
from archaeon.wse.worlds import Episode, WorldSpec, episodes_for   # noqa: E402
from archaeon.campaign1.sfe01 import FOUNDRY_C1, CAMPAIGN_SEED, engine_client, sha   # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SFE-03"
TARGET = WorldSpec("W1_d4", delay=4, value_bits=4)
SOURCES = {"relevant": WorldSpec("W1_d1", delay=1, value_bits=4),
           "random": WorldSpec("W7_K2", K=2, ask_kind="ASK2", value_bits=4)}
ARMS = ["fresh", "relevant", "random"]


def relevance(src: WorldSpec, tgt: WorldSpec) -> dict:
    """Declared structural relevance: knob equality on the pressure-defining knobs."""
    keys = ("K", "D", "ask_kind", "ask_mode", "op_mode", "topology")
    same = {k: getattr(src, k) == getattr(tgt, k) for k in keys}
    return {"rule": "all of K,D,ask_kind,ask_mode,op_mode,topology equal", "same": same, "relevant": all(same.values())}


def source_failure_episodes(spec: WorldSpec, seed: int, N: int, G_: int, E: int, k: int) -> dict:
    """Run the source search; return k episodes of its LAST training family on which the
    final population's median organism failed (a failure INPUT set, source answers attached)."""
    res = run_cell(spec, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=G_, E=E, branch="cmp1-sfe03-src", rng_label="cmp1-sfe03-src", foundry=FOUNDRY_C1)
    eps = episodes_for(spec, CAMPAIGN_SEED, "train", (G_ - 1) * 100003 + seed, E)
    pop = sorted(res["final_population"], key=lambda z: -z["reward"])
    probe = pop[len(pop) // 2]["manifest"]
    failed = []
    for ep in eps:
        ev = evaluate(probe, [ep], rng_seed=3)
        if ev["reward"] < 1.0:
            failed.append({"ticks": ep.ticks, "expected": {str(k2): v for k2, v in ep.expected.items()},
                           "intervention_tick": ep.intervention_tick, "meta": {"cell": spec.name}})
    return {"episodes": failed[:k], "n_failed_of": [len(failed), len(eps)], "source_elite_reward": res["elite_eval"]["reward"]}


def run_arm(job: dict) -> dict:
    arm, seed = job["arm"], job["seed"]
    transported = [Episode(ticks=e["ticks"], expected={int(k): v for k, v in e["expected"].items()}, intervention_tick=e["intervention_tick"], meta=e["meta"])
                   for e in job["episodes"]]
    k = len(transported)
    orig = EV.episodes_for

    def patched(spec, cs, family, index, n):
        eps = orig(spec, cs, family, index, n)
        if family == "train" and k:
            return transported + eps[:max(0, n - k)]        # matched budget: k transported REPLACE k fresh
        return eps
    EV.episodes_for = patched
    try:
        t0 = time.time()
        res = run_cell(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=job["N"], G_=job["G"], E=job["E"], branch="cmp1-sfe03-common", rng_label="cmp1-sfe03-common", foundry=FOUNDRY_C1)
    finally:
        EV.episodes_for = orig
    ho = evaluate(res["elite"]["manifest"], orig(TARGET, CAMPAIGN_SEED, "heldout", seed, 48), rng_seed=7)
    return {"arm": arm, "seed": seed, "k": k, "competence_heldout": ho["reward"], "train_last": res["elite_eval"]["reward"],
            "first_solved_gen": next((t["gen"] for t in res["trace"] if t["best_reward"] >= 0.5), None),
            "persist": ho["persist"], "ops_per_episode": ho["ops_per_episode"], "trace_best": [t["best_reward"] for t in res["trace"]],
            "wall_s": round(time.time() - t0, 1), "elite_manifest": res["elite"]["manifest"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--G-source", type=int, default=60)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--procs", type=int, default=9)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run SFE-03")
    OUT.mkdir(parents=True, exist_ok=True)
    T = time.time()
    receipt: Dict = {"experiment": "SFE-03", "campaign_seed": CAMPAIGN_SEED, "workspace": ws, "runtime_hash": RUNTIME_HASH,
                     "engine_path": not a.dry_run, "timings": {}, "worlds": {}, "artifacts": {}, "imports": {}, "errors": [],
                     "relevance": {name: relevance(s, TARGET) for name, s in SOURCES.items()}, "k": a.k}
    c = None
    if not a.dry_run:
        t0 = time.time()
        c, _ = engine_client()
        sid = c.create_session("cmp1-sfe03"); gid = c.create_topology_group("cmp1-sfe03 failure transport")
        for name in SOURCES:
            w = c.create_world(sid, "cmp1-sfe03-source-%s" % name, sharing_policy="FAILURES_ONLY", topology_group=gid, seed_root=CAMPAIGN_SEED)
            c.start(w["world_id"]); receipt["worlds"]["source_" + name] = w["world_id"]
        w = c.create_world(sid, "cmp1-sfe03-target", sharing_policy="EXPLICIT_IMPORT_ONLY", topology_group=gid, seed_root=CAMPAIGN_SEED)
        c.start(w["world_id"]); receipt["worlds"]["target"] = w["world_id"]; tw = w["world_id"]
        receipt["session_id"] = sid; receipt["topology_group"] = gid
        receipt["hypothesis"] = c.hypothesis(tw, "Transported failure episodes from a structurally RELEVANT source raise held-out competence on W1_d4 "
                                                 "above fresh search at matched budget; random-compatible transport does not.")
        receipt["timings"]["startup_s"] = round(time.time() - t0, 2)

    t0 = time.time()
    with mp.Pool(processes=min(a.procs, 2 * len(a.seeds))) as pool:
        src = pool.starmap(source_failure_episodes, [(SOURCES[n], s, a.N, a.G_source, a.E, a.k) for n in SOURCES for s in a.seeds])
    packs = {}
    i = 0
    for n in SOURCES:
        for s in a.seeds:
            packs[(n, s)] = src[i]; i += 1
    receipt["timings"]["sources_s"] = round(time.time() - t0, 1)
    receipt["packs"] = {"%s_s%d" % k: {kk: v for kk, v in p.items() if kk != "episodes"} | {"n_episodes": len(p["episodes"])} for k, p in packs.items()}

    if c is not None:
        t0 = time.time()
        for (n, s), p in packs.items():
            b = json.dumps({"source": n, "seed": s, "episodes": p["episodes"], "relevance": receipt["relevance"][n]}, sort_keys=True).encode()
            art = c.artifact(receipt["worlds"]["source_" + n], "cmp1.h1.failure_episodes.v0", b, {"info_kind": "failure", "seed": s, "source": n}, expected_blob_hash=sha(b))
            receipt["artifacts"]["%s_s%d" % (n, s)] = art["artifact_id"]
            try:
                imp = c.import_artifact(tw, receipt["worlds"]["source_" + n], art["artifact_id"])
                content = c.artifact_content(tw, imp["artifact_id"])
                raw = base64.b64decode(content["content_b64"])
                packs[(n, s)] = dict(packs[(n, s)], episodes=json.loads(raw)["episodes"])       # the target RUNS with what it fetched back
                receipt["imports"]["%s_s%d" % (n, s)] = {"artifact_id": imp["artifact_id"], "origin": imp.get("origin"), "bytes": len(raw),
                                                        "hash_ok": sha(raw) == art["artifact_id"].replace("sha256:", "")}
            except Exception as e:                                   # noqa: BLE001
                receipt["errors"].append({"step": "import", "source": n, "seed": s, "error": repr(e)})
        receipt["timings"]["exchange_s"] = round(time.time() - t0, 2)

    jobs = []
    for s in a.seeds:
        jobs.append({"arm": "fresh", "seed": s, "episodes": [], "N": a.N, "G": a.G, "E": a.E})
        for n in SOURCES:
            jobs.append({"arm": n, "seed": s, "episodes": packs[(n, s)]["episodes"], "N": a.N, "G": a.G, "E": a.E})
    t0 = time.time()
    with mp.Pool(processes=min(a.procs, len(jobs))) as pool:
        rows = pool.map(run_arm, jobs)
    receipt["timings"]["targets_s"] = round(time.time() - t0, 1)

    if c is not None:
        t0 = time.time()
        for r in rows:
            try:
                exp = c.experiment(tw, {"experiment": "SFE-03", "arm": r["arm"], "seed": r["seed"], "k": r["k"], "N": a.N, "G": a.G, "E": a.E,
                                        "target": TARGET.knobs(), "relevance": receipt["relevance"].get(r["arm"]), "runtime_hash": RUNTIME_HASH})
                obs = c.observation(tw, exp["exp_id"], {"competence_heldout": r["competence_heldout"], "train_last": r["train_last"], "first_solved_gen": r["first_solved_gen"]},
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

    means = {arm: sum(r["competence_heldout"] for r in rows if r["arm"] == arm) / len(a.seeds) for arm in ARMS}
    receipt["effects"] = {"means": means, "relevant_minus_fresh": means["relevant"] - means["fresh"], "random_minus_fresh": means["random"] - means["fresh"],
                          "relevant_minus_random": means["relevant"] - means["random"],
                          "per_seed": {arm: [r["competence_heldout"] for r in rows if r["arm"] == arm] for arm in ARMS},
                          "footholds": {arm: sum(1 for r in rows if r["arm"] == arm and r["competence_heldout"] >= 0.5) for arm in ARMS}}
    receipt["timings"]["total_s"] = round(time.time() - T, 1)
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    (OUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"effects": receipt["effects"], "packs": receipt["packs"], "timings": receipt["timings"], "errors": receipt["errors"], "teardown": receipt.get("teardown")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
