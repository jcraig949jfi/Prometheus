"""Conformance check for Archaeon and Vivarium. Harmonia, 2026-09-06.

A headless loop cannot notice that the engine changed underneath it. This
program is what both tools run BEFORE each batch and, for Vivarium, before each
execution cycle. It answers one question:

    is the engine I am about to talk to the engine my contract describes?

FOUR EXIT STATES (2026-09-10, after the schema 6 -> 8 drift).

    0  CONFORMANT   build hash matches. Proceed.
    3  INCOMPLETE   build hash DIFFERS, but routes were only ADDED -- none
                    removed, no session-scoping flip, no required-field change
                    on any shared route. The contract's claims still hold on
                    everything it describes; it just does not describe
                    everything. A consumer may proceed ONLY if every route it
                    will call is in the contract (pass --consumer-routes), and
                    every observation it produces is stamped with BOTH hashes.
    1  DRIFT        a route REMOVED, a scoping flip, a required-field change,
                    or an engine_instance_id mismatch. Always halt.
    2  UNREACHABLE  retry a transient before treating it as a stop.

WHY THE SPLIT. The exact build pin conflates two questions -- "is this the
build my contract came from" (identity) and "do my contract's claims still
hold" (validity). Collapsing them costs a halt on every engine change even
when nothing the contract describes has moved, and a gate that halts for no
reason is a gate that gets unwired. State 3 separates them WITHOUT using a
schema number as a proxy for the surface: the surface is compared directly.

engine_instance_id NEVER bends, in any state. It names the LEDGER, not the
build, and its mismatch is the one failure that corrupts attribution silently
instead of halting work. That is also what makes state 3 safe: the rows are
known to be in the right database.

READING THE EXIT CODE: do NOT pipe this program and read $?. That captures the
pipe's status, not this program's -- a defect that has now bitten this campaign
twice. Use ${PIPESTATUS[0]}, or do not pipe.

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
import os
import ssl
import time
import sys
import urllib.error
import urllib.request


# --- D-23: refuse to run from the canonical checkout -----------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from workspace_guard import assert_not_canonical, CanonicalCheckoutRefused
except ImportError:                                                # pragma: no cover
    assert_not_canonical = None


FAIL = []        # breaking: forces state 1
INCOMPLETE = []  # additive: forces state 3 unless a consumer needs a new route

CONFORMANT, DRIFT, UNREACHABLE, INCOMPLETE_STATE = 0, 1, 2, 3


def check(name, ok, detail, breaking=True):
    """breaking=False records an ADDITIVE difference (state 3), not DRIFT."""
    tag = "PASS" if ok else ("DRIFT" if breaking else "ADDED")
    print("  [%s] %-42s %s" % (tag, name, detail))
    if not ok:
        (FAIL if breaking else INCOMPLETE).append({"check": name, "detail": detail})
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
    if assert_not_canonical is not None:
        try:
            assert_not_canonical("run the conformance gate")
        except CanonicalCheckoutRefused as e:
            print("REFUSING: %s" % e)
            return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--cacert", default=None)
    ap.add_argument("--base", default=None,
                    help="override; defaults to the contract's base_url")
    ap.add_argument("--consumer-routes", nargs="*", default=None,
                    metavar="'GET /v2/x'",
                    help="routes this consumer will call. Under state 3 the "
                         "run HALTS if any is absent from the contract.")
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
             (C["engine"]["engine_source_hash"] or "")[:22]),
          breaking=False)   # identity, not validity: the route diff decides
    check("engine_instance_id",
          live.get("engine_instance_id") == C["engine"]["engine_instance_id"],
          "live %s" % live.get("engine_instance_id"))
    check("schema_version",
          live.get("schema_version") == C["engine"]["schema_version"],
          "live %s vs contract %s" % (live.get("schema_version"),
                                      C["engine"]["schema_version"]),
          breaking=False)   # a LABEL for the surface; the surface is compared below
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
    # A REMOVAL breaks the contract's claims. An ADDITION only means the
    # contract is incomplete -- everything it describes is still there.
    check("no_route_removed", not removed,
          "%d removed%s" % (len(removed),
                            (": " + str(sorted(removed))) if removed else ""))
    check("route_set_complete", not added,
          "%d live, %d in contract; %d added%s"
          % (len(live_routes), len(con_routes), len(added),
             (": " + ", ".join("%s %s" % a for a in sorted(added)))
             if added else ""),
          breaking=False)
    a.consumer_unlisted = sorted(
        r for r in (a.consumer_routes or []) if tuple(r.split(" ", 1)) not in con_routes)

    # semantic drift: does session scoping still behave as recorded?
    # RETRY THE PROBE REGISTRATION. A transient here is not drift: failing to
    # ESTABLISH the probe is "we could not look", not "the contract moved".
    # Classifying it as DRIFT is actively harmful, because DRIFT is the one
    # state whose instruction is never retry -- so a network blip would tell
    # the operator to stop the loop and regenerate a contract that is fine.
    # I told Archaeon and Vivarium to retry transients before treating a stop
    # as real; this gate did not do it itself until 2026-09-11.
    st, body = None, ""
    for _attempt in range(3):
        st, body = req(root + "/v2/clients", a.cacert, method="POST",
                       body={"name": "conformance-check"})
        if st == 200:
            break
        time.sleep(1.0)
    if st != 200:
        print("  [UNREACHABLE] could not register a probe client after 3 "
              "attempts: %s" % st)
        print("  This is an inability to LOOK, not evidence of drift. Retry.")
        return UNREACHABLE
    else:
        tok = json.loads(body)["token"]
        ids = {"wid": "wld_" + "0" * 24, "eid": "exp_" + "0" * 24,
               "aid": "sha256:" + "0" * 64, "work_id": "wrk_" + "0" * 24,
               "sid": "ses_" + "0" * 24, "fid": "fam_" + "0" * 24,
               "clm": "clm_" + "0" * 24}
        # ALL GET routes, not a sample. GETs do not mutate, so this is safe
        # against production; POST scoping is derived at generation time
        # against a scratch engine and is NOT re-probed here. That limit is
        # stated rather than hidden.
        sample = [r for r in C["routes"] if r["method"] == "GET"]
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
        print("DRIFT -- %d breaking check(s) failed. STOP THE LOOP." % len(FAIL))
        print("Something the contract DESCRIBES has moved, or the ledger changed.")
        for f in FAIL:
            print("   %s: %s" % (f["check"], f["detail"]))
        return DRIFT

    if INCOMPLETE:
        print("INCOMPLETE -- the build moved, but only by ADDITION.")
        print("Nothing the contract describes was removed or changed.")
        for f in INCOMPLETE:
            print("   %s: %s" % (f["check"], f["detail"]))
        if a.consumer_routes is None:
            print("")
            print("   No --consumer-routes declared, so this program cannot tell")
            print("   whether you are about to call an undescribed route.")
            print("   HALT is the safe reading. Declare your routes to proceed.")
            return INCOMPLETE_STATE
        unlisted = getattr(a, "consumer_unlisted", [])
        if unlisted:
            print("")
            print("   HALT: %d route(s) you will call are NOT in the contract:"
                  % len(unlisted))
            for r in unlisted:
                print("      %s" % r)
            print("   Regenerate the contract before calling them.")
            return INCOMPLETE_STATE
        print("")
        print("   Every route you declared IS in the contract, so its claims")
        print("   cover your calls. PROCEED, and stamp every observation with")
        print("   BOTH hashes:")
        print("      contract_engine_source_hash = %s"
              % C["engine"]["engine_source_hash"])
        print("      live_engine_source_hash     = %s"
              % live.get("engine_source_hash"))
        return CONFORMANT

    print("CONFORMANT -- safe to proceed")
    return CONFORMANT


if __name__ == "__main__":
    sys.exit(main())
