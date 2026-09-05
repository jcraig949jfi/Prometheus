#!/usr/bin/env python3
"""HARMONIA ARENA V0 -- the ONE shared SFE<->Proteus<->PEW orchestration path.

Round 2 of the M2 qualification, section 4A. This exists so that identity,
anchor selection, attestation, fossil writing and readback are implemented
EXACTLY ONCE. Bespoke per-experiment scripts are how two runs end up meaning
different things while looking the same.

    arena.run(specimen, world_config, action_plan) -> EncounterResult

Hard gates, in order. Any one of them aborts before a world exists, because a
world created against the wrong service is evidence about the wrong service:

    G1  SFE deployment attestation      live source_commit / schema / routes
    G2  PEW server-attested identity    db_system_id must equal the expected M2
    G3  specimen content identity       SFE-computed blob_hash == organism_id
    G4  interpretation identity         runtime_hash + affordance_hash present
    G5  exact causal anchor             event_id + entry_hash from the WRITE
    G6  PEW round-trip                  what was written is what reads back

G2 exists because `pew_battery.py` does not perform it: its identity gates read
/health, /schema and /fossil/contract, which are byte-identical on M1 and M2.
This module therefore does not delegate machine identity to that battery.

CAUSAL_SELECTION_SAFE and CAUSAL_INDEPENDENTLY_VERIFIED are NOT the same
property and this module never collapses them. The anchor is taken directly
from the SFE write response, so selection is safe; nothing here verifies that
anchor against SFE from PEW's side, so every fossil is written with
sfe_anchor_verified=false until a real verification mechanism lands.
"""
from __future__ import annotations

import base64
import hashlib
import json
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request

SFE_BASE = "https://192.168.1.191:8811/v2"
SFE_CA = "D:/Prometheus/SerendipityFoundry/SerendipityFoundryEngine/deploy/m2.crt"
PEW_BASE = "http://192.168.1.191:8377/api/v1"
PEW_CONFIG = "D:/Prometheus/evidence_wiki/config.json"

EXPECTED_M2_DB_SYSTEM_ID = "7681719240261676752"
REQUIRED_COMMIT = "67c28acee"
REQUIRED_SCHEMA = 4


class ArenaError(RuntimeError):
    """A hard gate refused. Never caught internally -- the run does not continue."""


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def organism_id(manifest) -> str:
    return hashlib.sha256(canonical(manifest)).hexdigest()


# --------------------------------------------------------------------- clients
class SFE:
    def __init__(self, token=None, name="harmonia-arena"):
        self.ctx = ssl.create_default_context(cafile=SFE_CA)
        self.token = token
        if token is None:
            self.client_id, self.token = self._register(name)
        else:
            self.client_id = None

    def _register(self, name):
        s, b = self.call("POST", "/clients", {"name": name}, auth=False)
        if s != 200:
            raise ArenaError("SFE client registration failed: %s %s" % (s, b))
        return b["client_id"], b["token"]

    def call(self, method, path, body=None, hdrs=None, auth=True):
        data = canonical(body) if body is not None else None
        req = urllib.request.Request(SFE_BASE + path, data=data, method=method)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        if auth and self.token:
            req.add_header("Authorization", "Bearer " + self.token)
        for k, v in (hdrs or {}).items():
            req.add_header(k, v)
        try:
            r = urllib.request.urlopen(req, context=self.ctx, timeout=60)
            return r.status, json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf8", "replace")


class PEW:
    def __init__(self, machine="M2", agent="harmonia"):
        cfg = json.loads(open(PEW_CONFIG, encoding="utf-8").read())
        try:
            cfg.update(json.loads(open(PEW_CONFIG.replace("config.json", "config.local.json"),
                                       encoding="utf-8").read()))
        except OSError:
            pass
        self.token = (cfg.get("machine_tokens") or {}).get(machine) or cfg["auth_token"]
        self.machine, self.agent = machine, agent

    def call(self, method, path, body=None, auth=True):
        data = canonical(body) if body is not None else None
        req = urllib.request.Request(PEW_BASE + path, data=data, method=method)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        if auth:
            req.add_header("Authorization", "Bearer " + self.token)
        req.add_header("X-Prometheus-Machine", self.machine)
        req.add_header("X-Prometheus-Agent", self.agent)
        try:
            r = urllib.request.urlopen(req, timeout=60)
            return r.status, json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf8", "replace")


