#!/usr/bin/env python3
"""Prepare a deployment for review. CHANGES NOTHING.

    python deploy/prepare_deployment.py [--out deploy/CANDIDATE_BUILD.json]

The review loop already had its verifier (verify_deploy.py) and its record
shape (DEPLOYED_BUILD.json). What it lacked was a generator, so the next pin
would have been thirteen file hashes written by hand on a packet that touches
most of them.

This writes a CANDIDATE pin and a diff against what is deployed, so the
operator can see exactly what a deploy would change before anything is
restarted. It never writes DEPLOYED_BUILD.json and never touches the service.

Read it as: these files change, the build identity moves from X to Y, the
schema moves from N to M, and here is the migration evidence for that move.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import ssl
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ENG))
DEPLOYED = os.path.join(HERE, "DEPLOYED_BUILD.json")

# the files that constitute the deployed implementation
FILES = [
    "SerendipityFoundry/SerendipityFoundryEngine/sfe/__init__.py",
    "SerendipityFoundry/SerendipityFoundryEngine/sfe/api.py",
    "SerendipityFoundry/SerendipityFoundryEngine/sfe/canary.py",
    "SerendipityFoundry/SerendipityFoundryEngine/sfe/errors.py",
    "SerendipityFoundry/SerendipityFoundryEngine/sfe/events.py",
    "SerendipityFoundry/SerendipityFoundryEngine/sfe/executors.py",
    "SerendipityFoundry/SerendipityFoundryEngine/sfe/ids.py",
    "SerendipityFoundry/SerendipityFoundryEngine/sfe/release.py",
    "SerendipityFoundry/SerendipityFoundryEngine/sfe/runtime.py",
    "SerendipityFoundry/SerendipityFoundryEngine/sfe/store.py",
    "SerendipityFoundry/SerendipityFoundryEngine/serve.py",
    "SerendipityFoundry/SerendipityFoundryClient/sfclient/client.py",
]


def norm(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def engine_source_hash(sfe_dir: str) -> str:
    """Byte-for-byte the computation in sfe/release.py:_source_hash."""
    h = hashlib.sha256()
    for n in sorted(p for p in os.listdir(sfe_dir) if p.endswith(".py")):
        h.update(n.encode("utf-8"))
        h.update(b"\x00")
        h.update(norm(io.open(os.path.join(sfe_dir, n), "rb").read()))
        h.update(b"\x00")
    return "sha256:" + h.hexdigest()


def schema_version() -> int:
    src = io.open(os.path.join(ENG, "sfe", "store.py"), encoding="utf-8").read()
    import re
    return int(re.search(r"^SCHEMA_VERSION = (\d+)", src, re.M).group(1))


def git(args):
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True)
    return (r.stdout.decode("utf-8", "replace").strip()
            if r.returncode == 0 else None)


def live_version(cacert):
    try:
        ctx = ssl.create_default_context(cafile=cacert)
        with urllib.request.urlopen(
                "https://192.168.1.202:8811/v2/version", context=ctx,
                timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:                                     # noqa: BLE001
        return {"_unreachable": repr(e)[:120]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE,
                                                  "CANDIDATE_BUILD.json"))
    ap.add_argument("--cacert", default=os.path.join(HERE, "m1.crt"))
    a = ap.parse_args()

    cand_hash = engine_source_hash(os.path.join(ENG, "sfe"))
    cand_schema = schema_version()
    files = {}
    for f in FILES:
        p = os.path.join(REPO, f.replace("/", os.sep))
        if not os.path.exists(p):
            files[f] = {"missing": True}
            continue
        d = norm(io.open(p, "rb").read())
        files[f] = {"sha256_lf": hashlib.sha256(d).hexdigest(),
                    "bytes_lf": len(d)}

    deployed = {}
    if os.path.exists(DEPLOYED):
        deployed = json.load(io.open(DEPLOYED, encoding="utf-8"))
    live = live_version(a.cacert)

    changed, added = [], []
    for f, c in files.items():
        d = (deployed.get("files") or {}).get(f)
        if d is None:
            added.append(f)
        elif d.get("sha256_lf") != c.get("sha256_lf"):
            changed.append({"file": f,
                            "deployed": (d.get("sha256_lf") or "")[:16],
                            "candidate": (c.get("sha256_lf") or "")[:16]})

    cand = {
        "_what_this_is": (
            "A CANDIDATE build, for review. Nothing has been deployed and no "
            "service was restarted. Applying it means copying these files into "
            "the deployment tree and restarting, after which "
            "deploy/verify_deploy.py should be re-pinned and re-run."),
        "candidate_commit": git(["rev-parse", "HEAD"]),
        "candidate_branch": git(["rev-parse", "--abbrev-ref", "HEAD"]),
        "engine_source_hash": cand_hash,
        "schema_version": cand_schema,
        "deployed_engine_source_hash": deployed.get("engine_source_hash"),
        "deployed_schema_version": deployed.get("schema_version"),
        "live_engine_source_hash": live.get("engine_source_hash"),
        "live_schema_version": live.get("schema_version"),
        "files_changed": changed,
        "files_added": added,
        "files_total": len(files),
        "files": files,
        "review_notes": {
            "schema_change": (
                None if deployed.get("schema_version") == cand_schema
                else "%s -> %s : a MIGRATION runs on first open. Take a "
                     "VACUUM INTO snapshot with the service stopped first; "
                     "rollback becomes code+data, because an older engine "
                     "REFUSES a newer ledger (store.py, 'refusing to run')."
                     % (deployed.get("schema_version"), cand_schema)),
            "build_identity_moves": cand_hash != deployed.get(
                "engine_source_hash"),
            "conformance_drift": (
                "Harmonia's conformance_check.py pins engine_source_hash "
                "exactly and is fail-closed, so any build change stops the "
                "automated seats until her contract is regenerated. Batch the "
                "regeneration into the same window."),
            "restart_procedure": (
                "Stop-ScheduledTask alone orphans the process tree and the "
                "orphan keeps the socket while the OLD build serves. Stop the "
                "task, tree-kill the venv stub, confirm the port is free, then "
                "start. Allow up to ~20s to bind."),
        },
    }
    io.open(a.out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(cand, indent=2) + "\n")

    print("=" * 72)
    print("CANDIDATE BUILD -- FOR REVIEW. Nothing deployed, nothing restarted.")
    print("=" * 72)
    print("  candidate commit    %s (%s)" % ((cand["candidate_commit"] or "?")[:12],
                                             cand["candidate_branch"]))
    print("  engine_source_hash  %s" % cand_hash)
    print("    deployed pin      %s" % deployed.get("engine_source_hash"))
    print("    live service      %s" % live.get("engine_source_hash"))
    print("  schema_version      %s   (deployed %s, live %s)"
          % (cand_schema, deployed.get("schema_version"),
             live.get("schema_version")))
    print()
    print("  files changed: %d   added: %d   of %d"
          % (len(changed), len(added), len(files)))
    for c in changed:
        print("    ~ %-58s %s -> %s" % (c["file"].split("/")[-1],
                                        c["deployed"], c["candidate"]))
    for f in added:
        print("    + %s" % f.split("/")[-1])
    print()
    for k, v in cand["review_notes"].items():
        if v:
            print("  [%s]" % k)
            print("    %s" % (v if isinstance(v, str) else json.dumps(v)))
    print()
    print("  written: %s" % a.out)
    print("  APPLY ONLY ON THE OPERATOR'S WORD.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
