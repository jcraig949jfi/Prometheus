"""Per-world, append-only, hash-chained event ledger.

Every state change in a world is accompanied by an event, appended in the SAME
transaction as the change (cross-store atomicity: evidence and state commit
together, or neither does). Events chain by `prev_hash` within a world's
sequence, so the world's history is independently verifiable and tamper-evident.

Forking shares the parent's immutable prefix BY REFERENCE: a child world is
created with its `next_index` and `head_hash` seeded from the parent's fork
point, so the child's first event chains onto the parent's fork-point
`entry_hash` without copying a single parent row. Parent rows are never written
by the child and child rows never touch the parent -- so parent and child cannot
mutate one another, structurally.

The chain hash covers content and ordering fields but NOT the random event_id or
the global autoincrement seq (those are identity/order, recomputed-independent),
so `verify` recomputes each entry from its stored fields and rejects any edit.
"""

from __future__ import annotations

from typing import Any, Optional

from sfe.errors import LedgerIntegrityError
from sfe.ids import canonical_bytes, content_hash, new_id
from sfe.store import now

SCHEMA_VER = 1

# Canonical Gen-2 event vocabulary (section 6). Not enforced as a DB CHECK so a
# domain extension can add a type without a migration, but the core set is named
# here so tests and the API share one source of truth.
EVENT_TYPES = frozenset({
    "WORLD_CREATED", "WORLD_STARTED", "WORLD_PAUSED", "WORLD_RESUMED",
    "WORLD_TERMINATED", "WORLD_FORKED", "CHECKPOINT_CREATED",
    "HYPOTHESIS_PROPOSED", "PREDICTION_REGISTERED", "EXPERIMENT_CREATED",
    "EXPERIMENT_COMMITTED",
    "WORK_ENQUEUED", "WORK_CLAIMED", "WORK_STARTED", "WORK_HEARTBEAT",
    "WORK_COMPLETED", "WORK_FAILED", "WORK_EXPIRED", "WORK_CANCELLED",
    "OBSERVATION_RECORDED", "FAILURE_RECORDED", "CLAIM_FALSIFIED",
    "CLAIM_SURVIVED", "ARTIFACT_CREATED", "ARTIFACT_IMPORTED",
    "FAILURE_CONSUMED", "MUTATION_PROPOSED", "LINEAGE_EDGE_ADDED",
    "BUDGET_CONSUMED", "BUDGET_EXHAUSTED", "MEASUREMENT_REGISTERED",
    "ERRATUM_RECORDED",
})


def _entry_hash(world_id: str, world_index: int, event_type: str, ts: float,
                actor: str, payload: Any, refs: Any, causal: Any,
                artifacts: Any, prev_hash: str) -> str:
    return content_hash({
        "world_id": world_id, "world_index": world_index,
        "event_type": event_type, "ts": ts, "actor": actor,
        "payload": payload, "refs": refs, "causal": causal,
        "artifacts": artifacts, "prev_hash": prev_hash, "schema_ver": SCHEMA_VER})


def append(cx, world_id: str, event_type: str, *, actor: str,
           payload: Optional[dict] = None, refs: Optional[dict] = None,
           causal: Optional[list] = None, artifacts: Optional[list] = None,
           ts: Optional[float] = None) -> dict:
    """Append one event to a world's chain, inside the caller's transaction.

    Reads the world's current head under the same write lock the caller holds
    (BEGIN IMMEDIATE), so concurrent appends cannot interleave and duplicate an
    index -- and the UNIQUE(world_id, world_index) constraint is the backstop.
    """
    row = cx.execute(
        "SELECT next_index, head_hash FROM worlds WHERE world_id=?",
        (world_id,)).fetchone()
    if row is None:
        raise LedgerIntegrityError("append to unknown world", world_id=world_id)
    idx = int(row["next_index"])
    prev = row["head_hash"] or ""
    payload = payload or {}
    refs = refs or {}
    causal = causal or []
    artifacts = artifacts or []
    ts = now() if ts is None else ts
    eh = _entry_hash(world_id, idx, event_type, ts, actor, payload, refs,
                     causal, artifacts, prev)
    eid = new_id("event")
    cx.execute(
        "INSERT INTO events(event_id, world_id, world_index, event_type, ts, "
        "actor, payload, refs, causal, artifacts, prev_hash, entry_hash, "
        "schema_ver) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (eid, world_id, idx, event_type, ts, actor,
         canonical_bytes(payload).decode(), canonical_bytes(refs).decode(),
         canonical_bytes(causal).decode(), canonical_bytes(artifacts).decode(),
         prev, eh, SCHEMA_VER))
    seq = cx.execute("SELECT last_insert_rowid() AS s").fetchone()["s"]
    cx.execute("UPDATE worlds SET next_index=?, head_hash=? WHERE world_id=?",
               (idx + 1, eh, world_id))
    return {"event_seq": int(seq), "event_id": eid, "world_id": world_id,
            "world_index": idx, "entry_hash": eh, "event_type": event_type}


