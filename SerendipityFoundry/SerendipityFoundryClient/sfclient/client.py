"""Serendipity Foundry Engine client -- STANDARD LIBRARY ONLY.

Copy this one file to any machine to drive the Engine's /v2 REST API with a
stock Python install (no Engine code, no dependencies). Two classes:

  EngineClient  -- register/authenticate, and one method per API operation.
  RemoteWorker  -- claim work over REST, run a LOCAL executor callable,
                   heartbeat the lease, and commit the result. Workers are
                   disposable: kill one mid-lease and the Engine reclaims the
                   work for another.

Auth: the Engine issues a bearer token when you register a client
(`EngineClient.register`); every later call carries it. Over a LAN the Engine
runs TLS, so pass `cafile=` (the Engine's cert) to verify it.

The network is never a scientific result: a completed work item's result is
authoritative on the Engine; a dropped connection is retried by the caller or
reclaimed by the Engine, never fabricated here.
"""

from __future__ import annotations

import http.client
import json
import ssl
import time
import urllib.parse
from typing import Any, Callable, Optional


class EngineError(Exception):
    def __init__(self, status: int, detail: Any):
        self.status, self.detail = status, detail
        super().__init__(f"HTTP {status}: {detail}")


class EngineClient:
    def __init__(self, base_url: str, token: Optional[str] = None, *,
                 cafile: Optional[str] = None, insecure: bool = False,
                 timeout: float = 30.0, session_key: Optional[str] = None,
                 client_id: Optional[str] = None):
        self._u = urllib.parse.urlsplit(base_url.rstrip("/"))
        if self._u.scheme not in ("http", "https"):
            raise ValueError("base_url must be http(s)")
        self.token = token
        self.timeout = timeout
        # THE ENGINE-ISSUED PRINCIPAL. register() used to return the token and
        # throw the client_id away, so a caller that needed to be NAMED -- to
        # be granted read on someone's scope, to appear in a cost event's
        # attribution, to reconcile a receipt -- had no way to say who it was
        # and would have had to derive something. There is no /v2/clients/me
        # route, so this is RETAINED, never reconstructed: if you built the
        # client from a bare token this stays None and says so, rather than
        # inventing a substitute principal that would then be wrong in exactly
        # the records that matter.
        self.client_id = client_id
        # Session affinity: set automatically by create_session() and then sent
        # on EVERY subsequent call. A caller never appends it per-endpoint --
        # that was the whole point of choosing one header. Pass it to the
        # constructor to resume an existing session in a second process.
        self.session_key = session_key
        if self._u.scheme == "https":
            if insecure:
                self._ctx = ssl._create_unverified_context()
            else:
                self._ctx = ssl.create_default_context(cafile=cafile)
        else:
            self._ctx = None

    # -- transport ---------------------------------------------------------
    def _conn(self):
        if self._u.scheme == "https":
            return http.client.HTTPSConnection(self._u.hostname, self._u.port,
                                               timeout=self.timeout,
                                               context=self._ctx)
        return http.client.HTTPConnection(self._u.hostname, self._u.port,
                                          timeout=self.timeout)

    def _req(self, method: str, path: str, body: Optional[dict] = None, *,
             idem_key: Optional[str] = None) -> Any:
        headers = {"accept": "application/json"}
        if self.token:
            headers["authorization"] = f"Bearer {self.token}"
        if self.session_key:
            headers["X-SFE-Session"] = self.session_key
        if idem_key is not None:
            # F5: a transport retry with the same key replays the same result;
            # the same key + a different request is a 409 conflict.
            headers["Idempotency-Key"] = idem_key
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["content-type"] = "application/json"
        conn = self._conn()
        try:
            conn.request(method, path, body=data, headers=headers)
            resp = conn.getresponse()
            raw = resp.read()
            status = resp.status
        finally:
            conn.close()
        parsed = json.loads(raw) if raw else None
        if 200 <= status < 300:
            return parsed
        detail = parsed.get("detail") if isinstance(parsed, dict) else parsed
        raise EngineError(status, detail)

    # -- identity ----------------------------------------------------------
    def register(self, name: str) -> str:
        """Register a client, adopting BOTH its token and its client_id.

        Returns the token, as it always did -- the id is retained on the
        instance as `client_id` rather than returned, so no existing caller
        changes. The token is shown once by the engine and is never logged or
        repeated by this client; `__repr__` deliberately shows the id and not
        the token."""
        r = self._req("POST", "/v2/clients", {"name": name})
        self.token = r["token"]
        self.client_id = r.get("client_id")
        return self.token

    def __repr__(self) -> str:
        """Names the principal, NEVER the credential. This class now holds an
        identity as well as a secret, and the moment both are on one object an
        accidental repr in a log is the obvious way to leak the wrong one."""
        return "EngineClient(base_url=%r, client_id=%r, authenticated=%s)" % (
            self._u.geturl(), self.client_id, self.token is not None)

    def version(self) -> dict:
        return self._req("GET", "/v2/version")

    def create_session(self, name: str) -> str:
        """Open a session and ADOPT its affinity key.

        Returns session_id, as before, so existing callers are unchanged. The
        key is stored on the client and sent on every later call; read it from
        `.session_key` if you need to hand it to another process."""
        r = self._req("POST", "/v2/sessions", {"name": name})
        self.session_key = r.get("session_key") or self.session_key
        self.engine_instance_id = r.get("engine_instance_id")
        return r["session_id"]

    def create_topology_group(self, note: Optional[str] = None) -> str:
        """Mint a REGISTERED sharing group (an unguessable server-issued
        capability). Cross-client sharing requires both worlds to carry this id,
        which you share with the other client by DELIBERATE transfer."""
        return self._req("POST", "/v2/topology-groups",
                         {"note": note})["group_id"]

    # -- worlds ------------------------------------------------------------
    def create_world(self, session_id: str, name: str, *,
                     require_attestation: bool = False,
                     sharing_policy: str = "ISOLATED",
                     topology_group: Optional[str] = None,
                     budget: Optional[dict] = None,
                     seed_root: Optional[int] = None) -> dict:
        return self._req("POST", "/v2/worlds", {
            "session_id": session_id, "name": name,
            "sharing_policy": sharing_policy, "topology_group": topology_group,
            "budget": budget or {}, "seed_root": seed_root,
            "require_attestation": require_attestation})

    def list_worlds(self) -> list:
        return self._req("GET", "/v2/worlds")["worlds"]

    def get_world(self, wid: str) -> dict:
        return self._req("GET", f"/v2/worlds/{wid}")

    def start(self, wid): return self._req("POST", f"/v2/worlds/{wid}/start")
    def pause(self, wid): return self._req("POST", f"/v2/worlds/{wid}/pause")
    def resume(self, wid): return self._req("POST", f"/v2/worlds/{wid}/resume")
    def terminate(self, wid):
        return self._req("POST", f"/v2/worlds/{wid}/terminate")

    def checkpoint(self, wid) -> dict:
        return self._req("POST", f"/v2/worlds/{wid}/checkpoint")

    def fork(self, wid, checkpoint_id: str, children: list) -> list:
        return self._req("POST", f"/v2/worlds/{wid}/fork",
                         {"checkpoint_id": checkpoint_id,
                          "children": children})["children"]

    def status(self, wid) -> dict:
        return self._req("GET", f"/v2/worlds/{wid}/status")

    def events(self, wid, limit: int = 100) -> list:
        return self._req("GET", f"/v2/worlds/{wid}/events?limit={limit}")["events"]

    def resources(self, wid) -> dict:
        return self._req("GET", f"/v2/worlds/{wid}/resources")

    def failures(self, wid, *, failure_type=None, consumed=None) -> list:
        q = []
        if failure_type:
            q.append(f"failure_type={urllib.parse.quote(failure_type)}")
        if consumed is not None:
            q.append(f"consumed={'true' if consumed else 'false'}")
        qs = ("?" + "&".join(q)) if q else ""
        return self._req("GET", f"/v2/worlds/{wid}/failures{qs}")["failures"]

    def lineage(self, wid, kind: str, obj_id: str,
                direction: str = "descendants") -> list:
        return self._req(
            "GET", f"/v2/worlds/{wid}/lineage?kind={kind}&id="
            f"{urllib.parse.quote(obj_id)}&direction={direction}")["nodes"]

    # -- research objects --------------------------------------------------
    def hypothesis(self, wid, statement: str, *,
                   idem_key: Optional[str] = None) -> str:
        return self._req("POST", f"/v2/worlds/{wid}/hypotheses",
                         {"statement": statement}, idem_key=idem_key)["hyp_id"]

    def prediction(self, wid, hyp_id: str, content: dict, *,
                   idem_key: Optional[str] = None) -> str:
        return self._req("POST", f"/v2/worlds/{wid}/predictions",
                         {"hyp_id": hyp_id, "content": content},
                         idem_key=idem_key)["pred_id"]

    def experiment(self, wid, spec: dict, *, hyp_id=None, pred_id=None,
                   commit: bool = True, enqueue: bool = False,
                   kind: str = "experiment", priority: int = 100,
                   unit_of_analysis: Optional[str] = None,
                   declared_n: Optional[int] = None,
                   source_set: Optional[list] = None) -> dict:
        """Register an experiment. commit=True (default) crosses the irreversible
        COMMIT boundary in the same call: it freezes the spec, CLOSES the
        prospective-prediction window, debits the experiment budget, and (with
        enqueue) releases it for execution. commit=False registers a plan only
        (no budget, window still open, non-executable) -- commit it later with
        commit_experiment().

        v6 -- ANALYSIS. Supplying unit_of_analysis + declared_n + source_set
        (all three, or none) registers this experiment as an ANALYSIS. The
        engine hashes the source set (order- and world-independent), COUNTS the
        distinct units under your declared key, and reports its count beside
        your declared_n in the returned `analysis` block. It never decides
        which number is scientifically right -- counting is not statistics --
        but 128 observations drawn from 8 worlds are n=8 under
        unit_of_analysis="world" and n=128 under "observation", and the engine
        will tell you which one your source set actually contains.

        Only the set's HASH is stored. Put the set itself in `spec` if you want
        it recoverable; there spec_hash seals it at commit."""
        return self._req("POST", f"/v2/worlds/{wid}/experiments", {
            "spec": spec, "hyp_id": hyp_id, "pred_id": pred_id,
            "commit": commit, "enqueue": enqueue, "kind": kind,
            "priority": priority, "unit_of_analysis": unit_of_analysis,
            "declared_n": declared_n, "source_set": source_set})

    def analysis(self, wid, exp_id: str) -> dict:
        """The SEALED unit-of-analysis verification for an analysis, read back
        from the world's hash chain rather than recomputed."""
        return self._req("GET",
                         f"/v2/worlds/{wid}/experiments/{exp_id}/analysis")

    def commit_experiment(self, wid, exp_id: str, *, enqueue: bool = False,
                          kind: str = "experiment", priority: int = 100) -> dict:
        """Cross the irreversible commit boundary for a previously registered
        experiment (see experiment(commit=False))."""
        return self._req("POST",
                         f"/v2/worlds/{wid}/experiments/{exp_id}/commit",
                         {"enqueue": enqueue, "kind": kind, "priority": priority})

    def observation(self, wid, exp_id: str, content: dict, outcome: str,
                    pred_id: Optional[str] = None,
                    work_id: Optional[str] = None,
                    retrospective: bool = False,
                    replication: bool = False,
                    idem_key: Optional[str] = None) -> str:
        """Record an outcome on a COMMITTED experiment. A bound prediction is
        prospective only if it preceded the commit; a post-commit prediction
        needs retrospective=True and is never prospective. Pass work_id to bind
        the authoritative completed work result (evidence_class
        ENGINE_WORK_RESULT); otherwise the evidence is CLIENT_ASSERTED. A SECOND
        observation bound to the same prediction needs replication=True and is
        recorded as a retest that never re-adjudicates the original (F3)."""
        return self._req("POST", f"/v2/worlds/{wid}/observations", {
            "exp_id": exp_id, "content": content, "outcome": outcome,
            "pred_id": pred_id, "work_id": work_id,
            "retrospective": retrospective, "replication": replication},
            idem_key=idem_key)["obs_id"]

    def failure(self, wid, *, failure_type: str, falsifier: str, violated: str,
                idem_key: Optional[str] = None, **kw) -> str:
        body = {"failure_type": failure_type, "falsifier": falsifier,
                "violated": violated, **kw}
        return self._req("POST", f"/v2/worlds/{wid}/failures", body,
                         idem_key=idem_key)["failure_id"]

    def artifact(self, wid, kind: str, data: bytes, meta=None,
                 *, idem_key=None, expected_blob_hash=None):
        """Store bytes. Pass expected_blob_hash to make the ENGINE enforce
        the content identity: it recomputes the digest and stores NOTHING
        on a mismatch. The gate has existed engine-side since D-CIDGATE-1
        and this client could not reach it, so corruption inside a
        caller's own pipeline was stored as a valid artifact carrying an
        honest digest of the WRONG bytes."""
        import base64
        return self._req("POST", f"/v2/worlds/{wid}/artifacts", {
            "kind": kind, "data_b64": base64.b64encode(data).decode(),
            "meta": meta or {},
            "expected_blob_hash": expected_blob_hash}, idem_key=idem_key)

    def artifact_content(self, wid, artifact_id: str, *,
                         expected_blob_hash: Optional[str] = None,
                         expected_digest: Optional[str] = None,
                         expected_bytes: Optional[int] = None,
                         max_bytes: Optional[int] = None) -> dict:
        """AUTHORIZED RESOLUTION of an artifact by (world_id, artifact_id).

        Succeeds iff the artifact is visible to this world -- native here or
        legally imported here -- and you are authorized for that world. Returns
        content_b64, the provenance, and a `resolution` receipt naming the
        engine instance, the build, the verified digest and the authorization
        basis.

        expected_digest is an ASSERTION about WHICH object you meant. The
        ENGINE checks it, and only AFTER authorization and the world-scoped
        lookup -- so a digest never authorizes a read, and a caller who knows
        only a hash still gets 404. A mismatch returns 422 and no bytes.
        expected_bytes / max_bytes assert size at that same gate rather than
        after you have already received the payload."""
        # expected_blob_hash is the PRIMARY name, matching the write path:
        # one thing should not have two names across two directions, which is
        # exactly what trips a headless consumer. expected_digest is kept as an
        # accepted alias so nothing written against the first cut breaks.
        want = expected_blob_hash or expected_digest
        if expected_blob_hash and expected_digest \
                and expected_blob_hash != expected_digest:
            raise ValueError(
                "expected_blob_hash and expected_digest disagree; they are the "
                "same field under two names, so passing both different is a "
                "bug rather than a choice")
        q = f"/v2/worlds/{wid}/artifacts/{artifact_id}/content"
        parts = []
        if want:
            parts.append("expected_blob_hash=" + want)
        if expected_bytes is not None:
            parts.append("expected_bytes=%d" % expected_bytes)
        if max_bytes is not None:
            parts.append("max_bytes=%d" % max_bytes)
        if parts:
            q += "?" + "&".join(parts)
        return self._req("GET", q)

    def artifact_bytes(self, wid, artifact_id: str, *,
                       expected_blob_hash: Optional[str] = None,
                       expected_digest: Optional[str] = None,
                       expected_bytes: Optional[int] = None,
                       max_bytes: Optional[int] = None) -> bytes:
        """The decoded bytes, with the engine's gates applied AND a local
        re-verification of the digest the engine reported.

        The local check is defence in depth, not the guarantee: the engine
        already re-hashes every byte it serves and refuses a mismatch. This
        catches corruption between the engine and here, which is the one span
        the engine cannot see."""
        import base64
        import hashlib
        r = self.artifact_content(wid, artifact_id,
                                  expected_blob_hash=expected_blob_hash,
                                  expected_digest=expected_digest,
                                  expected_bytes=expected_bytes,
                                  max_bytes=max_bytes)
        raw = base64.b64decode(r["content_b64"])
        got = "sha256:" + hashlib.sha256(raw).hexdigest()
        if got != r.get("blob_hash"):
            raise SFEError(0, {"error": "digest_mismatch_in_transit",
                               "message": "bytes received do not hash to the "
                                          "digest the engine reported",
                               "engine_reported": r.get("blob_hash"),
                               "locally_computed": got})
        return raw

    def knowledge_set(self, wid, seq: Optional[int] = None) -> dict:
        """F10: the information-availability frontier of this world at/<= seq
        (global event_seq; omit for now). Answers only 'could world W legally
        know X by seq N' -- not read, not used, not causal."""
        q = f"?seq={seq}" if seq is not None else ""
        return self._req("GET", f"/v2/worlds/{wid}/knowledge{q}")

    def import_artifact(self, wid, source_world: str, source_artifact: str):
        return self._req("POST", f"/v2/worlds/{wid}/import", {
            "source_world": source_world, "source_artifact": source_artifact})

    def consume_budget(self, wid, resource: str, amount: float, *,
                       idem_key: Optional[str] = None) -> dict:
        """Charge a resource. Pass idem_key so a transport retry does not
        double-bill: without one the engine cannot tell two identical charges
        apart, and a timeout retry bills twice."""
        return self._req("POST", f"/v2/worlds/{wid}/budget/consume",
                         {"resource": resource, "amount": amount},
                         idem_key=idem_key)

    # ---- v8 reservations and cost events ----------------------------------

    def reserve_budget(self, wid, resource: str, amount: float, *,
                       stage: str, attempt_id: Optional[str] = None,
                       idem_key: Optional[str] = None) -> dict:
        """Take the money BEFORE the work. An enforceable limit then stops an
        operation before it starts, instead of discovering afterwards that it
        should have -- a post-hoc debit is not enforcement. Settle with
        cost_event(reservation_id=...), or give it back with release_budget."""
        return self._req("POST", f"/v2/worlds/{wid}/budget/reserve",
                         {"resource": resource, "amount": amount,
                          "stage": stage, "attempt_id": attempt_id},
                         idem_key=idem_key)

    def release_budget(self, reservation_id: str, reason: str) -> dict:
        """Give the whole reservation back; the operation did not happen."""
        return self._req("POST",
                         f"/v2/budget/reservations/{reservation_id}/release",
                         {"reason": reason})

    def cost_event(self, wid, *, stage: str, resources: list,
                   attempt_id: Optional[str] = None,
                   reservation_id: Optional[str] = None,
                   source_artifacts: Optional[list] = None,
                   output_artifacts: Optional[list] = None,
                   environment: Optional[dict] = None,
                   refs: Optional[dict] = None) -> dict:
        """Record what an activity actually cost, settling its reservation
        EXACTLY ONCE -- a settled reservation is never billed again.

        Each resource entry is {resource, quantity, unit, method, scope}.
        `quantity` may be null, meaning UNAVAILABLE: not zero, and never summed
        into a total. There is deliberately no enforcement field -- the class
        belongs to the LIMIT and the engine resolves it, so a caller cannot
        declare its own spend exempt from a cap it was given."""
        return self._req("POST", f"/v2/worlds/{wid}/cost-events", {
            "stage": stage, "resources": resources, "attempt_id": attempt_id,
            "reservation_id": reservation_id,
            "source_artifacts": source_artifacts or [],
            "output_artifacts": output_artifacts or [],
            "environment": environment or {}, "refs": refs or {}})

    def get_cost_event(self, cost_event_id: str) -> dict:
        return self._req("GET", f"/v2/cost-events/{cost_event_id}")

    def cost_report(self, wid) -> dict:
        """Vector totals for a world: additive quantities summed, peaks taken
        as maxima and never sums, unavailable entries counted and never
        summed."""
        return self._req("GET", f"/v2/worlds/{wid}/cost-report")

    # -- work queue --------------------------------------------------------
    def claim(self, worker_id: str, *, world_id: Optional[str] = None,
              lease_s: float = 30.0) -> Optional[dict]:
        return self._req("POST", "/v2/work/claim", {
            "worker_id": worker_id, "world_id": world_id,
            "lease_s": lease_s})["work"]

    def heartbeat(self, work_id: str, worker_id: str, claim_id: str,
                  lease_s: float = 30.0):
        return self._req("POST", f"/v2/work/{work_id}/heartbeat",
                         {"worker_id": worker_id, "claim_id": claim_id,
                          "lease_s": lease_s})

    def complete(self, work_id: str, worker_id: str, claim_id: str,
                 result: dict, *, attestation: Optional[dict] = None):
        """v6 -- ATTESTATION. The engine has always held the REQUESTED
        configuration (spec_hash, sealed at commit) and never the executed one,
        so a run that quietly used different parameters returned a result the
        ledger could not tell from a faithful one.

        Pass attestation={"executed_config": <the config you actually ran>} and
        the engine hashes it with the SAME canonicalization that produced
        spec_hash -- so a faithful executor matches by construction and needs
        to do nothing special. Send "executed_config_hash" instead if you will
        not disclose the config; never both. The other three optional fields
        are "entry_state_hash" (what state the player ENTERED the world
        holding), "player_identity_hash" (which build of the agent) and
        "measurement_identity_hash" (which scorer/regime)."""
        return self._req("POST", f"/v2/work/{work_id}/complete",
                         {"worker_id": worker_id, "claim_id": claim_id,
                          "result": result, "attestation": attestation})

    def audit_envelope(self, wid, exp_id: str) -> dict:
        """The whole sealed record of one experiment as a single hash-sealed
        object, for export to a third party who holds no SFE credential.

        A first-class method because consumers were reaching it through the
        private transport (`client._req`), which turns a path or response-shape
        change into a silent break rather than an API-boundary one."""
        return self._req(
            "GET", f"/v2/worlds/{wid}/experiments/{exp_id}/audit-envelope")

    def verify_anchor(self, world_id: str, event_id: str, entry_hash: str, *,
                      exp_id: Optional[str] = None,
                      obs_id: Optional[str] = None) -> dict:
        """Verify a causal anchor. CREDENTIAL-FREE and cross-engine by design:
        a third party can check an anchor it did not produce.

        ALWAYS pass exp_id/obs_id. Without them the call proves only that an
        event EXISTS, so a wrong-but-real event passes; with them the engine
        checks BINDING and rejects a mismatch."""
        return self._req("POST", "/v2/audit/verify-anchor", {
            "world_id": world_id, "event_id": event_id,
            "entry_hash": entry_hash, "exp_id": exp_id, "obs_id": obs_id})

    def attestation(self, work_id: str) -> dict:
        """What the executor said it ran, beside what the engine sealed."""
        return self._req("GET", f"/v2/work/{work_id}/attestation")

    # ---- v6 families: the first CROSS-WORLD scientific container -----------
    #
    # Every other scientific object carries a world_id, which is right for a
    # ledger and makes a campaign, an analysis family or a comparison
    # inexpressible -- they span worlds by definition. Without this, "the
    # survivor of twelve" and "the only one I ran" are the same record.

    def family(self, kind: str, manifest: Optional[dict] = None, *,
               name: Optional[str] = None) -> dict:
        """kind: campaign | analysis | comparison | selection.

        The manifest is freeform and sealed by hash at creation. One convention
        the engine reads: an integer `planned_members` is compared against what
        you actually record, so a declared extent that grew after the results
        came in becomes visible."""
        return self._req("POST", "/v2/families",
                         {"kind": kind, "manifest": manifest or {},
                          "name": name})

    def family_member(self, family_id: str, member_kind: str, member_id: str,
                      *, role: Optional[str] = None,
                      arm: Optional[str] = None) -> dict:
        """member_kind: experiment | analysis | world | claim.
        role: planned | executed | abandoned | selected | alternative.
        arm: the experimental arm, per the ARM RULING.

        THE ARM IS PART OF THE SEALED DESIGN, NOT OF THE EXECUTION SPEC. That
        is what lets two members in different arms carry a byte-identical
        execution spec and therefore an IDENTICAL spec_hash -- what was run and
        what role it played are different facts, and folding the label into the
        spec would make identical executions hash differently and destroy the
        comparison the design exists to support.

        Role AND arm are APPEND-ONLY: re-adding the same member with a
        different role or arm is a 409, while an identical re-add is an
        idempotent no-op. A member quietly moving from `alternative` to
        `selected`, or from arm A to arm B, after the results are in is the
        rewrite this record exists to prevent.

        If the family's manifest declares `arms`, an arm outside that sealed
        vocabulary is refused at membership (422)."""
        return self._req("POST", f"/v2/families/{family_id}/members",
                         {"member_kind": member_kind, "member_id": member_id,
                          "role": role, "arm": arm})

    def get_family(self, family_id: str) -> dict:
        """The family plus its provenance census, including
        `selection_visible` -- true only when BOTH a selected member and at
        least one alternative are recorded. A survivor with no recorded losers
        is not a lie, but it is not a visible selection either."""
        return self._req("GET", f"/v2/families/{family_id}")

    def list_families(self, *, kind: Optional[str] = None,
                      limit: int = 100) -> list:
        q = f"/v2/families?limit={limit}" + (f"&kind={kind}" if kind else "")
        return self._req("GET", q)["families"]

    def close_family(self, family_id: str) -> dict:
        """Seal membership. A CLOSED family accepts no further members."""
        return self._req("POST", f"/v2/families/{family_id}/close")

    # ---- v6 claims --------------------------------------------------------

    # ---- v7 measurements: identity, meaning, and where the value lives ----

    def register_measurement(self, name: str, version: str, *,
                             implementation_hash: str, domain: str,
                             value_path: Optional[str] = None,
                             direction: Optional[str] = None,
                             unit: Optional[str] = None,
                             range_min: Optional[float] = None,
                             range_max: Optional[float] = None,
                             params: Optional[dict] = None,
                             inputs: Optional[list] = None,
                             outputs: Optional[list] = None,
                             provenance: Optional[dict] = None,
                             validation_status: str = "UNVALIDATED") -> dict:
        """Register a measurement DEFINITION: what it is, WHERE its value lives
        and what a value MEANS.

        `observations.content` is freeform by design, so nothing otherwise says
        which field of it is the outcome. `value_path` is a dotted ADDRESS of
        plain keys ("result.score"), deliberately not a query language: letting
        a measurement SELECT its own value would make choosing which of several
        values counts an act of interpretation, which the engine declines.

        `direction` matters more than it looks -- without it "0.2 vs 0.4" is not
        even orderable, and an analyst that guesses the sign gets a confident
        answer with the wrong one.

        `(name, version)` is UNIQUE and never silently replaced: a changed
        oracle needs a new version, because two runs scored under one name by
        two definitions are not comparable and nothing downstream could tell.
        The returned `identity_hash` is derived from the definition -- put it in
        an executor attestation's `measurement_identity_hash` so the hash
        resolves to a registered oracle instead of being comparable only with
        itself."""
        return self._req("POST", "/v2/measurements", {
            "name": name, "version": version,
            "implementation_hash": implementation_hash, "domain": domain,
            "value_path": value_path, "direction": direction, "unit": unit,
            "range_min": range_min, "range_max": range_max,
            "params": params or {}, "inputs": inputs or [],
            "outputs": outputs or [], "provenance": provenance or {},
            "validation_status": validation_status})

    def measurements(self, *, name: Optional[str] = None,
                     domain: Optional[str] = None, limit: int = 100) -> list:
        q = f"/v2/measurements?limit={limit}"
        if name:
            q += f"&name={name}"
        if domain:
            q += f"&domain={domain}"
        return self._req("GET", q)["measurements"]

    def measurement(self, measurement_id: str) -> dict:
        """Accepts a measurement_id OR an identity_hash, so an executor holding
        only the hash it attested can resolve what it measured."""
        return self._req("GET", f"/v2/measurements/{measurement_id}")

    def measured_value(self, wid, obs_id: str, measurement_id: str) -> dict:
        """Resolve ONE observation's value along the declared path. A lookup:
        the engine computes nothing across observations and takes no view on
        what the number means. Owner-scoped -- for another seat's corpus use
        read_observations(measurement=...)."""
        return self._req(
            "GET",
            f"/v2/worlds/{wid}/observations/{obs_id}/measured/{measurement_id}")

    # ---- v7 cross-seat read contract --------------------------------------
    #
    # Every ordinary read route is owner-scoped, which is right and which makes
    # an ARCHAEOLOGIST impossible without this. A grant is READ ONLY, scoped to
    # a read scope, revocable, and it never widens the owner-scoped routes: the
    # cross-tenancy is in the /v2/read/* path so an ordinary read can never
    # quietly start returning another seat's rows.

    def create_read_scope(self, name: str, *,
                          note: Optional[str] = None) -> dict:
        """A curated set of YOUR OWN worlds, existing only to be granted for
        reading. Deliberately not a topology group: that field gates
        artifact-crossing, so granting over one would confer import
        eligibility as a side effect, and it would mean mutating worlds that
        already exist. A scope writes nothing on the world."""
        return self._req("POST", "/v2/read/scopes",
                         {"name": name, "note": note})

    def add_scope_worlds(self, scope_id: str, world_ids: list) -> dict:
        """Add worlds you OWN. Ids you do not own are reported in `not_yours`
        rather than raising -- the engine will not tell you whether they
        exist."""
        return self._req("POST", f"/v2/read/scopes/{scope_id}/worlds",
                         {"world_ids": list(world_ids)})

    def read_scopes(self) -> list:
        return self._req("GET", "/v2/read/scopes")["scopes"]

    def grant_read(self, scope_id: str, grantee_client_id: str, *,
                   note: Optional[str] = None) -> dict:
        """Only the scope's owner may grant, so a capability cannot be re-lent
        by whoever it reaches."""
        return self._req("POST", f"/v2/read/scopes/{scope_id}/grants",
                         {"grantee_client_id": grantee_client_id,
                          "note": note})

    def revoke_read(self, grant_id: str) -> dict:
        """Immediate. The row survives with `revoked_ts`: a grant that existed
        and was withdrawn is a different fact from one that never existed."""
        return self._req("POST", f"/v2/read/grants/{grant_id}/revoke")

    def read_grants(self) -> dict:
        """-> {granted_by_me: [...], granted_to_me: [...]}"""
        return self._req("GET", "/v2/read/grants")

    def read_worlds(self, *, scope: Optional[str] = None,
                    limit: int = 500) -> dict:
        """Worlds you do NOT own, in scopes you have been granted. Your own are
        excluded so you cannot lose track of which rows are your evidence and
        which are another seat's. An ungranted scope returns empty, never 403."""
        q = f"/v2/read/worlds?limit={limit}" + (f"&scope={scope}" if scope else "")
        return self._req("GET", q)

    def read_observations(self, *, scope: Optional[str] = None,
                          world_id: Optional[str] = None,
                          evidence_class: Optional[str] = None,
                          measurement: Optional[str] = None,
                          limit: int = 1000) -> dict:
        """Observations from granted scopes, WITH the corpus census beside
        them -- worlds, by_client, by_evidence_class, the filter applied and
        whether the page truncated. Record that census in every survey: it is
        the declared population your detectors ran over, and the commonest way
        to fail is to pool tenancies and evidence classes without noticing.

        Pass `measurement` (an id or identity_hash) to attach a resolved
        `measured` block per observation, so a reader never guesses which field
        is the outcome."""
        q = f"/v2/read/observations?limit={limit}"
        for k, v in (("scope", scope), ("world_id", world_id),
                     ("evidence_class", evidence_class),
                     ("measurement", measurement)):
            if v:
                q += f"&{k}={v}"
        return self._req("GET", q)

    def record_claim(self, estimand: str, status: str, *,
                     family_id: Optional[str] = None,
                     analysis_exp_id: Optional[str] = None,
                     relevance_floor: Optional[Any] = None,
                     replication: Optional[dict] = None,
                     transport_domain: Optional[Any] = None) -> dict:
        """The scientific assertion -- deliberately NOT a world record, because
        it cites an analysis, which cites observations, which live in worlds.

        status: SUPPORTED | SUCCESSFUL_NEGATIVE | INCONCLUSIVE.
        SUCCESSFUL_NEGATIVE exists because "the effect is bounded below a
        declared relevance floor" is a POSITIVE result that could otherwise
        only be stored as SURVIVED (ambiguous) or INCONCLUSIVE (which destroys
        the information that made it valuable). It REQUIRES relevance_floor:
        the claim is about the bound, so without the bound there is no claim.

        replication is COMPOSITIONAL, never an ordinal. Declare any of
        resampled_noise, new_world_draws, new_landscape, reimplemented,
        rebuilt_player, independent_team as booleans. An UNDECLARED dimension
        is not a False -- it was simply not asserted.

        transport_domain is checked for containment against the cited
        analysis's spec `tested_domain`, if it declares one. The engine asserts
        nothing about whether a result transports; it reports that you claimed
        it holds somewhere you never tested."""
        return self._req("POST", "/v2/claims", {
            "estimand": estimand, "status": status, "family_id": family_id,
            "analysis_exp_id": analysis_exp_id,
            "relevance_floor": relevance_floor, "replication": replication,
            "transport_domain": transport_domain})

    def get_claim(self, claim_id: str) -> dict:
        return self._req("GET", f"/v2/claims/{claim_id}")

    def list_claims(self, *, family_id: Optional[str] = None,
                    status: Optional[str] = None, limit: int = 100) -> list:
        q = f"/v2/claims?limit={limit}"
        if family_id:
            q += f"&family_id={family_id}"
        if status:
            q += f"&status={status}"
        return self._req("GET", q)["claims"]

    def retract_claim(self, claim_id: str, reason: str) -> dict:
        """RETRACTED is a transition, never an origin state, and the original
        content_hash is preserved: a claim made and withdrawn is a different
        fact from a claim that never existed."""
        return self._req("POST", f"/v2/claims/{claim_id}/retract",
                         {"reason": reason})

    def fail(self, work_id: str, worker_id: str, claim_id: str, error: str,
             retry: bool = True):
        return self._req("POST", f"/v2/work/{work_id}/fail",
                         {"worker_id": worker_id, "claim_id": claim_id,
                          "error": error, "retry": retry})


