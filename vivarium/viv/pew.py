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


def _execution_inputs(run) -> dict:
    """The load/resource summary a fossil carries. Reference-sized, not a copy.

    Only what was WITNESSED, and only where a receipt exists: a run with no
    artifact slot contributes nothing here rather than a row of zeros, because
    "consumed no artifacts" and "was never asked to" are different facts.
    """
    out = {}
    receipt = getattr(run, "load_receipt", None) or {}
    if receipt.get("loaded"):
        out["artifacts_consumed"] = receipt.get("closure_manifest")
        out["closure_manifest_hash"] = receipt.get("closure_manifest_hash")
        out["artifact_bytes_loaded"] = receipt.get("bytes_loaded")
    elif receipt.get("rejected"):
        out["preflight_rejection_class"] = receipt.get("rejection_class")
    vector = getattr(run, "resources", None) or {}
    out["attempt_id"] = vector.get("attempt_id")
    out["stage"] = vector.get("stage")
    for name in ("wall_seconds", "cpu_seconds", "artifact_bytes"):
        if name in vector:
            out[name] = vector[name]["quantity"]
            out[name + "_enforcement_class"] = \
                vector[name]["enforcement_class"]
    return out


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


def build_bodies(*, spec: dict, run, engine: dict, producer_version: str,
                 namespace: str, relation: dict = None, producer: dict = None,
                 termination: dict = None) -> dict:
    """The two PEW bodies (world anchor, encounter) as PURE data -- what the
    outbox stores and the deliverer posts (point release). write_encounter
    below is build_bodies + post_bodies for the synchronous path that stays
    in use until the outbox table exists."""
    pew = spec["pew"]
    anchor = run.anchor
    if not anchor.get("resolved"):
        raise PewError("refusing to write a fossil with an unresolved SFE "
                       "anchor: %s" % anchor.get("reason"))
    failed = run.failure_class is not None
    mine = dict(producer or {})
    if not mine:
        mine = {"component": "vivarium.runner", "version": producer_version,
                "engine_source_hash": engine.get("engine_source_hash"),
                "spec_hash": run.summary.get("spec_hash")
                             or run.spec_hash_hint,
                "queue": {k: v for k, v in (relation or {}).items()
                          if v is not None}}
    producer = {**dict(pew.get("producer") or {}), **mine}
    envelope = run.summary.get("audit_envelope") or {}
    head_hash = envelope.get("ledger_head_hash")
    world_body = {
        "world_id": run.world_id, "sfe_world_id": run.world_id,
        "seed_root": str(spec["world"]["seed_root"]),
        "world_binding_id": pew.get("world_binding_id") or run.world_id,
        "namespace": namespace, "producer": producer}
    if head_hash:
        world_body["sfe_head_hash"] = head_hash
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
                           "attempted": True,
                           **_execution_inputs(run)},
        "namespace": namespace,
        "producer": producer}
    if termination is not None:
        # TERMINATION_ENVELOPE.md s4: the envelope travels verbatim so a
        # reader can tell OBSERVED from UNOBSERVED-BEYOND-THE-HORIZON.
        enc_body["resources_used"]["termination"] = termination
    if failed:
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
    return {"world": world_body, "encounter": enc_body,
            "encounter_id": pew["encounter_id"], "run_id": run.run_id,
            "failure_class": run.failure_class,
            "recorded_in_sfe": bool(run.obs_id or run.work_id)}


def post_bodies(client: PewClient, bodies: dict) -> dict:
    """POST the world anchor then the encounter, read the encounter back.
    Idempotent: a repeat reports write_outcome duplicate_identical."""
    status, body = client._req("POST", "/fossil/worlds", bodies["world"])  # noqa: SLF001
    world_anchor = {"http": status, "body": body}
    if status not in (200, 201, 409):
        raise PewError("world anchor rejected %s: %s" % (status, body))
    status, body = client._req("POST", "/fossil/encounters", bodies["encounter"])  # noqa: SLF001
    if status not in (200, 201):
        raise PewError("encounter rejected %s: %s" % (status, body))
    read_status, read_body = client._req(                    # noqa: SLF001
        "GET", "/fossil/encounters/%s" % bodies["encounter_id"])
    if read_status != 200:
        raise PewError("encounter not readable back (%s): %s"
                       % (read_status, read_body))
    outcome = (body or {}).get("status")
    return {"pew_reference": "pew:encounter/%s:%s"
                             % (bodies["encounter_id"], bodies["run_id"]),
            "failure_class": bodies["failure_class"],
            "world_anchor": world_anchor,
            "encounter": {"http": status, "body": body},
            "read_back": {"http": read_status},
            "write_outcome": outcome,
            "idempotent_replay": outcome == "duplicate_identical",
            "recorded_in_sfe": bodies["recorded_in_sfe"],
            "indexed_in_pew": read_status == 200}


def write_encounter(client: PewClient, *, spec: dict, run, engine: dict,
                    producer_version: str, relation: dict = None,
                    producer: dict = None, termination: dict = None) -> dict:
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
    bodies = build_bodies(spec=spec, run=run, engine=engine,
                          producer_version=producer_version,
                          namespace=client.namespace, relation=relation,
                          producer=producer, termination=termination)
    return post_bodies(client, bodies)
