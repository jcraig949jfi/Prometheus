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
#: Seat states (operator ruling 2026-09-11, Diomedes's omission): PARKED is intentional inactivity
#: (routable, no autonomous work, state must stay truthful); DORMANT is expected to operate but not;
#: BLOCKED is waiting on a named blocker; RETIRED is closed with an annotation.
STATES = ("active", "parked", "dormant", "blocked", "retired", "booting", "unknown")
#: Message status is DERIVED from receiving-side events; a sender never mutates it.
MESSAGE_STATES = ("POSTED", "SEEN", "CLAIMED", "ANSWERED", "CLOSED")
QUEUEABLE = ("prompt", "delegation")
REPO = Path(__file__).resolve().parents[1]
#: Machine labels for instance tags (the program's names; an unknown host falls back to its
#: lowercased hostname). Kept beside comms/environments.json's descriptions.
MACHINES = {"SKULLPORT": "m1", "SPECTREX5": "m2"}
SESSION_ENV = "CLAUDE_CODE_SESSION_ID"


def machine_label(hostname: Optional[str] = None) -> str:
    import re
    h = (hostname or platform.node() or "unknown-host").strip()
    return MACHINES.get(h.upper(), re.sub(r"[^a-z0-9]+", "-", h.lower()) or "unknown-host")


def instance_tag(session_id: Optional[str] = None, hostname: Optional[str] = None) -> str:
    """One seat, many instances (Harmonia #154; D-24 amendment 3). The tag is
    DERIVED, never chosen: <machine label>-<first 8 hex of the harness session
    id>, so two sessions cannot share it and one session always regenerates
    it. Without a session id the tag is <machine>-nosession: every untagged
    process on that host is ONE instance, which is exactly the pre-#154
    behaviour, kept rather than refused so that a sync never fails for want
    of a tag. Matches roles/Harmonia/instance.py for tagged sessions."""
    import re
    sid = (os.environ.get(SESSION_ENV, "") if session_id is None else (session_id or "")).strip().lower()
    m = re.match(r"([0-9a-z]{8})", sid.replace("session_", "", 1))   # UUID form -> 8 hex; bridge form -> 8 base36
    return "{}-{}".format(machine_label(hostname), m.group(1) if m else "nosession")


def split_sender(sender: str):
    """'Harmonia[m1-486e595f]' -> ('Harmonia', 'm1-486e595f'); a bare seat name
    -> (seat, the current process's tag)."""
    import re
    m = re.fullmatch(r"([A-Za-z0-9_-]+)\[([A-Za-z0-9_-]+)\]", sender or "")
    if m:
        return m.group(1), m.group(2)
    return sender, instance_tag()


def schema() -> str:
    s = os.environ.get("COMMS_SCHEMA", "comms")
    if not s.replace("_", "").isalnum():
        raise ValueError("unsafe schema name {!r}".format(s))
    return s


def connect(require_schema: bool = True):
    """The program's ONE comms database. Fails closed when the resolved host
    holds no comms schema (a seat booting off M1 resolves to localhost by
    default and would otherwise fork the queue with `comms init`; Atalanta
    #47 / Eos #55, 2026-09-11). `init` passes require_schema=False."""
    import sys
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from evidence_wiki.ew import db as ewdb
    from . import identity
    conn = ewdb.connect()
    # IDENTITY before structure (D-24 amendment 1, on Hermes #68). The
    # structural check below answers "is this a comms database"; this answers
    # "is it OURS". They are different questions: a database given
    # comms/schema.sql verbatim satisfies the structural check on any cluster
    # (comms/tests/test_identity.py builds one and proves it). `init` runs
    # with require_schema=False and is therefore covered by this line too,
    # which is what makes `comms init` on an unregistered environment refuse
    # instead of forking the queue.
    try:
        identity.require(conn, identity.current_environment())
    except identity.WrongEnvironment:
        conn.close()
        raise
    if require_schema:
        cur = conn.cursor()
        cur.execute("select to_regclass(%s)", (schema() + ".messages",))
        if cur.fetchone()[0] is None:
            host = getattr(conn, "info", None) and conn.info.host
            conn.close()
            raise RuntimeError(
                "comms: the database at host {!r} holds no {}.messages table; this is not the program's comms "
                "database. Set EW_DB_HOST to the host that holds it (M1: 192.168.1.202) instead of running "
                "`comms init` here -- init on the wrong host forks the queue.".format(host, schema()))
    return conn


