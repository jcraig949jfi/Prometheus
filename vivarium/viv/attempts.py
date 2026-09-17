"""Attempts, steps, receipts and the termination envelope beneath a queue row
(point release; roles/Vivarium/point_release/EXPERIMENT_TRANSACTION_MODEL.md,
TERMINATION_ENVELOPE.md, PREREQUISITE_GATE_RECEIPT.md,
INTERVENTION_RECEIPT_SCHEMA.md).

FEATURE-DETECTED, NOT FLAGGED. The tables come from migrations 006-009,
which are DRAFTS until the coordinated window. `Attempts.enabled` is true
iff `execution_attempt` exists in this schema; when it does not, every
method here is a no-op that returns what the loop needs to behave exactly
as it does today. So this code can land on main before the window without
changing production, and a throwaway test schema with the drafts applied
exercises the whole thing.

What is absorbed from archaeon/campaign2/runner.py Attempt:
    numbered attempts, never renamed; parent attempt on a NEW ATTEMPT;
    a step key that contains the design digest (viv/stepkey.py; trigger
    VIV20); REUSED / REPLAYED / RECOMPUTED / NEW / FAILED on every step;
    a receipt readable at any moment (the rows ARE the receipt).
What is not: any scientific reading of a result.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from . import db as _db
from . import spec as _spec
from . import stepkey as _sk

UNKNOWN = "UNKNOWN"
TERMINATION_VERSION = "viv.termination.v1"

#: Closed set (TERMINATION_ENVELOPE.md s2).
REASONS = ("COMPLETED_ALL_REPEATS", "STOPPED_ON_CONDITION", "HORIZON_REACHED",
           "BUDGET_EXHAUSTED", "PREREQUISITE_FAILED", "INSTRUMENT_INVALID",
           "EXECUTOR_ERROR", "ENGINE_TRANSPORT", "CANCELLED", "STRANDED", "UNKNOWN")
COMPLETED_REASONS = ("COMPLETED_ALL_REPEATS", "STOPPED_ON_CONDITION",
                     "HORIZON_REACHED", "BUDGET_EXHAUSTED")
CENSORING_REASONS = ("HORIZON_REACHED", "BUDGET_EXHAUSTED", "CANCELLED", "STRANDED",
                     "INSTRUMENT_INVALID")


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _digest(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(_spec.canonical_bytes(obj)).hexdigest()


def terminal_state_for(reason: str) -> str:
    if reason in COMPLETED_REASONS:
        return "COMPLETED"
    if reason in ("CANCELLED", "STRANDED"):
        return reason
    if reason == "UNKNOWN":
        return "FAILED"
    return "FAILED"


def envelope(reason: str, *, horizon: Optional[dict] = None, consumed: Optional[dict] = None,
             logical_time: Any = UNKNOWN, stopped_on: Optional[dict] = None,
             observations_recorded: int = 0, expected_observations: Optional[int] = None,
             censored_endpoints: Optional[list] = None, engine_termination_ref: Any = None,
             receipt_ref: Optional[dict] = None) -> dict:
    """The termination envelope. `censored` is MECHANICAL from the reason
    (plus any producer-named censored endpoints); nothing scientific."""
    if reason not in REASONS:
        raise ValueError("termination_reason %r is not in the closed set" % (reason,))
    censored = reason in CENSORING_REASONS or bool(censored_endpoints)
    partial = (expected_observations is not None and observations_recorded < expected_observations)
    return {
        "envelope_version": TERMINATION_VERSION,
        "termination_reason": reason,
        "terminal_state": terminal_state_for(reason),
        "horizon": horizon or {"kind": UNKNOWN, "declared": UNKNOWN},
        "budget_consumed": consumed or {},
        "logical_time_reached": logical_time,
        "stopped_on_condition": stopped_on,
        "censored": censored,
        "censoring_reason": reason if reason in CENSORING_REASONS else None,
        "censored_endpoints": list(censored_endpoints or []),
        "partial": partial,
        "observations_recorded": int(observations_recorded),
        "engine_termination_ref": engine_termination_ref,
        "terminal_receipt_ref": receipt_ref,
    }


@dataclass
class AttemptCtx:
    attempt_id: str
    experiment_id: str
    attempt_number: int
    design_digest: str
    parent_attempt_id: Optional[str]
    prior_steps: Dict[str, dict] = field(default_factory=dict)   # step_key -> prior step row (newest terminal attempt)
    steps: List[dict] = field(default_factory=list)
    enabled: bool = True


class Attempts:
    def __init__(self, *, schema: str, worker_id: str, log=print):
        self.schema = schema
        self.worker_id = worker_id
        self.log = log
        self._enabled: Optional[bool] = None

    # -- feature detection ------------------------------------------------
    def enabled(self, conn) -> bool:
        if self._enabled is None:
            with conn.cursor() as cur:
                cur.execute("SELECT to_regclass(%s)", (self.schema + ".execution_attempt",))
                self._enabled = cur.fetchone()[0] is not None
            conn.rollback()
        return self._enabled

    # -- open / close ------------------------------------------------------
    def open(self, conn, row, *, grant: dict, bundle_hash: Optional[str] = None,
             bundle_hash_declared: Optional[str] = None) -> AttemptCtx:
        eid = str(row["experiment_id"])
        if not self.enabled(conn):
            return AttemptCtx(attempt_id=eid, experiment_id=eid, attempt_number=1,
                              design_digest=row["spec_hash"], parent_attempt_id=None, enabled=False)
        with _db.dict_cur(conn) as cur:
            cur.execute("SELECT attempt_id, attempt_number, terminal_state FROM " + self.schema +
                        ".execution_attempt WHERE experiment_id = %s ORDER BY attempt_number DESC LIMIT 1", (eid,))
            prev = cur.fetchone()
            if prev is not None and prev["terminal_state"] is None:
                raise RuntimeError("attempt %s of %s is still OPEN; a NEW ATTEMPT opens only after a terminal one"
                                   % (prev["attempt_number"], eid))
            number = (prev["attempt_number"] + 1) if prev else 1
            parent = str(prev["attempt_id"]) if prev else None
            cur.execute("INSERT INTO " + self.schema + ".execution_attempt (experiment_id, attempt_number, "
                        "parent_attempt_id, design_digest, bundle_hash, bundle_hash_declared, worker_id, claim_grant) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING attempt_id",
                        (eid, number, parent, row["spec_hash"], bundle_hash, bundle_hash_declared,
                         self.worker_id, json.dumps(grant, default=str)))
            aid = str(cur.fetchone()["attempt_id"])
            prior: Dict[str, dict] = {}
            if parent is not None:
                cur.execute("SELECT step_id, step_key, step_kind, parts, status, result, result_digest FROM "
                            + self.schema + ".execution_step WHERE attempt_id = %s AND status <> 'FAILED'", (parent,))
                for r in cur.fetchall():
                    prior[r["step_key"]] = dict(r)
        conn.commit()
        self.log("[viv] attempt %d opened for %s (parent %s, %d prior step(s) available)"
                 % (number, eid[:8], parent[:8] if parent else "-", len(prior)))
        return AttemptCtx(attempt_id=aid, experiment_id=eid, attempt_number=number,
                          design_digest=row["spec_hash"], parent_attempt_id=parent, prior_steps=prior)

    def close(self, conn, ctx: AttemptCtx, *, termination: dict, extra: Optional[dict] = None) -> Optional[str]:
        """Terminal. Writes the envelope, the receipt digest and of_record."""
        if not ctx.enabled:
            return None
        receipt = self.receipt(conn, ctx, termination=termination, extra=extra)
        rdig = _digest(receipt)
        state = termination["terminal_state"]
        with conn.cursor() as cur:
            if state == "COMPLETED":
                cur.execute("UPDATE " + self.schema + ".execution_attempt SET of_record = false "
                            "WHERE experiment_id = %s AND of_record", (ctx.experiment_id,))
            cur.execute("UPDATE " + self.schema + ".execution_attempt SET terminal_state = %s, termination = %s, "
                        "receipt_digest = %s, closed_at = now(), of_record = %s WHERE attempt_id = %s",
                        (state, json.dumps(termination, default=str), rdig, state == "COMPLETED", ctx.attempt_id))
        conn.commit()
        return rdig

    # -- steps -------------------------------------------------------------
    def step(self, conn, ctx: AttemptCtx, kind: str, fn: Callable[[], Any], *, parts=(),
             replayable: bool = False, verify: Optional[Callable[[Any], bool]] = None,
             idempotency_key: Optional[str] = None) -> Any:
        """Run `fn` as a keyed step, or take a prior attempt's result.

        REUSED     prior result taken, no verifier, kind declared pure (replayable and verify is None)
        REPLAYED   prior result taken after verify(prior) returned True
        RECOMPUTED executed although a prior result existed (not replayable, or verify failed)
        NEW        executed; no prior result for this key
        FAILED     fn raised; recorded; re-raised
        """
        if not ctx.enabled:
            return fn()
        key = _sk.step_key(ctx.design_digest, kind, list(parts))
        prior = ctx.prior_steps.get(key)
        status = "NEW"
        replay_of = None
        recomputed_from = None
        if prior is not None:
            if replayable:
                ok = True if verify is None else self._verify(verify, prior.get("result"))
                if ok:
                    status = "REUSED" if verify is None else "REPLAYED"
                    replay_of = str(prior["step_id"])
                else:
                    status = "RECOMPUTED"; recomputed_from = str(prior["step_id"])
            else:
                status = "RECOMPUTED"; recomputed_from = str(prior["step_id"])
        if status in ("REUSED", "REPLAYED"):
            result = prior.get("result")
            self._insert_step(conn, ctx, key, kind, parts, status, result=result, replay_of=replay_of,
                              idempotency_key=idempotency_key or key, completed=True)
            self.log("[viv] step %s %s (attempt %d)" % (kind, status, ctx.attempt_number))
            return result
        sid = self._insert_step(conn, ctx, key, kind, parts, status, recomputed_from=recomputed_from,
                                idempotency_key=idempotency_key or key, completed=False)
        try:
            result = fn()
        except BaseException as exc:                              # noqa: BLE001
            self._finish_step(conn, ctx, sid, status="FAILED", error="%s: %s" % (type(exc).__name__, str(exc)[:2000]))
            raise
        self._finish_step(conn, ctx, sid, status=status, result=result)
        return result

    @staticmethod
    def _verify(verify, prior_result) -> bool:
        try:
            return bool(verify(prior_result))
        except Exception:                                          # noqa: BLE001
            return False

    def _insert_step(self, conn, ctx, key, kind, parts, status, *, result=None, replay_of=None,
                     recomputed_from=None, idempotency_key=None, completed=False) -> str:
        rec = _jsonable(result)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO " + self.schema + ".execution_step (attempt_id, step_key, step_kind, parts, "
                        "status, replay_of_step, recomputed_from_step, idempotency_key, result, result_digest, completed_at) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING step_id",
                        (ctx.attempt_id, key, kind, json.dumps(list(parts)), status, replay_of, recomputed_from,
                         idempotency_key, json.dumps(rec, default=str) if completed else None,
                         _digest(rec) if completed else None, _utc() if completed else None))
            sid = str(cur.fetchone()[0])
        conn.commit()
        ctx.steps.append({"step_id": sid, "step_key": key, "step_kind": kind, "parts": list(parts), "status": status})
        return sid

    def _finish_step(self, conn, ctx: AttemptCtx, sid: str, *, status: str, result=None,
                     error: Optional[str] = None) -> None:
        rec = _jsonable(result)
        # a failed step's transaction may be aborted; the receipt row must still land
        conn.rollback()
        with conn.cursor() as cur:
            cur.execute("UPDATE " + self.schema + ".execution_step SET status = %s, result = %s, result_digest = %s, "
                        "error = %s, completed_at = now() WHERE step_id = %s",
                        (status, json.dumps(rec, default=str) if error is None else None,
                         _digest(rec) if error is None else None, error, sid))
        conn.commit()
        for s in reversed(ctx.steps):
            if s["step_id"] == sid:
                s["status"] = status
                break

    # -- receipts --------------------------------------------------------------
    def gate_receipt(self, conn, ctx: AttemptCtx, *, gate: dict, measurement_ref: dict, measured: Any,
                     reference: Any, result: str, step_id: Optional[str] = None) -> Optional[str]:
        if not ctx.enabled:
            return None
        with conn.cursor() as cur:
            cur.execute("INSERT INTO " + self.schema + ".gate_receipt (attempt_id, step_id, gate_id, phase, condition, "
                        "measurement_ref, measured, rule, reference, result, definition_ref) VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING receipt_id",
                        (ctx.attempt_id, step_id, gate["gate_id"], gate.get("phase", "pre_execution"),
                         gate.get("condition", ""), json.dumps(measurement_ref, default=str),
                         json.dumps(_jsonable(measured), default=str), json.dumps(gate.get("rule", {}), default=str),
                         json.dumps(_jsonable(reference), default=str), result, gate.get("definition_ref", UNKNOWN)))
            rid = str(cur.fetchone()[0])
        conn.commit()                                                # DURABLE before any dependent action (operator s5)
        return rid

    def gate_action(self, conn, receipt_id: Optional[str], action: str) -> None:
        if receipt_id is None:
            return
        with conn.cursor() as cur:
            cur.execute("UPDATE " + self.schema + ".gate_receipt SET action_taken = %s WHERE receipt_id = %s",
                        (action, receipt_id))
        conn.commit()

    def intervention_receipt(self, conn, ctx: AttemptCtx, *, intervention_id: str, kind: str, writer: str,
                             intended: dict, realised: dict, target: dict, logical_time: Any = None,
                             supplied: Optional[list] = None, source_ids: Optional[list] = None,
                             applier_result: Optional[str] = None, reason: Optional[str] = None,
                             post_ref: Any = None, step_id: Optional[str] = None) -> Optional[str]:
        if not ctx.enabled:
            return None
        result = derive_intervention_result(intended, realised, applier_result)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO " + self.schema + ".intervention_receipt (attempt_id, step_id, intervention_id, "
                        "intervention_kind, writer, intended, realised, logical_time, target, supplied, source_ids, "
                        "result, reason, post_ref) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                        "RETURNING receipt_id",
                        (ctx.attempt_id, step_id, intervention_id, kind, writer, json.dumps(intended, default=str),
                         json.dumps(realised, default=str), json.dumps(logical_time, default=str),
                         json.dumps(target, default=str), json.dumps(supplied or [], default=str),
                         json.dumps(source_ids or [], default=str), result, reason, json.dumps(post_ref, default=str)))
            rid = str(cur.fetchone()[0])
        conn.commit()
        return rid

    def receipt(self, conn, ctx: AttemptCtx, *, termination: Optional[dict] = None, extra: Optional[dict] = None) -> dict:
        """The attempt receipt, assembled from ROWS (never from memory)."""
        if not ctx.enabled:
            return {}
        with _db.dict_cur(conn) as cur:
            cur.execute("SELECT attempt_id, experiment_id, attempt_number, parent_attempt_id, design_digest, bundle_hash, "
                        "bundle_hash_declared, worker_id, opened_at FROM " + self.schema + ".execution_attempt WHERE attempt_id = %s",
                        (ctx.attempt_id,))
            a = dict(cur.fetchone())
            cur.execute("SELECT step_key, step_kind, parts, status, replay_of_step, recomputed_from_step, idempotency_key, "
                        "result_digest, error FROM " + self.schema + ".execution_step WHERE attempt_id = %s ORDER BY started_at",
                        (ctx.attempt_id,))
            steps = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT gate_id, phase, result, action_taken, measured, reference FROM " + self.schema +
                        ".gate_receipt WHERE attempt_id = %s ORDER BY evaluated_at", (ctx.attempt_id,))
            gates = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT intervention_id, intervention_kind, writer, intended, realised, result, reason FROM "
                        + self.schema + ".intervention_receipt WHERE attempt_id = %s ORDER BY recorded_at", (ctx.attempt_id,))
            interventions = [dict(r) for r in cur.fetchall()]
        conn.rollback()
        counts = {"NEW": 0, "REUSED": 0, "REPLAYED": 0, "RECOMPUTED": 0, "FAILED": 0}
        for s in steps:
            counts[s["status"]] = counts.get(s["status"], 0) + 1
        inter = {"declared": len(interventions)}
        for r in ("APPLIED", "PARTIAL", "NOT_APPLIED", "REJECTED", "UNKNOWN"):
            inter[r.lower()] = sum(1 for i in interventions if i["result"] == r)
        return _jsonable({"receipt_version": "viv.attempt_receipt.v1", "attempt": a, "steps": steps,
                          "step_counts": counts, "gates": gates, "interventions": interventions,
                          "intervention_summary": inter, "termination": termination, **(extra or {})})


def derive_intervention_result(intended: dict, realised: dict, applier_result: Optional[str]) -> str:
    """Mechanical, numeric keys only (INTERVENTION_RECEIPT_SCHEMA.md s1)."""
    if applier_result == "REJECTED":
        return "REJECTED"
    nums = [(k, v) for k, v in (intended or {}).items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if not nums:
        return "APPLIED" if applier_result in ("APPLIED", "OK", "SUCCESS") else "UNKNOWN"
    if any((realised or {}).get(k, UNKNOWN) == UNKNOWN for k, _ in nums):
        return "UNKNOWN"
    got = [(v, (realised or {}).get(k)) for k, v in nums]
    if all(isinstance(r, (int, float)) and r == v for v, r in got):
        return "APPLIED"
    if all(isinstance(r, (int, float)) and r == 0 for _, r in got):
        return "NOT_APPLIED"
    return "PARTIAL"


def _jsonable(obj: Any) -> Any:
    return json.loads(json.dumps(obj, default=str))
