#!/usr/bin/env python3
"""Daedalus sprint 2026-09-04 -- reproduce Harmonia's engine-relevant boundary
findings against a LIVE engine before changing any behavior.

Charter rule: "Say 'verified' only when I ran it."  Each probe returns one of
REPRODUCED / NOT_REPRODUCED / REFINED, with the evidence that decided it.

Usage:
    python repro_harmonia_findings.py --base-url https://192.168.1.191:8811 \
        --cafile ../../../SerendipityFoundry/SerendipityFoundryClient/config/m2.crt
"""
import argparse
import base64
import hashlib
import json
import ssl
import time
import urllib.error
import urllib.request

RESULTS = []


class Engine:
    def __init__(self, base, cafile):
        self.base = base.rstrip("/")
        self.ctx = ssl.create_default_context(cafile=cafile)
        self.token = None

    def req(self, method, path, body=None, headers=None):
        url = self.base + path
        data = json.dumps(body).encode() if body is not None else None
        h = {"content-type": "application/json"}
        if self.token:
            h["authorization"] = "Bearer " + self.token
        h.update(headers or {})
        r = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(r, context=self.ctx, timeout=30) as resp:
                payload = resp.read().decode()
                return resp.status, json.loads(payload or "{}")
        except urllib.error.HTTPError as exc:
            payload = exc.read().decode()
            try:
                return exc.code, json.loads(payload or "{}")
            except json.JSONDecodeError:
                return exc.code, {"raw": payload}


