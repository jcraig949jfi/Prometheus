"""POST-HOC secondaries for E-BEL-MD, written after the frozen analysis and the merge review (tsk-bc42e48a52be,
tsk-def7523bd2f2). Labelled post-hoc; no frozen disposition depends on them.
- Q3 per-K acquisition rates (prereg s8 names them; the frozen md_analysis.py omitted them);
- LADDER1 previous-rung (ECHO) retention at the last checkpoint: over ALL ON runs (the frozen descriptive), and split
  by acquired vs not acquired;
- ops accounting from STATUS.json / supervisor.jsonl / memory.jsonl / per-run wall_s.
    python posthoc_secondaries.py <workdir> <out.json>
"""
import collections, json, pathlib, statistics as st, sys
wd = pathlib.Path(sys.argv[1])
R = [json.loads(l) for l in open(wd / "results.jsonl", encoding="utf-8")]
acq = lambda r: int(((r.get("competence") or {}).get("final_competent_sr") or 0) > 0)
out = {"about": "POST-HOC (labelled); not an endpoint"}
q3 = collections.defaultdict(lambda: [0, 0])
for r in R:
    if r["lane"] == "REPAIR" and not r.get("void"):
        q3[(r["K"], r["arm"])][0] += acq(r); q3[(r["K"], r["arm"])][1] += 1
out["Q3_repair_by_K"] = {"%s|%s" % k: {"k": v[0], "n": v[1]} for k, v in sorted(q3.items())}
ret = collections.defaultdict(list)
for r in R:
    if r["lane"] == "LADDER1" and r["arm"] == "ON" and r.get("checkpoints"):
        c = r["checkpoints"][-1]
        ret["acquired" if acq(r) else "not_acquired"].append((c.get("prev_rung_competent") or 0) / max(1, c["alive"]))
out["LADDER1_ON_ECHO_retention_last_checkpoint"] = {k: {"n": len(v), "mean": round(st.mean(v), 4)} for k, v in ret.items()}
S = json.loads((wd / "STATUS.json").read_text(encoding="utf-8"))
sup = [json.loads(l) for l in open(wd / "supervisor.jsonl", encoding="utf-8")]
M = [json.loads(l) for l in open(wd / "memory.jsonl", encoding="utf-8")]
w = [r["wall_s"] for r in R if "wall_s" in r]
out["ops"] = {"active_segments": S.get("active_segments"), "active_elapsed_s": S.get("active_elapsed_s"), "starts": S.get("starts"),
              "tail_repairs": S.get("tail_repairs"), "workers_by_start": S.get("workers_by_start"), "stopped_reason": S.get("stopped_reason"),
              "supervisor_events": [e["event"] for e in sup], "memory_samples": len(M), "min_free_gb": min(m["free_gb"] for m in M),
              "max_tree_rss_mb": max(m["tree_rss_mb"] or 0 for m in M), "max_worker_rss_mb": max(m["max_worker_rss_mb"] or 0 for m in M),
              "run_wall_s": {"mean": round(st.mean(w)), "max": max(w), "sum_cpu_h": round(sum(w) / 3600, 1)}}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
print(json.dumps({k: out[k] for k in ("Q3_repair_by_K", "LADDER1_ON_ECHO_retention_last_checkpoint")}, indent=1))
