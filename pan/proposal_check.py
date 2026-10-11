"""PAN-41: verify the Atlas/Hades schema PROPOSALS (roles/Pan/docs/sagacity/proposals/*.sql) for syntax and for the rules
they claim to enforce, in a THROWAWAY database on the canonical cluster that is created and dropped here (precedent:
Atlas's atlas_pgvector_smoke). Nothing is applied to schema atlas. The parent tables are minimal stubs with the real
column names the proposals reference.

python -m pan proposals check      -> roles/Pan/reports/controls/PROPOSALS_<ts>.json
"""
import datetime as dt
import json

from . import REPO

DB = "pan_proposal_check"
STUBS = """
create schema atlas;
create table atlas.harvest_run (harvest_id bigint primary key);
create table atlas.primitive (primitive_id text primary key);
create table atlas.proposition (proposition_id text primary key, kind text not null);
create table atlas.source (source_id bigint primary key, file_sha256 text, blob_sha text, commit_sha text);
create table atlas.proposition_evidence (proposition_id text references atlas.proposition on delete cascade,
                                         relation text not null, source_id bigint references atlas.source);
create table atlas.experiment (experiment_key text primary key, engine_id text, world_family text);
insert into atlas.primitive values ('memory_persistence'), ('environmental_feedback');
insert into atlas.proposition values ('P-persistence-not-use', 'distinction'), ('P-some-constraint', 'constraint');
insert into atlas.source values (1, 'aa', null, null), (2, 'bb', null, null);
insert into atlas.proposition_evidence values ('P-persistence-not-use', 'SUPPORTS', 1), ('P-persistence-not-use', 'SUPPORTS', 2);
insert into atlas.experiment values ('npe.x/1', 'npe', 'cw01'), ('sfe.y/2', 'sfe', 'damage'), ('npe.x/3', 'npe', 'cw01');
"""


def _attempt(conn, sql, args=None):
    """(ok, error) for one statement block in its own transaction (commit -> deferred triggers fire)."""
    import psycopg2
    cur = conn.cursor()
    try:
        cur.execute(sql, args)
        conn.commit()
        return True, None
    except psycopg2.Error as e:
        conn.rollback()
        return False, type(e).__name__ + ": " + (e.pgerror or str(e)).strip().splitlines()[0][:160]


