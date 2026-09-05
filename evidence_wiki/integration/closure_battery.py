"""PEW closure V0 battery (Mnemosyne, 2026-09-04). Gates C0-C9.

Proves the closure lane end to end against a LIVE service, every write checked
by an independent read-back. Namespace 'test' throughout (excluded from every
scientific query). Exit 0 = all_pass.

    python integration/closure_battery.py --host 127.0.0.1 --port 8378 \
        --machine M2 --agent closure-test
"""
import argparse
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
import uuid

import requests

_DEFAULT_CA = "D:/prometheus/SerendipityFoundry/SerendipityFoundryEngine/deploy/m2.crt"
_DEFAULT_SFE = "https://192.168.1.191:8811/v2"


def sfe_sealed_run(sfe_url, ca):
    """Create a genuine sealed SFE run over HTTP (own client, no key-file read)
    and return the real anchor tuple + the WORLD_CREATED event for the wrong-
    but-real control. Returns None if SFE is unreachable."""
    ctx = ssl.create_default_context(cafile=ca)
    tok = {"t": None}

    def req(m, p, body=None):
        d = json.dumps(body).encode() if body is not None else None
        h = {"content-type": "application/json"}
        if tok["t"]:
            h["authorization"] = "Bearer " + tok["t"]
        r = urllib.request.Request(sfe_url.rstrip("/") + p, data=d, headers=h, method=m)
        with urllib.request.urlopen(r, context=ctx, timeout=20) as z:
            return json.loads(z.read().decode() or "{}")
    try:
        tag = "pewC4-%d" % int(time.time())
        tok["t"] = req("POST", "/clients", {"name": tag})["token"]
        sid = req("POST", "/sessions", {"name": tag})["session_id"]
        w = req("POST", "/worlds", {"session_id": sid, "name": "c4",
                "seed_root": 424242, "sharing_policy": "ISOLATED",
                "budget": {"ticks": {"limit": 9, "enforcement": "enforceable"}}})
        wid = w["world_id"]
        req("POST", "/worlds/%s/start" % wid)
        h = req("POST", "/worlds/%s/hypotheses" % wid, {"statement": "H"})
        x = req("POST", "/worlds/%s/experiments" % wid,
                {"spec": {"action": "encounter", "ticks": 32},
                 "hyp_id": h["hyp_id"], "commit": True})
        eid = x["exp_id"]
        o = req("POST", "/worlds/%s/observations" % wid,
                {"exp_id": eid, "content": {"score": 0.5}, "outcome": "SURVIVED"})
        evs = req("GET", "/worlds/%s/events" % wid)
        evs = evs["events"] if isinstance(evs, dict) else evs
        wc = next(e for e in evs if e["event_type"] == "WORLD_CREATED")
        return {"world_id": wid, "exp_id": eid, "obs_id": o["obs_id"],
                "event_id": o["event_id"], "entry_hash": o["entry_hash"],
                "wc_event_id": wc["event_id"], "wc_entry_hash": wc["entry_hash"]}
    except Exception as exc:                                  # noqa: BLE001
        print("  (sfe_sealed_run failed: %s: %s)" % (type(exc).__name__, exc))
        return None

R = []
_ZERO = "sha256:" + "0" * 64
_H1 = "sha256:" + "a" * 64
_H2 = "sha256:" + "b" * 64