def _row_to_event(r) -> dict:
    import json
    return {"event_seq": r["event_seq"], "event_id": r["event_id"],
            "world_id": r["world_id"], "world_index": r["world_index"],
            "event_type": r["event_type"], "ts": r["ts"], "actor": r["actor"],
            "payload": json.loads(r["payload"]), "refs": json.loads(r["refs"]),
            "causal": json.loads(r["causal"]),
            "artifacts": json.loads(r["artifacts"]),
            "prev_hash": r["prev_hash"], "entry_hash": r["entry_hash"]}


def _own_events(cx, world_id: str, upto_index: Optional[int] = None) -> list:
    q = ("SELECT * FROM events WHERE world_id=? "
         + ("AND world_index<=? " if upto_index is not None else "")
         + "ORDER BY world_index ASC")
    args = (world_id, upto_index) if upto_index is not None else (world_id,)
    return [_row_to_event(r) for r in cx.execute(q, args).fetchall()]


def world_history(cx, world_id: str) -> list:
    """The full logical history of a world: its fork-inherited prefix (walked
    recursively from ancestors, each truncated at its fork point) followed by
    the world's own events. The inherited prefix is READ from ancestor rows and
    never copied, so it is the same immutable evidence the ancestor sees."""
    w = cx.execute(
        "SELECT parent_world_id, fork_point FROM worlds WHERE world_id=?",
        (world_id,)).fetchone()
    if w is None:
        raise LedgerIntegrityError("history of unknown world", world_id=world_id)
    prefix: list = []
    if w["parent_world_id"] is not None:
        # ancestor history up to (and including) the fork point
        anc = _ancestor_prefix(cx, w["parent_world_id"], int(w["fork_point"]))
        prefix = anc
    return prefix + _own_events(cx, world_id)


def _ancestor_prefix(cx, world_id: str, upto_index: int) -> list:
    w = cx.execute(
        "SELECT parent_world_id, fork_point FROM worlds WHERE world_id=?",
        (world_id,)).fetchone()
    prefix: list = []
    if w["parent_world_id"] is not None:
        prefix = _ancestor_prefix(cx, w["parent_world_id"], int(w["fork_point"]))
    return prefix + _own_events(cx, world_id, upto_index=upto_index)


def verify_world(cx, world_id: str) -> dict:
    """Recompute the world's OWN chain from stored fields and confirm it links
    correctly to the fork point (for a child) or to the empty start (for a
    root). Returns {ok, checked, head_hash}; raises LedgerIntegrityError on the
    first inconsistency so tampering cannot pass silently."""
    w = cx.execute(
        "SELECT parent_world_id, fork_point, head_hash FROM worlds "
        "WHERE world_id=?", (world_id,)).fetchone()
    if w is None:
        raise LedgerIntegrityError("verify unknown world", world_id=world_id)
    if w["parent_world_id"] is None:
        expected_prev = ""
    else:
        anc = cx.execute(
            "SELECT entry_hash FROM events WHERE world_id=? AND world_index=?",
            (w["parent_world_id"], int(w["fork_point"]))).fetchone()
        if anc is None:
            raise LedgerIntegrityError(
                "fork point missing in parent", world_id=world_id)
        expected_prev = anc["entry_hash"]
    rows = _own_events(cx, world_id)
    checked = 0
    for e in rows:
        if e["prev_hash"] != expected_prev:
            raise LedgerIntegrityError(
                "broken chain link", world_id=world_id,
                world_index=e["world_index"], expected_prev=expected_prev,
                got_prev=e["prev_hash"])
        recomputed = _entry_hash(
            e["world_id"], e["world_index"], e["event_type"], e["ts"],
            e["actor"], e["payload"], e["refs"], e["causal"], e["artifacts"],
            e["prev_hash"])
        if recomputed != e["entry_hash"]:
            raise LedgerIntegrityError(
                "entry hash mismatch (tamper/corruption)", world_id=world_id,
                world_index=e["world_index"], stored=e["entry_hash"],
                recomputed=recomputed)
        expected_prev = e["entry_hash"]
        checked += 1
    stored_head = w["head_hash"] or ""
    if rows and stored_head != rows[-1]["entry_hash"]:
        raise LedgerIntegrityError("head hash disagrees with last event",
                                   world_id=world_id)
    return {"ok": True, "checked": checked, "head_hash": stored_head}


# -- foundry-level audit chain (client/session lifecycle) --------------------

def append_foundry(cx, event_type: str, *, actor: str, scope_kind: str,
                   scope_id: str, payload: Optional[dict] = None) -> dict:
    payload = payload or {}
    ts = now()
    last = cx.execute(
        "SELECT entry_hash FROM foundry_events ORDER BY seq DESC LIMIT 1"
    ).fetchone()
    prev = last["entry_hash"] if last else ""
    eh = content_hash({"event_type": event_type, "ts": ts, "actor": actor,
                       "scope_kind": scope_kind, "scope_id": scope_id,
                       "payload": payload, "prev_hash": prev})
    eid = new_id("event")
    cx.execute(
        "INSERT INTO foundry_events(event_id, event_type, ts, actor, "
        "scope_kind, scope_id, payload, prev_hash, entry_hash) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (eid, event_type, ts, actor, scope_kind, scope_id,
         canonical_bytes(payload).decode(), prev, eh))
    return {"event_id": eid, "entry_hash": eh}
