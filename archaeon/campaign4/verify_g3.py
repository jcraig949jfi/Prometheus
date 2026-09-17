"""G3 proof: the Campaign 4 identity can actually read the M2 ledger through the grant.

    python -m archaeon.campaign4.verify_g3

Writes archaeon/campaign4/G3_READ_PROOF.json. The launch gate reads that receipt, so G3 stops
being "a seat said the grant is issued" and becomes "the read succeeded, here is what came back".
A grant row on the ledger is not the completion test; a successful scoped read is.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "archaeon" / "campaign4" / "G3_READ_PROOF.json"


def main() -> int:
    from archaeon.campaign2.runner import Engine
    from archaeon.campaign4.c4base import CAMPAIGN_4
    eng = Engine(config=CAMPAIGN_4["config"], client_name=CAMPAIGN_4["client"])
    d = eng.descriptor
    grants = eng.c.read_grants()
    to_me = grants.get("granted_to_me", [])
    worlds = eng.c.read_worlds()
    obs = eng.c.read_observations()
    wl = worlds.get("worlds", []) if isinstance(worlds, dict) else []
    ol = obs.get("observations", []) if isinstance(obs, dict) else []
    doc = {
        "_what_this_is": "G3 completion evidence: a real scoped read on the M2 ledger using the Campaign 4 identity.",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": "Archaeon[m2-411504ab]",
        "engine": {"instance": d["engine_instance_id"], "schema": d["schema_version"],
                   "endpoint": d["base_url"], "source_hash": d["engine_source_hash"]},
        "client": CAMPAIGN_4["client"],
        "grants_to_me": [{k: g.get(k) for k in ("grant_id", "scope_id", "grantee_client_id", "granted_by", "revoked_at")}
                         for g in to_me],
        "read_worlds_n": len(wl),
        "read_observations_n": len(ol),
        "sample_world_ids": [w.get("world_id") for w in wl[:3]],
        "sample_obs_ids": [o.get("obs_id") for o in ol[:3]],
        "checks": {
            "grant_present": len(to_me) > 0,
            "grant_not_revoked": all(not g.get("revoked_at") for g in to_me),
            "scoped_world_read_returned_rows": len(wl) > 0,
            "scoped_observation_read_returned_rows": len(ol) > 0,
        },
    }
    doc["all_pass"] = all(doc["checks"].values())
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: doc[k] for k in ("client", "read_worlds_n", "read_observations_n", "checks", "all_pass")}, indent=1))
    print("written:", OUT)
    return 0 if doc["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
