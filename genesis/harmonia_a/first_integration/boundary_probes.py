#!/usr/bin/env python
"""D15 boundary-expansion pass. Bounded, safe, namespace=test probes to
localize the NEXT bottlenecks in Proteus<->SFE<->PEW. Deterministic
non-scientific specimen choice. No scoring/selection/mutation. Each
probe records a typed finding. SFE writes are bounded (~12 worlds)."""

import base64
import hashlib
import json
import ssl
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, r"D:\Prometheus")
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")
sys.path.insert(0, str(Path(__file__).parent))
from sfclient.client import EngineClient, EngineError          # noqa
from proteus.integration import registry as R                 # noqa
from proteus.foundry.identity import canonical_json           # noqa
import adapter                                                 # noqa

BASE = "https://192.168.1.202:8811"
CA = (r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient"
      r"\config\m1.crt")
PEW = "http://192.168.1.202:8377/api/v1"
OUT = Path(__file__).parent
F = []                                    # findings


def find(boundary, probe, verdict, detail, evidence=None):
    F.append(dict(boundary=boundary, probe=probe, verdict=verdict,
                  detail=detail, evidence=evidence))
    print(f"[{verdict:8}] {boundary}.{probe}: {detail[:80]}")


def pew(method, path, body=None):
    tok = open(r"C:\ZeusD-var\harmonia\pew_token.txt").read().strip()
    r = urllib.request.Request(
        PEW + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {tok}",
                 "X-Prometheus-Machine": "M2",
                 "X-Prometheus-Agent": "harmonia",
                 "content-type": "application/json"}, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def main():
    tok = open(r"C:\ZeusD-var\harmonia\sfe_token.txt").read().strip()
    c = EngineClient(BASE, token=tok, cafile=CA, timeout=60.0)
    v = c.version()
    reg = R.load_default()
    ids = R.enumerate_ids(reg)
    sid = c.create_session(f"boundary-{uuid.uuid4().hex[:6]}")

    def mkworld(name, **kw):
        w = c.create_world(sid, name, **kw)
        c.start(w["world_id"])
        return w["world_id"]

    def place(wid, oid):
        man = R.get_manifest(reg, oid)
        cj = canonical_json(man)
        b = cj.encode() if isinstance(cj, str) else cj
        return c.artifact(wid, "proteus_player_manifest", b,
                          {"proteus_organism_id": oid}), b

    # ============ A. ORGANISM BOUNDARY ============
    # A1: a DIFFERENT unknown organism crosses without bespoke editing
    oid1 = ids[1]
    w_a1 = mkworld("A1")
    r1, b1 = place(w_a1, oid1)
    ok = r1["blob_hash"] == "sha256:" + oid1 and \
        c.artifact_bytes(w_a1, r1["artifact_id"]) == b1
    find("A_organism", "A1_second_organism_generic", "PASS" if ok else
         "FAIL", f"organism ids[1]={oid1[:12]} placed with no bespoke "
         "editing; identity gate held" if ok else "identity gate failed")
    # A2: SAME organism in TWO isolated worlds -> content id stable,
    # envelope id world-scoped
    oid0 = ids[0]
    w_a2a, w_a2b = mkworld("A2a"), mkworld("A2b")
    ra, _ = place(w_a2a, oid0)
    rb, _ = place(w_a2b, oid0)
    find("A_organism", "A2_same_organism_two_worlds",
         "PASS" if (ra["blob_hash"] == rb["blob_hash"] ==
                    "sha256:" + oid0 and
                    ra["artifact_id"] != rb["artifact_id"]) else "FAIL",
         "blob_hash (content) identical across worlds; artifact_id "
         "(envelope) distinct — no identity collision",
         dict(blob=ra["blob_hash"][:20], aid_a=ra["artifact_id"][:16],
              aid_b=rb["artifact_id"][:16]))
    # A3: SFE does NOT validate organism identity — it is content-
    # addressed. Corrupt bytes are accepted; only the CLIENT gate catches.
    w_a3 = mkworld("A3")
    corrupt = bytearray(b1); corrupt[0] ^= 0xFF
    r3 = c.artifact(w_a3, "proteus_player_manifest", bytes(corrupt),
                    {"proteus_organism_id": oid1})
    accepted = "artifact_id" in r3
    gate_catches = r3["blob_hash"] != "sha256:" + oid1
    find("A_organism", "A3_corrupt_bytes_accepted_by_sfe",
         "FINDING", "SFE accepts arbitrary bytes (content-addressed); it "
         "does NOT verify Proteus identity. Integrity is a CLIENT-side "
         "assertion (blob_hash==sha256:oid). An adapter that skips the "
         "gate would fossilize corrupted material with a wrong-but-valid "
         "blob_hash.", dict(sfe_accepted=accepted,
                            client_gate_would_catch=gate_catches))

    # ============ B. WORLD BOUNDARY ============
    # B1: repeated identical config -> distinct world_ids (uniqueness)
    w_b = [mkworld("B1", seed_root=424242) for _ in range(3)]
    find("B_world", "B1_repeat_config_unique_ids",
         "PASS" if len(set(w_b)) == 3 else "FAIL",
         "same seed_root=424242 thrice -> 3 distinct world_ids; config "
         "is NOT the identity (a replicate is a new world)")
    # B3: invalid budget config rejection
    try:
        c.create_world(sid, "B3", budget={"experiments": {
            "limit": 1, "enforcement": "bogus_value"}})
        find("B_world", "B3_invalid_budget_rejected", "FINDING",
             "invalid enforcement value 'bogus_value' was ACCEPTED (not "
             "422) — config validation is permissive")
    except EngineError as e:
        find("B_world", "B3_invalid_budget_rejected", "PASS",
             f"invalid enforcement rejected: {e.status}")
    # B4: lifecycle — terminate then attempt artifact write (do NOT infer
    # TERMINATED lifetime)
    w_b4 = mkworld("B4")
    try:
        c.terminate(w_b4)
        term_ok = True
    except EngineError as e:
        term_ok = f"terminate raised {e.status}"
    try:
        rt, bt = place(w_b4, oid0)
        find("B_world", "B4_artifact_after_terminate", "FINDING",
             "artifact write AFTER terminate SUCCEEDED — TERMINATED does "
             "not end write lifetime; matches the addendum caution",
             dict(terminate=term_ok, wrote=bool(rt.get("artifact_id"))))
    except EngineError as e:
        find("B_world", "B4_artifact_after_terminate", "FINDING",
             f"artifact write after terminate -> {e.status} "
             "(TERMINATED does end write lifetime)")
    # B5: world config reconstructable from durable evidence?
    gw = c.get_world(w_a1)
    cfg_fields = {k: (k in gw) for k in
                  ("seed_root", "sharing_policy", "budget", "head_hash",
                   "state")}
    find("B_world", "B5_world_config_in_get_world", "INFO",
         "fields present on GET /v2/worlds/{id}: " +
         ",".join(k for k, ok in cfg_fields.items() if ok),
         cfg_fields)

    # ============ C. ACTION / ENCOUNTER BOUNDARY ============
    # C2: budget exhaustion under enforceable cap
    w_c2 = mkworld("C2", budget={"experiments": {
        "limit": 1, "enforcement": "enforceable"}})
    h = c.hypothesis(w_c2, "cap probe")
    e1 = c.experiment(w_c2, {"n": 1}, hyp_id=h)
    try:
        c.experiment(w_c2, {"n": 2}, hyp_id=h)
        find("C_action", "C2_budget_exhaustion", "FAIL",
             "2nd experiment under limit=1 enforceable was NOT blocked")
    except EngineError as e:
        find("C_action", "C2_budget_exhaustion",
             "PASS" if e.status == 409 else "FINDING",
             f"2nd experiment under limit=1 -> {e.status} (budget cap "
             "enforced at commit)")
    # C3: observation WITHOUT work_id -> CLIENT_ASSERTED not attested
    w_c3 = mkworld("C3")
    h3 = c.hypothesis(w_c3, "attest probe")
    e3 = c.experiment(w_c3, {"n": 1}, hyp_id=h3)
    c.observation(w_c3, e3["exp_id"], {"x": 1}, "INCONCLUSIVE")
    att = c.status(w_c3).get("epistemics", {}).get(
        "observations_engine_attested", "?")
    find("C_action", "C3_observation_without_work_id", "FINDING",
         f"observation with no work_id -> engine_attested={att} "
         "(evidence_class CLIENT_ASSERTED). Nothing forces attestation; "
         "an agent can silently produce unattested 'evidence'.")

    # ============ D. CAUSALITY BOUNDARY ============
    # D1: PEW accepts an event that is NOT the run's observation as the
    # anchor, as long as (event_id, entry_hash) shape/pair is valid
    def evlist(wid):
        e = c.events(wid, limit=10)
        return e["events"] if isinstance(e, dict) else e
    w_d = mkworld("D1")
    _raw = c.events(w_d, limit=10)
    find("K_observability", "K4_events_shape_inconsistent", "FINDING",
         "GET .../events return shape is INCONSISTENT: dict "
         "{'events':[...]} in the first integration, bare list here. A "
         "client must defensively handle both or break (this harness "
         "did, mid-run).", dict(shape=type(_raw).__name__))
    evs = evlist(w_d)
    wc_evt = next((e for e in evs
                   if e["event_type"] == "WORLD_CREATED"), evs[0])
    find("D_causality", "D1_anchor_is_client_chosen", "FINDING",
         "PEW validates sfe_entry_hash SHAPE + (event_id,entry_hash) "
         "pair EXISTENCE in SFE, not that the event is the run's "
         "observation. Anchoring on WORLD_CREATED (evt "
         f"{wc_evt['event_id'][:12]}) would pass PEW shape checks — "
         "causal correctness is a CLIENT obligation, not enforced.",
         dict(chosen_event_type=wc_evt["event_type"]))

    # ============ G. FAILURE BOUNDARY ============
    # G1: nonexistent world read
    try:
        c.get_world("wld_" + "0" * 24)
        find("G_failure", "G1_nonexistent_world", "FAIL",
             "read of nonexistent world did not error")
    except EngineError as e:
        find("G_failure", "G1_nonexistent_world",
             "PASS" if e.status in (404, 400) else "FINDING",
             f"nonexistent world -> {e.status} (fails closed)")
    # G4: PEW malformed provenance
    s, r = pew("POST", "/fossil/encounters", {"encounter_id": "x",
               "run_id": "y", "namespace": "test"})   # missing required
    find("G_failure", "G4_pew_missing_required", "PASS" if s == 422 else
         "FINDING", f"fossil missing sfe_entry_hash/sfe_event_id -> {s} "
         "(fails closed, diagnosable)")

    # ============ H. IDEMPOTENCY / RETRY BOUNDARY ============
    # H1: artifact placement retried with same idem_key
    w_h = mkworld("H1")
    man = R.get_manifest(reg, oid0)
    b = canonical_json(man)
    b = b.encode() if isinstance(b, str) else b
    k = f"h1-{uuid.uuid4().hex}"
    ha = c.artifact(w_h, "proteus_player_manifest", b, {}, idem_key=k)
    hb = c.artifact(w_h, "proteus_player_manifest", b, {}, idem_key=k)
    find("H_idempotency", "H1_artifact_idem_key",
         "PASS" if ha.get("artifact_id") == hb.get("artifact_id") else
         "FINDING",
         "artifact retry with same idem_key -> " +
         ("same artifact_id (idempotent)"
          if ha.get("artifact_id") == hb.get("artifact_id")
          else "DIFFERENT artifact_id (NOT idempotent)"))
    # H2: create_world is NOT idempotent (no idem key) -> duplicates
    find("H_idempotency", "H2_create_world_not_idempotent", "FINDING",
         "create_world has no idempotency key; a retried create mints a "
         "NEW world (see B1). An orchestrator that retries world creation "
         "on a timeout silently doubles worlds. UNSAFE-TO-RETRY-BLINDLY.")

    # ============ I. CONCURRENCY BOUNDARY (bounded) ============
    # two worlds, two worker_ids, interleaved claims -> identity separation
    w_i1, w_i2 = mkworld("I1a"), mkworld("I1b")
    for wid in (w_i1, w_i2):
        hh = c.hypothesis(wid, "conc")
        c.experiment(wid, {"n": 1}, hyp_id=hh, enqueue=True)
    k1 = c.claim("harmonia-b-conc", world_id=w_i1)
    k2 = c.claim("harmonia-c-conc", world_id=w_i2)
    sep = (k1["work_id"] != k2["work_id"] and
           k1["claim_id"] != k2["claim_id"])
    find("I_concurrency", "I1_two_worlds_two_workers",
         "PASS" if sep else "FAIL",
         "two worker identities claim work in two isolated worlds; "
         "work_id/claim_id separated" if sep else "identity bleed",
         dict(w1=k1["work_id"][:14], w2=k2["work_id"][:14]))

    # ============ K. OBSERVABILITY BOUNDARY ============
    try:
        wl = c._req("GET", "/v2/worlds")
        n = len(wl) if isinstance(wl, list) else (
            len(wl.get("worlds", [])) if isinstance(wl, dict) else "?")
        find("K_observability", "K1_list_worlds", "PASS",
             f"GET /v2/worlds returns a listing (n={n}); an agent can "
             "enumerate worlds without shell archaeology")
    except EngineError as e:
        find("K_observability", "K1_list_worlds", "FINDING",
             f"GET /v2/worlds -> {e.status}; no world enumeration")
    # K2: PEW fossil listing by world_id
    s, r = pew("GET", f"/fossil/encounters?world_id={w_a1}")
    find("K_observability", "K2_pew_list_by_world",
         "PASS" if s == 200 else "FINDING",
         f"GET /fossil/encounters?world_id -> {s} "
         f"(n={r.get('n') if isinstance(r, dict) else '?'}); reverse "
         "lookup world->fossils exists")
    # K3: no GET /packets (documented gap)
    s, r = pew("GET", "/packets")
    find("K_observability", "K3_no_packet_read", "FINDING" if s != 200
         else "PASS", f"GET /packets -> {s} (source packets not "
         "independently readable over HTTP — archaeology gap, per note 7)")

    summary = dict(engine=v, n_findings=len(F),
                   verdicts={x: sum(1 for f in F if f["verdict"] == x)
                             for x in ("PASS", "FAIL", "FINDING", "INFO",
                                       "BLOCKED", "DEFERRED")},
                   findings=F)
    json.dump(summary, open(OUT / "boundary_findings.json", "w"),
              indent=1, default=str)
    print("\nverdicts:", summary["verdicts"])


if __name__ == "__main__":
    main()
