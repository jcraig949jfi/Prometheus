"""fabric.store -- the durable core of the Prometheus Agent Fabric (v0).

Every operation is one database transaction against schema {FABRIC_SCHEMA or
"fabric"} in the program's canonical Postgres (the one comms uses, reached
through the same credential resolver and identity check). The wire API
(fabric.gateway) and the CLI (fabric.cli) are thin callers of this module;
nothing canonical lives in them.

Invariants the database enforces (schema.sql), not the callers:
  - at most one RUNNING Attempt per Task          (attempts_one_live)
  - at most one unreleased lease per resource     (leases_one_holder)
  - one Task per (principal, idempotency_key)      (UNIQUE)
  - every expiry is measured on the database's clock (now())
Invariants this module enforces:
  - terminal Task states (completed, canceled, failed, rejected) never change
  - a claim takes the Task and all its resource leases in ONE transaction, or
    nothing: a busy resource leaves the Task available and moves on
  - an Attempt can finish only while it is still RUNNING (a fenced, expired or
    abandoned Attempt that comes back late cannot complete the Task)
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
TERMINAL = ("completed", "canceled", "failed", "rejected")
EXECUTORS = ("claude", "script", "synthetic")
MAX_BLOB_BYTES = 16 * 1024 * 1024
ONLINE_SECONDS = 120


class FabricError(Exception):
    pass


class NotCancelable(FabricError):
    pass


class NotFound(FabricError):
    pass


# ------------------------------------------------------------------ connection
def schema() -> str:
    s = os.environ.get("FABRIC_SCHEMA", "fabric")
    if not s.replace("_", "").isalnum():
        raise ValueError("unsafe schema name {!r}".format(s))
    return s


# DEF-ODY-019: libpq connections had no TCP keepalive or user timeout. After a network blip, a half-open socket made
# every store call wait forever (the ubu001 workers stopped claiming for ~36 min, 2026-09-30). These options make a
# dead peer raise within about a minute, so the callers' existing reconnect paths run.
TCP_OPTS = (("SO_KEEPALIVE", 1, "SOL_SOCKET"), ("TCP_KEEPIDLE", 30, "IPPROTO_TCP"), ("TCP_KEEPINTVL", 10, "IPPROTO_TCP"),
            ("TCP_KEEPCNT", 3, "IPPROTO_TCP"), ("TCP_USER_TIMEOUT", 60000, "IPPROTO_TCP"))


def _harden_socket(conn) -> None:
    """Set keepalive + TCP_USER_TIMEOUT on the connection's socket (Linux; options a platform lacks are skipped)."""
    import socket
    try:
        fd = conn.fileno()
    except Exception:
        return
    s = socket.socket(fileno=os.dup(fd))                    # a dup of the same socket: options apply to it
    try:
        for name, val, level in TCP_OPTS:
            if hasattr(socket, name):
                try:
                    s.setsockopt(getattr(socket, level), getattr(socket, name), val)
                except OSError:
                    pass
    finally:
        s.close()


