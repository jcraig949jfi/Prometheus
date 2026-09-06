"""Writing a proposal into the PostgreSQL experiment queue.

One public entry point, ``enqueue``, and it does the whole transaction:

    BEGIN -> take gate -> evaluate cadence -> negative-authority check
          -> INSERT -> log decision -> COMMIT

Failure of any step rolls the whole thing back, so a refused proposal leaves no
queue row and an admitted one leaves both a queue row and a cadence-log entry.

The negative-authority check runs at the WRITE BOUNDARY on purpose. Guarding at
the point of generation would leave every future call site free to forget; a
record that fails the check cannot reach the queue no matter who built it.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Optional, Tuple

from . import cadence as cad
from . import config as cfg

_FORBIDDEN = tuple(re.compile(p, re.IGNORECASE)
                   for p in cfg.FORBIDDEN_CLAIM_PATTERNS)

# Fields whose values are quoted verbatim from elsewhere and are therefore not
# Archaeon speaking. Detector names ("REPEATED_OUTLIER_REGION") and the standing
# disclaimers in `authority` would otherwise trip the scan on their own words.
_EXEMPT_KEYS = frozenset({"authority", "reading", "detector",
                          "detector_version", "co_firing_detectors",
                          "primary_detector", "detectors",
                          "detectors_fired_names", "detectors_eligible_names"})


class NegativeAuthorityViolation(Exception):
    """A record tried to carry a scientific verdict. It is not written.

    Archaeon has no negative authority and no positive authority. This is the
    mechanical enforcement of that; see roles/Archaeon/CHARTER.md.
    """


def _walk_strings(obj: Any, path: str = "$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in _EXEMPT_KEYS:
                continue
            yield from _walk_strings(v, "{}.{}".format(path, k))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from _walk_strings(v, "{}[{}]".format(path, i))
    elif isinstance(obj, str):
        yield path, obj


def assert_no_negative_authority(record: Dict[str, Any]) -> None:
    """Reject a record that states a scientific conclusion.

    Raises NegativeAuthorityViolation naming the field and the pattern, so the
    failure is actionable rather than mysterious.
    """
    for path, text in _walk_strings(record):
        for rx in _FORBIDDEN:
            m = rx.search(text)
            if m:
                raise NegativeAuthorityViolation(
                    "forbidden claim at {}: matched /{}/ in {!r}. Archaeon may "
                    "not assert scientific conclusions; a detector firing means "
                    "only that a region may be worth interrogating again."
                    .format(path, rx.pattern, text[:200]))


def proposal_id(spec_hash: str, corpus_hash: str, mode: str) -> str:
    blob = "|".join([spec_hash, corpus_hash, mode]).encode("utf-8")
    return "AX-" + hashlib.sha256(blob).hexdigest()[:12]


class QueueRetired(Exception):
    """archaeon.experiment_queue is retired; there is one register now."""


def enqueue(conn, *, spec: Dict[str, Any], source_reason: str,
            source_evidence: Dict[str, Any],
            created_by: str = "archaeon",
            config: Optional[cfg.ArchaeonConfig] = None,
            ) -> Tuple[str, cad.CadenceDecision]:
    """RETIRED 2026-09-06. Refuses to write.

    Two live queues meant Archaeon's proposals went nowhere. The single
    canonical pre-execution register is now viv.research_experiment_queue;
    write to it with ``archaeon.vivqueue.submit``, which preserves cadence,
    declares the experimental relation in COLUMNS rather than in the sealed
    spec, and registers a candidate set atomically.

    This function is left in place, refusing, rather than deleted: a deleted
    function is a silent behaviour change for any caller that still imports it,
    and this raises with the replacement named.
    """
    raise QueueRetired(
        "archaeon.experiment_queue is retired and this writer refuses. Use "
        "archaeon.vivqueue.submit(conn, candidates=[...], selected_index=..., "
        "source_reason=...) which writes to viv.research_experiment_queue, "
        "the single canonical pre-execution register.")


def _enqueue_retired_body(conn, *, spec, source_reason, source_evidence,
                          created_by="archaeon", config=None):
    """The original body, kept for reference only. Never called."""
    config = config or cfg.DEFAULT
    if source_reason not in ("weak_signal", "exploration", "human"):
        raise ValueError("source_reason must be weak_signal|exploration|human")

    # The guard runs over the WHOLE record, spec included.
    assert_no_negative_authority({"spec": spec,
                                  "source_evidence": source_evidence})

    corpus_hash = (source_evidence.get("corpus") or {}).get("hash")
    cfg_fp = (source_evidence.get("rules") or {}).get("config_fingerprint")
    seed = source_evidence.get("seed")
    spec_hash = spec.get("spec_hash") or ""
    # The lane is part of the identity: the same spec proposed in a test lane
    # and in production are different proposals, and must not collide on the
    # primary key.
    pid = proposal_id(spec_hash, corpus_hash or "",
                      "{}|{}".format(source_reason, config.cadence.lane))

    # Autonomy is a property of WHY the row exists, not of who wrote it. This
    # matches the database constraint exactly (migration 002).
    autonomous = source_reason in cad.AUTONOMOUS_REASONS
    lane = config.cadence.lane

    cur = conn.cursor()
    try:
        if autonomous:
            cad.take_gate(cur, lane)
            decision = cad.evaluate(cur, config.cadence)
            if not decision.admitted:
                cad.log_decision(cur, decision, None, lane)
                conn.commit()          # the REFUSAL is durable; the row is not
                raise cad.CadenceRefused(decision)
            ordinal = decision.day_ordinal
        else:
            decision = cad.CadenceDecision(
                True, "ADMITTED", None,
                {"note": "human-created row; autonomous quota does not apply",
                 "created_by": created_by})
            ordinal = None

        try:
            cur.execute(
                """
                INSERT INTO archaeon.experiment_queue
                    (proposal_id, lane, day_ordinal, created_by, source_reason,
                     spec, spec_hash, source_evidence, corpus_hash,
                     config_fingerprint, seed)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s)
                """,
                (pid, lane, ordinal, created_by, source_reason,
                 json.dumps(spec, default=str), spec_hash,
                 json.dumps(source_evidence, default=str),
                 corpus_hash, cfg_fp, seed))
        except Exception as exc:
            # Losing the (utc_day, day_ordinal) unique index to a concurrent
            # instance is the cap WORKING. Report it as a refusal, not a crash.
            conn.rollback()
            if autonomous and _is_ordinal_conflict(exc):
                lost = cad.CadenceDecision(
                    False, "REFUSED_RACE_LOST", ordinal,
                    {"note": ("another Archaeon instance took day_ordinal {} "
                              "first; the database cap held".format(ordinal)),
                     "instance": cad.instance_id(),
                     "error": str(exc)[:400]})
                cur2 = conn.cursor()
                cad.log_decision(cur2, lost, None, lane)
                conn.commit()
                raise cad.CadenceRefused(lost)
            raise

        cad.log_decision(cur, decision, pid, lane)
        conn.commit()
        return pid, decision
    except cad.CadenceRefused:
        raise
    except Exception:
        conn.rollback()
        raise


def _is_ordinal_conflict(exc: Exception) -> bool:
    txt = str(exc).lower()
    return ("uq_archaeon_day_ordinal" in txt
            or ("duplicate key" in txt and "day_ordinal" in txt))


def apply_migrations(conn, migrations_dir=None) -> list:
    """Apply archaeon/migrations/*.sql in order. Idempotent."""
    from pathlib import Path
    d = Path(migrations_dir or (Path(__file__).resolve().parent / "migrations"))
    applied = []
    cur = conn.cursor()
    for path in sorted(d.glob("*.sql")):
        cur.execute(path.read_text(encoding="utf-8"))
        applied.append(path.name)
    conn.commit()
    return applied
