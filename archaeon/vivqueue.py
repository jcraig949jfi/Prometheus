"""Archaeon's writer against the CANONICAL pre-execution register.

That register is ``viv.research_experiment_queue``. Archaeon's own
``archaeon.experiment_queue`` is retired (migration 003) and nothing here
writes to it.

Three things this module is responsible for, and nothing else:

1. **Declaring the experimental relation** -- family, arm, replication_of,
   candidate-set membership -- in the PROVENANCE partition, never inside
   ``experiment_spec`` and therefore never inside ``spec_hash``. Vivarium's
   boundary review (F2) measured three fields that violate that rule today
   (``notes``, ``experiment_kind``, ``world.name``); Archaeon must not add a
   fourth. Two rows in different arms of the same comparison may have
   byte-identical specs, and *must* be able to: that is what makes a
   comparison a comparison rather than two unrelated experiments.

2. **Preserving cadence** -- at most SIX autonomous proposals per UTC day per
   lane, at least FOUR HOURS apart, enforced by the database so two concurrent
   Archaeon instances cannot evade it. Only a SELECTED row consumes quota.

3. **Registering the candidate set before selection**, and cancelling the
   unchosen rather than deleting them. S15 found seven of eight selection
   mechanisms are class B -- information-theoretically absent from the
   substrate. The queue is the only object in the architecture written before
   anything runs, immutable once accepted, with a permanent ``cancelled``
   terminal state. Writing the whole candidate set to it converts Archaeon's
   own selection from class B to class A. Nothing else in the system can do
   this, and it is not required of anyone else.

**The count is never attested.** There is deliberately no
``candidate_set_size`` column: a stored count is an assertion and can be
wrong, while ``viv.candidate_sets`` derives the count from the rows that
actually exist. Vivarium's review notes it cannot honestly attest a count it
never saw -- it is handed one candidate by construction -- and Archaeon
resolves that by making the register count itself rather than by attesting
harder. Registration and selection happen in ONE transaction, so a partially
registered set cannot be presented as a complete one.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional, Sequence, Tuple

from . import cadence as cad
from . import config as cfg
from .queue import (NegativeAuthorityViolation,  # re-exported: same guard
                    assert_no_negative_authority)

def _schema() -> str:
    """The queue schema, resolved through Vivarium's own resolver.

    Corrected 2026-09-06 (Vivarium). This was the constant string "viv", so
    Archaeon's writer had NO way to target a test schema -- and its test suite
    therefore wrote into the PRODUCTION canonical register. 245 rows arrived
    there in one run, and a live Vivarium cycle picked one up and tried to
    execute it. It failed validation and nothing was harmed, but a
    well-formed test row would have executed against the real engine and
    written a real PEW fossil. A register that a test suite can inject into is
    not a register. Honouring VIV_SCHEMA closes it, and Archaeon's conftest
    now sets one."""
    import sys
    from pathlib import Path
    vivdir = str(Path(__file__).resolve().parent.parent / "vivarium")
    if vivdir not in sys.path:
        sys.path.insert(0, vivdir)
    from viv import db as _vdb              # noqa: PLC0415
    return _vdb.schema()


def _queue() -> str:
    return _schema() + ".research_experiment_queue"


class _Q:
    """`QUEUE` kept as a name for readability; it now resolves per call."""

    def __str__(self):
        return _queue()

    def format(self, **kw):                 # for '...{q}...'.format(q=QUEUE)
        return str(self)


QUEUE = _Q()
AUTONOMOUS_REASONS = cad.AUTONOMOUS_REASONS

# Columns Vivarium's migration 002 must have created. Archaeon NEVER creates
# them: viv.research_experiment_queue is Vivarium's table, and a consumer that
# silently ALTERs a producer's schema is how two seats end up with two
# divergent definitions of one contract -- which already happened once here and
# was caught only because a view refused to drop a column.
REQUIRED_COLUMNS = ("family_id", "arm_id", "replication_of",
                    "candidate_set_id", "request_key",
                    "cadence_lane", "cadence_day_ordinal", "cadence_utc_day")


class QueueContractMissing(Exception):
    """Vivarium's relation/cadence migration has not been applied."""


