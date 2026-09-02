"""Operator tool: client token lifecycle for the Serendipity Foundry Engine.

Runs ON THE ENGINE HOST against the Engine database directly -- possession of
the DB is the operator credential (no privileged API surface is added). Simple
lifecycle correctness, not an IAM system:

    python manage_client.py --db var/engine.db list
    python manage_client.py --db var/engine.db revoke  --client-id cli_...
    python manage_client.py --db var/engine.db reissue --client-id cli_...

`revoke` kills the client's current token immediately (401 from then on).
`reissue` binds a NEW token to the SAME client_id -- identity and all historical
provenance unchanged -- and prints the token ONCE. Both are recorded on the
foundry audit chain (CLIENT_TOKEN_REVOKED / CLIENT_TOKEN_REISSUED).
"""

from __future__ import annotations

import argparse
import hashlib
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sfe.runtime import Foundry                      # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    for c in ("revoke", "reissue"):
        p = sub.add_parser(c)
        p.add_argument("--client-id", required=True)
    args = ap.parse_args()

    f = Foundry(args.db)
    try:
        if args.cmd == "list":
            rows = f.store.read().execute(
                "SELECT client_id, name, token_hash IS NOT NULL AS has_token, "
                "created_ts FROM clients ORDER BY created_ts").fetchall()
            for r in rows:
                state = "ACTIVE" if r["has_token"] else "REVOKED/NO-TOKEN"
                print(f"{r['client_id']}  {state:16s}  {r['name']}")
            return 0
        if args.cmd == "revoke":
            f.revoke_token(args.client_id)
            print(f"revoked: {args.client_id} (its token now returns 401)")
            return 0
        if args.cmd == "reissue":
            tok = "gen2_" + secrets.token_urlsafe(24)
            f.reissue_token(args.client_id,
                            hashlib.sha256(tok.encode()).hexdigest())
            print(f"reissued for {args.client_id} -- token shown ONCE:")
            print(tok)
            return 0
        return 2
    finally:
        f.close()


if __name__ == "__main__":
    raise SystemExit(main())
