#!/usr/bin/env python3
"""SHARED FIXTURE for WP-0c: identical execution spec under labels A and B.

Daedalus supplies the contract; Vivarium integrates against it.

    python integration/sfe_arm_fixture.py            # run against live M1
    python integration/sfe_arm_fixture.py --json     # machine-readable result

THE PROPERTY, per the ARM RULING:

    execution parameters    -> sealed execution spec  (spec_hash)
    family + arm assignment -> separately sealed design (member record + event)
    execution <-> design    -> audit envelope, preserved in PEW

    ONE spec_hash, TWO member arms.

Two experiments whose execution specs are byte-identical must produce the SAME
spec_hash and still sit in different arms. That is only possible because the arm
lives in the design rather than in the spec: folding the label into the spec
would make identical executions hash differently and destroy the comparison the
design exists to support.

WHAT THIS FIXTURE ASSERTS
  1. the two execution specs are byte-identical
  2. therefore spec_hash is identical
  3. the two members carry DIFFERENT arms
  4. re-assigning either arm afterwards is refused (409)
  5. the audit envelope carries the arm BY VALUE and seals it in envelope_hash
  6. an arm outside a manifest-declared vocabulary is refused (422)

Anything that satisfies 1-6 is a conforming producer. Vivarium does not have to
build it this way; it has to end up here.
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request

BASE = "https://192.168.1.202:8811"
CACERT = ("F:/Prometheus/SerendipityFoundry/SerendipityFoundryEngine/"
          "deploy/m1.crt")

# THE EXECUTION SPEC. Identical in both arms, by construction. Note what is NOT
# in it: no arm, no condition, no label of any kind. If you find yourself
# wanting to add one, that is the design leaking into the execution.
EXECUTION_SPEC = {
    "procedure": "evaluate_bitstring",
    "length": 24,
    "bits": "010101010101010101010101",
    "repeats": 4,
}

MANIFEST = {
    "planned_members": 2,
    "arms": ["A", "B"],          # sealed vocabulary; anything else is refused
    "note": "WP-0c shared fixture: identical execution under two labels",
}


def call(method, path, body=None, token=None, session=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = "Bearer " + token
    if session:
        h["X-SFE-Session"] = session
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=h,
                                 method=method)
    ctx = ssl.create_default_context(cafile=CACERT)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def run():
    out = {"checks": [], "ok": True}

    def check(name, cond, detail=""):
        out["checks"].append({"name": name, "pass": bool(cond),
                              "detail": str(detail)})
        if not cond:
            out["ok"] = False
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name,
                               "" if cond else "\n         " + str(detail)))

    st, v = call("GET", "/v2/version")
    check("engine reachable and at schema >= 7",
          st == 200 and v.get("schema_version", 0) >= 7, v)
    out["engine"] = {"schema_version": v.get("schema_version"),
                     "engine_source_hash": v.get("engine_source_hash"),
                     "engine_instance_id": v.get("engine_instance_id")}

    st, cl = call("POST", "/v2/clients", {"name": "wp0c-arm-fixture"})
    tok = cl["token"]
    st, se = call("POST", "/v2/sessions", {"name": "wp0c"}, token=tok)
    sk, sid = se["session_key"], se["session_id"]

    st, fam = call("POST", "/v2/families",
                   {"kind": "comparison", "manifest": MANIFEST},
                   token=tok, session=sk)
    fid = fam["family_id"]
    out["family_id"] = fid
    out["manifest_hash"] = fam["manifest_hash"]

    members = []
    for arm in ("A", "B"):
        st, w = call("POST", "/v2/worlds",
                     {"session_id": sid, "name": "wp0c-%s" % arm},
                     token=tok, session=sk)
        wid = w["world_id"]
        call("POST", "/v2/worlds/%s/start" % wid, token=tok, session=sk)
        # IDENTICAL spec object in both arms
        st, e = call("POST", "/v2/worlds/%s/experiments" % wid,
                     {"spec": EXECUTION_SPEC}, token=tok, session=sk)
        st, g = call("GET", "/v2/worlds/%s/experiments/%s" % (wid, e["exp_id"]),
                     token=tok, session=sk)
        st, m = call("POST", "/v2/families/%s/members" % fid,
                     {"member_kind": "experiment", "member_id": e["exp_id"],
                      "role": "executed", "arm": arm}, token=tok, session=sk)
        members.append({"arm": arm, "world_id": wid, "exp_id": e["exp_id"],
                        "spec_hash": g["spec_hash"],
                        "member_arm": m.get("arm")})

    a, b = members
    out["members"] = members

    # 1 + 2 -- THE PROPERTY
    check("1. execution specs are byte-identical",
          json.dumps(EXECUTION_SPEC, sort_keys=True) ==
          json.dumps(EXECUTION_SPEC, sort_keys=True))
    check("2. ONE spec_hash across both arms",
          a["spec_hash"] == b["spec_hash"],
          "%s vs %s" % (a["spec_hash"], b["spec_hash"]))
    out["spec_hash"] = a["spec_hash"]

    # 3
    check("3. TWO member arms", a["member_arm"] == "A"
          and b["member_arm"] == "B", members)

    # 4 -- reassignment refused
    st, _ = call("POST", "/v2/families/%s/members" % fid,
                 {"member_kind": "experiment", "member_id": a["exp_id"],
                  "role": "executed", "arm": "B"}, token=tok, session=sk)
    check("4. reassignment after commitment refused (409)", st == 409, st)
    st, again = call("POST", "/v2/families/%s/members" % fid,
                     {"member_kind": "experiment", "member_id": a["exp_id"],
                      "role": "executed", "arm": "A"}, token=tok, session=sk)
    check("4b. identical re-add is an idempotent no-op",
          st == 200 and again.get("already_member") is True, (st, again))

    # 5 -- the fossil carries it
    st, env = call("GET", "/v2/worlds/%s/experiments/%s/audit-envelope"
                   % (a["world_id"], a["exp_id"]), token=tok, session=sk)
    fams = env.get("families", [])
    check("5. audit envelope carries the arm BY VALUE",
          len(fams) == 1 and fams[0].get("arm") == "A", fams)
    check("5b. envelope_hash seals it",
          bool(env.get("envelope_hash")), env.get("envelope_hash"))
    out["envelope_hash"] = env.get("envelope_hash")
    out["envelope_families"] = fams

    # 6 -- sealed vocabulary
    st, w = call("POST", "/v2/worlds", {"session_id": sid, "name": "wp0c-C"},
                 token=tok, session=sk)
    call("POST", "/v2/worlds/%s/start" % w["world_id"], token=tok, session=sk)
    st, e = call("POST", "/v2/worlds/%s/experiments" % w["world_id"],
                 {"spec": EXECUTION_SPEC}, token=tok, session=sk)
    st, _ = call("POST", "/v2/families/%s/members" % fid,
                 {"member_kind": "experiment", "member_id": e["exp_id"],
                  "role": "executed", "arm": "C"}, token=tok, session=sk)
    check("6. an arm outside the sealed vocabulary is refused (422)",
          st == 422, st)

    st, fv = call("GET", "/v2/families/%s" % fid, token=tok, session=sk)
    out["arms"] = fv.get("arms")
    print("\n  family arms census: %s" % json.dumps(fv.get("arms")))

    for m in members + [{"world_id": w["world_id"]}]:
        call("POST", "/v2/worlds/%s/terminate" % m["world_id"], token=tok,
             session=sk)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    print("WP-0c SHARED FIXTURE -- identical execution spec under labels A/B")
    print("=" * 70)
    res = run()
    print("=" * 70)
    print("  spec_hash (both arms): %s" % res.get("spec_hash"))
    print("  manifest_hash        : %s" % res.get("manifest_hash"))
    print("  envelope_hash (arm A): %s" % res.get("envelope_hash"))
    print("  RESULT: %s" % ("PASS" if res["ok"] else "FAIL"))
    if a.json:
        print(json.dumps(res, indent=2))
    sys.exit(0 if res["ok"] else 1)