def assert_queue_ready(conn) -> None:
    """Fail loudly rather than diverge silently."""
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='viv' "
                "  AND table_name='research_experiment_queue'")
    have = {r[0] for r in cur.fetchall()}
    if not have:
        raise QueueContractMissing(
            "viv.research_experiment_queue does not exist. Apply Vivarium's "
            "migrations; Archaeon does not create Vivarium's table.")
    missing = [c for c in REQUIRED_COLUMNS if c not in have]
    if missing:
        raise QueueContractMissing(
            "viv.research_experiment_queue is missing {}. Apply "
            "vivarium/migrations/002_relations_cadence_idempotency.sql. "
            "Archaeon will not create these columns itself: the table is "
            "Vivarium's, and a consumer that ALTERs a producer's schema is how "
            "one contract becomes two divergent definitions.".format(missing))


class RelationContractViolation(Exception):
    """A proposal tried to put design metadata where it does not belong."""


# Fields that must never appear in experiment_spec, because they would change
# spec_hash without changing what is executed -- Vivarium F2. The first three
# are the measured offenders; the rest are the relation vocabulary, which must
# live in columns.
FORBIDDEN_SPEC_KEYS = ("notes", "experiment_kind", "family_id", "arm_id",
                       "arm", "family", "candidate_set_id", "replication_of",
                       "policy", "source_reason", "created_by")


def assert_spec_is_execution_only(spec: Dict[str, Any]) -> None:
    """The sealed spec contains exactly the execution inputs.

    Harmonia S14: spec_hash is the substrate's grouping surface, so anything in
    the spec that does not change what is executed is a channel by which the
    selecting policy leaks into the sealed record and splits the derived
    universe along the arm boundary.
    """
    for k in FORBIDDEN_SPEC_KEYS:
        if k in spec:
            raise RelationContractViolation(
                "experiment_spec carries {!r}, which is design/provenance and "
                "not an execution input. It would change spec_hash without "
                "changing what is executed, splitting the derived universe "
                "along the policy boundary (Vivarium F2 / Harmonia S14). "
                "Declare it in a column instead.".format(k))
    w = spec.get("world")
    if isinstance(w, dict) and "name" in w:
        raise RelationContractViolation(
            "experiment_spec.world.name is inside spec_hash and is an "
            "author-supplied label; S14 already burned a result on trusting "
            "one. Vivarium derives the world name from spec_hash instead.")


# --------------------------------------------------------------------------
def _spec_hash(spec: Dict[str, Any]) -> str:
    """The canonicalization VIVARIUM and SFE use, imported rather than copied.

    Corrected 2026-09-06 (Vivarium). The local copy omitted
    ``ensure_ascii=False``, so Python escaped every non-ASCII character and
    Archaeon's hash diverged from the one SFE seals at commit for any spec
    containing one -- a hypothesis with an accent was enough. The queue and
    the ledger would then have been talking about different objects, silently
    and only sometimes. There is now ONE implementation of the
    canonicalization in the repo, and vivarium/tests/test_spec.py asserts it
    against sfe.ids.content_hash."""
    import sys
    from pathlib import Path
    vivdir = str(Path(__file__).resolve().parent.parent / "vivarium")
    if vivdir not in sys.path:
        sys.path.insert(0, vivdir)
    from viv.spec import spec_hash as _canonical      # noqa: PLC0415
    return _canonical(spec)


def make_candidate(spec: Dict[str, Any], *,
                   family_id: Optional[str] = None,
                   arm_id: Optional[str] = None,
                   replication_of: Optional[str] = None,
                   request_key: Optional[str] = None,
                   source_evidence: Optional[Dict[str, Any]] = None,
                   ) -> Dict[str, Any]:
    """One candidate: an execution-only spec plus its relation declaration."""
    assert_spec_is_execution_only(spec)
    return {"spec": spec, "spec_hash": _spec_hash(spec),
            "family_id": family_id, "arm_id": arm_id,
            "replication_of": replication_of,
            "request_key": request_key or ("rk-" + uuid.uuid4().hex[:16]),
            "source_evidence": source_evidence or {}}


