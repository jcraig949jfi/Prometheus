"""The recomb layer: deterministic rules over the index that SURFACE
candidates -- weak signals, sign reversals, changed conclusions, rarely
crossed regions, calibration specimens, data gaps. Every row written is
ATLAS_DERIVED: it carries its rule id, rule version and the SQL that
produced it. Nothing here is a directive; Archaeon/Nestor/the operator
decide what to pursue (charter addendum, anomaly layer).

A rule is (id, version, kind, sql). The SQL returns
(subject_type, subject_key, summary, evidence_json). Re-running replaces
this rule's OPEN rows; rows a human/seat moved off OPEN are kept.
"""
from __future__ import annotations

import json
from typing import List, Tuple

from atlas import db
from atlas.harvest import common as C

VERSION = "comb/2"
# a measured quantity: not a preregistered threshold, count, control or design field
NAME_TAIL = r"regexp_replace(f.name, '^.*\.', '')"
MEASURED = ("f.kind IN ('measurement','metric_summary') AND f.name NOT LIKE 'prereg.%%' AND " + NAME_TAIL +
            " !~* '^(min|max|n|n_.*|min_.*|max_.*|declared|attacked|survived|paired|seed|seeds)$'")
SIGNED = "(effect|delta|diff|slope|corr|gain|loss|pct|ratio|dependence|advantage|lift|shift|change)"

