"""The queue state machine.

Every function here takes an open connection and does NOT commit: the caller
owns the transaction boundary, because a transition and its event row must land
together or not at all.

The invariants are enforced in the DATABASE (migrations/001), not here:

  * a unique partial index on `active_singleton` makes two simultaneously
    claimed/running rows impossible, so a race loses with unique_violation
    rather than double-running an experiment;
  * a BEFORE UPDATE trigger freezes terminal rows whole and rejects every
    transition outside the legal graph;
  * an append-only trigger on the events table refuses UPDATE and DELETE.

This module's job is to make the legal moves and write down that it made them.
It never chooses WHICH experiment deserves to run on any ground other than
(priority, created_at) -- there is no scheduling intelligence and there is not
meant to be.
"""
from __future__ import annotations

import json
from typing import Any, Optional

import psycopg2
import psycopg2.errors
import psycopg2.extras

from . import db as _db
from . import spec as _spec

#: Rows in these states hold the single global execution slot.
ACTIVE = ("claimed", "running")
TERMINAL = ("completed", "failed", "cancelled")

COLUMNS = ("experiment_id, created_at, created_by, source_reason, "
           "source_evidence, experiment_spec, spec_hash, status, priority, "
           "not_before, claimed_by, claimed_at, started_at, finished_at, "
           "sfe_experiment_id, pew_reference, result_summary, error")

#: The same list qualified for statements that join (claim_next uses a CTE, so
#: an unqualified experiment_id in RETURNING is ambiguous).
Q_COLUMNS = ", ".join("q." + c.strip() for c in COLUMNS.split(","))


class QueueBusy(RuntimeError):
    """Another experiment already holds the single v0 execution slot."""


def _q(schema: str) -> str:
    return schema + ".research_experiment_queue"


def _e(schema: str) -> str:
    return schema + ".research_experiment_events"


def _json(obj: Any):
    return psycopg2.extras.Json(obj)


def record_event(conn, experiment_id, *, actor: str, event_type: str,
                 payload: Optional[dict] = None, schema: Optional[str] = None):
    s = schema or _db.schema()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO " + _e(s) + " (experiment_id, actor, event_type, "
            "payload) VALUES (%s, %s, %s, %s) RETURNING event_id",
            (str(experiment_id), actor, event_type, _json(payload or {})))
        return cur.fetchone()[0]


# ---------------------------------------------------------------------------
# Admission
# ---------------------------------------------------------------------------

def enqueue(conn, *, created_by: str, source_reason: str,
            experiment_spec: dict, source_evidence: Optional[dict] = None,
            priority: int = 100, not_before=None,
            schema: Optional[str] = None) -> str:
    """Admit one experiment. The spec is validated BEFORE it is stored and is
    stored EXACTLY as supplied -- Vivarium never normalises a caller's spec,
    because a normalised spec is a different experiment with the same name."""
    s = schema or _db.schema()
    _spec.validate(experiment_spec)
    h = _spec.spec_hash(experiment_spec)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO " + _q(s) + " (created_by, source_reason, "
            "source_evidence, experiment_spec, spec_hash, priority, "
            "not_before) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING experiment_id",
            (created_by, source_reason, _json(source_evidence or {}),
             _json(experiment_spec), h, priority, not_before))
        eid = cur.fetchone()[0]
    record_event(conn, eid, actor=created_by, event_type="enqueued",
                 payload={"spec_hash": h, "priority": priority,
                          "not_before": not_before.isoformat()
                          if not_before is not None else None,
                          "source_reason": source_reason}, schema=s)
    return str(eid)


# ---------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------

def get(conn, experiment_id, *, schema: Optional[str] = None):
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT " + COLUMNS + " FROM " + _q(s) +
                    " WHERE experiment_id = %s", (str(experiment_id),))
        return cur.fetchone()


def active(conn, *, schema: Optional[str] = None):
    """The single claimed/running row, or None. At most one can exist."""
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT " + COLUMNS + " FROM " + _q(s) +
                    " WHERE status IN ('claimed','running')")
        return cur.fetchone()


def next_eligible(conn, *, schema: Optional[str] = None):
    """What claim_next() would take right now. A read; it locks nothing."""
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT " + COLUMNS + " FROM " + _q(s) +
                    " WHERE status = 'queued' AND (not_before IS NULL OR "
                    "not_before <= now()) ORDER BY priority ASC, created_at ASC "
                    "LIMIT 1")
        return cur.fetchone()


def most_recent_finished(conn, *, schema: Optional[str] = None):
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT " + COLUMNS + " FROM " + _q(s) +
                    " WHERE finished_at IS NOT NULL "
                    "ORDER BY finished_at DESC LIMIT 1")
        return cur.fetchone()


def listing(conn, *, status: Optional[str] = None, limit: int = 50,
            schema: Optional[str] = None):
    s = schema or _db.schema()
    sql = "SELECT " + COLUMNS + " FROM " + _q(s)
    args: list = []
    if status:
        sql += " WHERE status = %s"
        args.append(status)
    sql += " ORDER BY created_at DESC LIMIT %s"
    args.append(limit)
    with _db.dict_cur(conn) as cur:
        cur.execute(sql, args)
        return cur.fetchall()


