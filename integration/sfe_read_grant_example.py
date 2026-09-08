#!/usr/bin/env python3
"""The cross-seat read contract, end to end -- and the two commands the
harmonia-m2 seat needs to run.

    python integration/sfe_read_grant_example.py --demo
        Runs the whole flow with two throwaway clients this script creates, so
        you can see it work without anyone's real token. Proves the commands
        below before you run them for real.

    python integration/sfe_read_grant_example.py --grant \
        --token <harmonia-m2 token> --grantee cli_1029e9255a074157a1b3ba1e
        THE REAL THING. Must be run with harmonia-m2's own credentials: only
        the owner of a world may put it in a scope, and only the owner of a
        scope may grant on it. Daedalus cannot do this for you and should not
        be able to.

    python integration/sfe_read_grant_example.py --consume --token <archaeon token>
        What Archaeon does afterwards.

Why a read SCOPE and not a topology group: _may_cross keys on
worlds.topology_group, so granting over a group would confer artifact-IMPORT
eligibility as a side effect, and 98 of harmonia-m2's 189 worlds are in no group
at all -- putting them in one would mean MUTATING live worlds. A read scope
writes nothing on the world.
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


def call(method, path, body=None, token=None, session=None, cacert=CACERT):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = "Bearer " + token
    if session:
        h["X-SFE-Session"] = session
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=h,
                                 method=method)
    ctx = ssl.create_default_context(cafile=cacert)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def session_for(token):
    st, s = call("POST", "/v2/sessions", {"name": "read-grant"}, token=token)
    if st != 200:
        sys.exit("could not open a session: %s %s" % (st, s))
    return s["session_key"]


# ---------------------------------------------------------------- THE GRANT
def grant(owner_token, grantee, scope_name, note, world_filter=None):
    """THE TWO COMMANDS, as one idempotent operation.

    1. create a read scope and add the worlds you own to it
    2. grant read on that scope to the grantee

    Nothing is written on any world. Revoke at any time with
    POST /v2/read/grants/{grant_id}/revoke."""
    sk = session_for(owner_token)

    st, ws = call("GET", "/v2/worlds?limit=1000", token=owner_token, session=sk)
    if st != 200:
        sys.exit("could not list your worlds: %s %s" % (st, ws))
    worlds = ws["worlds"] if isinstance(ws, dict) else ws
    ids = [w["world_id"] for w in worlds
           if world_filter is None or world_filter(w)]
    print("  you own %d worlds; %d selected for the scope" % (len(worlds),
                                                              len(ids)))

    st, sc = call("POST", "/v2/read/scopes", {"name": scope_name, "note": note},
                  token=owner_token, session=sk)
    if st != 200:
        sys.exit("could not create the scope: %s %s" % (st, sc))
    sid = sc["scope_id"]
    print("  scope %s created" % sid)

    for i in range(0, len(ids), 200):                 # chunked; idempotent
        st, add = call("POST", "/v2/read/scopes/%s/worlds" % sid,
                       {"world_ids": ids[i:i + 200]},
                       token=owner_token, session=sk)
        if st != 200:
            sys.exit("could not add worlds: %s %s" % (st, add))
    st, sc = call("GET", "/v2/read/scopes", token=owner_token, session=sk)
    n = [x for x in sc["scopes"] if x["scope_id"] == sid][0]["worlds"]
    print("  scope now holds %d worlds" % n)

    st, g = call("POST", "/v2/read/scopes/%s/grants" % sid,
                 {"grantee_client_id": grantee,
                  "note": "read-only corpus for archaeology"},
                 token=owner_token, session=sk)
    if st != 200:
        sys.exit("could not grant: %s %s" % (st, g))
    print("  GRANTED %s -> %s   (grant_id %s)" % (sid, grantee, g["grant_id"]))
    print("\n  revoke with:")
    print("    POST /v2/read/grants/%s/revoke" % g["grant_id"])
    return sid, g["grant_id"]


# -------------------------------------------------------------- THE CONSUMER
def consume(token, scope=None, limit=200):
    """What Archaeon does. Note the corpus census: record it in every survey,
    because it is the declared population your detectors ran over."""
    sk = session_for(token)

    st, gr = call("GET", "/v2/read/grants", token=token, session=sk)
    print("  grants to me: %d" % len(gr.get("granted_to_me", [])))
    for g in gr.get("granted_to_me", []):
        print("    scope=%s granted_by=%s" % (g["scope_id"], g["granted_by"]))

    q = "/v2/read/worlds?limit=%d" % limit + (("&scope=" + scope) if scope else "")
    st, w = call("GET", q, token=token, session=sk)
    print("  readable worlds: %d" % len(w.get("worlds", [])))
    for t in w.get("corpus_tenancy", []):
        print("    tenancy: %s -> %d worlds" % (t["client_id"], t["worlds"]))

    # resolve the outcome through the REGISTERED measurement, so the reader
    # never guesses which field is the outcome
    st, ms = call("GET", "/v2/measurements?name=evaluate_bitstring.score",
                  token=token, session=sk)
    mid = (ms.get("measurements") or [{}])[0].get("identity_hash")
    q = ("/v2/read/observations?limit=%d&evidence_class=ENGINE_WORK_RESULT"
         % limit) + (("&scope=" + scope) if scope else "")         + (("&measurement=" + mid) if mid else "")
    st, o = call("GET", q, token=token, session=sk)
    obs = o.get("observations", [])
    corpus = o.get("corpus", {})
    print("  observations: %d  (engine-attested only)" % len(obs))
    print("  CORPUS CENSUS -- record this in the survey:")
    print("    " + json.dumps(corpus))

    cm = corpus.get("measurement")
    if cm:
        print("  measurement %s v%s -> value_path=%s direction=%s"
              % (cm["name"], cm["version"], cm["value_path"], cm["direction"]))
        print("    resolved=%d unresolved=%d" % (cm["resolved"],
                                                 cm["unresolved"]))
        for ob in obs[:3]:
            m = ob.get("measured") or {}
            print("    %s -> found=%s value=%s in_range=%s"
                  % (ob["obs_id"][:16], m.get("found"), m.get("value"),
                     m.get("in_declared_range")))
    return obs


def demo():
    """Two throwaway clients and REAL data: the corpus owner runs an
    experiment, records an engine-attested observation, then grants read on it.
    Proves the data path, not just the grant machinery."""
    st, owner = call("POST", "/v2/clients", {"name": "demo-corpus-owner"})
    st, arch = call("POST", "/v2/clients", {"name": "demo-archaeologist"})
    ot, at = owner["token"], arch["token"]
    st, sess = call("POST", "/v2/sessions", {"name": "demo"}, token=ot)
    osk, sid_sess = sess["session_key"], sess["session_id"]

    st, w = call("POST", "/v2/worlds", {"session_id": sid_sess,
                 "name": "demo-world"}, token=ot, session=osk)
    wid = w["world_id"]
    call("POST", "/v2/worlds/%s/start" % wid, token=ot, session=osk)
    st, e = call("POST", "/v2/worlds/%s/experiments" % wid,
                 {"spec": {"procedure": "bitstring", "length": 24},
                  "enqueue": True}, token=ot, session=osk)
    st, wk = call("POST", "/v2/work/claim", {"worker_id": "demo", "world_id": wid},
                  token=ot, session=osk)
    work = wk["work"]
    call("POST", "/v2/work/%s/complete" % work["work_id"],
         {"worker_id": "demo", "claim_id": work["claim_id"],
          "result": {"score": 0.75},
          "attestation": {"executed_config": {"procedure": "bitstring",
                                              "length": 24}}},
         token=ot, session=osk)
    call("POST", "/v2/worlds/%s/observations" % wid,
         {"exp_id": e["exp_id"], "outcome": "SURVIVED",
          "work_id": work["work_id"],
          "content": {"result": {"score": 0.75, "solved": False}}},
         token=ot, session=osk)
    print("  corpus owner produced 1 engine-attested observation in %s" % wid)

    sid, gid = grant(ot, arch["client_id"], "demo scope",
                     "created by sfe_read_grant_example --demo")
    print("\n-- as the archaeologist, AFTER the grant --")
    got = consume(at, scope=sid)
    assert got, "the grant produced no readable observations"
    print("\n-- after revocation --")
    call("POST", "/v2/read/grants/%s/revoke" % gid, token=ot, session=osk)
    gone = consume(at)
    assert not gone, "revocation did not take effect"
    print("\n  DEMO OK: granted -> readable, revoked -> not readable")
    call("POST", "/v2/worlds/%s/terminate" % wid, token=ot, session=osk)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--grant", action="store_true")
    ap.add_argument("--consume", action="store_true")
    ap.add_argument("--token")
    ap.add_argument("--grantee", default="cli_1029e9255a074157a1b3ba1e")
    ap.add_argument("--scope-name", default="harmonia-m2 executed corpus")
    ap.add_argument("--scope")
    a = ap.parse_args()
    if a.demo:
        demo()
    elif a.grant:
        if not a.token:
            sys.exit("--grant needs --token (the CORPUS OWNER's, not mine)")
        grant(a.token, a.grantee, a.scope_name,
              "read-only archaeology corpus")
    elif a.consume:
        if not a.token:
            sys.exit("--consume needs --token (the GRANTEE's)")
        consume(a.token, scope=a.scope)
    else:
        ap.print_help()
