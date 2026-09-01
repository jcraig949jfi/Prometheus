"""Content-addressed identifiers.

Same submission => same ID on every machine; retries collapse on insert.
Identity fields are the minimal set that make two records "the same
scientific object" — NOT the full payload (a re-submission with a fixed typo
in a non-identity field is a new version, not a new object).
"""
import hashlib
import json


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(prefix: str, identity: dict) -> str:
    h = hashlib.sha256(canonical_json(identity).encode("utf-8")).hexdigest()
    return f"{prefix}-{h[:12]}"


def packet_id(uri: str, content_sha256: str | None) -> str:
    return _digest("SP", {"uri": uri, "sha": content_sha256})


def experiment_id(agent: str, project: str, title: str) -> str:
    return _digest("X", {"agent": agent, "project": project, "title": title})


def claim_id(text_canonical: str, packet: str | None, experiment: str | None) -> str:
    return _digest("C", {"text": text_canonical.strip().lower(),
                         "packet": packet, "experiment": experiment})


def evidence_id(packet: str, source_span: str | None, source_quote: str) -> str:
    return _digest("E", {"packet": packet, "span": source_span,
                         "quote": source_quote.strip()})


def relation_id(src_id: str, relation_type: str, dst_id: str,
                epistemic_class: str) -> str:
    return _digest("R", {"src": src_id, "rel": relation_type, "dst": dst_id,
                         "class": epistemic_class})


def snapshot_id(view_name: str, view_version: int, filter_spec: dict,
                content_sha256: str) -> str:
    return _digest("SN", {"view": view_name, "v": view_version,
                          "filters": filter_spec, "sha": content_sha256})


def artifact_id(kind: str, snapshot: str | None, params: dict) -> str:
    return _digest("DA", {"kind": kind, "snapshot": snapshot, "params": params})


def hypothesis_id(kind: str, view_name: str | None, coords: dict | None,
                  statement: str) -> str:
    return _digest("H", {"kind": kind, "view": view_name, "coords": coords,
                         "statement": statement.strip().lower()})


def payload_sha256(payload: dict) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
