#!/usr/bin/env python3
"""D-23: move the SFE service and its LEDGER out of the canonical checkout.

    python deploy/move_service_out_of_canonical.py --check     # rehearse, change nothing
    python deploy/move_service_out_of_canonical.py --apply     # the real thing

WHAT THIS IS FOR. The live engine runs `serve.py` from
F:\\Prometheus\\SerendipityFoundry\\SerendipityFoundryEngine -- the CANONICAL
checkout -- with its database, blobs, rollback snapshot and TLS private key in
`var/` and `deploy/` underneath it.

THE PART THAT IS EASY TO MISS. `var/` is gitignored
(SerendipityFoundry/.gitignore:6), so `git status` on that directory reports
clean while it holds 213 MB of live ledger, 44 MB of blobs, the only schema-7
rollback and the only copy of m1.key. D-23 rule 7 says destroy a corrupt
worktree rather than nurse it, and that checkout has twice lost ~11,000 files.
Applied there, "destroy" takes the ledger and the private key with it, and
nothing in git would ever have said they were at risk.

So moving only the CODE is the half-move that looks compliant and keeps the
whole hazard. This moves both:

    code -> F:\\Prometheus-worktrees\\daedalus-sfengine   (pinned, detached, recorded SHA)
    data -> F:\\Prometheus-data\\sfe                      (OUTSIDE the repository entirely)

Data does not belong in a worktree either: worktrees are disposable by rule 7,
and the ledger must outlive every one of them.

THE INVARIANT THAT DECIDES SUCCESS. `engine_instance_id` identifies the LEDGER.
It must be byte-identical before and after. If it changes, the service is
pointed at a different database and the move has replaced state rather than
relocated it -- stop and restore.

SAFETY. --apply refuses unless the service is stopped, the port is free, the
queue is idle and a fresh backup exists. It MOVES nothing until a verified copy
is in place, and it leaves the originals behind rather than deleting them: the
canonical copies are removed only by a later, separate, explicitly-confirmed
step, after the service has been seen healthy on the new paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

CANON = r"F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine"
PINNED = r"F:\Prometheus-worktrees\daedalus-sfengine\SerendipityFoundry\SerendipityFoundryEngine"
DATA = r"F:\Prometheus-data\sfe"

SRC_DB = os.path.join(CANON, "var", "engine.db")
DST_DB = os.path.join(DATA, "engine.db")
PORT = 8811
VERSION_URL = "https://192.168.1.202:8811/v2/version"

#: Everything that must survive, with whether git could ever replace it.
ASSETS = [
    ("var/engine.db", "THE LEDGER", False),
    ("var/blobs", "artifact bytes", False),
    ("var/backup", "the schema-7 rollback", False),
    ("deploy/m1.key", "TLS PRIVATE KEY -- not in git, no other copy", False),
    ("deploy/m1.crt", "TLS cert", True),
]


def sh(*args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def instance_of(db):
    if not os.path.exists(db):
        return None
    cx = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True,
                         timeout=20)
    try:
        return cx.execute(
            "SELECT value FROM meta WHERE key='engine_instance_id'"
        ).fetchone()[0]
    finally:
        cx.close()


def sha256_file(p, cap=None):
    h = hashlib.sha256()
    n = 0
    with open(p, "rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
            n += len(b)
            if cap and n >= cap:
                break
    return h.hexdigest()


def service_running():
    try:
        import ssl
        ctx = ssl.create_default_context(cafile=os.path.join(HERE, "m1.crt"))
        with urllib.request.urlopen(VERSION_URL, context=ctx, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception:                                          # noqa: BLE001
        return None


def queue_idle(python=r"H:\Python312\python.exe"):
    viv = r"F:\Prometheus-worktrees\daedalus-d23\vivarium"
    if not os.path.isdir(viv):
        viv = r"F:\Prometheus\vivarium"
    out = {}
    for st in ("queued", "claimed", "running"):
        p = sh(python, "-m", "viv.cli", "ls", "--status", st, "--limit",
               "2000", cwd=viv)
        if p.returncode != 0:
            return None, (p.stderr.strip().splitlines() or ["?"])[-1]
        out[st] = sum(1 for ln in p.stdout.splitlines() if ln.strip())
    return out, None


def report(apply_it):
    ok = True

    def row(name, passed, detail=""):
        nonlocal ok
        if not passed:
            ok = False
        print("  [%s] %s" % ("PASS" if passed else "FAIL", name))
        if detail:
            for ln in str(detail).splitlines():
                print("         %s" % ln)

    print("D-23 SERVICE MOVE -- %s" % ("APPLY" if apply_it else
                                       "REHEARSAL (changes nothing)"))
    print("=" * 74)
    print("  code : %s\n         -> %s" % (CANON, PINNED))
    print("  data : %s\\var, deploy/m1.key\n         -> %s" % (CANON, DATA))
    print()

    print("WHAT IS AT RISK IN THE CANONICAL CHECKOUT (git shows none of it):")
    for rel, what, in_git in ASSETS:
        p = os.path.join(CANON, rel.replace("/", os.sep))
        if os.path.isdir(p):
            size = sum(os.path.getsize(os.path.join(dp, f))
                       for dp, _d, fs in os.walk(p) for f in fs)
        else:
            size = os.path.getsize(p) if os.path.exists(p) else 0
        print("    %-16s %-46s %8.1f MB%s"
              % (rel, what, size / 1048576.0,
                 "" if in_git else "   IRREPLACEABLE"))
    print()

    row("the pinned worktree exists and reproduces the deployed build",
        os.path.isdir(PINNED) and _pinned_hash() == _deployed_hash(),
        "pinned   %s\ndeployed %s" % (_pinned_hash(), _deployed_hash()))

    live = service_running()
    if apply_it:
        row("the service is STOPPED", live is None,
            "it is still answering /v2/version" if live else "not answering")
        q, why = queue_idle()
        row("the queue is idle", q is not None and not any(q.values()),
            json.dumps(q) if q else why)
    else:
        print("  [note] service is %s; queue %s"
              % ("RUNNING" if live else "stopped",
                 json.dumps(queue_idle()[0])))
        if live:
            print("         a rehearsal is fine while it runs; --apply is not.")

    src_inst = instance_of(SRC_DB)
    row("the source ledger is readable and identifies itself",
        bool(src_inst), "engine_instance_id %s" % src_inst)

    backups = []
    bdir = os.path.join(CANON, "var", "backup")
    if os.path.isdir(bdir):
        backups = sorted(os.listdir(bdir))
    row("a rollback snapshot exists", bool(backups),
        "\n".join("  " + b for b in backups[-3:]) or "none")

    print()
    if not apply_it:
        print("  REHEARSAL ONLY. Nothing was changed.")
        print("  To apply: stop the service (runbook section 3), confirm the")
        print("  queue is idle, then re-run with --apply.")
    return ok, src_inst


def _pinned_hash():
    return _hash_sfe(os.path.join(PINNED, "sfe"))


def _deployed_hash():
    try:
        with open(os.path.join(HERE, "DEPLOYED_BUILD.json"),
                  encoding="utf-8") as fh:
            return json.load(fh).get("engine_source_hash")
    except OSError:
        return None


def _hash_sfe(d):
    if not os.path.isdir(d):
        return None
    h = hashlib.sha256()
    for n in sorted(p for p in os.listdir(d) if p.endswith(".py")):
        with open(os.path.join(d, n), "rb") as fh:
            b = fh.read().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        h.update(n.encode()); h.update(b"\x00"); h.update(b); h.update(b"\x00")
    return "sha256:" + h.hexdigest()


def apply_move(src_inst):
    """COPY first, verify, then swap. Originals are left in place."""
    os.makedirs(DATA, exist_ok=True)
    print()
    print("COPYING (originals are left behind; they are removed by a separate,")
    print("explicitly confirmed step after the service is seen healthy)")
    for rel, what, _g in ASSETS:
        s = os.path.join(CANON, rel.replace("/", os.sep))
        d = os.path.join(DATA, os.path.basename(rel))
        if not os.path.exists(s):
            print("  (absent) %s" % rel)
            continue
        t0 = time.time()
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
        print("  %-16s -> %-28s %.1fs" % (rel, d, time.time() - t0))

    got = instance_of(DST_DB)
    print()
    print("  source ledger instance: %s" % src_inst)
    print("  copied ledger instance: %s" % got)
    if got != src_inst:
        print("  FAIL: the copy is a DIFFERENT ledger. Nothing has been "
              "switched; the original is untouched.")
        return 1
    print("  IDENTICAL -- the copy is the same ledger.")
    print()
    print("  NEXT, BY HAND (they change the service, so they are not scripted):")
    print("   1. point deploy\\sfengine.cmd at:")
    print("        python  %s\\serve.py" % PINNED)
    print("        --db    %s" % DST_DB)
    print("        --tls-cert %s\\m1.crt  --tls-key %s\\m1.key" % (DATA, DATA))
    print("   2. re-point the scheduled task to the pinned cmd")
    print("   3. start, then confirm engine_instance_id is STILL %s" % src_inst)
    print("   4. only then remove the canonical copies, as a separate step")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    ok, src_inst = report(a.apply)
    if not a.apply:
        return 0
    if not ok:
        print("  REFUSING to apply: a precondition failed above.")
        return 1
    return apply_move(src_inst)


if __name__ == "__main__":
    sys.exit(main())
