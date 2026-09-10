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


#: Harmonia's fail-closed conformance contract. It pins the build hash
#: EXACTLY, so any build change stops the automated seats until it is
#: regenerated; the candidate has to say by how much.
CONTRACT = os.path.join(REPO, "roles", "Harmonia", "contracts",
                        "sfe_contract.json")


def identities(cand_hash, cand_schema, deployed, live, dev_instance):
    """The four identities, kept DISTINCT, with the mapping between them.

    They are routinely collapsed into one "version", and every one of this
    project's deployment incidents came from that collapse: a commit that
    named a tree which could not rebuild the running code, a schema that moved
    without the pin moving, a ledger id treated as a property of the machine.
    """
    return {
        "git_commit": {
            "value": git(["rev-parse", "HEAD"]),
            "branch": git(["rev-parse", "--abbrev-ref", "HEAD"]),
            "names": "a TREE in history",
            "authority": "best-effort. It is the tree this candidate was cut "
                         "from; it is NOT proof that the tree reproduces the "
                         "build, and /v2/version's source_commit has named a "
                         "commit that could not.",
        },
        "engine_source_hash": {
            "value": cand_hash,
            "names": "the RUNTIME BUILD",
            "authority": "AUTHORITATIVE. sha256 over sorted sfe/*.py, each "
                         "contributing name + NUL + LF-normalized bytes + "
                         "NUL, computed at import by sfe/release.py. LF "
                         "normalization is why a checkout's line-ending "
                         "convention cannot change build identity.",
        },
        "schema_version": {
            "value": cand_schema,
            "names": "the SHAPE OF THE LEDGER",
            "authority": "authoritative for the DATA. It moves only forward: "
                         "an older engine opened against a newer ledger "
                         "REFUSES to start (sfe/store.py, 'refusing to run'), "
                         "so a code-only rollback across a schema change is a "
                         "loud outage rather than a silent downgrade.",
        },
        "engine_instance_id": {
            "live_value": live.get("engine_instance_id"),
            "development_value": dev_instance,
            "names": "the LEDGER ITSELF",
            "authority": "authoritative for the DATABASE. Minted once per "
                         "database and stored in meta; it travels with the "
                         "substrate, not the path or the host. A code deploy "
                         "does NOT change it, and a changed value after a "
                         "deploy means the service was pointed at a different "
                         "ledger.",
        },
        "mapping": [
            "git_commit -> engine_source_hash : MANY-TO-ONE and not "
            "guaranteed. Two commits whose sfe/*.py agree produce one build "
            "hash; a commit whose tree was never copied into the deployment "
            "tree produces none.",
            "engine_source_hash -> schema_version : ONE-TO-ONE. SCHEMA_VERSION "
            "is a constant inside the hashed source, so a build cannot "
            "disagree with itself about the schema it writes.",
            "schema_version -> engine_instance_id : INDEPENDENT. A migration "
            "changes the shape of a ledger and never its identity.",
            "engine_instance_id -> engine_source_hash : INDEPENDENT. One "
            "ledger outlives many builds; one build serves many ledgers. The "
            "development receipt and production share a build hash and have "
            "DIFFERENT instance ids, which is exactly the property that lets "
            "a receipt be taken on a development ledger at all.",
        ],
    }


def rollback(deployed, cand_schema):
    """Code-and-data, because code alone is not a rollback across a
    migration."""
    d_schema = deployed.get("schema_version")
    crosses = d_schema is not None and cand_schema != d_schema
    return {
        "crosses_a_migration": crosses,
        "code": [
            "Copy the DEPLOYED pin's files back into the deployment tree from "
            "a checkout you own -- never `git checkout -- .` or `git clean` "
            "in F:/Prometheus, which carries other roles' uncommitted work.",
            "Restart with the documented procedure: stop the scheduled task, "
            "tree-kill the venv stub (Stop-ScheduledTask alone orphans the "
            "process tree and the orphan keeps the socket while the OLD build "
            "serves), confirm the port is free, start, allow ~20s to bind.",
            "Re-run deploy/verify_deploy.py against the restored pin.",
        ],
        "data": [
            "BEFORE deploying: stop the service and take a snapshot with "
            "VACUUM INTO. A file copy of a live SQLite database with a WAL is "
            "not a snapshot.",
            "The migration runs on first open and is additive; nothing is "
            "back-filled. There is no down-migration.",
            ("Reverting the code WITHOUT restoring the snapshot does not "
             "work: schema %s data under a schema %s engine is refused at "
             "startup. That is the correct failure direction, and it is why "
             "the snapshot is the rollback and the pin is only a recovery "
             "aid." % (cand_schema, d_schema)) if crosses else
            "This candidate does not move the schema, so the ledger is "
            "unchanged and a code-only revert is sufficient.",
        ],
        "instance_id_invariant":
            "engine_instance_id must be IDENTICAL before and after, in both "
            "directions. If it changes, the service was pointed at a "
            "different ledger and the rollback has not restored state -- it "
            "has replaced it.",
    }


