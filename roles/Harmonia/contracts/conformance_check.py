"""Conformance check for Archaeon and Vivarium. Harmonia, 2026-09-06.

A headless loop cannot notice that the engine changed underneath it. This
program is what both tools run BEFORE each batch and, for Vivarium, before each
execution cycle. It answers one question:

    is the engine I am about to talk to the engine my contract describes?

Exit 0 conform, 1 DRIFT, 2 unreachable. Non-zero must stop the loop. A tool
that keeps running through drift produces fossils attributed to a build that
was not the build, which is the failure this whole program has been chasing.

WHY THIS IS NOT OPTIONAL. Twice in this program a live engine's reported
source_commit named a commit that did not contain the running code, and both
times only the SOURCE HASH caught it. A deterministic tool has no judgement to
fall back on, so the check has to be mechanical and it has to fail closed.

Checks, in order of what they protect:
  1. reachable
  2. engine_source_hash EXACTLY equals the contract's           <- build identity
  3. engine_instance_id EXACTLY equals the contract's           <- ledger identity
  4. schema_version equals the contract's
  5. the live route set equals the contract's route set         <- surface drift
  6. session scoping still matches for a sample of routes       <- semantic drift
  7. science_profile and session_enforcement as recorded        <- consequence
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request

FAIL = []


def check(name, ok, detail):
    print("  [%s] %-42s %s" % ("PASS" if ok else "DRIFT", name, detail))
    if not ok:
        FAIL.append({"check": name, "detail": detail})
    return ok


def req(url, cafile=None, token=None, session=None, method="GET", body=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = "Bearer " + token
    if session:
        h["X-SFE-Session"] = session
    d = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=d, headers=h, method=method)
    ctx = ssl.create_default_context(cafile=cafile) if cafile else None
    kw = {"context": ctx} if ctx else {}
    try:
        with urllib.request.urlopen(r, timeout=20, **kw) as z:
            return z.status, z.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:                                         # noqa: BLE001
        return None, repr(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--cacert", default=None)
    ap.add_argument("--base", default=None,
                    help="override; defaults to the contract's base_url")
    a = ap.parse_args()
    C = json.load(open(a.contract, encoding="utf-8"))
    base = (a.base or C["engine"]["base_url"]).rstrip("/")
    root = base[:-3] if base.endswith("/v2") else base

    print("=" * 74)
    print("SFE CONFORMANCE CHECK")
    print("=" * 74)
    print("  contract describes : %s  schema %s"
          % (C["engine"]["engine_instance_id"], C["engine"]["schema_version"]))
    print("  target             : %s\n" % base)

    st, body = req(root + "/v2/version", a.cacert)
    if st != 200:
        print("  [UNREACHABLE] %s -> %s" % (root + "/v2/version", st))
        return 2
    live = json.loads(body)

    check("engine_reachable", True, "/v2/version -> 200")
    check("engine_source_hash",
          live.get("engine_source_hash") == C["engine"]["engine_source_hash"],
          "live %s vs contract %s"
          % ((live.get("engine_source_hash") or "")[:22],
             (C["engine"]["engine_source_hash"] or "")[:22]))
    check("engine_instance_id",
          live.get("engine_instance_id") == C["engine"]["engine_instance_id"],
          "live %s" % live.get("engine_instance_id"))
    check("schema_version",
          live.get("schema_version") == C["engine"]["schema_version"],
          "live %s vs contract %s" % (live.get("schema_version"),
                                      C["engine"]["schema_version"]))
    check("science_profile",
          live.get("science_profile") == C["engine"]["science_profile"],
          "live %s vs contract %s" % (live.get("science_profile"),
                                      C["engine"]["science_profile"]))
    check("session_enforcement",
          live.get("session_enforcement") == C["engine"]["session_enforcement"],
          "live %s vs contract %s" % (live.get("session_enforcement"),
                                      C["engine"]["session_enforcement"]))

    st, body = req(root + "/v2/openapi.json", a.cacert)
    spec = json.loads(body) if st == 200 else {"paths": {}}
    live_routes = {(m.upper(), p) for p, ops in spec["paths"].items()
                   for m in ops if m.upper() in ("GET", "POST")}
    con_routes = {(r["method"], r["path"]) for r in C["routes"]}
    added, removed = live_routes - con_routes, con_routes - live_routes
    check("route_set_identical", not added and not removed,
          "%d live, %d in contract; added=%s removed=%s"
          % (len(live_routes), len(con_routes),
             sorted(added) or "none", sorted(removed) or "none"))

    # semantic drift: does session scoping still behave as recorded?
    st, body = req(root + "/v2/clients", a.cacert, method="POST",
                   body={"name": "conformance-check"})
    if st != 200:
        check("session_scoping_sample", False,
              "could not register a client to probe with: %s" % st)
    else:
        tok = json.loads(body)["token"]
        ids = {"wid": "wld_" + "0" * 24, "eid": "exp_" + "0" * 24,
               "aid": "sha256:" + "0" * 64, "work_id": "wrk_" + "0" * 24,
               "sid": "ses_" + "0" * 24, "fid": "fam_" + "0" * 24,
               "clm": "clm_" + "0" * 24}
        sample = [r for r in C["routes"] if r["method"] == "GET"][:8]
        bad = []
        for r in sample:
            u = r["path"]
            for k, v in ids.items():
                u = u.replace("{%s}" % k, v)
            for q in r.get("required_query", []):
                u += ("&" if "?" in u else "?") + q + "=probe"
            stx, bx = req(root + u, a.cacert, token=tok,
                          session="not-a-session-key")
            scoped = (stx == 422 and "SESSION_MALFORMED" in bx)
            if scoped != r["requires_session_key"]:
                bad.append("%s %s: contract says scoped=%s, engine says %s"
                           % (r["method"], r["path"],
                              r["requires_session_key"], scoped))
        check("session_scoping_sample", not bad,
              "%d GET routes probed; %s" % (len(sample), bad or "all match"))

    print("\n" + "=" * 74)
    if FAIL:
        print("DRIFT DETECTED -- %d check(s) failed. STOP THE LOOP." % len(FAIL))
        print("The engine is not the engine this contract describes.")
        print("Regenerate the contract, re-read it, and only then resume.")
        for f in FAIL:
            print("   %s: %s" % (f["check"], f["detail"]))
        return 1
    print("CONFORMANT -- safe to proceed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
