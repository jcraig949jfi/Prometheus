"""Canonical evidence store — the ONLY module that writes ew.* tables.

Epistemic rules enforced here, not by convention:
  * append-only (no update/delete paths exist);
  * no provenance, no write;
  * derived views are quarantined from the evidence path;
  * agent submissions enter staged, never as adjudicated truth;
  * content-addressed IDs + idempotency keys make duplicates structurally
    impossible under retry/multi-writer conditions.
"""
import hashlib
import json
from pathlib import Path

from . import ONTOLOGY_VERSION, ids
from . import db as ewdb
from . import ontology

REPO = Path(__file__).resolve().parent.parent.parent


class RejectedWrite(Exception):
    """Write refused; .reason carries the machine-readable cause."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _vocab_check(cur, domain, term, allow_none=False):
    if term is None:
        if allow_none:
            return
        raise RejectedWrite(f"missing_{domain}")
    cur.execute("SELECT 1 FROM ew.vocab WHERE domain=%s AND term=%s AND NOT retired",
                (domain, term))
    if not cur.fetchone():
        raise RejectedWrite(f"unknown_{domain}:{term}")


def _idempotency_gate(cur, key, endpoint, machine, agent, payload):
    """Returns prior result id if this key already succeeded (replay)."""
    if not key:
        return None
    cur.execute("SELECT accepted, result_object_id FROM ew.write_log "
                "WHERE idempotency_key=%s", (key,))
    row = cur.fetchone()
    if row and row[0]:
        return row[1] or "__replayed__"
    return None


def _log_write(cur, key, endpoint, machine, agent, payload, accepted,
               reason=None, result_id=None):
    cur.execute(
        "INSERT INTO ew.write_log(idempotency_key, endpoint, machine, agent, "
        "payload_sha256, accepted, reject_reason, result_object_id) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (idempotency_key) DO NOTHING",
        (key, endpoint, machine, agent, ids.payload_sha256(payload),
         accepted, reason, result_id))


DERIVED_URI_MARKERS = ("evidence_wiki/derived", "/wiki/", "/api/v1/")


def register_packet(conn, uri, kind, registered_by, machine, git_commit=None,
                    idempotency_key=None):
    """Register an L0 source reference. Derived views are quarantined:
    they may be registered (kind='derived_view') for lineage, but evidence
    can never cite them (enforced in submit_evidence)."""
    payload = dict(uri=uri, kind=kind)
    with conn.cursor() as cur:
        prior = _idempotency_gate(cur, idempotency_key, "packet", machine,
                                  registered_by, payload)
        if prior:
            return prior
        _vocab_check(cur, "packet_kind", kind)
        if any(m in uri.replace("\\", "/") for m in DERIVED_URI_MARKERS) \
                and kind != "derived_view":
            _log_write(cur, idempotency_key, "packet", machine, registered_by,
                       payload, False, "derived_uri_must_be_derived_view_kind")
            conn.commit()
            raise RejectedWrite("derived_uri_must_be_derived_view_kind")
        sha = None
        p = REPO / uri
        if p.is_file():
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
        pid = ids.packet_id(uri, sha)
        rev = ewdb.next_revision(cur)
        cur.execute(
            "INSERT INTO ew.source_packets(packet_id, uri, content_sha256, "
            "git_commit, kind, registered_by, machine, revision) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (packet_id) DO NOTHING",
            (pid, uri, sha, git_commit, kind, registered_by, machine, rev))
        _log_write(cur, idempotency_key, "packet", machine, registered_by,
                   payload, True, result_id=pid)
    conn.commit()
    return pid


def submit_experiment(conn, agent, project, title, substrate, submitted_by,
                      machine, packet_id=None, git_commit=None, run_ref=None,
                      idempotency_key=None):
    payload = dict(agent=agent, project=project, title=title)
    with conn.cursor() as cur:
        prior = _idempotency_gate(cur, idempotency_key, "experiment", machine,
                                  submitted_by, payload)
        if prior:
            return prior
        xid = ids.experiment_id(agent, project, title)
        cur.execute("INSERT INTO ew.agents(agent_id) VALUES (%s) "
                    "ON CONFLICT DO NOTHING", (agent,))
        rev = ewdb.next_revision(cur)
        cur.execute(
            "INSERT INTO ew.experiments(experiment_id, agent_id, project, title, "
            "substrate, packet_id, git_commit, run_ref, submitted_by, machine, revision) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (experiment_id) DO NOTHING",
            (xid, agent, project, title, substrate, packet_id, git_commit,
             run_ref, submitted_by, machine, rev))
        _log_write(cur, idempotency_key, "experiment", machine, submitted_by,
                   payload, True, result_id=xid)
    conn.commit()
    return xid


def submit_claim(conn, text_canonical, status, creation_method, submitted_by,
                 machine, source_wording=None, claim_ceiling=None, agent=None,
                 experiment_id=None, packet_id=None, source_span=None,
                 write_stage="SUBMITTED", idempotency_key=None):
    payload = dict(text=text_canonical, status=status)
    with conn.cursor() as cur:
        prior = _idempotency_gate(cur, idempotency_key, "claim", machine,
                                  submitted_by, payload)
        if prior:
            return prior
        _vocab_check(cur, "claim_status", status)
        _vocab_check(cur, "creation_method", creation_method)
        _vocab_check(cur, "write_stage", write_stage)
        if packet_id is None and experiment_id is None:
            _log_write(cur, idempotency_key, "claim", machine, submitted_by,
                       payload, False, "claim_requires_packet_or_experiment")
            conn.commit()
            raise RejectedWrite("claim_requires_packet_or_experiment")
        # An agent submission cannot arrive pre-adjudicated as canonical:
        # adjudicated statuses require SOURCE_BOUND stage, which requires a packet.
        if status in ("ESTABLISHED", "SUPPORTED", "REFUTED", "RETRACTED") \
                and write_stage in ("SOURCE_BOUND", "INDEXED") and not packet_id:
            _log_write(cur, idempotency_key, "claim", machine, submitted_by,
                       payload, False, "adjudicated_status_requires_source_packet")
            conn.commit()
            raise RejectedWrite("adjudicated_status_requires_source_packet")
        if agent:
            cur.execute("INSERT INTO ew.agents(agent_id) VALUES (%s) "
                        "ON CONFLICT DO NOTHING", (agent,))
        cid = ids.claim_id(text_canonical, packet_id, experiment_id)
        rev = ewdb.next_revision(cur)
        cur.execute(
            "INSERT INTO ew.claims(claim_id, version, text_canonical, source_wording, "
            "status, claim_ceiling, agent_id, experiment_id, packet_id, source_span, "
            "creation_method, write_stage, ontology_version, submitted_by, machine, revision) "
            "VALUES (%s,1,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (claim_id, version) DO NOTHING",
            (cid, text_canonical, source_wording, status, claim_ceiling, agent,
             experiment_id, packet_id, source_span, creation_method, write_stage,
             ONTOLOGY_VERSION, submitted_by, machine, rev))
        _log_write(cur, idempotency_key, "claim", machine, submitted_by,
                   payload, True, result_id=cid)
    conn.commit()
    return cid


def submit_evidence(conn, packet_id, source_quote, evidence_type, submitted_by,
                    machine, claim_id=None, verdict_source=None,
                    outcome_canonical=None, metric_text=None, gate=None,
                    negative=False, substrate=None, source_span=None,
                    experiment_id=None, agent=None,
                    creation_method="MODEL_EXTRACTED",
                    write_stage="SUBMITTED", idempotency_key=None):
    payload = dict(packet=packet_id, quote=source_quote[:80])
    with conn.cursor() as cur:
        prior = _idempotency_gate(cur, idempotency_key, "evidence", machine,
                                  submitted_by, payload)
        if prior:
            return prior
        _vocab_check(cur, "evidence_type", evidence_type)
        _vocab_check(cur, "creation_method", creation_method)
        _vocab_check(cur, "outcome_canonical", outcome_canonical, allow_none=True)
        if not packet_id or not source_quote or not source_quote.strip():
            _log_write(cur, idempotency_key, "evidence", machine, submitted_by,
                       payload, False, "evidence_requires_packet_and_quote")
            conn.commit()
            raise RejectedWrite("evidence_requires_packet_and_quote")
        # HARD GATE (charter §25): evidence can never cite a derived view.
        cur.execute("SELECT kind FROM ew.source_packets WHERE packet_id=%s",
                    (packet_id,))
        row = cur.fetchone()
        if row is None:
            _log_write(cur, idempotency_key, "evidence", machine, submitted_by,
                       payload, False, "unknown_source_packet")
            conn.commit()
            raise RejectedWrite("unknown_source_packet")
        if row[0] == "derived_view":
            _log_write(cur, idempotency_key, "evidence", machine, submitted_by,
                       payload, False, "derived_view_cannot_back_evidence")
            conn.commit()
            raise RejectedWrite("derived_view_cannot_back_evidence")
        if agent:
            cur.execute("INSERT INTO ew.agents(agent_id) VALUES (%s) "
                        "ON CONFLICT DO NOTHING", (agent,))
        eid = ids.evidence_id(packet_id, source_span, source_quote)
        rev = ewdb.next_revision(cur)
        cur.execute(
            "INSERT INTO ew.evidence(evidence_id, claim_id, evidence_type, "
            "verdict_source, outcome_canonical, metric_text, gate, negative, "
            "substrate, packet_id, source_span, source_quote, experiment_id, "
            "agent_id, creation_method, write_stage, ontology_version, "
            "submitted_by, machine, revision) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (evidence_id) DO NOTHING",
            (eid, claim_id, evidence_type, verdict_source, outcome_canonical,
             metric_text, gate, negative, substrate, packet_id, source_span,
             source_quote, experiment_id, agent, creation_method, write_stage,
             ONTOLOGY_VERSION, submitted_by, machine, rev))
        _log_write(cur, idempotency_key, "evidence", machine, submitted_by,
                   payload, True, result_id=eid)
    conn.commit()
    return eid


def submit_relation(conn, src_type, src_id, relation_type, dst_type, dst_id,
                    epistemic_class, creation_method, submitted_by, machine,
                    confidence=None, rationale=None, packet_id=None,
                    source_span=None, derived_artifact_id=None,
                    idempotency_key=None):
    payload = dict(src=src_id, rel=relation_type, dst=dst_id)
    with conn.cursor() as cur:
        prior = _idempotency_gate(cur, idempotency_key, "relation", machine,
                                  submitted_by, payload)
        if prior:
            return prior
        _vocab_check(cur, "relation_type", relation_type)
        _vocab_check(cur, "epistemic_class", epistemic_class)
        _vocab_check(cur, "creation_method", creation_method)
        # Epistemic typing rules (charter §3):
        if epistemic_class == "OBSERVED" and not packet_id:
            _log_write(cur, idempotency_key, "relation", machine, submitted_by,
                       payload, False, "observed_relation_requires_packet")
            conn.commit()
            raise RejectedWrite("observed_relation_requires_packet")
        if creation_method == "TENSOR_INFERRED":
            if epistemic_class == "OBSERVED":
                _log_write(cur, idempotency_key, "relation", machine,
                           submitted_by, payload, False,
                           "tensor_output_cannot_be_observed")
                conn.commit()
                raise RejectedWrite("tensor_output_cannot_be_observed")
            if not derived_artifact_id:
                _log_write(cur, idempotency_key, "relation", machine,
                           submitted_by, payload, False,
                           "tensor_relation_requires_artifact_lineage")
                conn.commit()
                raise RejectedWrite("tensor_relation_requires_artifact_lineage")
        rid = ids.relation_id(src_id, relation_type, dst_id, epistemic_class)
        rev = ewdb.next_revision(cur)
        cur.execute(
            "INSERT INTO ew.relations(relation_id, src_type, src_id, relation_type, "
            "dst_type, dst_id, epistemic_class, creation_method, confidence, "
            "rationale, packet_id, source_span, derived_artifact_id, "
            "ontology_version, submitted_by, machine, revision) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (relation_id) DO NOTHING",
            (rid, src_type, src_id, relation_type, dst_type, dst_id,
             epistemic_class, creation_method, confidence, rationale, packet_id,
             source_span, derived_artifact_id, ONTOLOGY_VERSION, submitted_by,
             machine, rev))
        _log_write(cur, idempotency_key, "relation", machine, submitted_by,
                   payload, True, result_id=rid)
    conn.commit()
    return rid


def correct_claim(conn, claim_id, new_text, new_status, submitted_by, machine,
                  packet_id, source_span=None, rationale=None,
                  idempotency_key=None):
    """A correction is a NEW claim version + a CORRECTS relation.
    The historical version row is untouched (charter A13)."""
    with conn.cursor() as cur:
        cur.execute("SELECT max(version) FROM ew.claims WHERE claim_id=%s",
                    (claim_id,))
        row = cur.fetchone()
        if not row or row[0] is None:
            raise RejectedWrite("unknown_claim")
        _vocab_check(cur, "claim_status", new_status)
        new_version = row[0] + 1
        rev = ewdb.next_revision(cur)
        cur.execute(
            "INSERT INTO ew.claims(claim_id, version, text_canonical, status, "
            "packet_id, source_span, creation_method, write_stage, "
            "ontology_version, submitted_by, machine, revision) "
            "VALUES (%s,%s,%s,%s,%s,%s,'HUMAN','SOURCE_BOUND',%s,%s,%s,%s) "
            "ON CONFLICT (claim_id, version) DO NOTHING",
            (claim_id, new_version, new_text, new_status, packet_id,
             source_span, ONTOLOGY_VERSION, submitted_by, machine, rev))
    conn.commit()
    submit_relation(conn, "claim", f"{claim_id}#v{new_version}", "CORRECTS",
                    "claim", f"{claim_id}#v{new_version - 1}",
                    "OBSERVED", "HUMAN", submitted_by, machine,
                    rationale=rationale, packet_id=packet_id,
                    idempotency_key=idempotency_key)
    return f"{claim_id}#v{new_version}"


def record_hypothesis(conn, kind, statement, method, submitted_by, machine,
                      view_name=None, coords=None, score=None,
                      derived_artifact_id=None, basis=None,
                      idempotency_key=None):
    with conn.cursor() as cur:
        hid = ids.hypothesis_id(kind, view_name, coords, statement)
        rev = ewdb.next_revision(cur)
        cur.execute(
            "INSERT INTO ew.hypotheses(hypothesis_id, kind, view_name, coords, "
            "statement, score, method, derived_artifact_id, basis, submitted_by, "
            "machine, revision) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (hypothesis_id) DO NOTHING",
            (hid, kind, view_name, json.dumps(coords) if coords else None,
             statement, score, method, derived_artifact_id,
             json.dumps(basis) if basis else None, submitted_by, machine, rev))
    conn.commit()
    return hid


# ----------------------------------------------------------------- queries

def get_claim(conn, claim_id):
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.claims WHERE claim_id=%s "
                    "ORDER BY version DESC", (claim_id,))
        versions = cur.fetchall()
        if not versions:
            return None
        cur.execute("SELECT * FROM ew.evidence WHERE claim_id=%s "
                    "ORDER BY created_at", (claim_id,))
        evidence = cur.fetchall()
        cur.execute("SELECT * FROM ew.relations WHERE src_id=%s OR dst_id=%s "
                    "ORDER BY created_at", (claim_id, claim_id))
        relations = cur.fetchall()
        return {"claim_id": claim_id, "current": versions[0],
                "versions": versions, "evidence": evidence,
                "relations": relations}


def counterevidence(conn, claim_id, include_qualifications=True):
    types = ["REFUTES", "CONTRADICTS", "FAILS_TO_TRANSFER"]
    if include_qualifications:
        types.append("QUALIFIES")
    with ewdb.dict_cur(conn) as cur:
        cur.execute(
            "SELECT r.*, c.text_canonical AS src_text, c.status AS src_status "
            "FROM ew.relations r LEFT JOIN ew.claims c "
            "ON c.claim_id = r.src_id AND c.version = "
            "  (SELECT max(version) FROM ew.claims WHERE claim_id=r.src_id) "
            "WHERE r.dst_id=%s AND r.relation_type = ANY(%s)", (claim_id, types))
        rels = cur.fetchall()
        cur.execute(
            "SELECT * FROM ew.evidence WHERE claim_id=%s AND "
            "(negative OR outcome_canonical IN ('REFUTED','NULL_RESULT','MIXED'))",
            (claim_id,))
        neg = cur.fetchall()
    return {"claim_id": claim_id, "counter_relations": rels,
            "negative_evidence": neg}


def contradictions(conn, claim_id=None):
    """Direct vs conditional: for each CONTRADICTS/REFUTES pair between
    claims, report which contextual dimensions differ between the two sides'
    evidence (substrate, agent, evidence_type, gate). Differing dimensions =
    candidate conditional structure, surfaced for inspection — never
    auto-resolved (charter §12)."""
    with ewdb.dict_cur(conn) as cur:
        q = ("SELECT * FROM ew.relations WHERE relation_type IN "
             "('CONTRADICTS','REFUTES') AND epistemic_class='OBSERVED'")
        args = []
        if claim_id:
            q += " AND (src_id=%s OR dst_id=%s)"
            args = [claim_id, claim_id]
        cur.execute(q, args)
        rels = cur.fetchall()
        out = []
        for r in rels:
            cur.execute("SELECT substrate, agent_id, evidence_type, gate "
                        "FROM ew.evidence WHERE claim_id=%s", (r["src_id"],))
            a = cur.fetchall()
            cur.execute("SELECT substrate, agent_id, evidence_type, gate "
                        "FROM ew.evidence WHERE claim_id=%s", (r["dst_id"],))
            b = cur.fetchall()
            differing = []
            for dim in ("substrate", "agent_id", "evidence_type", "gate"):
                sa = {x[dim] for x in a if x[dim]}
                sb = {x[dim] for x in b if x[dim]}
                if sa and sb and sa.isdisjoint(sb):
                    differing.append({"dimension": dim, "side_a": sorted(sa),
                                      "side_b": sorted(sb)})
            out.append({**r,
                        "classification": ("APPARENT_UNDER_DIFFERING_CONDITIONS"
                                           if differing else "DIRECT"),
                        "differing_dimensions": differing})
    return out


def dependencies(conn, claim_id, max_depth=4):
    """Transitive DEPENDS_ON / PRODUCED_BY / CONSUMED_BY walk."""
    seen, frontier, edges = {claim_id}, [claim_id], []
    with ewdb.dict_cur(conn) as cur:
        for _ in range(max_depth):
            if not frontier:
                break
            cur.execute(
                "SELECT * FROM ew.relations WHERE relation_type IN "
                "('DEPENDS_ON','PRODUCED_BY','CONSUMED_BY','MOTIVATED',"
                "'REUSES_NEGATIVE_EVIDENCE') AND (src_id = ANY(%s) OR dst_id = ANY(%s))",
                (frontier, frontier))
            rows = cur.fetchall()
            nxt = []
            for r in rows:
                edges.append(r)
                for node in (r["src_id"], r["dst_id"]):
                    if node not in seen:
                        seen.add(node)
                        nxt.append(node)
            frontier = nxt
    return {"root": claim_id, "nodes": sorted(seen), "edges": edges}


def provenance_chain(conn, object_id):
    """Walk any object back to its packet / commit / file hash (gate G1)."""
    with ewdb.dict_cur(conn) as cur:
        chain = []
        oid = object_id.split("#")[0]
        for table, idcol in (("ew.claims", "claim_id"),
                             ("ew.evidence", "evidence_id"),
                             ("ew.experiments", "experiment_id"),
                             ("ew.relations", "relation_id"),
                             ("ew.hypotheses", "hypothesis_id")):
            cur.execute(f"SELECT * FROM {table} WHERE {idcol}=%s LIMIT 1", (oid,))
            row = cur.fetchone()
            if row:
                chain.append({"layer": table, "object": row})
                pid = row.get("packet_id")
                dai = row.get("derived_artifact_id")
                if pid:
                    cur.execute("SELECT * FROM ew.source_packets WHERE packet_id=%s",
                                (pid,))
                    chain.append({"layer": "ew.source_packets",
                                  "object": cur.fetchone()})
                if dai:
                    cur.execute("SELECT * FROM ew.derived_artifacts WHERE artifact_id=%s",
                                (dai,))
                    art = cur.fetchone()
                    chain.append({"layer": "ew.derived_artifacts", "object": art})
                    if art and art.get("snapshot_id"):
                        cur.execute("SELECT * FROM ew.snapshots WHERE snapshot_id=%s",
                                    (art["snapshot_id"],))
                        chain.append({"layer": "ew.snapshots",
                                      "object": cur.fetchone()})
                break
        return chain


def apply_migration(conn):
    mig_dir = Path(__file__).resolve().parent.parent / "migrations"
    with conn.cursor() as cur:
        for f in sorted(mig_dir.glob("*.sql")):
            cur.execute(f.read_text(encoding="utf-8"))
        ontology.seed(cur, ONTOLOGY_VERSION)
    conn.commit()