def conformance(cand_hash, cand_schema, live):
    if not os.path.exists(CONTRACT):
        return {"contract": CONTRACT, "present": False}
    try:
        C = json.load(io.open(CONTRACT, encoding="utf-8"))
    except Exception as e:                                     # noqa: BLE001
        return {"contract": CONTRACT, "unreadable": repr(e)[:120]}
    eng = C.get("engine") or {}
    return {
        "contract": os.path.relpath(CONTRACT, REPO).replace(os.sep, "/"),
        "pinned_engine_source_hash": eng.get("engine_source_hash"),
        "pinned_schema_version": eng.get("schema_version"),
        "pinned_engine_instance_id": eng.get("engine_instance_id"),
        "candidate_engine_source_hash": cand_hash,
        "candidate_schema_version": cand_schema,
        "live_engine_source_hash": live.get("engine_source_hash"),
        "live_schema_version": live.get("schema_version"),
        "hash_matches_candidate":
            eng.get("engine_source_hash") == cand_hash,
        "hash_matches_live":
            eng.get("engine_source_hash") == live.get("engine_source_hash"),
        "note": "conformance_check.py is FAIL-CLOSED and compares "
                "engine_source_hash EXACTLY, so it halts the automated seats "
                "on any build change -- including one that changes no route. "
                "Regenerate the contract (generate_sfe_contract.py) in the "
                "SAME window as the deploy, or the seats stop on a build that "
                "is otherwise fine. If the pin already disagrees with the "
                "LIVE service, it was stale before this candidate and the "
                "regeneration is overdue independently of this deploy.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE,
                                                  "CANDIDATE_BUILD.json"))
    ap.add_argument("--cacert", default=os.path.join(HERE, "m1.crt"))
    ap.add_argument("--dev-instance", default=None,
                    help="engine_instance_id of the DEVELOPMENT ledger a "
                         "receipt was taken on, recorded to keep it distinct "
                         "from the live one")
    ap.add_argument("--receipt", default=None,
                    help="path to a receipt JSON to reference from the pin")
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
        "identities": identities(cand_hash, cand_schema, deployed, live,
                                 a.dev_instance),
        "rollback": rollback(deployed, cand_schema),
        "conformance_pin": conformance(cand_hash, cand_schema, live),
        "receipt": a.receipt,
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
    print("  FOUR IDENTITIES, KEPT DISTINCT")
    ids = cand["identities"]
    print("    git_commit          %s (%s)  -- names a TREE, best-effort"
          % ((ids["git_commit"]["value"] or "?")[:12],
             ids["git_commit"]["branch"]))
    print("    engine_source_hash  %s  -- names the BUILD, authoritative"
          % ids["engine_source_hash"]["value"])
    print("    schema_version      %s  -- names the LEDGER'S SHAPE"
          % ids["schema_version"]["value"])
    print("    engine_instance_id  live=%s  dev=%s  -- names the LEDGER"
          % (ids["engine_instance_id"]["live_value"],
             ids["engine_instance_id"]["development_value"]))
    print()
    cp = cand["conformance_pin"]
    print("  CONFORMANCE PIN (%s)" % cp.get("contract"))
    print("    pinned  %s / schema %s"
          % ((cp.get("pinned_engine_source_hash") or "?")[:26],
             cp.get("pinned_schema_version")))
    print("    live    %s / schema %s   matches pin: %s"
          % ((cp.get("live_engine_source_hash") or "?")[:26],
             cp.get("live_schema_version"), cp.get("hash_matches_live")))
    print("    cand    %s / schema %s   matches pin: %s"
          % ((cp.get("candidate_engine_source_hash") or "?")[:26],
             cp.get("candidate_schema_version"),
             cp.get("hash_matches_candidate")))
    print()
    rb = cand["rollback"]
    print("  ROLLBACK IS CODE AND DATA (crosses a migration: %s)"
          % rb["crosses_a_migration"])
    for line in rb["data"]:
        print("    - %s" % line)
    print()
    print("  written: %s" % a.out)
    print("  APPLY ONLY ON THE OPERATOR'S WORD.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
