"""Typed reference / presence index and idempotent publication (H0-H5 iter 1).

Brief: roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md s4 C5.
Base:  docs/DESIGN_WP_X5_witness_and_lineage.md (accepted 2026-09-08).

PEW stores references, typed presence indexes, summaries and evidence links.
SFE is authoritative for bytes and observations. Nothing here holds scientific
content: a digest and a size are the whole record of it.
"""
import hashlib
import json
import re

from . import db as ewdb

# Extended by migration 012 for the corpus index. The vocabulary is closed:
# a new kind arrives with a migration, never by a producer inventing one.
REF_KINDS = ("WITNESS", "COMPONENT", "GENERATED_TASK", "DECODER",
             "SOURCE_SET", "RECEIPT",
             "EXPERIMENT", "OBSERVATION", "ENCOUNTER", "ARTIFACT")
WITNESS_SUBKINDS = ("PROGRAM_INPUT", "CA_INITIAL_STATE", "OTHER")
SOURCE_KINDS = ("OBSERVATION", "ARTIFACT", "EXPERIMENT",
                "ENCOUNTER", "EVENT")

# Five states, required. NULL cannot separate "there is none" from "I could not
# look", and X5-a requires that separation.
AVAILABILITY = ("PRESENT", "EMPTY", "TRUNCATED", "ABSENT", "UNAVAILABLE")

# Brief s4 C5: four different questions, four fields. A 1.0 implementation may
# carry a negative result; a passing test suite never promotes a connection.
SOFTWARE_STAGE = ("planned", "alpha", "beta", "1.0", "1.1")
CONNECTION_EVIDENCE = ("conceptual", "runnable", "demonstrated-transfer")
SCIENTIFIC_OUTCOME = ("not-run", "inconclusive", "supported-in-scope",
                      "meaningful-effect-not-supported", "harmful-in-scope")
REPRODUCTION_STATE = ("source-resolved", "built", "smoke-passed",
                      "benchmark-attempted", "reproduced-in-scope", "failed",
                      "blocked")

_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_EMPTY_SHA = "sha256:" + hashlib.sha256(b"").hexdigest()

# The identity of a reference: what it points at, not how reachable it is.
# availability is deliberately EXCLUDED so a reference keeps one identity as
# its reachability changes (see ew.ref_availability_events).
_IDENTITY = ("ref_kind", "ref_subkind", "encounter_id", "run_key",
             "source_kind", "source_id", "selector", "content_digest")

# Fields compared when deciding duplicate_identical vs conflict.
_COMPARED = _IDENTITY + ("sfe_world_id", "sfe_observation_id", "sfe_event_seq",
                         "sfe_entry_hash", "sfe_engine_instance_id",
                         "content_bytes", "source_scope", "visibility",
                         "origin", "namespace", "candidate_set_id",
                         "producer_experiment_id", "software_stage",
                         "connection_evidence", "scientific_outcome",
                         "reproduction_state")


def ref_id_for(d: dict) -> str:
    body = json.dumps({k: d.get(k) for k in _IDENTITY}, sort_keys=True,
                      default=str)
    return "R-" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]


def publication_id_for(intent: dict) -> str:
    body = json.dumps(intent, sort_keys=True, default=str)
    return ("P-" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:12],
            hashlib.sha256(body.encode("utf-8")).hexdigest())


def validate(d: dict):
    """Returns a rejection reason or None. Shape only -- PEW does not judge
    whether a witness is scientifically meaningful."""
    if d.get("ref_kind") not in REF_KINDS:
        return f"unknown_ref_kind: expected one of {REF_KINDS}"
    if d["ref_kind"] == "WITNESS" and d.get("ref_subkind") not in WITNESS_SUBKINDS:
        return (f"witness_requires_subkind: one of {WITNESS_SUBKINDS}; a witness "
                "whose kind is unstated cannot be selected for later")
    if d.get("source_kind") not in SOURCE_KINDS:
        return f"unknown_source_kind: expected one of {SOURCE_KINDS}"
    if not (d.get("source_id") or "").strip():
        return "source_id_required: a reference must name its authoritative source"
    if d.get("availability") not in AVAILABILITY:
        return (f"unknown_availability: expected one of {AVAILABILITY}. NULL is "
                "not a state: 'there is none' and 'I could not look' differ")
    dig = (d.get("content_digest") or "").strip()
    if not _DIGEST_RE.match(dig):
        return "content_digest_must_be_sha256_hex: expected sha256:<64 hex>"
    av = d["availability"]
    if av == "EMPTY" and dig != _EMPTY_SHA:
        return ("empty_witness_digest_mismatch: EMPTY means zero-length, whose "
                f"digest is {_EMPTY_SHA}; that is a fact, not a gap")
    if av == "TRUNCATED" and d.get("content_bytes") is None:
        return ("truncated_requires_content_bytes: a truncated reference must "
                "say how much was kept, or it cannot be told from a whole one")
    if av in ("TRUNCATED", "UNAVAILABLE") and not (d.get("availability_note") or "").strip():
        return f"{av.lower()}_requires_availability_note: say why"
    return None


