"""PEW closure V0 (Mnemosyne, 2026-09-04).

Pure helpers behind the closure routes in service.py:
  * server-ATTESTED identity (which PEW instance, which store), independent of
    the bearer token and the self-declared machine header;
  * source-packet read-back (closes I-NO-PACKET-READ);
  * the constraint-transfer + errata/supersession store.

Nothing here trusts a client's claim about which host it reached: db_system_id
comes from the Postgres cluster the service is actually connected to.
"""
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

from . import FOSSIL_CONTRACT_VERSION, ONTOLOGY_VERSION, SCHEMA_VERSION
from . import db as ewdb

_ROOT = Path(__file__).resolve().parent.parent   # evidence_wiki/
_ATTEST = None
_SRC = None

CONSTRAINT_KINDS = {"HARD", "ADVISORY"}
CONSTRAINT_STATUS = {"PROPOSED", "SUPPORTED", "NARROWED", "SUPERSEDED", "REFUTED"}


def source_commit():
    """(commit, dirty) of the running service's tree, cached. 'dirty' is
    load-bearing: IMPLEMENTED != DEPLOYED -- a service running on a dirty tree
    is not any committed version, and a fossil should be able to say so."""
    global _SRC
    if _SRC is not None:
        return _SRC
    commit = os.environ.get("EW_SOURCE_COMMIT") or ""
    dirty = None
    try:
        if not commit:
            commit = subprocess.run(
                ["git", "-C", str(_ROOT), "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=5).stdout.strip()
        st = subprocess.run(
            ["git", "-C", str(_ROOT), "status", "--porcelain"],
            capture_output=True, text=True, timeout=5).stdout
        dirty = bool(st.strip())
    except Exception:
        pass
    _SRC = (commit or "unknown", dirty)
    return _SRC


def service_attestation(conn):
    """Server-attested identity of THIS PEW instance and the store it is
    connected to. db_system_id is the Postgres cluster's system_identifier --
    non-spoofable proof of WHICH database persisted a row, independent of the
    bearer token (every host shares it) and the self-declared machine header.
    Cached per process (identity is fixed for a running service on one DB)."""
    global _ATTEST
    if _ATTEST is not None:
        return _ATTEST
    cfg = ewdb.load_config()
    sysid, dbname = None, cfg.get("db_name")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT system_identifier::text, current_database() "
                        "FROM pg_control_system()")
            sysid, dbname = cur.fetchone()
    except Exception:
        pass
    commit, dirty = source_commit()
    _ATTEST = {
        "service_name": cfg.get("service_name"),
        "db_system_id": sysid,
        "db_name": dbname,
        "db_host": cfg.get("db_host"),
        "source_commit": commit,
        "source_dirty": dirty,
        "schema_version": SCHEMA_VERSION,
        "ontology_version": ONTOLOGY_VERSION,
        "fossil_contract": FOSSIL_CONTRACT_VERSION,
        "closure_version": "pew.closure.v0",   # migration 008 (additive; does not change the v4 contract)
    }
    return _ATTEST


def fossil_attestation_json(conn):
    """The block stamped onto each fossil row (as a JSON string). sfe_anchor_
    verified is FALSE by construction: PEW validates anchor class/shape, never
    SFE ledger membership (no SFE client by design), so a fossil records that
    its causal anchor is client-asserted, not PEW-verified."""
    a = dict(service_attestation(conn))
    a["sfe_anchor_verified"] = False
    return json.dumps(a)


def get_packet(conn, packet_id):
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.source_packets WHERE packet_id=%s",
                    (packet_id,))
        return cur.fetchone()


def _mint(prefix, *parts):
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]
    return f"{prefix}-{h}"


