#!/usr/bin/env python3
"""SFE DEPLOYMENT ATTESTATION -- CT-SFE-1.

Answers one question before an experiment runs: AM I TALKING TO THE DAEMON I
THINK I AM?

Born from a real incident, 2026-09-04. Six engine repairs were committed,
tested (119 green) and pushed. The running M2 engine kept serving the OLD build
for hours afterwards, because the watchdog relaunches whatever is on disk only
when the health probe FAILS -- and a stale-but-healthy engine never fails a
health probe. Every "the fix is in" statement in that window was true about the
source tree and false about the service.

Four states, and the gap between them is where this class of error lives:

    CODE_FIXED  !=  SERVICE_DEPLOYED  !=  LIVE_VERIFIED  !=  QUALIFIED

This script decides the second and third. It is deliberately small, has no
dependencies beyond the stdlib and `git`, and exits non-zero on any HARD
failure so it can gate a campaign script.

Usage:
    python integration/sfe_preflight.py \
        --base-url https://192.168.1.191:8811 \
        --cacert SerendipityFoundry/SerendipityFoundryEngine/deploy/m2.crt \
        --require-commit-contains 67c28acee \
        --require-schema 4 \
        --require-endpoint /v2/worlds/{wid}/experiments/{eid} \
        --require-endpoint /v2/worlds/{wid}/observations

Traps this is built to catch (Harmonia SIMULATION_HANDBOOK v1.1.0 sec 8):
    T17  SFE binds its LAN address, never 0.0.0.0 -- localhost FAILS on M2.
    T18  The WRONG cert fails TLS so quietly it looks like a DEAD SERVICE.
         This script reports cert identity and separates the two causes.
    T20  A committed fix is NOT a deployed fix.
"""
from __future__ import annotations

import argparse
import json
import ssl
import subprocess
import sys
import urllib.error
import urllib.request

HARD, ADVISORY = "HARD", "ADVISORY"
CHECKS = []


def check(name, severity, ok, detail, evidence=None):
    CHECKS.append({"check": name, "severity": severity,
                   "status": "PASS" if ok else "FAIL",
                   "detail": detail, "evidence": evidence})
    mark = "PASS" if ok else ("FAIL" if severity == HARD else "WARN")
    print("  [%-4s] %-26s %s" % (mark, name, detail))
    return ok


def _get(url, ctx, timeout=10):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
        return r.status, r.read().decode()


def cert_identity(path):
    """CN/SAN of the pinned cert, so a mismatch is DIAGNOSED rather than
    presenting as a dead service (T18)."""
    try:
        import ssl as _ssl
        d = _ssl._ssl._test_decode_cert(path)
        subj = {k: v for t in d.get("subject", ()) for k, v in t}
        sans = [v for k, v in d.get("subjectAltName", ()) if k in ("IP Address",
                                                                   "DNS")]
        return {"common_name": subj.get("commonName"), "san": sans,
                "not_after": d.get("notAfter")}
    except Exception as exc:                                  # noqa: BLE001
        return {"error": "%s: %s" % (type(exc).__name__, exc)}


def _normalize_endpoint(spec):
    """Split "GET /v2/..." into (METHOD, path), and repair a POSIX path
    argument mangled by MSYS/Git-Bash path conversion.

    The METHOD is required, not decorative: OpenAPI keys routes by path, and a
    path-only check reports POST /observations as satisfying a requirement for
    GET /observations.

    Measured on M2, 2026-09-04: running this script from Git Bash turned
    `--require-endpoint /v2/worlds/{wid}/observations` into
    `C:/Program Files/Git/v2/worlds/{wid}/observations` before Python ever saw
    it. The check still FAILED -- but for the wrong reason, which is exactly
    the sort of false negative that makes a gate worse than no gate. An API
    path always starts at /v2 here, so anything before it is shell damage.
    (The other fix is MSYS2_ARG_CONV_EXCL=* or a leading //; this makes the
    script correct regardless of which shell a caller happens to use.)"""
    method, _, path = spec.strip().partition(" ")
    if not path:                       # no method given -> default to GET
        method, path = "GET", spec.strip()
    i = path.find("/v2/")
    return method.upper(), (path[i:] if i > 0 else path)


