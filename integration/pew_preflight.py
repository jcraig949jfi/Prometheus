#!/usr/bin/env python3
"""PEW DEPLOYMENT ATTESTATION -- CT-PEW-1: does the CODE agree with the SCHEMA?

Born from a live incident, 2026-09-11. The M2 PEW service auto-redeployed to
repo HEAD at 06:25:07. HEAD's fossil-encounter INSERT names 25 columns,
including five added by migration 010 (sfe_engine_instance_id, sfe_session_id,
sfe_session_key_fp, sfe_affinity_mode, sfe_ledger_head_hash). Migration 010 had
NOT been applied to the M2 database, which still had 22 columns. Every
fossil-encounter read and write returned HTTP 500 "Internal Server Error" with
no detail, for hours, while /health, /identity, /version, /fossil/contract,
/constraints and /fossil/worlds all returned 200.

WHY THE EXISTING CONSTRAINT DID NOT CATCH IT
  Harmonia filed HARD constraint K-18869f54f091 on 2026-09-04: "an experiment
  must not run against a service whose live source_commit lacks the required
  fix." That constraint is DIRECTIONAL -- it detects CODE TOO OLD. This incident
  is CODE TOO NEW FOR THE SCHEMA. The same class, the opposite sign, and the
  constraint as written is blind to it. This script closes that direction.

WHAT A HEALTH CHECK CANNOT SEE
  The service was HEALTHY throughout. /health answers from application state and
  never touches ew.fossil_encounters, so a schema mismatch on the single most
  important table in the evidence store is invisible to every liveness probe in
  the stack. That is the same shape as CT-SFE-1's stale-but-healthy daemon.

EXIT CODES
  0 code and schema agree on every table this checks
  1 a HARD check failed -- do not record evidence from this service
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

CHECKS = []


def check(name, ok, detail):
    CHECKS.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    print("  [%-4s] %-28s %s" % ("PASS" if ok else "FAIL", name, detail))
    return ok


def columns_code_expects(service_py: pathlib.Path):
    """Parse the fossil-encounter INSERT column list out of the service source.

    Deliberately source-parsing rather than importing: importing ew.service
    opens a DB pool and would fail for reasons unrelated to the question, and we
    want this runnable against a checkout that is not the running build."""
    src = service_py.read_text(encoding="utf-8")
    m = re.search(r"INSERT INTO ew\.fossil_encounters\((.*?)\)\s*VALUES",
                  src, re.S)
    if not m:
        return None, None
    cols = [c.strip() for c in re.sub(r'"\s*\n\s*"', "", m.group(1)).split(",")]
    cols = [c for c in cols if c]
    n = re.search(r"_ENC_NCOLS\s*=\s*(\d+)", src)
    return cols, int(n.group(1)) if n else None


def columns_db_has(conn, table="fossil_encounters", schema="ew"):
    with conn.cursor() as cur:
        cur.execute("SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema=%s AND table_name=%s", (schema, table))
        return {r[0] for r in cur.fetchall()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="D:/Prometheus")
    ap.add_argument("--db-host", default=None)
    args = ap.parse_args()

    repo = pathlib.Path(args.repo)
    sys.path.insert(0, str(repo / "evidence_wiki"))
    print("PEW DEPLOYMENT ATTESTATION (CT-PEW-1)")

    svc = repo / "evidence_wiki" / "ew" / "service.py"
    cols, ncols = columns_code_expects(svc)
    if cols is None:
        check("code_insert_parsed", False, "could not find the fossil_encounters INSERT")
        return 1
    check("code_insert_parsed", True,
          "code writes %d columns (_ENC_NCOLS=%s)" % (len(cols), ncols))
    ok = check("ncols_in_lockstep", ncols == len(cols),
               "_ENC_NCOLS=%s vs %d parsed columns%s"
               % (ncols, len(cols),
                  "" if ncols == len(cols) else "  -- the placeholder count and the "
                  "column list have drifted; inserts will fail or misalign"))

    try:
        from ew import db as ewdb
        if args.db_host:
            import os
            os.environ["EW_DB_HOST"] = args.db_host
        conn = ewdb.connect() if hasattr(ewdb, "connect") else ewdb.get_conn()
    except Exception as e:
        check("db_reachable", False, "%s: %s" % (type(e).__name__, str(e)[:120]))
        return 1
    check("db_reachable", True, "connected")

    have = columns_db_has(conn)
    missing = [c for c in cols if c not in have]
    ok &= check("schema_has_every_written_column", not missing,
                "OK (%d columns)" % len(have) if not missing else
                "DB IS MISSING %d COLUMN(S) THE CODE WRITES: %s -- every "
                "fossil-encounter read and write will 500 while /health stays 200"
                % (len(missing), ", ".join(missing)))

    print()
    if ok:
        print("ATTESTATION PASS -- code and schema agree (%d checks)." % len(CHECKS))
        return 0
    print("ATTESTATION FAIL -- %d of %d checks failed. DO NOT record evidence "
          "from this service." % (sum(1 for c in CHECKS if c["status"] == "FAIL"),
                                  len(CHECKS)))
    print("REMEDY: apply the outstanding migration(s) to this database, or roll "
          "the service back to a build whose INSERT matches the schema. The two "
          "must move together.")
    return 1


if __name__ == "__main__":
    rc = main()
    print(json.dumps({"checks": CHECKS}, indent=1))
    sys.exit(rc)