RULES: List[Tuple[str, str, str, str]] = [
    ("R01-weak-disposition", "1", "WEAK_SIGNAL", """
        SELECT 'experiment', e.experiment_key,
               format('%s reported %s (claim ceiling / reason: %s)', e.native_id, e.reported_disposition,
                      left(coalesce(e.result_summary, e.reported_conclusion, ''), 200)),
               jsonb_build_array(jsonb_build_object('type','experiment','key',e.experiment_key))
        FROM atlas.experiment e
        WHERE e.atlas_class = 'WEAK_POSITIVE'
           OR e.reported_conclusion ILIKE '%%weak%%' OR e.result_summary ILIKE 'weak%%'"""),

    ("R02-repeated-weak-effect", "2", "REPEATED_WEAK_EFFECT", """
        WITH w AS (
          SELECT """ + NAME_TAIL + """ AS tail, e.campaign_key, e.engine_id, e.experiment_key
          FROM atlas.fact f JOIN atlas.experiment e ON f.subject_type='experiment' AND f.subject_key=e.experiment_key
          WHERE f.layer='OBSERVED' AND f.value_num IS NOT NULL AND """ + MEASURED + """
            AND """ + NAME_TAIL + """ ~* '""" + SIGNED + """'
            AND e.atlas_class IN ('WEAK_POSITIVE','INCONCLUSIVE'))
        SELECT 'measurement', tail,
               format('measured "%s" recurs in %s weak/inconclusive experiments across %s campaigns and %s engines',
                      tail, count(DISTINCT experiment_key), count(DISTINCT campaign_key), count(DISTINCT engine_id)),
               jsonb_agg(DISTINCT jsonb_build_object('type','experiment','key',experiment_key))
        FROM w GROUP BY tail
        HAVING count(DISTINCT campaign_key) >= 2 AND count(DISTINCT experiment_key) >= 3"""),

    ("R03-sign-reversal", "2", "SIGN_REVERSAL", """
        WITH v AS (
          SELECT """ + NAME_TAIL + """ AS tail, f.subject_type, f.subject_key, f.value_num
          FROM atlas.fact f
          WHERE f.layer='OBSERVED' AND f.value_num IS NOT NULL AND f.value_num <> 0 AND """ + MEASURED + """
            AND """ + NAME_TAIL + """ ~* '""" + SIGNED + """')
        SELECT 'measurement', tail,
               format('"%s" is positive in %s subjects and negative in %s (range %s .. %s)', tail,
                      count(DISTINCT subject_key) FILTER (WHERE value_num > 0),
                      count(DISTINCT subject_key) FILTER (WHERE value_num < 0),
                      round(min(value_num)::numeric, 4), round(max(value_num)::numeric, 4)),
               (SELECT jsonb_agg(x) FROM (SELECT DISTINCT jsonb_build_object('type', v2.subject_type, 'key', v2.subject_key,
                        'sign', sign(v2.value_num)) x FROM v v2 WHERE v2.tail = v.tail LIMIT 40) q)
        FROM v GROUP BY tail
        HAVING count(DISTINCT subject_key) FILTER (WHERE value_num > 0) >= 2
           AND count(DISTINCT subject_key) FILTER (WHERE value_num < 0) >= 2"""),

    ("R04-conclusion-changed-across-attempts", "2", "CONCLUSION_CHANGED", """
        SELECT 'experiment', a.experiment_key,
               format('attempts disagree: %s', string_agg(DISTINCT a.native_id || '=' || coalesce(a.reported_status,'?'), ', ')),
               jsonb_agg(jsonb_build_object('type','attempt','key',a.attempt_key,'status',a.reported_status))
        FROM atlas.attempt a JOIN atlas.experiment e USING (experiment_key)
        WHERE a.reported_status IS NOT NULL AND e.engine_id <> 'vivarium'   -- executor terminal states are not conclusions
        GROUP BY a.experiment_key
        HAVING count(DISTINCT upper(split_part(a.reported_status, ' ', 1))) > 1 AND count(*) <= 20"""),

    ("R05-superseded-interpretation", "1", "CONCLUSION_CHANGED", """
        SELECT c.subject_type, c.subject_key, format('interpretation superseded: %s', left(c.text_verbatim, 240)),
               jsonb_build_array(jsonb_build_object('type','conclusion','id',c.conclusion_id),
                 (SELECT jsonb_agg(jsonb_build_object('type', g.src_type, 'key', g.src_key)) FROM atlas.edge g
                  WHERE g.relation='SUPERSEDES' AND g.dst_key=c.subject_key))
        FROM atlas.conclusion c WHERE c.status = 'SUPERSEDED_INTERPRETATION'"""),

    ("R06-null-with-rich-telemetry", "1", "NULL_WITH_TELEMETRY", """
        SELECT 'experiment', e.experiment_key,
               format('%s is %s but carries %s observed measurements', e.native_id, e.atlas_class, count(f.fact_id)),
               jsonb_build_array(jsonb_build_object('type','experiment','key',e.experiment_key))
        FROM atlas.experiment e JOIN atlas.fact f ON f.subject_type='experiment' AND f.subject_key=e.experiment_key
        WHERE e.atlas_class IN ('NEGATIVE','NULL','INCONCLUSIVE') AND f.layer='OBSERVED'
        GROUP BY e.experiment_key, e.native_id, e.atlas_class HAVING count(f.fact_id) >= 30"""),

    ("R07-unresolved-interpretation", "1", "UNRESOLVED_QUESTION", """
        SELECT c.subject_type, c.subject_key, format('open interpretation (%s): %s', c.disposition, left(c.text_verbatim, 240)),
               jsonb_build_array(jsonb_build_object('type','conclusion','id',c.conclusion_id))
        FROM atlas.conclusion c WHERE c.status = 'UNRESOLVED'"""),

    ("R08-open-defects-by-class", "1", "INSTRUMENT_FAILURE_CLUSTER", """
        SELECT 'defect_class', coalesce(d.extract->>'defect_class', d.category, 'uncategorised'),
               format('%s defects of class "%s" (%s open) across %s campaigns',
                      count(*), coalesce(d.extract->>'defect_class', d.category, 'uncategorised'),
                      count(*) FILTER (WHERE d.reported_status ILIKE 'open%%'), count(DISTINCT d.campaign_key)),
               jsonb_agg(jsonb_build_object('type','defect','key',d.defect_key))
        FROM atlas.defect d GROUP BY 2 HAVING count(*) >= 3"""),

    ("R09-cross-engine-lineage", "1", "CROSS_ENGINE_LINEAGE", """
        WITH ends AS (
          SELECT g.edge_id, g.relation, g.reason, g.src_key, g.dst_key,
                 coalesce(es.engine_id, i1.engine_id, c1.engine_id) AS e_src,
                 coalesce(ed.engine_id, i2.engine_id, c2.engine_id) AS e_dst
          FROM atlas.edge g
          LEFT JOIN atlas.experiment es ON g.src_type='experiment' AND es.experiment_key=g.src_key
          LEFT JOIN atlas.idea i1 ON g.src_type='idea' AND i1.idea_key=g.src_key
          LEFT JOIN atlas.campaign c1 ON g.src_type='campaign' AND c1.campaign_key=g.src_key
          LEFT JOIN atlas.experiment ed ON g.dst_type='experiment' AND ed.experiment_key=g.dst_key
          LEFT JOIN atlas.idea i2 ON g.dst_type='idea' AND i2.idea_key=g.dst_key
          LEFT JOIN atlas.campaign c2 ON g.dst_type='campaign' AND c2.campaign_key=g.dst_key
          WHERE g.lineage_kind IN ('SCIENTIFIC','EXECUTION'))
        SELECT 'edge', edge_id::text, format('%s --%s/%s--> %s (%s -> %s)', src_key, relation, reason, dst_key, e_src, e_dst),
               jsonb_build_array(jsonb_build_object('type','edge','id',edge_id))
        FROM ends WHERE e_src IS NOT NULL AND e_dst IS NOT NULL
          AND split_part(e_src,'.',1) <> split_part(e_dst,'.',1)
          AND NOT (split_part(e_src,'.',1) IN ('sfe','archaeon') AND split_part(e_dst,'.',1) IN ('sfe','archaeon'))"""),

    ("R10-world-organism-visited-once", "1", "VISITED_ONCE", """
        WITH combos AS (
          SELECT world_family w, organism_family o, 'experiment' t, experiment_key k FROM atlas.experiment
            WHERE world_family IS NOT NULL AND organism_family IS NOT NULL
          UNION ALL
          SELECT world_family, organism_family, 'idea', idea_key FROM atlas.idea
            WHERE world_family IS NOT NULL AND organism_family IS NOT NULL)
        SELECT 'combination', left(w, 120) || ' x ' || left(o, 120),
               format('world "%s" x organism "%s" appears once in the index', left(w, 80), left(o, 80)),
               jsonb_agg(jsonb_build_object('type', t, 'key', k))
        FROM combos GROUP BY w, o HAVING count(*) = 1"""),

    ("R11-calibration-specimens", "1", "CALIBRATION_SPECIMEN", """
        SELECT 'experiment', f.subject_key,
               format('declares %s control fact(s): %s', count(*), left(string_agg(DISTINCT f.name, ', '), 200)),
               jsonb_build_array(jsonb_build_object('type','experiment','key',f.subject_key))
        FROM atlas.fact f
        WHERE f.subject_type='experiment' AND f.kind='control'
          AND (f.name ILIKE '%%positive%%' OR f.name ILIKE '%%cheat%%' OR f.name ILIKE '%%battery%%')
        GROUP BY f.subject_key HAVING count(*) >= 2"""),

    ("R12-evidence-not-visible-here", "1", "DATA_GAP", """
        SELECT 'host', split_part(s.visibility, ':', 2),
               format('%s sources are referenced but not visible from any inspected host (%s); an Atlas instance on %s can fill them',
                      count(*), string_agg(DISTINCT s.kind, ','), split_part(s.visibility, ':', 2)),
               jsonb_build_array(jsonb_build_object('visibility', s.visibility, 'n', count(*)))
        FROM atlas.source s WHERE s.visibility LIKE 'EXPECTED:%%' GROUP BY s.visibility"""),

    ("R13-recurring-measurement-names", "2", "RECURRING_MEASUREMENT", """
        SELECT 'measurement', """ + NAME_TAIL + """,
               format('"%s" is measured under %s engines / %s campaigns (%s full names)', """ + NAME_TAIL + """,
                      count(DISTINCT e.engine_id), count(DISTINCT e.campaign_key), count(DISTINCT f.name)),
               jsonb_build_object('names', (array_agg(DISTINCT f.name))[1:12])
        FROM atlas.fact f JOIN atlas.experiment e ON f.subject_type='experiment' AND f.subject_key=e.experiment_key
        WHERE f.layer='OBSERVED' AND f.value_num IS NOT NULL AND """ + MEASURED + """
          AND length(""" + NAME_TAIL + """) >= 4
        GROUP BY """ + NAME_TAIL + """ HAVING count(DISTINCT e.engine_id) >= 2"""),
]


def run() -> dict:
    out = {}
    with db.harvest("comb", VERSION, source_ref="atlas.* (derived)") as h:
        cur = h.conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(%s)", (db.LOCK_COMB,))
        for rid, ver, kind, sql in RULES:
            cur.execute(sql)
            rows = cur.fetchall()
            sig = []
            for st, sk, summary, ev in rows:
                sig.append({"signal_key": C.h16(kind, rid, st, sk), "kind": kind, "rule_id": rid, "rule_version": ver,
                            "subject_type": st, "subject_key": str(sk)[:500], "summary": C.trunc(summary, 2000),
                            "evidence": ev if ev is not None else [], "query": " ".join(sql.split())})
            cur.execute("DELETE FROM atlas.signal WHERE rule_id = %s AND status = 'OPEN'", (rid,))
            n = db.upsert(cur, "atlas.signal", sig, ["signal_key"], h.id, replace=("summary", "evidence", "query"))
            out[rid] = n
            h.count(rid, n)
        from atlas.report import detect_collisions
        out["identity_collisions"] = detect_collisions(cur, h.id)
        h.count("identity_collisions", out["identity_collisions"])
        h.conn.commit()
    return out
