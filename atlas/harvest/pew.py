"""Source adapter: PEW (schema ew on the M1 store) -- POINTERS ONLY.

For every (campaign_id, harness_id) and (campaign_id, attempt_id) in
ew.campaign_observations, one pg:// source row with the row count, reader
versions and ingest window, linked to the Atlas experiment/attempt with the
same native identity. PEW's own ids stay in PEW. Campaigns PEW holds that
no git adapter has indexed yet (ssf-c1..3, wse-survey-v01) get minimal
campaign/experiment rows marked as visible only through PEW.
All reads run in a READ ONLY transaction.
"""
from __future__ import annotations

from atlas import db
from atlas.harvest import common as C

VERSION = "pew/1"
ARCH = "archaeon.campaign"
WSE = "archaeon.wse"


def _read(sql, args=None):
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(sql, args)
            rows = cur.fetchall()
        conn.rollback()
        return rows
    finally:
        conn.close()


def run(args) -> dict:
    b = C.Batch("pew", VERSION, "Mnemosyne")
    exp_rows = _read("""SELECT campaign_id, harness_id, count(*), array_agg(DISTINCT kind ORDER BY kind),
                               min(reader_version), max(reader_version), max(source_commit)
                        FROM ew.campaign_observations WHERE harness_id IS NOT NULL
                        GROUP BY campaign_id, harness_id""")
    att_rows = _read("""SELECT campaign_id, harness_id, attempt_id, count(*)
                        FROM ew.campaign_observations WHERE attempt_id IS NOT NULL
                        GROUP BY campaign_id, harness_id, attempt_id""")
    known = {r[0] for r in _read("SELECT experiment_key FROM atlas.experiment")}
    known_att = {r[0] for r in _read("SELECT attempt_key FROM atlas.attempt")}
    for cid, hid, n, kinds, rv0, rv1, sc in exp_rows:
        prog = ARCH if cid.startswith("cmp") else WSE
        ck = C.campaign_key(prog, cid)
        ek = C.experiment_key(ck, hid)
        if ek not in known:
            b.campaign(campaign_key=ck, program=prog, native_id=cid, engine_id="sfe", driver_seat="Archaeon",
                       title="{} (indexed from PEW; git adapter pending)".format(cid))
            b.experiment(experiment_key=ek, campaign_key=ck, engine_id="sfe", native_id=hid, kind="experiment",
                         driver_seat="Archaeon", atlas_class="UNKNOWN", atlas_class_confidence="LOW",
                         atlas_class_method="visible only through PEW so far",
                         inferred={"existence": "ew.campaign_observations rows with this campaign_id/harness_id"})
        uri = "pg://prometheus_fire/ew.campaign_observations?campaign_id={}&harness_id={}".format(cid, hid)
        b.other_source(uri, "pg_rows", "PG:M1", host_id="M1", pg_ref="ew.campaign_observations", row_count=n,
                       record_key="campaign_id={} harness_id={}".format(cid, hid), commit_sha=sc,
                       top_keys=list(kinds or []), present=True)
        b.link(uri, "experiment", ek, "pew")
        b.fact("OBSERVED", "telemetry_availability", "experiment", ek, "pew.campaign_observations",
               {"rows": n, "kinds": kinds, "reader_versions": [rv0, rv1]}, uri, "", author="ATLAS_DERIVED")
    for cid, hid, aid, n in att_rows:
        prog = ARCH if cid.startswith("cmp") else WSE
        ek = C.experiment_key(C.campaign_key(prog, cid), hid)
        anat = aid.split("/", 1)[1] if "/" in aid else aid
        ak = C.attempt_key(ek, anat)
        uri = "pg://prometheus_fire/ew.campaign_observations?campaign_id={}&attempt_id={}".format(cid, aid)
        b.other_source(uri, "pg_rows", "PG:M1", host_id="M1", pg_ref="ew.campaign_observations", row_count=n,
                       record_key="attempt_id={}".format(aid), present=True)
        if ak in known_att:
            b.link(uri, "attempt", ak, "pew")
        else:
            b.link(uri, "experiment", ek, "pew")
            b.fact("RAN", "telemetry_availability", "experiment", ek, "pew.attempt_without_atlas_attempt", aid, uri,
                   "", status="UNRESOLVED", author="ATLAS_DERIVED")
    for xid, agent, project, title, gc in _read(
            "SELECT experiment_id, agent_id, project, title, git_commit FROM ew.experiments"):
        b.other_source("pew:" + xid, "pew", "PG:M1", host_id="M1", pew_id=xid, pg_ref="ew.experiments",
                       record_key="{} / {} / {}".format(agent, project, (title or "")[:120]), commit_sha=gc, present=True)
    with db.harvest("pew", VERSION, source_ref="prometheus_fire.ew (read only)") as h:
        return b.flush(h)
