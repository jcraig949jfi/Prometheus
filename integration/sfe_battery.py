#!/usr/bin/env python3
"""SFE / WORLD-SERVER STANDARD INTEGRATION BATTERY  (S0-S8)

Run this FIRST, on any machine, before doing anything else with the Engine.
It exercises the LIVE service over its real external HTTPS interface -- no
in-process calls, no mocks -- and on success leaves you a USABLE world plus
the credentials to reach it.

Standard library only, so it runs on a bare Python 3.9+ with no pip install.

    # from a checkout of the Prometheus repo, on any host in 192.168.1.0/24
    python integration/sfe_battery.py \
        --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt

    # reuse a token you already hold instead of minting a new identity
    python integration/sfe_battery.py --cacert <path> --token gen2_XXXX

    # pin the exact build you expect to be talking to
    python integration/sfe_battery.py --cacert <path> \
        --expect-source-hash sha256:5274ddbe...

On success it writes handoff.json (override with --out) containing the
base_url, cacert path, token, and the world_id -- that file IS the handoff
artifact you give to a downstream player. The world is left RUNNING by
default; pass --terminate if you only wanted a health check.

Exit code 0 = all PASS. Non-zero = number of failures.

Connect by IP ONLY. The Engine's certificate carries an IP SAN
(192.168.1.202) and no DNS name, so connecting by hostname fails TLS
verification even though the host is correct.
"""
from __future__ import annotations

import argparse
import base64
import json
import ssl
import sys
import time
import urllib.error
import urllib.request

DEFAULT_BASE = "https://192.168.1.202:8811/v2"
SEED_ROOT = 424242              # fixed: the standard integration world seed
WORLD_NAME = "HARMONIA-INTEGRATION-W0"
PROBE_PAYLOAD = b"HARMONIA-INTEGRATION-PROBE-v1"
MIN_SCHEMA = 3                  # engine schema this battery is written against

RESULTS = []


def rec(sid, name, ok, detail=""):
    RESULTS.append((sid, name, bool(ok), detail))
    print("  [%s] %-4s %-42s %s" % ("PASS" if ok else "FAIL", sid, name,
                                    detail[:92]))
    return bool(ok)