def events(conn, experiment_id, *, schema: Optional[str] = None):
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT event_id, occurred_at, actor, event_type, payload "
                    "FROM " + _e(s) + " WHERE experiment_id = %s "
                    "ORDER BY event_id", (str(experiment_id),))
        return cur.fetchall()


def counts(conn, *, schema: Optional[str] = None) -> dict:
    s = schema or _db.schema()
    with conn.cursor() as cur:
        cur.execute("SELECT status, count(*) FROM " + _q(s) + " GROUP BY status")
        return {row[0]: row[1] for row in cur.fetchall()}


def stranded(conn, *, stale_after_s: float = 900.0,
             schema: Optional[str] = None):
    """Claimed/running rows whose worker has not heartbeated recently.

    v0 REPORTS these and does nothing else. Guessing that a stranded run is
    safe to repeat is exactly the guess that double-runs an experiment; the
    operator releases it explicitly with release_stranded()."""
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute(
            "SELECT q.experiment_id, q.status, q.claimed_by, q.claimed_at, "
            "       q.started_at, q.sfe_experiment_id, h.last_seen, "
            "       h.host, h.pid "
            "  FROM " + _q(s) + " q "
            "  LEFT JOIN " + s + ".worker_heartbeat h "
            "         ON h.worker_id = q.claimed_by "
            " WHERE q.status IN ('claimed','running') "
            "   AND (h.last_seen IS NULL "
            "        OR h.last_seen < now() - make_interval(secs => %s))",
            (stale_after_s,))
        return cur.fetchall()


# ---------------------------------------------------------------------------
# Transitions
# ---------------------------------------------------------------------------

def claim_next(conn, worker_id: str, *, schema: Optional[str] = None):
    """Atomically take the next eligible experiment, or return None.

    FOR UPDATE SKIP LOCKED is used even though v0 permits a single worker: the
    locking has to be right BEFORE a second worker exists, not after. If two
    workers select different rows and both try to become active, the unique
    partial index rejects the loser, which is reported as QueueBusy.
    """
    s = schema or _db.schema()
    sql = (
        "WITH nxt AS ("
        "  SELECT experiment_id FROM " + _q(s) +
        "   WHERE status = 'queued' "
        "     AND (not_before IS NULL OR not_before <= now()) "
        "   ORDER BY priority ASC, created_at ASC "
        "   FOR UPDATE SKIP LOCKED LIMIT 1) "
        "UPDATE " + _q(s) + " q "
        "   SET status = 'claimed', claimed_by = %s, claimed_at = now() "
        "  FROM nxt WHERE q.experiment_id = nxt.experiment_id "
        "RETURNING " + Q_COLUMNS)
    with _db.dict_cur(conn) as cur:
        try:
            cur.execute(sql, (worker_id,))
        except psycopg2.errors.UniqueViolation as exc:
            raise QueueBusy("another experiment holds the execution slot") from exc
        row = cur.fetchone()
    if row is None:
        return None
    record_event(conn, row["experiment_id"], actor=worker_id,
                 event_type="claimed",
                 payload={"spec_hash": row["spec_hash"]}, schema=s)
    return row


def mark_running(conn, experiment_id, *, worker_id: str,
                 sfe_experiment_id: Optional[str] = None,
                 detail: Optional[dict] = None,
                 schema: Optional[str] = None):
    """Cross into `running` the moment real execution begins -- not when the
    row is claimed, so a crash between the two is legible as a crash before
    execution rather than during it."""
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute(
            "UPDATE " + _q(s) + " SET status='running', started_at=now(), "
            "sfe_experiment_id = COALESCE(%s, sfe_experiment_id) "
            "WHERE experiment_id = %s AND status = 'claimed' AND claimed_by = %s "
            "RETURNING " + COLUMNS,
            (sfe_experiment_id, str(experiment_id), worker_id))
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("cannot mark running: %s is not claimed by %s"
                           % (experiment_id, worker_id))
    record_event(conn, experiment_id, actor=worker_id, event_type="running",
                 payload={"sfe_experiment_id": sfe_experiment_id,
                          **(detail or {})}, schema=s)
    return row


def mark_completed(conn, experiment_id, *, worker_id: str,
                   result_summary: dict,
                   sfe_experiment_id: Optional[str] = None,
                   pew_reference: Optional[str] = None,
                   schema: Optional[str] = None):
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute(
            "UPDATE " + _q(s) + " SET status='completed', finished_at=now(), "
            "result_summary=%s, "
            "sfe_experiment_id = COALESCE(%s, sfe_experiment_id), "
            "pew_reference = COALESCE(%s, pew_reference) "
            "WHERE experiment_id = %s AND status = 'running' AND claimed_by = %s "
            "RETURNING " + COLUMNS,
            (_json(result_summary), sfe_experiment_id, pew_reference,
             str(experiment_id), worker_id))
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("cannot complete: %s is not running under %s"
                           % (experiment_id, worker_id))
    record_event(conn, experiment_id, actor=worker_id, event_type="completed",
                 payload={"sfe_experiment_id": row["sfe_experiment_id"],
                          "pew_reference": row["pew_reference"],
                          "result_summary": result_summary}, schema=s)
    return row