def validate_axes(d: dict):
    """Brief s4 C5 axes. Each is optional; an asserted value must be in its own
    vocabulary, because the whole point is that they cannot be conflated."""
    for field, vocab in (("software_stage", SOFTWARE_STAGE),
                         ("connection_evidence", CONNECTION_EVIDENCE),
                         ("scientific_outcome", SCIENTIFIC_OUTCOME),
                         ("reproduction_state", REPRODUCTION_STATE)):
        v = d.get(field)
        if v is not None and v not in vocab:
            return f"unknown_{field}: expected one of {vocab}, got {v!r}"
    return None


def classify(existing, d):
    """inserted | duplicate_identical | conflict(list) -- the encounters' rule."""
    if existing is None:
        return "inserted", []
    diff = []
    for f in _COMPARED:
        new = d.get(f)
        if new is None:
            continue
        old = existing.get(f)
        if str(old) != str(new):
            diff.append(f"{f}(stored={old} submitted={new})")
    return ("duplicate_identical" if not diff else "conflict"), diff


def insert_ref(cur, d, ident):
    cur.execute("SELECT nextval('ew.canonical_revision_seq')")
    rev = cur.fetchone()["nextval"]
    cols = ["candidate_set_id", "producer_experiment_id", "software_stage",
            "connection_evidence", "scientific_outcome", "reproduction_state",
            "ref_id", "ref_kind", "ref_subkind", "encounter_id", "run_key",
            "sfe_world_id", "sfe_observation_id", "sfe_event_seq",
            "sfe_entry_hash", "sfe_engine_instance_id", "source_kind",
            "source_id", "selector", "content_digest", "content_bytes",
            "availability", "availability_note", "source_scope", "visibility",
            "origin", "producer", "namespace", "submitted_by", "machine",
            "revision"]
    vals = [d.get(c) for c in cols[:-3]]
    vals[cols.index("producer")] = (json.dumps(d["producer"])
                                    if d.get("producer") else None)
    vals += [ident.get("agent"), ident.get("machine"), rev]
    cur.execute(f"INSERT INTO ew.typed_refs({','.join(cols)}) VALUES "
                f"({','.join(['%s'] * len(cols))})", vals)
    cur.execute("INSERT INTO ew.ref_availability_events(ref_id, availability, "
                "note, observed_by) VALUES (%s,%s,%s,%s)",
                (d["ref_id"], d["availability"], d.get("availability_note"),
                 ident.get("agent")))
    return rev


def current_availability(cur, ref_id):
    """Derived from the append-only log: the latest event wins. The typed_refs
    row keeps the availability it was PUBLISHED with, which is a different
    fact and is not overwritten."""
    cur.execute("SELECT availability, note, observed_at FROM "
                "ew.ref_availability_events WHERE ref_id=%s "
                "ORDER BY event_id DESC LIMIT 1", (ref_id,))
    r = cur.fetchone()
    return dict(r) if r else None


def rebuild_presence_index(conn, namespace=None, candidate_set=None,
                           ref_kind="WITNESS"):
    """Deliverable 5: rebuild a derived presence index from the authoritative
    references ALONE -- no scientific bytes are read, and nothing in SFE is
    touched. Returns the index; the caller compares it to the previous one.

    'Which encounters carry a witness, and in what state' is a projection of
    ew.typed_refs plus the availability log. Rebuilding it is not an
    evidentiary act and must not alter execution identity."""
    # ref_kind=None rebuilds ACROSS kinds, which is what a corpus rebuild
    # needs: a candidate set is indexed as experiment/observation/encounter/
    # receipt references, and none of them is a witness.
    where, args = ["true"], []
    if ref_kind:
        where.append("ref_kind = %s")
        args.append(ref_kind)
    if namespace:
        where.append("namespace = %s")
        args.append(namespace)
    if candidate_set:
        where.append("candidate_set_id = %s")
        args.append(candidate_set)
    with ewdb.dict_cur(conn) as cur:
        cur.execute(
            "SELECT t.encounter_id, t.run_key, t.ref_kind, t.ref_subkind, t.ref_id, "
            "       t.content_digest, t.source_kind, t.source_id, "
            "       COALESCE(e.availability, t.availability) AS availability "
            "FROM ew.typed_refs t "
            "LEFT JOIN LATERAL ("
            "   SELECT availability FROM ew.ref_availability_events a "
            "   WHERE a.ref_id = t.ref_id ORDER BY a.event_id DESC LIMIT 1"
            ") e ON true "
            "WHERE " + " AND ".join(where) +
            " ORDER BY t.encounter_id, t.run_key, t.ref_id", args)
        rows = [dict(r) for r in cur.fetchall()]
    index = {}
    for r in rows:
        key = f"{r['encounter_id']}@{r['run_key']}"
        index.setdefault(key, []).append(
            {"ref_id": r["ref_id"], "kind": r["ref_kind"],
             "subkind": r["ref_subkind"],
             "availability": r["availability"], "digest": r["content_digest"],
             "source": f"{r['source_kind']}:{r['source_id']}"})
    return index


def index_digest(index) -> str:
    return hashlib.sha256(
        json.dumps(index, sort_keys=True).encode("utf-8")).hexdigest()