# ----------------------------------------------------------------------- gates
def gate_sfe_deployment(sfe: SFE) -> dict:
    """G1. The live daemon, not the source tree."""
    s, v = sfe.call("GET", "/version", auth=False)
    if s != 200:
        raise ArenaError("G1 SFE unreachable: %s %s" % (s, v))
    commit, schema = v.get("source_commit"), v.get("schema_version")
    if not commit:
        raise ArenaError("G1 live build is UNIDENTIFIABLE (source_commit is null)")
    try:
        subprocess.run(["git", "merge-base", "--is-ancestor", REQUIRED_COMMIT, commit],
                       cwd="D:/Prometheus", check=True, capture_output=True)
    except subprocess.CalledProcessError:
        raise ArenaError("G1 T20 deploy lag: live build %s does not contain %s"
                         % (commit[:12], REQUIRED_COMMIT))
    if schema != REQUIRED_SCHEMA:
        raise ArenaError("G1 schema_version live=%s required=%s" % (schema, REQUIRED_SCHEMA))
    s, api = sfe.call("GET", "/openapi.json", auth=False)
    for route, meth in [("/v2/worlds/{wid}/observations", "get"),
                        ("/v2/worlds/{wid}/experiments/{eid}", "get")]:
        if meth not in (api.get("paths", {}).get(route) or {}):
            raise ArenaError("G1 required route not served: %s %s" % (meth.upper(), route))
    return {"gate": "G1_sfe_deployment", "status": "PASS", "source_commit": commit,
            "engine_source_hash": v.get("engine_source_hash"), "schema_version": schema}


def gate_pew_identity(pew: PEW) -> dict:
    """G2. Server-attested machine identity. The battery does not do this."""
    s, i = pew.call("GET", "/identity", auth=False)
    if s != 200:
        raise ArenaError("G2 PEW /identity unavailable (%s) -- an older PEW build 404s this "
                         "route, which is itself evidence you are not on M2" % s)
    got = i.get("db_system_id")
    if got != EXPECTED_M2_DB_SYSTEM_ID:
        raise ArenaError("G2 WRONG MACHINE: db_system_id=%s expected=%s"
                         % (got, EXPECTED_M2_DB_SYSTEM_ID))
    return {"gate": "G2_pew_identity", "status": "PASS", **i}


