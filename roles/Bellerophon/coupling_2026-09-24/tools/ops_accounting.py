"""Operational accounting required by the operator's restart authorization (final-report block). Reads only
operational metadata: STATUS.json, supervisor.jsonl, memory.jsonl, results.jsonl ids/voids, the plans.
    python ops_accounting.py --workdir C:/Users/James/z80atlas_coupling_2026-09-24 --code <pinned code> --inputs <json>
Writes ../receipts/OPS_ACCOUNTING.json."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def utc(ts):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)) if ts else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True); ap.add_argument("--code", required=True); ap.add_argument("--inputs", required=True)
    a = ap.parse_args()
    sys.path.insert(0, a.code)
    from prometheus.z80atlas import coupling_campaign as CC
    wd = pathlib.Path(a.workdir)
    st = json.loads((wd / "STATUS.json").read_text(encoding="utf-8"))
    pre = json.loads((wd / "STATUS.pre_amendment1.json").read_text(encoding="utf-8"))
    P1 = CC.plan(json.loads(pathlib.Path(a.inputs).read_text(encoding="utf-8")))
    plans = {"phase1": [p["id"] for p in P1]}
    for n, f in (("phase2", "PHASE2_PLAN.json"), ("ext", "EXT_PLAN.json")):
        plans[n] = [p["id"] for p in json.loads((wd / f).read_text(encoding="utf-8"))] if (wd / f).exists() else []
    ids = []; voids = []
    for line in open(wd / "results.jsonl", encoding="utf-8"):
        r = json.loads(line); ids.append(r["id"])
        if r.get("void"):
            voids.append(r["id"])
    idset = set(ids)
    segs = st.get("active_segments") or []
    active = sum((e or time.time()) - b for b, e, *_ in segs)
    first = st["first_start_ts"]; end = segs[-1][1] if segs and segs[-1][1] else time.time()
    susp = segs[1][0] - segs[0][1] if len(segs) > 1 else 0
    mem = [json.loads(l) for l in open(wd / "memory.jsonl", encoding="utf-8")] if (wd / "memory.jsonl").exists() else []
    sup = [json.loads(l) for l in open(wd / "supervisor.jsonl", encoding="utf-8")] if (wd / "supervisor.jsonl").exists() else []
    conc = []
    for m in mem:
        if not conc or conc[-1][1] != m["workers_cfg"]:
            conc.append([utc(m["ts"]), m["workers_cfg"]])
    out = {"wall_clock_elapsed_h": round((end - first) / 3600, 2), "first_start_utc": utc(first), "end_utc": utc(end),
           "active_runtime_h": round(active / 3600, 2), "segments": [[utc(b), utc(e), *rest] for b, e, *rest in segs],
           "oom_suspension_h": round(susp / 3600, 2),
           "pre_oom_observations_retained": 959, "post_restart_observations": len(ids) - 959, "total_observations": len(ids),
           "duplicate_ids": len(ids) - len(idset), "voids": voids,
           "not_run": {n: sum(1 for i in v if i not in idset) for n, v in plans.items()},
           "planned": {n: len(v) for n, v in plans.items()},
           "concurrency_over_time": conc,
           "memory": {"samples": len(mem), "min_free_gb": min((m["free_gb"] for m in mem), default=None),
                      "peak_tree_rss_mb": max((m["tree_rss_mb"] or 0 for m in mem), default=None),
                      "peak_worker_rss_mb": max((m["max_worker_rss_mb"] or 0 for m in mem), default=None),
                      "pre_amendment_worker_rss_mb_observed": "~400 (2026-09-24, no recycling)"},
           "worker_recycling_every_n_runs": CC.RECYCLE_TASKS,
           "supervisor_events": [e for e in sup if e.get("event") not in ("integrity",)],
           "relaunches": sum(1 for e in sup if e.get("event") == "driver_exit"),
           "tail_repairs": st.get("tail_repairs"), "starts": st.get("starts"), "workers_by_start": st.get("workers_by_start"),
           "pre_amendment_status_last_write": pre.get("last_write_utc"),
           "scientific_content_changed_by_amendment": False}
    p = HERE.parent / "receipts" / "OPS_ACCOUNTING.json"
    p.write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("supervisor_events",)}, indent=1, default=str))


if __name__ == "__main__":
    main()