def init_schema(conn) -> None:
    sql = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8").replace("{schema}", schema())
    cur = conn.cursor(); cur.execute(sql); conn.commit()
    migrate_instances(conn)


def migrate_instances(conn) -> Dict[str, int]:
    """D-24 amendment 3, idempotent: every seat row that predates instance
    tracking gets ONE instance row derived from its recorded session and
    machine, credited with the seat's receipts so the migration replays
    nothing. Run by init; harmless afterwards (ON CONFLICT DO NOTHING).
    Applied to the live schema 2026-09-11 20:0x UTC: 31 seats, 255 receipts."""
    cur = conn.cursor(); s = schema()
    cur.execute("SELECT agent, session_id, machine, last_bootstrap_at, last_active_at, last_sync_at, last_message_id, boot_count, "
                "base_sha, branch, worktree_path, model FROM {s}.agents a WHERE NOT EXISTS "
                "(SELECT 1 FROM {s}.agent_instances i WHERE i.agent = a.agent)".format(s=s))
    seeded = 0
    for r in cur.fetchall():
        inst = instance_tag(r[1] or "", r[2])
        cur.execute("INSERT INTO {s}.agent_instances (agent, instance, first_boot_at, last_bootstrap_at, last_active_at, last_sync_at, "
                    "last_message_id, boot_count, machine, base_sha, branch, worktree_path, model, session_id) "
                    "VALUES (%s, %s, COALESCE(%s, now()), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (agent, instance) DO NOTHING".format(s=s),
                    (r[0], inst, r[3], r[3], r[4], r[5], r[6], r[7], r[2], r[8], r[9], r[10], r[11], r[1]))
        seeded += cur.rowcount
        cur.execute("INSERT INTO {s}.receipt_instances (message_id, agent, instance, seen_at) "
                    "SELECT message_id, agent, %s, COALESCE(seen_at, now()) FROM {s}.receipts WHERE agent = %s AND seen_at IS NOT NULL "
                    "ON CONFLICT (message_id, agent, instance) DO NOTHING".format(s=s), (inst, r[0]))
    conn.commit()
    return {"instances_seeded": seeded}


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
    sender, sender_instance = split_sender(sender)      # 'Seat[tag]' is accepted; the seat stays the sender
    cur = conn.cursor()
    cur.execute("INSERT INTO {s}.messages (sender, recipients, kind, subject, body, sha256, reply_to, task_ref, priority, machine, expires_at, sender_instance) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id".format(s=schema()),
                (sender, list(recipients), kind, subject, body, _sha(subject, body), reply_to, task_ref, priority, platform.node(), expires_at, sender_instance))
    mid = cur.fetchone()[0]; conn.commit()
    touch(conn, sender)
    return int(mid)


def broadcast(conn, sender: str, subject: str, body: str, **kw) -> int:
    return post(conn, sender, ["*"], "broadcast", subject, body, **kw)