def gate(name, ok, detail):
    R.append({"gate": name, "pass": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    return bool(ok)


class C:
    def __init__(self, host, port, machine, agent):
        self.base = f"http://{host}:{port}/api/v1"
        self.h = {"Authorization": "Bearer prometheus-ew-v0-shared-token",
                  "X-Prometheus-Machine": machine, "X-Prometheus-Agent": agent}

    def get(self, p, **q):
        return requests.get(f"{self.base}/{p}", headers=self.h, params=q, timeout=30)

    def post(self, p, b):
        b = dict(b); b.setdefault("idempotency_key", str(uuid.uuid4()))
        return requests.post(f"{self.base}/{p}", headers=self.h, json=b, timeout=30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--machine", default="M2")
    ap.add_argument("--agent", default="closure-test")
    ap.add_argument("--sfe-url", default=_DEFAULT_SFE)
    ap.add_argument("--sfe-cacert", default=_DEFAULT_CA)
    a = ap.parse_args()
    c = C(a.host, a.port, a.machine, a.agent)
    tag = uuid.uuid4().hex[:8]

    # C0 --- server-attested identity, independent of the token -------------
    idj = c.get("identity").json()
    gate("C0_identity_attested",
         bool(idj.get("db_system_id")) and idj.get("closure_version") == "pew.closure.v0",
         f"db_system_id={idj.get('db_system_id')} source_commit="
         f"{str(idj.get('source_commit'))[:12]} dirty={idj.get('source_dirty')}")

    # C1 --- packet read-back (I-NO-PACKET-READ) ----------------------------
    pk = c.post("packets", {"uri": "evidence_wiki/README.md", "kind": "doc"})
    pid = pk.json().get("packet_id") if pk.status_code == 200 else None
    if pid:
        rp = c.get(f"packets/{pid}")
        miss = c.get("packets/SP-nonexistentxx")
        gate("C1_packet_read", rp.status_code == 200 and rp.json().get("packet_id") == pid
             and miss.status_code == 404,
             f"GET packets/{pid}={rp.status_code} (was 405), unknown={miss.status_code}")
    else:
        gate("C1_packet_read", False, f"packet register failed: {pk.status_code} {pk.text[:80]}")

    # C2 --- fossil carries server attestation ------------------------------
    enc = f"CLOSURE-{tag}-ENC"
    c.post("fossil/worlds", {"world_id": f"CLOSURE-{tag}-W", "sfe_world_id": "wld_x",
                             "namespace": "test"})
    w = c.post("fossil/encounters", {
        "encounter_id": enc, "run_id": "r1", "sfe_event_id": "evt_" + "a" * 16,
        "sfe_entry_hash": _H1, "namespace": "test", "outcome": "SURVIVED"})
    rb = c.get(f"fossil/encounters/{enc}").json()
    att = (rb.get("runs") or [{}])[0].get("attestation") or {}
    gate("C2_fossil_attested",
         w.status_code == 200 and att.get("db_system_id") == idj.get("db_system_id")
         and att.get("sfe_anchor_verified") is False,
         f"write={w.status_code} attest.db_system_id={att.get('db_system_id')} "
         f"sfe_anchor_verified={att.get('sfe_anchor_verified')}")

    # C3 --- anchor: valid shape accepted, wrong CLASS rejected -------------
    good = c.post("fossil/encounters", {
        "encounter_id": f"CLOSURE-{tag}-GOOD", "run_id": "r", "namespace": "test",
        "sfe_event_id": "evt_" + "c" * 16, "sfe_entry_hash": _H2})
    badhash = c.post("fossil/encounters", {
        "encounter_id": f"CLOSURE-{tag}-BADH", "run_id": "r", "namespace": "test",
        "sfe_event_id": "evt_" + "c" * 16, "sfe_entry_hash": "not-a-sha"})
    badev = c.post("fossil/encounters", {
        "encounter_id": f"CLOSURE-{tag}-BADE", "run_id": "r", "namespace": "test",
        "sfe_event_id": "world_created", "sfe_entry_hash": _H2})
    gate("C3_anchor_shape_enforced",
         good.status_code == 200 and badhash.status_code == 422 and badev.status_code == 422,
         f"good={good.status_code} bad_hash={badhash.status_code} bad_evid={badev.status_code}")

    # C4 --- REAL causal-anchor verification (R-SFE-1 wired to SFE verify-anchor).
    #        The old known-gap pin is retired: PEW now calls the BOUND form and
    #        sets sfe_anchor_verified=true ONLY when the engine returns valid AND
    #        both bindings are explicitly true. Four controls, against a genuine
    #        sealed SFE run:
    #          C4a correct bound anchor          -> verified=true   (PASS)
    #          C4b wrong-but-real event          -> verified=false  (binds false)
    #          C4c forged entry_hash             -> verified=false  (hash mismatch)
    #          C4d unbound (no exp_id/obs_id)     -> verified=false  (cannot bind)
    run = sfe_sealed_run(a.sfe_url, a.sfe_cacert)

    def _verified(encid, sfe_event_id, entry_hash, prod):
        body = {"encounter_id": encid, "run_id": "r", "namespace": "test",
                "sfe_world_id": run["world_id"], "sfe_event_id": sfe_event_id,
                "sfe_entry_hash": entry_hash}
        if prod is not None:
            body["producer"] = prod
        w = c.post("fossil/encounters", body)
        rb = c.get(f"fossil/encounters/{encid}").json()
        att = (rb.get("runs") or [{}])[0].get("attestation") or {}
        return w.status_code, att

    if not run:
        for g in ("C4a_correct_bound_anchor_verified", "C4b_wrong_but_real_rejected",
                  "C4c_forged_hash_rejected", "C4d_unbound_cannot_verify"):
            gate(g, False, "SFE unreachable; cannot exercise the real mechanism")
    else:
        bound = {"exp_id": run["exp_id"], "obs_id": run["obs_id"]}
        st, att = _verified(f"CLOSURE-{tag}-C4A", run["event_id"], run["entry_hash"], bound)
        gate("C4a_correct_bound_anchor_verified",
             st == 200 and att.get("sfe_anchor_verified") is True,
             f"verified={att.get('sfe_anchor_verified')} checks={att.get('sfe_anchor_checks')}")

        st, att = _verified(f"CLOSURE-{tag}-C4B", run["wc_event_id"], run["wc_entry_hash"], bound)
        ck = att.get("sfe_anchor_checks") or {}
        gate("C4b_wrong_but_real_rejected",
             st == 200 and att.get("sfe_anchor_verified") is False
             and ck.get("entry_hash_matches") is True and ck.get("binds_exp_id") is False,
             f"verified={att.get('sfe_anchor_verified')} (real event, binds_exp_id="
             f"{ck.get('binds_exp_id')}, entry_hash_matches={ck.get('entry_hash_matches')})")

        st, att = _verified(f"CLOSURE-{tag}-C4C", run["event_id"], "sha256:" + "0" * 64, bound)
        ck = att.get("sfe_anchor_checks") or {}
        gate("C4c_forged_hash_rejected",
             st == 200 and att.get("sfe_anchor_verified") is False
             and ck.get("entry_hash_matches") is False,
             f"verified={att.get('sfe_anchor_verified')} entry_hash_matches={ck.get('entry_hash_matches')}")

        st, att = _verified(f"CLOSURE-{tag}-C4D", run["event_id"], run["entry_hash"], None)
        gate("C4d_unbound_cannot_verify",
             st == 200 and att.get("sfe_anchor_verified") is False,
             f"verified={att.get('sfe_anchor_verified')} (no exp_id/obs_id supplied -> "
             f"reason={(att.get('sfe_anchor_checks') or {}).get('reason')})")

    # C5 --- create a HARD and an ADVISORY constraint -----------------------
    hard = c.post("constraints", {
        "kind": "HARD", "namespace": "test",
        "title": "content-identity mismatch invalidates envelope",
        "statement": "A fossil whose stored output digest != submitted digest is void.",
        "scope": {"experiment_class": "any"}, "severity": "BLOCKER",
        "native_payload": {"check": "stored.output_digest == submitted.output_digest"}})
    adv = c.post("constraints", {
        "kind": "ADVISORY", "namespace": "test",
        "title": "primitive P shows no marginal incrementality in world family W",
        "statement": "R~=0 for P in family W under seed replication; scoped, not a ban.",
        "scope": {"primitive": "P", "world_family": "W"}, "severity": "INFO"})
    hid = hard.json().get("constraint_id"); aid = adv.json().get("constraint_id")
    gate("C5_constraint_kinds",
         hard.status_code == 200 and adv.status_code == 200
         and hard.json().get("kind") == "HARD" and adv.json().get("kind") == "ADVISORY",
         f"HARD={hid} ADVISORY={aid}")

    # C6 --- scope is mandatory (rejects a scopeless empirical ban) ---------
    noscope = c.post("constraints", {"kind": "ADVISORY", "scope": {},
                                     "statement": "never test P", "namespace": "test"})
    gate("C6_scope_mandatory", noscope.status_code == 422,
         f"scopeless constraint rejected={noscope.status_code} "
         "(prevents 'R~=0 here' -> 'never test this')")

    # C7 --- errata: PROPOSED -> REFUTED with adjudicating evidence ---------
    ev = c.post("constraints/%s/events" % aid, {
        "to_status": "REFUTED",
        "rationale": "effect explained by fitness in experiment E; scope was too broad",
        "reproducer": "replay under fresh seeds shows R recovers"})
    cur = c.get(f"constraints/{aid}").json()
    hist = cur.get("events") or []
    gate("C7_errata_transition",
         ev.status_code == 200 and cur.get("current_status") == "REFUTED"
         and len(hist) == 2 and hist[0]["to_status"] == "PROPOSED"
         and hist[-1]["to_status"] == "REFUTED",
         f"current_status={cur.get('current_status')} history="
         f"{[h['to_status'] for h in hist]}")

    # C8 --- a REFUTED constraint is not returned as active -----------------
    active = c.get("constraints", kind="ADVISORY", status="PROPOSED",
                   namespace="test").json()
    ids_active = [x["constraint_id"] for x in active.get("constraints", [])]
    gate("C8_refuted_not_active", aid not in ids_active,
         f"REFUTED {aid} absent from status=PROPOSED listing "
         f"(n_proposed={active.get('n')})")

    # C9 --- history is append-only (original PROPOSED row still present) ----
    still = [h for h in hist if h["to_status"] == "PROPOSED"]
    gate("C9_history_recoverable", len(still) == 1 and still[0].get("rationale") == "initial",
         "original PROPOSED event preserved after REFUTED (never mutated)")

    # ---- R2-1 PEW side: immutable audit/replay envelope ------------------
    # A full producer-supplied envelope (content-addressed identities). enc was
    # written in C2 with sfe_entry_hash=_H1.
    env = {
        "experiment_spec_id": "X-spec-" + tag, "organism_ids": ["org-A", "org-B"],
        "interpretation_id": "I-" + tag, "registry_id": "REG-" + tag,
        "entry_id": "ENTRY-" + tag, "composition_id": "COMP-" + tag,
        "topology": {"order": ["A", "B"], "glue": "seq"}, "ablation": "none",
        "action_id": "ACT-" + tag, "input_digest": "sha256:" + "1" * 64,
        "world_id": f"CLOSURE-{tag}-W", "world_config_digest": "sha256:" + "2" * 64,
        "measurement_def": "branches_taken", "measurement_version": "v0",
        "output_digest": "sha256:" + "3" * 64, "sfe_engine_id": "sha256:" + "e" * 64,
        "causal_anchor": {"sfe_event_id": "evt_" + "a" * 16, "sfe_entry_hash": _H1,
                          "sfe_event_seq": 1},
    }
    s1 = c.post("fossil/seal", {"encounter_id": enc, "run_id": "r1",
                                "envelope": env, "namespace": "test"})
    eid = s1.json().get("envelope_id") if s1.status_code == 200 else None
    gate("C10_seal_written",
         s1.status_code == 200 and str(eid).startswith("SEAL-")
         and s1.json().get("inserted") is True,
         f"seal={eid} inserted={s1.json().get('inserted')}")

    # C11 recover -- self-contained, PEW credential only (no SFE client cred)
    if eid:
        rr = c.get(f"fossil/seal/{eid}").json()
        slots_ok = not rr.get("slots_absent")     # every documented slot supplied
        gate("C11_seal_recoverable_sealed",
             rr.get("seal_valid") is True and slots_ok
             and (rr.get("fossil") or {}).get("encounter_id") == enc
             and (rr.get("envelope") or {}).get("sfe_engine_id"),
             f"seal_valid={rr.get('seal_valid')} slots_absent={rr.get('slots_absent')} "
             f"bound_fossil={(rr.get('fossil') or {}).get('encounter_id')}")
    else:
        gate("C11_seal_recoverable_sealed", False, "no seal to recover")

    # C12 immutable / idempotent: identical content -> same id, inserted False
    s2 = c.post("fossil/seal", {"encounter_id": enc, "run_id": "r1",
                                "envelope": env, "namespace": "test"})
    gate("C12_seal_idempotent",
         s2.status_code == 200 and s2.json().get("envelope_id") == eid
         and s2.json().get("inserted") is False,
         f"re-seal id={s2.json().get('envelope_id')} inserted={s2.json().get('inserted')}")

    # C13 content-addressed (NEGATIVE control): one changed slot -> different id
    env2 = dict(env); env2["action_id"] = "ACT-CHANGED"
    s3 = c.post("fossil/seal", {"encounter_id": enc, "run_id": "r1",
                                "envelope": env2, "namespace": "test"})
    gate("C13_content_addressed_tamper_evident",
         s3.status_code == 200 and s3.json().get("envelope_id") != eid,
         f"changed-slot seal={s3.json().get('envelope_id')} != {eid}")

    # C14 unknown encounter (NEGATIVE control) -> 404, no seal
    s4 = c.post("fossil/seal", {"encounter_id": f"NOPE-{tag}", "run_id": "r",
                                "envelope": env, "namespace": "test"})
    gate("C14_unknown_encounter_refused", s4.status_code == 404,
         f"seal of unknown encounter -> {s4.status_code}")

    # C15 anchor integrity (NEGATIVE control): envelope claims a DIFFERENT anchor
    # than the fossil it seals -> 409 (a seal cannot misrepresent the anchor)
    env3 = dict(env); env3["causal_anchor"] = {"sfe_event_id": "evt_" + "a" * 16,
                                               "sfe_entry_hash": _H2, "sfe_event_seq": 1}
    s5 = c.post("fossil/seal", {"encounter_id": enc, "run_id": "r1",
                                "envelope": env3, "namespace": "test"})
    gate("C15_seal_anchor_must_match_fossil", s5.status_code == 409,
         f"conflicting-anchor seal -> {s5.status_code}")

    all_pass = all(r["pass"] for r in R)
    out = {"all_pass": all_pass, "n": len(R), "passed": sum(r["pass"] for r in R),
           "gates": R}
    print(json.dumps({"all_pass": all_pass, "passed": out["passed"], "n": out["n"]}))
    with open("integration/closure_results.json", "w") as f:
        json.dump(out, f, indent=1)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
