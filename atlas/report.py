"""Coverage / manifest report (ASCII, 80-column friendly) and identity
collision detection. `python -m atlas report --out <file>`."""
from __future__ import annotations

import json
from typing import List

from atlas import db
from atlas.harvest import common as C

EXAMPLE_QUERIES = [
    ("Every descendant of Campaign 4's damage census (C4-01), across engines",
     "SELECT depth, ent_type, ent_key, via FROM atlas.descendants('experiment','archaeon.campaign/cmp4:C4-01') "
     "ORDER BY depth, ent_key LIMIT 12"),
    ("Scientific edges that cross engines (NPE <-> SFE <-> Vivarium)",
     "SELECT summary FROM atlas.signal WHERE rule_id='R09-cross-engine-lineage' ORDER BY summary LIMIT 8"),
    ("Experiments whose conclusion changed across attempts",
     "SELECT subject_key, summary FROM atlas.signal WHERE rule_id='R04-conclusion-changed-across-attempts' "
     "ORDER BY subject_key LIMIT 6"),
    ("Interpretations superseded or still open, with the verbatim text",
     "SELECT subject_key, status, left(text_verbatim, 110) FROM atlas.conclusion "
     "WHERE status IN ('SUPERSEDED_INTERPRETATION','UNRESOLVED') ORDER BY 1"),
    ("Which host / engine instance executed what (attempts)",
     "SELECT e.engine_id, a.host_id, coalesce(a.engine_instance_key,'-') ei, count(*) FROM atlas.attempt a "
     "JOIN atlas.experiment e USING (experiment_key) GROUP BY 1,2,3 ORDER BY 4 DESC LIMIT 10"),
    ("Where the evidence for one experiment lives (C5-03)",
     "SELECT l.role, s.visibility, s.uri FROM atlas.source_link l JOIN atlas.source s USING (source_id) "
     "WHERE l.entity_key='archaeon.campaign/cmp5:C5-03' ORDER BY 1 LIMIT 14"),
]


def q(cur, sql, args=None):
    cur.execute(sql, args)
    return cur.fetchall()


def detect_collisions(cur, harvest_id=None) -> int:
    """Same native id under more than one experiment key, or a key whose
    sources disagree with its path: recorded, never auto-merged. Rebuilt
    from scratch each pass (OPEN rows only); field conflicts that are the
    same instant in two spellings are discarded first (db._instant)."""
    cur.execute("""DELETE FROM atlas.field_conflict WHERE field IN ('started_at','finished_at')
                   AND value_kept::timestamptz = value_offered::timestamptz""")
    cur.execute("DELETE FROM atlas.identity_collision WHERE status = 'OPEN'")
    rows = q(cur, """SELECT native_id, jsonb_agg(jsonb_build_object('key', experiment_key, 'engine', engine_id))
                     FROM atlas.experiment GROUP BY native_id HAVING count(*) > 1""")
    out = [{"collision_key": C.h16("native", n, "experiment"), "namespace": "experiment.native_id", "native_id": n,
            "entity_type": "experiment", "candidates": c,
            "note": "one native id, several experiment keys (different campaigns/programs); not merged"}
           for n, c in rows]
    rows = q(cur, """SELECT subject_key, value_text FROM atlas.fact WHERE status='CONTRADICTORY'""")
    out += [{"collision_key": C.h16("contradictory", k, v), "namespace": "fact.CONTRADICTORY", "native_id": k,
             "entity_type": "experiment", "candidates": [{"value": v}],
             "note": "a source field disagrees with the identity Atlas derived (e.g. RECEIPT.campaign vs path)"}
            for k, v in rows]
    rows = q(cur, "SELECT entity_type, entity_key, field, value_kept, value_offered FROM atlas.field_conflict")
    out += [{"collision_key": C.h16("field", t, k, f, b), "namespace": "field_conflict." + f, "native_id": k,
             "entity_type": t, "candidates": [{"kept": a}, {"offered": b}], "note": "two harvests disagree"}
            for t, k, f, a, b in rows]
    if out and harvest_id:
        db.upsert(cur, "atlas.identity_collision", out, ["collision_key"], harvest_id, replace=("candidates", "note"))
    return len(out)


