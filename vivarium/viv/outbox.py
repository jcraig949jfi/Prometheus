"""The PEW outbox: producer side (point release; PEW_OUTBOX_DESIGN.md).

Rows are written in the SAME transaction that closes an attempt; a separate
one-shot (viv/deliver.py) drains them. The consumer's tick path never opens
a PEW connection once the outbox exists -- tests/test_outbox.py asserts the
tick path does not import the HTTP client.

Identity: event_id is CONTENT-derived (a replayed step that re-enqueues the
same fact gets the same id -> a duplicate is a no-op at PEW); sequence is
DENSE per (producer, stream), assigned by the 009 trigger under an advisory
lock -> a missing number is a GAP nobody heals. Two invariants, two fields
(Stage 3 answer to Mnemosyne, #335).

FEATURE-DETECTED like viv/attempts.py: without the pew_outbox table (before
the window) `enabled()` is False and the loop keeps today's synchronous
write_encounter path.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from . import spec as _spec

#: Two streams, so the fossil path never waits behind provenance events
#: that PEW cannot ingest yet (Stage 3, Mnemosyne s7.D): each stream is
#: ordered on its own; a gap in one is invisible to the other.
STREAM_FOSSIL = "viv.fossil.v1"        # WORLD_ANCHORED, ENCOUNTER_RECORDED -> the existing PEW routes
STREAM_EXECUTION = "viv.execution.v1"  # attempts, steps, gates, interventions, terminations -> the ingest route
STREAM = STREAM_EXECUTION


def stream_for(kind: str) -> str:
    return STREAM_FOSSIL if kind in ("WORLD_ANCHORED", "ENCOUNTER_RECORDED") else STREAM_EXECUTION
KINDS = ("WORLD_ANCHORED", "ENCOUNTER_RECORDED", "ATTEMPT_OPENED", "STEP_COMPLETED",
         "INTERVENTION_RECEIPTED", "GATE_EVALUATED", "ATTEMPT_TERMINATED", "ATTEMPT_REPLAYED")


def payload_digest(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(_spec.canonical_bytes(payload)).hexdigest()


def event_id(producer: str, stream: str, source_attempt: str, source_step: Optional[str],
             kind: str, pdigest: str) -> str:
    basis = "|".join([producer, stream, source_attempt, source_step or "", kind, pdigest])
    return "sha256:" + hashlib.sha256(basis.encode("utf-8")).hexdigest()


class Outbox:
    def __init__(self, *, schema: str, producer: str, log=print):
        self.schema = schema
        self.producer = producer
        self.log = log
        self._enabled: Optional[bool] = None

    def enabled(self, conn) -> bool:
        if self._enabled is None:
            with conn.cursor() as cur:
                cur.execute("SELECT to_regclass(%s)", (self.schema + ".pew_outbox",))
                self._enabled = cur.fetchone()[0] is not None
            conn.rollback()
        return self._enabled

    def enqueue(self, conn, *, kind: str, source_attempt: str, source_experiment: str,
                payload: dict, source_step: Optional[str] = None, commit: bool = True) -> Optional[str]:
        """Insert one event. Idempotent on event_id: re-enqueuing the same fact
        (same attempt, step, kind, payload) is a no-op that returns the id."""
        if kind not in KINDS:
            raise ValueError("outbox event kind %r is not in the closed set" % (kind,))
        if not self.enabled(conn):
            return None
        pd = payload_digest(payload)
        stream = stream_for(kind)
        eid = event_id(self.producer, stream, source_attempt, source_step, kind, pd)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO " + self.schema + ".pew_outbox (event_id, producer, stream, sequence, event_kind, "
                        "source_attempt, source_step, source_experiment, payload, payload_digest) "
                        "VALUES (%s, %s, %s, 0, %s, %s, %s, %s, %s, %s) ON CONFLICT (event_id) DO NOTHING",
                        (eid, self.producer, stream, kind, source_attempt, source_step, source_experiment,
                         json.dumps(payload, default=str), pd))
        if commit:
            conn.commit()
        return eid

    def stats(self, conn) -> Dict[str, Any]:
        if not self.enabled(conn):
            return {"enabled": False}
        with conn.cursor() as cur:
            cur.execute("SELECT state, count(*) FROM " + self.schema + ".pew_outbox GROUP BY state")
            by_state = {k: v for k, v in cur.fetchall()}
            cur.execute("SELECT producer, stream, max(sequence), count(*) FILTER (WHERE state = 'PENDING') FROM "
                        + self.schema + ".pew_outbox GROUP BY producer, stream")
            streams = [{"producer": p, "stream": s, "max_sequence": m, "pending": n} for p, s, m, n in cur.fetchall()]
        conn.rollback()
        return {"enabled": True, "by_state": by_state, "streams": streams,
                "pending": by_state.get("PENDING", 0)}

    def pending(self, conn, *, limit: int = 200) -> List[dict]:
        """PENDING rows in stream order, locked for this deliverer."""
        from . import db as _db
        with _db.dict_cur(conn) as cur:
            cur.execute("SELECT event_id, producer, stream, sequence, event_kind, source_attempt, source_step, "
                        "source_experiment, payload, payload_digest, attempts FROM " + self.schema +
                        ".pew_outbox WHERE state = 'PENDING' ORDER BY producer, stream, sequence "
                        "FOR UPDATE SKIP LOCKED LIMIT %s", (limit,))
            return [dict(r) for r in cur.fetchall()]

    def mark(self, conn, event_id_: str, *, state: str, http: Optional[int] = None,
             error: Optional[str] = None, pew_reference: Optional[str] = None) -> None:
        with conn.cursor() as cur:
            cur.execute("UPDATE " + self.schema + ".pew_outbox SET state = %s, attempts = attempts + 1, "
                        "last_attempt_at = now(), last_http = %s, last_error = %s, "
                        "delivered_at = CASE WHEN %s = 'DELIVERED' THEN now() ELSE delivered_at END, "
                        "pew_reference = COALESCE(%s, pew_reference) WHERE event_id = %s",
                        (state, http, (error or "")[:2000] or None, state, pew_reference, event_id_))