def call(base, method, path, cacert, token=None, body=None, insecure=False):
    """Returns (status, json_or_text, headers)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    ctx = (ssl._create_unverified_context() if insecure
           else ssl.create_default_context(cafile=cacert))
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
            raw = r.read().decode()
            hdrs = {k.lower(): v for k, v in r.headers.items()}
            try:
                return r.status, json.loads(raw), hdrs
            except Exception:
                return r.status, raw, hdrs
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        hdrs = {k.lower(): v for k, v in (e.headers or {}).items()}
        try:
            return e.code, json.loads(raw), hdrs
        except Exception:
            return e.code, raw, hdrs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--cacert", required=True,
                    help="path to m1.crt, the Engine's TLS trust anchor "
                         "(ships in the repo at SerendipityFoundryClient/"
                         "config/m1.crt)")
    ap.add_argument("--token", default=None,
                    help="existing gen2_ token; omitted = register a new client")
    ap.add_argument("--expect-source-hash", default=None,
                    help="fail unless the engine reports this "
                         "engine_source_hash (pins the exact build)")
    ap.add_argument("--insecure", action="store_true",
                    help="skip TLS verification. S0 reachability probe ONLY; "
                         "refused once a bearer token is in play")
    ap.add_argument("--terminate", action="store_true",
                    help="terminate the world at the end (default: leave it "
                         "RUNNING so it can actually be handed off)")
    ap.add_argument("--out", default="handoff.json",
                    help="where to write the handoff artifact")
    a = ap.parse_args()
    kw = dict(cacert=a.cacert, insecure=a.insecure)

    print("=" * 78)
    print("SFE / WORLD-SERVER STANDARD INTEGRATION BATTERY")
    print("base: %s" % a.base)
    print("=" * 78)

    # ---- S0 endpoint reachable -------------------------------------------
    try:
        st, v, hdr = call(a.base, "GET", "/version", **kw)
        rec("S0", "endpoint reachable (GET /version, no auth)",
            st == 200, "HTTP %s" % st)
    except Exception as e:
        rec("S0", "endpoint reachable", False, repr(e))
        print("\nS0 FAILED. In order, check:")
        print("  1. you are on 192.168.1.0/24   (the Engine admits only that)")
        print("  2. ping 192.168.1.202")
        print("  3. you used the IP, not a hostname (cert has an IP SAN only)")
        print("  4. --cacert points at a readable m1.crt")
        return len([r for r in RESULTS if not r[2]])

    # --insecure must never be combined with a real credential.
    if a.insecure:
        print("\nREFUSING to continue past S0 with --insecure: every step "
              "below carries a bearer token, and an unverified TLS session "
              "can be MITM'd and the token captured. Re-run without it.")
        return len([r for r in RESULTS if not r[2]]) or 1

    # ---- S1 version / build identity -- ASSERTED, not merely printed -----
    schema = v.get("schema_version") if isinstance(v, dict) else None
    rec("S1", "engine identity asserted (api/schema/build)",
        isinstance(v, dict) and v.get("api") == "v2"
        and v.get("runtime") == "serendipity-foundry-sfe"
        and isinstance(schema, int) and schema >= MIN_SCHEMA,
        "api=%s schema=%s (need >=%d) commit=%s"
        % (v.get("api"), schema, MIN_SCHEMA,
           str(v.get("source_commit"))[:12]))

    body_hash = v.get("engine_source_hash") if isinstance(v, dict) else None
    hdr_hash = hdr.get("x-sfe-engine-source-hash")
    rec("S1b", "response header build == body build (no split brain)",
        bool(body_hash) and body_hash == hdr_hash,
        "header %s body" % ("==" if body_hash == hdr_hash else "!="))

    if a.expect_source_hash:
        rec("S1c", "engine build matches --expect-source-hash",
            body_hash == a.expect_source_hash,
            "got %s" % str(body_hash)[:26])

    # ---- identity ---------------------------------------------------------
    token = a.token
    if not token:
        st, c, _ = call(a.base, "POST", "/clients",
                        body={"name": "harmonia-integration"}, **kw)
        token = c.get("token") if isinstance(c, dict) else None
        rec("S1d", "client registration (new identity)", bool(token),
            "client_id=%s" % (c.get("client_id") if isinstance(c, dict) else c))
        if not token:
            print("\nNo token. Is registration open? GET /v2/version -> "
                  "registration_open. If false, ask the operator for a token "
                  "and re-run with --token.")
            return len([r for r in RESULTS if not r[2]])
    else:
        rec("S1d", "using supplied token", True, "token supplied via --token")

    st, s, _ = call(a.base, "POST", "/sessions", token=token,
                    body={"name": "harmonia-integration"}, **kw)
    sid = s.get("session_id") if isinstance(s, dict) else None
    rec("S1e", "session opened", bool(sid), str(sid))

    # ---- S2 deterministic known-good world --------------------------------
    st, w, _ = call(a.base, "POST", "/worlds", token=token, body={
        "session_id": sid, "name": WORLD_NAME, "seed_root": SEED_ROOT,
        "budget": {"work_items": {"limit": 64,
                                  "enforcement": "enforceable"}}}, **kw)
    wid = w.get("world_id") if isinstance(w, dict) else None
    rec("S2", "standard integration world created", bool(wid),
        "world_id=%s seed_root=%s"
        % (wid, w.get("seed_root") if isinstance(w, dict) else "?"))
    if not wid:
        print("world create failed: %s" % json.dumps(w)[:300])
        return len([r for r in RESULTS if not r[2]])

    # ---- S3 identity stable / invariants ----------------------------------
    rec("S3", "world spec invariants (seed/state/policy/hash)",
        (w.get("seed_root") == SEED_ROOT and w.get("state") == "CREATED"
         and w.get("sharing_policy") == "ISOLATED"
         and str(w.get("head_hash", "")).startswith("sha256:")),
        "state=%s policy=%s" % (w.get("state"), w.get("sharing_policy")))

    st, w2, _ = call(a.base, "POST", "/worlds/%s/start" % wid, token=token,
                     body={}, **kw)
    rec("S3b", "start -> RUNNING and head_hash advances",
        isinstance(w2, dict) and w2.get("state") == "RUNNING"
        and w2.get("head_hash") != w.get("head_hash"),
        "state=%s" % (w2.get("state") if isinstance(w2, dict) else w2))

    # ---- S4 query through the external interface --------------------------
    st, sts, _ = call(a.base, "GET", "/worlds/%s/status" % wid, token=token,
                      **kw)
    rec("S4", "world queryable; ledger integrity verified",
        isinstance(sts, dict) and sts.get("ledger_integrity_ok") is True
        and "epistemics" in sts and "engine" in sts,
        "events=%s integrity=%s" % (sts.get("event_count"),
                                    sts.get("ledger_integrity_ok")))

    # ---- S7 the two player contracts, both actually exercised --------------
    # (a) PUSH: player writes an artifact straight into the world.
    b64 = base64.b64encode(PROBE_PAYLOAD).decode()
    st, art, _ = call(a.base, "POST", "/worlds/%s/artifacts" % wid,
                      token=token,
                      body={"kind": "success", "data_b64": b64,
                            "meta": {"probe": True}}, **kw)
    aid = art.get("artifact_id") if isinstance(art, dict) else None
    rec("S7", "PUSH: player posts an artifact", bool(aid),
        "artifact_id=%s" % str(aid)[:26])
    if aid:
        st, cont, _ = call(a.base, "GET",
                           "/worlds/%s/artifacts/%s/content" % (wid, aid),
                           token=token, **kw)
        got = (base64.b64decode(cont.get("content_b64", ""))
               if isinstance(cont, dict) else b"")
        rec("S7b", "PUSH: artifact round-trips byte-exactly",
            got == PROBE_PAYLOAD,
            "origin=%s" % (cont.get("origin") if isinstance(cont, dict)
                           else "?"))

    # (b) PULL: enqueue real work, claim it, heartbeat, complete it.
    #     Work is enqueued by COMMITTING AN EXPERIMENT with enqueue=true --
    #     there is no bare "enqueue" route, and none is needed.
    st, hyp, _ = call(a.base, "POST", "/worlds/%s/hypotheses" % wid,
                      token=token,
                      body={"statement": "integration probe: the work loop "
                                         "closes end to end"}, **kw)
    hid = hyp.get("hyp_id") if isinstance(hyp, dict) else None
    st, pred, _ = call(a.base, "POST", "/worlds/%s/predictions" % wid,
                       token=token,
                       body={"hyp_id": hid,
                             "content": {"expect": "work becomes claimable"}},
                       **kw)
    pid = pred.get("pred_id") if isinstance(pred, dict) else None
    rec("S7c", "hypothesis + prediction registered", bool(hid and pid),
        "hyp=%s pred=%s" % (str(hid)[:16], str(pid)[:16]))

    st, exp, _ = call(a.base, "POST", "/worlds/%s/experiments" % wid,
                      token=token,
                      body={"spec": {"probe": True, "task": "noop"},
                            "hyp_id": hid, "pred_id": pid,
                            "commit": True, "enqueue": True,
                            "kind": "probe", "priority": 1}, **kw)
    eid = exp.get("exp_id") if isinstance(exp, dict) else None
    rec("S7d", "experiment committed AND work enqueued", bool(eid),
        "exp_id=%s" % str(eid)[:22])

    # The Engine is effectively serial and can return a transient 5xx on a
    # WRITE endpoint when M1 is under heavy disk load (claim_work takes
    # BEGIN IMMEDIATE). Retry a few times before calling it a failure, and
    # always report the status so a real error is never silently read as
    # "queue empty".
    work, cst = None, None
    for attempt in range(4):
        cst, claim, _ = call(a.base, "POST", "/work/claim", token=token,
                             body={"worker_id": "integration-probe",
                                   "world_id": wid, "lease_s": 60}, **kw)
        work = claim.get("work") if isinstance(claim, dict) else None
        if work or cst == 200:
            break
        time.sleep(1.5 * (attempt + 1))
    rec("S7e", "PULL: enqueued work is actually claimable", bool(work),
        "HTTP %s work_id=%s" % (cst, str(work.get("work_id"))[:22] if work
                                else "NONE"))

    wkid = work.get("work_id") if work else None
    if work:
        cid = work.get("claim_id")
        st, _hb, _ = call(a.base, "POST", "/work/%s/heartbeat" % wkid,
                          token=token,
                          body={"worker_id": "integration-probe",
                                "claim_id": cid}, **kw)
        rec("S7f", "PULL: lease heartbeat accepted", st == 200, "HTTP %s" % st)
        st, comp, _ = call(a.base, "POST", "/work/%s/complete" % wkid,
                           token=token,
                           body={"worker_id": "integration-probe",
                                 "claim_id": cid,
                                 "result": {"ok": True,
                                            "note": "integration probe"}}, **kw)
        rec("S7g", "PULL: work completed with a result",
            st == 200 and isinstance(comp, dict)
            and comp.get("status") == "COMPLETED",
            "status=%s" % (comp.get("status") if isinstance(comp, dict)
                           else st))

    # Binding work_id promotes the observation from CLIENT_ASSERTED to
    # ENGINE_WORK_RESULT -- the Engine attests the result rather than taking
    # the client's word for it. Legal outcomes are FALSIFIED / SURVIVED /
    # INCONCLUSIVE: a prediction is never "confirmed" here.
    st, obs, _ = call(a.base, "POST", "/worlds/%s/observations" % wid,
                      token=token,
                      body={"exp_id": eid, "pred_id": pid, "work_id": wkid,
                            "content": {"saw": "loop closed"},
                            "outcome": "SURVIVED"}, **kw)
    # The POST returns only obs_id, so attestation CANNOT be read from it.
    # Confirm promotion by re-reading the world's epistemics: obs_engine
    # counts observations whose evidence_class is ENGINE_WORK_RESULT. Without
    # this the check would pass even with no work bound at all.
    _st2, sts2, _ = call(a.base, "GET", "/worlds/%s/status" % wid, token=token,
                         **kw)
    epi = sts2.get("epistemics", {}) if isinstance(sts2, dict) else {}
    rec("S7h", "observation is ENGINE-ATTESTED, not client-asserted",
        st == 200 and wkid is not None
        and epi.get("observations_engine_attested", 0) >= 1,
        "engine_attested=%s client_asserted=%s prospective=%s"
        % (epi.get("observations_engine_attested"),
           epi.get("observations_client_asserted"),
           epi.get("observations_prospectively_predicted")))

    # ---- S8 identifiers carried into PEW evidence -------------------------
    st, ev, _ = call(a.base, "GET", "/worlds/%s/events" % wid, token=token,
                     **kw)
    evs = ev.get("events") if isinstance(ev, dict) else None
    rec("S8", "events carry world_id AND event_seq (PEW citation keys)",
        bool(evs) and all(e.get("world_id") == wid
                          and isinstance(e.get("event_seq"), int)
                          for e in evs),
        "%d events, seq %s..%s" % (len(evs or []),
                                   (evs or [{}])[0].get("event_seq"),
                                   (evs or [{}])[-1].get("event_seq")))
    st, kn, _ = call(a.base, "GET", "/worlds/%s/knowledge" % wid, token=token,
                     **kw)
    rec("S8b", "knowledge frontier queryable",
        isinstance(kn, dict) and "available" in kn,
        "available=%s head_seq=%s" % (kn.get("available_count"),
                                      kn.get("world_head_seq")))

    # ---- S5 checkpoint / fork = reset & reproduce -------------------------
    st, ck, _ = call(a.base, "POST", "/worlds/%s/checkpoint" % wid,
                     token=token, body={}, **kw)
    ckid = ck.get("checkpoint_id") if isinstance(ck, dict) else None
    rec("S5", "checkpoint created", bool(ckid), "id=%s" % str(ckid)[:24])
    child = None
    if ckid:
        st, fk, _ = call(a.base, "POST", "/worlds/%s/fork" % wid, token=token,
                         body={"checkpoint_id": ckid,
                               "children": [{"name": WORLD_NAME + "-FORK"}]},
                         **kw)
        kids = fk.get("children") if isinstance(fk, dict) else None
        child = kids[0].get("world_id") if kids else None
        rec("S5b", "fork from checkpoint (branch without disturbing parent)",
            bool(kids) and kids[0].get("parent_world_id") == wid,
            "child=%s fork_point=%s" % (str(child)[:24],
                                        kids[0].get("fork_point") if kids
                                        else "?"))

    # ---- S6 malformed request fails overtly -------------------------------
    st, bad, _ = call(a.base, "POST", "/worlds", token=token,
                      body={"session_id": sid, "name": "BAD",
                            "budget": {"work_items": {"limit": 1,
                                                      "enforcement": "hard"}}},
                      **kw)
    rec("S6", "malformed request fails overtly, never silently",
        st == 422 and isinstance(bad, dict) and "detail" in bad,
        "HTTP %s with field path" % st)
    st, _un, _ = call(a.base, "GET", "/worlds/%s/status" % wid, **kw)
    rec("S6b", "unauthenticated read rejected", st in (401, 403),
        "HTTP %s" % st)

    # ---- cleanup / handoff -------------------------------------------------
    # The fork child is scratch: always tidy it. The MAIN world is the
    # deliverable and is left RUNNING unless --terminate was asked for.
    if child:
        call(a.base, "POST", "/worlds/%s/terminate" % child, token=token,
             body={}, **kw)
    if a.terminate:
        stt, _, _ = call(a.base, "POST", "/worlds/%s/terminate" % wid,
                         token=token, body={}, **kw)
        print("\n  world TERMINATED at your request (HTTP %s)" % stt)
    else:
        handoff = {"base_url": a.base, "cacert": a.cacert, "token": token,
                   "session_id": sid, "world_id": wid,
                   "world_state": "RUNNING", "seed_root": SEED_ROOT,
                   "engine_source_hash": body_hash,
                   "source_commit": v.get("source_commit"),
                   "schema_version": schema}
        try:
            with open(a.out, "w") as fh:
                json.dump(handoff, fh, indent=2)
            print("\n  handoff artifact written: %s" % a.out)
            print("  world %s left RUNNING and is yours to hand off." % wid)
            print("  THAT FILE CONTAINS A BEARER TOKEN -- treat it as a "
                  "credential.")
        except OSError as e:
            print("\n  WARNING: could not write %s: %s" % (a.out, e))
            print("  token (store it, it is not retrievable later): %s" % token)

    fails = [r for r in RESULTS if not r[2]]
    print("=" * 78)
    print("BATTERY: %d/%d PASS" % (len(RESULTS) - len(fails), len(RESULTS)))
    if fails:
        print("FAILURES: %s" % ", ".join(f[0] for f in fails))
    else:
        print("All checks passed against build %s" % str(body_hash)[:26])
    print("=" * 78)
    return len(fails)


if __name__ == "__main__":
    sys.exit(main())