def counts(cur) -> List[tuple]:
    one = lambda sql: q(cur, sql)[0][0]
    return [
        ("engines (registered / with experiments)", "{} / {}".format(one("SELECT count(*) FROM atlas.engine"),
                                                               one("SELECT count(DISTINCT engine_id) FROM atlas.experiment"))),
        ("hosts registered", one("SELECT count(*) FROM atlas.host")),
        ("engine instances", one("SELECT count(*) FROM atlas.engine_instance")),
        ("campaigns / programs", one("SELECT count(*) FROM atlas.campaign")),
        ("experiments", one("SELECT count(*) FROM atlas.experiment")),
        ("attempts", one("SELECT count(*) FROM atlas.attempt")),
        ("execution segments", one("SELECT count(*) FROM atlas.segment")),
        ("ideas (scientific-lineage nodes)", one("SELECT count(*) FROM atlas.idea")),
        ("source pointers", one("SELECT count(*) FROM atlas.source")),
        ("structured facts (RAN/OBSERVED/CONCLUDED)", "{} ({})".format(
            one("SELECT count(*) FROM atlas.fact"),
            " / ".join("{}".format(n) for (n,) in q(cur, """SELECT count(*) FROM atlas.fact GROUP BY layer
                                                          ORDER BY array_position(ARRAY['RAN','OBSERVED','CONCLUDED'], layer)""")))),
        ("conclusions (verbatim / by pointer)", one("SELECT count(*) FROM atlas.conclusion")),
        ("edges (all typed relations)", one("SELECT count(*) FROM atlas.edge")),
        ("  of which lineage (EXECUTION+SCIENTIFIC)", one("SELECT count(*) FROM atlas.edge WHERE lineage_kind IN ('EXECUTION','SCIENTIFIC')")),
        ("defects", one("SELECT count(*) FROM atlas.defect")),
        ("git commits classified", one("SELECT count(*) FROM atlas.git_commit")),
        ("unresolved: dangling edge endpoints", one("SELECT count(*) FROM atlas.v_edge_dangling WHERE dst_missing OR src_missing")),
        ("unresolved: experiments classed UNKNOWN", one("SELECT count(*) FROM atlas.experiment WHERE atlas_class='UNKNOWN'")),
        ("unresolved: identity collisions", one("SELECT count(*) FROM atlas.identity_collision WHERE status='OPEN'")),
        ("unresolved: facts UNRESOLVED/CONTRADICTORY", one("SELECT count(*) FROM atlas.fact WHERE status IN ('UNRESOLVED','CONTRADICTORY')")),
        ("machine-local-only sources (GIT_LOCAL/FS)", one("SELECT count(*) FROM atlas.source WHERE visibility LIKE 'GIT_LOCAL:%' OR visibility LIKE 'FS:%'")),
        ("referenced, not visible from M1 (EXPECTED)", one("SELECT count(*) FROM atlas.source WHERE visibility LIKE 'EXPECTED:%'")),
        ("git commits seen only on a local branch", one("SELECT count(*) FROM atlas.git_commit WHERE seen_on_host IS NOT NULL")),
        ("signals OPEN (weak-signal layer)", one("SELECT count(*) FROM atlas.signal WHERE status='OPEN'")),
    ]