def check(write=True, out=print):
    from . import db
    admin = db.connect(autocommit=True)
    cur = admin.cursor()
    cur.execute("select 1 from pg_database where datname = %s", (DB,))
    if cur.fetchone():
        cur.execute("drop database " + DB)
    cur.execute("create database " + DB)
    res = []
    try:
        conn = db.connect(DB)
        ok, err = _attempt(conn, STUBS)
        assert ok, err
        props = REPO / "roles" / "Pan" / "docs" / "sagacity" / "proposals"
        for f in ("atlas_distinction_detail.sql", "boundary.sql"):
            ok, err = _attempt(conn, (props / f).read_text(encoding="utf-8"))
            res.append(dict(kind="POSITIVE", name="{} applies cleanly to the stubs".format(f), ok=ok, detail=err or "applied"))
        D = """insert into atlas.distinction_detail (proposition_id, property_a, property_b, discriminating_behavior,
                   stated_by, lineage_digest) values (%s, 'persists', 'is causally used', 'recoverable but unused', 'test', %s)"""
        ok, err = _attempt(conn, D, ("P-persistence-not-use", None))
        res.append(dict(kind="POSITIVE", name="a distinction detail attaches to a kind='distinction' proposition", ok=ok, detail=err or "inserted"))
        ok, err = _attempt(conn, D, ("P-some-constraint", None))
        res.append(dict(kind="NEGATIVE", name="a detail on a kind='constraint' proposition is refused", ok=not ok, detail=err))
        c = conn.cursor()
        c.execute("select recomputed_digest, n_supports from atlas.v_distinction_lineage where proposition_id = 'P-persistence-not-use'")
        dig, n = c.fetchone()
        conn.commit()
        import hashlib
        want = hashlib.sha256(b"aa,bb").hexdigest()
        res.append(dict(kind="POSITIVE", name="lineage digest is recomputable from the evidence sources", ok=dig == want and n == 2,
                        detail="{} supports, digest {}".format(n, "matches sha256('aa,bb')" if dig == want else dig)))
        ok, err = _attempt(conn, "insert into atlas.distinction_detail (proposition_id, property_a, property_b, discriminating_behavior, stated_by, witness_ref) values ('P-persistence-not-use', 'a', 'b', 'c', 't', 'exp/1') on conflict (proposition_id) do update set witness_ref = excluded.witness_ref")
        res.append(dict(kind="CHEAT", name="a witness without pinned bytes (no sha256) is refused", ok=not ok, detail=err))

        B = "insert into atlas.boundary ({}) values ({})"

        def boundary(fields, evidence=True, members=()):
            cols = ", ".join(fields)
            vals = ", ".join(["%s"] * len(fields))
            sql = B.format(cols, vals) + ";"
            args = list(fields.values())
            if evidence:
                sql += " insert into atlas.boundary_evidence values (%s, 'experiment', 'npe.x/1', 'SUPPORTS', 1, 'L1', 'test', 'test');"
                args.append(fields["boundary_id"])
            for et, ek, role in members:
                sql += " insert into atlas.boundary_member values (%s, %s, %s, %s);"
                args += [fields["boundary_id"], et, ek, role]
            return _attempt(conn, sql, args)

        base = dict(statement="s", basis="DECLARED", stated_by="test")
        ok, err = boundary(dict(base, boundary_id="F1", kind="OBSERVED_FAILURE"),
                           members=[("experiment", "npe.x/1", "MEMBER"), ("blind_spot", "BS-memory-outside-world", "IMPLICATED_ASSUMPTION")])
        res.append(dict(kind="POSITIVE", name="an OBSERVED_FAILURE with evidence commits", ok=ok, detail=err or "committed"))
        ok, err = boundary(dict(base, boundary_id="F0", kind="OBSERVED_FAILURE"), evidence=False)
        res.append(dict(kind="NEGATIVE", name="an OBSERVED_FAILURE without evidence is refused at commit", ok=not ok, detail=err))
        ok, err = boundary(dict(base, boundary_id="E1", kind="SUPPORTED_EQUIVALENCE_CLASS", basis="SIMILARITY_SCORE"))
        res.append(dict(kind="CHEAT", name="equivalence from a similarity score is refused", ok=not ok, detail=err))
        ok, err = boundary(dict(base, boundary_id="E2", kind="SUPPORTED_EQUIVALENCE_CLASS", basis="INTERVENTION_WITNESS"))
        res.append(dict(kind="CHEAT", name="equivalence without an intervention suite and pinned witness is refused", ok=not ok, detail=err))
        ok, err = boundary(dict(base, boundary_id="E3", kind="SUPPORTED_EQUIVALENCE_CLASS", basis="INTERVENTION_WITNESS",
                                intervention_suite="suite-A", witness_ref="exp/1", witness_sha256="cc"))
        res.append(dict(kind="POSITIVE", name="equivalence with suite + pinned witness + evidence commits", ok=ok, detail=err or "committed"))
        ok, err = boundary(dict(base, boundary_id="U1", kind="UNRESOLVED_SIMILARITY", basis="SIMILARITY_SCORE"))
        res.append(dict(kind="NEGATIVE", name="an unresolved similarity without a discriminating experiment is refused", ok=not ok, detail=err))
        ok, err = boundary(dict(base, boundary_id="R1", kind="UNTESTED_REGION"), evidence=False)
        res.append(dict(kind="NEGATIVE", name="an untested region without reachability is refused", ok=not ok, detail=err))
        ok, err = boundary(dict(base, boundary_id="R2", kind="UNTESTED_REGION", reachability="UNKNOWN"), evidence=False)
        res.append(dict(kind="POSITIVE", name="an untested region with reachability needs no evidence", ok=ok, detail=err or "committed"))
        ok, err = boundary(dict(base, boundary_id="F2", kind="OBSERVED_FAILURE"),
                           members=[("experiment", "sfe.y/2", "MEMBER"), ("blind_spot", "BS-memory-outside-world", "IMPLICATED_ASSUMPTION")])
        ok3, err3 = boundary(dict(base, boundary_id="F3", kind="OBSERVED_FAILURE"),
                             members=[("experiment", "npe.x/3", "MEMBER"), ("blind_spot", "BS-memory-outside-world", "IMPLICATED_ASSUMPTION")])
        c = conn.cursor()
        c.execute("select engines_with_linked_failure, world_families, failure_boundaries from atlas.v_assumption_failure_recurrence where assumption_key = 'BS-memory-outside-world'")
        r = c.fetchone()
        conn.commit()
        res.append(dict(kind="POSITIVE", name="recurrence view counts distinct engines and world families per implicated assumption",
                        ok=ok and ok3 and r == (2, 2, 3), detail="engines, world families, boundaries = {}".format(r)))
        conn.close()
    finally:
        cur.execute("drop database if exists " + DB)
        admin.close()
    verdict = "PASS" if all(x["ok"] for x in res) else "FAIL"
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    doc = dict(control="PAN-41 schema proposals (throwaway database {}, dropped)".format(DB), at=at, verdict=verdict, checks=res)
    if write:
        p = REPO / "roles" / "Pan" / "reports" / "controls" / "PROPOSALS_{}.json".format(at)
        p.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        out("wrote " + str(p))
    for x in res:
        out("{:<8} {:<5} {}  ({})".format(x["kind"], "PASS" if x["ok"] else "FAIL", x["name"], x["detail"]))
    out(verdict)
    return doc