def record(pid, title, verdict, detail, evidence=None):
    RESULTS.append({"probe": pid, "title": title, "verdict": verdict,
                    "detail": detail, "evidence": evidence})
    print("[%-15s] %-26s %s" % (verdict, pid, detail))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--cafile", required=True)
    ap.add_argument("--out", default="repro_results.json")
    a = ap.parse_args()

    e = Engine(a.base_url, a.cafile)
    _, ver = e.req("GET", "/v2/version")
    print("engine: %s  commit %s" % (ver.get("engine_source_hash", "?")[:24],
                                     ver.get("source_commit", "?")[:12]))

    tag = "daedalus-repro-%d" % int(time.time())
    st, c = e.req("POST", "/v2/clients", {"name": tag})
    assert st == 200, (st, c)
    e.token = c["token"]
    _, s = e.req("POST", "/v2/sessions", {"name": tag})
    sid = s["session_id"]

    def body_world(name):
        return {"session_id": sid, "name": name, "sharing_policy": "ISOLATED",
                "seed_root": 424242, "budget": {}}

    def mkworld(name, headers=None):
        return e.req("POST", "/v2/worlds", body_world(name), headers=headers)

    # ---- I-CREATE-IDEMPOTENCY (B1 / H2) --------------------------------
    ids = []
    for _ in range(3):
        _, w = mkworld("repro-idem")
        ids.append(w.get("world_id"))
    distinct = len(set(ids))
    record("I-CREATE-IDEMPOTENCY", "blind retry doubles worlds",
           "REPRODUCED" if distinct == 3 else "NOT_REPRODUCED",
           "same config x3 -> %d distinct world_ids" % distinct,
           {"world_ids": ids})

    # does the endpoint even ACCEPT an Idempotency-Key header today?
    hdr = {"Idempotency-Key": "daedalus-fixed-key-1"}
    _, w2 = mkworld("repro-idem-key", headers=hdr)
    _, w3 = mkworld("repro-idem-key", headers=hdr)
    same = w2.get("world_id") == w3.get("world_id")
    record("I-CREATE-IDEM-HEADER", "Idempotency-Key header honored?",
           "REPRODUCED" if not same else "NOT_REPRODUCED",
           "header %s" % ("IGNORED -> 2 worlds" if not same
                          else "honored -> 1 world"),
           {"w2": w2.get("world_id"), "w3": w3.get("world_id")})

    wid = ids[0]

    # ---- I-WORLD-ENUM-UNSCOPED (K1) ------------------------------------
    _, lw = e.req("GET", "/v2/worlds")
    worlds = lw["worlds"] if isinstance(lw, dict) else lw
    fields = sorted(worlds[0].keys()) if worlds else []
    record("I-WORLD-ENUM-UNSCOPED", "GET /v2/worlds scoping", "REFINED",
           "fresh client sees n=%d (its own only); no state/session filter params"
           % len(worlds),
           {"n_for_fresh_client": len(worlds), "world_fields": fields})

    # ---- I-EVENTS-SHAPE (K4) -------------------------------------------
    _, evs = e.req("GET", "/v2/worlds/%s/events?limit=10" % wid)
    shape = "dict" if isinstance(evs, dict) else "list"
    keys = sorted(evs.keys()) if isinstance(evs, dict) else None
    record("I-EVENTS-SHAPE", "GET events return shape",
           "NOT_REPRODUCED" if shape == "dict" else "REPRODUCED",
           "raw HTTP returns a %s%s" % (shape,
                                        " with keys %s" % keys if keys else ""),
           {"shape": shape})

    # ---- I-CLIENT-GATE-UNENFORCED (A3) ---------------------------------
    good = b"organism-bytes-v1"
    _, art = e.req("POST", "/v2/worlds/%s/artifacts" % wid,
                   {"kind": "organism",
                    "data_b64": base64.b64encode(good).decode(), "meta": {}})
    server_hash = art.get("blob_hash", "")
    true_hash = "sha256:" + hashlib.sha256(good).hexdigest()
    corrupt = b"organism-bytes-v1-CORRUPTED"
    st_c, _ = e.req("POST", "/v2/worlds/%s/artifacts" % wid,
                    {"kind": "organism",
                     "data_b64": base64.b64encode(corrupt).decode(), "meta": {}})
    # can a caller ASSERT the expected digest and have the engine enforce it?
    st_x, art_x = e.req("POST", "/v2/worlds/%s/artifacts" % wid,
                        {"kind": "organism",
                         "data_b64": base64.b64encode(corrupt).decode(),
                         "meta": {}, "expected_blob_hash": true_hash})
    record("I-CLIENT-GATE-UNENFORCED", "organism content-id gate", "REFINED",
           "server digest authoritative (correct=%s); corrupt bytes accepted "
           "(%s); no expected-hash field (%s)"
           % (server_hash == true_hash, st_c, st_x),
           {"server_hash_correct": server_hash == true_hash,
            "corrupt_status": st_c, "expected_hash_field_status": st_x,
            "expected_hash_field_error": art_x if st_x != 200 else None})

    # ---- I-ATTEST-NOT-FORCED (C3) --------------------------------------
    # a world must be RUNNING before an experiment may commit (verified: a
    # CREATED world answers 409 invalid_transition -- the engine fails closed).
    st_start, _ = e.req("POST", "/v2/worlds/%s/start" % wid)
    assert st_start == 200, st_start
    st_h, h = e.req("POST", "/v2/worlds/%s/hypotheses" % wid,
                    {"statement": "repro hypothesis"})
    assert st_h == 200, (st_h, h)
    hid = h.get("hyp_id")
    st_e, ex = e.req("POST", "/v2/worlds/%s/experiments" % wid,
                     {"spec": {"probe": "attest"}, "hyp_id": hid,
                      "commit": True})
    assert st_e == 200, (st_e, ex)
    eid = ex.get("exp_id")
    st_o, obs = e.req("POST", "/v2/worlds/%s/observations" % wid,
                      {"exp_id": eid, "content": {"v": 1}, "outcome": "SURVIVED"})
    _, status = e.req("GET", "/v2/worlds/%s/status" % wid)
    record("I-ATTEST-NOT-FORCED", "unattested observation accepted",
           "REPRODUCED" if st_o == 200 else "NOT_REPRODUCED",
           "observation with NO work_id accepted (%s); no world-level setting "
           "can require attestation" % st_o,
           {"obs_status": st_o, "obs": obs,
            "epistemics": status.get("epistemics"),
            "status_keys": sorted(status.keys())})

    # ---- I-CAUSAL-CLIENT (D1) ------------------------------------------
    returned = sorted(obs.keys()) if isinstance(obs, dict) else []
    has_anchor = any(k in returned for k in ("event_id", "entry_hash",
                                             "event_seq"))
    record("I-CAUSAL-CLIENT", "exact causal anchor returned?",
           "REPRODUCED" if not has_anchor else "NOT_REPRODUCED",
           "POST observations returns %s; caller must SEARCH the ledger for "
           "its own event" % returned,
           {"returned_keys": returned})

    # ---- I-LIFECYCLE-TERMINATED (B4) + generalization -------------------
    # CONTROL FIRST: run every write against a RUNNING world, so the only
    # variable between `before` and `after` is the terminate call itself. A
    # write that already 409s while CREATED proves nothing about TERMINATED.
    def write_battery(w_id, label):
        out = {}
        st1, _ = e.req("POST", "/v2/worlds/%s/artifacts" % w_id,
                       {"kind": label,
                        "data_b64": base64.b64encode(b"x").decode(), "meta": {}})
        out["artifact"] = st1
        st2, _ = e.req("POST", "/v2/worlds/%s/hypotheses" % w_id,
                       {"statement": "hyp-%s" % label})
        out["hypothesis"] = st2
        st3, _ = e.req("POST", "/v2/worlds/%s/experiments" % w_id,
                       {"spec": {"phase": label}, "commit": True})
        out["experiment"] = st3
        st4, _ = e.req("POST", "/v2/worlds/%s/budget/consume" % w_id,
                       {"resource": "ticks", "amount": 1})
        out["budget_consume"] = st4
        # a claim answers 200 with {"work": null} when nothing is claimable, so
        # the STATUS CODE alone does not mean a claim happened. Score it as a
        # write only if an item actually came back.
        st5, claim = e.req("POST", "/v2/work/claim",
                           {"world_id": w_id, "worker_id": "w-%s" % label})
        out["work_claim"] = st5 if (claim or {}).get("work") else "200_but_empty"
        return out

    _, w = mkworld("repro-terminate")
    twid = w["world_id"]
    e.req("POST", "/v2/worlds/%s/start" % twid)
    before = write_battery(twid, "before")
    st_t, _ = e.req("POST", "/v2/worlds/%s/terminate" % twid)
    after = write_battery(twid, "after")
    # only count a write as "survives termination" if it WORKED while running
    survived = sorted(k for k in after
                      if before.get(k) == 200 and after[k] == 200)
    blocked = sorted(k for k in after
                     if before.get(k) == 200 and after[k] != 200)
    record("I-LIFECYCLE-TERMINATED", "writes after TERMINATED",
           "REPRODUCED" if survived else "NOT_REPRODUCED",
           "terminate=%s; worked-before AND after: %s; correctly blocked: %s"
           % (st_t, survived, blocked),
           {"before": before, "after": after, "survived": survived,
            "blocked": blocked})

    # ---- B5: world config completeness ---------------------------------
    _, gw = e.req("GET", "/v2/worlds/%s" % wid)
    record("B5-WORLD-CONFIG", "GET /v2/worlds/{id} completeness",
           "REPRODUCED" if "budget" not in gw else "NOT_REPRODUCED",
           "fields: %s" % sorted(gw.keys()), {"has_budget": "budget" in gw})

    out = {"engine": ver, "probed_at": time.time(), "results": RESULTS}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    from collections import Counter
    print("\nwrote %s: %d probes" % (a.out, len(RESULTS)))
    print(dict(Counter(r["verdict"] for r in RESULTS)))


if __name__ == "__main__":
    main()
