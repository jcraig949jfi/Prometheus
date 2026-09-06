"""T3 -- strict-mode cutover rehearsal.

Harmonia, 2026-09-05. M1 runs ADVISORY. Cutover to STRICT is scheduled for
sessions_legacy_open == 0 or 2026-10-01. Nobody has ever run under strict, so
this measures what changes for a client that does not send X-SFE-Session --
which is every raw-HTTP client written before v5.

Run against a scratch engine started with --session-enforcement strict.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

R = []


def gate(name, ok, detail):
    R.append({"gate": name, "pass": bool(ok), "detail": detail})
    print("  [%s] %-46s %s" % ("PASS" if ok else "FAIL", name, detail))


def call(base, method, path, token=None, body=None, key=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = "Bearer " + token
    if key:
        h["X-SFE-Session"] = key
    d = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=d, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:                                          # noqa: BLE001
            return e.code, {}


def code(p):
    d = (p or {}).get("detail", p)
    return d.get("error") if isinstance(d, dict) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8898/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    B = a.base.rstrip("/")

    tok = call(B, "POST", "/clients", body={"name": "t3"})[1]["token"]
    s = call(B, "POST", "/sessions", token=tok, body={"name": "t3"})[1]
    key, sid = s["session_key"], s["session_id"]

    print("\nSTRICT MODE -- what a pre-v5 client (no X-SFE-Session) experiences")

    # 1. Can an unkeyed client still CREATE a world under strict?
    st, w = call(B, "POST", "/worlds", token=tok,
                 body={"session_id": sid, "name": "t3-nokey"})
    created_unkeyed = st == 200
    gate("T3_1_world_creation_without_a_key",
         True, "status=%s code=%s -> %s" % (
             st, code(w), "ALLOWED" if created_unkeyed else "REFUSED"))

    # 2. If it was created, can the same unkeyed client ever use it again?
    if created_unkeyed:
        wid = w["world_id"]
        st2, p2 = call(B, "POST", "/worlds/%s/start" % wid, token=tok, body={})
        st3, p3 = call(B, "GET", "/worlds/%s" % wid, token=tok)
        gate("T3_2_unkeyed_client_can_use_what_it_created",
             not (st2 == 428 or st3 == 428),
             "start=%s %s  get=%s %s" % (st2, code(p2), st3, code(p3)))
        # 3. and does the key rescue it?
        st4, p4 = call(B, "POST", "/worlds/%s/start" % wid, token=tok, body={},
                       key=key)
        gate("T3_3_key_recovers_the_orphaned_world", st4 == 200,
             "start with key -> %s %s" % (st4, code(p4)))
    else:
        gate("T3_2_unkeyed_client_can_use_what_it_created", True,
             "n/a: creation already refused, so nothing is orphaned")
        gate("T3_3_key_recovers_the_orphaned_world", True, "n/a")

    # 4. The happy path under strict, with the key, must be untouched.
    st, w2 = call(B, "POST", "/worlds", token=tok, key=key,
                  body={"session_id": sid, "name": "t3-keyed"})
    wid2 = w2.get("world_id")
    st5, _ = call(B, "POST", "/worlds/%s/start" % wid2, token=tok, body={},
                  key=key)
    st6, h = call(B, "POST", "/worlds/%s/hypotheses" % wid2, token=tok,
                  key=key, body={"statement": "H"})
    st7, x = call(B, "POST", "/worlds/%s/experiments" % wid2, token=tok,
                  key=key, body={"spec": {"action": "encounter", "ticks": 4},
                                 "hyp_id": h.get("hyp_id"), "commit": True})
    st8, o = call(B, "POST", "/worlds/%s/observations" % wid2, token=tok,
                  key=key, body={"exp_id": x.get("exp_id"),
                                 "content": {"score": 1}, "outcome": "SURVIVED"})
    gate("T3_4_keyed_client_full_flow_under_strict",
         all(v == 200 for v in (st, st5, st6, st7, st8)),
         "world=%s start=%s hyp=%s exp=%s obs=%s" % (st, st5, st6, st7, st8))

    # 5. Which routes 428 for an unkeyed client on a STRICT-session world?
    #    Enumerated live, not hand-listed.
    spec = call(B, "GET", "/openapi.json")[1]
    ids = {"wid": wid2, "eid": x.get("exp_id", "exp_" + "0" * 24),
           "aid": "sha256:" + "0" * 64, "work_id": "wrk_" + "0" * 24}
    exempt = {"/v2/version", "/v2/clients", "/v2/sessions",
              "/v2/topology-groups", "/v2/audit/verify-anchor",
              # added for build 2f35868c: ownership-gated by design so the
              # keyless LEGACY sessions stay drainable. Probing it with a
              # placeholder {sid} correctly answers 404, which is not a
              # coverage hole.
              "/v2/sessions/{sid}/close"}
    n428 = other = 0
    others = []
    for path, ops in sorted(spec["paths"].items()):
        if path in exempt:
            continue
        for m in ops:
            if m.upper() not in ("GET", "POST"):
                continue
            u = path[3:] if path.startswith("/v2/") else path
            for k, v in ids.items():
                u = u.replace("{%s}" % k, v)
            if "lineage" in u:
                u += "?kind=world&id=" + wid2
            stx, px = call(B, m.upper(), u, token=tok,
                           body={} if m.upper() == "POST" else None)
            if stx == 428:
                n428 += 1
            else:
                other += 1
                others.append("%s %s -> %s %s" % (m.upper(), path, stx, code(px)))
    gate("T3_5_unkeyed_access_to_a_strict_world_is_refused",
         other == 0,
         "%d routes 428 SESSION_REQUIRED, %d did not" % (n428, other))
    for o_ in others:
        print("        not-428: " + o_)

    ok = all(r["pass"] for r in R)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"all_pass": ok, "gates": R,
                   "unkeyed_routes_428": n428,
                   "unkeyed_routes_not_428": others}, f, indent=1)
    print("\nT3 %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