# ------------------------------------------------------------------- the path
def run(specimen, world_config, action_plan, sfe=None, pew=None, session_id=None):
    """One encounter, end to end. `specimen` is a Proteus composition document."""
    t0 = time.time()
    sfe = sfe or SFE()
    pew = pew or PEW()
    rec = {"arena_version": "harmonia.arena.v0", "gates": [], "started_ts": t0}

    rec["gates"].append(gate_sfe_deployment(sfe))
    rec["gates"].append(gate_pew_identity(pew))

    # -- specimen canonicalization and identity ------------------------------
    manifest = specimen["manifest"]
    oid = organism_id(manifest)
    ident = {
        "organism_id": oid,
        "composition_id": specimen.get("composition_id"),
        "glue": specimen.get("glue"),
        "components": specimen.get("components"),
        "ablated": specimen.get("ablated"),
        "runtime_hash": specimen["identity"]["runtime_hash"],
        "affordance_hash": specimen["identity"]["affordance_hash"],
        "grammar_hash": specimen["identity"].get("grammar_hash"),
        "registry_entry_id": specimen.get("registry_entry_id"),
        "registry_organism_ids": specimen.get("registry_organism_ids")}
    if not (ident["runtime_hash"] and ident["affordance_hash"]):
        raise ArenaError("G4 interpretation identity incomplete: organism bytes without a "
                         "runtime_hash cannot be replayed, only re-guessed")
    rec["specimen"] = ident

    if session_id is None:
        s, se = sfe.call("POST", "/sessions", {"name": "harmonia-arena"})
        session_id = se["session_id"]
    rec["session_id"] = session_id

    # -- world, idempotent, attestation-required -----------------------------
    wcfg = dict(world_config, session_id=session_id)
    idem = "arena:" + hashlib.sha256(canonical([oid, wcfg, action_plan])).hexdigest()[:24]
    s, w = sfe.call("POST", "/worlds", wcfg, hdrs={"Idempotency-Key": idem})
    if s != 200:
        raise ArenaError("world create failed: %s %s" % (s, w))
    wid = w["world_id"]
    rec["world"] = {"world_id": wid, "idempotency_key": idem,
                    "require_attestation": w.get("require_attestation"),
                    "seed_root": w.get("seed_root")}
    sfe.call("POST", "/worlds/%s/start" % wid, {})

    # -- specimen bytes cross the boundary; SFE recomputes the digest --------
    s, art = sfe.call("POST", "/worlds/%s/artifacts" % wid,
                      {"kind": "blob", "data_b64": base64.b64encode(canonical(manifest)).decode(),
                       "meta": {"role": "specimen_manifest", "composition_id": ident["composition_id"]},
                       "expected_blob_hash": "sha256:" + oid})
    if s != 200:
        raise ArenaError("G3 specimen did not cross intact: %s %s" % (s, art))
    if art["blob_hash"] != "sha256:" + oid:
        raise ArenaError("G3 content identity mismatch: %s vs %s" % (art["blob_hash"], oid))
    rec["specimen_artifact"] = art

    # -- experiment, committed and enqueued in ONE call ----------------------
    spec = {"specimen": ident, "action_plan": action_plan, "world_config": world_config}
    s, ex = sfe.call("POST", "/worlds/%s/experiments" % wid,
                     {"spec": spec, "commit": True, "enqueue": True})
    if s != 200:
        raise ArenaError("experiment create failed: %s %s" % (s, ex))
    eid, work_id = ex["exp_id"], ex.get("work_id")
    rec["experiment"] = {"exp_id": eid, "work_id": work_id,
                         "committed_seq": ex.get("committed_seq")}

    # -- claim, execute, complete -------------------------------------------
    s, cl = sfe.call("POST", "/work/claim", {"worker_id": action_plan["worker_id"],
                                             "world_id": wid})
    item = (cl or {}).get("work") if isinstance(cl, dict) else None
    if not item:
        raise ArenaError("work claim returned no item (200 with work=null means NOTHING "
                         "CLAIMABLE, not claimed): %s %s" % (s, cl))
    claim_id = item["claim_id"]

    outcome = execute(manifest, action_plan)
    rec["execution"] = outcome

    s, done = sfe.call("POST", "/work/%s/complete" % work_id,
                       {"worker_id": action_plan["worker_id"], "claim_id": claim_id,
                        "result": {"transcript_hash": outcome["transcript_hash"],
                                   "meter": outcome["meter"],
                                   "statuses": outcome["statuses"]}})
    if s != 200:
        raise ArenaError("work complete failed: %s %s" % (s, done))
    rec["work_result_hash"] = done.get("result_hash")

    # -- observation; the anchor comes from THIS response, not from a search --
    s, obs = sfe.call("POST", "/worlds/%s/observations" % wid,
                      {"exp_id": eid, "work_id": work_id, "outcome": "SURVIVED",
                       "content": {"transcript_hash": outcome["transcript_hash"],
                                   "meter": outcome["meter"]}})
    if s != 200:
        raise ArenaError("observation write failed: %s %s" % (s, obs))
    if not (obs.get("event_id") and obs.get("entry_hash")):
        raise ArenaError("G5 SFE did not return an exact causal anchor; a ledger search "
                         "heuristic is NOT an acceptable substitute")
    rec["anchor"] = {"event_id": obs["event_id"], "entry_hash": obs["entry_hash"],
                     "event_seq": obs.get("event_seq"),
                     "evidence_class": obs.get("evidence_class"),
                     "evidence_role": obs.get("evidence_role"),
                     "obs_id": obs.get("obs_id")}
    if obs.get("evidence_class") != "ENGINE_WORK_RESULT":
        raise ArenaError("expected engine-attested evidence, got %s" % obs.get("evidence_class"))

    # -- PEW fossil ----------------------------------------------------------
    enc = "ARENA-%s" % eid
    run_id = "%s:%s" % (eid, work_id)
    fossil = {
        "encounter_id": enc, "run_id": run_id,
        "world_id": wid, "sfe_world_id": wid,
        "players": [oid],
        "sfe_event_id": obs["event_id"], "sfe_entry_hash": obs["entry_hash"],
        "sfe_event_seq": obs.get("event_seq"),
        "seed": str(world_config.get("seed_root")),
        "outcome": "SURVIVED",
        "resources_used": outcome["meter"],
        "occurred_ts": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
        "producer": {"component": "harmonia.arena.v0", "version": "0"},
        "namespace": action_plan.get("namespace", "test")}
    s, fw = pew.call("POST", "/fossil/encounters", fossil)
    if s != 200:
        raise ArenaError("PEW fossil write failed: %s %s" % (s, fw))
    rec["pew_write"] = fw

    # -- G6 readbacks --------------------------------------------------------
    s, back = pew.call("GET", "/fossil/encounters/%s" % enc)
    if s != 200:
        raise ArenaError("G6 PEW readback failed: %s %s" % (s, back))
    row = [r for r in back["runs"] if r["run_id"] == run_id]
    if not row:
        raise ArenaError("G6 PEW readback did not contain the run we just wrote")
    row = row[0]
    if row["sfe_entry_hash"] != obs["entry_hash"] or row["sfe_event_id"] != obs["event_id"]:
        raise ArenaError("G6 anchor did not survive the round trip")
    rec["pew_readback"] = row
    rec["sfe_anchor_verified"] = row.get("attestation", {}).get("sfe_anchor_verified")

    s, exb = sfe.call("GET", "/worlds/%s/experiments/%s" % (wid, eid))
    rec["sfe_readback"] = {"status": s, "spec_hash": exb.get("spec_hash"),
                           "spec_equals_submitted": exb.get("spec") == spec,
                           "state": exb.get("state")}
    s, obl = sfe.call("GET", "/worlds/%s/observations" % wid)
    rec["sfe_observations"] = {"status": s,
                               "n": len(obl.get("observations", [])) if isinstance(obl, dict) else None}

    rec["elapsed_s"] = round(time.time() - t0, 3)
    return rec


