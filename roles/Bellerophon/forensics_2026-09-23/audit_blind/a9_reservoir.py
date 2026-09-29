"""Replay the flagged RESERVOIR_CROSSED_MOAT treatment runs and attribute tail 'solvers' to niches/tasks."""
import json, os, sys, collections
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import grammar as G
from prometheus.z80atlas.world import World
W = r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs = [json.loads(l) for l in open(os.path.join(W, "runs.jsonl"), encoding="utf-8")]
byf = collections.defaultdict(list)
for r in runs: byf[r["family"]].append(r)
flags = [f for f in json.load(open(os.path.join(W, "flags.json"))) if f["flag"] == "RESERVOIR_CROSSED_MOAT"]
for f in flags:
    solved = [r for r in byf[f["family"]] if (r["summary"].get("solvers_tail") or 0) >= 1]
    r = solved[0]
    cj = json.load(open(os.path.join(r["dir"], "config.json")))
    cfg = G.to_config(cj["vec"], cj["ticks"], cj["cells"], cj["budget"], tuple(cj["init_tapes"]))
    w = World(cfg, cj["seed"])
    tail = collections.Counter(); n = 0
    for t in range(cfg.ticks):
        w.step()
        if t >= cfg.ticks - 20:
            for o in w.cells:
                if o is not None and o.score_ema >= 0.85:
                    tail[(o.niche, w.env.task_for(o.niche).kind)] += 1
            n += 1
        if not any(o is not None for o in w.cells): break
    per = {"niche%d:%s" % k: round(v / max(1, n), 2) for k, v in sorted(tail.items())}
    print(r["id"], r["kind"], cj["vec"]["task"], cj["vec"]["scoring"], cj["vec"]["init"], "stored solvers_tail", r["summary"]["solvers_tail"], "| replayed tail solvers by niche/task", per)
