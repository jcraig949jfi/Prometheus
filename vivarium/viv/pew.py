"""PEW fossil write -- the link from a queue item to the authoritative record.

Vivarium writes only what it OBSERVED. Every scientific identity in a fossil
encounter (encounter_id, players, world_binding_id) is DECLARED by the
requester in `spec.pew` and copied through unchanged; Vivarium mints none of
them, because encounter_id is a Proteus-authored specification identity and
inventing one would silently create a second, fake lineage.

What Vivarium supplies is exactly the execution half it witnessed: run_id
(exp_id:work_id), the anchoring ledger event, the world ids, the outcome the
pre-registered rule produced, and the resources the run reported.

Per HARMONIA_PEW_WRITE_CONTRACT.md (pew.fossil.v2). If a spec declares no
`pew` block, nothing is written and the skip is recorded as an event -- an
absent link is stated, never implied.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Optional


class PewError(RuntimeError):
    pass


class PewClient:
    def __init__(self, base_url: str, token: str, *, machine: str = "M1",
                 agent: str = "vivarium", namespace: str = "test",
                 timeout: float = 30.0):
        self.base = base_url.rstrip("/")
        self.namespace = namespace
        self.timeout = timeout
        self.headers = {"Authorization": "Bearer " + token,
                        "X-Prometheus-Machine": machine,
                        "X-Prometheus-Agent": agent,
                        "content-type": "application/json"}

    def _req(self, method: str, path: str, body: Optional[dict] = None):
        req = urllib.request.Request(
            self.base + path,
            data=json.dumps(body).encode() if body is not None else None,
            headers=self.headers, method=method)
        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as exc:
            try:
                detail = json.loads(exc.read() or b"{}")
            except Exception:                       # noqa: BLE001
                detail = {}
            return exc.code, detail

    def health(self) -> dict:
        status, body = self._req("GET", "/health")
        if status != 200:
            raise PewError("PEW health %s: %s" % (status, body))
        return body


def write_encounter(client: PewClient, *, spec: dict, run, engine: dict,
                    producer_version: str, relation: dict = None) -> dict:
    """Write the world anchor and the fossil encounter. Returns a record with
    `pew_reference` when the encounter was persisted.

    HANDLES FAILURES AS WELL AS RESULTS. A run that crossed the execution
    boundary and then failed is fossilized too: the endpoint that matters to a
    selection experiment is "failures discovered per experiment EXECUTED", and
    that requires `executed` to be countable from the fossil record rather than
    only from the queue. Such a fossil carries `failure_class` and NO invented
    outcome -- absence of a result is recorded as absence, and the anchor is
    EXPERIMENT_COMMITTED, which attests that execution was attempted and
    nothing about a measurement that never happened.

    `relation` is the PROVENANCE half -- experiment_id, request_key, family,
    arm, replication_of, candidate set. It travels in the producer block, which
    is what lets an archaeologist get from a fossil back to the request and
    hence to the policy that proposed it. It reaches PEW and never the
    executor.

    HTTP 200 is not treated as persistence: the encounter is read back and the
    reference is only issued if the read-back succeeds."""
    pew = spec["pew"]
    anchor = run.anchor
    if not anchor.get("resolved"):
        raise PewError("refusing to write a fossil with an unresolved SFE "
                       "anchor: %s" % anchor.get("reason"))
    failed = run.failure_class is not None

    # The requester may ADD producer fields; it may not overwrite the identity
    # of what actually produced the record. Vivarium's own keys go last.
    producer = {**dict(pew.get("producer") or {}),
                "component": "vivarium.runner", "version": producer_version,
                "engine_source_hash": engine.get("engine_source_hash"),
                "spec_hash": run.summary.get("spec_hash") or run.spec_hash_hint,
                "queue": {k: v for k, v in (relation or {}).items()
                          if v is not None}}

    envelope = run.summary.get("audit_envelope") or {}
    head_hash = envelope.get("ledger_head_hash")

    world_body = {
        "world_id": run.world_id, "sfe_world_id": run.world_id,
        "seed_root": str(spec["world"]["seed_root"]),
        "world_binding_id": pew.get("world_binding_id") or run.world_id,
        "namespace": client.namespace, "producer": producer}
    if head_hash:
        world_body["sfe_head_hash"] = head_hash
    status, body = client._req("POST", "/fossil/worlds", world_body)  # noqa: SLF001
    world_anchor = {"http": status, "body": body}
    if status not in (200, 201, 409):
        raise PewError("world anchor rejected %s: %s" % (status, body))

    # The execution-lineage fields (pew.fossil.v2 accepted_fields) are exactly
    # the identities Vivarium WITNESSED: which engine instance served the run
    # and under which session. The session KEY is never sent -- only its
    # fingerprint, because a key in a record is a leaked credential.
    session = run.summary.get("session") or {}
    enc_body = {
        "encounter_id": pew["encounter_id"],
        "run_id": run.run_id,
        "sfe_event_id": anchor["sfe_event_id"],
        "sfe_entry_hash": anchor["sfe_entry_hash"],
        "sfe_event_seq": anchor["sfe_event_seq"],
        "sfe_world_id": run.world_id, "world_id": run.world_id,
        "players": list(pew["players"]),
        "seed": str(spec["world"]["seed_root"]),
        "resources_used": {"work_id": run.work_id, "obs_id": run.obs_id,
                           "attempted": True},
        "namespace": client.namespace,
        "producer": producer}
    if failed:
        # No outcome. The pew.fossil.v2 contract permits outcome to be the work
        # item's TERMINAL STATUS, which is an observed fact -- but only when one
        # was observed. Where nothing was, the field is omitted rather than
        # filled, because "absence of a result" and "a result of failure" are
        # different claims and only the first one is true.
        enc_body["failure_class"] = run.failure_class
        if run.work_id is not None:
            enc_body["outcome"] = "FAILED"
    else:
        enc_body["outcome"] = run.outcome
    for key, value in (("sfe_engine_instance_id",
                        engine.get("engine_instance_id")),
                       ("sfe_ledger_head_hash", head_hash),
                       ("sfe_session_id", session.get("sfe_session_id")),
                       ("sfe_session_key_fp", session.get("sfe_session_key_fp"))):
        if value:
            enc_body[key] = value
    status, body = client._req("POST", "/fossil/encounters", enc_body)  # noqa: SLF001
    if status not in (200, 201):
        raise PewError("encounter rejected %s: %s" % (status, body))

    read_status, read_body = client._req(                    # noqa: SLF001
        "GET", "/fossil/encounters/%s" % pew["encounter_id"])
    if read_status != 200:
        raise PewError("encounter not readable back (%s): %s"
                       % (read_status, read_body))

    return {"pew_reference": "pew:encounter/%s:%s"
                             % (pew["encounter_id"], run.run_id),
            "failure_class": run.failure_class,
            "world_anchor": world_anchor,
            "encounter": {"http": status, "body": body},
            "read_back": {"http": read_status}}