def execute(manifest, action_plan):
    """Run the player. Deterministic: same manifest + seed + inputs => same everything."""
    from proteus.foundry.vm import Player, Meter
    from proteus.foundry.prng import SplitMix64

    p = Player(manifest)
    st = p.fresh_state()
    rng = SplitMix64(action_plan["seed"])
    m = Meter()
    transcript, statuses = [], []
    for tick in range(action_plan["ticks"]):
        outs, status = p.run_tick(st, action_plan["inputs"], action_plan["n_out"], rng, meter=m)
        transcript.append(outs)
        statuses.append(status)
        if status == "halt":
            break
    meter = m.as_dict(manifest)
    for k in ("wall_s", "cpu_s"):        # timings are not deterministic; excluded by design
        meter.pop(k, None)
    return {"transcript": transcript, "statuses": statuses,
            "transcript_hash": hashlib.sha256(canonical(transcript)).hexdigest(),
            "meter": meter, "meter_hash": hashlib.sha256(canonical(meter)).hexdigest(),
            "ticks_run": len(statuses)}


if __name__ == "__main__":
    sfe, pew = SFE(), PEW()
    for g in (gate_sfe_deployment(sfe), gate_pew_identity(pew)):
        print(json.dumps(g, indent=1))
    print("both hard gates PASS")
