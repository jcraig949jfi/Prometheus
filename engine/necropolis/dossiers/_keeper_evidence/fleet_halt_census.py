#!/usr/bin/env python3
"""
When did each May-fleet agent last write to its second channel? (Rhadamanthus, 2026-09-11)

Read-only SELECTs over agora.intelligence_outputs (stage prefix = agent) and
agora.agent_heartbeats. Purpose: test whether the trial graves (Pollux, Erebos) stopped
individually or with the fleet. Same caveat as intelligence_outputs_census.py: rows are
self-reports by the daemons (dual-recorded, single-mechanism).

Usage: python fleet_halt_census.py [--out result.json]
"""
import json, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4)))
import comms.api as api  # noqa: E402


def main():
    out = None
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    conn = api.connect(require_schema=False)
    cur = conn.cursor()
    cur.execute("select split_part(stage,'_',1), count(*), min(finished_at), max(finished_at) "
                "from agora.intelligence_outputs group by 1 order by max(finished_at)")
    last = [{"prefix": p, "rows": n, "first": str(a), "last": str(b)} for p, n, a, b in cur.fetchall()]
    cur.execute("select agent_name, status, last_heartbeat from agora.agent_heartbeats order by last_heartbeat")
    hb = [{"agent": a, "status": s, "last_heartbeat": str(t)} for a, s, t in cur.fetchall()]
    # bucket last-activity by day to expose halt waves
    waves = defaultdict(list)
    for r in last:
        waves[r["last"][:10]].append(r["prefix"])
    res = {"last_activity_by_stage_prefix": last, "heartbeats": hb,
           "last_activity_day_buckets": {k: sorted(v) for k, v in sorted(waves.items())},
           "note": "a prefix is the first '_' token of stage; 'machine'/'observability'/'agent' are shared telemetry stages, not agents"}
    print(json.dumps(res, indent=1, default=str))
    if out:
        json.dump(res, open(out, "w", encoding="utf-8"), indent=1, default=str)


if __name__ == "__main__":
    main()
