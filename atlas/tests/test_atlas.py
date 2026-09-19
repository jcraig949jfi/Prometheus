"""Atlas self-tests (base role s2: positive, negative and CHEAT controls).

Pure tests need nothing. Index tests read the live atlas schema on the M1
store and are skipped when it is unreachable; every write they make runs
inside a transaction that is rolled back, so the index is never changed.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from atlas import classify, comb, db  # noqa: E402
from atlas.harvest import common as C  # noqa: E402


# ------------------------------------------------------------------ pure

def test_status_class_is_conservative():
    assert classify.status_class("WEAK_POSITIVE") == "WEAK_POSITIVE"
    assert classify.status_class("CAPABLE_NEGATIVE") == "NEGATIVE"
    assert classify.status_class("INSTRUMENT_INVALID") == "INVALID"
    assert classify.status_class("banana") == "UNKNOWN"
    assert classify.status_class(None) == "UNKNOWN"


def test_host_from_tag_and_text():
    assert classify.host_from_tag("m2-411504ab") == "M2"
    assert classify.host_from_tag("gandalf-6cd1348b") == "M3"
    assert classify.host_from_tag("cw01") is None
    assert classify.host_from_text(r"D:\Prometheus-worktrees\archaeon-wse")[0] == "M2"
    assert classify.host_from_text("https://192.168.1.191:8811")[0] == "M2"
    assert classify.host_from_text("no host here") == (None, None)


def test_commit_classifier():
    c = classify.classify_commit("Harmonia[gandalf-6cd1348b]: HARM-46 PREREG for C5-03", "")
    assert (c["seat"], c["instance_tag"]) == ("Harmonia", "gandalf-6cd1348b")
    assert "PREREG" in c["classes"] and "HARM-46" in c["ids"] and "C5-03" in c["ids"]
    c = classify.classify_commit("E[m1-ba44317c]: rows E-R8-H1b-carrier-factorial (+8)", "")
    assert (c["seat"], c["lane"]) == ("Nestor", "E")


def test_keys_are_built_from_native_ids_not_filenames():
    ek = C.experiment_key(C.campaign_key("archaeon.campaign", "cmp5"), "C5-03")
    assert ek == "archaeon.campaign/cmp5:C5-03"
    assert C.attempt_key(ek, "a02") == ek + "#a02"
    assert C.segment_key(C.attempt_key(ek, "a02"), "chunk_000").endswith("#a02@chunk_000")


def test_validity_is_conservative():
    assert C.validity_from("INSTRUMENT_INVALID") == "INSTRUMENT_FAILURE"
    assert C.validity_from("WEAK_POSITIVE") == "UNKNOWN"   # a disposition is not a validity claim
    assert C.validity_from(None) == "UNKNOWN"


def test_timestamps_never_guessed():
    assert db._ts(1789400633).year == 2026
    assert db._ts(1789400633000).year == 2026
    assert db._ts("2026-09-18T14:32:07Z") == "2026-09-18T14:32:07Z"
    assert db._ts("yesterday") is None


# ------------------------------------------------------------------ index

@pytest.fixture(scope="module")
def conn():
    try:
        c = db.connect()
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM atlas.experiment")
            if cur.fetchone()[0] == 0:
                pytest.skip("atlas index empty")
    except Exception as e:  # unreachable store: skip, never fake a pass
        pytest.skip("atlas store unreachable: {}".format(e))
    yield c
    c.rollback()
    c.close()


def one(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        r = cur.fetchone()
    return r[0] if r else None


# positive controls: facts known from the sources must be in the index
def test_positive_declared_parents(conn):
    n = one(conn, """SELECT count(*) FROM atlas.edge WHERE src_key='archaeon.campaign/cmp5:C5-03'
                     AND relation='DESCENDANT_OF' AND dst_key IN ('archaeon.campaign/cmp4:C4-01','archaeon.campaign/cmp4:C4-03')""")
    assert n == 2


def test_positive_supersession_keeps_both(conn):
    assert one(conn, """SELECT count(*) FROM atlas.edge WHERE src_key='archaeon.campaign/cmp5:C5-08'
                        AND relation='SUPERSEDES' AND dst_key='archaeon.campaign/cmp4:C4-07'""") == 1
    # the superseded experiment and its original disposition are still there
    assert one(conn, "SELECT reported_disposition FROM atlas.experiment WHERE experiment_key='archaeon.campaign/cmp4:C4-07'")
    assert one(conn, """SELECT count(*) FROM atlas.conclusion WHERE subject_key='archaeon.campaign/cmp4:C4-07'
                        AND status='SUPERSEDED_INTERPRETATION'""") >= 1


def test_positive_cross_engine_lineage(conn):
    assert one(conn, """SELECT count(*) FROM atlas.edge g JOIN atlas.idea i ON g.src_type='idea' AND i.idea_key=g.src_key
                        WHERE i.engine_id='npe' AND g.dst_key LIKE 'archaeon.campaign/%%'""") >= 1


def test_positive_every_fact_has_evidence(conn):
    assert one(conn, """SELECT count(*) FROM atlas.fact f WHERE NOT EXISTS
                        (SELECT 1 FROM atlas.fact_evidence x WHERE x.fact_id = f.fact_id)""") == 0


# negative controls: things that must never appear
def test_negative_no_filename_identity(conn):
    assert one(conn, """SELECT count(*) FROM atlas.experiment
                        WHERE native_id ~ '\\.(json|jsonl|md|py)$' OR experiment_key ~ '\\.(json|jsonl|md)$'""") == 0


def test_negative_no_prose_minted_keys(conn):
    assert one(conn, "SELECT count(*) FROM atlas.edge WHERE src_key ~ ' \\(' OR dst_key ~ ' \\('") == 0


def test_negative_no_self_edges(conn):
    assert one(conn, "SELECT count(*) FROM atlas.edge WHERE src_type=dst_type AND src_key=dst_key") == 0


# cheat controls: inject the thing a measurement claims to detect and prove the channel sees it
def test_cheat_weak_signal_rule_sees_an_injected_weak_positive(conn):
    rid, ver, kind, sql = next(r for r in comb.RULES if r[0] == "R01-weak-disposition")
    tag = "cheat-" + uuid.uuid4().hex[:8]
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT cheat")
        cur.execute("""INSERT INTO atlas.campaign(campaign_key, program, native_id) VALUES (%s,'atlas.test',%s)""",
                    ("atlas.test/" + tag, tag))
        cur.execute("""INSERT INTO atlas.experiment(experiment_key, campaign_key, native_id, atlas_class,
                       reported_disposition) VALUES (%s,%s,%s,'WEAK_POSITIVE','WEAK_POSITIVE')""",
                    ("atlas.test/{0}:{0}".format(tag), "atlas.test/" + tag, tag))
        cur.execute(sql)
        keys = {r[1] for r in cur.fetchall()}
        cur.execute("ROLLBACK TO SAVEPOINT cheat")
    assert "atlas.test/{0}:{0}".format(tag) in keys


def test_cheat_merge_never_erases_and_records_conflicts(conn):
    tag = "cheat-" + uuid.uuid4().hex[:8]
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT m")
        cur.execute("INSERT INTO atlas.harvest_run(harvester, harvester_version, host_id) VALUES ('test','t','M1') RETURNING harvest_id")
        h = cur.fetchone()[0]
        ck, ek = "atlas.test/" + tag, "atlas.test/{0}:{0}".format(tag)
        db.upsert(cur, "atlas.campaign", [{"campaign_key": ck, "program": "atlas.test", "native_id": tag}], ["campaign_key"], h)
        db.upsert(cur, "atlas.experiment", [{"experiment_key": ek, "campaign_key": ck, "native_id": tag}], ["experiment_key"], h)
        base = {"attempt_key": ek + "#a01", "experiment_key": ek, "host_id": "M2", "seen_from_hosts": ["M1"]}
        db.upsert(cur, "atlas.attempt", [base], ["attempt_key"], h)
        # another host offers the same attempt with no host and its own visibility
        db.upsert(cur, "atlas.attempt", [dict(base, host_id=None, seen_from_hosts=["M2"])], ["attempt_key"], h,
                  watch=("host_id",))
        cur.execute("SELECT host_id, seen_from_hosts FROM atlas.attempt WHERE attempt_key=%s", (base["attempt_key"],))
        host, seen = cur.fetchone()
        # a disagreeing non-null host is kept as a recorded conflict
        db.upsert(cur, "atlas.attempt", [dict(base, host_id="M1")], ["attempt_key"], h, watch=("host_id",))
        cur.execute("SELECT count(*) FROM atlas.field_conflict WHERE entity_key=%s AND field='host_id'", (base["attempt_key"],))
        conflicts = cur.fetchone()[0]
        cur.execute("ROLLBACK TO SAVEPOINT m")
    assert host == "M2" and sorted(seen) == ["M1", "M2"]
    assert conflicts == 1


def test_cheat_prune_spares_other_hosts(conn):
    tag = "cheat-" + uuid.uuid4().hex[:8]
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT p")
        cur.execute("INSERT INTO atlas.harvest_run(harvester, harvester_version, host_id) VALUES (%s,'t','M2') RETURNING harvest_id", (tag,))
        other = cur.fetchone()[0]
        cur.execute("INSERT INTO atlas.harvest_run(harvester, harvester_version, host_id) VALUES (%s,'t','M1') RETURNING harvest_id", (tag,))
        old = cur.fetchone()[0]
        cur.execute("INSERT INTO atlas.harvest_run(harvester, harvester_version, host_id) VALUES (%s,'t','M1') RETURNING harvest_id", (tag,))
        now = cur.fetchone()[0]
        for h, k in ((other, "m2"), (old, "m1old")):
            cur.execute("""INSERT INTO atlas.edge(src_type, src_key, dst_type, dst_key, relation, lineage_kind, basis, method,
                           last_harvest_id) VALUES ('experiment',%s,'experiment','x','RERUN_OF','EXECUTION','DECLARED','t',%s)""",
                        (tag + k, h))

        class H:
            id = now
            counts = {}

            def count(self, k, n=1):
                self.counts[k] = n
        C.prune(cur, H())
        cur.execute("SELECT src_key FROM atlas.edge WHERE src_key LIKE %s", (tag + "%",))
        left = {r[0] for r in cur.fetchall()}
        cur.execute("ROLLBACK TO SAVEPOINT p")
    assert left == {tag + "m2"}    # M1's stale row pruned, M2's row untouched