def git_contains(ancestor, descendant, repo="."):
    """True iff `descendant` (the LIVE commit) contains `ancestor` (the fix).
    This is T20 made executable: 'is the fix I depend on actually IN the build
    that is running', not 'is it in my working tree'."""
    try:
        p = subprocess.run(["git", "-C", repo, "merge-base",
                            "--is-ancestor", ancestor, descendant],
                           capture_output=True, text=True, timeout=20)
        return p.returncode == 0, p.stderr.strip()
    except Exception as exc:                                  # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, exc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--cacert", required=True)
    ap.add_argument("--require-commit-contains", default=None,
                    help="commit-ish the LIVE build must contain (T20)")
    ap.add_argument("--require-commit-exact", default=None)
    ap.add_argument("--require-schema", type=int, default=None)
    ap.add_argument("--require-endpoint", action="append", default=[],
                    help="OpenAPI path that must be served; repeatable")
    ap.add_argument("--require-engine-hash", default=None)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()

    print("SFE DEPLOYMENT ATTESTATION (CT-SFE-1)")
    print("  target : %s" % a.base_url)
    print("  cacert : %s" % a.cacert)
    ident = cert_identity(a.cacert)
    print("  cert   : CN=%s SAN=%s expires=%s" % (ident.get("common_name"),
                                                  ident.get("san"),
                                                  ident.get("not_after")))
    if "localhost" in a.base_url or "127.0.0.1" in a.base_url:
        check("T17_bind_address", ADVISORY, False,
              "SFE binds its LAN address, never 0.0.0.0 -- localhost will not "
              "reach it on M2; use the 192.168.x.x form", ident)
    print()

    ctx = ssl.create_default_context(cafile=a.cacert)
    version = None
    try:
        st, body = _get(a.base_url.rstrip("/") + "/v2/version", ctx)
        version = json.loads(body)
        check("reachable", HARD, st == 200, "GET /v2/version -> %d" % st)
    except ssl.SSLError as exc:
        check("reachable", HARD, False,
              "TLS FAILURE, not a dead service (T18): %s -- wrong cert for "
              "this host?" % exc, {"cert": ident})
        return _finish(a, 1)
    except (urllib.error.URLError, OSError) as exc:
        # urllib WRAPS ssl.SSLError inside URLError, so the SSLError branch
        # above never fires for a certificate mismatch and this handler used to
        # report a perfectly healthy service as "service down" -- which is
        # precisely the T18 confusion this tool exists to prevent. Measured
        # 2026-09-04 by pointing m1.crt at the live M2 engine. Unwrap and
        # classify before blaming the service.
        reason = getattr(exc, "reason", None)
        if isinstance(reason, ssl.SSLError) or "CERTIFICATE" in str(exc).upper():
            check("reachable", HARD, False,
                  "TLS FAILURE, not a dead service (T18): %s -- the service "
                  "may be perfectly healthy; this is the WRONG CERT for this "
                  "host. Check cert+host form before declaring an outage."
                  % reason or exc, {"cert": ident})
        else:
            check("reachable", HARD, False,
                  "no answer: %s -- service down, firewall, or wrong bind "
                  "address (T17)" % exc)
        return _finish(a, 1)

    live_commit = version.get("source_commit")
    live_hash = version.get("engine_source_hash")
    live_schema = version.get("schema_version")
    print("  live source_commit     : %s" % live_commit)
    print("  live engine_source_hash: %s" % (live_hash or "")[:32])
    print("  live schema_version    : %s" % live_schema)
    print()

    check("source_commit_present", HARD, bool(live_commit),
          "source_commit=%s (null means git was not on PATH at launch; the "
          "build is then UNIDENTIFIABLE)" % live_commit)

    if a.require_commit_exact:
        check("commit_exact", HARD, live_commit == a.require_commit_exact,
              "live=%s required=%s" % (live_commit, a.require_commit_exact))

    if a.require_commit_contains and live_commit:
        ok, err = git_contains(a.require_commit_contains, live_commit, a.repo)
        check("T20_deploy_lag", HARD, ok,
              "live build %s %s %s" % (
                  live_commit[:12], "CONTAINS" if ok else "DOES NOT CONTAIN",
                  a.require_commit_contains[:12])
              + ("" if ok else " -- THE RUNNING SERVICE PREDATES THE FIX YOU "
                               "ARE RELYING ON"),
              {"git_error": err or None})

    if a.require_schema is not None:
        check("schema_version", HARD,
              isinstance(live_schema, int) and live_schema >= a.require_schema,
              "live=%s required>=%s" % (live_schema, a.require_schema))

    if a.require_engine_hash:
        check("engine_source_hash", HARD,
              (live_hash or "").endswith(a.require_engine_hash)
              or a.require_engine_hash in (live_hash or ""),
              "live=%s required=%s" % ((live_hash or "")[:24],
                                       a.require_engine_hash[:24]))

    # CAPABILITY PRESENCE: the commit can be right and the process still be
    # serving something else. Ask the service what it actually routes.
    if a.require_endpoint:
        try:
            # The schema lives at /v2/openapi.json, NOT the FastAPI default
            # /openapi.json -- create_app sets openapi_url explicitly. Probing
            # the default returns 404, which reads as "no route table" and can
            # be mistaken for a stripped-down build. Try the real one first.
            routes, used, n_paths = set(), None, 0
            for cand in ("/v2/openapi.json", "/openapi.json"):
                try:
                    st, body = _get(a.base_url.rstrip("/") + cand, ctx)
                except urllib.error.HTTPError:
                    continue
                if st == 200:
                    spec = json.loads(body).get("paths", {})
                    n_paths = len(spec)
                    # (METHOD, path) pairs, NOT paths. A path can exist for one
                    # verb and not another -- POST /observations has always
                    # existed while GET /observations is new -- so a path-only
                    # check reports a capability as present when it is absent.
                    # Measured: that gave a false PASS on the very build this
                    # script was written to reject.
                    routes = {(m.upper(), p) for p, ms in spec.items()
                              for m in ms}
                    used = cand
                    break
            check("openapi_readable", HARD, used is not None,
                  "route table at %s (%d paths / %d routes)"
                  % (used, n_paths, len(routes)) if used
                  else "no OpenAPI schema at /v2/openapi.json or /openapi.json")
            for raw in a.require_endpoint:
                method, ep = _normalize_endpoint(raw)
                served = (method, ep) in routes
                label = "%s %s" % (method, ep.rsplit("/", 1)[-1][:16])
                check(label, HARD, served,
                      "%s %s -> %s" % (method, ep,
                                       "served" if served
                                       else "NOT SERVED by the running process"),
                      {"raw_arg": raw})
        except Exception as exc:                              # noqa: BLE001
            check("openapi_readable", HARD, False,
                  "could not read the live route table: %s" % exc)

    hard_fail = any(c["status"] == "FAIL" and c["severity"] == HARD
                    for c in CHECKS)
    return _finish(a, 1 if hard_fail else 0, version)


def _finish(a, code, version=None):
    n_fail = sum(1 for c in CHECKS if c["status"] == "FAIL")
    print()
    if code == 0:
        print("ATTESTATION PASS -- the live service is the one you intend to "
              "test (%d checks)." % len(CHECKS))
    else:
        print("ATTESTATION FAIL -- %d of %d checks failed. DO NOT record "
              "results from this service as evidence about the new build."
              % (n_fail, len(CHECKS)))
    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as fh:
            json.dump({"target": a.base_url, "version": version,
                       "checks": CHECKS, "exit_code": code}, fh, indent=1)
        print("wrote %s" % a.json_out)
    sys.exit(code)


if __name__ == "__main__":
    main()
