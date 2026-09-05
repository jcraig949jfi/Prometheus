"""Cadence enforcement: at most SIX autonomous proposals per UTC day, at least
FOUR HOURS apart, unevadeable by concurrent instances.

The enforcement lives in PostgreSQL. This module is the client of it, and it is
written so that *its own correctness is not required*: if everything here were
wrong, the partial unique index on ``(lane, utc_day, day_ordinal)`` would still
cap the day at six.

The transaction shape, in order, is the whole design:

    BEGIN
      SELECT ... FROM archaeon.cadence_gate WHERE gate_id='lane:<lane>' FOR UPDATE
          -- serializes every concurrent Archaeon enqueue in this lane
      SELECT count(*), max(created_at), now()          -- DATABASE clock
        FROM archaeon.experiment_queue
       WHERE lane = <lane>
         AND source_reason IN ('weak_signal','exploration')
         AND utc_day = (now() AT TIME ZONE 'UTC')::date
      -- refuse on daily cap, or on min separation
      INSERT ... day_ordinal = <count>                  -- unique index backstop
    COMMIT

Four deliberate choices:

* **The database clock, never the process clock.** ``now()`` is read inside the
  transaction and used for every comparison. Two machines have two system
  clocks and one database; only the database clock can order them.

* **The gate is taken BEFORE the count.** Taken after, two instances would both
  read a stale count and both believe they were within the cap; the unique
  index would then reject one of them as a crash rather than a refusal.

* **A lost race is logged as REFUSED_RACE_LOST, not as an error.** Losing the
  ordinal is the mechanism working. It is recorded so the cadence log tells the
  truth about how many instances were trying.

* **Autonomy is keyed on source_reason, not on a created_by NAME.** A second
  Archaeon running under a different handle -- a hostname, a service account --
  must consume the SAME quota, or the cap is evaded by renaming. Migration 001
  keyed it on the literal string 'archaeon' and had exactly that hole.

Idle Vivarium is NOT a reason to relax anything: nothing in this module reads
queue depth or runner state. The four-hour boundary is about the four-hour
boundary.
"""
from __future__ import annotations

import os
import socket
from dataclasses import dataclass
from typing import Any, Dict, Optional

from . import config as cfg

def gate_id(lane: str) -> str:
    return "lane:{}".format(lane)


AUTONOMOUS_REASONS = ("weak_signal", "exploration")


def instance_id() -> str:
    return "{}#{}".format(socket.gethostname(), os.getpid())


@dataclass(frozen=True)
class CadenceDecision:
    admitted: bool
    decision: str                 # ADMITTED | REFUSED_*
    day_ordinal: Optional[int]
    detail: Dict[str, Any]

    def to_json(self) -> Dict[str, Any]:
        return {"admitted": self.admitted, "decision": self.decision,
                "day_ordinal": self.day_ordinal, "detail": dict(self.detail)}


class CadenceRefused(Exception):
    """Raised when the cadence layer declines to admit a proposal.

    This is a SCHEDULING refusal and carries no scientific meaning whatsoever.
    It does not say the corpus was uninteresting, that a lineage is finished,
    or that experimentation should stop. It says: not yet.
    """

    def __init__(self, decision: CadenceDecision):
        self.decision = decision
        super().__init__("cadence refused: {} ({})".format(
            decision.decision, decision.detail))


def take_gate(cur, lane: str = "prod") -> None:
    """Serialize concurrent Archaeon enqueues in this lane. First in the txn.

    Creates the lane's gate row if it does not exist yet, then takes it FOR
    UPDATE. The insert is ON CONFLICT DO NOTHING so two instances racing to
    create the same lane both end up waiting on the one row.
    """
    gid = gate_id(lane)
    cur.execute("INSERT INTO archaeon.cadence_gate (gate_id, lane, note) "
                "VALUES (%s, %s, %s) ON CONFLICT (gate_id) DO NOTHING",
                (gid, lane, "Per-lane serializing gate."))
    cur.execute("SELECT gate_id FROM archaeon.cadence_gate "
                "WHERE gate_id = %s FOR UPDATE", (gid,))
    if cur.fetchone() is None:
        raise RuntimeError(
            "archaeon.cadence_gate row for lane {!r} could not be taken; "
            "migrations 001/002 may not be applied. Refusing to enqueue "
            "without the serializing lock -- proceeding would let concurrent "
            "instances race.".format(lane))


