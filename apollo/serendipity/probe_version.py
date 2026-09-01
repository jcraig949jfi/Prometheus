"""probe_version.py -- read-only Foundry connectivity + live-release probe.

Does exactly one non-mutating thing: GET /v0/version, UNPINNED, so it learns the
current source_tree_hash instead of trusting any recorded pin (three different pins
are on record: ee4cfa87 / 50b5c232 / 5f62e12d -- the instrument is moving). Prints
only non-secret version metadata. NEVER prints the token. Budget-free, touches no
world, safe to run against a live host other seats are using.

Usage: python apollo/serendipity/probe_version.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import foundry_creds as fc  # noqa: E402
from remote import (  # noqa: E402
    FoundryClientError, ReleaseMismatch, FoundryHTTPError, TransportIndeterminate,
)

_SECRET_KEYS = {"token", "authorization", "bearer", "secret"}


def _safe(info: dict) -> dict:
    return {k: v for k, v in info.items() if k.lower() not in _SECRET_KEYS}


def main() -> int:
    pf = fc.preflight()
    print("preflight:", json.dumps(pf))
    if not (pf["token_present"] and pf["cert_present"]):
        print("NOT READY: credential kit incomplete (token/cert). "
              "Provision C:\\ZeusD-var\\d11\\remote or set FOUNDRY_ADMIN_TOKEN/"
              "FOUNDRY_M1_CERT.")
        return 2
    try:
        client = fc.make_client(expected_release_hash=None, timeout_s=15.0)
        info = client.version()  # GET /v0/version, no gate
    except ReleaseMismatch as e:
        print(f"RELEASE MISMATCH (unexpected on unpinned probe): {e}")
        return 1
    except FoundryHTTPError as e:
        print(f"HTTP {e.status}: definite rejection (auth/validation). "
              f"detail={e.detail}")
        return 1
    except TransportIndeterminate as e:
        print(f"INDETERMINATE: {e.cause} (trace {e.trace_id}). Host reachable? "
              f"Reconcile is not needed for a read-only GET.")
        return 1
    except FoundryClientError as e:
        print(f"CLIENT ERROR: {e}")
        return 1

    safe = _safe(info)
    print("LIVE FOUNDRY version:", json.dumps(safe, indent=2))
    pin = info.get("source_tree_hash")
    print(f"\nLIVE source_tree_hash = {pin}")
    print("  -> this is the pin Apollo experiments should declare from now on.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
