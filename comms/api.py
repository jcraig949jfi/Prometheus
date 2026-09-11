"""comms.api -- the inbox, broadcast, receipt and task-queue operations.

Connection: the Evidence Wiki's resolver (evidence_wiki.ew.db.connect), so
comms lives in the same Postgres the seats already reach (prometheus_fire
on M1) with the same credential precedence. Schema name from COMMS_SCHEMA
(default `comms`); tests use a throwaway schema.
"""
from __future__ import annotations

import datetime
import hashlib
import os
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

KINDS = ("prompt", "delegation", "report", "question", "ruling", "ack", "broadcast")
QUEUEABLE = ("prompt", "delegation")
REPO = Path(__file__).resolve().parents[1]


def schema() -> str:
    s = os.environ.get("COMMS_SCHEMA", "comms")
    if not s.replace("_", "").isalnum():
        raise ValueError("unsafe schema name {!r}".format(s))
    return s


def connect():
    import sys
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from evidence_wiki.ew import db as ewdb
    return ewdb.connect()


def init_schema(conn) -> None:
    sql = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8").replace("{schema}", schema())
    cur = conn.cursor(); cur.execute(sql); conn.commit()


def roster() -> List[str]:
    """Every seat directory under roles/ except base-role: the addressable set."""
    return sorted(p.name for p in (REPO / "roles").iterdir() if p.is_dir() and p.name != "base-role")


def _sha(subject: str, body: str) -> str:
    return "sha256:" + hashlib.sha256((subject + "\n" + body).encode("utf-8")).hexdigest()


def post(conn, sender: str, recipients: Sequence[str], kind: str, subject: str, body: str, *,
         reply_to: Optional[int] = None, task_ref: Optional[str] = None, priority: int = 100,
         expires_at: Optional[datetime.datetime] = None) -> int:
    if kind not in KINDS:
        raise ValueError("kind must be one of {}".format(KINDS))
    known = set(roster()) | {"*", "operator"}
    bad = [r for r in recipients if r not in known]
    if bad:
        raise ValueError("unknown recipients {} (roster is roles/*)".format(bad))
    cur = conn.cursor()
    cur.execute("INSERT INTO {s}.messages (sender, recipients, kind, subject, body, sha256, reply_to, task_ref, priority, machine, expires_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id".format(s=schema()),
                (sender, list(recipients), kind, subject, body, _sha(subject, body), reply_to, task_ref, priority, platform.node(), expires_at))
    mid = cur.fetchone()[0]; conn.commit()
    return int(mid)


def broadcast(conn, sender: str, subject: str, body: str, **kw) -> int:
    return post(conn, sender, ["*"], "broadcast", subject, body, **kw)


def inbox(conn, agent: str, *, unseen_only: bool = True, limit: int = 200) -> List[Dict[str, Any]]:
    """Messages addressed to `agent` or to '*', not sent by the agent, in
    priority then age order; unseen unless asked otherwise."""
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id, m.created_at, m.sender, m.recipients, m.kind, m.subject, m.body, m.sha256, m.reply_to, m.task_ref, m.priority,
               r.seen_at, r.queued_at, r.done_at
        FROM {s}.messages m
        LEFT JOIN {s}.receipts r ON r.message_id = m.id AND r.agent = %s
        WHERE (%s = ANY(m.recipients) OR '*' = ANY(m.recipients)) AND m.sender <> %s
          AND (m.expires_at IS NULL OR m.expires_at > now())
          AND (NOT %s OR r.seen_at IS NULL)
        ORDER BY m.priority ASC, m.created_at ASC LIMIT %s""".format(s=schema()),
                (agent, agent, agent, unseen_only, limit))
    cols = ["id", "created_at", "sender", "recipients", "kind", "subject", "body", "sha256", "reply_to", "task_ref", "priority", "seen_at", "queued_at", "done_at"]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def mark_seen(conn, agent: str, ids: Sequence[int]) -> None:
    if not ids:
        return
    cur = conn.cursor()
    for mid in ids:
        cur.execute("INSERT INTO {s}.receipts (message_id, agent, seen_at) VALUES (%s, %s, now()) "
                    "ON CONFLICT (message_id, agent) DO UPDATE SET seen_at = COALESCE({s}.receipts.seen_at, now())".format(s=schema()), (mid, agent))
    conn.commit()


def enqueue(conn, agent: str, message_id: int) -> int:
    """Append a message to the END of the agent's task queue (never reorders)."""
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(position), 0) + 1 FROM {s}.task_queue WHERE agent = %s".format(s=schema()), (agent,))
    pos = cur.fetchone()[0]
    cur.execute("INSERT INTO {s}.task_queue (agent, message_id, position) VALUES (%s, %s, %s) "
                "ON CONFLICT (agent, message_id) DO NOTHING RETURNING position".format(s=schema()), (agent, message_id, pos))
    row = cur.fetchone()
    cur.execute("INSERT INTO {s}.receipts (message_id, agent, seen_at, queued_at) VALUES (%s, %s, now(), now()) "
                "ON CONFLICT (message_id, agent) DO UPDATE SET queued_at = COALESCE({s}.receipts.queued_at, now())".format(s=schema()), (message_id, agent))
    conn.commit()
    return int(row[0]) if row else pos


def tasks(conn, agent: str, status: str = "queued") -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT q.position, q.status, m.id, m.sender, m.kind, m.subject, m.task_ref, m.created_at FROM {s}.task_queue q "
                "JOIN {s}.messages m ON m.id = q.message_id WHERE q.agent = %s AND q.status = %s ORDER BY q.position".format(s=schema()), (agent, status))
    cols = ["position", "status", "id", "sender", "kind", "subject", "task_ref", "created_at"]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def done(conn, agent: str, message_id: int, note: Optional[str] = None) -> None:
    cur = conn.cursor()
    cur.execute("UPDATE {s}.task_queue SET status = 'done', updated_at = now() WHERE agent = %s AND message_id = %s".format(s=schema()), (agent, message_id))
    cur.execute("INSERT INTO {s}.receipts (message_id, agent, seen_at, done_at, note) VALUES (%s, %s, now(), now(), %s) "
                "ON CONFLICT (message_id, agent) DO UPDATE SET done_at = now(), note = COALESCE(EXCLUDED.note, {s}.receipts.note)".format(s=schema()),
                (message_id, agent, note))
    conn.commit()


def sync(conn, agent: str) -> Dict[str, Any]:
    """The boundary call every seat makes before and after each prompt or
    loop iteration: fetch unseen inbox + broadcasts, mark them seen, append
    prompts and delegations to the END of the task queue, and return what
    was new so it can be printed and journaled."""
    new = inbox(conn, agent, unseen_only=True)
    mark_seen(conn, agent, [m["id"] for m in new])
    queued = []
    for m in new:
        if m["kind"] in QUEUEABLE:
            enqueue(conn, agent, m["id"]); queued.append(m["id"])
    return {"agent": agent, "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "new": new, "queued": queued, "queue": tasks(conn, agent)}