def inbox(conn, agent: str, *, unseen_only: bool = True, limit: int = 200, instance: Optional[str] = None) -> List[Dict[str, Any]]:
    """Messages addressed to `agent` or to '*', not sent by the agent, in
    priority then age order; unseen unless asked otherwise.

    UNSEEN is judged per INSTANCE (Harmonia #154): a message is unseen for
    instance I when the SEAT has no receipt for it at all, or when I has no
    receipt of its own AND the message arrived after I first booted. So a
    live sibling instance cannot swallow a message another instance would
    have acted on, while a freshly booted instance does not replay the
    seat's whole history. An instance that never booted (a bare sync) gets
    exactly the seat-level view, which is the pre-#154 behaviour."""
    inst = instance or instance_tag()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id, m.created_at, m.sender, m.recipients, m.kind, m.subject, m.body, m.sha256, m.reply_to, m.task_ref, m.priority,
               r.seen_at, r.queued_at, r.done_at, m.sender_instance,
               (ri.seen_at IS NOT NULL) AS seen_by_me
        FROM {s}.messages m
        LEFT JOIN {s}.receipts r ON r.message_id = m.id AND r.agent = %s
        LEFT JOIN {s}.receipt_instances ri ON ri.message_id = m.id AND ri.agent = %s AND ri.instance = %s
        LEFT JOIN {s}.agent_instances ai ON ai.agent = %s AND ai.instance = %s
        WHERE (%s = ANY(m.recipients) OR '*' = ANY(m.recipients)) AND m.sender <> %s
          AND (m.expires_at IS NULL OR m.expires_at > now())
          AND (NOT %s OR r.seen_at IS NULL
               OR (ri.seen_at IS NULL AND ai.first_boot_at IS NOT NULL AND m.created_at >= ai.first_boot_at))
        ORDER BY m.priority ASC, m.created_at ASC LIMIT %s""".format(s=schema()),
                (agent, agent, inst, agent, inst, agent, agent, unseen_only, limit))
    cols = ["id", "created_at", "sender", "recipients", "kind", "subject", "body", "sha256", "reply_to", "task_ref", "priority",
            "seen_at", "queued_at", "done_at", "sender_instance", "seen_by_me"]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def mark_seen(conn, agent: str, ids: Sequence[int], instance: Optional[str] = None) -> None:
    """Seen by the SEAT (receipts, what the operator's --all view reports) and
    seen by THIS INSTANCE (receipt_instances)."""
    if not ids:
        return
    inst = instance or instance_tag()
    cur = conn.cursor()
    for mid in ids:
        cur.execute("INSERT INTO {s}.receipts (message_id, agent, seen_at) VALUES (%s, %s, now()) "
                    "ON CONFLICT (message_id, agent) DO UPDATE SET seen_at = COALESCE({s}.receipts.seen_at, now())".format(s=schema()), (mid, agent))
        cur.execute("INSERT INTO {s}.receipt_instances (message_id, agent, instance) VALUES (%s, %s, %s) "
                    "ON CONFLICT (message_id, agent, instance) DO NOTHING".format(s=schema()), (mid, agent, inst))
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
    inst = instance_tag()
    new = inbox(conn, agent, unseen_only=True, instance=inst)
    mark_seen(conn, agent, [m["id"] for m in new], instance=inst)
    touch(conn, agent, last_message_id=max([m["id"] for m in new], default=None), synced=True)
    queued = []
    for m in new:
        if m["kind"] in QUEUEABLE:
            enqueue(conn, agent, m["id"]); queued.append(m["id"])
    return {"agent": agent, "instance": inst, "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
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
    machine, model and tier, capabilities, session and harness metadata. A
    boot is a presence event (it states revision and worktree), so it also
    stamps the sync fields."""
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
                                model, tier, capabilities, session_id, harness, status_json, updated_at,
                                last_sync_at, last_sync_sha, last_sync_worktree, last_sync_branch)
        VALUES (%s, %s, now(), now(), 1, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, now(), now(), %s, %s, %s)
        ON CONFLICT (agent) DO UPDATE SET
            status = EXCLUDED.status, last_active_at = now(), last_bootstrap_at = now(),
            last_sync_at = now(), last_sync_sha = EXCLUDED.last_sync_sha, last_sync_worktree = EXCLUDED.last_sync_worktree,
            last_sync_branch = EXCLUDED.last_sync_branch,
            boot_count = {s}.agents.boot_count + 1, machine = EXCLUDED.machine, base_sha = EXCLUDED.base_sha,
            branch = EXCLUDED.branch, worktree_path = EXCLUDED.worktree_path,
            model = COALESCE(EXCLUDED.model, {s}.agents.model), tier = CASE WHEN EXCLUDED.model IS NULL THEN {s}.agents.tier ELSE EXCLUDED.tier END,
            capabilities = CASE WHEN cardinality(EXCLUDED.capabilities) = 0 THEN {s}.agents.capabilities ELSE EXCLUDED.capabilities END,
            session_id = COALESCE(EXCLUDED.session_id, {s}.agents.session_id), harness = EXCLUDED.harness,
            status_json = {s}.agents.status_json || EXCLUDED.status_json, updated_at = now()""".format(s=schema()),
                (agent, status, platform.node(), ws.get("base_sha"), ws.get("branch"), ws.get("worktree_path"),
                 model, tier_for(model), list(capabilities), sid, _json.dumps(harness), _json.dumps(extra or {}),
                 ws.get("base_sha"), ws.get("worktree_path"), ws.get("branch")))
    inst = instance_tag(sid)
    cur.execute("""
        INSERT INTO {s}.agent_instances (agent, instance, last_bootstrap_at, last_active_at, last_sync_at, boot_count, machine,
                                         base_sha, branch, worktree_path, model, session_id)
        VALUES (%s, %s, now(), now(), now(), 1, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (agent, instance) DO UPDATE SET
            last_bootstrap_at = now(), last_active_at = now(), last_sync_at = now(),
            boot_count = {s}.agent_instances.boot_count + 1, machine = EXCLUDED.machine, base_sha = EXCLUDED.base_sha,
            branch = EXCLUDED.branch, worktree_path = EXCLUDED.worktree_path,
            model = COALESCE(EXCLUDED.model, {s}.agent_instances.model), session_id = COALESCE(EXCLUDED.session_id, {s}.agent_instances.session_id)
        """.format(s=schema()), (agent, inst, platform.node(), ws.get("base_sha"), ws.get("branch"), ws.get("worktree_path"), model, sid))
    conn.commit()
    return dict(agent=agent, instance=inst, status=status, machine=platform.node(), workspace=ws, model=model, tier=tier_for(model),
                capabilities=list(capabilities), session_id=sid, harness=harness)


def _workspace() -> Dict[str, Any]:
    try:
        import sys
        if str(REPO) not in sys.path:
            sys.path.insert(0, str(REPO))
        from archaeon import workspace as W
        return W.receipt()
    except Exception:                                            # noqa: BLE001
        return {}


def touch(conn, agent: str, *, last_message_id: Optional[int] = None, synced: bool = False) -> None:
    """Any comms call marks activity. A SYNC is the presence event: it
    records "read through message N at SHA X from worktree Y at time Z".
    A parked, blocked or retired seat keeps its state; nothing here makes a
    seat active by owning a row."""
    ws = _workspace() if synced else {}
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO {s}.agents (agent, status, last_active_at, last_sync_at, last_message_id, machine,
                                last_sync_sha, last_sync_worktree, last_sync_branch, updated_at)
        VALUES (%s, 'unknown', now(), CASE WHEN %s THEN now() ELSE NULL END, %s, %s, %s, %s, %s, now())
        ON CONFLICT (agent) DO UPDATE SET
            last_active_at = now(),
            last_sync_at = CASE WHEN EXCLUDED.last_sync_at IS NULL THEN {s}.agents.last_sync_at ELSE EXCLUDED.last_sync_at END,
            last_message_id = GREATEST(COALESCE({s}.agents.last_message_id, 0), COALESCE(EXCLUDED.last_message_id, 0)),
            last_sync_sha = COALESCE(EXCLUDED.last_sync_sha, {s}.agents.last_sync_sha),
            last_sync_worktree = COALESCE(EXCLUDED.last_sync_worktree, {s}.agents.last_sync_worktree),
            last_sync_branch = COALESCE(EXCLUDED.last_sync_branch, {s}.agents.last_sync_branch),
            status = CASE WHEN {s}.agents.status IN ('parked', 'blocked', 'retired', 'dormant') THEN {s}.agents.status
                          WHEN {s}.agents.status = 'unknown' AND %s THEN 'active' ELSE {s}.agents.status END,
            updated_at = now()""".format(s=schema()),
                (agent, synced, last_message_id, platform.node(), ws.get("base_sha"), ws.get("worktree_path"), ws.get("branch"), synced))
    # The instance's own presence. A row created here (never booted) carries first_boot_at = now(),
    # so its unseen window starts at this call and it cannot replay the seat's history.
    cur.execute("""
        INSERT INTO {s}.agent_instances (agent, instance, last_active_at, last_sync_at, last_message_id, machine, base_sha, branch, worktree_path)
        VALUES (%s, %s, now(), CASE WHEN %s THEN now() ELSE NULL END, %s, %s, %s, %s, %s)
        ON CONFLICT (agent, instance) DO UPDATE SET
            last_active_at = now(),
            last_sync_at = CASE WHEN EXCLUDED.last_sync_at IS NULL THEN {s}.agent_instances.last_sync_at ELSE EXCLUDED.last_sync_at END,
            last_message_id = GREATEST(COALESCE({s}.agent_instances.last_message_id, 0), COALESCE(EXCLUDED.last_message_id, 0)),
            base_sha = COALESCE(EXCLUDED.base_sha, {s}.agent_instances.base_sha),
            branch = COALESCE(EXCLUDED.branch, {s}.agent_instances.branch),
            worktree_path = COALESCE(EXCLUDED.worktree_path, {s}.agent_instances.worktree_path)""".format(s=schema()),
                (agent, instance_tag(), synced, last_message_id, platform.node(), ws.get("base_sha"), ws.get("branch"), ws.get("worktree_path")))
    conn.commit()


