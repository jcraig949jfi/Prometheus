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
                 timeout: float = 30.0, session_key: Optional[str] = None):
        self._u = urllib.parse.urlsplit(base_url.rstrip("/"))
        if self._u.scheme not in ("http", "https"):
            raise ValueError("base_url must be http(s)")
        self.token = token
        self.timeout = timeout
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
        """Register a client and adopt its token. Returns the token."""
        r = self._req("POST", "/v2/clients", {"name": name})
        self.token = r["token"]
        return self.token

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

    def artifact(self, wid, kind: str, data: bytes, meta: Optional[dict] = None,
                 *, idem_key: Optional[str] = None):
        import base64
        return self._req("POST", f"/v2/worlds/{wid}/artifacts", {
            "kind": kind, "data_b64": base64.b64encode(data).decode(),
            "meta": meta or {}}, idem_key=idem_key)

    def artifact_content(self, wid, artifact_id: str) -> dict:
        """F1: retrieve an artifact's CONTENT + provenance, iff it is
        epistemically visible to this world (native here or legally imported
        here). Returns content_b64 (bytes hash to source_hash) + provenance."""
        return self._req(
            "GET", f"/v2/worlds/{wid}/artifacts/{artifact_id}/content")

    def artifact_bytes(self, wid, artifact_id: str) -> bytes:
        """Convenience: the decoded content bytes for a visible artifact."""
        import base64
        return base64.b64decode(self.artifact_content(wid, artifact_id)[
            "content_b64"])

    def knowledge_set(self, wid, seq: Optional[int] = None) -> dict:
        """F10: the information-availability frontier of this world at/<= seq
        (global event_seq; omit for now). Answers only 'could world W legally
        know X by seq N' -- not read, not used, not causal."""
        q = f"?seq={seq}" if seq is not None else ""
        return self._req("GET", f"/v2/worlds/{wid}/knowledge{q}")

    def import_artifact(self, wid, source_world: str, source_artifact: str):
        return self._req("POST", f"/v2/worlds/{wid}/import", {
            "source_world": source_world, "source_artifact": source_artifact})

    def consume_budget(self, wid, resource: str, amount: float) -> dict:
        return self._req("POST", f"/v2/worlds/{wid}/budget/consume",
                         {"resource": resource, "amount": amount})

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
                      *, role: Optional[str] = None) -> dict:
        """member_kind: experiment | analysis | world | claim.
        role: planned | executed | abandoned | selected | alternative.

        Roles are APPEND-ONLY: re-adding the same member under a different role
        is a 409. A member quietly moving from `alternative` to `selected`
        after the fact is the rewrite this table exists to prevent."""
        return self._req("POST", f"/v2/families/{family_id}/members",
                         {"member_kind": member_kind, "member_id": member_id,
                          "role": role})

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
