"""Apply the DRAFT migrations to a throwaway schema on the canonical server and
exercise the triggers. Production schema `viv` is never touched (VIV_SCHEMA is a
throwaway; drop_schema refuses `viv`)."""
import os, sys, uuid, json, hashlib, pathlib
os.environ["VIV_SCHEMA"] = "viv_draft_" + uuid.uuid4().hex[:8]
os.environ.setdefault("EW_DB_HOST", "192.168.1.202"); os.environ.setdefault("VIV_DB_HOST", "192.168.1.202")
V = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(V))
from viv import db as _db
S = os.environ["VIV_SCHEMA"]
HA = "sha256:" + "a" * 64
HB = "sha256:" + "b" * 64
conn = _db.connect(); conn.autocommit = False


def run(sql, *args):
    with conn.cursor() as cur:
        cur.execute(sql.replace("{S}", S).replace("{schema}", S), args or None)
        try:
            return cur.fetchall()
        except Exception:
            return None


def expect_error(code, sql, *args):
    try:
        run(sql, *args); conn.commit(); print("  FAIL: no error, expected", code); return False
    except Exception as e:
        conn.rollback()
        ok = code in str(e); print("  %s %s -> %s" % ("ok " if ok else "BAD", code, str(e).splitlines()[0][:110])); return ok


def key(design, kind, parts="[]"):
    return "idem:" + hashlib.sha256(("%s|%s|%s" % (design, kind, parts)).encode()).hexdigest()[:32]


try:
    _db.apply_migrations(conn, target_schema=S)
    for f in sorted((V / "migrations" / "drafts").glob("*.sql")):
        run(f.read_text(encoding="utf-8")); conn.commit(); print("applied", f.name)
    eid = run("INSERT INTO {S}.research_experiment_queue (created_by, source_reason, experiment_spec, spec_hash, status) "
              "VALUES ('t','t',%s,%s,'completed') RETURNING experiment_id", json.dumps({"spec_version": 3}), HA)[0][0]
    conn.commit()
    print("triggers:")
    expect_error("VIV11", "INSERT INTO {S}.execution_attempt (experiment_id, attempt_number, design_digest, worker_id) VALUES (%s, 1, %s, 'w')", eid, HB)
    aid = run("INSERT INTO {S}.execution_attempt (experiment_id, attempt_number, design_digest, worker_id) VALUES (%s, 1, %s, 'w') RETURNING attempt_id", eid, HA)[0][0]; conn.commit()
    expect_error("VIV12", "INSERT INTO {S}.execution_attempt (experiment_id, attempt_number, design_digest, worker_id) VALUES (%s, 3, %s, 'w')", eid, HA)
    expect_error("VIV14", "INSERT INTO {S}.execution_attempt (experiment_id, attempt_number, design_digest, worker_id, parent_attempt_id) VALUES (%s, 2, %s, 'w', %s)", eid, HA, aid)
    expect_error("VIV20", "INSERT INTO {S}.execution_step (attempt_id, step_key, step_kind, status) VALUES (%s, 'idem:wrong', 'claim', 'NEW')", aid)
    sid = run("INSERT INTO {S}.execution_step (attempt_id, step_key, step_kind, status) VALUES (%s, %s, 'claim', 'NEW') RETURNING step_id", aid, key(HA, "claim"))[0][0]; conn.commit()
    print("  ok  step inserted with the design-keyed key")
    expect_error("VIV21", "INSERT INTO {S}.execution_step (attempt_id, step_key, step_kind, parts, status) VALUES (%s, %s, 'claim', '[1]', 'REPLAYED')", aid, key(HA, "claim", "[1]"))
    run("UPDATE {S}.execution_attempt SET terminal_state='FAILED', closed_at=now() WHERE attempt_id=%s", aid); conn.commit()
    expect_error("VIV17", "UPDATE {S}.execution_attempt SET terminal_state='COMPLETED' WHERE attempt_id=%s", aid)
    aid2 = run("INSERT INTO {S}.execution_attempt (experiment_id, attempt_number, design_digest, worker_id, parent_attempt_id) VALUES (%s, 2, %s, 'w', %s) RETURNING attempt_id", eid, HA, aid)[0][0]; conn.commit()
    print("  ok  attempt 2 opened with parent 1")
    run("INSERT INTO {S}.execution_step (attempt_id, step_key, step_kind, status, replay_of_step) VALUES (%s, %s, 'claim', 'REPLAYED', %s)", aid2, key(HA, "claim"), sid); conn.commit()
    print("  ok  REPLAYED step pointing at the same key in attempt 1")
    eid2 = run("INSERT INTO {S}.research_experiment_queue (created_by, source_reason, experiment_spec, spec_hash, status) VALUES ('t','t',%s,%s,'completed') RETURNING experiment_id", json.dumps({"spec_version": 3}), HA)[0][0]
    aid3 = run("INSERT INTO {S}.execution_attempt (experiment_id, attempt_number, design_digest, worker_id) VALUES (%s, 1, %s, 'w') RETURNING attempt_id", eid2, HA)[0][0]; conn.commit()
    expect_error("VIV22", "INSERT INTO {S}.execution_step (attempt_id, step_key, step_kind, status, replay_of_step) VALUES (%s, %s, 'claim', 'REPLAYED', %s)", aid3, key(HA, "claim"), sid)
    for n in (1, 2):
        run("INSERT INTO {S}.pew_outbox (event_id, producer, stream, sequence, event_kind, source_attempt, source_experiment, payload, payload_digest) VALUES (%s,'p','s',0,'ATTEMPT_OPENED',%s,%s,'{}','d')", "e%d" % n, aid2, eid)
    conn.commit()
    print("  ok  sequences", run("SELECT event_id, sequence FROM {S}.pew_outbox ORDER BY sequence"))
    expect_error("VIV42", "UPDATE {S}.pew_outbox SET state='DELIVERED' WHERE event_id='e2'")
    run("UPDATE {S}.pew_outbox SET state='DELIVERED' WHERE event_id='e1'"); run("UPDATE {S}.pew_outbox SET state='DELIVERED' WHERE event_id='e2'"); conn.commit()
    print("  ok  in-order delivery")
    expect_error("VIV40", "DELETE FROM {S}.pew_outbox WHERE event_id='e1'")
    expect_error("VIV15", "DELETE FROM {S}.execution_attempt WHERE attempt_id=%s", aid3)
    eid3 = run("INSERT INTO {S}.research_experiment_queue (created_by, source_reason, experiment_spec, spec_hash, status, error) VALUES ('t','t',%s,%s,'failed','BUDGET_EXCEEDED: something') RETURNING experiment_id", json.dumps({"spec_version": 3}), HA)[0][0]; conn.commit()
    run((V / "migrations" / "drafts" / "007_backfill_attempts_reversible.sql").read_text(encoding="utf-8")); conn.commit()
    r = run("SELECT attempt_number, terminal_state, termination->>'termination_reason', claim_grant->>'backfill' FROM {S}.execution_attempt WHERE experiment_id=%s", eid3)
    print("  ok  backfill", r, "(reason UNKNOWN although error text says BUDGET_EXCEEDED)" if r and r[0][2] == "UNKNOWN" else "BAD")
finally:
    conn.rollback(); _db.drop_schema(conn, S); conn.close(); print("dropped", S)
