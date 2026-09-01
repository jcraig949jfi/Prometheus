"""The Gen-2 Foundry runtime: the authoritative facade over the SQLite store.

Every mutating operation runs in one write transaction that changes state AND
appends the corresponding event atomically (invariants I4/I9: evidence is
immutable and the Foundry -- not an agent -- records what happened). Ownership
is checked on every world-scoped operation (I5: isolation by default; knowing an
id does not grant access). Open one Foundry per thread/worker.
"""

from __future__ import annotations

import json
import random
from typing import Any, Optional

from sfe import events
from sfe.errors import (AccessDenied, BudgetExhausted, ConflictError,
                         InvalidTransition, IsolationViolation, NotFound,
                         PredictionOrderingError, ValidationError)
from sfe.ids import content_hash, new_id
from sfe.store import Store, now

# world lifecycle transitions that are allowed (fail-closed otherwise)
_WORLD_TRANSITIONS = {
    "CREATED": {"RUNNING", "TERMINATED"},
    "RUNNING": {"PAUSED", "TERMINATED"},
    "PAUSED": {"RUNNING", "TERMINATED"},
    "TERMINATED": set(),
}

# sharing policies (section 13). ISOLATED is the default. A policy names the
# information KINDS that may cross a world boundary via explicit import.
SHARING_POLICIES = {
    "ISOLATED": frozenset(),
    "FAILURES_ONLY": frozenset({"failure"}),
    "HYPOTHESES_ONLY": frozenset({"hypothesis"}),
    "FAILURES_AND_HYPOTHESES": frozenset({"failure", "hypothesis"}),
    "SUCCESSES_ONLY": frozenset({"artifact"}),
    "FULLY_SHARED": frozenset({"failure", "hypothesis", "artifact",
                              "observation"}),
    "EXPLICIT_IMPORT_ONLY": frozenset({"failure", "hypothesis", "artifact",
                                       "observation"}),
}

DEFAULT_LEASE_S = 30.0

# resource enforcement classes (section 12): never fabricate precision.
ENFORCEMENT = ("enforceable", "measured", "estimated", "unavailable")