def connect(require_schema: bool = True):
    """The canonical store, through comms's resolver and identity guard: a
    fabric on the wrong cluster fails closed (WrongEnvironment), exactly as
    comms does. Never falls back to anything local."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from evidence_wiki.ew import db as ewdb
    from comms import identity
    conn = ewdb.connect()
    _harden_socket(conn)
    try:
        identity.require(conn, identity.current_environment())
    except identity.WrongEnvironment:
        conn.close()
        raise
    if require_schema:
        cur = conn.cursor()
        cur.execute("select to_regclass(%s)", (schema() + ".tasks",))
        if cur.fetchone()[0] is None:
            conn.close()
            raise FabricError("no {}.tasks table in the canonical store; run `python -m fabric init`".format(schema()))
    return conn


def init_schema(conn) -> None:
    sql = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8").replace("{schema}", schema())
    cur = conn.cursor(); cur.execute(sql); conn.commit()


def new_id(prefix: str) -> str:
    return "{}-{}".format(prefix, secrets.token_hex(6))


def _t(name: str) -> str:
    return "{}.{}".format(schema(), name)


def _event(cur, actor: str, kind: str, task_id=None, attempt_id=None, lease_id=None, **detail) -> None:
    cur.execute("INSERT INTO {} (task_id, attempt_id, lease_id, actor, kind, detail) VALUES (%s,%s,%s,%s,%s,%s)".format(_t("events")),
                (task_id, attempt_id, lease_id, actor, kind, json.dumps(detail, default=str)))


def _rows(cur) -> List[Dict[str, Any]]:
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


# ------------------------------------------------------------------ agents
def register_instance(conn, agent: str, kind: str, instance: str, host: str, *, capabilities: Sequence[str] = (),
                      executors: Sequence[str] = (), model: Optional[str] = None, capacity: int = 1,
                      endpoint: Optional[str] = None, description: str = "") -> None:
    cur = conn.cursor()
    cur.execute("INSERT INTO {} (agent, kind, description) VALUES (%s,%s,%s) "
                "ON CONFLICT (agent) DO UPDATE SET description = EXCLUDED.description".format(_t("agents")),
                (agent, kind, description))
    cur.execute("INSERT INTO {} (agent, instance, host, capabilities, executors, model, capacity, endpoint, status, started_at, last_seen_at) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'online',now(),now()) ON CONFLICT (agent, instance) DO UPDATE SET "
                "host=EXCLUDED.host, capabilities=EXCLUDED.capabilities, executors=EXCLUDED.executors, model=EXCLUDED.model, "
                "capacity=EXCLUDED.capacity, endpoint=EXCLUDED.endpoint, status='online', last_seen_at=now()".format(_t("agent_instances")),
                (agent, instance, host, list(capabilities), list(executors), model, capacity, endpoint))
    _event(cur, "{}[{}]".format(agent, instance), "agent_online", host=host, capabilities=list(capabilities))
    conn.commit()


def touch_instance(conn, agent: str, instance: str, status: str = "online") -> None:
    cur = conn.cursor()
    cur.execute("UPDATE {} SET last_seen_at = now(), status = %s WHERE agent = %s AND instance = %s".format(_t("agent_instances")),
                (status, agent, instance))
    conn.commit()


def agents(conn) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT i.agent, a.kind, a.description, i.instance, i.host, i.capabilities, i.executors, i.model, i.capacity, "
                "i.endpoint, i.status, i.last_seen_at, (i.status <> 'offline' AND i.last_seen_at > now() - make_interval(secs => %s)) AS live "
                "FROM {} i JOIN {} a USING (agent) ORDER BY i.agent, i.last_seen_at DESC".format(_t("agent_instances"), _t("agents")),
                (ONLINE_SECONDS,))
    return _rows(cur)


# ------------------------------------------------------------------ tasks
def submit(conn, principal: str, instruction: str, executor: str, *, title: str = "", required_caps: Sequence[str] = (),
           resources: Sequence[str] = (), host_affinity: Optional[str] = None, target_agent: Optional[str] = None,
           thread_id: Optional[str] = None, campaign_id: Optional[str] = None, experiment_id: Optional[str] = None,
           base_sha: Optional[str] = None, params: Optional[Dict[str, Any]] = None, priority: int = 0, max_attempts: int = 3,
           idempotency_key: Optional[str] = None, context_id: Optional[str] = None,
           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a Task, or return the existing one for (principal, idempotency_key)."""
    if executor not in EXECUTORS:
        raise FabricError("executor must be one of {}".format(EXECUTORS))
    cur = conn.cursor()
    tid = new_id("tsk")
    cur.execute("INSERT INTO {} (task_id, context_id, principal, target_agent, thread_id, campaign_id, experiment_id, base_sha, title, "
                "instruction, executor, params, required_caps, resources, host_affinity, priority, max_attempts, idempotency_key, metadata) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (principal, idempotency_key) DO NOTHING RETURNING task_id".format(_t("tasks")),
                (tid, context_id or new_id("ctx"), principal, target_agent, thread_id, campaign_id, experiment_id, base_sha, title,
                 instruction, executor, json.dumps(params or {}), list(required_caps), list(resources), host_affinity, priority,
                 max_attempts, idempotency_key, json.dumps(metadata or {})))
    row = cur.fetchone()
    if row is None:
        cur.execute("SELECT task_id, state FROM {} WHERE principal = %s AND idempotency_key = %s".format(_t("tasks")),
                    (principal, idempotency_key))
        existing = cur.fetchone(); conn.commit()
        return {"task_id": existing[0], "created": False, "state": existing[1]}
    cur.execute("INSERT INTO {} (task_id, message_id, role, parts) VALUES (%s,%s,'user',%s)".format(_t("messages")),
                (tid, idempotency_key or new_id("msg"), json.dumps([{"text": instruction}])))
    _event(cur, principal, "submitted", task_id=tid, executor=executor, required_caps=list(required_caps),
           resources=list(resources), thread_id=thread_id, idempotency_key=idempotency_key)
    conn.commit()
    return {"task_id": tid, "created": True, "state": "submitted"}


