"""Launch the Serendipity Foundry Engine as a network service.

    python serve.py --db <path> --host <ip> --port <n> [--tls-cert F --tls-key F]

Boring on purpose: it builds the FastAPI app over one SQLite database and runs
uvicorn. TLS is applied at the server (reuse a cert/key), because the API auth is
bearer-token and tokens must not cross a LAN in clear. Binds a SPECIFIC address
(never 0.0.0.0). The Engine is independent of any other service on the box.
"""

from __future__ import annotations

import argparse
import ipaddress
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sfe.api import create_app          # noqa: E402


def _unspecified(host: str) -> bool:
    if host in ("0.0.0.0", "::", "*", ""):
        return True
    try:
        return ipaddress.ip_address(host).is_unspecified
    except ValueError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="path to the Engine SQLite db")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8811)
    ap.add_argument("--tls-cert", default=None)
    ap.add_argument("--tls-key", default=None)
    ap.add_argument("--insecure", action="store_true",
                    help="allow a non-loopback bind without TLS (tokens in clear)")
    ap.add_argument("--science-profile", choices=("off", "warn", "strict"),
                    default="warn",
                    help="v6 scientific-provenance checks. off = not computed "
                         "(a true v5 control arm); warn = computed, reported "
                         "and sealed in the event, never blocking (default); "
                         "strict = a finding that contradicts a sealed "
                         "declaration fails the call.")
    ap.add_argument("--session-enforcement", choices=("advisory", "strict"),
                    default="advisory",
                    help="advisory (default): a missing X-SFE-Session is "
                         "allowed and counted. strict: a missing key on a "
                         "bound session is 428. A key from ANOTHER engine is "
                         "421 WRONG_SESSION in both modes -- that is never "
                         "optional.")
    ap.add_argument("--registration", choices=("open", "closed"),
                    default="open",
                    help="closed = POST /v2/clients is operator-gated (403); "
                         "existing tokens keep working. Use after bootstrap.")
    args = ap.parse_args()

    if _unspecified(args.host):
        print("ERROR: bind a specific address, not all interfaces.",
              file=sys.stderr)
        return 2
    tls = bool(args.tls_cert and args.tls_key)
    exposed = args.host not in ("127.0.0.1", "localhost", "::1")
    if exposed and not tls and not args.insecure:
        print("ERROR: a LAN bind needs TLS (--tls-cert/--tls-key) so bearer "
              "tokens are not sent in clear; or pass --insecure on a trusted "
              "segment.", file=sys.stderr)
        return 2

    import uvicorn
    app = create_app(args.db,
                     registration_open=(args.registration == "open"),
                     session_enforcement=args.session_enforcement,
                     science_profile=args.science_profile)
    scheme = "https" if tls else "http"
    print(f"Serendipity Foundry Engine listening on {scheme}://{args.host}:"
          f"{args.port}  db={args.db}")
    uvicorn.run(app, host=args.host, port=args.port,
                ssl_certfile=args.tls_cert, ssl_keyfile=args.tls_key,
                proxy_headers=False, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
