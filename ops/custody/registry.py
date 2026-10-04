"""Custody registry tool (C-004-OP2; draft B B5): read / verify for every seat, register for the Aporia registrar only.

Store: M1 Postgres (prometheus_fire) table custody.registry, reached through the comms connection (EW_DB_HOST).

  python -m ops.custody.registry read [--kind KIND] [--json]
  python -m ops.custody.registry verify            # recompute the hash chain; exit 1 on any break
  python -m ops.custody.registry register --kind KIND --path REPO_PATH --commit SHA --registrar Aporia
        # registrar only. Refuses unless the commit is an ancestor of origin/main and the blob at that commit
        # exists; the blob sha256 is computed here from `git show <commit>:<path>` bytes, never supplied.

verify and read are inference-free and safe for any seat. Exit codes: 0 ok, 1 chain/consistency failure,
2 usage or precondition refused, 3 store unreachable (STORE_UNREACHABLE).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys

KINDS = ("EVIDENCE_MANIFEST", "RUN_INVENTORY", "STAGE_RECORD", "WITHDRAWAL", "EXPECTED_ANSWER_TABLE")
ZERO = "0" * 64
COLS = "row_id, registered_at_utc, registrar, record_kind, repo_path, blob_sha256, commit_sha, campaign, prev_hash, row_hash"


def _conn():
    from comms.api import connect
    return connect()


def digest(r):
    ts = r["registered_at_utc"].astimezone(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    s = "|".join([str(r["row_id"]), ts, r["registrar"], r["record_kind"], r["repo_path"], r["blob_sha256"],
                  r["commit_sha"], r["prev_hash"]])
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def rows(kind=None):
    c = _conn()
    cur = c.cursor()
    q = "select %s from custody.registry" % COLS + (" where record_kind = %s" if kind else "") + " order by row_id"
    cur.execute(q, (kind,) if kind else None)
    names = [x.strip() for x in COLS.split(",")]
    out = [dict(zip(names, r)) for r in cur.fetchall()]
    c.close()
    return out


def verify():
    """Return (ok, problems) after recomputing the whole chain."""
    allr = rows()
    problems, prev = [], ZERO
    for i, r in enumerate(allr, 1):
        r = {k: (v.strip() if isinstance(v, str) else v) for k, v in r.items()}
        if r["row_id"] != i:
            problems.append("row %s: row_id gap/out of order (expected %d)" % (r["row_id"], i))
        if r["prev_hash"] != prev:
            problems.append("row %s: prev_hash does not match previous row_hash" % r["row_id"])
        if digest(r) != r["row_hash"]:
            problems.append("row %s: row_hash does not match its fields" % r["row_id"])
        prev = r["row_hash"]
    return (not problems), problems, (allr[-1]["row_hash"].strip() if allr else ZERO), len(allr)


def _git(*a):
    return subprocess.run(["git", *a], capture_output=True)


def register(kind, path, commit, registrar):
    if registrar != "Aporia":
        print("REFUSED: only the registrar (Aporia) registers", file=sys.stderr)
        return 2
    if kind not in KINDS:
        print("REFUSED: unknown record_kind %s" % kind, file=sys.stderr)
        return 2
    _git("fetch", "-q", "origin")
    full = _git("rev-parse", commit + "^{commit}").stdout.decode().strip()
    if len(full) != 40 or _git("merge-base", "--is-ancestor", full, "origin/main").returncode != 0:
        print("REFUSED: commit %s is not an ancestor of origin/main" % commit, file=sys.stderr)
        return 2
    blob = _git("show", "%s:%s" % (full, path))
    if blob.returncode != 0:
        print("REFUSED: %s not present at %s" % (path, full), file=sys.stderr)
        return 2
    sha = hashlib.sha256(blob.stdout).hexdigest()
    ok, problems, head, n = verify()
    if not ok:
        print("REFUSED: chain broken before registration: %s" % problems, file=sys.stderr)
        return 1
    c = _conn()
    cur = c.cursor()
    cur.execute("insert into custody.registry (registrar, record_kind, repo_path, blob_sha256, commit_sha, prev_hash, "
                "row_hash) values (%s,%s,%s,%s,%s,%s,%s) returning row_id, registered_at_utc, row_hash",
                (registrar, kind, path, sha, full, ZERO, ZERO))
    rid, ts, rh = cur.fetchone()
    c.commit()
    c.close()
    ok, problems, head, n = verify()
    print(json.dumps({"row_id": rid, "registered_at_utc": ts.isoformat(), "record_kind": kind, "repo_path": path,
                      "blob_sha256": sha, "commit_sha": full, "row_hash": rh.strip(), "chain_ok": ok,
                      "chain_head": head, "rows": n}))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read"); r.add_argument("--kind"); r.add_argument("--json", action="store_true")
    sub.add_parser("verify")
    g = sub.add_parser("register")
    g.add_argument("--kind", required=True); g.add_argument("--path", required=True)
    g.add_argument("--commit", required=True); g.add_argument("--registrar", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "read":
            rs = rows(a.kind)
            for x in rs:
                x["registered_at_utc"] = x["registered_at_utc"].isoformat()
                x = {k: (v.strip() if isinstance(v, str) else v) for k, v in x.items()}
                print(json.dumps(x, sort_keys=True) if a.json else
                      "%(row_id)s %(registered_at_utc)s %(record_kind)s %(repo_path)s blob=%(blob_sha256)s commit=%(commit_sha)s" % x)
            return 0
        if a.cmd == "verify":
            ok, problems, head, n = verify()
            print(json.dumps({"chain_ok": ok, "rows": n, "chain_head": head, "problems": problems}))
            return 0 if ok else 1
        return register(a.kind, a.path, a.commit, a.registrar)
    except Exception as e:  # store unreachable or schema missing: never report a pass
        print(json.dumps({"status": "STORE_UNREACHABLE", "error": str(e)[:300]}))
        return 3


if __name__ == "__main__":
    sys.exit(main())
