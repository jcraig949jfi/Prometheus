#!/usr/bin/env python3
"""The deploy gate, made mechanical and FAIL-CLOSED.

    python deploy/preflight_deploy.py --readout archaeon/docs/h0h5/C3_2_READOUT.json

Answers one question: may the schema-8 build be deployed to M1 right now? It
CHANGES NOTHING -- every read is read-only, the SQLite handle is opened
`mode=ro`, and the service is only ever asked for /v2/version.

WHY THIS IS A SCRIPT AND NOT A PARAGRAPH. The operator's authority to deploy is
conditional, and a condition checked by reading a document and forming an
impression is a condition that gets waived on a busy afternoon. Each gate below
either has evidence or fails. UNKNOWN is a FAILURE, not a shrug: "I could not
tell whether the campaign was still running" is precisely the state in which
one must not restart the engine underneath it.

Exit 0 = every gate passed. Exit 1 = at least one did not. Read the reasons.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import os
import sqlite3
import ssl
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ENG))

#: The live deployment tree on M1. NOT this checkout: the deployment tree is a
#: shared working copy sitting on another role's branch with other roles'
#: uncommitted work in it, which is why a deploy is a FILE COPY and never a git
#: operation there.
M1_TREE = r"F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine"
M1_DB = os.path.join(M1_TREE, "var", "engine.db")
M1_URL = "https://192.168.1.202:8811/v2/version"

#: How quiet the engine must be. A consumer mid-attempt writes events
#: continuously; restarting under one loses the attempt it was in the middle
#: of, and no amount of "the queue looked empty" makes that not have happened.
QUIET_SECONDS = 300


def norm(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def engine_source_hash(sfe_dir: str) -> str:
    h = hashlib.sha256()
    for n in sorted(p for p in os.listdir(sfe_dir) if p.endswith(".py")):
        h.update(n.encode("utf-8"))
        h.update(b"\x00")
        h.update(norm(io.open(os.path.join(sfe_dir, n), "rb").read()))
        h.update(b"\x00")
    return "sha256:" + h.hexdigest()


class Gate:
    def __init__(self):
        self.rows = []
        self.ok = True

    def __call__(self, condition, name, passed, detail):
        if not passed:
            self.ok = False
        self.rows.append({"condition": condition, "gate": name,
                          "pass": bool(passed), "evidence": detail})
        print("  [%s] (%s) %s" % ("PASS" if passed else "FAIL", condition,
                                  name))
        for line in str(detail).splitlines():
            print("         %s" % line)


def live_queue(python: str, candidate_set: str):
    """Vivarium's queue, live, for one candidate set.

    `viv.cli candidates <id>` does NOT break out queued/running -- its view
    reports registered/retained/executed and no more -- so the counts come
    from `ls --status <s>`, filtered on the cs= token that _short() renders.
    Needs an interpreter with psycopg2; the SFE venv does not have one, which
    is why the interpreter is a parameter and not an assumption.
    """
    import subprocess
    out = {}
    viv = os.path.join(REPO, "vivarium")
    for st in ("queued", "claimed", "running"):
        try:
            p = subprocess.run(
                [python, "-m", "viv.cli", "ls", "--status", st,
                 "--limit", "2000"],
                cwd=viv, capture_output=True, timeout=120)
        except (OSError, subprocess.SubprocessError) as e:
            return None, repr(e)[:200]
        if p.returncode != 0:
            return None, (p.stderr.decode("utf-8", "replace").strip()
                          .splitlines() or ["exit %d" % p.returncode])[-1]
        body = p.stdout.decode("utf-8", "replace")
        out[st] = sum(1 for line in body.splitlines()
                      if ("cs=%s" % candidate_set) in line)
    return out, None


def live_version(cacert):
    try:
        ctx = ssl.create_default_context(cafile=cacert)
        with urllib.request.urlopen(M1_URL, context=ctx, timeout=20) as r:
            return json.loads(r.read().decode()), None
    except Exception as e:                                     # noqa: BLE001
        return None, repr(e)[:200]


def main():                                                    # noqa: C901
    ap = argparse.ArgumentParser()
    ap.add_argument("--readout", default=os.path.join(
        REPO, "archaeon", "docs", "h0h5", "C3_2_READOUT.json"))
    ap.add_argument("--cacert", default=os.path.join(HERE, "m1.crt"))
    ap.add_argument("--backup-dir", default=os.path.join(M1_TREE, "var",
                                                         "backup"))
    ap.add_argument("--quiet-seconds", type=int, default=QUIET_SECONDS)
    ap.add_argument("--candidate-set", default="cs-c3-2")
    #: The SFE venv has no psycopg2; this one does. Named rather than assumed,
    #: because "the check could not run" must never read as "the check passed".
    ap.add_argument("--python", default=r"H:\Python312\python.exe")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    g = Gate()
    now = time.time()
    print("SCHEMA-8 DEPLOY PREFLIGHT -- reads only, changes nothing")
    print("=" * 74)
    print("  checked at %s" % time.strftime("%Y-%m-%dT%H:%M:%S",
                                            time.localtime(now)))
    print()

    # -- (a) the campaign is drained --------------------------------------
    # THREE independent sources, because they answer different halves.
    #
    #   1. Vivarium's queue, LIVE. The authoritative one: the campaign's rows
    #      live in Postgres, not in the engine, so the engine cannot see them.
    #   2. Archaeon's committed readout. A cross-check, and the source the
    #      order names -- but it is a file, and a file is as old as its
    #      timestamp.
    #   3. The engine's own ledger. Whether anything is executing against it
    #      RIGHT NOW. A drained Postgres queue with a consumer still flushing
    #      results is not a safe moment either.
    #
    # No single one is sufficient, so all three must agree.
    counts, why = live_queue(a.python, a.candidate_set)
    if counts is None:
        g("a", "Vivarium's LIVE queue reports the candidate set drained",
          False, "could not read the queue: %s\n"
                 "This gate cannot be waived by not being able to check it."
                 % why)
    else:
        outstanding_live = {k: v for k, v in counts.items() if v}
        g("a", "Vivarium's LIVE queue reports the candidate set drained",
          not outstanding_live,
          "%s: %s  (via `%s -m viv.cli ls --status <s>`, counted by cs=)"
          % (a.candidate_set, json.dumps(counts), os.path.basename(a.python)))

    try:
        R = json.load(io.open(a.readout, encoding="utf-8"))
        by_arm = R.get("status_by_arm") or {}
        outstanding = {arm: {k: v for k, v in st.items()
                             if k in ("queued", "running") and v}
                       for arm, st in by_arm.items()}
        outstanding = {k: v for k, v in outstanding.items() if v}
        age_h = None
        if R.get("written"):
            try:
                import datetime as _dt
                w = _dt.datetime.fromisoformat(R["written"])
                if w.tzinfo is None:
                    w = w.replace(tzinfo=_dt.timezone.utc)
                age_h = (_dt.datetime.now(_dt.timezone.utc)
                         - w).total_seconds() / 3600.0
            except ValueError:
                pass
        g("a", "Archaeon's readout reports the candidate set complete",
          bool(R.get("complete")) and not outstanding,
          "candidate_set=%s complete=%s %s/%s rows\n"
          "outstanding=%s\nwritten=%s (%s)"
          % (R.get("candidate_set"), R.get("complete"), R.get("n_completed"),
             R.get("n_rows"), json.dumps(outstanding) or "{}",
             R.get("written"),
             "%.1f h old" % age_h if age_h is not None else "age unknown"))
        g("a", "the readout is fresh enough to be believed",
          age_h is not None and age_h <= 1.0,
          "a readout older than an hour cannot answer 'right now'; refresh "
          "with archaeon/producer/c3_readout.py (needs the Postgres queue) "
          "-- age=%s"
          % ("%.1f h" % age_h if age_h is not None else "unknown"))
    except (OSError, ValueError) as e:
        g("a", "Archaeon's readout is readable", False,
          "%s: %s" % (a.readout, e))

    if not os.path.exists(M1_DB):
        g("a", "the live ledger is readable", False, "missing: %s" % M1_DB)
    else:
        uri = "file:%s?mode=ro" % M1_DB.replace("\\", "/")
        cx = sqlite3.connect(uri, uri=True, timeout=20)
        cx.row_factory = sqlite3.Row
        try:
            n = cx.execute("SELECT COUNT(*) n FROM work_items WHERE status IN "
                           "('CLAIMED','RUNNING')").fetchone()["n"]
            g("a", "no work is CLAIMED or RUNNING in the engine's ledger",
              n == 0, "CLAIMED+RUNNING = %d" % n)

            last = cx.execute("SELECT MAX(ts) t FROM events").fetchone()["t"]
            quiet = (now - float(last)) if last else None
            g("a", "the engine has been quiet for %ds" % a.quiet_seconds,
              quiet is not None and quiet >= a.quiet_seconds,
              "last event %s (%.1f s ago); a consumer mid-attempt writes "
              "continuously, and restarting under one loses the attempt it "
              "was inside"
              % (time.strftime("%H:%M:%S", time.localtime(last)) if last
                 else "never", quiet if quiet is not None else -1))

            recent = cx.execute(
                "SELECT COUNT(*) n FROM experiments WHERE created_ts > ?",
                (now - 3600,)).fetchone()["n"]
            g("a", "no experiments were created in the last hour",
              recent == 0, "experiments in the last hour = %d" % recent)

            sv = cx.execute("SELECT value FROM meta WHERE "
                            "key='schema_version'").fetchone()[0]
            iid = cx.execute("SELECT value FROM meta WHERE "
                             "key='engine_instance_id'").fetchone()[0]
            print("         (ledger schema=%s instance=%s)" % (sv, iid))
        finally:
            cx.close()

    # -- (c) the runbook, the backup, the rollback ------------------------
    runbook = os.path.join(HERE, "DEPLOY_SCHEMA8_2026-09-10.md")
    body = io.open(runbook, encoding="utf-8").read() if os.path.exists(
        runbook) else ""
    g("c", "the runbook is committed and names a rollback command",
      bool(body) and "VACUUM INTO" in body and "ROLLBACK" in body.upper(),
      "%s (%d bytes)" % (runbook, len(body)))

    backups = sorted(glob.glob(os.path.join(a.backup_dir, "engine-*.db")))
    fresh = [b for b in backups
             if now - os.path.getmtime(b) < 6 * 3600]
    g("c", "a pre-deploy backup exists and is less than 6 hours old",
      bool(fresh),
      "backup_dir=%s\nfound=%d, fresh=%d\n%s"
      % (a.backup_dir, len(backups), len(fresh),
         "\n".join("  %s  %s" % (os.path.basename(b),
                                 time.strftime("%Y-%m-%d %H:%M",
                                               time.localtime(
                                                   os.path.getmtime(b))))
                   for b in backups[-3:]) or "  (none)"))

    # -- the ceiling meets data that predates it --------------------------
    # THE GATE A CODE REVIEW DOES NOT CATCH. v8 introduced a per-artifact size
    # ceiling where there had been none, and it applies on READ as well as on
    # write. Any blob already in the store that exceeds it becomes unreadable
    # the moment the new build starts -- not corrupted, not deleted, just
    # refused. A deploy may add a limit; it must not silently retire data that
    # was readable an hour ago.
    sfe_dir = os.path.join(ENG, "sfe")
    ceiling = None
    try:
        src = io.open(os.path.join(sfe_dir, "runtime.py"),
                      encoding="utf-8").read()
        import re
        m = re.search(r"^DEFAULT_MAX_ARTIFACT_BYTES\s*=\s*([0-9_ *]+)", src,
                      re.M)
        if m:
            ceiling = int(eval(m.group(1), {"__builtins__": {}}))  # noqa: S307
    except (OSError, ValueError, SyntaxError):
        ceiling = None

    blobs = os.path.join(M1_TREE, "var", "blobs")
    over = []
    largest = 0
    if ceiling and os.path.isdir(blobs):
        for root, _d, files in os.walk(blobs):
            for fn in files:
                sz = os.path.getsize(os.path.join(root, fn))
                largest = max(largest, sz)
                if sz > ceiling:
                    over.append((fn, sz))
    launcher = os.path.join(HERE, "sfengine.cmd")
    cmd = io.open(launcher, encoding="utf-8").read() if os.path.exists(
        launcher) else ""
    configured = "--max-artifact-bytes" in cmd
    g("build", "no artifact that is readable today becomes unreadable",
      ceiling is None or not over or configured,
      "candidate ceiling = %s bytes (%.1f MiB)\n"
      "largest stored blob = %d bytes (%.1f MiB)\n"
      "blobs over the ceiling = %d%s\n"
      "launcher passes --max-artifact-bytes: %s\n"
      "%s"
      % (ceiling, (ceiling or 0) / 1048576.0, largest, largest / 1048576.0,
         len(over),
         "".join("\n  %s  %d" % (f[:40], s) for f, s in over[:3]),
         configured,
         "FIX: start the service with --max-artifact-bytes >= %d, which keeps "
         "every existing artifact readable while still installing a ceiling "
         "where there was none." % largest if over and not configured
         else "ok"))

    # -- the build itself --------------------------------------------------
    cand = engine_source_hash(os.path.join(ENG, "sfe"))
    pin = os.path.join(HERE, "CANDIDATE_BUILD.json")
    pinned = {}
    if os.path.exists(pin):
        pinned = json.load(io.open(pin, encoding="utf-8"))
    g("build", "the candidate pin describes THIS tree",
      pinned.get("engine_source_hash") == cand,
      "tree=%s\npin =%s" % (cand, pinned.get("engine_source_hash")))

    live, err = live_version(a.cacert)
    deployed = {}
    dp = os.path.join(HERE, "DEPLOYED_BUILD.json")
    if os.path.exists(dp):
        deployed = json.load(io.open(dp, encoding="utf-8"))
    g("build", "the live service is the build the DEPLOYED pin claims",
      live is not None
      and live.get("engine_source_hash") == deployed.get(
          "engine_source_hash"),
      "live=%s\npin =%s%s"
      % ((live or {}).get("engine_source_hash"),
         deployed.get("engine_source_hash"),
         "\nunreachable: %s" % err if err else ""))
    if live:
        g("build", "the live instance id is the one the pin expects",
          live.get("engine_instance_id")
          == (deployed.get("expected_runtime_config") or {}).get(
              "engine_instance_id"),
          "live=%s expected=%s -- this is the LEDGER's identity; if it "
          "changed, the service is pointed at a different database"
          % (live.get("engine_instance_id"),
             (deployed.get("expected_runtime_config") or {}).get(
                 "engine_instance_id")))

    print()
    print("=" * 74)
    print("  VERDICT: %s" % ("CLEAR TO DEPLOY" if g.ok else
                             "DO NOT DEPLOY"))
    if not g.ok:
        print("  Failing gates:")
        for r in g.rows:
            if not r["pass"]:
                print("    (%s) %s" % (r["condition"], r["gate"]))
    if a.json:
        print(json.dumps({"checked_at": time.strftime(
            "%Y-%m-%dT%H:%M:%S", time.localtime(now)),
            "clear_to_deploy": g.ok, "gates": g.rows}, indent=2))
    return 0 if g.ok else 1


if __name__ == "__main__":
    sys.exit(main())
