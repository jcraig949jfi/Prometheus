"""KAIROS-01 (b): an exported census of EVERY claim on an engine ledger, for a
seat that owns no worlds and therefore can read no claims through the API.

Deploy-side, run by the maintainer against the ledger file READ ONLY
(mode=ro; nothing is written, no lock is taken beyond a WAL reader's). It is
not an engine read path and it does not go through grants: the maintainer
holds the ledger, and this file hands the auditing seat what the owner-scoped
routes cannot. Say that plainly wherever the output is consumed -- a row in
this census is not evidence that its owner granted anything.

    python deploy/claim_census.py --db <ledger path> --out kairos/censuses/claims_M1_<date>.json

Per claim, exactly what GET /v2/claims/{id} returns to its owner: the stored
row plus the findings SEALED into CLAIM_RECORDED at creation and the build
hash that computed them (sfe/runtime.py get_claim). Plus the client NAME
(never the token hash) and, for claims in a family, the family's member
count so a lint can see the comparison set's size. No secrets: the census
is asserted token-free by tests/test_sfe_claim_census.py, which registers a
client and checks its token hash never appears in the output.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENGINE = os.path.dirname(_HERE)
if _ENGINE not in sys.path:
    sys.path.insert(0, _ENGINE)

from sfe.store import SCHEMA_VERSION  # noqa: E402


def _ro(path: str) -> sqlite3.Connection:
    uri = "file:{}?mode=ro".format(str(path).replace("?", "%3f"))
    c = sqlite3.connect(uri, uri=True, timeout=5)
    c.row_factory = sqlite3.Row
    return c


def _j(s):
    if not s:
        return None
    try:
        return json.loads(s)
    except (TypeError, ValueError):
        return None


def census(db_path: str) -> dict:
    c = _ro(db_path)
    try:
        meta = {r["key"]: r["value"] for r in c.execute("SELECT key, value FROM meta")}
        names = {r["client_id"]: r["name"] for r in c.execute("SELECT client_id, name FROM clients")}
        fam_n = {r["family_id"]: r["n"] for r in c.execute(
            "SELECT family_id, COUNT(*) n FROM family_members GROUP BY family_id")}
        rows = []
        for r in c.execute("SELECT * FROM claims ORDER BY created_ts"):
            ev = c.execute(
                "SELECT payload FROM foundry_events WHERE event_type='CLAIM_RECORDED' "
                "AND scope_kind='claim' AND scope_id=? ORDER BY seq DESC LIMIT 1",
                (r["claim_id"],)).fetchone()
            sealed = _j(ev["payload"]) if ev is not None else None
            sealed = sealed if isinstance(sealed, dict) else {}
            rows.append({
                "claim_id": r["claim_id"],
                "client_id": r["client_id"],
                "client_name": names.get(r["client_id"]),
                "status": r["status"],
                "family_id": r["family_id"],
                "family_members": fam_n.get(r["family_id"]) if r["family_id"] else None,
                "analysis_exp_id": r["analysis_exp_id"],
                "analysis_world_id": r["analysis_world_id"],
                "estimand": r["estimand"],
                "relevance_floor": _j(r["relevance_floor"]),
                "replication": _j(r["replication"]) or {},
                "transport_domain": _j(r["transport_domain"]),
                "content_hash": r["content_hash"],
                "created_ts": r["created_ts"],
                "science": {
                    "profile_findings": sealed.get("findings", []),
                    "sealed_at_creation": ev is not None,
                    "engine_source_hash": sealed.get("engine_source_hash"),
                },
            })
        by_status = {}
        for x in rows:
            by_status[x["status"]] = by_status.get(x["status"], 0) + 1
        return {
            "schema": "sfe_claim_census.v1",
            "census_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "engine_instance_id": meta.get("engine_instance_id"),
            "ledger_schema_version": int(meta.get("schema_version", 0)),
            "census_tool_schema_version": SCHEMA_VERSION,
            "read_path": "deploy-side ledger export (mode=ro); NOT an engine read route; NOT gated by read grants",
            "owners_included": sorted({x["client_name"] or x["client_id"] for x in rows}),
            "n_claims": len(rows),
            "by_status": by_status,
            "claims": rows,
        }
    finally:
        c.close()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", required=True, help="engine ledger (opened read-only)")
    ap.add_argument("--out", default=None, help="write the census JSON here")
    a = ap.parse_args(argv)
    out = census(a.db)
    text = json.dumps(out, indent=1, sort_keys=True)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("wrote %s: %d claims, %s" % (a.out, out["n_claims"], out["by_status"]))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
