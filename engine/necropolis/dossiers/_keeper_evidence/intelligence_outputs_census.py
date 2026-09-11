#!/usr/bin/env python3
"""
Second-channel census of the trial graves in agora.intelligence_outputs (Rhadamanthus, 2026-09-11).

Instrument handed over by Atalanta (comms #98): every May-era template agent wrote a second
recording channel into agora.intelligence_outputs on the canonical store. Read-only SELECTs.
Run with EW_DB_HOST pointed at the host that holds the comms schema (the resolver in
comms.api.connect fails closed otherwise). No row is written.

CAVEAT that travels with every number here: DUAL-RECORDED IS NOT INDEPENDENTLY VERIFIED.
These rows and the filesystem artifacts the August autopsies read were written by the same
daemon in the same tick. A match raises provenance to "dual-recorded, single-mechanism", not
to "verified". Use the rows to test a prediction about a mechanism, not to confirm a count.

Traps (Atalanta #98): started_at is a session constant, use finished_at; there is no
created_at; agent is usually NULL, filter on stage ILIKE '<name>%'.

Usage: python intelligence_outputs_census.py [--out result.json]
"""
import json, os, sys

# repo root = four levels up (dossiers/_keeper_evidence -> dossiers -> necropolis -> engine -> root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4)))
import comms.api as api  # noqa: E402

GRAVES = ("pollux", "erebos", "nous")


def census(conn):
    cur = conn.cursor()
    out = {"table": "agora.intelligence_outputs", "graves": {}}
    cur.execute("select count(*) from agora.intelligence_outputs")
    out["total_rows"] = cur.fetchone()[0]
    for g in GRAVES:
        cur.execute(
            "select stage, success, count(*), min(finished_at), max(finished_at) "
            "from agora.intelligence_outputs where stage ilike %s or agent ilike %s "
            "group by stage, success order by stage, success", (g + "%", g + "%"))
        stages = [{"stage": s, "success": ok, "n": n, "first": str(a), "last": str(b)} for s, ok, n, a, b in cur.fetchall()]
        cur.execute(
            "select count(*), min(finished_at), max(finished_at), count(distinct run_id), count(distinct cycle_id) "
            "from agora.intelligence_outputs where stage ilike %s or agent ilike %s", (g + "%", g + "%"))
        n, a, b, runs, cycles = cur.fetchone()
        cur.execute(
            "select output_summary from agora.intelligence_outputs where stage ilike %s "
            "order by finished_at limit 3", (g + "%",))
        samples = [r[0][:300] if r[0] else None for r in cur.fetchall()]
        cur.execute(
            "select count(distinct output_summary) from agora.intelligence_outputs where stage ilike %s", (g + "%",))
        distinct_summaries = cur.fetchone()[0]
        cur.execute("select agent_name, status, last_heartbeat from agora.agent_heartbeats where agent_name ilike %s", (g + "%",))
        hb = [{"agent": x, "status": s, "last_heartbeat": str(t)} for x, s, t in cur.fetchall()]
        out["graves"][g] = {"rows": n, "first_finished_at": str(a), "last_finished_at": str(b),
                            "distinct_run_id": runs, "distinct_cycle_id": cycles,
                            "distinct_output_summary": distinct_summaries,
                            "stages": stages, "first_three_summaries": samples, "heartbeats": hb}
    return out


def main():
    out = None
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    conn = api.connect(require_schema=False)
    res = census(conn)
    print(json.dumps(res, indent=1, default=str))
    if out:
        json.dump(res, open(out, "w", encoding="utf-8"), indent=1, default=str)


if __name__ == "__main__":
    main()