def _insert_event(cur, cid, frm, to, adj_ev, adj_pkt, succ, repro, rationale,
                  attest_json, ident):
    rev = ewdb.next_revision(cur)
    eid = _mint("KE", cid, to, adj_ev or "", repro or "", time.time())
    cur.execute(
        "INSERT INTO ew.constraint_events(event_id, constraint_id, from_status, "
        "to_status, adjudicating_evidence_id, adjudicating_packet_id, "
        "successor_constraint_id, reproducer, rationale, attestation, "
        "created_by, machine, revision) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (eid, cid, frm, to, adj_ev, adj_pkt, succ, repro, rationale,
         attest_json, ident["agent"], ident["machine"], rev))
    return eid


def create_constraint(conn, body, ident):
    attest = fossil_attestation_json(conn)   # same server block; harmless extra key
    cid = _mint("K", body.kind, body.title or "", body.statement or "",
                json.dumps(body.scope, sort_keys=True), time.time())
    status = body.status or "PROPOSED"
    with conn.cursor() as cur:
        rev = ewdb.next_revision(cur)
        cur.execute(
            "INSERT INTO ew.constraints(constraint_id, kind, title, statement, "
            "native_payload, scope, severity, applicability, source_evidence_ids, "
            "source_claim_id, packet_id, reproducer, origin_ref, supersedes, "
            "attestation, namespace, created_by, machine, revision) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (cid, body.kind, body.title, body.statement,
             json.dumps(body.native_payload) if body.native_payload else None,
             json.dumps(body.scope), body.severity,
             json.dumps(body.applicability) if body.applicability else None,
             body.source_evidence_ids, body.source_claim_id, body.packet_id,
             body.reproducer, body.origin_ref, body.supersedes, attest,
             body.namespace, ident["agent"], ident["machine"], rev))
        _insert_event(cur, cid, None, status, None, None, None,
                      body.reproducer, "initial", attest, ident)
    conn.commit()
    return cid, status


def append_event(conn, cid, body, ident):
    """Returns (event_id, from_status) or None if the constraint is unknown.
    Uses a plain (tuple) cursor: next_revision() does fetchone()[0], which a
    RealDictCursor would break."""
    attest = fossil_attestation_json(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM ew.constraints WHERE constraint_id=%s", (cid,))
        if cur.fetchone() is None:
            return None
        cur.execute("SELECT to_status FROM ew.constraint_events WHERE "
                    "constraint_id=%s ORDER BY seq DESC LIMIT 1", (cid,))
        row = cur.fetchone()
        frm = row[0] if row else None
        eid = _insert_event(cur, cid, frm, body.to_status,
                            body.adjudicating_evidence_id,
                            body.adjudicating_packet_id,
                            body.successor_constraint_id, body.reproducer,
                            body.rationale, attest, ident)
    conn.commit()
    return eid, frm


def get_constraint(conn, cid):
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.constraints_current WHERE constraint_id=%s",
                    (cid,))
        c = cur.fetchone()
        if not c:
            return None
        cur.execute("SELECT * FROM ew.constraint_events WHERE constraint_id=%s "
                    "ORDER BY seq", (cid,))
        c["events"] = cur.fetchall()
        return c


