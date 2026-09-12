"""B1 engine-side verification of a read grant, run by the maintainer against
the ledger READ ONLY after the owner (Vivarium) has issued it. Establishes,
from the ledger and the deployed code, the five facts the operator asked for:

  exact scope        scope_id, name, owner client
  exact grantee      grantee client_id and name; granted_by == owner; not revoked
  membership         worlds in the scope; how many carry the expected name
                     prefix; how many of the owner's prefixed worlds are NOT
                     in it (the scope is enumerated, so this is the lag)
  read-only          the only routes that consult read scopes are the
                     /v2/read/* GETs and the owner-side scope POSTs
  no import/claim    _may_cross and claim_work never read the scope tables

    python deploy/verify_read_grant.py --grantee cli_1029e9255a074157a1b3ba1e [--db ...] [--prefix viv-]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENGINE = os.path.dirname(_HERE)
DEFAULT_DB = r"D:\Prometheus-data\sfe\engine.db"


def code_facts(engine_root):
    rt = open(os.path.join(engine_root, "sfe", "runtime.py"), encoding="utf-8").read()
    api = open(os.path.join(engine_root, "sfe", "api.py"), encoding="utf-8").read()

    def body(src, name):
        m = re.search(r"\n    def %s\(.*?(?=\n    def |\Z)" % re.escape(name), src, re.S)
        return m.group(0) if m else ""

    facts = {
        "_may_cross_reads_scopes": bool(re.search(r"read_scope|read_grant", body(rt, "_may_cross"))),
        "claim_work_reads_scopes": bool(re.search(r"read_scope|read_grant", body(rt, "claim_work"))),
        "import_artifact_reads_scopes": bool(re.search(r"read_scope|read_grant", body(rt, "import_artifact"))),
        "mutating_routes_under_read": sorted(set(re.findall(r'@app\.(?:post|put|delete|patch)\("(/v2/read[^"]*)"', api))),
        "get_routes_under_read": sorted(set(re.findall(r'@app\.get\("(/v2/read[^"]*)"', api))),
    }
    return facts


def verify(grantee, *, db=DEFAULT_DB, prefix="viv-", engine_root=_ENGINE):
    c = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True, timeout=10)
    c.row_factory = sqlite3.Row
    try:
        g = c.execute("SELECT g.*, s.name AS scope_name, s.owner_client_id, oc.name AS owner_name, gc.name AS grantee_name "
                      "FROM read_grants g JOIN read_scopes s USING(scope_id) "
                      "JOIN clients oc ON oc.client_id = s.owner_client_id "
                      "JOIN clients gc ON gc.client_id = g.grantee_client_id "
                      "WHERE g.grantee_client_id=? AND g.revoked_ts IS NULL", (grantee,)).fetchall()
        out = {"schema": "read_grant_verification.v1", "grantee_client_id": grantee, "db": db,
               "grants": [], "code": code_facts(engine_root)}
        for r in g:
            members = [x["world_id"] for x in c.execute("SELECT world_id FROM read_scope_worlds WHERE scope_id=?", (r["scope_id"],))]
            owned = {x["world_id"]: x["name"] for x in c.execute("SELECT world_id, name FROM worlds WHERE client_id=?", (r["owner_client_id"],))}
            in_scope_prefixed = sum(1 for w in members if owned.get(w, "").startswith(prefix))
            not_owned = [w for w in members if w not in owned]
            owner_prefixed_missing = [w for w, n in owned.items() if n.startswith(prefix) and w not in set(members)]
            out["grants"].append({
                "grant_id": r["grant_id"], "scope_id": r["scope_id"], "scope_name": r["scope_name"],
                "owner_client_id": r["owner_client_id"], "owner_name": r["owner_name"],
                "grantee_name": r["grantee_name"], "granted_by": r["granted_by"],
                "granted_by_is_owner": r["granted_by"] == r["owner_client_id"],
                "created_ts": r["created_ts"], "revoked_ts": r["revoked_ts"], "note": r["note"],
                "worlds_in_scope": len(members), "worlds_in_scope_with_prefix": in_scope_prefixed,
                "worlds_in_scope_not_owned_by_owner": not_owned,
                "owner_prefixed_worlds_missing_from_scope": len(owner_prefixed_missing),
            })
        out["verdict"] = ("GRANT_PRESENT" if g else "NO_GRANT")
        out["read_only"] = (not out["code"]["_may_cross_reads_scopes"] and not out["code"]["claim_work_reads_scopes"]
                            and not out["code"]["import_artifact_reads_scopes"]
                            and all(p.startswith("/v2/read/scopes") or p.startswith("/v2/read/grants")
                                    for p in out["code"]["mutating_routes_under_read"]))
        return out
    finally:
        c.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--grantee", required=True)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--prefix", default="viv-")
    ap.add_argument("--engine-root", default=_ENGINE)
    a = ap.parse_args(argv)
    out = verify(a.grantee, db=a.db, prefix=a.prefix, engine_root=a.engine_root)
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0 if out["verdict"] == "GRANT_PRESENT" and out["read_only"] else 1


if __name__ == "__main__":
    sys.exit(main())