# --------------------------------------------------------------------------
def _evaluate_cadence(cur, ccfg: cfg.CadenceConfig) -> cad.CadenceDecision:
    """Cadence over the CANONICAL queue. Same rules, new table.

    Counts only rows that consumed quota (cadence_day_ordinal IS NOT NULL), so
    registered-but-cancelled candidates are free. Uses the DATABASE clock.
    """
    lane = ccfg.lane
    cur.execute(
        """
        SELECT now() AS db_now,
               (now() AT TIME ZONE 'UTC')::date AS db_utc_day,
               count(*) AS n_today
          FROM {q}
         WHERE cadence_lane = %s
           AND cadence_day_ordinal IS NOT NULL
           AND cadence_utc_day = (now() AT TIME ZONE 'UTC')::date
        """.format(q=QUEUE), (lane,))
    db_now, db_day, n_today = cur.fetchone()
    n_today = int(n_today)

    # Separation spans the UTC day boundary: 23:50 and 00:10 are 20 minutes
    # apart even though they fall on different days.
    cur.execute(
        """
        SELECT max(created_at),
               EXTRACT(EPOCH FROM (now() - max(created_at)))
          FROM {q}
         WHERE cadence_lane = %s AND cadence_day_ordinal IS NOT NULL
        """.format(q=QUEUE), (lane,))
    last_any, since_any = cur.fetchone()

    detail: Dict[str, Any] = {
        "lane": lane, "queue": str(QUEUE),
        "db_now": str(db_now), "db_utc_day": str(db_day),
        "autonomous_today": n_today,
        "max_per_utc_day": ccfg.max_per_utc_day,
        "last_autonomous_at_any_day": str(last_any) if last_any else None,
        "seconds_since_last": float(since_any) if since_any is not None else None,
        "min_separation_seconds": ccfg.min_separation_seconds,
        "instance": cad.instance_id(), "clock_source": "postgres now()",
    }
    if n_today >= ccfg.max_per_utc_day:
        detail["refusal"] = ("{} autonomous proposals already executed for UTC "
                             "day {}".format(n_today, db_day))
        return cad.CadenceDecision(False, "REFUSED_DAILY_CAP", None, detail)
    if since_any is not None and float(since_any) < ccfg.min_separation_seconds:
        detail["refusal"] = (
            "last autonomous proposal was {:.0f}s ago; {}s required"
            .format(float(since_any), ccfg.min_separation_seconds))
        detail["next_eligible_in_seconds"] = (
            ccfg.min_separation_seconds - float(since_any))
        return cad.CadenceDecision(False, "REFUSED_MIN_SEPARATION", None, detail)
    return cad.CadenceDecision(True, "ADMITTED", n_today, detail)


def _insert(cur, c: Dict[str, Any], *, created_by: str, source_reason: str,
            candidate_set_id: Optional[str], lane: Optional[str],
            ordinal: Optional[int]) -> str:
    cur.execute(
        """
        INSERT INTO {q}
            (created_by, source_reason, source_evidence, experiment_spec,
             spec_hash, status, family_id, arm_id, replication_of,
             candidate_set_id, request_key, cadence_lane, cadence_day_ordinal)
        VALUES (%s, %s, %s::jsonb, %s::jsonb, %s, 'queued',
                %s, %s, %s, %s, %s, %s, %s)
        RETURNING experiment_id
        """.format(q=QUEUE),
        (created_by, source_reason, json.dumps(c["source_evidence"], default=str),
         json.dumps(c["spec"], default=str), c["spec_hash"],
         c["family_id"], c["arm_id"], c["replication_of"],
         candidate_set_id, c["request_key"], lane, ordinal))
    return str(cur.fetchone()[0])