# ---- R2-1 PEW side: immutable content-addressed audit/replay envelope --------
# The documented slots. PEW does not invent them; a producer supplies the ones
# it has (content-addressed / immutable identities), and PEW seals the whole set.
SEAL_SLOTS = (
    "experiment_spec_id", "organism_ids", "interpretation_id",
    "registry_id", "entry_id", "composition_id", "topology", "ablation",
    "action_id", "input_digest", "world_id", "world_config_digest",
    "measurement_def", "measurement_version", "output_digest",
    "sfe_engine_id", "causal_anchor",
)


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def seal_record(conn, encounter_id, run_id, envelope, namespace, ident):
    """Content-address {encounter_id, run_id, envelope} and store it immutably.
    Returns:
      None                     -> the encounter does not exist
      ("__anchor__", stored)   -> the envelope's causal_anchor conflicts with the fossil
      (envelope_id, csha, inserted)
    Idempotent on identical content (ON CONFLICT DO NOTHING); a changed slot is a
    different envelope_id (tamper-evident). PEW stores the producer slots verbatim."""
    canonical = _canon({"encounter_id": encounter_id, "run_id": run_id or "",
                        "envelope": envelope})
    csha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    eid = "SEAL-" + csha[:24]
    attest = fossil_attestation_json(conn)
    # plain (tuple) cursor: next_revision() does fetchone()[0], which a
    # RealDictCursor would break.
    with conn.cursor() as cur:
        cur.execute("SELECT sfe_entry_hash FROM ew.fossil_encounters WHERE "
                    "encounter_id=%s AND run_key=%s", (encounter_id, run_id or ""))
        f = cur.fetchone()
        if f is None:
            return None
        fossil_anchor = f[0]
        # integrity: a seal must not claim a different anchor than the fossil it
        # seals (machine-checkable, not invented semantics).
        anchor = envelope.get("causal_anchor") if isinstance(envelope, dict) else None
        if isinstance(anchor, dict) and anchor.get("sfe_entry_hash") and \
           anchor["sfe_entry_hash"] != fossil_anchor:
            return ("__anchor__", fossil_anchor)
        cur.execute("SELECT 1 FROM ew.sealed_records WHERE envelope_id=%s", (eid,))
        inserted = cur.fetchone() is None
        if inserted:
            rev = ewdb.next_revision(cur)
            cur.execute(
                "INSERT INTO ew.sealed_records(envelope_id, content_sha256, "
                "content_canonical, encounter_id, encounter_run_id, envelope, "
                "attestation, namespace, created_by, machine, revision) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (envelope_id) DO NOTHING",
                (eid, csha, canonical, encounter_id, run_id, json.dumps(envelope),
                 attest, namespace, ident["agent"], ident["machine"], rev))
    conn.commit()
    return (eid, csha, inserted)


def get_seal(conn, envelope_id):
    """The sealed record + a tamper check + the bound fossil, so the record is
    self-contained and recoverable from PEW alone (no SFE client credential)."""
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.sealed_records WHERE envelope_id=%s",
                    (envelope_id,))
        r = cur.fetchone()
        if not r:
            return None
        recomputed = hashlib.sha256(r["content_canonical"].encode("utf-8")).hexdigest()
        r["seal_valid"] = (recomputed == r["content_sha256"]
                           and envelope_id == "SEAL-" + recomputed[:24])
        cur.execute("SELECT * FROM ew.fossil_encounters WHERE encounter_id=%s "
                    "AND run_key=%s", (r["encounter_id"], r["encounter_run_id"] or ""))
        r["fossil"] = cur.fetchone()
        r["slots_present"] = sorted(k for k in (r["envelope"] or {}) if k in SEAL_SLOTS)
        r["slots_absent"] = sorted(k for k in SEAL_SLOTS if k not in (r["envelope"] or {}))
        return r


def list_seals_for_encounter(conn, encounter_id, run_id=None):
    q = ("SELECT envelope_id, content_sha256, encounter_id, encounter_run_id, "
         "namespace, created_at FROM ew.sealed_records WHERE encounter_id=%s")
    args = [encounter_id]
    if run_id is not None:
        q += " AND encounter_run_key=%s"; args.append(run_id or "")
    q += " ORDER BY created_at"
    with ewdb.dict_cur(conn) as cur:
        cur.execute(q, args)
        return cur.fetchall()


def list_constraints(conn, kind=None, status=None, scope_key=None,
                     scope_val=None, namespace="prod", limit=200):
    q = "SELECT * FROM ew.constraints_current WHERE namespace=%s"
    args = [namespace]
    if kind:
        q += " AND kind=%s"; args.append(kind)
    if status:
        q += " AND current_status=%s"; args.append(status)
    if scope_key and scope_val is not None:
        q += " AND scope->>%s = %s"; args += [scope_key, scope_val]
    q += " ORDER BY created_at DESC LIMIT %s"; args.append(limit)
    with ewdb.dict_cur(conn) as cur:
        cur.execute(q, args)
        return cur.fetchall()
