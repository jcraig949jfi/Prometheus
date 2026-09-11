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
TIERS = {"light": ("haiku", "sonnet"), "heavy": ("opus", "fable", "mythos")}
HARNESS_ENV_KEYS = ("CLAUDE_CODE_SESSION_ID", "CLAUDE_EFFORT", "CLAUDE_CODE_ENTRYPOINT", "CLAUDECODE", "CLAUDE_CODE_CHILD_SESSION")
ONLINE_MINUTES = 30
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
    touch(conn, sender)
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
    touch(conn, agent, last_message_id=max([m["id"] for m in new], default=None), synced=True)
    queued = []
    for m in new:
        if m["kind"] in QUEUEABLE:
            enqueue(conn, agent, m["id"]); queued.append(m["id"])
    return {"agent": agent, "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "new": new, "queued": queued, "queue": tasks(conn, agent)}


# --------------------------------------------------------------------------
# Agents: who is online, for delegation
# --------------------------------------------------------------------------
def tier_for(model: Optional[str]) -> str:
    m = (model or "").lower()
    for tier, names in TIERS.items():
        if any(n in m for n in names):
            return tier
    return "unknown"


def harness_metadata() -> Dict[str, Any]:
    """What the harness exposes at boot: names and non-secret values only.
    Tokens and sockets are never read."""
    out = {k: os.environ.get(k) for k in HARNESS_ENV_KEYS if os.environ.get(k) is not None}
    out["python"] = platform.python_version()
    out["platform"] = platform.platform()
    return out


def boot(conn, agent: str, *, model: Optional[str] = None, capabilities: Sequence[str] = (), status: str = "active",
         session_id: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Record a bootstrap: workspace receipt (base_sha, branch, worktree_path),
    machine, model and tier, capabilities, session and harness metadata."""
    if agent not in roster():
        raise ValueError("unknown agent {!r}".format(agent))
    ws: Dict[str, Any] = {}
    try:
        import sys
        if str(REPO) not in sys.path:
            sys.path.insert(0, str(REPO))
        from archaeon import workspace as W
        ws = W.receipt()
    except Exception as exc:                                     # noqa: BLE001
        ws = {"error": "{}: {}".format(type(exc).__name__, str(exc)[:120])}
    import json as _json
    sid = session_id or os.environ.get("CLAUDE_CODE_SESSION_ID")
    harness = harness_metadata()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO {s}.agents (agent, status, last_active_at, last_bootstrap_at, boot_count, machine, base_sha, branch, worktree_path,
                                model, tier, capabilities, session_id, harness, status_json, updated_at)
        VALUES (%s, %s, now(), now(), 1, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, now())
        ON CONFLICT (agent) DO UPDATE SET
            status = EXCLUDED.status, last_active_at = now(), last_bootstrap_at = now(),
            boot_count = {s}.agents.boot_count + 1, machine = EXCLUDED.machine, base_sha = EXCLUDED.base_sha,
            branch = EXCLUDED.branch, worktree_path = EXCLUDED.worktree_path,
            model = COALESCE(EXCLUDED.model, {s}.agents.model), tier = CASE WHEN EXCLUDED.model IS NULL THEN {s}.agents.tier ELSE EXCLUDED.tier END,
            capabilities = CASE WHEN cardinality(EXCLUDED.capabilities) = 0 THEN {s}.agents.capabilities ELSE EXCLUDED.capabilities END,
            session_id = COALESCE(EXCLUDED.session_id, {s}.agents.session_id), harness = EXCLUDED.harness,
            status_json = {s}.agents.status_json || EXCLUDED.status_json, updated_at = now()""".format(s=schema()),
                (agent, status, platform.node(), ws.get("base_sha"), ws.get("branch"), ws.get("worktree_path"),
                 model, tier_for(model), list(capabilities), sid, _json.dumps(harness), _json.dumps(extra or {})))
    conn.commit()
    return dict(agent=agent, status=status, machine=platform.node(), workspace=ws, model=model, tier=tier_for(model),
                capabilities=list(capabilities), session_id=sid, harness=harness)


def touch(conn, agent: str, *, last_message_id: Optional[int] = None, synced: bool = False) -> None:
    """Any comms call by a seat marks it active; a sync also advances the
    last-seen pointer. Seats not yet booted get a minimal row."""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO {s}.agents (agent, status, last_active_at, last_sync_at, last_message_id, machine, updated_at)
        VALUES (%s, 'active', now(), CASE WHEN %s THEN now() ELSE NULL END, %s, %s, now())
        ON CONFLICT (agent) DO UPDATE SET
            last_active_at = now(),
            last_sync_at = CASE WHEN EXCLUDED.last_sync_at IS NULL THEN {s}.agents.last_sync_at ELSE EXCLUDED.last_sync_at END,
            last_message_id = GREATEST(COALESCE({s}.agents.last_message_id, 0), COALESCE(EXCLUDED.last_message_id, 0)),
            status = CASE WHEN {s}.agents.status IN ('paused', 'retired') THEN {s}.agents.status ELSE 'active' END,
            updated_at = now()""".format(s=schema()), (agent, synced, last_message_id, platform.node()))
    conn.commit()


def set_status(conn, agent: str, status: str, note: Optional[str] = None) -> None:
    import json as _json
    cur = conn.cursor()
    cur.execute("INSERT INTO {s}.agents (agent, status, updated_at, status_json) VALUES (%s, %s, now(), %s::jsonb) "
                "ON CONFLICT (agent) DO UPDATE SET status = EXCLUDED.status, updated_at = now(), "
                "status_json = {s}.agents.status_json || EXCLUDED.status_json".format(s=schema()),
                (agent, status, _json.dumps({"status_note": note} if note else {})))
    conn.commit()


def who(conn, *, online_minutes: int = ONLINE_MINUTES) -> List[Dict[str, Any]]:
    """Every seat with its online flag (active within `online_minutes`),
    tier, capabilities, queue depth and unseen count -- the delegation view."""
    cur = conn.cursor()
    cur.execute("""
        SELECT a.agent, a.status, a.last_active_at, a.last_sync_at, a.last_message_id, a.last_bootstrap_at, a.boot_count,
               a.machine, a.base_sha, a.model, a.tier, a.capabilities,
               (a.last_active_at IS NOT NULL AND a.last_active_at > now() - make_interval(mins => %s)) AS online,
               (SELECT count(*) FROM {s}.task_queue q WHERE q.agent = a.agent AND q.status = 'queued') AS queued,
               (SELECT count(*) FROM {s}.messages m LEFT JOIN {s}.receipts r ON r.message_id = m.id AND r.agent = a.agent
                 WHERE (a.agent = ANY(m.recipients) OR '*' = ANY(m.recipients)) AND m.sender <> a.agent AND r.seen_at IS NULL) AS unseen
        FROM {s}.agents a ORDER BY online DESC, a.last_active_at DESC NULLS LAST, a.agent""".format(s=schema()), (online_minutes,))
    cols = ["agent", "status", "last_active_at", "last_sync_at", "last_message_id", "last_bootstrap_at", "boot_count", "machine",
            "base_sha", "model", "tier", "capabilities", "online", "queued", "unseen"]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    known = {r["agent"] for r in rows}
    for seat in roster():
        if seat not in known:
            rows.append({"agent": seat, "status": "never_booted", "online": False, "queued": 0, "unseen": None, "tier": "unknown",
                         "capabilities": [], "model": None, "last_active_at": None, "last_sync_at": None, "last_message_id": None,
                         "last_bootstrap_at": None, "boot_count": 0, "machine": None, "base_sha": None})
    return rows
