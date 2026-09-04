#!/usr/bin/env python3
"""LIVE REPAIR BAR -- Daedalus, 2026-09-04.

Runs the eight pre-registered hazards against the DEPLOYED service, not against
the source tree. Each check names the PRE state measured on the stale daemon
(build 71e4e80e8, from repro_results.json) and asserts the POST behaviour of the
repaired contract.

Two of the eight are REGRESSION checks on findings that were REFUTED. They must
NOT flip -- turning a refuted finding into a fake success would be the worst
outcome available here.

    python live_repair_bar.py --base-url https://192.168.1.191:8811 \
        --cacert ../../../SerendipityFoundry/SerendipityFoundryEngine/deploy/m2.crt
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import ssl
import time
import urllib.error
import urllib.request

RESULTS = []


class C:
    def __init__(self, base, cafile):
        self.base = base.rstrip("/")
        self.ctx = ssl.create_default_context(cafile=cafile)
        self.token = None

    def req(self, method, path, body=None, headers=None):
        data = json.dumps(body).encode() if body is not None else None
        h = {"content-type": "application/json"}
        if self.token:
            h["authorization"] = "Bearer " + self.token
        h.update(headers or {})
        r = urllib.request.Request(self.base + path, data=data, headers=h,
                                   method=method)
        try:
            with urllib.request.urlopen(r, context=self.ctx, timeout=30) as z:
                return z.status, json.loads(z.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try:
                return e.code, json.loads(body or "{}")
            except json.JSONDecodeError:
                return e.code, {"raw": body}

    def register(self, name):
        _, c = self.req("POST", "/v2/clients", {"name": name})
        self.token = c["token"]
        _, s = self.req("POST", "/v2/sessions", {"name": name})
        return c["client_id"], s["session_id"]


def rec(hid, title, pre, post, ok, evidence=None):
    RESULTS.append({"hazard": hid, "title": title, "pre": pre, "post": post,
                    "verdict": "PASS" if ok else "FAIL", "evidence": evidence})
    print("[%s] %-22s %s" % ("PASS" if ok else "FAIL", hid, title))
    print("        PRE : %s" % pre)
    print("        POST: %s" % post)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--cacert", required=True)
    ap.add_argument("--out", default="live_repair_bar_results.json")
    a = ap.parse_args()

    e = C(a.base_url, a.cacert)
    _, ver = e.req("GET", "/v2/version")
    print("live source_commit : %s" % ver.get("source_commit"))
    print("live schema_version: %s" % ver.get("schema_version"))
    print("live engine hash   : %s\n" % (ver.get("engine_source_hash") or "")[:32])

    tag = "daedalus-livebar-%d" % int(time.time())
    cid, sid = e.register(tag)

    def world(name, **kw):
        b = {"session_id": sid, "name": name, "sharing_policy": "ISOLATED",
             "seed_root": 424242, "budget": {}}
        b.update(kw)
        return b

    def running(name, **kw):
        _, w = e.req("POST", "/v2/worlds", world(name, **kw))
        wid = w["world_id"]
        e.req("POST", "/v2/worlds/%s/start" % wid)
        return wid

    def committed_exp(wid, spec=None):
        _, h = e.req("POST", "/v2/worlds/%s/hypotheses" % wid,
                     {"statement": "H"})
        st, x = e.req("POST", "/v2/worlds/%s/experiments" % wid,
                      {"spec": spec or {"probe": 1}, "hyp_id": h["hyp_id"],
                       "commit": True})
        return x

    # ---- H1 CREATE-WORLD IDEMPOTENCY -----------------------------------
    hdr = {"Idempotency-Key": tag + "-k1"}
    _, w1 = e.req("POST", "/v2/worlds", world("idem"), headers=hdr)
    _, w2 = e.req("POST", "/v2/worlds", world("idem"), headers=hdr)
    same = w1.get("world_id") == w2.get("world_id")
    st_c, conflict = e.req("POST", "/v2/worlds",
                           world("idem", seed_root=999999), headers=hdr)
    rec("H1-IDEMPOTENCY", "create-world retry safety",
        "same config x3 -> 3 world_ids; Idempotency-Key silently IGNORED",
        "same key+request -> same world (%s); conflicting request -> %d %s"
        % (same, st_c, (conflict.get("detail") or {}).get("error")),
        same and st_c == 409,
        {"w1": w1.get("world_id"), "w2": w2.get("world_id"),
         "conflict_status": st_c})

    # ---- H2 REQUIRED ATTESTATION ---------------------------------------
    wid = running("attest", require_attestation=True)
    _, gw = e.req("GET", "/v2/worlds/%s" % wid)
    x = committed_exp(wid)
    st_bad, bad = e.req("POST", "/v2/worlds/%s/observations" % wid,
                        {"exp_id": x["exp_id"], "content": {"v": 1},
                         "outcome": "SURVIVED"})
    # the attested path must still work
    x2 = committed_exp(wid, {"probe": 2})
    _, x2e = e.req("POST", "/v2/worlds/%s/experiments" % wid,
                   {"spec": {"probe": 3}, "commit": True, "enqueue": True})
    _, claim = e.req("POST", "/v2/work/claim",
                     {"world_id": wid, "worker_id": "wk"})
    wk = claim.get("work") or {}
    e.req("POST", "/v2/work/%s/complete" % wk.get("work_id"),
          {"worker_id": "wk", "result": {"score": 1.0},
           "claim_id": wk.get("claim_id")})
    st_ok, good = e.req("POST", "/v2/worlds/%s/observations" % wid,
                        {"exp_id": x2e["exp_id"], "content": {"v": 1},
                         "outcome": "SURVIVED", "work_id": wk.get("work_id")})
    rec("H2-ATTESTATION", "forced evidence attestation",
        "observation with no work_id -> 200 CLIENT_ASSERTED; nothing could require it",
        "require_attestation world created (flag=%s); unattested -> %d; "
        "attested -> %d class=%s"
        % (gw.get("require_attestation"), st_bad, st_ok,
           good.get("evidence_class")),
        gw.get("require_attestation") is True and st_bad == 422
        and st_ok == 200 and good.get("evidence_class") == "ENGINE_WORK_RESULT",
        {"unattested_status": st_bad, "attested_status": st_ok,
         "attested_class": good.get("evidence_class")})

    # ---- H3 CONTENT IDENTITY GATE --------------------------------------
    wid = running("cidgate")
    good_bytes = b"organism-bytes-v1"
    ghash = "sha256:" + hashlib.sha256(good_bytes).hexdigest()
    st_a, art = e.req("POST", "/v2/worlds/%s/artifacts" % wid,
                      {"kind": "organism",
                       "data_b64": base64.b64encode(good_bytes).decode(),
                       "expected_blob_hash": ghash})
    _, evs_before = e.req("GET", "/v2/worlds/%s/events?limit=500" % wid)
    n_before = len(evs_before["events"])
    st_r, rej = e.req("POST", "/v2/worlds/%s/artifacts" % wid,
                      {"kind": "organism",
                       "data_b64": base64.b64encode(b"CORRUPTED").decode(),
                       "expected_blob_hash": ghash})
    _, evs_after = e.req("GET", "/v2/worlds/%s/events?limit=500" % wid)
    n_after = len(evs_after["events"])
    rec("H3-CONTENT-GATE", "organism content identity",
        "expected_blob_hash field did not exist (422 extra_forbidden); "
        "corrupt bytes stored with an honest digest of the WRONG object",
        "correct bytes+hash -> %d (%s); corrupt bytes+original hash -> %d; "
        "ledger events %d -> %d (rejected write appended %d)"
        % (st_a, art.get("blob_hash") == ghash, st_r, n_before, n_after,
           n_after - n_before),
        st_a == 200 and art.get("blob_hash") == ghash and st_r == 422
        and n_after == n_before,
        {"accept": st_a, "reject": st_r, "events_before": n_before,
         "events_after": n_after})

    # ---- H4 CAUSAL ANCHOR ----------------------------------------------
    wid = running("anchor")
    x = committed_exp(wid)
    st_o, obs = e.req("POST", "/v2/worlds/%s/observations" % wid,
                      {"exp_id": x["exp_id"], "content": {"v": 1},
                       "outcome": "SURVIVED"})
    keys = sorted(obs.keys()) if isinstance(obs, dict) else []
    need = ("obs_id", "event_id", "entry_hash", "event_seq", "world_index")
    _, evs = e.req("GET", "/v2/worlds/%s/events?limit=500" % wid)
    match = [v for v in evs["events"] if v["event_id"] == obs.get("event_id")]
    resolves = (len(match) == 1
                and match[0]["event_type"] == "OBSERVATION_RECORDED"
                and match[0]["entry_hash"] == obs.get("entry_hash"))
    rec("H4-CAUSAL-ANCHOR", "exact anchor returned by the write",
        "POST observations returned only ['obs_id']; caller had to SEARCH "
        "the ledger and could pick a wrong-but-real event",
        "returns %s; anchor resolves to THIS OBSERVATION_RECORDED event: %s"
        % (keys, resolves),
        all(k in keys for k in need) and resolves,
        {"returned_keys": keys, "anchor_resolves": resolves})

    # ---- H5 TERMINATED CONTRACT ----------------------------------------
    wid = running("terminated")
    e.req("POST", "/v2/worlds/%s/artifacts" % wid,
          {"kind": "pre", "data_b64": base64.b64encode(b"x").decode()})
    _, ck = e.req("POST", "/v2/worlds/%s/checkpoint" % wid)
    e.req("POST", "/v2/worlds/%s/terminate" % wid)
    forb = {}
    st, _ = e.req("POST", "/v2/worlds/%s/artifacts" % wid,
                  {"kind": "post", "data_b64": base64.b64encode(b"y").decode()})
    forb["artifact"] = st
    st, _ = e.req("POST", "/v2/worlds/%s/hypotheses" % wid,
                  {"statement": "post"})
    forb["hypothesis"] = st
    st, _ = e.req("POST", "/v2/worlds/%s/budget/consume" % wid,
                  {"resource": "ticks", "amount": 1})
    forb["budget"] = st
    perm = {}
    st, _ = e.req("GET", "/v2/worlds/%s/events?limit=5" % wid)
    perm["read_events"] = st
    st, _ = e.req("GET", "/v2/worlds/%s/status" % wid)
    perm["read_status"] = st
    st, _ = e.req("POST", "/v2/worlds/%s/checkpoint" % wid)
    perm["checkpoint"] = st
    st_f, kids = e.req("POST", "/v2/worlds/%s/fork" % wid,
                       {"checkpoint_id": ck["checkpoint_id"],
                        "children": [{"name": "replay"}]})
    perm["fork"] = st_f
    rec("H5-TERMINATED", "terminal-state write gate",
        "artifact/hypothesis/budget writes SUCCEEDED after terminate",
        "forbidden now %s; permitted still %s"
        % (forb, perm),
        all(v == 409 for v in forb.values())
        and all(v == 200 for v in perm.values()),
        {"forbidden": forb, "permitted": perm})

    # ---- H6 D-REPLAY-1 --------------------------------------------------
    wid = running("replay")
    spec = {"action": "encounter", "ticks": 32, "seed": 424242}
    x = committed_exp(wid, spec)
    st_g, got = e.req("GET", "/v2/worlds/%s/experiments/%s"
                      % (wid, x["exp_id"]))
    _, evs = e.req("GET", "/v2/worlds/%s/events?limit=500" % wid)
    comm = [v for v in evs["events"]
            if v["event_type"] == "EXPERIMENT_COMMITTED"]
    sealed = comm[0]["payload"]["spec_hash"] if comm else None
    rec("H6-REPLAY", "action recoverable and hash-verified",
        "no GET for experiments existed; spec could be VERIFIED if already "
        "held, never RECOVERED",
        "GET experiment -> %d; spec byte-equal: %s; recovered hash == sealed "
        "ledger hash: %s"
        % (st_g, got.get("spec") == spec, got.get("spec_hash") == sealed),
        st_g == 200 and got.get("spec") == spec
        and sealed is not None and got.get("spec_hash") == sealed,
        {"spec_equal": got.get("spec") == spec, "sealed": sealed,
         "recovered": got.get("spec_hash")})

    # ---- H7 CLIENT ISOLATION REGRESSION --------------------------------
    victim_world, victim_exp = wid, x["exp_id"]
    e2 = C(a.base_url, a.cacert)
    e2.register(tag + "-intruder")
    st_e, _ = e2.req("GET", "/v2/worlds/%s/experiments/%s"
                     % (victim_world, victim_exp))
    st_l, _ = e2.req("GET", "/v2/worlds/%s/experiments" % victim_world)
    st_ob, _ = e2.req("GET", "/v2/worlds/%s/observations" % victim_world)
    _, mine = e2.req("GET", "/v2/worlds")
    rec("H7-ISOLATION", "new read surfaces do not weaken isolation",
        "isolation was ALREADY correct (7/7); the risk is that new reads "
        "become a cross-experimenter oracle",
        "foreign GET experiment=%d list=%d observations=%d; intruder sees "
        "%d worlds (its own)"
        % (st_e, st_l, st_ob, len(mine["worlds"])),
        st_e in (403, 404) and st_l in (403, 404) and st_ob in (403, 404)
        and len(mine["worlds"]) == 0,
        {"experiment": st_e, "list": st_l, "observations": st_ob,
         "intruder_world_count": len(mine["worlds"])})

    # ---- H8 CORRECTED FINDINGS MUST STAY CORRECTED ----------------------
    _, raw_evs = e.req("GET", "/v2/worlds/%s/events?limit=5" % wid)
    shape_ok = isinstance(raw_evs, dict) and "events" in raw_evs
    _, all_mine = e.req("GET", "/v2/worlds")
    _, running_only = e.req("GET", "/v2/worlds?state=RUNNING")
    _, term_only = e.req("GET", "/v2/worlds?state=TERMINATED")
    st_badstate, _ = e.req("GET", "/v2/worlds?state=NOPE")
    filt_ok = (len(running_only["worlds"]) < len(all_mine["worlds"])
               and len(term_only["worlds"]) >= 1 and st_badstate == 422)
    rec("H8-CORRECTED", "refuted findings stay refuted",
        "I-EVENTS-SHAPE claimed dict-vs-list inconsistency; "
        "I-WORLD-ENUM-UNSCOPED claimed 189 unscoped worlds",
        "events STILL a dict with 'events' key: %s (NOT flipped); "
        "enumeration client-scoped (%d mine) + filters work: %s"
        % (shape_ok, len(all_mine["worlds"]), filt_ok),
        shape_ok and filt_ok,
        {"events_is_dict": shape_ok, "mine": len(all_mine["worlds"]),
         "running": len(running_only["worlds"]),
         "terminated": len(term_only["worlds"]),
         "bad_state_status": st_badstate})

    npass = sum(1 for r in RESULTS if r["verdict"] == "PASS")
    out = {"engine": ver, "at": time.time(), "results": RESULTS,
           "summary": "%d/%d PASS" % (npass, len(RESULTS))}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("\n%d/%d PASS  -> %s" % (npass, len(RESULTS), a.out))
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
