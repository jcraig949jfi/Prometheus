"""Prove that what M1 is SERVING is the source that is COMMITTED.

    python deploy/verify_deploy.py                 # tree + live service
    python deploy/verify_deploy.py --no-service    # tree only (engine down)

WHY THIS EXISTS. The deployment tree (F:/Prometheus) is a SHARED checkout that
other roles switch branches in, and on 2026-09-06 it was sitting on another
role's feature branch with the entire v6 engine present only as uncommitted
modifications and untracked files. The source was safe on origin/main; what was
not safe was the deployed COPY of it. A `git checkout -- .`, `git clean` or
`reset --hard` in that tree by any role would have reverted the files under the
running service.

That failure is LOUD rather than silent -- measured 2026-09-06, a pre-v6 engine
opened against the live schema-6 ledger raises

    RuntimeError: db schema version 6 is NEWER than this engine's 5;
                  refusing to run (would misread state)      (store.py:471)

so a revert kills the service instead of quietly serving pre-v6 semantics over
v6 data. That is the right direction to fail in, and it is exactly why this is
a VERIFIER and a recovery record rather than an interlock: the engine already
refuses to misread state. What it cannot do is tell you, before you restart it,
that the tree underneath it has drifted. This can.

Exit 0 = the running build, the tree, and the pinned commit agree.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import ssl
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ENG))
PIN = os.path.join(HERE, "DEPLOYED_BUILD.json")

OK, BAD = [], []


def check(name, cond, detail=""):
    (OK if cond else BAD).append(name)
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name,
                           "" if cond else "\n         " + str(detail)))


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-service", action="store_true",
                    help="skip the live-service check (engine intentionally down)")
    ap.add_argument("--cacert", default=os.path.join(HERE, "m1.crt"))
    a = ap.parse_args()

    if not os.path.exists(PIN):
        print("no DEPLOYED_BUILD.json beside this script -- nothing to verify against")
        return 2
    pin = json.load(io.open(PIN, encoding="utf-8"))

    print("=" * 74)
    print("SFE DEPLOY VERIFICATION -- %s" % pin["engine"])
    print("  pinned commit : %s" % pin["source_commit_containing_build"][:12])
    print("  pinned hash   : %s" % pin["engine_source_hash"])
    print("=" * 74)

    # 1. every pinned file present and byte-identical (LF-normalized)
    missing, drifted = [], []
    for rel, want in pin["files"].items():
        p = os.path.join(REPO, rel.replace("/", os.sep))
        if not os.path.exists(p):
            missing.append(rel)
            continue
        got = hashlib.sha256(norm(io.open(p, "rb").read())).hexdigest()
        if got != want["sha256_lf"]:
            drifted.append("%s\n           pinned %s\n           found  %s"
                           % (rel, want["sha256_lf"][:24], got[:24]))
    check("every pinned source file is present", not missing,
          "MISSING: " + ", ".join(missing))
    check("no pinned source file has drifted", not drifted,
          "\n         ".join(drifted))

    # 2. the tree reproduces the pinned engine identity
    tree = engine_source_hash(os.path.join(ENG, "sfe"))
    check("tree reproduces the pinned engine_source_hash",
          tree == pin["engine_source_hash"],
          "tree computes %s" % tree)

    # 3. the RUNNING service reports that same identity
    if a.no_service:
        print("  [SKIP] live service check (--no-service)")
    else:
        try:
            ctx = ssl.create_default_context(cafile=a.cacert)
            with urllib.request.urlopen(pin["endpoint"] + "/v2/version",
                                        context=ctx, timeout=15) as r:
                v = json.loads(r.read().decode())
            check("live service reports the pinned engine_source_hash",
                  v.get("engine_source_hash") == pin["engine_source_hash"],
                  "service reports %s" % v.get("engine_source_hash"))
            check("live schema_version matches the pin",
                  v.get("schema_version") == pin["schema_version"],
                  "service reports %s" % v.get("schema_version"))
            for k, want in pin["expected_runtime_config"].items():
                check("live %s == %s" % (k, want), v.get(k) == want,
                      "service reports %s" % v.get(k))
            # source_commit is EXPECTED to disagree: it names the deployment
            # tree's HEAD at process start, which is not the build's identity.
            sc = v.get("source_commit")
            if sc and not pin["source_commit_containing_build"].startswith(sc[:9]):
                print("  [note] live source_commit %s does not name the pinned "
                      "commit." % sc[:12])
                print("         Expected on a shared checkout. "
                      "engine_source_hash above is the authoritative id;")
                print("         it will agree only after the next restart from "
                      "a tree at the pinned commit.")
        except Exception as e:                                  # noqa: BLE001
            check("live service reachable", False, repr(e)[:160])

    print("-" * 74)
    print("%d passed, %d failed" % (len(OK), len(BAD)))
    if BAD:
        print("\nThe deployed source no longer matches the pin. Do NOT run")
        print("'git checkout -- .' or 'git clean' in %s --" % REPO)
        print("that tree carries uncommitted work owned by other roles. Restore")
        print("only the SFE paths, from the pinned commit:")
        print("  %s" % pin["restore"]["restore_source"])
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