def get_task(conn, task_id: str) -> Dict[str, Any]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM {} WHERE task_id = %s".format(_t("tasks")), (task_id,))
    rows = _rows(cur)
    if not rows:
        raise NotFound(task_id)
    t = rows[0]
    cur.execute("SELECT attempt_id, seq, agent, instance, host, model, status, base_sha, worktree, lease_ids, exit_code, error, "
                "started_at, heartbeat_at, expires_at, ended_at, env_receipt FROM {} WHERE task_id = %s ORDER BY seq".format(_t("attempts")),
                (task_id,))
    t["attempts"] = _rows(cur)
    cur.execute("SELECT artifact_id, attempt_id, name, kind, media_type, sha256, size_bytes, uri, metadata, created_at FROM {} "
                "WHERE task_id = %s ORDER BY created_at, artifact_id".format(_t("artifacts")), (task_id,))
    t["artifacts"] = _rows(cur)
    conn.commit()
    return t


def list_tasks(conn, *, state: Optional[str] = None, principal: Optional[str] = None, thread_id: Optional[str] = None,
               context_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    cond, args = [], []
    for col, v in (("state", state), ("principal", principal), ("thread_id", thread_id), ("context_id", context_id)):
        if v:
            cond.append("{} = %s".format(col)); args.append(v)
    cur = conn.cursor()
    cur.execute("SELECT task_id, context_id, principal, thread_id, title, executor, required_caps, resources, state, waiting_reason, "
                "attempts_made, max_attempts, current_attempt, priority, created_at, updated_at FROM {} {} "
                "ORDER BY created_at DESC LIMIT %s".format(_t("tasks"), ("WHERE " + " AND ".join(cond)) if cond else ""),
                tuple(args) + (limit,))
    rows = _rows(cur); conn.commit()
    return rows


def events(conn, task_id: str) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT event_id, at, attempt_id, lease_id, actor, kind, detail FROM {} WHERE task_id = %s ORDER BY event_id".format(_t("events")),
                (task_id,))
    rows = _rows(cur); conn.commit()
    return rows


def cancel(conn, task_id: str, actor: str) -> Dict[str, Any]:
    """A2A CancelTask: an unclaimed Task becomes canceled at once; a working
    Task is marked cancel_requested (its worker stops at the next heartbeat);
    a terminal Task refuses (NotCancelable)."""
    cur = conn.cursor()
    cur.execute("SELECT state FROM {} WHERE task_id = %s FOR UPDATE".format(_t("tasks")), (task_id,))
    row = cur.fetchone()
    if row is None:
        conn.rollback(); raise NotFound(task_id)
    state = row[0]
    if state in TERMINAL:
        conn.rollback(); raise NotCancelable("task {} is {}".format(task_id, state))
    if state in ("submitted", "input-required"):
        cur.execute("UPDATE {} SET state='canceled', cancel_requested=TRUE, terminal_at=now(), updated_at=now(), waiting_reason=NULL "
                    "WHERE task_id=%s".format(_t("tasks")), (task_id,))
        _event(cur, actor, "canceled", task_id=task_id, from_state=state)
        conn.commit()
        return {"task_id": task_id, "state": "canceled"}
    cur.execute("UPDATE {} SET cancel_requested=TRUE, updated_at=now() WHERE task_id=%s".format(_t("tasks")), (task_id,))
    _event(cur, actor, "cancel_requested", task_id=task_id)
    conn.commit()
    return {"task_id": task_id, "state": state, "cancel_requested": True}