def set_status(conn, agent: str, status: str, note: Optional[str] = None) -> None:
    import json as _json
    if status not in STATES:
        raise ValueError("status must be one of {}".format(STATES))
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
               (a.last_sync_at IS NOT NULL AND a.last_sync_at > now() - make_interval(mins => %s)) AS online,
               (SELECT count(*) FROM {s}.task_queue q WHERE q.agent = a.agent AND q.status = 'queued') AS queued,
               (SELECT count(*) FROM {s}.messages m LEFT JOIN {s}.receipts r ON r.message_id = m.id AND r.agent = a.agent
                 WHERE (a.agent = ANY(m.recipients) OR '*' = ANY(m.recipients)) AND m.sender <> a.agent AND r.seen_at IS NULL) AS unseen
               , a.last_sync_sha, a.last_sync_worktree
        FROM {s}.agents a ORDER BY online DESC, a.last_sync_at DESC NULLS LAST, a.agent""".format(s=schema()), (online_minutes,))
    cols = ["agent", "status", "last_active_at", "last_sync_at", "last_message_id", "last_bootstrap_at", "boot_count", "machine",
            "base_sha", "model", "tier", "capabilities", "online", "queued", "unseen", "last_sync_sha", "last_sync_worktree"]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.execute("""
        SELECT agent, instance, machine, last_sync_at, last_bootstrap_at, boot_count, base_sha, worktree_path, branch, model,
               (last_sync_at IS NOT NULL AND last_sync_at > now() - make_interval(mins => %s)) AS online
        FROM {s}.agent_instances ORDER BY agent, last_sync_at DESC NULLS LAST""".format(s=schema()), (online_minutes,))
    icols = ["agent", "instance", "machine", "last_sync_at", "last_bootstrap_at", "boot_count", "base_sha", "worktree_path", "branch", "model", "online"]
    by_agent: Dict[str, List[Dict[str, Any]]] = {}
    for r in cur.fetchall():
        d = dict(zip(icols, r)); by_agent.setdefault(d["agent"], []).append(d)
    for r in rows:
        r["instances"] = by_agent.get(r["agent"], [])
        r["instances_online"] = sum(1 for i in r["instances"] if i["online"])
        # a seat is online when ANY instance is; the seat row's own last_sync_at is the latest instance's
        r["online"] = bool(r["online"]) or r["instances_online"] > 0
    known = {r["agent"] for r in rows}
    for seat in roster():
        if seat not in known:
            rows.append({"agent": seat, "status": "never_booted", "online": False, "queued": 0, "unseen": None, "tier": "unknown",
                         "capabilities": [], "model": None, "last_active_at": None, "last_sync_at": None, "last_message_id": None,
                         "last_bootstrap_at": None, "boot_count": 0, "machine": None, "base_sha": None, "instances": [], "instances_online": 0})
    return rows


def message_status(conn, message_id: int) -> Dict[str, Any]:
    """POSTED -> SEEN -> CLAIMED -> ANSWERED / CLOSED, derived from
    receiving-side events only: receipts (seen, done), the task queue
    (active = claimed) and replies (a message whose reply_to is this one)."""
    cur = conn.cursor()
    cur.execute("SELECT id, sender, recipients, kind, subject, created_at FROM {s}.messages WHERE id = %s".format(s=schema()), (message_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError("no message {}".format(message_id))
    cur.execute("SELECT agent, seen_at, queued_at, done_at, note FROM {s}.receipts WHERE message_id = %s ORDER BY agent".format(s=schema()), (message_id,))
    receipts = [dict(zip(["agent", "seen_at", "queued_at", "done_at", "note"], r)) for r in cur.fetchall()]
    cur.execute("SELECT agent, status, claimed_by FROM {s}.task_queue WHERE message_id = %s".format(s=schema()), (message_id,))
    queue = [dict(zip(["agent", "status", "claimed_by"], r)) for r in cur.fetchall()]
    cur.execute("SELECT agent, instance, seen_at FROM {s}.receipt_instances WHERE message_id = %s ORDER BY seen_at".format(s=schema()), (message_id,))
    seen_by = [dict(zip(["agent", "instance", "seen_at"], r)) for r in cur.fetchall()]
    cur.execute("SELECT id, sender, kind, created_at FROM {s}.messages WHERE reply_to = %s ORDER BY id".format(s=schema()), (message_id,))
    replies = [dict(zip(["id", "sender", "kind", "created_at"], r)) for r in cur.fetchall()]
    state = "POSTED"
    if any(r["seen_at"] for r in receipts):
        state = "SEEN"
    if any(q["status"] == "active" for q in queue):
        state = "CLAIMED"
    if replies:
        state = "ANSWERED"
    if any(r["done_at"] for r in receipts) or any(q["status"] == "done" for q in queue):
        state = "CLOSED"
    return {"id": row[0], "sender": row[1], "recipients": row[2], "kind": row[3], "subject": row[4], "created_at": row[5],
            "status": state, "receipts": receipts, "seen_by_instances": seen_by, "queue": queue, "replies": replies}


def claim(conn, agent: str, message_id: int, instance: Optional[str] = None) -> Dict[str, Any]:
    """The receiver marks a queued item active (CLAIMED). Atomic: of two
    instances racing, exactly one gets CLAIMED and the other LOST with the
    holder's tag -- the caller MUST be able to learn it lost (Harmonia #154
    item 3: the old CLI printed nothing either way and the loser believed it
    held the item)."""
    inst = instance or instance_tag()
    cur = conn.cursor()
    cur.execute("UPDATE {s}.task_queue SET status = 'active', claimed_by = %s, updated_at = now() "
                "WHERE agent = %s AND message_id = %s AND status = 'queued' RETURNING id".format(s=schema()),
                (inst, agent, message_id))
    won = cur.fetchone() is not None
    conn.commit()
    touch(conn, agent)
    if won:
        return {"result": "CLAIMED", "agent": agent, "instance": inst, "message_id": message_id}
    cur.execute("SELECT status, claimed_by FROM {s}.task_queue WHERE agent = %s AND message_id = %s".format(s=schema()), (agent, message_id))
    row = cur.fetchone()
    if row is None:
        return {"result": "NOT_QUEUED", "agent": agent, "instance": inst, "message_id": message_id}
    return {"result": "LOST", "agent": agent, "instance": inst, "message_id": message_id, "status": row[0], "held_by": row[1]}
