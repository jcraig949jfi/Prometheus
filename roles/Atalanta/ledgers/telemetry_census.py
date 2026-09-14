"""ATALANTA-04 evidence: regenerate the telemetry census from agora.intelligence_outputs.

Second recording channel for the Atalanta lifecycle, independent of the M1
filesystem artifact census that Aporia P47 read in August. Independent RECORD,
not an independent MEASUREMENT: both were written by the same daemon process in
the same tick, so a fault in the tick loop would corrupt both identically.

Usage (the resolved database must be the canonical store, M1):
    EW_DB_HOST=<m1> python roles/Atalanta/ledgers/telemetry_census.py

Writes roles/Atalanta/ledgers/telemetry_census_2026-09-11.md. Read-only:
this script issues SELECTs and nothing else.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / "telemetry_census_2026-09-11.md"

QUERIES = [
    ("stage_census_atalanta",
     "per-stage row counts and the real per-row timeline for this agent",
     """select stage, count(*) as n, count(distinct cycle_id) as cycles,
               min(finished_at) as first_row, max(finished_at) as last_row
        from agora.intelligence_outputs
        where stage ilike 'atalanta%' group by 1 order by 2 desc"""),
    ("alarm_census_fleet",
     "every anti-silence alarm row ever written, by agent",
     """select stage, count(*) as n,
               sum(case when success = false then 1 else 0 end) as fail_rows,
               min(finished_at) as first_row, max(finished_at) as last_row
        from agora.intelligence_outputs
        where stage ilike '%self_audit_null%' group by 1 order by 2 desc"""),
    ("dead_upstream_census_fleet",
     "every dead-upstream / drought row ever written, by agent",
     """select stage, count(*) as n, min(finished_at) as first_row,
               max(finished_at) as last_row
        from agora.intelligence_outputs
        where stage ilike '%upstream_not_found%' or stage ilike '%drought%'
        group by 1 order by 2 desc"""),
    ("alarm_error_field",
     "the error string carried by this agent's alarm rows",
     """select error, success, count(*) from agora.intelligence_outputs
        where stage = 'atalanta_self_audit_null' group by 1, 2"""),
]


def main() -> int:
    sys.path.insert(0, str(REPO))
    from evidence_wiki.ew import db as ewdb
    conn = ewdb.connect()
    cur = conn.cursor()
    cur.execute("select current_database(), inet_server_addr()")
    dbname, host = cur.fetchone()
    lines = ["# Atalanta telemetry census (raw rows for ATALANTA-04)", "",
             "Regenerate: `EW_DB_HOST=<m1> python roles/Atalanta/ledgers/telemetry_census.py`",
             "", "Source: `agora.intelligence_outputs` on the canonical store",
             "(database `{}`, server `{}`). Read-only SELECTs.".format(dbname, host), ""]
    for key, why, sql in QUERIES:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        lines += ["## {}".format(key), "", why, "", "```",
                  "SQL: " + " ".join(sql.split()), "",
                  " | ".join(cols)]
        for r in rows:
            lines.append(" | ".join("" if v is None else str(v) for v in r))
        lines += ["```", ""]
    cur.execute("select count(*) from agora.intelligence_outputs")
    lines += ["## table_size", "",
              "Rows in agora.intelligence_outputs at read time: {}".format(cur.fetchone()[0]), ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
