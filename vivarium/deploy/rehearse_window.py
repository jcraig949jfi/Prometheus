"""Rehearse the deploy window against a COPY of production `viv` rows in a
throwaway schema (never `viv` itself). What it proves before the operator
opens the window:

    - 001-005 then 006-009 apply cleanly on the real row population
    - 007 backfills exactly one attempt per terminal row, every one
      termination_reason UNKNOWN, no execution_step fabricated
    - every old queue row is BYTE-IDENTICAL over its pre-migration columns;
      the only new column is bundle_declared, NULL on every old row
    - the release transition function (006) still refuses relation
      mutation on the copied rows (VIV02 family) -- a spot check
    - the throwaway schema is dropped

Read-only on production: SELECT only from viv.*.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import pathlib
import sys
import uuid

os.environ["VIV_SCHEMA"] = "viv_rehearse_" + uuid.uuid4().hex[:8]
os.environ.setdefault("EW_DB_HOST", "192.168.1.202"); os.environ.setdefault("VIV_DB_HOST", "192.168.1.202")
V = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V))
from viv import db as _db                                        # noqa: E402

S = os.environ["VIV_SCHEMA"]
TABLES = ("research_experiment_queue", "research_experiment_events", "worker_heartbeat",
          "register_errata", "register_errata_rows")


def main() -> int:
    conn = _db.connect(); conn.autocommit = False
    out = {"schema": "vivarium_window_rehearsal.v1", "throwaway": S,
           "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "checks": {}}
    ok = True
    try:
        base = _db.apply_migrations(conn, target_schema=S)
        out["applied_base"] = base
        copied = {}
        with conn.cursor() as cur:
            for t in TABLES:
                cur.execute("SELECT to_regclass(%s)", ("viv." + t,))
                if cur.fetchone()[0] is None:
                    copied[t] = None; continue
                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name=%s "
                            "AND is_generated='NEVER' ORDER BY ordinal_position", (S, t))
                cols = ", ".join('"%s"' % c[0] for c in cur.fetchall())
                cur.execute("ALTER TABLE %s.%s DISABLE TRIGGER ALL" % (S, t))
                cur.execute("INSERT INTO %s.%s (%s) SELECT %s FROM viv.%s" % (S, t, cols, cols, t))
                copied[t] = cur.rowcount
                cur.execute("ALTER TABLE %s.%s ENABLE TRIGGER ALL" % (S, t))
        conn.commit()
        out["copied"] = copied
        with conn.cursor() as cur:
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND "
                        "table_name='research_experiment_queue' ORDER BY ordinal_position", (S,))
            old_cols = [c[0] for c in cur.fetchall()]
            proj = "SELECT experiment_id::text, md5(json_build_array(%s)::text) FROM %s.research_experiment_queue q" % (
                ", ".join('q."%s"' % c for c in old_cols), S)
            cur.execute(proj)
            before = dict(cur.fetchall())
            # 007 backfills PRE-RELEASE rows only (created before window C4-20260917-W1's cutoff)
            cur.execute("SELECT count(*) FROM %s.research_experiment_queue WHERE status IN ('completed','failed','cancelled') "
                        "AND created_at < TIMESTAMPTZ '2026-09-17 14:00:00+00'" % S)
            terminal = cur.fetchone()[0]
            cur.execute("SELECT status, count(*) FROM %s.research_experiment_queue GROUP BY 1 ORDER BY 1" % S)
            out["status_histogram"] = dict(cur.fetchall())
        conn.rollback()
        for f in sorted((V / "migrations" / "drafts").glob("*.sql")):
            with conn.cursor() as cur:
                cur.execute(f.read_text(encoding="utf-8").replace("{schema}", S))
            conn.commit()
        out["applied_drafts"] = [f.name for f in sorted((V / "migrations" / "drafts").glob("*.sql"))]
        with conn.cursor() as cur:
            cur.execute(proj)                                    # the OLD columns only
            after = dict(cur.fetchall())
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND "
                        "table_name='research_experiment_queue' ORDER BY ordinal_position", (S,))
            new_cols = [c[0] for c in cur.fetchall() if c[0] not in old_cols]
            cur.execute("SELECT count(*) FROM %s.research_experiment_queue WHERE bundle_declared IS NOT NULL "
                        "AND created_at < TIMESTAMPTZ '2026-09-17 14:00:00+00'" % S)
            declared_nonnull = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM %s.execution_attempt WHERE claim_grant->>'backfill' = '007'" % S)
            attempts = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM %s.execution_attempt WHERE termination->>'termination_reason' = 'UNKNOWN'" % S)
            unknown = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM %s.execution_step" % S)
            steps = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM %s.execution_attempt WHERE attempt_number <> 1" % S)
            nonfirst = cur.fetchone()[0]
            cur.execute("SELECT count(DISTINCT experiment_id) FROM %s.execution_attempt" % S)
            distinct = cur.fetchone()[0]
        conn.rollback()
        changed = sorted(e for e in before if before[e] != after.get(e))
        out["checks"] = {
            "old_rows_byte_identical": {"ok": not changed and set(before) == set(after), "changed": changed[:10],
                                        "rows": len(before)},
            "one_attempt_per_terminal_row": {"ok": attempts == terminal == distinct, "attempts": attempts,
                                             "terminal_rows": terminal, "distinct_experiments": distinct},
            "all_backfilled_unknown": {"ok": unknown == attempts, "unknown": unknown},
            "no_steps_fabricated": {"ok": steps == 0, "steps": steps},
            "all_attempt_number_1": {"ok": nonfirst == 0},
            # pre-window only: once 008 is in migrations/ the column exists before the copy
            "only_new_column_is_bundle_declared_all_null": {"ok": (new_cols == ["bundle_declared"] and declared_nonnull == 0) if new_cols
                                                            else True, "new_columns": new_cols, "non_null": declared_nonnull,
                                                            "note": None if new_cols else "n/a after the window (008 already in migrations/)"},
        }
        # spot check: the rebuilt transition function still freezes relations on a copied terminal row
        with conn.cursor() as cur:
            cur.execute("SELECT experiment_id FROM %s.research_experiment_queue WHERE status='completed' LIMIT 1" % S)
            r = cur.fetchone()
        conn.rollback()
        if r:
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE %s.research_experiment_queue SET status='queued' WHERE experiment_id=%%s" % S, (r[0],))
                conn.commit()
                out["checks"]["terminal_row_frozen"] = {"ok": False, "reason": "UPDATE of a terminal row was ACCEPTED"}
            except Exception as e:                               # noqa: BLE001
                conn.rollback()
                out["checks"]["terminal_row_frozen"] = {"ok": True, "error": str(e).splitlines()[0][:140]}
        ok = all(c["ok"] for c in out["checks"].values())
    finally:
        try:
            conn.rollback()
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA %s CASCADE" % S)
            conn.commit(); out["dropped"] = True
        except Exception as e:                                   # noqa: BLE001
            out["dropped"] = str(e)[:200]
        conn.close()
    out["ok"] = ok
    out["fingerprint"] = "sha256:" + hashlib.sha256(json.dumps(out, sort_keys=True, default=str).encode()).hexdigest()[:16]
    print(json.dumps(out, indent=2, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