class Foundry:
    def __init__(self, db_path: str):
        self.store = Store(db_path)
        self.store.initialize()

    def close(self) -> None:
        self.store.close()

    # ================= identity =========================================
    def create_client(self, name: str, token_hash: Optional[str] = None) -> str:
        cid = new_id("client")
        with self.store.write() as cx:
            cx.execute("INSERT INTO clients(client_id,name,token_hash,created_ts)"
                       " VALUES(?,?,?,?)", (cid, name, token_hash, now()))
            events.append_foundry(cx, "CLIENT_CREATED", actor=cid,
                                  scope_kind="client", scope_id=cid,
                                  payload={"name": name})
        return cid

    def create_session(self, client_id: str, name: str) -> str:
        sid = new_id("session")
        with self.store.write() as cx:
            if cx.execute("SELECT 1 FROM clients WHERE client_id=?",
                          (client_id,)).fetchone() is None:
                raise NotFound("unknown client", client_id=client_id)
            cx.execute("INSERT INTO sessions(session_id,client_id,name,"
                       "created_ts) VALUES(?,?,?,?)",
                       (sid, client_id, name, now()))
            events.append_foundry(cx, "SESSION_CREATED", actor=client_id,
                                  scope_kind="session", scope_id=sid,
                                  payload={"name": name, "client_id": client_id})
        return sid

    # ================= world lifecycle ==================================
    def create_world(self, session_id: str, name: str, *,
                     sharing_policy: str = "ISOLATED",
                     seed_root: Optional[int] = None,
                     topology_group: Optional[str] = None,
                     budget: Optional[dict] = None) -> dict:
        if sharing_policy not in SHARING_POLICIES:
            raise ValidationError("unknown sharing policy",
                                  sharing_policy=sharing_policy,
                                  allowed=sorted(SHARING_POLICIES))
        wid = new_id("world")
        if seed_root is None:
            seed_root = random.SystemRandom().randrange(1 << 62)
        with self.store.write() as cx:
            s = cx.execute("SELECT client_id FROM sessions WHERE session_id=? "
                           "AND state='OPEN'", (session_id,)).fetchone()
            if s is None:
                raise NotFound("unknown or closed session",
                               session_id=session_id)
            cid = s["client_id"]
            cx.execute(
                "INSERT INTO worlds(world_id,session_id,client_id,name,state,"
                "sharing_policy,topology_group,seed_root,created_ts) "
                "VALUES(?,?,?,?,'CREATED',?,?,?,?)",
                (wid, session_id, cid, name, sharing_policy, topology_group,
                 int(seed_root), now()))
            self._init_budget(cx, wid, budget or {})
            events.append(cx, wid, "WORLD_CREATED", actor=cid, payload={
                "name": name, "sharing_policy": sharing_policy,
                "topology_group": topology_group, "seed_root": int(seed_root),
                "session_id": session_id})
        return self.get_world(wid, cid)

    def _world_row(self, cx, world_id: str):
        r = cx.execute("SELECT * FROM worlds WHERE world_id=?",
                       (world_id,)).fetchone()
        if r is None:
            raise NotFound("unknown world", world_id=world_id)
        return r

    def _authorize(self, cx, world_id: str, client_id: Optional[str]):
        """Ownership check (I5, T8). A client may only touch its own worlds.
        `client_id=None` is an internal/system call (executors) and is allowed;
        the API layer always passes a concrete client id."""
        r = self._world_row(cx, world_id)
        if client_id is not None and r["client_id"] != client_id:
            # do NOT leak existence details beyond "denied"
            raise AccessDenied("world is not owned by this client",
                               world_id=world_id)
        return r

    def get_world(self, world_id: str, client_id: Optional[str] = None) -> dict:
        cx = self.store.read()
        r = self._authorize(cx, world_id, client_id)
        return _world_dict(r)

    def _transition(self, world_id: str, client_id: Optional[str], target: str,
                    event_type: str, payload: Optional[dict] = None) -> dict:
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            cur = r["state"]
            if target not in _WORLD_TRANSITIONS[cur]:
                raise InvalidTransition(
                    f"cannot go {cur} -> {target}", world_id=world_id,
                    current=cur, target=target)
            extra = ""
            args = [target]
            if target == "TERMINATED":
                extra = ", terminated_ts=?"
                args.append(now())
            args.append(world_id)
            cx.execute(f"UPDATE worlds SET state=?{extra} WHERE world_id=?",
                       tuple(args))
            events.append(cx, world_id, event_type,
                          actor=r["client_id"], payload=payload or {})
            return _world_dict(self._world_row(cx, world_id))

    def start_world(self, world_id, client_id=None):
        return self._transition(world_id, client_id, "RUNNING", "WORLD_STARTED")

    def pause_world(self, world_id, client_id=None):
        return self._transition(world_id, client_id, "PAUSED", "WORLD_PAUSED")

    def resume_world(self, world_id, client_id=None):
        return self._transition(world_id, client_id, "RUNNING", "WORLD_RESUMED")

    def terminate_world(self, world_id, client_id=None):
        return self._transition(world_id, client_id, "TERMINATED",
                                "WORLD_TERMINATED")

    def list_worlds(self, *, session_id=None, client_id=None) -> list:
        cx = self.store.read()
        q, a = "SELECT * FROM worlds WHERE 1=1", []
        if session_id:
            q += " AND session_id=?"; a.append(session_id)
        if client_id:
            q += " AND client_id=?"; a.append(client_id)
        q += " ORDER BY created_ts"
        return [_world_dict(r) for r in cx.execute(q, tuple(a)).fetchall()]

    # ================= work queue =======================================
    def enqueue_work(self, world_id: str, kind: str, payload: dict, *,
                     client_id: Optional[str] = None, priority: int = 100,
                     max_attempts: int = 3,
                     dedup_key: Optional[str] = None) -> str:
        wkid = new_id("work")
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            if r["state"] == "TERMINATED":
                raise InvalidTransition("cannot enqueue into a terminated world",
                                        world_id=world_id)
            try:
                cx.execute(
                    "INSERT INTO work_items(work_id,world_id,kind,payload,"
                    "priority,max_attempts,dedup_key,created_ts,updated_ts) "
                    "VALUES(?,?,?,?,?,?,?,?,?)",
                    (wkid, world_id, kind, json.dumps(payload), priority,
                     max_attempts, dedup_key, now(), now()))
            except Exception as e:
                if "UNIQUE" in str(e) and dedup_key is not None:
                    ex = cx.execute("SELECT work_id FROM work_items WHERE "
                                    "world_id=? AND dedup_key=?",
                                    (world_id, dedup_key)).fetchone()
                    return ex["work_id"]     # idempotent enqueue
                raise
            events.append(cx, world_id, "WORK_ENQUEUED", actor=r["client_id"],
                          refs={"work_id": wkid}, payload={"kind": kind})
        return wkid

    def _reclaim_expired(self, cx) -> int:
        """Move leases that expired back to RETRYABLE (or EXPIRED if out of
        attempts). Called under the write lock at claim time so a dead worker's
        work is recovered without a background sweeper (I3, T5)."""
        t = now()
        rows = cx.execute(
            "SELECT work_id, world_id, attempts, max_attempts FROM work_items "
            "WHERE status IN ('CLAIMED','RUNNING') AND lease_expires < ?",
            (t,)).fetchall()
        for r in rows:
            newst = "RETRYABLE" if r["attempts"] < r["max_attempts"] else "EXPIRED"
            cx.execute("UPDATE work_items SET status=?, claimed_by=NULL, "
                       "lease_expires=NULL, updated_ts=? WHERE work_id=?",
                       (newst, t, r["work_id"]))
            events.append(cx, r["world_id"], "WORK_EXPIRED",
                          actor="foundry", refs={"work_id": r["work_id"]},
                          payload={"reclaimed_as": newst})
        return len(rows)

    def claim_work(self, worker_id: str, *, world_id: Optional[str] = None,
                   client_id: Optional[str] = None,
                   lease_s: float = DEFAULT_LEASE_S) -> Optional[dict]:
        """Atomically claim one claimable work item. Under BEGIN IMMEDIATE the
        select-then-update is exclusive, so two workers never claim the same
        unit (I3, T7). Paused/terminated worlds are skipped (a paused world must
        not consume execution resources, section 4).

        `client_id` scopes the claim to that client's OWN worlds (experimenter
        isolation, I5): an unscoped claim (world_id=None) by an experimenter
        never reaches another experimenter's queue -- it cannot even observe a
        foreign work item's payload, let alone hold a lease on it. client_id=None
        is an internal/system worker and applies no tenant filter (mirrors the
        _authorize convention)."""
        with self.store.write() as cx:
            self._reclaim_expired(cx)
            q = ("SELECT w.work_id, w.world_id FROM work_items w "
                 "JOIN worlds d ON d.world_id=w.world_id "
                 "WHERE w.status IN ('QUEUED','RETRYABLE') "
                 "AND d.state='RUNNING' ")
            a: list = []
            if client_id is not None:
                q += "AND d.client_id=? "; a.append(client_id)
            if world_id is not None:
                q += "AND w.world_id=? "; a.append(world_id)
            q += "ORDER BY w.priority ASC, w.created_ts ASC LIMIT 1"
            cand = cx.execute(q, tuple(a)).fetchone()
            if cand is None:
                return None
            t = now()
            cx.execute(
                "UPDATE work_items SET status='CLAIMED', claimed_by=?, "
                "lease_expires=?, heartbeat_ts=?, attempts=attempts+1, "
                "updated_ts=? WHERE work_id=? AND status IN "
                "('QUEUED','RETRYABLE')",
                (worker_id, t + lease_s, t, t, cand["work_id"]))
            events.append(cx, cand["world_id"], "WORK_CLAIMED", actor=worker_id,
                          refs={"work_id": cand["work_id"]})
            row = cx.execute("SELECT * FROM work_items WHERE work_id=?",
                             (cand["work_id"],)).fetchone()
            return _work_dict(row)

    def start_work(self, work_id: str, worker_id: str) -> dict:
        with self.store.write() as cx:
            r = self._owned_claim(cx, work_id, worker_id, {"CLAIMED"})
            cx.execute("UPDATE work_items SET status='RUNNING', updated_ts=? "
                       "WHERE work_id=?", (now(), work_id))
            events.append(cx, r["world_id"], "WORK_STARTED", actor=worker_id,
                          refs={"work_id": work_id})
            return _work_dict(cx.execute("SELECT * FROM work_items WHERE "
                                         "work_id=?", (work_id,)).fetchone())

    def heartbeat(self, work_id: str, worker_id: str,
                  lease_s: float = DEFAULT_LEASE_S, *,
                  client_id: Optional[str] = None) -> dict:
        with self.store.write() as cx:
            r = self._owned_claim(cx, work_id, worker_id, {"CLAIMED", "RUNNING"},
                                  client_id=client_id)
            t = now()
            cx.execute("UPDATE work_items SET lease_expires=?, heartbeat_ts=?, "
                       "updated_ts=? WHERE work_id=?",
                       (t + lease_s, t, t, work_id))
            events.append(cx, r["world_id"], "WORK_HEARTBEAT", actor=worker_id,
                          refs={"work_id": work_id})
            return {"work_id": work_id, "lease_expires": t + lease_s}

    def _owned_claim(self, cx, work_id, worker_id, allowed_states,
                     client_id=None):
        r = cx.execute("SELECT * FROM work_items WHERE work_id=?",
                       (work_id,)).fetchone()
        if r is None:
            raise NotFound("unknown work item", work_id=work_id)
        # defense-in-depth (I5): the work item's world must belong to the caller.
        # client_id=None is an internal/system worker (mirrors _authorize).
        if client_id is not None:
            self._authorize(cx, r["world_id"], client_id)
        if r["status"] not in allowed_states or r["claimed_by"] != worker_id:
            raise ConflictError(
                "work not held by this worker in an allowed state",
                work_id=work_id, status=r["status"], claimed_by=r["claimed_by"],
                worker_id=worker_id)
        return r

    def complete_work(self, work_id: str, worker_id: str, result: dict, *,
                      client_id: Optional[str] = None) -> dict:
        """Idempotent, exactly-once completion (I3, T7). If already completed by
        THIS worker, the stored result is returned; a second DISTINCT worker is
        rejected -- exactly one authoritative result."""
        with self.store.write() as cx:
            r = cx.execute("SELECT * FROM work_items WHERE work_id=?",
                           (work_id,)).fetchone()
            if r is None:
                raise NotFound("unknown work item", work_id=work_id)
            if client_id is not None:                 # defense-in-depth (I5)
                self._authorize(cx, r["world_id"], client_id)
            if r["status"] == "COMPLETED":
                if r["claimed_by"] == worker_id:
                    return _work_dict(r)          # idempotent replay
                raise ConflictError("work already completed by another worker",
                                    work_id=work_id, claimed_by=r["claimed_by"])
            if r["claimed_by"] != worker_id or r["status"] not in (
                    "CLAIMED", "RUNNING"):
                raise ConflictError("cannot complete work not held by worker",
                                    work_id=work_id, status=r["status"],
                                    claimed_by=r["claimed_by"])
            rhash = content_hash(result)
            cx.execute("UPDATE work_items SET status='COMPLETED', result=?, "
                       "result_hash=?, completed_ts=?, updated_ts=? "
                       "WHERE work_id=?",
                       (json.dumps(result), rhash, now(), now(), work_id))
            events.append(cx, r["world_id"], "WORK_COMPLETED", actor=worker_id,
                          refs={"work_id": work_id, "result_hash": rhash})
            return _work_dict(cx.execute("SELECT * FROM work_items WHERE "
                                         "work_id=?", (work_id,)).fetchone())

    def fail_work(self, work_id: str, worker_id: str, error: str, *,
                  retry: bool = True, client_id: Optional[str] = None) -> dict:
        with self.store.write() as cx:
            r = self._owned_claim(cx, work_id, worker_id, {"CLAIMED", "RUNNING"},
                                  client_id=client_id)
            retryable = retry and r["attempts"] < r["max_attempts"]
            newst = "RETRYABLE" if retryable else "FAILED"
            cx.execute("UPDATE work_items SET status=?, claimed_by=NULL, "
                       "lease_expires=NULL, error=?, updated_ts=? "
                       "WHERE work_id=?", (newst, error, now(), work_id))
            events.append(cx, r["world_id"], "WORK_FAILED", actor=worker_id,
                          refs={"work_id": work_id},
                          payload={"error": error[:500], "next": newst})
            return _work_dict(cx.execute("SELECT * FROM work_items WHERE "
                                         "work_id=?", (work_id,)).fetchone())

    def get_work(self, work_id: str) -> dict:
        r = self.store.read().execute("SELECT * FROM work_items WHERE work_id=?",
                                      (work_id,)).fetchone()
        if r is None:
            raise NotFound("unknown work item", work_id=work_id)
        return _work_dict(r)

    # ================= budgets ==========================================
    def _init_budget(self, cx, world_id: str, budget: dict) -> None:
        limits = {}
        for res, spec in (budget or {}).items():
            if isinstance(spec, dict):
                limit, enf = spec.get("limit"), spec.get("enforcement",
                                                          "measured")
            else:
                limit, enf = spec, "measured"
            if enf not in ENFORCEMENT:
                raise ValidationError("bad enforcement class", resource=res,
                                      enforcement=enf, allowed=list(ENFORCEMENT))
            limits[res] = {"limit": limit, "enforcement": enf}
        cx.execute("INSERT INTO budgets(world_id,limits,consumed,updated_ts) "
                   "VALUES(?,?,?,?)",
                   (world_id, json.dumps(limits), json.dumps({}), now()))

    def consume_budget(self, world_id: str, resource: str, amount: float, *,
                       client_id: Optional[str] = None) -> dict:
        """Account resource use and enforce the world's limit. Exceeding an
        ENFORCEABLE limit raises BudgetExhausted and emits BUDGET_EXHAUSTED; a
        MEASURED/ESTIMATED limit is recorded but not blocked (section 12: never
        fabricate enforcement you do not have)."""
        # The exhaustion TRANSITION (flag + event) must COMMIT even though the
        # call ultimately raises -- so we record it inside the transaction and
        # raise only AFTER the commit. Raising inside the write() block would
        # roll the transition back.
        blocked = False
        with self.store.write() as cx:
            self._authorize(cx, world_id, client_id)
            b = cx.execute("SELECT * FROM budgets WHERE world_id=?",
                           (world_id,)).fetchone()
            limits = json.loads(b["limits"]); consumed = json.loads(b["consumed"])
            spec = limits.get(resource)
            prospective = consumed.get(resource, 0) + amount
            over_enforced = (spec and spec.get("limit") is not None
                             and spec["enforcement"] == "enforceable"
                             and prospective > spec["limit"])
            if over_enforced:
                # an enforceable limit BLOCKS the use: consumed is NOT advanced
                # past the limit for the blocked amount; the world is marked
                # exhausted and the transition is recorded.
                blocked = True
                cur = consumed.get(resource, 0)
                if not b["exhausted"]:
                    cx.execute("UPDATE budgets SET exhausted=1, updated_ts=? "
                               "WHERE world_id=?", (now(), world_id))
                    events.append(cx, world_id, "BUDGET_EXHAUSTED",
                                  actor="foundry",
                                  payload={"resource": resource,
                                           "limit": spec["limit"],
                                           "consumed": cur, "requested": amount})
                lim = spec["limit"]
            else:
                consumed[resource] = prospective
                events.append(cx, world_id, "BUDGET_CONSUMED",
                              actor=client_id or "foundry",
                              payload={"resource": resource, "amount": amount,
                                       "total": prospective})
                cx.execute("UPDATE budgets SET consumed=?, updated_ts=? "
                           "WHERE world_id=?",
                           (json.dumps(consumed), now(), world_id))
                cur, lim = prospective, (spec.get("limit") if spec else None)
        if blocked:
            raise BudgetExhausted(
                "world resource budget exhausted", world_id=world_id,
                resource=resource, limit=lim, consumed=cur)
        return {"resource": resource, "consumed": cur, "limit": lim,
                "exhausted": bool(blocked)}

    def budget_status(self, world_id: str) -> dict:
        b = self.store.read().execute("SELECT * FROM budgets WHERE world_id=?",
                                      (world_id,)).fetchone()
        if b is None:
            raise NotFound("unknown world", world_id=world_id)
        return {"limits": json.loads(b["limits"]),
                "consumed": json.loads(b["consumed"]),
                "exhausted": bool(b["exhausted"])}

    # ================= research objects ==================================
    def propose_hypothesis(self, world_id: str, statement: str, *,
                           client_id: Optional[str] = None,
                           parents: Optional[list] = None) -> str:
        hid = new_id("hypothesis")
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            ev = events.append(cx, world_id, "HYPOTHESIS_PROPOSED",
                               actor=r["client_id"], refs={"hyp_id": hid},
                               payload={"statement": statement})
            cx.execute("INSERT INTO hypotheses(hyp_id,world_id,statement,"
                       "content_hash,created_ts,created_seq) VALUES(?,?,?,?,?,?)",
                       (hid, world_id, statement, content_hash(statement),
                        now(), ev["event_seq"]))
            for p in (parents or []):
                self._edge(cx, world_id, r["client_id"], p["kind"], p["id"],
                           "hypothesis", hid, "DERIVES_FROM")
        return hid

    def register_prediction(self, world_id: str, hyp_id: str, content: dict, *,
                            client_id: Optional[str] = None) -> str:
        """Register a SEALED prediction. Its content hash and its event_seq are
        frozen now, so a prediction cannot be edited post-hoc and its temporal
        position is authoritative (I6)."""
        pid = new_id("prediction")
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            if cx.execute("SELECT 1 FROM hypotheses WHERE hyp_id=? AND "
                          "world_id=?", (hyp_id, world_id)).fetchone() is None:
                raise NotFound("hypothesis not in this world", hyp_id=hyp_id)
            ph = content_hash(content)
            ev = events.append(cx, world_id, "PREDICTION_REGISTERED",
                               actor=r["client_id"],
                               refs={"pred_id": pid, "hyp_id": hyp_id},
                               payload={"content_hash": ph})
            cx.execute("INSERT INTO predictions(pred_id,world_id,hyp_id,content,"
                       "content_hash,created_ts,created_seq) "
                       "VALUES(?,?,?,?,?,?,?)",
                       (pid, world_id, hyp_id, json.dumps(content), ph, now(),
                        ev["event_seq"]))
            cx.execute("UPDATE hypotheses SET state='PREDICTED' WHERE hyp_id=? "
                       "AND state='PROPOSED'", (hyp_id,))
        return pid

    def create_experiment(self, world_id: str, spec: dict, *,
                          client_id: Optional[str] = None,
                          hyp_id: Optional[str] = None,
                          pred_id: Optional[str] = None,
                          enqueue: bool = False, kind: str = "experiment",
                          priority: int = 100) -> dict:
        eid = new_id("experiment")
        wk = None
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            ev = events.append(cx, world_id, "EXPERIMENT_CREATED",
                               actor=r["client_id"],
                               refs={"exp_id": eid, "hyp_id": hyp_id,
                                     "pred_id": pred_id})
            cx.execute("INSERT INTO experiments(exp_id,world_id,hyp_id,pred_id,"
                       "spec,spec_hash,created_ts,created_seq) "
                       "VALUES(?,?,?,?,?,?,?,?)",
                       (eid, world_id, hyp_id, pred_id, json.dumps(spec),
                        content_hash(spec), now(), ev["event_seq"]))
            if hyp_id:
                self._edge(cx, world_id, r["client_id"], "hypothesis", hyp_id,
                           "experiment", eid, "TESTS")
            if enqueue:
                wk = new_id("work")
                cx.execute(
                    "INSERT INTO work_items(work_id,world_id,kind,payload,"
                    "priority,created_ts,updated_ts) VALUES(?,?,?,?,?,?,?)",
                    (wk, world_id, kind, json.dumps({"exp_id": eid, **spec}),
                     priority, now(), now()))
                cx.execute("UPDATE experiments SET work_id=? WHERE exp_id=?",
                           (wk, eid))
                events.append(cx, world_id, "WORK_ENQUEUED", actor=r["client_id"],
                              refs={"work_id": wk, "exp_id": eid})
        return {"exp_id": eid, "work_id": wk}

    def record_observation(self, world_id: str, exp_id: str, content: dict,
                           outcome: str, *, client_id: Optional[str] = None,
                           pred_id: Optional[str] = None) -> str:
        """Record an observation. If it references a prediction, the prediction
        MUST have been registered earlier in the event order (I6, T11) -- a
        prediction whose registration event does not precede this observation is
        rejected as post-hoc laundering."""
        if outcome not in ("FALSIFIED", "SURVIVED", "INCONCLUSIVE"):
            raise ValidationError("bad outcome", outcome=outcome)
        oid = new_id("observation")
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            ex = cx.execute("SELECT * FROM experiments WHERE exp_id=? AND "
                            "world_id=?", (exp_id, world_id)).fetchone()
            if ex is None:
                raise NotFound("experiment not in this world", exp_id=exp_id)
            ev = events.append(cx, world_id, "OBSERVATION_RECORDED",
                               actor=r["client_id"],
                               refs={"obs_id": oid, "exp_id": exp_id,
                                     "pred_id": pred_id},
                               payload={"outcome": outcome})
            if pred_id is not None:
                p = cx.execute("SELECT created_seq FROM predictions WHERE "
                               "pred_id=? AND world_id=?",
                               (pred_id, world_id)).fetchone()
                if p is None:
                    raise NotFound("prediction not in this world",
                                   pred_id=pred_id)
                if p["created_seq"] >= ev["event_seq"]:
                    raise PredictionOrderingError(
                        "prediction did not precede observation; refusing to "
                        "record it as preregistered", pred_id=pred_id,
                        prediction_seq=p["created_seq"],
                        observation_seq=ev["event_seq"])
                cx.execute("UPDATE predictions SET state='OBSERVED' WHERE "
                           "pred_id=?", (pred_id,))
            cx.execute("INSERT INTO observations(obs_id,world_id,exp_id,pred_id,"
                       "content,outcome,created_ts,created_seq) "
                       "VALUES(?,?,?,?,?,?,?,?)",
                       (oid, world_id, exp_id, pred_id, json.dumps(content),
                        outcome, now(), ev["event_seq"]))
            cx.execute("UPDATE experiments SET state='OBSERVED' WHERE exp_id=?",
                       (exp_id,))
            if ex["hyp_id"]:
                st = {"FALSIFIED": "FALSIFIED", "SURVIVED": "SURVIVED"}.get(
                    outcome)
                if st:
                    cx.execute("UPDATE hypotheses SET state=? WHERE hyp_id=?",
                               (st, ex["hyp_id"]))
                    events.append(cx, world_id,
                                  "CLAIM_FALSIFIED" if outcome == "FALSIFIED"
                                  else "CLAIM_SURVIVED", actor=r["client_id"],
                                  refs={"hyp_id": ex["hyp_id"], "obs_id": oid})
        return oid

    def record_failure(self, world_id: str, *, failure_type: str,
                       falsifier: str, violated: str,
                       client_id: Optional[str] = None,
                       experiment_id: Optional[str] = None,
                       hypothesis_id: Optional[str] = None,
                       prediction_id: Optional[str] = None,
                       reference: Any = None, expected: Any = None,
                       observed: Any = None, measurement_id: Optional[str] = None,
                       artifact_refs: Optional[list] = None,
                       reproducibility: str = "UNKNOWN",
                       extensions: Optional[dict] = None) -> str:
        fid = new_id("failure")
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            ev = events.append(cx, world_id, "FAILURE_RECORDED",
                               actor=r["client_id"], refs={"failure_id": fid,
                               "experiment_id": experiment_id},
                               payload={"failure_type": failure_type})
            cx.execute(
                "INSERT INTO failures(failure_id,world_id,experiment_id,"
                "hypothesis_id,prediction_id,failure_type,reference,expected,"
                "observed,falsifier,violated,measurement_id,artifact_refs,"
                "reproducibility,extensions,created_ts,created_seq) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (fid, world_id, experiment_id, hypothesis_id, prediction_id,
                 failure_type, json.dumps(reference), json.dumps(expected),
                 json.dumps(observed), falsifier, violated, measurement_id,
                 json.dumps(artifact_refs or []), reproducibility,
                 json.dumps(extensions or {}), now(), ev["event_seq"]))
        return fid

    def consume_failure(self, world_id: str, failure_id: str, dst_kind: str,
                        dst_id: str, *, client_id: Optional[str] = None) -> str:
        """Record an agent's CLAIM that a failure was used to produce a
        downstream object. This is a CLAIMED reference only -- whether it was
        causally or empirically useful is a separate, measurable question
        (section 8)."""
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            if cx.execute("SELECT 1 FROM failures WHERE failure_id=? AND "
                          "world_id=?", (failure_id, world_id)).fetchone() is None:
                raise NotFound("failure not in this world", failure_id=failure_id)
            eid = self._edge(cx, world_id, r["client_id"], "failure",
                             failure_id, dst_kind, dst_id, "CONSUMED_BY")
            events.append(cx, world_id, "FAILURE_CONSUMED", actor=r["client_id"],
                          refs={"failure_id": failure_id, "dst_id": dst_id,
                                "dst_kind": dst_kind})
        return eid

    def _edge(self, cx, world_id, actor, src_kind, src_id, dst_kind, dst_id,
              relation, claimed=1) -> str:
        eid = new_id("edge")
        ev = events.append(cx, world_id, "LINEAGE_EDGE_ADDED", actor=actor,
                           refs={"src": src_id, "dst": dst_id,
                                 "relation": relation})
        cx.execute("INSERT INTO lineage_edges(edge_id,world_id,src_kind,src_id,"
                   "dst_kind,dst_id,relation,claimed,created_ts,created_seq) "
                   "VALUES(?,?,?,?,?,?,?,?,?,?)",
                   (eid, world_id, src_kind, src_id, dst_kind, dst_id, relation,
                    claimed, now(), ev["event_seq"]))
        return eid

    def add_lineage_edge(self, world_id, src_kind, src_id, dst_kind, dst_id,
                         relation, *, client_id=None) -> str:
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            return self._edge(cx, world_id, r["client_id"], src_kind, src_id,
                              dst_kind, dst_id, relation)

    # ================= artifacts + import (provenance) ==================
    def create_artifact(self, world_id: str, kind: str, data: bytes, *,
                        client_id: Optional[str] = None,
                        meta: Optional[dict] = None) -> dict:
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            blob = self.store.put_blob(data if isinstance(data, bytes)
                                       else str(data).encode())
            aid = content_hash({"world": world_id, "kind": kind, "blob": blob,
                                "meta": meta or {}})
            ev = events.append(cx, world_id, "ARTIFACT_CREATED",
                               actor=r["client_id"],
                               refs={"artifact_id": aid}, artifacts=[blob])
            cx.execute(
                "INSERT OR IGNORE INTO artifacts(artifact_id,world_id,kind,"
                "blob_hash,meta,origin,created_ts,created_seq) "
                "VALUES(?,?,?,?,?, 'NATIVE',?,?)",
                (aid, world_id, kind, blob, json.dumps(meta or {}), now(),
                 ev["event_seq"]))
            return {"artifact_id": aid, "blob_hash": blob, "origin": "NATIVE"}

    def get_artifact(self, world_id: str, artifact_id: str, *,
                     client_id: Optional[str] = None) -> dict:
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        r = cx.execute("SELECT * FROM artifacts WHERE world_id=? AND "
                       "artifact_id=?", (world_id, artifact_id)).fetchone()
        if r is None:
            raise NotFound("artifact not in this world", artifact_id=artifact_id)
        return _artifact_dict(r)

    def _may_cross(self, dst_row, src_row, info_kind: str, *,
                   same_client: bool) -> bool:
        """Whether `info_kind` may cross from src world to dst world (section 13).

        The DESTINATION must accept the kind (its sharing policy admits it). For a
        CROSS-client import (experimenter B pulling from experimenter A) that is
        NOT sufficient: A must have consented, so we additionally require an
        explicit bilateral topology share -- both worlds in the SAME (non-null)
        topology_group AND the SOURCE world's own policy emits this kind. Within a
        single client's own program (same_client) the experimenter controls both
        ends, so only the destination gate + matching-group rule apply. ISOLATED
        emits and accepts nothing, so it forbids all crossing in either role."""
        if info_kind not in SHARING_POLICIES.get(dst_row["sharing_policy"],
                                                 frozenset()):
            return False
        dg, sg = dst_row["topology_group"], src_row["topology_group"]
        if same_client:
            return not (dg is not None and sg is not None and dg != sg)
        # cross-client: an explicit bilateral topology share is mandatory, and
        # the SOURCE world must itself emit this kind (A's own consent).
        if dg is None or sg is None or dg != sg:
            return False
        return info_kind in SHARING_POLICIES.get(src_row["sharing_policy"],
                                                 frozenset())

    def import_artifact(self, dst_world: str, src_world: str,
                        src_artifact_id: str, *,
                        client_id: Optional[str] = None) -> dict:
        """Explicit cross-world import. The imported artifact is recorded with
        permanent provenance (origin=IMPORTED, source world/artifact/hash) so it
        can NEVER be mistaken for something independently discovered in the
        destination (I5, section 14, T10). Governed by the destination's sharing
        policy (T14)."""
        with self.store.write() as cx:
            dst = self._authorize(cx, dst_world, client_id)   # must own dest
            src = self._world_row(cx, src_world)
            same_client = (client_id is None
                           or src["client_id"] == client_id)
            # A CROSS-client import requires an explicit bilateral topology share.
            # Deny (uniformly, BEFORE the artifact is looked up) otherwise, so a
            # non-owner can neither pull a foreign artifact's bytes nor probe
            # which artifact ids exist in another experimenter's world (I5).
            if not same_client:
                dg, sg = dst["topology_group"], src["topology_group"]
                if dg is None or sg is None or dg != sg:
                    raise AccessDenied(
                        "cross-world import requires a shared topology group",
                        dst_world=dst_world, src_world=src_world)
            srow = cx.execute("SELECT * FROM artifacts WHERE world_id=? AND "
                              "artifact_id=?",
                              (src_world, src_artifact_id)).fetchone()
            if srow is None:
                raise NotFound("source artifact not found",
                               src_artifact_id=src_artifact_id)
            # The information KIND (failure / hypothesis / artifact / ...) the
            # artifact represents governs whether policy lets it cross; a
            # "success" carries kind 'artifact', a shared failure carries
            # 'failure'. Re-check with the specific kind (the earlier check used
            # the generic 'artifact' as a fast gate).
            info_kind = json.loads(srow["meta"]).get("info_kind", "artifact")
            if not self._may_cross(dst, src, info_kind, same_client=same_client):
                raise IsolationViolation(
                    "sharing policy forbids importing this information kind",
                    dst_world=dst_world, src_world=src_world, info_kind=info_kind,
                    dst_policy=dst["sharing_policy"])
            new_aid = content_hash({"import_into": dst_world,
                                    "source": src_artifact_id,
                                    "src_world": src_world})
            ev = events.append(cx, dst_world, "ARTIFACT_IMPORTED",
                               actor=dst["client_id"],
                               refs={"artifact_id": new_aid,
                                     "source_world": src_world,
                                     "source_artifact": src_artifact_id,
                                     "source_hash": srow["blob_hash"]},
                               artifacts=[srow["blob_hash"]])
            cx.execute(
                "INSERT OR IGNORE INTO artifacts(artifact_id,world_id,kind,"
                "blob_hash,meta,origin,source_world,source_artifact,import_seq,"
                "created_ts,created_seq) VALUES(?,?,?,?,?, 'IMPORTED',?,?,?,?,?)",
                (new_aid, dst_world, srow["kind"], srow["blob_hash"],
                 srow["meta"], src_world, src_artifact_id, ev["event_seq"],
                 now(), ev["event_seq"]))
            return {"artifact_id": new_aid, "origin": "IMPORTED",
                    "source_world": src_world, "source_artifact": src_artifact_id,
                    "source_hash": srow["blob_hash"]}

    # ================= checkpoint + fork ================================
    def checkpoint(self, world_id: str, *, client_id: Optional[str] = None,
                   meta: Optional[dict] = None) -> dict:
        ckid = new_id("checkpoint")
        with self.store.write() as cx:
            r = self._authorize(cx, world_id, client_id)
            idx = int(r["next_index"]) - 1     # last committed event index
            head = r["head_hash"] or ""
            snap = self._state_snapshot(cx, world_id)
            state_hash = content_hash(snap)
            cx.execute(
                "INSERT INTO checkpoints(checkpoint_id,world_id,world_index,"
                "head_hash,state_hash,meta,created_ts) VALUES(?,?,?,?,?,?,?)",
                (ckid, world_id, idx, head, state_hash,
                 json.dumps(meta or {}), now()))
            events.append(cx, world_id, "CHECKPOINT_CREATED",
                          actor=r["client_id"],
                          refs={"checkpoint_id": ckid},
                          payload={"world_index": idx, "state_hash": state_hash})
        return {"checkpoint_id": ckid, "world_index": idx, "head_hash": head,
                "state_hash": state_hash}

    def _state_snapshot(self, cx, world_id: str) -> dict:
        def c(t):
            return cx.execute(f"SELECT COUNT(*) n FROM {t} WHERE world_id=?",
                              (world_id,)).fetchone()["n"]
        return {"hypotheses": c("hypotheses"), "predictions": c("predictions"),
                "experiments": c("experiments"), "observations": c("observations"),
                "failures": c("failures"), "artifacts": c("artifacts"),
                "head": self._world_row(cx, world_id)["head_hash"]}

    def fork(self, world_id: str, checkpoint_id: str, children: list, *,
             client_id: Optional[str] = None) -> list:
        """Fork a world at a checkpoint into N children. Each child SHARES the
        parent's immutable event prefix up to the checkpoint BY REFERENCE (not a
        copy), then diverges independently. Parent rows are never written by a
        child and vice versa, so they cannot mutate one another (I5, section 5,
        T9). Inherited artifact hashes and per-child interventions are recorded
        in each child's WORLD_FORKED event.

        NOTE: fork inherits EVIDENCE (the event history) by reference. Relational
        research-state is per-child (empty at fork); identical starting
        conditions for a counterfactual are established by identical seed_root +
        identical initial configuration, which keeps mutation-isolation
        structural rather than copy-based.
        """
        out = []
        with self.store.write() as cx:
            parent = self._authorize(cx, world_id, client_id)
            ck = cx.execute("SELECT * FROM checkpoints WHERE checkpoint_id=? "
                            "AND world_id=?",
                            (checkpoint_id, world_id)).fetchone()
            if ck is None:
                raise NotFound("checkpoint not in this world",
                               checkpoint_id=checkpoint_id)
            fork_point = int(ck["world_index"])
            fork_head = ck["head_hash"]
            inherited_hashes = [r["blob_hash"] for r in cx.execute(
                "SELECT blob_hash FROM artifacts WHERE world_id=? AND "
                "created_seq<=(SELECT event_seq FROM events WHERE world_id=? AND "
                "world_index=?)", (world_id, world_id, fork_point)).fetchall()]
            plimits = cx.execute("SELECT limits FROM budgets WHERE world_id=?",
                                 (world_id,)).fetchone()
            for spec in children:
                cwid = new_id("world")
                pol = spec.get("sharing_policy", parent["sharing_policy"])
                if pol not in SHARING_POLICIES:
                    raise ValidationError("unknown sharing policy",
                                          sharing_policy=pol)
                sroot = spec.get("seed_root", parent["seed_root"])
                cx.execute(
                    "INSERT INTO worlds(world_id,session_id,client_id,name,"
                    "state,parent_world_id,fork_point,sharing_policy,"
                    "topology_group,seed_root,next_index,head_hash,created_ts) "
                    "VALUES(?,?,?,?,'CREATED',?,?,?,?,?,?,?,?)",
                    (cwid, parent["session_id"], parent["client_id"],
                     spec.get("name", "fork"), world_id, fork_point, pol,
                     spec.get("topology_group", parent["topology_group"]),
                     int(sroot), fork_point + 1, fork_head, now()))
                cx.execute("INSERT INTO budgets(world_id,limits,consumed,"
                           "updated_ts) VALUES(?,?,?,?)",
                           (cwid, plimits["limits"], json.dumps({}), now()))
                # the child's FIRST event chains onto the parent's fork head
                events.append(cx, cwid, "WORLD_FORKED", actor=parent["client_id"],
                              refs={"parent_world": world_id,
                                    "checkpoint_id": checkpoint_id},
                              artifacts=inherited_hashes,
                              payload={"fork_point": fork_point,
                                       "parent_head": fork_head,
                                       "interventions": spec.get("interventions",
                                                                 {})})
                out.append(self.get_world(cwid, parent["client_id"]))
        return out

    # ================= measurements ====================================
    def register_measurement(self, name: str, version: str, *,
                             implementation_hash: str, domain: str,
                             params: Optional[dict] = None,
                             inputs: Optional[list] = None,
                             outputs: Optional[list] = None,
                             provenance: Optional[dict] = None,
                             validation_status: str = "UNVALIDATED") -> str:
        mid = new_id("measurement")
        with self.store.write() as cx:
            try:
                cx.execute(
                    "INSERT INTO measurements(measurement_id,name,version,"
                    "implementation_hash,params,domain,inputs,outputs,"
                    "provenance,validation_status,created_ts) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (mid, name, version, implementation_hash,
                     json.dumps(params or {}), domain, json.dumps(inputs or []),
                     json.dumps(outputs or []), json.dumps(provenance or {}),
                     validation_status, now()))
            except Exception as e:
                if "UNIQUE" in str(e):
                    raise ValidationError(
                        "measurement (name,version) already registered; a new "
                        "definition needs a new version -- oracles are not "
                        "silently replaced", name=name, version=version)
                raise
            events.append_foundry(cx, "MEASUREMENT_REGISTERED", actor="foundry",
                                  scope_kind="foundry", scope_id=mid,
                                  payload={"name": name, "version": version,
                                           "implementation_hash":
                                           implementation_hash})
        return mid

    def get_measurement(self, measurement_id: str) -> dict:
        r = self.store.read().execute(
            "SELECT * FROM measurements WHERE measurement_id=?",
            (measurement_id,)).fetchone()
        if r is None:
            raise NotFound("unknown measurement", measurement_id=measurement_id)
        return {k: r[k] for k in r.keys()}

    # ================= observability + accounting ======================
    def verify_world(self, world_id: str) -> dict:
        return events.verify_world(self.store.read(), world_id)

    def world_events(self, world_id: str, *, client_id: Optional[str] = None,
                     limit: int = 100) -> list:
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        rows = cx.execute("SELECT * FROM events WHERE world_id=? ORDER BY "
                          "world_index DESC LIMIT ?", (world_id, limit)).fetchall()
        return [events._row_to_event(r) for r in rows][::-1]

    def world_history(self, world_id: str, *,
                      client_id: Optional[str] = None) -> list:
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        return events.world_history(cx, world_id)

    def epistemic_accounting(self, world_id: str, *,
                             client_id: Optional[str] = None) -> dict:
        """Mechanically-derived world statistics (section 19). Every number is a
        COUNT over authoritative rows/events -- no narration."""
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)

        def one(sql, *a):
            return cx.execute(sql, (world_id, *a)).fetchone()[0]
        hyp = one("SELECT COUNT(*) FROM hypotheses WHERE world_id=?")
        preds = one("SELECT COUNT(*) FROM predictions WHERE world_id=?")
        exps = one("SELECT COUNT(*) FROM experiments WHERE world_id=?")
        obs = one("SELECT COUNT(*) FROM observations WHERE world_id=?")
        fals = one("SELECT COUNT(*) FROM hypotheses WHERE world_id=? AND "
                   "state='FALSIFIED'")
        surv = one("SELECT COUNT(*) FROM hypotheses WHERE world_id=? AND "
                   "state='SURVIVED'")
        fails = one("SELECT COUNT(*) FROM failures WHERE world_id=?")
        # a failure is CONSUMED if it is the src of a CONSUMED_BY edge
        consumed = one(
            "SELECT COUNT(DISTINCT src_id) FROM lineage_edges WHERE world_id=? "
            "AND relation='CONSUMED_BY' AND src_kind='failure'")
        muts_from_fail = one(
            "SELECT COUNT(*) FROM lineage_edges WHERE world_id=? AND "
            "relation='CONSUMED_BY' AND src_kind='failure' AND "
            "dst_kind IN ('hypothesis','experiment')")
        return {
            "hypotheses_proposed": hyp, "predictions_registered": preds,
            "experiments_created": exps, "observations_recorded": obs,
            "claims_falsified": fals, "claims_surviving": surv,
            "failures_generated": fails, "failures_consumed": consumed,
            "failure_consumption_rate": (consumed / fails) if fails else 0.0,
            "mutations_attributed_to_failure": muts_from_fail,
            "unused_failure_count": fails - consumed,
            # NB: these three distinctions are section-8 load-bearing --
            # claimed consumption != causal lineage != empirical usefulness.
            "note": ("failures_consumed counts CLAIMED references only; whether "
                     "a consumed failure improved search is a separate "
                     "empirical question, not implied by this count"),
        }

    def world_status(self, world_id: str, *,
                     client_id: Optional[str] = None) -> dict:
        cx = self.store.read()
        r = self._authorize(cx, world_id, client_id)
        t = now()
        qd = {row["status"]: row["n"] for row in cx.execute(
            "SELECT status, COUNT(*) n FROM work_items WHERE world_id=? "
            "GROUP BY status", (world_id,)).fetchall()}
        active_workers = [x["claimed_by"] for x in cx.execute(
            "SELECT DISTINCT claimed_by FROM work_items WHERE world_id=? AND "
            "status IN ('CLAIMED','RUNNING') AND lease_expires>? AND "
            "claimed_by IS NOT NULL", (world_id, t)).fetchall()]
        expired = cx.execute(
            "SELECT COUNT(*) n FROM work_items WHERE world_id=? AND status IN "
            "('CLAIMED','RUNNING') AND lease_expires<=?",
            (world_id, t)).fetchone()["n"]
        fail_by_type = {x["failure_type"]: x["n"] for x in cx.execute(
            "SELECT failure_type, COUNT(*) n FROM failures WHERE world_id=? "
            "GROUP BY failure_type", (world_id,)).fetchall()}
        ckp = cx.execute("SELECT COUNT(*) n, MAX(world_index) m FROM "
                         "checkpoints WHERE world_id=?", (world_id,)).fetchone()
        try:
            integrity = self.verify_world(world_id)
            integrity_ok = integrity["ok"]
        except Exception as e:                       # noqa: BLE001
            integrity_ok = False
        return {
            "world_id": world_id, "state": r["state"],
            "queue_depth": qd,
            "active_workers": active_workers,
            "active_worker_count": len(active_workers),
            "expired_leases": expired,
            "resources": self.budget_status(world_id),
            "failure_counts": fail_by_type,
            "event_count": r["next_index"],
            "checkpoints": {"count": ckp["n"], "latest_index": ckp["m"]},
            "epistemics": self.epistemic_accounting(world_id),
            "ledger_integrity_ok": integrity_ok,
            "head_hash": r["head_hash"],
        }

    # ================= lineage / failure queries ========================
    def descendants(self, world_id: str, kind: str, obj_id: str, *,
                    relations: Optional[set] = None) -> list:
        """All research objects reachable FROM (kind,obj_id) by recorded edges
        (section 10). BFS over lineage_edges within the world; the DAG is the
        recorded references, never reconstructed."""
        cx = self.store.read()
        seen, frontier, out = {(kind, obj_id)}, [(kind, obj_id)], []
        while frontier:
            nk, nid = frontier.pop()
            q = ("SELECT dst_kind,dst_id,relation FROM lineage_edges WHERE "
                 "world_id=? AND src_kind=? AND src_id=?")
            for e in cx.execute(q, (world_id, nk, nid)).fetchall():
                if relations and e["relation"] not in relations:
                    continue
                node = (e["dst_kind"], e["dst_id"])
                out.append({"kind": e["dst_kind"], "id": e["dst_id"],
                            "relation": e["relation"], "via": (nk, nid)})
                if node not in seen:
                    seen.add(node); frontier.append(node)
        return out

    def ancestors(self, world_id: str, kind: str, obj_id: str) -> list:
        cx = self.store.read()
        seen, frontier, out = {(kind, obj_id)}, [(kind, obj_id)], []
        while frontier:
            nk, nid = frontier.pop()
            for e in cx.execute("SELECT src_kind,src_id,relation FROM "
                                "lineage_edges WHERE world_id=? AND dst_kind=? "
                                "AND dst_id=?", (world_id, nk, nid)).fetchall():
                node = (e["src_kind"], e["src_id"])
                out.append({"kind": e["src_kind"], "id": e["src_id"],
                            "relation": e["relation"], "of": (nk, nid)})
                if node not in seen:
                    seen.add(node); frontier.append(node)
        return out

    def query_failures(self, world_id: str, *, failure_type: Optional[str] = None,
                       consumed: Optional[bool] = None,
                       client_id: Optional[str] = None) -> list:
        cx = self.store.read()
        self._authorize(cx, world_id, client_id)
        q, a = "SELECT * FROM failures WHERE world_id=?", [world_id]
        if failure_type:
            q += " AND failure_type=?"; a.append(failure_type)
        rows = [dict(r) for r in cx.execute(q, tuple(a)).fetchall()]
        if consumed is not None:
            cons = {e["src_id"] for e in cx.execute(
                "SELECT DISTINCT src_id FROM lineage_edges WHERE world_id=? AND "
                "relation='CONSUMED_BY' AND src_kind='failure'",
                (world_id,)).fetchall()}
            rows = [r for r in rows
                    if (r["failure_id"] in cons) == consumed]
        return rows