def evaluate(cur, ccfg: Optional[cfg.CadenceConfig] = None) -> CadenceDecision:
    """Decide whether an autonomous proposal may be written NOW.

    Assumes ``take_gate`` has already run in this transaction.
    """
    ccfg = ccfg or cfg.DEFAULT.cadence
    lane = ccfg.lane

    # Autonomy is keyed on source_reason, not on a created_by NAME: a second
    # instance running under a different handle must consume the same quota.
    cur.execute(
        """
        SELECT now() AS db_now,
               (now() AT TIME ZONE 'UTC')::date AS db_utc_day,
               count(*)          AS n_today,
               max(created_at)   AS last_at,
               EXTRACT(EPOCH FROM (now() - max(created_at))) AS since_last
          FROM archaeon.experiment_queue
         WHERE lane = %s
           AND source_reason = ANY(%s)
           AND utc_day = (now() AT TIME ZONE 'UTC')::date
        """, (lane, list(AUTONOMOUS_REASONS)))
    row = cur.fetchone()
    db_now, db_day, n_today, last_at, since_last = row[0], row[1], int(row[2]), row[3], row[4]

    # The separation check must span the UTC day boundary: a proposal at 23:30
    # and one at 00:10 are 40 minutes apart even though they fall on different
    # days and the day-scoped query above would not see the earlier one.
    cur.execute(
        """
        SELECT max(created_at),
               EXTRACT(EPOCH FROM (now() - max(created_at)))
          FROM archaeon.experiment_queue
         WHERE lane = %s AND source_reason = ANY(%s)
        """, (lane, list(AUTONOMOUS_REASONS)))
    grow = cur.fetchone()
    last_any, since_any = grow[0], grow[1]

    detail: Dict[str, Any] = {
        "lane": lane,
        "db_now": str(db_now),
        "db_utc_day": str(db_day),
        "autonomous_today": n_today,
        "max_per_utc_day": ccfg.max_per_utc_day,
        "last_autonomous_at": str(last_at) if last_at else None,
        "last_autonomous_at_any_day": str(last_any) if last_any else None,
        "seconds_since_last": float(since_any) if since_any is not None else None,
        "min_separation_seconds": ccfg.min_separation_seconds,
        "instance": instance_id(),
        "clock_source": "postgres now()",
    }

    if n_today >= ccfg.max_per_utc_day:
        detail["refusal"] = ("{} autonomous proposals already written for UTC "
                             "day {}".format(n_today, db_day))
        return CadenceDecision(False, "REFUSED_DAILY_CAP", None, detail)

    if since_any is not None and float(since_any) < ccfg.min_separation_seconds:
        detail["refusal"] = (
            "last autonomous proposal was {:.0f}s ago; {}s separation required"
            .format(float(since_any), ccfg.min_separation_seconds))
        detail["next_eligible_in_seconds"] = (
            ccfg.min_separation_seconds - float(since_any))
        return CadenceDecision(False, "REFUSED_MIN_SEPARATION", None, detail)

    # The ordinal a compliant proposal would take. The unique index decides
    # whether this instance actually gets it.
    return CadenceDecision(True, "ADMITTED", n_today, detail)


def log_decision(cur, decision: CadenceDecision,
                 proposal_id: Optional[str] = None,
                 lane: str = "prod") -> None:
    """Record the decision, including refusals."""
    import json
    cur.execute(
        "INSERT INTO archaeon.cadence_log "
        "(instance, decision, detail, proposal_id, lane) "
        "VALUES (%s, %s, %s::jsonb, %s, %s)",
        (instance_id(), decision.decision,
         json.dumps(decision.detail, default=str), proposal_id, lane))