def submit(conn, *, candidates: Sequence[Dict[str, Any]],
           selected_index: int,
           source_reason: str,
           created_by: str = "archaeon",
           config: Optional[cfg.ArchaeonConfig] = None,
           candidate_set_id: Optional[str] = None,
           ) -> Dict[str, Any]:
    """Register a candidate set, select one, cancel the rest. One transaction.

    ``candidates`` is the FULL set Archaeon considered. ``selected_index`` names
    the one to run. Passing a single candidate is legal and simply registers a
    set of size one -- which is an honest statement that one candidate was
    considered, not a way of hiding that others were.

    Atomicity is the whole point: a set registered across several transactions
    could have been extended after seeing something, and "registered before
    selection" would become a claim rather than a property.
    """
    config = config or cfg.DEFAULT
    if source_reason not in ("weak_signal", "exploration", "human"):
        raise ValueError("source_reason must be weak_signal|exploration|human")
    if not candidates:
        raise ValueError("candidate set is empty")
    if not (0 <= selected_index < len(candidates)):
        raise IndexError("selected_index outside the candidate set")

    for c in candidates:
        assert_spec_is_execution_only(c["spec"])
        assert_no_negative_authority({"spec": c["spec"],
                                      "source_evidence": c["source_evidence"]})

    autonomous = source_reason in AUTONOMOUS_REASONS
    lane = config.cadence.lane
    csid = candidate_set_id or ("cs-" + uuid.uuid4().hex[:16])

    assert_queue_ready(conn)

    cur = conn.cursor()
    try:
        if autonomous:
            cad.take_gate(cur, lane)
            decision = _evaluate_cadence(cur, config.cadence)
            if not decision.admitted:
                cad.log_decision(cur, decision, None, lane)
                conn.commit()      # the REFUSAL is durable; no row is written
                raise cad.CadenceRefused(decision)
            ordinal = decision.day_ordinal
        else:
            decision = cad.CadenceDecision(
                True, "ADMITTED", None,
                {"note": "human row; autonomous quota does not apply",
                 "created_by": created_by, "queue": str(QUEUE)})
            ordinal = None

        ids: List[str] = []
        for i, c in enumerate(candidates):
            ids.append(_insert(
                cur, c, created_by=created_by, source_reason=source_reason,
                candidate_set_id=csid, lane=lane if i == selected_index else None,
                ordinal=ordinal if i == selected_index else None))

        # Cancel the unchosen. NOT deleted: a cancelled row is the only
        # class-A trace of a selection decision anywhere in the architecture.
        for i, eid in enumerate(ids):
            if i == selected_index:
                continue
            cur.execute("UPDATE {q} SET status='cancelled' "
                        "WHERE experiment_id = %s".format(q=QUEUE), (eid,))

        cad.log_decision(cur, decision, None, lane)
        conn.commit()
        return {"candidate_set_id": csid,
                "registered": len(ids),
                "selected_experiment_id": ids[selected_index],
                "cancelled_experiment_ids": [e for i, e in enumerate(ids)
                                             if i != selected_index],
                "decision": decision.to_json()}
    except cad.CadenceRefused:
        raise
    except Exception:
        conn.rollback()
        raise


def candidate_set(conn, candidate_set_id: str) -> Optional[Dict[str, Any]]:
    """The DERIVED view of a candidate set. Never an attested count."""
    cur = conn.cursor()
    cur.execute("SELECT candidate_set_id, registered, cancelled, retained, "
                "       registered_at, last_registered_at, registrars "
                "  FROM " + _schema() + ".candidate_sets WHERE candidate_set_id = %s",
                (candidate_set_id,))
    r = cur.fetchone()
    if not r:
        return None
    span = (r[5] - r[4]).total_seconds() if r[4] and r[5] else 0.0
    return {"candidate_set_id": r[0], "registered": int(r[1]),
            "cancelled": int(r[2]), "retained": int(r[3]),
            "registered_at": str(r[4]), "last_registered_at": str(r[5]),
            "registrars": int(r[6]),
            "registration_span_seconds": span,
            "count_source": "DERIVED from the register, not attested"}