def build() -> str:
    conn = db.connect()
    try:
        cur = conn.cursor()
        L = []
        L.append("ATLAS INDEX REPORT -- generated from atlas.* on the M1 store")
        L.append("=" * 78)
        L.append("")
        L.append("1. COUNTS")
        for k, v in counts(cur):
            L.append("   {:<48} {}".format(k, v))
        L.append("")
        L.append("2. BY ENGINE (experiments / attempts / hosts seen on attempts)")
        for row in q(cur, """SELECT e.engine_id, count(DISTINCT e.experiment_key), count(a.attempt_key),
                                    string_agg(DISTINCT coalesce(a.host_id,'?'), ',')
                             FROM atlas.experiment e LEFT JOIN atlas.attempt a USING (experiment_key)
                             GROUP BY 1 ORDER BY 2 DESC"""):
            L.append("   {:<22} {:>6} exp {:>6} att   hosts {}".format(*row))
        L.append("")
        L.append("3. BY CAMPAIGN / PROGRAM (experiments, reported classes)")
        for row in q(cur, """SELECT c.campaign_key, count(e.*),
                                    string_agg(DISTINCT e.atlas_class, ',')
                             FROM atlas.campaign c LEFT JOIN atlas.experiment e USING (campaign_key)
                             WHERE c.program NOT LIKE 'vivarium%' GROUP BY 1 ORDER BY 1"""):
            L.append("   {:<42} {:>4}  {}".format(row[0][:42], row[1], (row[2] or "")[:28]))
        vq = q(cur, "SELECT count(*), count(DISTINCT campaign_key) FROM atlas.experiment WHERE engine_id='vivarium'")[0]
        L.append("   vivarium.queue/* ({} families)                  {:>4}  queue status only".format(vq[1], vq[0]))
        L.append("")
        L.append("4. COVERAGE (last successful pass per harvester and host)")
        for row in q(cur, "SELECT host_id, harvester, harvester_version, last_success_at FROM atlas.v_coverage ORDER BY 2"):
            L.append("   {:<4} {:<20} {:<24} {}".format(row[0] or "?", row[1], row[2], str(row[3])[:19]))
        L.append("   Locality of sources:")
        for row in q(cur, "SELECT visibility, count(*) FROM atlas.source GROUP BY 1 ORDER BY 2 DESC"):
            L.append("     {:<24} {}".format(row[0], row[1]))
        L.append("")
        L.append("5. IDENTITY COLLISIONS AND CONFLICTS (recorded, never auto-merged)")
        for row in q(cur, """SELECT namespace, native_id, left(candidates::text, 120) FROM atlas.identity_collision
                             WHERE status='OPEN' ORDER BY 1, 2 LIMIT 25"""):
            L.append("   {} | {} | {}".format(*row))
        L.append("")
        L.append("6. EXAMPLE CROSS-EXPERIMENT QUERIES (live output)")
        for title, sql in EXAMPLE_QUERIES:
            L.append("   -- " + title)
            L.append("   " + sql[:160] + ("..." if len(sql) > 160 else ""))
            for row in q(cur, sql):
                L.append("     " + " | ".join(str(x) for x in row)[:150])
            L.append("")
        L.append("7. WEAK-SIGNAL SCAN (atlas.signal, OPEN, by rule)")
        for rid, kind, n in q(cur, """SELECT rule_id, kind, count(*) FROM atlas.signal WHERE status='OPEN'
                                      GROUP BY 1,2 ORDER BY 1"""):
            L.append("   {:<40} {:<26} {}".format(rid, kind, n))
            for (s,) in q(cur, "SELECT summary FROM atlas.signal WHERE rule_id=%s AND status='OPEN' ORDER BY summary LIMIT 3", (rid,)):
                L.append("     - " + s[:150])
        return "\n".join(L) + "\n"
    finally:
        conn.close()


def status() -> str:
    conn = db.connect()
    try:
        cur = conn.cursor()
        rows = q(cur, """SELECT harvest_id, harvester, harvester_version, host_id, status, started_at::text,
                                left(counts::text, 90) FROM atlas.harvest_run ORDER BY harvest_id DESC LIMIT 15""")
        return "\n".join(" | ".join(str(x) for x in r) for r in rows) + "\n\n" + \
            "\n".join("{:<48} {}".format(k, v) for k, v in counts(cur))
    finally:
        conn.close()
