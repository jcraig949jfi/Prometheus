"""B1: the owner of a set of worlds grants one other client READ over them.

Run by the WORLD OWNER (today: Vivarium, for Archaeon), never by Daedalus --
a read scope is a curated set of the caller's OWN worlds and only the owner
can create it, add to it, or grant it (sfe/runtime.py create_read_scope,
add_scope_worlds, grant_read). The maintainer holds no owner token and must
not; this tool exists so the owner's act is one command with a receipt.

    set SFE_TOKEN=<the owner's token>          (env only; never an argument)
    python deploy/read_scope_grant.py ^
        --base-url https://192.168.1.202:8811 ^
        --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt ^
        --scope-name archaeon-campaigns ^
        --grantee cli_xxxxxxxxxxxxxxxxxxxxxxxx ^
        --receipt roles/Vivarium/receipts/read_grant_archaeon.json

Idempotent by construction: the scope is reused by name, world membership is
INSERT OR IGNORE on the engine, and an unrevoked grant to the same grantee is
returned rather than duplicated. Re-run it after every campaign to EXTEND the
scope -- that maintenance is the safety property (a scope nobody has to touch
is a scope nobody is checking). Lifecycle: revoke with
POST /v2/read/grants/{grant_id}/revoke (owner only); the credential itself
cannot be revoked (backlog C6), so a leaked grantee token is handled by
revoking every grant that names it and registering a new grantee.

The receipt carries ids and counts only. It never carries a token.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_CLIENT = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "SerendipityFoundryClient")
if _CLIENT not in sys.path:
    sys.path.insert(0, _CLIENT)


def ensure_grant(c, *, scope_name: str, grantee_client_id: str,
                 world_filter=None, note: str = None, dry_run: bool = False) -> dict:
    """c: anything with list_worlds / read_scopes / create_read_scope /
    add_scope_worlds / grant_read / client_id. Returns the receipt dict."""
    owned = c.list_worlds()
    if world_filter:
        owned = [w for w in owned if world_filter(w)]
    world_ids = sorted(w["world_id"] for w in owned)
    existing = [s for s in c.read_scopes() if s["name"] == scope_name]
    receipt = {
        "schema": "read_scope_grant_receipt.v1",
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "owner_client_id": getattr(c, "client_id", None),
        "grantee_client_id": grantee_client_id,
        "scope_name": scope_name,
        "worlds_owned_matching": len(world_ids),
        "dry_run": dry_run,
    }
    if dry_run:
        receipt.update({"scope_id": existing[0]["scope_id"] if existing else None,
                        "scope_existed": bool(existing),
                        "would_add": len(world_ids)})
        return receipt
    if existing:
        scope = existing[0]
        created = False
    else:
        scope = c.create_read_scope(scope_name, note=note)
        created = True
    before = int(scope.get("worlds", 0))
    add = c.add_scope_worlds(scope["scope_id"], world_ids) if world_ids else {}
    after = [s for s in c.read_scopes() if s["scope_id"] == scope["scope_id"]][0]
    grant = c.grant_read(scope["scope_id"], grantee_client_id, note=note)
    receipt.update({
        "scope_id": scope["scope_id"],
        "scope_created": created,
        "worlds_in_scope_before": before,
        "worlds_in_scope_after": int(after["worlds"]),
        "worlds_added_this_run": int(after["worlds"]) - before,
        "not_yours": list(add.get("not_yours", [])) if isinstance(add, dict) else [],
        "grant_id": grant["grant_id"],
        "grant_revoked_ts": grant.get("revoked_ts"),
        "revoke_route": "POST /v2/read/grants/%s/revoke (owner only)" % grant["grant_id"],
        "extend": "re-run this command after each campaign; adds are idempotent",
    })
    return receipt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--cacert", default=None)
    ap.add_argument("--insecure", action="store_true")
    ap.add_argument("--scope-name", required=True)
    ap.add_argument("--grantee", required=True, help="grantee client_id (cli_...)")
    ap.add_argument("--name-prefix", default=None,
                    help="only worlds whose name starts with this (e.g. viv-)")
    ap.add_argument("--note", default=None)
    ap.add_argument("--receipt", default=None, help="write the receipt JSON here")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    token = os.environ.get("SFE_TOKEN")
    if not token:
        print("SFE_TOKEN is not set; the owner's token comes from the environment, never an argument",
              file=sys.stderr)
        return 2
    from sfclient.client import EngineClient
    c = EngineClient(a.base_url, token=token, cafile=a.cacert, insecure=a.insecure)
    flt = (lambda w: str(w.get("name", "")).startswith(a.name_prefix)) if a.name_prefix else None
    r = ensure_grant(c, scope_name=a.scope_name, grantee_client_id=a.grantee,
                     world_filter=flt, note=a.note, dry_run=a.dry_run)
    r["base_url"] = a.base_url
    out = json.dumps(r, indent=1, sort_keys=True)
    print(out)
    if a.receipt:
        with open(a.receipt, "w", encoding="ascii") as fh:
            fh.write(out + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
