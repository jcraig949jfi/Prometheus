#!/usr/bin/env python3
"""
Pollux settling query (Rhadamanthus as Keeper, 2026-09-11). Proposed by the Pollux Cleric
(CLERIC.md C-3 / C-8): the two readers of the lost kill_ledger (COMPONENT_DOSSIERS_2026-06-24.md:404,
P69) report a verdict split of 86 REJECTED / 39 PROMOTED / 161 UNVERIFIED; the on-tree code
replayed with a 95-tick v0.5 prefix (cleric_census_fit S2) gives 62 / 63 / 161. The second
channel (agora.intelligence_outputs, stage pollux_tick_complete) was written by the same daemon
in the same tick as the ledger, so its per-summary counts test which arithmetic the daemon
actually produced. Read-only SELECTs; no row is written.

Pre-registered predictions (CLERIC.md C-3):
  code wrote the ledger  -> 62 / 63 / 161 by verdict, and 95 rows before 2026-05-25 23:30 -04:00
  the two readers are right -> 86 / 39 / 161
Same caveat as intelligence_outputs_census.py: DUAL-RECORDED IS NOT INDEPENDENTLY VERIFIED;
a match settles what the daemon computed, not whether the computation was meaningful.

Usage: EW_DB_HOST=<host> python pollux_settling_query.py [--out result.json]
"""
import json, os, re, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4)))
import comms.api as api  # noqa: E402

BOUNDARY = "2026-05-25 23:30:00-04:00"
PRED_CODE = {"REJECTED": 62, "PROMOTED": 63, "UNVERIFIED": 161, "rows_before_boundary": 95}
PRED_READERS = {"REJECTED": 86, "PROMOTED": 39, "UNVERIFIED": 161}


def run(conn):
    cur = conn.cursor()
    cur.execute(
        "select output_summary, count(*), min(finished_at), max(finished_at) "
        "from agora.intelligence_outputs where stage ilike 'pollux%%' "
        "group by 1 order by min(finished_at)")
    rows = [{"output_summary": s, "n": n, "first": str(a), "last": str(b)} for s, n, a, b in cur.fetchall()]
    cur.execute(
        "select count(*) from agora.intelligence_outputs where stage ilike 'pollux%%' and finished_at < %s",
        (BOUNDARY,))
    before = cur.fetchone()[0]
    cur.execute(
        "select count(*) from agora.intelligence_outputs where stage ilike 'pollux%%'")
    total = cur.fetchone()[0]
    # per-tick ordering, to see the rotation and the v0.5 -> v0.6 transition directly
    cur.execute(
        "select finished_at, output_summary from agora.intelligence_outputs "
        "where stage ilike 'pollux%%' order by finished_at")
    ticks = [(str(t), s) for t, s in cur.fetchall()]
    by_verdict, by_pair, by_kp = {}, {}, {}
    for r in rows:
        s = r["output_summary"] or ""
        v = re.search(r"verdict=(\w+)", s)
        p = re.search(r"pair=(\S+)", s)
        k = re.search(r"kp=(\S+)", s)
        by_verdict[v.group(1) if v else "?"] = by_verdict.get(v.group(1) if v else "?", 0) + r["n"]
        by_pair[p.group(1) if p else "?"] = by_pair.get(p.group(1) if p else "?", 0) + r["n"]
        by_kp[k.group(1) if k else "?"] = by_kp.get(k.group(1) if k else "?", 0) + r["n"]
    # first tick per pair and the sequence of pairs over the first 120 ticks
    pair_seq = []
    for t, s in ticks:
        p = re.search(r"pair=(\S+)", s or "")
        pair_seq.append(p.group(1) if p else "?")
    # run-length encode the pair sequence
    rle = []
    for p in pair_seq:
        if rle and rle[-1][0] == p:
            rle[-1][1] += 1
        else:
            rle.append([p, 1])
    return {"script": "pollux_settling_query.py", "table": "agora.intelligence_outputs",
            "boundary": BOUNDARY, "total_rows": total, "rows_before_boundary": before,
            "by_output_summary": rows, "by_verdict": by_verdict, "by_pair": by_pair, "by_kill_pattern": by_kp,
            "pair_sequence_rle": rle, "tick_times_first_120": ticks[:120],
            "prediction_if_code_wrote_ledger": PRED_CODE, "prediction_if_readers_right": PRED_READERS,
            "caveat": "DUAL-RECORDED IS NOT INDEPENDENTLY VERIFIED: same daemon, same tick as the lost ledger."}


def main():
    out = None
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    conn = api.connect(require_schema=False)
    res = run(conn)
    print(json.dumps({k: v for k, v in res.items() if k != "tick_times_first_120"}, indent=1, default=str))
    if out:
        json.dump(res, open(out, "w", encoding="utf-8"), indent=1, default=str)


if __name__ == "__main__":
    main()