def _artifact_dict(r) -> dict:
    return {"artifact_id": r["artifact_id"], "world_id": r["world_id"],
            "kind": r["kind"], "blob_hash": r["blob_hash"],
            "meta": json.loads(r["meta"]), "origin": r["origin"],
            "source_world": r["source_world"],
            "source_artifact": r["source_artifact"]}


def _world_dict(r) -> dict:
    return {"world_id": r["world_id"], "session_id": r["session_id"],
            "client_id": r["client_id"], "name": r["name"], "state": r["state"],
            "parent_world_id": r["parent_world_id"], "fork_point": r["fork_point"],
            "sharing_policy": r["sharing_policy"],
            "topology_group": r["topology_group"], "seed_root": r["seed_root"],
            "created_ts": r["created_ts"], "terminated_ts": r["terminated_ts"],
            "next_index": r["next_index"], "head_hash": r["head_hash"]}


def _work_dict(r) -> dict:
    return {"work_id": r["work_id"], "world_id": r["world_id"], "kind": r["kind"],
            "payload": json.loads(r["payload"]), "status": r["status"],
            "priority": r["priority"], "attempts": r["attempts"],
            "max_attempts": r["max_attempts"], "claimed_by": r["claimed_by"],
            "lease_expires": r["lease_expires"], "heartbeat_ts": r["heartbeat_ts"],
            "result": json.loads(r["result"]) if r["result"] else None,
            "result_hash": r["result_hash"], "error": r["error"],
            "dedup_key": r["dedup_key"]}