# ------------------------------------------------------------------ leases
def _expire_stale_lease(cur, resource: str, actor: str) -> None:
    cur.execute("UPDATE {} SET released_at = now(), release_reason = 'expired' WHERE resource = %s AND released_at IS NULL "
                "AND expires_at < now() RETURNING lease_id, attempt_id, holder".format(_t("leases")), (resource,))
    for lid, aid, holder in cur.fetchall():
        _event(cur, actor, "lease_expired", attempt_id=aid, lease_id=lid, resource=resource, holder=holder)


# ---------------------------------------------------------------- leases
# The fabric lease is the ONE authority (operator ruling 2026-09-28). The ARC3 legacy detection (comms LEASE records,
# ~/ananke_runs/leases/*.json host files) was removed on 2026-09-30 under CWO 2026-09-30 (Odysseus NEXT), after the
# lease cutover 8370083ae was merged by every helper user (Archaeon #902, Nestor #904, Ananke #934). See FREEZE.md.


def _try_lease(cur, resource: str, holder: str, host: str, purpose: str, ttl_s: int, actor: str,
               attempt_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Inside the caller's transaction: expire a stale holder, then insert.
    A unique violation means BUSY; the savepoint keeps the transaction usable."""
    _expire_stale_lease(cur, resource, actor)
    lid, token = new_id("lse"), secrets.token_hex(8)
    cur.execute("SAVEPOINT lease_try")
    try:
        cur.execute("INSERT INTO {} (lease_id, resource, attempt_id, holder, host, purpose, token, expires_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s, now() + make_interval(secs => %s)) RETURNING expires_at".format(_t("leases")),
                    (lid, resource, attempt_id, holder, host, purpose, token, ttl_s))
        exp = cur.fetchone()[0]
        cur.execute("RELEASE SAVEPOINT lease_try")
    except Exception as e:  # psycopg2.errors.UniqueViolation
        if getattr(e, "pgcode", None) != "23505":
            raise
        cur.execute("ROLLBACK TO SAVEPOINT lease_try")
        return None
    _event(cur, actor, "lease_acquired", attempt_id=attempt_id, lease_id=lid, resource=resource, holder=holder, purpose=purpose)
    return {"lease_id": lid, "token": token, "resource": resource, "expires_at": exp}


def lease_holder(cur, resource: str) -> Optional[Dict[str, Any]]:
    cur.execute("SELECT lease_id, holder, host, purpose, attempt_id, acquired_at, expires_at FROM {} WHERE resource = %s "
                "AND released_at IS NULL".format(_t("leases")), (resource,))
    rows = _rows(cur)
    return rows[0] if rows else None


def lease_acquire(conn, resource: str, holder: str, host: str, *, purpose: str = "", ttl_s: int = 3600) -> Dict[str, Any]:
    """A lease held by hand (a principal or a seat outside the fabric). Fails
    closed: an unreachable store raises; it never falls back to a file."""
    cur = conn.cursor()
    got = _try_lease(cur, resource, holder, host, purpose, ttl_s, holder)
    if got is None:
        h = lease_holder(cur, resource); conn.commit()
        return {"result": "BUSY", "resource": resource, "held_by": h}
    conn.commit()
    return dict(got, result="ACQUIRED")


def lease_renew(conn, lease_id: str, token: str, ttl_s: int = 3600) -> bool:
    cur = conn.cursor()
    cur.execute("UPDATE {} SET renewed_at = now(), expires_at = now() + make_interval(secs => %s) WHERE lease_id = %s AND token = %s "
                "AND released_at IS NULL AND expires_at > now() RETURNING lease_id".format(_t("leases")), (ttl_s, lease_id, token))
    ok = cur.fetchone() is not None; conn.commit()
    return ok


def lease_release(conn, lease_id: str, token: str, actor: str, reason: str = "released") -> bool:
    cur = conn.cursor()
    cur.execute("UPDATE {} SET released_at = now(), release_reason = %s WHERE lease_id = %s AND token = %s AND released_at IS NULL "
                "RETURNING resource, attempt_id".format(_t("leases")), (reason, lease_id, token))
    row = cur.fetchone()
    if row:
        _event(cur, actor, "lease_released", attempt_id=row[1], lease_id=lease_id, resource=row[0], reason=reason)
    conn.commit()
    return row is not None


def leases(conn, *, active_only: bool = True) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT lease_id, resource, holder, host, purpose, attempt_id, acquired_at, renewed_at, expires_at, released_at, "
                "release_reason, (released_at IS NULL AND expires_at < now()) AS stale FROM {} {} ORDER BY acquired_at DESC LIMIT 200"
                .format(_t("leases"), "WHERE released_at IS NULL" if active_only else ""))
    rows = _rows(cur); conn.commit()
    return rows


def _release_attempt_leases(cur, attempt_id: str, actor: str, reason: str) -> None:
    cur.execute("UPDATE {} SET released_at = now(), release_reason = %s WHERE attempt_id = %s AND released_at IS NULL "
                "RETURNING lease_id, resource".format(_t("leases")), (reason, attempt_id))
    for lid, res in cur.fetchall():
        _event(cur, actor, "lease_released", attempt_id=attempt_id, lease_id=lid, resource=res, reason=reason)


# ------------------------------------------------------------------ claim / heartbeat / finish
def claim(conn, agent: str, instance: str, host: str, capabilities: Sequence[str], executors: Sequence[str], *,
          ttl_s: int = 90, scan: int = 25, lease_ttl_s: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Pull one compatible Task. In ONE transaction: lock candidate Tasks
    (SKIP LOCKED, so racing workers never block or double-claim), and for the
    first whose resources can all be leased, create the Attempt and move the
    Task to working. A Task whose resource is busy stays submitted with a
    waiting_reason, and the worker moves on to the next candidate."""
    actor = "{}[{}]".format(agent, instance)
    cur = conn.cursor()
    cur.execute("SELECT task_id, resources, attempts_made, base_sha, waiting_reason FROM {} WHERE state = 'submitted' "
                "AND NOT cancel_requested AND (target_agent IS NULL OR target_agent = %s) AND required_caps <@ %s::text[] "
                "AND executor = ANY(%s) AND (host_affinity IS NULL OR host_affinity = %s) "
                "ORDER BY priority DESC, created_at LIMIT %s FOR UPDATE SKIP LOCKED".format(_t("tasks")),
                (agent, list(capabilities), list(executors), host, scan))
    for task_id, resources, made, base_sha, waiting in cur.fetchall():
        aid = new_id("att")
        got, busy = [], None
        # the Attempt row must exist before leases reference it
        cur.execute("SAVEPOINT claim_try")
        cur.execute("INSERT INTO {} (attempt_id, task_id, seq, agent, instance, host, status, base_sha, expires_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,'running',%s, now() + make_interval(secs => %s))".format(_t("attempts")),
                    (aid, task_id, made + 1, agent, instance, host, base_sha, ttl_s))
        for res in resources or []:
            lease = _try_lease(cur, res, actor, host, "attempt {} of {}".format(aid, task_id), lease_ttl_s or ttl_s, actor, attempt_id=aid)
            if lease is None:
                busy = res
                break
            got.append(lease)
        if busy is not None:
            cur.execute("ROLLBACK TO SAVEPOINT claim_try")
            h = lease_holder(cur, busy)
            reason = "resource {} busy".format(busy)
            if waiting != reason:
                cur.execute("UPDATE {} SET waiting_reason = %s, updated_at = now() WHERE task_id = %s".format(_t("tasks")), (reason, task_id))
                _event(cur, actor, "resource_busy", task_id=task_id, resource=busy, held_by=(h or {}).get("holder"))
            continue
        cur.execute("RELEASE SAVEPOINT claim_try")
        cur.execute("UPDATE {} SET lease_ids = %s WHERE attempt_id = %s".format(_t("attempts")), ([g["lease_id"] for g in got], aid))
        cur.execute("UPDATE {} SET state = 'working', current_attempt = %s, attempts_made = %s, waiting_reason = NULL, updated_at = now() "
                    "WHERE task_id = %s".format(_t("tasks")), (aid, made + 1, task_id))
        _event(cur, actor, "claimed", task_id=task_id, attempt_id=aid, seq=made + 1, host=host)
        _event(cur, actor, "attempt_started", task_id=task_id, attempt_id=aid, leases=[g["lease_id"] for g in got])
        conn.commit()
        t = get_task(conn, task_id)
        return {"task": t, "attempt_id": aid, "leases": got}
    conn.commit()
    return None


def heartbeat(conn, attempt_id: str, actor: str, *, ttl_s: int = 90, record_event: bool = True) -> Dict[str, Any]:
    """Extend the Attempt and its leases. ok=False means the Attempt is no
    longer RUNNING (it was reaped or finished): the worker must stop, and
    nothing it produces afterwards can complete the Task."""
    cur = conn.cursor()
    cur.execute("UPDATE {} SET heartbeat_at = now(), expires_at = now() + make_interval(secs => %s) WHERE attempt_id = %s "
                "AND status = 'running' RETURNING task_id".format(_t("attempts")), (ttl_s, attempt_id))
    row = cur.fetchone()
    if row is None:
        conn.commit()
        return {"ok": False, "cancel_requested": False}
    cur.execute("UPDATE {} SET renewed_at = now(), expires_at = now() + make_interval(secs => %s) WHERE attempt_id = %s "
                "AND released_at IS NULL".format(_t("leases")), (ttl_s, attempt_id))
    cur.execute("SELECT cancel_requested FROM {} WHERE task_id = %s".format(_t("tasks")), (row[0],))
    cancel_req = cur.fetchone()[0]
    if record_event:
        _event(cur, actor, "heartbeat", task_id=row[0], attempt_id=attempt_id)
    conn.commit()
    return {"ok": True, "cancel_requested": bool(cancel_req)}


def add_artifact(conn, task_id: str, attempt_id: Optional[str], name: str, kind: str, content: bytes, *,
                 media_type: str = "text/plain", metadata: Optional[Dict[str, Any]] = None, actor: str = "fabric") -> Dict[str, Any]:
    if len(content) > MAX_BLOB_BYTES:
        raise FabricError("artifact {} is {} bytes; pilot limit {}".format(name, len(content), MAX_BLOB_BYTES))
    sha = hashlib.sha256(content).hexdigest()
    cur = conn.cursor()
    if attempt_id is not None:
        cur.execute("SELECT status FROM {} WHERE attempt_id = %s AND task_id = %s".format(_t("attempts")), (attempt_id, task_id))
        r = cur.fetchone()
        if r is None:
            conn.rollback(); raise NotFound("attempt {} of task {}".format(attempt_id, task_id))
        attempt_status = r[0]
    else:
        attempt_status = None
    cur.execute("INSERT INTO {} (sha256, size_bytes, content) VALUES (%s,%s,%s) ON CONFLICT (sha256) DO NOTHING".format(_t("blobs")),
                (sha, len(content), content))
    aid = new_id("art")
    md = dict(metadata or {}, attempt_status_at_upload=attempt_status)
    cur.execute("INSERT INTO {} (artifact_id, task_id, attempt_id, name, kind, media_type, sha256, size_bytes, metadata) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(_t("artifacts")),
                (aid, task_id, attempt_id, name, kind, media_type, sha, len(content), json.dumps(md, default=str)))
    _event(cur, actor, "artifact_added", task_id=task_id, attempt_id=attempt_id, artifact_id=aid, name=name, artifact_kind=kind,
           sha256=sha, size_bytes=len(content), attempt_status=attempt_status)
    conn.commit()
    return {"artifact_id": aid, "sha256": sha, "size_bytes": len(content)}


def artifact_content(conn, artifact_id: str) -> Dict[str, Any]:
    cur = conn.cursor()
    cur.execute("SELECT a.artifact_id, a.task_id, a.attempt_id, a.name, a.kind, a.media_type, a.sha256, a.size_bytes, a.metadata, b.content "
                "FROM {} a JOIN {} b USING (sha256) WHERE a.artifact_id = %s".format(_t("artifacts"), _t("blobs")), (artifact_id,))
    rows = _rows(cur); conn.commit()
    if not rows:
        raise NotFound(artifact_id)
    r = rows[0]
    r["content"] = bytes(r["content"])
    if hashlib.sha256(r["content"]).hexdigest() != r["sha256"]:
        raise FabricError("artifact {} content does not match its sha256".format(artifact_id))
    return r


def _task_after_attempt_end(cur, task_id: str, actor: str, outcome: str, *, error: Optional[str] = None,
                            result_summary: Optional[str] = None, attempt_id: Optional[str] = None) -> str:
    cur.execute("SELECT state, attempts_made, max_attempts, cancel_requested FROM {} WHERE task_id = %s FOR UPDATE".format(_t("tasks")),
                (task_id,))
    state, made, maxa, cancel_req = cur.fetchone()
    if state in TERMINAL:
        return state                                   # terminal never changes
    if outcome == "input-required":
        new = "input-required"
    elif outcome == "rejected":
        new = "rejected"
    elif outcome == "succeeded":
        new = "completed"
    elif outcome == "canceled" or cancel_req:
        new = "canceled"
    elif made < maxa:
        new = "submitted"
    else:
        new = "failed"
    cur.execute("UPDATE {} SET state = %s, current_attempt = NULL, updated_at = now(), "
                "result_summary = COALESCE(%s, result_summary), error_summary = CASE WHEN %s IN ('failed') THEN %s ELSE error_summary END, "
                "terminal_at = CASE WHEN %s IN ('completed','canceled','failed','rejected') THEN now() ELSE NULL END "
                "WHERE task_id = %s".format(_t("tasks")), (new, result_summary, new, error, new, task_id))
    _event(cur, actor, {"completed": "completed", "canceled": "canceled", "submitted": "requeued", "failed": "failed",
                        "input-required": "input_required", "rejected": "rejected"}[new],
           task_id=task_id, attempt_id=attempt_id, attempt_outcome=outcome, attempts_made=made, max_attempts=maxa, error=error)
    return new


def finish_attempt(conn, attempt_id: str, outcome: str, actor: str, *, exit_code: Optional[int] = None, error: Optional[str] = None,
                   model: Optional[str] = None, env_receipt: Optional[Dict[str, Any]] = None, worktree: Optional[str] = None,
                   result_summary: Optional[str] = None) -> Dict[str, Any]:
    """End a RUNNING Attempt. Rejected (accepted=False) if the Attempt is not
    running any more -- e.g. a reaper already abandoned it: a late worker
    cannot complete the Task (fencing by attempt status)."""
    if outcome not in ("succeeded", "failed", "canceled", "input-required", "rejected"):
        raise FabricError("outcome must be succeeded, failed, canceled, input-required or rejected")
    cur = conn.cursor()
    att_status = {"input-required": "succeeded", "rejected": "succeeded"}.get(outcome, outcome)
    cur.execute("UPDATE {} SET status = %s, ended_at = now(), exit_code = %s, error = %s, model = COALESCE(%s, model), "
                "env_receipt = COALESCE(%s::jsonb, env_receipt), worktree = COALESCE(%s, worktree) "
                "WHERE attempt_id = %s AND status = 'running' RETURNING task_id".format(_t("attempts")),
                (att_status, exit_code, error, model, json.dumps(env_receipt) if env_receipt is not None else None, worktree, attempt_id))
    row = cur.fetchone()
    if row is None:
        cur.execute("SELECT task_id, status FROM {} WHERE attempt_id = %s".format(_t("attempts")), (attempt_id,))
        r = cur.fetchone()
        _event(cur, actor, "late_finish_rejected", task_id=r[0] if r else None, attempt_id=attempt_id, outcome=outcome,
               attempt_status=r[1] if r else None)
        conn.commit()
        return {"accepted": False, "attempt_status": r[1] if r else None}
    task_id = row[0]
    _release_attempt_leases(cur, attempt_id, actor, "attempt_" + outcome)
    if outcome != "succeeded":
        _event(cur, actor, "attempt_failed" if outcome == "failed" else "attempt_canceled", task_id=task_id, attempt_id=attempt_id,
               exit_code=exit_code, error=error)
    new = _task_after_attempt_end(cur, task_id, actor, outcome, error=error, result_summary=result_summary, attempt_id=attempt_id)
    conn.commit()
    return {"accepted": True, "task_id": task_id, "task_state": new}


def reap(conn, actor: str = "reaper") -> Dict[str, Any]:
    """Anyone may call this (workers do, every loop). Abandons RUNNING
    Attempts whose heartbeat expired, releases their leases, returns each Task
    to submitted (retry) or failed/canceled; expires stale hand-held leases;
    marks silent instances offline."""
    cur = conn.cursor()
    cur.execute("SELECT attempt_id, task_id FROM {} WHERE status = 'running' AND expires_at < now() FOR UPDATE SKIP LOCKED".format(_t("attempts")))
    abandoned = []
    for aid, tid in cur.fetchall():
        cur.execute("UPDATE {} SET status = 'abandoned', ended_at = now(), error = 'heartbeat expired' WHERE attempt_id = %s".format(_t("attempts")),
                    (aid,))
        _release_attempt_leases(cur, aid, actor, "attempt_abandoned")
        _event(cur, actor, "attempt_abandoned", task_id=tid, attempt_id=aid, reason="heartbeat expired")
        new = _task_after_attempt_end(cur, tid, actor, "abandoned", error="attempt {} abandoned (heartbeat expired)".format(aid), attempt_id=aid)
        abandoned.append({"attempt_id": aid, "task_id": tid, "task_state": new})
    cur.execute("SELECT DISTINCT resource FROM {} WHERE released_at IS NULL AND expires_at < now()".format(_t("leases")))
    for (res,) in cur.fetchall():
        _expire_stale_lease(cur, res, actor)
    cur.execute("UPDATE {} SET status = 'offline' WHERE status <> 'offline' AND last_seen_at < now() - make_interval(secs => %s)".format(
        _t("agent_instances")), (ONLINE_SECONDS * 3,))
    conn.commit()
    return {"abandoned": abandoned}


def add_message(conn, task_id: str, message_id: str, role: str, parts: List[Dict[str, Any]], actor: str = "fabric") -> None:
    cur = conn.cursor()
    cur.execute("INSERT INTO {} (task_id, message_id, role, parts) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING".format(_t("messages")),
                (task_id, message_id, role, json.dumps(parts)))
    conn.commit()


def messages(conn, task_id: str) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT message_id, role, parts, created_at FROM {} WHERE task_id = %s ORDER BY seq".format(_t("messages")),
                (task_id,))
    rows = _rows(cur); conn.commit()
    return rows


