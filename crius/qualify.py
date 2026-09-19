"""Qualification on frozen held-out partitions (charter s11) with the full control battery (s10).

Selects from a search run: the best candidate, random contemporaries from
the final iteration, and evenly spaced ancestors of the best; adds the
baselines. Every selected Player runs the full battery on every
qualification seed of suite heldout_v1, from an empty workspace (unless a
transplant control says otherwise). One battery receipt per (player, seed).

CLI: python -m crius.qualify --run RUN_ID --suite heldout_v1 [--top 3 --contemporaries 3 --ancestors 3 --workers 8]
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from multiprocessing import Pool

from . import baselines, evaluate, receipts, tasks as tasks_mod, vm
from .player import VMPlayer

_W = {}


def _init(cfg, suite):
    _W["cfg"] = cfg
    _W["tasks"] = {s: tasks_mod.make_lifetime(cfg, s, suite) for s in cfg["seeds"]["qualification"]}
    _W["suite"] = suite


def _job(args):
    label, spec, seed, parent = args
    cfg = _W["cfg"]
    if spec["kind"] == "vm":
        player = VMPlayer(vm.program_from_json(spec["program"]), name=label)
    else:
        player = baselines.make_baseline(spec["name"])
    tasks = _W["tasks"][seed]
    t0 = time.time()
    bat = evaluate.full_battery(player, tasks, cfg, seed=seed)
    meta = _W["meta"]
    rec = receipts.battery_receipt(meta, player, tasks, seed, _W["suite"], bat, wall_seconds=time.time() - t0,
                                   parent_hash=parent, run_id=_W["run_id"])
    rec["label"] = label
    rec["role"] = spec.get("role", "candidate")
    rec["search_iteration"] = spec.get("iteration")
    rec["search_fitness"] = spec.get("fitness")
    return rec


def load_candidates(run_dir: str) -> dict:
    out = {}
    with receipts.open_text(os.path.join(run_dir, "candidates.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            out[r["candidate_id"]] = r
    return out


def select(run_dir: str, top: int, contemporaries: int, ancestors: int, seed: int) -> list:
    cands = load_candidates(run_dir)
    best = receipts.read_json(os.path.join(run_dir, "best.json"))
    rng = random.Random("qualify:%d" % seed)
    chosen = []
    # top-N distinct by fitness among all evaluated candidates
    ranked = sorted(cands.values(), key=lambda r: (-r["fitness"], r["length"], r["candidate_id"]))
    for r in ranked[:top]:
        chosen.append(("top%d_%s" % (len(chosen) + 1, r["candidate_id"]), r, "top"))
    best_rec = cands[best["best"]["candidate_id"]]
    last_it = max(r["iteration"] for r in cands.values())
    pool = [r for r in cands.values() if r["iteration"] == last_it and r["candidate_id"] not in {c[1]["candidate_id"] for c in chosen}]
    for r in rng.sample(pool, min(contemporaries, len(pool))):
        chosen.append(("contemp_%s" % r["candidate_id"], r, "contemporary"))
    chain = []
    cur = best_rec
    while cur is not None:
        chain.append(cur)
        cur = cands.get(cur["parent_id"]) if cur["parent_id"] else None
    chain = chain[1:]  # exclude best itself
    if chain:
        idx = sorted({int(round(i * (len(chain) - 1) / max(1, ancestors - 1))) for i in range(min(ancestors, len(chain)))})
        for i in idx:
            r = chain[i]
            chosen.append(("ancestor%d_it%d_%s" % (len(chain) - i, r["iteration"], r["candidate_id"]), r, "ancestor"))
    return chosen


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="run id under crius/runs (or a path)")
    ap.add_argument("--suite", default="heldout_v1")
    ap.add_argument("--config", default=None)
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--contemporaries", type=int, default=3)
    ap.add_argument("--ancestors", type=int, default=3)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--no-baselines", action="store_true")
    ap.add_argument("--select-seed", type=int, default=1)
    args = ap.parse_args(argv)
    run_dir = args.run if os.path.isdir(args.run) else os.path.join("crius", "runs", args.run)
    run_meta = receipts.read_json(os.path.join(run_dir, "RUN_META.json"))
    config_path = args.config or run_meta["config_path"]
    cfg = receipts.load_config(config_path)
    assert receipts.config_hash(cfg) == run_meta["config_hash"], "config hash differs from the search run's"
    out = os.path.join(run_dir, "qualify_%s" % args.suite)
    os.makedirs(out, exist_ok=True)
    meta = receipts.run_meta(cfg, config_path)
    meta["search_run_meta"] = {k: run_meta[k] for k in ("run_id", "arm", "iterations", "code_commit", "config_hash") if k in run_meta}
    jobs = []
    chosen = select(run_dir, args.top, args.contemporaries, args.ancestors, args.select_seed)
    for label, r, role in chosen:
        spec = {"kind": "vm", "program": r["program"], "role": role, "iteration": r["iteration"], "fitness": r["fitness"]}
        for seed in cfg["seeds"]["qualification"]:
            jobs.append((label, spec, seed, r["parent_id"]))
    if not args.no_baselines:
        for name in baselines.ALL_NAMES:
            for seed in cfg["seeds"]["qualification"]:
                jobs.append((name, {"kind": "python", "name": name, "role": "baseline"}, seed, None))
    _W["meta"] = meta
    _W["run_id"] = run_meta.get("run_id")

    def init():
        _init(cfg, args.suite)
        _W["meta"] = meta
        _W["run_id"] = run_meta.get("run_id")

    t0 = time.time()
    if args.workers > 1:
        with Pool(args.workers, initializer=_pool_init, initargs=(cfg, args.suite, meta, run_meta.get("run_id"))) as pool:
            recs = pool.map(_job, jobs, chunksize=1)
    else:
        init()
        recs = [_job(j) for j in jobs]
    summary = []
    for rec in recs:
        path = os.path.join(out, "%s_seed%d.json" % (rec["label"], rec["seed"]))
        receipts.write_json(path, rec)
        summary.append(summarize(rec))
        print(receipts.one_line(rec["label"][:13], rec["seed"], _bat_view(rec), rec["wall_seconds"]))
    receipts.write_json(os.path.join(out, "SUMMARY.json"), {"meta": meta, "rows": summary, "elapsed_s": round(time.time() - t0, 1),
                                                            "selection": [(l, r["candidate_id"], role) for l, r, role in chosen]})
    print("qualification receipts:", out)
    return 0


def _pool_init(cfg, suite, meta, run_id):
    _init(cfg, suite)
    _W["meta"] = meta
    _W["run_id"] = run_id


def _bat_view(rec):
    return {"ACCUMULATED": rec["conditions"]["ACCUMULATED"], "FRESH": rec["conditions"]["FRESH"],
            "WORKSPACE_RESET": rec["conditions"]["WORKSPACE_RESET"], "WORKSPACE_SCRAMBLED": rec["conditions"]["WORKSPACE_SCRAMBLED"],
            "reuse_gain": rec["reuse_gain"], "causal": rec["causal"]}


def summarize(rec: dict) -> dict:
    c = rec["conditions"]
    cz = rec["causal"]
    m = lambda k: c[k]["metrics"]
    acc = m("ACCUMULATED")
    stage_gain = {}
    for stage in ("A", "B", "C", "D", "E"):
        idx = [i for i, t in enumerate(rec["tasks"]) if t["stage"] == stage]
        stage_gain[stage] = round(sum(rec["reuse_gain"][i] for i in idx), 2)
    fam_success = {}
    for t, r in zip(rec["tasks"], c["ACCUMULATED"]["task_results"]):
        f = fam_success.setdefault(t["family"], [0, 0, 0.0])
        f[0] += 1
        f[1] += 1 if r["success"] else 0
        f[2] += r["interactions_used"]
    return {
        "label": rec["label"], "role": rec["role"], "candidate_hash": rec["candidate_hash"], "seed": rec["seed"],
        "search_iteration": rec.get("search_iteration"), "search_fitness": rec.get("search_fitness"),
        "eff": {k: m(k)["C0_EFFICIENCY"] for k in ("ACCUMULATED", "FRESH", "WORKSPACE_RESET", "WORKSPACE_SCRAMBLED")},
        "successes": {k: m(k)["successes"] for k in ("ACCUMULATED", "FRESH", "WORKSPACE_RESET", "WORKSPACE_SCRAMBLED")},
        "interactions": {k: m(k)["interactions_total"] for k in ("ACCUMULATED", "FRESH", "WORKSPACE_RESET", "WORKSPACE_SCRAMBLED")},
        "mean_cost": {k: m(k)["mean_cost"] for k in ("ACCUMULATED", "FRESH", "WORKSPACE_RESET", "WORKSPACE_SCRAMBLED")},
        "late_early_acc": acc["late_early_ratio_by_depth"],
        "late_early_fresh": m("FRESH")["late_early_ratio_by_depth"],
        "by_stage_acc": {k: v["mean_cost"] for k, v in acc["by_stage"].items()},
        "by_stage_fresh": {k: v["mean_cost"] for k, v in m("FRESH")["by_stage"].items()},
        "reuse_gain_total": round(sum(rec["reuse_gain"]), 2),
        "reuse_gain_by_stage": stage_gain,
        "family_success": {k: [v[0], v[1], v[2]] for k, v in fam_success.items()},
        "blocks_created": acc["blocks_created_total"], "artifacts_invoked": acc["artifacts_invoked_total"],
        "workspace_bytes_final": c["ACCUMULATED"]["workspace_history"][-1]["bytes"],
        "causal_mean_cost": {k: cz[k]["mean_cost"] for k in ("ACCUMULATED_remainder", "ARTIFACT_TRANSPLANT", "FULL_WORKSPACE_TRANSPLANT",
                                                             "CODE_ONLY", "COMPUTE_MATCHED", "STORAGE_MATCHED") if k in cz}
                            | ({"ARTIFACT_ABLATION_ALL": cz["ARTIFACT_ABLATION_ALL"]["mean_cost"]} if "ARTIFACT_ABLATION_ALL" in cz else {}),
        "causal_interactions": {k: cz[k]["interactions_total"] for k in ("ACCUMULATED_remainder", "ARTIFACT_TRANSPLANT", "FULL_WORKSPACE_TRANSPLANT",
                                                                         "CODE_ONLY", "COMPUTE_MATCHED", "STORAGE_MATCHED") if k in cz},
        "blocks_at_snapshot": len(cz["blocks_at_snapshot"]),
        "per_block_ablation_delta": {k: round(v["mean_cost"] - cz["ACCUMULATED_remainder"]["mean_cost"], 3) for k, v in cz["ARTIFACT_ABLATION"].items()},
        "replay_hash_acc": c["ACCUMULATED"]["replay_hash"],
        "wall_seconds": round(rec["wall_seconds"], 2),
    }


if __name__ == "__main__":
    raise SystemExit(main())