def mark_failed(conn, experiment_id, *, worker_id: str, error: str,
                result_summary: Optional[dict] = None,
                sfe_experiment_id: Optional[str] = None,
                schema: Optional[str] = None):
    """Preserve the failure. There is no automatic retry: a failed row stays
    failed and stays visible until a human decides otherwise."""
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute(
            "UPDATE " + _q(s) + " SET status='failed', finished_at=now(), "
            "error=%s, result_summary = COALESCE(%s, result_summary), "
            "sfe_experiment_id = COALESCE(%s, sfe_experiment_id) "
            "WHERE experiment_id = %s AND status IN ('claimed','running') "
            "  AND claimed_by = %s RETURNING " + COLUMNS,
            (error[:20000], _json(result_summary) if result_summary else None,
             sfe_experiment_id, str(experiment_id), worker_id))
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("cannot fail: %s is not active under %s"
                           % (experiment_id, worker_id))
    record_event(conn, experiment_id, actor=worker_id, event_type="failed",
                 payload={"error": error[:4000],
                          "sfe_experiment_id": row["sfe_experiment_id"]},
                 schema=s)
    return row


def cancel(conn, experiment_id, *, actor: str, reason: str,
           schema: Optional[str] = None):
    """Cancel a QUEUED experiment. A claimed or running one is deliberately
    NOT cancellable: the worker is mid-flight and the only honest records are
    `completed`, `failed`, or an operator release."""
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute(
            "UPDATE " + _q(s) + " SET status='cancelled', finished_at=now(), "
            "error=%s WHERE experiment_id = %s AND status = 'queued' "
            "RETURNING " + COLUMNS,
            ("cancelled: " + reason, str(experiment_id)))
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("cannot cancel %s: it is not queued" % experiment_id)
    record_event(conn, experiment_id, actor=actor, event_type="cancelled",
                 payload={"reason": reason}, schema=s)
    return row


def release_stranded(conn, experiment_id, *, actor: str, reason: str,
                     schema: Optional[str] = None):
    """The explicit operator recovery for a stranded claimed/running row.

    It resolves to `failed`, never back to `queued`. Requeueing would mean
    asserting the experiment did not run, which nothing in the queue can know
    -- SFE and PEW are where that is checked, by a person."""
    s = schema or _db.schema()
    row = get(conn, experiment_id, schema=s)
    if row is None:
        raise RuntimeError("no such experiment %s" % experiment_id)
    if row["status"] not in ACTIVE:
        raise RuntimeError("cannot release %s: status is %s"
                           % (experiment_id, row["status"]))
    with _db.dict_cur(conn) as cur:
        if row["status"] == "claimed":
            cur.execute(
                "UPDATE " + _q(s) + " SET status='failed', finished_at=now(), "
                "error=%s WHERE experiment_id=%s AND status='claimed' "
                "RETURNING " + COLUMNS,
                ("STRANDED, released by operator: " + reason,
                 str(experiment_id)))
        else:
            cur.execute(
                "UPDATE " + _q(s) + " SET status='failed', finished_at=now(), "
                "error=%s WHERE experiment_id=%s AND status='running' "
                "RETURNING " + COLUMNS,
                ("STRANDED, released by operator: " + reason,
                 str(experiment_id)))
        out = cur.fetchone()
    record_event(conn, experiment_id, actor=actor,
                 event_type="stranded_released",
                 payload={"reason": reason, "from_status": row["status"],
                          "claimed_by": row["claimed_by"],
                          "sfe_experiment_id": row["sfe_experiment_id"]},
                 schema=s)
    return out


# ---------------------------------------------------------------------------
# Worker liveness
# ---------------------------------------------------------------------------

def heartbeat(conn, worker_id: str, *, host: str, pid: int,
              current_experiment=None, build: Optional[dict] = None,
              schema: Optional[str] = None) -> None:
    s = schema or _db.schema()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO " + s + ".worker_heartbeat "
            "(worker_id, host, pid, current_experiment, build) "
            "VALUES (%s,%s,%s,%s,%s) "
            "ON CONFLICT (worker_id) DO UPDATE SET last_seen = now(), "
            "  host = EXCLUDED.host, pid = EXCLUDED.pid, "
            "  current_experiment = EXCLUDED.current_experiment, "
            "  build = EXCLUDED.build",
            (worker_id, host, pid,
             str(current_experiment) if current_experiment else None,
             _json(build or {})))


def workers(conn, *, schema: Optional[str] = None):
    s = schema or _db.schema()
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT worker_id, host, pid, started_at, last_seen, "
                    "current_experiment, build FROM " + s + ".worker_heartbeat "
                    "ORDER BY last_seen DESC")
        return cur.fetchall()