def continue_task(conn, task_id: str, message_id: str, text: str, actor: str,
                  params_patch: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """A2A multi-turn: a new user Message on an input-required Task appends
    to its instruction and returns it to the queue. Terminal Tasks refuse."""
    cur = conn.cursor()
    cur.execute("SELECT state FROM {} WHERE task_id = %s FOR UPDATE".format(_t("tasks")), (task_id,))
    row = cur.fetchone()
    if row is None:
        conn.rollback(); raise NotFound(task_id)
    if row[0] in TERMINAL:
        conn.rollback(); raise FabricError("task {} is {} (terminal)".format(task_id, row[0]))
    cur.execute("INSERT INTO {} (task_id, message_id, role, parts) VALUES (%s,%s,'user',%s)".format(_t("messages")),
                (task_id, message_id, json.dumps([{"text": text}])))
    if row[0] == "input-required":
        cur.execute("UPDATE {} SET instruction = instruction || %s, state = 'submitted', max_attempts = max_attempts + 1, "
                    "params = params || %s::jsonb, updated_at = now() WHERE task_id = %s".format(_t("tasks")),
                    ("\n\n[continued] " + text, json.dumps(params_patch or {}), task_id))
        _event(cur, actor, "continued", task_id=task_id, message_id=message_id)
    conn.commit()
    return {"task_id": task_id, "state": "submitted" if row[0] == "input-required" else row[0]}