class RemoteWorker:
    """A disposable execution worker that runs on ANY machine. It claims work
    over REST, runs a local `executor(kind, payload) -> dict`, heartbeats its
    lease, and commits the result. Kill it mid-lease and the Engine reclaims the
    work for another worker."""

    def __init__(self, client: EngineClient, worker_id: str,
                 executor: Callable[[str, dict], dict], *, lease_s: float = 30.0):
        self.c = client
        self.worker_id = worker_id
        self.executor = executor
        self.lease_s = lease_s

    def run_once(self, world_id: Optional[str] = None) -> bool:
        claim = self.c.claim(self.worker_id, world_id=world_id,
                             lease_s=self.lease_s)
        if claim is None:
            return False
        wid = claim["work_id"]
        # H1: the server-issued fencing token for THIS attempt; every follow-up
        # call must present it, so a stale (reclaimed) attempt cannot act.
        claim_id = claim["claim_id"]
        try:
            result = self.executor(claim["kind"], claim["payload"])
            self.c.complete(wid, self.worker_id, claim_id, result)
        except Exception as e:                       # noqa: BLE001
            self.c.fail(wid, self.worker_id, claim_id, f"executor error: {e}")
        return True

    def run(self, world_id: Optional[str] = None, *, poll_s: float = 0.2,
            max_idle_polls: int = 0) -> int:
        """Process work until idle. max_idle_polls=0 means stop as soon as no
        work is available; a positive value keeps polling that many empty
        cycles (a long-lived worker)."""
        n, idle = 0, 0
        while True:
            if self.run_once(world_id):
                n += 1
                idle = 0
            else:
                idle += 1
                if idle > max_idle_polls:
                    return n
                time.sleep(poll_s)
