#!/usr/bin/env python3
"""LIVE R2-1 audit-path check -- Daedalus, 2026-09-04.

Proves, against the DEPLOYED daemon, that the intended direction works:

    producer -> SFE sealed envelope -> (PEW) -> third-party auditor

and that the thing the directive forbids does NOT work: an arbitrary
investigator cannot bypass SFE authorization to read the material.
"""
from __future__ import annotations

import argparse
import json
import ssl
import time
import urllib.error
import urllib.request

R = []


class C:
    def __init__(self, base, ca):
        self.base = base.rstrip("/")
        self.ctx = ssl.create_default_context(cafile=ca)
        self.token = None

    def req(self, m, p, body=None):
        d = json.dumps(body).encode() if body is not None else None
        h = {"content-type": "application/json"}
        if self.token:
            h["authorization"] = "Bearer " + self.token
        r = urllib.request.Request(self.base + p, data=d, headers=h, method=m)
        try:
            with urllib.request.urlopen(r, context=self.ctx, timeout=30) as z:
                return z.status, json.loads(z.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            b = e.read().decode()
            try:
                return e.code, json.loads(b or "{}")
            except json.JSONDecodeError:
                return e.code, {"raw": b}

    def register(self, n):
        _, c = self.req("POST", "/v2/clients", {"name": n})
        self.token = c["token"]
        _, s = self.req("POST", "/v2/sessions", {"name": n})
        return s["session_id"]


def rec(cid, title, detail, ok):
    R.append({"check": cid, "title": title, "detail": detail,
              "verdict": "PASS" if ok else "FAIL"})
    print("[%s] %-26s %s" % ("PASS" if ok else "FAIL", cid, detail))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--cacert", required=True)
    ap.add_argument("--out", default="live_r2_1_results.json")
    a = ap.parse_args()

    prod = C(a.base_url, a.cacert)
    _, ver = prod.req("GET", "/v2/version")
    print("live source_commit: %s" % ver.get("source_commit"))
    print("live schema        : %s\n" % ver.get("schema_version"))

    tag = "r21-%d" % int(time.time())
    sid = prod.register(tag + "-producer")
    _, w = prod.req("POST", "/v2/worlds",
                    {"session_id": sid, "name": "audit", "seed_root": 424242,
                     "sharing_policy": "ISOLATED",
                     "budget": {"ticks": {"limit": 9,
                                          "enforcement": "enforceable"}}})
    wid = w["world_id"]
    prod.req("POST", "/v2/worlds/%s/start" % wid)
    _, h = prod.req("POST", "/v2/worlds/%s/hypotheses" % wid,
                    {"statement": "H"})
    spec = {"action": "encounter", "ticks": 32}
    _, x = prod.req("POST", "/v2/worlds/%s/experiments" % wid,
                    {"spec": spec, "hyp_id": h["hyp_id"], "commit": True})
    eid = x["exp_id"]
    _, obs = prod.req("POST", "/v2/worlds/%s/observations" % wid,
                      {"exp_id": eid, "content": {"score": 0.5},
                       "outcome": "SURVIVED"})

    # 1. PRODUCER exports the sealed envelope
    st_e, env = prod.req("GET", "/v2/worlds/%s/experiments/%s/audit-envelope"
                         % (wid, eid))
    have = {
        "engine_instance": bool(env.get("engine", {}).get("engine_instance_id")),
        "engine_build": bool(env.get("engine", {}).get("engine_source_hash")),
        "world_config": env.get("world", {}).get("seed_root") == 424242
        and env.get("world", {}).get("budget", {}).get("ticks", {}).get("limit") == 9,
        "sealed_spec": env.get("experiment", {}).get("spec") == spec,
        "hash_matches_ledger": (env.get("sealed_spec_hash_in_ledger")
                                == env.get("experiment", {}).get("spec_hash")),
        "recomputed_matches": (env.get("spec_hash_recomputed")
                               == env.get("experiment", {}).get("spec_hash")),
        "observation": bool(env.get("observations")),
        "anchor": any(z["event_id"] == obs["event_id"]
                      for z in env.get("anchors", [])),
        "envelope_hash": bool(env.get("envelope_hash")),
    }
    rec("R21-ENVELOPE", "producer exports sealed material",
        "GET audit-envelope -> %d; identities present: %s"
        % (st_e, {k: v for k, v in have.items()}),
        st_e == 200 and all(have.values()))

    # 2. THIRD PARTY: envelope DENIED (isolation must NOT be weakened)
    aud = C(a.base_url, a.cacert)
    aud.register(tag + "-auditor")
    st_d, _ = aud.req("GET", "/v2/worlds/%s/experiments/%s/audit-envelope"
                      % (wid, eid))
    st_x, _ = aud.req("GET", "/v2/worlds/%s/experiments/%s" % (wid, eid))
    st_o, _ = aud.req("GET", "/v2/worlds/%s/observations" % wid)
    _, mine = aud.req("GET", "/v2/worlds")
    rec("R21-ISOLATION", "third party still cannot read the engine",
        "envelope=%d experiment=%d observations=%d; auditor enumerates %d "
        "worlds" % (st_d, st_x, st_o, len(mine["worlds"])),
        st_d == 403 and st_x == 403 and st_o == 403
        and len(mine["worlds"]) == 0)

    # 3. THIRD PARTY: anchor verification WITHOUT the producer's credential
    st_v, v = aud.req("POST", "/v2/audit/verify-anchor",
                      {"world_id": wid, "event_id": obs["event_id"],
                       "entry_hash": obs["entry_hash"], "exp_id": eid,
                       "obs_id": obs["obs_id"]})
    rec("RSFE1-VERIFY", "auditor verifies the genuine anchor",
        "-> %d valid=%s checks=%s engine_instance=%s"
        % (st_v, v.get("valid"), v.get("checks"),
           (v.get("engine") or {}).get("engine_instance_id")),
        st_v == 200 and v.get("valid") is True)

    # 4. WRONG-BUT-REAL event must be REJECTED (the D1 hazard)
    _, evs = prod.req("GET", "/v2/worlds/%s/events?limit=200" % wid)
    created = [z for z in evs["events"] if z["event_type"] == "WORLD_CREATED"][0]
    st_w, vw = aud.req("POST", "/v2/audit/verify-anchor",
                       {"world_id": wid, "event_id": created["event_id"],
                        "entry_hash": created["entry_hash"], "exp_id": eid,
                        "obs_id": obs["obs_id"]})
    rec("RSFE1-WRONG-EVENT", "real-but-wrong event rejected",
        "WORLD_CREATED pair is genuine (exists=%s hash_ok=%s) but binds_exp=%s "
        "-> valid=%s"
        % (vw.get("checks", {}).get("event_exists"),
           vw.get("checks", {}).get("entry_hash_matches"),
           vw.get("checks", {}).get("binds_exp_id"), vw.get("valid")),
        st_w == 200 and vw.get("checks", {}).get("event_exists") is True
        and vw.get("checks", {}).get("entry_hash_matches") is True
        and vw.get("valid") is False)

    # 5. verify must disclose nothing
    blob = json.dumps(v)
    leak = [s for s in ("score", "encounter", "refs") if s in blob]
    rec("RSFE1-NO-DISCLOSURE", "verify is not a content oracle",
        "response keys=%s; leaked tokens=%s" % (sorted(v), leak),
        not leak and set(v) <= {"valid", "checks", "engine", "event_type",
                                "event_seq", "world_index"})

    # 6. auth wall still stands
    anon = C(a.base_url, a.cacert)
    st_a, _ = anon.req("POST", "/v2/audit/verify-anchor",
                       {"world_id": wid, "event_id": obs["event_id"],
                        "entry_hash": obs["entry_hash"]})
    rec("RSFE1-AUTH-WALL", "anonymous verification refused",
        "no token -> %d" % st_a, st_a == 401)

    # 7. engine instance identity is present and stable across calls
    _, v2 = aud.req("POST", "/v2/audit/verify-anchor",
                    {"world_id": wid, "event_id": obs["event_id"],
                     "entry_hash": obs["entry_hash"]})
    iid1 = (v.get("engine") or {}).get("engine_instance_id")
    iid2 = (v2.get("engine") or {}).get("engine_instance_id")
    rec("RSFE2-INSTANCE-ID", "engine instance identity in the anchor",
        "instance=%s stable=%s build=%s"
        % (iid1, iid1 == iid2,
           (v.get("engine") or {}).get("engine_source_hash", "")[:20]),
        bool(iid1) and iid1 == iid2)

    n = sum(1 for r in R if r["verdict"] == "PASS")
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump({"engine": ver, "at": time.time(), "results": R,
                   "envelope_hash": env.get("envelope_hash"),
                   "summary": "%d/%d PASS" % (n, len(R))}, fh, indent=1)
    print("\n%d/%d PASS -> %s" % (n, len(R), a.out))
    return 0 if n == len(R) else 1


if __name__ == "__main__":
    raise SystemExit(main())
